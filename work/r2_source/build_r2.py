#!/usr/bin/env python3
"""Build the corrected STINGRAY DF8 final exact-AP242 assemblies.

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
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Controller

import r2_geometry as g
import r2_hardware as hw
import r2_final_scope
import r2_hierarchy
import final_detail_naming
import forward_arm_repack_config as repack


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
RELEASE_DIR = ROOT / "work" / "final_release"
ANALYSIS_DIR = ROOT / "work" / "final_analysis"
INPUT_DIR = ROOT / "work" / "input"

STOWED_FILE = "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step"
DEPLOYED_FILE = "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step"

# These rigid definitions are authored once and reused verbatim in both
# endpoint assemblies.  Rebuilding the same Boolean history independently can
# preserve all geometric metrics yet change OCCT's serialized local topology;
# sharing the exact definition prevents a rigid part from acquiring a
# state-dependent BREP identity.  Flexible/softgood endpoint shapes are
# deliberately excluded because their local geometry is allowed to change.
STATE_INVARIANT_PART_NUMBERS = frozenset({
    "DF8-R2-AFT-SHELL-001",
    "DF8-R2-ARM-BLADE-001",
    "DF8-R2-ARM-STOP-PAD-001",
    "DF8-R2-BACKUP-ACCESS-FIXED-SECTOR-003",
    "DF8-R2-CROSSHEAD-001",
    "DF8-R2-FIXED-STOP-001",
    "DF8-R2-PIVOT-CARRIER-001",
    "DF8-R2-SHORT-LINK-001",
    "DF8-R2-STOW-DOG-001",
    "DF8-R2-STOW-DOG-GUIDE-001",
    "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
    "DF8-R2-STRUCT-RING-ROUTED-001",
    "SSCA-M3-8-A4-BL",
    "WP04-FOL-001-R2",
    "WP04-HST-001-R2",
    "WP04-LATCH-SEAR-E-RING-R2",
    "WP04-LATCH-SEAR-R2",
    "WP04-MOVING-GUIDE-SLEEVE-R2",
    "WP05-DOOR-R2",
    "WP05-SERVICE-THROAT-R2",
})
_STATE_INVARIANT_SHAPE_CACHE: dict[str, cq.Shape] = {}

# Automatic deployed-lock geometry.  The dog stays outside the rigid arm and
# captive pad-screw envelopes through 79 degrees, then advances after the pad
# strike bore aligns at 80 degrees.  The common outer spring seat makes the
# 3.30 mm dog stroke explicit in both endpoint B-reps.
LOCK_DEPLOYED_DOG_Y_MM = 3.65
LOCK_RETRACTED_DOG_Y_MM = 6.95
LOCK_SPRING_OUTER_SEAT_Y_MM = 9.90
LOCK_RETRACTED_SPRING_LENGTH_MM = 1.65
LOCK_DEPLOYED_SPRING_LENGTH_MM = 4.95
LOCK_BUSHING_Y_MM = 10.15
LOCK_GUIDE_INNER_Y_MM = 3.80
LOCK_GUIDE_OUTER_Y_MM = 10.00
LOCK_SPRING_MASS_KG = 2.8560892651638403e-6


def state_invariant_shape(part_number: str, shape: cq.Shape) -> cq.Shape:
    """Return one shared exact definition for every state-invariant part.

    The independently built candidate is still checked before reuse so a real
    state-dependent dimensional or topological change fails authoring instead
    of being hidden by the cache.
    """
    if part_number not in STATE_INVARIANT_PART_NUMBERS:
        return shape
    cached = _STATE_INVARIANT_SHAPE_CACHE.get(part_number)
    if cached is None:
        _STATE_INVARIANT_SHAPE_CACHE[part_number] = shape
        return shape
    cached_bbox = cached.BoundingBox()
    candidate_bbox = shape.BoundingBox()
    cached_bounds = (
        cached_bbox.xmin, cached_bbox.ymin, cached_bbox.zmin,
        cached_bbox.xmax, cached_bbox.ymax, cached_bbox.zmax,
    )
    candidate_bounds = (
        candidate_bbox.xmin, candidate_bbox.ymin, candidate_bbox.zmin,
        candidate_bbox.xmax, candidate_bbox.ymax, candidate_bbox.zmax,
    )
    mismatch = (
        len(cached.Solids()) != len(shape.Solids())
        or len(cached.Faces()) != len(shape.Faces())
        or abs(cached.Volume() - shape.Volume()) > 1.0e-6
        or max(abs(a - b) for a, b in zip(cached_bounds, candidate_bounds)) > 1.0e-6
    )
    if mismatch:
        raise ValueError(
            f"State-invariant part {part_number} changed between endpoint builds: "
            f"cached_solids={len(cached.Solids())}, candidate_solids={len(shape.Solids())}, "
            f"cached_faces={len(cached.Faces())}, candidate_faces={len(shape.Faces())}, "
            f"volume_delta_mm3={shape.Volume() - cached.Volume()}, "
            f"cached_bbox={cached_bounds}, candidate_bbox={candidate_bounds}"
        )
    return cached


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
    path.write_text(updated, encoding="latin-1", newline="\n")


def complete_make_definition(material: str, make_buy: str, process: str,
                             finish: str, notes: str) -> tuple[str, str, str]:
    """Append the common drawing controls required for fabrication release."""
    if make_buy != "MAKE":
        return process, finish, notes
    key = material.upper()
    controls = "Heat/lot CoC; drawing tolerances; deburr; clean; final dimensional inspection"
    default_finish = "Per controlled drawing"
    if "TUNGSTEN" in key:
        controls = (
            "ASTM B777 Class 4 W-Ni-Fe product form, density >=18.0 g/cm3; heat/lot CoC; "
            "density verification; UT for internal discontinuities; ground datum inspection"
        )
        default_finish = "Ground rope/penetration-safe edges; corrosion-inhibiting clean"
    elif "TI-6AL-4V" in key:
        controls = (
            "Ti-6Al-4V Grade 5 certified product form; heat/lot CoC; qualified argon-purged WPS where welded; "
            "PT after welding; alpha-case removal; galvanic isolation; CMM final inspection"
        )
        default_finish = "ASTM B600 clean/passivate; drawing-controlled surface finish"
    elif "TI-3AL-2.5V" in key:
        controls = (
            "ASTM B338 Grade 9 tube/product form; heat/lot CoC; qualified argon-purged laser-weld WPS; "
            "PT and borescope inspection; alpha-case removal; CMM final inspection"
        )
        default_finish = "ASTM B600 clean/passivate; drawing-controlled shell finish"
    elif "7075" in key:
        controls = (
            "ASTM B209/B221 7075-T6 certified stock as applicable; lot CoC; stress-relief machining sequence; "
            "edge break; Type II sulfuric anodize with sealed masked fits; CMM inspection"
        )
        default_finish = "MIL-PRF-8625 Type II anodize; mask pressure and locating fits"
    elif "316" in key or "1.4310" in key or "EN 10270-3" in key:
        controls = (
            "Certified stainless product form/condition; heat/lot CoC; qualified weld/braze procedure where applicable; "
            "ASTM A967 passivation; PT of pressure welds; dimensional inspection"
        )
        default_finish = "ASTM A967 passivated; rope-contact and seal surfaces polished per drawing"
    elif "17-4" in key:
        controls = (
            "ASTM A564 Type 630 certified stock; H900 unless the drawing explicitly selects a tougher condition; "
            "heat-treatment/hardness record; ASTM A967 passivation; grind/ream critical fits; CMM inspection"
        )
        default_finish = "ASTM A967 passivated; critical bearing surfaces ground"
    elif "PEEK" in key:
        controls = (
            "Virgin unfilled PEEK resin/stock with ASTM D6262 or ISO material certificate; annealed stock; "
            "controlled machining temperature; moisture conditioning; dimensional inspection after stabilization"
        )
        default_finish = "Machined, edge-broken, cleaned; no mold release or particulate"
    elif "ACETAL" in key or "POM" in key:
        controls = (
            "Hydrolysis-resistant POM-C certified resin/stock; lot CoC; moisture conditioning; "
            "water-compatibility verification; stabilized final dimensional inspection"
        )
        default_finish = "Machined, edge-broken and aqueous-service cleaned"
    elif "TPU-COATED NYLON" in key:
        controls = (
            "Controlled TPU-coated high-tenacity nylon laminate drawing: substrate denier/weave, areal weight, "
            "coating chemistry/thickness and lot CoC; qualified RF-weld schedule; 100% leak and pressure proof; aging coupon"
        )
        default_finish = "Clean RF-welded membrane; trimmed sealed edges"
    elif "UHMWPE" in key:
        controls = (
            "Sturges X-6292 1-inch Dyneema webbing with polyester edges; raw-lot CoC; controlled thread, fold, "
            "bar-tack pattern/density and traveler; finished-article dimensional inspection and proof load"
        )
        default_finish = "Heat-sealed ends; protected stitch tails; no cut load fibers"
    elif "HMPE" in key:
        controls = (
            "Controlled rope construction and raw-lot CoC; finished length tolerance; occurrence-specific eye/thimble/ferrule traveler; "
            "splice or swage dimensional inspection; finished-article proof load"
        )
        default_finish = "Chafe-protected, heat-sealed and clean"
    cooked_process = "; ".join(value for value in (process.strip(), controls) if value)
    cooked_finish = finish.strip() or default_finish
    cooked_notes = notes.strip()
    return cooked_process, cooked_finish, cooked_notes


class R2Builder:
    def __init__(self, state: str):
        self.state = state
        self.deployed = state == "DEPLOYED"
        self.catalog = g.PartCatalog()
        self.root = cq.Assembly(name=f"Stingray_{state.title()}_Inspection_Assembly")
        self.forward = cq.Assembly(name="100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY")
        self.arm_module = cq.Assembly(name="300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY")
        self.aft = cq.Assembly(name="500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY")
        self.occurrences: list[g.Occurrence] = []
        self.connections: list[g.Connection] = []
        self.global_shapes: dict[str, cq.Shape] = {}
        self.flexible_ids: set[str] = set()
        self.external_ids: set[str] = set()
        self.routes: list[dict[str, Any]] = []
        self.intentional_fits: list[dict[str, Any]] = []
        self.attachment_requirements: list[dict[str, Any]] = []
        self.motion_tracks: list[dict[str, Any]] = []
        self.mass_overrides_kg: dict[str, float] = {}
        self.state_notes: list[dict[str, Any]] = []
        self.definition_of_done_requirements: dict[str, Any] = {}
        self.integral_joint_eliminations: list[dict[str, Any]] = []
        self.assembly_hierarchy: dict[str, Any] = {}

    def define(self, part_number: str, revision: str, description: str, shape: cq.Shape,
               material: str, make_buy: str = "MAKE", manufacturer: str = "STINGRAY custom",
               cad_classification: str = "DRAWING_DERIVED", mass_kg: float | None = None,
               source_url: str = "", purchase_url: str = "", process: str = "",
               finish: str = "", notes: str = "", color_key: str = "steel",
               external_context: bool = False) -> g.PartDef:
        shape = state_invariant_shape(part_number, shape)
        process, finish, notes = complete_make_definition(
            material, make_buy, process, finish, notes
        )
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
        if part.mass_kg is not None:
            self.mass_overrides_kg[occurrence_id] = float(part.mass_kg)
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
                         service_slack_mm: float, pressure_rating: str, status: str,
                         maximum_endpoint_gap_mm: float = 0.15,
                         termination_occurrence_ids: list[str] | None = None,
                         support_occurrence_ids: list[str] | None = None,
                         integral_terminations: bool = True,
                         integral_support: bool = False,
                         penetration_occurrence_ids: list[str] | None = None,
                         integral_penetrations: bool = True,
                         origin_interface_occurrence: str | None = None,
                         destination_interface_occurrence: str | None = None) -> None:
        if origin.startswith("EXTERNAL_"):
            self.external_ids.add(origin)
        if destination.startswith("EXTERNAL_"):
            self.external_ids.add(destination)
        self.routes.append({
            "state": self.state, "route_occurrence_id": route_id,
            "origin_occurrence": origin, "destination_occurrence": destination,
            "termination_fittings": fittings, "controlled_penetrations": penetrations,
            "supports": supports, "minimum_bend_radius_mm": bend_radius_mm,
            "service_slack_mm": service_slack_mm, "pressure_rating": pressure_rating,
            "status": status,
            "maximum_endpoint_gap_mm": maximum_endpoint_gap_mm,
            "origin_interface_occurrence": (
                origin_interface_occurrence if origin_interface_occurrence is not None
                else (origin if not origin.startswith("EXTERNAL_") else "")
            ),
            "destination_interface_occurrence": (
                destination_interface_occurrence if destination_interface_occurrence is not None
                else (destination if not destination.startswith("EXTERNAL_") else "")
            ),
            "origin_external_boundary": origin.startswith("EXTERNAL_"),
            "destination_external_boundary": destination.startswith("EXTERNAL_"),
            "termination_occurrence_ids": termination_occurrence_ids or [],
            "integral_terminations": integral_terminations,
            "termination_process_basis": fittings,
            "support_occurrence_ids": support_occurrence_ids or [],
            "integral_support": integral_support,
            "support_process_basis": supports,
            "penetration_occurrence_ids": penetration_occurrence_ids or [],
            "integral_penetrations": integral_penetrations,
            "penetration_process_basis": penetrations,
            "maximum_support_gap_mm": 0.25,
        })

    def allow_intentional_fit(self, fit_id: str, occurrence_a: str, occurrence_b: str,
                              fit_type: str, min_common_volume_mm3: float,
                              max_common_volume_mm3: float, process_basis: str,
                              state_scope: str | None = None,
                              solid_index_a: int | None = None,
                              solid_index_b: int | None = None) -> None:
        if occurrence_a == occurrence_b:
            raise ValueError("Intentional-fit exception must name two occurrences")
        record = {
            "exception_id": fit_id, "state": state_scope or self.state,
            "occurrence_a": occurrence_a, "occurrence_b": occurrence_b,
            "fit_type": fit_type,
            "minimum_common_volume_mm3": min_common_volume_mm3,
            "maximum_common_volume_mm3": max_common_volume_mm3,
            "process_basis": process_basis,
        }
        if solid_index_a is not None or solid_index_b is not None:
            if solid_index_a is None or solid_index_b is None:
                raise ValueError("Both solid indices are required when one is specified")
            record["solid_index_a"] = int(solid_index_a)
            record["solid_index_b"] = int(solid_index_b)
        self.intentional_fits.append(record)

    def require_attachment(self, attachment_id: str, occurrence_a: str, occurrence_b: str,
                           attachment_type: str, maximum_separation_mm: float,
                           hardware_occurrence_ids: list[str] | None = None,
                           evidence_basis: str = "",
                           structural_load_path: bool = False) -> None:
        self.attachment_requirements.append({
            "attachment_id": attachment_id, "state": self.state,
            "occurrence_a": occurrence_a, "occurrence_b": occurrence_b,
            "attachment_type": attachment_type,
            "maximum_separation_mm": maximum_separation_mm,
            "hardware_occurrence_ids": hardware_occurrence_ids or [],
            "evidence_basis": evidence_basis,
            "structural_load_path": structural_load_path,
        })

    def add_motion_track(self, occurrence_id: str, mode: str, process_basis: str,
                         **parameters: Any) -> None:
        if occurrence_id not in self.global_shapes:
            raise ValueError(f"Motion track names unknown occurrence: {occurrence_id}")
        self.motion_tracks.append({
            "occurrence_id": occurrence_id,
            "mode": mode,
            "process_basis": process_basis,
            **parameters,
        })


def register_mandatory_hardware_part_definitions(b: R2Builder) -> dict[str, g.PartDef]:
    """Install the shared exact hardware catalog without duplicating source springs."""
    hw.validate_contract()
    parts = hw.make_part_definitions(b.state)
    for part in parts.values():
        part.shape = state_invariant_shape(part.part_number, part.shape)
        b.catalog.add(part)
    return parts


def radial_xy(radius: float, phi: float) -> tuple[float, float]:
    a = math.radians(phi)
    return radius * math.cos(a), radius * math.sin(a)


def radial_cylinder(phi: float, radius_start: float, length: float,
                    cutter_radius: float, z: float) -> cq.Shape:
    """Exact radial cylinder used for occurrence-clocked bosses and bores."""
    x, y = radial_xy(radius_start, phi)
    dx, dy = radial_xy(1.0, phi)
    return cq.Solid.makeCylinder(
        cutter_radius, length, cq.Vector(x, y, z), cq.Vector(dx, dy, 0.0)
    )


def ring_with_axial_route_holes(length: float, ro: float = 28.5, ri: float = 19.5,
                                arm_root_reliefs: bool = False,
                                route_transition: str = "NONE") -> cq.Shape:
    ring = g.tube_z(ro, ri, length, z0=-length / 2.0)
    if arm_root_reliefs:
        # Three shallow, manufactured aft-face deployment scallops clear the
        # exact root swept envelope from 0..80 degrees.  They stop 6 mm short
        # of the forward face and lie between the three fixed-sector/longeron
        # load-path lands at 60/180/300 degrees.
        for arm_clock in (0.0, 120.0, 240.0):
            ring = ring.cut(g.analytic_sector(28.7, 19.3, 8.4,
                                              arm_clock, 22.0, -4.2))
    # Three occupied service corridors: gas, pilot, and Bowden sheath/wire.
    # Each structural ring receives a straight, jig-bored r=26.2 mm passage
    # coaxial with its two-collar gland.  Radial transitions occur in the
    # separately machined shell corridors on either side, never inside ring
    # stock or through a diagonal gland.
    # Pilot service uses the unused 325-degree fixed-sector passage.  This is
    # the clear inter-booster corridor; the former 35-degree passage drove the
    # pilot line directly through BOOSTER-1 on its way out from the valve.
    transition_specs = ((85.0, 2.30), (325.0, 2.10), (205.0, 2.15))
    for phi, cutter_radius in transition_specs:
        a = math.radians(phi)
        x, y = 26.2 * math.cos(a), 26.2 * math.sin(a)
        ring = ring.cut(g.cyl_z(cutter_radius, length + 1.0, x, y, -length / 2.0 - 0.5))
    return ring


def forward_shell_with_port() -> cq.Shape:
    # The repack moves FWD-RING-02 forward with the pivot carrier.  This short
    # shell remains the unchanged pressure-cartridge/manifold bay closure.
    length = repack.FWD_RING_02_Z_MM - repack.FWD_RING_01_Z_MM - 8.0
    return g.tube_z(g.NORMAL_R, 25.35, length, z0=4.0)


def repack_transition_shell_shape() -> cq.Shape:
    """Continuous OD shell over the aft-relocated stationary hardware bay."""
    start = repack.ARM_TERMINATION_RING_Z_MM + 4.0
    end = repack.AFT_ROUTE_RING_Z_MM - 4.0
    return g.tube_z(g.NORMAL_R, 25.35, end - start)


def aft_shell_with_openings() -> cq.Shape:
    # The load-carrying shell ends at the service-throat pilot plane.  The R1
    # geometry incorrectly double-occupied the final 100 mm with two tubes.
    # Start at the aft face of the shifted z=1638 route ring and stop at the forward
    # face of the service throat.  This removes the former 4 mm double-volume
    # ring joint while retaining the same external product datums.
    shell = g.tube_z(g.NORMAL_R, 25.30, 286.0, z0=7.0)
    # Hardpoint lug aperture at global z=1900.
    shell = shell.cut(g.box_center(19.0, 17.0, 20.0, 24.0, 0.0, 265.0))
    # Full occurrence-matched latch/service aperture.  The former 8 x 7 mm
    # slot cleared only the latch centerline and left the housing, support
    # blade, and both captive screw heads embedded in shell stock.
    latch_window = g.box_center(12.0, 23.0, 24.0, 25.4, 0.0, 110.0).rotate((0, 0, 0), (0, 0, 1), 270.0)
    shell = shell.cut(latch_window)
    # The arm-module routes turn inboard immediately aft of the routed ring.
    # Machine four individual oblique passages that follow those centerlines;
    # no route is allowed to occupy intact shell wall stock.
    route_passages = ((85.0, 1.20), (325.0, 0.95), (205.0, 1.00))
    for phi, radius in route_passages:
        a = math.radians(phi)
        points = [
            (26.2 * math.cos(a), 26.2 * math.sin(a), 5.0),
            (26.2 * math.cos(a), 26.2 * math.sin(a), 7.5),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 25.0),
            (24.0 * math.cos(a), 24.0 * math.sin(a), 36.0),
        ]
        shell = shell.cut(g.routed_round(points, radius))
    for phi, radius in ((85.0, 2.60), (325.0, 2.35), (205.0, 2.40)):
        x, y = radial_xy(26.2, phi)
        shell = shell.cut(g.cyl_z(radius, 4.0, x, y, 6.5))
    # Inward six-place service flange.  The 90-degree countersinks are fully
    # inside the rigid envelope and open onto the throat pilot plane.
    shell = shell.fuse(g.tube_z(26.30, 20.00, 1.20, z0=291.80))
    for phi in (30.0, 90.0, 150.0, 210.0, 270.0, 330.0):
        x, y = radial_xy(22.20, phi)
        cutter = g.make_clearance_countersink_cutter_z(
            3.30, 6.72, 2.20, 1.86, z0=291.34
        ).translate((x, y, 0.0))
        shell = shell.cut(cutter)
    return shell


def service_throat_shape() -> cq.Shape:
    throat = g.tube_z(26.3, 23.8, 103.0)
    throat = throat.fuse(g.tube_z(26.30, 20.00, 4.50, z0=0.0))
    for phi in (30.0, 90.0, 150.0, 210.0, 270.0, 330.0):
        x, y = radial_xy(22.20, phi)
        tap = g.make_tapped_hole_cutter_z(
            2.50, 4.30, thread_major_diameter_mm=3.0, z0=0.0
        ).translate((x, y, 0.0))
        throat = throat.cut(tap)
    throat = throat.cut(cq.Solid.makeCylinder(2.55, 8.6, cq.Vector(28.0, -4.3, 100.0), cq.Vector(0, 1, 0)))
    # Open hinge-web notch: the door knuckle is joined to the disk by a real
    # load-carrying web, and this matching throat pocket clears that web
    # through the full closed/open sweep.
    throat = throat.cut(g.box_center(6.0, 8.0, 6.0, 25.0, 0.0, 100.0))
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
    # Integral internal lanyard anchor.  In the closed state the line packs
    # beneath the door; after opening it exits through the aft mouth before
    # descending outside the throat wall.
    anchor = g.ring_y(18.0, 77.0, 3.0, 3.2, 2.0)
    anchor_web = g.box_center(3.2, 3.0, 2.0, 22.5, 0.0, 77.0)
    throat = throat.fuse(anchor).fuse(anchor_web)
    solids = throat.Solids()
    if len(solids) != 1 or not throat.isValid():
        raise ValueError(
            "Fixed service-throat hinge leaf must remain one cohesive valid part; "
            f"found {len(solids)} solids (valid={throat.isValid()})"
        )
    return solids[0]


def radial_detent_shape() -> cq.Shape:
    # GN 615.3-M3-KN-PFB catalog envelope: 8 mm threaded housing with the
    # spring-loaded ball at the inward end.  The small compression spring is
    # internal and is represented by the purchased assembly envelope rather
    # than as an unretained occurrence.
    housing = cq.Solid.makeCylinder(1.50, 8.0, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    ball = cq.Solid.makeSphere(1.48, cq.Vector(-0.35, 0, 0))
    return housing.fuse(ball)


def cartridge_shape() -> cq.Shape:
    body = g.cyl_z(9.3345, 74.0)
    dome = cq.Solid.makeSphere(9.3345, cq.Vector(0, 0, 74.0)).intersect(g.cyl_z(10.0, 9.0, z0=74.0))
    neck = g.cyl_z(4.75, 8.55, z0=74.0)
    shoulder = cq.Solid.makeCone(9.3345, 4.75, 4.0, cq.Vector(0, 0, 72.0), cq.Vector(0, 0, 1))
    return body.fuse(dome).fuse(shoulder).fuse(neck)


def cartridge_carrier_shape() -> cq.Shape:
    plate = g.cyl_z(20.5, 4.0, z0=-2.0)
    for x in (-9.5, 9.5):
        for y in (-9.5, 9.5):
            plate = plate.cut(g.cyl_z(9.55, 4.6, x, y, -2.3))
    for phi in (0.0, 90.0, 180.0, 270.0):
        x, y = radial_xy(18.1, phi)
        plate = plate.cut(g.cyl_z(1.65, 4.6, x, y, -2.3))
        # ISO 10642 90-degree seat on the aft carrier face.  The screw's
        # 3.36 mm-radius outer head face is flush at local z=+2.0 and its
        # r=1.50 shank junction lies 1.86 mm below that face.
        plate = plate.cut(cq.Solid.makeCone(
            1.50, 3.36, 1.86,
            cq.Vector(x, y, 0.14), cq.Vector(0.0, 0.0, 1.0),
        ))
    return plate


def booster_tube_shape() -> cq.Shape:
    tube = g.tube_z(6.5, 5.5, 430.0)
    # Thickened bosses are contained within the controlled 430 mm length.
    fwd = g.tube_z(6.5, 2.0, 6.0, z0=0.0)
    aft = g.tube_z(6.5, 2.0, 6.0, z0=424.0)
    return tube.fuse(fwd).fuse(aft)


def booster_forward_adapter_closure_shape() -> cq.Shape:
    """Ported forward closure: welded face cap plus piloted pressure spigot."""
    cap = g.cyl_z(6.40, 1.0)
    spigot = g.cyl_z(1.95, 3.2, z0=0.8)
    bore = g.cyl_z(0.65, 4.6, z0=-0.3)
    return cap.fuse(spigot).cut(bore)


def booster_aft_welded_closure_shape() -> cq.Shape:
    """Solid aft closure with an in-bore locating pilot and external weld lip."""
    # r=5.35 clears the r=19.5 routed-ring ID by 0.15 mm at the r=14
    # reservoir station while retaining a broad weld face over the r=2 boss.
    cap = g.cyl_z(5.35, 1.0)
    spigot = g.cyl_z(1.95, 3.2, z0=-3.0)
    return cap.fuse(spigot)


def ss_chs2_1_check_valve_shape() -> cq.Shape:
    """Controlled analytic installation BREP for Swagelok SS-CHS2-1.

    Opposed blind port bores stop at the central poppet/seat barrier so the
    isolation occurrence is physically closed in its normal state rather
    than represented as another generic open cylinder.
    """
    body = g.cyl_z(2.20, 3.0)
    wrench_hex = cq.Workplane("XY").polygon(6, 5.20).extrude(1.20).translate((0, 0, 0.90)).val()
    inlet_nut = g.cyl_z(2.70, 0.60)
    outlet_nut = g.cyl_z(2.70, 0.60, z0=2.40)
    inlet_ferrule = g.cyl_z(1.30, 0.35, z0=0.55)
    outlet_ferrule = g.cyl_z(1.30, 0.35, z0=2.10)
    witness = g.box_center(0.45, 1.00, 0.50, 2.25, 0.0, 1.50)
    valve = body.fuse(wrench_hex).fuse(inlet_nut).fuse(outlet_nut)
    valve = valve.fuse(inlet_ferrule).fuse(outlet_ferrule).fuse(witness)
    valve = valve.cut(g.cyl_z(0.65, 1.25, z0=-0.1))
    valve = valve.cut(g.cyl_z(0.65, 1.25, z0=1.85))
    return valve


def booster_band_shape() -> cq.Shape:
    band = g.tube_z(7.2, 6.50, 5.0, z0=-2.5)
    foot = g.box_center(5.15, 8.0, 5.0, 8.775, 0.0, 0.0)
    clearance_half = cq.Solid.makeCylinder(
        1.65, 4.2, cq.Vector(9.0, -4.2, 0.0), cq.Vector(0, 1, 0)
    )
    tapped_half = cq.Solid.makeCylinder(
        1.25, 4.3, cq.Vector(9.0, 0.0, 0.0), cq.Vector(0, 1, 0)
    )
    reservoir_clearance = g.cyl_z(6.65, 5.8, z0=-2.9)
    out = band.cut(g.box_center(3.0, 8.0, 4.0, 6.8, 0, 0)).fuse(foot).cut(reservoir_clearance)
    out = out.cut(clearance_half.fuse(tapped_half))
    body_clearance = g.cyl_z(25.35, 6.0, -14.0, 0.0, -3.0)
    return out.intersect(body_clearance)


def puncture_head_shape() -> cq.Shape:
    body = g.cyl_z(5.4, 5.8)
    bore = g.cyl_z(2.1, 6.2, z0=-0.2)
    needle = cq.Solid.makeCone(1.2, 0.15, 3.5, cq.Vector(0, 0, 0.0), cq.Vector(0, 0, -1))
    # The annular skirt reaches the cartridge terminal face at local
    # z=-4.65 without entering its neck envelope.  Three short radial needle
    # supports make the pressure terminal one connected exact solid while
    # preserving the annular seal passage.
    seal_skirt = g.tube_z(5.4, 4.0, 4.65, z0=-4.65)
    supports: list[cq.Shape] = []
    for phi in (0.0, 120.0, 240.0):
        a = math.radians(phi)
        supports.append(g.rod_between(
            (0.95 * math.cos(a), 0.95 * math.sin(a), -0.30),
            (4.05 * math.cos(a), 4.05 * math.sin(a), -0.30),
            0.25,
        ))
    out = body.cut(bore).fuse(needle).fuse(seal_skirt)
    for support in supports:
        out = out.fuse(support)
    solids = out.Solids()
    if len(solids) != 1 or not out.isValid():
        raise ValueError(
            f"Puncture head must remain one valid exact solid; "
            f"found {len(solids)} solids (valid={out.isValid()})"
        )
    return solids[0]


def manifold_shape() -> cq.Shape:
    block = g.cyl_z(20.0, 10.0, z0=-5.0)
    cartridge_centers = [(-9.5, -9.5), (9.5, -9.5), (9.5, 9.5), (-9.5, 9.5)]
    # Four blind cartridge inlets enter from the forward face and stop in a
    # sealed mid-plane collection gallery. The former axial cutters crossed
    # the complete block and left four unintended openings on the aft face.
    # Each diagonal gallery ends inside the block; the central outlet opens
    # only on the aft feed face.
    for x, y in cartridge_centers:
        block = block.cut(g.cyl_z(5.55, 4.4, x, y, -5.2))
        block = block.cut(g.cyl_z(2.2, 5.9, x, y, -5.3))
        block = block.cut(g.rod_between((0.0, 0.0, 0.0), (x, y, 0.0), 1.20))
    block = block.cut(g.cyl_z(1.01, 5.5, 0, 0, -0.2))
    # Three dedicated booster-collection ports at the occurrence-matched
    # reservoir clocks.  Exact route liners occupy these bores with 0.10 mm
    # radial clearance and terminate at the manifold aft face.
    for phi in (30.0, 150.0, 270.0):
        x, y = radial_xy(14.0, phi)
        block = block.cut(g.cyl_z(1.10, 5.6, x, y, -0.3))
    for phi in (0.0, 90.0, 180.0, 270.0):
        x, y = radial_xy(18.1, phi)
        tap = g.make_tapped_hole_cutter_z(
            2.50, 6.40, thread_major_diameter_mm=3.0, z0=-5.0
        ).translate((x, y, 0.0))
        block = block.cut(tap)
    solids = block.Solids()
    if len(solids) != 1 or not block.isValid():
        raise ValueError(
            "Sealed collection manifold must remain one valid exact solid; "
            f"found {len(solids)} solids (valid={block.isValid()})"
        )
    return solids[0]


def water_trigger_housing_shape() -> cq.Shape:
    housing = g.tube_z(7.0, 5.3, 58.0)
    # Exact bayonet-skirt cavity: 0.10 mm radial clearance to both the inner
    # neck and outer collar.  The former uninterrupted r=5.3..7.0 tube filled
    # the removable cap envelope rather than providing a machinable socket.
    housing = housing.cut(g.tube_z(6.90, 6.00, 6.20, z0=-0.10))
    housing = housing.fuse(
        g.make_service_cap_mating_neck_local(
            neck_outer_diameter_mm=12.0,
            cap_skirt_outer_diameter_mm=13.6,
            collar_outer_diameter_mm=14.6,
        )
    )
    # Port center is local z=40 (global z=540), coaxial with the controlled
    # shell gland.  The 4.10 mm reamed boss bore clears the 3.90 mm inlet tube;
    # the parts seat at the defined flange instead of overlapping cylinders.
    radial_outer = cq.Solid.makeCylinder(2.4, 9.0, cq.Vector(0, 5.0, 40.0), cq.Vector(0, 1, 0))
    radial_inner = cq.Solid.makeCylinder(2.05, 9.4, cq.Vector(0, 4.8, 40.0), cq.Vector(0, 1, 0))
    housing = housing.fuse(radial_outer).cut(radial_inner)
    for phi in (90.0, 210.0, 330.0):
        a = math.radians(phi)
        start = (6.8 * math.cos(a), 6.8 * math.sin(a), 8.0)
        end = (25.15 * math.cos(a), 25.15 * math.sin(a), 8.0)
        # The radial mounting arm is a bored structural tube, not solid stock
        # hidden around the M3 shank.  Its 3.30 mm clearance lumen leaves the
        # screw free until the controlled thread-minor annulus in the outer
        # boss; the 4.0 mm tube OD preserves a real load path to the housing.
        housing = housing.fuse(g.tube_between(start, end, 2.0, 1.65))
        housing = housing.fuse(
            g.tube_between(
                (20.5 * math.cos(a), 20.5 * math.sin(a), 8.0),
                (25.15 * math.cos(a), 25.15 * math.sin(a), 8.0),
                3.0, 1.25,
            )
        )
        housing = housing.cut(radial_cylinder(phi, 23.20, 2.30, 2.85, 8.0))
    # Stepped, integral Bowden termination at the aft face.  The fixed sheath
    # seats in the r=0.85 counterbore and the moving 0.60 mm wire continues
    # through the r=0.35 guide.  Both have 0.05 mm radial assembly clearance;
    # the bridge is above the replaceable bobbin service envelope.
    bowden_bridge = g.cyl_z(7.0, 3.0, z0=55.0)
    bowden_bridge = bowden_bridge.cut(g.cyl_z(0.35, 2.6, z0=54.8))
    bowden_bridge = bowden_bridge.cut(g.cyl_z(0.85, 0.8, z0=57.4))
    housing = housing.fuse(bowden_bridge)
    return housing


def valve_body_shape() -> cq.Shape:
    body = g.cyl_z(5.5, 22.0)
    body = body.cut(g.cyl_z(1.01, 22.4, z0=-0.2))
    branch = cq.Solid.makeCylinder(3.0, 11.0, cq.Vector(0, 0, 11.0), cq.Vector(1, 0, 0))
    branch = branch.cut(cq.Solid.makeCylinder(1.2, 11.4, cq.Vector(-0.2, 0, 11), cq.Vector(1, 0, 0)))
    body = body.fuse(branch)
    # The valve occurrence is clocked +90 degrees, so this 235-degree local
    # branch becomes the global 325-degree pilot corridor. Coaxial routing
    # from its end face clears both adjacent booster envelopes.
    pilot_axis = cq.Vector(math.cos(math.radians(235.0)), math.sin(math.radians(235.0)), 0.0)
    pilot_branch = cq.Solid.makeCylinder(1.65, 6.5, cq.Vector(0, 0, 11.0), pilot_axis)
    pilot_bore = cq.Solid.makeCylinder(0.90, 7.0, cq.Vector(0, 0, 11.0) - pilot_axis * 0.25, pilot_axis)
    body = body.fuse(pilot_branch).cut(pilot_bore)
    # Three radial mounting lands terminate on the FWD-RING-02 front face and
    # inner pilot diameter, giving the valve a real occurrence load path.
    for phi in (0.0, 120.0, 240.0):
        land = g.box_center(14.0, 2.0, 2.0, 12.5, 0.0, 21.0).rotate((0, 0, 0), (0, 0, 1), phi)
        body = body.fuse(land)
    body = body.fuse(g.cyl_z(5.0, 4.0, z0=22.0))
    body = body.cut(g.make_external_circlip_groove_cutter_z(
        10.0, 9.30, 1.0, z_center=24.5
    ))
    # The central M4 guide-lock screw is inserted from the forward side of
    # the spider.  A shallow axial tool/head relief in the valve's aft collar
    # removes the former 26.46 mm3 hardware collision while leaving the
    # circlip groove and outer reaction shoulder intact.
    body = body.cut(g.cyl_z(3.60, 2.0, z0=25.0))
    return body


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


def actuator_fixed_yoke_shape(eye_ro: float = 6.0,
                              installation_radius: float | None = None,
                              support_radius: float = 23.0) -> cq.Shape:
    out = None
    for yy in (-3.25, 3.25):
        ear = g.ring_y(0.0, 0.0, 2.0, eye_ro + 0.5, 2.18, yy)
        web = g.box_center(8.0, 2.0, 12.0, 3.0, yy, 2.0)
        piece = ear.fuse(web)
        out = piece if out is None else out.fuse(piece)
    bridge = g.box_center(8.0, 8.5, 2.0, 3.0, 0.0, 8.0)
    out = out.fuse(bridge)
    if installation_radius is not None:
        if not 0.0 < installation_radius < support_radius:
            raise ValueError("Actuator-yoke support radii are inconsistent")
        # The raw tongue deliberately extends beyond the longeron's r=23
        # inner surface, then is clipped by that exact cylindrical datum in
        # the occurrence-local frame.  This produces a conformal zero-gap,
        # zero-common-volume permanent-joint face for each installation
        # radius without letting a flat box corner enter longeron stock.
        reach = support_radius - installation_radius
        tongue = g.box_center(
            reach - 5.0, 4.0, 2.0,
            (reach + 7.0) / 2.0, 0.0, 8.0,
        )
        support_clip = g.cyl_z(
            support_radius, 20.0,
            x=-installation_radius, y=0.0, z0=-5.0,
        )
        out = out.fuse(tongue.intersect(support_clip))
    bore = cq.Solid.makeCylinder(2.18, 10.0, cq.Vector(0, -5.0, 0), cq.Vector(0, 1, 0))
    out = out.cut(bore)
    solids = out.Solids()
    if len(solids) != 1 or not out.isValid():
        raise ValueError(
            f"Actuator fixed yoke must be one valid exact solid; "
            f"found {len(solids)} solids (valid={out.isValid()})"
        )
    return solids[0]


def make_body_longeron(length: float) -> cq.Shape:
    # The four 18.669 mm cartridge envelopes require the full +/-9.5 mm
    # square pattern.  Move the three primary rails outboard into the annulus
    # between the cartridge envelope and shell ID while preserving greater
    # section area than the previous inward rail.
    return g.analytic_sector(25.25, 22.95, length, 0.0, 3.5)


def build_forward(b: R2Builder) -> None:
    path = "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY"
    taper_bore_nose = g.make_taper_pin_bore_x(3.0, 3.6, 30.0, z=170.0)
    nose_shape = cq.Solid.makeCone(1.5, 26.3, 170.0).cut(taper_bore_nose)
    nose = b.define("DF8-R2-NOSE-001", "A", "TUNGSTEN PENETRATOR NOSE WITH OCCURRENCE-MATCHED TAPERED REAMED HALF BORE", nose_shape,
                    "Tungsten heavy alloy", process="CNC turn and grind", color_key="tungsten")
    b.add(b.forward, path, nose, "NOSE-001", g.identity_loc(), "FIXED", "SHRINK_FIT_AND_TAPER_PIN", notes="Identity transform justified: top-level product datum origin.")

    ballast_shape = g.cyl_z(24.8, 166.0).cut(g.cyl_z(8.0, 166.4, z0=-0.2))
    ballast_shape = ballast_shape.cut(g.make_taper_pin_bore_x(3.0, 3.6, 30.0, z=0.0))
    ballast = b.define("DF8-R2-BALLAST-001", "A", "FORWARD TUNGSTEN BALLAST, SPINE SOCKET AND TAPERED REAMED HALF BORE", ballast_shape,
                       "Tungsten heavy alloy", process="CNC turn; wire-EDM socket", color_key="tungsten")
    b.add(b.forward, path, ballast, "BALLAST-001", g.translation_loc(0, 0, 170.0), "FIXED", "SHRINK_FIT_AND_TAPER_PIN")

    shell = b.define("DF8-R2-FWD-SHELL-001", "A", "FORWARD GRADE-9 TITANIUM SHELL WITH CONTROLLED WATER PORT",
                     forward_shell_with_port(), "Ti-3Al-2.5V Grade 9", process="Cold draw; laser port; finish hone", color_key="titanium")
    b.add(b.forward, path, shell, "FWD-SHELL-001", g.translation_loc(0, 0, 340.0), "FIXED", "LASER_WELDED_RING_JOINT")

    ring_plain_shape = g.tube_z(25.3, 19.5, 8.0, z0=-4.0)
    for phi in (0.0, 90.0, 180.0, 270.0):
        land = g.box_center(7.0, 6.0, 8.0, 18.1, 0.0, 0.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        x, y = radial_xy(18.1, phi)
        tap = g.cyl_z(1.25, 2.40, x, y, 1.80)
        ring_plain_shape = ring_plain_shape.fuse(land).cut(tap)
    ring_plain = b.define("DF8-R2-STRUCT-RING-PLAIN-001", "B", "PRIMARY STRUCTURAL TRANSITION RING WITH FOUR TAPPED CARRIER LANDS",
                          ring_plain_shape, "Ti-6Al-4V", process="Mill-turn; mill four integral lands; tap 4X M3", color_key="titanium")
    route_ring_shape = ring_with_axial_route_holes(
        8.0, arm_root_reliefs=True, route_transition="OUTWARD"
    )
    # Integral three-spoke circlip reaction cage.  The r=8.54 bore leaves
    # 0.04 mm radial running clearance to the catalog HEC-10-A4 envelope;
    # the collar reacts the retained valve shoulder into the structural ring
    # without a floating central component.
    circlip_collar = g.tube_z(9.20, 8.54, 1.20, z0=-1.60)
    for phi in (0.0, 120.0, 240.0):
        spoke = g.box_center(10.60, 1.20, 1.20, 14.30, 0.0, -1.0).rotate(
            (0, 0, 0), (0, 0, 1), phi
        )
        circlip_collar = circlip_collar.fuse(spoke)
    route_ring_shape = route_ring_shape.fuse(circlip_collar)
    # Occurrence-matched full-depth dowel passages through the routed-ring
    # arm windows.  These six bores follow the deployed stop-land axes and
    # eliminate the former 1.7743 mm3 per-dowel ring collision without
    # enlarging unrelated structural sectors.
    ring_frame = g.translation_loc(0.0, 0.0, repack.FWD_RING_02_Z_MM)
    for phi in (0.0, 120.0, 240.0):
        stop_loc = (
            g.arm_occurrence_loc(g.DEPLOYED_ANGLE, phi)
            * g.translation_loc(4.0, 0.0, -8.5)
            * g.translation_loc(-0.4, 0.0, -4.0)
        )
        for y in (-8.0, 8.0):
            dowel_loc = stop_loc * g.translation_loc(7.0, y, 3.05)
            cutter = g.cyl_z(1.55, 8.40, z0=-0.20)
            route_ring_shape = route_ring_shape.cut(
                g.moved(cutter, ring_frame.inverse * dowel_loc)
            )
    route_ring = b.define(
        "DF8-R2-STRUCT-RING-ROUTED-001", "B",
        "STRUCTURAL RING WITH ROUTE PASSAGES, ARM RELIEFS AND FULLFLOW CIRCLIP REACTION CAGE",
        route_ring_shape, "Ti-6Al-4V",
        process="Mill-turn; jig-bore routes; machine integral three-spoke valve-retention cage",
        color_key="titanium",
    )
    for idx, z in enumerate((repack.FWD_RING_01_Z_MM, repack.FWD_RING_02_Z_MM), 1):
        p = ring_plain if idx == 1 else route_ring
        b.add(b.forward, path, p, f"FWD-RING-{idx:02d}", g.translation_loc(0, 0, z), "FIXED", "LASER_WELDED_RING_JOINT")

    fwd_longeron_length = repack.FWD_RING_02_Z_MM - repack.FWD_RING_01_Z_MM - 8.0
    fwd_longeron = b.define("DF8-R2-FWD-LONGERON-001", "C", "SHORTENED FORWARD PRIMARY LOAD-PATH LONGERON",
                            make_body_longeron(fwd_longeron_length), "Ti-6Al-4V", process="5-axis mill; trim both ring butt faces", color_key="titanium")
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, 344.0)
        b.add(b.forward, path, fwd_longeron, f"FWD-LONGERON-{idx}", loc, "FIXED", "WELDED_TO_STRUCTURAL_RINGS")

    cart = b.define("LELAND-81121", "A", "LELAND 81121 12 G CO2 CARTRIDGE", cartridge_shape(),
                    "Steel pressure cartridge", "BUY", "Leland Gas Technologies", "DRAWING_DERIVED",
                    mass_kg=0.045, source_url="https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
                    purchase_url="https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
                    notes="Incoming acceptance: 12 g CO2, 0.735 in body diameter, 3.250 in overall length, 3/8-24 neck, lot traceability and CoC; occurrence-matched puncture-head thread and pre-puncture clearance are inspected.", color_key="steel")
    carrier = b.define("DF8-R2-CARTRIDGE-CARRIER-001", "A", "FOUR-CARTRIDGE DOUBLE-PLATE CARRIER", cartridge_carrier_shape(),
                       "7075-T6 aluminum", process="5-axis mill", color_key="aluminum")
    b.add(b.forward, path, carrier, "CARTRIDGE-CARRIER-FWD", g.translation_loc(0, 0, 346.0), "FIXED", "BOLTED_TO_FORWARD_RING")
    b.add(b.forward, path, carrier, "CARTRIDGE-CARRIER-AFT", g.translation_loc(0, 0, 435.0), "FIXED", "BOLTED_TO_MANIFOLD")
    positions = [(-9.5, -9.5), (9.5, -9.5), (9.5, 9.5), (-9.5, 9.5)]
    for idx, (x, y) in enumerate(positions, 1):
        oid = b.add(b.forward, path, cart, f"CO2-CARTRIDGE-{idx}", g.translation_loc(x, y, 348.0), "CONSUMED", "THREADED_AND_CLAMPED")
        b.connect(f"CONN-CART-{idx}", oid, "CARTRIDGE-CARRIER-FWD", "CYLINDER_BODY_OD", f"CARRIER_BORE_{idx}",
                  "RADIAL_CLAMP", "0", "CARRIER-FWD/AFT", "PUNCTURE_HEAD SHOULDER", "TWO SPACED CARRIER BORES",
                  "THREAD INTO PUNCTURE HEAD", "NONE", "COLLECTION MANIFOLD", "UNTHREAD AFTER DISCHARGE", "Joint geometry report")

    manifold = b.define("DF8-R2-COLLECTION-MANIFOLD-001", "A", "FOUR-PORT COLLECTION MANIFOLD WITH BORED PASSAGES",
                        manifold_shape(), "316 stainless steel", process="5-axis mill; gun drill; proof test", color_key="stainless")
    b.add(b.forward, path, manifold, "COLLECTION-MANIFOLD-001", g.translation_loc(0, 0, 442.0), "FIXED", "BOLTED_TO_CARRIER")
    ph = b.define("DF8-R2-PUNCTURE-HEAD-001", "A", "CARTRIDGE PUNCTURE HEAD WITH CONTROLLED NEEDLE", puncture_head_shape(),
                  "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    for idx, (x, y) in enumerate(positions, 1):
        b.add(b.forward, path, ph, f"PUNCTURE-HEAD-{idx}", g.translation_loc(x, y, 435.2), "FIXED", "THREADED_MANIFOLD_PORT")

    booster = b.define("DF8-R2-BOOSTER-RESERVOIR-001", "A", "13 OD X 11 ID X 430 BOOSTER RESERVOIR WITH END BOSSES",
                       booster_tube_shape(), "316 stainless steel", process="ASTM A269 seamless tube; orbital-weld bosses; 34.5 MPa hydro proof; dye penetrant",
                       notes="Controlled MAKE item: 13.00 OD, 11.00 ID, 430.00 OAL; serialized leak and hydro-proof acceptance.", color_key="stainless")
    band = b.define("DF8-R2-BOOSTER-BAND-001", "A", "CAPTIVE BOOSTER SUPPORT BAND WITH M3 TAB", booster_band_shape(),
                    "PEEK", process="Machine from PEEK", color_key="peek")
    booster_fwd_closure = b.define(
        "DF8-R2-BOOSTER-FWD-ADAPTER-CLOSURE-001", "A",
        "PORTED FORWARD BOOSTER CLOSURE WITH WELD LIP AND VALVE ADAPTER",
        booster_forward_adapter_closure_shape(), "316 stainless steel",
        process="Swiss turn; orbital weld lip; passivate; helium leak and 34.5 MPa hydro proof",
        notes="Separate pressure-boundary occurrence; integral pilot enters the reservoir boss with controlled clearance while the full face weld closes the annulus.",
        color_key="stainless",
    )
    booster_aft_closure = b.define(
        "DF8-R2-BOOSTER-AFT-WELDED-CLOSURE-001", "A",
        "SOLID AFT BOOSTER CLOSURE WITH LOCATING PILOT",
        booster_aft_welded_closure_shape(), "316 stainless steel",
        process="Swiss turn; orbital closure weld; passivate; PT, helium leak and 34.5 MPa hydro proof",
        notes="Separate solid pressure-boundary occurrence; no open-ended-cylinder representation remains in the installed reservoir.",
        color_key="stainless",
    )
    booster_valve = b.define(
        "SS-CHS2-1", "CATALOG", "SWAGELOK 316 SS POPPET CHECK VALVE, 1/8-IN TUBE FITTINGS, 6000 PSIG",
        ss_chs2_1_check_valve_shape(),
        "316 stainless purchased check-valve assembly", "BUY", "Swagelok", "DRAWING_DERIVED",
        mass_kg=0.025,
        source_url="https://products.swagelok.com/en/c/fixed-pressure/p/SS-CHS2-1",
        purchase_url="https://products.swagelok.com/en/c/fixed-pressure/p/SS-CHS2-1",
        notes="Exact SS-CHS2-1 procurement identity; 316 SS poppet check valve with 1/8-in tube fittings and 6000 psig/413 bar catalog rating. The compact analytic exterior is a controlled installation BREP; incoming identity, rating, cracking direction and leak test are verified.",
        color_key="stainless",
    )
    booster_collection_line_length = repack.BOOSTER_BODY_START_Z_MM - 4.0 - 444.5
    booster_collection_line_shape = g.tube_z(1.0, 0.65, booster_collection_line_length)
    booster_collection_line_shape = booster_collection_line_shape.fuse(g.tube_z(1.05, 0.65, 0.30))
    booster_collection_line_shape = booster_collection_line_shape.fuse(
        g.tube_z(1.05, 0.65, 0.30, z0=booster_collection_line_length - 0.30)
    )
    booster_collection_line = b.define(
        "DF8-R2-BOOSTER-COLLECTION-LINE-001", "A",
        "LONG 316L BOOSTER COLLECTION LINE WITH INTEGRAL FERRULE ENDS",
        booster_collection_line_shape, "316 stainless steel",
        process="ASTM A269 capillary; face ends; form integral ferrules; passivate; helium leak and 34.5 MPa proof",
        notes="Occurrence-specific line bridges one dedicated manifold port to one SS-CHS2-1 inlet with 0.10 mm manifold-bore clearance.",
        color_key="route",
    )
    for idx, phi in enumerate((30.0, 150.0, 270.0), 1):
        x, y = radial_xy(14.0, phi)
        booster_z = repack.BOOSTER_BODY_START_Z_MM
        b.add(b.forward, path, booster, f"BOOSTER-{idx}", g.translation_loc(x, y, booster_z), "FIXED", "THREE_SPACED_PEEK_BANDS")
        b.add(b.forward, path, booster_fwd_closure, f"BOOSTER-FWD-CLOSURE-{idx}",
              g.translation_loc(x, y, booster_z - 1.0), "FIXED", "ORBITAL_WELDED_PORTED_CLOSURE")
        b.add(b.forward, path, booster_aft_closure, f"BOOSTER-AFT-CLOSURE-{idx}",
              g.translation_loc(x, y, booster_z + 430.0), "FIXED", "ORBITAL_WELDED_SOLID_CLOSURE")
        b.add(b.forward, path, booster_valve, f"BOOSTER-ISOLATION-VALVE-{idx}",
              g.translation_loc(x, y, booster_z - 4.0), "FIXED", "TUBE_FITTED_TO_PORTED_CLOSURE")
        collection_oid = b.add(
            b.forward, path, booster_collection_line, f"BOOSTER-COLLECTION-LINE-{idx}",
            g.translation_loc(x, y, 444.5), "FIXED", "FORMED_ROUTE_WITH_CAPTURED_FERRULES",
        )
        b.add_route_record(
            collection_oid, "COLLECTION-MANIFOLD-001", f"BOOSTER-ISOLATION-VALVE-{idx}",
            "Integral occurrence-matched 1/8-in ferrule ends",
            f"Dedicated axial manifold port at booster clock {phi:.0f} degrees",
            "Continuous exact manifold bore plus valve inlet pilot",
            2.0, 0.0, "34.5 MPa proof / 41.3 MPa valve catalog rating", "COMPLETE",
            maximum_endpoint_gap_mm=0.11,
            termination_occurrence_ids=[], support_occurrence_ids=[],
            integral_terminations=True, integral_support=True,
            penetration_occurrence_ids=[], integral_penetrations=True,
        )
        for bi, z in enumerate((1230.0, 1295.0, 1360.0), 1):
            loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(14.0, 0, z)
            b.add(b.forward, path, band, f"BOOSTER-BAND-{idx}-{bi}", loc, "FIXED", "M3_BOLTED_CLAMP")

    trigger = b.define("DF8-R2-WATER-TRIGGER-HSG-001", "A", "CENTRAL WATER-SENSITIVE TRIGGER HOUSING", water_trigger_housing_shape(),
                       "Acetal", process="CNC turn and mill", color_key="black")
    bobbin = b.define("V80040", "A", "HALKEY-ROBERTS WATER-SENSITIVE BOBBIN", g.cyl_z(5.0, 18.0),
                      "Water-sensitive media", "BUY", "Nordson MEDICAL / Halkey-Roberts", "DRAWING_DERIVED",
                      mass_kg=0.001696460,
                      source_url="https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-V80040-Bobbin-Instructions-For-Use.pdf",
                      purchase_url="https://fluid-components.nordsonmedical.com/Resources/Orders/",
                      notes="Exact V80040 identity; controlled incoming inspection verifies the 10 mm diameter by 18 mm modeled service envelope, lot traceability, and current Nordson/Halkey-Roberts IFU revision.", color_key="peek")
    b.add(b.forward, path, trigger, "WATER-TRIGGER-HSG-001", g.translation_loc(0, 0, repack.WATER_TRIGGER_Z_MM), "FIXED", "BOLTED_TO_CENTRAL_CARRIER")
    b.add(b.forward, path, bobbin, "WATER-BOBBIN-001", g.translation_loc(0, 0, repack.WATER_TRIGGER_Z_MM + 20.0), "CONSUMED", "CAPTIVE_TRIGGER_CUP")

    inlet_shape = g.tube_between((0, 0, 0), (23.5, 0, 0), 1.95, 1.45)
    inlet_shape = inlet_shape.fuse(g.ring_x(0, 0, 1.0, 4.0, 2.1, 19.8))
    inlet_shape = inlet_shape.fuse(g.ring_x(0, 0, 0.8, 4.0, 2.1, 22.2))
    inlet = b.define("DF8-R2-WATER-INLET-001", "A", "RADIAL FLOOD INLET, GLAND AND ANTI-DEBRIS SCREEN",
                     inlet_shape,
                     "316 stainless steel", process="Microtube form and braze", color_key="stainless")
    inlet_loc = g.rotation_loc((0, 0, 1), 90.0) * g.translation_loc(5.0, 0.0, repack.WATER_TRIGGER_Z_MM + 40.0)
    b.add(b.forward, path, inlet, "WATER-INLET-001", inlet_loc, "FIXED", "RADIAL_GLAND_AND_SCREEN")
    b.add_route_record("WATER-INLET-001", "EXTERNAL_WATER", "WATER-TRIGGER-HSG-001",
                       "Integral screen flange / housing O-ring nipple", "FWD-SHELL radial Ø4.30 mm port",
                       "Integral brazed gland", 20.0, 0.0, "Flood path, non-pressure", "COMPLETE",
                       integral_support=True)

    valve = b.define("DF8-R2-FULLFLOW-VALVE-001", "A", "DIRECT FULL-FLOW VALVE WITH BORED AXIAL AND RADIAL PORTS", valve_body_shape(),
                     "17-4PH stainless steel", process="Swiss turn; cross-drill; lap", color_key="steel")
    b.add(b.forward, path, valve, "FULLFLOW-VALVE-001", g.rotation_loc((0, 0, 1), 90.0) * g.translation_loc(0, 0, repack.FULLFLOW_VALVE_Z_MM), "MOVING", "GUIDED_SPOOL", "1 AXIAL")

    # The collection manifold previously had no physical pressure article to
    # the full-flow valve.  This formed 316L feed seats on the manifold's
    # central port collar, follows the clear inter-booster corridor, and
    # terminates on the valve's axial inlet shoulder.  Three spring clips are
    # real separate occurrences laser-welded to the shell inner land.
    feed_phi = 70.0
    feed_radius = 21.0
    feed_length = repack.FULLFLOW_VALVE_Z_MM - 447.0
    feed_shape = g.planar_tangent_routed_round(
        [(0.0, 0.0), (0.0, 12.0), (feed_radius, 33.0),
         (feed_radius, feed_length - 33.0), (0.0, feed_length - 12.0), (0.0, feed_length)],
        1.00, 0.65, bend_radius=6.0, clock_deg=feed_phi,
    )
    feed_solids = feed_shape.Solids()
    if len(feed_solids) != 1 or not feed_shape.isValid():
        raise ValueError(
            "Manifold feed must remain one valid exact solid; "
            f"found {len(feed_solids)} solids (valid={feed_shape.isValid()})"
        )
    feed = b.define(
        "DF8-FINAL-MANIFOLD-FULLFLOW-FEED-001", "A",
        "TERMINATED COLLECTION-MANIFOLD TO FULL-FLOW VALVE FEED",
        feed_solids[0], "ASTM A269 TP316L seamless capillary tube", "MAKE",
        "STINGRAY controlled pressure-route drawing", "DRAWING_DERIVED",
        mass_kg=0.0070,
        process=(
            "CNC form; prepare occurrence-matched direct-braze tube ends; "
            "passivate; helium leak and 20.7 MPa hydro proof"
        ),
        notes=(
            "2.00 mm OD x 0.35 mm wall exact formed feed with direct-braze end "
            "preparations; three occurrence-specific welded spring supports."
        ),
        color_key="route",
    )
    feed_id = b.add(
        b.forward, path, feed, "ROUTE-MANIFOLD-FEED-001",
        g.translation_loc(0.0, 0.0, 447.0), "FIXED",
        "FORMED_PRESSURE_ROUTE_WITH_DIRECT_BRAZE_ENDS", "0",
    )

    clip_ring = g.tube_z(1.80, 1.05, 4.0, z0=-2.0)
    clip_ring = clip_ring.cut(g.box_center(2.10, 0.80, 4.8, -1.05, 0.0, 0.0))
    clip_tab = g.box_center(2.74, 1.00, 4.0, 2.97, 0.0, 0.0)
    clip_shape = clip_ring.fuse(clip_tab)
    clip_solids = clip_shape.Solids()
    if len(clip_solids) != 1 or not clip_shape.isValid():
        raise ValueError(
            "Manifold-feed spring support must remain one valid exact solid; "
            f"found {len(clip_solids)} solids (valid={clip_shape.isValid()})"
        )
    feed_clip = b.define(
        "DF8-FINAL-MANIFOLD-FEED-SPRING-CLIP-001", "A",
        "LASER-WELDED TITANIUM SPRING CLIP FOR MANIFOLD FEED",
        clip_solids[0], "Ti-6Al-4V spring temper", "MAKE",
        "STINGRAY controlled route-support drawing", "DRAWING_DERIVED",
        mass_kg=0.000153628,
        process=(
            "Wire-EDM spring throat; form; stress relieve; laser weld radial "
            "tab to prepared shell inner land; snap-install tube; borescope inspect"
        ),
        notes="0.05 mm nominal tube running clearance and 0.01 mm shell weld-land stand-off.",
        color_key="titanium",
    )
    support_ids: list[str] = []
    for index, z in enumerate((650.0, 900.0, 1100.0), start=1):
        clip_id = f"MANIFOLD-FEED-CLAMP-{index}"
        support_ids.append(clip_id)
        b.add(
            b.forward, path, feed_clip, clip_id,
            g.rotation_loc((0, 0, 1), feed_phi)
            * g.translation_loc(feed_radius, 0.0, z),
            "FIXED", "WELDED_SPRING_ROUTE_SUPPORT", "0",
        )
    b.add_route_record(
        feed_id, "COLLECTION-MANIFOLD-001", "FULLFLOW-VALVE-001",
        "Occurrence-matched direct-braze tube-end preparations",
        "No wall penetration; protected forward-body internal corridor",
        "Three laser-welded titanium spring clips on the shell inner land",
        20.0, 0.0, "20.7 MPa proof", "COMPLETE",
        maximum_endpoint_gap_mm=0.02,
        termination_occurrence_ids=[], support_occurrence_ids=support_ids,
        integral_terminations=True, integral_support=False,
        penetration_occurrence_ids=[], integral_penetrations=True,
    )


def add_arm_hardware(b: R2Builder, arm_index: int, phi: float, theta: float, arm: g.PartDef,
                     carrier: g.PartDef, pivot_pin: g.PartDef, bushing: g.PartDef, washer: g.PartDef,
                     pivot_clip: g.PartDef, link: g.PartDef, link_pin: g.PartDef, link_clip: g.PartDef,
                     stop_pad: g.PartDef, fixed_stop: g.PartDef, stow_dog: g.PartDef,
                     stow_dog_guide: g.PartDef, stow_spring: g.PartDef,
                     transport_pin: g.PartDef, transport_keeper: g.PartDef,
                     lock_dog: g.PartDef,
                     lock_spring: g.PartDef, lock_bushing: g.PartDef) -> None:
    path = f"300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/33{arm_index}_ARM_{arm_index}_ASSY"
    arm_loc = g.arm_occurrence_loc(theta, phi)
    b.add(b.arm_module, path, arm, f"ARM-{arm_index}", arm_loc, "MOVING", "REVOLUTE", "1 ROTATION ABOUT 8 MM PIVOT")
    carrier_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(g.PIVOT_R, 0, g.PIVOT_Z)
    b.add(b.arm_module, path, carrier, f"PIVOT-CARRIER-{arm_index}", carrier_loc, "FIXED", "WELDED_AND_DOWELLED")
    b.add(b.arm_module, path, pivot_pin, f"PIVOT-PIN-{arm_index}", carrier_loc * g.translation_loc(0, -10.25, 0), "FIXED", "SHOULDER_PIN_WITH_SPIRAL_RING")
    for side, yy in enumerate((-4.75, 4.75), 1):
        loc = carrier_loc * g.translation_loc(0, yy, 0)
        b.add(b.arm_module, path, bushing, f"PIVOT-BUSH-{arm_index}-{side}", loc, "FIXED", "PRESS_FIT_IN_ARM_BOSS")
    for side, yy in enumerate((-5.90, 5.90), 1):
        loc = carrier_loc * g.translation_loc(0, yy, 0)
        b.add(b.arm_module, path, washer, f"PIVOT-WASHER-{arm_index}-{side}", loc, "FIXED", "CAPTIVE_ON_PIVOT_SHOULDER")
    clip_loc = carrier_loc * g.translation_loc(0, 9.45, 0)
    b.add(b.arm_module, path, pivot_clip, f"PIVOT-CLIP-{arm_index}", clip_loc, "FIXED", "EXTERNAL_GROOVE")

    kin = g.kinematic(theta)
    for li, yy in enumerate((-1.75, 1.75), 1):
        l_loc = g.link_occurrence_loc(theta, yy, phi)
        b.add(b.arm_module, path, link, f"LINK-{arm_index}-{li}", l_loc, "MOVING", "TWO_REVOLUTE_PIN_JOINTS", "PLANAR FOUR-BAR")
    # One full-span pin secures both link plates at each end; each has a modeled retainer.
    bell_local = g.translation_loc(g.BELL_U, 0, g.BELL_V)
    bell_global = arm_loc * bell_local
    crosshead_pin_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(g.CROSSHEAD_R, -6.4, kin["crosshead_z"])
    bell_pin_loc = bell_global * g.translation_loc(0, -6.4, 0)
    for end, loc in (("BELL", bell_pin_loc), ("CROSSHEAD", crosshead_pin_loc)):
        b.add(b.arm_module, path, link_pin, f"LINK-PIN-{arm_index}-{end}", loc, "MOVING", "CLEVIS_PIN_WITH_E_RING")
        b.add(b.arm_module, path, link_clip, f"LINK-CLIP-{arm_index}-{end}", loc * g.translation_loc(0, 12.0, 0), "MOVING", "EXTERNAL_GROOVE")

    pad_loc = arm_loc * g.translation_loc(4.0, 0, -8.5)
    b.add(b.arm_module, path, stop_pad, f"ARM-STOP-PAD-{arm_index}", pad_loc, "MOVING", "DOVETAIL_AND_TWO_M3_SCREWS")
    stop_pose = g.arm_occurrence_loc(g.DEPLOYED_ANGLE, phi) * g.translation_loc(4.0, 0, -8.5)
    stop_loc = stop_pose * g.translation_loc(-0.4, 0, -4.0)
    b.add(b.arm_module, path, fixed_stop, f"FIXED-STOP-{arm_index}", stop_loc, "FIXED", "DOWEL_AND_TWO_M3_SCREWS")
    dog_r = 17.0 if theta < 0.1 else 13.5
    dog_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(dog_r, 0, g.PIVOT_Z + g.ARM_LENGTH - 3.5)
    b.add(b.arm_module, path, stow_dog, f"STOW-DOG-{arm_index}", dog_loc, "MOVING", "RADIAL_GUIDE_AND_RETURN_SPRING", "1 RADIAL TRANSLATION")
    guide_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, g.PIVOT_Z + g.ARM_LENGTH - 3.5)
    b.add(b.arm_module, path, stow_dog_guide, f"STOW-DOG-GUIDE-{arm_index}", guide_loc,
          "FIXED", "BOLTED_TO_AFT_ROUTE_RING")
    b.add(b.arm_module, path, stow_spring, f"STOW-DOG-SPRING-{arm_index}",
          guide_loc * g.translation_loc(11.17, 0.0, 0.0) * g.rotation_loc((0, 1, 0), 90.0),
          "FLEXIBLE", "CAPTURED_STOW_DOG_RETURN_SPRING", "AXIAL COMPRESSION")
    inhibit_y = 3.40 if b.deployed else -3.0
    b.add(b.arm_module, path, transport_pin, f"STOW-DOG-INHIBIT-PIN-{arm_index}",
          guide_loc * g.translation_loc(17.0, inhibit_y, 0.0),
          "MOVING", "WITHDRAWABLE_TRANSPORT_INHIBIT_PIN", "1 AXIAL TRANSLATION")
    b.add(b.arm_module, path, transport_keeper, f"STOW-DOG-INHIBIT-KEEPER-{arm_index}",
          guide_loc * g.translation_loc(17.0, inhibit_y + 5.425, 0.0),
          "MOVING", "EXTERNAL_GROOVE_RETAINER", "1 AXIAL TRANSLATION WITH PARENT PIN")

    # Spring-driven automatic deployed lock.  The dog remains retracted in
    # its fixed-stop guide until the occurrence-specific pad bore aligns at
    # 80 degrees, then advances 0.30 mm into that bore.  The small coaxial
    # spring is captive between the dog head and the guide's closed outer seat.
    lock_y = LOCK_DEPLOYED_DOG_Y_MM if b.deployed else LOCK_RETRACTED_DOG_Y_MM
    b.add(b.arm_module, path, lock_dog, f"LOCK-DOG-{arm_index}",
          stop_loc * g.translation_loc(0.4, lock_y, 4.0), "MOVING",
          "SPRING_DRIVEN_GUIDED_DEPLOYED_LOCK", "1 TRANSLATION")
    b.add(b.arm_module, path, lock_spring, f"LOCK-SPRING-{arm_index}",
          stop_loc * g.translation_loc(0.4, LOCK_SPRING_OUTER_SEAT_Y_MM, 4.0)
          * g.rotation_loc((1, 0, 0), 90.0),
          "FLEXIBLE", "CAPTURED_LOCK_RETURN_SPRING", "AXIAL COMPRESSION")
    b.add(b.arm_module, path, lock_bushing, f"LOCK-BUSHING-{arm_index}",
          stop_loc * g.translation_loc(0.4, LOCK_BUSHING_Y_MM, 4.35),
          "FIXED", "PRESS_FIT_OUTER_LOCK_GUIDE_RETAINER")


def build_arm_module(b: R2Builder) -> None:
    path = "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY"
    theta = g.DEPLOYED_ANGLE if b.deployed else 0.0
    predicted_crosshead_z = g.kinematic(theta)["crosshead_z"]
    predicted_spring_length = g.SPRING_DEPLOYED if b.deployed else g.SPRING_STOWED
    predicted_fixed_seat_z = predicted_crosshead_z + predicted_spring_length + 9.75
    fixed_sector = b.define("DF8-R2-FIXED-SECTOR-001", "A", "ANALYTIC CYLINDRICAL FIXED BODY SECTOR", g.make_fixed_sector_local(),
                            "Ti-6Al-4V", process="Hot form and 5-axis trim", color_key="titanium")
    # Sector 3 carries the two radial backup-guide screws.  Machine
    # occurrence-specific inward-open head pockets at their exact axial
    # stations; the screw heads seat on the inner counterbore shoulders and
    # no longer occupy intact sector stock.
    fixed_sector_3_shape = g.make_fixed_sector_local()
    for local_z in (11.75, predicted_fixed_seat_z - repack.ARM_STRUCTURE_START_Z_MM):
        head_pocket = cq.Solid.makeCylinder(
            2.85, 3.45, cq.Vector(23.95, 0.0, local_z), cq.Vector(1, 0, 0)
        )
        fixed_sector_3_shape = fixed_sector_3_shape.cut(head_pocket)
    fixed_sector_3 = b.define(
        "DF8-R2-BACKUP-ACCESS-FIXED-SECTOR-003", "B",
        "FIXED SECTOR 3 WITH TWO RADIAL M3 BACKUP-GUIDE HEAD POCKETS",
        fixed_sector_3_shape, "Ti-6Al-4V",
        process="Hot form; 5-axis trim; occurrence-match mill two inward-open M3 head pockets",
        color_key="titanium",
    )
    longeron = b.define("DF8-R2-ROUTED-LONGERON-001", "A", "PRIMARY LONGERON WITH TWO JIG-BORED ROUTE CHANNELS", g.make_longeron_local(),
                        "Ti-6Al-4V", process="5-axis mill and jig bore", color_key="titanium")
    longeron_3_shape = g.make_longeron_local()
    for local_z in (11.75, predicted_fixed_seat_z - repack.ARM_STRUCTURE_START_Z_MM):
        hole_radius = 2.55
        longeron_3_shape = longeron_3_shape.cut(cq.Solid.makeCylinder(
            hole_radius, 1.8, cq.Vector(22.7, 0.0, local_z), cq.Vector(1, 0, 0)
        ))
    longeron_3 = b.define(
        "DF8-R2-BACKUP-GUIDE-LONGERON-003", "A",
        "PRIMARY LONGERON 3 WITH TWO RADIAL BACKUP-GUIDE M3 CLEARANCE BORES",
        longeron_3_shape, "Ti-6Al-4V",
        process="5-axis mill; jig bore routes; drill 2X radial M3 clearance",
        color_key="titanium",
    )
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, repack.ARM_STRUCTURE_START_Z_MM)
        selected_sector = fixed_sector_3 if idx == 3 else fixed_sector
        b.add(b.arm_module, path, selected_sector, f"FIXED-SECTOR-{idx}", loc, "FIXED", "WELDED_TO_LONGERON")
        selected_longeron = longeron_3 if idx == 3 else longeron
        b.add(b.arm_module, path, selected_longeron, f"ARM-LONGERON-{idx}", loc, "FIXED", "WELDED_BETWEEN_ROUTE_RINGS")

    termination_ring_shape = ring_with_axial_route_holes(8.0, arm_root_reliefs=False)
    termination_cage = g.tube_z(9.20, 8.54, 1.20, z0=-1.60)
    for phi in (0.0, 120.0, 240.0):
        termination_cage = termination_cage.fuse(
            g.box_center(10.60, 1.20, 1.20, 14.30, 0.0, -1.0).rotate(
                (0, 0, 0), (0, 0, 1), phi
            )
        )
    termination_ring_shape = termination_ring_shape.fuse(termination_cage)
    for phi in (30.0, 150.0, 270.0):
        x, y = radial_xy(14.0, phi)
        termination_ring_shape = termination_ring_shape.cut(g.cyl_z(6.8, 9.0, x, y, -4.5))
    termination_ring = b.define(
        "DF8-FORWARD-ARM-TERMINATION-RING-001", "A",
        "ARM MODULE AFT STRUCTURAL RING WITH THREE PRESSURE-RESERVOIR PASSAGES",
        termination_ring_shape, "Ti-6Al-4V",
        process="Mill-turn; jig-bore three reservoir passages and three service routes",
        color_key="titanium",
    )
    b.add(b.arm_module, path, termination_ring, "ARM-TERMINATION-RING-001",
          g.translation_loc(0, 0, repack.ARM_TERMINATION_RING_Z_MM), "FIXED", "LASER_WELDED_RING_JOINT")

    transition_shell = b.define(
        "DF8-FORWARD-ARM-AFT-REPACK-SHELL-001", "A",
        "AFT REPACK BAY GRADE-9 TITANIUM SHELL",
        repack_transition_shell_shape(), "Ti-3Al-2.5V Grade 9",
        process="Cold draw; trim; laser weld to structural rings; machine water-service port",
        color_key="titanium",
    )
    transition_start = repack.ARM_TERMINATION_RING_Z_MM + 4.0
    b.add(b.arm_module, path, transition_shell, "AFT-REPACK-SHELL-001",
          g.translation_loc(0, 0, transition_start), "FIXED", "LASER_WELDED_RING_JOINT")

    trim_length = 155.0
    trim_shape = g.cyl_z(6.512850623, trim_length)
    for local_z in (3.0, trim_length - 3.0):
        for phi in (90.0, 210.0, 330.0):
            x = 25.35 * math.cos(math.radians(phi))
            y = 25.35 * math.sin(math.radians(phi))
            trim_shape = trim_shape.fuse(g.rod_between((0.0, 0.0, local_z), (x, y, local_z), 0.80))
    trim_ballast = b.define(
        "DF8-FORWARD-ARM-CG-TRIM-BALLAST-001", "A",
        "CENTERED AFT CG TRIM BALLAST WITH SIX INTEGRAL RETENTION ARMS",
        trim_shape.clean(), "Tungsten heavy alloy", "MAKE", "STINGRAY custom",
        "EXACT_ANALYTIC", mass_kg=0.351133873274735,
        process="CNC turn; wire-EDM integral retention arms; six-place qualified shell joint",
        notes="Mass and axial station are controlled to restore the accepted baseline STOWED axial CG and transverse inertia after the forward-arm repack.",
        color_key="tungsten",
    )
    b.add(b.arm_module, path, trim_ballast, "CG-TRIM-BALLAST-001",
          g.translation_loc(0, 0, 1257.5), "FIXED", "SIX_ARM_QUALIFIED_SHELL_JOINT")

    arm = b.define("DF8-R2-ARM-BLADE-001", "C", "733.806 MM SMOOTH ANALYTIC HOLLOW OML ARM WITH SWEPT STOP-HARDWARE RELIEFS", g.make_arm_part_local(),
                   "Ti-6Al-4V", process="Hot form; 5-axis machine; laser weld; CMM inspect",
                   notes="Analytic cylindrical OML; no planar patch tiling or mesh-derived surfaces; one-degree swept service corridors clear the fixed-stop screw and dowel envelopes.", color_key="titanium")
    carrier_shape = g.make_pivot_carrier_local()
    # Occurrence-matched oblique bores for the fixed-stop side lands.  The
    # stop is clocked in the deployed-arm frame, so its +Z fastener axes are
    # transformed into the common carrier datum before authoring the holes.
    carrier_frame = g.translation_loc(g.PIVOT_R, 0.0, g.PIVOT_Z)
    stop_frame = (
        g.arm_occurrence_loc(g.DEPLOYED_ANGLE, 0.0)
        * g.translation_loc(4.0, 0.0, -8.5)
        * g.translation_loc(-0.4, 0.0, -4.0)
    )
    stop_to_carrier = carrier_frame.inverse * stop_frame
    for screw_x, y in g.FIXED_STOP_SCREW_STATIONS_MM:
        screw_neck_clearance = g.cyl_z(1.15, 5.20, screw_x, y, 2.50)
        screw_thread_minor = g.cyl_z(1.25, 3.40, screw_x, y, 7.35)
        for cutter in (screw_neck_clearance, screw_thread_minor):
            carrier_shape = carrier_shape.cut(g.moved(cutter, stop_to_carrier))
    for y in (-8.0, 8.0):
        dowel_h7 = g.cyl_z(1.50, 8.40, 7.0, y, 2.85)
        carrier_shape = carrier_shape.cut(g.moved(dowel_h7, stop_to_carrier))
    carrier = b.define(
        "DF8-R2-PIVOT-CARRIER-001", "D",
        "MATCHED DOUBLE-SHEAR PIVOT LUG SET WITH SWEPT BELL-CLEVIS ACCESS AND OBLIQUE STOP-LAND BORES",
        carrier_shape, "Ti-6Al-4V",
        process="5-axis mill swept bell-clevis access slot; ream pivot; occurrence-match drill/tap two M3 and ream two H7 stop-land bores",
        color_key="titanium",
    )
    pivot_pin = b.define("DF8-R2-PIVOT-PIN-008", "B", "8 MM CAPTIVE SHOULDER PIVOT PIN WITH EXTERNAL GROOVE", g.make_clevis_pin(8.0, 20.5, 8.8, 1.5),
                         "17-4PH stainless steel", process="Swiss turn; H900; grind", color_key="steel")
    bushing = b.define("DF8-R2-PIVOT-BUSH-008", "A", "8 MM PEEK-LINED PIVOT BUSHING", g.ring_y(0, 0, 2.0, 4.15, 4.02),
                       "PEEK", process="Turn and press fit", color_key="peek")
    washer = b.define("DF8-R2-PIVOT-WASHER-008", "A", "8 MM PEEK THRUST WASHER", g.ring_y(0, 0, 0.18, 6.0, 4.15),
                      "PEEK", process="Turn", color_key="peek")
    pivot_clip = b.define("DF8-R2-PIVOT-SPIRAL-RING-008", "A", "8 MM EXTERNAL SPIRAL PIVOT RETAINER", g.make_external_retaining_ring(8.0),
                          "1.4310 stainless spring steel", process="Wire form", color_key="spring")
    link = b.define("DF8-R2-SHORT-LINK-001", "A", "19.950 MM CENTER-DISTANCE REAMED SHORT LINK", g.make_link_part_local(),
                    "17-4PH stainless steel", process="Wire EDM; H900; ream", color_key="steel")
    link_pin_shape = g.make_clevis_pin(4.0, 12.8, 6.0, 1.0)
    dc4_groove = cq.Solid.makeCylinder(2.50, 0.44, cq.Vector(0, 11.78, 0), cq.Vector(0, 1, 0)).cut(
        cq.Solid.makeCylinder(1.55, 0.64, cq.Vector(0, 11.68, 0), cq.Vector(0, 1, 0))
    )
    link_pin_shape = link_pin_shape.cut(dc4_groove)
    link_pin = b.define("DF8-R2-LINK-PIN-004", "B", "4 MM FULL-SPAN LINK PIN WITH DC-4SS RETAINER GROOVE", link_pin_shape,
                        "17-4PH stainless steel", process="Swiss turn; H900; grind", color_key="steel")
    dc4_ring = g.ring_y(0.0, 0.0, 0.38, 2.50, 1.58).cut(g.box_center(2.2, 0.6, 2.0, 2.0, 0.0, 0.0))
    link_clip = b.define("ROTOR-CLIP-DC-4SS", "A", "ROTOR CLIP DC-4SS CRESCENT RETAINING RING FOR 4 MM SHAFT", dc4_ring,
                         "PH 15-7 Mo stainless spring steel", "BUY", "Rotor Clip", "DRAWING_DERIVED",
                         mass_kg=0.0000294216,
                         source_url="https://www.rotorclip.com/product/dc-4/",
                         purchase_url="https://www.rotorclip.com/product/dc-4/",
                         process="Catalog DC-4SS crescent ring; verify 4 mm shaft application, 3.13-3.20 mm groove diameter, 0.44 mm groove width, 0.35-0.40 mm ring thickness, 5 mm OD and material certification",
                         notes="Explicit occurrence mass is the 3.7479745 mm3 authored envelope at 7.85e-6 kg/mm3; incoming lot mass and material are verified.", color_key="spring")
    stop_pad_shape = g.box_center(10.0, 7.6, 4.4)
    stop_pad_shape = stop_pad_shape.cut(
        cq.Solid.makeCylinder(0.60, 1.0, cq.Vector(0.0, 3.15, 0.0), cq.Vector(0, 1, 0))
    )
    for x in (-2.8, 2.8):
        clearance = cq.Solid.makeCylinder(
            1.65, 8.2, cq.Vector(x, -4.1, 0.0), cq.Vector(0, 1, 0)
        )
        pilot_clearance = cq.Solid.makeCylinder(
            2.20, 1.0, cq.Vector(x, -4.10, 0.0), cq.Vector(0, 1, 0)
        )
        counterbore = cq.Solid.makeCylinder(
            2.79, 2.5, cq.Vector(x, -4.1, 0.0), cq.Vector(0, 1, 0)
        )
        stop_pad_shape = stop_pad_shape.cut(clearance.fuse(pilot_clearance).fuse(counterbore))
    stop_pad = b.define("DF8-R2-ARM-STOP-PAD-001", "B", "REPLACEABLE ARM STOP AND AUTOMATIC-LOCK STRIKE", stop_pad_shape,
                        "17-4PH stainless steel", process="Wire EDM and grind", color_key="steel")
    fixed_stop_shape = g.box_center(5.5, 8.2, 4.0)
    for sign in (-1.0, 1.0):
        fixed_stop_shape = fixed_stop_shape.fuse(
            g.routed_round(
                [(2.2, sign * 4.0, 1.2),
                 (2.5, sign * 6.8, 2.0),
                 (3.3, sign * 7.0, 4.0)],
                0.50,
            )
        )
        fixed_stop_shape = fixed_stop_shape.fuse(
            g.box_center(12.0, 5.0, 1.6, 4.0, sign * 8.0, 3.85)
        )
    # Exact four-wall lock channel.  It is open only at the pad and outer
    # bushing ends, stays outside the deployed arm/pad envelope, and is fused
    # to the fixed-stop body through both side walls.
    lock_guide_depth = LOCK_GUIDE_OUTER_Y_MM - LOCK_GUIDE_INNER_Y_MM
    lock_guide_center_y = (LOCK_GUIDE_INNER_Y_MM + LOCK_GUIDE_OUTER_Y_MM) / 2.0
    for wall in (
        g.box_center(0.30, lock_guide_depth, 3.60, -0.75, lock_guide_center_y, 3.40),
        g.box_center(0.30, lock_guide_depth, 3.60, 1.55, lock_guide_center_y, 3.40),
        g.box_center(2.60, lock_guide_depth, 0.30, 0.40, lock_guide_center_y, 5.05),
        g.box_center(2.60, lock_guide_depth, 0.30, 0.40, lock_guide_center_y, 2.95),
    ):
        fixed_stop_shape = fixed_stop_shape.fuse(wall)
    # Machine the stop/lock body to the exact deployed arm and replaceable-pad
    # envelopes.  This removes the former 8..43 mm3 positive-volume stop
    # collision while preserving zero-gap reaction faces and the guided lock
    # dog's 0.15 mm positive engagement.
    deployed_arm_frame = g.arm_occurrence_loc(g.DEPLOYED_ANGLE, 0.0)
    arm_in_stop = g.moved(arm.shape, stop_frame.inverse * deployed_arm_frame)
    pad_in_stop = g.moved(stop_pad_shape, g.translation_loc(0.4, 0.0, 4.0))
    fixed_stop_shape = fixed_stop_shape.cut(arm_in_stop).cut(pad_in_stop)
    # Two separated M3 side-land bores and two H7 dowel bores.  Heads remain
    # outside the lower land face; shanks enter the oblique carrier bores.
    for screw_x, y in g.FIXED_STOP_SCREW_STATIONS_MM:
        fixed_stop_shape = fixed_stop_shape.cut(
            g.cyl_z(1.65, 2.0, screw_x, y, 2.35)
        )
        fixed_stop_shape = fixed_stop_shape.cut(
            g.cyl_z(2.80, 3.04, screw_x, y, -0.50)
        )
    for y in (-8.0, 8.0):
        fixed_stop_shape = fixed_stop_shape.cut(g.cyl_z(1.50, 2.0, 7.0, y, 2.85))
    # Head pockets interrupt the former on-axis side ties.  Two outboard
    # bypass webs at x=-1.5 restore a continuous stop-to-land load path while
    # remaining outside each 5.6 mm head-clearance cylinder.
    for sign in (-1.0, 1.0):
        bypass = g.box_center(1.0, 2.0, 2.0, -1.5, sign * 4.75, 2.5)
        fixed_stop_shape = fixed_stop_shape.fuse(bypass)
    fixed_stop_shape = fixed_stop_shape.cut(arm_in_stop).cut(pad_in_stop)
    for screw_x, y in g.FIXED_STOP_SCREW_STATIONS_MM:
        fixed_stop_shape = fixed_stop_shape.cut(
            g.cyl_z(2.85, 3.10, screw_x, y, -0.55)
        )
        # The fixed stop is a clearance member; the captive threaded end
        # reacts in the two carrier lands.  Carry the 3.30 mm clearance bore
        # through the full five-millimetre captive neck so no stop material
        # grazes the unthreaded shank above the head pocket.
        fixed_stop_shape = fixed_stop_shape.cut(
            g.cyl_z(1.65, 5.40, screw_x, y, 2.35)
        )
    # Full occurrence-matched access for the two moving stop-pad screws at
    # the 80-degree endpoint.  Separate head, captive-neck and thread-envelope
    # reliefs retain material between the screws and around the lock channel.
    for x in (-2.4, 3.2):
        fixed_stop_shape = fixed_stop_shape.cut(cq.Solid.makeCylinder(
            2.85, 3.40, cq.Vector(x, -5.00, 4.0), cq.Vector(0, 1, 0)
        ))
        fixed_stop_shape = fixed_stop_shape.cut(cq.Solid.makeCylinder(
            1.20, 5.40, cq.Vector(x, -2.00, 4.0), cq.Vector(0, 1, 0)
        ))
        fixed_stop_shape = fixed_stop_shape.cut(cq.Solid.makeCylinder(
            1.65, 3.40, cq.Vector(x, 3.00, 4.0), cq.Vector(0, 1, 0)
        ))
    spring_running_clearance = cq.Solid.makeCylinder(
        0.82, 5.15, cq.Vector(0.4, 4.85, 4.0), cq.Vector(0, 1, 0)
    )
    fixed_stop_shape = fixed_stop_shape.cut(spring_running_clearance)
    # Machine the stationary stop body to the measured 0..79 degree moving
    # envelopes.  The 80-degree arm/pad reaction faces remain governed by the
    # existing exact endpoint cuts above; only the observed mid-stroke ranges,
    # plus one bounding sample, are removed here.
    moving_screw_clearance = (
        g.cyl_z(2.80, 3.10, z0=-3.05)
        .fuse(g.cyl_z(1.15, 5.10, z0=-0.05))
        .fuse(g.cyl_z(1.55, 3.10, z0=4.95))
    )
    stop_sweep_cutters: list[cq.Shape] = []
    for angle in range(42, 80):
        moving_arm_frame = g.arm_occurrence_loc(float(angle), 0.0)
        stop_sweep_cutters.append(g.moved(arm.shape, stop_frame.inverse * moving_arm_frame))
    for angle in range(69, 72):
        moving_pad_frame = (
            g.arm_occurrence_loc(float(angle), 0.0)
            * g.translation_loc(4.0, 0.0, -8.5)
        )
        stop_sweep_cutters.append(g.moved(stop_pad_shape, stop_frame.inverse * moving_pad_frame))
    for screw_x, angle_range in ((-2.80, range(42, 81)), (2.80, range(64, 81))):
        for angle in angle_range:
            moving_screw_frame = (
                g.arm_occurrence_loc(float(angle), 0.0)
                * g.translation_loc(4.0, 0.0, -8.5)
                * g.translation_loc(screw_x, -1.80, 0.0)
                * g.rotation_loc((1, 0, 0), -90.0)
            )
            stop_sweep_cutters.append(g.moved(
                moving_screw_clearance, stop_frame.inverse * moving_screw_frame,
            ))
    for cutter in stop_sweep_cutters:
        fixed_stop_shape = fixed_stop_shape.cut(cutter)
    # The swept arm corridor opens the original inboard neck to the negative-Y
    # side land.  Route a machined tie around that corridor at the outboard
    # edges of both existing side lands, then reapply every motion cutter so
    # the bridge can remain only where it is genuinely outside the audited
    # moving volume.
    swept_stop_bypass = g.box_center(0.60, 16.0, 1.0, 10.05, 0.0, 3.85)
    fixed_stop_shape = fixed_stop_shape.fuse(swept_stop_bypass)
    for cutter in stop_sweep_cutters:
        fixed_stop_shape = fixed_stop_shape.cut(cutter)
    # Machine a controlled cylindrical seat for the moved outer PEEK guide
    # bushing.  The 0.9365 mm seat radius preserves the previously qualified
    # bounded press-fit common volume while removing the unrelieved side-land
    # penetration introduced when the lock guide was extended.
    lock_bushing_press_seat = cq.Solid.makeCylinder(
        0.9365, 0.70,
        cq.Vector(0.4, LOCK_BUSHING_Y_MM - 0.35, 4.35),
        cq.Vector(0, 1, 0),
    )
    fixed_stop_shape = fixed_stop_shape.cut(lock_bushing_press_seat)
    fixed_stop_shape = fixed_stop_shape.clean()
    fixed_stop_solids = fixed_stop_shape.Solids()
    if len(fixed_stop_solids) != 1 or not fixed_stop_shape.isValid():
        closest_points = None
        if len(fixed_stop_solids) == 2:
            distance_probe = BRepExtrema_DistShapeShape(
                fixed_stop_solids[0].wrapped, fixed_stop_solids[1].wrapped,
            )
            distance_probe.Perform()
            if distance_probe.IsDone() and distance_probe.NbSolution() > 0:
                closest_points = {
                    "distance_mm": distance_probe.Value(),
                    "solid_1_point": distance_probe.PointOnShape1(1).Coord(),
                    "solid_2_point": distance_probe.PointOnShape2(1).Coord(),
                }
        raise ValueError(
            f"Fixed stop must remain one valid collision-cleared exact solid; "
            f"found {len(fixed_stop_solids)} solids (valid={fixed_stop_shape.isValid()}), "
            f"solids={[(solid.Volume(), (solid.BoundingBox().xmin, solid.BoundingBox().xmax, solid.BoundingBox().ymin, solid.BoundingBox().ymax, solid.BoundingBox().zmin, solid.BoundingBox().zmax)) for solid in fixed_stop_solids]}, "
            f"closest_points={closest_points}"
        )
    fixed_stop = b.define(
        "DF8-R2-FIXED-STOP-001", "E",
        "80 DEGREE SWEPT-CLEARANCE FIXED STOP WITH CONTROLLED AUTOMATIC-LOCK BUSHING SEAT",
        fixed_stop_solids[0], "17-4PH stainless steel",
        process="5-axis mill; wire EDM lock guide and controlled PEEK-bushing seat; occurrence-match drill two M3 clearance and ream two H7 side-land bores; grind stop faces",
        color_key="steel",
    )
    stow_dog_shape = g.box_center(4.0, 4.4, 5.5)
    stow_dog_shape = stow_dog_shape.cut(
        cq.Solid.makeCylinder(0.65, 5.0, cq.Vector(0.0, -2.5, 0.0), cq.Vector(0, 1, 0))
    )
    stow_dog = b.define("DF8-R2-STOW-DOG-001", "B", "CAPTIVE RADIAL STOWED-RETENTION DOG WITH TRANSPORT-INHIBIT BORE", stow_dog_shape,
                        "17-4PH stainless steel", process="Wire EDM and grind", color_key="steel")
    stow_dog_guide = b.define(
        "DF8-R2-STOW-DOG-GUIDE-001", "A", "FULL-STROKE AFT-RING-MOUNTED STOW-DOG U-GUIDE",
        g.make_stow_dog_guide_local(), "17-4PH stainless steel",
        process="Wire EDM; form; laser weld mounting pad; grind guide faces", color_key="steel",
    )
    stow_spring_length = 0.28 if b.deployed else 3.78
    stow_spring = b.define(
        "DF8-R2-STOW-DOG-RETURN-SPRING-001", "A", "CAPTIVE STOW-DOG RADIAL RETURN SPRING",
        g.make_compression_spring_local(1.20, 0.10, stow_spring_length, 2.5),
        "1.4310 stainless spring steel",
        process="Micro-coil; stress relieve; inspect installed force and 0.28-3.78 mm working stroke",
        notes="Endpoint B-reps bound the full radial dog stroke; spring is captured between the integral guide bridge and dog inboard face.",
        color_key="spring",
    )
    transport_pin = b.define(
        "DF8-R2-STOW-DOG-INHIBIT-PIN-001", "A", "WITHDRAWABLE HEADED TRANSPORT-INHIBIT PIN",
        g.make_captive_inhibit_slider_pin_local(), "17-4PH stainless steel",
        process="Swiss turn; H900; grind; tether-feature inspection", color_key="steel",
    )
    transport_keeper_shape = g.ring_y(0.0, 0.0, 0.35, 0.80, 0.32).cut(
        g.box_center(0.70, 0.55, 0.50, 0.55, 0.0, 0.0)
    )
    transport_keeper = b.define(
        "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001", "A",
        "CAPTIVE CRESCENT RETAINER FOR TRANSPORT-INHIBIT PIN",
        transport_keeper_shape, "1.4310 stainless spring steel",
        process="Stamp; deburr; passivate; inspect seating in occurrence-matched pin groove",
        notes="External keeper remains seated on and translates with the headed inhibit pin in both retained and withdrawn endpoint states.",
        color_key="spring",
    )
    lock_dog_shape = cq.Solid.makeCylinder(0.45, 1.15, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    lock_dog_shape = lock_dog_shape.fuse(
        cq.Solid.makeCylinder(0.75, 0.20, cq.Vector(0, 1.15, 0), cq.Vector(0, 1, 0))
    )
    lock_dog = b.define(
        "DF8-R2-AUTO-LOCK-DOG-001", "A", "SPRING-DRIVEN POSITIVE DEPLOYED LOCK DOG",
        lock_dog_shape, "17-4PH stainless steel", process="Swiss turn; H900; grind", color_key="steel",
    )
    lock_spring_length = (
        LOCK_DEPLOYED_SPRING_LENGTH_MM
        if b.deployed else LOCK_RETRACTED_SPRING_LENGTH_MM
    )
    lock_spring = b.define(
        "DF8-R2-AUTO-LOCK-SPRING-001", "B", "CAPTIVE LONG-STROKE AUTOMATIC-LOCK COMPRESSION SPRING",
        g.make_compression_spring_local(1.60, 0.16, lock_spring_length, 5.0),
        "1.4310 stainless spring steel", mass_kg=LOCK_SPRING_MASS_KG,
        process="Micro-coil; stress relieve; inspect force and 1.65-4.95 mm installed lengths",
        notes="Endpoint B-reps bound the 3.30 mm snap-lock stroke; physical wire mass is state-invariant and the spring remains captive between the dog head and press-fit outer bushing.",
        color_key="spring",
    )
    lock_bushing_shape = g.ring_y(0.0, 0.0, 0.30, 1.0, 0.82)
    lock_bushing_shape = lock_bushing_shape.cut(g.cyl_z(
        1.15, 5.40, 1.60, 0.65, -2.05
    ))
    lock_bushing = b.define(
        "DF8-R2-AUTO-LOCK-BUSHING-001", "A", "PRESS-FIT LOCK GUIDE OUTER RETAINER BUSHING",
        lock_bushing_shape, "PEEK",
        process="Turn; press fit; inspect spring-clear bore and retention", color_key="peek",
    )
    for idx, phi in enumerate((0.0, 120.0, 240.0), 1):
        add_arm_hardware(b, idx, phi, theta, arm, carrier, pivot_pin, bushing, washer, pivot_clip,
                         link, link_pin, link_clip, stop_pad, fixed_stop, stow_dog,
                         stow_dog_guide, stow_spring, transport_pin, transport_keeper,
                         lock_dog, lock_spring, lock_bushing)

    crosshead = b.define("DF8-R2-CROSSHEAD-001", "A", "ONE-PIECE SIX-CLEVIS GUIDED COMMON CROSSHEAD", g.make_crosshead_part_local(),
                         "17-4PH stainless steel", process="5-axis mill-turn; H900; hone", color_key="steel")
    zc = g.kinematic(theta)["crosshead_z"]
    b.add(b.arm_module, path, crosshead, "CROSSHEAD-001", g.translation_loc(0, 0, zc), "MOVING", "GUIDED_TRANSLATION", "1 AXIAL TRANSLATION")
    guide_shape = g.cyl_z(3.2, 47.0).fuse(g.cyl_z(4.45, 1.0))
    guide_shape = guide_shape.cut(g.make_tapped_hole_cutter_z(
        3.30, 6.20, thread_major_diameter_mm=4.0, z0=0.0
    ))
    guide = b.define("DF8-R2-CROSSHEAD-GUIDE-001", "C", "CENTRAL DLC CROSSHEAD GUIDE SHAFT WITH SPIDER SHOULDER", guide_shape,
                     "17-4PH stainless steel", process="Centerless grind and DLC", color_key="steel")
    b.add(b.arm_module, path, guide, "CROSSHEAD-GUIDE-001", g.translation_loc(0, 0, repack.ARM_STRUCTURE_START_Z_MM), "FIXED", "DOUBLE_SUPPORTED_SHAFT")
    guide_spider = b.define(
        "DF8-R2-CROSSHEAD-GUIDE-SPIDER-001", "A", "THREE-SPOKE CROSSHEAD-GUIDE FORWARD MOUNT",
        g.make_crosshead_guide_spider_local(), "Ti-6Al-4V",
        process="5-axis mill; conformal fit to FWD-RING-02 bore; qualified three-spoke laser weld; dimensional inspection",
        color_key="titanium",
    )
    b.add(b.arm_module, path, guide_spider, "CROSSHEAD-GUIDE-SPIDER",
          g.translation_loc(0, 0, repack.ARM_STRUCTURE_START_Z_MM), "FIXED", "THREE_SPOKE_QUALIFIED_PERMANENT_RING_JOINT")

    spring_length = g.SPRING_DEPLOYED if b.deployed else g.SPRING_STOWED
    backup_spring = b.define("DF8-R2-BACKUP-SPRING-16N-001", "B", "CONTROLLED 16 N/MM GUIDED BACKUP COMPRESSION SPRING",
                             g.make_compression_spring_local(g.SPRING_OD, g.SPRING_WIRE, spring_length, 25.3),
                             "1.4310 stainless spring steel", "MAKE", "STINGRAY controlled spring specification",
                             "DRAWING_DERIVED", mass_kg=0.092,
                             process="Cold coil; closed-ground ends; stress relieve; 100% rate/length inspection; proof cycle",
                             notes="OD 15.8 mm; wire 3.0 mm; free length 195.0 mm; rate 16.0 N/mm; controlled drawing and proof acceptance.", color_key="spring")
    spring_station = g.rotation_loc((0, 0, 1), 300.0) * g.translation_loc(12.0, 0.0, 0.0)
    moving_seat_z = zc + 4.75
    spring_z = zc + 7.25
    fixed_seat_z = spring_z + spring_length + 2.5
    b.add(b.arm_module, path, backup_spring, "BACKUP-SPRING-001", spring_station * g.translation_loc(0, 0, spring_z), "FLEXIBLE", "CAPTURED_GUIDED_SPRING", "AXIAL COMPRESSION")
    fixed_seat_shape = g.tube_z(8.5, 3.4, 5.0, z0=-2.5)
    fixed_seat_shape = fixed_seat_shape.fuse(
        g.rod_between((8.0, 0.0, 0.0), (10.90, 0.0, 0.0), 0.45)
    )
    fixed_seat_shape = fixed_seat_shape.cut(cq.Solid.makeCylinder(
        1.25, 3.4, cq.Vector(7.7, 0.0, 0.0), cq.Vector(1, 0, 0)
    ))
    # The M3 screw traverses the spring-seat body before engaging only the
    # outboard tongue.  Clear the pass-through portion and retain a short,
    # occurrence-gauged thread-minor annulus in x=8.5..11.1.
    fixed_seat_shape = fixed_seat_shape.cut(cq.Solid.makeCylinder(
        1.65, 6.50, cq.Vector(2.0, 0.0, 0.0), cq.Vector(1, 0, 0)
    ))
    fixed_seat_shape = fixed_seat_shape.fuse(g.tube_between(
        (8.45, 0.0, 0.0), (11.20, 0.0, 0.0), 2.50, 1.25
    ))
    fixed_seat = b.define("DF8-R2-BACKUP-SPRING-FIXED-SEAT-001", "B", "BACKUP SPRING AFT FIXED SEAT WITH LONGERON MOUNTING TONGUE", fixed_seat_shape,
                          "Ti-6Al-4V", process="Mill-turn", color_key="titanium")
    moving_seat = b.define(
        "DF8-R2-BACKUP-SPRING-MOVING-SEAT-001", "B",
        "BACKUP SPRING CROSSHEAD SEAT WITH PILOTED PERMANENT LAND",
        g.tube_z(8.5, 3.4, 5.0, z0=-2.5),
        "17-4PH stainless steel",
        process="Mill-turn; pilot to crosshead spoke; qualified laser weld; dimensional inspection",
        color_key="steel",
    )
    b.add(b.arm_module, path, fixed_seat, "BACKUP-SPRING-FIXED-SEAT", spring_station * g.translation_loc(0, 0, fixed_seat_z), "FIXED", "THREADED_TO_GUIDE_SUPPORT")
    b.add(
        b.arm_module, path, moving_seat, "BACKUP-SPRING-MOVING-SEAT",
        spring_station * g.translation_loc(0, 0, moving_seat_z), "MOVING",
        "PILOTED_QUALIFIED_PERMANENT_CROSSHEAD_JOINT",
    )
    guide_length = fixed_seat_z + 2.5 - g.PIVOT_Z
    spring_guide_shape = g.cyl_z(2.5, guide_length)
    spring_guide_shape = spring_guide_shape.fuse(
        g.rod_between((0.0, 0.0, 0.75), (10.90, 0.0, 0.75), 0.45)
    )
    spring_guide_shape = spring_guide_shape.fuse(
        g.cyl_z(3.35, 5.0, z0=guide_length - 5.0)
    )
    spring_guide_shape = spring_guide_shape.cut(cq.Solid.makeCylinder(
        1.25, 9.2, cq.Vector(2.0, 0.0, 0.75), cq.Vector(1, 0, 0)
    ))
    spring_guide_shape = spring_guide_shape.cut(cq.Solid.makeCylinder(
        1.65, 2.0,
        cq.Vector(1.95, 0.0, guide_length - 2.5), cq.Vector(1, 0, 0)
    ))
    spring_guide_shape = spring_guide_shape.cut(cq.Solid.makeCylinder(
        1.65, 6.50, cq.Vector(1.95, 0.0, 0.75), cq.Vector(1, 0, 0)
    ))
    spring_guide_shape = spring_guide_shape.fuse(g.tube_between(
        (8.45, 0.0, 0.75), (11.20, 0.0, 0.75), 2.50, 1.25
    ))
    spring_guide_shape = spring_guide_shape.fuse(g.rod_between(
        (0.0, 2.0, 0.75), (9.0, 2.0, 0.75), 0.60
    ))
    spring_guide = b.define("DF8-R2-BACKUP-SPRING-GUIDE-001", "B", "BACKUP SPRING DLC GUIDE SHAFT WITH TWO FIXED SUPPORT SHOULDERS", spring_guide_shape,
                            "17-4PH stainless steel", process="Centerless grind and DLC", color_key="steel")
    b.add(b.arm_module, path, spring_guide, "BACKUP-SPRING-GUIDE", spring_station * g.translation_loc(0, 0, g.PIVOT_Z), "FIXED", "SUPPORTED_AT_BOTH_ENDS")

    # Parallel GS/HBD installations occupy fixed-sector corridors aft of the crosshead.
    gs_src = next((INPUT_DIR / "wp02").rglob("ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp"))
    gs_body = b.define("GS-19-50-V4A-B8-B8", "R2-INSTALL", "ACE GS-19-50-V4A-B8-B8 PURCHASED ASSEMBLY — ARTICULATED INSTALLATION BODY",
                       actuator_body_shape(9.5, 5.2, 105.0, 112.0), "AISI 316L / 316Ti stainless catalog assembly", "BUY", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.144,
                       source_url="https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
                       purchase_url="https://www.acecontrols.com/us/calculations/gas-spring-configurator.html",
                       notes=f"Configured GS-19-50-V4A-B8-B8, 50 mm stroke, 164.1 mm extended length, 7.9 mm rod and 300±30 N setting. The controlled ACE STEP {gs_src.name} is the dimensional/interface verification source; this separated body/rod BREP is a drawing-derived articulated installation representation. Occurrence mass allocation is 0.124 kg body + 0.020 kg rod = 0.144 kg catalog assembly total.", color_key="gas")
    gs_rod = b.define("GS-19-50-V4A-B8-B8-ROD-CHILD", "R2-INSTALL", "ACE GS-19 MOVING ROD ARTICULATION CHILD", actuator_rod_shape(4.0, 70.0),
                      "AISI 316L / 316Ti stainless catalog assembly", "BUY", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.020,
                      source_url="https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a.html",
                      purchase_url="https://www.acecontrols.com/us/calculations/gas-spring-configurator.html",
                      notes="Included articulation child of the configured GS-19 purchased assembly; no separate purchase quantity. Occurrence-level mass allocation reconciles with the 0.144 kg parent assembly. Drawing-derived child verified against the controlled ACE STEP.", color_key="stainless")
    gs_body.mass_kg = 0.124
    gs_phi, gs_r, gs_body_z = 60.0, 13.5, g.PIVOT_Z + 60.0
    gs_body_loc = g.rotation_loc((0, 0, 1), gs_phi) * g.translation_loc(gs_r, 0, gs_body_z)
    gs_rod_loc = g.rotation_loc((0, 0, 1), gs_phi) * g.translation_loc(gs_r, 0, zc)
    b.add(b.arm_module, path, gs_body, "GS19-BODY-001", gs_body_loc, "FIXED", "PINNED_B8_END")
    b.add(b.arm_module, path, gs_rod, "GS19-ROD-001", gs_rod_loc, "MOVING", "TELESCOPING_GAS_SPRING", "1 AXIAL TRANSLATION")

    hbd_src = next((INPUT_DIR / "wp02").rglob("ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step"))
    hbd_body = b.define("HBD-15-25-AA-P", "R2-INSTALL", "ACE HBD-15-25-AA-P PURCHASED ASSEMBLY — ARTICULATED INSTALLATION BODY", actuator_body_shape(7.5, 4.0, 95.0, 102.0, 5.5),
                        "Black-anodized aluminum body / hard-chrome steel rod / zinc-plated steel AA-P fittings", "BUY", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.220,
                        source_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
                        purchase_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
                        notes=f"Configured HBD-15-25-AA-P, 24.9 mm stroke, 145.0 mm extended length, 15 mm body and 6.1 mm rod. The controlled ACE source {hbd_src.name} verifies the configured envelope/interfaces; this separated body/rod BREP is a drawing-derived articulated installation representation. External travel stops limit motion 1.0-1.5 mm before stroke ends. Occurrence mass allocation is 0.190 kg body + 0.030 kg rod = 0.220 kg catalog assembly total.", color_key="hydraulic")
    hbd_rod = b.define("HBD-15-25-AA-P-ROD-CHILD", "R2-INSTALL", "HBD MOVING ROD ARTICULATION CHILD", actuator_rod_shape(3.0, 60.0, 4.5),
                       "Hard-chrome steel rod with zinc-plated steel AA-P fitting", "BUY", "ACE Controls", "DRAWING_DERIVED", mass_kg=0.030,
                       source_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
                       purchase_url="https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15/hbd-15-25.html",
                       notes="Included articulation child of the configured HBD purchased assembly; no separate purchase quantity. Occurrence-level mass allocation reconciles with the 0.220 kg parent assembly. Drawing-derived child verified against the controlled ACE source.", color_key="stainless")
    hbd_body.mass_kg = 0.190
    hbd_phi, hbd_r, hbd_body_z = 180.0, 14.5, g.PIVOT_Z + 60.0
    hbd_body_loc = g.rotation_loc((0, 0, 1), hbd_phi) * g.translation_loc(hbd_r, 0, hbd_body_z)
    hbd_rod_loc = g.rotation_loc((0, 0, 1), hbd_phi) * g.translation_loc(hbd_r, 0, zc)
    b.add(b.arm_module, path, hbd_body, "HBD-BODY-001", hbd_body_loc, "FIXED", "PINNED_AA_END")
    b.add(b.arm_module, path, hbd_rod, "HBD-ROD-001", hbd_rod_loc, "MOVING", "TELESCOPING_DAMPER", "1 AXIAL TRANSLATION")

    fixed_yokes = {
        "GS19": b.define(
            "DF8-R2-ACTUATOR-FIXED-YOKE-GS19-001", "B",
            "DOUBLE-SHEAR GS19 ANCHOR YOKE WITH CONFORMAL LONGERON TONGUE",
            actuator_fixed_yoke_shape(installation_radius=gs_r),
            "Ti-6Al-4V",
            process="5-axis mill; conformal fit to r=23 longeron land; qualified laser weld; dimensional inspection",
            color_key="titanium",
        ),
        "HBD": b.define(
            "DF8-R2-ACTUATOR-FIXED-YOKE-HBD-001", "B",
            "DOUBLE-SHEAR HBD ANCHOR YOKE WITH CONFORMAL LONGERON TONGUE",
            actuator_fixed_yoke_shape(installation_radius=hbd_r),
            "Ti-6Al-4V",
            process="5-axis mill; conformal fit to r=23 longeron land; qualified laser weld; dimensional inspection",
            color_key="titanium",
        ),
    }
    actuator_pin = b.define("DF8-R2-ACTUATOR-PIN-004", "B", "4 MM CAPTIVE ACTUATOR CLEVIS PIN", g.make_clevis_pin(4.0, 11.0, 6.0, 1.0),
                            "17-4PH stainless steel", process="Swiss turn; H900", color_key="steel")
    actuator_clip = b.define("DF8-R2-ACTUATOR-E-RING-004", "A", "4 MM ACTUATOR PIN RETAINER", g.make_external_retaining_ring(4.0, 0.45),
                             "1.4310 stainless spring steel", process="Stamp", color_key="spring")
    for label, phi, radius, fixed_z in (("GS19", gs_phi, gs_r, gs_body_z + 112.0),
                                         ("HBD", hbd_phi, hbd_r, hbd_body_z + 102.0)):
        fixed_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(radius, 0, fixed_z)
        moving_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(radius, 0, zc)
        b.add(
            b.arm_module, path, fixed_yokes[label], f"{label}-FIXED-YOKE",
            fixed_loc, "FIXED", "QUALIFIED_PERMANENT_LONGERON_LAND_JOINT",
        )
        for end, base in (("FIXED", fixed_loc), ("MOVING", moving_loc)):
            b.add(b.arm_module, path, actuator_pin, f"{label}-PIN-{end}", base * g.translation_loc(0, -5.5, 0), "MOVING" if end == "MOVING" else "FIXED", "CLEVIS_PIN_WITH_E_RING")
            b.add(b.arm_module, path, actuator_clip, f"{label}-CLIP-{end}", base * g.translation_loc(0, 4.7, 0), "MOVING" if end == "MOVING" else "FIXED", "EXTERNAL_GROOVE")

    # Corrected continuous service centerlines.  Each route begins and ends on
    # a modeled port face, passes through counterbored structural transitions,
    # and remains inside the protected annular service corridor.  The Bowden
    # wire is concentric inside its sheath with positive radial clearance.
    def polar_point(radius: float, phi_deg: float, z: float) -> tuple[float, float, float]:
        x, y = radial_xy(radius, phi_deg)
        return (x, y, z)

    def localize(points: list[tuple[float, float, float]]) -> tuple[list[tuple[float, float, float]], cq.Location]:
        x0, y0, z0 = points[0]
        return ([(x - x0, y - y0, z - z0) for x, y, z in points], g.translation_loc(x0, y0, z0))

    gas_points = [
        (0.0, 11.0, repack.FULLFLOW_VALVE_Z_MM), (0.0, 17.0, repack.FULLFLOW_VALVE_Z_MM),
        polar_point(18.0, 85.0, repack.FULLFLOW_VALVE_Z_MM + 15.0),
        *[polar_point(26.2, 85.0, z) for z in (repack.FULLFLOW_VALVE_Z_MM + 35.0, 1638.0, 1642.5)],
        polar_point(24.0, 85.0, 1660.0),
        polar_point(23.0, 85.0, 1670.0), polar_point(22.5, 85.0, 1720.0),
    ]
    pilot_points = [
        polar_point(6.5, 325.0, repack.FULLFLOW_VALVE_Z_MM),
        polar_point(18.0, 325.0, repack.FULLFLOW_VALVE_Z_MM),
        *[polar_point(26.2, 325.0, z) for z in (repack.FULLFLOW_VALVE_Z_MM + 35.0, 1638.0, 1642.5)],
        polar_point(24.0, 325.0, 1660.0), polar_point(18.0, 325.0, 1680.0),
        polar_point(18.0, 315.0, 1700.0), polar_point(18.0, 300.0, 1720.0),
        polar_point(18.0, 290.0, 1735.0), polar_point(18.0, 280.0, 1748.0),
        polar_point(21.1, 270.0, 1753.85),
    ]
    bowden_points = [
        (0.0, 0.0, repack.WATER_TRIGGER_Z_MM + 57.5),
        (0.0, 0.0, repack.WATER_TRIGGER_Z_MM + 62.0),
        polar_point(18.0, 205.0, repack.WATER_TRIGGER_Z_MM + 65.0),
        polar_point(23.0, 205.0, repack.WATER_TRIGGER_Z_MM + 75.0),
        polar_point(26.2, 205.0, repack.WATER_TRIGGER_Z_MM + 90.0),
        polar_point(26.2, 205.0, 1642.5),
        polar_point(24.0, 205.0, 1660.0),
        polar_point(17.0, 205.0, 1680.0),
        polar_point(17.0, 225.0, 1700.0), polar_point(17.0, 240.0, 1720.0),
        polar_point(17.0, 255.0, 1735.0), polar_point(17.0, 260.0, 1745.0),
        polar_point(18.1, 270.0, 1745.0),
    ]
    # The wire terminates coplanar with the sear nose.  The former route first
    # ran past that face to r=21 and then doubled back to r=18.1, producing a
    # real wire/sear and sheath/sear positive-volume collision.
    bowden_wire_points = list(bowden_points)
    bowden_wire_points[0] = (0.0, 0.0, repack.WATER_TRIGGER_Z_MM + 56.8)
    # The fixed sheath seats in the latch boss.  Only the inner wire follows
    # the 3.2 mm sear withdrawal at the deployed endpoint.
    bowden_wire_points[-1] = (0.0, -18.1 - (3.2 if b.deployed else 0.0), 1745.0)

    route_specs = (
        ("GAS-MAIN", gas_points, 1.00, 0.65, "FULLFLOW-VALVE-001", "WP04-FULLFLOW-MANIFOLD",
         "ASTM A269 TP316L seamless capillary, 2.00 mm OD x 0.35 mm wall, solution annealed; controlled braze alloy; clean, passivate, helium leak and 20.7 MPa proof", "20.7 MPa proof",
         "ASTM A269 TP316L seamless capillary tube; controlled silver-braze termination alloy"),
        ("PILOT-LINE", pilot_points, 0.75, 0.45, "FULLFLOW-VALVE-001", "WP04-LATCH-001",
         "ASTM A269 TP316L seamless capillary, 1.50 mm OD x 0.30 mm wall, solution annealed; controlled braze alloy; clean, passivate, helium leak and 20.7 MPa proof", "20.7 MPa proof",
         "ASTM A269 TP316L seamless capillary tube; controlled silver-braze termination alloy"),
        ("BOWDEN-SHEATH", bowden_points, 0.80, 0.42, "WATER-TRIGGER-HSG-001", "WP04-LATCH-001",
         "PTFE liner with 316 stainless spiral support and overbraid; swaged 316 terminal sleeves; 445 N pull proof and full-stroke life test", "Non-pressure control cable",
         "PTFE liner / 316 stainless spiral-and-overbraid composite / 316 swaged terminal sleeves"),
        ("BOWDEN-WIRE", bowden_wire_points, 0.30, None, "WATER-TRIGGER-HSG-001", "WP04-SEAR-001",
         "0.60 mm 1x19 cold-worked 316 stainless control wire; matched-die 316 swaged barrel nipples; 445 N pull proof and full-stroke life test", "445 N tensile proof",
         "0.60 mm 1x19 cold-worked 316 stainless wire with 316 swaged terminal barrels"),
    )

    route_mass_kg = {
        "GAS-MAIN": 0.013522247,
        "PILOT-LINE": 0.008495814,
        "BOWDEN-SHEATH": 0.009000000,
        "BOWDEN-WIRE": 0.002744317,
    }
    route_mass_basis = {
        "GAS-MAIN": "1690.2809 mm3 controlled 316L tube/termination envelope at 8.00e-6 kg/mm3.",
        "PILOT-LINE": "1061.9767 mm3 controlled 316L tube/termination envelope at 8.00e-6 kg/mm3.",
        "BOWDEN-SHEATH": "Controlled finished-article mass including PTFE liner, 316 spiral/overbraid and swaged terminals.",
        "BOWDEN-WIRE": "343.0397 mm3 controlled 316 wire/terminal envelope at 8.00e-6 kg/mm3.",
    }
    route_occurrences: dict[str, str] = {}
    for rid, points, ro, ri, origin, destination, process, rating, material in route_specs:
        if rid == "PILOT-LINE":
            main_shape = g.planar_tangent_routed_round(
                [(6.5, repack.FULLFLOW_VALVE_Z_MM),
                 (26.2, repack.FULLFLOW_VALVE_Z_MM + 35.0), (26.2, 1642.5),
                 (24.0, 1660.0), (18.0, 1690.0)],
                ro, ri, bend_radius=3.0, clock_deg=325.0,
            )
            tail_points = [
                polar_point(18.0, 325.0, 1670.0), polar_point(18.0, 325.0, 1690.0),
                polar_point(18.0, 315.0, 1700.0), polar_point(18.0, 300.0, 1720.0),
                polar_point(18.0, 290.0, 1735.0), polar_point(18.0, 280.0, 1748.0),
                polar_point(21.1, 270.0, 1753.85),
            ]
            tail_local, tail_loc = localize(tail_points)
            tail_shape = g.moved(
                g.tangent_routed_round(tail_local, ro, ri, bend_radius=3.0), tail_loc
            )
            global_route = main_shape.fuse(tail_shape)
            route_origin = polar_point(6.5, 325.0, repack.FULLFLOW_VALVE_Z_MM)
            route_shape = global_route.translate(tuple(-value for value in route_origin))
            route_loc = g.translation_loc(*route_origin)
        elif rid == "BOWDEN-SHEATH":
            main_shape = g.planar_tangent_routed_round(
                [(0.0, repack.WATER_TRIGGER_Z_MM + 57.5),
                 (0.0, repack.WATER_TRIGGER_Z_MM + 62.0),
                 (18.0, repack.WATER_TRIGGER_Z_MM + 65.0),
                 (23.0, repack.WATER_TRIGGER_Z_MM + 75.0),
                 (26.2, repack.WATER_TRIGGER_Z_MM + 90.0),
                 (26.2, 1642.5), (24.0, 1660.0), (17.0, 1690.0)],
                ro, ri, bend_radius=2.0, clock_deg=205.0,
            )
            tail_points = [
                polar_point(17.0, 205.0, 1670.0), polar_point(17.0, 205.0, 1690.0),
                polar_point(17.0, 225.0, 1700.0), polar_point(17.0, 240.0, 1720.0),
                polar_point(17.0, 255.0, 1735.0), polar_point(17.0, 260.0, 1745.0),
                polar_point(18.1, 270.0, 1745.0),
            ]
            tail_local, tail_loc = localize(tail_points)
            tail_shape = g.moved(
                g.tangent_routed_round(tail_local, ro, ri, bend_radius=3.0), tail_loc
            )
            global_route = main_shape.fuse(tail_shape)
            route_origin = (0.0, 0.0, repack.WATER_TRIGGER_Z_MM + 57.5)
            route_shape = global_route.translate(tuple(-value for value in route_origin))
            route_loc = g.translation_loc(*route_origin)
        else:
            local_points, route_loc = localize(points)
            route_shape = g.tangent_routed_round(
                local_points, ro, ri,
                bend_radius={"GAS-MAIN": 4.0, "BOWDEN-SHEATH": 3.0,
                             "BOWDEN-WIRE": 3.0}[rid],
            )
        route = b.define(
            f"DF8-FINAL-{rid}-001", "A", f"COMPLETE TERMINATED {rid.replace('-', ' ')} ASSEMBLY",
            route_shape, material, "MAKE", "STINGRAY controlled route assembly", "DRAWING_DERIVED",
            mass_kg=route_mass_kg[rid], process=process,
            notes=(f"Controlled centerline and end terminations; {rating}; 100% continuity/engagement inspection. "
                   f"State-invariant mass basis: {route_mass_basis[rid]}"),
            color_key="route" if "BOWDEN" not in rid else "black",
        )
        oid = b.add(
            b.arm_module, path, route, f"ROUTE-{rid}-001", route_loc,
            "FLEXIBLE" if "BOWDEN" in rid else "FIXED", "FORMED_ROUTE_WITH_CAPTURED_END_FITTINGS",
            "CONTROLLED FLEXURE" if "BOWDEN" in rid else "0",
            notes="Non-identity placement carries the route-local origin to its first modeled port face.",
        )
        route_occurrences[rid] = oid
        b.add_route_record(
            oid, origin, destination,
            "Modeled port ferrules, ring glands, swaged/brazed end terminations",
            "Counterbored FWD-RING-02 and AFT-ROUTE-RING passages plus WP04 reaction-bulkhead passages",
            "Forward standoffs, two structural-ring glands, continuous arm-longeron channel, aft annular corridor",
            35.0, 12.0 if "BOWDEN" in rid else 4.0, rating, "COMPLETE",
            maximum_endpoint_gap_mm=0.20,
            termination_occurrence_ids=([] if rid == "BOWDEN-WIRE" else [f"GLAND-{rid}-FWD", f"GLAND-{rid}-AFT"]),
            support_occurrence_ids=([] if rid == "BOWDEN-WIRE" else [f"GLAND-{rid}-FWD", f"GLAND-{rid}-AFT"]),
            integral_terminations=True,
            integral_support=True,
            penetration_occurrence_ids=[],
            integral_penetrations=True,
        )

    # One-piece bulkhead gland assemblies include the bored body, both
    # ferrule shoulders, and captive external collars.  Their bores clear the
    # routed article; the flanges sit face-to-face outside the ring faces.
    for rid, phi, ro in (("GAS-MAIN", 85.0, 1.00), ("PILOT-LINE", 325.0, 0.75), ("BOWDEN-SHEATH", 205.0, 0.80)):
        gland = b.define(
            f"DF8-FINAL-{rid}-RING-GLAND", "A", f"{rid.replace('-', ' ')} TWO-COLLAR BULKHEAD GLAND",
            g.make_axial_bulkhead_union((ro + 0.90) * 2.0, (ro + 0.08) * 2.0, (ro + 1.45) * 2.0, 8.0),
            "316 stainless steel", "MAKE", "STINGRAY controlled micro-fitting drawing", "DRAWING_DERIVED",
            process="Swiss turn body/collars; laser braze collars; passivate; helium leak check",
            notes="Integral controlled fitting assembly; route bore includes diagonal-transition clearance.", color_key="stainless",
        )
        forward_gland_z = (
            repack.WATER_TRIGGER_Z_MM + 90.0
            if rid == "BOWDEN-SHEATH"
            else repack.FULLFLOW_VALVE_Z_MM + 35.0
        )
        for station, z in (("FWD", forward_gland_z), ("AFT", 1638.0)):
            x, y = radial_xy(26.2, phi)
            b.add(b.arm_module, path, gland, f"GLAND-{rid}-{station}", g.translation_loc(x, y, z), "FIXED", "SHOULDERED_BULKHEAD_GLAND")

    # Occurrence-specific split guide liners physically support the full
    # 889..1634 mm fixed-sector spans.  The route has 0.10 mm radial running
    # clearance, the liner has 0.02 mm clearance in its exact bored channel,
    # and short shoulders seat at the existing counterbore steps.
    for rid, base_phi, route_ro in (
        ("GAS-MAIN", 60.0, 1.00),
        ("PILOT-LINE", 300.0, 0.75),
        ("BOWDEN-SHEATH", 180.0, 0.80),
    ):
        liner = b.define(
            f"DF8-FINAL-{rid}-FIXED-SECTOR-GUIDE-LINER", "A",
            f"SPLIT PEEK GUIDE LINER FOR {rid.replace('-', ' ')} LONG SPAN",
            g.make_route_guide_liner_local(route_ro), "PEEK", "MAKE",
            "STINGRAY controlled guide-liner drawing", "DRAWING_DERIVED",
            process="Machine matched split halves; install in jig-bored sector channel; close end shoulders; inspect radial clearance and pull retention",
            notes="One occurrence-specific exact support spans the complete arm-module corridor; end shoulders are trapped between the two bulkhead glands.",
            color_key="peek",
        )
        b.add(
            b.arm_module, path, liner, f"ROUTE-LINER-{rid}-001",
            g.rotation_loc((0, 0, 1), base_phi) * g.translation_loc(0, 0, 895.4),
            "FIXED", "SPLIT_LINER_CAPTURED_IN_FIXED_SECTOR",
        )

    fullflow_manifold = b.define(
        "DF8-FINAL-WP04-FULLFLOW-MANIFOLD", "A", "WP04 FULL-FLOW TERMINAL MANIFOLD WITH BRAZED GAS PORT",
        g.tube_z(2.2, 1.10, 10.0, z0=-5.0), "316 stainless steel", "MAKE",
        "STINGRAY controlled manifold drawing", "DRAWING_DERIVED",
        process="Swiss turn; braze to WP04 discharge tube; passivate; helium leak and 20.7 MPa proof",
        notes="Gas-main route seats at the modeled forward port face; aft outlet is controlled by WP04 buoy-pack plumbing.",
        color_key="stainless",
    )
    mx, my = radial_xy(22.5, 85.0)
    b.add(b.arm_module, path, fullflow_manifold, "WP04-FULLFLOW-MANIFOLD", g.translation_loc(mx, my, 1725.0), "FIXED", "BRAZED_TO_WP04_DISTRIBUTION_TUBE")
    manifold_bracket = b.define(
        "DF8-FINAL-WP04-MANIFOLD-BRACKET", "A", "WP04 FULL-FLOW MANIFOLD RADIAL SUPPORT BRACKET",
        g.box_center(0.6, 2.0, 4.0, 2.5, 0.0, 0.0), "Ti-6Al-4V", process="5-axis mill; laser weld to aft shell land", color_key="titanium",
    )
    bracket_loc = g.rotation_loc((0, 0, 1), 85.0) * g.translation_loc(22.5, 0.0, 1725.0)
    b.add(b.arm_module, path, manifold_bracket, "WP04-MANIFOLD-BRACKET", bracket_loc, "FIXED", "WELDED_RADIAL_SUPPORT")


def build_aft(b: R2Builder) -> None:
    path = "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY"
    shell = b.define("DF8-R2-AFT-SHELL-001", "A", "AFT GRADE-9 SHELL WITH HARDPOINT AND HINGE APERTURES", aft_shell_with_openings(),
                     "Ti-3Al-2.5V Grade 9", process="Cold draw; laser cut controlled apertures", color_key="titanium")
    b.add(b.aft, path, shell, "AFT-SHELL-001", g.translation_loc(0, 0, 1635.0), "FIXED", "WELDED_TO_ROUTE_RING_AND_SERVICE_THROAT")
    route_ring = b.define("DF8-R2-AFT-ROUTE-RING-001", "A", "AFT STRUCTURAL RING WITH CONTROLLED ROUTE PASSAGES",
                          ring_with_axial_route_holes(8.0, route_transition="INWARD"), "Ti-6Al-4V", process="Mill-turn and jig-bore", color_key="titanium")
    b.add(b.aft, path, route_ring, "AFT-ROUTE-RING-001", g.translation_loc(0, 0, 1638.0), "FIXED", "LASER_WELDED_RING_JOINT")
    aft_longeron = b.define("DF8-R2-AFT-LONGERON-001", "A", "AFT PRIMARY LOAD-PATH LONGERON", make_body_longeron(253.8),
                            "Ti-6Al-4V", process="5-axis mill", color_key="titanium")
    for idx, phi in enumerate((60.0, 180.0, 300.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(0, 0, 1642.1)
        b.add(b.aft, path, aft_longeron, f"AFT-LONGERON-{idx}", loc, "FIXED", "WELDED_BETWEEN_STRUCTURAL_RINGS")

    bulkhead = b.define(
        "WP04-RB-001-R2", "B",
        "SPRING REACTION BULKHEAD WITH GUIDE-RAIL BORES AND PERMANENT SHELL LAND",
        g.make_reaction_bulkhead_local(), "Ti-6Al-4V",
        process="5-axis mill; pilot to shell; qualified circumferential laser weld; dimensional inspection",
        color_key="titanium",
    )
    b.add(
        b.aft, path, bulkhead, "WP04-REACTION-BULKHEAD",
        g.translation_loc(0, 0, 1655.0), "FIXED",
        "PILOTED_QUALIFIED_PERMANENT_SHELL_JOINT",
    )
    rail_shape = g.box_center(3.0, 5.0, 190.0, 0, 0, 95.0)
    # Integral circular end lands surround each captive screw head.  The
    # pockets receive the full 5.5 mm head envelope while leaving a positive
    # annular bearing shoulder at the shank plane and preserving a connected
    # PEEK rail from end to end.
    rail_shape = rail_shape.fuse(g.cyl_z(3.30, 6.10, 0.4, 0.0, 0.00))
    rail_shape = rail_shape.fuse(g.cyl_z(3.30, 6.00, 0.4, 0.0, 184.00))
    rail_shape = rail_shape.cut(g.cyl_z(1.65, 3.4, 0.4, 0.0, -0.2))
    rail_shape = rail_shape.cut(g.cyl_z(1.65, 3.4, 0.4, 0.0, 186.8))
    rail_shape = rail_shape.cut(g.cyl_z(2.79, 3.10, 0.4, 0.0, 3.00))
    rail_shape = rail_shape.cut(g.cyl_z(2.79, 3.25, 0.4, 0.0, 183.75))
    rail = b.define("WP04-GUIDE-RAIL-001-R2", "C", "FOLLOWER ANTI-ROTATION GUIDE RAIL WITH TWO M3 CAPTIVE-SCREW END LANDS", rail_shape,
                    "PEEK", process="Machine rail, slots, integral end lands, two clearance bores and two head pockets", color_key="peek")
    for idx, phi in enumerate((0.0, 120.0, 240.0), 1):
        loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(19.6, 0, 1658.0)
        b.add(b.aft, path, rail, f"WP04-GUIDE-RAIL-{idx}", loc, "FIXED", "M3_BOLTED_TO_REACTION_AND_STOP_RINGS")

    follower = b.define("WP04-FOL-001-R2", "A", "CAPTIVE PEEK FOLLOWER WITH THREE GUIDE SLOTS", g.make_follower_plate_local(),
                        "PEEK", process="5-axis machine", color_key="peek")
    follower_z = 1830.0 if b.deployed else 1745.0
    b.add(b.aft, path, follower, "WP04-FOLLOWER-001", g.translation_loc(0, 0, follower_z), "MOVING", "THREE_RAIL_GUIDED_TRANSLATION", "1 AXIAL TRANSLATION 85 MM")

    spring_len = g.WP04_SPRING_DEPLOYED if b.deployed else g.WP04_SPRING_STOWED
    wp04_spring = b.define("DF8-FINAL-WP04-EJECTOR-SPRING-001", "A", "CONTROLLED LONG-STROKE GUIDED EJECTOR SPRING",
                           g.make_compression_spring_local(g.WP04_SPRING_OD, g.WP04_SPRING_WIRE, spring_len, 18.5),
                           "EN 10270-3 1.4310 stainless spring wire, 2.00 mm", "MAKE", "STINGRAY controlled spring drawing", "DRAWING_DERIVED",
                           mass_kg=0.0319863,
                           process="Cold coil 18.5 active turns with closed-ground ends; stress relieve; passivate; inspect OD/free length/rate/solid height; 100% 115 mm proof stroke and 50-cycle deployment acceptance",
                           notes="Custom long-stroke article replaces the unsuitable catalog VD-244 dynamic-stroke application; 22.0 mm OD, 200.0 mm free length, 2.0 mm wire, 0.946 N/mm target rate, 85.0 mm minimum installed length and 170.0 mm released installed length.", color_key="spring")
    b.add(b.aft, path, wp04_spring, "WP04-EJECTOR-SPRING", g.translation_loc(0, 0, 1660.0), "FLEXIBLE", "OVERLAPPING_GUIDE_SLEEVES", "AXIAL COMPRESSION")
    fixed_sleeve_shape = g.tube_z(8.40, 7.70, 84.0)
    # Forward mounting shoulder touches the bulkhead spider at z=1658; the
    # raised spring seat ends at z=1660 and receives the first closed coil.
    fixed_sleeve_shape = fixed_sleeve_shape.fuse(g.tube_z(14.50, 7.70, 1.20))
    fixed_sleeve_shape = fixed_sleeve_shape.fuse(g.tube_z(10.90, 7.70, 0.80, z0=1.20))
    for phi in (0.0, 120.0, 240.0):
        x, y = radial_xy(12.70, phi)
        fixed_sleeve_shape = fixed_sleeve_shape.cut(
            g.make_tapped_hole_cutter_z(2.50, 2.20, 3.0, z0=0.0).translate((x, y, 0.0))
        )
    sleeve_fixed = b.define("WP04-FIXED-GUIDE-SLEEVE-R2", "C", "BULKHEAD-MOUNTED FIXED TELESCOPING SPRING GUIDE AND SEAT", fixed_sleeve_shape,
                            "PEEK", process="Turn mounting shoulder, guide bore and closed-coil seat in one setup", color_key="peek")
    moving_sleeve_shape = g.tube_z(7.40, 6.80, 100.60)
    # Forward closed-coil seat lies inside the follower's r=11.70 bore with
    # 0.05 mm radial clearance.  It is integral to the moving sleeve, so the
    # spring load passes directly into the screw-retained follower joint.
    moving_sleeve_shape = moving_sleeve_shape.fuse(
        g.tube_z(11.65, 6.80, 1.0, z0=98.0)
    )
    # The aft flange begins on the follower aft face.  It is beyond the
    # spring endpoint and therefore mounts the sleeve without occupying a
    # coil or the follower annulus.
    moving_sleeve_shape = moving_sleeve_shape.fuse(g.tube_z(17.0, 6.80, 3.0, z0=100.50))
    for phi in (60.0, 180.0, 300.0):
        x, y = radial_xy(15.0, phi)
        moving_sleeve_shape = moving_sleeve_shape.cut(
            g.make_tapped_hole_cutter_z(2.50, 3.20, 3.0, z0=100.50).translate((x, y, 0.0))
        )
    sleeve_moving = b.define("WP04-MOVING-GUIDE-SLEEVE-R2", "C", "FOLLOWER-MOUNTED INNER TELESCOPING SPRING GUIDE SLEEVE", moving_sleeve_shape,
                             "PEEK", process="Turn guide and integral follower-face mounting flange", color_key="peek")
    b.add(b.aft, path, sleeve_fixed, "WP04-FIXED-SLEEVE", g.translation_loc(0, 0, 1658.0), "FIXED", "SHOULDER_AND_THREE_M3_SCREWS")
    b.add(b.aft, path, sleeve_moving, "WP04-MOVING-SLEEVE", g.translation_loc(0, 0, follower_z - 98.0), "MOVING", "PILOTED_IN_FOLLOWER")

    latch_shape = g.box_center(4.2, 15.0, 16.0, 2.1, 0.0, 0.0)
    latch_shape = latch_shape.cut(cq.Solid.makeCylinder(2.18, 4.8, cq.Vector(-0.3, 0, 0), cq.Vector(1, 0, 0)))
    latch_shape = latch_shape.cut(g.cyl_z(1.05, 16.4, 1.0, 0.0, -8.2))
    # Fixed inward Bowden boss: the r=0.85 bore captures the r=0.80 sheath
    # with 0.05 mm radial clearance while the reduced sear nose and wire pass
    # through the same coaxial terminal stack.
    bowden_boss = g.tube_between((-3.5, 0.0, 0.0), (0.3, 0.0, 0.0), 2.0, 0.85)
    latch_shape = latch_shape.fuse(bowden_boss)
    latch_shape = latch_shape.cut(
        cq.Solid.makeCylinder(2.18, 4.8, cq.Vector(-0.3, 0, 0), cq.Vector(1, 0, 0))
    )
    for y in (-6.0, 6.0):
        latch_shape = latch_shape.cut(g.cyl_z(1.65, 7.4, 2.1, y, -8.2))
        latch_shape = latch_shape.cut(g.cyl_z(2.79, 3.4, 2.1, y, -1.2))
    latch = b.define("WP04-LATCH-HOUSING-R2", "A", "RADIAL FOLLOWER LATCH HOUSING WITH REAMED SEAR GUIDE", latch_shape,
                     "17-4PH stainless steel", process="5-axis mill and ream", color_key="steel")
    sear_shape = cq.Solid.makeCylinder(0.28, 3.0, cq.Vector(-3.0, 0, 0), cq.Vector(1, 0, 0))
    sear_shape = sear_shape.fuse(
        cq.Solid.makeCylinder(2.0, 5.0, cq.Vector(0.0, 0, 0), cq.Vector(1, 0, 0))
    )
    sear_shape = sear_shape.fuse(cq.Solid.makeCylinder(2.8, 0.8, cq.Vector(5.0, 0, 0), cq.Vector(1, 0, 0)))
    groove_outer = cq.Solid.makeCylinder(2.25, 0.45, cq.Vector(4.25, 0, 0), cq.Vector(1, 0, 0))
    groove_core = cq.Solid.makeCylinder(1.75, 0.65, cq.Vector(4.15, 0, 0), cq.Vector(1, 0, 0))
    sear_shape = sear_shape.cut(groove_outer.cut(groove_core))
    sear = b.define("WP04-LATCH-SEAR-R2", "A", "CAPTIVE RADIAL FOLLOWER SEAR PLUNGER WITH RETAINING RING", sear_shape,
                    "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    sear_clip = b.define("WP04-LATCH-SEAR-E-RING-R2", "A", "4 MM SEAR PIN EXTERNAL RETAINING RING",
                         g.make_external_retaining_ring(4.0, 0.45),
                         "1.4310 stainless spring steel", process="Stamped spring ring", color_key="spring")
    latch_loc = g.rotation_loc((0, 0, 1), 270.0) * g.translation_loc(21.1, 0, 1745.0)
    b.add(b.aft, path, latch, "WP04-LATCH-001", latch_loc, "FIXED", "M3_BOLTED_TO_GUIDE_RAIL")
    sear_shift = 3.2 if b.deployed else 0.0
    sear_loc = latch_loc * g.translation_loc(sear_shift, 0, 0)
    b.add(b.aft, path, sear, "WP04-SEAR-001", sear_loc, "MOVING", "GUIDED_SEAR_WITH_E_RING", "1 TRANSLATION")
    b.add(b.aft, path, sear_clip, "WP04-SEAR-CLIP-001",
          latch_loc * g.translation_loc(sear_shift + 4.475, 0, 0) * g.rotation_loc((0, 0, 1), 90.0),
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
    hinge_pin = b.define("WP05-HINGE-PIN-R2", "B", "DOOR HINGE PIN WITH EXTERNAL RETAINER", g.make_clevis_pin(3.0, 15.0, 5.0, 1.0),
                         "17-4PH stainless steel", process="Swiss turn and grind", color_key="steel")
    hinge_clip = b.define("WP05-HINGE-CRESCENT-RING-R2", "A", "3 MM HINGE-PIN EXTERNAL CRESCENT RETAINER",
                          g.make_external_retaining_ring(3.0, 0.40), "1.4310 stainless spring steel",
                          process="Stamped retaining ring; dimensional inspection", color_key="spring")
    hinge_loc = g.translation_loc(28.0, -7.5, 2028.0)
    b.add(b.aft, path, hinge_pin, "WP05-HINGE-PIN", hinge_loc, "FIXED", "HINGE_PIN_WITH_E_RING")
    b.add(b.aft, path, hinge_clip, "WP05-HINGE-CLIP", g.translation_loc(28.0, 6.7, 2028.0), "FIXED", "EXTERNAL_GROOVE_RETAINER")
    detent = b.define("GN-615.3-M3-KN-PFB", "CATALOG", "JW WINCO M3 STAINLESS BALL PLUNGER", radial_detent_shape(),
                      "AISI 303 housing / hardened AISI 420C ball / AISI 631 spring / PFB polyamide patch", "BUY", "JW Winco / Ganter", "DRAWING_DERIVED",
                      mass_kg=0.000482889,
                      source_url="https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
                      purchase_url="https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Spring-plungers/GN-615.3-Steel-Stainless-Steel-Ball-Plungers-with-thread-locking-with-ball-with-internal-hexagon",
                      notes="Exact GN 615.3 M3 KN PFB identity; 8.0 mm housing length, 1.5 mm ball travel, 3.0/4.5 N initial/final spring load; incoming dimensional/material verification and four-place seating-force inspection. Explicit mass is the 61.1253 mm3 authored catalog envelope at the controlled mixed-stainless density basis (~7.9e-6 kg/mm3).", color_key="stainless")
    for idx, phi in enumerate((45.0, 135.0, 225.0, 315.0), 1):
        x, y = radial_xy(23.25, phi)
        loc = g.translation_loc(x, y, 2026.5) * g.rotation_loc((0, 0, 1), phi)
        b.add(b.aft, path, detent, f"DOOR-DETENT-{idx}", loc, "FIXED", "M3_THREADED_AND_THREADLOCKED")

    # Flexible buoy articles preserve stable IDs while changing exact state geometry.
    # Preserve the verified terminal-to-harness alignment while bringing the
    # deployed rigid recovery terminal inside the 2032 mm product limit.  The
    # buoy/harness moves with the terminal by the same 30.5 mm so no flexible
    # connection is stretched or cosmetically detached.
    buoy_center_z = 2276.5
    for gi in range(8):
        shape = g.make_buoy_gore_deployed_local(gi) if b.deployed else g.make_buoy_gore_stowed_local(gi)
        gore = b.define(f"DF8-R2-BUOY-GORE-{gi+1:02d}", "A", f"60 L BUOY GORE {gi+1} OF 8", shape,
                        "TPU-coated nylon", mass_kg=0.02375,
                        process="Waterjet cut; RF weld 12 mm seams; leak and inflation proof", color_key="softgood")
        loc = g.translation_loc(0, 0, buoy_center_z) if b.deployed else g.translation_loc(0, 0, 1845.0)
        b.add(b.aft, path, gore, f"BUOY-GORE-{gi+1:02d}", loc, "SOFTGOOD", "RF_WELDED_GORE_SEAMS", "FLEXIBLE MEMBRANE")

    for hi in (1, 2):
        if b.deployed:
            band_shape = g.make_harness_band_local() if hi == 1 else g.make_harness_band_overpass_local()
        else:
            band_shape = g.make_harness_band_stowed_local(hi)
        harness = b.define(f"DF8-R2-HARNESS-BAND-{hi}", "A", f"X-6292 STRUCTURAL HARNESS CLOSED BAND {hi}", band_shape,
                           "UHMWPE webbing", "MAKE", "Sturges X-6292 raw webbing / STINGRAY finished assembly",
                           "DRAWING_DERIVED", mass_kg=0.045,
                           source_url="https://www.sturgesmfgco.com/webbing/engineered-webbing/uhmwpe/",
                           purchase_url="https://www.sturgesmfgco.com/contact/",
                           process="Cut, fold, controlled stitch pattern and 8.9 kN finished-loop proof load",
                           notes="Finished MAKE article from exact X-6292 raw webbing; lot CoC and proof record required.", color_key="rope")
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
        ("XP", "HARNESS-BAND-1", (9.0, 0.0, 12.2), (28.0, 0.0, 17.2), (1.0, 0.0)),
        ("XN", "HARNESS-BAND-1", (-9.0, 0.0, 12.2), (-28.0, 0.0, 17.2), (-1.0, 0.0)),
        ("YP", "HARNESS-BAND-2", (0.0, 9.0, 12.2), (0.0, 28.0, 17.2), (0.0, 1.0)),
        ("YN", "HARNESS-BAND-2", (0.0, -9.0, 12.2), (0.0, -28.0, 17.2), (0.0, -1.0)),
    )
    for leg_name, _band_id, terminal_point, deployed_point, direction in leg_specs:
        if b.deployed:
            dx, dy = direction
            radius = 243.309
            center_z_local = buoy_center_z - terminal_z
            def lower_surface(r: float, offset: float) -> float:
                return center_z_local - math.sqrt(radius * radius - r * r) - offset
            if leg_name.startswith("X"):
                # Stay below the orthogonal YZ band until the X leg is beyond
                # its +/-12.7 mm pole width, then rise into the XZ band lap.
                route_points = [
                    terminal_point,
                    (13.0 * dx, 0.0, 11.0),
                    (14.0 * dx, 0.0, lower_surface(14.0, 2.0)),
                    (23.0 * dx, 0.0, lower_surface(23.0, 2.0)),
                    (deployed_point[0], deployed_point[1], lower_surface(28.0, 0.80)),
                ]
            else:
                route_points = [
                    terminal_point,
                    (16.0 * dx, 16.0 * dy, lower_surface(16.0, 2.0)),
                    (23.0 * dx, 23.0 * dy, lower_surface(23.0, 2.0)),
                    # The final stitched lap sits on the outside of the inflated
                    # membrane.  A 0.80 mm radial offset clears the 0.45 mm gore
                    # shell while remaining inside the 1.10 mm harness band.
                    (deployed_point[0], deployed_point[1], lower_surface(28.0, 0.80)),
                ]
        else:
            # Each packed leg runs axially at r=9 inside the hardpoint bore,
            # guide rails and gore inner radius, then fans outward only in its
            # dedicated band lane.  Clocking this canonical radial path by the
            # leg direction keeps all four webs geometrically equivalent.
            dx, dy = direction
            if _band_id == "HARNESS-BAND-1":
                route_points = [
                    (9.0 * dx, 9.0 * dy, 12.2),
                    (9.0 * dx, 9.0 * dy, -90.0),
                    (9.0 * dx, 9.0 * dy, -126.0),
                    (15.831 * dx, 15.831 * dy, -140.0),
                ]
            else:
                route_points = [
                    (9.0 * dx, 9.0 * dy, 12.2),
                    (9.0 * dx, 9.0 * dy, -90.0),
                    (15.831 * dx, 15.831 * dy, -111.0),
                ]

        # Keep each flat web's 8 mm dimension tangential to its radial load
        # path.  The generic strap helper's width axis is global Y for X legs;
        # swapping its rectangular profile axes gives Y legs the equivalent
        # horizontal orientation instead of placing 8 mm of web vertically
        # through the service-throat and buoy membrane.
        segment_width, segment_thickness = ((1.1, 8.0) if leg_name.startswith("Y") else (8.0, 1.1))
        leg_shape = g.strap_between(route_points[0], route_points[1], segment_width, segment_thickness)
        for p0, p1 in zip(route_points[1:-1], route_points[2:]):
            leg_shape = leg_shape.fuse(g.strap_between(p0, p1, segment_width, segment_thickness))
        if not b.deployed:
            # Folded terminal keeper bars pass through the occurrence-matched
            # terminal slots.  Their outer faces meet the machined terminal at
            # zero gap and zero common volume; each bar overlaps its parent
            # web to remain one finished softgood occurrence.
            if leg_name.startswith("X"):
                keeper = g.box_center(
                    1.1, 12.0, 1.1,
                    9.0 if leg_name == "XP" else -9.0,
                    0.0, 12.55,
                )
            else:
                keeper = g.box_center(
                    12.0, 1.1, 1.1,
                    0.0,
                    9.0 if leg_name == "YP" else -9.0,
                    12.55,
                )
            leg_shape = leg_shape.fuse(keeper)
        leg_shape = leg_shape.clean()
        leg = b.define(f"DF8-R2-HARNESS-LEG-{leg_name}", "A", f"X-6292 TERMINAL HARNESS LEG {leg_name}", leg_shape,
                       "UHMWPE webbing", "MAKE", "Sturges X-6292 raw webbing / STINGRAY finished assembly",
                       "DRAWING_DERIVED", mass_kg=0.0075,
                       source_url="https://www.sturgesmfgco.com/webbing/engineered-webbing/uhmwpe/",
                       purchase_url="https://www.sturgesmfgco.com/contact/",
                       process="Fold, controlled bar-tack pattern and 4.45 kN leg proof load",
                       notes="Finished MAKE article; lot CoC, stitch traveler and proof record required.", color_key="rope")
        b.add(b.aft, path, leg, f"HARNESS-LEG-{leg_name}", terminal_loc, "FLEXIBLE", "STITCHED_BAND_TO_TERMINAL_SLOT", "FLEXIBLE")

    if b.deployed:
        for gi in range(1, 9):
            gj = 1 if gi == 8 else gi + 1
            b.allow_intentional_fit(
                f"FIT-RF-SEAM-{gi:02d}-{gj:02d}", f"BUOY-GORE-{gi:02d}", f"BUOY-GORE-{gj:02d}",
                "12_MM_RF_WELD_LAP", 350.0, 390.0,
                "Occurrence-specific 12 mm TPU-coated-nylon RF seam; bounded nominal-layer CAD lap; 100% leak proof.",
            )
    for leg_name, band_id in (("XP", "HARNESS-BAND-1"), ("XN", "HARNESS-BAND-1"),
                              ("YP", "HARNESS-BAND-2"), ("YN", "HARNESS-BAND-2")):
        if b.deployed:
            stitch_bounds = (16.0, 20.0) if leg_name.startswith("X") else (68.0, 82.0)
            stitch_scope = "DEPLOYED"
        else:
            stitch_bounds = (32.0, 40.0) if leg_name.startswith("X") else (46.0, 56.0)
            # Both packed articles are HOLD_STOWED and therefore are not
            # sampled as active dynamic pairs during the arm sweep.
            stitch_scope = "STOWED"
        b.allow_intentional_fit(
            f"FIT-STITCH-{leg_name}", f"HARNESS-LEG-{leg_name}", band_id,
            "CONTROLLED_STITCHED_WEB_LAP", stitch_bounds[0], stitch_bounds[1],
            "Occurrence-matched folded web lap inside the controlled bar-tack envelope; finished assembly proof loaded.",
            state_scope=stitch_scope,
        )
    thimble = b.define("DF8-R2-TETHER-THIMBLE-001", "A", "AMSTEEL EYE-SPLICE THIMBLE", g.make_thimble_local(),
                       "316 stainless steel", process="Stamp and form", color_key="stainless")
    body_thimble_loc = g.translation_loc(24.0, 0, 1900.0)
    harness_thimble_loc = terminal_loc
    b.add(b.aft, path, thimble, "TETHER-THIMBLE-BODY", body_thimble_loc, "MOVING", "PINNED_TO_BODY_HARDPOINT")
    b.add(b.aft, path, thimble, "TETHER-THIMBLE-HARNESS", harness_thimble_loc, "MOVING", "PINNED_TO_HARNESS_TERMINAL")

    tether_shape = g.make_structural_tether_local(-24.0, terminal_z - 1900.0, b.deployed)
    tether = b.define("AMSTEEL-BLUE-872-7-64-R2", "A", "STRUCTURAL RECOVERY TETHER WITH TWO BURIED EYE SPLICES", tether_shape,
                      "HMPE rope", "MAKE", "Samson Rope Technologies raw line / STINGRAY finished splices",
                      "DRAWING_DERIVED", mass_kg=0.020,
                      source_url="https://www.samsonrope.com/mooring/amsteel--blue",
                      purchase_url="https://www.samsonrope.com/resources/find-a-distributor",
                      process="Measure, cut, buried-eye splice, chafe sleeve, proof load",
                      notes="Samson product code 872, 7/64 in; controlled Class II buried-eye splices, chafe sleeves and 4.45 kN finished-assembly proof.", color_key="rope")
    b.add(b.aft, path, tether, "RECOVERY-TETHER-001", body_thimble_loc, "FLEXIBLE", "TWO_EYE_SPLICES_ON_THIMBLES", "FLEXIBLE")

    recovery_pin = b.define("DF8-R2-RECOVERY-PIN-006", "B", "6 MM CAPTIVE RECOVERY TERMINAL PIN WITH RETAINER GROOVE",
                            g.make_clevis_pin(6.0, 11.0, 9.0, 1.5), "17-4PH stainless steel",
                            process="Swiss turn; H900; grind", color_key="steel")
    recovery_clip = b.define("DF8-R2-RECOVERY-E-RING-006", "A", "6 MM RECOVERY PIN EXTERNAL RETAINER",
                             g.make_external_retaining_ring(6.0, 0.5), "1.4310 stainless spring steel",
                             process="Stamped spring ring", color_key="spring")
    for suffix, base_loc in (("BODY", body_thimble_loc), ("HARNESS", harness_thimble_loc)):
        pin_loc = base_loc * g.translation_loc(0, -5.5, 0)
        b.add(b.aft, path, recovery_pin, f"RECOVERY-PIN-{suffix}", pin_loc, "MOVING", "CLEVIS_PIN_WITH_E_RING")
        b.add(b.aft, path, recovery_clip, f"RECOVERY-PIN-CLIP-{suffix}", base_loc * g.translation_loc(0, 4.7, 0), "MOVING", "EXTERNAL_GROOVE")
    b.add_route_record("RECOVERY-TETHER-001", "BODY-HARDPOINT-001", "HARNESS-TERMINAL-001",
                       "Modeled body and harness thimbles with buried-eye splices", "Aft service throat, no wall crossing",
                       "Packed anti-chafe sleeve / deployed free span", 25.0, 50.0, "4.45 kN finished-assembly proof",
                       "COMPLETE", maximum_endpoint_gap_mm=0.30,
                       termination_occurrence_ids=["TETHER-THIMBLE-BODY", "TETHER-THIMBLE-HARNESS"],
                       integral_terminations=True, integral_support=True, integral_penetrations=True,
                       origin_interface_occurrence="TETHER-THIMBLE-BODY",
                       destination_interface_occurrence="TETHER-THIMBLE-HARNESS")

    # Door lanyard remains captive in both states.  The endpoint is the
    # accessible outer tangent of the machined door eye, not the old point in
    # the middle of the door plate.  Both state routes stay outside the throat
    # wall and approach each eye from free space.
    door_eye_vertex = g.moved(cq.Vertex.makeVertex(-15.0, 0.0, -5.5), g.door_occurrence_loc(b.deployed))
    door_eye = door_eye_vertex.toTuple()
    throat_eye_center = (18.0, 0.0, 2005.0)
    throat_tangent = (19.2, 0.0, 2005.0)
    door_tangent = (door_eye[0] + 1.2, 0.0, door_eye[2])
    if b.deployed:
        lanyard_points = [
            throat_tangent,
            (19.2, -4.0, 2005.0),
            (14.0, -18.0, 2020.0),
            (14.0, -18.0, 2032.1),
            (34.0, -18.0, 2032.1),
            (38.0, -18.0, door_eye[2]),
            (38.0, -4.0, door_eye[2]),
            (door_tangent[0], -4.0, door_eye[2]),
            door_tangent,
        ]
    else:
        lanyard_points = [
            throat_tangent,
            (19.2, -4.0, 2005.0),
            (18.0, -4.0, 2020.0),
            (-15.0, -4.0, 2020.0),
            (door_tangent[0], -4.0, door_eye[2]),
            door_tangent,
        ]
    # Use a 1.58 mm finished-line span entering the 1.60 mm swaged-eye stock.
    # The 0.01 mm radial swage upset avoids the equal-radius coincident trim
    # seam that OCCT reports as IntersectingWires after a stowed STEP round trip.
    lanyard_shape = g.routed_round(lanyard_points, 0.79)
    lanyard_shape = lanyard_shape.fuse(cq.Solid.makeTorus(
        1.2, 0.8, cq.Vector(*throat_eye_center), cq.Vector(0, 1, 0)
    ))
    lanyard_shape = lanyard_shape.fuse(cq.Solid.makeTorus(
        1.2, 0.8, cq.Vector(*door_eye), cq.Vector(0, 1, 0)
    )).clean()
    lanyard_solids = lanyard_shape.Solids()
    if len(lanyard_solids) != 1 or not lanyard_shape.isValid():
        raise ValueError(
            f"Door lanyard must be one valid closed-eye exact solid; "
            f"found {len(lanyard_solids)} solids (valid={lanyard_shape.isValid()})"
        )
    lanyard_shape = lanyard_solids[0]
    lanyard = b.define("WP05-DOOR-LANYARD-R2", "A", "CAPTIVE DOOR LANYARD WITH SWAGED EYES", lanyard_shape,
                       "HMPE rope", mass_kg=0.002, process="Swage two thimbled eyes; 445 N pull proof", color_key="rope")
    b.add(b.aft, path, lanyard, "WP05-DOOR-LANYARD", g.identity_loc(), "FLEXIBLE", "TWO_SWAGED_EYES", "FLEXIBLE",
          notes="Identity placement is intentional because the routed lanyard definition uses the product datum frame shared by its two moving endpoints.")


def add_mandatory_hardware_occurrences(b: R2Builder) -> None:
    """Install every helper-owned hardware occurrence at its physical joint."""
    parts = b.catalog.parts
    forward_path = "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY/190_MANDATORY_HARDWARE_ASSY"
    arm_path = "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/390_MANDATORY_HARDWARE_ASSY"
    aft_path = "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY/590_MANDATORY_HARDWARE_ASSY"

    def add(assembly: cq.Assembly, path: str, part_number: str, occurrence_id: str,
            loc: cq.Location, classification: str = "FIXED",
            joint_type: str = "THREADED_FASTENER") -> None:
        b.add(
            assembly, path, parts[part_number], occurrence_id, loc,
            classification, joint_type,
            "0" if classification == "FIXED" else "RIGID_WITH_PARENT",
            notes=(
                "Occurrence-specific exact hardware; location is defined by the "
                "machined coaxial mating features and is not baked into the PartDef."
            ),
        )

    # Forward and aft cartridge-carrier joints use the same four-place
    # cardinal pattern but opposite insertion directions.
    for index, phi in enumerate((0.0, 90.0, 180.0, 270.0), start=1):
        x, y = radial_xy(18.1, phi)
        add(
            b.forward, forward_path, "SSK-M3-6-A4-P80",
            f"FWD-CARRIER-SCREW-{index}",
            g.translation_loc(x, y, 346.14) * g.rotation_loc((1, 0, 0), 180.0),
        )
        add(
            b.forward, forward_path, "SSCF-M3-6-A4",
            f"MANIFOLD-CARRIER-SCREW-{index}",
            g.translation_loc(x, y, 433.0),
        )

    for booster, phi in enumerate((30.0, 150.0, 270.0), start=1):
        for band, z in enumerate((1230.0, 1295.0, 1360.0), start=1):
            band_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(14.0, 0.0, z)
            add(
                b.forward, forward_path, "SSCF-M3-10-A4",
                f"BOOSTER-CLAMP-SCREW-{booster}-{band}",
                band_loc * g.translation_loc(9.0, -4.0, 0.0)
                * g.rotation_loc((1, 0, 0), -90.0),
            )
    for index, phi in enumerate((90.0, 210.0, 330.0), start=1):
        add(
            b.forward, forward_path, "SSCF-M3-10-A4",
            f"TRIGGER-MOUNT-SCREW-{index}",
            g.rotation_loc((0, 0, 1), phi)
            * g.translation_loc(23.30, 0.0, repack.WATER_TRIGGER_Z_MM + 8.0)
            * g.rotation_loc((0, 1, 0), -90.0),
        )

    add(
        b.forward, forward_path, "HTP-3-30-A1", "NOSE-BALLAST-TAPER-PIN-001",
        g.translation_loc(-15.0, 0.0, 170.0) * g.rotation_loc((0, 1, 0), 90.0),
        joint_type="OCCURRENCE_MATCHED_TAPER_PIN",
    )
    add(
        b.forward, forward_path, "HEC-10-A4", "FULLFLOW-VALVE-CIRCLIP-001",
        g.translation_loc(0.0, 0.0, repack.FULLFLOW_VALVE_Z_MM + 24.5), "MOVING", "EXTERNAL_CIRCLIP_IN_GROOVE",
    )
    add(
        b.forward, forward_path, "DF8-WATER-BOBBIN-SERVICE-CAP-001",
        "WATER-BOBBIN-SERVICE-CAP-001",
        g.translation_loc(0.0, 0.0, repack.WATER_TRIGGER_Z_MM)
        * g.rotation_loc((0, 0, 1), 10.0),
        joint_type="POSITIVE_BAYONET_SERVICE_CAP",
    )

    theta = g.DEPLOYED_ANGLE if b.deployed else 0.0
    for arm_index, phi in enumerate((0.0, 120.0, 240.0), start=1):
        arm_loc = g.arm_occurrence_loc(theta, phi)
        pad_loc = arm_loc * g.translation_loc(4.0, 0.0, -8.5)
        for index, x in enumerate((-2.80, 2.80), start=1):
            add(
                b.arm_module, arm_path, "SSCA-M3-8-A4-BL",
                f"ARM-STOP-SCREW-{arm_index}-{index}",
                pad_loc * g.translation_loc(x, -1.80, 0.0)
                * g.rotation_loc((1, 0, 0), -90.0),
                "MOVING", "CAPTIVE_SCREW_IN_ARM_STOP",
            )

        stop_pose = g.arm_occurrence_loc(g.DEPLOYED_ANGLE, phi) * g.translation_loc(4.0, 0.0, -8.5)
        stop_loc = stop_pose * g.translation_loc(-0.4, 0.0, -4.0)
        for index, (screw_x, y) in enumerate(
            g.FIXED_STOP_SCREW_STATIONS_MM, start=1
        ):
            add(
                b.arm_module, arm_path, "SSCA-M3-8-A4-BL",
                f"FIXED-STOP-SCREW-{arm_index}-{index}",
                stop_loc * g.translation_loc(screw_x, y, 2.50),
            )
        for index, y in enumerate((-8.0, 8.0), start=1):
            add(
                b.arm_module, arm_path, "HDP-3-8-A1",
                f"FIXED-STOP-DOWEL-{arm_index}-{index}",
                stop_loc * g.translation_loc(7.0, y, 3.05),
                joint_type="H7_M6_OCCURRENCE_MATCHED_DOWEL",
            )

    spring_station = g.rotation_loc((0, 0, 1), 300.0) * g.translation_loc(12.0, 0.0, 0.0)
    guide = b.global_shapes["BACKUP-SPRING-GUIDE"]
    guide_bb = guide.BoundingBox()
    for index, z in enumerate((g.PIVOT_Z + 0.75, guide_bb.zmax - 2.50), start=1):
        add(
            b.arm_module, arm_path, "SSCF-M3-10-A4",
            f"BACKUP-GUIDE-SCREW-{index}",
            spring_station * g.translation_loc(12.20, 0.0, z)
            * g.rotation_loc((0, 1, 0), -90.0),
        )
    add(
        b.arm_module, arm_path, "SSCL-M4-8-A4", "CROSSHEAD-GUIDE-LOCK-SCREW-001",
        g.translation_loc(0.0, 0.0, repack.ARM_STRUCTURE_START_Z_MM - 2.0),
    )

    # One aft support closes the load path of all three guide rails.
    support_shape = g.tube_z(23.0, 17.5, 3.0)
    for phi in (0.0, 120.0, 240.0):
        x, y = radial_xy(20.0, phi)
        support_shape = support_shape.cut(g.cyl_z(1.25, 3.4, x, y, -0.2))
    rail_support = b.define(
        "WP04-AFT-RAIL-SUPPORT-R2", "A",
        "ONE-PIECE AFT GUIDE-RAIL SUPPORT RING WITH THREE M3 THREADS",
        support_shape, "Ti-6Al-4V", process="Mill-turn; tap 3X M3; weld to three aft longeron lands",
        color_key="titanium",
    )
    b.add(
        b.aft, aft_path, rail_support, "WP04-AFT-RAIL-SUPPORT",
        g.translation_loc(0.0, 0.0, 1848.0), "FIXED",
        "THREE_LONGERON_WELDS_AND_THREE_RAIL_SCREWS",
    )
    for rail, phi in enumerate((0.0, 120.0, 240.0), start=1):
        rail_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(19.6, 0.0, 1658.0)
        add(
            b.aft, aft_path, "SSCA-M3-8-A4-BL", f"GUIDE-RAIL-{rail}-SCREW-FWD",
            rail_loc * g.translation_loc(0.4, 0.0, 3.0)
            * g.rotation_loc((1, 0, 0), 180.0),
        )
        add(
            b.aft, aft_path, "SSCA-M3-8-A4-BL", f"GUIDE-RAIL-{rail}-SCREW-AFT",
            rail_loc * g.translation_loc(0.4, 0.0, 187.0),
        )

    for index, phi in enumerate((0.0, 120.0, 240.0), start=1):
        x, y = radial_xy(12.70, phi)
        add(
            b.aft, aft_path, "SSCA-M3-8-A4-BL", f"WP04-FIXED-SLEEVE-SCREW-{index}",
            g.translation_loc(x, y, 1652.0),
        )

    follower_z = 1830.0 if b.deployed else 1745.0
    for index, phi in enumerate((60.0, 180.0, 300.0), start=1):
        x, y = radial_xy(15.0, phi)
        add(
            b.aft, aft_path, "SSCA-M3-8-A4-BL", f"WP04-MOVING-SLEEVE-SCREW-{index}",
            g.translation_loc(x, y, follower_z - 2.5),
            "MOVING", "CAPTIVE_SCREW_RIGID_WITH_FOLLOWER",
        )

    # A continuous support blade joins the latch underside to guide rail 3.
    bracket_centerline = g.rod_between((-9.8, -16.974, 0.0), (0.0, -23.2, 0.0), 1.50)
    bracket_centerline = bracket_centerline.fuse(g.box_center(15.0, 5.0, 2.0, 0.0, -23.2, 0.0))
    # Conformal 0.01 mm-per-side preparation around Guide Rail 3.  The
    # support blade now terminates on the rail face instead of occupying
    # 17.61 mm3 of the PEEK rail envelope.
    rail_3_clearance = g.box_center(3.02, 5.02, 8.0, 0.0, 0.0, 0.0).rotate(
        (0, 0, 0), (0, 0, 1), 240.0
    ).translate((-9.8, -16.974, 0.0))
    bracket_centerline = bracket_centerline.cut(rail_3_clearance)
    # Face-trim the round transition at the latch mounting plane.  Its former
    # 0.5 mm crown protruded through the otherwise flush support blade and
    # occupied 2.43 mm3 of the latch housing.
    bracket_centerline = bracket_centerline.cut(
        g.box_center(80.0, 80.0, 10.0, 0.0, 0.0, 6.0)
    )
    for x in (-6.0, 6.0):
        bracket_centerline = bracket_centerline.cut(g.cyl_z(1.25, 2.4, x, -23.2, -1.2))
    latch_support = b.define(
        "WP04-LATCH-SUPPORT-R2", "A", "GUIDE-RAIL-3 TO LATCH TWO-SCREW SUPPORT BLADE",
        bracket_centerline, "17-4PH stainless steel", process="5-axis mill; ream rail pilot; tap 2X M3",
        color_key="steel",
    )
    b.add(
        b.aft, aft_path, latch_support, "LATCH-SUPPORT-BRACKET",
        g.translation_loc(0.0, 0.0, 1736.0), "FIXED", "PILOTED_TO_RAIL_3_AND_TWO_M3_LATCH_SCREWS",
        notes="Identity XY definition uses the aft-module product datum; the non-identity Z placement locates the machined support plane.",
    )
    latch_loc = g.rotation_loc((0, 0, 1), 270.0) * g.translation_loc(21.1, 0.0, 1745.0)
    for index, y in enumerate((-6.0, 6.0), start=1):
        add(
            b.aft, aft_path, "SSCA-M3-8-A4-BL", f"WP04-LATCH-SCREW-{index}",
            latch_loc * g.translation_loc(2.1, y, -1.0)
            * g.rotation_loc((1, 0, 0), 180.0),
        )

    for index, phi in enumerate((30.0, 90.0, 150.0, 210.0, 270.0, 330.0), start=1):
        x, y = radial_xy(22.20, phi)
        add(
            b.aft, aft_path, "SSK-M3-6-A4-P80", f"WP05-THROAT-SCREW-{index}",
            g.translation_loc(x, y, 1928.0),
        )

    missing = sorted(hw.HELPER_ADDED_HARDWARE_OCCURRENCE_IDS - set(b.global_shapes))
    duplicated_springs = sorted(
        set(hw.STOW_DOG_RETURN_SPRING_IDS)
        & set(hw.HELPER_ADDED_HARDWARE_OCCURRENCE_IDS)
    )
    if missing or duplicated_springs:
        raise RuntimeError(
            f"Mandatory hardware integration mismatch: missing={missing}, "
            f"duplicated_source_springs={duplicated_springs}"
        )


def add_engineered_fit_register(b: R2Builder) -> None:
    """Register only measured, manufactured positive-volume interfaces.

    The physical endpoint audit is otherwise intersection-free.  Endpoint-
    only records are scoped to their endpoint.  Only retained interfaces on
    active motion-track occurrences use ALL and therefore must be exercised
    by the 0..80 degree motion audit.
    """
    scope = b.state

    if b.deployed:
        for leg_name in ("XP", "XN"):
            b.allow_intentional_fit(
                f"FIT-TERMINAL-LOOP-{leg_name}", f"HARNESS-LEG-{leg_name}",
                "HARNESS-TERMINAL-001", "STITCHED_WEB_LOOP_THROUGH_MACHINED_SLOT",
                22.0, 28.0,
                "Occurrence-specific folded web loop passes through the cardinal terminal slot; controlled bar-tack traveler and 4.45 kN leg proof.",
                state_scope="DEPLOYED",
            )

    tether_bounds = {
        "BODY": (0.0015, 0.0035) if b.deployed else (1.80, 2.30),
        "HARNESS": (0.0015, 0.0035) if b.deployed else (2.30, 2.90),
    }
    for end, thimble in (("BODY", "TETHER-THIMBLE-BODY"),
                         ("HARNESS", "TETHER-THIMBLE-HARNESS")):
        lower, upper = tether_bounds[end]
        b.allow_intentional_fit(
            f"FIT-TETHER-SPLICE-{end}", "RECOVERY-TETHER-001", thimble,
            "CONTROLLED_BURIED_EYE_SPLICE_BEDDING", lower, upper,
            "Occurrence-specific HMPE buried-eye splice is closed around the formed 316 thimble groove; chafe sleeve, splice traveler, dimensional inspection and 4.45 kN proof.",
            state_scope=scope,
        )

    for index in range(1, 5):
        b.allow_intentional_fit(
            f"FIT-DETENT-THREAD-{index}", f"DOOR-DETENT-{index}",
            "WP05-SERVICE-THROAT", "M3_THREADED_HOUSING_ENGAGEMENT",
            2.40, 2.70,
            "Catalog GN 615.3 M3 housing engaged in the occurrence-specific machined throat thread with PFB locking patch; seating depth and force inspected.",
            state_scope=scope,
        )

    for index in range(1, 4):
        b.allow_intentional_fit(
            f"FIT-PIVOT-RETAINER-{index}", f"PIVOT-CLIP-{index}",
            f"PIVOT-PIN-{index}", "EXTERNAL_SPIRAL_RING_IN_MACHINED_GROOVE",
            0.25, 0.32,
            "Occurrence-matched 8 mm spiral ring seated in the ground pivot-pin groove; groove gauge and axial-retention inspection.",
            state_scope=scope,
        )
        b.allow_intentional_fit(
            f"FIT-STOW-INHIBIT-KEEPER-{index}",
            f"STOW-DOG-INHIBIT-KEEPER-{index}",
            f"STOW-DOG-INHIBIT-PIN-{index}",
            "EXTERNAL_CRESCENT_KEEPER_IN_MACHINED_PIN_GROOVE",
            0.015, 0.018,
            "Occurrence-matched spring keeper seated in the inhibit-pin ground external groove; the keeper translates with the pin and is visually inspected in both retained and withdrawn positions.",
            state_scope="DEPLOYED" if b.deployed else "ALL",
        )

    for end in ("BODY", "HARNESS"):
        b.allow_intentional_fit(
            f"FIT-RECOVERY-RETAINER-{end}", f"RECOVERY-PIN-{end}",
            f"RECOVERY-PIN-CLIP-{end}", "EXTERNAL_E_RING_IN_MACHINED_GROOVE",
            0.17, 0.22,
            "Occurrence-matched 6 mm recovery-pin retainer seated in its machined external groove; visual seating and pull retention inspection.",
            state_scope=scope,
        )

    for label in ("GS19", "HBD"):
        for end in ("FIXED", "MOVING"):
            fit_scope = "DEPLOYED" if b.deployed else ("ALL" if end == "MOVING" else "STOWED")
            b.allow_intentional_fit(
                f"FIT-ACTUATOR-RETAINER-{label}-{end}", f"{label}-CLIP-{end}",
                f"{label}-PIN-{end}", "EXTERNAL_E_RING_IN_MACHINED_GROOVE",
                0.10, 0.13,
                "Occurrence-matched actuator-pin retainer seated in the controlled external groove; groove gauge and axial-retention inspection.",
                state_scope=fit_scope,
            )

    b.allow_intentional_fit(
        "FIT-HINGE-RETAINER", "WP05-HINGE-CLIP", "WP05-HINGE-PIN",
        "EXTERNAL_CRESCENT_RING_IN_MACHINED_GROOVE", 0.065, 0.085,
        "Occurrence-matched hinge crescent ring seated in the machined pin groove; seating and axial-retention inspection.",
        state_scope=scope,
    )
    b.allow_intentional_fit(
        "FIT-MANIFOLD-BRACKET-WELD", "AFT-SHELL-001", "WP04-MANIFOLD-BRACKET",
        "QUALIFIED_STRUCTURAL_WELD_LAND", 0.045, 0.065,
        "Occurrence-specific manifold-bracket weld land; qualified argon-purged WPS, controlled overlap, post-weld PT and dimensional inspection.",
        state_scope=scope,
    )
    b.allow_intentional_fit(
        "FIT-PILOT-LATCH-PORT", "ROUTE-PILOT-LINE-001", "WP04-LATCH-001",
        "BRAZED_PILOT_PORT_INSERTION", 0.028, 0.037,
        "Pilot capillary occurrence is inserted to the machined latch-port stop and brazed; insertion depth, helium leak and 20.7 MPa proof inspected.",
        state_scope=scope,
    )
    for route, gland, bounds in (
        ("ROUTE-GAS-MAIN-001", "GLAND-GAS-MAIN-AFT", (0.00050, 0.00075)),
        ("ROUTE-PILOT-LINE-001", "GLAND-PILOT-LINE-AFT", (0.00025, 0.00045)),
        ("ROUTE-BOWDEN-SHEATH-001", "GLAND-BOWDEN-SHEATH-AFT", (0.00030, 0.00050)),
    ):
        b.allow_intentional_fit(
            f"FIT-{gland}-ROUTE", route, gland,
            "CONTROLLED_BULKHEAD_GLAND_FERRULE_ENGAGEMENT", bounds[0], bounds[1],
            "Occurrence-specific route is swaged/brazed into the two-collar aft bulkhead gland; insertion depth, pull/leak and visual seating inspection.",
            state_scope=scope,
        )

    # Mandatory-hardware controlled engagements.  These values are the exact
    # per-solid common volumes measured after every unrelated collision was
    # physically removed.  A two-percent inspection window accommodates only
    # the intended thread-major/minor, groove, bayonet, press-fit, or weld-land
    # representation; every row is occurrence- and solid-specific.
    def measured_hardware_fit(
        exception_id: str,
        occurrence_a: str,
        occurrence_b: str,
        fit_type: str,
        measured_volume_mm3: float,
        process_basis: str,
        state_scope: str,
        solid_index_a: int = 1,
        solid_index_b: int = 1,
    ) -> None:
        tolerance = max(0.000002, measured_volume_mm3 * 0.02)
        b.allow_intentional_fit(
            exception_id, occurrence_a, occurrence_b, fit_type,
            max(0.0, measured_volume_mm3 - tolerance),
            measured_volume_mm3 + tolerance,
            process_basis, state_scope=state_scope,
            solid_index_a=solid_index_a, solid_index_b=solid_index_b,
        )

    measured_hardware_fit(
        "FIT-THREAD-CROSSHEAD-GUIDE-LOCK", "CROSSHEAD-GUIDE-001",
        "CROSSHEAD-GUIDE-LOCK-SCREW-001", "M4_TAPPED_GUIDE_SHOULDER_ENGAGEMENT",
        23.739884709823,
        "Occurrence-specific M4x0.7 low-head screw major envelope engages the authored 3.30 mm tap-drill bore in the crosshead-guide shoulder; inspect thread depth, seating torque, locking control and tool access.",
        scope,
    )

    for index in range(1, 7):
        measured_hardware_fit(
            f"FIT-THREAD-WP05-THROAT-{index}", "WP05-SERVICE-THROAT",
            f"WP05-THROAT-SCREW-{index}", "M3_TAPPED_SERVICE_THROAT_ENGAGEMENT",
            8.757974920045,
            "Occurrence-specific M3 countersunk-screw major envelope engages the authored minor-diameter service-throat flange bore; inspect tap depth, Precote control, seating torque and flush head seating.",
            scope,
        )

    for band in range(1, 4):
        for index in range(1, 4):
            screw = f"BOOSTER-CLAMP-SCREW-{band}-{index}"
            measured_hardware_fit(
                f"FIT-THREAD-BOOSTER-BAND-{band}-{index}", f"BOOSTER-BAND-{band}-{index}",
                screw, "M3_TAPPED_CLAMP_HALF_ENGAGEMENT", 8.639379797372,
                f"Occurrence-specific M3x0.5 rolled-thread major envelope engages the authored minor-diameter tapped clamp half in BOOSTER-BAND-{band}-{index}; inspect tap depth, seating torque, locking control and witness mark.",
                scope,
            )
            shell_volume = 4.070722453394 if (band, index) == (1, 3) else 4.070722453369
            measured_hardware_fit(
                f"FIT-THREAD-BOOSTER-SHELL-LUG-{band}-{index}", screw, "FWD-SHELL-001",
                "M3_TAPPED_SHELL_BACKED_LUG_ENGAGEMENT", shell_volume,
                f"Occurrence-specific shell-integral tangential nut lug carries BOOSTER-CLAMP-SCREW-{band}-{index} behind the relieved clamp head corridor; inspect minor-diameter tap, thread depth, torque, locking control and shell-side witness.",
                scope,
            )

    motion_scope = "DEPLOYED" if b.deployed else "ALL"
    for arm in range(1, 4):
        for index, volume in ((1, 6.479534848029), (2, 6.423784002413)):
            measured_hardware_fit(
                f"FIT-THREAD-ARM-STOP-{arm}-{index}", f"ARM-{arm}",
                f"ARM-STOP-SCREW-{arm}-{index}", "M3_TAPPED_ARM_STOP_BOSS_ENGAGEMENT",
                volume,
                f"Occurrence-specific reversed-service M3 captive screw engages the authored minor-diameter tapped boss in ARM-{arm}; inspect effective thread depth, negative-face head clearance, torque, locking control and witness mark.",
                motion_scope,
            )
        for index in range(1, 3):
            measured_hardware_fit(
                f"FIT-THREAD-FIXED-STOP-CARRIER-{arm}-{index}",
                f"FIXED-STOP-SCREW-{arm}-{index}", f"PIVOT-CARRIER-{arm}",
                "M3_CAPTIVE_THREADED_CARRIER_ENGAGEMENT", 3.488212741352,
                f"Occurrence-specific captive M3 threaded end engages the authored minor-diameter tapped PIVOT-CARRIER-{arm} stop land; inspect thread depth, seating torque, locking control and stop-land bearing.",
                scope, solid_index_a=1, solid_index_b=index,
            )
        measured_hardware_fit(
            f"FIT-PRESS-LOCK-BUSHING-{arm}", f"FIXED-STOP-{arm}",
            f"LOCK-BUSHING-{arm}", "CONTROLLED_PEEK_PRESS_FIT", 0.048594445103,
            f"Occurrence-specific PEEK lock-retainer bushing OD is interference-installed in the FIXED-STOP-{arm} outer seat with a machined fixed-screw relief; inspect bore/OD, installed depth, spring-clear bore and axial pull retention.",
            scope,
        )

    for rail in range(1, 4):
        measured_hardware_fit(
            f"FIT-THREAD-GUIDE-RAIL-{rail}-FWD", f"GUIDE-RAIL-{rail}-SCREW-FWD",
            "WP04-REACTION-BULKHEAD", "M3_TAPPED_REACTION_BULKHEAD_ENGAGEMENT",
            6.479534848029,
            f"Occurrence-specific captive M3 threaded end engages the authored minor-diameter reaction-bulkhead bore for GUIDE-RAIL-{rail}; inspect tap depth, seating torque, locking control and rail-end bearing.",
            scope, solid_index_a=1, solid_index_b=2,
        )
        measured_hardware_fit(
            f"FIT-THREAD-GUIDE-RAIL-{rail}-AFT", f"GUIDE-RAIL-{rail}-SCREW-AFT",
            "WP04-AFT-RAIL-SUPPORT", "M3_TAPPED_AFT_SUPPORT_ENGAGEMENT",
            2.159844949343,
            f"Occurrence-specific captive M3 threaded end engages the authored minor-diameter aft-support bore for GUIDE-RAIL-{rail}; inspect tap depth, seating torque, locking control and rail-end bearing.",
            scope,
        )
        measured_hardware_fit(
            f"FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-{rail}", f"AFT-LONGERON-{rail}",
            "WP04-AFT-RAIL-SUPPORT", "QUALIFIED_LASER_WELD_LAND", 0.421038865428,
            f"Occurrence-specific aft rail-support tongue is laser welded to AFT-LONGERON-{rail} at the modeled controlled land; qualified argon-shielded WPS, post-weld PT and CMM position inspection.",
            scope,
        )

    for index in range(1, 4):
        measured_hardware_fit(
            f"FIT-THREAD-WP04-MOVING-SLEEVE-{index}", "WP04-MOVING-SLEEVE",
            f"WP04-MOVING-SLEEVE-SCREW-{index}", "M3_TAPPED_MOVING_SLEEVE_ENGAGEMENT",
            6.295751677794,
            "Occurrence-specific captive M3 threaded end engages the authored minor-diameter moving-sleeve flange bore; inspect tap depth, seating torque, locking control and follower-face seating.",
            motion_scope,
        )
        measured_hardware_fit(
            f"FIT-THREAD-TRIGGER-MOUNT-{index}", f"TRIGGER-MOUNT-SCREW-{index}",
            "WATER-TRIGGER-HSG-001", "M3_TAPPED_HOUSING_BOSS_ENGAGEMENT",
            5.831581363226,
            "Occurrence-specific M3x0.5 rolled-thread major envelope engages the authored minor-diameter outer trigger-housing boss; inspect tap depth, torque, locking control and shell-side head seating.",
            scope,
        )
        measured_hardware_fit(
            f"FIT-THREAD-WP04-FIXED-SLEEVE-{index}", "WP04-FIXED-SLEEVE",
            f"WP04-FIXED-SLEEVE-SCREW-{index}", "M3_TAPPED_FIXED_SLEEVE_ENGAGEMENT",
            2.408030768977,
            "Occurrence-specific captive M3 threaded end engages the authored minor-diameter fixed-sleeve flange bore; inspect tap depth, seating torque, locking control and pilot seating.",
            scope,
        )

    measured_hardware_fit(
        "FIT-THREAD-BACKUP-GUIDE-1", "BACKUP-GUIDE-SCREW-1",
        "BACKUP-SPRING-GUIDE", "M3_TAPPED_BACKUP_GUIDE_BOSS_ENGAGEMENT",
        6.180153346646,
        "Occurrence-specific M3 screw major envelope engages the authored minor-diameter radial boss in the backup spring guide; inspect tap depth, head seating, torque, locking control and longeron clearance.",
        scope,
    )
    measured_hardware_fit(
        "FIT-THREAD-BACKUP-SEAT-2", "BACKUP-GUIDE-SCREW-2",
        "BACKUP-SPRING-FIXED-SEAT", "M3_TAPPED_BACKUP_SEAT_BOSS_ENGAGEMENT",
        5.939573610693,
        "Occurrence-specific M3 screw major envelope engages the authored minor-diameter radial boss in the backup fixed seat; inspect tap depth, head seating, torque, locking control and guide clearance.",
        scope,
    )
    measured_hardware_fit(
        "FIT-CIRCLIP-FULLFLOW", "FULLFLOW-VALVE-001", "FULLFLOW-VALVE-CIRCLIP-001",
        "DIN471_RING_IN_MACHINED_GROOVE", 5.274151981614,
        "Occurrence-matched DIN 471 ring is seated in the authored 9.6 mm diameter x 1.1 mm valve groove; gauge the groove, visually verify full seating and inspect axial retention.",
        motion_scope,
    )

    for index in range(1, 5):
        measured_hardware_fit(
            f"FIT-THREAD-FWD-CARRIER-{index}", f"FWD-CARRIER-SCREW-{index}",
            "FWD-RING-01", "M3_TAPPED_RING_LAND_ENGAGEMENT", 4.319689898686,
            "Occurrence-specific M3 countersunk-screw major envelope engages the authored minor-diameter structural-ring land; inspect tap depth, Precote control, seating torque and flush head seating.",
            scope,
        )
        measured_hardware_fit(
            f"FIT-THREAD-MANIFOLD-CARRIER-{index}", "COLLECTION-MANIFOLD-001",
            f"MANIFOLD-CARRIER-SCREW-{index}", "M3_TAPPED_MANIFOLD_LAND_ENGAGEMENT",
            4.135906728451,
            "Occurrence-specific M3x0.5 screw major envelope engages the authored minor-diameter tapped manifold land; inspect thread depth, torque, locking control and head seating.",
            scope,
        )

    for index in range(1, 3):
        measured_hardware_fit(
            f"FIT-THREAD-LATCH-SUPPORT-{index}", "LATCH-SUPPORT-BRACKET",
            f"WP04-LATCH-SCREW-{index}", "M3_TAPPED_LATCH_SUPPORT_ENGAGEMENT",
            2.159844949343,
            "Occurrence-specific captive M3 threaded end engages the authored minor-diameter tapped latch-support blade; inspect tap depth, seating torque, locking control and latch seating.",
            scope,
        )

    measured_hardware_fit(
        "FIT-BAYONET-WATER-BOBBIN-SERVICE-CAP", "WATER-BOBBIN-SERVICE-CAP-001",
        "WATER-TRIGGER-HSG-001", "BAYONET_LUG_IN_OCCURRENCE_MATCHED_TRACK",
        0.649824987335,
        "Three occurrence-matched cap lugs engage the authored housing bayonet tracks at the locked stop; inspect insertion/rotation, positive lock, bobbin keeper contact and reset-tool access.",
        scope,
    )


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

    # Corrected occurrence-specific interfaces whose prior joint prose was
    # not backed by direct exact geometry.
    corrected_direct_interfaces = [
        ("CARRIER-FWD-RING", "CARTRIDGE-CARRIER-FWD", "FWD-RING-01", "BOLTED_CARRIER_FACE", "RING_CARRIER_DATUM"),
        ("CARRIER-AFT-MANIFOLD", "CARTRIDGE-CARRIER-AFT", "COLLECTION-MANIFOLD-001", "BOLTED_CARRIER_FACE", "MANIFOLD_FORWARD_FACE"),
        ("GUIDE-SPIDER-RING", "CROSSHEAD-GUIDE-SPIDER", "FWD-RING-02", "THREE_SPOKE_END_LANDS", "THREE_RING_INNER_LANDS"),
        ("GUIDE-SHAFT-SPIDER", "CROSSHEAD-GUIDE-001", "CROSSHEAD-GUIDE-SPIDER", "INTEGRAL_FORWARD_SHOULDER", "SPIDER_HUB_FACE"),
        ("BACKUP-GUIDE-LONGERON", "BACKUP-SPRING-GUIDE", "ARM-LONGERON-3", "FORWARD_RADIAL_MOUNT_FOOT", "LONGERON_INNER_LAND"),
        ("BACKUP-SEAT-LONGERON", "BACKUP-SPRING-FIXED-SEAT", "ARM-LONGERON-3", "AFT_RADIAL_MOUNT_TONGUE", "LONGERON_INNER_LAND"),
        ("BACKUP-GUIDE-SEAT", "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT", "AFT_GUIDE_FLANGE", "FIXED_SEAT_FORWARD_FACE"),
        ("WP04-FIXED-SLEEVE-BULKHEAD", "WP04-FIXED-SLEEVE", "WP04-REACTION-BULKHEAD", "INTEGRAL_FORWARD_SHOULDER", "BULKHEAD_THREE_SPOKE_HUB"),
        ("WP04-MOVING-SLEEVE-FOLLOWER", "WP04-MOVING-SLEEVE", "WP04-FOLLOWER-001", "INTEGRAL_AFT_FLANGE", "FOLLOWER_AFT_FACE"),
        ("WP04-SPRING-FIXED-SEAT", "WP04-EJECTOR-SPRING", "WP04-FIXED-SLEEVE", "CLOSED_FORWARD_COIL", "INTEGRAL_ANNULAR_SPRING_SEAT"),
        ("MANIFOLD-BRACKET", "WP04-FULLFLOW-MANIFOLD", "WP04-MANIFOLD-BRACKET", "MANIFOLD_OD_LAND", "BRACKET_SADDLE"),
        ("BRACKET-SHELL", "WP04-MANIFOLD-BRACKET", "AFT-SHELL-001", "BRACKET_WELD_LAND", "SHELL_WELD_LAND"),
        ("HINGE-CLIP-PIN", "WP05-HINGE-CLIP", "WP05-HINGE-PIN", "CRESCENT_RETAINER", "PIN_EXTERNAL_GROOVE"),
    ]
    for cid, occ, mate, ownf, matef in corrected_direct_interfaces:
        connect_present(
            cid, occ, mate, ownf, matef, "EXACT_SUPPORTED_DIRECT_INTERFACE", "0",
            "Occurrence-specific modeled shoulder, guide, weld land, or retained interface",
            "Modeled axial stop/shoulder", "Modeled pilot, guide, or weld land",
            "Clocked occurrence-specific geometry", mate, occ,
            "Service only at the named occurrence pair",
            f"Direct exact-BREP interface {occ}:{ownf} to {mate}:{matef}",
        )

    for idx in range(1, 4):
        for suffix, occ, mate, ownf, matef in (
            ("STOP-CARRIER", f"FIXED-STOP-{idx}", f"PIVOT-CARRIER-{idx}", "TWIN_CARRIER_TIE_EARS", "CARRIER_MOUNT_LANDS"),
            ("STOW-GUIDE-RING", f"STOW-DOG-GUIDE-{idx}", "AFT-ROUTE-RING-001", "RAISED_RING_MOUNT_PAD", f"DOG_GUIDE_LAND_{idx}"),
            ("STOW-DOG-GUIDE", f"STOW-DOG-{idx}", f"STOW-DOG-GUIDE-{idx}", "DOG_GUIDE_FACES", "FULL_STROKE_U_GUIDE"),
            ("STOW-SPRING-GUIDE", f"STOW-DOG-SPRING-{idx}", f"STOW-DOG-GUIDE-{idx}", "SPRING_FIXED_END", "INTEGRAL_INBOARD_SPRING_SEAT"),
            ("STOW-SPRING-DOG", f"STOW-DOG-SPRING-{idx}", f"STOW-DOG-{idx}", "SPRING_MOVING_END", "DOG_INBOARD_SPRING_FACE"),
            ("STOW-INHIBIT-GUIDE", f"STOW-DOG-INHIBIT-PIN-{idx}", f"STOW-DOG-GUIDE-{idx}", "GROUND_PIN_SHANK", "GUIDE_TRANSPORT_BORE_OR_PARKING_FACE"),
            ("STOW-INHIBIT-DOG", f"STOW-DOG-INHIBIT-PIN-{idx}", f"STOW-DOG-{idx}", "GROUND_PIN_SHANK", "DOG_TRANSPORT_BORE"),
            ("STOW-INHIBIT-KEEPER", f"STOW-DOG-INHIBIT-KEEPER-{idx}", f"STOW-DOG-INHIBIT-PIN-{idx}", "CRESCENT_RETAINER", "PIN_EXTERNAL_GROOVE"),
            ("LOCK-DOG-GUIDE", f"LOCK-DOG-{idx}", f"FIXED-STOP-{idx}", "GROUND_LOCK_SHANK", "LOCK_GUIDE_BORE"),
            ("LOCK-DOG-PAD", f"LOCK-DOG-{idx}", f"ARM-STOP-PAD-{idx}", "LOCK_NOSE", "LOCK_STRIKE_BORE"),
            ("LOCK-SPRING-GUIDE", f"LOCK-SPRING-{idx}", f"FIXED-STOP-{idx}", "SPRING_OUTER_END", "LOCK_GUIDE_CLOSED_SEAT"),
            ("LOCK-BUSHING-GUIDE", f"LOCK-BUSHING-{idx}", f"FIXED-STOP-{idx}", "PRESS_FIT_BUSHING_OD", "LOCK_CHANNEL_OUTER_SEAT"),
        ):
            connect_present(
                f"{suffix}-{idx}", occ, mate, ownf, matef,
                "EXACT_GUIDED_OR_SEATED_INTERFACE", "1 TRANSLATION" if "DOG" in suffix else "0",
                "Integral occurrence-specific guide/seat geometry",
                "Defined end shoulder", "Defined guide clearance", "Clocked guide geometry",
                mate, occ, "Remove occurrence-matched guide hardware",
                f"Direct exact-BREP support {occ}:{ownf} to {mate}:{matef}",
            )

    for rid, sector in (("GAS-MAIN", "FIXED-SECTOR-1"),
                        ("PILOT-LINE", "FIXED-SECTOR-3"),
                        ("BOWDEN-SHEATH", "FIXED-SECTOR-2")):
        route = f"ROUTE-{rid}-001"
        liner = f"ROUTE-LINER-{rid}-001"
        connect_present(
            f"ROUTE-{rid}-LINER", route, liner, "ROUTE_LONG_SPAN_OD", "SPLIT_LINER_GUIDE_ID",
            "CONTINUOUS_GUIDED_ROUTE", "0", "Captured split PEEK liner with two axial end shoulders",
            "Forward/aft liner shoulders", "0.10 mm radial route clearance", "Clocked fixed-sector corridor",
            sector, route, "Release both bulkhead glands and remove split liner",
            f"Exact supported long span {route} in {liner}",
        )
        connect_present(
            f"LINER-{rid}-SECTOR", liner, sector, "LINER_OD_AND_END_SHOULDERS", "BORED_CHANNEL_AND_COUNTERBORES",
            "CAPTURED_SPLIT_LINER", "0", "End shoulders trapped between occurrence-specific bulkhead glands",
            "Counterbore steps", "0.02 mm channel clearance", "Clocked fixed-sector bore",
            sector, liner, "Release both glands and remove split halves",
            f"Exact liner installation {liner} in {sector}",
        )
        for station in ("FWD", "AFT"):
            gland = f"GLAND-{rid}-{station}"
            connect_present(
                f"ROUTE-{rid}-{station}-GLAND", route, gland,
                f"{station}_TERMINATED_ROUTE_OD", "GLAND_FERRULE_BORE",
                "CONTROLLED_BULKHEAD_GLANTED_TERMINATION", "0", "Integral swaged/brazed ferrule and two-collar gland",
                "Ferrule shoulder", "Controlled gland bore", "Clocked structural passage",
                gland, route, "Release the occurrence-specific ferrule/gland",
                f"Exact route/gland interface {route} to {gland}",
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


def add_motion_tracks(b: R2Builder) -> None:
    """Author the complete 0..80 degree arm-sweep scope at one-degree steps.

    The arm train, its links, crosshead, captive moving hardware, and backup
    spring are active in this sweep.  Inflation/ejection, recovery deployment,
    water-valve actuation, and the service-door cycle are independent later
    mechanism phases.  Those articles remain in their stowed, retained state
    during the arm sweep and are independently validated in both endpoint
    masters.
    """
    for arm_index, phi in enumerate((0.0, 120.0, 240.0), start=1):
        arm_id = f"ARM-{arm_index}"
        b.add_motion_track(
            arm_id, "ARM_KINEMATIC",
            "Exact revolute transform about the occurrence-specific 8 mm pivot; 0..80 degrees in 1 degree increments.",
        )
        for link_index, y_offset in enumerate((-1.75, 1.75), start=1):
            samples = [
                {
                    "angle_deg": angle,
                    "transform_matrix_3x4": g.loc_matrix(g.link_occurrence_loc(float(angle), y_offset, phi)),
                }
                for angle in range(81)
            ]
            b.add_motion_track(
                f"LINK-{arm_index}-{link_index}", "KEYFRAMED_TRANSFORMS",
                "Exact closed-form four-bar link transform evaluated from the 19.950 mm center-distance law at every integer degree.",
                samples=samples,
            )
        b.add_motion_track(
            f"LINK-PIN-{arm_index}-BELL", "PARENT_RIGID",
            "Bell-end pin is captive in the arm clevis and inherits the exact arm revolute transform.",
            parent_occurrence_id=arm_id,
        )
        b.add_motion_track(
            f"LINK-CLIP-{arm_index}-BELL", "PARENT_RIGID",
            "Bell-end retainer remains seated in its occurrence-matched pin groove.",
            parent_occurrence_id=f"LINK-PIN-{arm_index}-BELL",
        )
        b.add_motion_track(
            f"LINK-PIN-{arm_index}-CROSSHEAD", "PARENT_RIGID",
            "Crosshead-end pin is captive in the crosshead clevis and inherits exact crosshead translation.",
            parent_occurrence_id="CROSSHEAD-001",
        )
        b.add_motion_track(
            f"LINK-CLIP-{arm_index}-CROSSHEAD", "PARENT_RIGID",
            "Crosshead-end retainer remains seated in its occurrence-matched pin groove.",
            parent_occurrence_id=f"LINK-PIN-{arm_index}-CROSSHEAD",
        )
        b.add_motion_track(
            f"ARM-STOP-PAD-{arm_index}", "PARENT_RIGID",
            "Dovetailed and bolted stop pad is rigidly retained on its occurrence-matched arm.",
            parent_occurrence_id=arm_id,
        )
        for screw_index in range(1, 3):
            b.add_motion_track(
                f"ARM-STOP-SCREW-{arm_index}-{screw_index}", "PARENT_RIGID",
                "Captive stop-pad screw inherits the exact arm/stop-pad revolute transform and remains seated in its counterbore.",
                parent_occurrence_id=f"ARM-STOP-PAD-{arm_index}",
            )
        dog_samples = []
        for angle in range(81):
            # The dog retracts before appreciable arm travel.  The first one-
            # degree sample is the fully retracted detent-limited position.
            dog_radius = 17.0 if angle == 0 else 13.5
            dog_loc = (
                g.rotation_loc((0, 0, 1), phi)
                * g.translation_loc(dog_radius, 0.0, g.PIVOT_Z + g.ARM_LENGTH - 3.5)
            )
            dog_samples.append({
                "angle_deg": angle,
                "transform_matrix_3x4": g.loc_matrix(dog_loc),
            })
        b.add_motion_track(
            f"STOW-DOG-{arm_index}", "KEYFRAMED_TRANSFORMS",
            "Occurrence-specific captive stow dog releases radially before arm rotation and remains at its machined inner stop.",
            samples=dog_samples,
        )
        guide_loc = g.rotation_loc((0, 0, 1), phi) * g.translation_loc(
            0, 0, g.PIVOT_Z + g.ARM_LENGTH - 3.5
        )
        stow_spring_loc = (
            guide_loc
            * g.translation_loc(11.17, 0.0, 0.0)
            * g.rotation_loc((0, 1, 0), 90.0)
        )
        stow_spring_samples = [
            {
                "angle_deg": angle,
                "endpoint_variant": "STOWED" if angle == 0 else "DEPLOYED",
                "transform_matrix_3x4": g.loc_matrix(stow_spring_loc),
            }
            for angle in range(81)
        ]
        b.add_motion_track(
            f"STOW-DOG-SPRING-{arm_index}", "KEYFRAMED_EXACT_BREP_VARIANTS",
            "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
            samples=stow_spring_samples,
        )
        inhibit_samples = [
            {
                "angle_deg": angle,
                "transform_matrix_3x4": g.loc_matrix(
                    guide_loc * g.translation_loc(17.0, -3.0 if angle == 0 else 3.40, 0.0)
                ),
            }
            for angle in range(81)
        ]
        b.add_motion_track(
            f"STOW-DOG-INHIBIT-PIN-{arm_index}", "KEYFRAMED_TRANSFORMS",
            "Headed transport-inhibit pin is withdrawn axially before dog retraction and remains in its modeled guide-side parking interface.",
            samples=inhibit_samples,
        )
        b.add_motion_track(
            f"STOW-DOG-INHIBIT-KEEPER-{arm_index}", "PARENT_RIGID",
            "Occurrence-matched crescent keeper remains seated in the inhibit-pin external groove through withdrawal and parking.",
            parent_occurrence_id=f"STOW-DOG-INHIBIT-PIN-{arm_index}",
        )
        stop_pose = g.arm_occurrence_loc(g.DEPLOYED_ANGLE, phi) * g.translation_loc(4.0, 0, -8.5)
        stop_loc = stop_pose * g.translation_loc(-0.4, 0, -4.0)
        lock_samples = [
            {
                "angle_deg": angle,
                "transform_matrix_3x4": g.loc_matrix(
                    stop_loc * g.translation_loc(
                        0.4,
                        LOCK_DEPLOYED_DOG_Y_MM if angle == 80 else LOCK_RETRACTED_DOG_Y_MM,
                        4.0,
                    )
                ),
            }
            for angle in range(81)
        ]
        b.add_motion_track(
            f"LOCK-DOG-{arm_index}", "KEYFRAMED_TRANSFORMS",
            "Spring-driven lock dog remains fully retracted outside the arm and pad-screw envelopes through 79 degrees, then advances 3.30 mm into positive engagement after bore alignment at 80 degrees.",
            samples=lock_samples,
        )
        lock_spring_loc = (
            stop_loc
            * g.translation_loc(0.4, LOCK_SPRING_OUTER_SEAT_Y_MM, 4.0)
            * g.rotation_loc((1, 0, 0), 90.0)
        )
        lock_spring_samples = [
            {
                "angle_deg": angle,
                "endpoint_variant": "DEPLOYED" if angle == 80 else "STOWED",
                "transform_matrix_3x4": g.loc_matrix(lock_spring_loc),
            }
            for angle in range(81)
        ]
        b.add_motion_track(
            f"LOCK-SPRING-{arm_index}", "KEYFRAMED_EXACT_BREP_VARIANTS",
            "The lock remains fully retracted through 79 degrees and advances 3.30 mm at 80 degrees: each sample audits the exact 1.65 or 4.95 mm installed-length endpoint B-rep matching the lock-dog keyframe.",
            samples=lock_spring_samples,
        )

    b.add_motion_track(
        "CROSSHEAD-001", "CROSSHEAD_KINEMATIC",
        "Exact common-crosshead translation from the closed-form 19.950 mm four-bar closure law.",
    )
    for occurrence_id in (
        "BACKUP-SPRING-MOVING-SEAT", "GS19-ROD-001", "HBD-ROD-001",
        "GS19-PIN-MOVING", "HBD-PIN-MOVING",
    ):
        b.add_motion_track(
            occurrence_id, "PARENT_RIGID",
            "Rigid crosshead-mounted occurrence inherits the exact common-crosshead translation.",
            parent_occurrence_id="CROSSHEAD-001",
        )
    for label in ("GS19", "HBD"):
        b.add_motion_track(
            f"{label}-CLIP-MOVING", "PARENT_RIGID",
            "Moving actuator-pin retainer remains seated in its occurrence-matched groove.",
            parent_occurrence_id=f"{label}-PIN-MOVING",
        )
    b.add_motion_track(
        "BACKUP-SPRING-001", "AXIAL_COMPRESSION_SPRING_KINEMATIC",
        "One exact helical B-rep is rebuilt at every integer-degree sample from the measured separation of the moving-seat +Z land and fixed-seat -Z land.",
        moving_seat_occurrence_id="BACKUP-SPRING-MOVING-SEAT",
        fixed_seat_occurrence_id="BACKUP-SPRING-FIXED-SEAT",
        moving_seat_face_offset_local_z_mm=2.5,
        fixed_seat_face_offset_local_z_mm=-2.5,
        outer_diameter_mm=g.SPRING_OD,
        wire_diameter_mm=g.SPRING_WIRE,
        total_turns=25.3,
        endpoint_equivalence_required=True,
    )
    b.add_motion_track(
        "FULLFLOW-VALVE-CIRCLIP-001", "PARENT_RIGID",
        "DIN 471 circlip remains seated in the full-flow valve spool groove and inherits the valve hold position during the arm sweep.",
        parent_occurrence_id="FULLFLOW-VALVE-001",
    )
    for screw_index in range(1, 4):
        b.add_motion_track(
            f"WP04-MOVING-SLEEVE-SCREW-{screw_index}", "PARENT_RIGID",
            "Captive moving-sleeve screw remains rigid with the follower/sleeve flange during the later ejector stroke and is held during the arm sweep.",
            parent_occurrence_id="WP04-MOVING-SLEEVE",
        )

    later_phase_ids = {
        "FULLFLOW-VALVE-001",
        "ROUTE-BOWDEN-SHEATH-001", "ROUTE-BOWDEN-WIRE-001",
        "WP04-FOLLOWER-001", "WP04-EJECTOR-SPRING", "WP04-MOVING-SLEEVE",
        "WP04-SEAR-001", "WP04-SEAR-CLIP-001", "WP05-DOOR-001",
        "HARNESS-BAND-1", "HARNESS-BAND-2", "HARNESS-TERMINAL-001",
        "TETHER-THIMBLE-BODY", "TETHER-THIMBLE-HARNESS", "RECOVERY-TETHER-001",
        "RECOVERY-PIN-BODY", "RECOVERY-PIN-CLIP-BODY",
        "RECOVERY-PIN-HARNESS", "RECOVERY-PIN-CLIP-HARNESS",
        "WP05-DOOR-LANYARD",
    }
    later_phase_ids.update(f"BUOY-GORE-{index:02d}" for index in range(1, 9))
    later_phase_ids.update(f"HARNESS-LEG-{suffix}" for suffix in ("XP", "XN", "YP", "YN"))
    for occurrence_id in sorted(later_phase_ids):
        b.add_motion_track(
            occurrence_id, "HOLD_STOWED",
            "Retained in the exact stowed configuration during the 0..80 degree arm sweep; its independent later-phase deployed geometry is validated in the complete deployed master.",
            stationary_during_arm_sweep=True,
        )

    required = {
        occurrence.occurrence_id for occurrence in b.occurrences
        if occurrence.classification in {"MOVING", "FLEXIBLE", "SOFTGOOD"}
    }
    tracked = {row["occurrence_id"] for row in b.motion_tracks}
    if required != tracked:
        raise RuntimeError(
            f"Motion-track scope mismatch: missing={sorted(required - tracked)}, extra={sorted(tracked - required)}"
        )


def build_state(state: str) -> R2Builder:
    b = R2Builder(state)
    register_mandatory_hardware_part_definitions(b)
    build_forward(b)
    build_arm_module(b)
    build_aft(b)
    add_mandatory_hardware_occurrences(b)
    add_engineered_fit_register(b)
    add_primary_connections(b)
    add_motion_tracks(b)
    r2_final_scope.install_final_scope(b, hw)
    final_detail_naming.apply_final_names(b)
    r2_hierarchy.rebuild_named_hierarchy(b)
    b.root.add(b.forward, name=b.forward.name)
    b.root.add(b.arm_module, name=b.arm_module.name)
    b.root.add(b.aft, name=b.aft.name)
    return b


def serialize_builder(b: R2Builder) -> dict[str, Any]:
    return {
        "state": b.state,
        "assembly_hierarchy": b.assembly_hierarchy,
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
        "intentional_fits": b.intentional_fits,
        "attachment_requirements": b.attachment_requirements,
        "motion_tracks": b.motion_tracks,
        "definition_of_done_requirements": b.definition_of_done_requirements,
        "integral_joint_eliminations": b.integral_joint_eliminations,
        "mass_overrides_kg": dict(sorted(b.mass_overrides_kg.items())),
        "flexible_occurrence_ids": sorted(b.flexible_ids),
        "external_context_ids": sorted(b.external_ids),
        "kinematics": {
            "arm_angle_deg": g.DEPLOYED_ANGLE if b.deployed else 0.0,
            "crosshead_z_mm": g.kinematic(g.DEPLOYED_ANGLE if b.deployed else 0.0)["crosshead_z"],
            "crosshead_travel_full_precision_mm": g.CROSSHEAD_TRAVEL,
        },
    }


def main() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    builders: list[R2Builder] = []
    for state, filename in (("STOWED", STOWED_FILE), ("DEPLOYED", DEPLOYED_FILE)):
        print(f"Building corrected final {state} source assembly", flush=True)
        builder = build_state(state)
        out = RELEASE_DIR / filename
        export_ap242(builder.root, out)
        name_assembly_usage_occurrences(out)
        builders.append(builder)
        data = serialize_builder(builder)
        (ANALYSIS_DIR / f"authoring_inventory_{state.lower()}.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8", newline="\n",
        )
        print(f"Wrote {out} ({out.stat().st_size} bytes)", flush=True)

    final_detail_naming.write_name_maps(builders[0], ANALYSIS_DIR / "final_detail_cleanup")

    manifest = {
        "release_status": "AUTHORING_COMPLETE — RELEASE DISPOSITION CALCULATED BY INDEPENDENT NEUTRAL-CAD VALIDATOR",
        "creo_environment": "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; OWNER CREO IMPORT OCCURS AFTER DELIVERY.",
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
        "inventories": {},
    }
    for path in (RELEASE_DIR / STOWED_FILE, RELEASE_DIR / DEPLOYED_FILE):
        manifest["files"][path.name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }
    for state in ("STOWED", "DEPLOYED"):
        inventory_path = ANALYSIS_DIR / f"authoring_inventory_{state.lower()}.json"
        manifest["inventories"][inventory_path.name] = {
            "sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
            "size_bytes": inventory_path.stat().st_size,
        }
    (ANALYSIS_DIR / "authoring_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8", newline="\n",
    )
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
