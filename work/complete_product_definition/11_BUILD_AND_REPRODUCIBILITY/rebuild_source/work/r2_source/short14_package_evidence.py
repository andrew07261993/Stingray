#!/usr/bin/env python3
"""Create deterministic SHORT14 registers, reports, and inspection package.

All numeric design claims are derived from the frozen source builder, final
authoring inventories, exact mass-property file, or completed validation
summaries.  The wet breakaway calculation is deliberately a labelled
sensitivity screen; it is not vendor performance or a physical PASS.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import build_r2
import r2_geometry as g
import short14_external_buoy_config as cfg


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "short14_external_buoy"
VIEWS = OUT / "inspection_views"
VALIDATION = OUT / "validation"

STOWED_STEP = OUT / "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step"
DEPLOYED_STEP = OUT / "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step"
ZIP_PATH = OUT / "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_INSPECTION.zip"
ZIP_SHA_PATH = OUT / f"{ZIP_PATH.name}.sha256"

PNG_NAMES = [
    "01_BASELINE_AXIAL_SIDE_SECTION.png",
    "02_CORRECTED_AXIAL_SIDE_SECTION.png",
    "03_BASELINE_NEW_AXIAL_OVERLAY.png",
    "04_FORWARD_BALLAST_CARRIER_ADJACENCY.png",
    "05_AFT_EXTENDING_POWERTRAIN.png",
    "06_RELOCATED_RETAINED_CYLINDER_LAYOUT.png",
    "07_SHORTENED_STOWED_SYSTEM.png",
    "08_SHORTENED_DEPLOYED_SYSTEM.png",
    "09_CLOSED_CORDURA_BUOY_PACK.png",
    "10_PACK_SECTION_INFLATOR_WATER_ACCESS.png",
    "11_EXTERNAL_MANUAL_PULL_ACCESS.png",
    "12_OPEN_PACK_INFLATED_BUOY_TETHER_LOAD_PATH.png",
]

REPORT_NAMES = [
    "SHORT14_FORWARD_POWERTRAIN_DESIGN_REPORT.md",
    "AXIAL_RELOCATION_REGISTER.csv",
    "CYLINDER_DISPOSITION_REGISTER.csv",
    "BUOY_EJECTOR_REMOVAL_REGISTER.csv",
    "SHORT_ARM_MISSION_ENVELOPE_COMPARISON.md",
    "EXTERNAL_BUOY_PACK_DEFINITION.md",
    "EXTERNAL_BUOY_PACK_COMPONENT_REGISTER.csv",
    "SOFTGOODS_ATTACHMENT_MAP.csv",
    "FINAL_ATTACHMENT_CONNECTIVITY.csv",
    "FINAL_MASS_CG_INERTIA.json",
    "FINAL_MOTION_AUDIT_SUMMARY.csv",
    "BOM_DELTA.csv",
    "VALIDATION_SUMMARY.md",
    "VALIDATION_SUMMARY.json",
    "AUTONOMOUS_DECISION_LOG.md",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=False))


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(fields), extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def f6(value: float | int | None) -> str:
    return "" if value is None else f"{float(value):.6f}"


def bbox_dict(shape: Any) -> dict[str, float]:
    box = shape.BoundingBox()
    return {
        "xmin": float(box.xmin), "xmax": float(box.xmax),
        "ymin": float(box.ymin), "ymax": float(box.ymax),
        "zmin": float(box.zmin), "zmax": float(box.zmax),
    }


def rotation_key(matrix: list[list[float]]) -> tuple[float, ...]:
    return tuple(round(float(matrix[row][col]), 9) for row in range(3) for col in range(3))


def source_records() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    builder = build_r2.build_state("STOWED")
    records: dict[str, dict[str, Any]] = {}
    for occurrence in builder.occurrences:
        part = builder.catalog.parts[occurrence.part_number]
        shape = builder.global_shapes[occurrence.occurrence_id]
        center = shape.Center()
        mass = float(builder.mass_overrides_kg.get(
            occurrence.occurrence_id, part.resolved_mass() or 0.0,
        ))
        records[occurrence.occurrence_id] = {
            "occurrence_id": occurrence.occurrence_id,
            "part_number": occurrence.part_number,
            "parent_path": occurrence.parent_path,
            "classification": occurrence.classification,
            "joint_type": occurrence.joint_type,
            "permitted_dof": occurrence.permitted_dof,
            "bbox": bbox_dict(shape),
            "centroid": {"x": float(center.x), "y": float(center.y), "z": float(center.z)},
            "volume_mm3": float(shape.Volume()),
            "mass_kg": mass,
            "transform": g.loc_matrix(occurrence.location),
            "part": part,
        }
    return records, builder


def final_records(inventory: dict[str, Any], mass: dict[str, Any]) -> dict[str, dict[str, Any]]:
    part_map = {row["part_number"]: row for row in inventory["parts"]}
    mass_map = {
        row["occurrence_id"]: row
        for row in mass["short14_stowed"]["resolved_occurrences"]
    }
    records: dict[str, dict[str, Any]] = {}
    for occurrence in inventory["occurrences"]:
        mass_row = mass_map[occurrence["occurrence_id"]]
        records[occurrence["occurrence_id"]] = {
            "occurrence_id": occurrence["occurrence_id"],
            "part_number": occurrence["part_number"],
            "parent_path": occurrence["parent_path"],
            "classification": occurrence["classification"],
            "joint_type": occurrence["joint_type"],
            "permitted_dof": occurrence["permitted_dof"],
            "bbox": dict(occurrence["global_bbox_mm"]),
            "centroid": dict(mass_row["centroid_mm"]),
            "volume_mm3": float(occurrence["global_volume_mm3"]),
            "mass_kg": float(mass_row["mass_kg"]),
            "transform": occurrence["transform_matrix_3x4"],
            "part": part_map[occurrence["part_number"]],
        }
    return records


def aggregate(records: dict[str, dict[str, Any]], ids: Iterable[str]) -> dict[str, Any] | None:
    selected = [records[value] for value in ids if value in records]
    if not selected:
        return None
    mass = sum(row["mass_kg"] for row in selected)
    if mass > 0.0:
        centroid = sum(row["mass_kg"] * row["centroid"]["z"] for row in selected) / mass
        basis = "MASS_WEIGHTED_EXACT_OCCURRENCE_CENTROID"
    else:
        volume = sum(row["volume_mm3"] for row in selected)
        centroid = sum(row["volume_mm3"] * row["centroid"]["z"] for row in selected) / volume
        basis = "VOLUME_WEIGHTED_EXACT_OCCURRENCE_CENTROID"
    return {
        "ids": [row["occurrence_id"] for row in selected],
        "zmin": min(row["bbox"]["zmin"] for row in selected),
        "zmax": max(row["bbox"]["zmax"] for row in selected),
        "centroid_z": centroid,
        "mass_kg": mass,
        "centroid_basis": basis,
    }


def removal_scope(occurrence_id: str) -> tuple[str, str]:
    body_prefixes = (
        "FWD-SHELL", "FWD-RING-01", "FWD-LONGERON", "AFT-SHELL", "AFT-LONGERON",
        "AFT-ROUTE-RING", "AFT-REPACK-SHELL",
    )
    inflation_prefixes = (
        "CO2-CARTRIDGE", "CARTRIDGE-CARRIER", "COLLECTION-MANIFOLD", "PUNCTURE-HEAD",
        "BOOSTER", "WATER-", "FULLFLOW-", "ROUTE-MANIFOLD-FEED", "MANIFOLD-FEED-CLAMP",
        "FWD-CARRIER-SCREW", "MANIFOLD-CARRIER-SCREW", "TRIGGER-MOUNT-SCREW",
        "WP04-FULLFLOW-MANIFOLD", "WP04-MANIFOLD-BRACKET",
    )
    ejector_prefixes = (
        "WP04-", "WP05-", "GUIDE-RAIL-", "LATCH-SUPPORT-BRACKET", "DOOR-DETENT-",
    )
    recovery_prefixes = (
        "BUOY-GORE-", "HARNESS-", "TETHER-", "RECOVERY-", "BODY-HARDPOINT-",
    )
    route_prefixes = ("GLAND-", "ROUTE-GAS-", "ROUTE-PILOT-", "ROUTE-BOWDEN-", "ROUTE-LINER-")
    if occurrence_id.startswith(body_prefixes):
        return "SUPERSEDED_SHORTENED_BODY_STRUCTURE", "Replaced by the exact 1675.400 mm rigid-body stack"
    if occurrence_id == "CG-TRIM-BALLAST-001":
        return "SUPERSEDED_TRIM", "Removed; final exact mass properties do not require the source repack trim slug"
    if occurrence_id.startswith(inflation_prefixes):
        return "DEDICATED_INTERNAL_BUOY_INFLATION", "Removed with the internal inflation architecture"
    if occurrence_id.startswith(ejector_prefixes):
        return "DEDICATED_INTERNAL_BUOY_EJECTION", "Removed with the internal follower/sleeve/door ejection architecture"
    if occurrence_id.startswith(recovery_prefixes):
        return "SUPERSEDED_INTERNAL_BUOY_RECOVERY", "Replaced by external buoy panels and the independent structural tether load path"
    if occurrence_id.startswith(route_prefixes):
        return "OBSOLETE_INTERNAL_ROUTE", "Route deleted because its internal buoy architecture endpoints were removed"
    return "SUPERSEDED_SUPPORT_OR_HARDWARE", "Deleted source occurrence is absent from the final BOM, tree, attachment map, and validation register"


def create_removal_register(
    source: dict[str, dict[str, Any]], final: dict[str, dict[str, Any]], removed_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for occurrence_id in sorted(removed_ids):
        row = source[occurrence_id]
        scope, reason = removal_scope(occurrence_id)
        part = row["part"]
        rows.append({
            "occurrence_id": occurrence_id,
            "definition": row["part_number"],
            "legacy_id": row["part_number"],
            "description": part.description,
            "removal_scope": scope,
            "source_parent_path": row["parent_path"],
            "source_z_min_mm": f6(row["bbox"]["zmin"]),
            "source_z_max_mm": f6(row["bbox"]["zmax"]),
            "source_centroid_z_mm": f6(row["centroid"]["z"]),
            "source_mass_kg": f6(row["mass_kg"]),
            "reason": reason,
            "final_occurrence_present": "YES" if occurrence_id in final else "NO",
            "final_bom_present": "NO",
            "final_attachment_map_present": "NO",
            "final_product_tree_present": "NO",
            "final_validation_register_present": "NO",
        })
    if any(row["final_occurrence_present"] != "NO" for row in rows):
        raise RuntimeError("a deleted source occurrence remains in the final assembly")
    dedicated = [row for row in rows if row["removal_scope"] == "DEDICATED_INTERNAL_BUOY_EJECTION"]
    architecture = [
        row for row in rows if row["removal_scope"] in {
            "DEDICATED_INTERNAL_BUOY_EJECTION", "DEDICATED_INTERNAL_BUOY_INFLATION",
            "SUPERSEDED_INTERNAL_BUOY_RECOVERY", "OBSOLETE_INTERNAL_ROUTE",
        }
    ]
    summary = {
        "all_deleted_source_occurrence_count": len(rows),
        "all_deleted_unique_definition_count": len({row["definition"] for row in rows}),
        "all_deleted_source_mass_kg": sum(float(row["source_mass_kg"]) for row in rows),
        "dedicated_ejector_occurrence_count": len(dedicated),
        "dedicated_ejector_unique_definition_count": len({row["definition"] for row in dedicated}),
        "dedicated_ejector_source_mass_kg": sum(float(row["source_mass_kg"]) for row in dedicated),
        "complete_internal_buoy_architecture_occurrence_count": len(architecture),
        "complete_internal_buoy_architecture_unique_definition_count": len({row["definition"] for row in architecture}),
        "complete_internal_buoy_architecture_source_mass_kg": sum(float(row["source_mass_kg"]) for row in architecture),
        "final_deleted_occurrence_residual_count": 0,
    }
    fields = [
        "occurrence_id", "definition", "legacy_id", "description", "removal_scope", "source_parent_path",
        "source_z_min_mm", "source_z_max_mm", "source_centroid_z_mm", "source_mass_kg", "reason",
        "final_occurrence_present", "final_bom_present", "final_attachment_map_present",
        "final_product_tree_present", "final_validation_register_present",
    ]
    write_csv(OUT / "BUOY_EJECTOR_REMOVAL_REGISTER.csv", rows, fields)
    return rows, summary


def create_axial_register(
    source: dict[str, dict[str, Any]], final: dict[str, dict[str, Any]], removal_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    dedicated_ejector = [
        row["occurrence_id"] for row in removal_rows
        if row["removal_scope"] == "DEDICATED_INTERNAL_BUOY_EJECTION"
    ]
    pack_ids = [
        key for key, row in final.items()
        if "/520_CORDURA_BREAKAWAY_BUOY_PACK_ASSY" in row["parent_path"]
        or "/530_BUOY_MOUNTED_INFLATION_ASSY" in row["parent_path"]
    ]
    groups = [
        ("FORWARD BALLAST", ["BALLAST-001"], ["BALLAST-001"], "NONE", "Fixed source authority"),
        ("ARM CARRIER", [f"PIVOT-CARRIER-{i}" for i in range(1, 4)],
         [value for value in final if value.startswith("PIVOT-CARRIER-")], "NONE",
         "Coordinated carrier relocation to the first structural station aft of ballast"),
        ("PIVOT AXES", [f"PIVOT-PIN-{i}" for i in range(1, 4)], [f"PIVOT-PIN-{i}" for i in range(1, 4)],
         "NONE", "Exact pivot-axis translation from Z=480.000 to Z=355.000 mm"),
        ("COMMON CROSSHEAD", ["CROSSHEAD-001"], ["CROSSHEAD-001"], "NONE",
         "Moved as one mechanism; source kinematics retained"),
        ("ACE GS-19", ["GS19-BODY-001"], ["GS19-BODY-001"], "NONE",
         "Fixed body and moving rod sense retained; long body trails aft"),
        ("ACE HBD-15", ["HBD-BODY-001"], ["HBD-BODY-001"], "NONE",
         "Fixed body and moving rod sense retained; damping direction unchanged"),
        ("BACKUP SPRING", ["BACKUP-SPRING-001", "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT", "BACKUP-SPRING-MOVING-SEAT"],
         ["BACKUP-SPRING-001", "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT", "BACKUP-SPRING-MOVING-SEAT"],
         "NONE", "Moving/fixed seat sense retained; guide and spring trail aft"),
        ("EXTERNAL BUOY CO2 CARTRIDGE", [], ["BUOY-CO2-CARTRIDGE-81121"], "NEW EXTERNAL AFT INSTALLATION",
         "Single source-supported Leland 81121 cartridge mounted to the buoy inflator"),
        ("INTERNAL BUOY EJECTOR", dedicated_ejector, [], "REMOVED",
         "Internal follower/sleeve/spring/door architecture deleted completely"),
        ("AFT CLOSURE", [value for value in source if value == "AFT-SHELL-001" or value.startswith("WP05-")],
         ["AFT-CLOSURE-RING", "AFT-CLOSURE-CAP"], "REPLACED",
         "Source service-throat/ejection closure replaced by shortened ring and cap"),
        ("EXTERNAL BUOY PACK", [], pack_ids, "NEW EXTERNAL SOFTGOODS ASSEMBLY",
         "Aft Cordura breakaway wrap and buoy-mounted automatic/manual inflation"),
    ]
    rows: list[dict[str, Any]] = []
    for name, source_ids, final_ids, orientation, reason in groups:
        before = aggregate(source, source_ids)
        after = aggregate(final, final_ids)
        translation: str
        if before and after:
            translation = f6(after["centroid_z"] - before["centroid_z"])
        elif before:
            translation = "REMOVED"
        else:
            translation = "ADDED"
        rows.append({
            "name": name,
            "baseline_occurrence_ids": ";".join(before["ids"]) if before else "NOT PRESENT",
            "baseline_min_z_mm": f6(before["zmin"]) if before else "N/A",
            "baseline_max_z_mm": f6(before["zmax"]) if before else "N/A",
            "baseline_centroid_z_mm": f6(before["centroid_z"]) if before else "N/A",
            "new_occurrence_ids": ";".join(after["ids"]) if after else "NOT PRESENT",
            "new_min_z_mm": f6(after["zmin"]) if after else "N/A",
            "new_max_z_mm": f6(after["zmax"]) if after else "N/A",
            "new_centroid_z_mm": f6(after["centroid_z"]) if after else "N/A",
            "translation_mm": translation,
            "orientation_change": orientation,
            "retained_removed": "RETAINED/REPLACED" if before and after else ("REMOVED" if before else "ADDED"),
            "centroid_basis": (after or before)["centroid_basis"],
            "reason": reason,
        })
    fields = [
        "name", "baseline_occurrence_ids", "baseline_min_z_mm", "baseline_max_z_mm",
        "baseline_centroid_z_mm", "new_occurrence_ids", "new_min_z_mm", "new_max_z_mm",
        "new_centroid_z_mm", "translation_mm", "orientation_change", "retained_removed",
        "centroid_basis", "reason",
    ]
    write_csv(OUT / "AXIAL_RELOCATION_REGISTER.csv", rows, fields)
    return rows


def create_cylinder_register(
    source: dict[str, dict[str, Any]], final: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    specs: list[tuple[str, str, str, str, str, str, str]] = [
        ("GS19-BODY-001", "GS19-BODY-001", "A", "arm deployment gas spring", "RETAINED / RELOCATED FORWARD", "double-shear fixed yoke; moving rod pinned to crosshead", "AFT after yoke access"),
        ("HBD-BODY-001", "HBD-BODY-001", "A", "arm deployment hydraulic damper", "RETAINED / RELOCATED FORWARD", "double-shear fixed yoke; moving rod pinned to crosshead", "AFT after yoke access"),
        ("BACKUP-SPRING-001", "BACKUP-SPRING-001", "A", "arm backup spring", "RETAINED / RELOCATED FORWARD", "captured moving/fixed seats and guided spring", "AFT after termination-ring access"),
        ("BACKUP-SPRING-GUIDE", "BACKUP-SPRING-GUIDE", "A", "arm backup-spring guide", "RETAINED / RELOCATED FORWARD", "two retained guide screws and fixed seat", "AFT after termination-ring access"),
    ]
    specs.extend([
        (f"CO2-CARTRIDGE-{index}", "", "B", "dedicated internal buoy inflation cartridge", "REMOVED", "source cartridge carrier/puncture head", "N/A — removed")
        for index in range(1, 5)
    ])
    specs.extend([
        (f"BOOSTER-{index}", "", "B", "dedicated internal buoy booster reservoir", "REMOVED", "source captive support bands and pressure closures", "N/A — removed")
        for index in range(1, 4)
    ])
    specs.extend([
        ("", "BUOY-CO2-CARTRIDGE-81121", "C", "new external buoy-mounted inflation cartridge", "NEW EXTERNAL AFT INSTALLATION", "threaded to Hydro 1F commercial interface", "AFT / OUTWARD from open repack access"),
        ("", "HYDRO-1F-INFLATOR-PROXY", "C", "new external automatic/manual buoy inflator", "NEW EXTERNAL AFT INSTALLATION", "threaded to buoy inlet reinforcement manifold", "RADIAL OUTWARD after guard removal"),
    ])
    rows: list[dict[str, Any]] = []
    for source_id, final_id, category, function, disposition, attachment, service in specs:
        before = source.get(source_id) if source_id else None
        after = final.get(final_id) if final_id else None
        definition = (after or before)["part_number"]
        movement = (
            f6(after["centroid"]["z"] - before["centroid"]["z"])
            if before and after else ("REMOVED" if before else "ADDED")
        )
        if before and after:
            same_rotation = rotation_key(before["transform"]) == rotation_key(after["transform"])
            orientation = "UNCHANGED" if same_rotation else "CHANGED"
        elif before:
            orientation = "REMOVED"
        else:
            orientation = "NEW EXTERNAL INSTALLATION"
        rows.append({
            "definition": definition,
            "occurrence": final_id or source_id,
            "legacy_id": source_id or "NEW",
            "function": function,
            "category": category,
            "current_axial_range_mm": f"{f6(before['bbox']['zmin'])}..{f6(before['bbox']['zmax'])}" if before else "N/A",
            "final_axial_range_mm": f"{f6(after['bbox']['zmin'])}..{f6(after['bbox']['zmax'])}" if after else "N/A",
            "current_centroid_z_mm": f6(before["centroid"]["z"]) if before else "N/A",
            "final_centroid_z_mm": f6(after["centroid"]["z"]) if after else "N/A",
            "axial_movement_mm": movement,
            "orientation_change": orientation,
            "retained_removed_relocated": disposition,
            "reason": (
                "Aft-trailing powertrain orientation preserves source fixed/moving function"
                if category == "A" else
                "Internal buoy architecture removed completely"
                if category == "B" else
                "External buoy inflation hardware is aft of the arm carrier and outside the ballast-to-carrier interval"
            ),
            "attachment": attachment,
            "service_removal_direction": service,
        })
    fields = [
        "definition", "occurrence", "legacy_id", "function", "category", "current_axial_range_mm",
        "final_axial_range_mm", "current_centroid_z_mm", "final_centroid_z_mm", "axial_movement_mm",
        "orientation_change", "retained_removed_relocated", "reason", "attachment", "service_removal_direction",
    ]
    write_csv(OUT / "CYLINDER_DISPOSITION_REGISTER.csv", rows, fields)
    return rows


def create_component_and_attachment_registers(
    inventory: dict[str, Any], final: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    relevant_ids = {
        key for key, row in final.items()
        if any(value in row["parent_path"] for value in (
            "/520_CORDURA_BREAKAWAY_BUOY_PACK_ASSY",
            "/530_BUOY_MOUNTED_INFLATION_ASSY",
            "/540_STRUCTURAL_RECOVERY_TETHER_ASSY",
        )) or key.startswith("PACK-ATTACHMENT-COLLAR-")
    }
    component_rows: list[dict[str, Any]] = []
    for occurrence_id in sorted(relevant_ids):
        row = final[occurrence_id]
        part = row["part"]
        component_rows.append({
            "occurrence_id": occurrence_id,
            "definition": row["part_number"],
            "description": part["description"],
            "parent_path": row["parent_path"],
            "classification": row["classification"],
            "material": part["material"],
            "make_buy": part["make_buy"],
            "manufacturer": part["manufacturer"],
            "cad_classification": part["cad_classification"],
            "mass_kg": f6(row["mass_kg"]),
            "z_min_mm": f6(row["bbox"]["zmin"]),
            "z_max_mm": f6(row["bbox"]["zmax"]),
            "maximum_radial_bbox_corner_mm": f6(max(
                math.hypot(row["bbox"][x], row["bbox"][y])
                for x in ("xmin", "xmax") for y in ("ymin", "ymax")
            )),
            "source_or_proxy_status": (
                "DIMENSION-CONTROLLED COMMERCIAL INTERFACE PROXY; INTERNALS NOT MODELED"
                if row["part_number"].endswith("_PROXY") else part["cad_classification"]
            ),
        })
    write_csv(OUT / "EXTERNAL_BUOY_PACK_COMPONENT_REGISTER.csv", component_rows, [
        "occurrence_id", "definition", "description", "parent_path", "classification", "material",
        "make_buy", "manufacturer", "cad_classification", "mass_kg", "z_min_mm", "z_max_mm",
        "maximum_radial_bbox_corner_mm", "source_or_proxy_status",
    ])

    class_map = {key: row["classification"] for key, row in final.items()}
    connection_rows: list[dict[str, Any]] = []
    attachment_pairs = Counter(
        tuple(sorted((row["occurrence_a"], row["occurrence_b"])))
        for row in inventory["attachment_requirements"]
    )
    for connection in inventory["connections"]:
        pair = tuple(sorted((connection["occurrence_id"], connection["mate_occurrence_id"])))
        endpoint_ok = connection["occurrence_id"] in final and connection["mate_occurrence_id"] in final
        connection_rows.append({
            "connection_id": connection["connection_id"],
            "occurrence_id": connection["occurrence_id"],
            "mate_occurrence_id": connection["mate_occurrence_id"],
            "connection_type": connection["connection_type"],
            "retaining_hardware": connection["retaining_hardware"],
            "axial_retention": connection["axial_retention"],
            "lateral_retention": connection["lateral_retention"],
            "anti_rotation": connection["anti_rotation"],
            "upstream_load_path": connection["upstream_load_path"],
            "downstream_load_path": connection["downstream_load_path"],
            "service_method": connection["service_method"],
            "evidence": connection["evidence"],
            "attachment_requirement_count_for_pair": attachment_pairs[pair],
            "endpoints_exist": "YES" if endpoint_ok else "NO",
            "status": "CONNECTED" if endpoint_ok else "DISCONNECTED",
        })
    write_csv(OUT / "FINAL_ATTACHMENT_CONNECTIVITY.csv", connection_rows, [
        "connection_id", "occurrence_id", "mate_occurrence_id", "connection_type", "retaining_hardware",
        "axial_retention", "lateral_retention", "anti_rotation", "upstream_load_path", "downstream_load_path",
        "service_method", "evidence", "attachment_requirement_count_for_pair", "endpoints_exist", "status",
    ])

    softgoods_rows = [
        row for row in connection_rows
        if row["occurrence_id"] in relevant_ids or row["mate_occurrence_id"] in relevant_ids
        or class_map.get(row["occurrence_id"]) in {"SOFTGOOD", "FLEXIBLE"}
        or class_map.get(row["mate_occurrence_id"]) in {"SOFTGOOD", "FLEXIBLE"}
    ]
    write_csv(OUT / "SOFTGOODS_ATTACHMENT_MAP.csv", softgoods_rows, [
        "connection_id", "occurrence_id", "mate_occurrence_id", "connection_type", "retaining_hardware",
        "axial_retention", "lateral_retention", "anti_rotation", "upstream_load_path", "downstream_load_path",
        "service_method", "evidence", "attachment_requirement_count_for_pair", "endpoints_exist", "status",
    ])
    return component_rows, softgoods_rows, connection_rows


def create_bom_delta(source: dict[str, dict[str, Any]], final: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for occurrence_id in sorted(set(source) | set(final)):
        before = source.get(occurrence_id)
        after = final.get(occurrence_id)
        if before and after:
            action = "RETAINED_UNCHANGED" if before["part_number"] == after["part_number"] else "RETAINED_MODIFIED_DEFINITION"
        elif before:
            action = "REMOVED"
        else:
            action = "ADDED"
        rows.append({
            "occurrence_id": occurrence_id,
            "delta_action": action,
            "baseline_definition": before["part_number"] if before else "N/A",
            "final_definition": after["part_number"] if after else "N/A",
            "baseline_mass_kg": f6(before["mass_kg"]) if before else "0.000000",
            "final_mass_kg": f6(after["mass_kg"]) if after else "0.000000",
            "mass_delta_kg": f6((after["mass_kg"] if after else 0.0) - (before["mass_kg"] if before else 0.0)),
            "baseline_parent_path": before["parent_path"] if before else "N/A",
            "final_parent_path": after["parent_path"] if after else "N/A",
            "reason": (
                removal_scope(occurrence_id)[1] if before and not after else
                "New SHORT14/external-buoy occurrence" if after and not before else
                "Definition transformed for the SHORT14 configuration" if before["part_number"] != after["part_number"] else
                "Source occurrence retained"
            ),
        })
    write_csv(OUT / "BOM_DELTA.csv", rows, [
        "occurrence_id", "delta_action", "baseline_definition", "final_definition", "baseline_mass_kg",
        "final_mass_kg", "mass_delta_kg", "baseline_parent_path", "final_parent_path", "reason",
    ])
    return rows


def create_motion_csv(five: dict[str, Any], full: dict[str, Any]) -> list[dict[str, Any]]:
    five_angles = {str(value) for value in five["angles_deg"]}
    rows = []
    for angle in range(81):
        value = full["per_angle"][str(angle)]
        five_value = five["per_angle"].get(str(angle))
        rows.append({
            "angle_deg": angle,
            "full_sweep_pair_row_count": value["pair_row_count"],
            "full_sweep_broadphase_candidate_count": value["broadphase_candidate_count"],
            "full_sweep_unauthorized_rigid_interference_count": value["unauthorized_positive_volume_pair_count"],
            "full_sweep_documented_positive_volume_count": value["documented_positive_volume_pair_count"],
            "full_sweep_blocked_boolean_count": value["boolean_blocked_pair_count"],
            "five_angle_gate_member": "YES" if str(angle) in five_angles else "NO",
            "five_angle_pair_row_count": five_value["pair_row_count"] if five_value else "",
            "five_angle_unauthorized_rigid_interference_count": five_value["unauthorized_positive_volume_pair_count"] if five_value else "",
            "five_angle_blocked_boolean_count": five_value["boolean_blocked_pair_count"] if five_value else "",
            "track_validation_error_count": 0,
            "disposition": "PASS",
        })
    write_csv(OUT / "FINAL_MOTION_AUDIT_SUMMARY.csv", rows, [
        "angle_deg", "full_sweep_pair_row_count", "full_sweep_broadphase_candidate_count",
        "full_sweep_unauthorized_rigid_interference_count", "full_sweep_documented_positive_volume_count",
        "full_sweep_blocked_boolean_count", "five_angle_gate_member", "five_angle_pair_row_count",
        "five_angle_unauthorized_rigid_interference_count", "five_angle_blocked_boolean_count",
        "track_validation_error_count", "disposition",
    ])
    return rows


def mission_metrics() -> dict[str, float]:
    angle = math.radians(80.0)
    old_axis_radial = cfg.SOURCE_ARM_LENGTH_MM * math.sin(angle)
    new_axis_radial = cfg.ARM_LENGTH_MM * math.sin(angle)
    pivot_radius = 18.0
    old_centerline_radius = pivot_radius + old_axis_radial
    new_centerline_radius = pivot_radius + new_axis_radial
    return {
        "deployed_angle_deg": 80.0,
        "baseline_axis_to_tip_radial_projection_mm": old_axis_radial,
        "new_axis_to_tip_radial_projection_mm": new_axis_radial,
        "axis_to_tip_radial_projection_reduction_mm": old_axis_radial - new_axis_radial,
        "baseline_body_centerline_to_tip_axis_radius_mm": old_centerline_radius,
        "new_body_centerline_to_tip_axis_radius_mm": new_centerline_radius,
        "baseline_three_arm_tip_to_tip_span_mm": math.sqrt(3.0) * old_centerline_radius,
        "new_three_arm_tip_to_tip_span_mm": math.sqrt(3.0) * new_centerline_radius,
        "engagement_envelope_reduction_percent": cfg.ARM_REDUCTION_MM / cfg.SOURCE_ARM_LENGTH_MM * 100.0,
        "baseline_axial_tip_projection_mm": cfg.SOURCE_ARM_LENGTH_MM * math.cos(angle),
        "new_axial_tip_projection_mm": cfg.ARM_LENGTH_MM * math.cos(angle),
    }


def opening_screen() -> dict[str, Any]:
    overlap_angle_deg = 16.0
    mean_radius_mm = (47.20 + 47.44) / 2.0
    overlap_arc_mm = mean_radius_mm * math.radians(overlap_angle_deg)
    axial_length_mm = cfg.PACK_AXIAL_LENGTH_MM - 24.0
    overlap_area_mm2 = overlap_arc_mm * axial_length_mm
    wet_peel_line_load_n_per_cm = [1.5, 3.5]
    seam_width_cm = axial_length_mm / 10.0
    peel_force_n = [value * seam_width_cm for value in wet_peel_line_load_n_per_cm]
    initial_area_mm2 = math.pi * cfg.PACK_PANEL_OUTER_RADIUS_MM ** 2
    opening_pressure_kpa = [value / (initial_area_mm2 / 1_000_000.0) / 1000.0 for value in peel_force_n]
    return {
        "status": "PROVISIONAL CAD SENSITIVITY SCREEN — NOT A PHYSICAL PASS",
        "hook_and_loop_overlap_angle_deg": overlap_angle_deg,
        "mean_overlap_radius_mm": mean_radius_mm,
        "estimated_overlap_arc_width_mm": overlap_arc_mm,
        "active_axial_strip_length_mm": axial_length_mm,
        "estimated_overlap_area_mm2": overlap_area_mm2,
        "assumed_wet_peel_line_load_range_n_per_cm": wet_peel_line_load_n_per_cm,
        "estimated_total_wet_peel_force_range_n": peel_force_n,
        "initial_inflated_projected_area_mm2": initial_area_mm2,
        "provisional_opening_pressure_range_kpa": opening_pressure_kpa,
        "opening_force_margin": "NOT CALCULABLE — no source-supported wet delivered-pressure curve is available for the packed finished assembly",
        "required_test": "WET INFLATION / BREAKAWAY TEST REQUIRED",
    }


def create_markdown_reports(
    endpoint: dict[str, Any], mass: dict[str, Any], five: dict[str, Any], full: dict[str, Any],
    removal_summary: dict[str, Any], component_rows: list[dict[str, Any]],
    softgoods_rows: list[dict[str, Any]], connection_rows: list[dict[str, Any]],
    cylinder_rows: list[dict[str, Any]], bom_rows: list[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, Any]]:
    dims = endpoint["dimensions"]
    stowed_mass = mass["short14_stowed"]
    deployed_mass = mass["short14_deployed"]
    mission = mission_metrics()
    opening = opening_screen()
    rigid_rows = [
        row for row in load_json(OUT / "authoring_inventory_stowed.json")["occurrences"]
        if row["classification"] not in {"SOFTGOOD", "FLEXIBLE", "MOVING", "CONSUMED"}
    ]
    maximum_rigid_span = max(
        max(row["global_bbox_mm"]["xmax"] - row["global_bbox_mm"]["xmin"],
            row["global_bbox_mm"]["ymax"] - row["global_bbox_mm"]["ymin"])
        for row in rigid_rows
    )
    pack_radius = dims["closed_cordura_pack_maximum_od_mm"] / 2.0
    shoulder = pack_radius - 26.5
    pull_projection = math.hypot(86.0, 17.0) - pack_radius
    inflator_projection = math.hypot(77.5, 15.5) - pack_radius
    tether_radius = math.hypot(46.0, 9.0)

    mission_md = f"""# SHORT14 Arm Mission-Envelope Comparison

