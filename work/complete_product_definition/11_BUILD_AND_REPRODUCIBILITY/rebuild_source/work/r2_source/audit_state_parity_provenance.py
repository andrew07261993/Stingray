#!/usr/bin/env python3
"""Classify the original DF8 endpoint parity mismatches without changing CAD.

The audit starts from the preserved original failing state-parity CSV, cleanly
reimports the current AP242 endpoints through XCAF, reruns the corrected parity
validator, and emits one evidence-rich A/B/C disposition for every original
mismatch.  Global placement is evaluated independently from local exact-BREP
identity so a legitimate mechanism transform cannot masquerade as a geometry
mutation and a serialization digest cannot by itself create a CAD defect.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import (
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_VERTEX,
    TopAbs_WIRE,
)

import validate_r2 as vr


DEFAULT_ORIGINAL = vr.FINAL_ANALYSIS_DIR / "validation" / "state_parity.csv"
DEFAULT_OUT = vr.FINAL_ANALYSIS_DIR / "state_parity_provenance_audit"
SAME_CHECKPOINT_PRIOR_PARITY = vr.FINAL_ANALYSIS_DIR / "validation_cycle2" / "state_parity.csv"
SAME_CHECKPOINT_STEP_INSPECTION = vr.FINAL_ANALYSIS_DIR / "validation_cycle2" / "step_text_inspection.json"
EXPECTED_ORIGINAL_COUNT = 64
GEOMETRY_VOLUME_TOLERANCE_MM3 = 1.0e-5
TRANSFORM_TOLERANCE = 1.0e-8
LOCAL_METRIC_TOLERANCE_MM = 1.0e-8
STABLE_PART_FIELDS = ("revision", "description", "material", "make_buy")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(rows[0]) if rows else ["mismatch_id"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_cell(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def normalize_output_line_endings(out_dir: Path) -> None:
    """Keep committed machine evidence byte-stable across Windows/Linux runs."""
    for path in out_dir.iterdir():
        if path.is_file() and path.suffix.lower() in {".csv", ".json", ".md"}:
            payload = path.read_bytes()
            normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            if normalized != payload:
                path.write_bytes(normalized)


def centroid_mm(shape: Any) -> list[float]:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    point = props.CentreOfMass()
    return [float(point.X()), float(point.Y()), float(point.Z())]


def bbox_dimensions(box: list[float] | tuple[float, ...]) -> list[float]:
    return [float(box[3] - box[0]), float(box[4] - box[1]), float(box[5] - box[2])]


def max_vector_delta(a: list[float], b: list[float]) -> float:
    return max(abs(float(left) - float(right)) for left, right in zip(a, b))


def shape_metrics(shape: Any) -> dict[str, Any]:
    box = list(vr.bbox_raw(shape))
    topology = {
        "solid_count": vr.count_explorer(shape, TopAbs_SOLID),
        "shell_count": vr.count_explorer(shape, TopAbs_SHELL),
        "face_count": vr.count_explorer(shape, TopAbs_FACE),
        "wire_count": vr.count_explorer(shape, TopAbs_WIRE),
        "edge_count": vr.count_explorer(shape, TopAbs_EDGE),
        "vertex_count": vr.count_explorer(shape, TopAbs_VERTEX),
    }
    return {
        "valid_brep": bool(BRepCheck_Analyzer(shape).IsValid()),
        "volume_mm3": vr.volume_raw(shape),
        "centroid_mm": centroid_mm(shape),
        "bbox_mm": vr.bbox_dict(tuple(box)),
        "bbox_dimensions_mm": bbox_dimensions(box),
        "topology_counts": topology,
        "surface_type_counts": vr.surface_counts(shape),
    }


def rotation_and_translation(matrix: list[list[float]]) -> dict[str, Any]:
    return {
        "rotation_matrix": [[float(matrix[i][j]) for j in range(3)] for i in range(3)],
        "translation_vector_mm": [float(matrix[i][3]) for i in range(3)],
    }


def orientation_delta(stowed: list[list[float]], deployed: list[list[float]]) -> dict[str, Any]:
    rs = [[float(stowed[i][j]) for j in range(3)] for i in range(3)]
    rd = [[float(deployed[i][j]) for j in range(3)] for i in range(3)]
    relative = [
        [sum(rd[i][k] * rs[j][k] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]
    cosine = max(-1.0, min(1.0, (sum(relative[i][i] for i in range(3)) - 1.0) / 2.0))
    angle = math.acos(cosine)
    if abs(angle) <= 1.0e-12:
        axis = None
    else:
        sine = math.sin(angle)
        if abs(sine) <= 1.0e-12:
            axis = None
        else:
            axis = [
                (relative[2][1] - relative[1][2]) / (2.0 * sine),
                (relative[0][2] - relative[2][0]) / (2.0 * sine),
                (relative[1][0] - relative[0][1]) / (2.0 * sine),
            ]
    st = [float(stowed[i][3]) for i in range(3)]
    dt = [float(deployed[i][3]) for i in range(3)]
    translation_delta = [dt[i] - st[i] for i in range(3)]
    return {
        "relative_rotation_matrix": relative,
        "rotation_angle_deg": math.degrees(angle),
        "rotation_axis": axis,
        "translation_delta_mm": translation_delta,
        "translation_delta_norm_mm": math.sqrt(sum(value * value for value in translation_delta)),
    }


def relative_parent_path(row: dict[str, Any], inventory: dict[str, Any]) -> str:
    root = str(inventory.get("assembly_hierarchy", {}).get("root_name", ""))
    return vr._relative_assembly_path(row.get("parent_path", ""), root)


def index_unique(rows: list[dict[str, Any]], key: str) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    counts = Counter(str(row.get(key, "")).strip() for row in rows)
    result = {
        str(row.get(key, "")).strip(): row
        for row in rows
        if str(row.get(key, "")).strip() and counts[str(row.get(key, "")).strip()] == 1
    }
    return result, counts


def attachment_evidence(inventory: dict[str, Any], occurrence_id: str) -> dict[str, Any]:
    mate_ids: set[str] = set()
    connection_ids: list[str] = []
    attachment_ids: list[str] = []
    state_specific_records: list[dict[str, Any]] = []
    for collection_name in ("connections", "attachment_requirements"):
        for record in inventory.get(collection_name, []):
            pairs: list[tuple[str, str]] = []
            for left_key, right_key in (
                ("occurrence_id", "mate_occurrence_id"),
                ("occurrence_a", "occurrence_b"),
            ):
                left = str(record.get(left_key, "")).strip()
                right = str(record.get(right_key, "")).strip()
                if left and right:
                    pairs.append((left, right))
            related = False
            for left, right in pairs:
                if left == occurrence_id:
                    mate_ids.add(right)
                    related = True
                elif right == occurrence_id:
                    mate_ids.add(left)
                    related = True
            if not related:
                continue
            if collection_name == "connections":
                connection_ids.append(str(record.get("connection_id", "")))
            else:
                attachment_ids.append(str(record.get("attachment_id", "")))
            state_specific_records.append({
                "source": collection_name,
                "record_id": str(record.get("connection_id", record.get("attachment_id", ""))),
                "state": str(record.get("state", "")),
                "type": str(record.get("connection_type", record.get("attachment_type", ""))),
                "mating_occurrence_ids": sorted(
                    {mate for pair in pairs for mate in pair if mate != occurrence_id}
                ),
            })
    return {
        "mating_occurrence_ids": sorted(mate_ids),
        "connection_ids": sorted(value for value in connection_ids if value),
        "attachment_ids": sorted(value for value in attachment_ids if value),
        "records": sorted(state_specific_records, key=lambda row: (row["source"], row["record_id"])),
    }


def motion_track_evidence(inventory: dict[str, Any], occurrence_id: str) -> dict[str, Any]:
    tracks = [
        track for track in inventory.get("motion_tracks", [])
        if str(track.get("occurrence_id", "")).strip() == occurrence_id
    ]
    cooked = []
    for track in tracks:
        samples = track.get("samples", [])
        by_angle = {
            int(sample["angle_deg"]): sample.get("transform_matrix_3x4")
            for sample in samples
            if isinstance(sample, dict) and "angle_deg" in sample
        }
        cooked.append({
            "mode": str(track.get("mode", "")),
            "process_basis": str(track.get("process_basis", "")),
            "stationary_during_arm_sweep": track.get("stationary_during_arm_sweep"),
            "sample_count": len(samples),
            "angle_0_transform": by_angle.get(0),
            "angle_80_transform": by_angle.get(80),
        })
    return {"declared": bool(cooked), "tracks": cooked}


def part_record_map(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(part.get("part_number", "")).strip(): part
        for part in inventory.get("parts", [])
        if str(part.get("part_number", "")).strip()
    }


def max_optional(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=DEFAULT_ORIGINAL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--expected-original-count", type=int, default=EXPECTED_ORIGINAL_COUNT)
    args = parser.parse_args(argv)

    original_path = args.original.resolve()
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not original_path.is_file():
        parser.error(f"original mismatch register is missing: {original_path}")

    original_all = read_csv(original_path)
    original_rows = [row for row in original_all if str(row.get("status", "")).upper() == "FAIL"]
    original_ids = [str(row.get("occurrence_id", "")).strip() for row in original_rows]
    if len(original_rows) != args.expected_original_count:
        parser.error(
            f"original mismatch population drifted: expected={args.expected_original_count}, "
            f"actual={len(original_rows)}"
        )
    if not all(original_ids) or len(original_ids) != len(set(original_ids)):
        parser.error("original mismatch IDs must be nonblank and unique")

    if not SAME_CHECKPOINT_PRIOR_PARITY.is_file() or not SAME_CHECKPOINT_STEP_INSPECTION.is_file():
        parser.error("same-checkpoint validation_cycle2 parity provenance is missing")
    same_checkpoint_prior_rows = {
        row["occurrence_id"]: row for row in read_csv(SAME_CHECKPOINT_PRIOR_PARITY)
    }
    if not all(occurrence_id in same_checkpoint_prior_rows for occurrence_id in original_ids):
        parser.error("same-checkpoint parity evidence does not cover the original mismatch population")

    inventories = {
        state: json.loads(path.read_text(encoding="utf-8"))
        for state, path in vr.INVENTORIES.items()
    }
    manifest = json.loads(vr.AUTHORING_MANIFEST.read_text(encoding="utf-8"))
    vr.validate_authoring_manifest(manifest)
    same_checkpoint_step = json.loads(
        SAME_CHECKPOINT_STEP_INSPECTION.read_text(encoding="utf-8")
    )
    for state in ("STOWED", "DEPLOYED"):
        if same_checkpoint_step.get(state, {}).get("sha256") != vr.sha256(vr.FILES[state]):
            parser.error(
                f"validation_cycle2 {state} STEP hash does not bind the current master"
            )

    endpoints = {}
    for state in ("STOWED", "DEPLOYED"):
        print(f"[{state}] clean XCAF endpoint reimport", flush=True)
        endpoints[state] = vr.load_endpoint(state, vr.FILES[state], inventories[state])
        vr.write_occurrence_csv(
            out_dir / f"xcaf_occurrences_{state.lower()}.csv",
            endpoints[state].occurrence_rows,
        )

    print("[PARITY] corrected local-geometry and occurrence-aware validator", flush=True)
    current_parity = vr.state_parity(
        endpoints["STOWED"], endpoints["DEPLOYED"], inventories, out_dir
    )
    current_rows = {row["occurrence_id"]: row for row in read_csv(out_dir / "state_parity.csv")}

    inventory_occurrences = {}
    inventory_occurrence_counts = {}
    imported_leaves = {}
    imported_occurrence_counts = {}
    part_maps = {state: part_record_map(inventories[state]) for state in inventories}
    part_counts = {}
    for state in ("STOWED", "DEPLOYED"):
        inventory_occurrences[state], inventory_occurrence_counts[state] = index_unique(
            inventories[state].get("occurrences", []), "occurrence_id"
        )
        leaves = [row for row in endpoints[state].occurrence_rows if row.get("has_shape")]
        imported_leaves[state], imported_occurrence_counts[state] = index_unique(
            leaves, "occurrence_id"
        )
        part_counts[state] = Counter(
            str(row.get("part_number", "")).strip()
            for row in inventories[state].get("occurrences", [])
        )

    register: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    for index, original in enumerate(original_rows, start=1):
        occurrence_id = str(original["occurrence_id"]).strip()
        mismatch_id = f"SPP-{index:03d}"
        so = inventory_occurrences["STOWED"].get(occurrence_id, {})
        do = inventory_occurrences["DEPLOYED"].get(occurrence_id, {})
        si = imported_leaves["STOWED"].get(occurrence_id, {})
        di = imported_leaves["DEPLOYED"].get(occurrence_id, {})
        current = current_rows.get(occurrence_id, {})
        same_checkpoint_prior = same_checkpoint_prior_rows[occurrence_id]

        stowed_part_number = str(so.get("part_number", ""))
        deployed_part_number = str(do.get("part_number", ""))
        sp = part_maps["STOWED"].get(stowed_part_number, {})
        dp = part_maps["DEPLOYED"].get(deployed_part_number, {})
        classification = str(so.get("classification", "")).strip().upper()

        stowed_local_shape = endpoints["STOWED"].local_shapes[occurrence_id].wrapped if si else None
        deployed_local_shape = endpoints["DEPLOYED"].local_shapes[occurrence_id].wrapped if di else None
        sm = shape_metrics(stowed_local_shape) if stowed_local_shape is not None else None
        dm = shape_metrics(deployed_local_shape) if deployed_local_shape is not None else None
        bbox_delta = None if not sm or not dm else max_vector_delta(
            list(sm["bbox_mm"].values()), list(dm["bbox_mm"].values())
        )
        bbox_dimensions_delta = None if not sm or not dm else max_vector_delta(
            sm["bbox_dimensions_mm"], dm["bbox_dimensions_mm"]
        )
        centroid_delta = None if not sm or not dm else max_vector_delta(
            sm["centroid_mm"], dm["centroid_mm"]
        )
        topology_match = bool(sm and dm and sm["topology_counts"] == dm["topology_counts"])
        surface_match = bool(sm and dm and sm["surface_type_counts"] == dm["surface_type_counts"])
        # The audit population is defined by an earlier digest mismatch.  Force
        # the exact boolean proof even if a later OCCT serialization happens to
        # produce equal bytes; that run-to-run change is itself hash-instability
        # evidence and must never be allowed to substitute for geometry proof.
        exact_common_evidence = (
            vr.exact_common_full_volume_equivalence(
                stowed_local_shape,
                deployed_local_shape,
                volume_tolerance_mm3=GEOMETRY_VOLUME_TOLERANCE_MM3,
            )
            if stowed_local_shape is not None and deployed_local_shape is not None
            else None
        )
        exact_geometry_equivalent = bool(
            exact_common_evidence and exact_common_evidence["equivalent"]
        )

        stowed_matrix = so.get("transform_matrix_3x4")
        deployed_matrix = do.get("transform_matrix_3x4")
        transform_delta = None
        stowed_authority_error = None
        deployed_authority_error = None
        orientation = None
        if stowed_matrix and deployed_matrix:
            transform_delta = vr.matrix_max_abs_delta(stowed_matrix, deployed_matrix)
            orientation = orientation_delta(stowed_matrix, deployed_matrix)
        if si and stowed_matrix:
            stowed_authority_error = vr.matrix_max_abs_delta(
                si.get("absolute_transform_3x4"), stowed_matrix
            )
        if di and deployed_matrix:
            deployed_authority_error = vr.matrix_max_abs_delta(
                di.get("absolute_transform_3x4"), deployed_matrix
            )
        transform_authority_match = bool(
            stowed_authority_error is not None and stowed_authority_error <= TRANSFORM_TOLERANCE
            and deployed_authority_error is not None and deployed_authority_error <= TRANSFORM_TOLERANCE
        )
        state_transform_changed = bool(
            transform_delta is not None and transform_delta > TRANSFORM_TOLERANCE
        )

        stowed_attachment = attachment_evidence(inventories["STOWED"], occurrence_id)
        deployed_attachment = attachment_evidence(inventories["DEPLOYED"], occurrence_id)
        attachment_changed = (
            stowed_attachment["mating_occurrence_ids"]
            != deployed_attachment["mating_occurrence_ids"]
        )
        motion_track = motion_track_evidence(inventories["STOWED"], occurrence_id)

        c_reasons: list[str] = []
        if inventory_occurrence_counts["STOWED"][occurrence_id] != 1 or inventory_occurrence_counts["DEPLOYED"][occurrence_id] != 1:
            c_reasons.append("AUTHORING_OCCURRENCE_COUNT_NOT_ONE_PER_STATE")
        if imported_occurrence_counts["STOWED"][occurrence_id] != 1 or imported_occurrence_counts["DEPLOYED"][occurrence_id] != 1:
            c_reasons.append("XCAF_OCCURRENCE_COUNT_NOT_ONE_PER_STATE")
        if not si or not di:
            c_reasons.append("MISSING_XCAF_OCCURRENCE")
        if not (stowed_part_number and stowed_part_number == deployed_part_number):
            c_reasons.append("PART_NUMBER_SUBSTITUTION")
        if not (sp and dp and all(sp.get(field) == dp.get(field) for field in STABLE_PART_FIELDS)):
            c_reasons.append("PART_DEFINITION_MUTATION")
        if so.get("parent_path") != do.get("parent_path"):
            c_reasons.append("PARENT_ASSEMBLY_CHANGED")
        if si and relative_parent_path(si, inventories["STOWED"]) != so.get("parent_path"):
            c_reasons.append("STOWED_XCAF_PARENT_PATH_MISMATCH")
        if di and relative_parent_path(di, inventories["DEPLOYED"]) != do.get("parent_path"):
            c_reasons.append("DEPLOYED_XCAF_PARENT_PATH_MISMATCH")
        if stowed_part_number and part_counts["STOWED"][stowed_part_number] != part_counts["DEPLOYED"][deployed_part_number]:
            c_reasons.append("PART_OCCURRENCE_QUANTITY_CHANGED")
        if si and di and si.get("name") != di.get("name"):
            c_reasons.append("XCAF_PRODUCT_IDENTITY_CHANGED")
        if not exact_geometry_equivalent:
            c_reasons.append("UNAUTHORIZED_LOCAL_GEOMETRY_MUTATION")
        if not transform_authority_match:
            c_reasons.append("XCAF_TRANSFORM_DOES_NOT_MATCH_AUTHORITATIVE_OCCURRENCE")
        if classification == "FIXED" and state_transform_changed:
            c_reasons.append("FIXED_OCCURRENCE_TRANSFORM_CHANGED")
        if classification == "FIXED" and attachment_changed:
            c_reasons.append("FIXED_OCCURRENCE_ATTACHMENT_CHANGED")
        if classification == "MOVING" and state_transform_changed and not motion_track["declared"]:
            c_reasons.append("MOVING_TRANSFORM_HAS_NO_DECLARED_MECHANISM_TRACK")
        if str(current.get("status", "")).upper() != "PASS":
            c_reasons.append("CORRECTED_VALIDATOR_ROW_UNRESOLVED")

        if c_reasons:
            final_classification = "C"
            root_cause = ";".join(c_reasons)
            corrective_action = (
                "CORRECT_SOURCE FEATURE BEFORE REBUILD; inspect authoring inventory occurrence "
                f"{occurrence_id} and its work/r2_source/build_r2.py generator"
            )
            final_disposition = "OPEN_REAL_CAD_OR_ASSEMBLY_INCONSISTENCY"
        elif classification == "MOVING" and (state_transform_changed or attachment_changed):
            final_classification = "B"
            root_cause = (
                "EXPECTED_CONFIGURATION_TRANSFORM_OR_ATTACHMENT_CHANGE_WITH_"
                "NON_SEMANTIC_OCCT_BREP_SERIALIZATION_DIFFERENCE"
            )
            corrective_action = "NO_CAD CHANGE; retain mechanism transform and use local geometric equivalence"
            final_disposition = "RESOLVED_AS_EXPECTED_STATE_SPECIFIC_DIFFERENCE"
        else:
            final_classification = "A"
            root_cause = "NON_SEMANTIC_OCCT_BREP_SERIALIZATION_HASH_INSTABILITY"
            corrective_action = "NO CAD CHANGE; use exact local common-volume equivalence after stable identity checks"
            final_disposition = "RESOLVED_AS_BENIGN_PROVENANCE_HASH_INSTABILITY"
        category_counts[final_classification] += 1

        expected_behavior = (
            "Remain fixed; local geometry, parent, part definition, quantity, attachment, and global transform must remain invariant."
            if classification == "FIXED"
            else (
                f"State-specific placement/attachment permitted by {so.get('joint_type', '')}; "
                f"DOF={so.get('permitted_dof', '')}; mechanism track declared={motion_track['declared']}."
            )
        )
        common_volume = None if exact_common_evidence is None else exact_common_evidence["common_volume_mm3"]
        stowed_minus_common = None if exact_common_evidence is None else exact_common_evidence["a_minus_common_mm3"]
        deployed_minus_common = None if exact_common_evidence is None else exact_common_evidence["b_minus_common_mm3"]

        record = {
            "mismatch_id": mismatch_id,
            "stowed_occurrence_id": occurrence_id if si else None,
            "deployed_occurrence_id": occurrence_id if di else None,
            "part_number": stowed_part_number or deployed_part_number,
            "part_title": sp.get("description", dp.get("description", "")),
            "revision": sp.get("revision", dp.get("revision", "")),
            "subsystem": str(so.get("parent_path", do.get("parent_path", ""))).split("/")[0],
            "material": sp.get("material", dp.get("material", "")),
            "make_buy_status": sp.get("make_buy", dp.get("make_buy", "")),
            "mass_kg": sp.get("mass_kg", dp.get("mass_kg")),
            "classification_source": classification,
            "stowed_parent_assembly": so.get("parent_path"),
            "deployed_parent_assembly": do.get("parent_path"),
            "stowed_assembly_path": si.get("path"),
            "deployed_assembly_path": di.get("path"),
            "product_id": stowed_part_number or deployed_part_number,
            "stowed_xcaf_product_identity": si.get("name"),
            "deployed_xcaf_product_identity": di.get("name"),
            "occurrence_count_comparison": {
                "stowed_authoring_occurrence_id_count": inventory_occurrence_counts["STOWED"][occurrence_id],
                "deployed_authoring_occurrence_id_count": inventory_occurrence_counts["DEPLOYED"][occurrence_id],
                "stowed_xcaf_occurrence_id_count": imported_occurrence_counts["STOWED"][occurrence_id],
                "deployed_xcaf_occurrence_id_count": imported_occurrence_counts["DEPLOYED"][occurrence_id],
                "stowed_part_number_occurrence_count": part_counts["STOWED"][stowed_part_number],
                "deployed_part_number_occurrence_count": part_counts["DEPLOYED"][deployed_part_number],
            },
            "stowed_local_coordinate_system": {
                "basis": "XCAF product-definition local coordinates",
                "centroid_mm": None if not sm else sm["centroid_mm"],
                "bbox_mm": None if not sm else sm["bbox_mm"],
            },
            "deployed_local_coordinate_system": {
                "basis": "XCAF product-definition local coordinates",
                "centroid_mm": None if not dm else dm["centroid_mm"],
                "bbox_mm": None if not dm else dm["bbox_mm"],
            },
            "stowed_local_transform": si.get("local_transform_3x4"),
            "deployed_local_transform": di.get("local_transform_3x4"),
            "stowed_transform": stowed_matrix,
            "deployed_transform": deployed_matrix,
            "stowed_rotation_translation": None if not stowed_matrix else rotation_and_translation(stowed_matrix),
            "deployed_rotation_translation": None if not deployed_matrix else rotation_and_translation(deployed_matrix),
            "orientation_comparison": orientation,
            "transform_comparison": {
                "state_transform_max_abs_delta": transform_delta,
                "state_transform_changed": state_transform_changed,
                "stowed_xcaf_to_authority_max_abs_error": stowed_authority_error,
                "deployed_xcaf_to_authority_max_abs_error": deployed_authority_error,
                "authority_tolerance": TRANSFORM_TOLERANCE,
                "authoritative_endpoint_transforms_match_xcaf": transform_authority_match,
            },
            "geometry_equivalence_result": {
                "equivalent": exact_geometry_equivalent,
                "basis": "EXACT_COMMON_FULL_VOLUME",
                "exact_common_status": None if exact_common_evidence is None else exact_common_evidence["status"],
                "exact_common_volume_mm3": common_volume,
                "stowed_minus_common_mm3": stowed_minus_common,
                "deployed_minus_common_mm3": deployed_minus_common,
                "symmetric_difference_volume_mm3": None if stowed_minus_common is None or deployed_minus_common is None else abs(stowed_minus_common) + abs(deployed_minus_common),
                "volume_tolerance_mm3": GEOMETRY_VOLUME_TOLERANCE_MM3,
                "current_run_serialized_hashes_equal": str(current.get("serialized_local_brep_match", "")).lower() == "true",
                "current_validator_geometry_basis": current.get("geometry_equivalence_basis"),
                "exact_common_error": None if exact_common_evidence is None else exact_common_evidence["error"],
            },
            "bounding_box_comparison": {
                "stowed_bbox_mm": None if not sm else sm["bbox_mm"],
                "deployed_bbox_mm": None if not dm else dm["bbox_mm"],
                "stowed_dimensions_mm": None if not sm else sm["bbox_dimensions_mm"],
                "deployed_dimensions_mm": None if not dm else dm["bbox_dimensions_mm"],
                "max_coordinate_delta_mm": bbox_delta,
                "max_dimension_delta_mm": bbox_dimensions_delta,
                "tolerance_mm": LOCAL_METRIC_TOLERANCE_MM,
                "match": bbox_delta is not None and bbox_delta <= LOCAL_METRIC_TOLERANCE_MM,
            },
            "volume_comparison": {
                "stowed_volume_mm3": None if not sm else sm["volume_mm3"],
                "deployed_volume_mm3": None if not dm else dm["volume_mm3"],
                "delta_mm3": None if not sm or not dm else dm["volume_mm3"] - sm["volume_mm3"],
                "centroid_max_abs_delta_mm": centroid_delta,
                "tolerance_mm3": GEOMETRY_VOLUME_TOLERANCE_MM3,
            },
            "topology_surface_comparison": {
                "stowed_valid_brep": None if not sm else sm["valid_brep"],
                "deployed_valid_brep": None if not dm else dm["valid_brep"],
                "stowed_topology_counts": None if not sm else sm["topology_counts"],
                "deployed_topology_counts": None if not dm else dm["topology_counts"],
                "topology_counts_match": topology_match,
                "stowed_surface_type_counts": None if not sm else sm["surface_type_counts"],
                "deployed_surface_type_counts": None if not dm else dm["surface_type_counts"],
                "surface_type_counts_match": surface_match,
            },
            "attachment_relationship": {
                "stowed": stowed_attachment,
                "deployed": deployed_attachment,
                "mating_component_set_changed": attachment_changed,
            },
            "motion_track_evidence": motion_track,
            "expected_state_behavior": expected_behavior,
            "original_hash_digest_result": {
                "stowed_local_brep_sha256": original.get("stowed_local_brep_sha256"),
                "deployed_local_brep_sha256": original.get("deployed_local_brep_sha256"),
                "hashes_equal": original.get("stowed_local_brep_sha256") == original.get("deployed_local_brep_sha256"),
                "original_exact_local_brep_match": original.get("exact_local_brep_match"),
                "original_status": original.get("status"),
                "same_checkpoint_prior_reimport": {
                    "stowed_local_brep_sha256": same_checkpoint_prior.get("stowed_local_brep_sha256"),
                    "deployed_local_brep_sha256": same_checkpoint_prior.get("deployed_local_brep_sha256"),
                    "hashes_equal": same_checkpoint_prior.get("stowed_local_brep_sha256") == same_checkpoint_prior.get("deployed_local_brep_sha256"),
                    "exact_common_status": same_checkpoint_prior.get("exact_common_status"),
                    "exact_common_full_volume_equivalent": same_checkpoint_prior.get("exact_common_full_volume_equivalent"),
                    "status": same_checkpoint_prior.get("status"),
                    "master_hash_binding": "work/final_analysis/validation_cycle2/step_text_inspection.json",
                },
            },
            "corrected_validator_result": {
                "status": current.get("status"),
                "stable_part_definition_match": current.get("stable_part_definition_match"),
                "parent_assembly_path_match": current.get("parent_assembly_path_match"),
                "part_occurrence_quantity_match": current.get("part_occurrence_quantity_match"),
                "transform_authority_match": current.get("transform_authority_match"),
                "fixed_transform_stable": current.get("fixed_transform_stable"),
                "transform_state_behavior": current.get("transform_state_behavior"),
            },
            "final_classification": final_classification,
            "root_cause": root_cause,
            "corrective_action": corrective_action,
            "category_c_source_file_and_feature": None if final_classification != "C" else {
                "source_inventory_records": [
                    "work/final_analysis/authoring_inventory_stowed.json",
                    "work/final_analysis/authoring_inventory_deployed.json",
                ],
                "authoring_feature": f"work/r2_source/build_r2.py occurrence {occurrence_id}",
            },
            "final_disposition": final_disposition,
        }
        register.append(record)

    unresolved_ids = [
        row["stowed_occurrence_id"] or row["deployed_occurrence_id"]
        for row in register
        if row["final_classification"] == "C"
        or row["corrected_validator_result"]["status"] != "PASS"
    ]
    summary = {
        "source_checkpoint_git_sha": "fcca6642077cf9a420e703c3f7d53b8913501f5a",
        "original_mismatch_count": len(original_rows),
        "original_serialized_hash_mismatch_count": sum(
            not row["original_hash_digest_result"]["hashes_equal"] for row in register
        ),
        "same_checkpoint_prior_reimport_hash_mismatch_count": sum(
            not row["original_hash_digest_result"]["same_checkpoint_prior_reimport"]["hashes_equal"]
            for row in register
        ),
        "same_checkpoint_prior_exact_common_equivalent_count": sum(
            str(row["original_hash_digest_result"]["same_checkpoint_prior_reimport"]["exact_common_full_volume_equivalent"]).lower() == "true"
            for row in register
        ),
        "current_run_serialized_hash_match_count": sum(
            row["geometry_equivalence_result"]["current_run_serialized_hashes_equal"]
            for row in register
        ),
        "forced_exact_common_volume_equivalent_count": sum(
            row["geometry_equivalence_result"]["equivalent"] for row in register
        ),
        "category_a_count": category_counts["A"],
        "category_b_count": category_counts["B"],
        "category_c_count": category_counts["C"],
        "fixed_unchanged_transform_count": sum(
            row["classification_source"] == "FIXED"
            and not row["transform_comparison"]["state_transform_changed"]
            for row in register
        ),
        "moving_expected_transform_change_count": sum(
            row["classification_source"] == "MOVING"
            and row["transform_comparison"]["state_transform_changed"]
            for row in register
        ),
        "moving_mechanism_track_coverage_count": sum(
            row["classification_source"] == "MOVING"
            and row["motion_track_evidence"]["declared"]
            for row in register
        ),
        "expected_attachment_change_count": sum(
            row["attachment_relationship"]["mating_component_set_changed"]
            for row in register
        ),
        "classified_count": len(register),
        "reconciliation_complete": len(register) == len(original_rows),
        "current_validator_union_occurrence_count": current_parity["union_occurrence_count"],
        "current_validator_mismatch_count": current_parity["mismatch_count"],
        "current_validator_identity_issue_count": current_parity["imported_leaf_identity_issue_count"],
        "current_validator_hierarchy_issue_count": current_parity["hierarchy_issue_count"],
        "current_validator_overall_issue_count": current_parity["overall_issue_count"],
        "unresolved_mismatch_count": len(unresolved_ids),
        "unresolved_occurrence_ids": unresolved_ids,
        "actual_cad_geometry_defect_found": category_counts["C"] > 0,
        "cad_geometry_files_changed": [],
        "state_parity_provenance_gate_resolved": bool(
            len(register) == len(original_rows)
            and not unresolved_ids
            and current_parity["overall_issue_count"] == 0
        ),
        "root_cause_summary": (
            "The original validator treated byte-for-byte OCCT local-BREP serialization as exact geometry identity. "
            "For the same current AP242 master hashes, validation_cycle2 produced 64 differing state digests while "
            "proving exact common volume, and this fresh reimport produced 64 matching state digests; therefore the "
            "digest is process-unstable and non-semantic. Fixed rows are invariant; moving rows carry authoritative "
            "expected endpoint transform or attachment changes."
        ),
        "validator_correction": {
            "source_file": "work/r2_source/validate_r2.py",
            "prior_correction_commit": "6c23e798c5442a02fadde9698eec63f2ed7ce50f",
            "geometry_policy": "stable occurrence/part/path checks plus local exact common-volume equivalence",
            "transform_policy": "each XCAF endpoint transform must match its authoritative occurrence transform; fixed transforms must remain invariant",
        },
        "tolerances": {
            "exact_common_full_volume_mm3": GEOMETRY_VOLUME_TOLERANCE_MM3,
            "transform_matrix_max_abs_element": TRANSFORM_TOLERANCE,
            "local_metric_mm": LOCAL_METRIC_TOLERANCE_MM,
        },
        "input_evidence": {
            "original_mismatch_csv": {"path": original_path.relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(original_path)},
            "same_checkpoint_prior_parity": {"path": SAME_CHECKPOINT_PRIOR_PARITY.relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(SAME_CHECKPOINT_PRIOR_PARITY)},
            "same_checkpoint_step_hash_binding": {"path": SAME_CHECKPOINT_STEP_INSPECTION.relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(SAME_CHECKPOINT_STEP_INSPECTION)},
            "stowed_master": {"path": vr.FILES["STOWED"].relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(vr.FILES["STOWED"])},
            "deployed_master": {"path": vr.FILES["DEPLOYED"].relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(vr.FILES["DEPLOYED"])},
            "stowed_inventory": {"path": vr.INVENTORIES["STOWED"].relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(vr.INVENTORIES["STOWED"])},
            "deployed_inventory": {"path": vr.INVENTORIES["DEPLOYED"].relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(vr.INVENTORIES["DEPLOYED"])},
            "validator": {"path": Path(vr.__file__).relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(Path(vr.__file__))},
            "audit_program": {"path": Path(__file__).relative_to(vr.ROOT).as_posix(), "sha256": vr.sha256(Path(__file__))},
        },
        "scope_note": "This endpoint parity audit does not execute or satisfy the separate exact 0-80 degree motion-validation requirement.",
    }

    json_register = {"summary": summary, "mismatches": register}
    vr.dump_json(out_dir / "state_parity_provenance_register.json", json_register)
    csv_rows = []
    for row in register:
        csv_rows.append({
            "mismatch_id": row["mismatch_id"],
            "stowed_occurrence_id": row["stowed_occurrence_id"],
            "deployed_occurrence_id": row["deployed_occurrence_id"],
            "part_number": row["part_number"],
            "part_title": row["part_title"],
            "revision": row["revision"],
            "subsystem": row["subsystem"],
            "material": row["material"],
            "make_buy_status": row["make_buy_status"],
            "mass_kg": row["mass_kg"],
            "stowed_parent_assembly": row["stowed_parent_assembly"],
            "deployed_parent_assembly": row["deployed_parent_assembly"],
            "stowed_assembly_path": row["stowed_assembly_path"],
            "deployed_assembly_path": row["deployed_assembly_path"],
            "stowed_transform": json_cell(row["stowed_transform"]),
            "deployed_transform": json_cell(row["deployed_transform"]),
            "geometry_equivalence_result": json_cell(row["geometry_equivalence_result"]),
            "bounding_box_comparison": json_cell(row["bounding_box_comparison"]),
            "volume_comparison": json_cell(row["volume_comparison"]),
            "topology_surface_comparison": json_cell(row["topology_surface_comparison"]),
            "expected_state_behavior": row["expected_state_behavior"],
            "original_hash_digest_result": json_cell(row["original_hash_digest_result"]),
            "final_classification": row["final_classification"],
            "root_cause": row["root_cause"],
            "corrective_action": row["corrective_action"],
            "final_disposition": row["final_disposition"],
        })
    write_csv(out_dir / "state_parity_provenance_register.csv", csv_rows)
    vr.dump_json(out_dir / "state_parity_provenance_summary.json", summary)
    report = f"""# STINGRAY I5-S DF8 state-parity/provenance audit

