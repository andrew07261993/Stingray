#!/usr/bin/env python3
"""Export every frozen SHORT14 unique part as neutral/native CAD plus CAD render evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import textwrap
from collections import defaultdict
from pathlib import Path
from typing import Any

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_r2
import short14_external_buoy_build as short14


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "short14_external_buoy"
OUT = ROOT / "work" / "complete_product_definition" / "02_PART_DEFINITIONS"
NEUTRAL = OUT / "neutral_ap242"
NATIVE = OUT / "native_brep"
RENDERS = OUT / "renders"
STATUS = "DEVELOPMENTAL PART DEFINITION - NOT RELEASED FOR FABRICATION OR PROCUREMENT"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value: str, limit: int = 120) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_.-")
    return (cleaned or "UNNAMED")[:limit]


def bbox(shape: cq.Shape) -> dict[str, float]:
    box = shape.BoundingBox()
    return {
        "xmin": box.xmin,
        "xmax": box.xmax,
        "ymin": box.ymin,
        "ymax": box.ymax,
        "zmin": box.zmin,
        "zmax": box.zmax,
    }


def export_ap242(part: Any, state: str, path: Path) -> None:
    assembly = cq.Assembly(name=f"{slug(part.final_display_name, 96)}_{state}_PART")
    assembly.add(
        part.shape,
        name=f"{slug(part.final_display_name, 96)}_{state}_LOCAL_DEFINITION",
        color=build_r2.g.COLORS.get(part.color_key, build_r2.g.COLORS["steel"]),
    )
    build_r2.export_ap242(assembly, path)
    try:
        build_r2.name_assembly_usage_occurrences(path)
    except RuntimeError:
        pass


def render_part(part: Any, state: str, path: Path) -> None:
    vertices, triangles = part.shape.tessellate(0.35)
    xyz = [vertex.toTuple() for vertex in vertices]
    polygons = [[xyz[index] for index in triangle] for triangle in triangles]
    xs, ys, zs = zip(*xyz)
    centers = [
        (min(xs) + max(xs)) / 2.0,
        (min(ys) + max(ys)) / 2.0,
        (min(zs) + max(zs)) / 2.0,
    ]
    spans = [max(max(xs) - min(xs), 1.0), max(max(ys) - min(ys), 1.0), max(max(zs) - min(zs), 1.0)]
    views = [
        ("ISOMETRIC", 24, -45),
        ("FRONT", 0, -90),
        ("RIGHT", 0, 0),
        ("TOP", 90, -90),
    ]
    fig = plt.figure(figsize=(12, 8), dpi=150, facecolor="white")
    for position, (label, elevation, azimuth) in enumerate(views, start=1):
        axis = fig.add_subplot(2, 2, position, projection="3d")
        mesh = Poly3DCollection(
            polygons,
            facecolor="#6DCBF4",
            edgecolor="#26323A",
            linewidth=0.12,
            alpha=0.92,
        )
        axis.add_collection3d(mesh)
        pad = 0.12
        axis.set_xlim(centers[0] - spans[0] * (0.5 + pad), centers[0] + spans[0] * (0.5 + pad))
        axis.set_ylim(centers[1] - spans[1] * (0.5 + pad), centers[1] + spans[1] * (0.5 + pad))
        axis.set_zlim(centers[2] - spans[2] * (0.5 + pad), centers[2] + spans[2] * (0.5 + pad))
        axis.set_box_aspect(spans)
        axis.view_init(elev=elevation, azim=azimuth)
        axis.set_axis_off()
        axis.text2D(
            0.02,
            0.96,
            label,
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            color="#0F172A",
            va="top",
        )
    fig.suptitle(
        f"{part.part_number} | {state}",
        fontsize=15,
        fontweight="bold",
        x=0.03,
        ha="left",
    )
    fig.text(
        0.03,
        0.945,
        textwrap.shorten(part.final_display_name.replace("_", " "), width=150, placeholder="..."),
        fontsize=9,
        color="#334155",
    )
    fig.text(
        0.03,
        0.030,
        f"BOUNDING SIZE: {spans[0]:.3f} x {spans[1]:.3f} x {spans[2]:.3f} mm | "
        f"MASS: {part.resolved_mass():.6f} kg | {part.manufacturer} | {part.material}",
        fontsize=7,
        color="#334155",
    )
    fig.text(0.03, 0.012, STATUS, fontsize=7, color="#7F1D1D", fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def relative(path: Path) -> str:
    return path.resolve().relative_to(OUT.resolve()).as_posix()


def main() -> None:
    for directory in (NEUTRAL, NATIVE, RENDERS):
        directory.mkdir(parents=True, exist_ok=True)

    print("Building STOWED and DEPLOYED part catalogs", flush=True)
    builders = {state: short14.build_short_state(state) for state in ("STOWED", "DEPLOYED")}
    short14._harmonize_pair_intentional_fits(builders["STOWED"], builders["DEPLOYED"])
    inventories = {
        state: json.loads((SOURCE / f"authoring_inventory_{state.lower()}.json").read_text(encoding="utf-8"))
        for state in ("STOWED", "DEPLOYED")
    }
    identities = {state: set(builder.catalog.parts) for state, builder in builders.items()}
    if identities["STOWED"] != identities["DEPLOYED"]:
        raise RuntimeError("STOWED and DEPLOYED part identities do not reconcile")
    if len(identities["STOWED"]) != 92:
        raise RuntimeError(f"Expected 92 unique part definitions, found {len(identities['STOWED'])}")

    occurrence_lookup: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for occurrence in inventories["STOWED"]["occurrences"]:
        occurrence_lookup[occurrence["part_number"]].append(occurrence)
    deployed_by_occurrence = {
        occurrence["occurrence_id"]: occurrence for occurrence in inventories["DEPLOYED"]["occurrences"]
    }
    flexible_part_numbers = {
        deployed_by_occurrence[occurrence_id]["part_number"]
        for occurrence_id in inventories["DEPLOYED"]["flexible_occurrence_ids"]
        if occurrence_id in deployed_by_occurrence
    }

    records: list[dict[str, Any]] = []
    identities_sorted = sorted(identities["STOWED"])
    export_count = len(identities_sorted) + len(flexible_part_numbers)
    progress = 0
    for part_number in identities_sorted:
        states = ["STOWED"] + (["DEPLOYED"] if part_number in flexible_part_numbers else [])
        for state in states:
            progress += 1
            part = builders[state].catalog.parts[part_number]
            stem = slug(f"{part_number}__{state}")
            step_path = NEUTRAL / f"{stem}__LOCAL_AP242.step"
            brep_path = NATIVE / f"{stem}__LOCAL_OCCT.brep"
            render_path = RENDERS / f"{stem}__FOUR_VIEW.png"
            export_ap242(part, state, step_path)
            cq.exporters.export(part.shape, str(brep_path), exportType="BREP")
            render_part(part, state, render_path)
            locations = occurrence_lookup.get(part_number, [])
            records.append(
                {
                    "part_number": part_number,
                    "physical_title": part.final_display_name,
                    "state_definition": state,
                    "revision": part.revision,
                    "description": part.description,
                    "material": part.material,
                    "finish": part.finish,
                    "make_buy": part.make_buy,
                    "manufacturer": part.manufacturer,
                    "cad_classification": part.cad_classification,
                    "mass_kg": part.resolved_mass(),
                    "volume_mm3": part.shape.Volume(),
                    "solid_count": len(part.shape.Solids()),
                    "face_count": len(part.shape.Faces()),
                    "bbox_mm": json.dumps(bbox(part.shape), separators=(",", ":")),
                    "neutral_ap242_path": relative(step_path),
                    "neutral_ap242_bytes": step_path.stat().st_size,
                    "neutral_ap242_sha256": sha256(step_path),
                    "native_brep_path": relative(brep_path),
                    "native_brep_bytes": brep_path.stat().st_size,
                    "native_brep_sha256": sha256(brep_path),
                    "four_view_render_path": relative(render_path),
                    "four_view_render_bytes": render_path.stat().st_size,
                    "four_view_render_sha256": sha256(render_path),
                    "installed_location_reference": " | ".join(
                        f"{row['occurrence_id']} in {row.get('display_parent_path', row.get('parent_path', ''))}"
                        for row in locations
                    ),
                    "installed_location_image": "NOT GENERATED - REGISTERED BY OCCURRENCE/BBOX; SYSTEM VIEWS PROVIDED",
                    "section_cutaway_status": "NOT PROVIDED - RELEASE DRAWING/ANALYSIS RELEVANCE NOT ESTABLISHED",
                    "release_status": STATUS,
                }
            )
            print(f"[{progress:03d}/{export_count:03d}] {state} {part_number}", flush=True)

    manifest_path = OUT / "PART_DEFINITION_MANIFEST.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "status": STATUS,
        "unique_part_definitions": len(identities_sorted),
        "flexible_state_variant_definitions": len(flexible_part_numbers),
        "exported_definition_rows": len(records),
        "neutral_ap242_count": len(list(NEUTRAL.glob("*.step"))),
        "native_brep_count": len(list(NATIVE.glob("*.brep"))),
        "render_count": len(list(RENDERS.glob("*.png"))),
        "manifest_sha256": sha256(manifest_path),
        "limitations": [
            "Installed locations are registered by occurrence and authoring-inventory bounds; per-part installed-location images are not generated.",
            "Sections/cutaways are not fabricated without approved analysis and drawing relevance.",
            "Dimension-controlled proxies and developmental softgood envelopes remain explicit and non-release.",
            "Neutral STEP byte reproducibility is subject to the recorded OCCT presentation-order exception.",
        ],
    }
    (OUT / "PART_DEFINITION_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (OUT / "PART_RENDER_CATALOG.md").write_text(
        "# Individual Part Render Catalog\n\n"
        f"Status: **{STATUS}**\n\n"
        f"The catalog contains {summary['render_count']} CAD-derived four-view PNGs for "
        f"{summary['unique_part_definitions']} unique definitions plus "
        f"{summary['flexible_state_variant_definitions']} deployed flexible-state variants.  "
        "Every row in `PART_DEFINITION_MANIFEST.csv` identifies material, finish, manufacturer/part "
        "number, neutral/native CAD, scale bounds, mass, and installed occurrences.\n\n"
        "No image-generation artwork or separately recreated geometry is used.  The absence of per-part "
        "installed-location images and analysis-specific cutaways is a documented non-release limitation.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
