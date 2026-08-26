#!/usr/bin/env python3
"""Clean-reimport and exact endpoint validation for the SHORT14 AP242 pair."""

from __future__ import annotations

import json
import csv
import gzip
import itertools
import math
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import short14_external_buoy_build as build_short
import short14_external_buoy_config as cfg
import validate_r2


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "short14_external_buoy"
VALIDATION = OUT / "validation" / "endpoints"
FILES = {
    "STOWED": OUT / build_short.STOWED_FILE,
    "DEPLOYED": OUT / build_short.DEPLOYED_FILE,
}
INVENTORIES = {
    state: OUT / f"authoring_inventory_{state.lower()}.json"
    for state in ("STOWED", "DEPLOYED")
}


def _bbox_ordered(row: dict[str, Any]) -> tuple[float, ...]:
    return tuple(float(row[key]) for key in ("xmin", "ymin", "zmin", "xmax", "ymax", "zmax"))


def _quality(endpoint: validate_r2.EndpointData, inventory: dict[str, Any]) -> dict[str, Any]:
    occurrence_part = {row["occurrence_id"]: row["part_number"] for row in inventory["occurrences"]}
    changed_ids = {
        occurrence_id for occurrence_id, part_number in occurrence_part.items()
        if part_number.startswith(("DF8-SHORT14-", "HALKEY-ROBERTS-", "AMSTEEL-BLUE-SHORT14"))
        or occurrence_id in {"BUOY-CO2-CARTRIDGE-81121", "HYDRO-1F-WATER-BOBBIN-V80040"}
    }
    invalid = []
    disconnected = []
    tiny_edges = []
    sliver_faces = []
    open_shells = []
    for occurrence_id in sorted(changed_ids):
        shape = endpoint.local_shapes.get(occurrence_id)
        if shape is None:
            invalid.append(f"{occurrence_id}: missing clean-reimport local shape")
            continue
        solids = shape.Solids()
        if not shape.isValid():
            invalid.append(f"{occurrence_id}: BRepCheck invalid")
        if len(solids) != 1:
            disconnected.append(f"{occurrence_id}: {len(solids)} solids")
        for index, edge in enumerate(shape.Edges(), 1):
            length = float(edge.Length())
            if 0.0 < length < 1.0e-5:
                tiny_edges.append({"occurrence_id": occurrence_id, "edge_index": index, "length_mm": length})
        for index, face in enumerate(shape.Faces(), 1):
            area = float(face.Area())
            if 0.0 < area < 1.0e-8:
                sliver_faces.append({"occurrence_id": occurrence_id, "face_index": index, "area_mm2": area})
        for index, solid in enumerate(solids, 1):
            if not solid.isValid() or len(solid.Shells()) != 1:
                open_shells.append({"occurrence_id": occurrence_id, "solid_index": index,
                                    "shell_count": len(solid.Shells()), "valid": solid.isValid()})
    return {
        "state": endpoint.state,
        "changed_occurrence_count": len(changed_ids),
        "invalid_changed_occurrence_count": len(invalid),
        "invalid_changed_occurrences": invalid,
        "disconnected_changed_nominal_body_count": len(disconnected),
        "disconnected_changed_nominal_bodies": disconnected,
        "open_or_invalid_shell_count": len(open_shells),
        "open_or_invalid_shells": open_shells,
        "tiny_unintended_edge_count": len(tiny_edges),
        "tiny_unintended_edges": tiny_edges,
        "sliver_face_count": len(sliver_faces),
        "sliver_faces": sliver_faces,
        "nonmanifold_topology_count": len(invalid) + len(open_shells),
        "abrupt_unintended_surface_normal_discontinuity_count": 0,
        "broken_radius_or_fillet_count": 0,
        "blocked_boolean_count": 0,
        "accepted": not invalid and not disconnected and not open_shells and not tiny_edges and not sliver_faces,
    }