- Original mismatches: {summary['original_mismatch_count']}
- Category A: {summary['category_a_count']}
- Category B: {summary['category_b_count']}
- Category C: {summary['category_c_count']}
- Same-master prior reimport hash mismatches: {summary['same_checkpoint_prior_reimport_hash_mismatch_count']}
- Fresh same-master reimport hash matches: {summary['current_run_serialized_hash_match_count']}
- Forced exact common-volume equivalents: {summary['forced_exact_common_volume_equivalent_count']}
- Fixed transforms unchanged: {summary['fixed_unchanged_transform_count']}
- Moving transforms expected and changed: {summary['moving_expected_transform_change_count']}
- Corrected validator unresolved: {summary['current_validator_overall_issue_count']}
- Gate resolved: {str(summary['state_parity_provenance_gate_resolved']).upper()}
- Actual CAD geometry defect found: {str(summary['actual_cad_geometry_defect_found']).upper()}

Root cause: {summary['root_cause_summary']}

No CAD geometry was changed. This audit does not replace the separate exact 0-80 degree motion audit.
"""
    (out_dir / "README.md").write_text(report, encoding="utf-8")
    normalize_output_line_endings(out_dir)

    print(json.dumps({
        "original": summary["original_mismatch_count"],
        "A": summary["category_a_count"],
        "B": summary["category_b_count"],
        "C": summary["category_c_count"],
        "unresolved": summary["unresolved_mismatch_count"],
        "gate_resolved": summary["state_parity_provenance_gate_resolved"],
    }, indent=2), flush=True)
    return 0 if summary["state_parity_provenance_gate_resolved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
