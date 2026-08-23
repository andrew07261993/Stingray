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


def routed_round(points: list[tuple[float, float, float]], ro: float, ri: float | None = None) -> cq.Shape:
    """Connected analytic tube/rod with spherical formed bends."""
    pieces: list[cq.Shape] = []
    for a, b in zip(points, points[1:]):
        pieces.append(tube_between(a, b, ro, ri) if ri is not None else rod_between(a, b, ro))
    for p in points[1:-1]:
        outer = cq.Solid.makeSphere(ro, cq.Vector(*p))
        pieces.append(outer.cut(cq.Solid.makeSphere(ri, cq.Vector(*p))) if ri is not None else outer)
    out = pieces[0]
    for piece in pieces[1:]:
        out = out.fuse(piece)
    return out


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
    spring = make_helix_z(od, wire, installed_length, total_turns)
    end1 = cq.Solid.makeTorus((od - wire) / 2.0, wire / 2.0, cq.Vector(0, 0, wire / 2.0), cq.Vector(0, 0, 1), 0, 360)
    end2 = cq.Solid.makeTorus((od - wire) / 2.0, wire / 2.0, cq.Vector(0, 0, installed_length - wire / 2.0), cq.Vector(0, 0, 1), 0, 360)
    return compound([spring, end1, end2])


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
    bell_bore = cq.Solid.makeCylinder(2.18, 12.0, cq.Vector(attach[0], -6.0, attach[1]), cq.Vector(0, 1, 0))
    arm = arm.cut(bell_bore)
    bell_head_relief = cq.Solid.makeCylinder(3.15, 1.4,
                                             cq.Vector(attach[0], -6.7, attach[1]),
                                             cq.Vector(0, 1, 0))
    arm = arm.cut(bell_head_relief)
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
    arm = arm.cut(box_center(5.2, 8.0, 4.2, 4.0, 0.0, -8.5))
    arm = arm.cut(box_center(4.4, 4.2, 3.4, 4.0, 0.0, -4.5))
    arm = arm.cut(box_center(3.2, 3.2, 5.5, -1.0, 0.0, ARM_LENGTH - 3.5))
    solids = arm.Solids()
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
    return solids[0]


def make_fixed_sector_local() -> cq.Shape:
    # Leave a manufactured angular access corridor around each adjacent pivot
    # lug set.  +/-38 degrees still contains both route bores at +/-25 degrees
    # with credible wall stock while eliminating the former lug/sector clash.
    out = analytic_sector(28.5, 24.2, 745.0, 0.0, 38.0, 0.0)
    for angle in (-25.0, 25.0):
        x = 26.2 * math.cos(math.radians(angle))
        y = 26.2 * math.sin(math.radians(angle))
        out = out.cut(cyl_z(1.2, 745.4, x, y, -0.2))
    return out


def make_longeron_local() -> cq.Shape:
    return analytic_sector(24.0, 23.0, 745.0, 0.0, 15.0, 0.0)


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
    return out.cut(bore)


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
    latch_relief = box_center(2.0, 6.4, 7.0, 21.7, 0.0, 0.0).rotate((0, 0, 0), (0, 0, 1), 60.0)
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
    disk = cyl_z(25.2, 6.0, z0=-3.0)
    disk = disk.cut(cyl_z(11.7, 6.4, z0=-3.2))
    for phi in (0.0, 120.0, 240.0):
        x, y = 19.6 * math.cos(math.radians(phi)), 19.6 * math.sin(math.radians(phi))
        hole = cyl_z(1.65, 6.4, x, y, -3.2)
        disk = disk.cut(hole)
    for phi in (60.0, 180.0, 300.0):
        disk = disk.cut(analytic_sector(24.0, 20.7, 6.4, phi, 4.2, -3.2))
    # Four formed services leave the arm longerons at r=26.2 mm, then
    # transition to r=24.0 mm before this bulkhead.  Cut occurrence-specific
    # passages instead of allowing the routes to occupy bulkhead material.
    for center, deltas in ((60.0, (-25.0, 25.0)), (180.0, (-25.0, 25.0))):
        for delta in deltas:
            phi = math.radians(center + delta)
            x, y = 24.0 * math.cos(phi), 24.0 * math.sin(phi)
            disk = disk.cut(cyl_z(1.25, 6.4, x, y, -3.2))
    return disk