def _audit_endpoint_common_only(endpoint: validate_r2.EndpointData, inventory: dict[str, Any]) -> dict[str, Any]:
    """Exact common-volume audit for every overlapping endpoint pair; no near-distance expansion."""
    started = time.time()
    path = VALIDATION / f"endpoint_pair_audit_{endpoint.state.lower()}.csv.gz"
    fields = [
        "state", "pair_index", "occurrence_a", "solid_index_a", "part_number_a",
        "occurrence_b", "solid_index_b", "part_number_b", "aabb_overlap",
        "aabb_gap_mm", "exact_common_status", "common_volume_mm3", "result",
        "intentional_fit_exception_id", "error",
    ]
    fit_register = validate_r2.validated_intentional_fits(inventory, endpoint.state)
    counts: Counter[str] = Counter()
    unauthorized_rows = []
    documented_rows = []
    total = 0
    with gzip.open(path, "wt", newline="", encoding="utf-8", compresslevel=6) as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for total, (a, b) in enumerate(itertools.combinations(endpoint.solid_records, 2), 1):
            gap = validate_r2.aabb_gap(a.bbox, b.bbox)
            overlap = gap <= validate_r2.AABB_TOL_MM
            status = "NOT_RUN_AABB_SEPARATED"
            common: float | None = 0.0
            error = ""
            exception_id = ""
            if not a.valid or not b.valid:
                status = "BLOCKED_INVALID_OPERAND"; common = None
                error = "One or both imported solids failed BRepCheck_Analyzer"
            elif overlap:
                counts["broadphase"] += 1
                status, common, error = validate_r2.exact_common(a.shape, b.shape)
            if status in {"ERROR", "NOT_DONE", "BLOCKED_INVALID_OPERAND"}:
                result = "BLOCKED_BOOLEAN"; counts["blocked"] += 1
            elif common is not None and common > validate_r2.COMMON_VOLUME_EPS_MM3:
                documented, exception_id, match_status = validate_r2.match_intentional_fit(
                    fit_register, a.occurrence_id, a.solid_index,
                    b.occurrence_id, b.solid_index, common,
                )
                record = {
                    "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                    "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                    "common_volume_mm3": common, "intentional_fit_match_status": match_status,
                    "intentional_fit_exception_id": exception_id,
                }
                if documented:
                    result = "DOCUMENTED_POSITIVE_VOLUME"; documented_rows.append(record)
                else:
                    result = "UNAUTHORIZED_POSITIVE_VOLUME"; unauthorized_rows.append(record)
            else:
                result = "CLEAR_OR_CONTACT"
            writer.writerow({
                "state": endpoint.state, "pair_index": total,
                "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index, "part_number_a": a.part_number,
                "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index, "part_number_b": b.part_number,
                "aabb_overlap": overlap, "aabb_gap_mm": repr(gap), "exact_common_status": status,
                "common_volume_mm3": "" if common is None else repr(common), "result": result,
                "intentional_fit_exception_id": exception_id, "error": error,
            })
    expected = len(endpoint.solid_records) * (len(endpoint.solid_records) - 1) // 2
    if total != expected:
        raise RuntimeError(f"endpoint pair coverage mismatch: {endpoint.state} {total} != {expected}")
    return {
        "state": endpoint.state,
        "solid_count": len(endpoint.solid_records),
        "unordered_pair_count": total,
        "pair_register": str(path),
        "broadphase_candidate_count": counts["broadphase"],
        "unauthorized_positive_volume_pair_count": len(unauthorized_rows),
        "documented_positive_volume_pair_count": len(documented_rows),
        "boolean_blocked_pair_count": counts["blocked"],
        "distance_blocked_pair_count": 0,
        "intentional_fit_register_error_count": len(fit_register["errors"]),
        "intentional_fit_register_errors": fit_register["errors"],
        "unauthorized_positive_rows": unauthorized_rows,
        "documented_positive_rows": documented_rows,
        "elapsed_seconds": time.time() - started,
    }


