#!/usr/bin/env python3
"""Fail-closed assembly of the three-file final DF8 delivery archive."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "work" / "final_release"
ANALYSIS = ROOT / "work" / "final_analysis"
OUTPUT = ROOT / "outputs" / "6f4e7892e9f1" / "STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD.zip"

MEMBERS = (
    "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step",
    "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step",
    "STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx",
)

STEP_MEMBERS = MEMBERS[:2]
INVENTORY_MEMBERS = (
    "authoring_inventory_stowed.json",
    "authoring_inventory_deployed.json",
)

REQUIRED_WORKSHEET_NAMES = (
    "01_OCCURRENCE_BOM",
    "02_UNIQUE_PARTS",
    "03_PURCHASED_ITEMS",
    "04_CUSTOM_PARTS",
    "05_ATTACHMENT_MAP",
    "06_CONFIGURATION_MATRIX",
    "07_CONSUMABLES",
    "08_FINAL_VALIDATION",
)

ENVIRONMENT_DISPOSITION = (
    "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; "
    "OWNER CREO IMPORT OCCURS AFTER DELIVERY."
)

FORBIDDEN_RELEASE_TOKENS = (
    "CREO_VALIDATION_PENDING",
    "CREO-CLEAN-SESSION",
    "R2_CANDIDATE_WIP",
    "CANDIDATE WIP",
)

REQUIRED_GATE_IDS = {
    "AP242-STOWED", "BREP-VALID-STOWED", "INTERFERENCE-STOWED",
    "INTENTIONAL-FIT-REGISTER-STOWED", "CLEARANCE-EVIDENCE-STOWED",
    "AP242-DEPLOYED", "BREP-VALID-DEPLOYED", "INTERFERENCE-DEPLOYED",
    "INTENTIONAL-FIT-REGISTER-DEPLOYED", "CLEARANCE-EVIDENCE-DEPLOYED",
    "STATE-PARITY", "OCCURRENCE-TRANSFORMS", "OCCURRENCE-BOM-RECONCILIATION",
    "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION", "DOD-POSITIVE-DEPLOYED-LOCKS",
    "DOD-POSITIVE-STOWED-RETENTION", "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
    "DOD-CLOSED-ROUTE-ENDS", "ARM-KINEMATICS-ENDPOINTS", "ARM-LENGTH",
    "ARM-SURFACE-QUALITY", "CROSSHEAD-TRAVEL", "NORMAL-BODY-OML",
    "ARM-MODULE-HARD-ENVELOPE", "RIGID-LENGTH", "SYSTEM-MASS",
    "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH", "PROCUREMENT-DEFINITION",
    "MOTION-FULL-MECHANISM", "INTENTIONAL-FIT-REGISTER-MOTION",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing required release-control file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"release-control file root is not an object: {path}")
    return value


def verify_record(path: Path, record: object, label: str) -> None:
    if not path.is_file() or not isinstance(record, dict):
        raise RuntimeError(f"{label} is missing or invalid for {path.name}")
    if record.get("size_bytes") != path.stat().st_size:
        raise RuntimeError(f"{label} size mismatch for {path.name}")
    if str(record.get("sha256", "")).lower() != sha256(path):
        raise RuntimeError(f"{label} SHA-256 mismatch for {path.name}")


def verify_workbook_contract(path: Path) -> None:
    """Verify required worksheet identity/order and final governance labels."""
    if not zipfile.is_zipfile(path):
        raise RuntimeError(f"workbook is not a valid XLSX/ZIP container: {path}")
    with zipfile.ZipFile(path, "r") as workbook:
        bad = workbook.testzip()
        if bad is not None:
            raise RuntimeError(f"workbook CRC failure: {bad}")
        try:
            workbook_xml = workbook.read("xl/workbook.xml")
        except KeyError as exc:
            raise RuntimeError("workbook lacks xl/workbook.xml") from exc
        root = ET.fromstring(workbook_xml)
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        names = tuple(
            str(node.attrib.get("name", "")).strip()
            for node in root.findall("x:sheets/x:sheet", namespace)
        )
        if len(names) != len(set(names)) or any(not name for name in names):
            raise RuntimeError(f"workbook contains blank or duplicate sheet names: {names!r}")
        required_positions = []
        for name in REQUIRED_WORKSHEET_NAMES:
            if name not in names:
                raise RuntimeError(f"workbook lacks required worksheet: {name}")
            required_positions.append(names.index(name))
        if required_positions != sorted(required_positions):
            raise RuntimeError(
                "required workbook worksheets are not in controlling-commission order: "
                f"{names!r}"
            )
        searchable = b"\n".join(
            workbook.read(name)
            for name in workbook.namelist()
            if name.endswith(".xml")
        ).decode("utf-8", errors="ignore")
    if ENVIRONMENT_DISPOSITION not in searchable:
        raise RuntimeError("workbook lacks the exact informational environment disposition")
    uppercase = searchable.upper()
    forbidden = [token for token in FORBIDDEN_RELEASE_TOKENS if token in uppercase]
    if forbidden:
        raise RuntimeError(f"workbook contains forbidden obsolete release token(s): {forbidden}")


def main() -> None:
    gate_file = ANALYSIS / "validation" / "gate_results.json"
    authoring_manifest_path = ANALYSIS / "authoring_manifest.json"
    validation_manifest_path = ANALYSIS / "validation" / "validation_manifest.json"
    workbook_manifest_path = ANALYSIS / "workbook_build_manifest.json"
    gates = load_object(gate_file)
    authoring_manifest = load_object(authoring_manifest_path)
    validation_manifest = load_object(validation_manifest_path)
    workbook_manifest = load_object(workbook_manifest_path)
    gate_rows = gates.get("gates", [])
    gate_ids = [row.get("gate_id") for row in gate_rows]
    statuses = [row.get("status") for row in gate_rows]
    if (
        len(gate_ids) != len(REQUIRED_GATE_IDS)
        or len(set(gate_ids)) != len(gate_ids)
        or set(gate_ids) != REQUIRED_GATE_IDS
        or any(status != "PASS" for status in statuses)
        or gates.get("computed_release_status") != "PASS"
        or gates.get("package_required_label") != "FINAL — RELEASED"
        or gates.get("gate_counts", {}).get("PASS") != len(REQUIRED_GATE_IDS)
        or gates.get("gate_counts", {}).get("FAIL") != 0
        or gates.get("gate_counts", {}).get("BLOCKED") != 0
    ):
        raise RuntimeError("final archive prohibited: Definition-of-Done gates are not all PASS")

    step_paths = {name: RELEASE / name for name in STEP_MEMBERS}
    inventory_paths = {name: ANALYSIS / name for name in INVENTORY_MEMBERS}
    if set(authoring_manifest.get("files", {})) != set(STEP_MEMBERS):
        raise RuntimeError("authoring manifest STEP member set is not exact")
    if set(authoring_manifest.get("inventories", {})) != set(INVENTORY_MEMBERS):
        raise RuntimeError("authoring manifest inventory member set is not exact")
    for name, path in step_paths.items():
        verify_record(path, authoring_manifest["files"].get(name), "authoring manifest STEP record")
    for name, path in inventory_paths.items():
        verify_record(path, authoring_manifest["inventories"].get(name), "authoring manifest inventory record")

    validation_records = validation_manifest.get("files")
    if not isinstance(validation_records, dict):
        raise RuntimeError("validation manifest lacks a files object")
    validation_bound_paths = {
        **step_paths,
        **inventory_paths,
        authoring_manifest_path.name: authoring_manifest_path,
        gate_file.name: gate_file,
    }
    for name, path in validation_bound_paths.items():
        verify_record(path, validation_records.get(name), "validation manifest record")

    if workbook_manifest.get("schema") != "DF8_FINAL_WORKBOOK_BUILD_MANIFEST_V1":
        raise RuntimeError("workbook build manifest schema mismatch")
    verify_record(
        validation_manifest_path,
        workbook_manifest.get("validation_manifest"),
        "workbook build validation-manifest record",
    )
    verify_record(
        gate_file,
        workbook_manifest.get("gate_results"),
        "workbook build gate-results record",
    )
    workbook_record = workbook_manifest.get("workbook")
    workbook_path = RELEASE / MEMBERS[2]
    if not isinstance(workbook_record, dict) or workbook_record.get("name") != MEMBERS[2]:
        raise RuntimeError("workbook build manifest names the wrong workbook")
    verify_record(workbook_path, workbook_record, "workbook build record")
    verify_workbook_contract(workbook_path)
    workbook_step_records = workbook_manifest.get("step_files")
    if not isinstance(workbook_step_records, dict) or set(workbook_step_records) != set(STEP_MEMBERS):
        raise RuntimeError("workbook build manifest STEP set is not exact")
    for name, path in step_paths.items():
        verify_record(path, workbook_step_records.get(name), "workbook build STEP record")

    sources = [RELEASE / member for member in MEMBERS]
    missing = [str(path) for path in sources if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"missing or empty release member(s): {missing}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite an existing final archive: {OUTPUT}")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD.",
            suffix=".zip.tmp", dir=OUTPUT.parent, delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sources:
                archive.write(path, arcname=path.name)
        with zipfile.ZipFile(temporary_path, "r") as archive:
            names = tuple(archive.namelist())
            if names != MEMBERS:
                raise RuntimeError(f"archive member mismatch: {names!r}")
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f"archive CRC failure: {bad}")
        os.replace(temporary_path, OUTPUT)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    print(json.dumps({
        "archive": str(OUTPUT),
        "sha256": sha256(OUTPUT),
        "size_bytes": OUTPUT.stat().st_size,
        "members": [
            {"name": path.name, "size_bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in sources
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
