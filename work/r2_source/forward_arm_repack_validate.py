#!/usr/bin/env python3
"""Bounded endpoint and five-angle validation for the owner checkpoint."""

from __future__ import annotations

import json
from pathlib import Path

import validate_r2

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "work" / "final_release"
ANALYSIS = ROOT / "work" / "final_analysis"
OUT = ROOT / "work" / "forward_arm_repack"
OUT.mkdir(parents=True, exist_ok=True)

files = {
    "STOWED": RELEASE / "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step",
    "DEPLOYED": RELEASE / "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step",
}
inventories = {
    state: json.loads((ANALYSIS / f"authoring_inventory_{state.lower()}.json").read_text(encoding="utf-8"))
    for state in files
}
endpoints = {state: validate_r2.load_endpoint(state, files[state], inventories[state]) for state in files}
identity = {state: validate_r2.imported_leaf_identity_audit(endpoint) for state, endpoint in endpoints.items()}
dimensions = validate_r2.key_dimensions(endpoints, inventories)
motion_path = OUT / "five_angle_boolean_gate_pass2" / "five_angle_exact_boolean_summary.json"
motion_gate = json.loads(motion_path.read_text(encoding="utf-8"))
motion = {
    "sample_count": len(motion_gate["angles_deg"]),
    "unauthorized_positive_volume_pair_count": len(motion_gate["unauthorized_positive_pairs"]),
    "boolean_blocked_pair_count": motion_gate["boolean_blocked_pair_count"],
    "track_errors": [] if motion_gate["track_validation_error_count"] == 0 else [
        f"{motion_gate['track_validation_error_count']} track validation errors"
    ],
    "disposition": motion_gate["disposition"],
    "per_angle": motion_gate["per_angle"],
    "evidence_path": str(motion_path.relative_to(ROOT)),
}

def total_mass(inventory):
    part_mass = {p["part_number"]: float(p.get("mass_kg") or 0.0) for p in inventory["parts"]}
    overrides = inventory.get("mass_overrides_kg", {})
    return sum(float(overrides.get(o["occurrence_id"], part_mass.get(o["part_number"], 0.0))) for o in inventory["occurrences"])

summary = {
    "checkpoint": "FORWARD-ARM REPACK CAD COMPLETE — OWNER CREO INSPECTION REQUIRED",
    "clean_reimport": {
        state: {
            "ap242": endpoint.step_text["ap242_schema_detected"],
            "faceted_brep_count": endpoint.step_text.get("faceted_brep_count", 0),
            "solid_count": len(endpoint.solid_records),
            "invalid_solid_count": sum(not solid.valid for solid in endpoint.solid_records),
            "leaf_identity_accepted": identity[state]["accepted"],
        }
        for state, endpoint in endpoints.items()
    },
    "mass_kg": {state: total_mass(inventory) for state, inventory in inventories.items()},
    "key_dimensions": dimensions,
    "motion_angles_deg": [0, 20, 40, 55, 80],
    "motion": {
        "sample_count": motion["sample_count"],
        "unauthorized_positive_volume_pair_count": motion["unauthorized_positive_volume_pair_count"],
        "boolean_blocked_pair_count": motion["boolean_blocked_pair_count"],
        "track_errors": motion.get("track_errors", []),
        "disposition": motion["disposition"],
        "per_angle": motion["per_angle"],
        "evidence_path": motion["evidence_path"],
    },
}
(OUT / "targeted_validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
