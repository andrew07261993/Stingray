#!/usr/bin/env python3
"""Consolidate the preserved five-angle exact Boolean pair register."""

from __future__ import annotations

import collections
import csv
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "forward_arm_repack" / "five_angle_boolean_gate_exact"
PAIR_PATH = OUT / "five_angle_exact_boolean_pairs.csv.gz"
ANGLES = [0, 20, 40, 55, 80]
EPSILON_MM3 = 1.0e-7


def group_rows(rows: list[dict[str, str]]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str, str], list[dict]] = collections.defaultdict(list)
    for row in rows:
        key = (
            row["occurrence_a"], row["solid_index_a"], row["occurrence_b"],
            row["solid_index_b"], row["intentional_fit_exception_id"],
        )
        grouped[key].append({
            "angle_deg": int(row["angle_deg"]),
            "common_volume_mm3": float(row["common_volume_mm3"]),
        })
    return [{
        "occurrence_a": key[0], "solid_index_a": int(key[1]),
        "occurrence_b": key[2], "solid_index_b": int(key[3]),
        "intentional_fit_exception_id": key[4] or None,
        "samples": sorted(samples, key=lambda sample: sample["angle_deg"]),
    } for key, samples in sorted(grouped.items())]


with gzip.open(PAIR_PATH, "rt", newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))

coverage = collections.Counter(int(row["angle_deg"]) for row in rows)
if sorted(coverage) != ANGLES or len(set(coverage.values())) != 1:
    raise RuntimeError(f"Incomplete or nonuniform five-angle coverage: {dict(coverage)}")

positive = [row for row in rows if float(row["common_volume_mm3"] or 0.0) > EPSILON_MM3]
authorized = [row for row in positive if row["result"] == "DOCUMENTED_POSITIVE_VOLUME"]
unauthorized = [row for row in positive if row["result"] == "UNAUTHORIZED_POSITIVE_VOLUME"]
blocked = [row for row in rows if row["result"] == "BLOCKED_BOOLEAN"]

with (OUT / "positive_common_volume_pairs.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(positive)

per_angle = {}
for angle in ANGLES:
    angle_rows = [row for row in rows if int(row["angle_deg"]) == angle]
    per_angle[str(angle)] = {
        "pair_row_count": len(angle_rows),
        "authorized_positive_volume_pair_count": sum(
            row["result"] == "DOCUMENTED_POSITIVE_VOLUME" for row in angle_rows
        ),
        "unauthorized_positive_volume_pair_count": sum(
            row["result"] == "UNAUTHORIZED_POSITIVE_VOLUME" for row in angle_rows
        ),
        "boolean_blocked_pair_count": sum(row["result"] == "BLOCKED_BOOLEAN" for row in angle_rows),
    }

summary = {
    "gate": "FORWARD-ARM FIVE-ANGLE EXACT BOOLEAN GATE",
    "angles_deg": ANGLES,
    "geometry_modified": False,
    "common_volume_epsilon_mm3": EPSILON_MM3,
    "pair_row_count": len(rows),
    "per_angle": per_angle,
    "authorized_positive_volume_pair_count": len(authorized),
    "authorized_unique_pair_count": len(group_rows(authorized)),
    "authorized_positive_contact_pairs": group_rows(authorized),
    "unauthorized_positive_volume_pair_count": len(unauthorized),
    "unauthorized_unique_pair_count": len(group_rows(unauthorized)),
    "unauthorized_positive_pairs": group_rows(unauthorized),
    "boolean_blocked_pair_count": len(blocked),
    "disposition": "PASS" if not unauthorized and not blocked else "FAIL",
    "correction_disposition": (
        "NOT LOCAL; BROAD PACKAGING INTERFERENCE SET; NO CORRECTION AUTHORIZED"
        if unauthorized else "NOT REQUIRED"
    ),
}
(OUT / "five_angle_exact_boolean_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    "disposition": summary["disposition"],
    "per_angle": per_angle,
    "authorized_positive_volume_pair_count": len(authorized),
    "unauthorized_positive_volume_pair_count": len(unauthorized),
    "unauthorized_unique_pair_count": summary["unauthorized_unique_pair_count"],
    "boolean_blocked_pair_count": len(blocked),
}, indent=2))