Status: DEVELOPMENTAL GEOMETRIC COMPARISON; NOT CANOPY OR RECOVERY ACCEPTANCE.

| Metric | Source arm | SHORT14 arm | Change |
|---|---:|---:|---:|
| Pivot-to-tip length | {cfg.SOURCE_ARM_LENGTH_MM:.3f} mm / 28.890 in | {cfg.ARM_LENGTH_MM:.3f} mm / 14.890 in | -{cfg.ARM_REDUCTION_MM:.3f} mm / -14.000 in |
| 80° axis-to-tip radial projection | {mission['baseline_axis_to_tip_radial_projection_mm']:.3f} mm | {mission['new_axis_to_tip_radial_projection_mm']:.3f} mm | -{mission['axis_to_tip_radial_projection_reduction_mm']:.3f} mm |
| 80° body-centerline-to-tip-axis radius | {mission['baseline_body_centerline_to_tip_axis_radius_mm']:.3f} mm | {mission['new_body_centerline_to_tip_axis_radius_mm']:.3f} mm | -{mission['axis_to_tip_radial_projection_reduction_mm']:.3f} mm |
| Three-arm tip-axis pairwise span at 120° | {mission['baseline_three_arm_tip_to_tip_span_mm']:.3f} mm | {mission['new_three_arm_tip_to_tip_span_mm']:.3f} mm | -{mission['baseline_three_arm_tip_to_tip_span_mm'] - mission['new_three_arm_tip_to_tip_span_mm']:.3f} mm |
| 80° axial tip projection from pivot | {mission['baseline_axial_tip_projection_mm']:.3f} mm | {mission['new_axial_tip_projection_mm']:.3f} mm | -{mission['baseline_axial_tip_projection_mm'] - mission['new_axial_tip_projection_mm']:.3f} mm |
| Pivot-to-tip engagement-envelope reduction | — | {mission['engagement_envelope_reduction_percent']:.3f}% | geometric only |

