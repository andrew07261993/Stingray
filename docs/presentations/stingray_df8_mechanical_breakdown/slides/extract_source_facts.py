#!/usr/bin/env python3
"""Extract deterministic presentation facts from the authoritative DF8 source tree.

The center-of-gravity values are recomputed from the current exact source B-reps:
each occurrence uses the global B-rep volume centroid and the occurrence mass
basis already resolved by the authoritative PartDef catalog.  This script does
not edit or re-export the source CAD.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_module(source_root: Path):
    module_path = source_root / "work" / "r2_source" / "build_r2.py"
    source_dir = module_path.parent
    sys.path.insert(0, str(source_dir))
    spec = importlib.util.spec_from_file_location("stingray_df8_build_r2", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load authoritative source module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_text(source_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=source_root, text=True, encoding="utf-8"
    ).strip()


def assembly_mass_properties(module: Any, state: str, inventory: dict[str, Any]) -> dict[str, Any]:
    builder = module.build_state(state)
    weighted = [0.0, 0.0, 0.0]
    total_mass = 0.0
    unresolved: list[str] = []
    overrides = inventory.get("mass_overrides_kg", {})
    parts_by_number = {row["part_number"]: row for row in inventory["parts"]}

    for occurrence in builder.occurrences:
        part_number = occurrence.part_number
        if occurrence.occurrence_id in overrides:
            mass = overrides[occurrence.occurrence_id]
            mass_basis = "STATE_INVARIANT_OCCURRENCE_OVERRIDE"
        elif part_number in overrides:
            mass = overrides[part_number]
            mass_basis = "STATE_INVARIANT_PART_OVERRIDE"
        else:
            mass = parts_by_number[part_number].get("mass_kg")
            mass_basis = "COMMITTED_AUTHORING_INVENTORY_PART_MASTER_MASS"
        if mass is None:
            unresolved.append(occurrence.occurrence_id)
            continue
        center = builder.global_shapes[occurrence.occurrence_id].Center()
        total_mass += float(mass)
        weighted[0] += float(mass) * float(center.x)
        weighted[1] += float(mass) * float(center.y)
        weighted[2] += float(mass) * float(center.z)

    if unresolved:
        raise RuntimeError(f"Unresolved occurrence masses: {unresolved}")
    cg = [value / total_mass for value in weighted]
    return {
        "state": state,
        "occurrence_count": len(builder.occurrences),
        "unique_part_definition_count": len(builder.catalog.parts),
        "system_mass_kg": total_mass,
        "center_of_gravity_mm_in_master_frame": {"x": cg[0], "y": cg[1], "z": cg[2]},
        "calculation_basis": (
            "Mass-weighted global volume centroid of every authoritative occurrence B-rep; "
            "mass follows the validator aggregation rule and the committed authoring inventory "
            "(occurrence override, part override, then part-master mass)."
        ),
        "mass_basis_precedence": [
            "STATE_INVARIANT_OCCURRENCE_OVERRIDE",
            "STATE_INVARIANT_PART_OVERRIDE",
            "COMMITTED_AUTHORING_INVENTORY_PART_MASTER_MASS",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    output = args.output.resolve()

    current = json.loads((source_root / "CURRENT_STATE.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (source_root / "work" / "final_analysis" / "authoring_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    inventories = {
        state: json.loads(
            (
                source_root
                / "work"
                / "final_analysis"
                / f"authoring_inventory_{state.lower()}.json"
            ).read_text(encoding="utf-8")
        )
        for state in ("STOWED", "DEPLOYED")
    }
    parity_summary = json.loads(
        (
            source_root
            / "work"
            / "final_analysis"
            / "state_parity_provenance_audit"
            / "state_parity_provenance_summary.json"
        ).read_text(encoding="utf-8")
    )
    checkpoint_path = (
        source_root
        / "work"
        / "final_analysis"
        / "manual_inspection_checkpoint"
        / "CAD_INSPECTION_STATUS.txt"
    )
    checkpoint_text = checkpoint_path.read_text(encoding="utf-8")

    module = load_module(source_root)
    stowed = assembly_mass_properties(module, "STOWED", inventories["STOWED"])
    deployed = assembly_mass_properties(module, "DEPLOYED", inventories["DEPLOYED"])

    metadata_mass = float(current["dimensions_mass_reserve"]["system_mass_kg"])
    state_mass_delta = stowed["system_mass_kg"] - deployed["system_mass_kg"]
    if abs(state_mass_delta) > 1e-9:
        raise RuntimeError(
            f"Source-derived endpoint masses differ: STOWED={stowed['system_mass_kg']} "
            f"DEPLOYED={deployed['system_mass_kg']}"
        )
    metadata_delta = stowed["system_mass_kg"] - metadata_mass
    if abs(metadata_delta) > 1e-3:
        raise RuntimeError(
            f"Source/current-state mass discrepancy exceeds 1 g: {metadata_delta} kg"
        )

    parity_register = (
        source_root
        / "work"
        / "final_analysis"
        / "state_parity_provenance_audit"
        / "state_parity_provenance_register.csv"
    )
    with parity_register.open(encoding="utf-8", newline="") as handle:
        parity_rows = list(csv.DictReader(handle))
    parity_pass = sum(1 for row in parity_rows if "RESOLVED" in row.get("final_disposition", ""))

    facts = {
        "schema": "STINGRAY_DF8_PRESENTATION_SOURCE_FACTS_V1",
        "authoritative_source_root": source_root.as_posix(),
        "source_commit_sha": git_text(source_root, "rev-parse", "HEAD"),
        "source_commit_timestamp": git_text(source_root, "show", "-s", "--format=%cI", "HEAD"),
        "source_branch": git_text(source_root, "branch", "--show-current"),
        "source_files": {
            "current_state": "CURRENT_STATE.json",
            "authoring_manifest": "work/final_analysis/authoring_manifest.json",
            "stowed_ap242": "work/final_release/STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step",
            "deployed_ap242": "work/final_release/STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step",
            "state_parity_summary": "work/final_analysis/state_parity_provenance_audit/state_parity_provenance_summary.json",
            "manual_checkpoint": "work/final_analysis/manual_inspection_checkpoint/CAD_INSPECTION_STATUS.txt",
        },
        "hard_requirements": manifest["hard_requirements"],
        "dimensions_mass_reserve": current["dimensions_mass_reserve"],
        "mass_properties": {"stowed": stowed, "deployed": deployed},
        "mass_reconciliation": {
            "source_derived_inventory_mass_kg": stowed["system_mass_kg"],
            "current_state_metadata_mass_kg": metadata_mass,
            "source_minus_metadata_kg": metadata_delta,
            "absolute_difference_kg": abs(metadata_delta),
            "source_derived_mass_reserve_kg": (
                float(manifest["hard_requirements"]["mass_max_kg"])
                - stowed["system_mass_kg"]
            ),
            "disposition": (
                "RECORDED_SOURCE_METADATA_DISCREPANCY — exact current source and committed "
                "authoring inventory control the presentation calculation"
            ),
        },
        "validation": {
            "computed_release_status": current["validation"]["computed_release_status"],
            "package_required_label": current["validation"]["package_required_label"],
            "latest_validator_exit_code": current["validation"]["last_validator_exit_code"],
            "validator_failure_stage": current["validation"]["validator_failure"]["failure_stage"],
            "validator_failure_message": current["validation"]["validator_failure"]["exception_message"],
            "state_parity_provenance_register_row_count": len(parity_rows),
            "state_parity_provenance_register_resolved_count": parity_pass,
            "state_parity_occurrence_count": int(
                parity_summary["current_validator_union_occurrence_count"]
            ),
            "state_parity_occurrence_pass_count": (
                int(parity_summary["current_validator_union_occurrence_count"])
                if int(parity_summary["current_validator_overall_issue_count"]) == 0
                else int(parity_summary["current_validator_union_occurrence_count"])
                - int(parity_summary["current_validator_overall_issue_count"])
            ),
            "state_parity_summary": parity_summary,
            "manual_checkpoint_text": checkpoint_text,
            "completed_automated_motion_range_deg": [0, 55],
            "first_unvalidated_motion_angle_deg": 56,
            "accepted_completed_angle_count": 56,
            "full_motion_gate_status": "INCOMPLETE — NOT PASS",
        },
        "limitations": [
            "Current final R2 validation is not release-authorized.",
            "The accepted automated motion checkpoint covers 0 through 55 degrees only; 56 through 80 degrees remain unvalidated in that checkpoint.",
            "No physical, environmental, calibrated damper force-speed, or manufacturing qualification evidence is asserted by this presentation.",
            "Computed CG values are source-derived CAD mass-property calculations, not a measured physical balance result.",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output), "stowed": stowed, "deployed": deployed}, indent=2))


if __name__ == "__main__":
    main()
