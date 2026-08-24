#!/usr/bin/env python3
"""Combine the exact trim-ballast tensor with the pre-trim checkpoint tensor."""

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
untrimmed = json.loads((OUT / "updated_mass_properties.json").read_text())

length = 155.0
shape = cq.Solid.makeCylinder(6.512850623, length)
for local_z in (3.0, length - 3.0):
    for phi in (90.0, 210.0, 330.0):
        end = (25.35 * math.cos(math.radians(phi)), 25.35 * math.sin(math.radians(phi)), local_z)
        shape = shape.fuse(rod_between((0.0, 0.0, local_z), end, 0.80))
shape = shape.clean()

trim_mass = 0.351133873274735
trim_center_local = shape.Center()
trim_center = np.array([trim_center_local.x, trim_center_local.y, trim_center_local.z + 1257.5])
trim_local = np.asarray(cq.Shape.matrixOfInertia(shape)) * (trim_mass / shape.Volume())

old_mass = float(untrimmed["total_mass_kg"])
old_cg = np.array(list(untrimmed["cg_mm"].values()), dtype=float)
old_inertia = np.asarray(untrimmed["inertia_tensor_kg_mm2"], dtype=float)
new_mass = old_mass + trim_mass
new_cg = (old_mass * old_cg + trim_mass * trim_center) / new_mass
new_inertia = old_inertia + shift(old_mass, old_cg - new_cg) + trim_local + shift(trim_mass, trim_center - new_cg)
principal = np.linalg.eigvalsh(new_inertia)

updated = {
    "state": "STOWED",
    "total_mass_kg": float(new_mass),
    "mass_reserve_to_18_14_kg": float(18.14 - new_mass),
    "cg_mm": {"x": float(new_cg[0]), "y": float(new_cg[1]), "z": float(new_cg[2])},
    "radial_cg_mm": float(np.hypot(new_cg[0], new_cg[1])),
    "tip_to_cg_mm": float(new_cg[2]),
    "inertia_tensor_kg_mm2": new_inertia.tolist(),
    "principal_moments_kg_mm2": principal.tolist(),
    "trim_ballast": {"mass_kg": trim_mass, "cg_mm": trim_center.tolist(), "solid_count": len(shape.Solids()), "valid": shape.isValid()},
}

payload = {"baseline": baseline, "updated": updated}
(OUT / "mass_cg_inertia_comparison.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(updated, indent=2))