def make_structural_ring_with_hardpoint_local() -> cq.Shape:
    ring = tube_z(25.3, 20.0, 8.0, z0=-4.0)
    ring = ring.cut(box_center(18.0, 4.4, 17.0, 24.0, 0.0, 0.0))
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
    knuckle = cq.Solid.makeCylinder(2.4, 8.0, cq.Vector(28.0, -4.0, 0.0), cq.Vector(0, 1, 0))
    knuckle = knuckle.cut(cq.Solid.makeCylinder(1.6, 8.4, cq.Vector(28.0, -4.2, 0.0), cq.Vector(0, 1, 0)))
    eye = ring_y(-15.0, -1.7, 3.0, 3.2, 2.0)
    eye_web = box_center(8.0, 3.0, 3.0, -10.5, 0.0, -0.8)
    return disk.fuse(knuckle).fuse(eye_web).fuse(eye)


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
    return shell.intersect(triangular_wedge(radius * 2.5, radius * 2.5,
                                             gore_index * 45.0, 22.7, -radius * 1.25))


def make_buoy_gore_stowed_local(gore_index: int) -> cq.Shape:
    # Controlled folded-sheet representation: eight nested corrugated strips,
    # each retaining its R2 occurrence identity and fabric volume.
    radial = 2.0 + gore_index * 1.6
    strip = box_center(0.45, 16.0, 174.0, radial, 0.0, 0.0)
    return strip.rotate((0, 0, 0), (0, 0, 1), gore_index * 45.0)


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
    """Controlled folded representation that fits inside the 47.6 mm throat.

    The developed web length is represented by six alternating folds.  The
    flexible article retains the same occurrence ID as its deployed closed
    loop, but no impossible 488 mm-diameter ring is hidden inside the body.
    """
    solids: list[cq.Shape] = []
    clock = 0.0 if band_index == 1 else 90.0
    for fold in range(6):
        radial = -3.0 + fold * 1.2
        z = -70.0 + fold * 28.0
        strip = box_center(thickness, width, 26.0, radial, 0.0, z)
        solids.append(strip.rotate((0, 0, 0), (0, 0, 1), clock + (180.0 if fold % 2 else 0.0)))
    return compound(solids)


def make_thimble_local(rope_d: float = 2.5) -> cq.Shape:
    ring = ring_y(0.0, 0.0, 4.0, 8.0, 3.15)
    groove = cq.Solid.makeTorus(7.0, rope_d / 2.0 + 0.15, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    return ring.cut(groove).cut(box_center(5.0, 4.4, 4.8, 7.0, 0.0, 0.0))


def make_harness_terminal_local() -> cq.Shape:
    """Four-slot web terminal with a separate double-shear tether clevis."""
    top = box_center(24.0, 8.0, 3.0, 0.0, 0.0, 10.5)
    # Four stitched-web slots, two for each closed great-circle band.
    for x in (-7.0, -2.3, 2.3, 7.0):
        top = top.cut(box_center(2.6, 8.6, 1.8, x, 0.0, 10.5))
    out = top
    for yy in (-3.25, 3.25):
        ear = ring_y(0.0, 0.0, 2.0, 6.0, 3.2, yy)
        web = box_center(4.0, 2.0, 10.0, 0.0, yy, 5.0)
        out = out.fuse(ear).fuse(web)
    bore = cq.Solid.makeCylinder(3.2, 12.0, cq.Vector(0.0, -6.0, 0.0), cq.Vector(0, 1, 0))
    return out.cut(bore)


def make_structural_tether_local(end_x: float, end_z: float, deployed: bool,
                                 rope_radius: float = 1.25) -> cq.Shape:
    """Two closed eye splices plus a connected flexible recovery span."""
    loop_radius = 7.0
    body_loop = cq.Solid.makeTorus(loop_radius, rope_radius, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    end_loop = cq.Solid.makeTorus(loop_radius, rope_radius, cq.Vector(end_x, 0, end_z), cq.Vector(0, 1, 0))
    if deployed:
        points = [(0.0, 0.0, loop_radius), (-8.0, 0.0, end_z * 0.30),
                  (-20.0, 0.0, end_z * 0.62), (end_x, 0.0, end_z - loop_radius)]
    else:
        points = [(0.0, 0.0, loop_radius), (8.0, 7.0, 9.0),
                  (2.0, -7.0, 13.0), (end_x + 5.0, 5.0, end_z - 4.0),
                  (end_x, 0.0, end_z - loop_radius)]
    span = routed_round(points, rope_radius)
    return compound([body_loop, span, end_loop])


def make_shackle_local() -> cq.Shape:
    left = cq.Solid.makeTorus(7.0, 2.0, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 20.0, 320.0)
    pin = cq.Solid.makeCylinder(2.5, 8.0, cq.Vector(-5.5, -4.0, 0.0), cq.Vector(0, 1, 0))
    return compound([left, pin])


def make_external_test_hook_local() -> cq.Shape:
    hook = cq.Solid.makeTorus(18.0, 6.0, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    hook = hook.cut(box_center(30.0, 14.0, 28.0, 14.0, 0.0, 12.0))
    shank = cq.Solid.makeCylinder(6.0, 42.0, cq.Vector(-18.0, 0.0, 0.0), cq.Vector(0, 0, 1))
    return hook.fuse(shank)
