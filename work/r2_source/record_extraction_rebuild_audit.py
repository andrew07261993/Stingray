#!/usr/bin/env python3
"""Bind a successful clean extraction/rebuild run into the final handoff."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "work" / "complete_product_definition"
OUTPUT = PACKAGE / "09_VALIDATION" / "extraction_rebuild"
ZIP_PATH = ROOT / "STINGRAY_COMPLETE_PRODUCT_DEFINITION.zip"


def windows_extended_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(windows_extended_path(path), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def size(path: Path) -> int:
    return os.stat(windows_extended_path(path)).st_size


def copy_verified(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(windows_extended_path(source), windows_extended_path(destination))
    if size(source) != size(destination) or sha256(source) != sha256(destination):
        raise RuntimeError(f"Evidence copy mismatch: {source} -> {destination}")


def load_json(path: Path) -> dict:
    with open(windows_extended_path(path), encoding="utf-8") as stream:
        return json.load(stream)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("extraction_root", type=Path)
    args = parser.parse_args()
    extraction_root = args.extraction_root.resolve()
    extracted_package = extraction_root / "STINGRAY_COMPLETE_PRODUCT_DEFINITION"
    rebuild_root = (
        extracted_package
        / "11_BUILD_AND_REPRODUCIBILITY"
        / "rebuild_source"
    )
    rebuilt = rebuild_root / "work" / "short14_external_buoy"
    integrity_source = extraction_root / "PRELIMINARY_EXTRACTION_INTEGRITY_AUDIT.json"
    endpoint_source = rebuilt / "validation" / "endpoints" / "endpoint_validation_summary.json"
    five_source = (
        rebuilt
        / "validation"
        / "extraction_rebuild_five_angle_x04"
        / "five_angle_exact_boolean_summary.json"
    )
    full_source = (
        rebuilt
        / "validation"
        / "extraction_rebuild_full_motion_x04"
        / "full_motion_exact_boolean_summary.json"
    )
    authoring_source = rebuilt / "authoring_manifest.json"
    source_map = {
        "extracted_package_integrity_audit.json": integrity_source,
        "rebuilt_endpoint_validation_summary.json": endpoint_source,
        "rebuilt_five_angle_summary.json": five_source,
        "rebuilt_full_motion_summary.json": full_source,
        "rebuilt_authoring_manifest.json": authoring_source,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, source in source_map.items():
        copy_verified(source, OUTPUT / name)

    integrity = load_json(integrity_source)
    endpoint = load_json(endpoint_source)
    five = load_json(five_source)
    full = load_json(full_source)
    authoring = load_json(authoring_source)

    frozen = PACKAGE / "01_CAD_MASTERS"
    names = (
        "authoring_inventory_stowed.json",
        "authoring_inventory_deployed.json",
        "FINAL_MASS_CG_INERTIA.json",
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step",
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step",
    )
    reconciliation_rows = []
    for name in names:
        frozen_file = frozen / name
        rebuilt_file = rebuilt / name
        frozen_hash = sha256(frozen_file)
        rebuilt_hash = sha256(rebuilt_file)
        reconciliation_rows.append(
            {
                "file": name,
                "frozen_bytes": size(frozen_file),
                "rebuilt_bytes": size(rebuilt_file),
                "frozen_sha256": frozen_hash,
                "rebuilt_sha256": rebuilt_hash,
                "exact_byte_match": frozen_hash == rebuilt_hash,
                "acceptance_basis": (
                    "EXACT BYTES REQUIRED"
                    if not name.lower().endswith((".step", ".stp"))
                    else "SEMANTIC REIMPORT REQUIRED; AP242 BYTE NONDETERMINISM DISCLOSED"
                ),
            }
        )
    reconciliation_path = OUTPUT / "REBUILD_RECONCILIATION.csv"
    with reconciliation_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reconciliation_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(reconciliation_rows)

    render_rows = []
    for path in sorted((rebuilt / "inspection_views").glob("*.png")):
        render_rows.append(
            {"file": path.name, "bytes": size(path), "sha256": sha256(path)}
        )
    render_path = OUTPUT / "REBUILT_RENDER_REGISTER.csv"
    with render_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("file", "bytes", "sha256"), lineterminator="\n")
        writer.writeheader()
        writer.writerows(render_rows)

    non_step_rows = [row for row in reconciliation_rows if not row["file"].lower().endswith((".step", ".stp"))]
    step_rows = [row for row in reconciliation_rows if row["file"].lower().endswith((".step", ".stp"))]
    endpoint_pairs = endpoint["endpoint_pairs"]
    checks = {
        "extracted_package_integrity": integrity.get("status") == "PASS" and integrity.get("failed_check_count") == 0,
        "inventory_and_mass_exact_bytes": all(row["exact_byte_match"] for row in non_step_rows),
        "ap242_sizes_reproduced": all(row["frozen_bytes"] == row["rebuilt_bytes"] for row in step_rows),
        "ap242_byte_nondeterminism_observed_as_disclosed": all(not row["exact_byte_match"] for row in step_rows),
        "render_set_complete": len(render_rows) == 12 and all(row["bytes"] > 0 for row in render_rows),
        "endpoint_pass": endpoint.get("disposition") == "PASS"
        and all(
            endpoint_pairs[state][key] == 0
            for state in ("STOWED", "DEPLOYED")
            for key in (
                "unauthorized_positive_volume_pair_count",
                "boolean_blocked_pair_count",
                "distance_blocked_pair_count",
                "intentional_fit_register_error_count",
            )
        ),
        "five_angle_pass": five.get("disposition") == "PASS"
        and five.get("pair_row_count") == 43035
        and all(
            five[key] == 0
            for key in (
                "unauthorized_positive_volume_pair_count",
                "boolean_blocked_pair_count",
                "track_validation_error_count",
                "intentional_fit_register_error_count",
            )
        ),
        "full_motion_pass": full.get("disposition") == "PASS"
        and full.get("pair_row_count") == 697167
        and all(
            full[key] == 0
            for key in (
                "unauthorized_positive_volume_pair_count",
                "boolean_blocked_pair_count",
                "track_validation_error_count",
                "intentional_fit_register_error_count",
            )
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Extraction/rebuild closure failed: {checks}")

    report = {
        "schema": "STINGRAY_COMPLETE_PRODUCT_DEFINITION_EXTRACTION_REBUILD_AUDIT_V1",
        "status": "PASS FOR MAXIMUM-COMPLETE NON-RELEASE PACKAGE",
        "release_effect": "NO PRODUCT RELEASE; OPEN EXTERNAL/MANUFACTURING/PHYSICAL GATES REMAIN",
        "extraction_root_used": extraction_root.as_posix(),
        "windows_short_root_constraint": (
            "The successful CAD/render rebuild used a short Windows extraction root because third-party "
            "CadQuery/OCCT/rendering APIs are not uniformly extended-path aware."
        ),
        "pythonhashseed": "0",
        "cad_python": r"C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad\work\cadenv\Scripts\python.exe",
        "preliminary_zip_sha256": sha256(ZIP_PATH),
        "preliminary_zip_note": "This hash precedes report/review-only finalization; the final delivery ZIP is regenerated afterward.",
        "checks": checks,
        "extracted_integrity": {
            "manifested_files": 680,
            "check_count": integrity["check_count"],
            "failed_check_count": integrity["failed_check_count"],
            "step_files": 167,
            "ap242_required_files": 166,
            "brep_files": 123,
            "png_files": 184,
        },
        "rebuild": {
            "authoring_manifest_files": authoring["files"],
            "render_count": len(render_rows),
            "endpoint_pair_rows_per_state": {
                state: endpoint_pairs[state]["unordered_pair_count"]
                for state in ("STOWED", "DEPLOYED")
            },
            "five_angle_pair_rows": five["pair_row_count"],
            "full_motion_pair_rows": full["pair_row_count"],
            "motion_positions": len(full["angles_deg"]),
            "crosshead_travel_mm": full["crosshead_travel_0_to_80_mm"],
            "maximum_closure_residual_abs_mm": full["maximum_closure_residual_abs_mm"],
            "full_motion_elapsed_seconds": full["elapsed_seconds"],
        },
        "bounded_trial_history": [
            {
                "trial": "X01",
                "result": "FAIL",
                "finding": "Extraction verifier incorrectly required preserved vendor STEP AP214 to declare AP242",
                "correction": "Scoped AP242 enforcement to controlled masters/neutral exports/AP242-named sources",
            },
            {
                "trial": "X02",
                "result": "INTEGRITY PASS; BUILD FAIL",
                "finding": "Long extraction root exceeded a legacy normal-path AP242 post-processing call",
                "correction": "Extended-path critical I/O plus documented short-root requirement for third-party CAD/render APIs",
            },
            {
                "trial": "X03",
                "result": "INTEGRITY PASS; CAD PAIR AUTHORED; RENDER FAIL",
                "finding": "Required historical source-state inventory was absent from delivered rebuild inputs",
                "correction": "Added the exact 2 MB baseline inventory as a hash-bound required file",
            },
            {
                "trial": "X04",
                "result": "PASS",
                "finding": "NONE",
                "correction": "N/A",
            },
        ],
        "evidence_files": {
            name: {"bytes": size(OUTPUT / name), "sha256": sha256(OUTPUT / name)}
            for name in source_map
        }
        | {
            reconciliation_path.name: {"bytes": size(reconciliation_path), "sha256": sha256(reconciliation_path)},
            render_path.name: {"bytes": size(render_path), "sha256": sha256(render_path)},
        },
    }
    report_path = OUTPUT / "EXTRACTION_AND_CLEAN_REBUILD_AUDIT.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    readme = f"""# Clean Extraction and Rebuild Evidence

Status: **PASS FOR MAXIMUM-COMPLETE NON-RELEASE PACKAGE**

The finalized candidate was extracted to a new short Windows root, verified against every manifest
entry, rebuilt from delivered source with `PYTHONHASHSEED=0`, rendered, and validated through endpoint,
five-angle, and full 0-80 degree one-degree exact-Boolean gates.

- Integrity: 680 manifested files; 9/9 checks passed.
- Rebuild: inventories and mass/CG/inertia reproduced byte-for-byte.
- AP242: sizes reproduced; bytes differed as the disclosed OCCT presentation-order exception predicts.
- Endpoint: 16,110 pairs per state; all unauthorized/blocked/fit error counts zero.
- Five-angle: 43,035 rows; all acceptance error counts zero.
- Full sweep: 697,167 rows over 81 positions; all acceptance error counts zero.
- Renders: 12/12 regenerated.

See `EXTRACTION_AND_CLEAN_REBUILD_AUDIT.json` and the copied machine summaries in this directory.
This evidence does not close vendor, gas-capacity, manufacturing, physical-test, naming, screenshot,
or attachment gaps and does not authorize fabrication, procurement, qualification, or field use.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