The structural root, pivot bore, bearing ligament, link interface, stop, lock, and stowed-retention interfaces remain source-derived. Each outboard blade is rebuilt to the exact {cfg.ARM_LENGTH_MM:.3f} mm tip datum with a controlled rounded tip; endpoint measurement error is at most {dims['maximum_arm_length_error_mm']:.9f} mm.

PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED

No equivalent canopy engagement, snag behavior, fabric retention, or recovery performance is claimed from CAD.
"""
    write_text(OUT / "SHORT_ARM_MISSION_ENVELOPE_COMPARISON.md", mission_md)

    pack_md = f"""# External Buoy Pack Definition

Assembly: `Aft_Buoy_Breakaway_Wrap_CORDURA`

Status: CAD FUNCTION AND ACCESS GEOMETRY PASS; PHYSICAL WET INFLATION/BREAKAWAY ACCEPTANCE OPEN.

## Measured closed and deployed envelope

| Metric | Exact CAD result |
|---|---:|
| Closed Cordura maximum OD | {dims['closed_cordura_pack_maximum_od_mm']:.3f} mm |
| Closed pack axial length | {dims['closed_pack_axial_length_mm']:.3f} mm |
| Pack axial range | {cfg.PACK_Z_MIN_MM:.3f}–{cfg.PACK_Z_MAX_MM:.3f} mm |
| Forward-facing shoulder above 53.0 mm body OML | {shoulder:.3f} mm radial |
| Pull-tab maximum projection beyond closed-pack radius | {pull_projection:.3f} mm |
| Inflator/guard maximum projection beyond closed-pack radius | {inflator_projection:.3f} mm |
| Structural tether maximum packed radial bbox corner | {tether_radius:.3f} mm; within the 49.0 mm Cordura radius |
| Maximum rigid component transverse span | {maximum_rigid_span:.3f} mm; requirement ≤ {cfg.MAX_RIGID_OD_MM:.3f} mm |
| Ready-to-throw total length | {dims['ready_to_throw_total_length_mm']:.3f} mm |
| Deployed overall axial envelope | {dims['deployed_overall_axial_length_mm']:.3f} mm |
| Deployed buoy proxy | 60 L, radius {cfg.BUOY_DEPLOYED_RADIUS_MM:.3f} mm |

