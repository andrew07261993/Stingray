#!/usr/bin/env python3
"""Create the final package manifests and deterministic delivery ZIP."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "work" / "complete_product_definition"
MANIFESTS = PACKAGE / "12_MANIFESTS"
ZIP_PATH = ROOT / "STINGRAY_COMPLETE_PRODUCT_DEFINITION.zip"
ZIP_HASH_PATH = ROOT / "STINGRAY_COMPLETE_PRODUCT_DEFINITION.zip.sha256"
DELIVERY_SUMMARY = ROOT / "STINGRAY_COMPLETE_PRODUCT_DEFINITION_DELIVERY_SUMMARY.json"
PREFIX = "STINGRAY_COMPLETE_PRODUCT_DEFINITION/"
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


def read_bytes(path: Path) -> bytes:
    with open(windows_extended_path(path), "rb") as stream:
        return stream.read()


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


def package_files(*, include_final: bool) -> list[Path]:
    files = []
    for path in walk_files(PACKAGE):
        relative = path.relative_to(PACKAGE).as_posix()
        if not include_final and relative in FINAL_NAMES:
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(PACKAGE).as_posix())


def write_final_manifests() -> dict[str, object]:
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "path": path.relative_to(PACKAGE).as_posix(),
            "bytes": size(path),
            "sha256": sha256(path),
        }
        for path in package_files(include_final=False)
    ]
    manifest = MANIFESTS / "FINAL_PACKAGE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "bytes", "sha256"), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    checksums = MANIFESTS / "FINAL_SHA256SUMS.txt"
    checksums.write_text(
        "".join(f"{row['sha256']}  {row['path']}\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    summary = {
        "schema": "STINGRAY_COMPLETE_PRODUCT_DEFINITION_FINAL_PACKAGE_V1",
        "status": "MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE",
        "manifest_scope": "all package files except the three self-referential FINAL_* manifest files",
        "manifested_file_count": len(rows),
        "manifested_total_bytes": sum(int(row["bytes"]) for row in rows),
        "final_package_manifest_sha256": sha256(manifest),
        "final_sha256sums_sha256": sha256(checksums),
    }
    summary_path = MANIFESTS / "FINAL_PACKAGE_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    return summary


def build_zip() -> dict[str, object]:
    temporary = ZIP_PATH.with_suffix(".zip.tmp")
    files = package_files(include_final=True)
    with zipfile.ZipFile(
        windows_extended_path(temporary),
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
        strict_timestamps=True,
    ) as archive:
        for path in files:
            relative = path.relative_to(PACKAGE).as_posix()
            info = zipfile.ZipInfo(PREFIX + relative, date_time=(2026, 8, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, read_bytes(path), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(windows_extended_path(temporary), windows_extended_path(ZIP_PATH))

    with zipfile.ZipFile(windows_extended_path(ZIP_PATH)) as archive:
        corrupt = archive.testzip()
        members = [info for info in archive.infolist() if not info.is_dir()]
    if corrupt is not None or len(members) != len(files):
        raise RuntimeError(f"ZIP verification failed: corrupt={corrupt}; members={len(members)}; files={len(files)}")

    zip_hash = sha256(ZIP_PATH)
    ZIP_HASH_PATH.write_text(f"{zip_hash}  {ZIP_PATH.name}\n", encoding="utf-8", newline="\n")
    delivery = {
        "schema": "STINGRAY_COMPLETE_PRODUCT_DEFINITION_DELIVERY_V1",
        "status": "MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE",
        "zip_filename": ZIP_PATH.name,
        "zip_bytes": size(ZIP_PATH),
        "zip_sha256": zip_hash,
        "zip_member_count": len(members),
        "zip_crc_test": "PASS",
        "top_level_prefix": PREFIX,
    }
    DELIVERY_SUMMARY.write_text(json.dumps(delivery, indent=2) + "\n", encoding="utf-8", newline="\n")
    return delivery


def main() -> None:
    package_summary = write_final_manifests()
    delivery_summary = build_zip()
    print(json.dumps({"package": package_summary, "delivery": delivery_summary}, indent=2))


if __name__ == "__main__":
    main()
