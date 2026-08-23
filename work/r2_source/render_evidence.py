#!/usr/bin/env python3
"""Render controlled technical evidence views from the frozen R2 authoring model."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_r2


OUT = build_r2.ROOT / "work" / "r2_evidence_views"

PALETTE = {
    "arm": "#91A8BA", "structure": "#657A8C", "route": "#00A6A6",
    "moving": "#D97706", "spring": "#E95D0F", "softgood": "#E44C3A",
    "harness": "#263B54", "hardware": "#C7CDD3", "water": "#1388A8",
}


def color_for(occurrence_id: str) -> str:
    if occurrence_id.startswith("ARM-"):
        return PALETTE["arm"]
    if occurrence_id.startswith(("ROUTE-", "UNION-", "WATER-")):
        return PALETTE["route"] if not occurrence_id.startswith("WATER-") else PALETTE["water"]
    if occurrence_id.startswith(("BUOY-GORE",)):
        return PALETTE["softgood"]
    if occurrence_id.startswith(("HARNESS-", "RECOVERY-TETHER", "WP05-DOOR-LANYARD")):
        return PALETTE["harness"]
    if "SPRING" in occurrence_id:
        return PALETTE["spring"]
    if occurrence_id.startswith(("CROSSHEAD", "WP04-FOLLOWER", "LOCK-DOG", "STOW-DOG")):
        return PALETTE["moving"]
    if occurrence_id.startswith(("FWD-", "AFT-", "FIXED-SECTOR", "BODY-HARDPOINT", "WP04-REACTION", "WP05-SERVICE")):
        return PALETTE["structure"]
    return PALETTE["hardware"]


def group_label(occurrence_id: str) -> str:
    for prefix, label in (
        ("BUOY-GORE", "8 RF-welded buoy gores"),
        ("HARNESS-LEG", "4 stitched harness legs"),
        ("ARM-", "analytic arm"),
        ("ROUTE-", "formed route"),
        ("UNION-", "bulkhead union"),
        ("PIVOT-", "pivot hardware"),
        ("LINK-", "link hardware"),
    ):
        if occurrence_id.startswith(prefix):
            return label
    return occurrence_id


def render(builder, occurrence_ids: list[str], filename: str, title: str,
           elev: float, azim: float, tolerance: float = 1.2,
           view_bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]] | None = None) -> None:
    fig = plt.figure(figsize=(12, 8), dpi=170, facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    all_xyz: list[tuple[float, float, float]] = []
    legend: dict[str, str] = {}
    for occurrence_id in occurrence_ids:
        shape = builder.global_shapes.get(occurrence_id)
        if shape is None:
            continue
        try:
            vertices, triangles = shape.tessellate(tolerance)
        except Exception:
            continue
        xyz = [v.toTuple() for v in vertices]
        all_xyz.extend(xyz)
        polys = [[xyz[i] for i in tri] for tri in triangles]
        color = color_for(occurrence_id)
        alpha = 0.28 if "SHELL" in occurrence_id else (0.60 if occurrence_id.startswith("BUOY-GORE") else 0.86)
        mesh = Poly3DCollection(polys, facecolor=color, edgecolor="#26323A",
                                linewidth=0.08, alpha=alpha)
        ax.add_collection3d(mesh)
        legend.setdefault(group_label(occurrence_id), color)
    if not all_xyz:
        raise RuntimeError(f"No renderable occurrences for {filename}")
    xs, ys, zs = zip(*all_xyz)
    bounds = list(view_bounds) if view_bounds is not None else [
        (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))
    ]
    centers = [(lo + hi) / 2.0 for lo, hi in bounds]
    spans = [max(hi - lo, 1.0) for lo, hi in bounds]
    pad = 0.08
    ax.set_xlim(centers[0] - spans[0] * (0.5 + pad), centers[0] + spans[0] * (0.5 + pad))
    ax.set_ylim(centers[1] - spans[1] * (0.5 + pad), centers[1] + spans[1] * (0.5 + pad))
    ax.set_zlim(centers[2] - spans[2] * (0.5 + pad), centers[2] + spans[2] * (0.5 + pad))
    ax.set_box_aspect(spans)
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_zlabel("Z [mm]")
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=18)
    ax.grid(True, linewidth=0.25, alpha=0.5)
    handles = [Patch(facecolor=color, edgecolor="#26323A", label=label) for label, color in legend.items()]
    ax.legend(handles=handles, loc="upper right", fontsize=7, framealpha=0.92, ncol=1)
    fig.text(0.015, 0.015,
             "Technical evidence view generated from frozen scripted B-rep source; not Creo evidence. Units: mm.",
             fontsize=7, color="#3A4650")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(OUT / filename, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stowed = build_r2.build_state("STOWED")
    deployed = build_r2.build_state("DEPLOYED")
    views = [
        (deployed, ["BODY-HARDPOINT-001", "TETHER-THIMBLE-BODY", "RECOVERY-PIN-BODY",
                    "RECOVERY-PIN-CLIP-BODY", "RECOVERY-TETHER-001"],
         "AFTER_IMAGE_01_PRODUCT_BOUNDARY.png", "Image 1 correction — controlled product boundary at recovery hardpoint", 18, -58),
        (deployed, [*[f"BUOY-GORE-{i:02d}" for i in range(1, 9)], "HARNESS-BAND-1", "HARNESS-BAND-2",
                    "HARNESS-LEG-XP", "HARNESS-LEG-XN", "HARNESS-LEG-YP", "HARNESS-LEG-YN",
                    "HARNESS-TERMINAL-001", "RECOVERY-TETHER-001", "BODY-HARDPOINT-001"],
         "AFTER_IMAGE_02_DEPLOYED_COHESION.png", "Image 2 correction — deployed buoy/harness/terminal/body chain", 16, -52, 4.0),
        (deployed, ["HARNESS-BAND-1", "HARNESS-BAND-2", "HARNESS-LEG-XP", "HARNESS-LEG-XN",
                    "HARNESS-LEG-YP", "HARNESS-LEG-YN", "HARNESS-TERMINAL-001",
                    "TETHER-THIMBLE-HARNESS", "RECOVERY-PIN-HARNESS", "RECOVERY-PIN-CLIP-HARNESS",
                    "RECOVERY-TETHER-001"],
         "AFTER_IMAGE_03_TERMINAL_CHAIN.png", "Image 3 correction — occurrence-specific harness terminal and tether joint", 10, -35),
        (stowed, ["FWD-SHELL-001", "WATER-INLET-001", "WATER-TRIGGER-HSG-001", "WATER-BOBBIN-001"],
         "AFTER_IMAGE_04_WATER_PORT.png", "Image 4 correction — controlled shell gland and reamed trigger-housing port", 12, 34),
        (stowed, ["FWD-RING-02", "FIXED-SECTOR-1", "FIXED-SECTOR-2", "FIXED-SECTOR-3",
                  "PIVOT-CARRIER-1", "PIVOT-CARRIER-2", "PIVOT-CARRIER-3",
                  "ROUTE-GAS-MAIN-001", "ROUTE-PILOT-LINE-001", "ROUTE-BOWDEN-SHEATH-001",
                  "ROUTE-BOWDEN-WIRE-001", "BACKUP-SPRING-001", "CROSSHEAD-001"],
         "AFTER_IMAGE_05_ROOT_ROUTE_CLEARANCE.png", "Image 5 correction — routed ring passages clear the spring/mechanism envelope", 18, -62),
        (stowed, ["CROSSHEAD-001", *[f"LINK-{a}-{l}" for a in range(1, 4) for l in (1, 2)],
                  *[f"LINK-PIN-{a}-{e}" for a in range(1, 4) for e in ("BELL", "CROSSHEAD")],
                  "GS19-ROD-001", "HBD-ROD-001", "BACKUP-SPRING-MOVING-SEAT"],
         "AFTER_IMAGE_06_CROSSHEAD_RETENTION.png", "Image 6 correction — captive crosshead, links, and retained clevis pins", 22, -45),
        (deployed, ["ARM-1", "PIVOT-CARRIER-1", "PIVOT-PIN-1", "PIVOT-BUSH-1-1", "PIVOT-BUSH-1-2",
                    "PIVOT-WASHER-1-1", "PIVOT-WASHER-1-2", "PIVOT-CLIP-1", "LINK-1-1", "LINK-1-2",
                    "FIXED-STOP-1", "LOCK-DOG-1", "LOCK-SPRING-1"],
         "AFTER_IMAGE_07_ARM_ROOT.png", "Image 7 correction — analytic arm root with double-shear pivot and lock", 12, -62,
         0.45, ((-5.0, 55.0), (-22.0, 22.0), (875.0, 935.0))),
        (stowed, ["BACKUP-SPRING-001", "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT",
                  "BACKUP-SPRING-MOVING-SEAT", "GS19-BODY-001", "GS19-ROD-001", "GS19-FIXED-YOKE",
                  "HBD-BODY-001", "HBD-ROD-001", "HBD-FIXED-YOKE", "CROSSHEAD-001"],
         "AFTER_IMAGE_08_ACTUATOR_SPRING.png", "Image 8 correction — separated actuator/damper/spring corridors", 16, -40),
        (deployed, ["AFT-SHELL-001", "WP04-FOLLOWER-001", "WP04-GUIDE-RAIL-1", "WP04-GUIDE-RAIL-2",
                    "WP04-GUIDE-RAIL-3", "WP04-LATCH-001", "WP04-SEAR-001", "WP04-SEAR-CLIP-001",
                    "UNION-GAS-MAIN-WP04", "UNION-PILOT-LINE-WP04", "UNION-BOWDEN-SHEATH-WP04",
                    "UNION-BOWDEN-WIRE-WP04"],
         "AFTER_IMAGE_09_ROUTE_AND_SEAR.png", "Image 9 correction — terminated routes and radial retained sear", 18, -30),
    ]
    for view in views:
        render(*view)

    closest_before = [
        "DEPLOYED_ISOMETRIC.png", "DEPLOYED_ISOMETRIC.png", "DEPLOYED_CROSS_SECTION.png",
        "STOWED_CROSS_SECTION.png", "ARM_ROOT_DETAIL.png", "CROSSHEAD_LINKAGE_DETAIL.png",
        "ARM_ROOT_DETAIL.png", "STOWED_CROSS_SECTION.png", "LOCK_DETAIL.png",
    ]
    with (OUT / "before_after_evidence_index.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["owner_image_id", "owner_binary_received", "closest_r1_package_reference_view",
                         "r2_after_view", "status", "limitation"])
        for idx, (_, _, after_name, *_rest) in enumerate(views, 1):
            writer.writerow([
                f"IMAGE-{idx:02d}", "NO",
                f"../r1_controlled_reference_views/{closest_before[idx - 1]}", after_name,
                "BLOCKED — OWNER SCREENSHOT BINARY NOT RECEIVED",
                "The commission text supplied defect descriptions, but the nine cited screenshot binaries were not present; closest controlled R1 package view is retained separately.",
            ])
    print(f"Wrote {len(views)} technical views and evidence index to {OUT}")


if __name__ == "__main__":
    sys.exit(main())
