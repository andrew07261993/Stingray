#!/usr/bin/env python3
"""Create the exactly twelve deterministic SHORT14 inspection views."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw

import render_evidence


FILENAMES = [
    "01_BASELINE_AXIAL_SIDE_SECTION.png",
    "02_CORRECTED_AXIAL_SIDE_SECTION.png",
    "03_BASELINE_NEW_AXIAL_OVERLAY.png",
    "04_FORWARD_BALLAST_CARRIER_ADJACENCY.png",
    "05_AFT_EXTENDING_POWERTRAIN.png",
    "06_RELOCATED_RETAINED_CYLINDER_LAYOUT.png",
    "07_SHORTENED_STOWED_SYSTEM.png",
    "08_SHORTENED_DEPLOYED_SYSTEM.png",
    "09_CLOSED_CORDURA_BUOY_PACK.png",
    "10_PACK_SECTION_INFLATOR_WATER_ACCESS.png",
    "11_EXTERNAL_MANUAL_PULL_ACCESS.png",
    "12_OPEN_PACK_INFLATED_BUOY_TETHER_LOAD_PATH.png",
]


def _all_ids(builder) -> list[str]:
    return [occurrence.occurrence_id for occurrence in builder.occurrences]


def _matching(builder, prefixes: tuple[str, ...] = (), exact: tuple[str, ...] = ()) -> list[str]:
    return [
        occurrence.occurrence_id
        for occurrence in builder.occurrences
        if occurrence.occurrence_id in exact or occurrence.occurrence_id.startswith(prefixes)
    ]


def _overlay(baseline_path: Path, corrected_path: Path, output_path: Path) -> None:
    corrected = Image.open(corrected_path).convert("RGBA")
    baseline = Image.open(baseline_path).convert("RGBA").resize(corrected.size, Image.Resampling.LANCZOS)
    white = Image.new("RGBA", corrected.size, "white")
    baseline_layer = Image.blend(white, baseline, 0.42)
    corrected_layer = corrected.copy()
    corrected_layer.putalpha(178)
    merged = Image.alpha_composite(baseline_layer, corrected_layer)
    draw = ImageDraw.Draw(merged)
    draw.rectangle((20, 20, 630, 76), fill=(255, 255, 255, 225), outline=(38, 59, 84, 255), width=2)
    draw.text((34, 34), "SOURCE BASELINE 480 mm PIVOT (FAINT) / SHORT14 355 mm PIVOT (SOLID)", fill=(20, 45, 68, 255))
    merged.convert("RGB").save(output_path, format="PNG", optimize=False)


def render_views(stowed, deployed, root: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for existing in output_dir.glob("*.png"):
        existing.unlink()
    render_evidence.OUT = output_dir

    baseline_source = root / "work" / "forward_arm_repack" / "inspection_views" / "02_UPDATED_STOWED_FULL_LENGTH_NEW_PIVOT.png"
    shutil.copyfile(baseline_source, output_dir / FILENAMES[0])

    axial_ids = _matching(
        stowed,
        prefixes=("NOSE-", "BALLAST-", "FWD-RING", "PIVOT-CARRIER", "ARM-", "CROSSHEAD",
                  "GS19-", "HBD-", "BACKUP-SPRING", "FIXED-SECTOR", "SHORT-AFT-SHELL",
                  "AFT-CLOSURE", "RECOVERY-HARDPOINT", "CORDURA-", "PACK-ATTACHMENT",
                  "HYDRO-1F", "BUOY-CO2", "MANUAL-PULL", "WATER-ENTRY"),
    )
    render_evidence.render(
        stowed, axial_ids, FILENAMES[1],
        "Corrected axial side section — ballast / minimum transition / carrier / aft powertrain / external pack",
        3, -90, 2.2, ((-95, 95), (-95, 95), (0, 1680)),
    )
    _overlay(output_dir / FILENAMES[0], output_dir / FILENAMES[1], output_dir / FILENAMES[2])

    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("BALLAST-", "FWD-RING", "PIVOT-CARRIER", "ARM-", "PIVOT-PIN",
                                           "CROSSHEAD-GUIDE-SPIDER", "FIXED-SECTOR")),
        FILENAMES[3], "Exact forward-ballast aft face Z=336 / 8 mm transition / carrier face Z=344 / pivot Z=355",
        16, -62, 0.55, ((-40, 40), (-40, 40), (315, 420)),
    )
    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("PIVOT-CARRIER", "CROSSHEAD", "LINK-", "GS19-", "HBD-",
                                           "BACKUP-SPRING", "FIXED-SECTOR", "ARM-LONGERON")),
        FILENAMES[4], "Forward carrier with GS-19 / HBD-15 / backup spring bodies extending aft",
        17, -48, 0.6, ((-38, 38), (-38, 38), (335, 565)),
    )
    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("SHORT-AFT-SHELL", "PACK-ATTACHMENT-COLLAR", "BUOY-CO2",
                                           "HYDRO-1F", "BUOY-INLET", "INFLATOR-GUARD")),
        FILENAMES[5], "Cylinder disposition — no retained internal reservoirs; buoy cartridge/inflator external aft",
        8, -70, 0.7, ((-90, 90), (-70, 70), (1325, 1640)),
    )
    render_evidence.render(
        stowed, _all_ids(stowed), FILENAMES[6],
        "SHORT14 STOWED — exact source-derived named assembly",
        8, -68, 2.4, ((-105, 105), (-105, 105), (0, 1680)),
    )
    render_evidence.render(
        deployed, _all_ids(deployed), FILENAMES[7],
        "SHORT14 DEPLOYED — shortened 80-degree arms and deployed external buoy",
        12, -58, 4.0, ((-420, 420), (-420, 420), (0, 2170)),
    )
    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("CORDURA-", "HOOK-", "LOOP-", "PACK-EDGE", "PACK-ATTACHMENT-WEBBING",
                                           "PACK-RADIAL", "WATER-ENTRY", "MANUAL-PULL", "PULL-TAB")),
        FILENAMES[8], "Closed Aft_Buoy_Breakaway_Wrap_CORDURA with peel closure and external pull tab",
        13, -55, 0.45, ((-100, 100), (-90, 90), (1345, 1630)),
    )
    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("CORDURA-CRADLE", "CORDURA-FLAP-LEFT", "EXT-BUOY-PANEL", "BUOY-INLET",
                                           "HYDRO-1F", "BUOY-CO2", "INFLATOR-GUARD", "WATER-ENTRY")),
        FILENAMES[9], "Pack section — buoy-mounted Hydro 1F proxy and direct closed-pack water-entry window",
        7, -88, 0.40, ((-95, 95), (-80, 80), (1360, 1615)),
    )
    render_evidence.render(
        stowed,
        _matching(stowed, prefixes=("HYDRO-1F", "MANUAL-PULL", "PULL-TAB", "CORDURA-FLAP-RIGHT", "WATER-ENTRY")),
        FILENAMES[10], "External gloved manual pull — keeper, modeled slack, and unobstructed fired travel",
        12, -35, 0.25, ((35, 100), (-35, 35), (1440, 1580)),
    )
    render_evidence.render(
        deployed,
        _matching(deployed, prefixes=("EXT-BUOY-PANEL", "CORDURA-", "STRUCTURAL-RECOVERY-TETHER",
                                             "TETHER-THIMBLE", "RECOVERY-HARDPOINT", "RECOVERY-PIN",
                                             "HYDRO-1F", "BUOY-INLET", "INFLATOR-GUARD")),
        FILENAMES[11], "Open pack / inflated buoy / structural tether load path bypassing Cordura and hook-and-loop",
        14, -52, 3.0, ((-310, 310), (-310, 310), (1325, 2180)),
    )
    import short14_external_buoy_postrender
    short14_external_buoy_postrender.overwrite_polished_views(root, output_dir)
    paths = [output_dir / name for name in FILENAMES]
    if len(list(output_dir.glob("*.png"))) != 12 or any(not path.is_file() for path in paths):
        raise RuntimeError("inspection render set must contain exactly twelve named PNG files")
    return paths
