#!/usr/bin/env python3
"""Polished dimensioned axial projections from exact authoring inventories."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch, Rectangle

import short14_external_buoy_config as cfg


COLORS = {
    "rigid": "#526777",
    "forward": "#91A8BA",
    "ballast": "#D6A84B",
    "carrier": "#D97706",
    "powertrain": "#E95D0F",
    "arm": "#335C81",
    "legacy": "#9B6A6C",
    "pack": "#1388A8",
    "buoy": "#62B6CB",
    "tether": "#263B54",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _occurrences(inventory: dict) -> dict[str, dict]:
    return {row["occurrence_id"]: row for row in inventory["occurrences"]}


def _zr(occurrences: dict[str, dict], occurrence_id: str) -> tuple[float, float]:
    bbox = occurrences[occurrence_id]["global_bbox_mm"]
    return float(bbox["zmin"]), float(bbox["zmax"])


def _bar(ax, z0: float, z1: float, y: float, color: str, label: str,
         *, height: float = 0.58, hatch: str | None = None) -> None:
    ax.add_patch(Rectangle((z0, y - height / 2), z1 - z0, height,
                           facecolor=color, edgecolor="#26323A", linewidth=1.0,
                           hatch=hatch, alpha=0.90))
    if z1 - z0 > 70:
        ax.text((z0 + z1) / 2, y, label, ha="center", va="center", fontsize=8,
                color="white" if color not in (COLORS["forward"], COLORS["ballast"]) else "#17242E",
                fontweight="bold")


def _finish_stack(ax, title: str, xmax: float, yticks: list[tuple[float, str]]) -> None:
    ax.set_xlim(-20, xmax + 25)
    ax.set_ylim(-0.8, max(y for y, _ in yticks) + 0.8)
    ax.set_yticks([y for y, _ in yticks], [label for _, label in yticks])
    ax.set_xlabel("Nose-tip axial station Z [mm]")
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=14)
    ax.grid(axis="x", color="#CBD3D9", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)


def _source_stack(source: dict, output: Path) -> None:
    occ = _occurrences(source)
    fig, ax = plt.subplots(figsize=(16, 6), dpi=170, facecolor="white")
    _bar(ax, 0, 2031, 0, COLORS["rigid"], "SOURCE RIGID ENVELOPE 2031.000 mm")
    _bar(ax, *_zr(occ, "NOSE-001"), 1, COLORS["forward"], "PENETRATOR")
    _bar(ax, *_zr(occ, "BALLAST-001"), 2, COLORS["ballast"], "FORWARD BALLAST")
    _bar(ax, 348, 431, 3, COLORS["legacy"], "4 x CO2")
    _bar(ax, *_zr(occ, "PIVOT-CARRIER-1"), 4, COLORS["carrier"], "CARRIER")
    _bar(ax, *_zr(occ, "CROSSHEAD-001"), 5, COLORS["carrier"], "XHEAD")
    for occurrence_id in ("GS19-BODY-001", "HBD-BODY-001", "BACKUP-SPRING-001"):
        _bar(ax, *_zr(occ, occurrence_id), 6, COLORS["powertrain"], occurrence_id.split("-")[0], height=0.18)
    _bar(ax, 950, 1380, 7, COLORS["legacy"], "3 x BOOSTER RESERVOIRS")
    _bar(ax, 1647, 1750.5, 8, COLORS["legacy"], "INTERNAL EJECTOR")
    _bar(ax, 1788.7, 1870.01, 9, COLORS["legacy"], "INTERNAL BUOY")
    _bar(ax, 1928, 2031, 10, COLORS["legacy"], "AFT SERVICE")
    for z, text, color in ((336, "BALLAST AFT 336", COLORS["ballast"]),
                           (480, "SOURCE PIVOT 480", COLORS["carrier"]),
                           (2031, "RIGID END 2031", COLORS["rigid"])):
        ax.axvline(z, color=color, linewidth=1.6, linestyle="--")
        ax.text(z + 6, 10.55, text, rotation=90, va="top", ha="left", fontsize=8, color=color)
    ticks = [(0, "Rigid body"), (1, "Penetrator"), (2, "Ballast"), (3, "Forward cylinders"),
             (4, "Arm carrier"), (5, "Crosshead"), (6, "Arm powertrain"), (7, "Retained reservoirs"),
             (8, "Buoy ejector"), (9, "Internal buoy"), (10, "Aft closure")]
    _finish_stack(ax, "1 — Source baseline axial side section (exact inventory stations)", 2031, ticks)
    fig.text(0.012, 0.012, "Source: frozen a31fce0e authoring inventory; exact occurrence bounding stations, units mm.", fontsize=7, color="#3A4650")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def _new_stack(short: dict, output: Path) -> None:
    occ = _occurrences(short)
    fig, ax = plt.subplots(figsize=(16, 6), dpi=170, facecolor="white")
    _bar(ax, 0, cfg.RIGID_LENGTH_MM, 0, COLORS["rigid"], f"SHORT14 RIGID ENVELOPE {cfg.RIGID_LENGTH_MM:.3f} mm")
    _bar(ax, *_zr(occ, "NOSE-001"), 1, COLORS["forward"], "PENETRATOR")
    _bar(ax, *_zr(occ, "BALLAST-001"), 2, COLORS["ballast"], "FORWARD BALLAST")
    _bar(ax, *_zr(occ, "FWD-RING-02"), 3, COLORS["forward"], "8 mm")
    _bar(ax, *_zr(occ, "PIVOT-CARRIER-1"), 4, COLORS["carrier"], "CARRIER")
    _bar(ax, *_zr(occ, "CROSSHEAD-001"), 5, COLORS["carrier"], "XHEAD")
    for occurrence_id in ("GS19-BODY-001", "HBD-BODY-001", "BACKUP-SPRING-001"):
        _bar(ax, *_zr(occ, occurrence_id), 6, COLORS["powertrain"], occurrence_id.split("-")[0], height=0.18)
    _bar(ax, *_zr(occ, "ARM-1"), 7, COLORS["arm"], "SHORT ARM 378.206 mm")
    _bar(ax, 741.4, cfg.RIGID_LENGTH_MM, 8, COLORS["rigid"], "SHORTENED AFT BODY")
    _bar(ax, cfg.PACK_Z_MIN_MM, cfg.PACK_Z_MAX_MM, 9, COLORS["pack"], "EXTERNAL CORDURA PACK")
    _bar(ax, 1408, 1554, 10, COLORS["buoy"], "BUOY-MOUNTED INFLATION / PULL")
    for z, text, color in ((336, "BALLAST AFT 336", COLORS["ballast"]),
                           (344, "CARRIER FACE 344", COLORS["forward"]),
                           (355, "NEW PIVOT 355", COLORS["carrier"]),
                           (cfg.RIGID_LENGTH_MM, "RIGID END 1675.4", COLORS["rigid"])):
        ax.axvline(z, color=color, linewidth=1.6, linestyle="--")
        ax.text(z + 6, 10.55, text, rotation=90, va="top", ha="left", fontsize=8, color=color)
    ticks = [(0, "Rigid body"), (1, "Penetrator"), (2, "Ballast"), (3, "Transition"),
             (4, "Arm carrier"), (5, "Crosshead"), (6, "Aft-extending powertrain"), (7, "Short arms"),
             (8, "Aft structure"), (9, "External pack"), (10, "Inflator/manual pull")]
    _finish_stack(ax, "2 — Corrected axial side section: true forward carrier and external buoy pack", 1700, ticks)
    fig.text(0.012, 0.012, "Source: final SHORT14 STOWED authoring inventory; exact occurrence bounding stations, units mm.", fontsize=7, color="#3A4650")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def _overlay(source: dict, short: dict, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 4.7), dpi=170, facecolor="white")
    ax.add_patch(Rectangle((0, 1.15), 2031, 0.5, color="#9AA7B0", ec="#26323A"))
    ax.add_patch(Rectangle((0, 0.15), cfg.RIGID_LENGTH_MM, 0.5, color=COLORS["rigid"], ec="#26323A"))
    ax.add_patch(Rectangle((348, 1.05), 1032, 0.70, facecolor=COLORS["legacy"], alpha=0.32, hatch="////", ec=COLORS["legacy"]))
    ax.add_patch(Rectangle((cfg.PACK_Z_MIN_MM, 0.05), cfg.PACK_AXIAL_LENGTH_MM, 0.70,
                           facecolor=COLORS["pack"], alpha=0.38, ec=COLORS["pack"]))
    ax.axvline(336, color=COLORS["ballast"], lw=2)
    ax.axvline(480, color="#9B4D55", lw=2, ls="--", label="Source pivot 480 mm")
    ax.axvline(355, color=COLORS["carrier"], lw=2, label="New pivot 355 mm")
    ax.annotate("125.000 mm actual forward movement", xy=(355, 2.05), xytext=(480, 2.05),
                arrowprops=dict(arrowstyle="<->", color=COLORS["carrier"], lw=1.8),
                ha="center", va="bottom", fontsize=10, fontweight="bold", color=COLORS["carrier"])
    ax.annotate("355.600 mm rigid-body reduction", xy=(cfg.RIGID_LENGTH_MM, -0.25), xytext=(2031, -0.25),
                arrowprops=dict(arrowstyle="<->", color=COLORS["rigid"], lw=1.8),
                ha="center", va="top", fontsize=10, fontweight="bold", color=COLORS["rigid"])
    ax.set_xlim(-20, 2070); ax.set_ylim(-0.55, 2.45)
    ax.set_yticks([0.4, 1.4], ["SHORT14 / external pack", "SOURCE / internal buoy architecture"])
    ax.set_xlabel("Nose-tip axial station Z [mm]")
    ax.set_title("3 — Baseline / SHORT14 axial overlay", loc="left", fontsize=15, fontweight="bold")
    ax.grid(axis="x", color="#CBD3D9"); ax.legend(loc="upper right", ncol=2)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.text(0.012, 0.012, "Hatched source region contains superseded cartridges/reservoirs/ejector; blue region is the external pack.", fontsize=8, color="#3A4650")
    fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(output, bbox_inches="tight"); plt.close(fig)


def _powertrain(short: dict, output: Path) -> None:
    occ = _occurrences(short)
    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=170, facecolor="white")
    rows = [
        ("PIVOT-CARRIER-1", "Arm pivot carrier", COLORS["carrier"]),
        ("CROSSHEAD-001", "Common crosshead", COLORS["carrier"]),
        ("GS19-BODY-001", "ACE GS-19 fixed body", COLORS["powertrain"]),
        ("HBD-BODY-001", "ACE HBD-15 fixed body", "#B54A2A"),
        ("BACKUP-SPRING-001", "Backup spring / guide corridor", "#F59E0B"),
    ]
    for y, (occurrence_id, label, color) in enumerate(rows):
        z0, z1 = _zr(occ, occurrence_id)
        _bar(ax, z0, z1, y, color, f"{z0:.3f}–{z1:.3f} mm", height=0.52)
        ax.annotate("AFT", xy=(z1 + 65, y), xytext=(z1 + 18, y), arrowprops=dict(arrowstyle="->", lw=1.5, color=color),
                    ha="left", va="center", fontsize=8, color=color, fontweight="bold")
    ax.axvline(cfg.FORWARD_BALLAST_AFT_FACE_Z_MM, color=COLORS["ballast"], ls="--", lw=1.8)
    ax.axvline(cfg.ARM_PIVOT_Z_MM, color=COLORS["carrier"], ls="--", lw=1.8)
    ax.set_xlim(325, 590); ax.set_ylim(-0.7, 4.7)
    ax.set_yticks(range(len(rows)), [label for _, label, _ in rows])
    ax.set_xlabel("Nose-tip axial station Z [mm]")
    ax.set_title("5 — Aft-extending GS-19 / HBD-15 / backup-spring powertrain", loc="left", fontsize=15, fontweight="bold")
    ax.grid(axis="x", color="#CBD3D9"); ax.tick_params(axis="y", length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.text(0.012, 0.012, "Fixed bodies trail aft from the forward carrier; rods retain source fixed/moving kinematic interfaces.", fontsize=8, color="#3A4650")
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(output, bbox_inches="tight"); plt.close(fig)


def _system_stowed(short: dict, output: Path) -> None:
    occ = _occurrences(short)
    fig, ax = plt.subplots(figsize=(16, 5.6), dpi=170, facecolor="white")
    ax.add_patch(Rectangle((170, -28.575), cfg.RIGID_LENGTH_MM - 170, 57.15,
                           facecolor="#D8E0E5", edgecolor="#26323A", lw=1.2))
    ax.fill([0, 170, 170], [0, -28.575, 28.575], color="#91A8BA", ec="#26323A")
    ax.add_patch(Rectangle((170, -24.8), 166, 49.6, facecolor=COLORS["ballast"], edgecolor="#26323A"))
    ax.axvline(344, color=COLORS["forward"], lw=2); ax.axvline(355, color=COLORS["carrier"], lw=2)
    for offset in (-9, 0, 9):
        ax.add_patch(Rectangle((344.9, offset - 2.2), 378.206, 4.4, color=COLORS["arm"], ec="#17324A"))
    ax.add_patch(Rectangle((cfg.PACK_Z_MIN_MM, -48.65), cfg.PACK_AXIAL_LENGTH_MM, 97.3,
                           facecolor=COLORS["pack"], alpha=0.32, edgecolor=COLORS["pack"], lw=2))
    tab = occ["MANUAL-PULL-TAB"]["global_bbox_mm"]
    ax.add_patch(Rectangle((tab["zmin"], tab["xmin"]), tab["zmax"] - tab["zmin"], tab["xmax"] - tab["xmin"],
                           facecolor="#F59E0B", edgecolor="#26323A"))
    ax.annotate("External manual pull", xy=((tab["zmin"] + tab["zmax"]) / 2, tab["xmax"]),
                xytext=(1450, 78), arrowprops=dict(arrowstyle="->", color="#8A4F00"), fontsize=9, color="#8A4F00")
    ax.annotate("1675.400 mm ready-to-throw rigid length", xy=(0, -75), xytext=(cfg.RIGID_LENGTH_MM, -75),
                arrowprops=dict(arrowstyle="<->", lw=1.8), ha="center", va="top", fontweight="bold")
    ax.set_xlim(-30, 1720); ax.set_ylim(-105, 110); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Nose-tip axial station Z [mm]"); ax.set_ylabel("Radial X [mm]")
    ax.set_title("7 — Shortened STOWED system / closed external Cordura pack", loc="left", fontsize=15, fontweight="bold")
    ax.grid(color="#D6DDE2"); ax.set_axisbelow(True)
    legend = [Patch(color=COLORS["ballast"], label="fixed forward ballast"), Patch(color=COLORS["arm"], label="378.206 mm stowed arms"),
              Patch(color=COLORS["pack"], alpha=.4, label="closed external pack")]
    ax.legend(handles=legend, loc="upper right", ncol=3)
    fig.tight_layout(); fig.savefig(output, bbox_inches="tight"); plt.close(fig)


def _system_deployed(short: dict, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 7), dpi=170, facecolor="white")
    ax.add_patch(Rectangle((170, -28.575), cfg.RIGID_LENGTH_MM - 170, 57.15,
                           facecolor="#D8E0E5", edgecolor="#26323A", lw=1.2))
    ax.fill([0, 170, 170], [0, -28.575, 28.575], color="#91A8BA", ec="#26323A")
    theta = cfg.MOTION_ANGLES_FULL[-1]
    radial = cfg.ARM_LENGTH_MM * __import__("math").sin(__import__("math").radians(theta))
    axial = cfg.ARM_LENGTH_MM * __import__("math").cos(__import__("math").radians(theta))
    for endpoint, style in (((cfg.ARM_PIVOT_Z_MM + axial, 18 + radial), "-"),
                            ((cfg.ARM_PIVOT_Z_MM + axial, -9 - radial / 2), "-"),
                            ((cfg.ARM_PIVOT_Z_MM + axial, -9 - radial / 2), "--")):
        ax.plot([cfg.ARM_PIVOT_Z_MM, endpoint[0]], [0, endpoint[1]], style, lw=7 if style == "-" else 3,
                color=COLORS["arm"], solid_capstyle="round")
    ax.add_patch(Rectangle((cfg.PACK_Z_MIN_MM, -48.65), cfg.PACK_AXIAL_LENGTH_MM, 97.3,
                           facecolor=COLORS["pack"], alpha=0.18, edgecolor=COLORS["pack"], lw=2, linestyle="--"))
    ax.plot([1613, 1640, cfg.BUOY_DEPLOYED_CENTER_Z_MM - cfg.BUOY_DEPLOYED_RADIUS_MM + 3],
            [22, 35, 0], color=COLORS["tether"], lw=3)
    ax.add_patch(Circle((cfg.BUOY_DEPLOYED_CENTER_Z_MM, 0), cfg.BUOY_DEPLOYED_RADIUS_MM,
                        facecolor=COLORS["buoy"], edgecolor="#1E6175", alpha=0.42, lw=2))
    ax.annotate("60 L deployed buoy proxy\nR = 242.859 mm", xy=(cfg.BUOY_DEPLOYED_CENTER_Z_MM, 0),
                ha="center", va="center", fontsize=10, fontweight="bold", color="#174E5F")
    ax.annotate("Structural tether bypasses pack", xy=(1645, 34), xytext=(1370, 150),
                arrowprops=dict(arrowstyle="->", color=COLORS["tether"]), fontsize=9, color=COLORS["tether"])
    ax.set_xlim(-30, 2190); ax.set_ylim(-430, 430); ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Nose-tip axial station Z [mm]"); ax.set_ylabel("Radial X projection [mm]")
    ax.set_title("8 — Shortened DEPLOYED system / 80-degree arms / external inflated buoy", loc="left", fontsize=15, fontweight="bold")
    ax.grid(color="#D6DDE2"); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(output, bbox_inches="tight"); plt.close(fig)


def overwrite_polished_views(root: Path, output_dir: Path) -> None:
    source = _load(root / "work" / "final_analysis" / "authoring_inventory_stowed.json")
    short = _load(root / "work" / "short14_external_buoy" / "authoring_inventory_stowed.json")
    _source_stack(source, output_dir / "01_BASELINE_AXIAL_SIDE_SECTION.png")
    _new_stack(short, output_dir / "02_CORRECTED_AXIAL_SIDE_SECTION.png")
    _overlay(source, short, output_dir / "03_BASELINE_NEW_AXIAL_OVERLAY.png")
    _powertrain(short, output_dir / "05_AFT_EXTENDING_POWERTRAIN.png")
    _system_stowed(short, output_dir / "07_SHORTENED_STOWED_SYSTEM.png")
    _system_deployed(short, output_dir / "08_SHORTENED_DEPLOYED_SYSTEM.png")
