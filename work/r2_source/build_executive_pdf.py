#!/usr/bin/env python3
"""Create the visually faithful executive PDF from the verified PPTX renders."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[2]
EXECUTIVE = ROOT / "work" / "complete_product_definition" / "08_EXECUTIVE"
RENDERS = EXECUTIVE / "_qa" / "pptx_rendered"
OUTPUT = EXECUTIVE / "STINGRAY_EXECUTIVE_STAKEHOLDER_RELEASE_STATUS.pdf"
PAGE_SIZE = (960.0, 540.0)


def slide_number(path: Path) -> int:
    match = re.fullmatch(r"slide-(\d+)\.png", path.name)
    if match is None:
        raise ValueError(f"Unexpected slide-render filename: {path.name}")
    return int(match.group(1))


def main() -> None:
    images = sorted(RENDERS.glob("slide-*.png"), key=slide_number)
    expected = list(range(1, 14))
    actual = [slide_number(path) for path in images]
    if actual != expected:
        raise RuntimeError(f"Expected slide renders {expected}; found {actual}")

    pdf = canvas.Canvas(
        str(OUTPUT),
        pagesize=PAGE_SIZE,
        pageCompression=1,
        invariant=1,
    )
    pdf.setTitle("STINGRAY Executive Stakeholder Release Status")
    pdf.setAuthor("STINGRAY engineering evidence package")
    pdf.setSubject(
        "Maximum-complete digital development package; not released for fabrication, "
        "procurement, qualification, or field use"
    )
    pdf.setKeywords("STINGRAY, CAD, engineering, non-release, AP242, validation")

    for image_path in images:
        pdf.drawImage(
            ImageReader(str(image_path)),
            0,
            0,
            width=PAGE_SIZE[0],
            height=PAGE_SIZE[1],
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        pdf.showPage()

    pdf.save()
    if not OUTPUT.is_file() or OUTPUT.stat().st_size == 0:
        raise RuntimeError(f"PDF was not created: {OUTPUT}")
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size} bytes, {len(images)} pages)")


if __name__ == "__main__":
    main()