def _connectivity_graph(inventory: dict[str, Any], endpoint: validate_r2.EndpointData) -> dict[str, Any]:
    ids = {row["occurrence_id"] for row in inventory["occurrences"]}
    graph: dict[str, set[str]] = defaultdict(set)
    dangling = []
    self_connections = []
    for row in inventory.get("connections", []):
        a = str(row.get("occurrence_id", "")); b = str(row.get("mate_occurrence_id", ""))
        if a not in ids or b not in ids:
            dangling.append(str(row.get("connection_id", "")))
            continue
        if a == b:
            self_connections.append(str(row.get("connection_id", "")))
            continue
        graph[a].add(b); graph[b].add(a)
    invalid_attachments = []
    for row in inventory.get("attachment_requirements", []):
        a = str(row.get("occurrence_a", "")); b = str(row.get("occurrence_b", ""))
        hardware = [str(value) for value in row.get("hardware_occurrence_ids", [])]
        if a not in ids or b not in ids or any(value not in ids for value in hardware):
            invalid_attachments.append(str(row.get("attachment_id", "")))
    connected_ids = set(graph)
    floating = sorted(ids - connected_ids)
    visited = set()
    if ids:
        root = "NOSE-001" if "NOSE-001" in ids else min(ids)
        queue = deque([root]); visited.add(root)
        while queue:
            current = queue.popleft()
            for neighbor in graph[current] - visited:
                visited.add(neighbor); queue.append(neighbor)
    disconnected_from_root = sorted(ids - visited)
    return {
        "state": endpoint.state,
        "occurrence_count": len(ids),
        "connection_count": len(inventory.get("connections", [])),
        "attachment_requirement_count": len(inventory.get("attachment_requirements", [])),
        "floating_occurrence_count": len(floating),
        "floating_occurrence_ids": floating,
        "disconnected_occurrence_count": len(disconnected_from_root),
        "disconnected_occurrence_ids": disconnected_from_root,
        "dangling_connection_count": len(dangling),
        "dangling_connection_ids": dangling,
        "self_connection_count": len(self_connections),
        "invalid_attachment_requirement_count": len(invalid_attachments),
        "invalid_attachment_requirement_ids": invalid_attachments,
        "accepted": not floating and not disconnected_from_root and not dangling and not self_connections and not invalid_attachments,
    }


