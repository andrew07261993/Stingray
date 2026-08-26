#!/usr/bin/env python3
"""Verify an extracted STINGRAY_COMPLETE_PRODUCT_DEFINITION package."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


FINAL_NAMES = {
    "12_MANIFESTS/FINAL_PACKAGE_MANIFEST.csv",
    "12_MANIFESTS/FINAL_SHA256SUMS.txt",
    "12_MANIFESTS/FINAL_PACKAGE_SUMMARY.json",
}


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


def matching_files(root: Path, suffix: str) -> list[Path]:
    return [path for path in walk_files(root) if path.suffix.lower() == suffix.lower()]


def read_head_tail(path: Path, head: int = 5000, tail: int = 128) -> tuple[bytes, bytes]:
    with open(windows_extended_path(path), "rb") as stream:
        first = stream.read(head)
        stream.seek(max(0, size(path) - tail))
        last = stream.read(tail)
    return first, last


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    package = args.package_root.resolve()
    if not os.path.isdir(windows_extended_path(package)):
        raise FileNotFoundError(package)

    checks: list[dict[str, object]] = []

    def check(identifier: str, accepted: bool, detail: str) -> None:
        checks.append({"check_id": identifier, "accepted": bool(accepted), "detail": detail})

    manifests = package / "12_MANIFESTS"
    manifest_path = manifests / "FINAL_PACKAGE_MANIFEST.csv"
    with manifest_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    errors = []
    for row in rows:
        path = package / row["path"]
        if not os.path.isfile(windows_extended_path(path)) or size(path) != int(row["bytes"]) or sha256(path) != row["sha256"]:
            errors.append(row["path"])
    check("EXT-001", not errors, f"manifested files={len(rows)}; byte/hash errors={errors}")

    final_summary_path = manifests / "FINAL_PACKAGE_SUMMARY.json"
    final_summary = json.loads(final_summary_path.read_text(encoding="utf-8"))
    checksums_path = manifests / "FINAL_SHA256SUMS.txt"
    check(
        "EXT-002",
        sha256(manifest_path) == final_summary["final_package_manifest_sha256"]
        and sha256(checksums_path) == final_summary["final_sha256sums_sha256"],
        "self-excluded final manifest and checksum hashes agree with FINAL_PACKAGE_SUMMARY.json",
    )

    all_files = walk_files(package)
    actual_files = {path.relative_to(package).as_posix() for path in all_files}
    expected_files = {row["path"] for row in rows} | FINAL_NAMES
    check(
        "EXT-003",
        actual_files == expected_files,
        f"missing={sorted(expected_files - actual_files)}; unexpected={sorted(actual_files - expected_files)}",
    )

    structured_errors = []
    for path in matching_files(package, ".json"):
        try:
            with open(windows_extended_path(path), encoding="utf-8") as stream:
                json.load(stream)
        except Exception as error:  # noqa: BLE001 - evidence report records exact artifact failure
            structured_errors.append(f"{path.relative_to(package).as_posix()}: {error}")
    for path in matching_files(package, ".csv"):
        try:
            with open(windows_extended_path(path), encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream)
                next(reader)
        except Exception as error:  # noqa: BLE001
            structured_errors.append(f"{path.relative_to(package).as_posix()}: {error}")
    check("EXT-004", not structured_errors, f"JSON/CSV parse errors={structured_errors}")

    cad_errors = []
    step_files = matching_files(package, ".step") + matching_files(package, ".stp")
    for path in step_files:
        first, last = read_head_tail(path)
        if not first.startswith(b"ISO-10303-21;") or b"AP242" not in first or not last.rstrip().endswith(b"END-ISO-10303-21;"):
            cad_errors.append(path.relative_to(package).as_posix())
    brep_files = matching_files(package, ".brep")
    for path in brep_files:
        first, _ = read_head_tail(path, head=128, tail=8)
        if b"DBRep_DrawableShape" not in first:
            cad_errors.append(path.relative_to(package).as_posix())
    check("EXT-005", len(step_files) >= 125 and len(brep_files) == 123 and not cad_errors, f"STEP={len(step_files)}; BREP={len(brep_files)}; syntax errors={cad_errors}")

    image_errors = []
    png_files = matching_files(package, ".png")
    for path in png_files:
        try:
            with Image.open(windows_extended_path(path)) as image:
                image.verify()
        except Exception as error:  # noqa: BLE001
            image_errors.append(f"{path.relative_to(package).as_posix()}: {error}")
    check("EXT-006", len(png_files) >= 150 and not image_errors, f"PNG files={len(png_files)}; verification errors={image_errors}")

    pptx = package / "08_EXECUTIVE" / "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pptx"
    with zipfile.ZipFile(windows_extended_path(pptx)) as archive:
        corrupt = archive.testzip()
        slide_count = sum(bool(re.fullmatch(r"ppt/slides/slide\d+\.xml", name)) for name in archive.namelist())
    pdf = package / "08_EXECUTIVE" / "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pdf"
    reader = PdfReader(windows_extended_path(pdf))
    check("EXT-007", corrupt is None and slide_count == 13 and len(reader.pages) == 13 and not reader.is_encrypted, f"PPTX corrupt={corrupt}; slides={slide_count}; PDF pages={len(reader.pages)}")

    gzip_errors = []
    gzip_files = matching_files(package, ".gz")
    for path in gzip_files:
        try:
            with gzip.open(windows_extended_path(path), "rb") as stream:
                while stream.read(1024 * 1024):
                    pass
        except Exception as error:  # noqa: BLE001
            gzip_errors.append(f"{path.relative_to(package).as_posix()}: {error}")
    check("EXT-008", not gzip_errors, f"gzip files={len(gzip_files)}; errors={gzip_errors}")

    stale = [
        path.relative_to(package).as_posix()
        for path in all_files
        if (
            path.suffix.lower() in {".tmp", ".bak", ".pyc", ".pyo"}
            or "__pycache__" in path.parts
            or path.name.endswith("~")
        )
    ]
    check("EXT-009", not stale, f"stale/transient files={stale}")

    failures = [row for row in checks if not row["accepted"]]
    result = {
        "schema": "STINGRAY_COMPLETE_PRODUCT_DEFINITION_EXTRACTION_AUDIT_V1",
        "status": "PASS" if not failures else "FAIL",
        "package_root": package.as_posix(),
        "check_count": len(checks),
        "failed_check_count": len(failures),
        "checks": checks,
    }
    output = json.dumps(result, indent=2) + "\n"
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8", newline="\n")
    print(output, end="")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
