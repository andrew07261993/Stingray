#!/usr/bin/env python3
"""Combine the baseline and final exact occurrence-level mass tensors."""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "forward_arm_repack"


def rod_between(start, end, radius):
    a, b = cq.Vector(*start), cq.Vector(*end)
    delta = b - a
    return cq.Solid.makeCylinder(radius, delta.Length, a, delta.normalized())


def shift(mass, delta):
    eye = np.eye(3)
    return mass * ((delta @ delta) * eye - np.outer(delta, delta))


baseline = json.loads((OUT / "baseline_mass_properties.json").read_text())
updated = json.loads((OUT / "updated_mass_properties.json").read_text())
updated["mass_reserve_to_18_14_kg"] = 18.14 - float(updated["total_mass_kg"])
updated["trim_ballast"] = {
    "mass_kg": 0.351133873274735,
    "included_in_occurrence_level_tensor": True,
    "occurrence_id": "CG-TRIM-BALLAST-001",
}

payload = {"baseline": baseline, "updated": updated}
(OUT / "mass_cg_inertia_comparison.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(updated, indent=2))
