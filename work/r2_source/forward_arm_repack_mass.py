#!/usr/bin/env python3
"""Exact occurrence-level mass properties for the forward-arm checkpoint."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np


def load_builder(source: Path, state: str):
    sys.path.insert(0, str(source))
    build_r2 = importlib.import_module("build_r2")
    return build_r2, build_r2.build_state(state)


def properties(build_r2, builder):
    masses, centers, local_inertias = [], [], []
    for occurrence in builder.occurrences:
        part = builder.catalog.parts[occurrence.part_number]
        mass = float(part.resolved_mass() or 0.0)
        if mass <= 0.0:
            continue
        shape = build_r2.g.moved(part.shape, occurrence.location)
        volume = float(shape.Volume())
        center = shape.Center()
        matrix = np.asarray(cq.Shape.matrixOfInertia(shape), dtype=float)
        masses.append(mass)
        centers.append(np.array([center.x, center.y, center.z], dtype=float))
        local_inertias.append(matrix * (mass / volume))
    total = float(sum(masses))
    cg = sum(m * c for m, c in zip(masses, centers)) / total
    inertia = np.zeros((3, 3), dtype=float)
    eye = np.eye(3)
    for mass, center, local in zip(masses, centers, local_inertias):
        d = center - cg
        inertia += local + mass * ((d @ d) * eye - np.outer(d, d))
    principal = np.linalg.eigvalsh(inertia)
    return {
        "state": builder.state,
        "total_mass_kg": total,
        "cg_mm": {"x": float(cg[0]), "y": float(cg[1]), "z": float(cg[2])},
        "radial_cg_mm": float(np.hypot(cg[0], cg[1])),
        "tip_to_cg_mm": float(cg[2]),
        "inertia_tensor_kg_mm2": inertia.tolist(),
        "principal_moments_kg_mm2": principal.tolist(),
        "occurrence_count": len(builder.occurrences),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--state", choices=("STOWED", "DEPLOYED"), default="STOWED")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_r2, builder = load_builder(args.source.resolve(), args.state)
    result = properties(build_r2, builder)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
