#!/usr/bin/env python3
"""Freeze the neutral candidate file set supplied to the fresh-context reviewer."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "work" / "complete_product_definition"
PACKET = PACKAGE / "10_REVIEWS" / "independent_review_packet"


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(windows_extended_path(path), "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def included(path: Path) -> bool:
    relative = path.relative_to(PACKAGE).as_posix()
    if relative.startswith("10_REVIEWS/independent_review_packet/"):
        return False
    if relative == "10_REVIEWS/INDEPENDENT_REVIEW_REPORT.md":
        return False
    if relative.startswith("12_MANIFESTS/"):
        return False
    return True


def main() -> None:
    PACKET.mkdir(parents=True, exist_ok=True)
    files = [path for path in walk_files(PACKAGE) if included(path)]
    rows = [
        {
            "path": path.relative_to(PACKAGE).as_posix(),
            "bytes": os.stat(windows_extended_path(path)).st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    manifest = PACKET / "CANDIDATE_REVIEW_FREEZE_MANIFEST.csv"
    with manifest.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "bytes", "sha256"), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # Re-enumerate after the manifest write and prove that every eligible candidate
    # path is represented exactly once.  Packet and final-manifest files are excluded
    # by policy because they are self-referential or produced only after review.
    eligible_paths = {
        path.relative_to(PACKAGE).as_posix()
        for path in walk_files(PACKAGE)
        if included(path)
    }
    manifest_paths = {row["path"] for row in rows}
    missing_from_manifest = sorted(eligible_paths - manifest_paths)
    extra_in_manifest = sorted(manifest_paths - eligible_paths)
    duplicate_manifest_path_count = len(rows) - len(manifest_paths)
    exact_set_equality = (
        not missing_from_manifest
        and not extra_in_manifest
        and duplicate_manifest_path_count == 0
    )
    if not exact_set_equality:
        raise RuntimeError(
            "candidate freeze manifest set mismatch: "
            f"missing={missing_from_manifest}, extra={extra_in_manifest}, "
            f"duplicates={duplicate_manifest_path_count}"
        )

    brief = """# Independent Fresh-Context Review Brief

Review only the frozen candidate rooted two directories above this brief.  The supplied manifest
defines the review input.  Do not modify candidate artifacts.

## Required review questions

1. Does the package truthfully distinguish digital-developmental PASS results from production release?
2. Are any safety, vendor, geometry, COTS, manufacturing, qualification, or procurement claims
   unsupported or overstated?
3. Are the gas-capacity failure, proxy geometry, missing screenshots/attachments, physical-test gaps,
   manufacturing-definition gaps, AP242 byte nondeterminism, and naming nonconformance visible and
   consistently dispositioned?
4. Do the master hashes, BOM/part counts, validation totals, executive deck, PDF, and internal audit
   agree across the package?
5. Is the package complete and usable as a maximum-complete non-release engineering handoff?

Classify each finding as CRITICAL, MAJOR, MINOR, or OBSERVATION.  A known product-release blocker is not
automatically a package-review defect when it is explicit and correctly prevents release.  The owner
decision that the DEPLOYED pack is intentionally open is controlling; review its evidence and status,
but do not relabel the open state as a cleanup defect.
"""
    (PACKET / "REVIEW_BRIEF.md").write_text(brief, encoding="utf-8", newline="\n")

    summary = {
        "schema": "STINGRAY_INDEPENDENT_REVIEW_PACKET_V1",
        "status": "FROZEN FOR READ-ONLY FRESH-CONTEXT REVIEW",
        "package_root": PACKAGE.as_posix(),
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "manifest_sha256": sha256(manifest),
        "eligible_set_equality": "PASS",
        "unmanifested_eligible_file_count": len(missing_from_manifest),
        "extra_manifest_path_count": len(extra_in_manifest),
        "duplicate_manifest_path_count": duplicate_manifest_path_count,
        "excluded": [
            "10_REVIEWS/independent_review_packet/** (self-referential packet files)",
            "10_REVIEWS/INDEPENDENT_REVIEW_REPORT.md (review output)",
            "12_MANIFESTS/** (regenerated only after review closure)",
        ],
    }
    (PACKET / "PACKET_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