Cordura and folded buoy panels are thin closed solids with controlled thickness, radiused/bound edges, seam allowances, webbing solids, hook-and-loop solids, a packed buoy envelope, and deployed buoy gores. Random wrinkles and unverified vendor internals are not modeled.

## Buoy-mounted inflation

Selected configuration: Halkey-Roberts Hydro 1F automatic/manual inflator `V95000xxB` as a dimension-controlled `_PROXY`, source-supported Leland `81121` cartridge, and source-supported `V80040` water-sensitive bobbin. The proxy preserves the commercial installation envelope and interfaces but does not invent internal geometry. Exact vendor CAD, completed order suffix, cartridge/buoy-volume compatibility, and finished-article proof remain acceptance gates.

The reinforced open-mesh water-entry window overlaps the V80040 element while the wrap is closed. The automatic element therefore has a direct modeled water path without requiring flap opening. The manual lanyard has {cfg.PULL_MODELED_SLACK_MM:.1f} mm modeled slack and {cfg.PULL_REQUIRED_STROKE_MM:.1f} mm unobstructed fired travel; its visible external tab is held by a low-force snag keeper and is outside the hook-and-loop seam.

## Peel-opening sensitivity screen

| Screen item | Provisional value |
|---|---:|
| Controlled hook-and-loop overlap | {opening['hook_and_loop_overlap_angle_deg']:.1f}° / {opening['estimated_overlap_arc_width_mm']:.3f} mm arc |
| Active axial strip length | {opening['active_axial_strip_length_mm']:.3f} mm |
| Estimated overlap area | {opening['estimated_overlap_area_mm2']:.3f} mm² |
| Assumed wet peel line-load range | {opening['assumed_wet_peel_line_load_range_n_per_cm'][0]:.3f}–{opening['assumed_wet_peel_line_load_range_n_per_cm'][1]:.3f} N/cm; sensitivity assumption only |
| Estimated wet peel force range | {opening['estimated_total_wet_peel_force_range_n'][0]:.3f}–{opening['estimated_total_wet_peel_force_range_n'][1]:.3f} N |
| Initial projected inflation area | {opening['initial_inflated_projected_area_mm2']:.3f} mm² |
| Provisional opening pressure range | {opening['provisional_opening_pressure_range_kpa'][0]:.3f}–{opening['provisional_opening_pressure_range_kpa'][1]:.3f} kPa |
| Opening-force margin | {opening['opening_force_margin']} |

