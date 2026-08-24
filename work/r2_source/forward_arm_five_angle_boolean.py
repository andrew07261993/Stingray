#!/usr/bin/env python3
"""Run only the authorized forward-arm five-angle exact Boolean gate."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import json
import multiprocessing
import shutil
import tempfile
import time
from pathlib import Path

import validate_r2


ANGLES = [0, 20, 40, 55, 80]
ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "work" / "final_release"
ANALYSIS = ROOT / "work" / "final_analysis"
OUT = ROOT / "work" / "forward_arm_repack" / "five_angle_boolean_gate_pass2"


def merge_csv_gz(shards: list[dict], destination: Path) -> int:
    fieldnames = None
    count = 0
    with gzip.open(destination, "wt", newline="", encoding="utf-8", compresslevel=6) as stream:
        writer = None
        for shard in shards:
            with gzip.open(shard["pair_path"], "rt", newline="", encoding="utf-8") as source:
                reader = csv.DictReader(source)
                fields = list(reader.fieldnames or [])
                if fieldnames is None:
                    fieldnames = fields
                    writer = csv.DictWriter(stream, fieldnames=fieldnames)
                    writer.writeheader()
                elif fields != fieldnames:
                    raise RuntimeError(f"Angle {shard['angle']} pair schema mismatch")
                for row in reader:
                    if int(row["angle_deg"]) != shard["angle"]:
                        raise RuntimeError(f"Angle {shard['angle']} contains an out-of-angle row")
                    writer.writerow(row)
                    count += 1
    return count


def merge_kinematics(shards: list[dict], destination: Path) -> None:
    rows = []
    fieldnames = None
    for shard in shards:
        with Path(shard["kinematics_path"]).open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            fields = list(reader.fieldnames or [])
            values = list(reader)
        if len(values) != 1 or int(float(values[0]["arm_angle_deg"])) != shard["angle"]:
            raise RuntimeError(f"Angle {shard['angle']} kinematics identity mismatch")
        if fieldnames is None:
            fieldnames = fields
        elif fields != fieldnames:
            raise RuntimeError(f"Angle {shard['angle']} kinematics schema mismatch")
        rows.extend(values)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 5:
        raise ValueError("workers must be 1..5")
    if OUT.exists():
        raise RuntimeError(f"Output already exists; preserve or remove explicitly: {OUT}")

    files = {
        state: RELEASE / f"STINGRAY_I5S_DF8_FINAL_{state}_MASTER_AP242.step"
        for state in ("STOWED", "DEPLOYED")
    }
    inventories = {
        state: ANALYSIS / f"authoring_inventory_{state.lower()}.json"
        for state in ("STOWED", "DEPLOYED")
    }
    hashes = {
        **{f"STEP:{state}": validate_r2.sha256(path) for state, path in files.items()},
        **{f"INVENTORY:{state}": validate_r2.sha256(path) for state, path in inventories.items()},
    }
    started = time.time()
    OUT.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="forward_arm_five_angle_") as temporary:
        tasks = [(angle, str(Path(temporary) / f"angle_{angle:02d}")) for angle in ANGLES]
        context = multiprocessing.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers,
            mp_context=context,
            initializer=validate_r2._initialize_motion_worker,
            initargs=(
                {state: str(path.resolve()) for state, path in files.items()},
                {state: str(path.resolve()) for state, path in inventories.items()},
                hashes,
            ),
        ) as executor:
            shards = list(executor.map(validate_r2._run_motion_boolean_angle_task, tasks, chunksize=1))
        shards.sort(key=lambda row: row["angle"])
        if [row["angle"] for row in shards] != ANGLES:
            raise RuntimeError("Five-angle coverage mismatch")
        for shard in shards:
            if validate_r2.sha256(Path(shard["pair_path"])) != shard["pair_sha256"]:
                raise RuntimeError(f"Angle {shard['angle']} pair shard hash mismatch")
            if validate_r2.sha256(Path(shard["kinematics_path"])) != shard["kinematics_sha256"]:
                raise RuntimeError(f"Angle {shard['angle']} kinematics shard hash mismatch")
        pair_path = OUT / "five_angle_exact_boolean_pairs.csv.gz"
        pair_count = merge_csv_gz(shards, pair_path)
        merge_kinematics(shards, OUT / "five_angle_kinematics.csv")

        positive_rows = []
        with gzip.open(pair_path, "rt", newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                common = float(row["common_volume_mm3"] or 0.0)
                if common > validate_r2.COMMON_VOLUME_EPS_MM3:
                    positive_rows.append(row)

        per_angle = {}
        for shard in shards:
            summary = shard["summary"]
            per_angle[str(shard["angle"])] = {
                "pair_row_count": summary["pair_row_count"],
                "broadphase_candidate_count": summary["broadphase_candidate_count"],
                "authorized_positive_volume_pair_count": summary["documented_positive_volume_pair_count"],
                "unauthorized_positive_volume_pair_count": summary["unauthorized_positive_volume_pair_count"],
                "boolean_blocked_pair_count": summary["boolean_blocked_pair_count"],
                "distance_blocked_pair_count": summary["distance_blocked_pair_count"],
                "track_validation_error_count": summary["track_validation_error_count"],
                "elapsed_seconds": summary["elapsed_seconds"],
            }
        authorized = [row for row in positive_rows if row["result"] == "DOCUMENTED_POSITIVE_VOLUME"]
        unauthorized = [row for row in positive_rows if row["result"] == "UNAUTHORIZED_POSITIVE_VOLUME"]
        summary = {
            "gate": "FORWARD-ARM FIVE-ANGLE EXACT BOOLEAN GATE",
            "angles_deg": ANGLES,
            "input_sha256": hashes,
            "geometry_modified": False,
            "common_volume_epsilon_mm3": validate_r2.COMMON_VOLUME_EPS_MM3,
            "pair_row_count": pair_count,
            "authorized_positive_contact_pairs": authorized,
            "unauthorized_positive_pairs": unauthorized,
            "per_angle": per_angle,
            "boolean_blocked_pair_count": sum(v["boolean_blocked_pair_count"] for v in per_angle.values()),
            "track_validation_error_count": sum(v["track_validation_error_count"] for v in per_angle.values()),
            "disposition": "PASS" if not unauthorized and all(
                v["boolean_blocked_pair_count"] == 0 and v["track_validation_error_count"] == 0
                for v in per_angle.values()
            ) else "FAIL_OR_BLOCKED",
            "elapsed_seconds": time.time() - started,
        }
        (OUT / "five_angle_exact_boolean_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        with (OUT / "positive_common_volume_pairs.csv").open("w", newline="", encoding="utf-8") as stream:
            fields = list(positive_rows[0]) if positive_rows else [
                "angle_deg", "occurrence_a", "solid_index_a", "occurrence_b",
                "solid_index_b", "common_volume_mm3", "result", "intentional_fit_exception_id",
            ]
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(positive_rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
