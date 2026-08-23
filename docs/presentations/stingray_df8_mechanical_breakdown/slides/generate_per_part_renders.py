#!/usr/bin/env python3
"""Generate deterministic per-part PNGs from the authoritative DF8 B-rep source.

This utility is intentionally read-only with respect to the CAD checkpoint.  It
imports the checkpoint's scripted CadQuery/OCCT model, rebuilds the two endpoint
states in memory, and tessellates each qualifying PartDef directly from its
exact source-backed shape.  It does not infer or redraw geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


RENDERER_VERSION = "STINGRAY-DF8-PER-PART-RENDERER-1.0"
FIGURE_SIZE_IN = (8.0, 6.0)
FIGURE_DPI = 200
CAMERA_ELEV_DEG = 23.0
CAMERA_AZIM_DEG = -55.0
BODY_COLOR = "#AEB7BE"
EDGE_COLOR = "#3F4A52"
LIGHT_VECTOR = np.asarray((-0.35, -0.55, 0.76), dtype=float)
LIGHT_VECTOR /= np.linalg.norm(LIGHT_VECTOR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Authoritative DF8 checkpoint root containing work/r2_source.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Documentation repository root receiving generated artifacts.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Output directory relative to or within the documentation repo.",
    )
    return parser.parse_args()


def run_git(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_filename(value: str) -> str:
    cooked = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cooked.strip("._") or "UNNAMED_PART"


def is_standard_fastener(part: Any) -> bool:
    """Exclude only catalog fastening hardware, never functional pins/clips."""
    description = str(part.description).upper()
    catalog_fastener = re.search(r"\b(SCREW|BOLT|NUT|RIVET|STANDARD WASHER)\b", description)
    return str(part.make_buy).upper() == "BUY" and bool(catalog_fastener)


def is_o_ring(part: Any) -> bool:
    token = f"{part.part_number} {part.description}".upper()
    return bool(re.search(r"\bO[- ]?RING\b", token))


def classify_subsystem(part_number: str, description: str, occurrence_ids: list[str]) -> str:
    token = " ".join((part_number, description, *occurrence_ids)).upper()

    explicit = {
        "HDP-3-8-A1": "Arm deployment / activation",
        "HTP-3-30-A1": "Body structure",
        "HEC-10-A4": "Gas / inflation path",
        "ROTOR-CLIP-DC-4SS": "Arm deployment / activation",
        "GN-615.3-M3-KN-PFB": "Body ejection / buoy extraction",
        "WP04-AFT-RAIL-SUPPORT-R2": "Body ejection / buoy extraction",
    }
    if part_number in explicit:
        return explicit[part_number]
    if re.search(
        r"^DF8-R2-(NOSE|BALLAST|FWD-SHELL|AFT-SHELL|FWD-LONGERON|AFT-LONGERON|"
        r"STRUCT-RING|AFT-ROUTE-RING)",
        part_number.upper(),
    ):
        return "Body structure"
    if re.search(r"WATER|V80040|BOBBIN", token):
        return "Water activation"
    if re.search(r"HARNESS|RECOVERY|TETHER|THIMBLE|HARDPOINT|WP04-HST|WP04-RHP", token):
        return "Load path / recovery attachment"
    if re.search(r"BUOY-GORE|EJECTOR|WP04-(FOL|FOLLOWER|GUIDE|LATCH|SEAR|FIXED|MOVING|RB)|WP05-", token):
        return "Body ejection / buoy extraction"
    if re.search(
        r"LELAND|CO2|BOOSTER|CARTRIDGE|PUNCTURE|COLLECTION-MANIFOLD|FULLFLOW|SS-CHS2|"
        r"GAS-MAIN|PILOT-LINE|MANIFOLD-FEED|BOWDEN|WP04-FULLFLOW|MANIFOLD-BRACKET",
        token,
    ):
        return "Gas / inflation path"
    if re.search(
        r"ARM|PIVOT|CROSSHEAD|SHORT-LINK|LINK-PIN|ACTUATOR|GS-19|GS19|HBD|BACKUP-SPRING|"
        r"AUTO-LOCK|LOCK-DOG|STOW-DOG|FIXED-STOP|STOP-PAD|FIXED-SECTOR|ROUTED-LONGERON",
        token,
    ):
        return "Arm deployment / activation"
    if re.search(r"NOSE|BALLAST|SHELL|LONGERON|STRUCT-RING|AFT-ROUTE-RING", token):
        return "Body structure"
    return "Shared retention / interfaces"


def function_summary(part_number: str, description: str, make_buy: str, subsystem: str,
                     occurrence_ids: list[str], connection_types: list[str]) -> str:
    token = f"{part_number} {description}".upper()
    if make_buy.upper() == "BUY" and re.search(
        r"\b(SCREW|BOLT|NUT|RIVET|STANDARD WASHER)\b", description.upper()
    ):
        return "Provides standard threaded fastening; excluded from the render scope."
    if re.search(r"\bO[- ]?RING\b", token):
        return "Provides an O-ring seal; excluded from the render scope."
    if "NOSE" in token:
        return "Defines the forward penetrator geometry and closes the forward load path."
    if "BALLAST" in token:
        return "Concentrates forward mass and supports the controlled center-of-gravity placement."
    if "SHELL" in token:
        return "Closes the body envelope while carrying the modeled apertures and local interfaces."
    if "LONGERON" in token or "STRUCT-RING" in token or "AFT-ROUTE-RING" in token:
        return "Maintains the slender body geometry and transfers structural load between body stations."
    if "WATER-INLET" in token:
        return "Admits water through the screened body port to the water-sensitive trigger housing."
    if "WATER-BOBBIN" in token or "V80040" in token:
        return "Provides the source-controlled water-sensitive element in the activation chain."
    if "WATER-TRIGGER" in token:
        return "Houses and locates the water-sensitive trigger components at the controlled inlet."
    if "LELAND" in token or "CO2 CARTRIDGE" in token:
        return "Stores the modeled inflation-gas charge for puncture and downstream distribution."
    if "PUNCTURE" in token:
        return "Opens the cartridge at activation and passes gas into the collection path."
    if "BOOSTER-RESERVOIR" in token:
        return "Provides distributed gas-storage volume along the forward body."
    if "CHECK VALVE" in token or "SS-CHS2" in token:
        return "Isolates the booster branch and enforces one-way flow in the modeled gas path."
    if "MANIFOLD" in token:
        return "Collects or distributes flow between the cartridge, valve, and downstream route interfaces."
    if any(value in token for value in ("GAS-MAIN", "PILOT-LINE", "BOWDEN", "COLLECTION-LINE")):
        return "Carries the modeled pressure or mechanical-control path between terminated interfaces."
    if "GS-19" in token or "GS19" in token:
        return "Provides the primary powered stroke into the common crosshead linkage."
    if "HBD" in token:
        return "Damps crosshead motion to control deployment rate without replacing the positive stops."
    if "BACKUP-SPRING" in token:
        return "Provides the independent mechanical bias path acting on the common crosshead."
    if "CROSSHEAD" in token:
        return "Combines actuator, damper, and spring inputs and drives all three arm-link pairs."
    if "SHORT-LINK" in token:
        return "Transfers crosshead translation into arm-root rotation through the paired clevis joints."
    if "ARM-BLADE" in token:
        return "Provides the 733.806 mm deployment member and its controlled root/stop interfaces."
    if "PIVOT" in token:
        return "Supports the arm-root revolute joint and its double-shear retention stack."
    if "FIXED-STOP" in token or "STOP-PAD" in token:
        return "Defines the mechanical deployment limit and receives the positive lock interface."
    if "AUTO-LOCK" in token or "LOCK-DOG" in token:
        return "Engages the deployed stop system to retain an arm independently after deployment."
    if "STOW-DOG" in token:
        return "Retains the arm in the transport position and releases through the controlled mechanism."
    if "BUOY-GORE" in token:
        return "Forms one source-defined panel of the eight-gore 60 L buoy envelope."
    if "EJECTOR-SPRING" in token:
        return "Stores the mechanical energy that drives the aft follower and buoy package outward."
    if any(value in token for value in ("FOLLOWER", "GUIDE-RAIL", "GUIDE-SLEEVE", "REACTION BULKHEAD")):
        return "Guides and reacts the ejector/follower stroke while controlling rotation and alignment."
    if "LATCH" in token or "SEAR" in token:
        return "Retains the follower before activation and releases it through the source-defined sear chain."
    if "DOOR" in token or "SERVICE-THROAT" in token or "HINGE" in token:
        return "Closes and services the aft ejection opening while remaining captive during deployment."
    if "HARNESS" in token:
        return "Transfers buoy load into the modeled structural terminal and recovery connection."
    if any(value in token for value in ("TETHER", "THIMBLE", "RECOVERY-PIN", "RECOVERY-E-RING", "HARDPOINT")):
        return "Carries or retains the recovery load path between the buoy harness and rigid body hardpoint."
    if connection_types:
        types = ", ".join(value.replace("_", " ").lower() for value in connection_types[:2])
        return f"Provides the modeled {description.lower()}; registered interfaces use {types}."
    count = len(occurrence_ids)
    return f"Provides the modeled {description.lower()} in {count} occurrence{'s' if count != 1 else ''}."


def choose_geometry_state(part_number: str, description: str) -> str:
    token = f"{part_number} {description}".upper()
    if re.search(r"BUOY-GORE|HARNESS|RECOVERY-TETHER|DOOR-LANYARD", token):
        return "DEPLOYED"
    return "STOWED"


def tessellation_tolerance(shape: Any) -> float:
    bbox = shape.BoundingBox()
    diagonal = math.sqrt(bbox.xlen ** 2 + bbox.ylen ** 2 + bbox.zlen ** 2)
    return max(0.01, min(0.35, diagonal / 500.0))


def axis_permutation(vertices: np.ndarray) -> tuple[list[int], str]:
    spans = np.ptp(vertices, axis=0)
    order = sorted(range(3), key=lambda index: (-float(spans[index]), index))
    # Longest dimension is horizontal, shortest is camera depth, middle is vertical.
    permutation = [order[0], order[2], order[1]]
    axes = "xyz"
    note = f"source axes {axes} -> display axes {''.join(axes[index] for index in permutation)}"
    return permutation, note


def render_shape(shape: Any, output_path: Path, part_number: str, description: str,
                 make_buy: str, subsystem: str, source_state: str) -> dict[str, Any]:
    tolerance = tessellation_tolerance(shape)
    vertices_raw, triangles_raw = shape.tessellate(tolerance)
    vertices = np.asarray([vertex.toTuple() for vertex in vertices_raw], dtype=float)
    triangles = np.asarray(triangles_raw, dtype=int)
    if len(vertices) < 3 or len(triangles) < 1:
        raise RuntimeError("tessellation returned no drawable faces")

    permutation, permutation_note = axis_permutation(vertices)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
    display_vertices = (vertices - center)[:, permutation]
    polygons = display_vertices[triangles]

    edge_a = polygons[:, 1, :] - polygons[:, 0, :]
    edge_b = polygons[:, 2, :] - polygons[:, 0, :]
    normals = np.cross(edge_a, edge_b)
    magnitudes = np.linalg.norm(normals, axis=1)
    magnitudes[magnitudes == 0.0] = 1.0
    normals /= magnitudes[:, None]
    illumination = 0.58 + 0.42 * np.clip(np.abs(normals @ LIGHT_VECTOR), 0.0, 1.0)
    base = np.asarray(to_rgb(BODY_COLOR), dtype=float)
    facecolors = np.clip(illumination[:, None] * base[None, :], 0.0, 1.0)

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })
    fig = plt.figure(figsize=FIGURE_SIZE_IN, dpi=FIGURE_DPI, facecolor="white")
    ax = fig.add_axes((0.02, 0.17, 0.96, 0.80), projection="3d")
    ax.set_proj_type("ortho")
    collection = Poly3DCollection(
        polygons,
        facecolors=facecolors,
        edgecolors=EDGE_COLOR,
        linewidths=0.035 if len(polygons) > 6000 else 0.10,
        antialiased=True,
    )
    ax.add_collection3d(collection)

    minima = display_vertices.min(axis=0)
    maxima = display_vertices.max(axis=0)
    centers = (minima + maxima) / 2.0
    spans = np.maximum(maxima - minima, 1.0e-6)
    max_span = float(max(spans))
    camera_spans = np.maximum(spans, max_span * 0.075)
    pad = 1.10
    ax.set_xlim(centers[0] - camera_spans[0] * pad / 2.0, centers[0] + camera_spans[0] * pad / 2.0)
    ax.set_ylim(centers[1] - camera_spans[1] * pad / 2.0, centers[1] + camera_spans[1] * pad / 2.0)
    ax.set_zlim(centers[2] - camera_spans[2] * pad / 2.0, centers[2] + camera_spans[2] * pad / 2.0)
    ax.set_box_aspect(camera_spans)
    ax.view_init(elev=CAMERA_ELEV_DEG, azim=CAMERA_AZIM_DEG)
    ax.set_axis_off()

    fig.add_artist(plt.Line2D((0.04, 0.96), (0.145, 0.145), transform=fig.transFigure,
                              color="#CBD2D8", linewidth=0.8))
    fig.text(0.04, 0.112, part_number, fontsize=14.5, fontweight="bold", color="#152635")
    wrapped = textwrap.fill(description, width=74)
    fig.text(0.04, 0.058, wrapped, fontsize=9.6, color="#33434F", va="center")
    fig.text(0.96, 0.108, make_buy, fontsize=11.0, fontweight="bold", color="#006D77", ha="right")
    fig.text(0.96, 0.069, subsystem, fontsize=8.9, color="#52626D", ha="right")
    fig.text(0.96, 0.031, f"Exact source-backed B-rep | {source_state}", fontsize=7.8,
             color="#6B7780", ha="right")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        dpi=FIGURE_DPI,
        facecolor="white",
        edgecolor="none",
        metadata={"Software": RENDERER_VERSION},
    )
    plt.close(fig)
    return {
        "tessellation_tolerance_mm": tolerance,
        "triangle_count": int(len(triangles)),
        "camera_view_note": (
            f"Orthographic hero view; {permutation_note}; fixed elev={CAMERA_ELEV_DEG:.1f} deg, "
            f"azim={CAMERA_AZIM_DEG:.1f} deg; fixed neutral Lambert lighting."
        ),
    }


def relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_manifests(rows: list[dict[str, Any]], manifest_dir: Path) -> None:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / "per_part_render_manifest.json"
    csv_path = manifest_dir / "per_part_render_manifest.csv"
    json_path.write_text(
        json.dumps(rows, indent=2, sort_keys=False, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    fieldnames = [
        "part_number", "part_name", "classification", "subsystem", "included",
        "exclusion_reason", "classification_rationale", "source_geometry_path",
        "render_png_path", "camera_view_note", "timestamp", "png_sha256",
        "render_status", "unrenderable_reason", "source_commit_sha", "geometry_state",
        "tessellation_tolerance_mm", "triangle_count", "occurrence_count",
        "occurrence_ids", "function_summary", "material", "manufacturer",
        "cad_classification", "volume_mm3", "solid_count", "face_count",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            cooked = dict(row)
            cooked["included"] = "true" if row["included"] else "false"
            cooked["occurrence_ids"] = ";".join(row["occurrence_ids"])
            writer.writerow({key: cooked.get(key, "") for key in fieldnames})


def main() -> int:
    args = parse_args()
    source_root = args.source_root.resolve()
    repo_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()
    source_dir = source_root / "work" / "r2_source"
    if not (source_dir / "build_r2.py").is_file():
        raise SystemExit(f"Authoritative source not found: {source_dir / 'build_r2.py'}")
    if not output_root.is_relative_to(repo_root):
        raise SystemExit("Output root must remain inside the documentation repository")

    sys.path.insert(0, str(source_dir))
    import build_r2  # pylint: disable=import-error,import-outside-toplevel

    source_commit_sha = run_git(source_root, "rev-parse", "HEAD")
    source_timestamp = run_git(source_root, "show", "-s", "--format=%cI", "HEAD")
    inventory_paths = {
        state: source_root / "work" / "final_analysis" / f"authoring_inventory_{state.lower()}.json"
        for state in ("STOWED", "DEPLOYED")
    }
    inventories = {
        state: json.loads(path.read_text(encoding="utf-8"))
        for state, path in inventory_paths.items()
    }

    print("Building authoritative STOWED endpoint in memory", flush=True)
    builders = {"STOWED": build_r2.build_state("STOWED")}
    print("Building authoritative DEPLOYED endpoint in memory", flush=True)
    builders["DEPLOYED"] = build_r2.build_state("DEPLOYED")

    part_sets = {state: set(builder.catalog.parts) for state, builder in builders.items()}
    if part_sets["STOWED"] != part_sets["DEPLOYED"]:
        raise RuntimeError("STOWED and DEPLOYED PartDef sets differ")
    if len(part_sets["STOWED"]) != 121:
        raise RuntimeError(f"Expected 121 unique PartDefs, found {len(part_sets['STOWED'])}")

    inventory_parts = {
        state: {row["part_number"]: row for row in inventory["parts"]}
        for state, inventory in inventories.items()
    }
    for state in ("STOWED", "DEPLOYED"):
        if set(inventory_parts[state]) != part_sets[state]:
            raise RuntimeError(f"{state} source-build PartDefs do not match the committed inventory")

    occurrences_by_part: dict[str, list[str]] = defaultdict(list)
    part_by_occurrence: dict[str, str] = {}
    for occurrence in builders["STOWED"].occurrences:
        occurrences_by_part[occurrence.part_number].append(occurrence.occurrence_id)
        part_by_occurrence[occurrence.occurrence_id] = occurrence.part_number
    connection_types_by_part: dict[str, set[str]] = defaultdict(set)
    for connection in builders["STOWED"].connections:
        for occurrence_id in (connection.occurrence_id, connection.mate_occurrence_id):
            part_number = part_by_occurrence.get(occurrence_id)
            if part_number:
                connection_types_by_part[part_number].add(connection.connection_type)

    renders_dir = output_root / "renders"
    manifest_dir = output_root / "manifests"
    rows: list[dict[str, Any]] = []
    for index, part_number in enumerate(sorted(part_sets["STOWED"]), start=1):
        base_part = builders["STOWED"].catalog.parts[part_number]
        occurrence_ids = sorted(occurrences_by_part.get(part_number, []))
        subsystem = classify_subsystem(part_number, base_part.description, occurrence_ids)
        excluded_fastener = is_standard_fastener(base_part)
        excluded_o_ring = is_o_ring(base_part)
        included = not excluded_fastener and not excluded_o_ring
        exclusion_reason = ""
        rationale = "Included: unique modeled functional part definition; inclusion favored when ambiguous."
        if excluded_fastener:
            exclusion_reason = "standard fastener"
            rationale = "Excluded: catalog screw/bolt/nut/rivet/standard washer used as fastening hardware."
        elif excluded_o_ring:
            exclusion_reason = "O-ring"
            rationale = "Excluded: modeled O-ring definition."

        geometry_state = choose_geometry_state(part_number, base_part.description)
        part = builders[geometry_state].catalog.parts[part_number]
        committed = inventory_parts[geometry_state][part_number]
        volume_delta = abs(float(part.shape.Volume()) - float(committed["volume_mm3"]))
        volume_limit = max(1.0e-6, abs(float(committed["volume_mm3"])) * 1.0e-9)
        if volume_delta > volume_limit:
            raise RuntimeError(
                f"{part_number} {geometry_state} volume differs from committed authoring inventory: "
                f"delta={volume_delta} mm^3"
            )

        classification = str(part.make_buy).upper()
        filename = f"{classification}_{safe_filename(part_number)}.png"
        output_path = renders_dir / filename
        render_path = ""
        png_hash = ""
        camera_note = ""
        tolerance: float | str = ""
        triangle_count: int | str = ""
        render_status = "EXCLUDED"
        unrenderable_reason = ""
        if included:
            try:
                metadata = render_shape(
                    part.shape, output_path, part_number, part.description, classification,
                    subsystem, geometry_state,
                )
                render_path = relative_path(output_path, repo_root)
                png_hash = sha256(output_path)
                camera_note = metadata["camera_view_note"]
                tolerance = metadata["tessellation_tolerance_mm"]
                triangle_count = metadata["triangle_count"]
                render_status = "RENDERED"
                print(f"[{index:03d}/121] rendered {filename}", flush=True)
            except Exception as exc:  # Continue and record every unrenderable source part.
                render_status = "ERROR"
                unrenderable_reason = f"{type(exc).__name__}: {exc}"
                print(f"[{index:03d}/121] ERROR {part_number}: {unrenderable_reason}", flush=True)
        else:
            camera_note = f"Not rendered: {exclusion_reason}."
            print(f"[{index:03d}/121] excluded {part_number}: {exclusion_reason}", flush=True)

        generation_source = (
            f"{(source_dir / 'build_r2.py').as_posix()}::build_state({geometry_state})"
            f"/PartCatalog[{part_number}].shape @ {source_commit_sha}"
        )
        row = {
            "part_number": part_number,
            "part_name": part.description,
            "classification": classification,
            "subsystem": subsystem,
            "included": included,
            "exclusion_reason": exclusion_reason,
            "classification_rationale": rationale,
            "source_geometry_path": generation_source,
            "render_png_path": render_path,
            "camera_view_note": camera_note,
            "timestamp": source_timestamp,
            "png_sha256": png_hash,
            "render_status": render_status,
            "unrenderable_reason": unrenderable_reason,
            "source_commit_sha": source_commit_sha,
            "geometry_state": geometry_state,
            "tessellation_tolerance_mm": tolerance,
            "triangle_count": triangle_count,
            "occurrence_count": len(occurrence_ids),
            "occurrence_ids": occurrence_ids,
            "function_summary": function_summary(
                part_number, part.description, part.make_buy, subsystem, occurrence_ids,
                sorted(connection_types_by_part.get(part_number, set())),
            ),
            "material": part.material,
            "manufacturer": part.manufacturer,
            "cad_classification": part.cad_classification,
            "volume_mm3": float(part.shape.Volume()),
            "solid_count": len(part.shape.Solids()),
            "face_count": len(part.shape.Faces()),
        }
        rows.append(row)
        write_manifests(rows, manifest_dir)

    write_manifests(rows, manifest_dir)
    counts = Counter(
        "rendered" if row["render_status"] == "RENDERED" else row["exclusion_reason"] or "error"
        for row in rows
    )
    print(json.dumps({"part_definitions": len(rows), "counts": counts}, indent=2), flush=True)
    errors = [row for row in rows if row["render_status"] == "ERROR"]
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