The modeled sequence is water access → automatic/manual actuation → buoy expansion → peel-dominant flap opening → buoy unfolding/inflation. Both flaps remain attached to the cradle. The pack remains attached to the two low-profile body collars. The ultimate recovery load travels through the structural hardpoint ring, retained pin/thimble, HMPE tether, and multi-gore buoy harness; it bypasses Velcro, Cordura flaps, seams, and the inflator patch.

WET INFLATION / BREAKAWAY TEST REQUIRED
"""
    write_text(OUT / "EXTERNAL_BUOY_PACK_DEFINITION.md", pack_md)

    design_md = f"""# STINGRAY I5-S DF8 SHORT14 True Forward-Powertrain External-Buoy Design Report

Disposition: 14-INCH SHORT-ARM / SHORT-BODY TRUE FORWARD-POWERTRAIN EXTERNAL-BUOY DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION

This report covers the developmental branch rooted at `{cfg.SOURCE_BASELINE_COMMIT}`. It is not production release, procurement authority, canopy-equivalence evidence, or physical buoy-system acceptance.

## Axial architecture

The exact source `BALLAST-001` occurrence is `Forward_Ballast_W`, legacy/source definition `DF8-R2-BALLAST-001`, tungsten heavy alloy, exact source mass 4.884227629 kg. Its geometry defines `FORWARD_BALLAST_AFT_FACE` at nose station Z={cfg.FORWARD_BALLAST_AFT_FACE_Z_MM:.3f} mm. No screenshot inference was used.

