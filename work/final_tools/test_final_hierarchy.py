#!/usr/bin/env python3
"""Nonpersistent round-trip diagnostic for the authored AP242 hierarchy.

The script deliberately bypasses final-scope registration because it tests
only XCAF assembly-tree construction, export, and clean reimport.  It writes
all output beneath a caller-provided temporary directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_r2
import r2_hardware as hardware
import r2_hierarchy
import validate_r2


def build_endpoint(state: str) -> build_r2.R2Builder:
    builder = build_r2.R2Builder(state)
    build_r2.register_mandatory_hardware_part_definitions(builder)
    build_r2.build_forward(builder)
    build_r2.build_arm_module(builder)
    build_r2.build_aft(builder)
    build_r2.add_mandatory_hardware_occurrences(builder)
    build_r2.add_engineered_fit_register(builder)
    build_r2.add_primary_connections(builder)
    build_r2.add_motion_tracks(builder)
    hierarchy = r2_hierarchy.rebuild_named_hierarchy(builder)
    for assembly in (builder.forward, builder.arm_module, builder.aft):
        builder.root.add(assembly, name=assembly.name)
    assert hierarchy["leaf_occurrence_count"] == len(builder.occurrences)
    return builder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", choices=("STOWED", "DEPLOYED"), default="STOWED")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    builder = build_endpoint(args.state)
    step_path = args.out / f"hierarchy_{args.state.lower()}.step"
    build_r2.export_ap242(builder.root, step_path)
    build_r2.name_assembly_usage_occurrences(step_path)

    inventory = build_r2.serialize_builder(builder)
    inventory["assembly_hierarchy"] = builder.assembly_hierarchy
    endpoint = validate_r2.load_endpoint(args.state, step_path, inventory)
    result = {
        "state": args.state,
        "step_path": str(step_path),
        "step_size_bytes": step_path.stat().st_size,
        "authored_occurrence_count": len(builder.occurrences),
        "imported_shape_node_count": sum(
            bool(row.get("has_shape")) for row in endpoint.occurrence_rows
        ),
        "imported_assembly_node_count": sum(
            not bool(row.get("has_shape")) for row in endpoint.occurrence_rows
        ),
        "hierarchy": builder.assembly_hierarchy,
        "leaf_identity_audit": validate_r2.imported_leaf_identity_audit(endpoint),
        "assembly_hierarchy_audit": validate_r2.assembly_hierarchy_audit(endpoint, inventory),
    }
    output_path = args.out / f"hierarchy_{args.state.lower()}_audit.json"
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["leaf_identity_audit"]["accepted"]:
        raise SystemExit(1)
    if not result["assembly_hierarchy_audit"]["accepted"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
