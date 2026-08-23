#!/usr/bin/env python3
"""Validate exact-solid STEP/AP242 files by text inspection and XCAF reimport.

The validator deliberately uses two independent views of each file:

* the ISO 10303-21 text is inspected for its header, product/occurrence names,
  exact-BREP entities, and tessellated/faceted entities; and
* CadQuery's ``Assembly.importStep`` (an OCCT STEPCAF/XCAF importer) is used to
  recover the assembly tree and exact topology.  The recovered topology is
  checked with OCCT's BRepCheck_Analyzer.

Exit status is 0 when every input passes the exact AP242 gate, 1 when one or
more files import successfully but fail a gate, and 2 when an input cannot be
read or imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS


STEP_STRING = r"'(?:''|[^'])*'"
ENTITY_TYPE_RE = re.compile(r"#\s*\d+\s*=\s*([A-Z][A-Z0-9_]*)\s*\(", re.I)
PRODUCT_RE = re.compile(
    rf"#\s*(\d+)\s*=\s*PRODUCT\s*\(\s*({STEP_STRING}|\$)\s*,\s*"
    rf"({STEP_STRING}|\$)",
    re.I | re.S,
)
OCCURRENCE_RE = re.compile(
    rf"#\s*(\d+)\s*=\s*NEXT_ASSEMBLY_USAGE_OCCURRENCE\s*\(\s*"
    rf"({STEP_STRING}|\$)\s*,\s*({STEP_STRING}|\$)",
    re.I | re.S,
)
STEP_LITERAL_RE = re.compile(STEP_STRING, re.S)

EXACT_BREP_ENTITY_TYPES = (
    "MANIFOLD_SOLID_BREP",
    "BREP_WITH_VOIDS",
    "ADVANCED_BREP_SHAPE_REPRESENTATION",
)
FACETED_OR_TESSELLATED_TYPES = (
    "FACETED_BREP",
    "FACETED_BREP_SHAPE_REPRESENTATION",
    "TESSELLATED_SHAPE_REPRESENTATION",
    "TESSELLATED_ITEM",
    "TESSELLATED_GEOMETRIC_SET",
    "TRIANGULATED_FACE",
    "TRIANGULATED_FACE_SET",
    "TRIANGULATED_SURFACE_SET",
    "CARTESIAN_TRIANGULATED_SURFACE_SET",
    "COMPLEX_TRIANGULATED_FACE",
    "COMPLEX_TRIANGULATED_SURFACE_SET",
)
GENERIC_NAME_RE = re.compile(
    r"^(?:unnamed|assembly|part|component|occurrence)(?:[-_ ]?\d+)?$", re.I
)


def _step_unquote(token: str | None) -> str | None:
    """Decode the common, ASCII-safe subset of a STEP string token."""

    if token is None or token == "$":
        return None
    if len(token) >= 2 and token[0] == "'" and token[-1] == "'":
        return token[1:-1].replace("''", "'")
    return token


def _step_strings(fragment: str | None) -> list[str]:
    if not fragment:
        return []
    return [_step_unquote(match.group(0)) or "" for match in STEP_LITERAL_RE.finditer(fragment)]


def _header_record(text: str, record_name: str) -> str | None:
    match = re.search(
        rf"\b{re.escape(record_name)}\s*\((.*?)\)\s*;",
        text,
        re.I | re.S,
    )
    return match.group(1).strip() if match else None


def _is_unnamed(value: str | None) -> bool:
    if value is None:
        return True
    clean = value.strip()
    if not clean or clean.upper() in {"$", "*", "NONE", "N/A", "NA", "NULL"}:
        return True
    return bool(GENERIC_NAME_RE.fullmatch(clean))


def _round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _walk_assembly(root: cq.Assembly) -> list[dict[str, Any]]:
    """Return a deterministic root-first view of the XCAF assembly tree."""

    nodes: list[dict[str, Any]] = []

    def visit(node: cq.Assembly, parent_path: str, depth: int, ordinal: int) -> None:
        name = node.name if isinstance(node.name, str) else None
        path_token = name.strip() if name and name.strip() else f"<unnamed:{ordinal}>"
        path = f"{parent_path}/{path_token}" if parent_path else path_token
        nodes.append(
            {
                "path": path,
                "name": name,
                "depth": depth,
                "is_leaf": not bool(node.children),
                "has_shape": node.obj is not None,
                "child_count": len(node.children),
            }
        )
        for child_ordinal, child in enumerate(node.children, start=1):
            visit(child, path, depth + 1, child_ordinal)

    visit(root, "", 0, 1)
    return nodes


def _count_topology(shape: cq.Shape) -> dict[str, Any]:
    wrapped = shape.wrapped

    solid_count = 0
    invalid_solid_indices: list[int] = []
    solid_explorer = TopExp_Explorer(wrapped, TopAbs_SOLID)
    while solid_explorer.More():
        solid_count += 1
        solid = TopoDS.Solid_s(solid_explorer.Current())
        if not BRepCheck_Analyzer(solid).IsValid():
            invalid_solid_indices.append(solid_count)
        solid_explorer.Next()

    face_count = 0
    faces_with_triangulation = 0
    triangulation_node_count = 0
    triangle_count = 0
    face_explorer = TopExp_Explorer(wrapped, TopAbs_FACE)
    while face_explorer.More():
        face_count += 1
        face = TopoDS.Face_s(face_explorer.Current())
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is not None:
            faces_with_triangulation += 1
            triangulation_node_count += int(triangulation.NbNodes())
            triangle_count += int(triangulation.NbTriangles())
        face_explorer.Next()

    return {
        "solid_count": solid_count,
        "face_count": face_count,
        "whole_shape_valid": bool(BRepCheck_Analyzer(wrapped).IsValid()),
        "invalid_solid_count": len(invalid_solid_indices),
        "invalid_solid_indices": invalid_solid_indices,
        "faces_with_polygonal_triangulation": faces_with_triangulation,
        "triangulation_node_count": triangulation_node_count,
        "triangle_count": triangle_count,
    }


def _bounding_box(shape: cq.Shape) -> dict[str, Any]:
    box = shape.BoundingBox(tolerance=1.0e-7)
    x_length = float(box.xlen)
    y_length = float(box.ylen)
    z_length = float(box.zlen)
    return {
        "minimum_mm": {"x": _round(box.xmin), "y": _round(box.ymin), "z": _round(box.zmin)},
        "maximum_mm": {"x": _round(box.xmax), "y": _round(box.ymax), "z": _round(box.zmax)},
        "span_mm": {"x": _round(x_length), "y": _round(y_length), "z": _round(z_length)},
        "axial_z_length_mm": _round(z_length),
        "overall_max_span_mm": _round(max(x_length, y_length, z_length)),
        "diagonal_mm": _round(math.sqrt(x_length**2 + y_length**2 + z_length**2)),
    }


def _parse_step_text(path: Path, data: bytes) -> tuple[str, dict[str, Any]]:
    text = data.decode("latin-1", errors="replace")
    entity_counts = Counter(match.group(1).upper() for match in ENTITY_TYPE_RE.finditer(text))

    file_description_record = _header_record(text, "FILE_DESCRIPTION")
    file_name_record = _header_record(text, "FILE_NAME")
    file_schema_record = _header_record(text, "FILE_SCHEMA")
    schemas = _step_strings(file_schema_record)
    file_name_strings = _step_strings(file_name_record)
    file_description_strings = _step_strings(file_description_record)

    product_records = [
        {
            "entity_id": int(match.group(1)),
            "product_id": _step_unquote(match.group(2)),
            "name": _step_unquote(match.group(3)),
        }
        for match in PRODUCT_RE.finditer(text)
    ]
    occurrence_records = [
        {
            "entity_id": int(match.group(1)),
            "occurrence_id": _step_unquote(match.group(2)),
            "name": _step_unquote(match.group(3)),
        }
        for match in OCCURRENCE_RE.finditer(text)
    ]

    protocol_records = []
    for match in re.finditer(
        r"APPLICATION_PROTOCOL_DEFINITION\s*\((.*?)\)\s*;", text, re.I | re.S
    ):
        protocol_records.append(_step_strings(match.group(1)))

    exact_counts = {name: int(entity_counts.get(name, 0)) for name in EXACT_BREP_ENTITY_TYPES}
    faceted_counts = {
        name: int(entity_counts.get(name, 0))
        for name in FACETED_OR_TESSELLATED_TYPES
        if entity_counts.get(name, 0)
    }
    broad_faceted_counts = {
        name: int(count)
        for name, count in sorted(entity_counts.items())
        if "FACET" in name or "TESSELLAT" in name or "TRIANGULAT" in name
    }

    return text, {
        "header": {
            "iso_10303_21_marker": bool(re.search(r"^\s*ISO-10303-21\s*;", text, re.I)),
            "has_header_section": bool(re.search(r"\bHEADER\s*;", text, re.I)),
            "has_data_section": bool(re.search(r"\bDATA\s*;", text, re.I)),
            "file_description": file_description_strings,
            "file_name": file_name_strings[0] if file_name_strings else None,
            "timestamp": file_name_strings[1] if len(file_name_strings) > 1 else None,
            "file_name_strings": file_name_strings,
            "schemas": schemas,
            "application_protocol_definitions": protocol_records,
        },
        "products": {
            "count": len(product_records),
            "records": product_records,
            "names": [record["name"] for record in product_records],
            "unnamed": [record for record in product_records if _is_unnamed(record["name"])],
        },
        "raw_occurrences": {
            "next_assembly_usage_occurrence_count": len(occurrence_records),
            "records": occurrence_records,
            "unnamed": [record for record in occurrence_records if _is_unnamed(record["name"])],
        },
        "step_entities": {
            "total_simple_entity_instances": int(sum(entity_counts.values())),
            "exact_brep": exact_counts,
            "exact_brep_total": int(sum(exact_counts.values())),
            "faceted_or_tessellated": faceted_counts,
            "faceted_or_tessellated_broad": broad_faceted_counts,
            "faceted_or_tessellated_total": int(sum(broad_faceted_counts.values())),
            "selected_topology": {
                name: int(entity_counts.get(name, 0))
                for name in (
                    "ADVANCED_FACE",
                    "CLOSED_SHELL",
                    "OPEN_SHELL",
                    "MANIFOLD_SOLID_BREP",
                    "BREP_WITH_VOIDS",
                    "FACETED_BREP",
                )
            },
        },
    }


def validate_file(path_arg: str) -> dict[str, Any]:
    path = Path(path_arg).expanduser().resolve()
    result: dict[str, Any] = {
        "path": str(path),
        "file_name": path.name,
        "exists": path.is_file(),
        "import_engine": "CadQuery Assembly.importStep / OCCT STEPCAF-XCAF",
        "errors": [],
        "warnings": [],
        "gate_failures": [],
    }
    if not path.is_file():
        result["errors"].append("FILE_NOT_FOUND")
        result["pass"] = False
        return result

    try:
        data = path.read_bytes()
    except OSError as exc:
        result["errors"].append(f"FILE_READ_ERROR: {exc}")
        result["pass"] = False
        return result

    result["file_size_bytes"] = len(data)
    result["sha256"] = hashlib.sha256(data).hexdigest()

    try:
        _, parsed = _parse_step_text(path, data)
        result.update(parsed)
    except Exception as exc:  # keep an actionable JSON record for malformed inputs
        result["errors"].append(f"STEP_TEXT_PARSE_ERROR: {type(exc).__name__}: {exc}")
        result["pass"] = False
        return result

    try:
        assembly = cq.Assembly.importStep(str(path))
        assembly_nodes = _walk_assembly(assembly)
        compound = assembly.toCompound()
        topology = _count_topology(compound)
        bbox = _bounding_box(compound)
    except Exception as exc:
        result["errors"].append(f"XCAF_REIMPORT_ERROR: {type(exc).__name__}: {exc}")
        result["pass"] = False
        return result

    unnamed_nodes = [node for node in assembly_nodes if _is_unnamed(node["name"])]
    result["xcaf_assembly"] = {
        "root_name": assembly.name,
        "node_count_including_root": len(assembly_nodes),
        "occurrence_node_count_excluding_root": max(0, len(assembly_nodes) - 1),
        "leaf_count": sum(1 for node in assembly_nodes if node["is_leaf"]),
        "maximum_depth": max((node["depth"] for node in assembly_nodes), default=0),
        "nodes": assembly_nodes,
        "unnamed_occurrences": unnamed_nodes,
        "unnamed_occurrence_count": len(unnamed_nodes),
    }
    result["geometry"] = topology
    result["bounding_box"] = bbox

    schema_names = [schema.upper() for schema in result["header"]["schemas"]]
    is_ap242 = any("AP242" in schema for schema in schema_names)
    result["header"]["is_ap242"] = is_ap242

    gates = {
        "ISO_10303_21_CONTAINER": bool(result["header"]["iso_10303_21_marker"]),
        "AP242_SCHEMA": is_ap242,
        "PRODUCT_RECORD_PRESENT": result["products"]["count"] > 0,
        "XCAF_ASSEMBLY_REIMPORT": True,
        "SOLID_TOPOLOGY_PRESENT": topology["solid_count"] > 0,
        "EXACT_BREP_ENTITY_PRESENT": result["step_entities"]["exact_brep_total"] > 0,
        "NO_FACETED_OR_TESSELLATED_ENTITIES": (
            result["step_entities"]["faceted_or_tessellated_total"] == 0
        ),
        "NO_POLYGONAL_TRIANGULATION": topology["faces_with_polygonal_triangulation"] == 0,
        "WHOLE_SHAPE_VALID": topology["whole_shape_valid"],
        "ALL_SOLIDS_VALID": topology["invalid_solid_count"] == 0,
        "ALL_PRODUCTS_NAMED": len(result["products"]["unnamed"]) == 0,
        "ALL_OCCURRENCES_NAMED_IN_STEP": len(result["raw_occurrences"]["unnamed"]) == 0,
        "ALL_XCAF_NODES_NAMED": len(unnamed_nodes) == 0,
    }
    result["gates"] = gates
    result["gate_failures"] = [name for name, passed in gates.items() if not passed]
    result["pass"] = not result["errors"] and not result["gate_failures"]
    return result


def _human_report(result: dict[str, Any]) -> str:
    lines = [f"FILE: {result['path']}", f"PASS: {str(bool(result.get('pass'))).lower()}"]
    if result.get("errors"):
        lines.extend(f"ERROR: {error}" for error in result["errors"])
        return "\n".join(lines)

    header = result["header"]
    products = result["products"]
    raw_occurrences = result["raw_occurrences"]
    assembly = result["xcaf_assembly"]
    geometry = result["geometry"]
    entities = result["step_entities"]
    bbox = result["bounding_box"]
    span = bbox["span_mm"]
    lines.extend(
        [
            f"Schema: {', '.join(header['schemas']) or '<missing>'}",
            (
                "Assembly: "
                f"products={products['count']}, "
                f"STEP_occurrences={raw_occurrences['next_assembly_usage_occurrence_count']}, "
                f"XCAF_nodes={assembly['node_count_including_root']}, "
                f"unnamed={assembly['unnamed_occurrence_count']}"
            ),
            (
                "Geometry: "
                f"solids={geometry['solid_count']}, faces={geometry['face_count']}, "
                f"valid={str(geometry['whole_shape_valid']).lower()}, "
                f"invalid_solids={geometry['invalid_solid_count']}"
            ),
            (
                "STEP representation: "
                f"exact_BREP_entities={entities['exact_brep_total']}, "
                f"faceted_or_tessellated_entities={entities['faceted_or_tessellated_total']}"
            ),
            (
                "Triangulation: "
                f"faces={geometry['faces_with_polygonal_triangulation']}, "
                f"nodes={geometry['triangulation_node_count']}, "
                f"triangles={geometry['triangle_count']}"
            ),
            (
                "Bounding box [mm]: "
                f"X={span['x']:.6f}, Y={span['y']:.6f}, Z={span['z']:.6f}; "
                f"overall_max_span={bbox['overall_max_span_mm']:.6f}"
            ),
            "Gate failures: " + (", ".join(result["gate_failures"]) or "none"),
        ]
    )
    return "\n".join(lines)


def _contains_import_error(result: dict[str, Any]) -> bool:
    return any(
        error.startswith(("FILE_NOT_FOUND", "FILE_READ_ERROR", "XCAF_REIMPORT_ERROR"))
        for error in result.get("errors", [])
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate exact-solid STEP/AP242 files using ISO text and XCAF reimport."
    )
    parser.add_argument("step_files", nargs="+", help="one or more STEP/STP files")
    parser.add_argument(
        "--json",
        action="store_true",
        help="write the complete machine-readable result to standard output",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    results = [validate_file(path) for path in args.step_files]
    payload: dict[str, Any] = {
        "validator": "validate_step.py",
        "input_count": len(results),
        "all_pass": all(result.get("pass", False) for result in results),
        "results": results,
    }
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write("\n\n".join(_human_report(result) for result in results) + "\n")

    if any(_contains_import_error(result) for result in results):
        return 2
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
