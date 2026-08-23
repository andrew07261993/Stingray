#!/usr/bin/env python3
"""Independent, evidence-producing validation of the DF8 R2 AP242 endpoints.

This program is deliberately separate from the authoring program.  It starts
from the AP242 files on disk, imports each into a fresh XCAF document through
CadQuery/OCCT, walks the occurrence hierarchy, expands every leaf occurrence
into individual solids, and writes a deterministic row for every unordered
solid pair.  AABB-separated pairs are not silently discarded: they remain in
the compressed pair register with an explicit broad-phase disposition.

OCCT validation is an intermediate digital check.  It is not, and is never
reported as, Creo reimport/regeneration evidence.  The Creo gate is therefore
always BLOCKED until evidence from a real clean Creo session is supplied.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


ROOT = Path(__file__).resolve().parents[2]
RELEASE_DIR = ROOT / "work" / "r2_release"
ANALYSIS_DIR = ROOT / "work" / "r2_analysis"
DEFAULT_OUT = ANALYSIS_DIR / "validation"

FILES = {
    "STOWED": RELEASE_DIR / "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_STOWED_AP242.step",
    "DEPLOYED": RELEASE_DIR / "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_DEPLOYED_AP242.step",
}
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

PAIR_FIELDS = [
    "state", "pair_index", "occurrence_a", "solid_index_a", "part_number_a",
    "classification_a", "occurrence_b", "solid_index_b", "part_number_b",
    "classification_b", "same_occurrence", "direct_attachment_connection",
    "documented_positive_volume_exception", "aabb_overlap", "aabb_gap_mm",
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
    return {
        frozenset((c["occurrence_id"], c["mate_occurrence_id"]))
        for c in inventory["connections"]
        if c["occurrence_id"] in occurrence_ids and c["mate_occurrence_id"] in occurrence_ids
        and c["occurrence_id"] != c["mate_occurrence_id"]
    }


def audit_endpoint_pairs(endpoint: EndpointData, inventory: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    start = time.time()
    path = out_dir / f"endpoint_pair_audit_{endpoint.state.lower()}.csv.gz"
    positives: list[dict[str, Any]] = []
    clearance_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    min_clearance: float | None = None
    conn_pairs = connection_pairs(inventory)
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
            # No positive-volume exception register is present in the authoring
            # evidence.  A connection row alone is not a geometric exception.
            documented_exception = False
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
                    "common_volume_mm3": common_volume,
                }
                positives.append(positive)
                counts[result] += 1
            else:
                result = "CLEAR_OR_CONTACT"
                counts["clear_pairs"] += 1
                # Exact distance is deterministic and well behaved for pairs
                # separated in at least one Cartesian broad-phase axis.  OCCT's
                # distance extrema can become pathologically slow for complex,
                # mutually overlapping AABBs even when their common volume is
                # zero.  Those rows are explicitly BLOCKED instead of hanging
                # or pretending that an AABB overlap is a measured clearance.
                if AABB_TOL_MM < gap <= NEAR_DISTANCE_LIMIT_MM:
                    distance_status, clearance, dist_error = exact_distance(a.shape, b.shape)
                    if dist_error:
                        error = f"{error}; {dist_error}".strip("; ")
                    if distance_status != "DONE":
                        counts["distance_blocked_pairs"] += 1
                    elif clearance is not None:
                        min_clearance = clearance if min_clearance is None else min(min_clearance, clearance)
                elif overlaps:
                    distance_status = "BLOCKED_AABB_OVERLAP_ZERO_COMMON"
                    counts["distance_blocked_pairs"] += 1

            row = {
                "state": endpoint.state, "pair_index": pair_index,
                "occurrence_a": a.occurrence_id, "solid_index_a": a.solid_index,
                "part_number_a": a.part_number, "classification_a": a.classification,
                "occurrence_b": b.occurrence_id, "solid_index_b": b.solid_index,
                "part_number_b": b.part_number, "classification_b": b.classification,
                "same_occurrence": a.occurrence_id == b.occurrence_id,
                "direct_attachment_connection": direct_connection,
                "documented_positive_volume_exception": documented_exception,
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
        "minimum_exact_noninterfering_clearance_mm": min_clearance,
        "positive_rows": positives, "boolean_or_distance_errors": errors,
        "critical_clearance_rows": clearance_rows,
        "elapsed_seconds": time.time() - start,
    }


def authoring_connectivity(inventory: dict[str, Any], state: str, out_dir: Path) -> dict[str, Any]:
    occurrences = {o["occurrence_id"]: o for o in inventory["occurrences"]}
    valid_neighbors: dict[str, set[str]] = defaultdict(set)
    connection_ids: dict[str, list[str]] = defaultdict(list)
    dangling: list[dict[str, Any]] = []
    self_connections: list[str] = []
    generic_evidence: list[str] = []
    graph: dict[str, set[str]] = defaultdict(set)
    structural_graph: dict[str, set[str]] = defaultdict(set)
    generic_patterns = ("AUTO-SPEC", "Occurrence-specific hardware named in BOM/joint record")

    for connection in inventory["connections"]:
        a, b = connection["occurrence_id"], connection["mate_occurrence_id"]
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
        valid_neighbors[a].add(b)
        valid_neighbors[b].add(a)
        graph[a].add(b)
        graph[b].add(a)
        connection_type = connection.get("connection_type", "").upper()
        if any(token in connection_type for token in ("STRUCTURAL", "CLOSED_SPLICE", "STITCHED", "RF_WELD", "PINNED")):
            structural_graph[a].add(b)
            structural_graph[b].add(a)

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
        "state": state, "occurrence_count": len(occurrences), "connection_count": len(inventory["connections"]),
        "floating_rigid_occurrences": floating, "floating_rigid_count": len(floating),
        "dangling_connections": dangling, "dangling_connection_count": len(dangling),
        "self_connections": self_connections, "self_connection_count": len(self_connections),
        "generic_or_blanket_evidence_connection_ids": sorted(set(generic_evidence)),
        "generic_or_blanket_evidence_count": len(set(generic_evidence)),
        "graph_component_count_including_flexible_and_consumed": components,
        "body_hardpoint_to_harness_terminal_path": recovery_path,
        "continuous_recovery_load_path_found": recovery_path is not None,
    }


def state_parity(stowed: EndpointData, deployed: EndpointData, inventories: dict[str, dict[str, Any]], out_dir: Path) -> dict[str, Any]:
    auth = {
        state: {o["occurrence_id"]: o for o in inv["occurrences"]}
        for state, inv in inventories.items()
    }
    leaf = {
        state: {r["occurrence_id"]: r for r in endpoint.occurrence_rows if r["has_shape"]}
        for state, endpoint in (("STOWED", stowed), ("DEPLOYED", deployed))
    }
    ids = sorted(set(leaf["STOWED"]) | set(leaf["DEPLOYED"]))
    rows = []
    mismatches = []
    for occurrence_id in ids:
        s = leaf["STOWED"].get(occurrence_id)
        d = leaf["DEPLOYED"].get(occurrence_id)
        so = auth["STOWED"].get(occurrence_id, {})
        do = auth["DEPLOYED"].get(occurrence_id, {})
        flexible = so.get("classification") in {"FLEXIBLE", "SOFTGOOD"}
        same_part = bool(s and d and s.get("part_number") == d.get("part_number") == so.get("part_number") == do.get("part_number"))
        topology_match = bool(s and d and s.get("solid_count") == d.get("solid_count") and s.get("face_count") == d.get("face_count"))
        volume_delta = None if not s or not d else float(d["volume_mm3"] - s["volume_mm3"])
        rigid_geometry_match = flexible or bool(topology_match and volume_delta is not None and abs(volume_delta) <= 1.0e-5)
        status = "PASS" if s and d and same_part and rigid_geometry_match else "FAIL"
        row = {
            "occurrence_id": occurrence_id, "classification": so.get("classification", ""),
            "present_stowed": bool(s), "present_deployed": bool(d), "same_part_number": same_part,
            "stowed_solid_count": "" if not s else s.get("solid_count"),
            "deployed_solid_count": "" if not d else d.get("solid_count"),
            "stowed_face_count": "" if not s else s.get("face_count"),
            "deployed_face_count": "" if not d else d.get("face_count"),
            "volume_delta_mm3": "" if volume_delta is None else repr(volume_delta),
            "flexible_state_geometry_exception": flexible, "status": status,
        }
        rows.append(row)
        if status == "FAIL":
            mismatches.append(occurrence_id)
    with (out_dir / "state_parity.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["occurrence_id"])
        writer.writeheader()
        writer.writerows(rows)
    return {
        "union_occurrence_count": len(ids), "mismatch_count": len(mismatches),
        "mismatch_occurrence_ids": mismatches,
        "stowed_only": sorted(set(leaf["STOWED"]) - set(leaf["DEPLOYED"])),
        "deployed_only": sorted(set(leaf["DEPLOYED"]) - set(leaf["STOWED"])),
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
    normal_oml_ids = ["FWD-SHELL-001", "AFT-SHELL-001", "FIXED-SECTOR-1", "FIXED-SECTOR-2", "FIXED-SECTOR-3"]
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
            })
    result["arms"] = arm_rows
    crosshead_z = {
        state: transform_translation(leaves[state]["CROSSHEAD-001"])[2]
        for state in ("STOWED", "DEPLOYED")
    }
    result["crosshead_z_mm"] = crosshead_z
    result["crosshead_travel_from_reimported_transforms_mm"] = crosshead_z["STOWED"] - crosshead_z["DEPLOYED"]
    result["crosshead_travel_from_independent_closure_equation_mm"] = kinematic(80.0)["crosshead_travel_mm"]

    parts = {p["part_number"]: p for p in inventories["STOWED"]["parts"]}
    mass_missing = []
    total_mass = 0.0
    for occurrence in inventories["STOWED"]["occurrences"]:
        mass = parts[occurrence["part_number"]].get("mass_kg")
        if mass is None:
            mass_missing.append(occurrence["occurrence_id"])
        else:
            total_mass += float(mass)
    result["mass_rollup_from_authoring_inventory_kg"] = total_mass
    result["mass_unresolved_occurrence_ids"] = mass_missing
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


def motion_audit(stowed: EndpointData, inventory: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    """One-degree exact sweep of the three principal arm bodies vs fixed solids.

    This is intentionally labeled partial: links, crosshead, rods, spring and
    state-changing softgoods are not reconstructed by this independent tool.
    Consequently the complete mechanism-motion gate remains BLOCKED even when
    this principal-arm sweep is clear.
    """
    start = time.time()
    motion_path = out_dir / "motion_arm_clearance_audit.csv.gz"
    fields = [
        "sample_index", "angle_deg", "arm_occurrence", "arm_solid_index",
        "fixed_occurrence", "fixed_solid_index", "fixed_part_number", "aabb_overlap",
        "aabb_gap_mm", "exact_common_status", "common_volume_mm3", "result", "error",
    ]
    fixed = [s for s in stowed.solid_records if s.classification == "FIXED"]
    local_arm_solids: dict[int, list[Any]] = {}
    for arm_index in (1, 2, 3):
        local_shape = stowed.local_shapes[f"ARM-{arm_index}"]
        explorer = TopExp_Explorer(local_shape.wrapped, TopAbs_SOLID)
        local_arm_solids[arm_index] = []
        while explorer.More():
            local_arm_solids[arm_index].append(TopoDS.Solid_s(explorer.Current()))
            explorer.Next()

    sample_rows = []
    positives = []
    blocked = []
    total_rows = 0
    broadphase = 0
    with gzip.open(motion_path, "wt", newline="", encoding="utf-8", compresslevel=6) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for sample_index, angle in enumerate(range(0, 81), start=1):
            kin = kinematic(float(angle))
            sample_positive = 0
            sample_blocked = 0
            sample_broadphase = 0
            for arm_index, clock in enumerate((0.0, 120.0, 240.0), start=1):
                loc = arm_occurrence_loc(float(angle), clock)
                for arm_solid_index, local_solid in enumerate(local_arm_solids[arm_index], start=1):
                    arm_shape = cq.Shape.cast(local_solid).moved(loc).wrapped
                    arm_bbox = bbox_raw(arm_shape)
                    arm_id = f"ARM-{arm_index}"
                    for fixed_solid in fixed:
                        total_rows += 1
                        gap = aabb_gap(arm_bbox, fixed_solid.bbox)
                        overlaps = gap <= AABB_TOL_MM
                        status = "NOT_RUN_AABB_SEPARATED"
                        common: float | None = 0.0
                        error = ""
                        if overlaps:
                            broadphase += 1
                            sample_broadphase += 1
                            status, common, error = exact_common(arm_shape, fixed_solid.shape)
                        if status in {"ERROR", "NOT_DONE"}:
                            result = "BLOCKED_BOOLEAN"
                            sample_blocked += 1
                            blocked.append({
                                "angle_deg": angle, "arm_occurrence": arm_id,
                                "fixed_occurrence": fixed_solid.occurrence_id,
                                "fixed_solid_index": fixed_solid.solid_index,
                                "status": status, "error": error,
                            })
                        elif common is not None and common > COMMON_VOLUME_EPS_MM3:
                            result = "POSITIVE_VOLUME"
                            sample_positive += 1
                            positives.append({
                                "angle_deg": angle, "arm_occurrence": arm_id,
                                "arm_solid_index": arm_solid_index,
                                "fixed_occurrence": fixed_solid.occurrence_id,
                                "fixed_solid_index": fixed_solid.solid_index,
                                "common_volume_mm3": common,
                            })
                        else:
                            result = "CLEAR_OR_CONTACT"
                        writer.writerow({
                            "sample_index": sample_index, "angle_deg": angle,
                            "arm_occurrence": arm_id, "arm_solid_index": arm_solid_index,
                            "fixed_occurrence": fixed_solid.occurrence_id,
                            "fixed_solid_index": fixed_solid.solid_index,
                            "fixed_part_number": fixed_solid.part_number,
                            "aabb_overlap": overlaps, "aabb_gap_mm": repr(gap),
                            "exact_common_status": status,
                            "common_volume_mm3": "" if common is None else repr(common),
                            "result": result, "error": error,
                        })
            sample_rows.append({
                **kin, "sample_index": sample_index, "arm_fixed_pair_rows": 3 * sum(len(v) for v in local_arm_solids.values()) // 3 * len(fixed),
                "broadphase_candidates": sample_broadphase,
                "positive_volume_pairs": sample_positive, "boolean_blocked_pairs": sample_blocked,
            })
    with (out_dir / "motion_kinematics_1deg.csv").open("w", newline="", encoding="utf-8") as stream:
        fields_kin = list(sample_rows[0])
        writer = csv.DictWriter(stream, fieldnames=fields_kin)
        writer.writeheader()
        writer.writerows(sample_rows)
    return {
        "scope": "Three principal arm bodies versus all endpoint FIXED rigid solids at 0..80 degrees in 1-degree increments",
        "scope_limit": "Links, crosshead, rods, springs, locks, and state-changing flexible/softgood geometry are not swept; full mechanism sweep remains BLOCKED",
        "sample_count": len(sample_rows), "angle_increment_deg": 1,
        "pair_register": str(motion_path), "kinematics_register": str(out_dir / "motion_kinematics_1deg.csv"),
        "pair_row_count": total_rows, "broadphase_candidate_count": broadphase,
        "positive_volume_pair_count": len(positives), "boolean_blocked_pair_count": len(blocked),
        "positive_rows": positives, "blocked_rows": blocked,
        "maximum_closure_residual_abs_mm": max(abs(row["closure_residual_mm"]) for row in sample_rows),
        "crosshead_travel_0_to_80_mm": sample_rows[-1]["crosshead_travel_mm"] - sample_rows[0]["crosshead_travel_mm"],
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
    motion: dict[str, Any], out_dir: Path,
) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    for state in ("STOWED", "DEPLOYED"):
        step = endpoints[state].step_text
        gates.append(gate(
            f"AP242-{state}", f"{state} master is AP242 exact B-rep with named products/occurrences",
            "PASS" if step["ap242_schema_detected"] and step["faceted_or_tessellated_total"] == 0
            and step["unnamed_product_count"] == 0 and step["unnamed_nauo_name_count"] == 0 else "FAIL",
            {
                "schema": step["schema_record"], "faceted_or_tessellated_total": step["faceted_or_tessellated_total"],
                "unnamed_products": step["unnamed_product_count"], "unnamed_nauos": step["unnamed_nauo_name_count"],
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
            "No occurrence-pair positive-volume exception register was supplied; attachment rows alone are not exceptions.",
        ))
        distance_status = "BLOCKED" if pairs["distance_blocked_pair_count"] else "PASS"
        gates.append(gate(
            f"CLEARANCE-EVIDENCE-{state}", f"Near-pair exact clearance evidence completes for {state}",
            distance_status,
            {
                "near_limit_mm": NEAR_DISTANCE_LIMIT_MM,
                "minimum_exact_noninterfering_clearance_mm": pairs["minimum_exact_noninterfering_clearance_mm"],
                "distance_blocked_pairs": pairs["distance_blocked_pair_count"],
            }, f"minimum_clearance_register.csv; endpoint_pair_audit_{state.lower()}.csv.gz",
            "Pairs outside the near limit retain a conservative positive AABB lower bound in the exhaustive register.",
        ))

    gates.append(gate(
        "STATE-PARITY", "The two masters contain the same occurrence identities and rigid part definitions",
        "PASS" if parity["mismatch_count"] == 0 else "FAIL", parity, "state_parity.csv",
    ))
    unmapped = sum(
        1 for endpoint in endpoints.values() for row in endpoint.occurrence_rows
        if row["has_shape"] and not row["mapped_to_authoring_inventory"]
    )
    identity_without_note = sum(
        1 for inv in inventories.values() for occurrence in inv["occurrences"]
        if occurrence["identity_transform"] and not occurrence.get("notes", "").strip()
    )
    gates.append(gate(
        "OCCURRENCE-TRANSFORMS", "Every XCAF leaf maps to an occurrence and identity placements are justified",
        "PASS" if unmapped == 0 and identity_without_note == 0 else "FAIL",
        {"unmapped_leaf_occurrences": unmapped, "identity_occurrences_without_justification": identity_without_note},
        "xcaf_occurrences_stowed.csv; xcaf_occurrences_deployed.csv",
    ))

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
    gates.append(gate(
        "NORMAL-BODY-OML", "Normal shell/fixed-sector OML does not exceed the 53.0 mm target",
        "PASS" if normal_spans and max(normal_spans.values()) <= NORMAL_OD_MM + 1e-6 else "FAIL",
        {"measured_xy_spans_mm": normal_spans, "target_max_mm": NORMAL_OD_MM},
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
    resolved_mass = dimensions["mass_rollup_from_authoring_inventory_kg"]
    mass_status = "BLOCKED" if mass_missing else (
        "PASS" if resolved_mass <= MAX_SYSTEM_MASS_KG and MAX_SYSTEM_MASS_KG - resolved_mass >= MIN_MASS_RESERVE_KG else "FAIL"
    )
    gates.append(gate(
        "SYSTEM-MASS", "System mass is <=18.14 kg with >=1.0 kg reserve and no unresolved occurrence masses",
        mass_status,
        {"resolved_mass_kg": resolved_mass, "unresolved_occurrence_ids": mass_missing,
         "resolved-only-reserve_kg": MAX_SYSTEM_MASS_KG - resolved_mass}, "key_dimensions.json",
    ))

    floating = sum(v["floating_rigid_count"] for v in connectivity.values())
    dangling = sum(v["dangling_connection_count"] for v in connectivity.values())
    self_count = sum(v["self_connection_count"] for v in connectivity.values())
    generic = sum(v["generic_or_blanket_evidence_count"] for v in connectivity.values())
    gates.append(gate(
        "ATTACHMENT-COHESION", "Every rigid occurrence has occurrence-specific, non-self attachment evidence",
        "PASS" if floating == 0 and dangling == 0 and self_count == 0 and generic == 0 else "FAIL",
        {"floating_rigid_rows_across_states": floating, "dangling_connections_across_states": dangling,
         "self_connections_across_states": self_count, "generic_evidence_rows_across_states": generic},
        "connectivity_summary.json; attachment_connectivity_stowed.csv; attachment_connectivity_deployed.csv",
    ))
    load_path_ok = all(v["continuous_recovery_load_path_found"] for v in connectivity.values())
    gates.append(gate(
        "RECOVERY-LOAD-PATH", "A continuous structural graph connects body hardpoint to harness terminal in both states",
        "PASS" if load_path_ok else "FAIL",
        {state: v["body_hardpoint_to_harness_terminal_path"] for state, v in connectivity.items()},
        "connectivity_summary.json",
        "Flexible/control/inflation routes are not accepted as implicit structural substitutes.",
    ))

    parts = inventories["STOWED"]["parts"]
    provisional = [p["part_number"] for p in parts if "PROVISIONAL" in p.get("cad_classification", "").upper()]
    bought_without_purchase_link = [p["part_number"] for p in parts if p.get("make_buy") == "BUY" and not p.get("purchase_url")]
    gates.append(gate(
        "PROCUREMENT-DEFINITION", "Purchased identities and sourcing records are complete and non-provisional",
        "PASS" if not provisional and not bought_without_purchase_link else "FAIL",
        {"provisional_part_numbers": provisional, "bought_without_purchase_link": bought_without_purchase_link},
        "authoring_inventory_stowed.json",
    ))

    arm_motion_status = "BLOCKED" if motion["boolean_blocked_pair_count"] else (
        "PASS" if motion["positive_volume_pair_count"] == 0 else "FAIL"
    )
    gates.append(gate(
        "MOTION-ARM-BODIES-1DEG", "Principal arm bodies have zero positive-volume intersections versus fixed geometry at 0..80 degrees / 1 degree",
        arm_motion_status,
        {"samples": motion["sample_count"], "positive_volume_pairs": motion["positive_volume_pair_count"],
         "boolean_blocked_pairs": motion["boolean_blocked_pair_count"]},
        "motion_arm_clearance_audit.csv.gz; motion_kinematics_1deg.csv",
    ))
    gates.append(gate(
        "MOTION-FULL-MECHANISM", "All moving rigid and flexible geometry is collision/clearance checked through 0..80 degrees at <=1 degree",
        "BLOCKED", {"completed_scope": motion["scope"], "missing_scope": motion["scope_limit"]},
        "motion_audit_summary.json",
    ))
    gates.append(gate(
        "CREO-CLEAN-SESSION", "Masters reimport, regenerate, and save successfully in a clean Creo session",
        "BLOCKED", {"creo_session_available": False, "report": None},
        "No Creo report supplied",
        "OCCT/XCAF reimport is not target-CAD verification.",
    ))

    counts = Counter(g["status"] for g in gates)
    release_status = "PASS" if counts["FAIL"] == 0 and counts["BLOCKED"] == 0 else "NOT_RELEASED"
    result = {
        "computed_release_status": release_status,
        "package_required_label": "CREO_VALIDATION_PENDING — WIP — NOT RELEASED",
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
        "direct_attachment_connection", "documented_positive_volume_exception", "common_volume_mm3",
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
        "aabb_gap_mm", "exact_clearance_status", "exact_clearance_mm", "common_volume_mm3",
        "disposition", "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def validation_manifest(out_dir: Path, inputs: list[Path]) -> dict[str, Any]:
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
        },
        "files": files,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skip-motion", action="store_true", help="Diagnostic only; leaves full and partial motion gates BLOCKED")
    args = parser.parse_args(argv)
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    inventories = {state: json.loads(path.read_text(encoding="utf-8")) for state, path in INVENTORIES.items()}
    author_manifest = json.loads(AUTHORING_MANIFEST.read_text(encoding="utf-8"))
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
        state: authoring_connectivity(inventories[state], state, out_dir)
        for state in ("STOWED", "DEPLOYED")
    }
    dump_json(out_dir / "connectivity_summary.json", connectivity)
    dimensions = key_dimensions(endpoints, inventories)
    dump_json(out_dir / "key_dimensions.json", dimensions)

    if args.skip_motion:
        motion = {
            "scope": "Skipped by diagnostic command-line option", "scope_limit": "No sweep evidence produced",
            "sample_count": 0, "positive_volume_pair_count": 0, "boolean_blocked_pair_count": 1,
        }
    else:
        print("[MOTION] principal-arm 0..80 degree / 1 degree exact sweep", flush=True)
        motion = motion_audit(endpoints["STOWED"], inventories["STOWED"], out_dir)
        dump_json(out_dir / "motion_audit_summary.json", motion)

    gates = compute_gates(endpoints, inventories, pair_results, parity, connectivity, dimensions, motion, out_dir)
    summary = {
        "validation_status": gates["computed_release_status"],
        "required_package_label": gates["package_required_label"],
        "validator_scope": "Clean-process OCCT/XCAF AP242 endpoint reimport plus exhaustive endpoint pair audit; partial principal-arm motion sweep",
        "validator_limit": "No Creo installation/session was available. Full-mechanism motion reconstruction is not completed by this validator.",
        "authoring_manifest_release_status": author_manifest.get("release_status"),
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
            "positive_volume_pairs": motion["positive_volume_pair_count"],
            "boolean_blocked_pairs": motion["boolean_blocked_pair_count"],
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
    )
    dump_json(out_dir / "validation_manifest.json", manifest)
    # Rewrite once so the manifest self-hash is intentionally excluded instead
    # of creating a non-convergent self-referential digest.
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
