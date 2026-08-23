#!/usr/bin/env python3
"""Deterministic exact per-solid endpoint audit of the editable final source."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

import build_r2


FUZZY_MM = 1.0e-7
POSITIVE_MM3 = 1.0e-6


def _signed_volume(shape: Any) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return float(props.Mass())


def _boxes_overlap(a: Any, b: Any) -> bool:
    return not (
        a.xmax < b.xmin - FUZZY_MM or b.xmax < a.xmin - FUZZY_MM
        or a.ymax < b.ymin - FUZZY_MM or b.ymax < a.ymin - FUZZY_MM
        or a.zmax < b.zmin - FUZZY_MM or b.zmax < a.zmin - FUZZY_MM
    )


def _state_applies(record: dict[str, Any], state: str) -> bool:
    token = str(record.get("state", state)).upper().strip()
    return token in {state, "ALL"}


def _matches(record: dict[str, Any], a: dict[str, Any], b: dict[str, Any]) -> bool:
    endpoints = {record.get("occurrence_a"), record.get("occurrence_b")}
    if endpoints != {a["occurrence_id"], b["occurrence_id"]}:
        return False
    ra = record.get("solid_index_a")
    rb = record.get("solid_index_b")
    if ra is None and rb is None:
        return True
    direct = (
        record.get("occurrence_a") == a["occurrence_id"]
        and int(ra) == a["solid_index"] and int(rb) == b["solid_index"]
    )
    reverse = (
        record.get("occurrence_a") == b["occurrence_id"]
        and int(ra) == b["solid_index"] and int(rb) == a["solid_index"]
    )
    return direct or reverse


def audit(state: str) -> dict[str, Any]:
    started = time.monotonic()
    builder = build_r2.build_state(state)
    records: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for occurrence_id in sorted(builder.global_shapes):
        for solid_index, solid in enumerate(builder.global_shapes[occurrence_id].Solids(), 1):
            volume = _signed_volume(solid.wrapped)
            valid = bool(BRepCheck_Analyzer(solid.wrapped, True).IsValid())
            row = {
                "occurrence_id": occurrence_id,
                "solid_index": solid_index,
                "solid": solid,
                "bbox": solid.BoundingBox(),
                "signed_volume_mm3": volume,
            }
            records.append(row)
            if not valid or not math.isfinite(volume) or volume <= 0.0:
                invalid.append({
                    "occurrence_id": occurrence_id,
                    "solid_index": solid_index,
                    "brepcheck_valid": valid,
                    "signed_volume_mm3": volume,
                })

    fits = [dict(row) for row in builder.intentional_fits if _state_applies(row, state)]
    fit_errors: list[str] = []
    seen_ids: set[str] = set()
    for row in fits:
        fit_id = str(row.get("exception_id", "")).strip()
        if not fit_id or fit_id in seen_ids:
            fit_errors.append(f"blank or duplicate exception id: {fit_id!r}")
        seen_ids.add(fit_id)
        try:
            lower = float(row["minimum_common_volume_mm3"])
            upper = float(row["maximum_common_volume_mm3"])
            if not (math.isfinite(lower) and math.isfinite(upper) and 0.0 <= lower <= upper):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            fit_errors.append(f"invalid finite bounds: {fit_id!r}")
        if not str(row.get("process_basis", "")).strip():
            fit_errors.append(f"missing process basis: {fit_id!r}")

    positives: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    used: set[str] = set()
    broadphase = 0
    for index, a in enumerate(records):
        for b in records[index + 1:]:
            if a["occurrence_id"] == b["occurrence_id"] or not _boxes_overlap(a["bbox"], b["bbox"]):
                continue
            broadphase += 1
            if any(
                item["occurrence_id"] == a["occurrence_id"] and item["solid_index"] == a["solid_index"]
                for item in invalid
            ) or any(
                item["occurrence_id"] == b["occurrence_id"] and item["solid_index"] == b["solid_index"]
                for item in invalid
            ):
                blocked.append({
                    "occurrence_a": a["occurrence_id"], "solid_index_a": a["solid_index"],
                    "occurrence_b": b["occurrence_id"], "solid_index_b": b["solid_index"],
                    "status": "BLOCKED_INVALID_OPERAND",
                })
                continue
            try:
                operation = BRepAlgoAPI_Common(a["solid"].wrapped, b["solid"].wrapped)
                operation.SetRunParallel(False)
                operation.SetFuzzyValue(FUZZY_MM)
                operation.Build()
                if not operation.IsDone():
                    raise RuntimeError("BRepAlgoAPI_Common not done")
                common = abs(_signed_volume(operation.Shape()))
                if common > min(a["signed_volume_mm3"], b["signed_volume_mm3"]) + 1.0e-5:
                    raise RuntimeError("nonphysical common volume exceeds smaller operand")
            except Exception as exc:
                blocked.append({
                    "occurrence_a": a["occurrence_id"], "solid_index_a": a["solid_index"],
                    "occurrence_b": b["occurrence_id"], "solid_index_b": b["solid_index"],
                    "status": "BLOCKED_BOOLEAN", "error": str(exc),
                })
                continue
            if common <= POSITIVE_MM3:
                continue
            matching = [row for row in fits if _matches(row, a, b)]
            accepted: list[str] = []
            for row in matching:
                lower = float(row["minimum_common_volume_mm3"])
                upper = float(row["maximum_common_volume_mm3"])
                if lower - POSITIVE_MM3 <= common <= upper + POSITIVE_MM3:
                    accepted.append(str(row["exception_id"]))
            if len(accepted) == 1:
                used.add(accepted[0])
            positives.append({
                "occurrence_a": a["occurrence_id"], "solid_index_a": a["solid_index"],
                "occurrence_b": b["occurrence_id"], "solid_index_b": b["solid_index"],
                "common_volume_mm3": common,
                "matching_exception_ids": [str(row.get("exception_id", "")) for row in matching],
                "accepted_exception_ids": accepted,
                "documented": len(accepted) == 1,
            })

    positives.sort(key=lambda row: row["common_volume_mm3"], reverse=True)
    unauthorized = [row for row in positives if not row["documented"]]
    files = (build_r2.SOURCE_DIR / "build_r2.py", build_r2.SOURCE_DIR / "r2_geometry.py")
    return {
        "state": state,
        "method": "Per-constituent-solid BRepAlgoAPI_Common; no occurrence-compound Boolean",
        "source_files_sha256_at_import": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files
        },
        "summary": {
            "occurrences": len(builder.global_shapes),
            "solid_records": len(records),
            "expected_solid_pairs": len(records) * (len(records) - 1) // 2,
            "broadphase_solid_pairs": broadphase,
            "invalid_solid_records": len(invalid),
            "positive_solid_pairs": len(positives),
            "documented_positive_solid_pairs": len(positives) - len(unauthorized),
            "unauthorized_positive_solid_pairs": len(unauthorized),
            "blocked_solid_pairs": len(blocked),
            "register_error_count": len(fit_errors),
            "unused_valid_exception_count": len(set(seen_ids) - used),
            "elapsed_seconds": time.monotonic() - started,
        },
        "invalid_solid_records": invalid,
        "all_positive_solid_pairs": positives,
        "unauthorized_positive_solid_pairs": unauthorized,
        "blocked_solid_pairs": blocked,
        "intentional_fit_register_errors": fit_errors,
        "used_intentional_fit_exception_ids": sorted(used),
        "unused_valid_intentional_fit_exception_ids": sorted(set(seen_ids) - used),
    }


def main() -> None:
    state = sys.argv[1].upper() if len(sys.argv) > 1 else "STOWED"
    if state not in {"STOWED", "DEPLOYED"}:
        raise SystemExit("state must be STOWED or DEPLOYED")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        build_r2.ANALYSIS_DIR / f"per_solid_authoring_audit_{state.lower()}.json"
    )
    result = audit(state)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
