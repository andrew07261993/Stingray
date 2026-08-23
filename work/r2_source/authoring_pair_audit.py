#!/usr/bin/env python3
"""Fast authoring-model overlap audit used before independent STEP validation."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

import build_r2


def boxes_overlap(a, b, tol: float = 1.0e-7) -> bool:
    return not (
        a.xmax < b.xmin - tol or b.xmax < a.xmin - tol
        or a.ymax < b.ymin - tol or b.ymax < a.ymin - tol
        or a.zmax < b.zmin - tol or b.zmax < a.zmin - tol
    )


def common_volume(a, b) -> float:
    op = BRepAlgoAPI_Common(a.wrapped, b.wrapped)
    op.SetRunParallel(False)
    op.SetFuzzyValue(1.0e-7)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("BRepAlgoAPI_Common failed")
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), props)
    return abs(props.Mass())


def audit(state: str) -> dict:
    builder = build_r2.build_state(state)
    ids = sorted(builder.global_shapes)
    shapes = builder.global_shapes
    bboxes = {key: shapes[key].BoundingBox() for key in ids}
    results = []
    blocked = []
    broadphase = 0
    for i, ida in enumerate(ids):
        for idb in ids[i + 1:]:
            if not boxes_overlap(bboxes[ida], bboxes[idb]):
                continue
            broadphase += 1
            try:
                volume = common_volume(shapes[ida], shapes[idb])
            except Exception as exc:  # Boolean failure is never treated as zero.
                blocked.append({"a": ida, "b": idb, "error": str(exc)})
                continue
            if volume > 1.0e-5:
                results.append({"a": ida, "b": idb, "common_volume_mm3": volume})
    results.sort(key=lambda row: row["common_volume_mm3"], reverse=True)
    return {
        "state": state,
        "occurrences": len(ids),
        "expected_pairs": len(ids) * (len(ids) - 1) // 2,
        "broadphase_candidates": broadphase,
        "positive_volume_pairs": len(results),
        "blocked_pairs": blocked,
        "overlaps": results,
    }


def main() -> None:
    state = sys.argv[1].upper() if len(sys.argv) > 1 else "STOWED"
    if state not in {"STOWED", "DEPLOYED"}:
        raise SystemExit("state must be STOWED or DEPLOYED")
    result = audit(state)
    out = build_r2.ANALYSIS_DIR / f"authoring_pair_audit_{state.lower()}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "overlaps"}, indent=2))
    print(json.dumps(result["overlaps"][:80], indent=2))


if __name__ == "__main__":
    main()