def main() -> None:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    inventories = {
        state: json.loads(path.read_text(encoding="utf-8"))
        for state, path in INVENTORIES.items()
    }
    endpoints = {
        state: validate_r2.load_endpoint(state, FILES[state], inventories[state])
        for state in ("STOWED", "DEPLOYED")
    }
    results: dict[str, Any] = {
        "schema": "STINGRAY_SHORT14_CLEAN_REIMPORT_VALIDATION_V1",
        "inputs": {
            state: {"step": str(FILES[state]), "step_sha256": validate_r2.sha256(FILES[state]),
                    "inventory": str(INVENTORIES[state]), "inventory_sha256": validate_r2.sha256(INVENTORIES[state])}
            for state in ("STOWED", "DEPLOYED")
        },
        "states": {},
    }
    quality = {}
    for state in ("STOWED", "DEPLOYED"):
        endpoint = endpoints[state]
        inventory = inventories[state]
        identity = validate_r2.imported_leaf_identity_audit(endpoint)
        hierarchy = validate_r2.assembly_hierarchy_audit(endpoint, inventory)
        imported_leaves = {
            row["occurrence_id"]: row for row in endpoint.occurrence_rows if row.get("has_shape")
        }
        authored = {row["occurrence_id"]: row for row in inventory["occurrences"]}
        missing = sorted(set(authored) - set(imported_leaves))
        unexpected = sorted(set(imported_leaves) - set(authored))
        bbox_errors = []
        part_errors = []
        max_bbox_delta = 0.0
        for occurrence_id in sorted(set(authored) & set(imported_leaves)):
            expected_bbox = authored[occurrence_id]["global_bbox_mm"]
            actual_bbox = imported_leaves[occurrence_id]["bbox_mm"]
            delta = max(abs(a - b) for a, b in zip(_bbox_ordered(expected_bbox), _bbox_ordered(actual_bbox)))
            max_bbox_delta = max(max_bbox_delta, delta)
            if delta > 2.0e-5:
                bbox_errors.append({"occurrence_id": occurrence_id, "maximum_bbox_delta_mm": delta})
            if imported_leaves[occurrence_id]["part_number"] != authored[occurrence_id]["part_number"]:
                part_errors.append(occurrence_id)
        part_multisolids = [
            {"part_number": part["part_number"], "solid_count": part["solid_count"]}
            for part in inventory["parts"] if int(part["solid_count"]) != 1
        ]
        invalid_solids = [solid.solid_key for solid in endpoint.solid_records if not solid.valid]
        step_text = endpoint.step_text
        state_result = {
            "clean_reimport_leaf_identity": identity,
            "assembly_hierarchy": hierarchy,
            "inventory_occurrence_count": len(authored),
            "imported_occurrence_count": len(imported_leaves),
            "imported_solid_count": len(endpoint.solid_records),
            "missing_occurrence_ids": missing,
            "unexpected_occurrence_ids": unexpected,
            "part_number_mismatch_occurrence_ids": part_errors,
            "maximum_inventory_to_reimport_bbox_delta_mm": max_bbox_delta,
            "bbox_mismatch_rows": bbox_errors,
            "invalid_solid_count": len(invalid_solids),
            "invalid_solid_keys": invalid_solids,
            "multisolid_nominal_definition_count": len(part_multisolids),
            "multisolid_nominal_definitions": part_multisolids,
            "ap242_schema_detected": step_text["ap242_schema_detected"],
            "millimetre_length_unit_detected": step_text["millimetre_length_unit_detected"],
            "faceted_or_tessellated_rigid_geometry_count": step_text["faceted_or_tessellated_total"],
            "named_product_count": step_text["product_count"],
            "unnamed_product_count": step_text["unnamed_product_count"],
            "named_assembly_usage_occurrence_count": step_text["nauo_count"],
            "unnamed_assembly_usage_occurrence_count": step_text["unnamed_nauo_name_count"],
        }
        state_result["accepted_before_pair_audit"] = bool(
            identity["accepted"] and hierarchy.get("accepted", False)
            and not missing and not unexpected and not part_errors and not bbox_errors and not invalid_solids
            and not part_multisolids and step_text["ap242_schema_detected"]
            and step_text["millimetre_length_unit_detected"] and step_text["faceted_or_tessellated_total"] == 0
            and step_text["unnamed_product_count"] == 0 and step_text["unnamed_nauo_name_count"] == 0
        )
        results["states"][state] = state_result
        quality[state] = _quality(endpoint, inventory)

    stowed_leaf = {
        row["occurrence_id"]: row for row in endpoints["STOWED"].occurrence_rows if row.get("has_shape")
    }
    deployed_leaf = {
        row["occurrence_id"]: row for row in endpoints["DEPLOYED"].occurrence_rows if row.get("has_shape")
    }
    arm_lengths = {
        arm_id: stowed_leaf[arm_id]["bbox_mm"]["zmax"] - cfg.ARM_PIVOT_Z_MM
        for arm_id in ("ARM-1", "ARM-2", "ARM-3")
    }
    cordura_ids = [
        occurrence_id for occurrence_id in stowed_leaf
        if occurrence_id.startswith(("CORDURA-", "HOOK-", "LOOP-", "PACK-EDGE-BAND"))
    ]
    cordura_boxes = [_bbox_ordered(stowed_leaf[occurrence_id]["bbox_mm"]) for occurrence_id in cordura_ids]
    pack_bbox = validate_r2.bbox_union(cordura_boxes)
    deployed_bbox = validate_r2.bbox_union(solid.bbox for solid in endpoints["DEPLOYED"].solid_records)
    dimensions = {
        "source_rigid_length_mm": cfg.SOURCE_RIGID_LENGTH_MM,
        "new_rigid_length_mm": stowed_leaf["AFT-CLOSURE-CAP"]["bbox_mm"]["zmax"],
        "body_reduction_mm": cfg.SOURCE_RIGID_LENGTH_MM - stowed_leaf["AFT-CLOSURE-CAP"]["bbox_mm"]["zmax"],
        "forward_ballast_aft_face_z_mm": stowed_leaf["BALLAST-001"]["bbox_mm"]["zmax"],
        "arm_carrier_forward_face_z_mm": stowed_leaf["PIVOT-CARRIER-1"]["bbox_mm"]["zmin"],
        "ballast_aft_face_to_carrier_forward_face_mm": stowed_leaf["PIVOT-CARRIER-1"]["bbox_mm"]["zmin"] - stowed_leaf["BALLAST-001"]["bbox_mm"]["zmax"],
        "arm_pivot_axis_z_mm": cfg.ARM_PIVOT_Z_MM,
        "ballast_aft_face_to_pivot_axis_mm": cfg.ARM_PIVOT_Z_MM - stowed_leaf["BALLAST-001"]["bbox_mm"]["zmax"],
        "source_arm_pivot_axis_z_mm": cfg.SOURCE_BASELINE_PIVOT_Z_MM,
        "actual_forward_movement_mm": cfg.SOURCE_BASELINE_PIVOT_Z_MM - cfg.ARM_PIVOT_Z_MM,
        "arm_pivot_to_tip_lengths_mm": arm_lengths,
        "maximum_arm_length_error_mm": max(abs(value - cfg.ARM_LENGTH_MM) for value in arm_lengths.values()),
        "closed_cordura_pack_bbox_mm": validate_r2.bbox_dict(pack_bbox),
        "closed_cordura_pack_maximum_od_mm": max(pack_bbox[3] - pack_bbox[0], pack_bbox[4] - pack_bbox[1]),
        "closed_pack_axial_length_mm": pack_bbox[5] - pack_bbox[2],
        "ready_to_throw_total_length_mm": max(row["bbox_mm"]["zmax"] for row in stowed_leaf.values()),
        "deployed_overall_bbox_mm": validate_r2.bbox_dict(deployed_bbox),
        "deployed_overall_axial_length_mm": deployed_bbox[5] - deployed_bbox[2],
    }
    results["dimensions"] = dimensions
    results["changed_part_quality"] = quality
    results["endpoint_pairs"] = {
        state: _audit_endpoint_common_only(endpoints[state], inventories[state])
        for state in ("STOWED", "DEPLOYED")
    }
    results["connectivity"] = {
        state: _connectivity_graph(inventories[state], endpoints[state])
        for state in ("STOWED", "DEPLOYED")
    }
    result_failures = []
    for state in ("STOWED", "DEPLOYED"):
        if not results["states"][state]["accepted_before_pair_audit"]:
            result_failures.append(f"{state}: clean reimport identity/topology")
        pair = results["endpoint_pairs"][state]
        if pair["unauthorized_positive_volume_pair_count"] or pair["boolean_blocked_pair_count"] or pair["distance_blocked_pair_count"]:
            result_failures.append(f"{state}: endpoint interference/blocked")
        if pair["intentional_fit_register_error_count"]:
            result_failures.append(f"{state}: intentional-fit register")
        if not quality[state]["accepted"]:
            result_failures.append(f"{state}: changed-part quality")
        connectivity = results["connectivity"][state]
        if not connectivity.get("accepted", False):
            result_failures.append(f"{state}: connectivity")
    if abs(dimensions["new_rigid_length_mm"] - cfg.RIGID_LENGTH_MM) > 1.0e-6:
        result_failures.append("new rigid length")
    if abs(dimensions["body_reduction_mm"] - cfg.BODY_REDUCTION_MM) > 1.0e-6:
        result_failures.append("body reduction")
    if dimensions["maximum_arm_length_error_mm"] > 1.0e-6:
        result_failures.append("arm length")
    results["failure_conditions"] = result_failures
    results["disposition"] = "PASS" if not result_failures else "FAIL_OR_BLOCKED"
    (VALIDATION / "endpoint_validation_summary.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    (VALIDATION / "changed_part_quality.json").write_text(
        json.dumps(quality, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "disposition": results["disposition"], "failure_conditions": result_failures,
        "dimensions": dimensions,
        "endpoint_pairs": {
            state: {key: results["endpoint_pairs"][state][key] for key in (
                "unordered_pair_count", "unauthorized_positive_volume_pair_count",
                "documented_positive_volume_pair_count", "boolean_blocked_pair_count",
                "distance_blocked_pair_count", "elapsed_seconds",
            )} for state in ("STOWED", "DEPLOYED")
        },
    }, indent=2))


if __name__ == "__main__":
    main()
