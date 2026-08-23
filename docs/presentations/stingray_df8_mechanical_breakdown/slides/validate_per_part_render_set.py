#!/usr/bin/env python3
"""Validate DF8 render/manifest coverage, PNG hashes, and image dimensions."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    manifest_path = args.manifest.resolve()
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    rendered = [row for row in rows if row["included"]]
    excluded = [row for row in rows if not row["included"]]
    png_paths: list[Path] = []
    for row in rendered:
        if row["render_status"] != "RENDERED":
            issues.append(f"{row['part_number']}: included but status={row['render_status']}")
            continue
        path = repo_root / row["render_png_path"]
        png_paths.append(path)
        if not path.is_file():
            issues.append(f"{row['part_number']}: missing PNG {path}")
            continue
        if sha256(path) != row["png_sha256"]:
            issues.append(f"{row['part_number']}: PNG hash mismatch")
        with Image.open(path) as image:
            if image.format != "PNG":
                issues.append(f"{row['part_number']}: expected PNG, found {image.format}")
            if image.size != (1600, 1200):
                issues.append(f"{row['part_number']}: expected 1600x1200, found {image.size}")
            if image.mode not in {"RGB", "RGBA"}:
                issues.append(f"{row['part_number']}: unexpected image mode {image.mode}")

    if len(set(png_paths)) != len(png_paths):
        issues.append("duplicate render_png_path values found")
    actual_pngs = sorted((manifest_path.parent.parent / "renders").glob("*.png"))
    if set(actual_pngs) != set(png_paths):
        extras = sorted(str(path) for path in set(actual_pngs) - set(png_paths))
        missing = sorted(str(path) for path in set(png_paths) - set(actual_pngs))
        if extras:
            issues.append(f"unexpected PNGs: {extras}")
        if missing:
            issues.append(f"manifest PNGs absent from render folder: {missing}")

    exclusion_counts = Counter(row["exclusion_reason"] for row in excluded)
    expected = {
        "part_definition_count": 121,
        "included_render_count": 116,
        "fastener_exclusion_count": 5,
        "o_ring_exclusion_count": 0,
    }
    actual = {
        "part_definition_count": len(rows),
        "included_render_count": len(rendered),
        "fastener_exclusion_count": exclusion_counts["standard fastener"],
        "o_ring_exclusion_count": exclusion_counts["O-ring"],
    }
    for key, value in expected.items():
        if actual[key] != value:
            issues.append(f"{key}: expected {value}, found {actual[key]}")

    report = {
        "status": "PASS" if not issues else "FAIL",
        "manifest_path": manifest_path.as_posix(),
        "counts": actual,
        "unrenderable_parts": [
            row["part_number"] for row in rows if row["render_status"] == "ERROR"
        ],
        "issues": issues,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
