#!/usr/bin/env python3
"""Create an occurrence-level source-versus-clean-XCAF-reimport comparison.

The authoring inventories are frozen by ``build_r2.py`` before the AP242 masters
are closed.  ``validate_r2.py`` then opens those masters in an independent
process and records the reimported XCAF occurrence/shape properties.  This tool
joins the two data sets by stable occurrence ID and records every measured delta
used by the comparison gate.  It intentionally does not claim Creo coverage.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "work" / "r2_analysis"
VALIDATION = ANALYSIS / "validation"

TRANSFORM_TOL = 1.0e-9
BBOX_TOL_MM = 1.0e-6
VOLUME_ABS_TOL_MM3 = 1.0e-5
VOLUME_REL_TOL = 1.0e-9


def _matrix(value: object) -> list[list[float]]:
    if isinstance(value, str):
        value = json.loads(value)
    return [[float(number) for number in row] for row in value]  # type: ignore[arg-type]


def _bbox(value: object) -> dict[str, float]:
    if isinstance(value, str):
        value = json.loads(value)
    return {str(key): float(number) for key, number in dict(value).items()}  # type: ignore[arg-type]


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _maximum_matrix_delta(left: list[list[float]], right: list[list[float]]) -> float:
    return max(abs(left[row][column] - right[row][column]) for row in range(3) for column in range(4))


def compare_state(state: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    state_lower = state.lower()
    source_path = ANALYSIS / f"authoring_inventory_{state_lower}.json"
    reimport_path = VALIDATION / f"xcaf_occurrences_{state_lower}.csv"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    with reimport_path.open(newline="", encoding="utf-8-sig") as stream:
        all_reimport_rows = list(csv.DictReader(stream))

    reimport_leaf_rows = [row for row in all_reimport_rows if _bool(row["is_leaf"]) and row["occurrence_id"]]
    by_occurrence: dict[str, list[dict[str, str]]] = {}
    for row in reimport_leaf_rows:
        by_occurrence.setdefault(row["occurrence_id"], []).append(row)

    parts = {part["part_number"]: part for part in source["parts"]}
    rows: list[dict[str, object]] = []
    source_ids: set[str] = set()
    for occurrence in source["occurrences"]:
        occurrence_id = occurrence["occurrence_id"]
        source_ids.add(occurrence_id)
        matches = by_occurrence.get(occurrence_id, [])
        part = parts[occurrence["part_number"]]
        if len(matches) != 1:
            rows.append({
                "state": state,
                "occurrence_id": occurrence_id,
                "part_number": occurrence["part_number"],
                "source_parent_path": occurrence["parent_path"],
                "reimport_path": "",
                "source_occurrence_count": 1,
                "reimport_occurrence_count": len(matches),
                "source_solid_count": part["solid_count"],
                "reimport_solid_count": "",
                "solid_count_delta": "",
                "source_face_count": part["face_count"],
                "reimport_face_count": "",
                "face_count_delta": "",
                "source_volume_mm3": occurrence["global_volume_mm3"],
                "reimport_volume_mm3": "",
                "volume_delta_mm3": "",
                "volume_relative_delta": "",
                "source_bbox_mm": json.dumps(occurrence["global_bbox_mm"], separators=(",", ":")),
                "reimport_bbox_mm": "",
                "bbox_max_abs_delta_mm": "",
                "source_transform_3x4": json.dumps(occurrence["transform_matrix_3x4"], separators=(",", ":")),
                "reimport_transform_3x4": "",
                "transform_max_abs_delta": "",
                "source_identity_transform": occurrence["identity_transform"],
                "reimport_identity_transform": "",
                "source_classification": occurrence["classification"],
                "reimport_classification": "",
                "reimport_valid": "",
                "comparison_status": "FAIL",
                "comparison_reason": f"Stable occurrence ID matched {len(matches)} reimport leaves; exactly one required",
            })
            continue

        reimport = matches[0]
        source_transform = _matrix(occurrence["transform_matrix_3x4"])
        reimport_transform = _matrix(reimport["local_transform_3x4"])
        transform_delta = _maximum_matrix_delta(source_transform, reimport_transform)
        source_bbox = _bbox(occurrence["global_bbox_mm"])
        reimport_bbox = _bbox(reimport["bbox_mm"])
        bbox_delta = max(abs(source_bbox[key] - reimport_bbox[key]) for key in source_bbox)
        source_volume = float(occurrence["global_volume_mm3"])
        reimport_volume = float(reimport["volume_mm3"])
        volume_delta = reimport_volume - source_volume
        volume_relative_delta = abs(volume_delta) / max(abs(source_volume), 1.0)
        source_solids = int(part["solid_count"])
        reimport_solids = int(reimport["solid_count"])
        source_faces = int(part["face_count"])
        reimport_faces = int(reimport["face_count"])
        volume_tolerance = max(VOLUME_ABS_TOL_MM3, abs(source_volume) * VOLUME_REL_TOL)

        checks = {
            "part_number": reimport["part_number"] == occurrence["part_number"],
            "classification": reimport["classification"] == occurrence["classification"],
            "valid": _bool(reimport["valid"]),
            "solid_count": source_solids == reimport_solids,
            "face_count": source_faces == reimport_faces,
            "identity_transform": _bool(reimport["local_transform_identity"]) == bool(occurrence["identity_transform"]),
            "transform": transform_delta <= TRANSFORM_TOL,
            "bbox": bbox_delta <= BBOX_TOL_MM,
            "volume": abs(volume_delta) <= volume_tolerance,
        }
        failed = [name for name, passed in checks.items() if not passed]
        rows.append({
            "state": state,
            "occurrence_id": occurrence_id,
            "part_number": occurrence["part_number"],
            "source_parent_path": occurrence["parent_path"],
            "reimport_path": reimport["path"],
            "source_occurrence_count": 1,
            "reimport_occurrence_count": 1,
            "source_solid_count": source_solids,
            "reimport_solid_count": reimport_solids,
            "solid_count_delta": reimport_solids - source_solids,
            "source_face_count": source_faces,
            "reimport_face_count": reimport_faces,
            "face_count_delta": reimport_faces - source_faces,
            "source_volume_mm3": f"{source_volume:.15g}",
            "reimport_volume_mm3": f"{reimport_volume:.15g}",
            "volume_delta_mm3": f"{volume_delta:.15g}",
            "volume_relative_delta": f"{volume_relative_delta:.15g}",
            "source_bbox_mm": json.dumps(source_bbox, separators=(",", ":")),
            "reimport_bbox_mm": json.dumps(reimport_bbox, separators=(",", ":")),
            "bbox_max_abs_delta_mm": f"{bbox_delta:.15g}",
            "source_transform_3x4": json.dumps(source_transform, separators=(",", ":")),
            "reimport_transform_3x4": json.dumps(reimport_transform, separators=(",", ":")),
            "transform_max_abs_delta": f"{transform_delta:.15g}",
            "source_identity_transform": bool(occurrence["identity_transform"]),
            "reimport_identity_transform": _bool(reimport["local_transform_identity"]),
            "source_classification": occurrence["classification"],
            "reimport_classification": reimport["classification"],
            "reimport_valid": _bool(reimport["valid"]),
            "comparison_status": "PASS" if not failed else "FAIL",
            "comparison_reason": "All measured properties within tolerance" if not failed else "; ".join(failed),
        })

    extra_ids = sorted(set(by_occurrence) - source_ids)
    for occurrence_id in extra_ids:
        for reimport in by_occurrence[occurrence_id]:
            rows.append({
                "state": state,
                "occurrence_id": occurrence_id,
                "part_number": reimport["part_number"],
                "source_parent_path": "",
                "reimport_path": reimport["path"],
                "source_occurrence_count": 0,
                "reimport_occurrence_count": 1,
                "comparison_status": "FAIL",
                "comparison_reason": "Reimport leaf has no stable occurrence ID in frozen authoring inventory",
            })

    pass_count = sum(row["comparison_status"] == "PASS" for row in rows)
    fail_count = len(rows) - pass_count
    summary = {
        "state": state,
        "source_inventory": source_path.name,
        "clean_reimport_inventory": reimport_path.name,
        "source_occurrence_count": len(source["occurrences"]),
        "reimport_leaf_occurrence_count": len(reimport_leaf_rows),
        "comparison_row_count": len(rows),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "status": "PASS" if fail_count == 0 else "FAIL",
    }
    return rows, summary


def main() -> None:
    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for state in ("STOWED", "DEPLOYED"):
        state_rows, summary = compare_state(state)
        rows.extend(state_rows)
        summaries.append(summary)

    columns = [
        "state", "occurrence_id", "part_number", "source_parent_path", "reimport_path",
        "source_occurrence_count", "reimport_occurrence_count", "source_solid_count",
        "reimport_solid_count", "solid_count_delta", "source_face_count", "reimport_face_count",
        "face_count_delta", "source_volume_mm3", "reimport_volume_mm3", "volume_delta_mm3",
        "volume_relative_delta", "source_bbox_mm", "reimport_bbox_mm", "bbox_max_abs_delta_mm",
        "source_transform_3x4", "reimport_transform_3x4", "transform_max_abs_delta",
        "source_identity_transform", "reimport_identity_transform", "source_classification",
        "reimport_classification", "reimport_valid", "comparison_status", "comparison_reason",
    ]
    output_csv = VALIDATION / "source_vs_reimport.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    overall_fail = sum(int(item["fail_count"]) for item in summaries)
    output_json = VALIDATION / "source_vs_reimport_summary.json"
    output_json.write_text(json.dumps({
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "comparison_scope": "Frozen scripted-B-rep authoring inventory versus independent clean-process AP242 XCAF reimport",
        "explicit_limit": "This comparison is not Creo validation.",
        "tolerances": {
            "transform_max_abs": TRANSFORM_TOL,
            "bbox_max_abs_mm": BBOX_TOL_MM,
            "volume_abs_mm3": VOLUME_ABS_TOL_MM3,
            "volume_relative": VOLUME_REL_TOL,
            "solid_count_delta": 0,
            "face_count_delta": 0,
        },
        "states": summaries,
        "overall_status": "PASS" if overall_fail == 0 else "FAIL",
        "overall_fail_count": overall_fail,
        "raw_evidence": output_csv.name,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output_json.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
