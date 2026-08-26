#!/usr/bin/env python3
"""Stage frozen CAD, source, evidence, and validation into the handoff tree."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "short14_external_buoy"
OUT = ROOT / "work" / "complete_product_definition"
ATTACHMENT = (
    Path(r"C:\Users\ANDRE.ANDREWSPC\.codex\attachments")
    / "c71c0002-3da5-4adc-858e-c8a3784c7146"
    / "pasted-text.txt"
)
STATUS = (
    "MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR "
    "FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(windows_extended_path(path), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def windows_extended_path(path: Path) -> str:
    """Return a CopyFile2-safe absolute path when staged names exceed MAX_PATH."""
    resolved = str(path.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def copy_verified(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    os.makedirs(windows_extended_path(destination.parent), exist_ok=True)
    shutil.copy2(windows_extended_path(source), windows_extended_path(destination))
    source_size = os.stat(windows_extended_path(source)).st_size
    destination_size = os.stat(windows_extended_path(destination)).st_size
    if source_size != destination_size or sha256(source) != sha256(destination):
        raise RuntimeError(f"Byte-preserving copy failed: {source} -> {destination}")


def source_files(root: Path) -> Iterable[Path]:
    root_extended = windows_extended_path(root)
    for directory, directory_names, filenames in os.walk(root_extended):
        directory_names[:] = sorted(name for name in directory_names if name != "__pycache__")
        for filename in sorted(filenames):
            path_string = os.path.join(directory, filename)
            if path_string.startswith("\\\\?\\"):
                path_string = path_string[4:]
            path = Path(path_string)
            if path.suffix.lower() in {".pyc", ".pyo"}:
                continue
            yield path


def copy_tree_verified(source: Path, destination: Path) -> int:
    count = 0
    for path in source_files(source):
        target = destination / path.relative_to(source)
        copy_verified(path, target)
        count += 1
    return count


def stage_cad_masters() -> None:
    target = OUT / "01_CAD_MASTERS"
    names = [
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step",
        "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step",
        "authoring_inventory_stowed.json",
        "authoring_inventory_deployed.json",
        "authoring_manifest.json",
        "FINAL_MASS_CG_INERTIA.json",
    ]
    for name in names:
        copy_verified(SOURCE / name, target / name)


def stage_source_and_build_inputs() -> None:
    rebuild = OUT / "11_BUILD_AND_REPRODUCIBILITY" / "rebuild_source"
    trees = [
        ROOT / "work" / "r2_source",
        ROOT / "work" / "input",
        ROOT / "work" / "forward_arm_repack",
    ]
    rows = []
    for tree in trees:
        destination = rebuild / tree.relative_to(ROOT)
        count = copy_tree_verified(tree, destination)
        rows.append(
            {
                "source_tree": tree.relative_to(ROOT).as_posix(),
                "staged_tree": relative(destination),
                "file_count": count,
            }
        )
    manifest = OUT / "11_BUILD_AND_REPRODUCIBILITY" / "REBUILD_SOURCE_TREE_REGISTER.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stage_source_package_registers() -> None:
    target = OUT / "03_BOM_AND_REGISTERS" / "SOURCE_PACKAGE05_REGISTERS"
    names = [
        "AUTONOMOUS_DECISION_LOG.md",
        "AXIAL_RELOCATION_REGISTER.csv",
        "BOM_DELTA.csv",
        "BUOY_EJECTOR_REMOVAL_REGISTER.csv",
        "CYLINDER_DISPOSITION_REGISTER.csv",
        "EXTERNAL_BUOY_PACK_COMPONENT_REGISTER.csv",
        "EXTERNAL_BUOY_PACK_DEFINITION.md",
        "FINAL_ATTACHMENT_CONNECTIVITY.csv",
        "FINAL_MOTION_AUDIT_SUMMARY.csv",
        "SHORT14_FORWARD_POWERTRAIN_DESIGN_REPORT.md",
        "SHORT_ARM_MISSION_ENVELOPE_COMPARISON.md",
        "SOFTGOODS_ATTACHMENT_MAP.csv",
    ]
    for name in names:
        copy_verified(SOURCE / name, target / name)


def stage_validation() -> None:
    mappings = [
        (SOURCE / "validation" / "endpoints", OUT / "09_VALIDATION" / "endpoints"),
        (
            SOURCE / "validation" / "complete_product_definition_five_angle",
            OUT / "09_VALIDATION" / "five_angle",
        ),
        (
            SOURCE / "validation" / "complete_product_definition_full_motion",
            OUT / "09_VALIDATION" / "full_motion",
        ),
    ]
    for source, destination in mappings:
        copy_tree_verified(source, destination)


def stage_system_views() -> None:
    source_views = SOURCE / "inspection_views"
    destination = OUT / "07_RENDERING_AND_SCREENSHOTS" / "system_views"
    copy_tree_verified(source_views, destination)
    open_pack = source_views / "12_OPEN_PACK_INFLATED_BUOY_TETHER_LOAD_PATH.png"
    copy_verified(open_pack, destination / "open_pack_overview.png")


def stage_commission() -> None:
    copy_verified(ATTACHMENT, OUT / "00_RELEASE_INDEX" / "COMMISSION_SOURCE.txt")


def refresh_dependency_manifest() -> None:
    """Bind the dependency record to every delivered Python/Node pipeline source."""
    manifest = (
        OUT
        / "11_BUILD_AND_REPRODUCIBILITY"
        / "DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json"
    )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    source_root = ROOT / "work" / "r2_source"
    staged_root = (
        OUT
        / "11_BUILD_AND_REPRODUCIBILITY"
        / "rebuild_source"
        / "work"
        / "r2_source"
    )
    sources = sorted(
        (
            path
            for path in source_files(source_root)
            if path.parent == source_root and path.suffix.lower() in {".py", ".mjs"}
        ),
        key=lambda path: path.name.lower(),
    )
    rows = []
    for path in sources:
        staged = staged_root / path.name
        if (
            not os.path.isfile(windows_extended_path(staged))
            or os.stat(windows_extended_path(path)).st_size
            != os.stat(windows_extended_path(staged)).st_size
            or sha256(path) != sha256(staged)
        ):
            raise RuntimeError(f"Staged pipeline source is not byte-identical: {path.name}")
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "source_kind": "PYTHON" if path.suffix.lower() == ".py" else "NODE_ESM",
                "bytes": os.stat(windows_extended_path(path)).st_size,
                "sha256": sha256(path),
            }
        )
    data["source_inventory_scope"] = (
        "Every direct .py and .mjs file delivered under work/r2_source; refreshed by "
        "stage_complete_product_definition.py after byte-verified staging."
    )
    data["source_inventory_file_count"] = len(rows)
    data["delivered_source_inventory"] = rows
    # Retain the historical key for consumers while widening it to the exact delivered scope.
    data["authoring_sources"] = rows
    data["required_python_modules_by_scope"] = {
        "cad_build_and_validation": ["cadquery", "OCP", "numpy", "matplotlib"],
        "package_audit_and_extraction": ["Pillow", "pypdf"],
        "executive_pdf_authoring": ["reportlab"],
    }
    data["required_node_modules_by_scope"] = {
        "executive_presentation_authoring": ["@oai/artifact-tool"],
        "historical_workbook_authoring": ["@oai/artifact-tool"],
    }
    data["required_native_tools_by_scope"] = {
        "pptx_render_and_overflow_qa": ["LibreOffice-compatible headless renderer"],
        "pdf_inspection_and_render_qa": ["Poppler pdfinfo", "Poppler pdftoppm"],
    }
    data["reviewed_status_transition_procedure"] = (
        "11_BUILD_AND_REPRODUCIBILITY/CONTROLLED_STATUS_TRANSITION_PROCEDURE.md"
    )
    data["manifest_refresh_status"] = "PASS - ALL DELIVERED PIPELINE SOURCES HASH-BOUND"
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_evidence_register() -> None:
    manifests = OUT / "12_MANIFESTS"
    manifests.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in source_files(OUT):
        if manifests in path.parents:
            continue
        relative_path = relative(path)
        rows.append(
            {
                "path": relative_path,
                "category": relative_path.split("/", 1)[0],
                "bytes": os.stat(windows_extended_path(path)).st_size,
                "sha256": sha256(path),
                "status": STATUS,
            }
        )
    register = manifests / "EVIDENCE_REGISTER.csv"
    with register.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "status": STATUS,
        "file_count_excluding_12_MANIFESTS": len(rows),
        "total_bytes_excluding_12_MANIFESTS": sum(int(row["bytes"]) for row in rows),
        "category_counts": {
            category: sum(row["category"] == category for row in rows)
            for category in sorted({row["category"] for row in rows})
        },
        "evidence_register_sha256": sha256(register),
    }
    (manifests / "STAGING_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def main() -> None:
    if not OUT.is_dir():
        raise FileNotFoundError(OUT)
    stage_cad_masters()
    stage_source_and_build_inputs()
    stage_source_package_registers()
    stage_validation()
    stage_system_views()
    stage_commission()
    refresh_dependency_manifest()
    write_evidence_register()
    summary = json.loads((OUT / "12_MANIFESTS" / "STAGING_SUMMARY.json").read_text(encoding="utf-8"))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
