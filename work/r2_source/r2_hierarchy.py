#!/usr/bin/env python3
"""Deterministic XCAF assembly-tree reconstruction from authored parent paths."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

import cadquery as cq

import r2_geometry as g
import final_detail_naming


def _slug(value: str, limit: int = 72) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]+", "_", value.upper()).strip("_")[:limit]


def rebuild_named_hierarchy(builder: Any) -> dict[str, Any]:
    """Construct the exact authored nested tree before it is added to root.

    Occurrence transforms remain part-local-to-product-datum placements; all
    intermediate assembly nodes are identity datums.  CadQuery copies a child
    assembly when it is added, so this routine populates leaves first and then
    attaches subassemblies strictly deepest-first.
    """
    top_names = (
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY",
    )
    if getattr(builder.root, "children", None):
        raise ValueError(
            "Root assembly must be empty before named hierarchy reconstruction; "
            "call this routine before adding the three top-level assemblies"
        )
    occurrence_ids = [str(occurrence.occurrence_id).strip() for occurrence in builder.occurrences]
    blank_ids = [index for index, value in enumerate(occurrence_ids, start=1) if not value]
    duplicate_ids = sorted(
        value for value, count in Counter(occurrence_ids).items() if value and count > 1
    )
    if blank_ids or duplicate_ids:
        raise ValueError(
            "Every hierarchy leaf requires a unique nonblank occurrence ID: "
            f"blank_rows={blank_ids}, duplicates={duplicate_ids}"
        )
    normalized_parent_paths = {
        occurrence.occurrence_id: str(occurrence.parent_path).strip().strip("/")
        for occurrence in builder.occurrences
    }
    paths = set(normalized_parent_paths.values())
    if not paths or any(not path for path in paths):
        raise ValueError("Every installed occurrence requires a nonblank assembly parent path")
    bad_top = sorted(path for path in paths if path.split("/", 1)[0] not in top_names)
    if bad_top:
        raise ValueError(f"Occurrence parent paths name unknown top assemblies: {bad_top}")

    all_paths: set[str] = set(top_names)
    for path in paths:
        segments = path.split("/")
        all_paths.update("/".join(segments[:index]) for index in range(1, len(segments) + 1))
    nodes = {
        path: cq.Assembly(name=final_detail_naming.display_assembly_path(path).rsplit("/", 1)[-1])
        for path in sorted(all_paths, key=lambda value: (value.count("/"), value))
    }

    for occurrence in builder.occurrences:
        part = builder.catalog.parts[occurrence.part_number]
        node_name = occurrence.display_name
        nodes[normalized_parent_paths[occurrence.occurrence_id]].add(
            part.shape,
            name=node_name,
            loc=occurrence.location,
            color=g.COLORS.get(part.color_key, g.COLORS["steel"]),
        )

    nested_paths = sorted(
        (path for path in all_paths if "/" in path),
        key=lambda value: (-value.count("/"), value),
    )
    for child_path in nested_paths:
        parent_path, _legacy_child_name = child_path.rsplit("/", 1)
        child_name = final_detail_naming.display_assembly_path(child_path).rsplit("/", 1)[-1]
        nodes[parent_path].add(nodes[child_path], name=child_name)

    builder.forward = nodes[top_names[0]]
    builder.arm_module = nodes[top_names[1]]
    builder.aft = nodes[top_names[2]]
    hierarchy = {
        "root_name": builder.root.name,
        "top_level_assembly_names": [final_detail_naming.display_assembly_path(path) for path in top_names],
        "assembly_paths": sorted(final_detail_naming.display_assembly_path(path) for path in all_paths),
        "leaf_occurrence_count": len(builder.occurrences),
    }
    builder.assembly_hierarchy = hierarchy
    return hierarchy


__all__ = ["rebuild_named_hierarchy"]
