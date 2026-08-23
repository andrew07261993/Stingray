#!/usr/bin/env python3
"""Build subsystem contact sheets for visual QA of the generated render set."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    rows = json.loads(args.manifest.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["render_status"] == "RENDERED":
            grouped[row["subsystem"]].append(row)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    columns = 4
    rows_per_sheet = 4
    cell_width = 400
    cell_height = 300
    title_height = 42
    for subsystem, items in sorted(grouped.items()):
        items.sort(key=lambda row: row["part_number"])
        page_size = columns * rows_per_sheet
        for page_index in range(0, len(items), page_size):
            page = items[page_index:page_index + page_size]
            canvas = Image.new("RGB", (columns * cell_width, title_height + rows_per_sheet * cell_height), "white")
            draw = ImageDraw.Draw(canvas)
            page_number = page_index // page_size + 1
            draw.text((16, 14), f"{subsystem} - render QA sheet {page_number}", fill="#152635", font=font)
            for index, item in enumerate(page):
                source = repo_root / item["render_png_path"]
                with Image.open(source) as image:
                    thumb = image.convert("RGB")
                    thumb.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
                    x = (index % columns) * cell_width + (cell_width - thumb.width) // 2
                    y = title_height + (index // columns) * cell_height + (cell_height - thumb.height) // 2
                    canvas.paste(thumb, (x, y))
            out = args.out_dir / f"{slug(subsystem)}_{page_number:02d}.png"
            canvas.save(out, format="PNG", optimize=False)
            print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
