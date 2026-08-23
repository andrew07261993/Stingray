#!/usr/bin/env python3
"""Targeted exact-BREP exploration for arm/crosshead clearance."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import cadquery as cq


SOURCE = Path(__file__).with_name("build_final_cad.py")
SPEC = importlib.util.spec_from_file_location("df8", SOURCE)
assert SPEC and SPEC.loader
df8 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = df8
SPEC.loader.exec_module(df8)


def candidate(theta: float, ring_ro: float, cheek_xmax: float) -> tuple[cq.Shape, list[tuple[str, cq.Shape]]]:
    z = df8.kinematic(theta)["crosshead_z"]
    out = df8.tube(7.0, 3.55, z - 3.0, z + 3.0)
    components: list[tuple[str, cq.Shape]] = []
    xmin = 6.5
    dx = cheek_xmax - xmin
    xc = (xmin + cheek_xmax) / 2.0
    for phi in (0.0, 120.0, 240.0):
        for yy in (-3.5, 3.5):
            cheek = df8.rz(df8.box_center(dx, 1.5, 5.2, xc, yy, z), phi)
            ring = df8.rz(df8.ring_y(df8.RC, z, 1.5, ring_ro, 2.18, yy), phi)
            components.extend([("cheek", cheek), ("ring", ring)])
            out = out.fuse(cheek).fuse(ring)
    for phi in (60.0, 180.0, 300.0):
        spoke = df8.rz(df8.box_center(8.0, 3.4, 5.2, 10.5, 0.0, z), phi)
        components.append(("spoke", spoke))
        out = out.fuse(spoke)
    return out, components


def vol(a: cq.Shape, b: cq.Shape) -> float:
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
        return 0.0
    return a.intersect(b).Volume()


angles = (45.0, 50.0, 60.0, 70.0, 80.0)
arms = {theta: df8.arm_shape(theta, 0.0) for theta in angles}

for ring_ro, cheek_xmax in ((4.2, 18.0), (3.6, 17.5), (3.2, 17.5), (2.8, 17.0), (2.55, 17.0)):
    print(f"candidate ro={ring_ro:.2f} xmax={cheek_xmax:.2f}")
    for theta in angles:
        ch, components = candidate(theta, ring_ro, cheek_xmax)
        av = vol(arms[theta], ch)
        by_kind = {kind: 0.0 for kind in ("cheek", "ring", "spoke")}
        for kind, item in components:
            by_kind[kind] += vol(arms[theta], item)
        print(theta, f"arm={av:.9g}", "parts=" + ",".join(f"{k}:{v:.6g}" for k, v in by_kind.items()))
