#!/usr/bin/env python3
"""Assemble and hash the controlled R2 candidate WIP delivery archive."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work"
STATUS = "CREO_VALIDATION_PENDING — WIP — NOT RELEASED"
ZIP_NAME = "STINGRAY_I5S_DF8_AP242_COHESION_CORRECTION_R2_CANDIDATE_WIP.zip"
STOWED = WORK / "r2_release" / "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_STOWED_AP242.step"
DEPLOYED = WORK / "r2_release" / "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_DEPLOYED_AP242.step"
CONTEXT = WORK / "r2_release" / "STINGRAY_I5S_DF8_R2_EXTERNAL_TEST_CONTEXT_PROVISIONAL_AP242.step"
WORKBOOK = WORK / "r2_release" / "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_REVIEW_WORKBOOK.xlsx"
VALIDATION = WORK / "r2_analysis" / "validation"
NCR_CSV = WORK / "r2_analysis" / "workbook_exports" / "ncr_closure_register.csv"
GATE_CSV = WORK / "r2_analysis" / "workbook_exports" / "validation_gate_table.csv"
STAGE = WORK / "r2_package" / "stage"
OUTPUT_DIR = ROOT / "outputs" / "6f4e7892e9f1"
COMPONENT_ROOT = WORK / "r2_components"
ACCEPTED_SOURCE_INPUT_NAMES = (
    "ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp",
    "ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in sorted(source.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        copy_file(path, destination / path.relative_to(source))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_current_file(record: dict, path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if int(record.get("size_bytes", -1)) != path.stat().st_size:
        raise RuntimeError(f"{label} size mismatch: {path}")
    if record.get("sha256") != sha256(path):
        raise RuntimeError(f"{label} hash mismatch: {path}")


def validate_component_catalog(expected_master_hashes: dict[str, str]) -> dict:
    """Reject stale, incomplete, untraceable, or path-unsafe component CAD."""
    provenance_path = COMPONENT_ROOT / "provenance.json"
    provenance = read_json(provenance_path)
    if provenance.get("package_status") != STATUS:
        raise RuntimeError("Component provenance does not carry the exact WIP status")
    if provenance.get("catalog_states") != ["STOWED", "DEPLOYED"]:
        raise RuntimeError("Component catalog does not explicitly cover both endpoint states")
    if provenance.get("controlled_unique_part_count") != 90:
        raise RuntimeError("Expected 90 reconciled controlled part identities")
    if provenance.get("controlled_state_definition_count") != 180:
        raise RuntimeError("Expected 180 state-explicit controlled part definitions")
    if provenance.get("state_definition_counts") != {"STOWED": 90, "DEPLOYED": 90}:
        raise RuntimeError("Component state-definition counts do not reconcile")
    if provenance.get("state_dependent_part_count") != 18:
        raise RuntimeError("Expected exactly 18 state-dependent controlled part identities")

    component_records = [
        record for record in provenance.get("records", [])
        if record.get("record_type") == "CONTROLLED_PART_DEFINITION"
    ]
    source_records = [
        record for record in provenance.get("records", [])
        if record.get("record_type") == "SOURCE_CAD_REFERENCE"
    ]
    if len(component_records) != 180 or len(source_records) != 2:
        raise RuntimeError("Component provenance record counts are incomplete")

    inventory_parts: dict[tuple[str, str, str], dict] = {}
    for state in ("STOWED", "DEPLOYED"):
        inventory = read_json(WORK / "r2_analysis" / f"authoring_inventory_{state.lower()}.json")
        for part in inventory.get("parts", []):
            inventory_parts[(state, str(part.get("part_number")), str(part.get("revision")))] = part
    if len(inventory_parts) != 180:
        raise RuntimeError("Authoring inventories do not contain 180 state-explicit part definitions")

    identities: dict[tuple[str, str], set[str]] = {}
    listed_paths: set[Path] = set()
    for record in component_records:
        state = record.get("state")
        if state not in {"STOWED", "DEPLOYED"}:
            raise RuntimeError(f"Invalid component state token: {state!r}")
        identity = (str(record.get("part_number")), str(record.get("revision")))
        identities.setdefault(identity, set()).add(state)
        inventory_part = inventory_parts.get((state, identity[0], identity[1]))
        if inventory_part is None:
            raise RuntimeError(f"Component definition has no frozen authoring-inventory row: {state} {identity}")
        for field in ("solid_count", "face_count"):
            if int(record.get(field, -1)) != int(inventory_part.get(field, -2)):
                raise RuntimeError(f"Component {field} differs from frozen inventory: {state} {identity}")
        if abs(float(record.get("volume_mm3", 0.0)) - float(inventory_part.get("volume_mm3", 1.0))) > 1.0e-7:
            raise RuntimeError(f"Component volume differs from frozen inventory: {state} {identity}")
        for kind in ("step", "brep"):
            relative = Path(str(record.get(f"{kind}_path", "")))
            path = (COMPONENT_ROOT / relative).resolve()
            if COMPONENT_ROOT.resolve() not in path.parents:
                raise RuntimeError(f"Unsafe component provenance path: {relative}")
            if f"STATE_{state}" not in path.name:
                raise RuntimeError(f"Component filename lacks explicit state token: {path.name}")
            require_current_file(
                {"size_bytes": record.get(f"{kind}_size_bytes"), "sha256": record.get(f"{kind}_sha256")},
                path,
                f"Component {kind.upper()}",
            )
            listed_paths.add(path)
    if len(identities) != 90 or any(states != {"STOWED", "DEPLOYED"} for states in identities.values()):
        raise RuntimeError("Every controlled identity must have one STOWED and one DEPLOYED definition")

    actual_cad = {
        path.resolve()
        for path in (COMPONENT_ROOT / "controlled_part_definitions").iterdir()
        if path.is_file() and path.suffix.lower() in {".step", ".brep"}
    }
    if actual_cad != listed_paths:
        raise RuntimeError("Component directory contains stale/unlisted CAD or is missing listed CAD")

    for record in source_records:
        relative = Path(str(record.get("step_path", "")))
        path = (COMPONENT_ROOT / relative).resolve()
        if COMPONENT_ROOT.resolve() not in path.parents:
            raise RuntimeError(f"Unsafe source-reference provenance path: {relative}")
        require_current_file(
            {"size_bytes": record.get("step_size_bytes"), "sha256": record.get("step_sha256")},
            path,
            "Source CAD reference",
        )
        if record.get("copied_byte_for_byte") is not True or record.get("source_sha256") != record.get("step_sha256"):
            raise RuntimeError(f"Source CAD is not proven byte-preserved: {path.name}")
    actual_source_cad = {
        path.resolve()
        for path in (COMPONENT_ROOT / "source_cad_as_received").iterdir()
        if path.is_file() and path.suffix.lower() in {".step", ".stp"}
    }
    listed_source_cad = {
        (COMPONENT_ROOT / Path(str(record["step_path"]))).resolve() for record in source_records
    }
    if actual_source_cad != listed_source_cad:
        raise RuntimeError("Source-CAD directory contains stale/unlisted files or is missing listed files")

    provenance_csv = COMPONENT_ROOT / "provenance.csv"
    provenance_csv_record = provenance.get("provenance_files", {}).get(provenance_csv.name, {})
    require_current_file(provenance_csv_record, provenance_csv, "Component provenance CSV")

    basis = provenance.get("catalog_basis", {})
    current_basis_paths = {
        "authoring_sources": {
            "build_r2.py": WORK / "r2_source" / "build_r2.py",
            "r2_geometry.py": WORK / "r2_source" / "r2_geometry.py",
            "export_components.py": WORK / "r2_source" / "export_components.py",
        },
        "authoring_inventories": {
            "authoring_inventory_stowed.json": WORK / "r2_analysis" / "authoring_inventory_stowed.json",
            "authoring_inventory_deployed.json": WORK / "r2_analysis" / "authoring_inventory_deployed.json",
        },
    }
    basis_mtimes: list[int] = []
    for group, paths in current_basis_paths.items():
        records = basis.get(group, {})
        for name, path in paths.items():
            require_current_file(records.get(name, {}), path, f"Component catalog basis {group}")
            basis_mtimes.append(path.stat().st_mtime_ns)
    author_manifest_path = WORK / "r2_analysis" / "authoring_manifest.json"
    require_current_file(basis.get("authoring_manifest", {}), author_manifest_path, "Component catalog authoring manifest")
    basis_mtimes.append(author_manifest_path.stat().st_mtime_ns)
    master_records = basis.get("frozen_masters", {})
    for path in (STOWED, DEPLOYED, CONTEXT):
        require_current_file(master_records.get(path.name, {}), path, "Component catalog frozen master")
        if master_records[path.name].get("sha256") != expected_master_hashes[path.name]:
            raise RuntimeError(f"Component catalog is not locked to frozen master: {path.name}")
        basis_mtimes.append(path.stat().st_mtime_ns)
    if provenance_path.stat().st_mtime_ns < max(basis_mtimes):
        raise RuntimeError("Component provenance predates a frozen catalog basis file")
    return provenance


def validate_source_reimport_comparison() -> dict:
    summary_path = VALIDATION / "source_vs_reimport_summary.json"
    raw_path = VALIDATION / "source_vs_reimport.csv"
    summary = read_json(summary_path)
    if summary.get("overall_status") != "PASS" or int(summary.get("overall_fail_count", -1)) != 0:
        raise RuntimeError("Source-versus-clean-XCAF-reimport comparison did not pass")
    states = {item.get("state"): item for item in summary.get("states", [])}
    if set(states) != {"STOWED", "DEPLOYED"}:
        raise RuntimeError("Source-versus-reimport comparison does not cover both endpoint states")
    for state, item in states.items():
        if item.get("status") != "PASS" or int(item.get("fail_count", -1)) != 0:
            raise RuntimeError(f"Source-versus-reimport comparison failed for {state}")
        if int(item.get("source_occurrence_count", 0)) != int(item.get("reimport_leaf_occurrence_count", -1)):
            raise RuntimeError(f"Source-versus-reimport occurrence count mismatch for {state}")
        if int(item.get("comparison_row_count", 0)) != int(item.get("pass_count", -1)):
            raise RuntimeError(f"Source-versus-reimport row reconciliation failed for {state}")
    if summary.get("raw_evidence") != raw_path.name or not raw_path.is_file():
        raise RuntimeError("Source-versus-reimport raw evidence is missing or misidentified")
    with raw_path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    expected_rows = sum(int(item["comparison_row_count"]) for item in states.values())
    if len(rows) != expected_rows or any(row.get("comparison_status") != "PASS" for row in rows):
        raise RuntimeError("Source-versus-reimport raw evidence does not reconcile to its summary")
    return {
        "overall_status": summary["overall_status"],
        "overall_fail_count": summary["overall_fail_count"],
        "comparison_row_count": len(rows),
        "states": {
            state: {
                "source_occurrence_count": int(item["source_occurrence_count"]),
                "reimport_leaf_occurrence_count": int(item["reimport_leaf_occurrence_count"]),
                "pass_count": int(item["pass_count"]),
                "fail_count": int(item["fail_count"]),
                "status": item["status"],
            }
            for state, item in sorted(states.items())
        },
        "summary_sha256": sha256(summary_path),
        "raw_sha256": sha256(raw_path),
        "explicit_limit": summary.get("explicit_limit"),
    }


def validate_workbook_categories() -> dict:
    """Confirm the consolidated workbook contains every commission register category."""
    category_map = {
        "occurrence_bom": ["04_OCCURRENCE_BOM"],
        "unique_part_master": ["02_UNIQUE_PARTS"],
        "purchased_items_register": ["03_PURCHASED_ITEMS"],
        "custom_parts_register": ["18_CUSTOM_PARTS"],
        "attachment_retention_matrix": ["05_ATTACHMENT_REGISTER", "06_HARDWARE_FITTINGS"],
        "configuration_matrix": ["11_STATE_MATRIX"],
        "consumables_register": ["19_CONSUMABLES"],
        "occurrence_transform_register": ["04_OCCURRENCE_BOM"],
        "interference_register": ["08_INTERFERENCE_REGISTER"],
        "intentional_fit_exception_register": ["08_INTERFERENCE_REGISTER"],
        "minimum_clearance_register": ["07_CLEARANCE_REGISTER"],
        "mechanism_sweep_register": ["09_MOTION_SWEEP"],
        "state_delta_register": ["11_STATE_MATRIX"],
        "routing_termination_register": ["17_ROUTING"],
        "owner_ncr_closure_register": ["01_NCR_CLOSURE"],
        "final_validation": ["12_VALIDATION_GATES", "16_CREO_VALIDATION"],
    }
    with zipfile.ZipFile(WORKBOOK) as archive:
        workbook_xml = ET.fromstring(archive.read("xl/workbook.xml"))
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        sheet_names = {
            sheet.attrib["name"] for sheet in workbook_xml.findall(".//x:sheets/x:sheet", namespace)
        }
    missing = {
        category: [sheet for sheet in required_sheets if sheet not in sheet_names]
        for category, required_sheets in category_map.items()
        if any(sheet not in sheet_names for sheet in required_sheets)
    }
    if missing:
        raise RuntimeError(f"Workbook is missing required commission register categories: {missing}")
    if len(sheet_names) < 20:
        raise RuntimeError(f"Workbook has {len(sheet_names)} sheets; expected the 20-sheet final register")
    return {
        "sheet_count": len(sheet_names),
        "sheet_names": sorted(sheet_names),
        "commission_category_count": len(category_map),
        "commission_category_map": category_map,
    }


def closed_ncr_count(path: Path) -> tuple[int, int]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 8:
        raise RuntimeError(f"Expected the eight controlled commission NCRs, found {len(rows)}")
    status_key = next(
        (key for key in rows[0] if "status" in key.strip().lower().replace(" ", "_")),
        None,
    )
    if status_key is None:
        raise RuntimeError("NCR export has no status column")
    return sum(str(row[status_key]).strip().upper() == "CLOSED" for row in rows), len(rows)


def exported_gate_counts(path: Path) -> dict[str, int]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 23:
        raise RuntimeError(f"Expected 23 exported validation gates, found {len(rows)}")
    status_key = next(
        (key for key in rows[0] if "status" in key.strip().lower().replace(" ", "_")),
        None,
    )
    if status_key is None:
        raise RuntimeError("Gate export has no status column")
    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    for row in rows:
        status = str(row[status_key]).strip().upper()
        if status not in counts:
            raise RuntimeError(f"Unexpected exported gate status: {status!r}")
        counts[status] += 1
    return counts


def write_manifest_csv(root: Path, path: Path) -> None:
    excluded = {
        path.relative_to(root).as_posix(),
        "06_MANIFEST/SHA256SUMS.txt",
    }
    rows = []
    for item in sorted(root.rglob("*")):
        if not item.is_file():
            continue
        relative = item.relative_to(root).as_posix()
        if relative in excluded:
            continue
        rows.append({"relative_path": relative, "size_bytes": item.stat().st_size, "sha256": sha256(item)})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["relative_path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def write_sha256sums(root: Path, path: Path) -> None:
    rows = []
    for item in sorted(root.rglob("*")):
        if not item.is_file() or item == path:
            continue
        rows.append(f"{sha256(item)}  {item.relative_to(root).as_posix()}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def deterministic_zip(source_root: Path, output: Path) -> None:
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.relative_to(source_root).as_posix(), (2026, 8, 21, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    temporary.replace(output)


def main() -> None:
    gate_results = read_json(VALIDATION / "gate_results.json")
    validation_summary = read_json(VALIDATION / "validation_summary.json")
    author_manifest = read_json(WORK / "r2_analysis" / "authoring_manifest.json")
    creo = read_json(WORK / "r2_metadata" / "CREO_VALIDATION.json")
    if gate_results.get("package_required_label") != STATUS:
        raise RuntimeError("Validator package label does not match the required WIP status")
    if author_manifest.get("release_status") != STATUS or creo.get("package_status") != STATUS:
        raise RuntimeError("Authoring or Creo metadata does not carry the exact WIP status")
    expected_hashes = {
        STOWED.name: author_manifest["files"][STOWED.name]["sha256"],
        DEPLOYED.name: author_manifest["files"][DEPLOYED.name]["sha256"],
        CONTEXT.name: author_manifest["files"][CONTEXT.name]["sha256"],
    }
    for path in (STOWED, DEPLOYED, CONTEXT):
        if sha256(path) != expected_hashes[path.name]:
            raise RuntimeError(f"Frozen authoring hash mismatch: {path.name}")
    component_provenance = validate_component_catalog(expected_hashes)
    source_reimport = validate_source_reimport_comparison()
    validation_manifest_text = (VALIDATION / "validation_manifest.json").read_text(encoding="utf-8")
    for path in (STOWED, DEPLOYED):
        if expected_hashes[path.name] not in validation_manifest_text:
            raise RuntimeError(f"Validation manifest does not reference the frozen master hash: {path.name}")
    closed, ncr_total = closed_ncr_count(NCR_CSV)
    if exported_gate_counts(GATE_CSV) != gate_results["gate_counts"]:
        raise RuntimeError("Workbook gate export does not reconcile to independent gate_results.json")
    if WORKBOOK.stat().st_mtime_ns < (VALIDATION / "gate_results.json").stat().st_mtime_ns:
        raise RuntimeError("Workbook predates the final independent gate results")
    workbook_categories = validate_workbook_categories()
    failed_blocked = int(gate_results["gate_counts"]["FAIL"]) + int(gate_results["gate_counts"]["BLOCKED"])

    if STAGE.exists():
        shutil.rmtree(STAGE)
    for name in (
        "01_EDITABLE_SOURCE", "02_FINAL_AP242", "03_COMPONENT_AND_VENDOR_CAD",
        "04_MASTER_BUILD_REGISTER", "05_VALIDATION_EVIDENCE", "06_MANIFEST",
    ):
        (STAGE / name).mkdir(parents=True, exist_ok=True)

    editable = STAGE / "01_EDITABLE_SOURCE"
    copy_tree(WORK / "r2_source", editable / "work" / "r2_source")
    copy_file(WORK / "r2_metadata" / "BUILD_INSTRUCTIONS.md", editable / "BUILD_INSTRUCTIONS.md")
    copy_file(WORK / "r2_metadata" / "DEPENDENCIES.json", editable / "DEPENDENCIES.json")
    for name in ("BUILD_INSTRUCTIONS.md", "DEPENDENCIES.json", "CREO_VALIDATION.json", "PACKAGE_STATUS.txt"):
        copy_file(WORK / "r2_metadata" / name, editable / "work" / "r2_metadata" / name)
    accepted_inputs = editable / "work" / "input" / "wp02" / "accepted_source_cad"
    for name in ACCEPTED_SOURCE_INPUT_NAMES:
        copy_file(COMPONENT_ROOT / "source_cad_as_received" / name, accepted_inputs / name)
    copy_file(COMPONENT_ROOT / "provenance.json", accepted_inputs / "COMPONENT_AND_SOURCE_PROVENANCE.json")
    copy_file(COMPONENT_ROOT / "provenance.csv", accepted_inputs / "COMPONENT_AND_SOURCE_PROVENANCE.csv")

    copy_file(STOWED, STAGE / "02_FINAL_AP242" / STOWED.name)
    copy_file(DEPLOYED, STAGE / "02_FINAL_AP242" / DEPLOYED.name)

    copy_tree(COMPONENT_ROOT, STAGE / "03_COMPONENT_AND_VENDOR_CAD")
    copy_file(CONTEXT, STAGE / "03_COMPONENT_AND_VENDOR_CAD" / "external_test_context" / CONTEXT.name)

    copy_file(WORKBOOK, STAGE / "04_MASTER_BUILD_REGISTER" / WORKBOOK.name)

    evidence = STAGE / "05_VALIDATION_EVIDENCE"
    copy_tree(VALIDATION, evidence / "clean_xcaf_reimport")
    for name in (
        "authoring_inventory_stowed.json", "authoring_inventory_deployed.json", "authoring_manifest.json",
        "authoring_pair_audit_stowed.json", "authoring_pair_audit_deployed.json",
    ):
        copy_file(WORK / "r2_analysis" / name, evidence / "authoring_source_checks" / name)
    copy_tree(WORK / "r2_evidence_views", evidence / "before_after_views" / "r2_technical_views")
    before_dirs = list((WORK / "input" / "r1").glob("**/11_VISUAL_REVIEW"))
    if len(before_dirs) != 1:
        raise RuntimeError(f"Expected one controlled R1 visual-reference directory, found {len(before_dirs)}")
    copy_tree(before_dirs[0], evidence / "before_after_views" / "r1_controlled_reference_views")
    copy_file(ROOT / "upload" / "Pasted markdown(20260821-171406).md", evidence / "corrective_commission.md")
    copy_file(WORK / "r2_metadata" / "CREO_VALIDATION.json", evidence / "creo" / "creo_validation.json")
    copy_file(NCR_CSV, evidence / "workbook_exports" / NCR_CSV.name)
    copy_file(GATE_CSV, evidence / "workbook_exports" / GATE_CSV.name)

    manifest = STAGE / "06_MANIFEST"
    copy_file(WORK / "r2_metadata" / "PACKAGE_STATUS.txt", manifest / "PACKAGE_STATUS.txt")
    copy_file(WORK / "r2_metadata" / "DEPENDENCIES.json", manifest / "software_tool_versions.json")
    copy_file(COMPONENT_ROOT / "provenance.csv", manifest / "source_file_provenance.csv")
    copy_file(COMPONENT_ROOT / "provenance.json", manifest / "source_file_provenance.json")
    configuration = {
        "package_status": STATUS,
        "configuration": "R2_CANDIDATE_WIP",
        "masters": {path.name: {"sha256": sha256(path), "size_bytes": path.stat().st_size} for path in (STOWED, DEPLOYED)},
        "external_context": {CONTEXT.name: {"sha256": sha256(CONTEXT), "size_bytes": CONTEXT.stat().st_size}},
        "validation_gate_counts": gate_results["gate_counts"],
        "remaining_failed_or_blocked_gates": failed_blocked,
        "closed_ncr_count": closed,
        "controlled_ncr_count": ncr_total,
        "clean_creo_passed": bool(creo.get("clean_creo_passed")),
        "creo_gate_result": creo.get("gate_result"),
        "validator_scope": validation_summary.get("validator_scope"),
        "validator_limit": validation_summary.get("validator_limit"),
        "source_vs_reimport": source_reimport,
        "workbook_register_categories": workbook_categories,
        "component_unique_part_count": component_provenance.get("controlled_unique_part_count"),
        "component_state_definition_count": component_provenance.get("controlled_state_definition_count"),
        "component_state_definition_counts": component_provenance.get("state_definition_counts"),
        "state_dependent_part_count": component_provenance.get("state_dependent_part_count"),
    }
    (manifest / "configuration_manifest.json").write_text(
        json.dumps(configuration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (manifest / "MANIFEST_README.md").write_text(
        "# Controlled R2 Candidate WIP Manifest\n\n"
        f"Exact package status: `{STATUS}`\n\n"
        "`file_manifest.csv` hashes every payload/control file that existed before the manifest itself was written. "
        "`SHA256SUMS.txt` then hashes every archive file except itself, avoiding an impossible self-referential digest.\n",
        encoding="utf-8",
    )
    write_manifest_csv(STAGE, manifest / "file_manifest.csv")
    write_sha256sums(STAGE, manifest / "SHA256SUMS.txt")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / ZIP_NAME
    deterministic_zip(STAGE, output)
    archive_hash = sha256(output)
    output.with_suffix(output.suffix + ".sha256").write_text(f"{archive_hash}  {output.name}\n", encoding="utf-8")
    print(json.dumps({
        "package_status": STATUS,
        "zip_filename": output.name,
        "zip_path": output.as_posix(),
        "zip_size_bytes": output.stat().st_size,
        "zip_sha256": archive_hash,
        "closed_ncrs": closed,
        "remaining_failed_or_blocked_gates": failed_blocked,
        "clean_creo_passed": bool(creo.get("clean_creo_passed")),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