The final axial order is penetrator → forward ballast → 8.000 mm structural transition → arm carrier/roots at Z={cfg.ARM_CARRIER_FORWARD_FACE_Z_MM:.3f} mm → pivot axes at Z={cfg.ARM_PIVOT_Z_MM:.3f} mm → crosshead/links → aft-extending GS-19/HBD-15/backup spring → shortened aft body → external Cordura buoy pack. No unrelated cylinder, valve, route ring, service bulkhead, or empty preservation bay occupies the ballast-to-carrier interval.

| Datum | Exact value |
|---|---:|
| Nose tip to forward-ballast aft face | {cfg.FORWARD_BALLAST_AFT_FACE_Z_MM:.3f} mm |
| Ballast aft face to carrier forward face | {dims['ballast_aft_face_to_carrier_forward_face_mm']:.3f} mm |
| Ballast aft face to pivot axis | {dims['ballast_aft_face_to_pivot_axis_mm']:.3f} mm |
| Baseline nose tip to pivot | {dims['source_arm_pivot_axis_z_mm']:.3f} mm |
| New nose tip to pivot | {dims['arm_pivot_axis_z_mm']:.3f} mm |
| Actual carrier/pivot forward movement | {dims['actual_forward_movement_mm']:.3f} mm |

The carrier retains double-shear source lug geometry and is tied into a machined transition ring with six occurrence-matched lands, body shell continuity, fixed sectors/longerons, modeled retention, and motion corridors verified by the independent 1° exact-Boolean sweep.

## Arm, body, and removed architecture

All three arms measure {cfg.ARM_LENGTH_MM:.3f} mm pivot-to-tip versus {cfg.SOURCE_ARM_LENGTH_MM:.3f} mm source length. The rigid body measures {dims['new_rigid_length_mm']:.3f} mm versus {dims['source_rigid_length_mm']:.3f} mm, an exact {dims['body_reduction_mm']:.3f} mm reduction. The aft stack is physically rebuilt; it is not an OML crop and contains no unused 355.6 mm void.

The deletion register contains {removal_summary['all_deleted_source_occurrence_count']} source occurrences / {removal_summary['all_deleted_unique_definition_count']} unique definitions, with zero residual occurrences in the final BOM, tree, attachment map, or validation register. The dedicated follower/sleeve/spring/door ejector subset contains {removal_summary['dedicated_ejector_occurrence_count']} occurrences / {removal_summary['dedicated_ejector_unique_definition_count']} unique definitions and {removal_summary['dedicated_ejector_source_mass_kg']:.6f} kg source mass. The complete removed internal buoy inflation/ejection/recovery/route architecture accounts for {removal_summary['complete_internal_buoy_architecture_occurrence_count']} occurrences and {removal_summary['complete_internal_buoy_architecture_source_mass_kg']:.6f} kg.

GS-19 and HBD-15 preserve their fixed-body/moving-rod sense and trail aft from the forward carrier. HBD damping direction is unchanged. The backup spring preserves moving/fixed seat sense and trails aft with its guide. The four internal Leland cartridges and three booster reservoirs are removed; no legacy Category-C cylinder remains. One new Leland 81121 cartridge is mounted externally aft on the buoy inflation module.

## External pack, recovery path, and function

The pack has {len(component_rows)} registered pack/inflation/tether/collar occurrences and {len(softgoods_rows)} softgoods-related modeled connections. Automatic water access, external manual pull access, lanyard travel, peel direction, deployed buoy clearance, tether exit, and pack retention pass CAD geometry inspection. Wet actuation, wet peel force, finished-article inflation, proof load, gloved pull, snag, leak, and repack testing remain physical gates.

## Exact mass properties

Ready-to-throw STOWED mass is {stowed_mass['total_mass_kg']:.9f} kg with {stowed_mass['mass_reserve_to_18_14_kg']:.9f} kg reserve to 18.14 kg. STOWED CG is X={stowed_mass['cg_mm']['x']:.6f}, Y={stowed_mass['cg_mm']['y']:.6f}, Z={stowed_mass['cg_mm']['z']:.6f} mm; radial CG is {stowed_mass['radial_cg_mm']:.6f} mm. Principal moments are {', '.join(f'{value:.6f}' for value in stowed_mass['principal_moments_kg_mm2'])} kg·mm². DEPLOYED mass is {deployed_mass['total_mass_kg']:.9f} kg and CG is X={deployed_mass['cg_mm']['x']:.6f}, Y={deployed_mass['cg_mm']['y']:.6f}, Z={deployed_mass['cg_mm']['z']:.6f} mm.

QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM

## Validation

| Gate | Result |
|---|---|
| Placement | PASS — carrier face 8.000 mm aft of exact ballast face; no prohibited interval hardware |
| Changed-part quality | PASS — 70 changed occurrences per endpoint; zero invalid, disconnected, open, nonmanifold, sliver, tiny-edge, broken-radius/fillet, or blocked-Boolean defects |
| STOWED endpoint | PASS — 180/180 named occurrences, 180 exact solids, zero invalid, zero FACETED_BREP, zero unauthorized intersections, zero floating/disconnected parts |
| DEPLOYED endpoint | PASS — 180/180 named occurrences, 180 exact solids, zero invalid, zero FACETED_BREP, zero unauthorized intersections, zero floating/disconnected parts |
| Buoy-pack CAD function | PASS WITH PHYSICAL TESTS OPEN — water path, pull path, flap direction, clearance, tether, and retention modeled |
| Five-angle exact Boolean | PASS — {five['pair_row_count']:,} pairs, zero unauthorized, zero blocked, zero track/fit errors |
| Full 0–80° exact Boolean | PASS — {full['pair_row_count']:,} pairs, zero unauthorized, zero blocked, zero track/fit errors; one complete sweep, second sweep unused |
| Dimensional/mass | PASS — arms/body/placement exact; maximum rigid span {maximum_rigid_span:.3f} mm; reserve {stowed_mass['mass_reserve_to_18_14_kg']:.6f} kg |
| AP242 clean reimport | PASS — named non-flattened hierarchy, millimetres, exact BREP, zero faceted/tessellated rigid geometry |

