#!/usr/bin/env python3
"""Independent, evidence-producing validation of the final DF8 AP242 endpoints.

This program is deliberately separate from the authoring program.  It starts
from the AP242 files on disk, imports each into a fresh XCAF document through
CadQuery/OCCT, walks the occurrence hierarchy, expands every leaf occurrence
into individual solids, and writes a deterministic row for every unordered
solid pair.  AABB-separated pairs are not silently discarded: they remain in
the compressed pair register with an explicit broad-phase disposition.

The controlling commission defines clean-process OCCT/XCAF AP242 reimport as
the neutral-CAD acceptance gate.  Target-owner import after delivery is an
informational environment disposition and is deliberately excluded from gate
counts and release logic.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import io
import itertools
import json
import math
import multiprocessing
import os
import re
import tempfile
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_FormatVersion
from OCP.gp import gp_Trsf


ROOT = Path(__file__).resolve().parents[2]
FINAL_RELEASE_DIR = ROOT / "work" / "final_release"
FINAL_ANALYSIS_DIR = ROOT / "work" / "final_analysis"
ANALYSIS_DIR = FINAL_ANALYSIS_DIR
DEFAULT_OUT = ANALYSIS_DIR / "validation"

FINAL_FILES = {
    "STOWED": FINAL_RELEASE_DIR / "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step",
    "DEPLOYED": FINAL_RELEASE_DIR / "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step",
}
FILES = FINAL_FILES
INVENTORIES = {
    "STOWED": ANALYSIS_DIR / "authoring_inventory_stowed.json",
    "DEPLOYED": ANALYSIS_DIR / "authoring_inventory_deployed.json",
}
AUTHORING_MANIFEST = ANALYSIS_DIR / "authoring_manifest.json"

# Frozen acceptance values, repeated here to keep this validator independent
# from the geometry authoring module.
NORMAL_OD_MM = 53.0
HARD_OD_MM = 57.150
MAX_RIGID_LENGTH_MM = 2032.0
MAX_SYSTEM_MASS_KG = 18.14
MIN_MASS_RESERVE_KG = 1.0
PIVOT_RADIUS_MM = 18.0
PIVOT_Z_MM = 900.0
ARM_LENGTH_MM = 733.806
DEPLOYED_ANGLE_DEG = 80.0
BELL_U_MM = 6.0
BELL_V_MM = 9.0
LINK_CENTER_DISTANCE_MM = 19.95
CROSSHEAD_RADIUS_MM = 18.0
MIN_CROSSHEAD_TRAVEL_MM = 15.050

COMMON_VOLUME_EPS_MM3 = 1.0e-6
AABB_TOL_MM = 1.0e-9
NEAR_DISTANCE_LIMIT_MM = 2.0
ATTACHMENT_DEFAULT_MAX_GAP_MM = 0.050
EXPECTED_PRESSURE_SUBSYSTEM_IDS = {
    *(f"CO2-CARTRIDGE-{index}" for index in range(1, 5)),
    *(f"BOOSTER-{index}" for index in range(1, 4)),
}
REQUIRED_NORMAL_OML_OCCURRENCE_IDS = {
    "FWD-SHELL-001", "AFT-SHELL-001",
    "FIXED-SECTOR-1", "FIXED-SECTOR-2", "FIXED-SECTOR-3",
}
EXPECTED_GATE_IDS = (
    "AP242-STOWED", "BREP-VALID-STOWED", "INTERFERENCE-STOWED",
    "INTENTIONAL-FIT-REGISTER-STOWED", "CLEARANCE-EVIDENCE-STOWED",
    "AP242-DEPLOYED", "BREP-VALID-DEPLOYED", "INTERFERENCE-DEPLOYED",
    "INTENTIONAL-FIT-REGISTER-DEPLOYED", "CLEARANCE-EVIDENCE-DEPLOYED",
    "STATE-PARITY", "OCCURRENCE-TRANSFORMS", "OCCURRENCE-BOM-RECONCILIATION",
    "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION", "DOD-POSITIVE-DEPLOYED-LOCKS",
    "DOD-POSITIVE-STOWED-RETENTION", "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
    "DOD-CLOSED-ROUTE-ENDS", "ARM-KINEMATICS-ENDPOINTS", "ARM-LENGTH",
    "ARM-SURFACE-QUALITY", "CROSSHEAD-TRAVEL", "NORMAL-BODY-OML",
    "ARM-MODULE-HARD-ENVELOPE", "RIGID-LENGTH", "SYSTEM-MASS",
    "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH", "PROCUREMENT-DEFINITION",
    "MOTION-FULL-MECHANISM", "INTENTIONAL-FIT-REGISTER-MOTION",
)
CREO_ENVIRONMENT_DISPOSITION = (
    "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; "
    "OWNER CREO IMPORT OCCURS AFTER DELIVERY."
)

PAIR_FIELDS = [
    "state", "pair_index", "occurrence_a", "solid_index_a", "part_number_a",
    "classification_a", "occurrence_b", "solid_index_b", "part_number_b",
    "classification_b", "same_occurrence", "direct_attachment_connection",
    "documented_positive_volume_exception", "intentional_fit_exception_id",
    "intentional_fit_match_status", "aabb_overlap", "aabb_gap_mm",
    "exact_common_status", "common_volume_mm3", "exact_distance_status",
    "exact_clearance_mm", "result", "bbox_a", "bbox_b", "error",
]


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=False, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid_http_url(value: Any) -> bool:
    """Accept only a complete whitespace-free HTTP(S) URL with a host."""
    text = str(value or "").strip()
    if not text or re.search(r"\s", text):
        return False
    try:
        parsed = urlparse(text)
        return bool(
            parsed.scheme.lower() in {"http", "https"}
            and parsed.netloc
            and parsed.hostname
        )
    except ValueError:
        return False


def validate_authoring_manifest(manifest: dict[str, Any]) -> None:
    """Fail closed unless the manifest binds final masters and inventories."""
    if str(manifest.get("schema", "")).strip().upper() != "AP242":
        raise ValueError("authoring manifest schema must be exactly AP242")

    records = manifest.get("files")
    if not isinstance(records, dict):
        raise ValueError("authoring manifest files must be an object")
    expected_names = {path.name for path in FILES.values()}
    actual_names = set(records)
    if actual_names != expected_names:
        raise ValueError(
            "authoring manifest must name exactly the two final STEP masters; "
            f"expected={sorted(expected_names)}, actual={sorted(actual_names)}"
        )

    inventory_records = manifest.get("inventories")
    if not isinstance(inventory_records, dict):
        raise ValueError("authoring manifest inventories must be an object")
    expected_inventory_names = {path.name for path in INVENTORIES.values()}
    actual_inventory_names = set(inventory_records)
    if actual_inventory_names != expected_inventory_names:
        raise ValueError(
            "authoring manifest must name exactly the two final inventories; "
            f"expected={sorted(expected_inventory_names)}, "
            f"actual={sorted(actual_inventory_names)}"
        )

    for path, record_group in [
        *((path, records) for path in FILES.values()),
        *((path, inventory_records) for path in INVENTORIES.values()),
    ]:
        record = record_group.get(path.name)
        if not isinstance(record, dict):
            raise ValueError(f"authoring manifest file record is invalid: {path.name}")
        actual_size = path.stat().st_size
        recorded_size = record.get("size_bytes")
        if isinstance(recorded_size, bool) or not isinstance(recorded_size, int):
            raise ValueError(f"authoring manifest size_bytes must be an integer: {path.name}")
        if recorded_size != actual_size:
            raise ValueError(
                f"authoring manifest size mismatch for {path.name}: "
                f"recorded={recorded_size}, actual={actual_size}"
            )
        actual_hash = sha256(path)
        recorded_hash = str(record.get("sha256", "")).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", recorded_hash):
            raise ValueError(f"authoring manifest SHA-256 is invalid: {path.name}")
        if recorded_hash != actual_hash:
            raise ValueError(
                f"authoring manifest SHA-256 mismatch for {path.name}: "
                f"recorded={recorded_hash}, actual={actual_hash}"
            )


def matrix_3x4(loc: cq.Location) -> list[list[float]]:
    tr = loc.wrapped.Transformation()
    return [[float(tr.Value(i, j)) for j in range(1, 5)] for i in range(1, 4)]


def is_identity_matrix(matrix: list[list[float]], tol: float = 1.0e-10) -> bool:
    ref = ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0))
    return all(abs(matrix[i][j] - ref[i][j]) <= tol for i in range(3) for j in range(4))


def bbox_raw(shape: Any) -> tuple[float, float, float, float, float, float]:
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, True, False)
    return tuple(float(v) for v in box.Get())


def bbox_dict(box: tuple[float, float, float, float, float, float]) -> dict[str, float]:
    return dict(zip(("xmin", "ymin", "zmin", "xmax", "ymax", "zmax"), box))


def bbox_union(boxes: Iterable[tuple[float, float, float, float, float, float]]) -> tuple[float, float, float, float, float, float] | None:
    boxes = list(boxes)
    if not boxes:
        return None
    return (
        min(b[0] for b in boxes), min(b[1] for b in boxes), min(b[2] for b in boxes),
        max(b[3] for b in boxes), max(b[4] for b in boxes), max(b[5] for b in boxes),
    )


def aabb_gap(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    dx = max(0.0, a[0] - b[3], b[0] - a[3])
    dy = max(0.0, a[1] - b[4], b[1] - a[4])
    dz = max(0.0, a[2] - b[5], b[2] - a[5])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def volume_raw(shape: Any) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return float(props.Mass())


def count_explorer(shape: Any, topology: Any) -> int:
    explorer = TopExp_Explorer(shape, topology)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def surface_counts(shape: Any) -> dict[str, int]:
    result: Counter[str] = Counter()
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        enum_value = BRepAdaptor_Surface(face).GetType()
        name = getattr(enum_value, "name", str(enum_value)).replace("GeomAbs_", "")
        result[name] += 1
        explorer.Next()
    return dict(sorted(result.items()))


def parse_occurrence_name(name: str) -> tuple[str, str]:
    tokens = name.split("__")
    occurrence_id = tokens[0]
    part_number = tokens[1] if len(tokens) >= 2 else ""
    return occurrence_id, part_number


@dataclass
class SolidRecord:
    state: str
    occurrence_id: str
    occurrence_name: str
    part_number: str
    classification: str
    solid_index: int
    shape: Any = field(repr=False)
    bbox: tuple[float, float, float, float, float, float]
    volume_mm3: float
    face_count: int
    surface_types: dict[str, int]
    valid: bool

    @property
    def solid_key(self) -> str:
        return f"{self.occurrence_id}::SOLID-{self.solid_index:03d}"


@dataclass
class EndpointData:
    state: str
    path: Path
    assembly: cq.Assembly = field(repr=False)
    occurrence_rows: list[dict[str, Any]]
    solid_records: list[SolidRecord]
    local_shapes: dict[str, cq.Shape] = field(repr=False)
    step_text: dict[str, Any]


def inspect_step_text(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    text = data.decode("latin-1", errors="replace")
    schema_match = re.search(r"FILE_SCHEMA\s*\(\s*\((.*?)\)\s*\)\s*;", text, re.I | re.S)
    schema_record = schema_match.group(1).strip() if schema_match else ""
    product_names = [m.replace("''", "'") for m in re.findall(r"\bPRODUCT\s*\(\s*'((?:''|[^'])*)'", text, re.I | re.S)]
    nauos = re.findall(
        r"\bNEXT_ASSEMBLY_USAGE_OCCURRENCE\s*\(\s*'((?:''|[^'])*)'\s*,\s*'((?:''|[^'])*)'",
        text, re.I | re.S,
    )
    entity_names = re.findall(r"#[0-9]+\s*=\s*([A-Z0-9_]+)\s*\(", text, re.I)
    entities = Counter(n.upper() for n in entity_names)
    compact_upper = re.sub(r"\s+", "", text.upper())
    millimetre_unit_detected = bool(
        re.search(r"SI_UNIT\(\.MILLI\.,\.METRE\.\)", compact_upper)
        or re.search(r"CONVERSION_BASED_UNIT\('MILLI(?:METRE|METER)'", compact_upper)
    )
    faceted_names = (
        "FACETED_BREP", "TESSELLATED_SHAPE_REPRESENTATION", "TESSELLATED_SOLID",
        "TRIANGULATED_FACE", "COMPLEX_TRIANGULATED_FACE", "CARTESIAN_POINT_LIST_3D",
    )
    return {
        "file": str(path), "file_size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "schema_record": schema_record, "ap242_schema_detected": "AP242" in schema_record.upper(),
        "product_count": len(product_names), "unnamed_product_count": sum(not n.strip() for n in product_names),
        "product_names": product_names,
        "nauo_count": len(nauos), "unnamed_nauo_name_count": sum(not name.strip() for _, name in nauos),
        "millimetre_length_unit_detected": millimetre_unit_detected,
        "manifold_solid_brep_count": entities.get("MANIFOLD_SOLID_BREP", 0),
        "brep_with_voids_count": entities.get("BREP_WITH_VOIDS", 0),
        "advanced_face_count": entities.get("ADVANCED_FACE", 0),
        "closed_shell_count": entities.get("CLOSED_SHELL", 0),
        "faceted_or_tessellated_counts": {name: entities.get(name, 0) for name in faceted_names},
        "faceted_or_tessellated_total": sum(entities.get(name, 0) for name in faceted_names),
    }


def load_endpoint(state: str, path: Path, inventory: dict[str, Any]) -> EndpointData:
    """Fresh XCAF reimport followed by a recursive relative/absolute transform walk."""
    assembly = cq.Assembly.importStep(str(path))
    occurrence_lookup = {o["occurrence_id"]: o for o in inventory["occurrences"]}
    occurrence_rows: list[dict[str, Any]] = []
    solids: list[SolidRecord] = []
    local_shapes: dict[str, cq.Shape] = {}

    def visit(node: cq.Assembly, parent_path: str, parent_abs: cq.Location, depth: int) -> None:
        local_loc = node.loc if node.loc is not None else cq.Location()
        absolute_loc = parent_abs * local_loc
        node_name = str(node.name or "")
        node_path = f"{parent_path}/{node_name}" if parent_path else node_name
        local_matrix = matrix_3x4(local_loc)
        absolute_matrix = matrix_3x4(absolute_loc)
        occurrence_id, parsed_part = parse_occurrence_name(node_name)
        auth = occurrence_lookup.get(occurrence_id, {})
        part_number = auth.get("part_number", parsed_part)
        classification = auth.get("classification", "ASSEMBLY" if node.obj is None else "UNMAPPED")
        row: dict[str, Any] = {
            "state": state, "path": node_path, "parent_path": parent_path, "depth": depth,
            "name": node_name, "occurrence_id": occurrence_id if node.obj is not None else "",
            "part_number": part_number if node.obj is not None else "",
            "classification": classification, "has_shape": node.obj is not None,
            "is_leaf": not bool(node.children), "child_count": len(node.children),
            "local_transform_3x4": local_matrix, "absolute_transform_3x4": absolute_matrix,
            "local_transform_identity": is_identity_matrix(local_matrix),
            "absolute_transform_identity": is_identity_matrix(absolute_matrix),
            "mapped_to_authoring_inventory": bool(auth),
        }
        if node.obj is not None:
            local_shapes[occurrence_id] = node.obj
            global_shape = node.obj.moved(absolute_loc)
            shape_bbox = bbox_raw(global_shape.wrapped)
            row.update({
                "bbox_mm": bbox_dict(shape_bbox), "volume_mm3": volume_raw(global_shape.wrapped),
                "solid_count": count_explorer(global_shape.wrapped, TopAbs_SOLID),
                "face_count": count_explorer(global_shape.wrapped, TopAbs_FACE),
                "surface_types": surface_counts(global_shape.wrapped),
                "valid": bool(BRepCheck_Analyzer(global_shape.wrapped).IsValid()),
            })
            explorer = TopExp_Explorer(global_shape.wrapped, TopAbs_SOLID)
            solid_index = 0
            while explorer.More():
                solid_index += 1
                solid = TopoDS.Solid_s(explorer.Current())
                solids.append(SolidRecord(
                    state=state, occurrence_id=occurrence_id, occurrence_name=node_name,
                    part_number=part_number, classification=classification,
                    solid_index=solid_index, shape=solid, bbox=bbox_raw(solid),
                    volume_mm3=volume_raw(solid), face_count=count_explorer(solid, TopAbs_FACE),
                    surface_types=surface_counts(solid), valid=bool(BRepCheck_Analyzer(solid).IsValid()),
                ))
                explorer.Next()
        occurrence_rows.append(row)
        for child in node.children:
            visit(child, node_path, absolute_loc, depth + 1)

    visit(assembly, "", cq.Location(), 0)
    solids.sort(key=lambda s: (s.occurrence_id, s.solid_index, s.part_number))
    return EndpointData(
        state=state, path=path, assembly=assembly, occurrence_rows=occurrence_rows,
        solid_records=solids, local_shapes=local_shapes, step_text=inspect_step_text(path),
    )


def imported_leaf_identity_audit(endpoint: EndpointData) -> dict[str, Any]:
    """Audit raw imported leaf IDs before any ID-keyed lookup can mask them."""
    leaf_rows = [row for row in endpoint.occurrence_rows if row.get("has_shape")]
    raw_ids = [str(row.get("occurrence_id", "")).strip() for row in leaf_rows]
    counts = Counter(value for value in raw_ids if value)
    blank_rows = [
        {"row_index": index, "path": row.get("path", ""), "name": row.get("name", "")}
        for index, (row, occurrence_id) in enumerate(zip(leaf_rows, raw_ids), start=1)
        if not occurrence_id
    ]
    duplicate_ids = sorted(value for value, count in counts.items() if count > 1)
    return {
        "leaf_row_count": len(leaf_rows),
        "blank_occurrence_id_count": len(blank_rows),
        "blank_occurrence_id_rows": blank_rows,
        "duplicate_occurrence_ids": duplicate_ids,
        "duplicate_occurrence_id_count": len(duplicate_ids),
        "accepted": not blank_rows and not duplicate_ids,
    }


def _relative_assembly_path(path: Any, root_name: str) -> str:
    cooked = "/".join(part for part in str(path or "").strip().strip("/").split("/") if part)
    root = str(root_name or "").strip().strip("/")
    if cooked == root:
        return ""
    prefix = f"{root}/" if root else ""
    return cooked[len(prefix):] if prefix and cooked.startswith(prefix) else cooked


def assembly_hierarchy_audit(endpoint: EndpointData, inventory: dict[str, Any]) -> dict[str, Any]:
    """Reconcile the complete imported assembly tree and every leaf parent path."""
    hierarchy = inventory.get("assembly_hierarchy")
    schema_errors: list[str] = []
    if not isinstance(hierarchy, dict):
        hierarchy = {}
        schema_errors.append("assembly_hierarchy must be an object")

    expected_root = str(hierarchy.get("root_name", "")).strip()
    if not expected_root:
        schema_errors.append("assembly_hierarchy.root_name is required")

    expected_top_raw = hierarchy.get("top_level_assembly_names")
    if not isinstance(expected_top_raw, list) or not expected_top_raw:
        expected_top_raw = []
        schema_errors.append("assembly_hierarchy.top_level_assembly_names must be a nonempty list")
    expected_top = [str(value).strip() for value in expected_top_raw]
    if any(not value for value in expected_top):
        schema_errors.append("top_level_assembly_names contains a blank name")
    expected_top_duplicates = sorted(value for value, count in Counter(expected_top).items() if value and count > 1)
    if expected_top_duplicates:
        schema_errors.append(f"duplicate top-level assembly names: {expected_top_duplicates}")

    expected_paths_raw = hierarchy.get("assembly_paths")
    if not isinstance(expected_paths_raw, list) or not expected_paths_raw:
        expected_paths_raw = []
        schema_errors.append("assembly_hierarchy.assembly_paths must be a nonempty list")
    expected_paths = [
        "/".join(part for part in str(value).strip().strip("/").split("/") if part)
        for value in expected_paths_raw
    ]
    if any(not value for value in expected_paths):
        schema_errors.append("assembly_paths contains a blank path")
    expected_path_duplicates = sorted(value for value, count in Counter(expected_paths).items() if value and count > 1)
    if expected_path_duplicates:
        schema_errors.append(f"duplicate assembly paths: {expected_path_duplicates}")

    root_rows = [row for row in endpoint.occurrence_rows if int(row.get("depth", -1)) == 0]
    actual_root = str(root_rows[0].get("name", "")).strip() if len(root_rows) == 1 else ""
    root_shape_free = bool(len(root_rows) == 1 and not root_rows[0].get("has_shape"))
    root_has_children = bool(len(root_rows) == 1 and int(root_rows[0].get("child_count", 0)) > 0)
    assembly_rows = [
        row for row in endpoint.occurrence_rows
        if int(row.get("depth", -1)) >= 1 and not row.get("has_shape")
    ]
    actual_paths = sorted(
        _relative_assembly_path(row.get("path", ""), actual_root)
        for row in assembly_rows
    )
    actual_top = sorted(
        str(row.get("name", "")).strip()
        for row in assembly_rows if int(row.get("depth", -1)) == 1
    )
    blank_assembly_node_paths = sorted(
        str(row.get("path", "")) for row in assembly_rows
        if not str(row.get("name", "")).strip()
    )

    inventory_occurrences = {
        str(row.get("occurrence_id", "")).strip(): row
        for row in inventory.get("occurrences", [])
        if isinstance(row, dict) and str(row.get("occurrence_id", "")).strip()
    }
    leaf_parent_mismatches: list[dict[str, Any]] = []
    for row in endpoint.occurrence_rows:
        if not row.get("has_shape"):
            continue
        occurrence_id = str(row.get("occurrence_id", "")).strip()
        authored = inventory_occurrences.get(occurrence_id)
        expected_parent = "" if authored is None else "/".join(
            part for part in str(authored.get("parent_path", "")).strip().strip("/").split("/") if part
        )
        actual_parent = _relative_assembly_path(row.get("parent_path", ""), actual_root)
        if authored is None or actual_parent != expected_parent:
            leaf_parent_mismatches.append({
                "occurrence_id": occurrence_id,
                "imported_path": row.get("path", ""),
                "expected_parent_path": expected_parent,
                "actual_parent_path": actual_parent,
                "inventory_occurrence_present": authored is not None,
            })

    missing_assembly_paths = sorted(set(expected_paths) - set(actual_paths))
    unexpected_assembly_paths = sorted(set(actual_paths) - set(expected_paths))
    missing_top_level_names = sorted(set(expected_top) - set(actual_top))
    unexpected_top_level_names = sorted(set(actual_top) - set(expected_top))
    issues: list[dict[str, Any]] = []
    issues.extend({"code": "HIERARCHY_SCHEMA", "detail": error} for error in schema_errors)
    if len(root_rows) != 1:
        issues.append({"code": "ROOT_NODE_COUNT", "measured": len(root_rows), "required": 1})
    if actual_root != expected_root:
        issues.append({"code": "ROOT_NAME_MISMATCH", "expected": expected_root, "actual": actual_root})
    if not root_shape_free:
        issues.append({"code": "ROOT_IS_NOT_A_SHAPE_FREE_ASSEMBLY"})
    if not root_has_children:
        issues.append({"code": "ROOT_HAS_NO_CHILDREN"})
    if blank_assembly_node_paths:
        issues.append({"code": "BLANK_ASSEMBLY_NODE_NAMES", "paths": blank_assembly_node_paths})
    if missing_top_level_names or unexpected_top_level_names or len(actual_top) != len(expected_top):
        issues.append({
            "code": "TOP_LEVEL_ASSEMBLY_SET_MISMATCH",
            "missing": missing_top_level_names, "unexpected": unexpected_top_level_names,
            "expected_count": len(expected_top), "actual_count": len(actual_top),
        })
    if missing_assembly_paths or unexpected_assembly_paths or len(actual_paths) != len(expected_paths):
        issues.append({
            "code": "ASSEMBLY_PATH_SET_MISMATCH",
            "missing": missing_assembly_paths, "unexpected": unexpected_assembly_paths,
            "expected_count": len(expected_paths), "actual_count": len(actual_paths),
        })
    if leaf_parent_mismatches:
        issues.append({"code": "LEAF_PARENT_PATH_MISMATCH", "rows": leaf_parent_mismatches})

    return {
        "state": endpoint.state,
        "expected_root_name": expected_root, "actual_root_name": actual_root,
        "expected_top_level_assembly_names": sorted(expected_top),
        "actual_top_level_assembly_names": actual_top,
        "expected_assembly_paths": sorted(expected_paths), "actual_assembly_paths": actual_paths,
        "missing_assembly_paths": missing_assembly_paths,
        "unexpected_assembly_paths": unexpected_assembly_paths,
        "leaf_parent_path_mismatch_count": len(leaf_parent_mismatches),
        "leaf_parent_path_mismatches": leaf_parent_mismatches,
        "flattened_or_missing_named_subassembly_tree": not actual_paths or not actual_top,
        "issue_count": len(issues), "issues": issues, "accepted": not issues,
    }


def exact_local_brep_fingerprint(shape: cq.Shape) -> dict[str, Any]:
    """Return deterministic local exact-BREP evidence with tessellation excluded."""
    stream = io.BytesIO()
    BRepTools.Write_s(
        shape.wrapped, stream, False, False,
        TopTools_FormatVersion.TopTools_FormatVersion_VERSION_3,
    )
    payload = stream.getvalue()
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "serialized_bytes": len(payload),
        "bbox_mm": list(bbox_raw(shape.wrapped)),
        "surface_types": surface_counts(shape.wrapped),
    }


def write_occurrence_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "state", "path", "parent_path", "depth", "name", "occurrence_id", "part_number",
        "classification", "has_shape", "is_leaf", "child_count", "local_transform_identity",
        "absolute_transform_identity", "mapped_to_authoring_inventory", "solid_count", "face_count",
        "volume_mm3", "valid", "bbox_mm", "surface_types", "local_transform_3x4",
        "absolute_transform_3x4",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            cooked = {k: row.get(k, "") for k in fields}
            for key in ("bbox_mm", "surface_types", "local_transform_3x4", "absolute_transform_3x4"):
                if cooked.get(key) != "":
                    cooked[key] = json.dumps(cooked[key], separators=(",", ":"))
            writer.writerow(cooked)


def write_solid_csv(path: Path, solids: list[SolidRecord]) -> None:
    fields = [
        "state", "solid_key", "occurrence_id", "solid_index", "part_number", "classification",
        "valid", "volume_mm3", "face_count", "surface_types", "bbox_mm",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for s in solids:
            writer.writerow({
                "state": s.state, "solid_key": s.solid_key, "occurrence_id": s.occurrence_id,
                "solid_index": s.solid_index, "part_number": s.part_number,
                "classification": s.classification, "valid": s.valid,
                "volume_mm3": repr(s.volume_mm3), "face_count": s.face_count,
                "surface_types": json.dumps(s.surface_types, separators=(",", ":")),
                "bbox_mm": json.dumps(bbox_dict(s.bbox), separators=(",", ":")),
            })


def exact_common(a: Any, b: Any) -> tuple[str, float | None, str]:
    try:
        operation = BRepAlgoAPI_Common(a, b)
        operation.SetNonDestructive(True)
        operation.SetRunParallel(False)
        operation.Build()
        if not operation.IsDone():
            return "NOT_DONE", None, "BRepAlgoAPI_Common.IsDone() returned false"
        return "DONE", volume_raw(operation.Shape()), ""
    except Exception as exc:  # evidence must preserve, not hide, kernel failures
        return "ERROR", None, f"{type(exc).__name__}: {exc}"


def exact_common_full_volume_equivalence(
    a: Any, b: Any, volume_tolerance_mm3: float = 1.0e-5,
) -> dict[str, Any]:
    """Prove two exact BREP shapes occupy the same full local volume."""
    volume_a = volume_raw(a)
    volume_b = volume_raw(b)
    common_status, common_volume, common_error = exact_common(a, b)
    a_minus_common = None if common_volume is None else volume_a - common_volume
    b_minus_common = None if common_volume is None else volume_b - common_volume
    equivalent = bool(
        common_status == "DONE"
        and common_volume is not None
        and abs(volume_a - volume_b) <= volume_tolerance_mm3
        and abs(a_minus_common) <= volume_tolerance_mm3
        and abs(b_minus_common) <= volume_tolerance_mm3
    )
    return {
        "status": common_status,
        "volume_a_mm3": volume_a,
        "volume_b_mm3": volume_b,
        "common_volume_mm3": common_volume,
        "a_minus_common_mm3": a_minus_common,
        "b_minus_common_mm3": b_minus_common,
        "volume_tolerance_mm3": volume_tolerance_mm3,
        "equivalent": equivalent,
        "error": common_error,
    }


def exact_distance(a: Any, b: Any) -> tuple[str, float | None, str]:
    try:
        distance = BRepExtrema_DistShapeShape(a, b)
        distance.Perform()
        if not distance.IsDone():
            return "NOT_DONE", None, "BRepExtrema_DistShapeShape.IsDone() returned false"
        return "DONE", float(distance.Value()), ""
    except Exception as exc:
        return "ERROR", None, f"{type(exc).__name__}: {exc}"


def connection_pairs(inventory: dict[str, Any]) -> set[frozenset[str]]:
    occurrence_ids = {o["occurrence_id"] for o in inventory["occurrences"]}
    records = inventory.get("attachment_requirements", [])
    return {
        frozenset((c.get("occurrence_id", c.get("occurrence_a")), c.get("mate_occurrence_id", c.get("occurrence_b"))))
        for c in records
        if c.get("occurrence_id", c.get("occurrence_a")) in occurrence_ids
        and c.get("mate_occurrence_id", c.get("occurrence_b")) in occurrence_ids
        and c.get("occurrence_id", c.get("occurrence_a")) != c.get("mate_occurrence_id", c.get("occurrence_b"))
    }


def _fit_states(record: dict[str, Any]) -> set[str]:
    raw = record.get("states", record.get("state", ""))
    if isinstance(raw, str):
        values = [value.strip().upper() for value in re.split(r"[,;|]", raw) if value.strip()]
    elif isinstance(raw, list):
        values = [str(value).strip().upper() for value in raw if str(value).strip()]
    else:
        values = []
    expanded: set[str] = set()
    for value in values:
        if value == "BOTH":
            expanded.update(("STOWED", "DEPLOYED"))
        elif value == "ALL":
            expanded.update(("STOWED", "DEPLOYED", "MOTION"))
        else:
            expanded.add(value)
    return expanded


def _canonical_fit_scope(
    occurrence_a: str, solid_a: int | None, occurrence_b: str, solid_b: int | None,
) -> tuple[str, int | None, str, int | None]:
    left = (occurrence_a, -1 if solid_a is None else solid_a)
    right = (occurrence_b, -1 if solid_b is None else solid_b)
    if left <= right:
        return occurrence_a, solid_a, occurrence_b, solid_b
    return occurrence_b, solid_b, occurrence_a, solid_a


def validated_intentional_fits(
    inventory: dict[str, Any], state: str,
) -> dict[str, Any]:
    """Validate the bounded occurrence/solid-pair exception register.

    A connection is never an interference exception.  A positive common is
    documented only when a state-applicable register row names the exact
    occurrence pair, provides finite inclusive volume bounds, and supplies a
    nonblank manufacturing/process basis.  Same-occurrence exceptions must
    additionally identify both solid indices so that a whole multibody part
    cannot be exempted by a blanket row.
    """
    occurrence_ids = {o["occurrence_id"] for o in inventory.get("occurrences", [])}
    raw_records = inventory.get("intentional_fits", [])
    errors: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, source in enumerate(raw_records, start=1):
        record = dict(source)
        exception_id = str(record.get("exception_id", "")).strip()
        record_errors: list[str] = []
        states = _fit_states(record)
        if not exception_id:
            record_errors.append("missing exception_id")
            exception_id = f"UNNAMED-{index:03d}"
        elif exception_id in seen_ids:
            record_errors.append("duplicate exception_id")
        seen_ids.add(exception_id)
        if not states or not states.issubset({"STOWED", "DEPLOYED", "MOTION"}):
            record_errors.append("state/states must resolve only to STOWED, DEPLOYED, and/or MOTION")
        a = str(record.get("occurrence_a", "")).strip()
        b = str(record.get("occurrence_b", "")).strip()
        if not a or not b:
            record_errors.append("occurrence_a and occurrence_b are required")
        for occurrence_id in (a, b):
            if occurrence_id and occurrence_id not in occurrence_ids:
                record_errors.append(f"unknown occurrence: {occurrence_id}")
        solid_a_raw = record.get("solid_index_a")
        solid_b_raw = record.get("solid_index_b")
        try:
            solid_a = None if solid_a_raw in (None, "") else int(solid_a_raw)
            solid_b = None if solid_b_raw in (None, "") else int(solid_b_raw)
            if solid_a is not None and solid_a < 1:
                raise ValueError
            if solid_b is not None and solid_b < 1:
                raise ValueError
        except (TypeError, ValueError):
            solid_a = solid_b = None
            record_errors.append("solid indices must be positive integers when supplied")
        if a == b and (solid_a is None or solid_b is None or solid_a == solid_b):
            record_errors.append("same-occurrence exception requires two distinct solid indices")
        min_raw = record.get("minimum_common_volume_mm3", record.get("min_common_volume_mm3"))
        max_raw = record.get("maximum_common_volume_mm3", record.get("max_common_volume_mm3"))
        try:
            min_volume = float(min_raw)
            max_volume = float(max_raw)
            if not math.isfinite(min_volume) or not math.isfinite(max_volume):
                raise ValueError
            if min_volume < 0.0 or max_volume < min_volume:
                raise ValueError
        except (TypeError, ValueError):
            min_volume = max_volume = math.nan
            record_errors.append("finite 0 <= minimum_common_volume_mm3 <= maximum_common_volume_mm3 is required")
        process_basis = str(record.get("process_basis", "")).strip()
        if not process_basis:
            record_errors.append("nonblank process_basis is required")
        if record_errors:
            errors.append({"exception_id": exception_id, "record_index": index, "errors": record_errors})
            continue
        if state.upper() not in states:
            continue
        candidates.append({
            **record, "exception_id": exception_id, "states_resolved": sorted(states),
            "occurrence_a": a, "occurrence_b": b, "solid_index_a": solid_a,
            "solid_index_b": solid_b, "minimum_common_volume_mm3": min_volume,
            "maximum_common_volume_mm3": max_volume, "process_basis": process_basis,
            "scope": _canonical_fit_scope(a, solid_a, b, solid_b),
        })

    scopes: dict[tuple[str, int | None, str, int | None], list[dict[str, Any]]] = defaultdict(list)
    for record in candidates:
        scopes[record["scope"]].append(record)
    valid_records: list[dict[str, Any]] = []
    for scope, records in scopes.items():
        if len(records) > 1:
            for record in records:
                errors.append({
                    "exception_id": record["exception_id"], "record_index": None,
                    "errors": [f"duplicate state-applicable exception scope: {scope}"],
                })
        else:
            valid_records.append(records[0])
    return {"state": state.upper(), "records": valid_records, "errors": errors}


def match_intentional_fit(
    register: dict[str, Any], occurrence_a: str, solid_a: int,
    occurrence_b: str, solid_b: int, common_volume_mm3: float,
) -> tuple[bool, str, str]:
    exact_scope = _canonical_fit_scope(occurrence_a, solid_a, occurrence_b, solid_b)
    occurrence_scope = _canonical_fit_scope(occurrence_a, None, occurrence_b, None)
    out_of_bounds: list[str] = []
    for record in register["records"]:
        if record["scope"] not in (exact_scope, occurrence_scope):
            continue
        minimum = record["minimum_common_volume_mm3"]
        maximum = record["maximum_common_volume_mm3"]
        if minimum - COMMON_VOLUME_EPS_MM3 <= common_volume_mm3 <= maximum + COMMON_VOLUME_EPS_MM3:
            return True, record["exception_id"], "VALID_BOUNDED_MATCH"
        out_of_bounds.append(
            f"{record['exception_id']} bounds [{minimum}, {maximum}] mm3 do not contain {common_volume_mm3} mm3"
        )
    if out_of_bounds:
        return False, "", "; ".join(out_of_bounds)
    return False, "", "NO_VALID_STATE_SPECIFIC_EXCEPTION"


def audit_endpoint_pairs(endpoint: EndpointData, inventory: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    start = time.time()
    path = out_dir / f"endpoint_pair_audit_{endpoint.state.lower()}.csv.gz"
    positives: list[dict[str, Any]] = []
    clearance_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    min_clearance: float | None = None
    conn_pairs = connection_pairs(inventory)
    fit_register = validated_intentional_fits(inventory, endpoint.state)
    used_exception_ids: set[str] = set()
    total_pairs = len(endpoint.solid_records) * (len(endpoint.solid_records) - 1) // 2

    all_pairs = [
        (pair_index, a, b, aabb_gap(a.bbox, b.bbox))
        for pair_index, (a, b) in enumerate(itertools.combinations(endpoint.solid_records, 2), start=1)
    ]

    with gzip.open(path, "wt", newline="", encoding="utf-8", compresslevel=6) as stream:
        writer = csv.DictWriter(stream, fieldnames=PAIR_FIELDS)
        writer.writeheader()
        pair_index = 0
        for pair_index, a, b, gap in all_pairs:
            overlaps = gap <= AABB_TOL_MM
            direct_connection = frozenset((a.occurrence_id, b.occurrence_id)) in conn_pairs
            documented_exception = False
            exception_id = ""
            exception_match_status = "NOT_APPLICABLE"
            common_status = "NOT_RUN_AABB_SEPARATED"
            common_volume: float | None = 0.0
            distance_status = "NOT_RUN_OUTSIDE_NEAR_LIMIT"
            clearance: float | None = None
            error = ""

            if not a.valid or not b.valid:
                common_status = "BLOCKED_INVALID_OPERAND"
                common_volume = None
                error = "One or both imported solids failed BRepCheck_Analyzer"
            elif overlaps:
                counts["broadphase_candidates"] += 1
                common_status, common_volume, error = exact_common(a.shape, b.shape)

            if common_status in {"ERROR", "NOT_DONE", "BLOCKED_INVALID_OPERAND"}:
                result = "BLOCKED_BOOLEAN"
                errors.append({
                    "state": endpoint.state, "pair_index": pair_index, "occurrence_a": a.occurrence_id,
                    "solid_index_a": a.solid_index, "occurrence_b": b.occurrence_id,
                    "solid_index_b": b.solid_index, "status": common_status, "error": error,
                })
                counts["blocked_pairs"] += 1
            elif common_volume is not None and common_volume > COMMON_VOLUME_EPS_MM3:
                documented_exception, exception_id, exception_match_status = match_intentional_fit(
                    fit_register, a.occurrence_id, a.solid_index,
                    b.occurrence_id, b.solid_index, common_volume,
                )
                if documented_exception:
                    used_exception_ids.add(exception_id)
                result = "UNAUTHORIZED_POSITIVE_VOLUME" if not documented_exception else "DOCUMENTED_POSITIVE_VOLUME"
                clearance = 0.0
                distance_status = "ZERO_BY_POSITIVE_COMMON"
                positive = {
                    "state": endpoint.state, "pair_index": pair_index,
                    "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                    "part_number_a": a.part_number, "classification_a": a.classification,
                    "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                    "part_number_b": b.part_number, "classification_b": b.classification,
                    "same_occurrence": a.occurrence_id == b.occurrence_id,
                    "direct_attachment_connection": direct_connection,
                    "documented_positive_volume_exception": documented_exception,
                    "intentional_fit_exception_id": exception_id,
                    "intentional_fit_match_status": exception_match_status,
                    "common_volume_mm3": common_volume,
                }
                positives.append(positive)
                counts[result] += 1
            else:
                result = "CLEAR_OR_CONTACT"
                counts["clear_pairs"] += 1
                # Every zero-common pair with overlapping AABBs receives an
                # exact OCCT distance result.  Near separated pairs do as well;
                # no AABB-overlap row is converted into a blanket block.
                if gap <= NEAR_DISTANCE_LIMIT_MM:
                    counts["near_noninterfering_candidate_pairs"] += 1
                    distance_status, clearance, dist_error = exact_distance(a.shape, b.shape)
                    if dist_error:
                        error = f"{error}; {dist_error}".strip("; ")
                    if distance_status != "DONE":
                        counts["distance_blocked_pairs"] += 1
                        errors.append({
                            "state": endpoint.state, "pair_index": pair_index,
                            "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                            "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                            "status": f"DISTANCE_{distance_status}", "error": dist_error,
                        })
                    elif clearance is not None:
                        counts["exact_distance_measured_pairs"] += 1
                        min_clearance = clearance if min_clearance is None else min(min_clearance, clearance)

            row = {
                "state": endpoint.state, "pair_index": pair_index,
                "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                "part_number_a": a.part_number, "classification_a": a.classification,
                "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                "part_number_b": b.part_number, "classification_b": b.classification,
                "same_occurrence": a.occurrence_id == b.occurrence_id,
                "direct_attachment_connection": direct_connection,
                "documented_positive_volume_exception": documented_exception,
                "intentional_fit_exception_id": exception_id,
                "intentional_fit_match_status": exception_match_status,
                "aabb_overlap": overlaps, "aabb_gap_mm": repr(gap),
                "exact_common_status": common_status,
                "common_volume_mm3": "" if common_volume is None else repr(common_volume),
                "exact_distance_status": distance_status,
                "exact_clearance_mm": "" if clearance is None else repr(clearance),
                "result": result,
                "bbox_a": json.dumps(bbox_dict(a.bbox), separators=(",", ":")),
                "bbox_b": json.dumps(bbox_dict(b.bbox), separators=(",", ":")),
                "error": error,
            }
            if (
                result in {"UNAUTHORIZED_POSITIVE_VOLUME", "DOCUMENTED_POSITIVE_VOLUME"}
                or distance_status == "DONE"
                or distance_status.startswith("BLOCKED_")
            ):
                clearance_rows.append({
                    "state": endpoint.state, "pair_index": pair_index,
                    "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                    "part_number_a": a.part_number, "occurrence_b": b.occurrence_id,
                    "solid_index_b": b.solid_index, "part_number_b": b.part_number,
                    "direct_attachment_connection": direct_connection,
                    "intentional_fit_exception_id": exception_id,
                    "intentional_fit_match_status": exception_match_status,
                    "aabb_gap_mm": gap, "exact_clearance_status": distance_status,
                    "exact_clearance_mm": clearance, "common_volume_mm3": common_volume,
                    "disposition": result, "error": error,
                })
            writer.writerow(row)

    emitted_pairs = pair_index if total_pairs else 0
    if emitted_pairs != total_pairs:
        raise RuntimeError(f"Pair register row count mismatch for {endpoint.state}")
    return {
        "state": endpoint.state, "solid_count": len(endpoint.solid_records),
        "unordered_pair_count": total_pairs, "pair_register": str(path),
        "broadphase_candidate_count": counts["broadphase_candidates"],
        "clear_pair_count": counts["clear_pairs"],
        "unauthorized_positive_volume_pair_count": counts["UNAUTHORIZED_POSITIVE_VOLUME"],
        "documented_positive_volume_pair_count": counts["DOCUMENTED_POSITIVE_VOLUME"],
        "boolean_blocked_pair_count": counts["blocked_pairs"],
        "distance_blocked_pair_count": counts["distance_blocked_pairs"],
        "near_noninterfering_candidate_pair_count": counts["near_noninterfering_candidate_pairs"],
        "exact_distance_measured_pair_count": counts["exact_distance_measured_pairs"],
        "intentional_fit_register_valid_record_count": len(fit_register["records"]),
        "intentional_fit_register_errors": fit_register["errors"],
        "intentional_fit_register_error_count": len(fit_register["errors"]),
        "used_intentional_fit_exception_ids": sorted(used_exception_ids),
        "unused_intentional_fit_exception_ids": sorted(
            record["exception_id"] for record in fit_register["records"]
            if record["exception_id"] not in used_exception_ids
        ),
        "minimum_exact_noninterfering_clearance_mm": min_clearance,
        "positive_rows": positives, "boolean_or_distance_errors": errors,
        "critical_clearance_rows": clearance_rows,
        "elapsed_seconds": time.time() - start,
    }


def occurrence_solid_lookup(endpoint: EndpointData) -> dict[str, list[SolidRecord]]:
    result: dict[str, list[SolidRecord]] = defaultdict(list)
    for solid in endpoint.solid_records:
        result[solid.occurrence_id].append(solid)
    return result


def minimum_occurrence_distance(
    solids_by_occurrence: dict[str, list[SolidRecord]], occurrence_a: str, occurrence_b: str,
) -> tuple[str, float | None, str]:
    solids_a = solids_by_occurrence.get(occurrence_a, [])
    solids_b = solids_by_occurrence.get(occurrence_b, [])
    if not solids_a or not solids_b:
        missing = [occ for occ, solids in ((occurrence_a, solids_a), (occurrence_b, solids_b)) if not solids]
        return "MISSING_OCCURRENCE_GEOMETRY", None, f"No imported solid geometry for: {', '.join(missing)}"
    candidates = sorted(
        ((aabb_gap(a.bbox, b.bbox), a, b) for a in solids_a for b in solids_b),
        key=lambda item: item[0],
    )
    best = math.inf
    errors: list[str] = []
    completed = 0
    for lower_bound, solid_a, solid_b in candidates:
        if lower_bound > best + AABB_TOL_MM:
            break
        status, distance, error = exact_distance(solid_a.shape, solid_b.shape)
        if status != "DONE" or distance is None:
            errors.append(
                f"{solid_a.solid_key}<>{solid_b.solid_key}: {status}: {error}"
            )
            continue
        completed += 1
        best = min(best, distance)
        if best <= AABB_TOL_MM:
            break
    if completed:
        return "DONE", best, "; ".join(errors)
    return "BLOCKED", None, "; ".join(errors) or "No exact distance result"


def _id_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def authoring_connectivity(
    inventory: dict[str, Any], state: str, out_dir: Path, endpoint: EndpointData,
) -> dict[str, Any]:
    occurrences = {o["occurrence_id"]: o for o in inventory["occurrences"]}
    solids_by_occurrence = occurrence_solid_lookup(endpoint)
    valid_neighbors: dict[str, set[str]] = defaultdict(set)
    connection_ids: dict[str, list[str]] = defaultdict(list)
    dangling: list[dict[str, Any]] = []
    self_connections: list[str] = []
    generic_evidence: list[str] = []
    graph: dict[str, set[str]] = defaultdict(set)
    structural_graph: dict[str, set[str]] = defaultdict(set)
    generic_patterns = ("AUTO-SPEC", "Occurrence-specific hardware named in BOM/joint record")
    connection_geometry_rows: list[dict[str, Any]] = []
    invalid_attachment_connections: list[str] = []
    passed_connection_pairs: set[frozenset[str]] = set()
    attachment_records = inventory.get("attachment_requirements", [])
    if not isinstance(attachment_records, list):
        attachment_records = []
    attachment_source = "attachment_requirements"
    invalid_attachment_record_indices = [
        index for index, row in enumerate(attachment_records, start=1)
        if not isinstance(row, dict)
    ]
    attachment_id_values = [
        str(row.get("attachment_id", row.get("connection_id", ""))).strip()
        if isinstance(row, dict) else ""
        for row in attachment_records
    ]
    blank_attachment_id_record_indices = [
        index for index, value in enumerate(attachment_id_values, start=1) if not value
    ]
    duplicate_attachment_ids = sorted(
        value for value, count in Counter(attachment_id_values).items()
        if value and count > 1
    )

    # Coverage is deliberately independent of whether the declared rows later
    # pass their exact-distance/fastener checks. Every installed occurrence
    # must first be named as endpoint A or B in the curated register. Only an
    # explicitly classified internal child, or governed external context, is
    # outside that occurrence-level attachment scope.
    external_ids = set(_id_list(inventory.get("external_context_ids")))
    attachment_endpoint_ids: set[str] = set()
    for source_connection in attachment_records:
        if not isinstance(source_connection, dict):
            continue
        endpoint_a = str(source_connection.get(
            "occurrence_id", source_connection.get("occurrence_a", "")
        )).strip()
        endpoint_b = str(source_connection.get(
            "mate_occurrence_id", source_connection.get("occurrence_b", "")
        )).strip()
        if endpoint_a:
            attachment_endpoint_ids.add(endpoint_a)
        if endpoint_b:
            attachment_endpoint_ids.add(endpoint_b)
    attachment_coverage_exempt_ids = {
        occurrence_id for occurrence_id, occurrence in occurrences.items()
        if occurrence_id in external_ids
        or str(occurrence.get("classification", "")).strip().upper()
        in {"INTERNAL_CHILD", "EXTERNAL_CONTEXT"}
    }
    attachment_coverage_required_ids = set(occurrences) - attachment_coverage_exempt_ids
    uncovered_attachment_endpoint_ids = sorted(
        attachment_coverage_required_ids - attachment_endpoint_ids
    )

    for connection_index, source_connection in enumerate(attachment_records, start=1):
        if not isinstance(source_connection, dict):
            continue
        connection = dict(source_connection)
        connection_id = str(
            connection.get("attachment_id", connection.get("connection_id", f"ATTACHMENT-{connection_index:03d}"))
        ).strip()
        connection["connection_id"] = connection_id
        connection["occurrence_id"] = connection.get("occurrence_id", connection.get("occurrence_a", ""))
        connection["mate_occurrence_id"] = connection.get("mate_occurrence_id", connection.get("occurrence_b", ""))
        connection["connection_type"] = connection.get("connection_type", connection.get("attachment_type", ""))
        connection["maximum_attachment_gap_mm"] = connection.get(
            "maximum_attachment_gap_mm", connection.get("maximum_separation_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM)
        )
        connection["retaining_occurrence_ids"] = connection.get(
            "retaining_occurrence_ids",
            connection.get("fastener_occurrence_ids", connection.get("hardware_occurrence_ids", [])),
        )
        connection["process_basis"] = connection.get(
            "process_basis", connection.get("evidence_basis", connection.get("evidence", ""))
        )
        a = str(connection["occurrence_id"]).strip()
        b = str(connection["mate_occurrence_id"]).strip()
        connection["occurrence_id"], connection["mate_occurrence_id"] = a, b
        connection_ids[a].append(connection["connection_id"])
        if any(p in connection["connection_id"] or p in connection.get("evidence", "") for p in generic_patterns):
            generic_evidence.append(connection["connection_id"])
        if a == b:
            self_connections.append(connection["connection_id"])
            continue
        if a not in occurrences or b not in occurrences:
            dangling.append({
                "connection_id": connection["connection_id"], "occurrence_id": a,
                "mate_occurrence_id": b, "missing": [x for x in (a, b) if x not in occurrences],
            })
            continue
        maximum_gap = float(connection.get("maximum_attachment_gap_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM))
        direct_status, direct_gap, direct_error = minimum_occurrence_distance(solids_by_occurrence, a, b)
        direct_supported = direct_status == "DONE" and direct_gap is not None and direct_gap <= maximum_gap + AABB_TOL_MM
        retainer_ids = _id_list(
            connection.get("retaining_occurrence_ids", connection.get("fastener_occurrence_ids"))
        )
        retainer_results: list[dict[str, Any]] = []
        hardware_graph: dict[str, set[str]] = defaultdict(set)
        for retainer_id in retainer_ids:
            if retainer_id not in occurrences:
                retainer_results.append({"occurrence_id": retainer_id, "status": "MISSING"})
                continue
            status_a, gap_a, error_a = minimum_occurrence_distance(solids_by_occurrence, retainer_id, a)
            status_b, gap_b, error_b = minimum_occurrence_distance(solids_by_occurrence, retainer_id, b)
            bridges = (
                status_a == status_b == "DONE" and gap_a is not None and gap_b is not None
                and gap_a <= maximum_gap + AABB_TOL_MM and gap_b <= maximum_gap + AABB_TOL_MM
            )
            if status_a == "DONE" and gap_a is not None and gap_a <= maximum_gap + AABB_TOL_MM:
                hardware_graph[a].add(retainer_id)
                hardware_graph[retainer_id].add(a)
            if status_b == "DONE" and gap_b is not None and gap_b <= maximum_gap + AABB_TOL_MM:
                hardware_graph[b].add(retainer_id)
                hardware_graph[retainer_id].add(b)
            retainer_results.append({
                "occurrence_id": retainer_id, "status_to_a": status_a, "gap_to_a_mm": gap_a,
                "status_to_b": status_b, "gap_to_b_mm": gap_b, "bridges_pair": bridges,
                "error": "; ".join(value for value in (error_a, error_b) if value),
            })
        for retainer_a, retainer_b in itertools.combinations(retainer_ids, 2):
            if retainer_a not in occurrences or retainer_b not in occurrences:
                continue
            status, gap, _ = minimum_occurrence_distance(solids_by_occurrence, retainer_a, retainer_b)
            if status == "DONE" and gap is not None and gap <= maximum_gap + AABB_TOL_MM:
                hardware_graph[retainer_a].add(retainer_b)
                hardware_graph[retainer_b].add(retainer_a)
        fastener_supported = False
        queue = deque([a])
        seen_hardware = {a}
        while queue:
            node = queue.popleft()
            if node == b:
                fastener_supported = True
                break
            for neighbor in hardware_graph[node]:
                if neighbor not in seen_hardware:
                    seen_hardware.add(neighbor)
                    queue.append(neighbor)
        if attachment_source == "attachment_requirements":
            feature_definition_complete = bool(
                str(connection.get("connection_type", "")).strip()
                and str(connection.get("process_basis", "")).strip()
            )
        else:
            feature_definition_complete = bool(
                str(connection.get("own_feature_id", "")).strip()
                and str(connection.get("mate_feature_id", "")).strip()
                and str(connection.get("process_basis", connection.get("evidence", ""))).strip()
            )
        generic_row = any(
            p in connection.get("connection_id", "") or p in connection.get("evidence", "")
            for p in generic_patterns
        )
        supported = (direct_supported or fastener_supported) and feature_definition_complete and not generic_row
        support_mode = "DIRECT_GEOMETRIC" if direct_supported else (
            "FASTENER_BRIDGE" if fastener_supported else "UNSUPPORTED"
        )
        connection_geometry_rows.append({
            "state": state, "connection_id": connection["connection_id"],
            "occurrence_id": a, "mate_occurrence_id": b,
            "maximum_attachment_gap_mm": maximum_gap, "direct_distance_status": direct_status,
            "direct_gap_mm": direct_gap, "retaining_occurrence_ids": retainer_ids,
            "retainer_results": retainer_results, "feature_definition_complete": feature_definition_complete,
            "support_mode": support_mode, "geometric_or_fastener_supported": supported,
            "error": direct_error,
        })
        if not supported:
            invalid_attachment_connections.append(connection["connection_id"])
            continue
        passed_connection_pairs.add(frozenset((a, b)))
        valid_neighbors[a].add(b)
        valid_neighbors[b].add(a)
        graph[a].add(b)
        graph[b].add(a)
        connection_type = connection.get("connection_type", "").upper()
        if bool(connection.get("structural_load_path", False)) or any(
            token in connection_type for token in ("STRUCTURAL", "CLOSED_SPLICE", "STITCHED", "RF_WELD", "PINNED")
        ):
            structural_graph[a].add(b)
            structural_graph[b].add(a)

    connection_fields = [
        "state", "connection_id", "occurrence_id", "mate_occurrence_id",
        "maximum_attachment_gap_mm", "direct_distance_status", "direct_gap_mm",
        "retaining_occurrence_ids", "retainer_results", "feature_definition_complete",
        "support_mode", "geometric_or_fastener_supported", "error",
    ]
    with (out_dir / f"attachment_geometry_{state.lower()}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=connection_fields)
        writer.writeheader()
        for row in connection_geometry_rows:
            cooked = dict(row)
            cooked["retaining_occurrence_ids"] = json.dumps(cooked["retaining_occurrence_ids"], separators=(",", ":"))
            cooked["retainer_results"] = json.dumps(cooked["retainer_results"], separators=(",", ":"))
            writer.writerow(cooked)

    route_rows: list[dict[str, Any]] = []
    failed_routes: list[str] = []
    route_records = inventory.get("routes", [])
    if not isinstance(route_records, list):
        route_records = []
    invalid_route_record_indices = [
        index for index, row in enumerate(route_records, start=1)
        if not isinstance(row, dict)
    ]
    route_id_values = [
        str(row.get("route_occurrence_id", "")).strip() if isinstance(row, dict) else ""
        for row in route_records
    ]
    blank_route_id_record_indices = [
        index for index, value in enumerate(route_id_values, start=1) if not value
    ]
    duplicate_route_ids = sorted(
        value for value, count in Counter(route_id_values).items()
        if value and count > 1
    )
    for route in route_records:
        if not isinstance(route, dict):
            continue
        route_id = str(route.get("route_occurrence_id", "")).strip()
        issues: list[str] = []
        endpoint_results: dict[str, Any] = {}
        if route_id not in occurrences:
            issues.append(f"route occurrence missing: {route_id or '<blank>'}")
        maximum_endpoint_gap = float(route.get("maximum_endpoint_gap_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM))
        for side in ("origin", "destination"):
            declared = str(route.get(f"{side}_occurrence", "")).strip()
            interface = str(route.get(f"{side}_interface_occurrence", declared)).strip()
            explicit_external = bool(route.get(f"{side}_external_boundary", False)) and declared in external_ids
            side_result: dict[str, Any] = {
                "declared_occurrence": declared, "interface_occurrence": interface,
                "explicit_external_boundary": explicit_external,
            }
            if explicit_external:
                side_result["status"] = "EXPLICIT_EXTERNAL_BOUNDARY"
            elif declared not in occurrences:
                side_result["status"] = "MISSING_DECLARED_ENDPOINT"
                issues.append(f"{side} endpoint missing or not explicitly external: {declared or '<blank>'}")
            elif interface not in occurrences:
                side_result["status"] = "MISSING_INTERFACE_OCCURRENCE"
                issues.append(f"{side} interface occurrence missing: {interface or '<blank>'}")
            elif route_id not in occurrences:
                side_result["status"] = "ROUTE_GEOMETRY_MISSING"
            else:
                status, gap, error = minimum_occurrence_distance(solids_by_occurrence, route_id, interface)
                interface_connected = interface == declared or frozenset((interface, declared)) in passed_connection_pairs
                terminated = (
                    status == "DONE" and gap is not None and gap <= maximum_endpoint_gap + AABB_TOL_MM
                    and interface_connected
                )
                side_result.update({
                    "distance_status": status, "gap_mm": gap,
                    "maximum_gap_mm": maximum_endpoint_gap,
                    "interface_connected_to_declared_endpoint": interface_connected,
                    "status": "TERMINATED" if terminated else "NOT_TERMINATED", "error": error,
                })
                if not terminated:
                    issues.append(
                        f"{side} route termination failed: route={route_id}, interface={interface}, "
                        f"gap={gap}, status={status}, interface_connected={interface_connected}"
                    )
            endpoint_results[side] = side_result

        termination_ids = _id_list(route.get("termination_occurrence_ids"))
        integral_termination = bool(route.get("integral_terminations", False))
        termination_basis = str(route.get("termination_process_basis", "")).strip()
        termination_results: list[dict[str, Any]] = []
        if not termination_ids and not (integral_termination and termination_basis):
            issues.append("no explicit termination_occurrence_ids or controlled integral-termination process basis")
        for termination_id in termination_ids:
            status, gap, error = minimum_occurrence_distance(solids_by_occurrence, route_id, termination_id)
            accepted = status == "DONE" and gap is not None and gap <= maximum_endpoint_gap + AABB_TOL_MM
            termination_results.append({
                "occurrence_id": termination_id, "distance_status": status, "gap_mm": gap,
                "accepted": accepted, "error": error,
            })
            if termination_id not in occurrences or not accepted:
                issues.append(f"termination fitting is missing or not engaged: {termination_id}")

        support_ids = _id_list(route.get("support_occurrence_ids"))
        integral_support = bool(route.get("integral_support", False))
        support_basis = str(route.get("support_process_basis", "")).strip()
        maximum_support_gap = float(route.get("maximum_support_gap_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM))
        support_results: list[dict[str, Any]] = []
        if not support_ids and not (integral_support and support_basis):
            issues.append("no explicit support_occurrence_ids or controlled integral-support process basis")
        for support_id in support_ids:
            status, gap, error = minimum_occurrence_distance(solids_by_occurrence, route_id, support_id)
            accepted = status == "DONE" and gap is not None and gap <= maximum_support_gap + AABB_TOL_MM
            support_results.append({
                "occurrence_id": support_id, "distance_status": status, "gap_mm": gap,
                "accepted": accepted, "error": error,
            })
            if support_id not in occurrences or not accepted:
                issues.append(f"route support is missing or not geometrically engaged: {support_id}")

        penetration_ids = _id_list(route.get("penetration_occurrence_ids"))
        integral_penetrations = bool(route.get("integral_penetrations", False))
        penetration_basis = str(route.get("penetration_process_basis", "")).strip()
        penetration_results: list[dict[str, Any]] = []
        if not penetration_ids and not (integral_penetrations and penetration_basis):
            issues.append("no explicit penetration_occurrence_ids or controlled integral-penetration process basis")
        for penetration_id in penetration_ids:
            status, gap, error = minimum_occurrence_distance(solids_by_occurrence, route_id, penetration_id)
            accepted = status == "DONE" and gap is not None and gap <= maximum_support_gap + AABB_TOL_MM
            penetration_results.append({
                "occurrence_id": penetration_id, "distance_status": status, "gap_mm": gap,
                "accepted": accepted, "error": error,
            })
            if penetration_id not in occurrences or not accepted:
                issues.append(f"route penetration hardware is missing or not geometrically engaged: {penetration_id}")
        route_status = "PASS" if not issues else "FAIL"
        if route_status != "PASS":
            failed_routes.append(route_id or "<blank>")
        route_rows.append({
            "state": state, "route_occurrence_id": route_id, "status": route_status,
            "endpoint_results": endpoint_results, "termination_results": termination_results,
            "support_results": support_results, "penetration_results": penetration_results, "issues": issues,
        })
    route_fields = [
        "state", "route_occurrence_id", "status", "endpoint_results",
        "termination_results", "support_results", "penetration_results", "issues",
    ]
    with (out_dir / f"route_termination_audit_{state.lower()}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=route_fields)
        writer.writeheader()
        for row in route_rows:
            writer.writerow({
                **row,
                "endpoint_results": json.dumps(row["endpoint_results"], separators=(",", ":")),
                "termination_results": json.dumps(row["termination_results"], separators=(",", ":")),
                "support_results": json.dumps(row["support_results"], separators=(",", ":")),
                "penetration_results": json.dumps(row["penetration_results"], separators=(",", ":")),
                "issues": json.dumps(row["issues"], separators=(",", ":")),
            })

    fields = [
        "state", "occurrence_id", "part_number", "classification", "joint_type",
        "permitted_dof", "valid_attachment_degree", "valid_mates", "connection_ids",
        "floating_rigid", "identity_transform", "identity_justification_present",
    ]
    rows: list[dict[str, Any]] = []
    floating: list[str] = []
    for occurrence_id in sorted(occurrences):
        occurrence = occurrences[occurrence_id]
        rigid = occurrence["classification"] in {"FIXED", "MOVING"}
        degree = len(valid_neighbors[occurrence_id])
        is_floating = rigid and degree == 0
        if is_floating:
            floating.append(occurrence_id)
        row = {
            "state": state, "occurrence_id": occurrence_id,
            "part_number": occurrence["part_number"], "classification": occurrence["classification"],
            "joint_type": occurrence["joint_type"], "permitted_dof": occurrence["permitted_dof"],
            "valid_attachment_degree": degree,
            "valid_mates": ";".join(sorted(valid_neighbors[occurrence_id])),
            "connection_ids": ";".join(sorted(connection_ids[occurrence_id])),
            "floating_rigid": is_floating, "identity_transform": occurrence["identity_transform"],
            "identity_justification_present": bool(occurrence.get("notes", "").strip()) if occurrence["identity_transform"] else True,
        }
        rows.append(row)
    with (out_dir / f"attachment_connectivity_{state.lower()}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    def shortest_path(start: str, goal: str, path_graph: dict[str, set[str]]) -> list[str] | None:
        if start not in occurrences or goal not in occurrences:
            return None
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        seen = {start}
        while queue:
            node, path = queue.popleft()
            if node == goal:
                return path
            for neighbor in sorted(path_graph[node]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    recovery_path = shortest_path("BODY-HARDPOINT-001", "HARNESS-TERMINAL-001", structural_graph)
    components = 0
    remaining = set(occurrences)
    while remaining:
        components += 1
        seed = next(iter(remaining))
        stack = [seed]
        remaining.remove(seed)
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return {
        "state": state, "occurrence_count": len(occurrences), "connection_count": len(attachment_records),
        "attachment_source": attachment_source,
        "attachment_endpoint_occurrence_count": len(attachment_endpoint_ids & set(occurrences)),
        "attachment_coverage_required_occurrence_count": len(attachment_coverage_required_ids),
        "attachment_coverage_exempt_occurrence_ids": sorted(attachment_coverage_exempt_ids),
        "uncovered_attachment_endpoint_occurrence_ids": uncovered_attachment_endpoint_ids,
        "uncovered_attachment_endpoint_occurrence_count": len(uncovered_attachment_endpoint_ids),
        "invalid_attachment_record_indices": invalid_attachment_record_indices,
        "invalid_attachment_record_count": len(invalid_attachment_record_indices),
        "blank_attachment_id_record_indices": blank_attachment_id_record_indices,
        "blank_attachment_id_count": len(blank_attachment_id_record_indices),
        "duplicate_attachment_ids": duplicate_attachment_ids,
        "duplicate_attachment_id_count": len(duplicate_attachment_ids),
        "attachment_results": connection_geometry_rows,
        "floating_rigid_occurrences": floating, "floating_rigid_count": len(floating),
        "dangling_connections": dangling, "dangling_connection_count": len(dangling),
        "self_connections": self_connections, "self_connection_count": len(self_connections),
        "generic_or_blanket_evidence_connection_ids": sorted(set(generic_evidence)),
        "generic_or_blanket_evidence_count": len(set(generic_evidence)),
        "geometric_or_fastener_unsupported_connection_ids": sorted(set(invalid_attachment_connections)),
        "geometric_or_fastener_unsupported_connection_count": len(set(invalid_attachment_connections)),
        "route_count": len(route_rows),
        "invalid_route_record_indices": invalid_route_record_indices,
        "invalid_route_record_count": len(invalid_route_record_indices),
        "blank_route_id_record_indices": blank_route_id_record_indices,
        "blank_route_id_count": len(blank_route_id_record_indices),
        "duplicate_route_ids": duplicate_route_ids,
        "duplicate_route_id_count": len(duplicate_route_ids),
        "failed_route_occurrence_ids": sorted(set(failed_routes)),
        "failed_route_count": len(set(failed_routes)), "route_results": route_rows,
        "graph_component_count_including_flexible_and_consumed": components,
        "body_hardpoint_to_harness_terminal_path": recovery_path,
        "continuous_recovery_load_path_found": recovery_path is not None,
    }


def definition_of_done_audit(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]],
    connectivity: dict[str, dict[str, Any]], out_dir: Path,
) -> dict[str, Any]:
    """Calculate mechanically-complete DoD evidence from authoring records and B-reps.

    The authoring inventory declares the finite scope; it cannot declare the
    result. Every claimed occurrence must independently survive clean XCAF
    reimport as a valid positive-volume solid with positive resolved mass.
    Attachments, route closures, and endpoint engagements are accepted only
    from exact-distance evidence calculated by this validator.
    """

    def audit_state(state: str) -> dict[str, Any]:
        inventory = inventories[state]
        endpoint = endpoints[state]
        requirements = inventory.get("definition_of_done_requirements")
        failures: list[dict[str, Any]] = []
        blocked: list[dict[str, Any]] = []
        occurrence_checks: dict[str, dict[str, Any]] = {}
        engagement_checks: list[dict[str, Any]] = []
        attachment_checks: list[dict[str, Any]] = []
        route_checks: list[dict[str, Any]] = []
        pressure_topology_checks: list[dict[str, Any]] = []
        motion_track_checks: list[dict[str, Any]] = []

        inventory_occurrences = {
            str(row.get("occurrence_id", "")).strip(): row
            for row in inventory.get("occurrences", [])
            if str(row.get("occurrence_id", "")).strip()
        }
        imported_occurrences = leaf_lookup(endpoint)
        part_definitions = {
            str(row.get("part_number", "")).strip(): row
            for row in inventory.get("parts", [])
            if str(row.get("part_number", "")).strip()
        }
        mass_overrides = inventory.get("mass_overrides_kg", {})
        solids_by_occurrence = occurrence_solid_lookup(endpoint)
        attachment_results = {
            str(row.get("connection_id", "")).strip(): row
            for row in connectivity[state].get("attachment_results", [])
            if str(row.get("connection_id", "")).strip()
        }
        route_results = {
            str(row.get("route_occurrence_id", "")).strip(): row
            for row in connectivity[state].get("route_results", [])
            if str(row.get("route_occurrence_id", "")).strip()
        }
        route_definition_rows = inventory.get("routes", [])
        if not isinstance(route_definition_rows, list):
            route_definition_rows = []
        invalid_route_definition_record_indices = [
            index for index, row in enumerate(route_definition_rows, start=1)
            if not isinstance(row, dict)
        ]
        route_definition_id_values = [
            str(row.get("route_occurrence_id", "")).strip() if isinstance(row, dict) else ""
            for row in route_definition_rows
        ]
        blank_route_definition_record_indices = [
            index for index, value in enumerate(route_definition_id_values, start=1)
            if not value
        ]
        duplicate_route_definition_ids = sorted(
            value for value, count in Counter(route_definition_id_values).items()
            if value and count > 1
        )
        route_definitions = {
            str(row.get("route_occurrence_id", "")).strip(): row
            for row in route_definition_rows
            if isinstance(row, dict) and str(row.get("route_occurrence_id", "")).strip()
        }
        motion_tracks = {
            str(row.get("motion_track_id", row.get("track_id", row.get("occurrence_id", "")))).strip(): row
            for row in inventory.get("motion_tracks", [])
            if str(row.get("motion_track_id", row.get("track_id", row.get("occurrence_id", "")))).strip()
        }

        def fail(code: str, **details: Any) -> None:
            failures.append({"code": code, **details})

        def block(code: str, **details: Any) -> None:
            blocked.append({"code": code, **details})

        def required_list(owner: dict[str, Any], key: str, context: str) -> list[str]:
            raw = owner.get(key)
            if not isinstance(raw, list) or not raw:
                fail("REQUIRED_NONEMPTY_LIST_MISSING", context=context, field=key)
                return []
            values = [str(value).strip() for value in raw]
            if any(not value for value in values):
                fail("BLANK_IDENTIFIER", context=context, field=key)
            nonblank = [value for value in values if value]
            duplicates = sorted(value for value, count in Counter(nonblank).items() if count > 1)
            if duplicates:
                fail("DUPLICATE_IDENTIFIER", context=context, field=key, identifiers=duplicates)
            return nonblank

        def occurrence_check(occurrence_id: str, context: str) -> dict[str, Any]:
            if occurrence_id in occurrence_checks:
                check = occurrence_checks[occurrence_id]
                check["contexts"] = sorted(set(check["contexts"] + [context]))
                return check
            authored = inventory_occurrences.get(occurrence_id)
            imported = imported_occurrences.get(occurrence_id)
            part_number = str(authored.get("part_number", "")).strip() if authored else ""
            part = part_definitions.get(part_number)
            raw_mass = mass_overrides.get(occurrence_id) if isinstance(mass_overrides, dict) else None
            if raw_mass is None and part is not None:
                raw_mass = part.get("mass_kg")
            try:
                resolved_mass = float(raw_mass)
            except (TypeError, ValueError):
                resolved_mass = None
            check = {
                "occurrence_id": occurrence_id, "contexts": [context],
                "authoring_occurrence_present": authored is not None,
                "ap242_occurrence_present": imported is not None,
                "part_number": part_number,
                "part_definition_present": part is not None,
                "solid_count": 0 if imported is None else int(imported.get("solid_count", 0)),
                "valid_brep": False if imported is None else bool(imported.get("valid", False)),
                "volume_mm3": None if imported is None else imported.get("volume_mm3"),
                "resolved_mass_kg": resolved_mass,
            }
            occurrence_checks[occurrence_id] = check
            if authored is None:
                fail("AUTHORING_OCCURRENCE_MISSING", context=context, occurrence_id=occurrence_id)
            if imported is None:
                fail("AP242_OCCURRENCE_MISSING", context=context, occurrence_id=occurrence_id)
            elif (
                int(imported.get("solid_count", 0)) <= 0
                or not bool(imported.get("valid", False))
                or float(imported.get("volume_mm3", 0.0)) <= 0.0
            ):
                fail("PHYSICAL_SOLID_EVIDENCE_FAILED", context=context, occurrence_id=occurrence_id)
            if part is None:
                fail("PART_DEFINITION_MISSING", context=context, occurrence_id=occurrence_id, part_number=part_number)
            if resolved_mass is None or not math.isfinite(resolved_mass) or resolved_mass <= 0.0:
                fail("POSITIVE_MASS_MISSING", context=context, occurrence_id=occurrence_id, value=raw_mass)
            return check

        def attachment_check(attachment_id: str, context: str) -> None:
            result = attachment_results.get(attachment_id)
            accepted = bool(result and result.get("geometric_or_fastener_supported"))
            attachment_checks.append({
                "context": context, "attachment_id": attachment_id,
                "calculated_result_present": result is not None, "accepted": accepted,
                "support_mode": None if result is None else result.get("support_mode"),
            })
            if not accepted:
                fail("REQUIRED_ATTACHMENT_EVIDENCE_FAILED", context=context, attachment_id=attachment_id)

        def route_check(route_id: str, context: str) -> None:
            definition = route_definitions.get(route_id)
            result = route_results.get(route_id)
            endpoint_results = {} if result is None else result.get("endpoint_results", {})
            endpoint_failures = [
                side for side in ("origin", "destination")
                if endpoint_results.get(side, {}).get("status")
                not in {"TERMINATED", "EXPLICIT_EXTERNAL_BOUNDARY"}
            ]
            accepted = bool(
                definition is not None and result is not None and result.get("status") == "PASS"
                and not endpoint_failures
            )
            route_checks.append({
                "context": context, "route_occurrence_id": route_id,
                "definition_present": definition is not None,
                "calculated_result_present": result is not None,
                "calculated_status": None if result is None else result.get("status"),
                "endpoint_failures": endpoint_failures, "accepted": accepted,
            })
            occurrence_check(route_id, context)
            if not accepted:
                fail("REQUIRED_ROUTE_CLOSURE_EVIDENCE_FAILED", context=context, route_occurrence_id=route_id)

        def calculated_pressure_graph(
            attachment_ids: Iterable[str], route_ids: Iterable[str],
        ) -> dict[str, set[str]]:
            """Build a row-scoped graph only from calculated exact-supported evidence."""
            graph: dict[str, set[str]] = defaultdict(set)
            for attachment_id in attachment_ids:
                result = attachment_results.get(attachment_id)
                if not result or not result.get("geometric_or_fastener_supported"):
                    continue
                occurrence_a = str(result.get("occurrence_id", "")).strip()
                occurrence_b = str(result.get("mate_occurrence_id", "")).strip()
                if occurrence_a and occurrence_b and occurrence_a != occurrence_b:
                    graph[occurrence_a].add(occurrence_b)
                    graph[occurrence_b].add(occurrence_a)
            for route_id in route_ids:
                definition = route_definitions.get(route_id)
                result = route_results.get(route_id)
                if definition is None or result is None or result.get("status") != "PASS":
                    continue
                endpoint_results = result.get("endpoint_results", {})
                for side in ("origin", "destination"):
                    side_result = endpoint_results.get(side, {})
                    if side_result.get("status") != "TERMINATED":
                        continue
                    declared = str(definition.get(f"{side}_occurrence", "")).strip()
                    interface = str(definition.get(
                        f"{side}_interface_occurrence", declared
                    )).strip()
                    if not interface:
                        continue
                    graph[route_id].add(interface)
                    graph[interface].add(route_id)
                    # A distinct interface is admitted only when connectivity
                    # already accepted its exact-supported attachment to the
                    # declared endpoint. That edge comes from attachment_ids.
                    if declared and declared == interface:
                        graph[route_id].add(declared)
                        graph[declared].add(route_id)
            return graph

        def graph_path(
            graph: dict[str, set[str]], start: str, goal: str,
        ) -> list[str] | None:
            if not start or not goal:
                return None
            queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
            seen = {start}
            while queue:
                node, path = queue.popleft()
                if node == goal:
                    return path
                for neighbor in sorted(graph[node]):
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            return None

        def route_has_exact_supported_endpoints(
            route_id: str, occurrence_a: str, occurrence_b: str,
        ) -> bool:
            definition = route_definitions.get(route_id)
            result = route_results.get(route_id)
            if definition is None or result is None or result.get("status") != "PASS":
                return False
            declared = {
                str(definition.get("origin_occurrence", "")).strip(),
                str(definition.get("destination_occurrence", "")).strip(),
            }
            endpoint_results = result.get("endpoint_results", {})
            return (
                declared == {occurrence_a, occurrence_b}
                and all(
                    endpoint_results.get(side, {}).get("status") == "TERMINATED"
                    for side in ("origin", "destination")
                )
            )

        def motion_track_check(track_id: str, context: str) -> None:
            row = motion_tracks.get(track_id)
            occurrence_id = "" if row is None else str(row.get("occurrence_id", "")).strip()
            accepted = bool(
                row and occurrence_id and str(row.get("mode", "")).strip()
                and str(row.get("process_basis", "")).strip()
            )
            motion_track_checks.append({
                "context": context, "motion_track_id": track_id,
                "definition_present": row is not None, "occurrence_id": occurrence_id,
                "accepted": accepted,
            })
            if row is not None and occurrence_id:
                occurrence_check(occurrence_id, context)
            if not accepted:
                fail("REQUIRED_MOTION_TRACK_EVIDENCE_FAILED", context=context, motion_track_id=track_id)

        def engagement_check(pair: Any, maximum_gap_raw: Any, context: str) -> None:
            if not isinstance(pair, list) or len(pair) != 2 or any(not str(item).strip() for item in pair):
                fail("INVALID_ENGAGEMENT_PAIR", context=context, value=pair)
                return
            occurrence_a, occurrence_b = (str(item).strip() for item in pair)
            occurrence_check(occurrence_a, context)
            occurrence_check(occurrence_b, context)
            try:
                maximum_gap = float(maximum_gap_raw)
            except (TypeError, ValueError):
                maximum_gap = math.nan
            if not math.isfinite(maximum_gap) or maximum_gap < 0.0:
                fail("INVALID_MAXIMUM_ENGAGEMENT_GAP", context=context, value=maximum_gap_raw)
                return
            status, gap, error = minimum_occurrence_distance(solids_by_occurrence, occurrence_a, occurrence_b)
            accepted = status == "DONE" and gap is not None and gap <= maximum_gap + AABB_TOL_MM
            engagement_checks.append({
                "context": context, "occurrence_a": occurrence_a, "occurrence_b": occurrence_b,
                "distance_status": status, "gap_mm": gap, "maximum_gap_mm": maximum_gap,
                "accepted": accepted, "error": error,
            })
            if status != "DONE" or gap is None:
                block(
                    "EXACT_ENGAGEMENT_DISTANCE_BLOCKED", context=context,
                    occurrence_a=occurrence_a, occurrence_b=occurrence_b, error=error,
                )
            elif not accepted:
                fail(
                    "ENGAGEMENT_GAP_EXCEEDED", context=context,
                    occurrence_a=occurrence_a, occurrence_b=occurrence_b,
                    gap_mm=gap, maximum_gap_mm=maximum_gap,
                )

        sections: dict[str, dict[str, Any]] = {}
        if not isinstance(requirements, dict):
            fail("DEFINITION_OF_DONE_REQUIREMENTS_MISSING", state=state)
            requirements = {}

        hardware_start = len(failures), len(blocked)
        required_hardware = required_list(requirements, "required_hardware_occurrence_ids", "required hardware")
        undeclared_installed_occurrences = sorted(set(inventory_occurrences) - set(required_hardware))
        if undeclared_installed_occurrences:
            fail(
                "INSTALLED_OCCURRENCE_SCOPE_INCOMPLETE",
                context="required hardware and installed-item scope",
                occurrence_ids=undeclared_installed_occurrences,
            )
        for occurrence_id in required_hardware:
            occurrence_check(occurrence_id, "required hardware")
        pin_rows = requirements.get("retained_pin_requirements")
        if not isinstance(pin_rows, list) or not pin_rows:
            fail("REQUIRED_NONEMPTY_LIST_MISSING", context="retained pins", field="retained_pin_requirements")
            pin_rows = []
        declared_pin_ids: list[str] = []
        for index, row in enumerate(pin_rows, start=1):
            context = f"retained pin row {index}"
            if not isinstance(row, dict):
                fail("INVALID_REQUIREMENT_ROW", context=context)
                continue
            pin_id = str(row.get("pin_occurrence_id", "")).strip()
            if not pin_id:
                fail("BLANK_IDENTIFIER", context=context, field="pin_occurrence_id")
                continue
            declared_pin_ids.append(pin_id)
            occurrence_check(pin_id, context)
            retention_ids = required_list(row, "retention_occurrence_ids", context)
            support_ids = required_list(row, "support_occurrence_ids", context)
            maximum_gap = row.get("maximum_engagement_gap_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM)
            for occurrence_id in retention_ids + support_ids:
                occurrence_check(occurrence_id, context)
                engagement_check([pin_id, occurrence_id], maximum_gap, context)
        physical_pin_candidates: list[str] = []
        for occurrence_id, authored in inventory_occurrences.items():
            part = part_definitions.get(str(authored.get("part_number", "")).strip(), {})
            occurrence_name = occurrence_id.upper()
            description = str(part.get("description", "")).upper()
            # Occurrence IDs may identify either a PIN or DOWEL directly.  In
            # prose descriptions, however, standalone DOWEL is often an
            # interface adjective (for example, "DOWEL-LOCATED FIXED STOP")
            # and must not turn the mating component into a retained-pin
            # candidate.  Description-only dowel discovery therefore requires
            # the noun phrase DOWEL PIN, while PIN remains sufficient for
            # source items such as WP04-SEAR-001 whose occurrence ID omits it.
            names_a_pin = bool(
                re.search(r"(?:^|[^A-Z0-9])(PIN|DOWEL)(?:$|[^A-Z0-9])", occurrence_name)
                or re.search(r"(?:^|[^A-Z0-9])(PIN|DOWEL[ _-]+PIN)(?:$|[^A-Z0-9])", description)
            )
            searchable = " ".join((occurrence_name, description))
            names_a_retainer = bool(re.search(r"(?:^|[^A-Z0-9])(CLIP|RETAINER|RETAINING[ _-]RING|CIRCLIP)(?:$|[^A-Z0-9])", searchable))
            if names_a_pin and not names_a_retainer:
                physical_pin_candidates.append(occurrence_id)
        undeclared_pin_candidates = sorted(set(physical_pin_candidates) - set(declared_pin_ids))
        duplicate_declared_pins = sorted(value for value, count in Counter(declared_pin_ids).items() if count > 1)
        if undeclared_pin_candidates:
            fail("RETAINED_PIN_SCOPE_INCOMPLETE", occurrence_ids=undeclared_pin_candidates)
        if duplicate_declared_pins:
            fail("DUPLICATE_RETAINED_PIN_REQUIREMENT", occurrence_ids=duplicate_declared_pins)
        sections["required_hardware_and_pin_retention"] = {
            "declared_hardware_count": len(required_hardware),
            "undeclared_installed_occurrence_ids": undeclared_installed_occurrences,
            "retained_pin_requirement_count": len(pin_rows),
            "physical_pin_candidate_count": len(physical_pin_candidates),
            "undeclared_pin_candidate_ids": undeclared_pin_candidates,
            "failure_count": len(failures) - hardware_start[0],
            "blocked_count": len(blocked) - hardware_start[1],
        }

        def mechanism_section(
            field_name: str, engagement_field: str, maximum_gap_field: str,
        ) -> dict[str, Any]:
            start = len(failures), len(blocked)
            rows = requirements.get(field_name)
            if not isinstance(rows, list) or not rows:
                fail("REQUIRED_NONEMPTY_LIST_MISSING", context=field_name, field=field_name)
                rows = []
            mechanism_ids: list[str] = []
            arm_indices: list[int] = []
            for index, row in enumerate(rows, start=1):
                context = f"{field_name} row {index}"
                if not isinstance(row, dict):
                    fail("INVALID_REQUIREMENT_ROW", context=context)
                    continue
                mechanism_id = str(row.get("mechanism_id", "")).strip()
                if not mechanism_id:
                    fail("BLANK_IDENTIFIER", context=context, field="mechanism_id")
                else:
                    mechanism_ids.append(mechanism_id)
                try:
                    arm_index = int(row.get("arm_index"))
                except (TypeError, ValueError):
                    arm_index = -1
                if arm_index not in (1, 2, 3):
                    fail("INVALID_ARM_INDEX", context=context, value=row.get("arm_index"))
                else:
                    arm_indices.append(arm_index)
                for occurrence_id in required_list(row, "required_occurrence_ids", context):
                    occurrence_check(occurrence_id, context)
                for attachment_id in required_list(row, "required_attachment_ids", context):
                    attachment_check(attachment_id, context)
                for track_id in required_list(row, "required_motion_track_ids", context):
                    motion_track_check(track_id, context)
                engagement_check(row.get(engagement_field), row.get(maximum_gap_field), context)
            duplicate_ids = sorted(value for value, count in Counter(mechanism_ids).items() if count > 1)
            if duplicate_ids:
                fail("DUPLICATE_MECHANISM_ID", context=field_name, identifiers=duplicate_ids)
            if sorted(arm_indices) != [1, 2, 3]:
                fail("THREE_ARM_MECHANISM_COVERAGE_FAILED", context=field_name, arm_indices=sorted(arm_indices))
            return {
                "mechanism_count": len(rows), "arm_indices": sorted(arm_indices),
                "failure_count": len(failures) - start[0], "blocked_count": len(blocked) - start[1],
            }

        if state == "DEPLOYED":
            sections["positive_deployed_locks"] = mechanism_section(
                "positive_lock_mechanisms", "deployed_engagement_pair", "maximum_deployed_gap_mm",
            )
        if state == "STOWED":
            sections["positive_stowed_retention"] = mechanism_section(
                "stowed_retention_mechanisms", "stowed_engagement_pair", "maximum_stowed_gap_mm",
            )

        pressure_start = len(failures), len(blocked)
        pressure_rows = requirements.get("pressure_subsystems")
        if not isinstance(pressure_rows, list) or not pressure_rows:
            fail("REQUIRED_NONEMPTY_LIST_MISSING", context="pressure subsystems", field="pressure_subsystems")
            pressure_rows = []
        pressure_ids: list[str] = []
        for index, row in enumerate(pressure_rows, start=1):
            context = f"pressure subsystem row {index}"
            if not isinstance(row, dict):
                fail("INVALID_REQUIREMENT_ROW", context=context)
                continue
            subsystem_id = str(row.get("subsystem_id", "")).strip()
            if not subsystem_id:
                fail("BLANK_IDENTIFIER", context=context, field="subsystem_id")
            else:
                pressure_ids.append(subsystem_id)
                context = f"pressure subsystem {subsystem_id}"
            reservoir_id = str(row.get("reservoir_occurrence_id", "")).strip()
            manifold_id = str(row.get("manifold_occurrence_id", "")).strip()
            if not reservoir_id:
                fail("BLANK_IDENTIFIER", context=context, field="reservoir_occurrence_id")
            else:
                occurrence_check(reservoir_id, context)
            if not manifold_id:
                fail("BLANK_IDENTIFIER", context=context, field="manifold_occurrence_id")
            else:
                occurrence_check(manifold_id, context)
            closure_ids = required_list(row, "closure_occurrence_ids", context)
            maximum_closure_gap = row.get("maximum_closure_gap_mm", ATTACHMENT_DEFAULT_MAX_GAP_MM)
            for occurrence_id in closure_ids:
                occurrence_check(occurrence_id, context)
                if reservoir_id:
                    engagement_check([reservoir_id, occurrence_id], maximum_closure_gap, context)
            isolation_valve_ids = required_list(row, "isolation_valve_occurrence_ids", context)
            for occurrence_id in isolation_valve_ids:
                occurrence_check(occurrence_id, context)
            collection_route_ids = required_list(row, "collection_route_occurrence_ids", context)
            for route_id in collection_route_ids:
                route_check(route_id, context)
            required_attachment_ids = required_list(row, "required_attachment_ids", context)
            for attachment_id in required_attachment_ids:
                attachment_check(attachment_id, context)
            required_route_ids = required_list(row, "required_route_ids", context)
            for route_id in required_route_ids:
                route_check(route_id, context)

            # Enforce calculated pressure topology, rather than accepting a
            # bag of individually valid occurrences/routes. The expected IDs
            # are stable product occurrences; endpoint continuity remains
            # schema-driven from each route definition and its exact audit.
            fullflow_id = "FULLFLOW-VALVE-001"
            wp04_id = "WP04-FULLFLOW-MANIFOLD"
            manifold_feed_id = "ROUTE-MANIFOLD-FEED-001"
            gas_main_id = "ROUTE-GAS-MAIN-001"
            occurrence_check(fullflow_id, context)
            occurrence_check(wp04_id, context)
            row_route_ids = set(collection_route_ids) | set(required_route_ids)
            graph = calculated_pressure_graph(required_attachment_ids, row_route_ids)

            upstream_path: list[str] | None = None
            for closure_id in closure_ids:
                reservoir_to_closure = graph_path(graph, reservoir_id, closure_id)
                closure_to_manifold = graph_path(graph, closure_id, manifold_id)
                if reservoir_to_closure and closure_to_manifold:
                    upstream_path = reservoir_to_closure + closure_to_manifold[1:]
                    break
            feed_in_both_scopes = (
                manifold_feed_id in collection_route_ids
                and manifold_feed_id in required_route_ids
            )
            gas_main_in_both_scopes = (
                gas_main_id in collection_route_ids
                and gas_main_id in required_route_ids
            )
            fullflow_declared = fullflow_id in isolation_valve_ids
            feed_continuity = route_has_exact_supported_endpoints(
                manifold_feed_id, manifold_id, fullflow_id
            )
            gas_main_continuity = route_has_exact_supported_endpoints(
                gas_main_id, fullflow_id, wp04_id
            )
            complete_path = graph_path(graph, reservoir_id, wp04_id)
            required_path_nodes = {
                manifold_id, fullflow_id, manifold_feed_id, gas_main_id, wp04_id,
            }
            path_contains_required_nodes = bool(
                complete_path and required_path_nodes.issubset(complete_path)
            )
            topology_accepted = bool(
                upstream_path and fullflow_declared
                and feed_in_both_scopes and gas_main_in_both_scopes
                and feed_continuity and gas_main_continuity
                and path_contains_required_nodes
            )
            pressure_topology_checks.append({
                "context": context, "subsystem_id": subsystem_id,
                "reservoir_occurrence_id": reservoir_id,
                "closure_occurrence_ids": closure_ids,
                "collection_manifold_occurrence_id": manifold_id,
                "fullflow_valve_occurrence_id": fullflow_id,
                "wp04_distribution_occurrence_id": wp04_id,
                "manifold_feed_route_occurrence_id": manifold_feed_id,
                "gas_main_route_occurrence_id": gas_main_id,
                "upstream_reservoir_closure_manifold_path": upstream_path,
                "complete_pressure_path": complete_path,
                "fullflow_declared_as_isolation_valve": fullflow_declared,
                "manifold_feed_in_collection_and_required_route_scope": feed_in_both_scopes,
                "gas_main_in_collection_and_required_route_scope": gas_main_in_both_scopes,
                "manifold_feed_exact_endpoint_continuity": feed_continuity,
                "gas_main_exact_endpoint_continuity": gas_main_continuity,
                "complete_path_contains_required_nodes": path_contains_required_nodes,
                "accepted": topology_accepted,
            })
            if not upstream_path:
                fail("PRESSURE_RESERVOIR_CLOSURE_MANIFOLD_TOPOLOGY_FAILED", context=context)
            if not fullflow_declared:
                fail("PRESSURE_FULLFLOW_VALVE_SCOPE_MISSING", context=context, occurrence_id=fullflow_id)
            if not feed_in_both_scopes:
                fail("PRESSURE_MANIFOLD_FEED_ROUTE_SCOPE_MISSING", context=context, route_occurrence_id=manifold_feed_id)
            if not feed_continuity:
                fail("PRESSURE_MANIFOLD_FEED_ENDPOINT_CONTINUITY_FAILED", context=context, route_occurrence_id=manifold_feed_id)
            if not gas_main_in_both_scopes:
                fail("PRESSURE_GAS_MAIN_ROUTE_SCOPE_MISSING", context=context, route_occurrence_id=gas_main_id)
            if not gas_main_continuity:
                fail("PRESSURE_GAS_MAIN_ENDPOINT_CONTINUITY_FAILED", context=context, route_occurrence_id=gas_main_id)
            if not complete_path or not path_contains_required_nodes:
                fail("PRESSURE_END_TO_END_EXACT_TOPOLOGY_FAILED", context=context)
        duplicate_pressure_ids = sorted(value for value, count in Counter(pressure_ids).items() if count > 1)
        if duplicate_pressure_ids:
            fail("DUPLICATE_PRESSURE_SUBSYSTEM_ID", identifiers=duplicate_pressure_ids)
        actual_pressure_id_set = set(pressure_ids)
        missing_pressure_subsystem_ids = sorted(
            EXPECTED_PRESSURE_SUBSYSTEM_IDS - actual_pressure_id_set
        )
        unexpected_pressure_subsystem_ids = sorted(
            actual_pressure_id_set - EXPECTED_PRESSURE_SUBSYSTEM_IDS
        )
        if (
            missing_pressure_subsystem_ids
            or unexpected_pressure_subsystem_ids
            or len(pressure_ids) != len(EXPECTED_PRESSURE_SUBSYSTEM_IDS)
        ):
            fail(
                "PRESSURE_SUBSYSTEM_SCOPE_MISMATCH",
                expected_subsystem_ids=sorted(EXPECTED_PRESSURE_SUBSYSTEM_IDS),
                actual_subsystem_ids=sorted(pressure_ids),
                missing_subsystem_ids=missing_pressure_subsystem_ids,
                unexpected_subsystem_ids=unexpected_pressure_subsystem_ids,
            )
        sections["closed_pressure_subsystems"] = {
            "subsystem_count": len(pressure_rows),
            "expected_subsystem_ids": sorted(EXPECTED_PRESSURE_SUBSYSTEM_IDS),
            "actual_subsystem_ids": sorted(pressure_ids),
            "missing_subsystem_ids": missing_pressure_subsystem_ids,
            "unexpected_subsystem_ids": unexpected_pressure_subsystem_ids,
            "topology_check_count": len(pressure_topology_checks),
            "topology_failure_count": sum(
                not row["accepted"] for row in pressure_topology_checks
            ),
            "failure_count": len(failures) - pressure_start[0],
            "blocked_count": len(blocked) - pressure_start[1],
        }

        route_start = len(failures), len(blocked)
        if invalid_route_definition_record_indices:
            fail(
                "INVALID_ROUTE_DEFINITION_ROWS",
                record_indices=invalid_route_definition_record_indices,
            )
        if blank_route_definition_record_indices:
            fail(
                "BLANK_ROUTE_OCCURRENCE_IDS",
                record_indices=blank_route_definition_record_indices,
            )
        if duplicate_route_definition_ids:
            fail(
                "DUPLICATE_ROUTE_OCCURRENCE_IDS",
                identifiers=duplicate_route_definition_ids,
            )
        required_closed_routes = required_list(requirements, "required_closed_route_ids", "closed routes")
        undeclared_routes = sorted(set(route_definitions) - set(required_closed_routes))
        unknown_declared_routes = sorted(set(required_closed_routes) - set(route_definitions))
        if undeclared_routes:
            fail("ROUTE_CLOSURE_SCOPE_INCOMPLETE", undeclared_route_occurrence_ids=undeclared_routes)
        if unknown_declared_routes:
            fail("UNKNOWN_REQUIRED_CLOSED_ROUTE", route_occurrence_ids=unknown_declared_routes)
        for route_id in required_closed_routes:
            route_check(route_id, "required closed route")
        sections["closed_route_ends"] = {
            "declared_closed_route_count": len(required_closed_routes),
            "inventory_route_count": len(route_definitions),
            "invalid_route_definition_record_indices": invalid_route_definition_record_indices,
            "blank_route_definition_record_indices": blank_route_definition_record_indices,
            "duplicate_route_definition_ids": duplicate_route_definition_ids,
            "undeclared_route_occurrence_ids": undeclared_routes,
            "failure_count": len(failures) - route_start[0],
            "blocked_count": len(blocked) - route_start[1],
        }

        elimination_rows = requirements.get("integral_joint_eliminations", [])
        if not isinstance(elimination_rows, list):
            fail("INVALID_OPTIONAL_LIST", field="integral_joint_eliminations")
            elimination_rows = []
        elimination_checks: list[dict[str, Any]] = []
        for index, row in enumerate(elimination_rows, start=1):
            context = f"integral joint elimination row {index}"
            if not isinstance(row, dict):
                fail("INVALID_REQUIREMENT_ROW", context=context)
                continue
            pair = row.get("occurrence_pair")
            process_basis = str(row.get("process_basis", row.get("process", ""))).strip()
            if not isinstance(pair, list) or len(pair) != 2 or any(not str(item).strip() for item in pair):
                fail("INVALID_INTEGRAL_JOINT_PAIR", context=context, value=pair)
                continue
            occurrence_a, occurrence_b = (str(item).strip() for item in pair)
            occurrence_check(occurrence_a, context)
            occurrence_check(occurrence_b, context)
            status, gap, error = minimum_occurrence_distance(solids_by_occurrence, occurrence_a, occurrence_b)
            geometrically_joined = status == "DONE" and gap is not None and gap <= AABB_TOL_MM
            accepted = bool(process_basis and geometrically_joined)
            elimination_checks.append({
                "occurrence_pair": [occurrence_a, occurrence_b], "process_basis_present": bool(process_basis),
                "distance_status": status, "gap_mm": gap, "geometrically_joined": geometrically_joined,
                "accepted": accepted, "error": error,
            })
            if status != "DONE" or gap is None:
                block("INTEGRAL_JOINT_DISTANCE_BLOCKED", context=context, error=error)
            elif not accepted:
                fail("INTEGRAL_JOINT_ELIMINATION_UNSUPPORTED", context=context)

        for section in sections.values():
            section["status"] = (
                "FAIL" if section["failure_count"] else "BLOCKED" if section["blocked_count"] else "PASS"
            )
        return {
            "state": state,
            "requirements_object_present": isinstance(inventory.get("definition_of_done_requirements"), dict),
            "sections": sections, "failure_count": len(failures), "blocked_count": len(blocked),
            "failures": failures, "blocked": blocked,
            "occurrence_checks": [occurrence_checks[key] for key in sorted(occurrence_checks)],
            "engagement_checks": engagement_checks, "attachment_checks": attachment_checks,
            "route_checks": route_checks, "pressure_topology_checks": pressure_topology_checks,
            "motion_track_checks": motion_track_checks,
            "integral_joint_elimination_checks": elimination_checks,
        }

    result = {state: audit_state(state) for state in ("STOWED", "DEPLOYED")}
    dump_json(out_dir / "definition_of_done_audit.json", result)
    return result


def state_parity(stowed: EndpointData, deployed: EndpointData, inventories: dict[str, dict[str, Any]], out_dir: Path) -> dict[str, Any]:
    auth = {
        state: {
            str(o.get("occurrence_id", "")).strip(): o
            for o in inv.get("occurrences", [])
            if isinstance(o, dict) and str(o.get("occurrence_id", "")).strip()
        }
        for state, inv in inventories.items()
    }
    endpoints = {"STOWED": stowed, "DEPLOYED": deployed}
    identity_audits = {
        state: imported_leaf_identity_audit(endpoint)
        for state, endpoint in endpoints.items()
    }
    hierarchy_audits = {
        state: assembly_hierarchy_audit(endpoint, inventories[state])
        for state, endpoint in endpoints.items()
    }
    leaf: dict[str, dict[str, dict[str, Any]]] = {}
    for state, endpoint in endpoints.items():
        leaf_rows = [row for row in endpoint.occurrence_rows if row.get("has_shape")]
        id_counts = Counter(str(row.get("occurrence_id", "")).strip() for row in leaf_rows)
        leaf[state] = {
            str(row.get("occurrence_id", "")).strip(): row
            for row in leaf_rows
            if (
                str(row.get("occurrence_id", "")).strip()
                and id_counts[str(row.get("occurrence_id", "")).strip()] == 1
            )
        }
    ids = sorted(set(leaf["STOWED"]) | set(leaf["DEPLOYED"]))
    rows = []
    mismatches = []
    for occurrence_id in ids:
        s = leaf["STOWED"].get(occurrence_id)
        d = leaf["DEPLOYED"].get(occurrence_id)
        so = auth["STOWED"].get(occurrence_id, {})
        do = auth["DEPLOYED"].get(occurrence_id, {})
        flexible = bool(
            so and do
            and str(so.get("classification", "")).strip().upper() in {"FLEXIBLE", "SOFTGOOD"}
            and str(do.get("classification", "")).strip().upper() in {"FLEXIBLE", "SOFTGOOD"}
        )
        same_part = bool(s and d and s.get("part_number") == d.get("part_number") == so.get("part_number") == do.get("part_number"))
        topology_match = bool(s and d and s.get("solid_count") == d.get("solid_count") and s.get("face_count") == d.get("face_count"))
        volume_delta = None if not s or not d else float(d["volume_mm3"] - s["volume_mm3"])
        stowed_fingerprint: dict[str, Any] | None = None
        deployed_fingerprint: dict[str, Any] | None = None
        fingerprint_error = ""
        bbox_max_abs_delta_mm: float | None = None
        serialized_brep_match = False
        exact_common_equivalence: dict[str, Any] | None = None
        surface_types_match = False
        if s and d:
            try:
                stowed_fingerprint = exact_local_brep_fingerprint(stowed.local_shapes[occurrence_id])
                deployed_fingerprint = exact_local_brep_fingerprint(deployed.local_shapes[occurrence_id])
                bbox_max_abs_delta_mm = max(
                    abs(float(a) - float(b))
                    for a, b in zip(
                        stowed_fingerprint["bbox_mm"], deployed_fingerprint["bbox_mm"]
                    )
                )
                surface_types_match = bool(
                    stowed_fingerprint["surface_types"]
                    == deployed_fingerprint["surface_types"]
                )
                serialized_brep_match = bool(
                    stowed_fingerprint["sha256"] == deployed_fingerprint["sha256"]
                    and surface_types_match
                    and bbox_max_abs_delta_mm <= 1.0e-9
                )
                if (
                    not flexible
                    and topology_match
                    and volume_delta is not None and abs(volume_delta) <= 1.0e-5
                    and surface_types_match
                    and bbox_max_abs_delta_mm <= 1.0e-9
                    and not serialized_brep_match
                ):
                    exact_common_equivalence = exact_common_full_volume_equivalence(
                        stowed.local_shapes[occurrence_id].wrapped,
                        deployed.local_shapes[occurrence_id].wrapped,
                    )
            except Exception as exc:  # pragma: no cover - kernel failure is evidence, not a pass
                fingerprint_error = f"{type(exc).__name__}: {exc}"
        exact_geometry_equivalent = bool(
            serialized_brep_match
            or (exact_common_equivalence and exact_common_equivalence["equivalent"])
        )
        rigid_geometry_match = flexible or bool(
            topology_match
            and volume_delta is not None and abs(volume_delta) <= 1.0e-5
            and exact_geometry_equivalent
            and not fingerprint_error
        )
        status = "PASS" if s and d and same_part and rigid_geometry_match else "FAIL"
        row = {
            "occurrence_id": occurrence_id, "classification": so.get("classification", ""),
            "present_stowed": bool(s), "present_deployed": bool(d), "same_part_number": same_part,
            "stowed_solid_count": "" if not s else s.get("solid_count"),
            "deployed_solid_count": "" if not d else d.get("solid_count"),
            "stowed_face_count": "" if not s else s.get("face_count"),
            "deployed_face_count": "" if not d else d.get("face_count"),
            "volume_delta_mm3": "" if volume_delta is None else repr(volume_delta),
            "stowed_local_brep_sha256": "" if not stowed_fingerprint else stowed_fingerprint["sha256"],
            "deployed_local_brep_sha256": "" if not deployed_fingerprint else deployed_fingerprint["sha256"],
            "local_bbox_max_abs_delta_mm": "" if bbox_max_abs_delta_mm is None else repr(bbox_max_abs_delta_mm),
            "surface_type_counts_match": surface_types_match,
            "serialized_local_brep_match": serialized_brep_match,
            "exact_common_status": "" if not exact_common_equivalence else exact_common_equivalence["status"],
            "exact_common_volume_mm3": "" if not exact_common_equivalence else exact_common_equivalence["common_volume_mm3"],
            "stowed_minus_common_mm3": "" if not exact_common_equivalence else exact_common_equivalence["a_minus_common_mm3"],
            "deployed_minus_common_mm3": "" if not exact_common_equivalence else exact_common_equivalence["b_minus_common_mm3"],
            "exact_common_volume_tolerance_mm3": "" if not exact_common_equivalence else exact_common_equivalence["volume_tolerance_mm3"],
            "exact_common_full_volume_equivalent": bool(
                exact_common_equivalence and exact_common_equivalence["equivalent"]
            ),
            "exact_geometry_equivalent": exact_geometry_equivalent,
            "geometry_equivalence_basis": (
                "FLEXIBLE_STATE_GEOMETRY_EXCEPTION" if flexible
                else "SERIALIZED_LOCAL_BREP_SHA256" if serialized_brep_match
                else "EXACT_COMMON_FULL_VOLUME" if exact_geometry_equivalent
                else "NOT_EQUIVALENT"
            ),
            "exact_common_error": "" if not exact_common_equivalence else exact_common_equivalence["error"],
            "fingerprint_error": fingerprint_error,
            "flexible_state_geometry_exception": flexible, "status": status,
        }
        rows.append(row)
        if status == "FAIL":
            mismatches.append(occurrence_id)
    with (out_dir / "state_parity.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["occurrence_id"])
        writer.writeheader()
        writer.writerows(rows)
    identity_issue_count = sum(
        audit["blank_occurrence_id_count"] + audit["duplicate_occurrence_id_count"]
        for audit in identity_audits.values()
    )
    hierarchy_issue_count = sum(audit["issue_count"] for audit in hierarchy_audits.values())
    return {
        "union_occurrence_count": len(ids), "mismatch_count": len(mismatches),
        "mismatch_occurrence_ids": mismatches,
        "stowed_only": sorted(set(leaf["STOWED"]) - set(leaf["DEPLOYED"])),
        "deployed_only": sorted(set(leaf["DEPLOYED"]) - set(leaf["STOWED"])),
        "imported_leaf_identity_audits": identity_audits,
        "imported_leaf_identity_issue_count": identity_issue_count,
        "hierarchy_audits": hierarchy_audits,
        "hierarchy_issue_count": hierarchy_issue_count,
        "overall_issue_count": len(mismatches) + identity_issue_count + hierarchy_issue_count,
    }


def occurrence_bom_reconciliation(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]], out_dir: Path,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    imported_leaf_identity_audits: dict[str, dict[str, Any]] = {}
    hierarchy_audits: dict[str, dict[str, Any]] = {}
    for state in ("STOWED", "DEPLOYED"):
        inventory = inventories[state]
        part_numbers = [str(part.get("part_number", "")) for part in inventory.get("parts", [])]
        duplicate_parts = sorted(part for part, count in Counter(part_numbers).items() if part and count > 1)
        occurrence_ids = [str(occ.get("occurrence_id", "")) for occ in inventory.get("occurrences", [])]
        duplicate_occurrences = sorted(occ for occ, count in Counter(occurrence_ids).items() if occ and count > 1)
        if duplicate_parts:
            issues.append({"state": state, "issue": "DUPLICATE_PART_DEFINITION", "identifiers": duplicate_parts})
        if duplicate_occurrences:
            issues.append({"state": state, "issue": "DUPLICATE_OCCURRENCE_ID", "identifiers": duplicate_occurrences})
        leaf_identity = imported_leaf_identity_audit(endpoints[state])
        imported_leaf_identity_audits[state] = leaf_identity
        if leaf_identity["blank_occurrence_id_count"]:
            issues.append({
                "state": state,
                "issue": "BLANK_IMPORTED_AP242_LEAF_OCCURRENCE_ID",
                "rows": leaf_identity["blank_occurrence_id_rows"],
            })
        if leaf_identity["duplicate_occurrence_id_count"]:
            issues.append({
                "state": state,
                "issue": "DUPLICATE_IMPORTED_AP242_LEAF_OCCURRENCE_ID",
                "identifiers": leaf_identity["duplicate_occurrence_ids"],
            })
        hierarchy = assembly_hierarchy_audit(endpoints[state], inventory)
        hierarchy_audits[state] = hierarchy
        if not hierarchy["accepted"]:
            issues.append({
                "state": state,
                "issue": "AP242_ASSEMBLY_HIERARCHY_MISMATCH",
                "hierarchy_issue_count": hierarchy["issue_count"],
                "hierarchy_issues": hierarchy["issues"],
            })
        part_set = set(part_numbers)
        inventory_occurrences = {
            occurrence["occurrence_id"]: occurrence for occurrence in inventory.get("occurrences", [])
            if occurrence.get("occurrence_id")
        }
        raw_imported_leaves = [
            row for row in endpoints[state].occurrence_rows if row.get("has_shape")
        ]
        imported_id_counts = Counter(
            str(row.get("occurrence_id", "")).strip() for row in raw_imported_leaves
        )
        imported_leaves = {
            str(row.get("occurrence_id", "")).strip(): row
            for row in raw_imported_leaves
            if (
                str(row.get("occurrence_id", "")).strip()
                and imported_id_counts[str(row.get("occurrence_id", "")).strip()] == 1
            )
        }
        for occurrence_id in sorted(set(inventory_occurrences) | set(imported_leaves)):
            inventory_row = inventory_occurrences.get(occurrence_id)
            imported_row = imported_leaves.get(occurrence_id)
            inventory_part = "" if not inventory_row else str(inventory_row.get("part_number", ""))
            imported_part = "" if not imported_row else str(imported_row.get("part_number", ""))
            issue_codes: list[str] = []
            if inventory_row is None:
                issue_codes.append("AP242_LEAF_NOT_IN_OCCURRENCE_BOM")
            if imported_row is None:
                issue_codes.append("OCCURRENCE_BOM_ROW_NOT_IN_AP242")
            if inventory_row is not None and inventory_part not in part_set:
                issue_codes.append("OCCURRENCE_PART_DEFINITION_MISSING")
            if inventory_row is not None and imported_row is not None and inventory_part != imported_part:
                issue_codes.append("AP242_BOM_PART_NUMBER_MISMATCH")
            if issue_codes:
                issues.append({"state": state, "occurrence_id": occurrence_id, "issues": issue_codes})
            rows.append({
                "state": state, "occurrence_id": occurrence_id,
                "in_occurrence_bom": inventory_row is not None, "in_ap242_xcaf": imported_row is not None,
                "inventory_part_number": inventory_part, "ap242_part_number": imported_part,
                "part_definition_present": inventory_part in part_set if inventory_part else False,
                "status": "PASS" if not issue_codes else "FAIL", "issues": ";".join(issue_codes),
            })

        actual_counts = Counter(
            str(occurrence.get("part_number", "")) for occurrence in inventory.get("occurrences", [])
        )
        for part in inventory.get("parts", []):
            expected_raw = part.get("occurrence_quantity")
            if expected_raw in (None, ""):
                continue
            try:
                expected = int(expected_raw)
            except (TypeError, ValueError):
                issues.append({
                    "state": state, "part_number": part.get("part_number"),
                    "issue": "INVALID_OCCURRENCE_QUANTITY",
                })
                continue
            actual = actual_counts[str(part.get("part_number", ""))]
            if expected != actual:
                issues.append({
                    "state": state, "part_number": part.get("part_number"),
                    "issue": "OCCURRENCE_QUANTITY_MISMATCH", "expected": expected, "actual": actual,
                })
    fields = [
        "state", "occurrence_id", "in_occurrence_bom", "in_ap242_xcaf",
        "inventory_part_number", "ap242_part_number", "part_definition_present", "status", "issues",
    ]
    with (out_dir / "occurrence_bom_reconciliation.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "row_count": len(rows), "issue_count": len(issues), "issues": issues,
        "imported_leaf_identity_audits": imported_leaf_identity_audits,
        "hierarchy_audits": hierarchy_audits,
        "stowed_occurrence_count": len(inventories["STOWED"].get("occurrences", [])),
        "deployed_occurrence_count": len(inventories["DEPLOYED"].get("occurrences", [])),
    }


def transform_translation(row: dict[str, Any]) -> tuple[float, float, float]:
    matrix = row["absolute_transform_3x4"]
    return float(matrix[0][3]), float(matrix[1][3]), float(matrix[2][3])


def leaf_lookup(endpoint: EndpointData) -> dict[str, dict[str, Any]]:
    return {row["occurrence_id"]: row for row in endpoint.occurrence_rows if row["has_shape"]}


def projection_bounds(shape: cq.Shape, axis: tuple[float, float, float] = (0.0, 0.0, 1.0)) -> tuple[float, float]:
    values = []
    explorer = TopExp_Explorer(shape.wrapped, TopAbs_VERTEX)
    while explorer.More():
        vertex = TopoDS.Vertex_s(explorer.Current())
        point = cq.Vertex(vertex).toTuple()
        values.append(sum(point[i] * axis[i] for i in range(3)))
        explorer.Next()
    if not values:
        raise ValueError("No vertices available for projection extent")
    return min(values), max(values)


def kinematic(theta_deg: float) -> dict[str, float]:
    theta = math.radians(theta_deg)
    bell_r = PIVOT_RADIUS_MM + BELL_U_MM * math.cos(theta) + BELL_V_MM * math.sin(theta)
    bell_z = PIVOT_Z_MM - BELL_U_MM * math.sin(theta) + BELL_V_MM * math.cos(theta)
    radicand = LINK_CENTER_DISTANCE_MM ** 2 - (bell_r - CROSSHEAD_RADIUS_MM) ** 2
    if radicand <= 0.0:
        raise ValueError(f"Kinematic closure has non-positive radicand at {theta_deg} degrees")
    crosshead_z = bell_z + math.sqrt(radicand)
    z0 = PIVOT_Z_MM + BELL_V_MM + math.sqrt(
        LINK_CENTER_DISTANCE_MM ** 2 - (PIVOT_RADIUS_MM + BELL_U_MM - CROSSHEAD_RADIUS_MM) ** 2
    )
    return {
        "arm_angle_deg": float(theta_deg), "bell_r_mm": bell_r, "bell_z_mm": bell_z,
        "crosshead_z_mm": crosshead_z, "crosshead_travel_mm": z0 - crosshead_z,
        "closure_residual_mm": math.sqrt((bell_r - CROSSHEAD_RADIUS_MM) ** 2 + (bell_z - crosshead_z) ** 2) - LINK_CENTER_DISTANCE_MM,
    }


def key_dimensions(endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]]) -> dict[str, Any]:
    leaves = {state: leaf_lookup(endpoint) for state, endpoint in endpoints.items()}
    result: dict[str, Any] = {}
    for state, endpoint in endpoints.items():
        rigid_boxes = [
            solid.bbox for solid in endpoint.solid_records
            if solid.classification in {"FIXED", "MOVING"}
        ]
        all_box = bbox_union(s.bbox for s in endpoint.solid_records)
        rigid_box = bbox_union(rigid_boxes)
        result[state.lower()] = {
            "all_geometry_bbox_mm": bbox_dict(all_box) if all_box else None,
            "rigid_geometry_bbox_mm": bbox_dict(rigid_box) if rigid_box else None,
            "rigid_length_mm": None if not rigid_box else rigid_box[5] - rigid_box[2],
            "all_geometry_length_mm": None if not all_box else all_box[5] - all_box[2],
            "solid_count": len(endpoint.solid_records),
            "invalid_solid_count": sum(not s.valid for s in endpoint.solid_records),
            "face_count": sum(s.face_count for s in endpoint.solid_records),
            "surface_type_counts": dict(sorted(sum((Counter(s.surface_types) for s in endpoint.solid_records), Counter()).items())),
        }

    # The hard arm-module envelope is measured in the stowed endpoint over the
    # controlled 885..1635 mm module interval.
    arm_module_boxes = [
        s.bbox for s in endpoints["STOWED"].solid_records
        if s.bbox[5] >= 885.0 - 1e-8 and s.bbox[2] <= 1635.0 + 1e-8
        and s.classification in {"FIXED", "MOVING"}
    ]
    arm_box = bbox_union(arm_module_boxes)
    result["arm_module_stowed_bbox_mm"] = bbox_dict(arm_box) if arm_box else None
    result["arm_module_stowed_xy_span_mm"] = None if not arm_box else max(arm_box[3] - arm_box[0], arm_box[4] - arm_box[1])
    normal_oml_ids = sorted(REQUIRED_NORMAL_OML_OCCURRENCE_IDS)
    result["normal_body_oml_required_occurrence_ids"] = normal_oml_ids
    result["normal_body_oml_missing_occurrence_ids"] = sorted(
        REQUIRED_NORMAL_OML_OCCURRENCE_IDS - set(leaves["STOWED"])
    )
    result["normal_body_oml_xy_spans_mm"] = {
        occurrence_id: max(
            leaves["STOWED"][occurrence_id]["bbox_mm"]["xmax"] - leaves["STOWED"][occurrence_id]["bbox_mm"]["xmin"],
            leaves["STOWED"][occurrence_id]["bbox_mm"]["ymax"] - leaves["STOWED"][occurrence_id]["bbox_mm"]["ymin"],
        )
        for occurrence_id in normal_oml_ids if occurrence_id in leaves["STOWED"]
    }

    arm_rows = []
    for state in ("STOWED", "DEPLOYED"):
        for index, clock in enumerate((0.0, 120.0, 240.0), start=1):
            row = leaves[state][f"ARM-{index}"]
            matrix = row["absolute_transform_3x4"]
            axis = (matrix[0][2], matrix[1][2], matrix[2][2])
            angle = math.degrees(math.acos(max(-1.0, min(1.0, axis[2]))))
            clock_measured = math.degrees(math.atan2(axis[1], axis[0])) % 360.0 if abs(axis[0]) + abs(axis[1]) > 1e-12 else clock
            local_min, local_tip = projection_bounds(endpoints[state].local_shapes[f"ARM-{index}"], (0.0, 0.0, 1.0))
            arm_rows.append({
                "state": state, "arm_index": index, "required_clock_deg": clock,
                "measured_axis_clock_deg": clock_measured, "measured_axis_angle_deg": angle,
                "local_geometry_min_from_pivot_mm": local_min,
                "local_pivot_to_tip_extent_mm": local_tip,
                "face_count": row["face_count"], "surface_types": row["surface_types"],
            })
    result["arms"] = arm_rows
    crosshead_z = {
        state: transform_translation(leaves[state]["CROSSHEAD-001"])[2]
        for state in ("STOWED", "DEPLOYED")
    }
    result["crosshead_z_mm"] = crosshead_z
    result["crosshead_travel_from_reimported_transforms_mm"] = crosshead_z["STOWED"] - crosshead_z["DEPLOYED"]
    result["crosshead_travel_from_independent_closure_equation_mm"] = kinematic(80.0)["crosshead_travel_mm"]

    overrides = {
        state: inventories[state].get("mass_overrides_kg", {})
        if isinstance(inventories[state].get("mass_overrides_kg", {}), dict) else {}
        for state in ("STOWED", "DEPLOYED")
    }
    override_mismatches: list[str] = []
    for key in sorted(set(overrides["STOWED"]) | set(overrides["DEPLOYED"])):
        stowed_value = overrides["STOWED"].get(key)
        deployed_value = overrides["DEPLOYED"].get(key)
        try:
            equal = stowed_value is not None and deployed_value is not None and math.isclose(
                float(stowed_value), float(deployed_value), rel_tol=0.0, abs_tol=1.0e-12,
            )
        except (TypeError, ValueError):
            equal = False
        if not equal:
            override_mismatches.append(key)

    parts_by_state = {
        state: {p["part_number"]: p for p in inventories[state]["parts"]}
        for state in ("STOWED", "DEPLOYED")
    }
    known_mass_keys = {
        occurrence["occurrence_id"] for occurrence in inventories["STOWED"]["occurrences"]
    } | set(parts_by_state["STOWED"])
    invalid_override_keys: list[str] = []
    for key, value in overrides["STOWED"].items():
        try:
            value_ok = math.isfinite(float(value)) and float(value) > 0.0
        except (TypeError, ValueError):
            value_ok = False
        if key not in known_mass_keys or not value_ok:
            invalid_override_keys.append(str(key))
    part_mass_mismatches: list[str] = []
    for part_number in sorted(set(parts_by_state["STOWED"]) & set(parts_by_state["DEPLOYED"])):
        a = parts_by_state["STOWED"][part_number].get("mass_kg")
        b = parts_by_state["DEPLOYED"][part_number].get("mass_kg")
        if a is None and b is None:
            continue
        try:
            same = a is not None and b is not None and math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1.0e-12)
        except (TypeError, ValueError):
            same = False
        if not same:
            occurrence_ids_for_part = [
                occurrence["occurrence_id"] for occurrence in inventories["STOWED"]["occurrences"]
                if occurrence["part_number"] == part_number
            ]
            covered_by_state_invariant_override = (
                part_number in overrides["STOWED"] and part_number in overrides["DEPLOYED"]
            ) or bool(occurrence_ids_for_part) and all(
                occurrence_id in overrides["STOWED"] and occurrence_id in overrides["DEPLOYED"]
                for occurrence_id in occurrence_ids_for_part
            )
            if not covered_by_state_invariant_override:
                part_mass_mismatches.append(part_number)

    mass_missing: list[str] = []
    invalid_mass_values: list[str] = []
    mass_basis_rows: list[dict[str, Any]] = []
    total_mass = 0.0
    for occurrence in inventories["STOWED"]["occurrences"]:
        occurrence_id = occurrence["occurrence_id"]
        part_number = occurrence["part_number"]
        if occurrence_id in overrides["STOWED"]:
            mass = overrides["STOWED"][occurrence_id]
            basis = "STATE_INVARIANT_OCCURRENCE_OVERRIDE"
        elif part_number in overrides["STOWED"]:
            mass = overrides["STOWED"][part_number]
            basis = "STATE_INVARIANT_PART_OVERRIDE"
        else:
            mass = parts_by_state["STOWED"].get(part_number, {}).get("mass_kg")
            basis = "PART_MASTER_MASS"
        if mass is None:
            mass_missing.append(occurrence_id)
            continue
        try:
            mass_value = float(mass)
            if not math.isfinite(mass_value) or mass_value <= 0.0:
                raise ValueError
        except (TypeError, ValueError):
            invalid_mass_values.append(occurrence_id)
            continue
        total_mass += mass_value
        mass_basis_rows.append({
            "occurrence_id": occurrence_id, "part_number": part_number,
            "mass_kg": mass_value, "basis": basis,
        })
    result["mass_rollup_from_authoring_inventory_kg"] = total_mass
    result["mass_unresolved_occurrence_ids"] = mass_missing
    result["mass_invalid_occurrence_ids"] = invalid_mass_values
    result["mass_override_state_mismatch_keys"] = override_mismatches
    result["mass_override_invalid_or_unknown_keys"] = sorted(set(invalid_override_keys))
    result["part_mass_state_mismatch_part_numbers"] = part_mass_mismatches
    result["mass_basis_rows"] = mass_basis_rows
    result["mass_reserve_using_resolved_mass_only_kg"] = MAX_SYSTEM_MASS_KG - total_mass
    return result


def loc_rotation(axis: tuple[float, float, float], angle_deg: float) -> cq.Location:
    return cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), angle_deg)


def loc_translation(x: float, y: float, z: float) -> cq.Location:
    return cq.Location(cq.Vector(x, y, z))


def arm_occurrence_loc(theta_deg: float, clock_deg: float) -> cq.Location:
    return (
        loc_rotation((0, 0, 1), clock_deg)
        * loc_translation(PIVOT_RADIUS_MM, 0.0, PIVOT_Z_MM)
        * loc_rotation((0, 1, 0), theta_deg)
    )


def exact_motion_compression_spring(
    outer_diameter_mm: float,
    wire_diameter_mm: float,
    installed_length_mm: float,
    total_turns: float,
) -> cq.Shape:
    """Independently build one valid analytic helix for a motion sample."""
    if not (
        outer_diameter_mm > wire_diameter_mm > 0.0
        and installed_length_mm > wire_diameter_mm
        and total_turns > 1.0
    ):
        raise ValueError(
            "Invalid analytic spring parameters: "
            f"OD={outer_diameter_mm}, wire={wire_diameter_mm}, "
            f"length={installed_length_mm}, turns={total_turns}"
        )
    mean_diameter = outer_diameter_mm - wire_diameter_mm
    helix_height = installed_length_mm - wire_diameter_mm
    pitch = helix_height / (total_turns - 1.0)
    path = cq.Wire.makeHelix(
        pitch, helix_height, mean_diameter / 2.0,
        center=cq.Vector(0.0, 0.0, wire_diameter_mm / 2.0),
        dir=cq.Vector(0.0, 0.0, 1.0),
    )
    profile = cq.Workplane(
        "XZ", origin=(mean_diameter / 2.0, 0.0, wire_diameter_mm / 2.0),
    ).circle(wire_diameter_mm / 2.0)
    spring = profile.sweep(path, isFrenet=True).val()
    solids = spring.Solids()
    if (
        len(solids) != 1
        or not BRepCheck_Analyzer(solids[0].wrapped).IsValid()
        or solids[0].Volume() <= 0.0
    ):
        raise ValueError(
            "Analytic motion spring is not one valid positive-volume exact solid: "
            f"solids={len(solids)}, volume={spring.Volume()}"
        )
    return solids[0]


def location_from_matrix(matrix: list[list[float]]) -> cq.Location:
    transform = gp_Trsf()
    transform.SetValues(
        float(matrix[0][0]), float(matrix[0][1]), float(matrix[0][2]), float(matrix[0][3]),
        float(matrix[1][0]), float(matrix[1][1]), float(matrix[1][2]), float(matrix[1][3]),
        float(matrix[2][0]), float(matrix[2][1]), float(matrix[2][2]), float(matrix[2][3]),
    )
    return cq.Location(TopLoc_Location(transform))


def _rotation_quaternion(matrix: list[list[float]]) -> tuple[float, float, float, float]:
    m00, m01, m02 = matrix[0][:3]
    m10, m11, m12 = matrix[1][:3]
    m20, m21, m22 = matrix[2][:3]
    trace = m00 + m11 + m22
    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        q = (0.25 * s, (m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        q = ((m21 - m12) / s, 0.25 * s, (m01 + m10) / s, (m02 + m20) / s)
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        q = ((m02 - m20) / s, (m01 + m10) / s, 0.25 * s, (m12 + m21) / s)
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
        q = ((m10 - m01) / s, (m02 + m20) / s, (m12 + m21) / s, 0.25 * s)
    norm = math.sqrt(sum(value * value for value in q))
    return tuple(value / norm for value in q)


def _quaternion_matrix(q: tuple[float, float, float, float]) -> list[list[float]]:
    w, x, y, z = q
    return [
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
        [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
        [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
    ]


def interpolate_location(a: list[list[float]], b: list[list[float]], fraction: float) -> cq.Location:
    qa = _rotation_quaternion(a)
    qb = _rotation_quaternion(b)
    dot = sum(qa[i] * qb[i] for i in range(4))
    if dot < 0.0:
        qb = tuple(-value for value in qb)
        dot = -dot
    if dot > 0.9995:
        q = tuple(qa[i] + fraction * (qb[i] - qa[i]) for i in range(4))
        norm = math.sqrt(sum(value * value for value in q))
        q = tuple(value / norm for value in q)
    else:
        theta = math.acos(max(-1.0, min(1.0, dot)))
        sin_theta = math.sin(theta)
        wa = math.sin((1.0 - fraction) * theta) / sin_theta
        wb = math.sin(fraction * theta) / sin_theta
        q = tuple(wa * qa[i] + wb * qb[i] for i in range(4))
    rotation = _quaternion_matrix(q)
    matrix = [
        rotation[row] + [float(a[row][3]) + fraction * (float(b[row][3]) - float(a[row][3]))]
        for row in range(3)
    ]
    return location_from_matrix(matrix)


def _local_solids(shape: cq.Shape) -> list[Any]:
    result: list[Any] = []
    explorer = TopExp_Explorer(shape.wrapped, TopAbs_SOLID)
    while explorer.More():
        result.append(TopoDS.Solid_s(explorer.Current()))
        explorer.Next()
    return result


@dataclass
class MotionSolid:
    occurrence_id: str
    part_number: str
    classification: str
    solid_index: int
    variant: str
    dynamic: bool
    shape: Any = field(repr=False)
    bbox: tuple[float, float, float, float, float, float]


def _motion_angle_audit(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]], out_dir: Path,
    angles: Iterable[int],
) -> dict[str, Any]:
    """Run the unchanged exact-BREP motion body for specified global angles.

    Every MOVING/FLEXIBLE/SOFTGOOD occurrence must have one explicit motion
    track.  Tracks either prescribe exact keyframes, name a verified kinematic
    law, inherit a moving parent's rigid transform, generate an exact analytic
    compression-spring B-rep from its two seat lands, conservatively audit both
    endpoint B-reps, or document that the item remains stowed during the arm
    sweep.  Missing or malformed scope never passes silently.
    """
    start = time.time()
    angle_values = list(angles)
    if not angle_values or any(type(angle) is not int or angle < 0 or angle > 80 for angle in angle_values):
        raise ValueError(f"Motion angles must be nonempty integer samples inside 0..80: {angle_values}")
    if len(set(angle_values)) != len(angle_values) or angle_values != sorted(angle_values):
        raise ValueError(f"Motion angles must be unique and ascending: {angle_values}")
    stowed = endpoints["STOWED"]
    deployed = endpoints["DEPLOYED"]
    stowed_inventory = inventories["STOWED"]
    leaves = {state: leaf_lookup(endpoints[state]) for state in ("STOWED", "DEPLOYED")}
    occurrences = {o["occurrence_id"]: o for o in stowed_inventory["occurrences"]}
    required_scope = {
        occurrence_id for occurrence_id, occurrence in occurrences.items()
        if occurrence.get("classification") in {"MOVING", "FLEXIBLE", "SOFTGOOD"}
    }
    tracks: dict[str, dict[str, Any]] = {}
    track_errors: list[str] = []
    raw_track_rows = {
        state: inventories[state].get("motion_tracks", [])
        for state in ("STOWED", "DEPLOYED")
    }

    def nonfinite_numeric_paths(value: Any, path: str = "$") -> list[str]:
        if isinstance(value, float) and not math.isfinite(value):
            return [path]
        if isinstance(value, list):
            return [
                child
                for index, item in enumerate(value)
                for child in nonfinite_numeric_paths(item, f"{path}[{index}]")
            ]
        if isinstance(value, dict):
            return [
                child
                for key, item in value.items()
                for child in nonfinite_numeric_paths(item, f"{path}.{key}")
            ]
        return []

    for state, rows in raw_track_rows.items():
        if not isinstance(rows, list):
            track_errors.append(f"{state} motion_tracks root is not a list")
            continue
        bad_rows = [index for index, row in enumerate(rows) if not isinstance(row, dict)]
        if bad_rows:
            track_errors.append(f"{state} motion_tracks contains non-object rows: {bad_rows}")
        nonfinite = nonfinite_numeric_paths(rows)
        if nonfinite:
            track_errors.append(f"{state} motion_tracks contains non-finite numeric values: {nonfinite}")
    track_rows = raw_track_rows["STOWED"] if isinstance(raw_track_rows["STOWED"], list) else []
    deployed_track_rows = (
        raw_track_rows["DEPLOYED"] if isinstance(raw_track_rows["DEPLOYED"], list) else []
    )
    if json.dumps(track_rows, sort_keys=True, separators=(",", ":"), allow_nan=True) != json.dumps(
        deployed_track_rows, sort_keys=True, separators=(",", ":"), allow_nan=True,
    ):
        track_errors.append("STOWED and DEPLOYED motion-track definitions differ")
    allowed_modes = {
        "ARM_KINEMATIC", "CROSSHEAD_KINEMATIC", "PARENT_RIGID",
        "KEYFRAMED_TRANSFORMS", "KEYFRAMED_EXACT_BREP_VARIANTS",
        "RIGID_ENDPOINT_INTERPOLATION",
        "CONSERVATIVE_ENDPOINT_BREPS", "AXIAL_COMPRESSION_SPRING_KINEMATIC",
        "HOLD_STOWED",
    }
    for record in track_rows:
        if not isinstance(record, dict):
            continue
        occurrence_id = str(record.get("occurrence_id", "")).strip()
        if not occurrence_id or occurrence_id in tracks:
            track_errors.append(f"blank or duplicate motion track occurrence_id: {occurrence_id or '<blank>'}")
            continue
        tracks[occurrence_id] = dict(record)
    scope_missing = sorted(required_scope - set(tracks))
    extra_tracks = sorted(set(tracks) - set(occurrences))
    if extra_tracks:
        track_errors.append(f"motion tracks name unknown occurrences: {extra_tracks}")

    stowed_local_solids = {occ: _local_solids(shape) for occ, shape in stowed.local_shapes.items()}
    deployed_local_solids = {occ: _local_solids(shape) for occ, shape in deployed.local_shapes.items()}
    for occurrence_id in sorted(set(tracks) & set(occurrences)):
        track = tracks[occurrence_id]
        mode = str(track.get("mode", "")).strip().upper()
        track["mode"] = mode
        if mode not in allowed_modes:
            track_errors.append(f"{occurrence_id}: unsupported motion mode {mode or '<blank>'}")
            continue
        if not str(track.get("process_basis", "")).strip():
            track_errors.append(f"{occurrence_id}: nonblank process_basis is required")
        if mode == "HOLD_STOWED" and not bool(track.get("stationary_during_arm_sweep", False)):
            track_errors.append(f"{occurrence_id}: HOLD_STOWED requires stationary_during_arm_sweep=true")
        if mode == "ARM_KINEMATIC" and not re.fullmatch(r"ARM-[123]", occurrence_id):
            track_errors.append(f"{occurrence_id}: ARM_KINEMATIC is restricted to ARM-1/2/3")
        if mode == "PARENT_RIGID":
            parent_id = str(track.get("parent_occurrence_id", "")).strip()
            if parent_id not in tracks:
                track_errors.append(f"{occurrence_id}: PARENT_RIGID parent track missing: {parent_id}")
        if mode == "KEYFRAMED_TRANSFORMS":
            samples = track.get("samples", [])
            angles = [sample.get("angle_deg") for sample in samples if isinstance(sample, dict)] if isinstance(samples, list) else []
            if angles != list(range(81)) or any(
                not isinstance(sample.get("transform_matrix_3x4"), list) for sample in samples
            ):
                track_errors.append(f"{occurrence_id}: KEYFRAMED_TRANSFORMS requires exact ordered samples 0..80")
        if mode == "KEYFRAMED_EXACT_BREP_VARIANTS":
            samples = track.get("samples", [])
            sample_angles = [
                sample.get("angle_deg") for sample in samples if isinstance(sample, dict)
            ] if isinstance(samples, list) else []
            variants = [
                str(sample.get("endpoint_variant", "")).strip().upper()
                for sample in samples if isinstance(sample, dict)
            ] if isinstance(samples, list) else []
            if (
                sample_angles != list(range(81))
                or len(variants) != 81
                or any(variant not in {"STOWED", "DEPLOYED"} for variant in variants)
                or any(
                    not isinstance(sample.get("transform_matrix_3x4"), list)
                    for sample in samples if isinstance(sample, dict)
                )
            ):
                track_errors.append(
                    f"{occurrence_id}: KEYFRAMED_EXACT_BREP_VARIANTS requires exact ordered variant/transform samples 0..80"
                )
            elif re.fullmatch(r"STOW-DOG-SPRING-[123]", occurrence_id):
                if variants != ["STOWED", *(["DEPLOYED"] * 80)]:
                    track_errors.append(
                        f"{occurrence_id}: stow-dog spring must release between the 0 and 1 degree samples"
                    )
            elif re.fullmatch(r"LOCK-SPRING-[123]", occurrence_id):
                if variants != [*(["STOWED"] * 80), "DEPLOYED"]:
                    track_errors.append(
                        f"{occurrence_id}: lock spring must advance only at the 80 degree sample"
                    )
            else:
                track_errors.append(
                    f"{occurrence_id}: exact endpoint B-rep variant keyframes are not authorized for this occurrence"
                )
            if (
                len(stowed_local_solids.get(occurrence_id, [])) != 1
                or len(deployed_local_solids.get(occurrence_id, [])) != 1
            ):
                track_errors.append(
                    f"{occurrence_id}: exact endpoint B-rep variant keyframes require one local solid in each endpoint"
                )
        if mode == "AXIAL_COMPRESSION_SPRING_KINEMATIC":
            try:
                moving_seat_id = str(track["moving_seat_occurrence_id"]).strip()
                fixed_seat_id = str(track["fixed_seat_occurrence_id"]).strip()
                expected_seats = {
                    "moving": "BACKUP-SPRING-MOVING-SEAT",
                    "fixed": "BACKUP-SPRING-FIXED-SEAT",
                }
                if occurrence_id != "BACKUP-SPRING-001":
                    raise ValueError(
                        "AXIAL_COMPRESSION_SPRING_KINEMATIC is restricted to BACKUP-SPRING-001"
                    )
                if moving_seat_id != expected_seats["moving"] or fixed_seat_id != expected_seats["fixed"]:
                    raise ValueError(
                        "backup spring track must name its occurrence-specific modeled seat lands: "
                        f"moving={expected_seats['moving']}, fixed={expected_seats['fixed']}"
                    )
                if moving_seat_id not in occurrences or fixed_seat_id not in occurrences:
                    raise ValueError(
                        f"unknown seat occurrence(s): moving={moving_seat_id}, fixed={fixed_seat_id}"
                    )
                if moving_seat_id not in tracks:
                    raise ValueError(f"moving seat has no motion track: {moving_seat_id}")
                moving_seat_track = tracks[moving_seat_id]
                if (
                    str(moving_seat_track.get("mode", "")).strip().upper() != "PARENT_RIGID"
                    or str(moving_seat_track.get("parent_occurrence_id", "")).strip() != "CROSSHEAD-001"
                    or str(tracks.get("CROSSHEAD-001", {}).get("mode", "")).strip().upper()
                    != "CROSSHEAD_KINEMATIC"
                ):
                    raise ValueError(
                        "moving seat must remain PARENT_RIGID to the exact CROSSHEAD-001 kinematic track"
                    )
                if (
                    str(occurrences[fixed_seat_id].get("classification", "")).strip().upper() != "FIXED"
                    or fixed_seat_id in tracks
                ):
                    raise ValueError("fixed seat must be classified FIXED and have no active motion track")
                if moving_seat_id == fixed_seat_id or occurrence_id in {moving_seat_id, fixed_seat_id}:
                    raise ValueError("spring and seat occurrence IDs must be distinct")
                outer_diameter = float(track["outer_diameter_mm"])
                wire_diameter = float(track["wire_diameter_mm"])
                total_turns = float(track["total_turns"])
                float(track["moving_seat_face_offset_local_z_mm"])
                float(track["fixed_seat_face_offset_local_z_mm"])
                if outer_diameter <= wire_diameter or wire_diameter <= 0.0 or total_turns <= 1.0:
                    raise ValueError("invalid analytic spring dimensions")
                if not bool(track.get("endpoint_equivalence_required", False)):
                    raise ValueError("endpoint_equivalence_required must be true")
                expected_attachments = {
                    "ATT-BACKUP-SPRING-MOVING": frozenset((occurrence_id, moving_seat_id)),
                    "ATT-BACKUP-SPRING-FIXED": frozenset((occurrence_id, fixed_seat_id)),
                    "ATT-BACKUP-MOVING-SEAT-CROSSHEAD": frozenset((moving_seat_id, "CROSSHEAD-001")),
                }
                for endpoint_state in ("STOWED", "DEPLOYED"):
                    attachment_rows = {
                        str(row.get("attachment_id", "")).strip(): row
                        for row in inventories[endpoint_state].get("attachment_requirements", [])
                        if isinstance(row, dict) and str(row.get("attachment_id", "")).strip()
                    }
                    for attachment_id, expected_pair in expected_attachments.items():
                        attachment = attachment_rows.get(attachment_id)
                        actual_pair = frozenset((
                            str((attachment or {}).get("occurrence_a", "")).strip(),
                            str((attachment or {}).get("occurrence_b", "")).strip(),
                        ))
                        if attachment is None or actual_pair != expected_pair:
                            raise ValueError(
                                f"{endpoint_state} attachment register does not bind "
                                f"{attachment_id} to {sorted(expected_pair)}"
                            )
            except Exception as exc:
                track_errors.append(
                    f"{occurrence_id}: invalid axial compression-spring track: "
                    f"{type(exc).__name__}: {exc}"
                )
        if mode == "RIGID_ENDPOINT_INTERPOLATION":
            if not bool(track.get("interpolation_verified", False)):
                track_errors.append(f"{occurrence_id}: endpoint interpolation must be explicitly verified")
            if len(stowed_local_solids.get(occurrence_id, [])) != len(deployed_local_solids.get(occurrence_id, [])):
                track_errors.append(f"{occurrence_id}: rigid interpolation endpoint solid counts differ")
        if mode == "CONSERVATIVE_ENDPOINT_BREPS" and (
            occurrence_id not in stowed.local_shapes or occurrence_id not in deployed.local_shapes
        ):
            track_errors.append(f"{occurrence_id}: both endpoint B-reps are required")
        if mode == "CONSERVATIVE_ENDPOINT_BREPS" and not bool(track.get("interpolation_verified", False)):
            track_errors.append(f"{occurrence_id}: conservative endpoint placement interpolation must be explicitly verified")
    missing_arm_tracks = [
        f"ARM-{index}" for index in (1, 2, 3)
        if tracks.get(f"ARM-{index}", {}).get("mode", "").upper() != "ARM_KINEMATIC"
    ]
    if missing_arm_tracks:
        track_errors.append(f"all three arms require ARM_KINEMATIC tracks: {missing_arm_tracks}")

    stowed_abs = {occ: location_from_matrix(row["absolute_transform_3x4"]) for occ, row in leaves["STOWED"].items()}
    deployed_abs = {occ: location_from_matrix(row["absolute_transform_3x4"]) for occ, row in leaves["DEPLOYED"].items()}
    for occurrence_id, track in tracks.items():
        if track.get("mode") != "KEYFRAMED_EXACT_BREP_VARIANTS":
            continue
        if occurrence_id not in leaves["STOWED"] or occurrence_id not in leaves["DEPLOYED"]:
            track_errors.append(f"{occurrence_id}: endpoint occurrence geometry is missing")
            continue
        stowed_matrix = leaves["STOWED"][occurrence_id]["absolute_transform_3x4"]
        deployed_matrix = leaves["DEPLOYED"][occurrence_id]["absolute_transform_3x4"]
        matrices = [stowed_matrix, deployed_matrix] + [
            sample.get("transform_matrix_3x4", [])
            for sample in track.get("samples", []) if isinstance(sample, dict)
        ]
        try:
            if any(
                len(matrix) != 3
                or any(not isinstance(row, list) or len(row) != 4 for row in matrix)
                for matrix in matrices
            ):
                raise ValueError("one or more transform matrices are not 3x4")
            if any(
                max(
                    abs(float(matrix[i][j]) - float(stowed_matrix[i][j]))
                    for i in range(3) for j in range(4)
                ) > 1.0e-9
                for matrix in matrices[1:]
            ):
                raise ValueError("endpoint/sample placement is not fixed and identical")
        except Exception as exc:
            track_errors.append(
                f"{occurrence_id}: exact endpoint B-rep variant placement contract failed: "
                f"{type(exc).__name__}: {exc}"
            )
    backup_spring_track = tracks.get("BACKUP-SPRING-001", {})
    if backup_spring_track.get("mode") == "AXIAL_COMPRESSION_SPRING_KINEMATIC":
        fixed_seat_id = str(backup_spring_track.get("fixed_seat_occurrence_id", ""))
        if fixed_seat_id in leaves["STOWED"] and fixed_seat_id in leaves["DEPLOYED"]:
            fixed_stowed_matrix = leaves["STOWED"][fixed_seat_id]["absolute_transform_3x4"]
            fixed_deployed_matrix = leaves["DEPLOYED"][fixed_seat_id]["absolute_transform_3x4"]
            if max(
                abs(float(fixed_stowed_matrix[i][j]) - float(fixed_deployed_matrix[i][j]))
                for i in range(3) for j in range(4)
            ) > 1.0e-9:
                track_errors.append(
                    "BACKUP-SPRING-FIXED-SEAT absolute transform differs between endpoints"
                )

    def axial_spring_geometry(
        track: dict[str, Any], spring_location: cq.Location,
    ) -> tuple[float, float, float]:
        """Return installed length, lateral residual, and seat-axis alignment."""
        fixed_seat_id = str(track["fixed_seat_occurrence_id"])
        fixed_face_location = (
            stowed_abs[fixed_seat_id]
            * loc_translation(0.0, 0.0, float(track["fixed_seat_face_offset_local_z_mm"]))
        )
        moving_matrix = matrix_3x4(spring_location)
        fixed_matrix = matrix_3x4(fixed_face_location)
        moving_origin = tuple(moving_matrix[i][3] for i in range(3))
        fixed_origin = tuple(fixed_matrix[i][3] for i in range(3))
        moving_axis = tuple(moving_matrix[i][2] for i in range(3))
        fixed_axis = tuple(fixed_matrix[i][2] for i in range(3))
        delta = tuple(fixed_origin[i] - moving_origin[i] for i in range(3))
        installed_length = sum(delta[i] * moving_axis[i] for i in range(3))
        lateral = math.sqrt(max(
            0.0, sum(value * value for value in delta) - installed_length * installed_length,
        ))
        axis_alignment = sum(moving_axis[i] * fixed_axis[i] for i in range(3))
        return installed_length, lateral, axis_alignment

    def sample_location(
        occurrence_id: str, angle: int, cache: dict[str, cq.Location], stack: set[str],
    ) -> cq.Location:
        if occurrence_id in cache:
            return cache[occurrence_id]
        if occurrence_id in stack:
            raise ValueError(f"motion-track parent cycle at {occurrence_id}")
        stack.add(occurrence_id)
        track = tracks[occurrence_id]
        mode = track["mode"]
        if mode == "ARM_KINEMATIC":
            arm_index = int(occurrence_id.rsplit("-", 1)[1])
            loc = arm_occurrence_loc(float(angle), (arm_index - 1) * 120.0)
        elif mode == "CROSSHEAD_KINEMATIC":
            delta_z = kinematic(float(angle))["crosshead_z_mm"] - kinematic(0.0)["crosshead_z_mm"]
            loc = loc_translation(0.0, 0.0, delta_z) * stowed_abs[occurrence_id]
        elif mode == "PARENT_RIGID":
            parent_id = str(track["parent_occurrence_id"])
            parent_loc = sample_location(parent_id, angle, cache, stack)
            loc = parent_loc * stowed_abs[parent_id].inverse * stowed_abs[occurrence_id]
        elif mode == "KEYFRAMED_TRANSFORMS":
            loc = location_from_matrix(track["samples"][angle]["transform_matrix_3x4"])
        elif mode == "KEYFRAMED_EXACT_BREP_VARIANTS":
            loc = location_from_matrix(track["samples"][angle]["transform_matrix_3x4"])
        elif mode == "AXIAL_COMPRESSION_SPRING_KINEMATIC":
            moving_seat_id = str(track["moving_seat_occurrence_id"])
            moving_seat_location = sample_location(moving_seat_id, angle, cache, stack)
            loc = (
                moving_seat_location
                * loc_translation(
                    0.0, 0.0, float(track["moving_seat_face_offset_local_z_mm"]),
                )
            )
            installed_length, lateral, alignment = axial_spring_geometry(track, loc)
            if installed_length <= 0.0 or lateral > 1.0e-7 or abs(alignment - 1.0) > 1.0e-10:
                raise ValueError(
                    f"axial spring seat geometry invalid at {angle} degrees: "
                    f"length={installed_length}, lateral={lateral}, alignment={alignment}"
                )
        elif mode in {"RIGID_ENDPOINT_INTERPOLATION", "CONSERVATIVE_ENDPOINT_BREPS"}:
            loc = interpolate_location(
                leaves["STOWED"][occurrence_id]["absolute_transform_3x4"],
                leaves["DEPLOYED"][occurrence_id]["absolute_transform_3x4"], angle / 80.0,
            )
        elif mode == "HOLD_STOWED":
            loc = stowed_abs[occurrence_id]
        else:
            raise ValueError(f"Unsupported motion mode for {occurrence_id}: {mode}")
        stack.remove(occurrence_id)
        cache[occurrence_id] = loc
        return loc

    motion_path = out_dir / "motion_full_mechanism_audit.csv.gz"
    fields = [
        "sample_index", "angle_deg", "occurrence_a", "solid_index_a", "variant_a",
        "part_number_a", "occurrence_b", "solid_index_b", "variant_b", "part_number_b",
        "aabb_overlap", "aabb_gap_mm", "exact_common_status", "common_volume_mm3",
        "documented_positive_volume_exception", "intentional_fit_exception_id",
        "exact_distance_status", "exact_clearance_mm", "result", "error",
    ]
    part_number_by_occurrence = {occ: row["part_number"] for occ, row in occurrences.items()}
    classification_by_occurrence = {occ: row["classification"] for occ, row in occurrences.items()}
    fit_register = validated_intentional_fits(stowed_inventory, "MOTION")
    used_fit_ids: set[str] = set()
    positive_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    total_rows = broadphase = documented_count = distance_blocked = 0
    minimum_clearance: float | None = None
    dynamic_ids = {
        occurrence_id for occurrence_id, track in tracks.items()
        if occurrence_id in occurrences and track.get("mode") != "HOLD_STOWED"
    }
    fixed_motion_solids = [
        MotionSolid(
            occurrence_id=solid.occurrence_id, part_number=solid.part_number,
            classification=solid.classification, solid_index=solid.solid_index,
            variant="STOWED", dynamic=False, shape=solid.shape, bbox=solid.bbox,
        )
        for solid in stowed.solid_records if solid.occurrence_id not in dynamic_ids
    ]

    with gzip.open(motion_path, "wt", newline="", encoding="utf-8", compresslevel=6) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for angle in angle_values:
            sample_index = angle + 1
            sample_counts: Counter[str] = Counter()
            cache: dict[str, cq.Location] = {}
            sample_solids = list(fixed_motion_solids)
            for occurrence_id in sorted(dynamic_ids):
                if occurrence_id not in stowed.local_shapes or occurrence_id not in tracks:
                    continue
                try:
                    loc = sample_location(occurrence_id, angle, cache, set())
                except Exception as exc:
                    track_errors.append(f"{occurrence_id}@{angle}: {type(exc).__name__}: {exc}")
                    continue
                mode = tracks[occurrence_id]["mode"]
                local_variants = [("STOWED", stowed_local_solids.get(occurrence_id, []))]
                if mode == "CONSERVATIVE_ENDPOINT_BREPS":
                    local_variants.append(("DEPLOYED", deployed_local_solids.get(occurrence_id, [])))
                elif mode == "KEYFRAMED_EXACT_BREP_VARIANTS":
                    selected_variant = str(
                        tracks[occurrence_id]["samples"][angle]["endpoint_variant"]
                    ).strip().upper()
                    selected_solids = (
                        stowed_local_solids if selected_variant == "STOWED"
                        else deployed_local_solids
                    ).get(occurrence_id, [])
                    local_variants = [(selected_variant, selected_solids)]
                elif mode == "AXIAL_COMPRESSION_SPRING_KINEMATIC":
                    try:
                        track = tracks[occurrence_id]
                        installed_length, lateral, alignment = axial_spring_geometry(track, loc)
                        if lateral > 1.0e-7 or abs(alignment - 1.0) > 1.0e-10:
                            raise ValueError(
                                f"seat axes are not coincident: lateral={lateral}, alignment={alignment}"
                            )
                        exact_spring = exact_motion_compression_spring(
                            float(track["outer_diameter_mm"]),
                            float(track["wire_diameter_mm"]),
                            installed_length,
                            float(track["total_turns"]),
                        )
                        local_variants = [(f"EXACT_KINEMATIC_{angle:02d}", [exact_spring.wrapped])]
                        if angle in {0, 80}:
                            endpoint_state = "STOWED" if angle == 0 else "DEPLOYED"
                            moving_seat_id = str(track["moving_seat_occurrence_id"])
                            moving_seat_location = sample_location(
                                moving_seat_id, angle, cache, set(),
                            )
                            moving_seat_matrix = matrix_3x4(moving_seat_location)
                            endpoint_moving_seat_matrix = leaves[endpoint_state][moving_seat_id][
                                "absolute_transform_3x4"
                            ]
                            if max(
                                abs(
                                    moving_seat_matrix[i][j]
                                    - float(endpoint_moving_seat_matrix[i][j])
                                )
                                for i in range(3) for j in range(4)
                            ) > 1.0e-9:
                                raise ValueError(
                                    f"{endpoint_state} moving-seat placement does not match its exact kinematic law"
                                )
                            endpoint_solids = (
                                stowed_local_solids if angle == 0 else deployed_local_solids
                            ).get(occurrence_id, [])
                            if len(endpoint_solids) != 1:
                                raise ValueError(
                                    f"{endpoint_state} endpoint has {len(endpoint_solids)} local solids"
                                )
                            endpoint_solid = endpoint_solids[0]
                            generated_bbox = bbox_raw(exact_spring.wrapped)
                            endpoint_bbox = bbox_raw(endpoint_solid)
                            generated_volume = exact_spring.Volume()
                            endpoint_volume = volume_raw(endpoint_solid)
                            common_status, common_volume, common_error = exact_common(
                                exact_spring.wrapped, endpoint_solid,
                            )
                            endpoint_matrix = leaves[endpoint_state][occurrence_id]["absolute_transform_3x4"]
                            generated_matrix = matrix_3x4(loc)
                            common_identity_tolerance_mm3 = max(
                                1.0e-5,
                                1.0e-7 * max(abs(generated_volume), abs(endpoint_volume), 1.0),
                            )
                            if (
                                common_status != "DONE"
                                or common_volume is None
                                or abs(generated_volume - common_volume) > common_identity_tolerance_mm3
                                or abs(endpoint_volume - common_volume) > common_identity_tolerance_mm3
                                or abs(generated_volume - endpoint_volume) > common_identity_tolerance_mm3
                                or max(abs(a - b) for a, b in zip(generated_bbox, endpoint_bbox)) > 1.0e-7
                                or surface_counts(exact_spring.wrapped) != surface_counts(endpoint_solid)
                                or max(
                                    abs(generated_matrix[i][j] - float(endpoint_matrix[i][j]))
                                    for i in range(3) for j in range(4)
                                ) > 1.0e-9
                            ):
                                raise ValueError(
                                    f"{endpoint_state} analytic B-rep/placement does not match the clean-reimported endpoint; "
                                    f"common_status={common_status}, common_volume={common_volume}, "
                                    f"common_error={common_error}, "
                                    f"common_identity_tolerance_mm3={common_identity_tolerance_mm3}"
                                )
                    except Exception as exc:
                        track_errors.append(
                            f"{occurrence_id}@{angle}: analytic B-rep generation/equivalence failed: "
                            f"{type(exc).__name__}: {exc}"
                        )
                        local_variants = []
                for variant, solids in local_variants:
                    for solid_index, local_solid in enumerate(solids, start=1):
                        moved = cq.Shape.cast(local_solid).moved(loc).wrapped
                        sample_solids.append(MotionSolid(
                            occurrence_id=occurrence_id,
                            part_number=part_number_by_occurrence.get(occurrence_id, ""),
                            classification=classification_by_occurrence.get(occurrence_id, ""),
                            solid_index=solid_index, variant=variant, dynamic=True,
                            shape=moved, bbox=bbox_raw(moved),
                        ))
            sample_solids.sort(key=lambda solid: (solid.occurrence_id, solid.variant, solid.solid_index))
            for a, b in itertools.combinations(sample_solids, 2):
                if not (a.dynamic or b.dynamic):
                    continue
                if a.occurrence_id == b.occurrence_id and a.variant != b.variant:
                    continue  # conservative endpoint variants are alternatives, not simultaneous solids
                total_rows += 1
                gap = aabb_gap(a.bbox, b.bbox)
                overlaps = gap <= AABB_TOL_MM
                common_status = "NOT_RUN_AABB_SEPARATED"
                common: float | None = 0.0
                distance_status = "NOT_RUN_OUTSIDE_NEAR_LIMIT"
                clearance: float | None = None
                error = ""
                if overlaps:
                    broadphase += 1
                    sample_counts["broadphase"] += 1
                    common_status, common, error = exact_common(a.shape, b.shape)
                documented = False
                exception_id = ""
                if common_status in {"ERROR", "NOT_DONE"}:
                    result = "BLOCKED_BOOLEAN"
                    sample_counts["blocked_boolean"] += 1
                    blocked_rows.append({
                        "angle_deg": angle, "occurrence_a": a.occurrence_id,
                        "solid_index_a": a.solid_index, "occurrence_b": b.occurrence_id,
                        "solid_index_b": b.solid_index, "status": common_status, "error": error,
                    })
                elif common is not None and common > COMMON_VOLUME_EPS_MM3:
                    documented, exception_id, _ = match_intentional_fit(
                        fit_register, a.occurrence_id, a.solid_index,
                        b.occurrence_id, b.solid_index, common,
                    )
                    if documented:
                        used_fit_ids.add(exception_id)
                        documented_count += 1
                        sample_counts["documented_positive"] += 1
                        result = "DOCUMENTED_POSITIVE_VOLUME"
                    else:
                        result = "UNAUTHORIZED_POSITIVE_VOLUME"
                        sample_counts["unauthorized_positive"] += 1
                        positive_rows.append({
                            "angle_deg": angle, "occurrence_a": a.occurrence_id,
                            "solid_index_a": a.solid_index, "variant_a": a.variant,
                            "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                            "variant_b": b.variant, "common_volume_mm3": common,
                        })
                    distance_status = "ZERO_BY_POSITIVE_COMMON"
                    clearance = 0.0
                else:
                    result = "CLEAR_OR_CONTACT"
                    if gap <= NEAR_DISTANCE_LIMIT_MM:
                        distance_status, clearance, dist_error = exact_distance(a.shape, b.shape)
                        if dist_error:
                            error = f"{error}; {dist_error}".strip("; ")
                        if distance_status != "DONE":
                            distance_blocked += 1
                            sample_counts["blocked_distance"] += 1
                            blocked_rows.append({
                                "angle_deg": angle, "occurrence_a": a.occurrence_id,
                                "solid_index_a": a.solid_index, "occurrence_b": b.occurrence_id,
                                "solid_index_b": b.solid_index,
                                "status": f"DISTANCE_{distance_status}", "error": dist_error,
                            })
                        elif clearance is not None:
                            minimum_clearance = clearance if minimum_clearance is None else min(minimum_clearance, clearance)
                writer.writerow({
                    "sample_index": sample_index, "angle_deg": angle,
                    "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                    "variant_a": a.variant, "part_number_a": a.part_number,
                    "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                    "variant_b": b.variant, "part_number_b": b.part_number,
                    "aabb_overlap": overlaps, "aabb_gap_mm": repr(gap),
                    "exact_common_status": common_status,
                    "common_volume_mm3": "" if common is None else repr(common),
                    "documented_positive_volume_exception": documented,
                    "intentional_fit_exception_id": exception_id,
                    "exact_distance_status": distance_status,
                    "exact_clearance_mm": "" if clearance is None else repr(clearance),
                    "result": result, "error": error,
                })
            sample_rows.append({
                **kinematic(float(angle)), "sample_index": sample_index,
                "active_dynamic_occurrences": len(dynamic_ids),
                "broadphase_candidates": sample_counts["broadphase"],
                "unauthorized_positive_volume_pairs": sample_counts["unauthorized_positive"],
                "documented_positive_volume_pairs": sample_counts["documented_positive"],
                "boolean_blocked_pairs": sample_counts["blocked_boolean"],
                "distance_blocked_pairs": sample_counts["blocked_distance"],
            })
    with (out_dir / "motion_kinematics_1deg.csv").open("w", newline="", encoding="utf-8") as stream:
        fields_kin = list(sample_rows[0])
        writer = csv.DictWriter(stream, fieldnames=fields_kin)
        writer.writeheader()
        writer.writerows(sample_rows)
    unique_track_errors = sorted(set(track_errors))
    return {
        "scope": "Every inventory MOVING/FLEXIBLE/SOFTGOOD occurrence explicitly tracked; every pair with at least one active dynamic occurrence audited",
        "scope_missing_occurrence_ids": scope_missing,
        "scope_missing": scope_missing,
        "track_validation_errors": unique_track_errors,
        "track_validation_error_count": len(unique_track_errors),
        "required_scope_occurrence_count": len(required_scope),
        "tracked_scope_occurrence_count": len(required_scope & set(tracks)),
        "active_dynamic_occurrence_count": len(dynamic_ids),
        "sample_count": len(sample_rows), "angle_increment_deg": 1,
        "pair_register": str(motion_path), "kinematics_register": str(out_dir / "motion_kinematics_1deg.csv"),
        "pair_row_count": total_rows, "broadphase_candidate_count": broadphase,
        "positive_volume_pair_count": len(positive_rows),
        "unauthorized_positive_volume_pair_count": len(positive_rows),
        "documented_positive_volume_pair_count": documented_count,
        "boolean_blocked_pair_count": sum(row["boolean_blocked_pairs"] for row in sample_rows),
        "distance_blocked_pair_count": distance_blocked,
        "minimum_exact_noninterfering_clearance_mm": minimum_clearance,
        "intentional_fit_register_errors": fit_register["errors"],
        "intentional_fit_register_error_count": len(fit_register["errors"]),
        "used_intentional_fit_exception_ids": sorted(used_fit_ids),
        "unused_intentional_fit_exception_ids": sorted(
            record["exception_id"] for record in fit_register["records"]
            if record["exception_id"] not in used_fit_ids
        ),
        "positive_rows": positive_rows, "blocked_rows": blocked_rows,
        "maximum_closure_residual_abs_mm": max(abs(row["closure_residual_mm"]) for row in sample_rows),
        "crosshead_travel_0_to_80_mm": sample_rows[-1]["crosshead_travel_mm"] - sample_rows[0]["crosshead_travel_mm"],
        "elapsed_seconds": time.time() - start,
    }


_MOTION_WORKER_ENDPOINTS: dict[str, EndpointData] | None = None
_MOTION_WORKER_INVENTORIES: dict[str, dict[str, Any]] | None = None
_MOTION_WORKER_CONTEXT_FINGERPRINT = ""


def _motion_context_fingerprint(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]],
) -> str:
    """Stable semantic identity for independently reimported motion inputs."""
    payload = {
        "endpoint_solids": {
            state: [
                {
                    "solid_key": solid.solid_key,
                    "part_number": solid.part_number,
                    "classification": solid.classification,
                    "valid": solid.valid,
                    "volume_mm3": repr(solid.volume_mm3),
                    "bbox_mm": [repr(value) for value in solid.bbox],
                }
                for solid in sorted(
                    endpoints[state].solid_records,
                    key=lambda row: (row.occurrence_id, row.solid_index, row.part_number),
                )
            ]
            for state in ("STOWED", "DEPLOYED")
        },
        "motion_tracks": {
            state: inventories[state].get("motion_tracks", [])
            for state in ("STOWED", "DEPLOYED")
        },
        "occurrence_scope": [
            {
                "occurrence_id": row.get("occurrence_id"),
                "part_number": row.get("part_number"),
                "classification": row.get("classification"),
            }
            for row in inventories["STOWED"].get("occurrences", [])
        ],
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _initialize_motion_worker(
    file_paths: dict[str, str], inventory_paths: dict[str, str],
    expected_hashes: dict[str, str],
) -> None:
    """Clean-reimport both endpoints once into isolated spawn-process state."""
    global _MOTION_WORKER_ENDPOINTS, _MOTION_WORKER_INVENTORIES
    global _MOTION_WORKER_CONTEXT_FINGERPRINT

    paths_to_verify = {
        **{f"STEP:{state}": Path(file_paths[state]) for state in ("STOWED", "DEPLOYED")},
        **{f"INVENTORY:{state}": Path(inventory_paths[state]) for state in ("STOWED", "DEPLOYED")},
    }
    for key, path in paths_to_verify.items():
        actual = sha256(path)
        if actual != expected_hashes.get(key):
            raise RuntimeError(
                f"Motion worker input hash mismatch for {key}: "
                f"expected={expected_hashes.get(key)}, actual={actual}"
            )

    inventories = {
        state: json.loads(Path(inventory_paths[state]).read_text(encoding="utf-8"))
        for state in ("STOWED", "DEPLOYED")
    }
    endpoints = {
        state: load_endpoint(state, Path(file_paths[state]), inventories[state])
        for state in ("STOWED", "DEPLOYED")
    }
    _MOTION_WORKER_ENDPOINTS = endpoints
    _MOTION_WORKER_INVENTORIES = inventories
    _MOTION_WORKER_CONTEXT_FINGERPRINT = _motion_context_fingerprint(endpoints, inventories)


def _run_motion_angle_task(task: tuple[int, str]) -> dict[str, Any]:
    """Evaluate one exact global angle and materialize an atomic evidence shard."""
    angle, output_directory = task
    if _MOTION_WORKER_ENDPOINTS is None or _MOTION_WORKER_INVENTORIES is None:
        raise RuntimeError("Motion worker context was not initialized")
    angle_dir = Path(output_directory)
    angle_dir.mkdir(parents=True, exist_ok=False)
    summary = _motion_angle_audit(
        _MOTION_WORKER_ENDPOINTS, _MOTION_WORKER_INVENTORIES, angle_dir, [angle],
    )
    pair_path = angle_dir / "motion_full_mechanism_audit.csv.gz"
    kinematics_path = angle_dir / "motion_kinematics_1deg.csv"
    if not pair_path.is_file() or not kinematics_path.is_file():
        raise RuntimeError(f"Motion angle {angle} did not materialize both evidence shards")
    return {
        "angle": angle,
        "context_fingerprint": _MOTION_WORKER_CONTEXT_FINGERPRINT,
        "summary": summary,
        "pair_path": str(pair_path),
        "pair_sha256": sha256(pair_path),
        "pair_size_bytes": pair_path.stat().st_size,
        "kinematics_path": str(kinematics_path),
        "kinematics_sha256": sha256(kinematics_path),
        "kinematics_size_bytes": kinematics_path.stat().st_size,
        "worker_pid": os.getpid(),
    }


def motion_audit(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]], out_dir: Path,
    worker_count: int = 8,
) -> dict[str, Any]:
    """Run all 81 exact angles in isolated spawn processes and merge in angle order."""
    if type(worker_count) is not int or not 1 <= worker_count <= 8:
        raise ValueError(f"motion worker_count must be an integer inside 1..8: {worker_count}")
    start = time.time()
    angles = list(range(81))
    expected_context_fingerprint = _motion_context_fingerprint(endpoints, inventories)
    file_paths = {
        state: str(endpoints[state].path.resolve()) for state in ("STOWED", "DEPLOYED")
    }
    inventory_paths = {
        state: str(INVENTORIES[state].resolve()) for state in ("STOWED", "DEPLOYED")
    }
    expected_hashes = {
        **{f"STEP:{state}": sha256(Path(file_paths[state])) for state in ("STOWED", "DEPLOYED")},
        **{
            f"INVENTORY:{state}": sha256(Path(inventory_paths[state]))
            for state in ("STOWED", "DEPLOYED")
        },
    }

    with tempfile.TemporaryDirectory(prefix="stingray_motion_angle_shards_") as temporary_root:
        tasks = [
            (angle, str(Path(temporary_root) / f"angle_{angle:02d}"))
            for angle in angles
        ]
        spawn_context = multiprocessing.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=worker_count,
            mp_context=spawn_context,
            initializer=_initialize_motion_worker,
            initargs=(file_paths, inventory_paths, expected_hashes),
        ) as executor:
            shard_results = list(executor.map(_run_motion_angle_task, tasks, chunksize=1))

        shard_results.sort(key=lambda row: row["angle"])
        actual_angles = [row["angle"] for row in shard_results]
        if actual_angles != angles:
            raise RuntimeError(
                f"Motion shard angle coverage mismatch: expected={angles}, actual={actual_angles}"
            )
        for shard in shard_results:
            if shard["context_fingerprint"] != expected_context_fingerprint:
                raise RuntimeError(
                    f"Motion angle {shard['angle']} context fingerprint mismatch: "
                    f"expected={expected_context_fingerprint}, "
                    f"actual={shard['context_fingerprint']}"
                )

        motion_path = out_dir / "motion_full_mechanism_audit.csv.gz"
        pair_fieldnames: list[str] | None = None
        merged_pair_rows = 0
        with gzip.open(motion_path, "wt", newline="", encoding="utf-8", compresslevel=6) as stream:
            writer: csv.DictWriter[str] | None = None
            for shard in shard_results:
                angle = shard["angle"]
                pair_path = Path(shard["pair_path"])
                if (
                    not pair_path.is_file()
                    or pair_path.stat().st_size != shard["pair_size_bytes"]
                    or sha256(pair_path) != shard["pair_sha256"]
                ):
                    raise RuntimeError(f"Motion angle {angle} pair shard integrity check failed")
                shard_row_count = 0
                with gzip.open(pair_path, "rt", newline="", encoding="utf-8") as shard_stream:
                    reader = csv.DictReader(shard_stream)
                    if pair_fieldnames is None:
                        pair_fieldnames = list(reader.fieldnames or [])
                        if not pair_fieldnames:
                            raise RuntimeError("First motion pair shard has no CSV header")
                        writer = csv.DictWriter(stream, fieldnames=pair_fieldnames)
                        writer.writeheader()
                    elif list(reader.fieldnames or []) != pair_fieldnames:
                        raise RuntimeError(f"Motion angle {angle} pair shard schema mismatch")
                    assert writer is not None
                    for row in reader:
                        if int(row["sample_index"]) != angle + 1 or int(row["angle_deg"]) != angle:
                            raise RuntimeError(
                                f"Motion angle {angle} pair shard contains an out-of-angle row"
                            )
                        writer.writerow(row)
                        shard_row_count += 1
                expected_rows = int(shard["summary"]["pair_row_count"])
                if shard_row_count != expected_rows:
                    raise RuntimeError(
                        f"Motion angle {angle} pair row mismatch: "
                        f"expected={expected_rows}, actual={shard_row_count}"
                    )
                merged_pair_rows += shard_row_count

        kinematics_rows: list[dict[str, str]] = []
        kinematics_fieldnames: list[str] | None = None
        for shard in shard_results:
            angle = shard["angle"]
            kinematics_path = Path(shard["kinematics_path"])
            if (
                not kinematics_path.is_file()
                or kinematics_path.stat().st_size != shard["kinematics_size_bytes"]
                or sha256(kinematics_path) != shard["kinematics_sha256"]
            ):
                raise RuntimeError(f"Motion angle {angle} kinematics shard integrity check failed")
            with kinematics_path.open("r", newline="", encoding="utf-8") as shard_stream:
                reader = csv.DictReader(shard_stream)
                fields = list(reader.fieldnames or [])
                if kinematics_fieldnames is None:
                    kinematics_fieldnames = fields
                    if not kinematics_fieldnames:
                        raise RuntimeError("First motion kinematics shard has no CSV header")
                elif fields != kinematics_fieldnames:
                    raise RuntimeError(f"Motion angle {angle} kinematics shard schema mismatch")
                rows = list(reader)
            if len(rows) != 1:
                raise RuntimeError(
                    f"Motion angle {angle} must emit exactly one kinematics row; actual={len(rows)}"
                )
            row = rows[0]
            if "arm_angle_deg" not in row:
                raise RuntimeError(
                    f"Motion angle {angle} kinematics row lacks arm_angle_deg"
                )
            if int(row["sample_index"]) != angle + 1 or int(float(row["arm_angle_deg"])) != angle:
                raise RuntimeError(f"Motion angle {angle} kinematics row identity mismatch")
            kinematics_rows.append(row)

        kinematics_path = out_dir / "motion_kinematics_1deg.csv"
        with kinematics_path.open("w", newline="", encoding="utf-8") as stream:
            if kinematics_fieldnames is None:
                raise RuntimeError("Motion kinematics merge has no schema")
            writer = csv.DictWriter(stream, fieldnames=kinematics_fieldnames)
            writer.writeheader()
            writer.writerows(kinematics_rows)

        summaries = [row["summary"] for row in shard_results]
        if any(summary["sample_count"] != 1 for summary in summaries):
            raise RuntimeError("Every motion angle shard must report exactly one sample")
        if merged_pair_rows != sum(int(summary["pair_row_count"]) for summary in summaries):
            raise RuntimeError("Merged motion pair count does not equal the complete shard sum")

        invariant_keys = (
            "scope", "scope_missing_occurrence_ids", "scope_missing",
            "required_scope_occurrence_count", "tracked_scope_occurrence_count",
            "active_dynamic_occurrence_count", "intentional_fit_register_errors",
            "intentional_fit_register_error_count",
        )
        reference = summaries[0]
        for angle, summary in zip(angles[1:], summaries[1:]):
            for key in invariant_keys:
                if summary[key] != reference[key]:
                    raise RuntimeError(f"Motion angle {angle} invariant summary mismatch for {key}")

        used_fit_ids = {
            exception_id
            for summary in summaries
            for exception_id in summary["used_intentional_fit_exception_ids"]
        }
        complete_fit_ids: set[str] | None = None
        for angle, summary in zip(angles, summaries):
            shard_fit_ids = set(summary["used_intentional_fit_exception_ids"]) | set(
                summary["unused_intentional_fit_exception_ids"]
            )
            if complete_fit_ids is None:
                complete_fit_ids = shard_fit_ids
            elif shard_fit_ids != complete_fit_ids:
                raise RuntimeError(f"Motion angle {angle} intentional-fit register identity mismatch")
        complete_fit_ids = complete_fit_ids or set()

        positive_rows = [row for summary in summaries for row in summary["positive_rows"]]
        blocked_rows = [row for summary in summaries for row in summary["blocked_rows"]]
        track_errors = sorted({
            error for summary in summaries for error in summary["track_validation_errors"]
        })
        minimum_clearances = [
            float(summary["minimum_exact_noninterfering_clearance_mm"])
            for summary in summaries
            if summary["minimum_exact_noninterfering_clearance_mm"] is not None
        ]

    execution_topology = {
        "mode": "SPAWN_PROCESS_PER_EXACT_ANGLE",
        "start_method": "spawn",
        "worker_count": worker_count,
        "task_count": len(angles),
        "angles_per_task": 1,
        "angle_order": "0..80 inclusive",
        "merge_order": "strict ascending angle; original per-angle sorted-solid pair order",
        "worker_import": "clean XCAF reimport of both endpoint STEP masters once per process",
        "nested_occt_parallelism": False,
        "context_fingerprint_sha256": expected_context_fingerprint,
    }
    return {
        "scope": reference["scope"],
        "scope_missing_occurrence_ids": reference["scope_missing_occurrence_ids"],
        "scope_missing": reference["scope_missing"],
        "track_validation_errors": track_errors,
        "track_validation_error_count": len(track_errors),
        "required_scope_occurrence_count": reference["required_scope_occurrence_count"],
        "tracked_scope_occurrence_count": reference["tracked_scope_occurrence_count"],
        "active_dynamic_occurrence_count": reference["active_dynamic_occurrence_count"],
        "sample_count": len(kinematics_rows), "angle_increment_deg": 1,
        "pair_register": str(motion_path), "kinematics_register": str(kinematics_path),
        "pair_row_count": merged_pair_rows,
        "broadphase_candidate_count": sum(int(summary["broadphase_candidate_count"]) for summary in summaries),
        "positive_volume_pair_count": len(positive_rows),
        "unauthorized_positive_volume_pair_count": len(positive_rows),
        "documented_positive_volume_pair_count": sum(
            int(summary["documented_positive_volume_pair_count"]) for summary in summaries
        ),
        "boolean_blocked_pair_count": sum(
            int(summary["boolean_blocked_pair_count"]) for summary in summaries
        ),
        "distance_blocked_pair_count": sum(
            int(summary["distance_blocked_pair_count"]) for summary in summaries
        ),
        "minimum_exact_noninterfering_clearance_mm": (
            min(minimum_clearances) if minimum_clearances else None
        ),
        "intentional_fit_register_errors": reference["intentional_fit_register_errors"],
        "intentional_fit_register_error_count": reference["intentional_fit_register_error_count"],
        "used_intentional_fit_exception_ids": sorted(used_fit_ids),
        "unused_intentional_fit_exception_ids": sorted(complete_fit_ids - used_fit_ids),
        "positive_rows": positive_rows, "blocked_rows": blocked_rows,
        "maximum_closure_residual_abs_mm": max(
            abs(float(row["closure_residual_mm"])) for row in kinematics_rows
        ),
        "crosshead_travel_0_to_80_mm": (
            float(kinematics_rows[-1]["crosshead_travel_mm"])
            - float(kinematics_rows[0]["crosshead_travel_mm"])
        ),
        "execution_topology": execution_topology,
        "elapsed_seconds": time.time() - start,
    }


def gate(gate_id: str, requirement: str, status: str, measured: Any, evidence: str, note: str = "") -> dict[str, Any]:
    if status not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError(f"Invalid gate status: {status}")
    return {
        "gate_id": gate_id, "requirement": requirement, "status": status,
        "measured": measured, "evidence": evidence, "note": note,
    }


def compute_gates(
    endpoints: dict[str, EndpointData], inventories: dict[str, dict[str, Any]],
    pair_results: dict[str, dict[str, Any]], parity: dict[str, Any],
    connectivity: dict[str, dict[str, Any]], dimensions: dict[str, Any],
    reconciliation: dict[str, Any], motion: dict[str, Any],
    definition_of_done: dict[str, Any], out_dir: Path,
) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    for state in ("STOWED", "DEPLOYED"):
        step = endpoints[state].step_text
        leaf_identity = reconciliation["imported_leaf_identity_audits"][state]
        hierarchy = reconciliation["hierarchy_audits"][state]
        exact_solid_entities = step["manifold_solid_brep_count"] + step["brep_with_voids_count"]
        gates.append(gate(
            f"AP242-{state}", f"{state} master is AP242 exact B-rep with named products/occurrences",
            "PASS" if step["ap242_schema_detected"] and step["faceted_or_tessellated_total"] == 0
            and exact_solid_entities > 0 and step["closed_shell_count"] >= exact_solid_entities
            and step["millimetre_length_unit_detected"]
            and step["product_count"] > 0 and step["nauo_count"] > 0
            and step["unnamed_product_count"] == 0 and step["unnamed_nauo_name_count"] == 0
            and leaf_identity["accepted"] and hierarchy["accepted"] else "FAIL",
            {
                "schema": step["schema_record"], "faceted_or_tessellated_total": step["faceted_or_tessellated_total"],
                "manifold_solid_brep_count": step["manifold_solid_brep_count"],
                "brep_with_voids_count": step["brep_with_voids_count"],
                "closed_shell_count": step["closed_shell_count"],
                "millimetre_length_unit_detected": step["millimetre_length_unit_detected"],
                "unnamed_products": step["unnamed_product_count"], "unnamed_nauos": step["unnamed_nauo_name_count"],
                "imported_leaf_identity_audit": leaf_identity,
                "assembly_hierarchy_audit": hierarchy,
            }, "step_text_inspection.json",
        ))
        invalid = dimensions[state.lower()]["invalid_solid_count"]
        gates.append(gate(
            f"BREP-VALID-{state}", f"Every reimported {state} leaf solid passes BRepCheck_Analyzer",
            "PASS" if invalid == 0 else "FAIL", {"invalid_solid_count": invalid},
            f"leaf_solids_{state.lower()}.csv",
        ))
        pairs = pair_results[state]
        interference_status = "BLOCKED" if pairs["boolean_blocked_pair_count"] else (
            "PASS" if pairs["unauthorized_positive_volume_pair_count"] == 0 else "FAIL"
        )
        gates.append(gate(
            f"INTERFERENCE-{state}", f"Zero undocumented positive-volume intersections in {state}",
            interference_status,
            {
                "all_unordered_pairs": pairs["unordered_pair_count"],
                "unauthorized_positive_volume_pairs": pairs["unauthorized_positive_volume_pair_count"],
                "boolean_blocked_pairs": pairs["boolean_blocked_pair_count"],
            }, f"endpoint_interference_register.csv; endpoint_pair_audit_{state.lower()}.csv.gz",
            "Only measured positives inside a finite state-specific occurrence/solid-pair process bound are documented exceptions.",
        ))
        fit_definition_failed = bool(
            pairs["intentional_fit_register_error_count"]
            or pairs["unused_intentional_fit_exception_ids"]
        )
        gates.append(gate(
            f"INTENTIONAL-FIT-REGISTER-{state}",
            f"Every {state} positive-volume exception is unique, bounded, process-based, and exercised",
            "FAIL" if fit_definition_failed else "PASS",
            {
                "valid_record_count": pairs["intentional_fit_register_valid_record_count"],
                "definition_errors": pairs["intentional_fit_register_errors"],
                "unused_exception_ids": pairs["unused_intentional_fit_exception_ids"],
                "used_exception_ids": pairs["used_intentional_fit_exception_ids"],
            }, f"authoring_inventory_{state.lower()}.json; endpoint_pair_audit_{state.lower()}.csv.gz",
        ))
        missing_exact_near_minimum = bool(
            pairs["near_noninterfering_candidate_pair_count"] > 0
            and (
                pairs["exact_distance_measured_pair_count"] == 0
                or pairs["minimum_exact_noninterfering_clearance_mm"] is None
            )
        )
        distance_status = "BLOCKED" if (
            pairs["distance_blocked_pair_count"] or missing_exact_near_minimum
        ) else "PASS"
        gates.append(gate(
            f"CLEARANCE-EVIDENCE-{state}", f"Near-pair exact clearance evidence completes for {state}",
            distance_status,
            {
                "near_limit_mm": NEAR_DISTANCE_LIMIT_MM,
                "near_noninterfering_candidate_pair_count": pairs["near_noninterfering_candidate_pair_count"],
                "exact_distance_measured_pair_count": pairs["exact_distance_measured_pair_count"],
                "minimum_exact_noninterfering_clearance_mm": pairs["minimum_exact_noninterfering_clearance_mm"],
                "distance_blocked_pairs": pairs["distance_blocked_pair_count"],
                "missing_exact_near_minimum": missing_exact_near_minimum,
            }, f"minimum_clearance_register.csv; endpoint_pair_audit_{state.lower()}.csv.gz",
            "Pairs outside the near limit retain a conservative positive AABB lower bound in the exhaustive register.",
        ))

    gates.append(gate(
        "STATE-PARITY", "The two masters contain the same occurrence identities and rigid part definitions",
        "PASS" if parity["overall_issue_count"] == 0 else "FAIL", parity, "state_parity.csv",
    ))
    unmapped = sum(
        1 for endpoint in endpoints.values() for row in endpoint.occurrence_rows
        if row["has_shape"] and not row["mapped_to_authoring_inventory"]
    )
    identity_without_note = sum(
        1 for inv in inventories.values() for occurrence in inv["occurrences"]
        if occurrence["identity_transform"] and not occurrence.get("notes", "").strip()
    )
    transform_mismatches: list[dict[str, Any]] = []
    maximum_transform_element_error = 0.0
    for state in ("STOWED", "DEPLOYED"):
        imported = leaf_lookup(endpoints[state])
        for occurrence in inventories[state]["occurrences"]:
            occurrence_id = occurrence["occurrence_id"]
            if occurrence_id not in imported:
                continue
            expected = occurrence.get("transform_matrix_3x4")
            measured = imported[occurrence_id]["absolute_transform_3x4"]
            if not isinstance(expected, list) or len(expected) != 3:
                transform_mismatches.append({
                    "state": state, "occurrence_id": occurrence_id, "reason": "missing authoring transform matrix",
                })
                continue
            try:
                error = max(abs(float(expected[i][j]) - float(measured[i][j])) for i in range(3) for j in range(4))
            except (TypeError, ValueError, IndexError):
                transform_mismatches.append({
                    "state": state, "occurrence_id": occurrence_id, "reason": "invalid authoring transform matrix",
                })
                continue
            maximum_transform_element_error = max(maximum_transform_element_error, error)
            if error > 1.0e-8:
                transform_mismatches.append({
                    "state": state, "occurrence_id": occurrence_id,
                    "maximum_matrix_element_error": error,
                })
    gates.append(gate(
        "OCCURRENCE-TRANSFORMS", "Every XCAF leaf maps to an occurrence and identity placements are justified",
        "PASS" if unmapped == 0 and identity_without_note == 0 and not transform_mismatches else "FAIL",
        {"unmapped_leaf_occurrences": unmapped,
         "identity_occurrences_without_justification": identity_without_note,
         "maximum_transform_matrix_element_error": maximum_transform_element_error,
         "transform_mismatches": transform_mismatches},
        "xcaf_occurrences_stowed.csv; xcaf_occurrences_deployed.csv",
    ))
    gates.append(gate(
        "OCCURRENCE-BOM-RECONCILIATION",
        "Every AP242 leaf occurrence reconciles one-to-one to a unique occurrence-BOM row and part definition",
        "PASS" if reconciliation["issue_count"] == 0 else "FAIL",
        reconciliation, "occurrence_bom_reconciliation.csv",
    ))

    def dod_section_gate(
        gate_id: str, requirement: str, state_sections: list[tuple[str, str]],
    ) -> None:
        measured = {
            state: definition_of_done[state]["sections"].get(section, {
                "status": "FAIL", "failure_count": 1, "blocked_count": 0,
                "error": "required calculated section absent",
            })
            for state, section in state_sections
        }
        statuses = [row["status"] for row in measured.values()]
        status = "FAIL" if "FAIL" in statuses else "BLOCKED" if "BLOCKED" in statuses else "PASS"
        gates.append(gate(
            gate_id, requirement, status, measured, "definition_of_done_audit.json",
            "Acceptance uses authoring scope plus clean-reimport solid, mass, exact-distance, attachment, and route evidence; inventory status text is ignored.",
        ))

    dod_section_gate(
        "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "Every declared required fastener/retainer is a positive-mass valid AP242 occurrence and every retained pin has modeled support and retention engagement",
        [("STOWED", "required_hardware_and_pin_retention"), ("DEPLOYED", "required_hardware_and_pin_retention")],
    )
    dod_section_gate(
        "DOD-POSITIVE-DEPLOYED-LOCKS",
        "All three arms have complete positive deployed-lock mechanisms with modeled hardware, attachment/motion definitions, and exact engaged endpoint geometry",
        [("DEPLOYED", "positive_deployed_locks")],
    )
    dod_section_gate(
        "DOD-POSITIVE-STOWED-RETENTION",
        "All three arms have complete distributed positive stowed-retention mechanisms with modeled hardware, attachment/motion definitions, and exact retained endpoint geometry",
        [("STOWED", "positive_stowed_retention")],
    )
    dod_section_gate(
        "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
        "Every declared pressure reservoir is physically closed and its isolation valves, collection routes, manifold, fittings, and required connections have calculated geometry evidence",
        [("STOWED", "closed_pressure_subsystems"), ("DEPLOYED", "closed_pressure_subsystems")],
    )
    dod_section_gate(
        "DOD-CLOSED-ROUTE-ENDS",
        "Every authored route is explicitly in the closure scope and each non-external route/tube end has an exact connected termination",
        [("STOWED", "closed_route_ends"), ("DEPLOYED", "closed_route_ends")],
    )

    arm_rows = dimensions["arms"]
    clock_error = max(abs((((r["measured_axis_clock_deg"] - r["required_clock_deg"]) + 180) % 360) - 180) for r in arm_rows)
    stowed_angle_error = max(abs(r["measured_axis_angle_deg"]) for r in arm_rows if r["state"] == "STOWED")
    deployed_angle_error = max(abs(r["measured_axis_angle_deg"] - DEPLOYED_ANGLE_DEG) for r in arm_rows if r["state"] == "DEPLOYED")
    arm_length_error = max(abs(r["local_pivot_to_tip_extent_mm"] - ARM_LENGTH_MM) for r in arm_rows)
    gates.append(gate(
        "ARM-KINEMATICS-ENDPOINTS", "Three arms are clocked 0/120/240 degrees and move 0 to 80 degrees",
        "PASS" if clock_error <= 1e-7 and stowed_angle_error <= 1e-7 and deployed_angle_error <= 1e-7 else "FAIL",
        {"maximum_clock_error_deg": clock_error, "maximum_stowed_angle_error_deg": stowed_angle_error,
         "maximum_deployed_angle_error_deg": deployed_angle_error}, "key_dimensions.json",
    ))
    gates.append(gate(
        "ARM-LENGTH", "Each arm pivot-to-tip extent is 733.806 mm",
        "PASS" if arm_length_error <= 1e-6 else "FAIL",
        {"maximum_absolute_error_mm": arm_length_error, "measurements": arm_rows}, "key_dimensions.json",
    ))
    arm_surface_failures = [
        {
            "state": row["state"], "arm_index": row["arm_index"],
            "face_count": row["face_count"], "surface_types": row["surface_types"],
        }
        for row in arm_rows
        if row["face_count"] > 150
        or sum(count for name, count in row["surface_types"].items() if name != "Plane") == 0
    ]
    gates.append(gate(
        "ARM-SURFACE-QUALITY",
        "Each arm is a compact smooth exact B-rep with curved analytic/spline faces and no planar-patch faceting",
        "PASS" if not arm_surface_failures else "FAIL",
        {"maximum_allowed_faces_per_arm": 150, "failures": arm_surface_failures,
         "measurements": [{"state": row["state"], "arm_index": row["arm_index"],
                           "face_count": row["face_count"], "surface_types": row["surface_types"]}
                          for row in arm_rows]},
        "key_dimensions.json; leaf_solids_stowed.csv; leaf_solids_deployed.csv",
    ))
    travel = dimensions["crosshead_travel_from_reimported_transforms_mm"]
    gates.append(gate(
        "CROSSHEAD-TRAVEL", "Crosshead travel is at least 15.050 mm at full precision",
        "PASS" if travel >= MIN_CROSSHEAD_TRAVEL_MM else "FAIL",
        {"travel_mm": travel, "minimum_mm": MIN_CROSSHEAD_TRAVEL_MM,
         "independent_equation_mm": dimensions["crosshead_travel_from_independent_closure_equation_mm"]},
        "key_dimensions.json; motion_kinematics_1deg.csv",
    ))
    arm_span = dimensions["arm_module_stowed_xy_span_mm"]
    normal_spans = dimensions["normal_body_oml_xy_spans_mm"]
    missing_normal_oml_ids = dimensions["normal_body_oml_missing_occurrence_ids"]
    gates.append(gate(
        "NORMAL-BODY-OML", "Normal shell/fixed-sector OML does not exceed the 53.0 mm target",
        "PASS" if (
            not missing_normal_oml_ids
            and set(normal_spans) == REQUIRED_NORMAL_OML_OCCURRENCE_IDS
            and max(normal_spans.values()) <= NORMAL_OD_MM + 1e-6
        ) else "FAIL",
        {
            "required_occurrence_ids": sorted(REQUIRED_NORMAL_OML_OCCURRENCE_IDS),
            "missing_occurrence_ids": missing_normal_oml_ids,
            "measured_xy_spans_mm": normal_spans,
            "target_max_mm": NORMAL_OD_MM,
        },
        "key_dimensions.json",
    ))
    gates.append(gate(
        "ARM-MODULE-HARD-ENVELOPE", "Stowed arm-module hard XY span is no more than 57.150 mm",
        "PASS" if arm_span is not None and arm_span <= HARD_OD_MM + 1e-7 else "FAIL",
        {"measured_span_mm": arm_span, "limit_mm": HARD_OD_MM, "normal_target_mm": NORMAL_OD_MM},
        "key_dimensions.json",
    ))
    rigid_lengths = {state: dimensions[state.lower()]["rigid_length_mm"] for state in ("STOWED", "DEPLOYED")}
    gates.append(gate(
        "RIGID-LENGTH", "Complete rigid length is no more than 2032 mm in both endpoint states",
        "PASS" if all(v is not None and v <= MAX_RIGID_LENGTH_MM + 1e-7 for v in rigid_lengths.values()) else "FAIL",
        {"measured_mm": rigid_lengths, "limit_mm": MAX_RIGID_LENGTH_MM}, "key_dimensions.json",
    ))
    mass_missing = dimensions["mass_unresolved_occurrence_ids"]
    mass_invalid = dimensions["mass_invalid_occurrence_ids"]
    mass_invariance_errors = (
        dimensions["mass_override_state_mismatch_keys"]
        + dimensions["part_mass_state_mismatch_part_numbers"]
        + dimensions["mass_override_invalid_or_unknown_keys"]
    )
    resolved_mass = dimensions["mass_rollup_from_authoring_inventory_kg"]
    mass_status = "BLOCKED" if mass_missing or mass_invalid else (
        "FAIL" if mass_invariance_errors else
        "PASS" if resolved_mass <= MAX_SYSTEM_MASS_KG and MAX_SYSTEM_MASS_KG - resolved_mass >= MIN_MASS_RESERVE_KG else "FAIL"
    )
    gates.append(gate(
        "SYSTEM-MASS", "System mass is <=18.14 kg with >=1.0 kg reserve and every installed occurrence has a positive resolved mass",
        mass_status,
        {"resolved_mass_kg": resolved_mass, "unresolved_occurrence_ids": mass_missing,
         "invalid_mass_occurrence_ids": mass_invalid,
         "state_invariance_errors": mass_invariance_errors,
         "resolved-only-reserve_kg": MAX_SYSTEM_MASS_KG - resolved_mass}, "key_dimensions.json",
    ))

    floating = sum(v["floating_rigid_count"] for v in connectivity.values())
    dangling = sum(v["dangling_connection_count"] for v in connectivity.values())
    self_count = sum(v["self_connection_count"] for v in connectivity.values())
    generic = sum(v["generic_or_blanket_evidence_count"] for v in connectivity.values())
    unsupported = sum(v["geometric_or_fastener_unsupported_connection_count"] for v in connectivity.values())
    uncovered = sum(v["uncovered_attachment_endpoint_occurrence_count"] for v in connectivity.values())
    failed_routes = sum(v["failed_route_count"] for v in connectivity.values())
    invalid_attachment_rows = sum(v["invalid_attachment_record_count"] for v in connectivity.values())
    blank_attachment_ids = sum(v["blank_attachment_id_count"] for v in connectivity.values())
    duplicate_attachment_ids = sum(v["duplicate_attachment_id_count"] for v in connectivity.values())
    invalid_route_rows = sum(v["invalid_route_record_count"] for v in connectivity.values())
    blank_route_ids = sum(v["blank_route_id_count"] for v in connectivity.values())
    duplicate_route_ids = sum(v["duplicate_route_id_count"] for v in connectivity.values())
    gates.append(gate(
        "ATTACHMENT-COHESION", "Every governed installed occurrence and route has occurrence-specific geometric or fastener-supported attachment and exact termination evidence",
        "PASS" if (
            floating == 0 and dangling == 0 and self_count == 0 and generic == 0
            and unsupported == 0 and uncovered == 0 and failed_routes == 0
            and invalid_attachment_rows == 0 and blank_attachment_ids == 0
            and duplicate_attachment_ids == 0 and invalid_route_rows == 0
            and blank_route_ids == 0 and duplicate_route_ids == 0
        ) else "FAIL",
        {"floating_rigid_rows_across_states": floating, "dangling_connections_across_states": dangling,
         "self_connections_across_states": self_count, "generic_evidence_rows_across_states": generic,
         "geometric_or_fastener_unsupported_connections_across_states": unsupported,
         "uncovered_attachment_endpoint_occurrences_across_states": uncovered,
         "uncovered_attachment_endpoint_occurrence_ids_by_state": {
             state: value["uncovered_attachment_endpoint_occurrence_ids"]
             for state, value in connectivity.items()
         },
         "invalid_attachment_rows_across_states": invalid_attachment_rows,
         "blank_attachment_ids_across_states": blank_attachment_ids,
         "duplicate_attachment_ids_across_states": duplicate_attachment_ids,
         "invalid_route_rows_across_states": invalid_route_rows,
         "blank_route_ids_across_states": blank_route_ids,
         "duplicate_route_ids_across_states": duplicate_route_ids,
         "failed_routes_across_states": failed_routes},
        "connectivity_summary.json; attachment_geometry_stowed.csv; attachment_geometry_deployed.csv; route_termination_audit_stowed.csv; route_termination_audit_deployed.csv",
    ))
    load_path_ok = all(v["continuous_recovery_load_path_found"] for v in connectivity.values())
    gates.append(gate(
        "RECOVERY-LOAD-PATH", "A continuous structural graph connects body hardpoint to harness terminal in both states",
        "PASS" if load_path_ok else "FAIL",
        {state: v["body_hardpoint_to_harness_terminal_path"] for state, v in connectivity.items()},
        "connectivity_summary.json",
        "Flexible/control/inflation routes are not accepted as implicit structural substitutes.",
    ))

    parts = [
        {**part, "_validation_state": state}
        for state in ("STOWED", "DEPLOYED")
        for part in inventories[state].get("parts", [])
        if isinstance(part, dict)
    ]
    part_number = lambda part: (
        f"{part.get('_validation_state', '')}:"
        f"{str(part.get('part_number', '')).strip()}"
    )
    part_title = lambda part: str(part.get("title", part.get("description", ""))).strip()
    make_buy = lambda part: str(part.get("make_buy", "")).strip().upper()
    provisional = [
        part_number(part) for part in parts
        if "PROVISIONAL" in str(part.get("cad_classification", "")).upper()
    ]
    invalid_make_buy = [
        part_number(part) for part in parts if make_buy(part) not in {"MAKE", "BUY"}
    ]
    buy_without_title = [
        part_number(part) for part in parts if make_buy(part) == "BUY" and not part_title(part)
    ]
    buy_without_material = [
        part_number(part) for part in parts
        if make_buy(part) == "BUY" and not str(part.get("material", "")).strip()
    ]
    buy_without_manufacturer = [
        part_number(part) for part in parts
        if make_buy(part) == "BUY" and not str(part.get("manufacturer", "")).strip()
    ]
    buy_without_vendor_cad_classification = [
        part_number(part) for part in parts
        if make_buy(part) == "BUY" and not str(part.get("cad_classification", "")).strip()
    ]
    buy_with_invalid_product_url = [
        part_number(part) for part in parts
        if make_buy(part) == "BUY" and not valid_http_url(part.get("source_url"))
    ]
    buy_with_invalid_purchase_url = [
        part_number(part) for part in parts
        if make_buy(part) == "BUY" and not valid_http_url(part.get("purchase_url"))
    ]
    incomplete_buy_identity = [
        part_number(part) for part in parts if make_buy(part) == "BUY" and (
            not str(part.get("manufacturer", "")).strip()
            or any(
                token in " ".join(
                    str(part.get(key, ""))
                    for key in ("manufacturer", "cad_classification", "notes")
                ).upper()
                for token in ("TBD", "HELD", "HOLD")
            )
        )
    ]
    make_without_title_material_or_process = [
        part_number(part) for part in parts if make_buy(part) == "MAKE" and (
            not part_title(part)
            or not str(part.get("process", "")).strip()
            or not str(part.get("material", "")).strip()
        )
    ]
    procurement_failures = (
        provisional + invalid_make_buy + buy_without_title + buy_without_material
        + buy_without_manufacturer + buy_without_vendor_cad_classification
        + buy_with_invalid_product_url + buy_with_invalid_purchase_url
        + incomplete_buy_identity + make_without_title_material_or_process
    )
    gates.append(gate(
        "PROCUREMENT-DEFINITION", "Purchased identities/sourcing and make-process definitions are complete and non-provisional",
        "PASS" if not procurement_failures else "FAIL",
        {"provisional_part_numbers": provisional, "invalid_make_buy_part_numbers": invalid_make_buy,
         "buy_parts_without_title": buy_without_title,
         "buy_parts_without_material": buy_without_material,
         "buy_parts_without_manufacturer": buy_without_manufacturer,
         "buy_parts_without_vendor_cad_classification": buy_without_vendor_cad_classification,
         "buy_parts_with_invalid_product_url": buy_with_invalid_product_url,
         "buy_parts_with_invalid_purchase_url": buy_with_invalid_purchase_url,
         "bought_without_purchase_link": buy_with_invalid_purchase_url,
         "incomplete_or_held_buy_identity": incomplete_buy_identity,
         "make_parts_without_title_material_or_process": make_without_title_material_or_process,
         "make_parts_without_material_or_process": make_without_title_material_or_process},
        "authoring_inventory_stowed.json",
    ))

    motion_scope_blocked = bool(
        motion.get("scope_missing") or motion.get("track_validation_error_count")
        or motion.get("boolean_blocked_pair_count") or motion.get("distance_blocked_pair_count")
        or motion.get("sample_count") != 81 or motion.get("angle_increment_deg", math.inf) > 1.0
    )
    motion_status = "BLOCKED" if motion_scope_blocked else (
        "PASS" if motion.get("unauthorized_positive_volume_pair_count", motion.get("positive_volume_pair_count", 0)) == 0
        else "FAIL"
    )
    gates.append(gate(
        "MOTION-FULL-MECHANISM",
        "Every moving/flexible/softgood occurrence is explicitly parameterized and exact-BREP collision/clearance checked through 0..80 degrees at <=1 degree",
        motion_status,
        {
            "samples": motion.get("sample_count"), "angle_increment_deg": motion.get("angle_increment_deg"),
            "scope_missing": motion.get("scope_missing", []),
            "track_validation_errors": motion.get("track_validation_errors", []),
            "unauthorized_positive_volume_pairs": motion.get("unauthorized_positive_volume_pair_count", motion.get("positive_volume_pair_count", 0)),
            "documented_positive_volume_pairs": motion.get("documented_positive_volume_pair_count", 0),
            "boolean_blocked_pairs": motion.get("boolean_blocked_pair_count", 0),
            "distance_blocked_pairs": motion.get("distance_blocked_pair_count", 0),
            "minimum_exact_noninterfering_clearance_mm": motion.get("minimum_exact_noninterfering_clearance_mm"),
        }, "motion_full_mechanism_audit.csv.gz; motion_kinematics_1deg.csv; motion_audit_summary.json",
    ))
    motion_fit_failed = bool(
        motion.get("intentional_fit_register_error_count", 0)
        or motion.get("unused_intentional_fit_exception_ids", [])
    )
    gates.append(gate(
        "INTENTIONAL-FIT-REGISTER-MOTION",
        "Every motion-sweep positive-volume exception is unique, bounded, process-based, and exercised",
        "FAIL" if motion_fit_failed else "PASS",
        {
            "definition_errors": motion.get("intentional_fit_register_errors", []),
            "unused_exception_ids": motion.get("unused_intentional_fit_exception_ids", []),
            "used_exception_ids": motion.get("used_intentional_fit_exception_ids", []),
        }, "authoring_inventory_stowed.json; motion_full_mechanism_audit.csv.gz",
    ))

    gate_ids = [row["gate_id"] for row in gates]
    duplicate_gate_ids = sorted(
        value for value, count in Counter(gate_ids).items() if count > 1
    )
    missing_gate_ids = sorted(set(EXPECTED_GATE_IDS) - set(gate_ids))
    unexpected_gate_ids = sorted(set(gate_ids) - set(EXPECTED_GATE_IDS))
    if (
        len(gate_ids) != 31
        or len(EXPECTED_GATE_IDS) != 31
        or duplicate_gate_ids
        or missing_gate_ids
        or unexpected_gate_ids
    ):
        raise RuntimeError(
            "Definition-of-Done gate set is not the frozen exact 31-gate set: "
            f"count={len(gate_ids)}, duplicates={duplicate_gate_ids}, "
            f"missing={missing_gate_ids}, unexpected={unexpected_gate_ids}"
        )
    counts = Counter(g["status"] for g in gates)
    release_status = "PASS" if counts["FAIL"] == 0 and counts["BLOCKED"] == 0 else "NOT_RELEASED"
    result = {
        "computed_release_status": release_status,
        "package_required_label": "FINAL — RELEASED" if release_status == "PASS" else "CORRECTIVE VALIDATION FAILED — NOT RELEASED",
        "informational_environment_items": [{
            "item_id": "CREO-ENVIRONMENT", "status": "N/A",
            "disposition": CREO_ENVIRONMENT_DISPOSITION,
            "included_in_acceptance_logic": False,
        }],
        "gate_counts": {status: counts[status] for status in ("PASS", "FAIL", "BLOCKED")},
        "gates": gates,
    }
    dump_json(out_dir / "gate_results.json", result)
    return result


def write_positive_register(path: Path, pair_results: dict[str, dict[str, Any]]) -> None:
    rows = [row for state in ("STOWED", "DEPLOYED") for row in pair_results[state]["positive_rows"]]
    fields = [
        "state", "pair_index", "occurrence_a", "solid_index_a", "part_number_a", "classification_a",
        "occurrence_b", "solid_index_b", "part_number_b", "classification_b", "same_occurrence",
        "direct_attachment_connection", "documented_positive_volume_exception",
        "intentional_fit_exception_id", "intentional_fit_match_status", "common_volume_mm3",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_minimum_clearance_register(path: Path, pair_results: dict[str, dict[str, Any]]) -> None:
    """Write critical/measured rows, not a duplicate of the exhaustive pair files."""
    rows = [row for state in ("STOWED", "DEPLOYED") for row in pair_results[state]["critical_clearance_rows"]]
    rows.sort(key=lambda row: (
        row["state"],
        float("inf") if row["exact_clearance_mm"] is None else row["exact_clearance_mm"],
        row["pair_index"],
    ))
    fields = [
        "state", "pair_index", "occurrence_a", "solid_index_a", "part_number_a",
        "occurrence_b", "solid_index_b", "part_number_b", "direct_attachment_connection",
        "intentional_fit_exception_id", "intentional_fit_match_status",
        "aabb_gap_mm", "exact_clearance_status", "exact_clearance_mm", "common_volume_mm3",
        "disposition", "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def validation_manifest(
    out_dir: Path, inputs: list[Path], execution_topology: dict[str, Any],
) -> dict[str, Any]:
    files = {}
    evidence_files = {p for p in out_dir.iterdir() if p.is_file() and p.name != "validation_manifest.json"}
    for path in sorted(set(inputs) | evidence_files):
        files[path.name] = {"sha256": sha256(path), "size_bytes": path.stat().st_size}
    return {
        "validator": str(Path(__file__).resolve()),
        "validation_engine": f"CadQuery {getattr(cq, '__version__', 'unknown')} / OCCT XCAF and exact BRepAlgoAPI",
        "determinism": {
            "solid_order": "occurrence_id, solid_index, part_number",
            "pair_order": "itertools.combinations of sorted solids",
            "aabb_tolerance_mm": AABB_TOL_MM, "common_volume_epsilon_mm3": COMMON_VOLUME_EPS_MM3,
            "near_distance_limit_mm": NEAR_DISTANCE_LIMIT_MM,
            "zero_common_aabb_overlap_distance_policy": "EXACT_BREPEXTREMA_REQUIRED",
            "positive_volume_exception_policy": "UNIQUE_STATE_SPECIFIC_OCCURRENCE_OR_SOLID_PAIR_WITH_FINITE_PROCESS_BOUNDS",
        },
        "execution_topology": execution_topology,
        "files": files,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skip-motion", action="store_true", help="Diagnostic only; leaves the full-mechanism motion gate BLOCKED")
    parser.add_argument(
        "--motion-workers", type=int, default=8, metavar="1..8",
        help="Spawn-process workers for exact per-angle motion shards (default: 8)",
    )
    args = parser.parse_args(argv)
    if not 1 <= args.motion_workers <= 8:
        parser.error("--motion-workers must be an integer inside 1..8")
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    required_inputs = [*FILES.values(), *INVENTORIES.values(), AUTHORING_MANIFEST]
    missing_inputs = [str(path) for path in required_inputs if not path.is_file()]
    if missing_inputs:
        parser.error(
            "final-only validation requires the complete final authoring set; "
            f"missing: {missing_inputs}"
        )

    try:
        inventories = {
            state: json.loads(path.read_text(encoding="utf-8"))
            for state, path in INVENTORIES.items()
        }
        authoring_manifest = json.loads(AUTHORING_MANIFEST.read_text(encoding="utf-8"))
        if not isinstance(authoring_manifest, dict):
            raise ValueError("authoring manifest root must be an object")
        validate_authoring_manifest(authoring_manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(f"final authoring input integrity check failed: {exc}")
    endpoints: dict[str, EndpointData] = {}
    for state in ("STOWED", "DEPLOYED"):
        print(f"[{state}] clean XCAF reimport", flush=True)
        endpoints[state] = load_endpoint(state, FILES[state], inventories[state])
        write_occurrence_csv(out_dir / f"xcaf_occurrences_{state.lower()}.csv", endpoints[state].occurrence_rows)
        write_solid_csv(out_dir / f"leaf_solids_{state.lower()}.csv", endpoints[state].solid_records)
    dump_json(out_dir / "step_text_inspection.json", {state: endpoint.step_text for state, endpoint in endpoints.items()})

    pair_results: dict[str, dict[str, Any]] = {}
    for state in ("STOWED", "DEPLOYED"):
        print(f"[{state}] exhaustive unordered leaf-solid pair audit", flush=True)
        pair_results[state] = audit_endpoint_pairs(endpoints[state], inventories[state], out_dir)
        print(
            f"[{state}] pairs={pair_results[state]['unordered_pair_count']} "
            f"positive={pair_results[state]['unauthorized_positive_volume_pair_count']} "
            f"blocked={pair_results[state]['boolean_blocked_pair_count']}", flush=True,
        )
    dump_json(out_dir / "endpoint_pair_summary.json", pair_results)
    write_positive_register(out_dir / "endpoint_interference_register.csv", pair_results)
    write_minimum_clearance_register(out_dir / "minimum_clearance_register.csv", pair_results)

    parity = state_parity(endpoints["STOWED"], endpoints["DEPLOYED"], inventories, out_dir)
    connectivity = {
        state: authoring_connectivity(inventories[state], state, out_dir, endpoints[state])
        for state in ("STOWED", "DEPLOYED")
    }
    dump_json(out_dir / "connectivity_summary.json", connectivity)
    definition_of_done = definition_of_done_audit(endpoints, inventories, connectivity, out_dir)
    reconciliation = occurrence_bom_reconciliation(endpoints, inventories, out_dir)
    dump_json(out_dir / "occurrence_bom_reconciliation.json", reconciliation)
    dimensions = key_dimensions(endpoints, inventories)
    dump_json(out_dir / "key_dimensions.json", dimensions)

    if args.skip_motion:
        motion = {
            "scope": "Skipped by diagnostic command-line option", "scope_missing": ["ALL_MOTION_SCOPE"],
            "sample_count": 0, "angle_increment_deg": None,
            "positive_volume_pair_count": 0, "unauthorized_positive_volume_pair_count": 0,
            "documented_positive_volume_pair_count": 0,
            "boolean_blocked_pair_count": 1, "distance_blocked_pair_count": 1,
            "track_validation_errors": ["Motion audit skipped"], "track_validation_error_count": 1,
            "intentional_fit_register_errors": [], "intentional_fit_register_error_count": 0,
            "unused_intentional_fit_exception_ids": [], "used_intentional_fit_exception_ids": [],
            "execution_topology": {
                "mode": "SKIPPED_BY_DIAGNOSTIC_OPTION", "worker_count": 0,
                "requested_worker_count": args.motion_workers,
            },
        }
    else:
        print("[MOTION] full-mechanism 0..80 degree / 1 degree exact sweep", flush=True)
        motion = motion_audit(endpoints, inventories, out_dir, worker_count=args.motion_workers)
        dump_json(out_dir / "motion_audit_summary.json", motion)

    gates = compute_gates(
        endpoints, inventories, pair_results, parity, connectivity, dimensions,
        reconciliation, motion, definition_of_done, out_dir,
    )
    summary = {
        "validation_status": gates["computed_release_status"],
        "required_package_label": gates["package_required_label"],
        "validator_scope": "Clean-process OCCT/XCAF AP242 endpoint reimport, exhaustive endpoint pair audit, and inventory-parameterized full-mechanism exact-BREP motion audit",
        "validator_limit": None if not motion.get("scope_missing") and not motion.get("track_validation_errors") else {
            "scope_missing": motion.get("scope_missing", []),
            "track_validation_errors": motion.get("track_validation_errors", []),
        },
        "informational_environment_items": gates["informational_environment_items"],
        "endpoint_pair_counts": {
            state: {
                "solid_count": pair_results[state]["solid_count"],
                "unordered_pairs": pair_results[state]["unordered_pair_count"],
                "positive_volume_pairs": pair_results[state]["unauthorized_positive_volume_pair_count"],
                "boolean_blocked_pairs": pair_results[state]["boolean_blocked_pair_count"],
            } for state in ("STOWED", "DEPLOYED")
        },
        "motion": {
            "sample_count": motion["sample_count"],
            "positive_volume_pairs": motion.get("unauthorized_positive_volume_pair_count", motion["positive_volume_pair_count"]),
            "boolean_blocked_pairs": motion["boolean_blocked_pair_count"],
            "distance_blocked_pairs": motion.get("distance_blocked_pair_count", 0),
            "scope_missing": motion.get("scope_missing", []),
        },
        "gate_counts": gates["gate_counts"], "elapsed_seconds": time.time() - started,
        "evidence_directory": str(out_dir),
    }
    dump_json(out_dir / "validation_summary.json", summary)
    manifest = validation_manifest(
        out_dir,
        [
            FILES["STOWED"], FILES["DEPLOYED"], INVENTORIES["STOWED"], INVENTORIES["DEPLOYED"],
            AUTHORING_MANIFEST, Path(__file__).resolve(),
        ],
        execution_topology={
            "endpoint_pair_audits": {
                "mode": "SERIAL_UNCHANGED",
                "pair_order": "itertools.combinations of sorted solids",
            },
            "motion_audit": motion["execution_topology"],
        },
    )
    dump_json(out_dir / "validation_manifest.json", manifest)
    # Rewrite once so the manifest self-hash is intentionally excluded instead
    # of creating a non-convergent self-referential digest.
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
