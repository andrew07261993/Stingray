#!/usr/bin/env python3
"""Build the mechanically cohesive STINGRAY DF8 R2 candidate assemblies.

This authoring process emits editable part-local definitions, occurrence
placements, occurrence-specific connectivity, and the two AP242 endpoint
states.  Validation is intentionally performed by a separate clean process.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import cadquery as cq
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Controller

import r2_geometry as g


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
RELEASE_DIR = ROOT / "work" / "r2_release"
ANALYSIS_DIR = ROOT / "work" / "r2_analysis"
INPUT_DIR = ROOT / "work" / "input"

STOWED_FILE = "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_STOWED_AP242.step"
DEPLOYED_FILE = "STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_DEPLOYED_AP242.step"
EXTERNAL_CONTEXT_FILE = "STINGRAY_I5S_DF8_R2_EXTERNAL_TEST_CONTEXT_PROVISIONAL_AP242.step"


def slug(value: str, limit: int = 72) -> str:
    return re.sub(r"[^A-Za-z0-9_+.-]+", "_", value.upper()).strip("_")[:limit]


def export_ap242(assembly: cq.Assembly, path: Path) -> None:
    STEPCAFControl_Controller.Init_s()
    Interface_Static.SetIVal_s("write.step.schema", 5)
    assembly.export(str(path), exportType="STEP", mode="default", unit="MM", outputUnit="MM", name_geometries=True)


def name_assembly_usage_occurrences(path: Path) -> None:
    """Mirror child product identity into any empty AP242 NAUO name field."""
    text = path.read_text(encoding="latin-1")
    entities = {int(m.group(1)): m.group(2) for m in re.finditer(r"#(\d+)\s*=\s*(.*?);", text, re.S)}

    def child_product(pd_id: int) -> str:
        pd_refs = [int(v) for v in re.findall(r"#(\d+)", entities.get(pd_id, ""))]
        if not pd_refs:
            return f"ASSEMBLY_PD_{pd_id}"
        formation_refs = [int(v) for v in re.findall(r"#(\d+)", entities.get(pd_refs[0], ""))]
        if not formation_refs:
            return f"ASSEMBLY_PD_{pd_id}"
        m = re.search(r"PRODUCT\(\s*'((?:''|[^'])*)'", entities.get(formation_refs[0], ""), re.S)
        return m.group(1).replace("\n", "").strip() if m else f"ASSEMBLY_PD_{pd_id}"

    pattern = re.compile(
        r"#(\d+)\s*=\s*NEXT_ASSEMBLY_USAGE_OCCURRENCE\(\s*"
        r"'((?:''|[^'])*)'\s*,\s*'((?:''|[^'])*)'\s*,\s*"
        r"'((?:''|[^'])*)'\s*,\s*#(\d+)\s*,\s*#(\d+)\s*,\s*\$\s*\);",
        re.S,
    )

    def repl(m: re.Match[str]) -> str:
        eid, oid, oname, _desc, parent_pd, child_pd = m.groups()
        if oname:
            return m.group(0)
        cname = child_product(int(child_pd)).replace("'", "''")
        return f"#{eid} = NEXT_ASSEMBLY_USAGE_OCCURRENCE('{oid}','{cname}__OCC_{oid}','NAMED ASSEMBLY OCCURRENCE',#{parent_pd},#{child_pd},$);"

    updated, count = pattern.subn(repl, text)
    if count == 0:
        raise RuntimeError(f"No NAUO entities found in {path}")
    path.write_text(updated, encoding="latin-1")


class R2Builder:
    def __init__(self, state: str):
        self.state = state
        self.deployed = state == "DEPLOYED"
        self.catalog = g.PartCatalog()
        self.root = cq.Assembly(name=f"STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_{state}_ASSY")
        self.forward = cq.Assembly(name="100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY")
        self.arm_module = cq.Assembly(name="300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY")
        self.aft = cq.Assembly(name="500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY")
        self.occurrences: list[g.Occurrence] = []
        self.connections: list[g.Connection] = []
        self.global_shapes: dict[str, cq.Shape] = {}
        self.flexible_ids: set[str] = set()
        self.external_ids: set[str] = set()
        self.routes: list[dict[str, Any]] = []
        self.state_notes: list[dict[str, Any]] = []

    def define(self, part_number: str, revision: str, description: str, shape: cq.Shape,
               material: str, make_buy: str = "MAKE", manufacturer: str = "STINGRAY custom",
               cad_classification: str = "DRAWING_DERIVED", mass_kg: float | None = None,
               source_url: str = "", purchase_url: str = "", process: str = "",
               finish: str = "", notes: str = "", color_key: str = "steel",
               external_context: bool = False) -> g.PartDef:
        return self.catalog.add(g.PartDef(
            part_number=part_number, revision=revision, description=description, shape=shape,
            material=material, make_buy=make_buy, manufacturer=manufacturer,
            cad_classification=cad_classification, mass_kg=mass_kg,
            source_url=source_url, purchase_url=purchase_url, process=process,
            finish=finish, notes=notes, color_key=color_key, external_context=external_context,
        ))

    def add(self, assembly: cq.Assembly, parent_path: str, part: g.PartDef, occurrence_id: str,
            loc: cq.Location, classification: str, joint_type: str, permitted_dof: str = "0",
            state_membership: str = "BOTH", notes: str = "") -> str:
        node_name = f"{occurrence_id}__{part.part_number}__REV_{part.revision}__{slug(part.description)}"
        assembly.add(part.shape, name=node_name, loc=loc, color=g.COLORS.get(part.color_key, g.COLORS["steel"]))
        occ = g.Occurrence(
            occurrence_id=occurrence_id, part_number=part.part_number, parent_path=parent_path,
            state=self.state, location=loc, classification=classification,
            joint_type=joint_type, permitted_dof=permitted_dof,
            state_membership=state_membership, notes=notes,
        )
        self.occurrences.append(occ)
        self.global_shapes[occurrence_id] = g.moved(part.shape, loc)
        if classification in {"FLEXIBLE", "SOFTGOOD"}:
            self.flexible_ids.add(occurrence_id)
        if part.external_context:
            self.external_ids.add(occurrence_id)
        return occurrence_id

    def connect(self, cid: str, occ: str, mate: str, own_feature: str, mate_feature: str,
                connection_type: str, permitted_dof: str, retaining_hardware: str,
                axial: str, lateral: str, anti_rotation: str,
                upstream: str, downstream: str, service: str, evidence: str) -> None:
        self.connections.append(g.Connection(
            connection_id=cid, state=self.state, occurrence_id=occ, mate_occurrence_id=mate,
            own_feature_id=own_feature, mate_feature_id=mate_feature,
            connection_type=connection_type, permitted_dof=permitted_dof,
            retaining_hardware=retaining_hardware, axial_retention=axial,
            lateral_retention=lateral, anti_rotation=anti_rotation,
            upstream_load_path=upstream, downstream_load_path=downstream,
            service_method=service, evidence=evidence,
        ))

    def add_route_record(self, route_id: str, origin: str, destination: str, fittings: str,
                         penetrations: str, supports: str, bend_radius_mm: float,
                         service_slack_mm: float, pressure_rating: str, status: str) -> None:
        self.routes.append({
            "state": self.state, "route_occurrence_id": route_id,
            "origin_occurrence": origin, "destination_occurrence": destination,
            "termination_fittings": fittings, "controlled_penetrations": penetrations,
            "supports": supports, "minimum_bend_radius_mm": bend_radius_mm,
            "service_slack_mm": service_slack_mm, "pressure_rating": pressure_rating,
            "status": status,
        })


def radial_xy(radius: float, phi: float) -> tuple[float, float]:
    a = math.radians(phi)
    return radius * math.cos(a), radius * math.sin(a)


def ring_with_axial_route_holes(length: float, ro: float = 28.5, ri: float = 19.5,
                                arm_root_reliefs: bool = False) -> cq.Shape:
    ring = g.tube_z(ro, ri, length, z0=-length / 2.0)
    if arm_root_reliefs:
        # Three shallow, manufactured aft-face deployment scallops clear the
        # exact root swept envelope from 0..80 degrees.  They stop 6 mm short
        # of the forward face and lie between the three fixed-sector/longeron
        # load-path lands at 60/180/300 degrees.
        for arm_clock in (0.0, 120.0, 240.0):
            ring = ring.cut(g.analytic_sector(25.5, 19.3, 2.6,
                                              arm_clock, 22.0, 1.8))
    # Two channels within each of the three fixed-sector longerons.
    for center in (60.0, 180.0, 300.0):
        for delta in (-25.0, 25.0):
            x, y = radial_xy(26.2, center + delta)
            ring = ring.cut(g.cyl_z(1.55, length + 0.8, x, y, -length / 2.0 - 0.4))
    return ring


def forward_shell_with_port() -> cq.Shape:
    # Butt between the aft face of FWD-RING-01 (z=344) and the forward face
    # of FWD-RING-02 (z=881).  The prior 545 mm tube double-occupied 4 mm of
    # both weld rings.
    shell = g.tube_z(g.NORMAL_R, 25.35, 537.0, z0=4.0)
    # Deliberate radial water path at local z=200 (global z=540), phi=90.
    bore = cq.Solid.makeCylinder(2.15, 4.0, cq.Vector(0.0, 24.5, 200.0), cq.Vector(0, 1, 0))
    # Shallow conformal counterbore receives the inner gland flange without
    # allowing its flat annulus to occupy the curved shell wall.
    gland_counterbore = cq.Solid.makeCylinder(4.15, 1.2, cq.Vector(0.0, 24.3, 200.0), cq.Vector(0, 1, 0))
    shell = shell.cut(bore.fuse(gland_counterbore))
    # Four edge-open, jig-machined axial service grooves lead the formed
    # routes from the shell interior into their individual bulkhead unions at
    # the routed ring.  Each cutter includes 0.20 mm radial assembly clearance.
    route_grooves = ((35.0, 1.20), (85.0, 0.95), (155.0, 1.00), (205.0, 0.50))
    for phi, radius in route_grooves:
        x, y = radial_xy(26.2, phi)
        shell = shell.cut(g.cyl_z(radius, 31.4, x, y, 509.8))
    return shell


def aft_shell_with_openings() -> cq.Shape:
    # The load-carrying shell ends at the service-throat pilot plane.  The R1
    # geometry incorrectly double-occupied the final 100 mm with two tubes.
    # Start at the aft face of the shifted z=1638 route ring and stop at the forward
    # face of the service throat.  This removes the former 4 mm double-volume
    # ring joint while retaining the same external product datums.
    shell = g.tube_z(g.NORMAL_R, 25.30, 286.0, z0=7.0)
    # Hardpoint lug aperture at global z=1900.
    shell = shell.cut(g.box_center(5.6, 11.0, 14.0, 25.7, 0.0, 265.0))
    latch_window = g.box_center(8.0, 7.0, 18.0, 25.4, 0.0, 110.0).rotate((0, 0, 0), (0, 0, 1), 270.0)
    shell = shell.cut(latch_window)
    # The arm-module routes turn inboard immediately aft of the routed ring.
    # Machine four individual oblique passages that follow those centerlines;
    # no route is allowed to occupy intact shell wall stock.
    route_passages = ((35.0, 1.20), (85.0, 0.95), (155.0, 1.00), (205.0, 0.50))
    for phi, radius in route_passages:
        a = math.radians(phi)
        points = [
            (26.2 * math.cos(a), 26.2 * math.sin(a), 3.6),
            (26.2 * math.cos(a), 26.2 * math.sin(a), 5.0),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 25.0),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 36.0),
        ]
        shell = shell.cut(g.routed_round(points, radius))
    return shell


def service_throat_shape() -> cq.Shape:
    throat = g.tube_z(26.3, 23.8, 103.0)
    throat = throat.cut(cq.Solid.makeCylinder(2.55, 8.6, cq.Vector(28.0, -4.3, 100.0), cq.Vector(0, 1, 0)))
    # External double-shear hinge ears at the local aft plane z=100 mm.
    for yy in (-5.2, 5.2):
        ear = g.ring_y(28.0, 100.0, 2.0, 3.0, 1.6, yy)
        web = g.box_center(4.0, 2.0, 5.0, 26.3, yy, 98.5)
        throat = throat.fuse(ear).fuse(web)
    throat = throat.cut(cq.Solid.makeCylinder(1.6, 14.0, cq.Vector(28.0, -7.0, 100.0), cq.Vector(0, 1, 0)))
    # Four radial M3 threaded bores for the door detents.  They are modeled as
    # actual penetrations; the purchased plungers no longer occupy wall stock.
    for phi in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(phi)
        origin = cq.Vector(22.8 * math.cos(a), 22.8 * math.sin(a), 98.0)
        direction = cq.Vector(math.cos(a), math.sin(a), 0.0)
        throat = throat.cut(cq.Solid.makeCylinder(1.62, 4.2, origin, direction))
    return throat


def radial_detent_shape() -> cq.Shape:
    return cq.Solid.makeCylinder(1.50, 3.8, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))


def cartridge_shape() -> cq.Shape:
    body = g.cyl_z(9.3345, 74.0)
    dome = cq.Solid.makeSphere(9.3345, cq.Vector(0, 0, 74.0)).intersect(g.cyl_z(10.0, 9.0, z0=74.0))
    neck = g.cyl_z(4.75, 8.55, z0=74.0)
    shoulder = cq.Solid.makeCone(9.3345, 4.75, 4.0, cq.Vector(0, 0, 72.0), cq.Vector(0, 0, 1))
    return body.fuse(dome).fuse(shoulder).fuse(neck)


def cartridge_carrier_shape() -> cq.Shape:
    plate = g.cyl_z(24.2, 4.0, z0=-2.0)
    for x in (-9.5, 9.5):
        for y in (-9.5, 9.5):
            plate = plate.cut(g.cyl_z(9.55, 4.6, x, y, -2.3))
    return plate


def booster_tube_shape() -> cq.Shape:
    tube = g.tube_z(6.5, 5.5, 430.0)
    # Thickened bosses are contained within the controlled 430 mm length.
    fwd = g.tube_z(6.5, 2.0, 6.0, z0=0.0)
    aft = g.tube_z(6.5, 2.0, 6.0, z0=424.0)
    return tube.fuse(fwd).fuse(aft)


def booster_band_shape() -> cq.Shape:
    band = g.tube_z(7.2, 6.65, 5.0, z0=-2.5)
    foot = g.box_center(4.0, 8.0, 5.0, 8.2, 0.0, 0.0)
    hole = cq.Solid.makeCylinder(1.55, 8.4, cq.Vector(9.0, -4.2, 0.0), cq.Vector(0, 1, 0))
    return band.cut(g.box_center(3.0, 8.0, 4.0, 6.8, 0, 0)).fuse(foot).cut(hole)


def puncture_head_shape() -> cq.Shape:
    body = g.cyl_z(5.4, 5.8)
    bore = g.cyl_z(2.1, 6.2, z0=-0.2)
    needle = cq.Solid.makeCone(1.2, 0.15, 3.5, cq.Vector(0, 0, 0.0), cq.Vector(0, 0, -1))
    return body.cut(bore).fuse(needle)


def manifold_shape() -> cq.Shape:
    block = g.cyl_z(20.0, 10.0, z0=-5.0)
    for x in (-9.5, 9.5):
        for y in (-9.5, 9.5):
            block = block.cut(g.cyl_z(2.2, 10.6, x, y, -5.3))
    block = block.cut(g.cyl_z(3.0, 10.6, 0, 0, -5.3))
    return block


def water_trigger_housing_shape() -> cq.Shape:
    housing = g.tube_z(7.0, 5.3, 58.0)
    # Port center is local z=40 (global z=540), coaxial with the controlled
    # shell gland.  The 4.10 mm reamed boss bore clears the 3.90 mm inlet tube;
    # the parts seat at the defined flange instead of overlapping cylinders.
    radial_outer = cq.Solid.makeCylinder(2.4, 9.0, cq.Vector(0, 5.0, 40.0), cq.Vector(0, 1, 0))
    radial_inner = cq.Solid.makeCylinder(2.05, 9.4, cq.Vector(0, 4.8, 40.0), cq.Vector(0, 1, 0))
    return housing.fuse(radial_outer).cut(radial_inner)


def valve_body_shape() -> cq.Shape:
    body = g.cyl_z(5.5, 22.0)
    body = body.cut(g.cyl_z(2.1, 22.4, z0=-0.2))
    branch = cq.Solid.makeCylinder(3.0, 11.0, cq.Vector(0, 0, 11.0), cq.Vector(1, 0, 0))
    branch = branch.cut(cq.Solid.makeCylinder(1.2, 11.4, cq.Vector(-0.2, 0, 11), cq.Vector(1, 0, 0)))
    return body.fuse(branch)


def local_route_channel_shape(length: float, ro: float, ri: float | None = None) -> cq.Shape:
    return g.tube_z(ro, ri, length) if ri is not None else g.cyl_z(ro, length)


def actuator_body_shape(ro: float, bore_r: float, length: float, eye_z: float,
                        eye_ro: float = 6.0) -> cq.Shape:
    body = g.tube_z(ro, bore_r, length)
    neck = g.box_center(5.0, 4.0, max(eye_z - length, 2.0), 0.0, 0.0,
                        length + max(eye_z - length, 2.0) / 2.0)
    out = body.fuse(neck).fuse(g.ring_y(0.0, eye_z, 4.0, eye_ro, 2.18))
    bore = cq.Solid.makeCylinder(2.18, 8.0, cq.Vector(0, -4.0, eye_z), cq.Vector(0, 1, 0))
    return out.cut(bore)


def actuator_rod_shape(radius: float, shaft_length: float, eye_ro: float = 5.0) -> cq.Shape:
    eye = g.ring_y(0.0, 0.0, 4.0, eye_ro, 2.18)
    shaft = g.cyl_z(radius, shaft_length - 6.0, z0=6.0)
    neck = g.box_center(radius * 1.8, 3.8, 7.0, 0.0, 0.0, 4.5)
    out = eye.fuse(neck).fuse(shaft)
    bore = cq.Solid.makeCylinder(2.18, 8.0, cq.Vector(0, -4.0, 0.0), cq.Vector(0, 1, 0))
    return out.cut(bore)


def actuator_fixed_yoke_shape(eye_ro: float = 6.0) -> cq.Shape:
    out = None
    for yy in (-3.25, 3.25):
        ear = g.ring_y(0.0, 0.0, 2.0, eye_ro + 0.5, 2.18, yy)
        web = g.box_center(8.0, 2.0, 12.0, 3.0, yy, 2.0)
        piece = ear.fuse(web)
        out = piece if out is None else out.fuse(piece)
    bridge = g.box_center(8.0, 8.5, 2.0, 3.0, 0.0, 8.0)
    out = out.fuse(bridge)
    bore = cq.Solid.makeCylinder(2.18, 10.0, cq.Vector(0, -5.0, 0), cq.Vector(0, 1, 0))
    return out.cut(bore)


def make_body_longeron(length: float) -> cq.Shape:
    return g.analytic_sector(23.8, 20.8, length, 0.0, 4.0)


def build_forward(b: R2Builder) -> None:
    path = "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY"
    nose = b.define("DF8-R2-NOSE-001", "A", "TUNGSTEN PENETRATOR NOSE", cq.Solid.makeCone(1.5, 26.3, 170.0),
                    "Tungsten heavy alloy", process="CNC turn and grind", color_key="tungsten")
    b.add(b.forward, path, nose, "NOSE-001", g.identity_loc(), "FIXED", "SHRINK_FIT_AND_TAPER_PIN", notes="Identity transform justified: top-level product datum origin.")

    ballast_shape = g.cyl_z(24.8, 166.0).cut(g.cyl_z(8.0, 166.4, z0=-0.2))
    ballast = b.define("DF8-R2-BALLAST-001", "A", "FORWARD TUNGSTEN BALLAST AND PRIMARY SPINE SOCKET", ballast_shape,
                       "Tungsten heavy alloy", process="CNC turn; wire-EDM socket", color_key="tungsten")
    b.add(b.forward, path, ballast, "BALLAST-001", g.translation_loc(0, 0, 170.0), "FIXED", "SHRINK_FIT_AND_TAPER_PIN")

    shell = b.define("DF8-R2-FWD-SHELL-001", "A", "FORWARD GRADE-9 TITANIUM SHELL WITH CONTROLLED WATER PORT",
                     forward_shell_with_port(), "Ti-3Al-2.5V Grade 9", process="Cold draw; laser port; finish hone", color_key="titanium")
    b.add(b.forward, path, shell, "FWD-SHELL-001", g.translation_loc(0, 0, 340.0), "FIXED", "LASER_WELDED_RING_JOINT")

    ring_plain = b.define("DF8-R2-STRUCT-RING-PLAIN-001", "A", "PRIMARY STRUCTURAL TRANSITION RING",
                          g.tube_z(25.3, 19.5, 8.0, z0=-4.0), "Ti-6Al-4V", process="Mill-turn", color_key="titanium")
    route_ring = b.define("DF8-R2-STRUCT-RING-ROUTED-001", "A", "STRUCTURAL RING WITH SIX CONTROLLED ROUTE PASSAGES AND THREE ARM-ROOT RELIEFS",
                          ring_with_axial_route_holes(8.0, arm_root_reliefs=True), "Ti-6Al-4V", process="Mill-turn and jig-bore", color_key="titanium")
    for idx, z in enumerate((340.0, 885.0), 1):
        p = ring_plain if idx == 1 else route_ring
        b.add(b.forward, path, p, f"FWD-RING-{idx:02d}", g.translation_loc(0, 0, z), "FIXED", "LASER_WELDED_RING_JOINT")

    fwd_longeron = b.define("DF8-R2-FWD-LONGERON-001", "A", "FORWARD PRIMARY LOAD-PATH LONGERON",
                            make_body_longeron(425.9), "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, 455.0)
        b.add(b.forward, path, fwd_longeron, f"FWD-LONGERON-{idx}", loc, "FIXED", "WELDED_TO_STRUCTURAL_RINGS")

    cart = b.define("LELAND-81121", "A", "LELAND 81121 12 G CO2 CARTRIDGE", cartridge_shape(),
                    "Steel pressure cartridge", "BUY", "Leland Gas Technologies", "DRAWING_DERIVED",
                    mass_kg=0.045, source_url="https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
                    purchase_url="https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
                    notes="Exact puncture installation remains physical/procurement verification hold.", color_key="steel")
    carrier = b.define("DF8-R2-CARTRIDGE-CARRIER-001", "A", "FOUR-CARTRIDGE DOUBLE-PLATE CARRIER", cartridge_carrier_shape(),
                       "7075-T6 aluminum", process="5-axis mill", color_key="aluminum")
    b.add(b.forward, path, carrier, "CARTRIDGE-CARRIER-FWD", g.translation_loc(0, 0, 346.1), "FIXED", "BOLTED_TO_FORWARD_RING")
    b.add(b.forward, path, carrier, "CARTRIDGE-CARRIER-AFT", g.translation_loc(0, 0, 433.5), "FIXED", "BOLTED_TO_MANIFOLD")
    positions = [(-9.5, -9.5), (9.5, -9.5), (9.5, 9.5), (-9.5, 9.5)]
    for idx, (x, y) in enumerate(positions, 1):
        oid = b.add(b.forward, path, cart, f"CO2-CARTRIDGE-{idx}", g.translation_loc(x, y, 348.0), "CONSUMED", "THREADED_AND_CLAMPED")
        b.connect(f"CONN-CART-{idx}", oid, "CARTRIDGE-CARRIER-FWD", "CYLINDER_BODY_OD", f"CARRIER_BORE_{idx}",
                  "RADIAL_CLAMP", "0", "CARRIER-FWD/AFT", "PUNCTURE_HEAD SHOULDER", "TWO SPACED CARRIER BORES",
                  "THREAD INTO PUNCTURE HEAD", "NONE", "COLLECTION MANIFOLD", "UNTHREAD AFTER DISCHARGE", "Joint geometry report")

    manifold = b.define("DF8-R2-COLLECTION-MANIFOLD-001", "A", "FOUR-PORT COLLECTION MANIFOLD WITH BORED PASSAGES",
                        manifold_shape(), "316 stainless steel", process="5-axis mill; gun drill; proof test", color_key="stainless")
    b.add(b.forward, path, manifold, "COLLECTION-MANIFOLD-001", g.translation_loc(0, 0, 445.0), "FIXED", "BOLTED_TO_CARRIER")
    ph = b.define("DF8-R2-PUNCTURE-HEAD-001", "A", "CARTRIDGE PUNCTURE HEAD WITH CONTROLLED NEEDLE", puncture_head_shape(),
                  "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    for idx, (x, y) in enumerate(positions, 1):
        b.add(b.forward, path, ph, f"PUNCTURE-HEAD-{idx}", g.translation_loc(x, y, 434.2), "FIXED", "THREADED_MANIFOLD_PORT")

    booster = b.define("DF8-R2-BOOSTER-RESERVOIR-001", "A", "13 OD X 11 ID X 430 BOOSTER RESERVOIR WITH END BOSSES",
                       booster_tube_shape(), "316 stainless steel", process="Seamless tube; orbital weld; proof test",
                       notes="PROVISIONAL — BLOCKS FINAL RELEASE: pressure design and supplier unresolved.", color_key="stainless")
    band = b.define("DF8-R2-BOOSTER-BAND-001", "A", "CAPTIVE BOOSTER SUPPORT BAND WITH M3 TAB", booster_band_shape(),
                    "PEEK", process="Machine from PEEK", color_key="peek")
    for idx, phi in enumerate((30.0, 150.0, 270.0), 1):
        x, y = radial_xy(14.0, phi)
        b.add(b.forward, path, booster, f"BOOSTER-{idx}", g.translation_loc(x, y, 451.0), "FIXED", "THREE_SPACED_PEEK_BANDS")
        for bi, z in enumerate((454.0, 650.0, 858.0), 1):
            loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(14.0, 0, z)
            b.add(b.forward, path, band, f"BOOSTER-BAND-{idx}-{bi}", loc, "FIXED", "M3_BOLTED_CLAMP")

    trigger = b.define("DF8-R2-WATER-TRIGGER-HSG-001", "A", "CENTRAL WATER-SENSITIVE TRIGGER HOUSING", water_trigger_housing_shape(),
                       "Acetal", process="CNC turn and mill", color_key="black")
    bobbin = b.define("V80040", "A", "HALKEY-ROBERTS WATER-SENSITIVE BOBBIN", g.cyl_z(5.0, 18.0),
                      "Water-sensitive media", "BUY", "Nordson MEDICAL / Halkey-Roberts", "DRAWING_DERIVED",
                      source_url="https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-V80040-Bobbin-Instructions-For-Use.pdf",
                      notes="Custom housing use remains manufacturer-compatibility hold.", color_key="peek")
    b.add(b.forward, path, trigger, "WATER-TRIGGER-HSG-001", g.translation_loc(0, 0, 500.0), "FIXED", "BOLTED_TO_CENTRAL_CARRIER")
    b.add(b.forward, path, bobbin, "WATER-BOBBIN-001", g.translation_loc(0, 0, 520.0), "CONSUMED", "CAPTIVE_TRIGGER_CUP")

    inlet_shape = g.tube_between((0, 0, 0), (23.5, 0, 0), 1.95, 1.45)
    inlet_shape = inlet_shape.fuse(g.ring_x(0, 0, 1.0, 4.0, 2.1, 19.8))
    inlet_shape = inlet_shape.fuse(g.ring_x(0, 0, 0.8, 4.0, 2.1, 22.2))
    inlet = b.define("DF8-R2-WATER-INLET-001", "A", "RADIAL FLOOD INLET, GLAND AND ANTI-DEBRIS SCREEN",
                     inlet_shape,
                     "316 stainless steel", process="Microtube form and braze", color_key="stainless")
    inlet_loc = g.rotation_loc((0, 0, 1), 90.0) * g.translation_loc(5.0, 0.0, 540.0)
    b.add(b.forward, path, inlet, "WATER-INLET-001", inlet_loc, "FIXED", "RADIAL_GLAND_AND_SCREEN")
    b.add_route_record("WATER-INLET-001", "EXTERNAL_WATER", "WATER-TRIGGER-HSG-001",
                       "Integral screen flange / housing O-ring nipple", "FWD-SHELL radial Ø4.30 mm port",
                       "Integral brazed gland", 20.0, 0.0, "Flood path, non-pressure", "GEOMETRY COMPLETE; compatibility provisional")

    valve = b.define("DF8-R2-FULLFLOW-VALVE-001", "A", "DIRECT FULL-FLOW VALVE WITH BORED AXIAL AND RADIAL PORTS", valve_body_shape(),
                     "17-4PH stainless steel", process="Swiss turn; cross-drill; lap", color_key="steel")
    b.add(b.forward, path, valve, "FULLFLOW-VALVE-001", g.rotation_loc((0, 0, 1), 90.0) * g.translation_loc(0, 0, 850.0), "MOVING", "GUIDED_SPOOL", "1 AXIAL")


def add_arm_hardware(b: R2Builder, arm_index: int, phi: float, theta: float, arm: g.PartDef,
                     carrier: g.PartDef, pivot_pin: g.PartDef, bushing: g.PartDef, washer: g.PartDef,
                     pivot_clip: g.PartDef, link: g.PartDef, link_pin: g.PartDef, link_clip: g.PartDef,
                     stop_pad: g.PartDef, fixed_stop: g.PartDef, lock_dog: g.PartDef,
                     lock_spring: g.PartDef, stow_dog: g.PartDef) -> None:
    path = f"300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/33{arm_index}_ARM_{arm_index}_ASSY"
    arm_loc = g.arm_occurrence_loc(theta, phi)
    b.add(b.arm_module, path, arm, f"ARM-{arm_index}", arm_loc, "MOVING", "REVOLUTE", "1 ROTATION ABOUT 8 MM PIVOT")
    carrier_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(g.PIVOT_R, 0, g.PIVOT_Z)
    b.add(b.arm_module, path, carrier, f"PIVOT-CARRIER-{arm_index}", carrier_loc, "FIXED", "WELDED_AND_DOWELLED")
    b.add(b.arm_module, path, pivot_pin, f"PIVOT-PIN-{arm_index}", carrier_loc * g.translation_loc(0, -9.0, 0), "FIXED", "SHOULDER_PIN_WITH_SPIRAL_RING")
    for side, yy in enumerate((-4.75, 4.75), 1):
        loc = carrier_loc * g.translation_loc(0, yy, 0)
        b.add(b.arm_module, path, bushing, f"PIVOT-BUSH-{arm_index}-{side}", loc, "FIXED", "PRESS_FIT_IN_ARM_BOSS")
    for side, yy in enumerate((-5.90, 5.90), 1):
        loc = carrier_loc * g.translation_loc(0, yy, 0)
        b.add(b.arm_module, path, washer, f"PIVOT-WASHER-{arm_index}-{side}", loc, "FIXED", "CAPTIVE_ON_PIVOT_SHOULDER")
    clip_loc = carrier_loc * g.translation_loc(0, 8.2, 0)
    b.add(b.arm_module, path, pivot_clip, f"PIVOT-CLIP-{arm_index}", clip_loc, "FIXED", "EXTERNAL_GROOVE")

    kin = g.kinematic(theta)
    for li, yy in enumerate((-1.75, 1.75), 1):
        l_loc = g.link_occurrence_loc(theta, yy, phi)
        b.add(b.arm_module, path, link, f"LINK-{arm_index}-{li}", l_loc, "MOVING", "TWO_REVOLUTE_PIN_JOINTS", "PLANAR FOUR-BAR")
    # One full-span pin secures both link plates at each end; each has a modeled retainer.
    bell_local = g.translation_loc(g.BELL_U, 0, g.BELL_V)
    bell_global = arm_loc * bell_local
    crosshead_pin_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(g.CROSSHEAD_R, -5.5, kin["crosshead_z"])
    bell_pin_loc = bell_global * g.translation_loc(0, -5.5, 0)
    for end, loc in (("BELL", bell_pin_loc), ("CROSSHEAD", crosshead_pin_loc)):
        b.add(b.arm_module, path, link_pin, f"LINK-PIN-{arm_index}-{end}", loc, "MOVING", "CLEVIS_PIN_WITH_E_RING")
        b.add(b.arm_module, path, link_clip, f"LINK-CLIP-{arm_index}-{end}", loc * g.translation_loc(0, 10.25, 0), "MOVING", "EXTERNAL_GROOVE")

    pad_loc = arm_loc * g.translation_loc(4.0, 0, -8.5)
    b.add(b.arm_module, path, stop_pad, f"ARM-STOP-PAD-{arm_index}", pad_loc, "MOVING", "DOVETAIL_AND_TWO_M3_SCREWS")
    stop_pose = g.arm_occurrence_loc(g.DEPLOYED_ANGLE, phi) * g.translation_loc(4.0, 0, -8.5)
    b.add(b.arm_module, path, fixed_stop, f"FIXED-STOP-{arm_index}", stop_pose * g.translation_loc(-0.4, 0, -4.0), "FIXED", "DOWEL_AND_TWO_M3_SCREWS")
    dog_shift = 0.0 if theta >= 79.9 else -10.0
    b.add(b.arm_module, path, lock_dog, f"LOCK-DOG-{arm_index}", stop_pose * g.translation_loc(dog_shift, 0, 4.0), "MOVING", "GUIDED_SPRING_DOG", "1 TRANSLATION")
    b.add(b.arm_module, path, lock_spring, f"LOCK-SPRING-{arm_index}", stop_pose * g.translation_loc(dog_shift - 4.0, 0, 4.0), "FLEXIBLE", "CAPTURED_SPRING_SEATS", "AXIAL COMPRESSION")
    dog_r = 17.0 if theta < 0.1 else 13.5
    dog_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(dog_r, 0, g.PIVOT_Z + g.ARM_LENGTH - 3.5)
    b.add(b.arm_module, path, stow_dog, f"STOW-DOG-{arm_index}", dog_loc, "MOVING", "RADIAL_GUIDE_AND_RETURN_SPRING", "1 RADIAL TRANSLATION")


def build_arm_module(b: R2Builder) -> None:
    path = "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY"
    theta = g.DEPLOYED_ANGLE if b.deployed else 0.0
    fixed_sector = b.define("DF8-R2-FIXED-SECTOR-001", "A", "ANALYTIC CYLINDRICAL FIXED BODY SECTOR", g.make_fixed_sector_local(),
                            "Ti-6Al-4V", process="Hot form and 5-axis trim", color_key="titanium")
    longeron = b.define("DF8-R2-ROUTED-LONGERON-001", "A", "PRIMARY LONGERON WITH TWO JIG-BORED ROUTE CHANNELS", g.make_longeron_local(),
                        "Ti-6Al-4V", process="5-axis mill and jig bore", color_key="titanium")
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, 889.0)
        b.add(b.arm_module, path, fixed_sector, f"FIXED-SECTOR-{idx}", loc, "FIXED", "WELDED_TO_LONGERON")
        b.add(b.arm_module, path, longeron, f"ARM-LONGERON-{idx}", loc, "FIXED", "WELDED_BETWEEN_ROUTE_RINGS")

    arm = b.define("DF8-R2-ARM-BLADE-001", "A", "733.806 MM SMOOTH ANALYTIC HOLLOW OML ARM", g.make_arm_part_local(),
                   "Ti-6Al-4V", process="Hot form; 5-axis machine; laser weld; CMM inspect",
                   notes="Analytic cylindrical OML; no planar patch tiling or mesh-derived surfaces.", color_key="titanium")
    carrier = b.define("DF8-R2-PIVOT-CARRIER-001", "A", "MATCHED DOUBLE-SHEAR PIVOT LUG SET", g.make_pivot_carrier_local(),
                       "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    pivot_pin = b.define("DF8-R2-PIVOT-PIN-008", "A", "8 MM CAPTIVE SHOULDER PIVOT PIN WITH GROOVE", g.make_clevis_pin(8.0, 18.0, 10.0, 1.5),
                         "17-4PH stainless steel", process="Swiss turn; H900; grind", color_key="steel")
    bushing = b.define("DF8-R2-PIVOT-BUSH-008", "A", "8 MM PEEK-LINED PIVOT BUSHING", g.ring_y(0, 0, 2.0, 4.15, 4.02),
                       "PEEK", process="Turn and press fit", color_key="peek")
    washer = b.define("DF8-R2-PIVOT-WASHER-008", "A", "8 MM PEEK THRUST WASHER", g.ring_y(0, 0, 0.18, 6.0, 4.15),
                      "PEEK", process="Turn", color_key="peek")
    pivot_clip = b.define("DF8-R2-PIVOT-SPIRAL-RING-008", "A", "8 MM EXTERNAL SPIRAL PIVOT RETAINER", g.make_external_retaining_ring(8.0),
                          "1.4310 stainless spring steel", process="Wire form", color_key="spring")
    link = b.define("DF8-R2-SHORT-LINK-001", "A", "19.950 MM CENTER-DISTANCE REAMED SHORT LINK", g.make_link_part_local(),
                    "17-4PH stainless steel", process="Wire EDM; H900; ream", color_key="steel")
    link_pin = b.define("DF8-R2-LINK-PIN-004", "A", "4 MM FULL-SPAN LINK PIN WITH RETAINER GROOVE", g.make_clevis_pin(4.0, 11.0, 6.0, 1.0),
                        "17-4PH stainless steel", process="Swiss turn; H900; grind", color_key="steel")
    link_clip = b.define("DF8-R2-LINK-E-RING-004", "A", "4 MM LINK-PIN EXTERNAL RETAINING RING", g.make_external_retaining_ring(4.0, 0.45),
                         "1.4310 stainless spring steel", "BUY", "Qualified retainer supplier TBD", "PROVISIONAL — BLOCKS FINAL RELEASE",
                         process="Stamped spring ring", color_key="spring")
    stop_pad = b.define("DF8-R2-ARM-STOP-PAD-001", "A", "REPLACEABLE ARM STOP AND LOCK STRIKE", g.box_center(5.0, 7.6, 3.8),
                        "17-4PH stainless steel", process="Wire EDM and grind", color_key="steel")
    fixed_stop = b.define("DF8-R2-FIXED-STOP-001", "A", "80 DEGREE DOWEL-LOCATED FIXED STOP", g.box_center(5.5, 8.2, 4.0),
                          "17-4PH stainless steel", process="Wire EDM and grind", color_key="steel")
    lock_dog = b.define("DF8-R2-LOCK-DOG-001", "A", "CAPTIVE DEPLOYED LOCK DOG", g.box_center(4.0, 3.8, 3.0),
                        "17-4PH stainless steel", process="Wire EDM and lap", color_key="steel")
    lock_spring = b.define("DF8-R2-LOCK-SPRING-001", "A", "CAPTURED LOCK-DOG RETURN SPRING", g.make_compression_spring_local(3.6, 0.55, 8.0, 7.0),
                           "1.4310 stainless spring steel", process="Cold coil", color_key="spring")
    stow_dog = b.define("DF8-R2-STOW-DOG-001", "A", "CAPTIVE RADIAL STOWED-RETENTION DOG", g.box_center(4.0, 4.4, 5.5),
                        "17-4PH stainless steel", process="Wire EDM and grind", color_key="steel")
    for idx, phi in enumerate((0.0, 120.0, 240.0), 1):
        add_arm_hardware(b, idx, phi, theta, arm, carrier, pivot_pin, bushing, washer, pivot_clip,
                         link, link_pin, link_clip, stop_pad, fixed_stop, lock_dog, lock_spring, stow_dog)

    crosshead = b.define("DF8-R2-CROSSHEAD-001", "A", "ONE-PIECE SIX-CLEVIS GUIDED COMMON CROSSHEAD", g.make_crosshead_part_local(),
                         "17-4PH stainless steel", process="5-axis mill-turn; H900; hone", color_key="steel")
    zc = g.kinematic(theta)["crosshead_z"]
    b.add(b.arm_module, path, crosshead, "CROSSHEAD-001", g.translation_loc(0, 0, zc), "MOVING", "GUIDED_TRANSLATION", "1 AXIAL TRANSLATION")
    guide = b.define("DF8-R2-CROSSHEAD-GUIDE-001", "A", "CENTRAL DLC CROSSHEAD GUIDE SHAFT", g.cyl_z(3.2, 36.0),
                     "17-4PH stainless steel", process="Centerless grind and DLC", color_key="steel")
    b.add(b.arm_module, path, guide, "CROSSHEAD-GUIDE-001", g.translation_loc(0, 0, 900.0), "FIXED", "DOUBLE_SUPPORTED_SHAFT")

    spring_length = g.SPRING_DEPLOYED if b.deployed else g.SPRING_STOWED
    backup_spring = b.define("DF8-R2-BACKUP-SPRING-16N-001", "A", "CUSTOM 16 N/MM GUIDED BACKUP COMPRESSION SPRING",
                             g.make_compression_spring_local(g.SPRING_OD, g.SPRING_WIRE, spring_length, 25.3),
                             "1.4310 stainless spring steel", "MAKE", "Qualified spring supplier TBD",
                             "PROVISIONAL — BLOCKS FINAL RELEASE", process="Cold coil and stress relieve",
                             notes="Exact performance supplier and qualification remain open.", color_key="spring")
    spring_station = g.rotation_loc((0, 0, 1), 300.0) * g.translation_loc(12.0, 0.0, 0.0)
    moving_seat_z = zc + 4.0
    spring_z = zc + 6.5
    fixed_seat_z = spring_z + spring_length + 2.5
    b.add(b.arm_module, path, backup_spring, "BACKUP-SPRING-001", spring_station * g.translation_loc(0, 0, spring_z), "FLEXIBLE", "CAPTURED_GUIDED_SPRING", "AXIAL COMPRESSION")
    fixed_seat = b.define("DF8-R2-BACKUP-SPRING-FIXED-SEAT-001", "A", "BACKUP SPRING AFT FIXED SEAT", g.tube_z(8.5, 3.4, 5.0, z0=-2.5),
                          "Ti-6Al-4V", process="Mill-turn", color_key="titanium")
    moving_seat = b.define("DF8-R2-BACKUP-SPRING-MOVING-SEAT-001", "A", "BACKUP SPRING CROSSHEAD SEAT", g.tube_z(8.5, 3.4, 5.0, z0=-2.5),
                           "17-4PH stainless steel", process="Mill-turn", color_key="steel")
    b.add(b.arm_module, path, fixed_seat, "BACKUP-SPRING-FIXED-SEAT", spring_station * g.translation_loc(0, 0, fixed_seat_z), "FIXED", "THREADED_TO_GUIDE_SUPPORT")
    b.add(b.arm_module, path, moving_seat, "BACKUP-SPRING-MOVING-SEAT", spring_station * g.translation_loc(0, 0, moving_seat_z), "MOVING", "FACE_MOUNTED_TO_CROSSHEAD_SPOKE")
    spring_guide = b.define("DF8-R2-BACKUP-SPRING-GUIDE-001", "A", "BACKUP SPRING DLC GUIDE SHAFT", g.cyl_z(2.5, 185.0),
                            "17-4PH stainless steel", process="Centerless grind and DLC", color_key="steel")
    b.add(b.arm_module, path, spring_guide, "BACKUP-SPRING-GUIDE", spring_station * g.translation_loc(0, 0, 900.0), "FIXED", "SUPPORTED_AT_BOTH_ENDS")

    # Parallel GS/HBD installations occupy fixed-sector corridors aft of the crosshead.
    gs_src = next((INPUT_DIR / "wp02").rglob("ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp"))
    gs_body = b.define("GS-19-50-V4A-B8-B8", "R2-INSTALL", "ACE GS-19-50-V4A-B8-B8 PURCHASED ASSEMBLY — ARTICULATED INSTALLATION BODY",
                       actuator_body_shape(9.5, 5.2, 105.0, 112.0), "316 stainless steel", "BUY", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.420,
                       source_url="https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
                       purchase_url="https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
                       notes=f"Articulated drawing-derived installation model; unmodified authentic vendor STEP retained separately at {gs_src.name}; 300±30 N setting requires CoC.", color_key="gas")
    gs_rod = b.define("GS-19-50-V4A-B8-B8-ROD-CHILD", "R2-INSTALL", "ACE GS-19 MOVING ROD ARTICULATION CHILD", actuator_rod_shape(4.0, 70.0),
                      "316 stainless steel", "INTERNAL CHILD", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.0,
                      notes="No separate purchase quantity; authentic vendor source is not modified.", color_key="stainless")
    gs_phi, gs_r, gs_body_z = 60.0, 13.5, 960.0
    gs_body_loc = g.rotation_loc((0, 0, 1), gs_phi) * g.translation_loc(gs_r, 0, gs_body_z)
    gs_rod_loc = g.rotation_loc((0, 0, 1), gs_phi) * g.translation_loc(gs_r, 0, zc)
    b.add(b.arm_module, path, gs_body, "GS19-BODY-001", gs_body_loc, "FIXED", "PINNED_B8_END")
    b.add(b.arm_module, path, gs_rod, "GS19-ROD-001", gs_rod_loc, "MOVING", "TELESCOPING_GAS_SPRING", "1 AXIAL TRANSLATION")

    hbd_src = next((INPUT_DIR / "wp02").rglob("ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step"))
    hbd_body = b.define("HBD-15-25-AA-P", "R2-INSTALL", "ACE HBD-15-25-AA-P PURCHASED ASSEMBLY — ARTICULATED INSTALLATION BODY", actuator_body_shape(7.5, 4.0, 95.0, 102.0, 5.5),
                        "316 stainless steel", "BUY", "ACE Controls", "PROVISIONAL — BLOCKS FINAL RELEASE", mass_kg=0.220,
                        source_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
                        purchase_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
                        notes=f"Drawing-derived installation geometry from {hbd_src.name}; exact AA-P configuration and force-speed data unresolved.", color_key="hydraulic")
    hbd_rod = b.define("HBD-15-25-AA-P-ROD-CHILD", "R2-INSTALL", "HBD MOVING ROD ARTICULATION CHILD", actuator_rod_shape(3.0, 60.0, 4.5),
                       "316 stainless steel", "INTERNAL CHILD", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.0,
                       notes="No separate purchase quantity.", color_key="stainless")
    hbd_phi, hbd_r, hbd_body_z = 180.0, 14.5, 960.0
    hbd_body_loc = g.rotation_loc((0, 0, 1), hbd_phi) * g.translation_loc(hbd_r, 0, hbd_body_z)
    hbd_rod_loc = g.rotation_loc((0, 0, 1), hbd_phi) * g.translation_loc(hbd_r, 0, zc)
    b.add(b.arm_module, path, hbd_body, "HBD-BODY-001", hbd_body_loc, "FIXED", "PINNED_AA_END")
    b.add(b.arm_module, path, hbd_rod, "HBD-ROD-001", hbd_rod_loc, "MOVING", "TELESCOPING_DAMPER", "1 AXIAL TRANSLATION")

    fixed_yoke = b.define("DF8-R2-ACTUATOR-FIXED-YOKE-001", "A", "DOUBLE-SHEAR ACTUATOR BODY ANCHOR YOKE", actuator_fixed_yoke_shape(),
                           "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    actuator_pin = b.define("DF8-R2-ACTUATOR-PIN-004", "A", "4 MM CAPTIVE ACTUATOR CLEVIS PIN", g.make_clevis_pin(4.0, 8.0, 6.0, 1.0),
                            "17-4PH stainless steel", process="Swiss turn; H900", color_key="steel")
    actuator_clip = b.define("DF8-R2-ACTUATOR-E-RING-004", "A", "4 MM ACTUATOR PIN RETAINER", g.make_external_retaining_ring(4.0, 0.45),
                             "1.4310 stainless spring steel", process="Stamp", color_key="spring")
    for label, phi, radius, fixed_z in (("GS19", gs_phi, gs_r, gs_body_z + 112.0),
                                         ("HBD", hbd_phi, hbd_r, hbd_body_z + 102.0)):
        fixed_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(radius, 0, fixed_z)
        moving_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(radius, 0, zc)
        b.add(b.arm_module, path, fixed_yoke, f"{label}-FIXED-YOKE", fixed_loc, "FIXED", "BOLTED_TO_FIXED_SECTOR")
        for end, base in (("FIXED", fixed_loc), ("MOVING", moving_loc)):
            b.add(b.arm_module, path, actuator_pin, f"{label}-PIN-{end}", base * g.translation_loc(0, -4.0, 0), "MOVING" if end == "MOVING" else "FIXED", "CLEVIS_PIN_WITH_E_RING")
            b.add(b.arm_module, path, actuator_clip, f"{label}-CLIP-{end}", base * g.translation_loc(0, 3.35, 0), "MOVING" if end == "MOVING" else "FIXED", "EXTERNAL_GROOVE")

    # Continuous routes live inside deliberately bored longerons and terminate at bulkhead unions.
    route_specs = [
        ("GAS-MAIN", 60.0, -25.0, 1.00, 0.65, "FULLFLOW-VALVE-001", "WP04-FULLFLOW-MANIFOLD"),
        ("PILOT-LINE", 60.0, 25.0, 0.75, 0.45, "FULLFLOW-VALVE-001", "WP04-LATCH-001"),
        ("BOWDEN-SHEATH", 180.0, -25.0, 0.80, 0.42, "WATER-TRIGGER-HSG-001", "WP04-LATCH-001"),
        ("BOWDEN-WIRE", 180.0, 25.0, 0.30, None, "WATER-TRIGGER-HSG-001", "WP04-LATCH-001"),
    ]
    for rid, center, delta, ro, ri, origin, dest in route_specs:
        phi = center + delta
        local_points = [(0.0, 0.0, 0.0), (0.0, 0.0, 790.0), (-2.2, 0.0, 810.0), (-2.2, 0.0, 895.0)]
        local_route = g.routed_round(local_points, ro, ri)
        route = b.define(f"DF8-R2-{rid}-001", "A", f"CONTINUOUS TERMINATED {rid.replace('-', ' ')}",
                         local_route,
                         "316 stainless steel" if ri is not None else "17-4PH stainless steel",
                         process="Seamless formed tube" if ri is not None else "Bowden wire",
                         notes="Exact supplier/fitting pressure rating remains provisional." if "BOWDEN" not in rid else "Exact cable nipple supplier unresolved.",
                         color_key="route" if "BOWDEN" not in rid else "black")
        route_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(26.2, 0.0, 850.0)
        oid = b.add(b.arm_module, path, route, f"ROUTE-{rid}-001", route_loc, "FLEXIBLE" if "BOWDEN" in rid else "FIXED",
                    "SUPPORTED_IN_BORED_LONGERON", "AXIAL SLIP FOR SERVICE" if "BOWDEN" in rid else "0")
        b.add_route_record(oid, origin, dest, "Two modeled bulkhead unions plus end nipples",
                           f"Ø2.90 mm jig-bored channels at z=885 and z=1638, phi={phi:.1f}",
                           f"Continuous longeron channel {center:.0f}° plus end strain relief", 35.0, 12.0,
                           "PROVISIONAL — supplier/rating unresolved", "GEOMETRICALLY TERMINATED; PROCUREMENT BLOCKED")
        union = b.define(f"DF8-R2-{rid}-UNION-001", "A", f"{rid.replace('-', ' ')} DOUBLE-FERRULE BULKHEAD UNION",
                         g.make_axial_bulkhead_union(ro * 2.1, ro * 2.0 + 0.10, ro * 4.0, 8.0),
                         "316 stainless steel", "BUY", "Qualified micro-fitting supplier TBD", "PROVISIONAL — BLOCKS FINAL RELEASE",
                         notes="Exact fitting, ferrule, seal, and rating unresolved.", color_key="stainless")
        for end, radius, z in (("FWD", 26.2, 885.0), ("AFT", 26.2, 1638.0), ("WP04", 24.0, 1655.0)):
            x, y = radial_xy(radius, phi)
            b.add(b.arm_module, path, union, f"UNION-{rid}-{end}", g.translation_loc(x, y, z), "FIXED", "BULKHEAD_UNION_WITH_FERRULES")


def build_aft(b: R2Builder) -> None:
    path = "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY"
    shell = b.define("DF8-R2-AFT-SHELL-001", "A", "AFT GRADE-9 SHELL WITH HARDPOINT AND HINGE APERTURES", aft_shell_with_openings(),
                     "Ti-3Al-2.5V Grade 9", process="Cold draw; laser cut controlled apertures", color_key="titanium")
    b.add(b.aft, path, shell, "AFT-SHELL-001", g.translation_loc(0, 0, 1635.0), "FIXED", "WELDED_TO_ROUTE_RING_AND_SERVICE_THROAT")
    route_ring = b.define("DF8-R2-AFT-ROUTE-RING-001", "A", "AFT STRUCTURAL RING WITH CONTROLLED ROUTE PASSAGES",
                          ring_with_axial_route_holes(8.0), "Ti-6Al-4V", process="Mill-turn and jig-bore", color_key="titanium")
    b.add(b.aft, path, route_ring, "AFT-ROUTE-RING-001", g.translation_loc(0, 0, 1638.0), "FIXED", "LASER_WELDED_RING_JOINT")
    aft_longeron = b.define("DF8-R2-AFT-LONGERON-001", "A", "AFT PRIMARY LOAD-PATH LONGERON", make_body_longeron(253.8),
                            "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, 1642.1)
        b.add(b.aft, path, aft_longeron, f"AFT-LONGERON-{idx}", loc, "FIXED", "WELDED_BETWEEN_STRUCTURAL_RINGS")

    bulkhead = b.define("WP04-RB-001-R2", "A", "SPRING REACTION BULKHEAD WITH GUIDE-RAIL BORES", g.make_reaction_bulkhead_local(),
                        "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    b.add(b.aft, path, bulkhead, "WP04-REACTION-BULKHEAD", g.translation_loc(0, 0, 1655.0), "FIXED", "PILOTED_RING_AND_SIX_M3_SCREWS")
    rail = b.define("WP04-GUIDE-RAIL-001-R2", "A", "FOLLOWER ANTI-ROTATION GUIDE RAIL", g.box_center(3.0, 5.0, 190.0, 0, 0, 95.0),
                    "PEEK", process="Machine and slot", color_key="peek")
    for idx, phi in enumerate((0.0, 120.0, 240.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(19.6, 0, 1660.0)
        b.add(b.aft, path, rail, f"WP04-GUIDE-RAIL-{idx}", loc, "FIXED", "M3_BOLTED_TO_REACTION_AND_STOP_RINGS")

    follower = b.define("WP04-FOL-001-R2", "A", "CAPTIVE PEEK FOLLOWER WITH THREE GUIDE SLOTS", g.make_follower_plate_local(),
                        "PEEK", process="5-axis machine", color_key="peek")
    follower_z = 1830.0 if b.deployed else 1745.0
    b.add(b.aft, path, follower, "WP04-FOLLOWER-001", g.translation_loc(0, 0, follower_z), "MOVING", "THREE_RAIL_GUIDED_TRANSLATION", "1 AXIAL TRANSLATION 85 MM")

    spring_len = g.WP04_SPRING_DEPLOYED if b.deployed else g.WP04_SPRING_STOWED
    wp04_spring = b.define("VD-244", "CATALOG", "GUTEKUNST VD-244 GUIDED EJECTOR SPRING",
                           g.make_compression_spring_local(g.WP04_SPRING_OD, g.WP04_SPRING_WIRE, spring_len, 17.4),
                           "1.4310 stainless spring steel", "BUY", "Gutekunst Federn", "DRAWING_DERIVED",
                           source_url="https://www.federnshop.com/en/products/compression_springs/vd-244.html",
                           purchase_url="https://www.federnshop.com/en/products/compression_springs/vd-244.html",
                           notes="Installed-force and pack-test acceptance remain open.", color_key="spring")
    b.add(b.aft, path, wp04_spring, "WP04-EJECTOR-SPRING", g.translation_loc(0, 0, 1660.0), "FLEXIBLE", "OVERLAPPING_GUIDE_SLEEVES", "AXIAL COMPRESSION")
    sleeve_fixed = b.define("WP04-FIXED-GUIDE-SLEEVE-R2", "A", "FIXED OVERLAPPING SPRING GUIDE SLEEVE", g.tube_z(11.65, 10.9, 100.0),
                            "PEEK", process="Turn", color_key="peek")
    sleeve_moving = b.define("WP04-MOVING-GUIDE-SLEEVE-R2", "A", "FOLLOWER OVERLAPPING SPRING GUIDE SLEEVE", g.tube_z(10.75, 10.0, 100.0),
                             "PEEK", process="Turn", color_key="peek")
    b.add(b.aft, path, sleeve_fixed, "WP04-FIXED-SLEEVE", g.translation_loc(0, 0, 1658.0), "FIXED", "SHOULDER_AND_THREE_M3_SCREWS")
    b.add(b.aft, path, sleeve_moving, "WP04-MOVING-SLEEVE", g.translation_loc(0, 0, follower_z - 98.0), "MOVING", "PILOTED_IN_FOLLOWER")

    latch_shape = g.box_center(5.0, 6.0, 16.0, 2.5, 0.0, 0.0)
    latch_shape = latch_shape.cut(cq.Solid.makeCylinder(2.18, 5.6, cq.Vector(-0.3, 0, 0), cq.Vector(1, 0, 0)))
    latch = b.define("WP04-LATCH-HOUSING-R2", "A", "RADIAL FOLLOWER LATCH HOUSING WITH REAMED SEAR GUIDE", latch_shape,
                     "17-4PH stainless steel", process="5-axis mill and ream", color_key="steel")
    sear_shape = cq.Solid.makeCylinder(2.0, 8.0, cq.Vector(-3.0, 0, 0), cq.Vector(1, 0, 0))
    sear_shape = sear_shape.fuse(cq.Solid.makeCylinder(3.0, 1.0, cq.Vector(5.0, 0, 0), cq.Vector(1, 0, 0)))
    groove_outer = cq.Solid.makeCylinder(2.25, 0.45, cq.Vector(4.0, 0, 0), cq.Vector(1, 0, 0))
    groove_core = cq.Solid.makeCylinder(1.75, 0.65, cq.Vector(3.9, 0, 0), cq.Vector(1, 0, 0))
    sear_shape = sear_shape.cut(groove_outer.cut(groove_core))
    sear = b.define("WP04-LATCH-SEAR-R2", "A", "CAPTIVE RADIAL FOLLOWER SEAR PLUNGER WITH RETAINING RING", sear_shape,
                    "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    sear_clip = b.define("WP04-LATCH-SEAR-E-RING-R2", "A", "4 MM SEAR PIN EXTERNAL RETAINING RING",
                         g.make_external_retaining_ring(4.0, 0.45),
                         "1.4310 stainless spring steel", process="Stamped spring ring", color_key="spring")
    latch_loc = g.rotation_loc((0, 0, 1), 270.0) * g.translation_loc(23.3, 0, 1745.0)
    b.add(b.aft, path, latch, "WP04-LATCH-001", latch_loc, "FIXED", "M3_BOLTED_TO_GUIDE_RAIL")
    sear_shift = 3.2 if b.deployed else 0.0
    sear_loc = latch_loc * g.translation_loc(sear_shift, 0, 0)
    b.add(b.aft, path, sear, "WP04-SEAR-001", sear_loc, "MOVING", "GUIDED_SEAR_WITH_E_RING", "1 TRANSLATION")
    b.add(b.aft, path, sear_clip, "WP04-SEAR-CLIP-001",
          latch_loc * g.translation_loc(sear_shift + 4.225, 0, 0) * g.rotation_loc((0, 0, 1), 90.0),
          "MOVING", "EXTERNAL_GROOVE_RETAINER", "1 TRANSLATION WITH SEAR")

    hardpoint = b.define("WP04-RHP-001-R2", "A", "INTEGRAL STRUCTURAL RING AND RECOVERY HARDPOINT LUG",
                         g.make_structural_ring_with_hardpoint_local(), "Ti-6Al-4V", process="5-axis mill from forged ring",
                         color_key="titanium")
    b.add(b.aft, path, hardpoint, "BODY-HARDPOINT-001", g.translation_loc(0, 0, 1900.0), "FIXED", "WELDED_TO_THREE_LONGERONS_AND_AFT_SHELL")

    throat = b.define("WP05-SERVICE-THROAT-R2", "A", "AFT SERVICE THROAT WITH CONTROLLED DETENT BORES", service_throat_shape(),
                      "Ti-6Al-4V", process="Mill-turn; machine bayonet/hinge features", color_key="titanium")
    b.add(b.aft, path, throat, "WP05-SERVICE-THROAT", g.translation_loc(0, 0, 1928.0), "FIXED", "SIX_M3_SCREWS_AND_PILOT")
    door = b.define("WP05-DOOR-R2", "A", "CAPTIVE LOW-FORCE AFT DOOR WITH HINGE AND LANYARD EYE", g.make_service_door_local(),
                    "Ti-6Al-4V", process="5-axis mill and face grind", color_key="titanium")
    b.add(b.aft, path, door, "WP05-DOOR-001", g.door_occurrence_loc(b.deployed), "MOVING", "REVOLUTE_HINGE", "1 ROTATION 0-90 DEG")
    hinge_pin = b.define("WP05-HINGE-PIN-R2", "A", "DOOR HINGE PIN WITH EXTERNAL RETAINER", g.make_clevis_pin(3.0, 12.0, 5.0, 1.0),
                         "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    hinge_loc = g.translation_loc(28.0, -6.0, 2028.0)
    b.add(b.aft, path, hinge_pin, "WP05-HINGE-PIN", hinge_loc, "FIXED", "HINGE_PIN_WITH_E_RING")
    detent = b.define("GN-615.3-M3-KN-PFB", "CATALOG", "JW WINCO M3 STAINLESS BALL PLUNGER", radial_detent_shape(),
                      "316 stainless steel", "BUY", "JW Winco / Ganter", "DRAWING_DERIVED",
                      source_url="https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
                      purchase_url="https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
                      notes="Marine endurance and authentic CAD remain open.", color_key="stainless")
    for idx, phi in enumerate((45.0, 135.0, 225.0, 315.0), 1):
        x, y = radial_xy(22.9, phi)
        loc = g.translation_loc(x, y, 2026.0) * g.rotation_loc((0, 0, 1), phi)
        b.add(b.aft, path, detent, f"DOOR-DETENT-{idx}", loc, "FIXED", "M3_THREADED_AND_THREADLOCKED")

    # Flexible buoy articles preserve stable IDs while changing exact state geometry.
    # Preserve the verified terminal-to-harness alignment while bringing the
    # deployed rigid recovery terminal inside the 2032 mm product limit.  The
    # buoy/harness moves with the terminal by the same 30.5 mm so no flexible
    # connection is stretched or cosmetically detached.
    buoy_center_z = 2274.5
    for gi in range(8):
        shape = g.make_buoy_gore_deployed_local(gi) if b.deployed else g.make_buoy_gore_stowed_local(gi)
        gore = b.define(f"DF8-R2-BUOY-GORE-{gi+1:02d}", "A", f"60 L BUOY GORE {gi+1} OF 8", shape,
                        "TPU-coated nylon", process="Waterjet cut; RF weld 12 mm seams", color_key="softgood")
        loc = g.translation_loc(0, 0, buoy_center_z) if b.deployed else g.translation_loc(0, 0, 1845.0)
        b.add(b.aft, path, gore, f"BUOY-GORE-{gi+1:02d}", loc, "SOFTGOOD", "RF_WELDED_GORE_SEAMS", "FLEXIBLE MEMBRANE")

    for hi in (1, 2):
        if b.deployed:
            band_shape = g.make_harness_band_local() if hi == 1 else g.make_harness_band_overpass_local()
        else:
            band_shape = g.make_harness_band_stowed_local(hi)
        harness = b.define(f"DF8-R2-HARNESS-BAND-{hi}", "A", f"X-6292 STRUCTURAL HARNESS CLOSED BAND {hi}", band_shape,
                           "UHMWPE webbing", "MAKE", "Sturges X-6292 raw webbing / STINGRAY finished assembly",
                           "PROVISIONAL — BLOCKS FINAL RELEASE", process="Cut, fold, stitch and proof load",
                           notes="Finished stitching, MBS and proof acceptance remain open.", color_key="rope")
        if b.deployed:
            # The source torus lies in the XY plane.  Rotate it about X or Y
            # to form the two orthogonal XZ/YZ vertical great circles.  The
            # second definition includes engineered pole overpasses, so the
            # two web layers do not interpenetrate.
            band_rotation = g.rotation_loc((1, 0, 0), 90.0) if hi == 1 else g.rotation_loc((0, 1, 0), 90.0)
            loc = g.translation_loc(0, 0, buoy_center_z) * band_rotation
        else:
            loc = g.translation_loc(0, 0, 1845.0)
        b.add(b.aft, path, harness, f"HARNESS-BAND-{hi}", loc, "FLEXIBLE", "STITCHED_CLOSED_LOOP", "FLEXIBLE")

    terminal = b.define("WP04-HST-001-R2", "A", "HARNESS STRUCTURAL TERMINAL WITH FOUR WEB SLOTS AND DOUBLE-SHEAR CLEVIS", g.make_harness_terminal_local(),
                        "17-4PH stainless steel", process="5-axis mill and proof test", color_key="steel")
    terminal_z = 2018.0 if b.deployed else 1916.0
    terminal_loc = g.translation_loc(0, 0, terminal_z)
    b.add(b.aft, path, terminal, "HARNESS-TERMINAL-001", terminal_loc, "MOVING", "FOUR_STITCHED_WEB_LOOPS")

    # Four occurrence-specific harness legs bridge the great-circle bands to
    # the four terminal slots.  Flexible state geometry changes, but the part
    # and occurrence identities remain stable.
    leg_specs = (
        ("XP", "HARNESS-BAND-1", (6.0, 0.0, 12.0), (28.0, 0.0, 15.8)),
        ("XN", "HARNESS-BAND-1", (-6.0, 0.0, 12.0), (-28.0, 0.0, 15.8)),
        ("YP", "HARNESS-BAND-2", (0.0, 6.0, 12.0), (0.0, 28.0, 15.8)),
        ("YN", "HARNESS-BAND-2", (0.0, -6.0, 12.0), (0.0, -28.0, 15.8)),
    )
    for leg_name, _band_id, terminal_point, deployed_point in leg_specs:
        packed_point = (
            math.copysign(14.0, deployed_point[0]) if deployed_point[0] else 0.0,
            math.copysign(14.0, deployed_point[1]) if deployed_point[1] else 0.0,
            11.0,
        )
        far_point = deployed_point if b.deployed else packed_point
        leg_shape = g.strap_between(terminal_point, far_point, 12.0, 1.1)
        leg = b.define(f"DF8-R2-HARNESS-LEG-{leg_name}", "A", f"X-6292 TERMINAL HARNESS LEG {leg_name}", leg_shape,
                       "UHMWPE webbing", "MAKE", "Sturges X-6292 raw webbing / STINGRAY finished assembly",
                       "PROVISIONAL — BLOCKS FINAL RELEASE", process="Fold, stitch and proof load",
                       notes="Finished stitch pattern and proof basis remain open.", color_key="rope")
        b.add(b.aft, path, leg, f"HARNESS-LEG-{leg_name}", terminal_loc, "FLEXIBLE", "STITCHED_BAND_TO_TERMINAL_SLOT", "FLEXIBLE")
    thimble = b.define("DF8-R2-TETHER-THIMBLE-001", "A", "AMSTEEL EYE-SPLICE THIMBLE", g.make_thimble_local(),
                       "316 stainless steel", process="Stamp and form", color_key="stainless")
    body_thimble_loc = g.translation_loc(24.0, 0, 1900.0)
    harness_thimble_loc = terminal_loc
    b.add(b.aft, path, thimble, "TETHER-THIMBLE-BODY", body_thimble_loc, "MOVING", "PINNED_TO_BODY_HARDPOINT")
    b.add(b.aft, path, thimble, "TETHER-THIMBLE-HARNESS", harness_thimble_loc, "MOVING", "PINNED_TO_HARNESS_TERMINAL")

    tether_shape = g.make_structural_tether_local(-24.0, terminal_z - 1900.0, b.deployed)
    tether = b.define("AMSTEEL-BLUE-872-7-64-R2", "A", "STRUCTURAL RECOVERY TETHER WITH TWO BURIED EYE SPLICES", tether_shape,
                      "HMPE rope", "MAKE", "Samson Rope Technologies raw line / STINGRAY finished splices",
                      "PROVISIONAL — BLOCKS FINAL RELEASE",
                      source_url="https://www.samsonrope.com/mooring/amsteel--blue",
                      purchase_url="https://www.samsonrope.com/resources/find-a-distributor",
                      process="Measure, cut, buried-eye splice, chafe sleeve, proof load",
                      notes="Finished length, splice process and proof acceptance remain open.", color_key="rope")
    b.add(b.aft, path, tether, "RECOVERY-TETHER-001", body_thimble_loc, "FLEXIBLE", "TWO_EYE_SPLICES_ON_THIMBLES", "FLEXIBLE")

    recovery_pin = b.define("DF8-R2-RECOVERY-PIN-006", "A", "6 MM CAPTIVE RECOVERY TERMINAL PIN WITH RETAINER GROOVE",
                            g.make_clevis_pin(6.0, 9.5, 9.0, 1.5), "17-4PH stainless steel",
                            process="Swiss turn; H900; grind", color_key="steel")
    recovery_clip = b.define("DF8-R2-RECOVERY-E-RING-006", "A", "6 MM RECOVERY PIN EXTERNAL RETAINER",
                             g.make_external_retaining_ring(6.0, 0.5), "1.4310 stainless spring steel",
                             process="Stamped spring ring", color_key="spring")
    for suffix, base_loc in (("BODY", body_thimble_loc), ("HARNESS", harness_thimble_loc)):
        pin_loc = base_loc * g.translation_loc(0, -4.75, 0)
        b.add(b.aft, path, recovery_pin, f"RECOVERY-PIN-{suffix}", pin_loc, "MOVING", "CLEVIS_PIN_WITH_E_RING")
        b.add(b.aft, path, recovery_clip, f"RECOVERY-PIN-CLIP-{suffix}", base_loc * g.translation_loc(0, 4.0, 0), "MOVING", "EXTERNAL_GROOVE")
    b.add_route_record("RECOVERY-TETHER-001", "BODY-HARDPOINT-001", "HARNESS-TERMINAL-001",
                       "Modeled body and harness thimbles with buried-eye splices", "Aft service throat, no wall crossing",
                       "Packed anti-chafe sleeve / deployed free span", 25.0, 50.0, "Structural proof basis provisional",
                       "GEOMETRICALLY TERMINATED; STRUCTURAL QUALIFICATION BLOCKED")

    # Door lanyard remains captive in both states.
    door_eye_vertex = g.moved(cq.Vertex.makeVertex(-15.0, 0.0, 0.0), g.door_occurrence_loc(b.deployed))
    door_eye = door_eye_vertex.toTuple()
    lanyard_shape = g.routed_round([(18.0, 0, 2005.0), door_eye], 0.8)
    lanyard = b.define("WP05-DOOR-LANYARD-R2", "A", "CAPTIVE DOOR LANYARD WITH SWAGED EYES", lanyard_shape,
                       "HMPE rope", process="Swage two thimbled eyes", color_key="rope")
    b.add(b.aft, path, lanyard, "WP05-DOOR-LANYARD", g.identity_loc(), "FLEXIBLE", "TWO_SWAGED_EYES", "FLEXIBLE",
          notes="Identity placement is intentional because the routed lanyard definition uses the product datum frame shared by its two moving endpoints.")


def add_primary_connections(b: R2Builder) -> None:
    """Occurrence-specific mechanical graph; no blanket subsystem entries."""
    def connect_present(cid: str, occ: str, mate: str, own_feature: str, mate_feature: str,
                        connection_type: str, permitted_dof: str, retaining_hardware: str,
                        axial: str, lateral: str, anti_rotation: str,
                        upstream: str, downstream: str, service: str, evidence: str) -> None:
        """Add one enumerated, non-self connection when both occurrences exist."""
        if occ == mate:
            raise ValueError(f"Self-connection is not valid attachment evidence: {cid} -> {occ}")
        if occ not in b.global_shapes or mate not in b.global_shapes:
            return
        b.connect(cid, occ, mate, own_feature, mate_feature, connection_type, permitted_dof,
                  retaining_hardware, axial, lateral, anti_rotation, upstream, downstream,
                  service, evidence)

    # Primary forward spine.  The arm/aft ring interfaces are enumerated below
    # with the individual longeron end joints instead of a fictitious direct
    # AFT-ROUTE-RING-001 to FWD-RING-02 connection.
    chain = [
        ("BALLAST-001", "NOSE-001", "BALLAST_FORWARD_SOCKET", "NOSE_AFT_TENON"),
        ("FWD-RING-01", "BALLAST-001", "RING_ID_SHOULDER", "BALLAST_AFT_PILOT"),
        ("FWD-SHELL-001", "FWD-RING-01", "SHELL_FORWARD_WELD_LAND", "RING_OUTER_WELD_LAND"),
        ("FWD-RING-02", "FWD-SHELL-001", "RING_FORWARD_WELD_LAND", "SHELL_AFT_WELD_LAND"),
    ]
    for idx, (occ, mate, ownf, matef) in enumerate(chain, 1):
        connect_present(
            f"STRUCT-FWD-{idx:03d}", occ, mate, ownf, matef,
            "STRUCTURAL_WELD_OR_PILOT", "0", "Integral weld/pilot defined at this pair",
            "Axial shoulder or continuous weld", "Circumferential pilot/weld",
            "Clocked pilot or keyed spine feature", mate, occ,
            "Cut the identified weld or remove the identified controlled fasteners",
            f"Modeled forward-spine interface {occ}:{ownf} to {mate}:{matef}",
        )

    # Each primary longeron has two independently identified end joints.  This
    # makes the load path FWD-RING-01 -> FWD longerons -> FWD-RING-02 -> ARM
    # longerons -> AFT-ROUTE-RING -> AFT longerons -> BODY-HARDPOINT explicit.
    longeron_spans = (
        ("FWD-LONGERON", "FWD-RING-01", "FWD-RING-02"),
        ("ARM-LONGERON", "FWD-RING-02", "AFT-ROUTE-RING-001"),
        ("AFT-LONGERON", "AFT-ROUTE-RING-001", "BODY-HARDPOINT-001"),
    )
    for prefix, forward_support, aft_support in longeron_spans:
        for idx in range(1, 4):
            occ = f"{prefix}-{idx}"
            for end, mate in (("FWD", forward_support), ("AFT", aft_support)):
                ownf = f"{end}_END_TONGUE_{idx}"
                matef = f"{prefix}_SEAT_{idx}_{end}"
                connect_present(
                    f"LONG-{prefix}-{idx}-{end}", occ, mate, ownf, matef,
                    "WELDED_PRIMARY_LONGERON_END", "0",
                    f"Continuous structural fillet weld at {occ} {end.lower()} end",
                    f"{end.title()} end shoulder and weld throat",
                    f"Seat sidewalls for longeron clock position {idx}",
                    f"Clocked {matef}", mate, occ,
                    f"Cut and inspect the {occ} {end.lower()}-end weld during depot overhaul",
                    f"Enumerated {occ} {end.lower()} interface: {ownf} to {mate}:{matef}",
                )

    aft_structure = (
        ("AFT-SHELL-ROUTE-RING", "AFT-SHELL-001", "AFT-ROUTE-RING-001",
         "SHELL_FORWARD_CIRCUMFERENTIAL_WELD_LAND", "RING_OUTER_CIRCUMFERENTIAL_WELD_LAND",
         "LASER_WELDED_RING_JOINT", "Continuous circumferential laser weld"),
        ("AFT-SHELL-REACTION-BULKHEAD", "WP04-REACTION-BULKHEAD", "AFT-SHELL-001",
         "BULKHEAD_OUTER_PILOT_AND_6X_M3_PATTERN", "SHELL_REACTION_BULKHEAD_PILOT_AND_INSERTS",
         "PILOTED_SIX_FASTENER_BULKHEAD", "Six M3 fasteners with locking feature"),
        ("AFT-SHELL-HARDPOINT", "BODY-HARDPOINT-001", "AFT-SHELL-001",
         "HARDPOINT_RING_OUTER_WELD_LAND", "SHELL_HARDPOINT_APERTURE_WELD_LAND",
         "STRUCTURAL_RING_WELD", "Continuous qualified structural weld"),
        ("AFT-SHELL-SERVICE-THROAT", "WP05-SERVICE-THROAT", "AFT-SHELL-001",
         "THROAT_FORWARD_PILOT_AND_6X_M3_PATTERN", "SHELL_AFT_PILOT_AND_INSERTS",
         "PILOTED_SIX_FASTENER_SERVICE_JOINT", "Six M3 fasteners with locking feature"),
        ("HARDPOINT-SERVICE-THROAT", "WP05-SERVICE-THROAT", "BODY-HARDPOINT-001",
         "THROAT_FORWARD_STRUCTURAL_SHOULDER", "HARDPOINT_RING_AFT_STRUCTURAL_SHOULDER",
         "PILOTED_STRUCTURAL_SHOULDER", "Controlled pilot plus the service-throat fastener pattern"),
    )
    for cid, occ, mate, ownf, matef, ctype, hardware in aft_structure:
        connect_present(
            cid, occ, mate, ownf, matef, ctype, "0", hardware,
            "Piloted shoulder and/or continuous circumferential joint",
            "Concentric pilot or weld land", "Clocked fastener pattern or continuous ring",
            mate, occ, "Remove the enumerated fasteners or cut the enumerated weld",
            f"Modeled aft-structure interface {occ}:{ownf} to {mate}:{matef}",
        )

    for idx in range(1, 4):
        b.connect(f"PIVOT-{idx}", f"ARM-{idx}", f"PIVOT-CARRIER-{idx}", "ARM_8MM_REAMED_BORE", "CARRIER_COAXIAL_EARS",
                  "DOUBLE_SHEAR_REVOLUTE", "1 ROTATION", f"PIVOT-PIN-{idx}; PIVOT-CLIP-{idx}; two bushings; two washers",
                  "Pin head and external spiral ring", "Carrier ears and thrust washers", "Shouldered pin head",
                  f"ARM-{idx}", f"PIVOT-CARRIER-{idx}", "Remove spiral ring and withdraw pin", "Coaxiality/clearance/retention check")
        for end in ("BELL", "CROSSHEAD"):
            for li in (1, 2):
                mate = f"ARM-{idx}" if end == "BELL" else "CROSSHEAD-001"
                b.connect(f"LINK-{idx}-{li}-{end}", f"LINK-{idx}-{li}", mate,
                          f"LINK_{end}_REAMED_BORE", f"{end}_DOUBLE_SHEAR_CLEVIS",
                          "REVOLUTE_PIN", "1 ROTATION", f"LINK-PIN-{idx}-{end}; LINK-CLIP-{idx}-{end}",
                          "Pin head and E-ring", "Two clevis cheeks with 0.20 mm face gap", "Headed pin shoulder",
                          "CROSSHEAD-001", f"ARM-{idx}", "Remove E-ring and withdraw pin", "Pin/bore common-volume and coaxiality check")

    # Recovery terminals are integrated double-shear yoke features, not
    # stand-alone floating yoke occurrences.  Enumerate the thimble, pin, and
    # external retainer at each end so the physical load path is auditable.
    recovery_terminals = (
        ("BODY", "TETHER-THIMBLE-BODY", "BODY-HARDPOINT-001",
         "INTEGRAL_DOUBLE_SHEAR_RECOVERY_YOKE", "BODY-HARDPOINT-001", "RECOVERY-TETHER-001"),
        ("HARNESS", "TETHER-THIMBLE-HARNESS", "HARNESS-TERMINAL-001",
         "INTEGRAL_DOUBLE_SHEAR_TERMINAL_YOKE", "RECOVERY-TETHER-001", "HARNESS-TERMINAL-001"),
    )
    for suffix, thimble, yoke, yoke_feature, upstream, downstream in recovery_terminals:
        pin = f"RECOVERY-PIN-{suffix}"
        clip = f"RECOVERY-PIN-CLIP-{suffix}"
        connect_present(
            f"RECOVERY-{suffix}-THIMBLE-YOKE", thimble, yoke,
            "THIMBLE_6MM_EYE", f"{yoke_feature}_6MM_COAXIAL_BORES",
            "DOUBLE_SHEAR_PINNED_STRUCTURAL_TERMINAL", "1 ROTATION",
            f"{pin} headed clevis pin retained by {clip}",
            "Pin head at one outer yoke ear and external retainer at the opposite ear",
            "Two yoke ears capture the thimble with controlled side clearance",
            "Coaxial pin through both yoke ears and thimble eye", upstream, downstream,
            f"Remove {clip}, withdraw {pin}, and retain the thimble",
            f"Modeled recovery joint {thimble}:THIMBLE_6MM_EYE to {yoke}:{yoke_feature}_6MM_COAXIAL_BORES",
        )
        connect_present(
            f"RECOVERY-{suffix}-PIN-YOKE", pin, yoke,
            "PIN_6MM_GROUND_SHANK", f"{yoke_feature}_6MM_COAXIAL_BORES",
            "CAPTIVE_DOUBLE_SHEAR_CLEVIS_PIN", "1 ROTATION",
            f"Integral pin head plus {clip} in the external groove",
            "Integral pin head and occurrence-specific external retainer",
            "Ground shank supported by both yoke ears", "Pin head prevents axial reversal",
            upstream, downstream, f"Remove {clip} and withdraw {pin}",
            f"Modeled {pin} shank through {yoke} integral yoke bores",
        )
        connect_present(
            f"RECOVERY-{suffix}-PIN-THIMBLE", pin, thimble,
            "PIN_6MM_GROUND_SHANK", "THIMBLE_6MM_EYE",
            "PIN_THROUGH_THIMBLE_EYE", "1 ROTATION",
            f"{pin} head and {clip}", "Head/retainer react terminal axial escape",
            "Ground pin shank reacts thimble bearing load", "Yoke ears prevent thimble roll-off",
            upstream, downstream, f"Remove {clip} and withdraw {pin}",
            f"Modeled {pin}:PIN_6MM_GROUND_SHANK through {thimble}:THIMBLE_6MM_EYE",
        )
        connect_present(
            f"RECOVERY-{suffix}-CLIP-PIN", clip, pin,
            "EXTERNAL_RETAINING_RING", "MACHINED_EXTERNAL_RETAINER_GROOVE",
            "EXTERNAL_GROOVE_RETAINER", "0", "Spring retaining ring seated in machined pin groove",
            "Retaining-ring shoulder blocks pin withdrawal", "Groove sidewalls retain the ring",
            "Split spring ring closes around the pin groove", upstream, downstream,
            f"Expand and remove {clip} with retaining-ring pliers",
            f"Modeled {clip}:EXTERNAL_RETAINING_RING seated on {pin}:MACHINED_EXTERNAL_RETAINER_GROOVE",
        )
    connect_present(
        "TETHER-BODY-EYE", "RECOVERY-TETHER-001", "TETHER-THIMBLE-BODY",
        "BURIED_EYE_SPLICE_BODY", "FORMED_ROPE_GROOVE", "CLOSED_SPLICE_ON_THIMBLE", "FLEXIBLE",
        "Buried eye splice", "Closed eye", "Thimble groove", "Eye splice",
        "BODY-HARDPOINT-001", "RECOVERY-TETHER-001", "Cut and replace proof-loaded tether",
        "Modeled body-end rope eye closed around TETHER-THIMBLE-BODY formed groove",
    )
    connect_present(
        "TETHER-HARNESS-EYE", "RECOVERY-TETHER-001", "TETHER-THIMBLE-HARNESS",
        "BURIED_EYE_SPLICE_HARNESS", "FORMED_ROPE_GROOVE", "CLOSED_SPLICE_ON_THIMBLE", "FLEXIBLE",
        "Buried eye splice", "Closed eye", "Thimble groove", "Eye splice",
        "RECOVERY-TETHER-001", "HARNESS-TERMINAL-001", "Cut and replace proof-loaded tether",
        "Modeled harness-end rope eye closed around TETHER-THIMBLE-HARNESS formed groove",
    )
    for leg_name, band_id in (("XP", "HARNESS-BAND-1"), ("XN", "HARNESS-BAND-1"),
                              ("YP", "HARNESS-BAND-2"), ("YN", "HARNESS-BAND-2")):
        b.connect(f"HARNESS-LEG-{leg_name}-TERMINAL", f"HARNESS-LEG-{leg_name}", "HARNESS-TERMINAL-001",
                  "STITCHED_TERMINAL_LOOP", f"TERMINAL_SLOT_{leg_name}", "STITCHED_LOOP", "FLEXIBLE",
                  "Qualified stitch pattern and keeper", "Closed sewn loop", "Terminal slot shoulders", "Opposed web legs",
                  "HARNESS-TERMINAL-001", f"HARNESS-LEG-{leg_name}", "Cut and replace stitched loop", "Connectivity and proof check")
        b.connect(f"HARNESS-LEG-{leg_name}-BAND", f"HARNESS-LEG-{leg_name}", band_id,
                  "STITCHED_BAND_END", f"CLOSED_BAND_{leg_name}_PATCH", "STRUCTURAL_STITCHED_LAP", "FLEXIBLE",
                  "Qualified box-X stitch pattern", "Closed sewn lap", "Full-width web overlap", "Opposed leg pair",
                  band_id, f"HARNESS-LEG-{leg_name}", "Cut and replace stitched lap", "Connectivity and proof check")

    # Complete the graph only with enumerated joint families and named support
    # occurrences.  There is deliberately no parent-subsystem fallback: an
    # unclassified occurrence must remain visible for review instead of being
    # assigned blanket attachment evidence.
    known = {
        endpoint
        for connection in b.connections
        for endpoint in (connection.occurrence_id, connection.mate_occurrence_id)
    }
    explicit_supports = {
        "CARTRIDGE-CARRIER-AFT": (
            "COLLECTION-MANIFOLD-001", "PILOTED_BOLTED_CARRIER",
            "AFT_CARRIER_4X_M3_PATTERN", "MANIFOLD_FORWARD_4X_M3_PATTERN",
            "Four M3 socket-head screws with locking compound",
        ),
        "COLLECTION-MANIFOLD-001": (
            "CARTRIDGE-CARRIER-AFT", "PILOTED_BOLTED_MANIFOLD",
            "MANIFOLD_FORWARD_PILOT_AND_4X_M3", "AFT_CARRIER_PILOT_AND_4X_M3",
            "Four M3 socket-head screws with locking compound",
        ),
        "WATER-TRIGGER-HSG-001": (
            "CARTRIDGE-CARRIER-AFT", "BOLTED_TRIGGER_CARRIER",
            "TRIGGER_HOUSING_MOUNTING_FLANGE", "CARRIER_TRIGGER_MOUNT_PATTERN",
            "Three M3 screws and a piloted housing shoulder",
        ),
        "WATER-BOBBIN-001": (
            "WATER-TRIGGER-HSG-001", "CAPTIVE_CONSUMABLE_CUP",
            "BOBBIN_OUTER_CYLINDER", "TRIGGER_CAPTIVE_CUP",
            "Trigger cup shoulder and service cap",
        ),
        "WATER-INLET-001": (
            "FWD-SHELL-001", "RADIAL_GLAND_PENETRATION",
            "INLET_INNER_AND_OUTER_GLAND_FLANGES", "SHELL_CONTROLLED_WATER_PORT",
            "Brazed gland flanges and captured screen",
        ),
        "FULLFLOW-VALVE-001": (
            "FWD-RING-02", "GUIDED_FULLFLOW_SPOOL",
            "VALVE_GUIDE_PILOT", "RING_VALVE_GUIDE_BORE",
            "Retaining shoulder and service circlip",
        ),
        "CROSSHEAD-GUIDE-001": (
            "FWD-RING-02", "DOUBLE_SUPPORTED_GUIDE_SHAFT",
            "GUIDE_FORWARD_SUPPORT_TENON", "RING_GUIDE_SUPPORT_BORE",
            "Threaded guide shoulder with mechanical lock",
        ),
        "BACKUP-SPRING-001": (
            "BACKUP-SPRING-FIXED-SEAT", "CAPTURED_GUIDED_COMPRESSION_SPRING",
            "SPRING_FIXED_END_COIL", "FIXED_SEAT_ANNULAR_POCKET",
            "Closed end coil captured by annular seat and guide",
        ),
        "BACKUP-SPRING-FIXED-SEAT": (
            "BACKUP-SPRING-GUIDE", "THREADED_FIXED_SPRING_SEAT",
            "FIXED_SEAT_THREADED_BORE", "SPRING_GUIDE_THREADED_END",
            "Threaded seat with prevailing-torque lock",
        ),
        "BACKUP-SPRING-MOVING-SEAT": (
            "CROSSHEAD-001", "BOLTED_MOVING_SPRING_SEAT",
            "MOVING_SEAT_PILOT_AND_SCREW", "CROSSHEAD_SPOKE_PILOT_AND_THREAD",
            "Piloted M3 screw with locking compound",
        ),
        "BACKUP-SPRING-GUIDE": (
            "FIXED-SECTOR-3", "DOUBLE_SUPPORTED_SPRING_GUIDE",
            "GUIDE_SUPPORT_TABS", "FIXED_SECTOR_GUIDE_SUPPORTS",
            "Two piloted M3 support screws",
        ),
        "GS19-BODY-001": (
            "GS19-FIXED-YOKE", "PINNED_ACTUATOR_BODY_END",
            "GS19_B8_END_EYE", "FIXED_YOKE_COAXIAL_EARS",
            "GS19-PIN-FIXED and GS19-CLIP-FIXED",
        ),
        "GS19-ROD-001": (
            "CROSSHEAD-001", "PINNED_TELESCOPING_ROD_END",
            "GS19_ROD_B8_END_EYE", "CROSSHEAD_GS19_CLEVIS",
            "GS19-PIN-MOVING and GS19-CLIP-MOVING",
        ),
        "HBD-BODY-001": (
            "HBD-FIXED-YOKE", "PINNED_DAMPER_BODY_END",
            "HBD_AA_BODY_END_EYE", "FIXED_YOKE_COAXIAL_EARS",
            "HBD-PIN-FIXED and HBD-CLIP-FIXED",
        ),
        "HBD-ROD-001": (
            "CROSSHEAD-001", "PINNED_DAMPER_ROD_END",
            "HBD_ROD_END_EYE", "CROSSHEAD_HBD_CLEVIS",
            "HBD-PIN-MOVING and HBD-CLIP-MOVING",
        ),
        "GS19-FIXED-YOKE": (
            "FIXED-SECTOR-1", "BOLTED_ACTUATOR_YOKE",
            "YOKE_PILOT_AND_2X_M3_PATTERN", "SECTOR_GS19_YOKE_DATUM",
            "Two M3 screws, two dowels, and locking compound",
        ),
        "HBD-FIXED-YOKE": (
            "FIXED-SECTOR-2", "BOLTED_DAMPER_YOKE",
            "YOKE_PILOT_AND_2X_M3_PATTERN", "SECTOR_HBD_YOKE_DATUM",
            "Two M3 screws, two dowels, and locking compound",
        ),
    }
    for occ in b.occurrences:
        if occ.occurrence_id in known:
            continue
        mate = ""
        ctype = ""
        ownf = ""
        matef = ""
        hardware = ""
        if occ.occurrence_id.startswith("BUOY-GORE"):
            mate = "HARNESS-BAND-1"
            ctype = "RF_WELDED_SEAM_AND_HARNESS_CAPTURE"
            ownf, matef = "12MM_RF_SEAM", "CLOSED_HARNESS_BAND"
            hardware = "Qualified RF-welded adjacent gore seams captured beneath the closed harness band"
        elif occ.occurrence_id.startswith("ROUTE-"):
            mate = "ARM-LONGERON-1" if "GAS" in occ.occurrence_id or "PILOT" in occ.occurrence_id else "ARM-LONGERON-2"
            ctype = "BORED_CHANNEL_AND_END_UNIONS"
            ownf, matef = "ROUTE_OD", "JIG_BORED_CHANNEL"
            hardware = "Named forward, aft, and WP04 bulkhead unions with ferrules and strain relief"
        elif "UNION" in occ.occurrence_id:
            mate = "FWD-RING-02" if occ.occurrence_id.endswith("FWD") else "AFT-ROUTE-RING-001"
            ctype = "BULKHEAD_UNION"
            ownf, matef = "UNION_SHANK_AND_FLANGES", "REAMED_ROUTE_PASSAGE"
            hardware = "Double-ferrule bulkhead union body, nut, ferrules, and anti-rotation flats"
        elif occ.occurrence_id.startswith("BOOSTER-BAND"):
            mate = "FWD-SHELL-001"
            ctype = "M3_BOLTED_PEEK_CLAMP"
            ownf, matef = "CLAMP_TAB_BORE", "SHELL_THREADED_INSERT"
            hardware = "M3 clamp screw in the identified shell insert"
        elif occ.occurrence_id.startswith("BOOSTER-"):
            mate = occ.occurrence_id.replace("BOOSTER-", "BOOSTER-BAND-") + "-2"
            ctype = "THREE_SPACED_SUPPORT_BANDS"
            ownf, matef = "RESERVOIR_OD", "CLAMP_ID"
            hardware = "Three occurrence-matched PEEK support bands with M3 clamp screws"
        elif occ.occurrence_id.startswith("CO2-CARTRIDGE"):
            continue
        elif occ.occurrence_id.startswith("PUNCTURE-HEAD"):
            mate = "COLLECTION-MANIFOLD-001"
            ctype = "THREADED_PRESSURE_PORT"
            ownf, matef = "HEAD_THREAD_AND_SEAL", "MANIFOLD_PORT"
            hardware = "Threaded puncture head with occurrence-specific pressure seal"
        elif occ.occurrence_id.startswith("PIVOT-"):
            tokens = occ.occurrence_id.split("-")
            arm_index = tokens[2] if len(tokens) > 2 and tokens[2].isdigit() else ""
            if not arm_index:
                continue
            mate = f"PIVOT-PIN-{arm_index}" if tokens[1] == "CLIP" else f"ARM-{arm_index}"
            ctype = "CAPTIVE_HARDWARE"
            if tokens[1] == "CLIP":
                ownf, matef = "EXTERNAL_SPIRAL_RING", "PIVOT_PIN_RETAINER_GROOVE"
                hardware = f"{occ.occurrence_id} seated in {mate} external groove"
            elif tokens[1] == "BUSH":
                ownf, matef = "BUSHING_PRESS_FIT_OD", "ARM_PIVOT_BOSS_COUNTERBORE"
                hardware = "Interference-fit PEEK-lined bushing with controlled shoulder"
            elif tokens[1] == "WASHER":
                ownf, matef = "THRUST_WASHER_FACES", "ARM_PIVOT_BOSS_THRUST_FACE"
                hardware = f"Captive thrust washer on PIVOT-PIN-{arm_index} shoulder"
            else:
                ownf, matef = "PIN_GROUND_SHANK_AND_HEAD", "ARM_AND_CARRIER_COAXIAL_BORES"
                hardware = f"PIVOT-PIN-{arm_index} retained by PIVOT-CLIP-{arm_index}"
        elif occ.occurrence_id.startswith("LINK-PIN-"):
            tokens = occ.occurrence_id.split("-")
            arm_index, end = tokens[2], tokens[3]
            mate = f"ARM-{arm_index}" if end == "BELL" else "CROSSHEAD-001"
            ctype = "CAPTIVE_LINK_CLEVIS_PIN"
            ownf, matef = "PIN_GROUND_SHANK_AND_HEAD", f"{end}_DOUBLE_SHEAR_CLEVIS_BORES"
            hardware = f"{occ.occurrence_id} retained by LINK-CLIP-{arm_index}-{end}"
        elif occ.occurrence_id.startswith("LINK-CLIP-"):
            tokens = occ.occurrence_id.split("-")
            arm_index, end = tokens[2], tokens[3]
            mate = f"LINK-PIN-{arm_index}-{end}"
            ctype = "EXTERNAL_GROOVE_RETAINER"
            ownf, matef = "EXTERNAL_E_RING", "LINK_PIN_RETAINER_GROOVE"
            hardware = f"{occ.occurrence_id} seated in {mate} external groove"
        elif occ.occurrence_id.startswith("FIXED-SECTOR-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"ARM-LONGERON-{arm_index}"
            ctype = "WELDED_FIXED_BODY_SECTOR"
            ownf, matef = "SECTOR_LONGITUDINAL_WELD_LANDS", "LONGERON_SECTOR_WELD_LANDS"
            hardware = "Two continuous qualified longitudinal structural welds"
        elif occ.occurrence_id.startswith("ARM-STOP-PAD-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"ARM-{arm_index}"
            ctype = "DOVETAIL_REPLACEABLE_STOP_PAD"
            ownf, matef = "STOP_PAD_DOVETAIL_AND_2X_M3", "ARM_TIP_DOVETAIL_AND_THREADS"
            hardware = "Dovetail plus two M3 screws with locking compound"
        elif occ.occurrence_id.startswith("FIXED-STOP-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"PIVOT-CARRIER-{arm_index}"
            ctype = "DOWELLED_FIXED_DEPLOY_STOP"
            ownf, matef = "STOP_DOWELS_AND_2X_M3", "CARRIER_STOP_DATUM_AND_THREADS"
            hardware = "Two dowels and two M3 screws with locking compound"
        elif occ.occurrence_id.startswith("LOCK-DOG-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"FIXED-STOP-{arm_index}"
            ctype = "CAPTIVE_GUIDED_LOCK_DOG"
            ownf, matef = "DOG_GUIDE_FACES", "STOP_DOG_GUIDE_SLOT"
            hardware = f"LOCK-SPRING-{arm_index} captured between defined seats"
        elif occ.occurrence_id.startswith("LOCK-SPRING-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"LOCK-DOG-{arm_index}"
            ctype = "CAPTURED_LOCK_RETURN_SPRING"
            ownf, matef = "SPRING_MOVING_END_COIL", "LOCK_DOG_SPRING_SEAT"
            hardware = f"Opposite end captured in FIXED-STOP-{arm_index} spring pocket"
        elif occ.occurrence_id.startswith("STOW-DOG-"):
            arm_index = occ.occurrence_id.rsplit("-", 1)[1]
            mate = f"PIVOT-CARRIER-{arm_index}"
            ctype = "CAPTIVE_RADIAL_STOW_DOG"
            ownf, matef = "DOG_RADIAL_GUIDE_FACES", "CARRIER_RADIAL_GUIDE_SLOT"
            hardware = "Captured return spring and guide-end shoulders"
        elif occ.occurrence_id.startswith("GS19-") or occ.occurrence_id.startswith("HBD-"):
            label = "GS19" if occ.occurrence_id.startswith("GS19-") else "HBD"
            if "CLIP-" in occ.occurrence_id:
                end = occ.occurrence_id.rsplit("-", 1)[1]
                mate = f"{label}-PIN-{end}"
                ctype = "EXTERNAL_GROOVE_RETAINER"
                ownf, matef = "EXTERNAL_E_RING", "ACTUATOR_PIN_RETAINER_GROOVE"
                hardware = f"{occ.occurrence_id} seated in {mate} external groove"
            elif "PIN-" in occ.occurrence_id:
                end = occ.occurrence_id.rsplit("-", 1)[1]
                mate = f"{label}-FIXED-YOKE" if end == "FIXED" else "CROSSHEAD-001"
                ctype = "CAPTIVE_ACTUATOR_CLEVIS_PIN"
                ownf, matef = "PIN_GROUND_SHANK_AND_HEAD", f"{label}_{end}_COAXIAL_CLEVIS_BORES"
                hardware = f"{occ.occurrence_id} retained by {label}-CLIP-{end}"
            else:
                support = explicit_supports.get(occ.occurrence_id)
                if support is None:
                    continue
                mate, ctype, ownf, matef, hardware = support
        elif occ.occurrence_id.startswith("WP04-"):
            if occ.occurrence_id.startswith("WP04-GUIDE-RAIL-"):
                mate, ctype = "WP04-REACTION-BULKHEAD", "TWO_END_BOLTED_GUIDE_RAIL"
                ownf, matef = "RAIL_FORWARD_M3_BORE_AND_PILOT", "BULKHEAD_RAIL_M3_THREAD_AND_PILOT"
                hardware = "M3 screw at reaction bulkhead plus aft stop-ring fastener"
            elif occ.occurrence_id == "WP04-FOLLOWER-001":
                mate, ctype = "WP04-GUIDE-RAIL-1", "THREE_RAIL_GUIDED_TRANSLATION"
                ownf, matef = "FOLLOWER_THREE_GUIDE_SLOTS", "THREE_CLOCKED_GUIDE_RAILS"
                hardware = "Three captured rail/slot pairs and the moving spring sleeve"
            elif occ.occurrence_id == "WP04-EJECTOR-SPRING":
                mate, ctype = "WP04-FIXED-SLEEVE", "CAPTURED_GUIDED_EJECTOR_SPRING"
                ownf, matef = "SPRING_FIXED_END_COIL", "FIXED_SLEEVE_ANNULAR_SEAT"
                hardware = "Overlapping fixed and moving guide sleeves"
            elif occ.occurrence_id == "WP04-FIXED-SLEEVE":
                mate, ctype = "WP04-REACTION-BULKHEAD", "BOLTED_FIXED_GUIDE_SLEEVE"
                ownf, matef = "SLEEVE_SHOULDER_AND_3X_M3", "BULKHEAD_SLEEVE_PILOT_AND_THREADS"
                hardware = "Shoulder plus three M3 screws with locking compound"
            elif occ.occurrence_id == "WP04-MOVING-SLEEVE":
                mate, ctype = "WP04-FOLLOWER-001", "PILOTED_MOVING_GUIDE_SLEEVE"
                ownf, matef = "SLEEVE_AFT_PILOT", "FOLLOWER_CENTRAL_PILOT_BORE"
                hardware = "Piloted shoulder and three captured screws"
            elif occ.occurrence_id == "WP04-LATCH-001":
                mate, ctype = "WP04-GUIDE-RAIL-3", "BOLTED_LATCH_HOUSING"
                ownf, matef = "LATCH_HOUSING_2X_M3_PATTERN", "GUIDE_RAIL_LATCH_THREADS"
                hardware = "Two M3 screws, pilot key, and locking compound"
            elif occ.occurrence_id == "WP04-SEAR-001":
                mate, ctype = "WP04-LATCH-001", "CAPTIVE_GUIDED_SEAR"
                ownf, matef = "SEAR_GROUND_SHANK_AND_GROOVE", "LATCH_REAMED_SEAR_GUIDE"
                hardware = "Integral head and WP04-SEAR-CLIP-001 external retaining ring"
            elif occ.occurrence_id == "WP04-SEAR-CLIP-001":
                mate, ctype = "WP04-SEAR-001", "EXTERNAL_GROOVE_RETAINER"
                ownf, matef = "EXTERNAL_E_RING", "SEAR_PIN_RETAINER_GROOVE"
                hardware = "WP04-SEAR-CLIP-001 seated in the machined sear-pin groove"
            else:
                continue
        elif occ.occurrence_id.startswith("WP05-") or occ.occurrence_id.startswith("DOOR-"):
            if occ.occurrence_id == "WP05-DOOR-001":
                mate, ctype = "WP05-SERVICE-THROAT", "REVOLUTE_SERVICE_DOOR_HINGE"
                ownf, matef = "DOOR_HINGE_KNUCKLE_BORE", "THROAT_HINGE_EAR_BORES"
                hardware = "WP05-HINGE-PIN with external retainer and captive lanyard"
            elif occ.occurrence_id == "WP05-HINGE-PIN":
                mate, ctype = "WP05-DOOR-001", "CAPTIVE_HINGE_PIN"
                ownf, matef = "HINGE_PIN_GROUND_SHANK_AND_HEAD", "DOOR_AND_THROAT_COAXIAL_HINGE_BORES"
                hardware = "Integral pin head and external retaining ring"
            elif occ.occurrence_id.startswith("DOOR-DETENT-"):
                mate, ctype = "WP05-SERVICE-THROAT", "THREADED_DOOR_DETENT"
                ownf, matef = "M3_DETENT_THREAD_AND_DRIVE", "THROAT_DETENT_M3_THREAD"
                hardware = "M3 threaded ball plunger with thread-locking feature"
            elif occ.occurrence_id == "WP05-DOOR-LANYARD":
                mate, ctype = "WP05-DOOR-001", "CLOSED_SWAGED_LANYARD_EYE"
                ownf, matef = "DOOR_END_SWAGED_EYE", "INTEGRAL_DOOR_LANYARD_EYE"
                hardware = "Closed swaged eye plus body-end closed eye"
            else:
                continue
        elif occ.occurrence_id.startswith("HARNESS") or occ.occurrence_id.startswith("TETHER") or occ.occurrence_id == "RECOVERY-TETHER-001":
            # All harness legs, bands, terminal, thimbles, and the recovery
            # tether are already enumerated above.  Never invent a direct
            # harness-to-terminal shortcut for an unmatched softgood.
            continue
        elif occ.occurrence_id in explicit_supports:
            mate, ctype, ownf, matef, hardware = explicit_supports[occ.occurrence_id]
        else:
            continue
        if not mate or mate not in b.global_shapes or mate == occ.occurrence_id:
            continue
        connect_present(
            f"DETAIL-{occ.occurrence_id}-TO-{mate}", occ.occurrence_id, mate, ownf, matef, ctype,
            occ.permitted_dof, hardware,
            f"{occ.occurrence_id}:{ownf} is axially retained at {mate}:{matef}",
            f"{mate}:{matef} provides the lateral pilot, clevis, channel, or guide for {occ.occurrence_id}",
            f"{ownf}/{matef} and the named hardware prevent unintended rotation",
            mate, occ.occurrence_id, f"Service the named {hardware} at this exact occurrence pair",
            f"Enumerated modeled joint {occ.occurrence_id}:{ownf} to {mate}:{matef}; class {ctype}",
        )


def build_state(state: str) -> R2Builder:
    b = R2Builder(state)
    build_forward(b)
    build_arm_module(b)
    build_aft(b)
    add_primary_connections(b)
    b.root.add(b.forward, name=b.forward.name)
    b.root.add(b.arm_module, name=b.arm_module.name)
    b.root.add(b.aft, name=b.aft.name)
    return b


def serialize_builder(b: R2Builder) -> dict[str, Any]:
    return {
        "state": b.state,
        "parts": [
            {
                **{k: v for k, v in asdict(p).items() if k != "shape"},
                "mass_kg": p.resolved_mass(),
                "volume_mm3": p.shape.Volume(),
                "solid_count": len(p.shape.Solids()),
                "face_count": len(p.shape.Faces()),
            }
            for p in b.catalog.parts.values()
        ],
        "occurrences": [
            {
                **{k: v for k, v in asdict(o).items() if k != "location"},
                "transform_matrix_3x4": g.loc_matrix(o.location),
                "identity_transform": g.loc_is_identity(o.location),
                "global_volume_mm3": b.global_shapes[o.occurrence_id].Volume(),
                "global_bbox_mm": {
                    "xmin": b.global_shapes[o.occurrence_id].BoundingBox().xmin,
                    "xmax": b.global_shapes[o.occurrence_id].BoundingBox().xmax,
                    "ymin": b.global_shapes[o.occurrence_id].BoundingBox().ymin,
                    "ymax": b.global_shapes[o.occurrence_id].BoundingBox().ymax,
                    "zmin": b.global_shapes[o.occurrence_id].BoundingBox().zmin,
                    "zmax": b.global_shapes[o.occurrence_id].BoundingBox().zmax,
                },
            }
            for o in b.occurrences
        ],
        "connections": [asdict(c) for c in b.connections],
        "routes": b.routes,
        "flexible_occurrence_ids": sorted(b.flexible_ids),
        "external_context_ids": sorted(b.external_ids),
        "kinematics": {
            "arm_angle_deg": g.DEPLOYED_ANGLE if b.deployed else 0.0,
            "crosshead_z_mm": g.kinematic(g.DEPLOYED_ANGLE if b.deployed else 0.0)["crosshead_z"],
            "crosshead_travel_full_precision_mm": g.CROSSHEAD_TRAVEL,
        },
    }


def build_external_context() -> cq.Assembly:
    root = cq.Assembly(name="900_EXTERNAL_TEST_CONTEXT_PROVISIONAL_NOT_STINGRAY_PRODUCT_ASSY")
    hook = g.make_external_test_hook_local()
    load_cell = g.cyl_z(15.0, 70.0)
    shackle = g.make_shackle_local()
    root.add(hook, name="EXT-CRANE-HOOK-UNCONTROLLED__EXTERNAL_CONTEXT_ONLY", loc=g.translation_loc(0, 0, 2100.0), color=g.COLORS["external"])
    root.add(load_cell, name="EXT-LOAD-CELL-UNCONTROLLED__EXTERNAL_CONTEXT_ONLY", loc=g.translation_loc(0, 0, 2030.0), color=g.COLORS["external"])
    root.add(shackle, name="EXT-SHACKLE-UNCONTROLLED__EXTERNAL_CONTEXT_ONLY", loc=g.translation_loc(0, 0, 2015.0), color=g.COLORS["external"])
    return root


def main() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    builders: list[R2Builder] = []
    for state, filename in (("STOWED", STOWED_FILE), ("DEPLOYED", DEPLOYED_FILE)):
        print(f"Building R2 {state} source assembly", flush=True)
        builder = build_state(state)
        out = RELEASE_DIR / filename
        export_ap242(builder.root, out)
        name_assembly_usage_occurrences(out)
        builders.append(builder)
        data = serialize_builder(builder)
        (ANALYSIS_DIR / f"authoring_inventory_{state.lower()}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Wrote {out} ({out.stat().st_size} bytes)", flush=True)

    context_path = RELEASE_DIR / EXTERNAL_CONTEXT_FILE
    export_ap242(build_external_context(), context_path)
    name_assembly_usage_occurrences(context_path)

    manifest = {
        "release_status": "CREO_VALIDATION_PENDING — WIP — NOT RELEASED",
        "authoring_kernel": f"CadQuery {cq.__version__} / OCCT 7.9",
        "schema": "AP242",
        "crosshead_travel_mm": g.CROSSHEAD_TRAVEL,
        "hard_requirements": {
            "arm_module_od_max_mm": g.HARD_OD,
            "normal_body_target_mm": g.NORMAL_OD,
            "arm_clocking_deg": [0.0, 120.0, 240.0],
            "arm_deployed_angle_deg": g.DEPLOYED_ANGLE,
            "arm_pivot_to_tip_mm": g.ARM_LENGTH,
            "rigid_length_max_mm": g.MAX_RIGID_LENGTH,
            "mass_max_kg": g.MAX_SYSTEM_MASS_KG,
            "crosshead_travel_min_mm": 15.050,
        },
        "files": {},
    }
    for path in (RELEASE_DIR / STOWED_FILE, RELEASE_DIR / DEPLOYED_FILE, context_path):
        manifest["files"][path.name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }
    (ANALYSIS_DIR / "authoring_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