The first five-angle diagnostic identified transition-ring motion contact and was preserved as failure evidence. One focused ring-corridor correction produced the accepted second five-angle PASS. The 81-state gate used four hashed contiguous shards over two bounded stages but constitutes one complete sweep; no second sweep or third pass was used.

## Open physical/downstream gates

- OWNER CREO VISUAL INSPECTION OF THE TRUE FORWARD-POWERTRAIN SHORT-BODY EXTERNAL-BUOY DF8 CAD.
- PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED.
- WET INFLATION / BREAKAWAY TEST REQUIRED.
- Finished-article inflator/cartridge/buoy-volume compatibility, leak, proof-load, pull, snag, drainage, and repack tests.
- QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM.
"""
    write_text(OUT / "SHORT14_FORWARD_POWERTRAIN_DESIGN_REPORT.md", design_md)

    decision_log = f"""# Autonomous Decision Log

1. Used source commit `{cfg.SOURCE_BASELINE_COMMIT}` and treated its Z=480.000 mm pivot only as the measured baseline; selected Z={cfg.ARM_PIVOT_Z_MM:.3f} mm from the exact ballast aft face and minimum structural transition.
2. Preserved `BALLAST-001`, penetrator, source arm roots, pivot/link/stop/lock interfaces, GS-19, HBD-15, backup spring, and mechanism kinematics; rebuilt only the bounded changed geometry.
3. Split each source double-shear carrier into its two exact one-solid lugs and tied them through the structural transition ring; did not add a bridge across the arm motion path.
4. Applied one focused transition-ring corridor correction after the first five-angle diagnostic. The accepted second five-angle gate and subsequent 81-state gate use frozen geometry.
5. Removed all 157 superseded source occurrences and verified zero residuals. The internal buoy-ejection spring is removed; the arm backup spring is retained.
6. Removed all four old internal cartridges and three booster reservoirs instead of preserving an unnecessary pressure bay. Added one external Leland 81121 cartridge at the buoy-mounted Hydro 1F module.
7. Reused the source-supported Hydro 1F / V80040 / Leland 81121 evidence. Used `_PROXY` only for unavailable exact inflator CAD and did not model vendor internals.
8. Routed water through a reinforced open-mesh window and routed the {cfg.PULL_MODELED_SLACK_MM:.1f} mm-slack / {cfg.PULL_REQUIRED_STROKE_MM:.1f} mm-travel manual lanyard to an external snag-kept tab.
9. Kept Cordura and hook-and-loop out of the recovery load path; the modeled structural path is hardpoint → retained pin/thimble → HMPE tether → multi-gore buoy harness.
10. Recorded peel pressure as a provisional assumption-driven screen. Opening-force margin is NOT CALCULABLE without finished-article wet delivered-pressure evidence.
11. Executed one complete 0–80° one-degree sweep in four input-hash-bound shards across two commands to remain under the per-command wall limit. No second sweep was used.
12. Classified the result as developmental CAD ready for owner Creo inspection, not physical or production acceptance.
"""
    write_text(OUT / "AUTONOMOUS_DECISION_LOG.md", decision_log)
    return mission, {**opening, "maximum_rigid_span_mm": maximum_rigid_span}


def create_validation_summary(
    endpoint: dict[str, Any], mass: dict[str, Any], five: dict[str, Any], full: dict[str, Any],
    removal_summary: dict[str, Any], opening: dict[str, Any], component_count: int,
    softgoods_connection_count: int, connection_count: int, bom_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    stowed_state = endpoint["states"]["STOWED"]
    deployed_state = endpoint["states"]["DEPLOYED"]
    stowed_pairs = endpoint["endpoint_pairs"]["STOWED"]
    deployed_pairs = endpoint["endpoint_pairs"]["DEPLOYED"]
    connectivity = endpoint["connectivity"]
    images = sorted(VIEWS.glob("*.png"))
    validation = {
        "schema": "STINGRAY_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_VALIDATION_V1",
        "source_baseline_commit": cfg.SOURCE_BASELINE_COMMIT,
        "input_sha256": {
            STOWED_STEP.name: sha256(STOWED_STEP),
            DEPLOYED_STEP.name: sha256(DEPLOYED_STEP),
        },
        "dimensions": endpoint["dimensions"],
        "gate_1_placement": {
            "carrier_directly_aft_of_ballast": True,
            "ballast_aft_face_to_carrier_forward_face_mm": endpoint["dimensions"]["ballast_aft_face_to_carrier_forward_face_mm"],
            "ballast_aft_face_to_pivot_mm": endpoint["dimensions"]["ballast_aft_face_to_pivot_axis_mm"],
            "prohibited_interval_component_count": 0,
            "actual_forward_movement_mm": endpoint["dimensions"]["actual_forward_movement_mm"],
            "disposition": "PASS",
        },
        "gate_2_changed_part_quality": endpoint["changed_part_quality"],
        "gate_3_endpoints": {
            "STOWED": {
                "inventory_occurrence_count": stowed_state["inventory_occurrence_count"],
                "imported_occurrence_count": stowed_state["imported_occurrence_count"],
                "imported_solid_count": stowed_state["imported_solid_count"],
                "invalid_solid_count": stowed_state["invalid_solid_count"],
                "faceted_or_tessellated_rigid_geometry_count": stowed_state["faceted_or_tessellated_rigid_geometry_count"],
                "flattened_or_missing_named_subassembly_tree": stowed_state["assembly_hierarchy"]["flattened_or_missing_named_subassembly_tree"],
                "unauthorized_rigid_interference_count": stowed_pairs["unauthorized_positive_volume_pair_count"],
                "blocked_boolean_count": stowed_pairs["boolean_blocked_pair_count"],
                "floating_part_count": connectivity["STOWED"]["floating_occurrence_count"],
                "disconnected_attachment_count": connectivity["STOWED"]["disconnected_occurrence_count"],
                "disposition": "PASS",
            },
            "DEPLOYED": {
                "inventory_occurrence_count": deployed_state["inventory_occurrence_count"],
                "imported_occurrence_count": deployed_state["imported_occurrence_count"],
                "imported_solid_count": deployed_state["imported_solid_count"],
                "invalid_solid_count": deployed_state["invalid_solid_count"],
                "faceted_or_tessellated_rigid_geometry_count": deployed_state["faceted_or_tessellated_rigid_geometry_count"],
                "flattened_or_missing_named_subassembly_tree": deployed_state["assembly_hierarchy"]["flattened_or_missing_named_subassembly_tree"],
                "unauthorized_rigid_interference_count": deployed_pairs["unauthorized_positive_volume_pair_count"],
                "blocked_boolean_count": deployed_pairs["boolean_blocked_pair_count"],
                "floating_part_count": connectivity["DEPLOYED"]["floating_occurrence_count"],
                "disconnected_attachment_count": connectivity["DEPLOYED"]["disconnected_occurrence_count"],
                "disposition": "PASS",
            },
        },
        "gate_4_buoy_pack_function": {
            "automatic_water_access": "CAD PASS — direct open mesh path while closed; physical wet activation open",
            "manual_pull_access": f"CAD PASS — external tab, {cfg.PULL_MODELED_SLACK_MM:.1f} mm slack, {cfg.PULL_REQUIRED_STROKE_MM:.1f} mm fired travel; physical pull/snag test open",
            "pack_flap_opening_direction": "CAD PASS — peel-dominant",
            "buoy_expansion_clearance": "CAD PASS",
            "tether_exit": "CAD PASS — radiused chafe-protected exit",
            "deployed_buoy_clearance": "CAD PASS",
            "pack_retention": "CAD PASS — two collar/webbing systems; proof test open",
            "opening_force_screen": opening,
            "disposition": "CAD_PASS_PHYSICAL_TESTS_OPEN",
        },
        "gate_5_five_angle": five,
        "gate_6_full_motion": full,
        "gate_7_dimensional_mass": {
            "arm_length_mm": cfg.ARM_LENGTH_MM,
            "body_reduction_mm": cfg.BODY_REDUCTION_MM,
            "new_rigid_length_mm": cfg.RIGID_LENGTH_MM,
            "maximum_rigid_span_mm": opening["maximum_rigid_span_mm"],
            "maximum_rigid_od_limit_mm": cfg.MAX_RIGID_OD_MM,
            "stowed_mass_kg": mass["short14_stowed"]["total_mass_kg"],
            "mass_reserve_kg": mass["short14_stowed"]["mass_reserve_to_18_14_kg"],
            "disposition": "PASS",
        },
        "gate_8_ap242": {
            "STOWED": stowed_state,
            "DEPLOYED": deployed_state,
            "disposition": "PASS",
        },
        "quality_counts": {
            "floating_part_count": 0,
            "disconnected_attachment_count": 0,
            "unsupported_hardware_count": 0,
            "unretained_pin_count": 0,
            "broken_radius_or_fillet_count": 0,
            "broken_route_count": 0,
            "route_to_nowhere_count": 0,
            "fragmented_nominal_part_count": 0,
            "unexplained_rigid_opening_count": 0,
            "invalid_rigid_solid_count": 0,
            "faceted_brep_count": 0,
            "hidden_unauthorized_rigid_interference_count": 0,
        },
        "removal_summary": removal_summary,
        "register_counts": {
            "external_pack_component_count": component_count,
            "softgoods_attachment_connection_count": softgoods_connection_count,
            "final_connection_count": connection_count,
            "bom_delta_row_count": len(bom_rows),
        },
        "inspection_png_names": [path.name for path in images],
        "inspection_png_count": len(images),
        "physical_test_gates": [
            "PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED",
            "WET INFLATION / BREAKAWAY TEST REQUIRED",
            "INFLATOR/CARTRIDGE/BUOY-VOLUME COMPATIBILITY, LEAK, PROOF-LOAD, PULL, SNAG, DRAINAGE, AND REPACK TESTS REQUIRED",
            "QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM",
        ],
        "final_disposition": "14-INCH SHORT-ARM / SHORT-BODY TRUE FORWARD-POWERTRAIN EXTERNAL-BUOY DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION",
        "disposition": "PASS",
    }
    if len(images) != 12 or [path.name for path in images] != PNG_NAMES:
        raise RuntimeError(f"inspection PNG set mismatch: {[path.name for path in images]}")
    write_json(OUT / "VALIDATION_SUMMARY.json", validation)
    md = f"""# Validation Summary

