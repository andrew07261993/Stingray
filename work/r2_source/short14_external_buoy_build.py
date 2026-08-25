#!/usr/bin/env python3
"""Author the short-14 true-forward-powertrain external-buoy AP242 pair.

The module deliberately starts from the clean ``a31fce0e`` forward-arm
builder, removes the superseded internal water/inflation/ejector architecture,
then applies a bounded occurrence/definition transformation.  Unaffected
penetrator, ballast, arm-root, kinematic, stop, lock, actuator and retention
definitions remain source-derived.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

import cadquery as cq
import numpy as np

import build_r2
import final_detail_naming
import r2_geometry as g
import r2_hierarchy
import short14_external_buoy_config as cfg


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "short14_external_buoy"
STOWED_FILE = "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step"
DEPLOYED_FILE = "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step"

TOP_FORWARD = "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY"
TOP_ARM = "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY"
TOP_AFT = "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY"
PATH_AFT_STRUCTURE = f"{TOP_AFT}/510_SHORTENED_AFT_STRUCTURE_ASSY"
PATH_PACK = f"{TOP_AFT}/520_CORDURA_BREAKAWAY_BUOY_PACK_ASSY"
PATH_INFLATION = f"{TOP_AFT}/530_BUOY_MOUNTED_INFLATION_ASSY"
PATH_TETHER = f"{TOP_AFT}/540_STRUCTURAL_RECOVERY_TETHER_ASSY"

SOURCE_ARM_PART = "DF8-R2-ARM-BLADE-001"
SHORT_ARM_PART = "DF8-SHORT14-ARM-BLADE-001"

ARM_ROUTE_REMOVALS = {
    "AFT-REPACK-SHELL-001",
    "CG-TRIM-BALLAST-001",
    "GLAND-BOWDEN-SHEATH-AFT", "GLAND-BOWDEN-SHEATH-FWD",
    "GLAND-GAS-MAIN-AFT", "GLAND-GAS-MAIN-FWD",
    "GLAND-PILOT-LINE-AFT", "GLAND-PILOT-LINE-FWD",
    "ROUTE-BOWDEN-SHEATH-001", "ROUTE-BOWDEN-WIRE-001",
    "ROUTE-GAS-MAIN-001", "ROUTE-PILOT-LINE-001",
    "ROUTE-LINER-BOWDEN-SHEATH-001", "ROUTE-LINER-GAS-MAIN-001",
    "ROUTE-LINER-PILOT-LINE-001",
    "WP04-FULLFLOW-MANIFOLD", "WP04-MANIFOLD-BRACKET",
}

FORWARD_KEEP = {
    "NOSE-001", "BALLAST-001", "NOSE-BALLAST-TAPER-PIN-001", "FWD-RING-02",
}


def _world_z_shift(location: cq.Location, dz: float) -> cq.Location:
    return g.translation_loc(0.0, 0.0, dz) * location


def _shift_matrix_z(matrix: list[list[float]], dz: float) -> list[list[float]]:
    shifted = copy.deepcopy(matrix)
    shifted[2][3] = float(shifted[2][3]) + dz
    return shifted


def _part_copy(source: g.PartDef, *, part_number: str, revision: str, description: str,
               shape: cq.Shape, material: str | None = None, mass_kg: float | None = None,
               process: str | None = None, notes: str | None = None,
               color_key: str | None = None) -> g.PartDef:
    return g.PartDef(
        part_number=part_number,
        revision=revision,
        description=description,
        shape=shape,
        material=material or source.material,
        make_buy=source.make_buy,
        manufacturer=source.manufacturer,
        cad_classification="EXACT_ANALYTIC",
        mass_kg=mass_kg,
        source_url=source.source_url,
        purchase_url=source.purchase_url,
        process=process if process is not None else source.process,
        finish=source.finish,
        notes=notes if notes is not None else source.notes,
        color_key=color_key or source.color_key,
        external_context=False,
    )


def _valid_single(shape: cq.Shape, label: str) -> cq.Shape:
    shape = shape.clean()
    solids = shape.Solids()
    if len(solids) != 1 or not shape.isValid() or solids[0].Volume() <= 0.0:
        raise ValueError(
            f"{label} must be one valid positive exact solid; "
            f"solids={len(solids)}, valid={shape.isValid()}"
        )
    return solids[0]


def make_short_arm() -> cq.Shape:
    original_pivot, original_length = g.PIVOT_Z, g.ARM_LENGTH
    try:
        g.PIVOT_Z = cfg.ARM_PIVOT_Z_MM
        g.ARM_LENGTH = cfg.ARM_LENGTH_MM
        return _valid_single(g.make_arm_part_local(), "shortened arm")
    finally:
        g.PIVOT_Z, g.ARM_LENGTH = original_pivot, original_length


def make_integral_pivot_carrier() -> cq.Shape:
    """Close the inherited two-lug nominal-part fragmentation with a root web."""
    source = g.make_pivot_carrier_local()
    root_web = g.box_center(3.0, 14.4, 2.4, -4.8, 0.0, -9.0)
    return _valid_single(source.fuse(root_web), "integral pivot carrier")


def make_integral_crosshead() -> cq.Shape:
    """Preserve the source envelope while eliminating two slivers and joined cheeks."""
    source_solids = sorted(
        g.make_crosshead_part_local().Solids(), key=lambda solid: solid.Volume(), reverse=True
    )
    if len(source_solids) != 5 or source_solids[3].Volume() >= 1.0:
        raise ValueError("source crosshead topology changed; bounded repair must be requalified")
    # The two sub-1 mm3 products are source Boolean debris, not design features.
    # The two 81.7 mm3 clevis cheeks are retained and positively joined to the
    # central body by material inside the source overall envelope.
    repaired = source_solids[0].fuse(source_solids[1]).fuse(source_solids[2])
    repaired = repaired.fuse(g.box_center(5.0, 2.0, 3.0, -7.5, -3.0, 0.0))
    repaired = repaired.fuse(g.box_center(5.0, 2.0, 3.0, -7.5, 3.0, 0.0))
    return _valid_single(repaired, "integral common crosshead")


def make_integral_actuator_body(ro: float, bore_r: float, length: float,
                                eye_z: float, eye_ro: float) -> cq.Shape:
    """Join the drawing-derived actuator neck to its annular body end closure."""
    source = build_r2.actuator_body_shape(ro, bore_r, length, eye_z, eye_ro)
    # The source proxy's central neck lies inside the body bore and was therefore
    # topologically separate.  A commercial-body end shoulder occupies this
    # already-bounded envelope and joins the neck without changing interfaces.
    end_shoulder = g.box_center(2.0 * ro, 4.0, 2.0, 0.0, 0.0, length - 0.5)
    return _valid_single(source.fuse(end_shoulder), "integral actuator installation body")


def make_short_fixed_sector() -> cq.Shape:
    length = cfg.ARM_STRUCTURE_SPAN_MM
    out = g.analytic_sector(28.5, 24.2, length, 0.0, 29.0, 0.0)
    for angle in (-25.0, 25.0):
        x = 26.2 * math.cos(math.radians(angle))
        y = 26.2 * math.sin(math.radians(angle))
        out = out.cut(g.cyl_z(1.35, length + 0.4, x, y, -0.2))
        out = out.cut(g.cyl_z(2.60, 1.6, x, y, -0.2))
        out = out.cut(g.cyl_z(2.60, 1.6, x, y, length - 1.4))
    return _valid_single(out, "short fixed sector")


def make_short_longeron(*, backup_access: bool, deployed: bool) -> cq.Shape:
    length = cfg.ARM_STRUCTURE_SPAN_MM
    out = g.analytic_sector(24.2, 23.0, length, 0.0, 15.0, 0.0)
    if backup_access:
        theta = g.DEPLOYED_ANGLE if deployed else 0.0
        kin = g.kinematic(theta)
        spring_length = g.SPRING_DEPLOYED if deployed else g.SPRING_STOWED
        source_fixed_seat = kin["crosshead_z"] + spring_length + 9.75
        source_structure_start = 469.0
        for local_z in (11.75, source_fixed_seat - source_structure_start):
            out = out.cut(cq.Solid.makeCylinder(
                2.55, 1.8, cq.Vector(22.7, 0.0, local_z), cq.Vector(1, 0, 0)
            ))
    return _valid_single(out, "short arm longeron")


def make_short_sector_three(deployed: bool) -> cq.Shape:
    out = make_short_fixed_sector()
    theta = g.DEPLOYED_ANGLE if deployed else 0.0
    kin = g.kinematic(theta)
    spring_length = g.SPRING_DEPLOYED if deployed else g.SPRING_STOWED
    source_fixed_seat = kin["crosshead_z"] + spring_length + 9.75
    for local_z in (11.75, source_fixed_seat - 469.0):
        out = out.cut(cq.Solid.makeCylinder(
            2.85, 3.45, cq.Vector(23.95, 0.0, local_z), cq.Vector(1, 0, 0)
        ))
    return _valid_single(out, "short fixed sector three")


def make_short_stow_guide() -> cq.Shape:
    dog_center_z = cfg.ARM_PIVOT_Z_MM + cfg.ARM_LENGTH_MM - 3.5
    ring_forward_rel_z = cfg.ARM_TERMINATION_RING_FORWARD_FACE_Z_MM - dog_center_z
    guide = g.box_center(8.0, 0.50, 6.0, 15.0, 2.50, 0.0)
    guide = guide.fuse(g.box_center(8.0, 0.50, 6.0, 15.0, -2.50, 0.0))
    guide = guide.fuse(g.box_center(0.84, 5.50, 0.90, 10.70, 0.0, 0.0))
    guide = guide.fuse(g.box_center(0.50, 5.50, 0.40, 18.75, 0.0, 3.0))
    mount_height = max(0.40, ring_forward_rel_z - 3.2)
    guide = guide.fuse(g.box_center(
        1.50, 5.50, mount_height, 19.25, 0.0, 3.2 + mount_height / 2.0,
    ))
    guide = guide.cut(cq.Solid.makeCylinder(
        0.65, 6.4, cq.Vector(17.0, -3.2, 0.0), cq.Vector(0, 1, 0)
    ))
    guide = guide.cut(cq.Solid.makeCylinder(
        0.85, 1.4, cq.Vector(17.0, 1.8, 0.0), cq.Vector(0, 1, 0)
    ))
    guide = guide.fuse(g.make_captive_inhibit_closed_guide_local())
    return _valid_single(guide, "short stow-dog guide")


def make_plain_transition_ring() -> cq.Shape:
    ring = g.tube_z(25.30, 19.50, 8.0, z0=-4.0)
    for phi in (0.0, 120.0, 240.0):
        # Six machined carrier weld lands terminate at the aft ring face.
        land = g.box_center(6.0, 3.0, 2.0, 21.6, 0.0, 3.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        ring = ring.fuse(land)
    return _valid_single(ring, "ballast-to-carrier transition ring")


def make_termination_ring() -> cq.Shape:
    ring = g.tube_z(25.30, 19.50, 8.0, z0=-4.0)
    for phi in (0.0, 120.0, 240.0):
        land = g.box_center(5.0, 3.0, 2.0, 21.8, 0.0, -3.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        ring = ring.fuse(land)
    return _valid_single(ring, "short-arm termination ring")


def make_recovery_hardpoint_ring() -> cq.Shape:
    ring = g.tube_z(25.30, 19.00, 8.0, z0=-4.0)
    for yy in (-3.25, 3.25):
        ear = g.ring_y(22.0, 0.0, 2.0, 5.3, 3.15, yy)
        web = g.box_center(8.0, 2.0, 10.0, 21.3, yy, 0.0)
        ring = ring.fuse(ear).fuse(web)
    bore = cq.Solid.makeCylinder(3.15, 12.0, cq.Vector(22.0, -6.0, 0.0), cq.Vector(0, 1, 0))
    return _valid_single(ring.cut(bore), "recovery hardpoint ring")


def make_open_flap(side: str) -> cq.Shape:
    length = cfg.PACK_AXIAL_LENGTH_MM
    radial_width = 42.0
    thickness = 1.20
    x = 48.0 if side == "RIGHT" else -48.0
    plate = g.box_center(thickness, radial_width, length, x, 0.0, length / 2.0)
    edge = g.box_center(3.0, 4.0, length, x, -radial_width / 2.0 if side == "RIGHT" else radial_width / 2.0, length / 2.0)
    return _valid_single(plate.fuse(edge), f"open {side.lower()} flap")


def make_mesh_window() -> cq.Shape:
    frame = g.box_center(1.0, 30.0, 52.0, 0.0, 0.0, 0.0)
    opening = g.box_center(1.4, 24.0, 42.0, 0.0, 0.0, 0.0)
    frame = frame.cut(opening)
    for y in (-8.0, 0.0, 8.0):
        frame = frame.fuse(g.box_center(1.0, 1.2, 42.0, 0.0, y, 0.0))
    for z in (-14.0, 0.0, 14.0):
        frame = frame.fuse(g.box_center(1.0, 24.0, 1.2, 0.0, 0.0, z))
    return _valid_single(frame, "water-entry mesh frame")


def make_inflator_proxy() -> cq.Shape:
    housing = g.box_center(16.0, 22.0, 46.0, 8.0, 0.0, 0.0)
    inlet = cq.Solid.makeCylinder(5.0, 12.0, cq.Vector(-4.0, 0.0, 0.0), cq.Vector(1, 0, 0))
    lever = g.box_center(8.0, 4.0, 28.0, 17.0, 0.0, 10.0)
    pivot = cq.Solid.makeCylinder(2.0, 26.0, cq.Vector(17.0, -13.0, -4.0), cq.Vector(0, 1, 0))
    return _valid_single(housing.fuse(inlet).fuse(lever).fuse(pivot), "Hydro 1F inflator proxy")


def make_inflator_guard() -> cq.Shape:
    guard = g.box_center(3.0, 30.0, 3.0, 0.0, 0.0, -28.0)
    guard = guard.fuse(g.box_center(3.0, 30.0, 3.0, 0.0, 0.0, 28.0))
    for y in (-14.0, 14.0):
        guard = guard.fuse(g.box_center(3.0, 3.0, 59.0, 0.0, y, 0.0))
    return _valid_single(guard, "inflator guard")


def _add(builder: build_r2.R2Builder, part: g.PartDef, occurrence_id: str,
         path: str, location: cq.Location, classification: str = "FIXED",
         joint_type: str = "DEFINED_PERMANENT_JOINT", permitted_dof: str = "0") -> str:
    builder.catalog.add(part)
    assembly = builder.aft if path.startswith(TOP_AFT) else builder.arm_module
    return builder.add(
        assembly, path, part, occurrence_id, location, classification, joint_type, permitted_dof,
    )


def _define(builder: build_r2.R2Builder, part_number: str, description: str, shape: cq.Shape,
            material: str, *, revision: str = "A", make_buy: str = "MAKE",
            manufacturer: str = "STINGRAY custom", mass_kg: float | None = None,
            process: str = "", notes: str = "", color_key: str = "steel",
            source_url: str = "") -> g.PartDef:
    return builder.define(
        part_number, revision, description, shape, material, make_buy, manufacturer,
        "EXACT_ANALYTIC" if not part_number.endswith("_PROXY") else "DIMENSION_CONTROLLED_PROXY",
        mass_kg=mass_kg, source_url=source_url, process=process, notes=notes,
        color_key=color_key,
    )


def _connect(builder: build_r2.R2Builder, cid: str, occurrence: str, mate: str,
             connection_type: str, retaining_hardware: str, evidence: str,
             *, structural: bool = False) -> None:
    builder.connect(
        cid, occurrence, mate, "CONTROLLED_INTERFACE", "CONTROLLED_MATE_INTERFACE",
        connection_type, "0", retaining_hardware,
        "POSITIVE", "POSITIVE", "DEFINED",
        occurrence, mate, "CONTROLLED SERVICE PROCEDURE", evidence,
    )
    builder.require_attachment(
        f"ATT-{cid}", occurrence, mate, connection_type, 0.25,
        evidence_basis=evidence, structural_load_path=structural,
    )


def _refresh_global_shapes(builder: build_r2.R2Builder) -> None:
    builder.global_shapes = {
        occurrence.occurrence_id: g.moved(
            builder.catalog.parts[occurrence.part_number].shape, occurrence.location
        )
        for occurrence in builder.occurrences
    }


def _filter_source(builder: build_r2.R2Builder) -> tuple[set[str], list[g.Occurrence]]:
    kept: list[g.Occurrence] = []
    removed: set[str] = set()
    for occurrence in builder.occurrences:
        if occurrence.parent_path.startswith(TOP_FORWARD):
            keep = occurrence.occurrence_id in FORWARD_KEEP
        elif occurrence.parent_path.startswith(TOP_ARM):
            keep = occurrence.occurrence_id not in ARM_ROUTE_REMOVALS
        else:
            keep = False
        (kept if keep else []).append(occurrence) if keep else removed.add(occurrence.occurrence_id)
    builder.occurrences = kept
    ids = {occ.occurrence_id for occ in kept}
    builder.connections = [
        row for row in builder.connections
        if row.occurrence_id in ids and row.mate_occurrence_id in ids
    ]
    builder.routes = [
        row for row in builder.routes
        if row.get("route_occurrence_id") in ids
        and (row.get("origin_external_boundary") or row.get("origin_occurrence") in ids)
        and (row.get("destination_external_boundary") or row.get("destination_occurrence") in ids)
    ]
    builder.intentional_fits = [
        row for row in builder.intentional_fits
        if row.get("occurrence_a") in ids and row.get("occurrence_b") in ids
    ]
    builder.attachment_requirements = [
        row for row in builder.attachment_requirements
        if row.get("occurrence_a") in ids and row.get("occurrence_b") in ids
        and all(hw in ids for hw in row.get("hardware_occurrence_ids", []))
    ]
    builder.motion_tracks = [row for row in builder.motion_tracks if row.get("occurrence_id") in ids]
    builder.mass_overrides_kg = {
        key: value for key, value in builder.mass_overrides_kg.items() if key in ids
    }
    builder.flexible_ids &= ids
    builder.external_ids &= ids
    _refresh_global_shapes(builder)
    return removed, kept


def _replace_part(builder: build_r2.R2Builder, old_part_numbers: Iterable[str], new_part: g.PartDef,
                  occurrence_ids: Iterable[str]) -> None:
    builder.catalog.add(new_part)
    targets = set(occurrence_ids)
    for occurrence in builder.occurrences:
        if occurrence.occurrence_id in targets:
            if occurrence.part_number not in set(old_part_numbers):
                raise ValueError(
                    f"Unexpected source definition for {occurrence.occurrence_id}: {occurrence.part_number}"
                )
            occurrence.part_number = new_part.part_number


def _shift_occurrences(builder: build_r2.R2Builder) -> dict[str, float]:
    shifts: dict[str, float] = {}
    terminal_prefixes = (
        "STOW-DOG-", "STOW-DOG-GUIDE-", "STOW-DOG-INHIBIT-",
    )
    for occurrence in builder.occurrences:
        if not occurrence.parent_path.startswith(TOP_ARM):
            continue
        if occurrence.occurrence_id == "ARM-TERMINATION-RING-001" or occurrence.occurrence_id.startswith(terminal_prefixes):
            dz = cfg.SOURCE_TO_NEW_TERMINATION_TRANSLATION_MM
        else:
            dz = cfg.SOURCE_TO_NEW_PIVOT_TRANSLATION_MM
        occurrence.location = _world_z_shift(occurrence.location, dz)
        shifts[occurrence.occurrence_id] = dz

    for track in builder.motion_tracks:
        dz = shifts.get(str(track.get("occurrence_id")), 0.0)
        for sample in track.get("samples", []) if isinstance(track.get("samples"), list) else []:
            matrix = sample.get("transform_matrix_3x4")
            if isinstance(matrix, list) and len(matrix) == 3:
                sample["transform_matrix_3x4"] = _shift_matrix_z(matrix, dz)
    _refresh_global_shapes(builder)
    return shifts


def _install_short_definitions(builder: build_r2.R2Builder) -> None:
    arm_source = builder.catalog.parts[SOURCE_ARM_PART]
    short_arm = _part_copy(
        arm_source,
        part_number=SHORT_ARM_PART,
        revision="A",
        description="378.206 MM PIVOT-TO-TIP SHORTENED ARM BLADE WITH CONTROLLED ROUNDED TIP",
        shape=make_short_arm(),
        mass_kg=None,
        process="Source arm-root machining retained; outboard analytic blade rebuilt to the 378.206 mm tip datum; deburr and CMM inspect",
        notes="Root, pivot, link, stop, lock and retention interfaces are source-derived. PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED.",
    )
    _replace_part(builder, {SOURCE_ARM_PART}, short_arm, {"ARM-1", "ARM-2", "ARM-3"})

    carrier_source = builder.catalog.parts["DF8-R2-PIVOT-CARRIER-001"]
    integral_carrier = _part_copy(
        carrier_source,
        part_number="DF8-SHORT14-PIVOT-CARRIER-001",
        revision="A",
        description="INTEGRAL DOUBLE-SHEAR PIVOT CARRIER WITH ROOT LOAD-PATH WEB",
        shape=make_integral_pivot_carrier(),
        mass_kg=None,
        process="5-axis mill from one billet; ream pivot; machine stop-land bores; CMM inspect",
        notes="Source carrier interfaces and envelope retained; root web provides a one-solid load path into the new transition-ring lands.",
    )
    _replace_part(
        builder, {carrier_source.part_number}, integral_carrier,
        {"PIVOT-CARRIER-1", "PIVOT-CARRIER-2", "PIVOT-CARRIER-3"},
    )

    crosshead_source = builder.catalog.parts["DF8-R2-CROSSHEAD-001"]
    integral_crosshead = _part_copy(
        crosshead_source,
        part_number="DF8-SHORT14-CROSSHEAD-001",
        revision="A",
        description="ONE-PIECE SIX-CLEVIS GUIDED COMMON CROSSHEAD WITHOUT BOOLEAN DEBRIS",
        shape=make_integral_crosshead(),
        mass_kg=None,
        process="5-axis mill-turn from one billet; H900; hone; CMM inspect all six clevis interfaces",
        notes="Source interface datums retained; two sub-1 mm3 Boolean-debris solids removed and retained cheeks joined inside the source envelope.",
    )
    _replace_part(
        builder, {crosshead_source.part_number}, integral_crosshead, {"CROSSHEAD-001"}
    )

    for part_number, dimensions, occurrence_id in (
        ("GS-19-50-V4A-B8-B8", (9.5, 5.2, 105.0, 112.0, 6.0), "GS19-BODY-001"),
        ("HBD-15-25-AA-P", (7.5, 4.0, 95.0, 102.0, 5.5), "HBD-BODY-001"),
    ):
        source = builder.catalog.parts[part_number]
        integral = copy.deepcopy(source)
        integral.revision = "SHORT14-INSTALL-B"
        integral.shape = make_integral_actuator_body(*dimensions)
        integral.description = source.description.replace(
            "ARTICULATED INSTALLATION BODY", "ONE-SOLID ARTICULATED INSTALLATION BODY"
        )
        integral.process = (
            f"{source.process}; drawing-derived body end shoulder restored inside the controlled catalog envelope"
        )
        integral.notes = (
            f"{source.notes} The previously separated end-neck proxy topology is joined by a bounded end shoulder; "
            "catalog interfaces, overall envelope, fixed/moving orientation, stroke and allocated mass are unchanged."
        )
        builder.catalog.parts[part_number] = integral
        if not any(occ.occurrence_id == occurrence_id for occ in builder.occurrences):
            raise KeyError(f"missing retained actuator occurrence {occurrence_id}")

    sector_source = builder.catalog.parts["DF8-R2-FIXED-SECTOR-001"]
    short_sector = _part_copy(
        sector_source,
        part_number="DF8-SHORT14-FIXED-SECTOR-001",
        revision="A",
        description="SHORTENED ANALYTIC CYLINDRICAL FIXED BODY SECTOR",
        shape=make_short_fixed_sector(),
        mass_kg=None,
    )
    sector_three_source = builder.catalog.parts["DF8-R2-BACKUP-ACCESS-FIXED-SECTOR-003"]
    short_sector_three = _part_copy(
        sector_three_source,
        part_number="DF8-SHORT14-BACKUP-ACCESS-FIXED-SECTOR-003",
        revision="A",
        description="SHORTENED FIXED SECTOR 3 WITH BACKUP-GUIDE ACCESS",
        shape=make_short_sector_three(builder.deployed),
        mass_kg=None,
    )
    _replace_part(builder, {sector_source.part_number}, short_sector, {"FIXED-SECTOR-1", "FIXED-SECTOR-2"})
    _replace_part(builder, {sector_three_source.part_number}, short_sector_three, {"FIXED-SECTOR-3"})

    longeron_source = builder.catalog.parts["DF8-R2-ROUTED-LONGERON-001"]
    short_longeron = _part_copy(
        longeron_source,
        part_number="DF8-SHORT14-ARM-LONGERON-001",
        revision="A",
        description="SHORTENED PRIMARY ARM-MODULE LONGERON",
        shape=make_short_longeron(backup_access=False, deployed=builder.deployed),
        mass_kg=None,
    )
    longeron_three_source = builder.catalog.parts["DF8-R2-BACKUP-GUIDE-LONGERON-003"]
    short_longeron_three = _part_copy(
        longeron_three_source,
        part_number="DF8-SHORT14-BACKUP-GUIDE-LONGERON-003",
        revision="A",
        description="SHORTENED PRIMARY LONGERON 3 WITH BACKUP-GUIDE BORES",
        shape=make_short_longeron(backup_access=True, deployed=builder.deployed),
        mass_kg=None,
    )
    _replace_part(builder, {longeron_source.part_number}, short_longeron, {"ARM-LONGERON-1", "ARM-LONGERON-2"})
    _replace_part(builder, {longeron_three_source.part_number}, short_longeron_three, {"ARM-LONGERON-3"})

    guide_source = builder.catalog.parts["DF8-R2-STOW-DOG-GUIDE-001"]
    short_guide = _part_copy(
        guide_source,
        part_number="DF8-SHORT14-STOW-DOG-GUIDE-001",
        revision="A",
        description="SHORTENED-ARM STOW-DOG GUIDE WITH TERMINATION-RING WELD TONGUE",
        shape=make_short_stow_guide(),
        mass_kg=None,
        process="5-axis mill; qualified permanent weld to termination-ring land",
    )
    _replace_part(builder, {guide_source.part_number}, short_guide,
                  {"STOW-DOG-GUIDE-1", "STOW-DOG-GUIDE-2", "STOW-DOG-GUIDE-3"})

    transition_source = builder.catalog.parts["DF8-R2-STRUCT-RING-ROUTED-001"]
    transition = _part_copy(
        transition_source,
        part_number="DF8-SHORT14-BALLAST-CARRIER-TRANSITION-RING-001",
        revision="A",
        description="BALLAST-AFT-FACE TO ARM-CARRIER STRUCTURAL TRANSITION RING",
        shape=make_plain_transition_ring(),
        mass_kg=None,
        process="Mill-turn; machine six carrier weld lands; CMM inspect ballast-face and pivot datums",
        notes="FORWARD_BALLAST_AFT_FACE is the exact BALLAST-001 planar face at Z=336.000 mm; ring spans Z=336.000..344.000 mm.",
    )
    _replace_part(builder, {transition_source.part_number}, transition, {"FWD-RING-02"})
    for occurrence in builder.occurrences:
        if occurrence.occurrence_id == "FWD-RING-02":
            occurrence.location = g.translation_loc(0.0, 0.0, cfg.TRANSITION_RING_Z_MM)

    termination_source = builder.catalog.parts["DF8-FORWARD-ARM-TERMINATION-RING-001"]
    termination = _part_copy(
        termination_source,
        part_number="DF8-SHORT14-ARM-TERMINATION-RING-001",
        revision="A",
        description="SHORT-ARM MODULE AFT STRUCTURAL TERMINATION RING",
        shape=make_termination_ring(),
        mass_kg=None,
        process="Mill-turn; machine three longeron and stow-guide lands; CMM inspect",
    )
    _replace_part(builder, {termination_source.part_number}, termination, {"ARM-TERMINATION-RING-001"})
    _refresh_global_shapes(builder)


def _add_aft_structure(builder: build_r2.R2Builder) -> None:
    forward_shell_length = cfg.RECOVERY_HARDPOINT_FORWARD_FACE_Z_MM - cfg.ARM_TERMINATION_RING_AFT_FACE_Z_MM
    aft_shell_length = cfg.AFT_CLOSURE_RING_FORWARD_FACE_Z_MM - cfg.RECOVERY_HARDPOINT_AFT_FACE_Z_MM
    shell_forward = _define(
        builder, "DF8-SHORT14-AFT-SHELL-FORWARD-001",
        "SHORTENED AFT GRADE-9 TITANIUM SHELL FORWARD SEGMENT",
        g.tube_z(g.NORMAL_R, 25.35, forward_shell_length), "Ti-3Al-2.5V Grade 9",
        process="Cold draw; trim; laser weld to termination and recovery rings", color_key="titanium",
    )
    shell_aft = _define(
        builder, "DF8-SHORT14-AFT-SHELL-CLOSURE-001",
        "SHORTENED AFT GRADE-9 TITANIUM SHELL CLOSURE SEGMENT",
        g.tube_z(g.NORMAL_R, 25.35, aft_shell_length), "Ti-3Al-2.5V Grade 9",
        process="Cold draw; trim; laser weld to recovery and closure rings", color_key="titanium",
    )
    _add(builder, shell_forward, "SHORT-AFT-SHELL-FWD", PATH_AFT_STRUCTURE,
         g.translation_loc(0, 0, cfg.ARM_TERMINATION_RING_AFT_FACE_Z_MM))
    _add(builder, shell_aft, "SHORT-AFT-SHELL-AFT", PATH_AFT_STRUCTURE,
         g.translation_loc(0, 0, cfg.RECOVERY_HARDPOINT_AFT_FACE_Z_MM))

    hardpoint = _define(
        builder, "DF8-SHORT14-RECOVERY-HARDPOINT-RING-001",
        "LOW-PROFILE STRUCTURAL RECOVERY HARDPOINT RING WITH DOUBLE-SHEAR YOKE",
        make_recovery_hardpoint_ring(), "Ti-6Al-4V",
        process="5-axis mill from forged ring; ream yoke; weld to shell and three longerons; proof load",
        notes="Ultimate recovery load bypasses Cordura, hook-and-loop, pack seams and inflator patch.",
        color_key="titanium",
    )
    _add(builder, hardpoint, "RECOVERY-HARDPOINT-RING", PATH_AFT_STRUCTURE,
         g.translation_loc(0, 0, cfg.RECOVERY_HARDPOINT_Z_MM))

    closure_ring = _define(
        builder, "DF8-SHORT14-AFT-CLOSURE-RING-001", "AFT STRUCTURAL CLOSURE RING",
        g.tube_z(25.30, 19.0, 8.0, z0=-4.0), "Ti-6Al-4V",
        process="Mill-turn; weld to shell; face grind", color_key="titanium",
    )
    cap_shape = g.cyl_z(g.NORMAL_R, cfg.AFT_CAP_Z_MAX_MM - cfg.AFT_CAP_Z_MIN_MM)
    cap_shape = cap_shape.cut(g.cyl_z(3.2, 4.4, 22.0, 0.0, -0.2))
    cap = _define(
        builder, "DF8-SHORT14-AFT-CAP-001", "SHORTENED BODY AFT CAP WITH TETHER SERVICE PASSAGE",
        _valid_single(cap_shape, "aft cap"), "Ti-6Al-4V",
        process="5-axis mill; machine chafe-safe service passage; bolt and safety-wire to closure ring",
        color_key="titanium",
    )
    _add(builder, closure_ring, "AFT-CLOSURE-RING", PATH_AFT_STRUCTURE,
         g.translation_loc(0, 0, cfg.AFT_CLOSURE_RING_Z_MM))
    _add(builder, cap, "AFT-CLOSURE-CAP", PATH_AFT_STRUCTURE,
         g.translation_loc(0, 0, cfg.AFT_CAP_Z_MIN_MM))

    for segment, z0, length in (
        ("FWD", cfg.ARM_TERMINATION_RING_AFT_FACE_Z_MM, forward_shell_length),
        ("AFT", cfg.RECOVERY_HARDPOINT_AFT_FACE_Z_MM, aft_shell_length),
    ):
        longeron = _define(
            builder, f"DF8-SHORT14-AFT-LONGERON-{segment}-001",
            f"AFT PRIMARY LOAD-PATH LONGERON {segment}",
            g.analytic_sector(25.35, 23.0, length, 0.0, 3.5), "Ti-6Al-4V",
            process="5-axis mill; qualified longitudinal shell weld", color_key="titanium",
        )
        for index, phi in enumerate((60.0, 180.0, 300.0), 1):
            _add(builder, longeron, f"AFT-LONGERON-{segment}-{index}", PATH_AFT_STRUCTURE,
                 g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, z0))

    collar = _define(
        builder, "DF8-SHORT14-PACK-ATTACHMENT-COLLAR-001",
        "LOW-PROFILE PACK ATTACHMENT COLLAR WITHIN 57.15 MM RIGID LIMIT",
        g.tube_z(28.25, 26.50, 4.0, z0=-2.0), "Ti-6Al-4V",
        process="Split-ring machine; qualified shell attachment; proof load pack retention", color_key="titanium",
    )
    for index, z in enumerate((1382.0, 1592.0), 1):
        _add(builder, collar, f"PACK-ATTACHMENT-COLLAR-{index}", PATH_AFT_STRUCTURE,
             g.translation_loc(0, 0, z))

    _connect(builder, "TRANSITION-BALLAST", "FWD-RING-02", "BALLAST-001",
             "CONTROLLED_SHRINK_LAND_AND_CIRCUMFERENTIAL_WELD", "INTEGRAL RING LAND",
             "Exact shared Z=336.000 mm source-face datum and qualified structural joint", structural=True)
    for index in (1, 2, 3):
        _connect(builder, f"CARRIER-TRANSITION-{index}", f"PIVOT-CARRIER-{index}", "FWD-RING-02",
                 "QUALIFIED_DOUBLE_FILLET_WELD", "TWO CARRIER WEBS",
                 "Carrier forward face Z=344.000 mm on transition-ring aft face", structural=True)
        _connect(builder, f"LONGERON-TERMINATION-{index}", f"ARM-LONGERON-{index}", "ARM-TERMINATION-RING-001",
                 "QUALIFIED_LASER_WELD", "INTEGRAL LONGERON LAND",
                 "Shortened arm-module axial/torsional load path", structural=True)
        _connect(builder, f"STOW-GUIDE-TERMINATION-{index}", f"STOW-DOG-GUIDE-{index}", "ARM-TERMINATION-RING-001",
                 "QUALIFIED_PERMANENT_WELD", "INTEGRAL GUIDE TONGUE",
                 "Occurrence-matched short-arm stowed-retention support", structural=False)
        _connect(builder, f"AFT-LONGERON-HARDPOINT-FWD-{index}", f"AFT-LONGERON-FWD-{index}", "RECOVERY-HARDPOINT-RING",
                 "QUALIFIED_LASER_WELD", "INTEGRAL RING LAND",
                 "Recovery load transfers into forward shell/arm termination ring", structural=True)
        _connect(builder, f"AFT-LONGERON-HARDPOINT-AFT-{index}", f"AFT-LONGERON-AFT-{index}", "RECOVERY-HARDPOINT-RING",
                 "QUALIFIED_LASER_WELD", "INTEGRAL RING LAND",
                 "Recovery load transfers into aft closure segment", structural=True)
        _connect(builder, f"AFT-LONGERON-SHELL-FWD-{index}", f"AFT-LONGERON-FWD-{index}", "SHORT-AFT-SHELL-FWD",
                 "QUALIFIED_CONTINUOUS_LONGITUDINAL_WELD", "INTEGRAL SHELL LAND",
                 "Modeled primary axial and torsional shell reinforcement", structural=True)
        _connect(builder, f"AFT-LONGERON-SHELL-AFT-{index}", f"AFT-LONGERON-AFT-{index}", "SHORT-AFT-SHELL-AFT",
                 "QUALIFIED_CONTINUOUS_LONGITUDINAL_WELD", "INTEGRAL SHELL LAND",
                 "Modeled primary axial and torsional shell reinforcement", structural=True)
    for cid, occ, mate in (
        ("AFT-SHELL-TERMINATION", "SHORT-AFT-SHELL-FWD", "ARM-TERMINATION-RING-001"),
        ("AFT-SHELL-HARDPOINT-FWD", "SHORT-AFT-SHELL-FWD", "RECOVERY-HARDPOINT-RING"),
        ("AFT-SHELL-HARDPOINT-AFT", "SHORT-AFT-SHELL-AFT", "RECOVERY-HARDPOINT-RING"),
        ("AFT-SHELL-CLOSURE", "SHORT-AFT-SHELL-AFT", "AFT-CLOSURE-RING"),
        ("AFT-CAP-CLOSURE", "AFT-CLOSURE-CAP", "AFT-CLOSURE-RING"),
    ):
        _connect(builder, cid, occ, mate, "QUALIFIED_STRUCTURAL_JOINT", "CONTROLLED LAND",
                 "Modeled butt interface with defined axial/torsional load transfer", structural=True)
    for index in (1, 2):
        _connect(builder, f"PACK-COLLAR-SHELL-{index}", f"PACK-ATTACHMENT-COLLAR-{index}", "SHORT-AFT-SHELL-FWD",
                 "QUALIFIED_THREE-POINT_COLLAR_ATTACHMENT", "MODELED INTEGRAL COLLAR LANDS",
                 "Low-profile collar positively attached within the rigid 57.15 mm diameter limit", structural=False)


def _panel_shape_stowed(index: int) -> cq.Shape:
    return _valid_single(g.analytic_sector(
        cfg.PACK_PANEL_OUTER_RADIUS_MM, cfg.PACK_PANEL_INNER_RADIUS_MM,
        200.0, (index - 1) * 45.0, 21.5, 0.0,
    ), f"packed buoy panel {index}")


def _panel_shape_deployed(index: int) -> cq.Shape:
    # The proven source gore is already a validated one-solid OCCT result.
    # Re-running ``clean()`` on this thin spherical/wedge topology can
    # invalidate an otherwise valid exact shell, so preserve its authored
    # topology verbatim.
    shape = g.make_buoy_gore_deployed_local(index - 1, cfg.BUOY_DEPLOYED_RADIUS_MM)
    solids = shape.Solids()
    if len(solids) != 1 or not shape.isValid() or solids[0].Volume() <= 0.0:
        raise ValueError(
            f"deployed buoy gore {index} must retain the proven valid source topology; "
            f"solids={len(solids)}, valid={shape.isValid()}"
        )
    return solids[0]


def _pack_module_location(deployed: bool) -> cq.Location:
    if not deployed:
        return g.translation_loc(
            cfg.INFLATOR_BASE_RADIUS_MM, 0.0, cfg.INFLATOR_CENTER_Z_MM
        )
    # Hydro 1F stays attached to the buoy reinforcement at the +X equator.
    return g.translation_loc(cfg.BUOY_DEPLOYED_RADIUS_MM + 1.0, 0, cfg.BUOY_DEPLOYED_CENTER_Z_MM)


def _add_external_pack(builder: build_r2.R2Builder) -> None:
    deployed = builder.deployed
    for side, center_angle in (("LEFT", 225.0), ("RIGHT", 315.0)):
        cradle = _define(
            builder, f"DF8-SHORT14-CORDURA-CRADLE-{side}-001",
            f"AFT BUOY BREAKAWAY WRAP CORDURA CRADLE {side} PANEL WITH DRAINAGE GAPS",
            _valid_single(g.analytic_sector(
                cfg.PACK_CRADLE_OUTER_RADIUS_MM, cfg.PACK_CRADLE_INNER_RADIUS_MM,
                cfg.PACK_AXIAL_LENGTH_MM, center_angle, 44.0, 0.0,
            ), f"Cordura cradle {side.lower()} panel"),
            "1000D Cordura nylon with polyurethane coating", mass_kg=0.0575,
            process="Pattern cut; bound radiused edges; controlled seam allowance and bar-tacks",
            notes="Two-panel closed-solid cradle retains the pack only; it is not in the ultimate recovery load path.",
            color_key="softgood",
        )
        _add(builder, cradle, f"CORDURA-CRADLE-{side}", PATH_PACK,
             g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM), "SOFTGOOD", "WEBBING_RETAINED_CRADLE", "FLEXIBLE")

    if deployed:
        flap_left_shape = make_open_flap("LEFT")
        flap_right_shape = make_open_flap("RIGHT")
        flap_left_loc = g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM)
        flap_right_loc = g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM)
    else:
        flap_left_shape = g.analytic_sector(
            cfg.PACK_INNER_FLAP_OUTER_RADIUS_MM, cfg.PACK_INNER_FLAP_INNER_RADIUS_MM,
            cfg.PACK_AXIAL_LENGTH_MM, 55.0, 45.0, 0.0,
        )
        flap_right_shape = g.analytic_sector(
            cfg.PACK_OUTER_FLAP_OUTER_RADIUS_MM, cfg.PACK_OUTER_FLAP_INNER_RADIUS_MM,
            cfg.PACK_AXIAL_LENGTH_MM, 125.0, 45.0, 0.0,
        )
        flap_left_loc = flap_right_loc = g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM)
    for name, shape, loc in (
        ("LEFT", flap_left_shape, flap_left_loc),
        ("RIGHT", flap_right_shape, flap_right_loc),
    ):
        flap = _define(
            builder, f"DF8-SHORT14-CORDURA-BREAKAWAY-FLAP-{name}-001",
            f"CORDURA PEEL-OPEN BREAKAWAY FLAP {name}", _valid_single(shape, f"{name} pack flap"),
            "1000D Cordura nylon with polyurethane coating", mass_kg=0.065,
            process="Pattern cut; reinforced bound edges; peel-oriented hook-and-loop sewing",
            notes="Opened geometry remains attached to cradle; closure is peel-dominant, not full-area shear.",
            color_key="softgood",
        )
        _add(builder, flap, f"CORDURA-FLAP-{name}", PATH_PACK, loc,
             "SOFTGOOD", "STITCHED_HINGE_AND_HOOK_LOOP_BREAKAWAY", "FLEXIBLE")

    hook = _define(
        builder, "DF8-SHORT14-HOOK-STRIP-001", "WET-RATED HOOK CLOSURE STRIP",
        g.analytic_sector(47.40, 47.20, cfg.PACK_AXIAL_LENGTH_MM - 24.0, 92.0, 8.0, 0.0),
        "Nylon hook-and-loop", mass_kg=0.012,
        process="Sew to reinforced flap with peel-axis orientation", color_key="black",
    )
    loop = _define(
        builder, "DF8-SHORT14-LOOP-STRIP-001", "WET-RATED LOOP CLOSURE STRIP",
        g.analytic_sector(47.44, 47.41, cfg.PACK_AXIAL_LENGTH_MM - 24.0, 92.0, 8.0, 0.0),
        "Nylon hook-and-loop", mass_kg=0.012,
        process="Sew to reinforced flap with bounded 16-degree overlap", color_key="black",
    )
    if deployed:
        hook_loc = g.translation_loc(-48.0, 0.0, cfg.PACK_Z_MIN_MM + 12.0)
        loop_loc = g.translation_loc(48.0, 0.0, cfg.PACK_Z_MIN_MM + 12.0)
    else:
        hook_loc = loop_loc = g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM + 12.0)
    _add(builder, hook, "HOOK-STRIP", PATH_PACK, hook_loc, "SOFTGOOD", "SEWN_TO_LEFT_FLAP", "FLEXIBLE")
    _add(builder, loop, "LOOP-STRIP", PATH_PACK, loop_loc, "SOFTGOOD", "SEWN_TO_RIGHT_FLAP", "FLEXIBLE")

    edge_band_shape = g.tube_z(49.0, 45.0, 6.0, z0=-3.0)
    edge_band = _define(
        builder, "DF8-SHORT14-PACK-EDGE-BAND-001", "REINFORCED PACK EDGE BINDING",
        edge_band_shape, "Cordura binding and HMPE webbing", mass_kg=0.020,
        process="Bound edge; continuous stitch and bar-tack termination", color_key="rope",
    )
    for index, z in enumerate((cfg.PACK_Z_MIN_MM + 3.0, cfg.PACK_Z_MAX_MM - 3.0), 1):
        _add(builder, edge_band, f"PACK-EDGE-BAND-{index}", PATH_PACK,
             g.translation_loc(0, 0, z), "SOFTGOOD", "SEWN_TO_CRADLE_AND_FLAPS", "FLEXIBLE")

    for index in range(1, 9):
        shape = _panel_shape_deployed(index) if deployed else _panel_shape_stowed(index)
        panel = _define(
            builder, f"DF8-SHORT14-BUOY-PANEL-{index:02d}",
            f"60 L BUOY PANEL {index:02d} WITH PACKED-ENVELOPE AND DEPLOYED-GORE STATES",
            shape, "TPU-coated nylon", mass_kg=0.02375,
            process="Waterjet cut; RF weld 12 mm seams; leak and inflation proof",
            notes="Packed state is Buoy_Packed_Softgoods_Envelope_PROXY; deployed state is a thin closed exact gore solid.",
            color_key="softgood",
        )
        loc = (
            g.translation_loc(0, 0, cfg.BUOY_DEPLOYED_CENTER_Z_MM)
            if deployed else g.translation_loc(0, 0, cfg.PACK_Z_MIN_MM + 19.0)
        )
        _add(builder, panel, f"EXT-BUOY-PANEL-{index:02d}", PATH_PACK, loc,
             "SOFTGOOD", "RF_WELDED_GORE_SEAMS", "FLEXIBLE MEMBRANE")

    webbing = _define(
        builder, "DF8-SHORT14-PACK-ATTACHMENT-WEBBING-001",
        "STRUCTURAL PACK-RETENTION WEBBING STRAP",
        g.tube_z(45.60, 44.40, 12.0, z0=-6.0), "HMPE webbing", mass_kg=0.028,
        process="Closed-loop stitch; two-place collar lacing; pack retention proof",
        notes="Retains pack only and is excluded from the recovery load path.", color_key="rope",
    )
    for index, z in enumerate((1382.0, 1592.0), 1):
        _add(builder, webbing, f"PACK-ATTACHMENT-WEBBING-{index}", PATH_PACK,
             g.translation_loc(0, 0, z), "SOFTGOOD", "LACED_TO_LOW_PROFILE_COLLAR", "FLEXIBLE")
        for clock_index, phi in enumerate((60.0, 180.0, 300.0), 1):
            tie = _define(
                builder, f"DF8-SHORT14-PACK-RADIAL-TIE-{index}-{clock_index}",
                "PACK COLLAR-TO-CRADLE RADIAL WEBBING TIE",
                g.box_center(17.2, 5.0, 3.0, 36.6, 0.0, 0.0), "HMPE webbing", mass_kg=0.004,
                process="Folded and bar-tacked around collar and cradle webbing", color_key="rope",
            )
            _add(builder, tie, f"PACK-RADIAL-TIE-{index}-{clock_index}", PATH_PACK,
                 g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, z),
                 "SOFTGOOD", "BAR_TACKED_CLOSED_TIE", "FLEXIBLE")

    mesh = _define(
        builder, "DF8-SHORT14-WATER-ENTRY-MESH-001",
        "REINFORCED OPEN-MESH WATER-ENTRY WINDOW AND DRAIN",
        make_mesh_window(), "Polyester open mesh with Cordura frame", mass_kg=0.012,
        process="Laser cut frame; bind mesh; stitch to window perimeter",
        notes="Direct open area exposes the automatic water-sensitive element while the wrap remains closed.",
        color_key="softgood",
    )
    mesh_loc = (
        _pack_module_location(deployed) * g.translation_loc(17.0, 0.0, 0.0)
        if deployed else g.translation_loc(cfg.PACK_OUTER_FLAP_OUTER_RADIUS_MM + 0.5, 0, cfg.INFLATOR_CENTER_Z_MM)
    )
    _add(builder, mesh, "WATER-ENTRY-MESH", PATH_PACK, mesh_loc,
         "SOFTGOOD", "SEWN_REINFORCED_WINDOW", "FLEXIBLE")

    _connect(builder, "PACK-WEBBING-COLLAR-1", "PACK-ATTACHMENT-WEBBING-1", "PACK-ATTACHMENT-COLLAR-1",
             "CLOSED_WEBBING_LACE", "THREE RADIAL BAR-TACKED TIES", "Modeled retention loop and three ties")
    _connect(builder, "PACK-WEBBING-COLLAR-2", "PACK-ATTACHMENT-WEBBING-2", "PACK-ATTACHMENT-COLLAR-2",
             "CLOSED_WEBBING_LACE", "THREE RADIAL BAR-TACKED TIES", "Modeled retention loop and three ties")
    for side in ("LEFT", "RIGHT"):
        for index in (1, 2):
            _connect(
                builder, f"PACK-CRADLE-{side}-WEBBING-{index}",
                f"CORDURA-CRADLE-{side}", f"PACK-ATTACHMENT-WEBBING-{index}",
                "BAR_TACKED_SOFTGOODS_JOINT", "BOUND SEAM",
                "Controlled stitch traveler and pack-retention proof",
            )
    _connect(builder, "PACK-CRADLE-CENTER-SEAM", "CORDURA-CRADLE-LEFT", "CORDURA-CRADLE-RIGHT",
             "BOUND_DRAINAGE_SEAM", "HMPE EDGE TAPE AND BAR TACKS",
             "Two one-solid cradle panels retain controlled centerline drainage")
    for side in ("LEFT", "RIGHT"):
        _connect(builder, f"PACK-FLAP-HINGE-{side}", f"CORDURA-FLAP-{side}", f"CORDURA-CRADLE-{side}",
                 "CONTINUOUS_STITCHED_PEEL_HINGE", "BOUND CORDURA SEAM",
                 "Flap remains attached through inflation and breakaway opening")
    _connect(builder, "PACK-HOOK-FLAP", "HOOK-STRIP", "CORDURA-FLAP-LEFT",
             "SEWN_HOOK_STRIP", "MULTIROW PEEL-AXIS STITCH", "Hook strip sewn to reinforced left flap")
    _connect(builder, "PACK-LOOP-FLAP", "LOOP-STRIP", "CORDURA-FLAP-RIGHT",
             "SEWN_LOOP_STRIP", "MULTIROW PEEL-AXIS STITCH", "Loop strip sewn to reinforced right flap")
    _connect(builder, "PACK-PEEL-CLOSURE", "HOOK-STRIP", "LOOP-STRIP",
             "WET_RATED_PEEL_BREAKAWAY", "16 DEGREE CONTROLLED OVERLAP", "Inflation opens the closure in peel")
    for index in (1, 2):
        _connect(builder, f"PACK-EDGE-BAND-LEFT-{index}", f"PACK-EDGE-BAND-{index}", "CORDURA-CRADLE-LEFT",
                 "CONTINUOUS_BOUND_EDGE_STITCH", "HMPE BINDING", "Radiused reinforced cradle edge")
        _connect(builder, f"PACK-EDGE-BAND-RIGHT-{index}", f"PACK-EDGE-BAND-{index}", "CORDURA-CRADLE-RIGHT",
                 "CONTINUOUS_BOUND_EDGE_STITCH", "HMPE BINDING", "Radiused reinforced cradle edge")
        for clock_index in (1, 2, 3):
            tie_id = f"PACK-RADIAL-TIE-{index}-{clock_index}"
            _connect(builder, f"PACK-TIE-WEBBING-{index}-{clock_index}", tie_id,
                     f"PACK-ATTACHMENT-WEBBING-{index}", "CLOSED_BAR_TACKED_WEBBING_LOOP",
                     "MULTIROW BAR TACKS", "Modeled collar-side pack retention")
            cradle_side = "LEFT" if clock_index == 2 else "RIGHT"
            _connect(builder, f"PACK-TIE-CRADLE-{index}-{clock_index}", tie_id,
                     f"CORDURA-CRADLE-{cradle_side}", "BAR_TACKED_CRADLE_TIE",
                     "REINFORCED PATCH AND BAR TACKS", "Modeled cradle-side pack retention")
    for index in range(1, 9):
        next_index = 1 if index == 8 else index + 1
        _connect(builder, f"BUOY-GORE-SEAM-{index:02d}", f"EXT-BUOY-PANEL-{index:02d}",
                 f"EXT-BUOY-PANEL-{next_index:02d}", "12_MM_RF_WELDED_GORE_SEAM",
                 "TPU LAMINATE SEAM ALLOWANCE", "Closed leak-proof buoy envelope seam")
    _connect(builder, "WATER-MESH-FLAP", "WATER-ENTRY-MESH", "CORDURA-FLAP-RIGHT",
             "SEWN_REINFORCED_OPEN_WINDOW", "BOUND MESH FRAME", "Direct water path while wrap remains closed")


def _add_inflation_module(builder: build_r2.R2Builder) -> None:
    deployed = builder.deployed
    module_loc = _pack_module_location(deployed)
    patch = _define(
        builder, "DF8-SHORT14-BUOY-INLET-REINFORCEMENT-PATCH-001",
        "BUOY INLET RF-WELDED REINFORCEMENT PATCH",
        g.box_center(1.2, 58.0, 70.0, 0.0, 0.0, 0.0), "TPU-coated nylon laminate", mass_kg=0.026,
        process="Multi-ply RF weld; leak proof and pull proof", color_key="softgood",
    )
    inlet = _define(
        builder, "DF8-SHORT14-BUOY-INLET-MANIFOLD-001",
        "BUOY-MOUNTED INLET MANIFOLD WITH INFLATOR THREAD INTERFACE",
        g.tube_between((-1.0, 0.0, 0.0), (10.0, 0.0, 0.0), 5.2, 3.0),
        "316 stainless steel", process="Swiss turn; passivate; RF-patch clamp and leak proof", color_key="stainless",
    )
    inflator = _define(
        builder, "HALKEY-ROBERTS-HYDRO-1F-V95000XXB_PROXY",
        "HALKEY-ROBERTS HYDRO 1F AUTOMATIC/MANUAL INFLATOR DIMENSION-CONTROLLED PROXY",
        make_inflator_proxy(), "Acetal and stainless commercial inflator assembly", make_buy="BUY",
        manufacturer="Nordson MEDICAL / Halkey-Roberts", mass_kg=0.180,
        process="Incoming identity and interface inspection",
        notes="Commercial interfaces and external service envelope preserved; internals are not invented. Exact vendor CAD and buoy-volume compatibility remain physical acceptance gates.",
        color_key="black",
        source_url="https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-Drawing-V95000xxB.pdf",
    )
    guard = _define(
        builder, "DF8-SHORT14-INFLATOR-GUARD-001", "INFLATOR IMPACT GUARD WITH OPEN WATER PATH",
        make_inflator_guard(), "Ti-6Al-4V", mass_kg=0.055,
        process="Wire form/machine; rounded edges; patch-mounted proof", color_key="titanium",
    )

    patch_id = _add(builder, patch, "BUOY-INLET-PATCH", PATH_INFLATION, module_loc,
                    "SOFTGOOD", "RF_WELDED_MULTI_PLY_PATCH", "FLEXIBLE")
    inlet_id = _add(builder, inlet, "BUOY-INLET-MANIFOLD", PATH_INFLATION, module_loc,
                    "MOVING", "CLAMPED_AND_RF_PATCH_CAPTURED", "LATER_PHASE_BUOY_MOTION")
    inflator_loc = module_loc * g.translation_loc(10.0, 0.0, 0.0)
    inflator_id = _add(builder, inflator, "HYDRO-1F-INFLATOR-PROXY", PATH_INFLATION, inflator_loc,
                       "MOVING", "THREADED_TO_BUOY_INLET", "LATER_PHASE_BUOY_MOTION")
    guard_id = _add(builder, guard, "INFLATOR-GUARD", PATH_INFLATION,
                    module_loc * g.translation_loc(31.0, 0.0, 0.0),
                    "MOVING", "PATCH_AND_WEBBING_SUPPORTED", "LATER_PHASE_BUOY_MOTION")

    cartridge_source = builder.catalog.parts.get("LELAND-81121")
    if cartridge_source is None:
        raise KeyError("Source-supported LELAND-81121 cartridge definition is unavailable")
    cartridge_loc = (
        module_loc * g.translation_loc(17.0, 0.0, -80.0)
        if deployed else g.translation_loc(cfg.CARTRIDGE_CENTER_RADIUS_MM, 0, cfg.CARTRIDGE_Z_MIN_MM)
    )
    cartridge_id = _add(builder, cartridge_source, "BUOY-CO2-CARTRIDGE-81121", PATH_INFLATION,
                        cartridge_loc, "CONSUMED", "THREADED_TO_HYDRO_1F", "LATER_PHASE_BUOY_MOTION")

    bobbin_source = builder.catalog.parts.get("V80040")
    if bobbin_source is None:
        raise KeyError("Source-supported V80040 water bobbin definition is unavailable")
    bobbin_loc = module_loc * g.translation_loc(31.0, 0.0, 0.0)
    bobbin_id = _add(builder, bobbin_source, "HYDRO-1F-WATER-BOBBIN-V80040", PATH_INFLATION,
                     bobbin_loc, "CONSUMED", "CAPTURED_AUTOMATIC_WATER_ELEMENT", "LATER_PHASE_BUOY_MOTION")

    lanyard_points = (
        [(0.0, 0.0, 18.0), (8.0, 0.0, 32.0), (18.0, 6.0, 43.0), (29.0, 0.0, 55.0)]
        if not deployed else
        [(0.0, 0.0, 18.0), (12.0, 0.0, 32.0), (28.0, 8.0, 48.0), (45.0, 0.0, 64.0)]
    )
    lanyard_shape = g.routed_round(lanyard_points, 1.2)
    lanyard = _define(
        builder, "DF8-SHORT14-MANUAL-PULL-LANYARD-001",
        "MANUAL INFLATOR PULL LANYARD WITH MODELED SLACK AND FIRED TRAVEL",
        lanyard_shape, "HMPE cord", mass_kg=0.008,
        process="Eye splice; controlled finished length; 445 N pull proof",
        notes=f"Modeled slack {cfg.PULL_MODELED_SLACK_MM:.1f} mm; required unobstructed fired travel {cfg.PULL_REQUIRED_STROKE_MM:.1f} mm.",
        color_key="rope",
    )
    lanyard_id = _add(builder, lanyard, "MANUAL-PULL-LANYARD", PATH_INFLATION,
                      inflator_loc, "FLEXIBLE", "PINNED_TO_MANUAL_LEVER", "FLEXIBLE")
    tab = _define(
        builder, "DF8-SHORT14-MANUAL-PULL-TAB-001",
        "GLOVED-HAND MANUAL PULL TAB WITH SNAG-RETENTION KEEPER",
        g.box_center(4.0, 34.0, 22.0, 0.0, 0.0, 0.0).cut(
            cq.Solid.makeCylinder(4.0, 5.0, cq.Vector(-2.5, 0.0, 0.0), cq.Vector(1, 0, 0))
        ), "TPU overmold on HMPE webbing", mass_kg=0.018,
        process="Overmold; high-visibility marking; gloved pull and snag test", color_key="softgood",
    )
    tab_loc = inflator_loc * g.translation_loc(lanyard_points[-1][0], lanyard_points[-1][1], lanyard_points[-1][2])
    tab_id = _add(builder, tab, "MANUAL-PULL-TAB", PATH_INFLATION, tab_loc,
                  "MOVING", "LANYARD_EYE_AND_BREAKAWAY_KEEPER", "MANUAL 25 MM PULL")
    keeper = _define(
        builder, "DF8-SHORT14-PULL-TAB-KEEPER-001",
        "LOW-FORCE PULL-TAB SNAG KEEPER",
        g.box_center(3.0, 38.0, 26.0, 0.0, 0.0, 0.0).cut(g.box_center(4.0, 32.0, 20.0)),
        "Cordura and low-force hook-and-loop", mass_kg=0.010,
        process="Bound frame; calibrated breakaway stitch", color_key="softgood",
    )
    keeper_id = _add(builder, keeper, "PULL-TAB-KEEPER", PATH_INFLATION,
                     tab_loc * g.translation_loc(-2.0, 0.0, 0.0),
                     "SOFTGOOD", "LOW_FORCE_BREAKAWAY_KEEPER", "FLEXIBLE")

    for cid, occ, mate, ctype, hardware, evidence in (
        ("PATCH-BUOY", patch_id, "EXT-BUOY-PANEL-01", "MULTI_PLY_RF_WELDED_PATCH", "CONTROLLED PATCH LAND", "Inflator assembly is directly attached to the buoy inlet reinforcement"),
        ("INLET-PATCH", inlet_id, patch_id, "CLAMPED_RF_REINFORCED_INLET", "INLET RETAINING FLANGE", "Direct buoy inlet reinforcement interface"),
        ("INFLATOR-INLET", inflator_id, inlet_id, "THREADED_SEALED_INTERFACE", "CATALOG THREAD AND SEAL", "Hydro 1F commercial interface retained by proxy"),
        ("CARTRIDGE-INFLATOR", cartridge_id, inflator_id, "THREADED_PUNCTURE_INTERFACE", "CATALOG CARTRIDGE THREAD", "Source-supported cartridge envelope; compatibility test required"),
        ("BOBBIN-INFLATOR", bobbin_id, inflator_id, "CAPTURED_WATER_ELEMENT", "CATALOG BOBBIN RETAINER", "V80040 exposed through direct water-entry mesh"),
        ("GUARD-PATCH", guard_id, patch_id, "WEBBING_AND_PATCH_SUPPORTED_GUARD", "TWO REINFORCED LOOPS", "Guard does not occlude water or service access"),
        ("LANYARD-INFLATOR", lanyard_id, inflator_id, "PINNED_MANUAL_LEVER", "CAPTURED LANYARD EYE", "Modeled slack and 25 mm fired travel"),
        ("TAB-LANYARD", tab_id, lanyard_id, "CLOSED_WEBBING_EYE", "BAR-TACKED EYE", "Gloved-hand external pull interface"),
        ("TAB-KEEPER", tab_id, keeper_id, "LOW_FORCE_BREAKAWAY_KEEPER", "CALIBRATED HOOK-AND-LOOP", "Visible external tab retained against snag"),
    ):
        _connect(builder, cid, occ, mate, ctype, hardware, evidence)


def _add_structural_tether(builder: build_r2.R2Builder) -> None:
    deployed = builder.deployed
    thimble_source = builder.catalog.parts.get("DF8-R2-TETHER-THIMBLE-001")
    if thimble_source is None:
        thimble_source = _define(
            builder, "DF8-SHORT14-TETHER-THIMBLE-001", "STRUCTURAL TETHER EYE THIMBLE",
            g.make_thimble_local(), "316 stainless steel", process="Stamp; form; passivate", color_key="stainless",
        )
    body_thimble_loc = g.translation_loc(22.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM)
    buoy_attach = (
        (0.0, 0.0, cfg.BUOY_DEPLOYED_CENTER_Z_MM - cfg.BUOY_DEPLOYED_RADIUS_MM + 3.0)
        if deployed else (40.0, 0.0, cfg.PACK_Z_MAX_MM - 18.0)
    )
    buoy_thimble_loc = g.translation_loc(*buoy_attach)
    _add(builder, thimble_source, "TETHER-THIMBLE-BODY-SHORT14", PATH_TETHER,
         body_thimble_loc, "MOVING", "PINNED_TO_RECOVERY_HARDPOINT", "LATER_PHASE_TETHER_MOTION")
    _add(builder, thimble_source, "TETHER-THIMBLE-BUOY-SHORT14", PATH_TETHER,
         buoy_thimble_loc, "MOVING", "PINNED_TO_BUOY_HARNESS", "LATER_PHASE_TETHER_MOTION")

    tether_points = (
        [(22.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM),
         (36.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM + 12.0),
         (44.0, 7.0, cfg.PACK_Z_MAX_MM - 42.0), buoy_attach]
        if not deployed else
        [(22.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM),
         (35.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM + 15.0),
         (24.0, 0.0, cfg.RECOVERY_HARDPOINT_Z_MM + 35.0), buoy_attach]
    )
    tether = _define(
        builder, "AMSTEEL-BLUE-SHORT14-STRUCTURAL-TETHER-001",
        "STRUCTURAL RECOVERY TETHER WITH TWO BURIED EYE SPLICES",
        g.routed_round(tether_points, 2.0), "HMPE rope", make_buy="MAKE",
        manufacturer="Samson Rope Technologies raw line / STINGRAY finished splices",
        mass_kg=0.090, process="Controlled eye splices; chafe sleeve; finished-article proof load",
        notes="Ultimate recovery load runs hardpoint ring -> pin/thimble -> HMPE tether -> buoy harness. Cordura and hook-and-loop are bypassed.",
        color_key="rope",
    )
    _add(builder, tether, "STRUCTURAL-RECOVERY-TETHER", PATH_TETHER, g.identity_loc(),
         "FLEXIBLE", "TWO_PROOF_LOADED_EYE_SPLICES", "FLEXIBLE")

    pin_source = builder.catalog.parts.get("DF8-R2-RECOVERY-PIN-006")
    clip_source = builder.catalog.parts.get("DF8-R2-RECOVERY-PIN-CLIP-006")
    if pin_source is not None:
        _add(builder, pin_source, "RECOVERY-PIN-BODY-SHORT14", PATH_TETHER,
             body_thimble_loc * g.translation_loc(0, -5.5, 0), "FIXED", "DOUBLE_SHEAR_PIN_WITH_CLIP")
    if clip_source is not None:
        _add(builder, clip_source, "RECOVERY-PIN-CLIP-BODY-SHORT14", PATH_TETHER,
             body_thimble_loc * g.translation_loc(0, 4.7, 0), "FIXED", "EXTERNAL_GROOVE_RETAINER")

    _connect(builder, "TETHER-HARDPOINT", "TETHER-THIMBLE-BODY-SHORT14", "RECOVERY-HARDPOINT-RING",
             "DOUBLE_SHEAR_PINNED_EYE", "RECOVERY-PIN-BODY-SHORT14 and retained clip",
             "Modeled structural recovery pin and thimble; proof load required", structural=True)
    _connect(builder, "TETHER-ROPE-BODY", "STRUCTURAL-RECOVERY-TETHER", "TETHER-THIMBLE-BODY-SHORT14",
             "BURIED_EYE_SPLICE", "CAPTURED THIMBLE", "Finished tether proof-load traveler", structural=True)
    _connect(builder, "TETHER-ROPE-BUOY", "STRUCTURAL-RECOVERY-TETHER", "TETHER-THIMBLE-BUOY-SHORT14",
             "BURIED_EYE_SPLICE", "CAPTURED THIMBLE", "Buoy harness proof-load traveler", structural=True)
    _connect(builder, "TETHER-BUOY-PANEL", "TETHER-THIMBLE-BUOY-SHORT14", "EXT-BUOY-PANEL-01",
             "MULTI-PLY_RF_PATCH_AND_HARNESS_JUNCTION", "STRUCTURAL BUOY HARNESS",
             "Tether load enters reinforced buoy harness, not pack fabric", structural=True)
    if pin_source is not None:
        _connect(builder, "RECOVERY-PIN-HARDPOINT", "RECOVERY-PIN-BODY-SHORT14", "RECOVERY-HARDPOINT-RING",
                 "DOUBLE_SHEAR_SHOULDER_PIN", "EXTERNAL GROOVE RETAINER",
                 "Modeled pin passes through hardpoint yoke and body thimble", structural=True)
    if clip_source is not None:
        _connect(builder, "RECOVERY-PIN-CLIP", "RECOVERY-PIN-CLIP-BODY-SHORT14", "RECOVERY-PIN-BODY-SHORT14",
                 "CAPTIVE_EXTERNAL_GROOVE_RETAINER", "SPRING CLIP",
                 "Positive axial retention of structural recovery pin", structural=True)


def _install_motion_tracks(builder: build_r2.R2Builder) -> None:
    tracked = {str(row.get("occurrence_id")) for row in builder.motion_tracks}
    for occurrence in builder.occurrences:
        if occurrence.classification not in {"MOVING", "FLEXIBLE", "SOFTGOOD", "CONSUMED"}:
            continue
        if occurrence.occurrence_id in tracked:
            continue
        builder.add_motion_track(
            occurrence.occurrence_id, "HOLD_STOWED",
            "External-buoy deployment is a later phase; hold the exact packed configuration during the independent 0..80 degree arm sweep.",
            stationary_during_arm_sweep=True,
        )


def _complete_inherited_attachment_map(builder: build_r2.R2Builder) -> None:
    """Close source hardware/sector rows that were geometry-only in the baseline."""
    for index in (1, 2, 3):
        _connect(builder, f"SECTOR-TRANSITION-{index}", f"FIXED-SECTOR-{index}", "FWD-RING-02",
                 "QUALIFIED_SECTOR_TO_RING_WELD", "MACHINED RING LAND",
                 "Fixed sector carries shell, pivot-stop and actuator reactions into the forward transition ring",
                 structural=True)
        _connect(builder, f"SECTOR-TERMINATION-{index}", f"FIXED-SECTOR-{index}", "ARM-TERMINATION-RING-001",
                 "QUALIFIED_SECTOR_TO_RING_WELD", "MACHINED RING LAND",
                 "Fixed sector closes the arm-module axial and torsional load path", structural=True)
        for screw_index in (1, 2):
            _connect(builder, f"ARM-STOP-PAD-SCREW-{index}-{screw_index}",
                     f"ARM-STOP-SCREW-{index}-{screw_index}", f"ARM-STOP-PAD-{index}",
                     "CAPTIVE_THREADED_STOP_PAD_FASTENER", "M3 CAPTIVE SOCKET SCREW",
                     "Modeled two-screw positive arm-stop-pad attachment")
    _connect(builder, "NOSE-BALLAST-TAPER-PIN", "NOSE-BALLAST-TAPER-PIN-001", "BALLAST-001",
             "REAMED_TAPER_PIN", "DIN 1B TAPER PIN", "Modeled anti-rotation pin across source nose/ballast joint",
             structural=True)
    for index, mate in ((1, "FWD-RING-02"), (2, "BACKUP-SPRING-FIXED-SEAT")):
        _connect(builder, f"BACKUP-GUIDE-SCREW-{index}", f"BACKUP-GUIDE-SCREW-{index}",
                 "BACKUP-SPRING-GUIDE", "FULL_THREAD_GUIDE_SUPPORT_SCREW", "M3 FULL-THREAD SOCKET SCREW",
                 f"Positive backup-guide support; adjacent structural mate {mate}")
    _connect(builder, "CROSSHEAD-GUIDE-LOCK-SCREW", "CROSSHEAD-GUIDE-LOCK-SCREW-001",
             "CROSSHEAD-GUIDE-SPIDER", "FULL_THREAD_GUIDE_LOCK_SCREW", "M4 LOW-HEAD SOCKET SCREW",
             "Positive axial lock for the double-supported crosshead guide")


def _finalize_builder(builder: build_r2.R2Builder) -> None:
    ids = {occ.occurrence_id for occ in builder.occurrences}
    builder.connections = [
        row for row in builder.connections
        if row.occurrence_id in ids and row.mate_occurrence_id in ids
    ]
    builder.attachment_requirements = [
        row for row in builder.attachment_requirements
        if row.get("occurrence_a") in ids and row.get("occurrence_b") in ids
        and all(hw in ids for hw in row.get("hardware_occurrence_ids", []))
    ]
    builder.intentional_fits = [
        row for row in builder.intentional_fits
        if row.get("occurrence_a") in ids and row.get("occurrence_b") in ids
    ]
    builder.motion_tracks = [row for row in builder.motion_tracks if row.get("occurrence_id") in ids]
    builder.flexible_ids = {
        occ.occurrence_id for occ in builder.occurrences
        if occ.classification in {"FLEXIBLE", "SOFTGOOD"}
    }
    used_parts = {occ.part_number for occ in builder.occurrences}
    builder.catalog.parts = {
        part_number: part for part_number, part in builder.catalog.parts.items()
        if part_number in used_parts
    }
    builder.mass_overrides_kg = {
        key: value for key, value in builder.mass_overrides_kg.items() if key in ids
    }
    builder.definition_of_done_requirements = {
        "source_baseline_commit": cfg.SOURCE_BASELINE_COMMIT,
        "forward_ballast_aft_face_z_mm": cfg.FORWARD_BALLAST_AFT_FACE_Z_MM,
        "arm_pivot_z_mm": cfg.ARM_PIVOT_Z_MM,
        "arm_length_mm": cfg.ARM_LENGTH_MM,
        "rigid_length_mm": cfg.RIGID_LENGTH_MM,
        "internal_buoy_ejector_occurrence_count": 0,
        "faceted_brep_allowed": 0,
        "physical_test_gates": [
            "PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED",
            "WET INFLATION / BREAKAWAY TEST REQUIRED",
            "QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM",
        ],
    }
    _refresh_global_shapes(builder)
    final_detail_naming.apply_final_names(builder)
    builder.root = cq.Assembly(name=f"STINGRAY_I5S_DF8_SHORT14_EXTERNAL_BUOY_{builder.state}_ASSY")
    r2_hierarchy.rebuild_named_hierarchy(builder)
    builder.root.add(builder.forward, name=builder.forward.name)
    builder.root.add(builder.arm_module, name=builder.arm_module.name)
    builder.root.add(builder.aft, name=builder.aft.name)


def build_short_state(state: str) -> build_r2.R2Builder:
    builder = build_r2.build_state(state)
    removed, _kept = _filter_source(builder)
    builder.removed_source_occurrence_ids = sorted(removed)
    _shift_occurrences(builder)
    _install_short_definitions(builder)
    _add_aft_structure(builder)
    _add_external_pack(builder)
    _add_inflation_module(builder)
    _add_structural_tether(builder)
    _install_motion_tracks(builder)
    _complete_inherited_attachment_map(builder)
    _finalize_builder(builder)
    return builder


def serialize_builder(builder: build_r2.R2Builder) -> dict[str, Any]:
    data = build_r2.serialize_builder(builder)
    data["kinematics"] = {
        "arm_angle_deg": g.DEPLOYED_ANGLE if builder.deployed else 0.0,
        "crosshead_z_mm": (
            g.kinematic(g.DEPLOYED_ANGLE if builder.deployed else 0.0)["crosshead_z"]
            + cfg.SOURCE_TO_NEW_PIVOT_TRANSLATION_MM
        ),
        "crosshead_travel_full_precision_mm": g.CROSSHEAD_TRAVEL,
        "pivot_z_mm": cfg.ARM_PIVOT_Z_MM,
        "arm_length_mm": cfg.ARM_LENGTH_MM,
    }
    data["source_baseline_commit"] = cfg.SOURCE_BASELINE_COMMIT
    data["removed_source_occurrence_ids"] = list(builder.removed_source_occurrence_ids)
    return data


def exact_mass_properties(builder: build_r2.R2Builder) -> dict[str, Any]:
    masses: list[float] = []
    centers: list[np.ndarray] = []
    local_inertias: list[np.ndarray] = []
    resolved_occurrences: list[dict[str, Any]] = []
    for occurrence in builder.occurrences:
        part = builder.catalog.parts[occurrence.part_number]
        mass = float(part.resolved_mass() or 0.0)
        if mass <= 0.0:
            raise ValueError(f"non-positive resolved mass for {occurrence.occurrence_id}")
        shape = g.moved(part.shape, occurrence.location)
        volume = float(shape.Volume())
        if volume <= 0.0 or not shape.isValid():
            raise ValueError(f"invalid mass-property shape for {occurrence.occurrence_id}")
        center = shape.Center()
        matrix = np.asarray(cq.Shape.matrixOfInertia(shape), dtype=float)
        masses.append(mass)
        centers.append(np.array([center.x, center.y, center.z], dtype=float))
        local_inertias.append(matrix * (mass / volume))
        resolved_occurrences.append({
            "occurrence_id": occurrence.occurrence_id,
            "part_number": occurrence.part_number,
            "mass_kg": mass,
            "centroid_mm": {"x": center.x, "y": center.y, "z": center.z},
        })
    total = float(sum(masses))
    cg = sum(mass * center for mass, center in zip(masses, centers)) / total
    inertia = np.zeros((3, 3), dtype=float)
    eye = np.eye(3)
    for mass, center, local in zip(masses, centers, local_inertias):
        delta = center - cg
        inertia += local + mass * ((delta @ delta) * eye - np.outer(delta, delta))
    principal = np.linalg.eigvalsh(inertia)
    return {
        "state": builder.state,
        "total_mass_kg": total,
        "mass_reserve_to_18_14_kg": cfg.MAX_MASS_KG - total,
        "cg_mm": {"x": float(cg[0]), "y": float(cg[1]), "z": float(cg[2])},
        "radial_cg_mm": float(np.hypot(cg[0], cg[1])),
        "tip_to_cg_mm": float(cg[2]),
        "inertia_tensor_kg_mm2": inertia.tolist(),
        "products_of_inertia_kg_mm2": {
            "Ixy": float(inertia[0, 1]), "Ixz": float(inertia[0, 2]), "Iyz": float(inertia[1, 2]),
        },
        "principal_moments_kg_mm2": principal.tolist(),
        "occurrence_count": len(builder.occurrences),
        "resolved_occurrences": resolved_occurrences,
    }


def write_pair(*, render: bool = False) -> tuple[build_r2.R2Builder, build_r2.R2Builder]:
    OUT.mkdir(parents=True, exist_ok=True)
    builders: list[build_r2.R2Builder] = []
    for state, filename in (("STOWED", STOWED_FILE), ("DEPLOYED", DEPLOYED_FILE)):
        print(f"Building SHORT14 {state} exact source assembly", flush=True)
        builder = build_short_state(state)
        output_path = OUT / filename
        build_r2.export_ap242(builder.root, output_path)
        build_r2.name_assembly_usage_occurrences(output_path)
        inventory_path = OUT / f"authoring_inventory_{state.lower()}.json"
        inventory_path.write_text(
            json.dumps(serialize_builder(builder), indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"Wrote {output_path} ({output_path.stat().st_size} bytes)", flush=True)
        builders.append(builder)

    manifest = {
        "schema": "AP242",
        "source_baseline_commit": cfg.SOURCE_BASELINE_COMMIT,
        "files": {},
        "hard_requirements": {
            "forward_ballast_aft_face_z_mm": cfg.FORWARD_BALLAST_AFT_FACE_Z_MM,
            "arm_pivot_z_mm": cfg.ARM_PIVOT_Z_MM,
            "arm_length_mm": cfg.ARM_LENGTH_MM,
            "rigid_length_mm": cfg.RIGID_LENGTH_MM,
            "body_reduction_mm": cfg.BODY_REDUCTION_MM,
            "maximum_rigid_od_mm": cfg.MAX_RIGID_OD_MM,
            "maximum_mass_kg": cfg.MAX_MASS_KG,
        },
    }
    for path in (OUT / STOWED_FILE, OUT / DEPLOYED_FILE,
                 OUT / "authoring_inventory_stowed.json", OUT / "authoring_inventory_deployed.json"):
        manifest["files"][path.name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }
    (OUT / "authoring_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    baseline_path = ROOT / "work" / "forward_arm_repack" / "updated_mass_properties.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    mass_result = {
        "schema": "STINGRAY_SHORT14_EXACT_OCCURRENCE_MASS_PROPERTIES_V1",
        "source_baseline": baseline,
        "short14_stowed": exact_mass_properties(builders[0]),
        "short14_deployed": exact_mass_properties(builders[1]),
        "fall_orientation_disposition": "QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM",
    }
    (OUT / "FINAL_MASS_CG_INERTIA.json").write_text(
        json.dumps(mass_result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    if render:
        import short14_external_buoy_render
        short14_external_buoy_render.render_views(
            builders[0], builders[1], ROOT, OUT / "inspection_views"
        )
    return builders[0], builders[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", choices=("STOWED", "DEPLOYED", "PAIR"), default="PAIR")
    parser.add_argument("--render", action="store_true", help="render exactly twelve inspection PNGs with PAIR")
    args = parser.parse_args()
    if args.state == "PAIR":
        write_pair(render=args.render)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    builder = build_short_state(args.state)
    filename = STOWED_FILE if args.state == "STOWED" else DEPLOYED_FILE
    output_path = OUT / filename
    build_r2.export_ap242(builder.root, output_path)
    build_r2.name_assembly_usage_occurrences(output_path)
    (OUT / f"authoring_inventory_{args.state.lower()}.json").write_text(
        json.dumps(serialize_builder(builder), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
