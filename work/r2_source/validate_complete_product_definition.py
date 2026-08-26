#!/usr/bin/env python3
"""Run deterministic internal package-consistency checks."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import os
import re
import zipfile
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "work" / "complete_product_definition"
RESULT = PACKAGE / "10_REVIEWS" / "INTERNAL_AUDIT_RESULTS.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def windows_extended_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def walk_files(root: Path) -> list[Path]:
    files = []
    for directory, directory_names, filenames in os.walk(windows_extended_path(root)):
        directory_names.sort()
        for filename in sorted(filenames):
            path_string = os.path.join(directory, filename)
            if path_string.startswith("\\\\?\\"):
                path_string = path_string[4:]
            files.append(Path(path_string))
    return files


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(identifier: str, accepted: bool, detail: str) -> None:
        checks.append({"check_id": identifier, "accepted": bool(accepted), "detail": detail})

    expected_directories = [f"{index:02d}_{name}" for index, name in [
        (0, "RELEASE_INDEX"),
        (1, "CAD_MASTERS"),
        (2, "PART_DEFINITIONS"),
        (3, "BOM_AND_REGISTERS"),
        (4, "INTERFACES"),
        (5, "ANALYSES"),
        (6, "MANUFACTURING_AND_SERVICE"),
        (7, "RENDERING_AND_SCREENSHOTS"),
        (8, "EXECUTIVE"),
        (9, "VALIDATION"),
        (10, "REVIEWS"),
        (11, "BUILD_AND_REPRODUCIBILITY"),
        (12, "MANIFESTS"),
    ]]
    missing_directories = [name for name in expected_directories if not (PACKAGE / name).is_dir()]
    check("AUD-001", not missing_directories, f"required top-level directories; missing={missing_directories}")

    all_files = walk_files(PACKAGE)
    zero_byte = [
        path.relative_to(PACKAGE).as_posix()
        for path in all_files
        if os.stat(windows_extended_path(path)).st_size == 0
    ]
    check("AUD-002", not zero_byte, f"zero-byte files={zero_byte}")

    expected_master_hashes = {
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step":
            "22342157b2ac96870bbf7cd227e729342b357fd241787be8dc03cf16a92ce7fd",
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step":
            "3f33da7fc6c658c84bfad075ed9c28c9dd96087e675fc9f5d3de7562b19ee045",
        "authoring_inventory_stowed.json":
            "67ae4314d128993d6ab0de761645717f704cbec47b14f33848999025a9f83765",
        "authoring_inventory_deployed.json":
            "7cebfb5c59d25ac148cda125ddce6094558b6fdfebc29c65f6243a1973d50498",
    }
    masters = PACKAGE / "01_CAD_MASTERS"
    mismatched = {
        name: sha256(masters / name)
        for name, expected in expected_master_hashes.items()
        if not (masters / name).is_file() or sha256(masters / name) != expected
    }
    check("AUD-003", not mismatched, f"frozen master hash mismatches={mismatched}")

    step_errors = []
    for step in sorted(masters.glob("*.step")):
        data = step.read_bytes()
        if not data.startswith(b"ISO-10303-21;") or b"AP242" not in data[:5000] or not data.rstrip().endswith(b"END-ISO-10303-21;"):
            step_errors.append(step.name)
    check("AUD-004", len(step_errors) == 0 and len(list(masters.glob("*.step"))) == 2, f"master AP242 syntax errors={step_errors}")

    inventory_details = {}
    for state in ("stowed", "deployed"):
        data = json.loads((masters / f"authoring_inventory_{state}.json").read_text(encoding="utf-8"))
        occurrence_ids = [row["occurrence_id"] for row in data["occurrences"]]
        part_numbers = {row["part_number"] for row in data["parts"]}
        inventory_details[state.upper()] = {
            "state": data["state"],
            "occurrences": len(occurrence_ids),
            "unique_occurrence_ids": len(set(occurrence_ids)),
            "part_definitions": len(part_numbers),
        }
    accepted_inventory = all(
        row["state"] == state and row["occurrences"] == 180 and row["unique_occurrence_ids"] == 180 and row["part_definitions"] == 92
        for state, row in inventory_details.items()
    )
    check("AUD-005", accepted_inventory, f"inventory reconciliation={inventory_details}")

    part_root = PACKAGE / "02_PART_DEFINITIONS"
    manifest_path = part_root / "PART_DEFINITION_MANIFEST.csv"
    with manifest_path.open(encoding="utf-8", newline="") as stream:
        part_rows = list(csv.DictReader(stream))
    part_errors = []
    for row in part_rows:
        for path_field, size_field, hash_field in (
            ("neutral_ap242_path", "neutral_ap242_bytes", "neutral_ap242_sha256"),
            ("native_brep_path", "native_brep_bytes", "native_brep_sha256"),
            ("four_view_render_path", "four_view_render_bytes", "four_view_render_sha256"),
        ):
            artifact = part_root / row[path_field]
            if not artifact.is_file() or artifact.stat().st_size != int(row[size_field]) or sha256(artifact) != row[hash_field]:
                part_errors.append(f"{row['part_number']}:{row['state_definition']}:{path_field}")
    check("AUD-006", len(part_rows) == 123 and not part_errors, f"part rows={len(part_rows)}; file/hash errors={part_errors}")
    check(
        "AUD-007",
        len(list((part_root / "neutral_ap242").glob("*.step"))) == 123
        and len(list((part_root / "native_brep").glob("*.brep"))) == 123
        and len(list((part_root / "renders").glob("*.png"))) == 123,
        "123 neutral AP242, 123 native BREP, and 123 render artifacts required",
    )

    bom_path = PACKAGE / "03_BOM_AND_REGISTERS" / "FULL_BOM.csv"
    with bom_path.open(encoding="utf-8-sig", newline="") as stream:
        bom_rows = list(csv.DictReader(stream))
    make_count = sum(row["make_buy"] == "MAKE" for row in bom_rows)
    buy_count = sum(row["make_buy"] == "BUY" for row in bom_rows)
    check("AUD-008", len(bom_rows) == 92 and make_count == 79 and buy_count == 13, f"BOM rows={len(bom_rows)}, MAKE={make_count}, BUY={buy_count}")

    endpoint = json.loads((PACKAGE / "09_VALIDATION" / "endpoints" / "endpoint_validation_summary.json").read_text(encoding="utf-8"))
    endpoint_ok = endpoint["disposition"] == "PASS" and all(
        endpoint["endpoint_pairs"][state][key] == 0
        for state in ("STOWED", "DEPLOYED")
        for key in (
            "unauthorized_positive_volume_pair_count",
            "boolean_blocked_pair_count",
            "distance_blocked_pair_count",
            "intentional_fit_register_error_count",
        )
    )
    check("AUD-009", endpoint_ok, f"endpoint disposition={endpoint['disposition']}")

    motion_details = {}
    for folder, filename, expected_rows, expected_angles in (
        ("five_angle", "five_angle_exact_boolean_summary.json", 43035, 5),
        ("full_motion", "full_motion_exact_boolean_summary.json", 697167, 81),
    ):
        data = json.loads((PACKAGE / "09_VALIDATION" / folder / filename).read_text(encoding="utf-8"))
        motion_details[folder] = {
            "disposition": data["disposition"],
            "rows": data["pair_row_count"],
            "angles": len(data["angles_deg"]),
            "unauthorized": data["unauthorized_positive_volume_pair_count"],
            "blocked": data["boolean_blocked_pair_count"],
            "track_errors": data["track_validation_error_count"],
            "fit_errors": data["intentional_fit_register_error_count"],
        }
        check(
            f"AUD-01{0 if folder == 'five_angle' else 1}",
            data["disposition"] == "PASS"
            and data["pair_row_count"] == expected_rows
            and len(data["angles_deg"]) == expected_angles
            and all(data[key] == 0 for key in (
                "unauthorized_positive_volume_pair_count",
                "boolean_blocked_pair_count",
                "track_validation_error_count",
                "intentional_fit_register_error_count",
            )),
            f"{folder}={motion_details[folder]}",
        )

    gas = json.loads((PACKAGE / "05_ANALYSES" / "STORED_GAS_INDEPENDENT_CALCULATION.json").read_text(encoding="utf-8"))
    gas_values = json.dumps(gas, sort_keys=True)
    gas_ok = all(token in gas_values for token in ("6.559", "109.77", "97.77", "60"))
    check("AUD-012", gas_ok, "stored-gas JSON contains the independently reported capacity, required mass, deficit, and 60 L basis")

    screenshot_path = PACKAGE / "07_RENDERING_AND_SCREENSHOTS" / "SCREENSHOT_CLOSURE_REPORT.csv"
    with screenshot_path.open(encoding="utf-8-sig", newline="") as stream:
        screenshot_rows = list(csv.DictReader(stream))
    check(
        "AUD-013",
        len(screenshot_rows) == 11 and all("MISSING" in row["input_presence"] for row in screenshot_rows),
        f"screenshot rows={len(screenshot_rows)}; missing inputs={sum('MISSING' in row['input_presence'] for row in screenshot_rows)}",
    )

    executive = PACKAGE / "08_EXECUTIVE"
    pptx = executive / "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pptx"
    with zipfile.ZipFile(pptx) as archive:
        slide_xml = [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        corrupt = archive.testzip()
    check("AUD-014", len(slide_xml) == 13 and corrupt is None, f"PPTX slides={len(slide_xml)}; corrupt entry={corrupt}")
    pdf = executive / "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pdf"
    pdf_reader = PdfReader(pdf)
    check("AUD-015", len(pdf_reader.pages) == 13 and not pdf_reader.is_encrypted, f"PDF pages={len(pdf_reader.pages)}; encrypted={pdf_reader.is_encrypted}")
    check(
        "AUD-016",
        len(list((executive / "_qa" / "pptx_rendered").glob("slide-*.png"))) == 13
        and len(list((executive / "_qa" / "pdf_rendered").glob("page-*.png"))) == 13,
        "13 verified PPTX renders and 13 PDF page renders required",
    )

    release_index = (PACKAGE / "00_RELEASE_INDEX" / "RELEASE_INDEX.md").read_text(encoding="utf-8")
    exception_report = (PACKAGE / "00_RELEASE_INDEX" / "NON_RELEASE_EXCEPTION_REPORT.md").read_text(encoding="utf-8")
    check(
        "AUD-017",
        "NO RELEASE" in release_index
        and "12 g" in exception_report
        and "60 L" in exception_report
        and "authorizes no purchase" in exception_report,
        "release index and exception report preserve no-release/procurement boundaries",
    )

    commission = PACKAGE / "00_RELEASE_INDEX" / "COMMISSION_SOURCE.txt"
    original = Path(r"C:\Users\ANDRE.ANDREWSPC\.codex\attachments\c71c0002-3da5-4adc-858e-c8a3784c7146\pasted-text.txt")
    check("AUD-018", commission.is_file() and sha256(commission) == sha256(original), "commission source is byte-preserved")

    relocation = PACKAGE / "09_VALIDATION" / "VALIDATION_PATH_RELOCATION_MAP.md"
    check("AUD-019", relocation.is_file(), "absolute run-time validation paths have a package-relative relocation map")

    traceability_path = PACKAGE / "00_RELEASE_INDEX" / "REQUIREMENT_TRACEABILITY_MATRIX.csv"
    with traceability_path.open(encoding="utf-8-sig", newline="") as stream:
        traceability = {row["commission_section"]: row for row in csv.DictReader(stream)}
    status_ok = (
        traceability["20"]["status"].startswith("PASS")
        and traceability["23"]["status"].startswith("PASS")
        and (
            traceability["24"]["status"] == "PENDING CLOSURE VERIFICATION"
            or traceability["24"]["status"].startswith("PASS")
        )
        and (
            traceability["26"]["status"] == "PENDING"
            or traceability["26"]["status"].startswith("PASS")
        )
    )
    check(
        "AUD-020",
        status_ok,
        "traceability status state: "
        + ", ".join(f"section {section}={traceability[section]['status']}" for section in ("20", "23", "24", "26")),
    )

    procurement_path = PACKAGE / "03_BOM_AND_REGISTERS" / "PROCUREMENT_REGISTER.csv"
    with procurement_path.open(encoding="utf-8-sig", newline="") as stream:
        procurement = {row["part_number"]: row for row in csv.DictReader(stream)}
    child_numbers = ("GS-19-50-V4A-B8-B8-ROD-CHILD", "HBD-15-25-AA-P-ROD-CHILD")
    procurement_ok = all(
        procurement[number]["quantity_per_product"] == "0"
        and procurement[number]["orderable_configuration"].startswith("INCLUDED IN PARENT ASSEMBLY")
        and procurement[number]["action"].startswith("NO SEPARATE PURCHASE")
        for number in child_numbers
    )
    check("AUD-021", procurement_ok, "articulation children are non-separately-orderable and controlled with parent assemblies")

    build_root = PACKAGE / "11_BUILD_AND_REPRODUCIBILITY"
    dependency_path = build_root / "DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json"
    dependency = json.loads(dependency_path.read_text(encoding="utf-8"))
    staged_source_root = build_root / "rebuild_source" / "work" / "r2_source"
    delivered_source_paths = {
        path.relative_to(staged_source_root).as_posix()
        for path in walk_files(staged_source_root)
        if path.parent == staged_source_root and path.suffix.lower() in {".py", ".mjs"}
    }
    dependency_rows = dependency.get("delivered_source_inventory", [])
    dependency_paths = {
        Path(row["path"]).relative_to("work/r2_source").as_posix()
        for row in dependency_rows
    }
    dependency_errors = []
    for row in dependency_rows:
        source_name = Path(row["path"]).relative_to("work/r2_source")
        artifact = staged_source_root / source_name
        if (
            not os.path.isfile(windows_extended_path(artifact))
            or os.stat(windows_extended_path(artifact)).st_size != int(row["bytes"])
            or sha256(artifact) != row["sha256"]
        ):
            dependency_errors.append(row["path"])
    build_instructions = (build_root / "BUILD_AND_VALIDATION_INSTRUCTIONS.md").read_text(encoding="utf-8")
    procedure = build_root / "CONTROLLED_STATUS_TRANSITION_PROCEDURE.md"
    provenance_ok = (
        delivered_source_paths == dependency_paths
        and len(dependency_rows) == len(dependency_paths)
        and not dependency_errors
        and dependency.get("source_inventory_file_count") == len(dependency_rows)
        and dependency.get("manifest_refresh_status") == "PASS - ALL DELIVERED PIPELINE SOURCES HASH-BOUND"
        and "DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json" in build_instructions
        and "DEPENDENCY_AND_RUNTIME_MANIFEST.md" not in build_instructions
        and procedure.is_file()
        and "pre-review template generator" in procedure.read_text(encoding="utf-8")
    )
    check(
        "AUD-022",
        provenance_ok,
        f"delivered sources={len(delivered_source_paths)}; dependency rows={len(dependency_rows)}; "
        f"missing={sorted(delivered_source_paths - dependency_paths)}; extra={sorted(dependency_paths - delivered_source_paths)}; "
        f"hash/size errors={dependency_errors}; controlled status procedure={procedure.is_file()}",
    )

    assembly_drawing_path = PACKAGE / "06_MANUFACTURING_AND_SERVICE" / "ASSEMBLY_DRAWING_REGISTER.csv"
    with assembly_drawing_path.open(encoding="utf-8-sig", newline="") as stream:
        assembly_drawing_rows = list(csv.DictReader(stream))
    assembly_register_ok = (
        len(assembly_drawing_rows) == 8
        and all(row["assembly_drawing"] == "NOT RELEASED" for row in assembly_drawing_rows)
        and all(row["release_authority"] == "PROHIBITED" for row in assembly_drawing_rows)
        and {row["state"] for row in assembly_drawing_rows} >= {"STOWED", "DEPLOYED", "STOWED/DEPLOYED"}
    )
    check(
        "AUD-023",
        assembly_register_ok,
        f"assembly drawing rows={len(assembly_drawing_rows)}; all drawings unreleased and fabrication prohibited",
    )

    extracted_verifier = staged_source_root / "verify_extracted_complete_product_definition.py"
    verifier_tree = ast.parse(extracted_verifier.read_text(encoding="utf-8"))
    stale_filter_comprehensions = [
        node
        for node in ast.walk(verifier_tree)
        if isinstance(node, ast.ListComp)
        and any(
            isinstance(generator.target, ast.Name)
            and generator.target.id == "path"
            and isinstance(generator.iter, ast.Name)
            and generator.iter.id == "all_files"
            and bool(generator.ifs)
            for generator in node.generators
        )
    ]
    check(
        "AUD-024",
        bool(stale_filter_comprehensions),
        "extracted-package stale/transient scan iterates all_files with an AST-confirmed comprehension filter",
    )

    failed = [row for row in checks if not row["accepted"]]
    result = {
        "schema": "STINGRAY_COMPLETE_PRODUCT_DEFINITION_INTERNAL_AUDIT_V1",
        "status": "PASS" if not failed else "FAIL",
        "scope": "artifact presence, frozen hashes, internal consistency, and presentation/PDF openability; not physical qualification",
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "checks": checks,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
