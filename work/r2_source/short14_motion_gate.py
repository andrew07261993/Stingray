#!/usr/bin/env python3
"""Bounded exact-Boolean five-angle and full 0..80 SHORT14 motion gates."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import json
import multiprocessing
import tempfile
import time
from collections import Counter
from pathlib import Path

import short14_external_buoy_build as build_short
import short14_external_buoy_config as cfg
import validate_r2


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "short14_external_buoy"
FILES = {"STOWED": SOURCE / build_short.STOWED_FILE, "DEPLOYED": SOURCE / build_short.DEPLOYED_FILE}
INVENTORIES = {state: SOURCE / f"authoring_inventory_{state.lower()}.json" for state in ("STOWED", "DEPLOYED")}


def _initialize_short_worker(file_paths: dict[str, str], inventory_paths: dict[str, str], hashes: dict[str, str]) -> None:
    validate_r2.PIVOT_Z_MM = cfg.ARM_PIVOT_Z_MM
    validate_r2.ARM_LENGTH_MM = cfg.ARM_LENGTH_MM
    validate_r2._initialize_motion_worker(file_paths, inventory_paths, hashes)


def _merge_pair_shards(shards: list[dict[str, object]], destination: Path) -> int:
    fields = None
    count = 0
    with gzip.open(destination, "wt", newline="", encoding="utf-8", compresslevel=6) as output:
        writer = None
        for shard in shards:
            expected_angles = {
                int(value) for value in shard.get("angles", [shard.get("angle")])
            }
            with gzip.open(str(shard["pair_path"]), "rt", newline="", encoding="utf-8") as source:
                reader = csv.DictReader(source)
                current = list(reader.fieldnames or [])
                if fields is None:
                    fields = current
                    writer = csv.DictWriter(output, fieldnames=fields)
                    writer.writeheader()
                elif current != fields:
                    raise RuntimeError("motion pair shard schema mismatch")
                for row in reader:
                    if int(row["angle_deg"]) not in expected_angles:
                        raise RuntimeError("motion pair shard angle mismatch")
                    writer.writerow(row)
                    count += 1
    return count


def _merge_kinematics(shards: list[dict[str, object]], destination: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    fields = None
    for shard in shards:
        with Path(str(shard["kinematics_path"])).open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            current = list(reader.fieldnames or [])
            values = list(reader)
        expected_angles = [
            int(value) for value in shard.get("angles", [shard.get("angle")])
        ]
        actual_angles = [int(float(value["arm_angle_deg"])) for value in values]
        if actual_angles != expected_angles:
            raise RuntimeError("motion kinematics shard identity mismatch")
        if fields is None:
            fields = current
        elif fields != current:
            raise RuntimeError("motion kinematics shard schema mismatch")
        rows.extend(values)
    with destination.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    return rows


def _run_motion_boolean_batch_task(task: tuple[list[int], str]) -> dict[str, object]:
    """Audit one contiguous optimized angle batch in an initialized worker."""
    angles, output_directory = task
    if validate_r2._MOTION_WORKER_ENDPOINTS is None or validate_r2._MOTION_WORKER_INVENTORIES is None:
        raise RuntimeError("Motion worker context was not initialized")
    angle_dir = Path(output_directory)
    angle_dir.mkdir(parents=True, exist_ok=False)
    summary = validate_r2._motion_angle_audit(
        validate_r2._MOTION_WORKER_ENDPOINTS,
        validate_r2._MOTION_WORKER_INVENTORIES,
        angle_dir, angles, exact_common_only=True,
    )
    pair_path = angle_dir / "motion_full_mechanism_audit.csv.gz"
    kinematics_path = angle_dir / "motion_kinematics_1deg.csv"
    if not pair_path.is_file() or not kinematics_path.is_file():
        raise RuntimeError(f"Motion batch {angles[0]}..{angles[-1]} did not materialize both evidence shards")
    return {
        "angles": angles,
        "context_fingerprint": validate_r2._MOTION_WORKER_CONTEXT_FINGERPRINT,
        "summary": summary,
        "pair_path": str(pair_path), "pair_sha256": validate_r2.sha256(pair_path),
        "kinematics_path": str(kinematics_path), "kinematics_sha256": validate_r2.sha256(kinematics_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("five", "full"), required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        raise ValueError("SHORT14 governance permits at most two independent workers")
    angles = list(cfg.MOTION_ANGLES_FIVE if args.mode == "five" else cfg.MOTION_ANGLES_FULL)
    if args.mode == "five":
        first_attempt = SOURCE / "validation" / "five_angle_gate"
        directory_name = "five_angle_gate_attempt_2" if first_attempt.exists() else "five_angle_gate"
    else:
        directory_name = "full_motion_sweep_1"
    out = SOURCE / "validation" / directory_name
    if out.exists():
        raise RuntimeError(f"bounded gate output already exists: {out}")
    out.mkdir(parents=True)
    file_paths = {state: str(path.resolve()) for state, path in FILES.items()}
    inventory_paths = {state: str(path.resolve()) for state, path in INVENTORIES.items()}
    hashes = {
        **{f"STEP:{state}": validate_r2.sha256(path) for state, path in FILES.items()},
        **{f"INVENTORY:{state}": validate_r2.sha256(path) for state, path in INVENTORIES.items()},
    }
    started = time.time()
    with tempfile.TemporaryDirectory(prefix=f"short14_{args.mode}_motion_") as temporary:
        if args.mode == "full":
            split = (len(angles) + 1) // 2
            angle_batches = (angles[:split], angles[split:])
            tasks = [
                (batch, str(Path(temporary) / f"angles_{batch[0]:02d}_{batch[-1]:02d}"))
                for batch in angle_batches
            ]
            worker_function = _run_motion_boolean_batch_task
        else:
            tasks = [(angle, str(Path(temporary) / f"angle_{angle:02d}")) for angle in angles]
            worker_function = validate_r2._run_motion_boolean_angle_task
        context = multiprocessing.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers, mp_context=context,
            initializer=_initialize_short_worker, initargs=(file_paths, inventory_paths, hashes),
        ) as executor:
            shards = list(executor.map(worker_function, tasks, chunksize=1))
        shards.sort(key=lambda row: int(row["angle"] if "angle" in row else row["angles"][0]))
        covered_angles = [
            int(value)
            for shard in shards
            for value in shard.get("angles", [shard.get("angle")])
        ]
        if covered_angles != angles:
            raise RuntimeError("motion angle coverage mismatch")
        for shard in shards:
            if validate_r2.sha256(Path(str(shard["pair_path"]))) != shard["pair_sha256"]:
                raise RuntimeError("motion pair shard hash mismatch")
            if validate_r2.sha256(Path(str(shard["kinematics_path"]))) != shard["kinematics_sha256"]:
                raise RuntimeError("motion kinematics shard hash mismatch")
        pair_file = out / f"{args.mode}_motion_exact_boolean_pairs.csv.gz"
        pair_count = _merge_pair_shards(shards, pair_file)
        kinematics = _merge_kinematics(shards, out / f"{args.mode}_motion_kinematics.csv")

        unauthorized_rows = []
        documented_rows = []
        angle_counts: dict[int, Counter[str]] = {angle: Counter() for angle in angles}
        with gzip.open(pair_file, "rt", newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                counts = angle_counts[int(row["angle_deg"])]
                counts["pairs"] += 1
                if row["aabb_overlap"].strip().lower() == "true":
                    counts["broadphase"] += 1
                if row["result"] == "UNAUTHORIZED_POSITIVE_VOLUME":
                    unauthorized_rows.append(row); counts["unauthorized"] += 1
                elif row["result"] == "DOCUMENTED_POSITIVE_VOLUME":
                    documented_rows.append(row); counts["documented"] += 1
                elif row["result"] == "BLOCKED_BOOLEAN":
                    counts["blocked"] += 1
        per_angle = {
            str(angle): {
                "pair_row_count": angle_counts[angle]["pairs"],
                "broadphase_candidate_count": angle_counts[angle]["broadphase"],
                "unauthorized_positive_volume_pair_count": angle_counts[angle]["unauthorized"],
                "documented_positive_volume_pair_count": angle_counts[angle]["documented"],
                "boolean_blocked_pair_count": angle_counts[angle]["blocked"],
                "track_validation_error_count": 0,
                "intentional_fit_register_error_count": 0,
                "elapsed_seconds": None,
            }
            for angle in angles
        }
        track_errors = sorted({
            error for shard in shards for error in shard["summary"]["track_validation_errors"]
        })
        intentional_fit_errors = {
            json.dumps(error, sort_keys=True)
            for shard in shards
            for error in shard["summary"]["intentional_fit_register_errors"]
        }
        summary = {
            "gate": "SHORT14 FIVE-ANGLE EXACT BOOLEAN GATE" if args.mode == "five" else "SHORT14 FULL 0..80 ONE-DEGREE EXACT BOOLEAN SWEEP 1",
            "angles_deg": angles,
            "worker_count": args.workers,
            "input_sha256": hashes,
            "geometry_modified": False,
            "common_volume_epsilon_mm3": validate_r2.COMMON_VOLUME_EPS_MM3,
            "pair_register": str(pair_file),
            "kinematics_register": str(out / f"{args.mode}_motion_kinematics.csv"),
            "pair_row_count": pair_count,
            "unauthorized_positive_volume_pair_count": len(unauthorized_rows),
            "documented_positive_volume_pair_count": len(documented_rows),
            "boolean_blocked_pair_count": sum(value["boolean_blocked_pair_count"] for value in per_angle.values()),
            "track_validation_error_count": len(track_errors),
            "track_validation_errors": track_errors,
            "intentional_fit_register_error_count": len(intentional_fit_errors),
            "per_angle": per_angle,
            "crosshead_travel_0_to_80_mm": float(kinematics[-1]["crosshead_travel_mm"]) - float(kinematics[0]["crosshead_travel_mm"]),
            "maximum_closure_residual_abs_mm": max(abs(float(row["closure_residual_mm"])) for row in kinematics),
            "elapsed_seconds": time.time() - started,
        }
        summary["disposition"] = "PASS" if (
            summary["unauthorized_positive_volume_pair_count"] == 0
            and summary["boolean_blocked_pair_count"] == 0
            and summary["track_validation_error_count"] == 0
            and summary["intentional_fit_register_error_count"] == 0
        ) else "FAIL_OR_BLOCKED"
        summary_path = out / ("five_angle_exact_boolean_summary.json" if args.mode == "five" else "full_motion_exact_boolean_summary.json")
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: summary[key] for key in (
            "gate", "pair_row_count", "unauthorized_positive_volume_pair_count",
            "documented_positive_volume_pair_count", "boolean_blocked_pair_count",
            "track_validation_error_count", "intentional_fit_register_error_count",
            "crosshead_travel_0_to_80_mm", "maximum_closure_residual_abs_mm",
            "elapsed_seconds", "disposition",
        )}, indent=2))


if __name__ == "__main__":
    main()
