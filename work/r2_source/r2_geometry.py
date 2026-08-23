#!/usr/bin/env python3
"""Exact analytic B-rep geometry and kinematics for STINGRAY DF8 R2.

All unique rigid parts are authored in part-local coordinates.  Assembly state
is expressed only through occurrence placements.  Flexible articles may use a
state-specific exact B-rep representation while preserving occurrence identity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable

import cadquery as cq


# Frozen owner requirements -------------------------------------------------
NORMAL_OD = 53.0
NORMAL_R = NORMAL_OD / 2.0
HARD_OD = 57.150
HARD_R = HARD_OD / 2.0
PIVOT_R = 18.0
PIVOT_Z = 900.0
ARM_LENGTH = 733.806
DEPLOYED_ANGLE = 80.0
MAX_RIGID_LENGTH = 2032.0
MAX_SYSTEM_MASS_KG = 18.14
# The positive-side fixed-stop screw is shifted 0.25 mm outboard in stop-local
# X so its head clears both automatic-lock spring states and the retracted dog
# without approaching the pivot washer.  One shared station tuple keeps the
# stop, carrier, arm reliefs, and occurrence placement occurrence-matched.
FIXED_STOP_SCREW_STATIONS_MM = ((2.0, -7.8), (2.25, 7.8))

# R2 closure law.  The bell crank is aft/outboard of the pivot, allowing the
# crosshead and its three parallel power elements to occupy the arm module aft
# of WP03 instead of intersecting the long booster cylinders.
BELL_U = 6.0
BELL_V = 9.0
LINK_CENTER_DISTANCE = 19.95
CROSSHEAD_R = 18.0

SPRING_OD = 15.8
SPRING_WIRE = 3.0
SPRING_FREE = 195.0
SPRING_STOWED = 145.0
SPRING_RATE = 16.0

WP04_SPRING_OD = 22.0
WP04_SPRING_WIRE = 2.0
WP04_SPRING_FREE = 200.0
WP04_SPRING_STOWED = 85.0
WP04_SPRING_DEPLOYED = 170.0


DENSITY_KG_PER_MM3 = {
    "Ti-6Al-4V": 4.43e-6,
    "Ti-3Al-2.5V Grade 9": 4.48e-6,
    "17-4PH stainless steel": 7.75e-6,
    "316 stainless steel": 8.00e-6,
    "A4-80 stainless steel": 8.00e-6,
    "1.4310 stainless spring steel": 7.85e-6,
    "7075-T6 aluminum": 2.81e-6,
    "PEEK": 1.32e-6,
    "EPDM": 1.18e-6,
    "Acetal": 1.41e-6,
    "TPU-coated nylon": 1.20e-6,
    "HMPE rope": 0.97e-6,
    "Tungsten heavy alloy": 17.0e-6,
}


COLORS = {
    "titanium": cq.Color(0.53, 0.59, 0.64),
    "aluminum": cq.Color(0.58, 0.66, 0.73),
    "steel": cq.Color(0.29, 0.33, 0.37),
    "stainless": cq.Color(0.72, 0.75, 0.78),
    "tungsten": cq.Color(0.20, 0.22, 0.24),
    "peek": cq.Color(0.75, 0.58, 0.21),
    "spring": cq.Color(0.79, 0.43, 0.15),
    "gas": cq.Color(0.16, 0.47, 0.63),
    "hydraulic": cq.Color(0.11, 0.32, 0.50),
    "softgood": cq.Color(0.90, 0.34, 0.14, 0.70),
    "route": cq.Color(0.05, 0.57, 0.63),
    "rope": cq.Color(0.16, 0.25, 0.34),
    "black": cq.Color(0.06, 0.07, 0.08),
    "external": cq.Color(0.50, 0.50, 0.50, 0.35),
}


@dataclass
class PartDef:
    part_number: str
    revision: str
    description: str
    shape: cq.Shape
    material: str
    make_buy: str
    manufacturer: str
    cad_classification: str
    mass_kg: float | None = None
    source_url: str = ""
    purchase_url: str = ""
    process: str = ""
    finish: str = ""
    notes: str = ""
    color_key: str = "steel"
    external_context: bool = False

    def resolved_mass(self) -> float | None:
        if self.mass_kg is not None:
            return self.mass_kg
        density = DENSITY_KG_PER_MM3.get(self.material)
        return self.shape.Volume() * density if density else None


@dataclass
class Occurrence:
    occurrence_id: str
    part_number: str
    parent_path: str
    state: str
    location: cq.Location
    classification: str
    joint_type: str
    permitted_dof: str
    state_membership: str = "BOTH"
    notes: str = ""


@dataclass
class Connection:
    connection_id: str
    state: str
    occurrence_id: str
    mate_occurrence_id: str
    own_feature_id: str
    mate_feature_id: str
    connection_type: str
    permitted_dof: str
    retaining_hardware: str
    axial_retention: str
    lateral_retention: str
    anti_rotation: str
    upstream_load_path: str
    downstream_load_path: str
    service_method: str
    evidence: str


@dataclass
class PartCatalog:
    parts: dict[str, PartDef] = field(default_factory=dict)

    def add(self, part: PartDef) -> PartDef:
        prior = self.parts.get(part.part_number)
        if prior is not None:
            if prior.description != part.description or abs(prior.shape.Volume() - part.shape.Volume()) > 1.0e-6:
                raise ValueError(f"Conflicting part definition for {part.part_number}")
            return prior
        self.parts[part.part_number] = part
        return part


def identity_loc() -> cq.Location:
    return cq.Location()


def translation_loc(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> cq.Location:
    return cq.Location(cq.Vector(x, y, z))


def rotation_loc(axis: tuple[float, float, float], angle_deg: float) -> cq.Location:
    return cq.Location(cq.Vector(0, 0, 0), cq.Vector(*axis), angle_deg)


def loc_matrix(loc: cq.Location) -> list[list[float]]:
    tr = loc.wrapped.Transformation()
    return [[tr.Value(i, j) for j in range(1, 5)] for i in range(1, 4)]


def loc_is_identity(loc: cq.Location, tol: float = 1.0e-10) -> bool:
    ref = ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0))
    m = loc_matrix(loc)
    return all(abs(m[i][j] - ref[i][j]) <= tol for i in range(3) for j in range(4))


def moved(shape: cq.Shape, loc: cq.Location) -> cq.Shape:
    return shape.moved(loc)


def compound(shapes: Iterable[cq.Shape]) -> cq.Shape:
    return cq.Compound.makeCompound(list(shapes))


def cyl_z(radius: float, length: float, x: float = 0.0, y: float = 0.0, z0: float = 0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def tube_z(ro: float, ri: float, length: float, x: float = 0.0, y: float = 0.0, z0: float = 0.0) -> cq.Shape:
    return cyl_z(ro, length, x, y, z0).cut(cyl_z(ri, length + 0.4, x, y, z0 - 0.2))


def box_center(dx: float, dy: float, dz: float, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> cq.Shape:
    return cq.Workplane("XY").box(dx, dy, dz).translate((x, y, z)).val()


def triangular_wedge(radius: float, length: float, center_deg: float, half_deg: float, z0: float = 0.0,
                     x0: float = 0.0, y0: float = 0.0) -> cq.Shape:
    """Exact three-plane angular wedge; no polygonal arc approximation."""
    a0 = math.radians(center_deg - half_deg)
    a1 = math.radians(center_deg + half_deg)
    pts = [
        (x0, y0),
        (x0 + radius * math.cos(a0), y0 + radius * math.sin(a0)),
        (x0 + radius * math.cos(a1), y0 + radius * math.sin(a1)),
    ]
    return cq.Workplane("XY").polyline(pts).close().extrude(length).translate((0, 0, z0)).val()


def analytic_sector(ro: float, ri: float, length: float, center_deg: float, half_deg: float,
                    z0: float = 0.0, x0: float = 0.0, y0: float = 0.0) -> cq.Shape:
    annulus = tube_z(ro, ri, length, x0, y0, z0)
    wedge = triangular_wedge(ro * 2.5, length + 0.4, center_deg, half_deg, z0 - 0.2, x0, y0)
    return annulus.intersect(wedge)


def ring_y(x: float, z: float, width: float, ro: float, ri: float, y_center: float = 0.0) -> cq.Shape:
    outer = cq.Solid.makeCylinder(ro, width, cq.Vector(x, y_center - width / 2.0, z), cq.Vector(0, 1, 0))
    inner = cq.Solid.makeCylinder(ri, width + 0.6, cq.Vector(x, y_center - width / 2.0 - 0.3, z), cq.Vector(0, 1, 0))
    return outer.cut(inner)


def ring_x(y: float, z: float, width: float, ro: float, ri: float, x_center: float = 0.0) -> cq.Shape:
    outer = cq.Solid.makeCylinder(ro, width, cq.Vector(x_center - width / 2.0, y, z), cq.Vector(1, 0, 0))
    inner = cq.Solid.makeCylinder(ri, width + 0.6, cq.Vector(x_center - width / 2.0 - 0.3, y, z), cq.Vector(1, 0, 0))
    return outer.cut(inner)


def rod_between(p1: tuple[float, float, float], p2: tuple[float, float, float], radius: float) -> cq.Shape:
    v = cq.Vector(*(p2[i] - p1[i] for i in range(3)))
    return cq.Solid.makeCylinder(radius, v.Length, cq.Vector(*p1), v.normalized())


def tube_between(p1: tuple[float, float, float], p2: tuple[float, float, float], ro: float, ri: float) -> cq.Shape:
    v = cq.Vector(*(p2[i] - p1[i] for i in range(3)))
    outer = cq.Solid.makeCylinder(ro, v.Length, cq.Vector(*p1), v.normalized())
    inner = cq.Solid.makeCylinder(ri, v.Length + 0.4, cq.Vector(*p1) - v.normalized() * 0.2, v.normalized())
    return outer.cut(inner)


def _routed_round_solid(points: list[tuple[float, float, float]], radius: float) -> cq.Shape:
    """Fuse one positive-orientation round route before any lumen cut."""
    pieces: list[cq.Shape] = []
    for a, b in zip(points, points[1:]):
        pieces.append(rod_between(a, b, radius))
    for p in points[1:-1]:
        pieces.append(cq.Solid.makeSphere(radius, cq.Vector(*p)))
    out = pieces[0]
    for piece in pieces[1:]:
        out = out.fuse(piece)
    # Do not call removeSplitter/clean here: OCCT 7.9 can invalidate a valid
    # tangent rod/sphere union by collapsing the analytic seam at a formed
    # bend (observed on the captive door-lanyard route).
    return out


def routed_round(points: list[tuple[float, float, float]], ro: float, ri: float | None = None) -> cq.Shape:
    """Connected analytic tube/rod with spherical formed bends.

    Hollow routes are authored as one fused outer solid followed by one lumen
    subtraction.  Fusing individually hollow segment/bend pieces can leave
    disconnected or reverse-oriented solids where OCCT merges coincident
    inner faces; that construction produced the five-solid Bowden sheath.
    """
    if len(points) < 2:
        raise ValueError("A routed round article requires at least two points")
    if ro <= 0.0 or (ri is not None and not 0.0 < ri < ro):
        raise ValueError(f"Invalid routed-round radii ro={ro}, ri={ri}")
    for a, b in zip(points, points[1:]):
        if cq.Vector(*(b[i] - a[i] for i in range(3))).Length <= 1.0e-9:
            raise ValueError(f"Consecutive routed-round points must be distinct: {a}, {b}")

    outer = _routed_round_solid(points, ro)
    if ri is None:
        out = outer
    else:
        # Extend only the lumen centerline ends so the subtraction passes
        # cleanly through both outer end faces instead of leaving coincident
        # circular faces with ambiguous shell orientation.
        p0, p1 = (cq.Vector(*points[0]), cq.Vector(*points[1]))
        pn1, pn = (cq.Vector(*points[-2]), cq.Vector(*points[-1]))
        extension = max(0.20, ro * 0.25)
        first = p0 - (p1 - p0).normalized() * extension
        last = pn + (pn - pn1).normalized() * extension
        lumen_points = [first.toTuple(), *points[1:-1], last.toTuple()]
        lumen = _routed_round_solid(lumen_points, ri)
        out = outer.cut(lumen)

    solids = out.Solids()
    signed_volume = out.Volume()
    if len(solids) != 1 or not out.isValid() or signed_volume <= 0.0:
        raise ValueError(
            "Routed round article must be one valid positive-orientation solid; "
            f"found {len(solids)} solids, valid={out.isValid()}, "
            f"signed_volume_mm3={signed_volume}"
        )
    return solids[0]


def strap_between(p1: tuple[float, float, float], p2: tuple[float, float, float], width: float, thickness: float) -> cq.Shape:
    """Flat structural web aligned with a straight load-path segment."""
    v = cq.Vector(*(p2[i] - p1[i] for i in range(3)))
    length = v.Length
    base = box_center(thickness, width, length, 0.0, 0.0, length / 2.0)
    z_axis = cq.Vector(0, 0, 1)
    axis = z_axis.cross(v.normalized())
    angle = math.degrees(z_axis.getAngle(v.normalized()))
    if axis.Length > 1.0e-9:
        base = base.rotate((0, 0, 0), axis.toTuple(), angle)
    elif z_axis.dot(v.normalized()) < 0:
        base = base.rotate((0, 0, 0), (1, 0, 0), 180.0)
    return base.translate(p1)


def make_helix_z(od: float, wire: float, installed_length: float, turns: float, z0: float = 0.0,
                 x: float = 0.0, y: float = 0.0) -> cq.Shape:
    mean_d = od - wire
    helix_height = installed_length - wire
    pitch = helix_height / max(turns - 1.0, 1.0)
    path = cq.Wire.makeHelix(pitch, helix_height, mean_d / 2.0,
                             center=cq.Vector(x, y, z0 + wire / 2.0), dir=cq.Vector(0, 0, 1))
    profile = cq.Workplane("XZ", origin=(x + mean_d / 2.0, y, z0 + wire / 2.0)).circle(wire / 2.0)
    return profile.sweep(path, isFrenet=True).val()


def make_compression_spring_local(od: float, wire: float, installed_length: float, total_turns: float) -> cq.Shape:
    # A compression spring is one swept wire.  The former representation put
    # two complete torus solids over the first and last helix turns, producing
    # a formally valid three-solid compound with positive-volume internal
    # intersections.  The exact helical sweep already has closed planar end
    # faces and therefore needs no separate cosmetic end-coil solids.
    spring = make_helix_z(od, wire, installed_length, total_turns)
    solids = spring.Solids()
    if len(solids) != 1 or not spring.isValid():
        raise ValueError(
            f"Compression spring must be one valid swept solid; "
            f"found {len(solids)} solids (valid={spring.isValid()})"
        )
    return solids[0]


def make_counterbored_screw(diameter: float, length: float, head_d: float, head_h: float) -> cq.Shape:
    shank = cq.Solid.makeCylinder(diameter / 2.0, length, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    head = cq.Solid.makeCylinder(head_d / 2.0, head_h, cq.Vector(0, 0, length), cq.Vector(0, 0, 1))
    drive = box_center(head_d * 0.42, head_d * 0.13, head_h * 0.65, 0, 0, length + head_h * 0.72)
    return shank.fuse(head).cut(drive)


def make_flush_screw(diameter: float, length: float, head_d: float, head_h: float) -> cq.Shape:
    shank = cq.Solid.makeCylinder(diameter / 2.0, length, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    cone = cq.Solid.makeCone(diameter / 2.0, head_d / 2.0, head_h, cq.Vector(0, 0, length), cq.Vector(0, 0, 1))
    slot = box_center(head_d * 0.45, head_d * 0.12, head_h * 0.40, 0, 0, length + head_h * 0.75)
    return shank.fuse(cone).cut(slot)


def _single_valid_positive(shape: cq.Shape, label: str) -> cq.Shape:
    """Return one exact solid or fail immediately at the authoring boundary."""
    solids = shape.Solids()
    if len(solids) != 1 or not shape.isValid() or shape.Volume() <= 0.0:
        raise ValueError(
            f"{label} must be one valid positive-volume solid; "
            f"solids={len(solids)}, valid={shape.isValid()}, volume={shape.Volume()}"
        )
    return solids[0]


def make_clearance_counterbore_cutter_z(
    shank_diameter_mm: float,
    head_diameter_mm: float,
    through_thickness_mm: float,
    head_depth_mm: float,
    z0: float = 0.0,
    overrun_mm: float = 0.20,
) -> cq.Shape:
    """Coaxial +Z clearance/counterbore void with a finite Boolean overrun.

    ``z0`` is the parent entry face.  The cutter begins just before that face,
    the clearance portion traverses the requested parent thickness, and the
    larger counterbore stops at ``z0 + head_depth_mm``.
    """
    if not (
        shank_diameter_mm > 0.0
        and head_diameter_mm > shank_diameter_mm
        and through_thickness_mm > 0.0
        and head_depth_mm > 0.0
        and overrun_mm > 0.0
    ):
        raise ValueError("Counterbore dimensions must be positive and head diameter must exceed shank diameter")
    clearance = cyl_z(
        shank_diameter_mm / 2.0,
        through_thickness_mm + 2.0 * overrun_mm,
        z0=z0 - overrun_mm,
    )
    counterbore = cyl_z(
        head_diameter_mm / 2.0,
        head_depth_mm + overrun_mm,
        z0=z0 - overrun_mm,
    )
    return _single_valid_positive(clearance.fuse(counterbore), "clearance/counterbore cutter")


def make_clearance_countersink_cutter_z(
    shank_diameter_mm: float,
    head_diameter_mm: float,
    through_thickness_mm: float,
    countersink_depth_mm: float,
    z0: float = 0.0,
    overrun_mm: float = 0.20,
) -> cq.Shape:
    """Coaxial +Z through-clearance and conical countersink Boolean cutter."""
    if not (
        shank_diameter_mm > 0.0
        and head_diameter_mm > shank_diameter_mm
        and through_thickness_mm > 0.0
        and countersink_depth_mm > 0.0
        and overrun_mm > 0.0
    ):
        raise ValueError("Countersink dimensions must be positive and head diameter must exceed shank diameter")
    clearance = cyl_z(
        shank_diameter_mm / 2.0,
        through_thickness_mm + 2.0 * overrun_mm,
        z0=z0 - overrun_mm,
    )
    sink = cq.Solid.makeCone(
        head_diameter_mm / 2.0,
        shank_diameter_mm / 2.0,
        countersink_depth_mm + overrun_mm,
        cq.Vector(0.0, 0.0, z0 - overrun_mm),
        cq.Vector(0.0, 0.0, 1.0),
    )
    return _single_valid_positive(clearance.fuse(sink), "clearance/countersink cutter")


def make_tapped_hole_cutter_z(
    tap_drill_diameter_mm: float,
    depth_mm: float,
    thread_major_diameter_mm: float | None = None,
    lead_chamfer_depth_mm: float = 0.30,
    z0: float = 0.0,
    overrun_mm: float = 0.20,
) -> cq.Shape:
    """Blind +Z tapped-hole authoring void using the controlled minor bore.

    Cosmetic helical thread faces are intentionally omitted.  When a major
    diameter is supplied, a finite conical lead-in represents the tap chamfer
    while the load-bearing thread identity remains in the process definition.
    """
    major = thread_major_diameter_mm or tap_drill_diameter_mm
    if not (
        tap_drill_diameter_mm > 0.0
        and major >= tap_drill_diameter_mm
        and depth_mm > 0.0
        and 0.0 <= lead_chamfer_depth_mm < depth_mm
        and overrun_mm > 0.0
    ):
        raise ValueError("Tapped-hole cutter dimensions are inconsistent")
    bore = cyl_z(
        tap_drill_diameter_mm / 2.0,
        depth_mm + overrun_mm,
        z0=z0 - overrun_mm,
    )
    if major == tap_drill_diameter_mm or lead_chamfer_depth_mm == 0.0:
        return _single_valid_positive(bore, "tapped-hole cutter")
    lead = cq.Solid.makeCone(
        major / 2.0,
        tap_drill_diameter_mm / 2.0,
        lead_chamfer_depth_mm + overrun_mm,
        cq.Vector(0.0, 0.0, z0 - overrun_mm),
        cq.Vector(0.0, 0.0, 1.0),
    )
    return _single_valid_positive(bore.fuse(lead), "tapped-hole cutter")


def make_bored_mounting_boss_z(
    outer_diameter_mm: float,
    height_mm: float,
    bore_diameter_mm: float,
    z0: float = 0.0,
) -> cq.Shape:
    """One +Z annular mounting boss with an exact full-depth cylindrical bore."""
    if not (outer_diameter_mm > bore_diameter_mm > 0.0 and height_mm > 0.0):
        raise ValueError("Mounting-boss OD must exceed its positive bore diameter")
    boss = cyl_z(outer_diameter_mm / 2.0, height_mm, z0=z0)
    bore = cyl_z(bore_diameter_mm / 2.0, height_mm + 0.40, z0=z0 - 0.20)
    return _single_valid_positive(boss.cut(bore), "bored mounting boss")


def make_fixed_stop_landing_local(
    width_mm: float = 14.0,
    depth_mm: float = 12.0,
    thickness_mm: float = 1.60,
    top_z: float = -2.80,
) -> cq.Shape:
    """Connected fixed-stop mounting land in the existing local stop frame.

    A short central neck overlaps the current 5.5 x 8.2 x 4.0 stop body, so
    fusing this helper cannot leave a floating landing plate.
    """
    if not (width_mm >= 12.0 and depth_mm >= 10.0 and thickness_mm > 0.0):
        raise ValueError("Fixed-stop land is too small for two M3 and two H7 features")
    land = box_center(
        width_mm, depth_mm, thickness_mm,
        0.0, 0.0, top_z - thickness_mm / 2.0,
    )
    neck = box_center(5.50, 8.20, 1.00, 0.0, 0.0, top_z + 0.45)
    return _single_valid_positive(land.fuse(neck), "fixed-stop mounting land")


def make_fixed_stop_hole_cutters_local(
    through_thickness_mm: float = 2.80,
    entry_z: float = -4.40,
    m3_clearance_diameter_mm: float = 3.20,
    dowel_h7_diameter_mm: float = 3.00,
) -> tuple[cq.Shape, cq.Shape]:
    """Return separate two-hole M3 and two-hole H7 cutter compounds.

    The local pattern preserves finite edge distance on the default 14 x 12
    mm land.  Keeping screw and dowel cutters separate lets the integrator cut
    clearance in one parent and the occurrence-matched tapped/reamed void in
    its mate without conflating the two manufacturing operations.
    """
    if not (through_thickness_mm > 0.0 and m3_clearance_diameter_mm > 0.0 and dowel_h7_diameter_mm > 0.0):
        raise ValueError("Fixed-stop hole dimensions must be positive")
    screw_cutters = [
        cyl_z(m3_clearance_diameter_mm / 2.0, through_thickness_mm + 0.40,
              x=x, y=-2.60, z0=entry_z - 0.20)
        for x in (-3.50, 3.50)
    ]
    dowel_cutters = [
        cyl_z(dowel_h7_diameter_mm / 2.0, through_thickness_mm + 0.40,
              x=x, y=2.60, z0=entry_z - 0.20)
        for x in (-3.50, 3.50)
    ]
    if any(not cutter.isValid() or cutter.Volume() <= 0.0 for cutter in screw_cutters + dowel_cutters):
        raise ValueError("Fixed-stop hole cutter generation failed")
    return compound(screw_cutters), compound(dowel_cutters)


def make_taper_pin_bore_x(
    small_diameter_mm: float,
    large_diameter_mm: float,
    length_mm: float,
    y: float = 0.0,
    z: float = 0.0,
    x_center: float = 0.0,
    overrun_mm: float = 0.20,
) -> cq.Shape:
    """Centered +X taper-pin bore cutter with constant-diameter overruns."""
    if not (
        large_diameter_mm > small_diameter_mm > 0.0
        and length_mm > 0.0
        and overrun_mm > 0.0
    ):
        raise ValueError("Taper-pin bore dimensions are inconsistent")
    x0 = x_center - length_mm / 2.0
    lead = cq.Solid.makeCylinder(
        small_diameter_mm / 2.0, overrun_mm,
        cq.Vector(x0 - overrun_mm, y, z), cq.Vector(1.0, 0.0, 0.0),
    )
    taper = cq.Solid.makeCone(
        small_diameter_mm / 2.0, large_diameter_mm / 2.0, length_mm,
        cq.Vector(x0, y, z), cq.Vector(1.0, 0.0, 0.0),
    )
    exit_relief = cq.Solid.makeCylinder(
        large_diameter_mm / 2.0, overrun_mm,
        cq.Vector(x0 + length_mm, y, z), cq.Vector(1.0, 0.0, 0.0),
    )
    return _single_valid_positive(lead.fuse(taper).fuse(exit_relief), "taper-pin bore cutter")


def make_external_circlip_groove_cutter_z(
    shaft_diameter_mm: float,
    groove_diameter_mm: float,
    groove_width_mm: float,
    z_center: float,
    axial_overrun_mm: float = 0.02,
    radial_overrun_mm: float = 0.20,
) -> cq.Shape:
    """Annular cutter for an occurrence-matched external circlip groove."""
    if not (
        shaft_diameter_mm > groove_diameter_mm > 0.0
        and groove_width_mm > 0.0
        and axial_overrun_mm >= 0.0
        and radial_overrun_mm > 0.0
    ):
        raise ValueError("External-circlip groove dimensions are inconsistent")
    cutter = tube_z(
        shaft_diameter_mm / 2.0 + radial_overrun_mm,
        groove_diameter_mm / 2.0,
        groove_width_mm + 2.0 * axial_overrun_mm,
        z0=z_center - groove_width_mm / 2.0 - axial_overrun_mm,
    )
    return _single_valid_positive(cutter, "external-circlip groove cutter")


def make_service_cap_mating_neck_local(
    bore_diameter_mm: float = 10.60,
    neck_outer_diameter_mm: float = 13.90,
    cap_skirt_outer_diameter_mm: float = 15.60,
    collar_outer_diameter_mm: float = 17.00,
    height_mm: float = 6.50,
) -> cq.Shape:
    """One connected bobbin-cap neck with shoulder and three bayonet slots.

    The central neck supports the bobbin axially.  A base annulus joins it to
    the outer lock collar.  Three L-shaped openings in that collar provide an
    axial insertion lane followed by a finite tangential locking pocket for
    the service-cap lugs.
    """
    bore_r = bore_diameter_mm / 2.0
    neck_r = neck_outer_diameter_mm / 2.0
    skirt_r = cap_skirt_outer_diameter_mm / 2.0
    collar_r = collar_outer_diameter_mm / 2.0
    if not (0.0 < bore_r < neck_r < skirt_r < collar_r and height_mm >= 5.0):
        raise ValueError("Service-cap mating-neck diameters or height are inconsistent")
    # The bridge shoulder is at the top of the bayonet cavity.  Placing it
    # below z=0 formerly made the service-cap disk occupy 229 mm3 of housing
    # stock; the top shoulder instead joins neck and collar while providing a
    # real axial stop at the end of the cap skirt.
    base = tube_z(collar_r, bore_r, 0.50, z0=height_mm - 0.50)
    neck = tube_z(neck_r, bore_r, height_mm)
    collar = tube_z(collar_r, skirt_r + 0.10, height_mm)
    mating = base.fuse(neck).fuse(collar)
    for phi in (0.0, 120.0, 240.0):
        entry = box_center(1.50, 2.40, 3.20, collar_r - 0.25, 0.0, height_mm - 1.40)
        lock = box_center(1.50, 4.20, 1.40, collar_r - 0.25, 1.50, height_mm - 1.80)
        cutter = entry.fuse(lock).rotate((0, 0, 0), (0, 0, 1), phi)
        mating = mating.cut(cutter)
    return _single_valid_positive(mating, "service-cap mating neck")


def make_captive_inhibit_slider_pin_local(
    diameter_mm: float = 1.20,
    grip_mm: float = 6.00,
    head_diameter_mm: float = 1.60,
    head_height_mm: float = 0.60,
    groove_from_end_mm: float = 0.80,
) -> cq.Shape:
    """Grooved +Y inhibit slider compatible with the source pose convention."""
    pin = make_clevis_pin(
        diameter_mm, grip_mm, head_diameter_mm, head_height_mm,
        groove_from_end=groove_from_end_mm,
    )
    return _single_valid_positive(pin, "captive inhibit slider pin")


def make_captive_inhibit_closed_guide_local(
    pin_x: float = 17.0,
    pin_z: float = 0.0,
    cage_y0: float = 2.24,
    cage_length_mm: float = 7.30,
    cage_outer_radius_mm: float = 1.15,
    keeper_clearance_radius_mm: float = 0.85,
    pin_clearance_radius_mm: float = 0.65,
    end_stop_width_mm: float = 0.35,
) -> cq.Shape:
    """Closed +Y keeper cage for the occurrence-specific inhibit slider.

    The annular cage overlaps the existing guide-side rail at its inboard end.
    Its reduced-bore outboard stop passes the pin shank but cannot pass the
    r=0.80 crescent keeper.  The keeper therefore remains positively trapped
    over the full y=2.425..8.825 mm endpoint motion while the pin can translate.
    """
    if not (
        cage_length_mm > end_stop_width_mm > 0.0
        and cage_outer_radius_mm > keeper_clearance_radius_mm > pin_clearance_radius_mm > 0.0
    ):
        raise ValueError("Captive inhibit-guide dimensions are inconsistent")
    cage = ring_y(
        pin_x, pin_z, cage_length_mm,
        cage_outer_radius_mm, keeper_clearance_radius_mm,
        cage_y0 + cage_length_mm / 2.0,
    )
    stop = ring_y(
        pin_x, pin_z, end_stop_width_mm,
        cage_outer_radius_mm, pin_clearance_radius_mm,
        cage_y0 + cage_length_mm - end_stop_width_mm / 2.0,
    )
    return _single_valid_positive(cage.fuse(stop), "captive inhibit closed guide")


def make_hex_nut(thread_d: float, across_flats: float, thickness: float) -> cq.Shape:
    ro = across_flats / math.sqrt(3.0)
    pts = [(ro * math.cos(math.radians(60 * i)), ro * math.sin(math.radians(60 * i))) for i in range(6)]
    nut = cq.Workplane("XY").polyline(pts).close().extrude(thickness).val()
    return nut.cut(cyl_z(thread_d / 2.0 + 0.12, thickness + 0.4, z0=-0.2))


def make_clevis_pin(diameter: float, grip: float, head_d: float, head_h: float, groove_from_end: float = 0.8) -> cq.Shape:
    shaft = cq.Solid.makeCylinder(diameter / 2.0, grip, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    head = cq.Solid.makeCylinder(head_d / 2.0, head_h, cq.Vector(0, -head_h, 0), cq.Vector(0, 1, 0))
    groove = cq.Solid.makeCylinder(diameter / 2.0 + 0.25, 0.45,
                                   cq.Vector(0, grip - groove_from_end, 0), cq.Vector(0, 1, 0))
    core = cq.Solid.makeCylinder(diameter / 2.0 - 0.25, 0.65,
                                 cq.Vector(0, grip - groove_from_end - 0.1, 0), cq.Vector(0, 1, 0))
    return shaft.fuse(head).cut(groove.cut(core))


def make_external_retaining_ring(shaft_d: float, width: float = 0.55) -> cq.Shape:
    ring = ring_y(0.0, 0.0, width, shaft_d / 2.0 + 0.9, shaft_d / 2.0 - 0.05, 0.0)
    return ring.cut(box_center(shaft_d * 0.75, width + 0.2, shaft_d * 0.55,
                               shaft_d * 0.55, 0.0, 0.0))


def make_axial_bulkhead_union(tube_od: float, bore_d: float, flange_d: float, length: float) -> cq.Shape:
    body = cq.Solid.makeCylinder(tube_od / 2.0, length, cq.Vector(0, 0, -length / 2.0), cq.Vector(0, 0, 1))
    flange1 = cq.Solid.makeCylinder(flange_d / 2.0, 1.2, cq.Vector(0, 0, -length / 2.0 - 1.2), cq.Vector(0, 0, 1))
    flange2 = cq.Solid.makeCylinder(flange_d / 2.0, 1.2, cq.Vector(0, 0, length / 2.0), cq.Vector(0, 0, 1))
    bore = cq.Solid.makeCylinder(bore_d / 2.0, length + 3.0, cq.Vector(0, 0, -length / 2.0 - 1.5), cq.Vector(0, 0, 1))
    return body.fuse(flange1).fuse(flange2).cut(bore)


def make_p_clamp(tube_od: float, band_t: float = 0.7, band_w: float = 5.0) -> cq.Shape:
    band = ring_y(0.0, 0.0, band_w, tube_od / 2.0 + band_t, tube_od / 2.0 + 0.15, 0.0)
    gap = box_center(tube_od, band_w + 0.4, tube_od * 0.8, tube_od * 0.48, 0.0, 0.0)
    tab = box_center(6.0, band_w, 2.0, tube_od / 2.0 + 3.0, 0.0, -tube_od / 2.0)
    hole = cq.Solid.makeCylinder(1.6, band_w + 0.4,
                                 cq.Vector(tube_od / 2.0 + 4.0, -band_w / 2.0 - 0.2, -tube_od / 2.0), cq.Vector(0, 1, 0))
    return band.cut(gap).fuse(tab).cut(hole)


def kinematic(theta_deg: float) -> dict[str, float]:
    t = math.radians(theta_deg)
    bell_r = PIVOT_R + BELL_U * math.cos(t) + BELL_V * math.sin(t)
    bell_z = PIVOT_Z - BELL_U * math.sin(t) + BELL_V * math.cos(t)
    radicand = LINK_CENTER_DISTANCE**2 - (bell_r - CROSSHEAD_R) ** 2
    if radicand <= 0:
        raise ValueError(f"Kinematic closure failed at {theta_deg} degrees")
    crosshead_z = bell_z + math.sqrt(radicand)
    travel = kinematic_z0() - crosshead_z
    return {"bell_r": bell_r, "bell_z": bell_z, "crosshead_z": crosshead_z, "travel": travel}


def kinematic_z0() -> float:
    bell_r = PIVOT_R + BELL_U
    bell_z = PIVOT_Z + BELL_V
    return bell_z + math.sqrt(LINK_CENTER_DISTANCE**2 - (bell_r - CROSSHEAD_R) ** 2)


CROSSHEAD_TRAVEL = kinematic(DEPLOYED_ANGLE)["travel"]
SPRING_DEPLOYED = SPRING_STOWED + CROSSHEAD_TRAVEL
SPRING_FIXED_Z = kinematic_z0() + SPRING_STOWED


def arm_occurrence_loc(theta_deg: float, clock_deg: float) -> cq.Location:
    return (
        rotation_loc((0, 0, 1), clock_deg)
        * translation_loc(PIVOT_R, 0.0, PIVOT_Z)
        * rotation_loc((0, 1, 0), theta_deg)
    )


def radial_occurrence_loc(radius: float, phi_deg: float, z: float = 0.0,
                          local_axis: str = "Z") -> cq.Location:
    loc = rotation_loc((0, 0, 1), phi_deg) * translation_loc(radius, 0.0, z)
    if local_axis == "X_TO_Z":
        loc = loc * rotation_loc((0, 1, 0), -90.0)
    return loc


def link_occurrence_loc(theta_deg: float, y_offset: float, clock_deg: float) -> cq.Location:
    kin = kinematic(theta_deg)
    dx = kin["bell_r"] - CROSSHEAD_R
    dz = kin["bell_z"] - kin["crosshead_z"]
    angle_y = -math.degrees(math.atan2(dz, dx))
    return (
        rotation_loc((0, 0, 1), clock_deg)
        * translation_loc(CROSSHEAD_R, y_offset, kin["crosshead_z"])
        * rotation_loc((0, 1, 0), angle_y)
    )


def make_arm_part_local() -> cq.Shape:
    """Smooth analytic stowed OML with true local pivot datum at the origin."""
    axis_x = -PIVOT_R
    # A narrow analytic sector prevents the three roots from occupying the
    # same central volume at high deployment angles.  The section is a true
    # cylindrical B-rep, not planar patch tiling.
    root = analytic_sector(NORMAL_R, 18.8, 67.0, 0.0, 15.0, -10.0, axis_x, 0.0)
    blade = analytic_sector(NORMAL_R, 24.0, ARM_LENGTH - 42.0, 0.0, 15.0, 42.0, axis_x, 0.0)
    transition = analytic_sector(NORMAL_R, 22.2, 57.0, 0.0, 15.0, 15.0, axis_x, 0.0)
    arm = root.fuse(transition).fuse(blade)
    # Real root access clears both link plates and the crosshead clevis through
    # their full motion; it is machined before the integral clevis is added.
    # Clear the crosshead and linkage on the inboard side while leaving a
    # continuous outer radial backbone beyond global r=22.5 mm.  The former
    # full-depth pocket either severed the pivot boss or, when narrowed,
    # placed side rails inside the crosshead and link-pin envelopes.
    arm = arm.cut(box_center(19.2, 14.0, 50.0, -4.0, 0.0, 15.0))
    # A second local corridor receives the two bell-crank link plates between
    # the reamed ears; it stops before the outer backbone becomes load-bearing.
    arm = arm.cut(box_center(7.0, 7.0, 22.0, 6.0, 0.0, 9.0))
    # The analytic shell itself reaches the exact 733.806 mm tip datum.  A
    # formerly separate inboard tongue was radially disconnected and was then
    # discarded by the largest-solid selector, shortening the exported arm.
    # Integral pivot boss and bell-crank clevis, both genuinely reamed after fusion.
    arm = arm.fuse(ring_y(0.0, 0.0, 11.6, 6.2, 4.18))
    attach = (BELL_U, BELL_V)
    for yy in (-3.65, 3.65):
        # Narrow, fully machined clevis ribs remain outside the two 1.5 mm link
        # plates with 0.15 mm nominal side clearance.
        web = rod_between((0.0, yy, 0.0), (attach[0], yy, attach[1]), 1.0)
        ear = ring_y(attach[0], attach[1], 1.9, 4.2, 2.18, yy)
        arm = arm.fuse(web).fuse(ear)
    # Full-span link pin and its crescent retainer require clearance through
    # both cheeks, not merely the nominal 12 mm grip interval.
    bell_bore = cq.Solid.makeCylinder(2.18, 14.4, cq.Vector(attach[0], -7.2, attach[1]), cq.Vector(0, 1, 0))
    arm = arm.cut(bell_bore)
    bell_head_relief = cq.Solid.makeCylinder(3.20, 1.8,
                                             cq.Vector(attach[0], -7.6, attach[1]),
                                             cq.Vector(0, 1, 0))
    arm = arm.cut(bell_head_relief)
    bell_clip_relief = cq.Solid.makeCylinder(2.62, 1.2,
                                             cq.Vector(attach[0], 5.0, attach[1]),
                                             cq.Vector(0, 1, 0))
    arm = arm.cut(bell_clip_relief)
    pivot_bore = cq.Solid.makeCylinder(4.18, 14.0, cq.Vector(0.0, -7.0, 0.0), cq.Vector(0, 1, 0))
    arm = arm.cut(pivot_bore)
    # Machine both thrust faces clear of the cylindrical OML/root stock.  The
    # integral boss ends at y=+/-5.8 mm; these shallow coaxial reliefs remove
    # only material outside those faces so the PEEK washers seat without
    # occupying the arm solid during rotation.
    arm = arm.cut(cq.Solid.makeCylinder(6.10, 1.4,
                                        cq.Vector(0.0, 5.8, 0.0), cq.Vector(0, 1, 0)))
    arm = arm.cut(cq.Solid.makeCylinder(6.10, 1.4,
                                        cq.Vector(0.0, -5.8, 0.0), cq.Vector(0, -1, 0)))
    # Replaceable stop strike and aft retention pockets are real machined cavities.
    arm = arm.cut(box_center(10.2, 10.0, 4.8, 4.0, 0.0, -8.5))
    for x in (1.2, 6.8):
        arm = arm.cut(cq.Solid.makeCylinder(
            1.25, 3.8, cq.Vector(x, 3.0, -8.5), cq.Vector(0, 1, 0)
        ))
    arm = arm.cut(box_center(4.4, 4.2, 3.4, 4.0, 0.0, -4.5))
    arm = arm.cut(box_center(3.2, 3.2, 5.5, -1.0, 0.0, ARM_LENGTH - 3.5))
    # Occurrence-reused arm-local strike gives each stow dog a real 0.15 mm
    # retained interface at 0 degrees and exits the dog/guide envelope before
    # the first one-degree motion sample.
    arm = arm.fuse(box_center(
        5.05, 3.60, 4.60, 3.675, 0.0, ARM_LENGTH - 3.5
    ))
    # Two equal occurrence-matched M3 tapped bosses close the replaceable
    # stop-pad joint from its negative-Y service face.  The heads therefore
    # remain opposite the positive-Y automatic-lock channel at full deploy.
    for x in (1.2, 6.8):
        arm = arm.cut(cq.Solid.makeCylinder(
            1.65, 3.50, cq.Vector(x, 3.00, -8.5), cq.Vector(0, 1, 0)
        ))
    for x in (1.2, 6.8):
        boss = cq.Solid.makeCylinder(
            1.60, 3.10, cq.Vector(x, 3.20, -8.5), cq.Vector(0, 1, 0)
        ).cut(cq.Solid.makeCylinder(
            1.25, 3.50, cq.Vector(x, 3.00, -8.5), cq.Vector(0, 1, 0)
        ))
        arm = arm.fuse(boss)
        arm = arm.fuse(box_center(1.00, 1.00, 2.50, x, 5.50, -6.95))
    for x in (1.2, 6.8):
        arm = arm.cut(cq.Solid.makeCylinder(
            1.25, 3.50, cq.Vector(x, 3.00, -8.5), cq.Vector(0, 1, 0)
        ))
        # The captive screw head is seated by the replaceable stop pad, not
        # by the arm.  Clear its full positive-Y envelope from the arm so the
        # only remaining screw/arm common volume is the occurrence-matched
        # M3 major/minor thread representation in the equal tapped bosses.
        arm = arm.cut(cq.Solid.makeCylinder(
            2.85, 3.40, cq.Vector(x, -5.00, -8.5), cq.Vector(0, 1, 0)
        ))
    arm = arm.cut(cq.Solid.makeCylinder(
        6.10, 1.4, cq.Vector(0.0, 5.8, 0.0), cq.Vector(0, 1, 0)
    ))
    # Re-establish the negative-side thrust-washer relief after fusing the
    # tapped-boss support webs; no later feature may re-enter that bearing
    # envelope.
    arm = arm.cut(cq.Solid.makeCylinder(
        6.10, 1.4, cq.Vector(0.0, -5.8, 0.0), cq.Vector(0, -1, 0)
    ))
    # At the 80-degree stop the two fixed carrier screws pass immediately
    # outboard of the arm root.  Machine occurrence-matched head, captive-neck
    # and thread-envelope reliefs in the arm so the stationary fasteners have
    # a real service corridor rather than grazing the rotating arm solid.
    for stop_x, y in FIXED_STOP_SCREW_STATIONS_MM:
        arm_x = 3.6 + stop_x
        arm = arm.cut(cyl_z(2.85, 3.20, arm_x, y, -13.10))
        arm = arm.cut(cyl_z(1.20, 5.40, arm_x, y, -10.20))
        arm = arm.cut(cyl_z(1.65, 3.40, arm_x, y, -5.20))
    # The stationary stop-land screws and dowels trace short arcs through the
    # arm-local frame during deployment.  Endpoint-only cylindrical reliefs
    # left positive-volume intersections at 36..66 degrees (dowels) and
    # 75..78 degrees (screw heads after the positive-side 0.25 mm station
    # shift).  Machine their measured one-degree swept
    # envelopes with 0.05 mm radial/axial stock allowance, including one
    # bounding sample on either side of every observed range.
    stop_frame = (
        arm_occurrence_loc(DEPLOYED_ANGLE, 0.0)
        * translation_loc(4.0, 0.0, -8.5)
        * translation_loc(-0.4, 0.0, -4.0)
    )
    fixed_screw_clearance = (
        cyl_z(2.80, 3.10, z0=-3.05)
        .fuse(cyl_z(1.15, 5.10, z0=-0.05))
        .fuse(cyl_z(1.55, 3.10, z0=4.95))
    )
    dowel_clearance = cyl_z(1.55, 8.10, z0=-0.05)
    swept_fixed_hardware_cutters: list[cq.Shape] = []
    for angle in range(35, 68):
        stop_to_arm = arm_occurrence_loc(float(angle), 0.0).inverse * stop_frame
        for y in (-8.0, 8.0):
            swept_fixed_hardware_cutters.append(
                moved(dowel_clearance, stop_to_arm * translation_loc(7.0, y, 3.05))
            )
    for angle in range(74, 81):
        stop_to_arm = arm_occurrence_loc(float(angle), 0.0).inverse * stop_frame
        for screw_x, y in FIXED_STOP_SCREW_STATIONS_MM:
            swept_fixed_hardware_cutters.append(
                moved(
                    fixed_screw_clearance,
                    stop_to_arm * translation_loc(screw_x, y, 2.50),
                )
            )
    for cutter in swept_fixed_hardware_cutters:
        arm = arm.cut(cutter)
    solids = arm.Solids()
    if len(solids) > 1:
        ordered = sorted(solids, key=lambda solid: solid.Volume(), reverse=True)
        machining_islands = sum(solid.Volume() for solid in ordered[1:])
        if machining_islands <= 1.0:
            # The occurrence-matched boss bores can isolate sub-mm3 crescent
            # chips at the root-pocket boundary.  They are removed by the
            # specified milling operation and are not part of the finished
            # arm article.
            arm = ordered[0]
            solids = [arm]
    if len(solids) != 1:
        detail = [
            {
                "volume_mm3": solid.Volume(),
                "bbox_mm": (
                    solid.BoundingBox().xmin, solid.BoundingBox().xmax,
                    solid.BoundingBox().ymin, solid.BoundingBox().ymax,
                    solid.BoundingBox().zmin, solid.BoundingBox().zmax,
                ),
            }
            for solid in solids
        ]
        raise ValueError(f"Arm must be one connected solid; found {len(solids)} solids: {detail}")
    # Unify coplanar and coaxial machining faces after every functional cut.
    # This retains the analytic cylindrical OML and all bores/pockets while
    # eliminating Boolean-history seam fragments from the exported exact BREP.
    arm = solids[0].clean()
    cleaned_solids = arm.Solids()
    if len(cleaned_solids) != 1 or not arm.isValid():
        raise ValueError(
            f"Cleaned arm must remain one valid exact solid; "
            f"found {len(cleaned_solids)} solids (valid={arm.isValid()})"
        )
    return cleaned_solids[0]


def make_fixed_sector_local() -> cq.Shape:
    # Leave a manufactured angular access corridor around each adjacent pivot
    # lug set.  The two route bores remain at +/-25 degrees with machined edge
    # stock, while the +/-29 degree sector boundary clears adjacent pin heads
    # and retainers throughout the arm sweep.
    out = analytic_sector(28.5, 24.2, 745.0, 0.0, 29.0, 0.0)
    for angle in (-25.0, 25.0):
        x = 26.2 * math.cos(math.radians(angle))
        y = 26.2 * math.sin(math.radians(angle))
        out = out.cut(cyl_z(1.35, 745.4, x, y, -0.2))
        # Counterbores clear the largest two-collar gas gland flange
        # (2.45 mm radius) plus 0.15 mm assembly clearance.  The prior
        # 2.25 mm recess left both end flanges inside sector stock.
        out = out.cut(cyl_z(2.60, 1.6, x, y, -0.2))
        out = out.cut(cyl_z(2.60, 1.6, x, y, 743.6))
    return out


def make_longeron_local() -> cq.Shape:
    return analytic_sector(24.2, 23.0, 745.0, 0.0, 15.0, 0.0)


def make_pivot_carrier_local() -> cq.Shape:
    pieces: list[cq.Shape] = []
    for yy in (-8.0, 8.0):
        ear = ring_y(0.0, 0.0, 2.0, 6.5, 4.15, yy)
        # The carrier grows aft from the route-ring aft face.  R1/R2-preaudit
        # geometry extended these webs 3 mm into the structural ring.  The
        # shortened web starts at local z=-11 (global z=889), producing a
        # true butt/weld-land condition at the ring face instead of two solids
        # occupying the same volume.
        bridge = box_center(12.0, 2.0, 19.0, 0.0, yy, -1.5)
        pieces.append(ear.fuse(bridge))
    out = pieces[0].fuse(pieces[1])
    bore = cq.Solid.makeCylinder(4.15, 18.0, cq.Vector(0.0, -9.0, 0.0), cq.Vector(0, 1, 0))
    # The bell-end link pin rotates with the arm, so a single endpoint tunnel
    # is not a valid service corridor.  The exact audit localizes the positive
    # common volume to 3..22 degrees, so cut 0..23 degrees at the controlling
    # one-degree increment with 0.05 mm radial clearance.  Later positions are
    # already outside carrier stock; both matched lug solids must remain valid.
    carrier = out.cut(bore)
    for angle in range(24):
        theta = math.radians(float(angle))
        center_x = BELL_U * math.cos(theta) + BELL_V * math.sin(theta)
        center_z = -BELL_U * math.sin(theta) + BELL_V * math.cos(theta)
        bell_pin_access = cq.Solid.makeCylinder(
            3.30, 20.0,
            cq.Vector(center_x, -10.0, center_z), cq.Vector(0, 1, 0),
        )
        carrier = carrier.cut(bell_pin_access)
    carrier = carrier.clean()
    carrier_solids = carrier.Solids()
    if (
        len(carrier_solids) != 2
        or not carrier.isValid()
        or any(not solid.isValid() or solid.Volume() <= 0.0 for solid in carrier_solids)
    ):
        raise ValueError(
            "Pivot carrier swept bell-pin access must retain two valid positive lug solids; "
            f"solids={len(carrier_solids)}, valid={carrier.isValid()}, "
            f"volumes={[solid.Volume() for solid in carrier_solids]}"
        )
    return carrier


def make_link_part_local() -> cq.Shape:
    length = LINK_CENTER_DISTANCE
    # A shallow outboard dogleg clears the arm pivot boss throughout travel
    # while retaining the exact endpoint center distance.  The former straight
    # plate grazed the pivot ring near maximum deployment.
    offset = 1.5
    points = (
        (0.0, 0.0, 0.0),
        (0.25 * length, 0.0, offset),
        (0.75 * length, 0.0, offset),
        (length, 0.0, 0.0),
    )
    plate = strap_between(points[0], points[1], 1.5, 2.7)
    for start, end in zip(points[1:-1], points[2:]):
        plate = plate.fuse(strap_between(start, end, 1.5, 2.7))
    out = plate.fuse(ring_y(0.0, 0.0, 1.5, 3.2, 2.12)).fuse(ring_y(length, 0.0, 1.5, 3.2, 2.12))
    for x in (0.0, length):
        bore = cq.Solid.makeCylinder(2.12, 2.3, cq.Vector(x, -1.15, 0.0), cq.Vector(0, 1, 0))
        out = out.cut(bore)
    return out


def make_crosshead_part_local() -> cq.Shape:
    out = tube_z(7.0, 3.55, 2.5, z0=-1.25)
    for phi in (0.0, 120.0, 240.0):
        bridge = box_center(5.0, 9.6, 2.6, 7.5, 0.0, 0.0)
        out = out.fuse(bridge.rotate((0, 0, 0), (0, 0, 1), phi))
        for yy in (-3.85, 3.85):
            cheek = box_center(11.5, 1.9, 2.6, 12.25, yy, 0.0)
            ring = ring_y(CROSSHEAD_R, 0.0, 1.9, 4.2, 2.18, yy)
            out = out.fuse(cheek.rotate((0, 0, 0), (0, 0, 1), phi))
            out = out.fuse(ring.rotate((0, 0, 0), (0, 0, 1), phi))
    for phi in (60.0, 180.0, 300.0):
        spoke = box_center(8.0, 3.4, 4.5, 10.5, 0.0, 0.0).rotate((0, 0, 0), (0, 0, 1), phi)
        out = out.fuse(spoke)
    # Occurrence-specific GS and HBD rod clevises are integral to the common
    # crosshead at the two powered stations.  The 300° spoke supports the
    # separate spring seat face-to-face.
    for phi, radius in ((60.0, 13.5), (180.0, 14.5)):
        for yy in (-3.0, 3.0):
            cheek = box_center(7.0, 1.5, 2.8, radius - 3.0, yy, 0.0)
            ear = ring_y(radius, 0.0, 1.5, 4.5, 2.18, yy)
            out = out.fuse(cheek.rotate((0, 0, 0), (0, 0, 1), phi))
            out = out.fuse(ear.rotate((0, 0, 0), (0, 0, 1), phi))
    for phi in (0.0, 120.0, 240.0):
        bore = cq.Solid.makeCylinder(2.18, 13.0, cq.Vector(CROSSHEAD_R, -6.5, 0.0), cq.Vector(0, 1, 0))
        out = out.cut(bore.rotate((0, 0, 0), (0, 0, 1), phi))
    for phi, radius in ((60.0, 13.5), (180.0, 14.5)):
        pocket = cq.Solid.makeCylinder(5.2, 4.4, cq.Vector(radius, -2.2, 0.0), cq.Vector(0, 1, 0))
        out = out.cut(pocket.rotate((0, 0, 0), (0, 0, 1), phi))
        bore = cq.Solid.makeCylinder(2.18, 10.0, cq.Vector(radius, -5.0, 0.0), cq.Vector(0, 1, 0))
        out = out.cut(bore.rotate((0, 0, 0), (0, 0, 1), phi))
    x, y = 12.0 * math.cos(math.radians(300.0)), 12.0 * math.sin(math.radians(300.0))
    out = out.cut(cyl_z(2.65, 8.0, x, y, -4.0))
    return out


def make_crosshead_guide_spider_local() -> cq.Shape:
    """One-piece forward mounting spider for the central crosshead guide.

    The three spokes terminate on the routed-ring structural lands at the
    60/180/300-degree clocks.  The central hub supports the guide's integral
    forward shoulder with a controlled 0.05 mm diametral running clearance.
    """
    spider = cyl_z(4.50, 2.0, z0=-2.0).cut(cyl_z(2.15, 2.4, z0=-2.2))
    # Extend each spoke conformally to the r=19.5 structural-ring bore.  The
    # cylindrical clip produces a true zero-gap weld preparation without
    # allowing either occurrence to occupy positive common volume.
    ring_bore_clip = cyl_z(19.5, 2.0, z0=-2.0)
    for phi in (60.0, 180.0, 300.0):
        spoke = box_center(15.4, 2.0, 2.0, 11.95, 0.0, -1.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        ).intersect(ring_bore_clip)
        spider = spider.fuse(spoke)
    solids = spider.Solids()
    if len(solids) != 1 or not spider.isValid():
        raise ValueError(
            f"Crosshead-guide spider must be one valid solid; "
            f"found {len(solids)} solids (valid={spider.isValid()})"
        )
    return solids[0]


def make_stow_dog_guide_local() -> cq.Shape:
    """Fixed U-guide supporting one radial stow dog over its full stroke.

    Local +X is body-radial.  The two side rails provide 0.05 mm lateral
    clearance to the 4.4 mm-wide dog at both r=17.0 retained and r=13.5
    retracted positions.  The raised outboard pad reaches the aft route-ring
    forward face without entering the moving dog envelope.
    """
    dog_center_z = PIVOT_Z + ARM_LENGTH - 3.5
    ring_forward_rel_z = 1634.0 - dog_center_z
    guide = box_center(8.0, 0.50, 6.0, 15.0, 2.50, 0.0)
    guide = guide.fuse(box_center(8.0, 0.50, 6.0, 15.0, -2.50, 0.0))
    # Inboard spring-seat bridge connects both guide rails while leaving the
    # full dog envelope clear.  Its outer face at x=11.40 seats the first coil
    # with 0.05 mm nominal axial clearance.
    guide = guide.fuse(box_center(0.84, 5.50, 0.90, 10.70, 0.0, 0.0))
    guide = guide.fuse(box_center(0.50, 5.50, 0.40, 18.75, 0.0, 3.0))
    guide = guide.fuse(
        box_center(
            1.50, 5.50, ring_forward_rel_z - 3.2,
            19.25, 0.0, (3.2 + ring_forward_rel_z) / 2.0,
        )
    )
    transport_bore = cq.Solid.makeCylinder(
        0.65, 6.4, cq.Vector(17.0, -3.2, 0.0), cq.Vector(0, 1, 0)
    )
    keeper_counterbore = cq.Solid.makeCylinder(
        0.85, 1.4, cq.Vector(17.0, 1.8, 0.0), cq.Vector(0, 1, 0)
    )
    guide = guide.cut(transport_bore.fuse(keeper_counterbore))
    guide = guide.fuse(make_captive_inhibit_closed_guide_local())
    solids = guide.Solids()
    if len(solids) != 1 or not guide.isValid():
        raise ValueError(
            f"Stow-dog guide must be one valid solid; "
            f"found {len(solids)} solids (valid={guide.isValid()})"
        )
    return solids[0]


def make_route_guide_liner_local(route_outer_radius: float) -> cq.Shape:
    """Split-guide envelope for one long fixed-sector service corridor.

    The liner body occupies the existing r=1.35 mm bored corridor with
    0.02 mm radial assembly clearance.  Short end shoulders sit between the
    two bulkhead glands and the counterbore steps, providing positive axial
    retention without overlapping either gland.
    """
    inner_radius = route_outer_radius + 0.10
    if inner_radius >= 1.33:
        raise ValueError("Route liner requires positive wall thickness")
    x = 26.2 * math.cos(math.radians(25.0))
    y = 26.2 * math.sin(math.radians(25.0))
    liner = tube_z(1.33, inner_radius, 742.6, x, y, 1.2)
    liner = liner.fuse(tube_z(2.45, inner_radius, 0.20, x, y, 1.2))
    liner = liner.fuse(tube_z(2.45, inner_radius, 0.20, x, y, 743.6))
    solids = liner.Solids()
    if len(solids) != 1 or not liner.isValid():
        raise ValueError(
            f"Route guide liner must be one valid solid; "
            f"found {len(solids)} solids (valid={liner.isValid()})"
        )
    return solids[0]


def make_follower_plate_local() -> cq.Shape:
    plate = cyl_z(22.2, 5.0, z0=-2.5).cut(cyl_z(11.7, 5.4, z0=-2.7))
    for phi in (0.0, 120.0, 240.0):
        # Author once on the +X radial datum, then clock the complete slot.
        # The prior code pre-clocked its center and rotated it a second time,
        # leaving the 120/240-degree guide rails partly inside follower stock.
        slot = box_center(4.2, 5.2, 7.0, 19.6, 0.0, 0).rotate((0, 0, 0), (0, 0, 1), phi)
        plate = plate.cut(slot)
    for phi in (60.0, 180.0, 300.0):
        plate = plate.cut(analytic_sector(24.0, 20.7, 7.0, phi, 4.2, -3.5))
        x = 15.0 * math.cos(math.radians(phi))
        y = 15.0 * math.sin(math.radians(phi))
        plate = plate.cut(cyl_z(1.65, 5.4, x, y, -2.7))
    latch_relief = box_center(12.5, 17.0, 7.0, 17.0, 0.0, 0.0).rotate((0, 0, 0), (0, 0, 1), 270.0)
    plate = plate.cut(latch_relief)
    # Radial 4 mm sear capture bore at the 270-degree latch station.  The short
    # plunger tip occupies this manufactured feature in STOWED and withdraws
    # radially for deployment; it no longer occupies solid follower stock.
    sear_bore = cq.Solid.makeCylinder(2.18, 12.5,
                                      cq.Vector(0.0, -23.5, 0.0),
                                      cq.Vector(0, 1, 0))
    plate = plate.cut(sear_bore)
    return plate


def make_reaction_bulkhead_local() -> cq.Shape:
    disk = cyl_z(25.3, 6.0, z0=-3.0)
    disk = disk.cut(cyl_z(11.7, 6.4, z0=-3.2))
    for phi in (0.0, 120.0, 240.0):
        x, y = 20.0 * math.cos(math.radians(phi)), 20.0 * math.sin(math.radians(phi))
        hole = cyl_z(1.25, 6.4, x, y, -3.2)
        disk = disk.cut(hole)
        sx, sy = 12.7 * math.cos(math.radians(phi)), 12.7 * math.sin(math.radians(phi))
        disk = disk.cut(cyl_z(1.65, 6.4, sx, sy, -3.2))
    for phi in (60.0, 180.0, 300.0):
        disk = disk.cut(analytic_sector(25.4, 22.75, 6.4, phi, 4.1, -3.2))
    # The services are oblique through this 6 mm plate as they transition
    # from the r=26.2 structural-ring passages to the protected r=24 annular
    # corridor.  Cut the actual centerlines with route-specific radial
    # clearance; vertical holes at r=24 left each route in plate material.
    for phi_deg, cutter_radius in ((85.0, 1.20), (325.0, 0.95), (205.0, 1.00)):
        a = math.radians(phi_deg)
        points = [
            (26.2 * math.cos(a), 26.2 * math.sin(a), -12.5),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 5.0),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 12.0),
        ]
        disk = disk.cut(routed_round(points, cutter_radius))
    # A one-piece three-spoke pilot supports the fixed telescoping sleeve at
    # the aft bulkhead face.  It remains forward of the ejector spring and
    # leaves a controlled r=8.55 mm sleeve-pilot bore.
    hub = tube_z(10.50, 8.55, 2.0, z0=1.0)
    disk = disk.fuse(hub)
    for phi in (0.0, 120.0, 240.0):
        spoke = box_center(2.0, 2.0, 2.0, 10.8, 0.0, 2.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        disk = disk.fuse(spoke)
    # Recut the three fixed-sleeve screw clearances after fusing the pilot
    # spokes.  The earlier operation bored only the disk, then put spoke
    # material back into the screw envelope.
    for phi in (0.0, 120.0, 240.0):
        sx = 12.7 * math.cos(math.radians(phi))
        sy = 12.7 * math.sin(math.radians(phi))
        disk = disk.cut(cyl_z(1.65, 6.6, sx, sy, -3.3))
    return disk


def make_structural_ring_with_hardpoint_local() -> cq.Shape:
    ring = tube_z(25.3, 20.0, 8.0, z0=-4.0)
    # Full yoke service aperture clears the headed pin, retainer and buried
    # rope eye.  Structural continuity is carried by the two integral yoke
    # webs and three occurrence-specific longeron welds.
    ring = ring.cut(box_center(18.0, 16.0, 17.0, 24.0, 0.0, 0.0))
    # True double-shear recovery yoke.  The 4 mm-wide thimble lies between the
    # two ears; a retained 6 mm pin passes through the coaxial bores.
    out = ring
    for yy in (-3.25, 3.25):
        ear = ring_y(24.0, 0.0, 2.0, 6.0, 3.2, yy)
        web = box_center(10.0, 2.0, 12.0, 23.0, yy, 0.0)
        out = out.fuse(ear).fuse(web)
    bore = cq.Solid.makeCylinder(3.2, 12.0, cq.Vector(24.0, -6.0, 0.0), cq.Vector(0, 1, 0))
    return out.cut(bore)


def make_service_door_local() -> cq.Shape:
    disk = cyl_z(23.5, 3.0, z0=-1.5)
    # Hinge knuckle and tether eye are part of the same machined door.
    knuckle = cq.Solid.makeCylinder(2.4, 8.2, cq.Vector(28.0, -4.1, 0.0), cq.Vector(0, 1, 0))
    knuckle = knuckle.cut(cq.Solid.makeCylinder(1.6, 8.4, cq.Vector(28.0, -4.2, 0.0), cq.Vector(0, 1, 0)))
    eye = ring_y(-15.0, -5.5, 3.0, 3.2, 2.0)
    eye_web = box_center(4.0, 3.0, 1.4, -15.0, 0.0, -1.9)
    knuckle_web = box_center(5.0, 8.0, 2.8, 25.5, 0.0, 0.0)
    out = disk.fuse(knuckle_web).fuse(knuckle).fuse(eye_web).fuse(eye)
    # Recut the hinge bore after the web union; otherwise the connecting web
    # refills the central portion of the pre-bored knuckle and occupies the
    # retained hinge pin.
    hinge_bore = cq.Solid.makeCylinder(1.6, 8.4, cq.Vector(28.0, -4.2, 0.0), cq.Vector(0, 1, 0))
    out = out.cut(hinge_bore)
    # Preserve the eye bore after union with the door disk; otherwise the
    # disk filled the nominal ring opening and no physical lanyard path
    # existed through the machined feature.
    eye_bore = cq.Solid.makeCylinder(2.0, 8.0, cq.Vector(-15.0, -4.0, -5.5), cq.Vector(0, 1, 0))
    out = out.cut(eye_bore)
    # Four hemispherical detent seats clear the catalog plunger balls in the
    # closed state; preload is carried at the spherical contact, not by two
    # solids occupying one another.
    for phi in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(phi)
        center = cq.Vector(22.9 * math.cos(a), 22.9 * math.sin(a), -1.5)
        out = out.cut(cq.Solid.makeSphere(1.62, center))
    return out


def door_occurrence_loc(deployed: bool, pivot_z: float = 2028.0) -> cq.Location:
    if not deployed:
        return translation_loc(0.0, 0.0, pivot_z)
    return (
        translation_loc(28.0, 0.0, pivot_z)
        * rotation_loc((0, 1, 0), -90.0)
        * translation_loc(-28.0, 0.0, 0.0)
    )


def make_buoy_gore_deployed_local(gore_index: int, radius: float = 242.859) -> cq.Shape:
    # CadQuery's primitive defaults to the +Z hemisphere.  Explicit angular
    # bounds are mandatory here to represent the full 60 L buoy.
    outer = cq.Solid.makeSphere(radius + 0.45, angleDegrees1=-90.0, angleDegrees2=90.0)
    inner = cq.Solid.makeSphere(radius, angleDegrees1=-90.0, angleDegrees2=90.0)
    shell = outer.cut(inner)
    gore = shell.intersect(triangular_wedge(radius * 2.5, radius * 2.5,
                                             gore_index * 45.0, 22.7, -radius * 1.25))
    # Two occurrence-specific RF capture tails close the measured harness
    # stand-offs without thickening or radially shifting the complete buoy.
    if gore_index == 0:
        gore = gore.fuse(box_center(0.50, 4.0, 4.0, 243.15, 0.0, 0.0))
    elif gore_index == 4:
        # Band 2 is the pole-overpass loop.  A direct radial tab from Gore 05
        # would cross Band 1 before reaching it.  Route a narrow integral
        # RF-welded capture tail around the outside of Band 1 instead.  The
        # 245.40 mm centerline radius plus 0.40 mm tail radius stays outside
        # both harness envelopes until its tangent termination on Band 2.
        def capture_point(radius: float, angle_deg: float) -> tuple[float, float, float]:
            angle = math.radians(angle_deg)
            return radius * math.cos(angle), radius * math.sin(angle), 0.0

        capture_points = [
            capture_point(243.10, 190.0),
            capture_point(245.40, 190.0),
            *(capture_point(245.40, float(angle)) for angle in range(191, 270)),
            capture_point(244.95, 270.0),
        ]
        gore = gore.fuse(routed_round(capture_points, 0.40))
    solids = gore.Solids()
    if len(solids) != 1 or not gore.isValid():
        raise ValueError(
            f"Deployed gore {gore_index + 1} must be one valid captured solid; "
            f"found {len(solids)} solids (valid={gore.isValid()})"
        )
    return solids[0]


def make_buoy_gore_stowed_local(gore_index: int) -> cq.Shape:
    """Eight edge-matched 45-degree sectors for the packed buoy envelope.

    Each sector preserves the controlled 1252.8 mm3 fabric volume.  Exact
    cyclic sector boundaries meet at zero gap and zero common volume, giving
    the RF-welded packed article a continuous occurrence-specific seam rather
    than eight separated packets with unsupported 6.16 mm gaps.
    """
    if not 0 <= gore_index < 8:
        raise ValueError(f"gore_index must be in [0, 7], got {gore_index}")
    inner_radius = 12.0
    outer_radius = 17.0
    packed_length = 22.001579333
    # Keep the packed membrane forward face exactly at the aft rail plane;
    # the former z0=1.499210333 placed four gore sectors 0.408..0.816 mm3
    # inside the guide-rail end envelopes.
    z0 = 3.0
    packet = analytic_sector(
        outer_radius,
        inner_radius,
        packed_length,
        22.5 + gore_index * 45.0,
        22.5,
        z0,
    )
    # Gore 01 and Gore 05 carry narrow integral RF-weld capture tails to the
    # two packed harness-band lanes.  Each tail ends on the band face with
    # zero common volume and stays inside its own 45-degree gore sector.
    if gore_index == 0:
        # Band 1 sits behind Band 2 in the packed stack.  Route Gore 01's
        # integral RF-welded tail just outside the Band-2 coil, then turn it
        # in tangentially onto the Band-1 forward face.  A direct axial tail
        # occupied 40.64 mm3 of Band 2.
        phi = math.radians(22.5)

        def capture_point(radius: float, z: float) -> tuple[float, float, float]:
            return radius * math.cos(phi), radius * math.sin(phi), z

        packet = packet.fuse(routed_round([
            capture_point(15.80, 3.50),
            capture_point(16.30, 2.30),
            capture_point(16.30, -55.90),
            capture_point(15.40, -55.90),
        ], 0.40))
    elif gore_index == 4:
        band_top_z = -27.3
        capture_length = z0 - band_top_z
        capture = box_center(
            0.80, 2.0, capture_length,
            15.40, 0.0, band_top_z + capture_length / 2.0,
        ).rotate((0, 0, 0), (0, 0, 1), 202.5)
        packet = packet.fuse(capture)
    solids = packet.Solids()
    if len(solids) != 1 or not packet.isValid():
        raise ValueError(
            f"Packed gore {gore_index + 1} must be one valid solid; "
            f"found {len(solids)} solids (valid={packet.isValid()})"
        )
    return solids[0]


def make_harness_band_local(radius: float = 244.0, width: float = 25.4, thickness: float = 1.1) -> cq.Shape:
    profile = cq.Workplane("XZ").moveTo(radius, 0.0).rect(thickness, width)
    return profile.revolve(360.0, (0, -1), (0, 1)).val()


def make_harness_band_overpass_local(radius: float = 244.0, width: float = 25.4,
                                     thickness: float = 1.1,
                                     lift: float = 1.2) -> cq.Shape:
    """Closed great-circle band with engineered pole crossovers.

    Two orthogonal harness bands must cross at the buoy poles.  Modeling both
    at the same radius made them occupy one another.  This second band is cut
    locally and routed over the first with 0.10 mm nominal layer clearance;
    the short bridges are part of the same sewn closed-loop occurrence.
    """
    band = make_harness_band_local(radius, width, thickness)
    gap_length = 34.0
    # The base revolved band lies in the local XY plane.  After the occurrence
    # rotates it into the YZ great circle, its two buoy-pole crossings map from
    # local +/-X.  Raise those short spans outward along local X.
    for sign in (-1.0, 1.0):
        pole_x = sign * radius
        band = band.cut(box_center(4.0, gap_length, width + 2.0,
                                   pole_x, 0.0, 0.0))
        bridge_x = sign * (radius + lift)
        bridge = box_center(thickness, gap_length - 2.0, width,
                            bridge_x, 0.0, 0.0)
        # Short sloped end transitions keep the overpass a single continuous
        # flexible article while remaining clear of the underlying band.
        # strap_between aligns its long axis with the supplied vector and its
        # width normal to the local bridge plane.  Model these very short
        # ramps explicitly as boxes so the web axial width remains local Z.
        ramp_length = 3.0
        left = box_center(abs(bridge_x - pole_x) + thickness,
                          ramp_length, width,
                          (bridge_x + pole_x) / 2.0,
                          -gap_length / 2.0 + 0.5,
                          0.0)
        right = box_center(abs(bridge_x - pole_x) + thickness,
                           ramp_length, width,
                           (bridge_x + pole_x) / 2.0,
                           gap_length / 2.0 - 0.5,
                           0.0)
        band = band.fuse(bridge).fuse(left).fuse(right)
    return band


def make_harness_band_stowed_local(band_index: int, thickness: float = 1.1,
                                   width: float = 25.4) -> cq.Shape:
    """One-piece packed closed-loop band in a dedicated annular lane.

    Six disconnected boxes previously stood in for each folded band.  Besides
    failing attachment cohesion, those boxes crossed the gore packets and the
    orthogonal band.  A compressed annular coil is an exact, connected closed
    loop; the two bands occupy separate axial lanes between the spring guide
    and the packed buoy.  The prior modeled stowed volume is preserved.
    """
    if band_index not in (1, 2):
        raise ValueError(f"band_index must be 1 or 2, got {band_index}")
    target_volume = 6.0 * thickness * width * 26.0
    inner_radius = 14.0
    outer_radius = math.sqrt(
        inner_radius**2 + target_volume / (math.pi * width)
    )
    center_z = -69.0 if band_index == 1 else -40.0
    band = tube_z(
        outer_radius,
        inner_radius,
        width,
        z0=center_z - width / 2.0,
    )
    solids = band.Solids()
    if len(solids) != 1 or not band.isValid():
        raise ValueError(
            f"Packed harness band {band_index} must be one valid solid; "
            f"found {len(solids)} solids (valid={band.isValid()})"
        )
    return solids[0]


def make_thimble_local(rope_d: float = 2.5) -> cq.Shape:
    ring = ring_y(0.0, 0.0, 4.0, 8.0, 3.15)
    groove = cq.Solid.makeTorus(7.0, rope_d / 2.0 + 0.30, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    return ring.cut(groove).cut(box_center(5.0, 4.4, 4.8, 7.0, 0.0, 0.0))


def make_harness_terminal_local() -> cq.Shape:
    """Four radial through-slots above a separate double-shear tether clevis."""
    top = cyl_z(15.0, 3.0, z0=9.0)
    # Each 8 mm finished web leg receives its own cardinal, full-thickness
    # slot.  The prior four collinear partial-depth slots forced the Y legs
    # through terminal metal and across the X-leg web layers.
    for phi in (0.0, 90.0, 180.0, 270.0):
        slot = box_center(4.0, 10.0, 3.8, 9.0, 0.0, 10.5).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        top = top.cut(slot)
    out = top
    for yy in (-3.25, 3.25):
        ear = ring_y(0.0, 0.0, 2.0, 6.0, 3.2, yy)
        web = box_center(4.0, 2.0, 10.0, 0.0, yy, 5.0)
        out = out.fuse(ear).fuse(web)
    bore = cq.Solid.makeCylinder(3.2, 12.0, cq.Vector(0.0, -6.0, 0.0), cq.Vector(0, 1, 0))
    return out.cut(bore)


def make_structural_tether_local(end_x: float, end_z: float, deployed: bool,
                                 rope_radius: float = 1.25) -> cq.Shape:
    """One fused structural rope solid with two closed eye-splice ends."""
    loop_radius = 7.0
    body_loop = cq.Solid.makeTorus(loop_radius, rope_radius, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    end_loop = cq.Solid.makeTorus(loop_radius, rope_radius, cq.Vector(end_x, 0, end_z), cq.Vector(0, 1, 0))
    if deployed:
        points = [
            (0.0, 0.0, loop_radius),
            (-8.0, 0.0, end_z * 0.30),
            (-20.0, 0.0, end_z * 0.62),
            (end_x, 0.0, end_z - loop_radius),
        ]
    else:
        # Fold the packed span through the hardpoint aperture and then through
        # a diagonal inboard corridor.  It stays out of the shell wall, the
        # four cardinal harness legs, and the terminal clevis stock.
        points = [
            (0.0, 0.0, loop_radius),
            (-5.0, -3.0, 8.3),
            (-10.0, -6.0, 8.4),
            (-17.0, -7.0, 8.4),
            (-22.0, -4.0, 8.6),
            (end_x, 0.0, end_z - loop_radius),
        ]
    span = routed_round(points, rope_radius)
    # As with routed_round(), do not remove analytic splitters at tangent eye
    # joins: OCCT 7.9 can invalidate the otherwise valid single fused rope.
    tether = body_loop.fuse(span).fuse(end_loop)
    solids = tether.Solids()
    if len(solids) != 1 or not tether.isValid():
        raise ValueError(
            f"Structural tether must be one valid fused solid; "
            f"found {len(solids)} solids (valid={tether.isValid()})"
        )
    return solids[0]


def make_shackle_local() -> cq.Shape:
    left = cq.Solid.makeTorus(7.0, 2.0, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 20.0, 320.0)
    pin = cq.Solid.makeCylinder(2.5, 8.0, cq.Vector(-5.5, -4.0, 0.0), cq.Vector(0, 1, 0))
    return compound([left, pin])


def make_external_test_hook_local() -> cq.Shape:
    hook = cq.Solid.makeTorus(18.0, 6.0, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    hook = hook.cut(box_center(30.0, 14.0, 28.0, 14.0, 0.0, 12.0))
    shank = cq.Solid.makeCylinder(6.0, 42.0, cq.Vector(-18.0, 0.0, 0.0), cq.Vector(0, 0, 1))
    return hook.fuse(shank)