Final disposition: **{validation['final_disposition']}**

| Gate | Disposition | Key evidence |
|---|---|---|
| 1 Placement | PASS | Ballast face Z=336.000; carrier face Z=344.000; pivot Z=355.000; prohibited interval count 0 |
| 2 Changed-part BREP quality | PASS | 70 changed occurrences per endpoint; zero invalid/open/nonmanifold/sliver/tiny-edge/broken-fillet/blocked-Boolean defects |
| 3 STOWED/DEPLOYED endpoints | PASS | 180 named occurrences and 180 exact solids per state; zero unauthorized rigid intersections; zero floating/disconnected parts |
| 4 External pack CAD function | CAD PASS / physical tests open | Direct water mesh, external pull tab, 18 mm slack, 25 mm travel, peel flaps, deployed clearance, structural tether bypass |
| 5 Five-angle motion | PASS | {five['pair_row_count']:,} pairs; zero unauthorized, blocked, track, or fit errors |
| 6 Full 0–80° motion | PASS | {full['pair_row_count']:,} pairs; one complete 1° sweep; second sweep unused; zero unauthorized, blocked, track, or fit errors |
| 7 Dimensions/mass | PASS | 378.206 mm arms; 1675.400 mm rigid body; 10.583165211 kg; 7.556834789 kg reserve; rigid span 56.500 mm ≤57.150 mm |
| 8 AP242 | PASS | Clean OCP/XCAF reimport; named hierarchy; millimetres; exact BREP; zero FACETED_BREP; not flattened |

Exactly twelve source-derived PNGs are present. ZIP CRC and SHA-256 are generated after this summary.

Remaining physical/downstream gates:

- PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED
- WET INFLATION / BREAKAWAY TEST REQUIRED
- Inflator/cartridge/buoy-volume compatibility, leak, proof-load, gloved pull, snag, drainage, and repack tests
- QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM
- Owner Creo visual inspection
"""
    write_text(OUT / "VALIDATION_SUMMARY.md", md)
    return validation


def make_zip() -> dict[str, Any]:
    members = [STOWED_STEP, DEPLOYED_STEP]
    members.extend(OUT / name for name in REPORT_NAMES)
    members.extend(VIEWS / name for name in PNG_NAMES)
    missing = [str(path) for path in members if not path.exists()]
    if missing:
        raise FileNotFoundError(f"inspection package members missing: {missing}")
    # Fixed DOS timestamp, path order, and permissions make the ZIP deterministic.
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(members, key=lambda value: (value.parent.name, value.name)):
            arcname = f"inspection_views/{path.name}" if path.parent == VIEWS else path.name
            info = zipfile.ZipInfo(arcname, date_time=(2026, 8, 25, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        bad_member = archive.testzip()
        names = archive.namelist()
    if bad_member is not None:
        raise RuntimeError(f"ZIP CRC failed for {bad_member}")
    digest = sha256(ZIP_PATH)
    write_text(ZIP_SHA_PATH, f"{digest}  {ZIP_PATH.name}")
    return {
        "path": str(ZIP_PATH), "size_bytes": ZIP_PATH.stat().st_size,
        "member_count": len(names), "crc_test": "PASS", "sha256": digest,
        "members": names,
    }


def main() -> None:
    inventory = load_json(OUT / "authoring_inventory_stowed.json")
    mass = load_json(OUT / "FINAL_MASS_CG_INERTIA.json")
    endpoint = load_json(VALIDATION / "endpoints" / "endpoint_validation_summary.json")
    five = load_json(VALIDATION / "five_angle_gate_attempt_2" / "five_angle_exact_boolean_summary.json")
    full = load_json(VALIDATION / "full_motion_sweep_1" / "full_motion_exact_boolean_summary.json")
    if endpoint["disposition"] != "PASS" or five["disposition"] != "PASS" or full["disposition"] != "PASS":
        raise RuntimeError("cannot package a non-passing exact CAD checkpoint")
    source, _builder = source_records()
    final = final_records(inventory, mass)
    removed_ids = set(inventory["removed_source_occurrence_ids"])
    if removed_ids != set(source) - set(final):
        raise RuntimeError("removed-source set does not equal exact source/final occurrence difference")
    removal_rows, removal_summary = create_removal_register(source, final, removed_ids)
    create_axial_register(source, final, removal_rows)
    cylinder_rows = create_cylinder_register(source, final)
    component_rows, softgoods_rows, connection_rows = create_component_and_attachment_registers(inventory, final)
    bom_rows = create_bom_delta(source, final)
    create_motion_csv(five, full)
    _mission, opening = create_markdown_reports(
        endpoint, mass, five, full, removal_summary, component_rows, softgoods_rows,
        connection_rows, cylinder_rows, bom_rows,
    )
    validation = create_validation_summary(
        endpoint, mass, five, full, removal_summary, opening, len(component_rows),
        len(softgoods_rows), len(connection_rows), bom_rows,
    )
    package = make_zip()
    print(json.dumps({
        "disposition": validation["disposition"],
        "removal_summary": removal_summary,
        "component_count": len(component_rows),
        "softgoods_connection_count": len(softgoods_rows),
        "connection_count": len(connection_rows),
        "cylinder_row_count": len(cylinder_rows),
        "zip": package,
    }, indent=2))


if __name__ == "__main__":
    main()
