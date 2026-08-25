#!/usr/bin/env python3
"""Run the single SHORT14 0..80 exact-Boolean sweep in two bounded stages."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import json
import multiprocessing
import time
from collections import Counter
from pathlib import Path

import short14_motion_gate as gate
import validate_r2


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "short14_external_buoy"
OUT = SOURCE / "validation" / "full_motion_sweep_1"
SHARDS = OUT / "shards"


def _inputs() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    files = {state: str(path.resolve()) for state, path in gate.FILES.items()}
    inventories = {state: str(path.resolve()) for state, path in gate.INVENTORIES.items()}
    hashes = {
        **{f"STEP:{state}": validate_r2.sha256(path) for state, path in gate.FILES.items()},
        **{f"INVENTORY:{state}": validate_r2.sha256(path) for state, path in gate.INVENTORIES.items()},
    }
    return files, inventories, hashes


def _manifest_path(angles: list[int]) -> Path:
    return OUT / f"shard_manifest_{angles[0]:02d}_{angles[-1]:02d}.json"


def _run_stage(stage: int) -> None:
    if stage not in (1, 2):
        raise ValueError(stage)
    OUT.mkdir(parents=True, exist_ok=True)
    SHARDS.mkdir(parents=True, exist_ok=True)
    if (OUT / "full_motion_exact_boolean_summary.json").exists():
        raise RuntimeError("full motion sweep 1 is already complete")
    batches = (
        ([*range(0, 21)], [*range(21, 41)])
        if stage == 1 else
        ([*range(41, 61)], [*range(61, 81)])
    )
    for batch in batches:
        if _manifest_path(batch).exists() or (SHARDS / f"angles_{batch[0]:02d}_{batch[-1]:02d}").exists():
            raise RuntimeError(f"stage {stage} batch already exists: {batch[0]}..{batch[-1]}")
    files, inventories, hashes = _inputs()
    if stage == 2:
        marker = OUT / "stage_1_complete.json"
        if not marker.exists():
            raise RuntimeError("stage 1 completion marker is required before stage 2")
        prior = json.loads(marker.read_text(encoding="utf-8"))
        if prior.get("input_sha256") != hashes:
            raise RuntimeError("stage 1 input hashes do not match current AP242/inventory inputs")
    started = time.time()
    tasks = [
        (batch, str(SHARDS / f"angles_{batch[0]:02d}_{batch[-1]:02d}"))
        for batch in batches
    ]
    context = multiprocessing.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=2, mp_context=context,
        initializer=gate._initialize_short_worker,
        initargs=(files, inventories, hashes),
    ) as executor:
        results = list(executor.map(gate._run_motion_boolean_batch_task, tasks, chunksize=1))
    results.sort(key=lambda row: int(row["angles"][0]))
    for result in results:
        pair_path = Path(str(result["pair_path"])); kin_path = Path(str(result["kinematics_path"]))
        if validate_r2.sha256(pair_path) != result["pair_sha256"]:
            raise RuntimeError("pair shard hash changed before checkpoint")
        if validate_r2.sha256(kin_path) != result["kinematics_sha256"]:
            raise RuntimeError("kinematics shard hash changed before checkpoint")
        manifest = {**result, "input_sha256": hashes}
        _manifest_path([int(value) for value in result["angles"]]).write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
        )
    elapsed = time.time() - started
    marker = {
        "stage": stage, "angles_deg": [value for batch in batches for value in batch],
        "worker_count": 2, "input_sha256": hashes, "elapsed_seconds": elapsed,
        "disposition": "STAGE_PASS",
    }
    (OUT / f"stage_{stage}_complete.json").write_text(
        json.dumps(marker, indent=2) + "\n", encoding="utf-8",
    )
    if stage == 1:
        print(json.dumps(marker, indent=2))
        return
    _merge_complete(hashes, elapsed)


def _merge_complete(hashes: dict[str, str], stage_2_elapsed: float) -> None:
    manifests = []
    for first, last in ((0, 20), (21, 40), (41, 60), (61, 80)):
        path = OUT / f"shard_manifest_{first:02d}_{last:02d}.json"
        if not path.exists():
            raise RuntimeError(f"missing full-sweep shard manifest: {path.name}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("input_sha256") != hashes:
            raise RuntimeError(f"input hash mismatch in {path.name}")
        manifests.append(value)
    covered = [int(angle) for manifest in manifests for angle in manifest["angles"]]
    if covered != list(range(81)):
        raise RuntimeError(f"full-sweep staged angle coverage mismatch: {covered}")
    pair_file = OUT / "full_motion_exact_boolean_pairs.csv.gz"
    pair_count = gate._merge_pair_shards(manifests, pair_file)
    kinematics = gate._merge_kinematics(manifests, OUT / "full_motion_kinematics.csv")
    counts = {angle: Counter() for angle in range(81)}
    unauthorized = documented = blocked = 0
    with gzip.open(pair_file, "rt", newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            counter = counts[int(row["angle_deg"])]
            counter["pairs"] += 1
            if row["aabb_overlap"].strip().lower() == "true":
                counter["broadphase"] += 1
            if row["result"] == "UNAUTHORIZED_POSITIVE_VOLUME":
                unauthorized += 1; counter["unauthorized"] += 1
            elif row["result"] == "DOCUMENTED_POSITIVE_VOLUME":
                documented += 1; counter["documented"] += 1
            elif row["result"] == "BLOCKED_BOOLEAN":
                blocked += 1; counter["blocked"] += 1
    track_errors = sorted({
        error for manifest in manifests for error in manifest["summary"]["track_validation_errors"]
    })
    fit_errors = {
        json.dumps(error, sort_keys=True)
        for manifest in manifests
        for error in manifest["summary"]["intentional_fit_register_errors"]
    }
    stage_1 = json.loads((OUT / "stage_1_complete.json").read_text(encoding="utf-8"))
    summary = {
        "gate": "SHORT14 FULL 0..80 ONE-DEGREE EXACT BOOLEAN SWEEP 1",
        "angles_deg": list(range(81)), "angle_increment_deg": 1,
        "execution_topology": {
            "mode": "TWO_BOUNDED_STAGES_FOUR_CONTIGUOUS_HASHED_SHARDS",
            "stage_1_batches": ["0..20", "21..40"],
            "stage_2_batches": ["41..60", "61..80"],
            "workers_per_stage": 2, "complete_sweep_count": 1,
            "second_sweep_used": False,
        },
        "input_sha256": hashes, "geometry_modified": False,
        "common_volume_epsilon_mm3": validate_r2.COMMON_VOLUME_EPS_MM3,
        "pair_register": str(pair_file),
        "kinematics_register": str(OUT / "full_motion_kinematics.csv"),
        "pair_row_count": pair_count,
        "unauthorized_positive_volume_pair_count": unauthorized,
        "documented_positive_volume_pair_count": documented,
        "boolean_blocked_pair_count": blocked,
        "track_validation_error_count": len(track_errors),
        "track_validation_errors": track_errors,
        "intentional_fit_register_error_count": len(fit_errors),
        "crosshead_travel_0_to_80_mm": float(kinematics[-1]["crosshead_travel_mm"]) - float(kinematics[0]["crosshead_travel_mm"]),
        "maximum_closure_residual_abs_mm": max(abs(float(row["closure_residual_mm"])) for row in kinematics),
        "per_angle": {
            str(angle): {
                "pair_row_count": counts[angle]["pairs"],
                "broadphase_candidate_count": counts[angle]["broadphase"],
                "unauthorized_positive_volume_pair_count": counts[angle]["unauthorized"],
                "documented_positive_volume_pair_count": counts[angle]["documented"],
                "boolean_blocked_pair_count": counts[angle]["blocked"],
            } for angle in range(81)
        },
        "stage_elapsed_seconds": {
            "stage_1": float(stage_1["elapsed_seconds"]), "stage_2": stage_2_elapsed,
        },
        "elapsed_seconds": float(stage_1["elapsed_seconds"]) + stage_2_elapsed,
    }
    summary["disposition"] = "PASS" if (
        unauthorized == 0 and blocked == 0 and not track_errors and not fit_errors
        and pair_count > 0 and len(kinematics) == 81
    ) else "FAIL_OR_BLOCKED"
    (OUT / "full_motion_exact_boolean_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({key: summary[key] for key in (
        "gate", "pair_row_count", "unauthorized_positive_volume_pair_count",
        "documented_positive_volume_pair_count", "boolean_blocked_pair_count",
        "track_validation_error_count", "intentional_fit_register_error_count",
        "crosshead_travel_0_to_80_mm", "maximum_closure_residual_abs_mm",
        "stage_elapsed_seconds", "elapsed_seconds", "disposition",
    )}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, choices=(1, 2), required=True)
    args = parser.parse_args()
    _run_stage(args.stage)


if __name__ == "__main__":
    main()
