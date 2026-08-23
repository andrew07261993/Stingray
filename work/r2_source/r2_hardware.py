#!/usr/bin/env python3
"""Exact-solid hardware catalog for the DF8 corrective final build.

This module is intentionally independent of ``build_r2.py``.  It defines the
67 occurrence IDs retained after the honest permanent-joint redesign: 64 are
helper-added and three return-spring occurrences remain source-owned.  It also
provides exact nominal drawing-derived B-rep shapes, positive-mass ``PartDef``
records, and a JSON-serializable integration schema.  All local part datums use
+Z as the fastener/pin insertion axis.  For screws, Z=0 is the underside of the
head and the shank extends in +Z unless the part description states otherwise.
"""

from __future__ import annotations

import math
from typing import Any

import cadquery as cq

import r2_geometry as g


OFFICIAL_RETRIEVAL_DATE = "2026-08-22"

OFFICIAL_PRODUCT_URLS: dict[str, str] = {
    "SSCF-M3-6-A4": "https://www.accu.co.uk/metric-cap-head-screws/3973-SSCF-M3-6-A4",
    "SSCF-M3-10-A4": "https://www.accu.co.uk/us/socket-cap-head-screws/3975-SSCF-M3-10-A4",
    "SSK-M3-6-A4-P80": "https://www.accu.co.uk/countersunk-socket-head-screws/795226-SSK-M3-6-A4-P80",
    "SSCA-M3-8-A4-BL": "https://www.accu.co.uk/cap-head-captive-screws/779966-SSCA-M3-8-A4-BL",
    "SSCL-M4-8-A4": "https://www.accu.co.uk/low-head-cap-screws/8885-SSCL-M4-8-A4",
    "HDP-3-8-A1": "https://www.accu.co.uk/dowel-pins/72653-HDP-3-8-A1",
    "HTP-3-30-A1": "https://www.accu.co.uk/taper-pins/389498-HTP-3-30-A1",
    "HEC-10-A4": "https://www.accu.co.uk/external-circlips/629101-HEC-10-A4",
}


MANIFOLD_CARRIER_SCREW_IDS = tuple(
    f"MANIFOLD-CARRIER-SCREW-{index}" for index in range(1, 5)
)
FWD_CARRIER_SCREW_IDS = tuple(
    f"FWD-CARRIER-SCREW-{index}" for index in range(1, 5)
)
BOOSTER_CLAMP_SCREW_IDS = tuple(
    f"BOOSTER-CLAMP-SCREW-{booster}-{band}"
    for booster in range(1, 4)
    for band in range(1, 4)
)
TRIGGER_MOUNT_SCREW_IDS = tuple(
    f"TRIGGER-MOUNT-SCREW-{index}" for index in range(1, 4)
)
BACKUP_GUIDE_SCREW_IDS = tuple(
    f"BACKUP-GUIDE-SCREW-{index}" for index in range(1, 3)
)
ARM_STOP_SCREW_IDS = tuple(
    f"ARM-STOP-SCREW-{arm}-{index}"
    for arm in range(1, 4)
    for index in range(1, 3)
)
FIXED_STOP_SCREW_IDS = tuple(
    f"FIXED-STOP-SCREW-{arm}-{index}"
    for arm in range(1, 4)
    for index in range(1, 3)
)
GUIDE_RAIL_SCREW_IDS = tuple(
    f"GUIDE-RAIL-{rail}-SCREW-{end}"
    for rail in range(1, 4)
    for end in ("FWD", "AFT")
)
FIXED_SLEEVE_SCREW_IDS = tuple(
    f"WP04-FIXED-SLEEVE-SCREW-{index}" for index in range(1, 4)
)
MOVING_SLEEVE_SCREW_IDS = tuple(
    f"WP04-MOVING-SLEEVE-SCREW-{index}" for index in range(1, 4)
)
LATCH_SCREW_IDS = tuple(
    f"WP04-LATCH-SCREW-{index}" for index in range(1, 3)
)
SERVICE_THROAT_SCREW_IDS = tuple(
    f"WP05-THROAT-SCREW-{index}" for index in range(1, 7)
)
CROSSHEAD_GUIDE_LOCK_SCREW_IDS = ("CROSSHEAD-GUIDE-LOCK-SCREW-001",)

SCREW_OCCURRENCE_IDS_BY_PART_NUMBER: dict[str, tuple[str, ...]] = {
    "SSCF-M3-6-A4": MANIFOLD_CARRIER_SCREW_IDS,
    "SSCF-M3-10-A4": (
        *BOOSTER_CLAMP_SCREW_IDS,
        *TRIGGER_MOUNT_SCREW_IDS,
        *BACKUP_GUIDE_SCREW_IDS,
    ),
    "SSK-M3-6-A4-P80": (*FWD_CARRIER_SCREW_IDS, *SERVICE_THROAT_SCREW_IDS),
    "SSCA-M3-8-A4-BL": (
        *ARM_STOP_SCREW_IDS,
        *FIXED_STOP_SCREW_IDS,
        *GUIDE_RAIL_SCREW_IDS,
        *FIXED_SLEEVE_SCREW_IDS,
        *MOVING_SLEEVE_SCREW_IDS,
        *LATCH_SCREW_IDS,
    ),
    "SSCL-M4-8-A4": CROSSHEAD_GUIDE_LOCK_SCREW_IDS,
}

FIXED_STOP_DOWEL_IDS = tuple(
    f"FIXED-STOP-DOWEL-{arm}-{index}"
    for arm in range(1, 4)
    for index in range(1, 3)
)
TAPER_PIN_IDS = ("NOSE-BALLAST-TAPER-PIN-001",)
CIRCLIP_IDS = ("FULLFLOW-VALVE-CIRCLIP-001",)
SERVICE_CAP_IDS = ("WATER-BOBBIN-SERVICE-CAP-001",)
STOW_DOG_RETURN_SPRING_IDS = tuple(
    f"STOW-DOG-SPRING-{index}" for index in range(1, 4)
)

OCCURRENCE_IDS_BY_PART_NUMBER: dict[str, tuple[str, ...]] = {
    **SCREW_OCCURRENCE_IDS_BY_PART_NUMBER,
    "HDP-3-8-A1": FIXED_STOP_DOWEL_IDS,
    "HTP-3-30-A1": TAPER_PIN_IDS,
    "HEC-10-A4": CIRCLIP_IDS,
    "DF8-WATER-BOBBIN-SERVICE-CAP-001": SERVICE_CAP_IDS,
    "DF8-R2-STOW-DOG-RETURN-SPRING-001": STOW_DOG_RETURN_SPRING_IDS,
}

REQUIRED_HARDWARE_OCCURRENCE_IDS = frozenset(
    occurrence_id
    for occurrence_ids in OCCURRENCE_IDS_BY_PART_NUMBER.values()
    for occurrence_id in occurrence_ids
)

EXPECTED_COUNTS = {
    "screws": 55,
    "dowels": 6,
    "taper_pins": 1,
    "circlips": 1,
    "service_caps": 1,
    "return_springs": 3,
    "total": 67,
}

# These exact spring occurrences are already authored in build_r2.py.  They
# remain in the 67-item mandatory installed-hardware register, but this helper
# must not add duplicate occurrences or a competing part definition.
SOURCE_OWNED_REQUIRED_HARDWARE_OCCURRENCE_IDS = frozenset(
    STOW_DOG_RETURN_SPRING_IDS
)
HELPER_ADDED_HARDWARE_OCCURRENCE_IDS = frozenset(
    REQUIRED_HARDWARE_OCCURRENCE_IDS
    - SOURCE_OWNED_REQUIRED_HARDWARE_OCCURRENCE_IDS
)
EXPECTED_HELPER_ADDED_COUNT = 64


def _single_valid(shape: cq.Shape, label: str) -> cq.Shape:
    solids = shape.Solids()
    if len(solids) != 1 or not shape.isValid() or shape.Volume() <= 0.0:
        raise ValueError(
            f"{label} must be one valid positive-volume solid; "
            f"solids={len(solids)}, valid={shape.isValid()}, volume={shape.Volume()}"
        )
    return solids[0]


def _hex_socket(across_flats: float, depth: float, z0: float) -> cq.Shape:
    circumradius = across_flats / math.sqrt(3.0)
    points = [
        (
            circumradius * math.cos(math.radians(60.0 * index + 30.0)),
            circumradius * math.sin(math.radians(60.0 * index + 30.0)),
        )
        for index in range(6)
    ]
    return (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(depth)
        .translate((0.0, 0.0, z0))
        .val()
    )


def make_socket_cap_screw(
    thread_diameter_mm: float,
    length_mm: float,
    head_diameter_mm: float,
    head_height_mm: float,
    socket_across_flats_mm: float,
    socket_depth_mm: float,
) -> cq.Shape:
    """Nominal full-thread socket-cap envelope with a real hex socket."""
    shank = g.cyl_z(thread_diameter_mm / 2.0, length_mm)
    head = g.cyl_z(head_diameter_mm / 2.0, head_height_mm, z0=-head_height_mm)
    socket = _hex_socket(
        socket_across_flats_mm,
        socket_depth_mm + 0.02,
        -head_height_mm - 0.01,
    )
    return _single_valid(shank.fuse(head).cut(socket), "socket-cap screw")


def make_captive_socket_cap_screw() -> cq.Shape:
    """Accu SSCA-M3-8-A4-BL nominal captive-shank envelope."""
    head = g.cyl_z(2.75, 3.0, z0=-3.0)
    captive_neck = g.cyl_z(1.10, 5.0)
    threaded_end = g.cyl_z(1.50, 3.0, z0=5.0)
    socket = _hex_socket(2.5, 1.32, -3.01)
    return _single_valid(
        head.fuse(captive_neck).fuse(threaded_end).cut(socket),
        "captive socket-cap screw",
    )


def make_countersunk_screw() -> cq.Shape:
    """Accu SSK-M3-6-A4-P80 nominal ISO 10642 envelope."""
    overall_length = 6.0
    head_height = 1.86
    head = cq.Solid.makeCone(
        3.36,
        1.50,
        head_height,
        cq.Vector(0.0, 0.0, -head_height),
        cq.Vector(0.0, 0.0, 1.0),
    )
    shank = g.cyl_z(1.50, overall_length - head_height)
    socket = _hex_socket(2.0, 1.12, -head_height - 0.01)
    return _single_valid(head.fuse(shank).cut(socket), "countersunk screw")


def make_low_head_screw() -> cq.Shape:
    """Accu SSCL-M4-8-A4 nominal DIN 7984 low-head envelope."""
    return make_socket_cap_screw(4.0, 8.0, 7.0, 2.8, 2.5, 2.3)


def make_dowel_pin() -> cq.Shape:
    """Accu HDP-3-8-A1 DIN 7 nominal m6 pin with 0.45 mm end radii."""
    radius = 1.50
    end = 0.45
    middle = g.cyl_z(radius, 8.0 - 2.0 * end, z0=end)
    forward = cq.Solid.makeCone(
        radius - end,
        radius,
        end,
        cq.Vector(0.0, 0.0, 0.0),
        cq.Vector(0.0, 0.0, 1.0),
    )
    aft = cq.Solid.makeCone(
        radius,
        radius - end,
        end,
        cq.Vector(0.0, 0.0, 8.0 - end),
        cq.Vector(0.0, 0.0, 1.0),
    )
    return _single_valid(forward.fuse(middle).fuse(aft), "dowel pin")


def make_taper_pin() -> cq.Shape:
    """Accu HTP-3-30-A1 DIN 1B nominal 3.0/3.6 x 30 mm pin."""
    return _single_valid(
        cq.Solid.makeCone(
            1.50,
            1.80,
            30.0,
            cq.Vector(0.0, 0.0, 0.0),
            cq.Vector(0.0, 0.0, 1.0),
        ),
        "taper pin",
    )


def make_external_circlip() -> cq.Shape:
    """Accu HEC-10-A4 DIN 471 nominal 10 mm external circlip."""
    ring = g.cyl_z(8.50, 1.0).cut(g.cyl_z(4.65, 1.2, z0=-0.1))
    ring = ring.cut(g.box_center(4.2, 2.8, 1.4, 7.2, 0.0, 0.5))
    for y in (-2.15, 2.15):
        lug = g.box_center(3.2, 2.2, 1.0, 5.9, y, 0.5)
        hole = g.cyl_z(0.75, 1.4, 6.15, y, -0.2)
        ring = ring.fuse(lug).cut(hole)
    return _single_valid(ring, "external circlip")


def make_service_cap() -> cq.Shape:
    """Controlled 316 stainless bayonet/thread service cap nominal envelope."""
    disk = g.cyl_z(6.80, 2.0, z0=-2.0)
    skirt = g.cyl_z(6.80, 6.0).cut(g.cyl_z(6.10, 6.4, z0=-0.2))
    for phi in (0.0, 120.0, 240.0):
        lug = g.box_center(1.0, 1.8, 1.2, 6.55, 0.0, 4.7).rotate(
            (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), phi
        )
        skirt = skirt.fuse(lug)
    # Integral axial keeper post reaches the bobbin's forward face through
    # the housing bore.  It is part of the removable cap, not an unretained
    # extra occurrence, and provides the second physical bridge endpoint.
    keeper_post = g.cyl_z(1.50, 20.0)
    return _single_valid(disk.fuse(skirt).fuse(keeper_post), "water-bobbin service cap")


def _buy_part(
    part_number: str,
    description: str,
    shape: cq.Shape,
    material: str,
    mass_kg: float,
    process: str,
    finish: str,
    notes: str,
) -> g.PartDef:
    if mass_kg <= 0.0:
        raise ValueError(f"BUY part {part_number} must have positive mass")
    url = OFFICIAL_PRODUCT_URLS[part_number]
    return g.PartDef(
        part_number=part_number,
        revision="ACCU-CATALOG",
        description=description,
        shape=_single_valid(shape, part_number),
        material=material,
        make_buy="BUY",
        manufacturer="Accu",
        cad_classification="DRAWING_DERIVED",
        mass_kg=mass_kg,
        source_url=url,
        purchase_url=url,
        process=process,
        finish=finish,
        notes=(
            f"Official Accu product identity and nominal dimensions verified "
            f"{OFFICIAL_RETRIEVAL_DATE}; {notes}"
        ),
        color_key="stainless",
    )


def make_part_definitions(state: str = "STOWED") -> dict[str, g.PartDef]:
    """Return the nine helper-owned hardware definitions for one endpoint state."""
    state_key = state.upper()
    if state_key not in {"STOWED", "DEPLOYED"}:
        raise ValueError("Hardware state must be STOWED or DEPLOYED")

    cap6 = make_socket_cap_screw(3.0, 6.0, 5.5, 3.0, 2.5, 1.3)
    cap10 = make_socket_cap_screw(3.0, 10.0, 5.5, 3.0, 2.5, 1.3)
    countersunk = make_countersunk_screw()
    captive = make_captive_socket_cap_screw()
    low_head = make_low_head_screw()
    dowel = make_dowel_pin()
    taper = make_taper_pin()
    circlip = make_external_circlip()
    service_cap = make_service_cap()
    parts = {
        "SSCF-M3-6-A4": _buy_part(
            "SSCF-M3-6-A4",
            "M3 X 6 FULL-THREAD SOCKET CAP SCREW, DIN 912 / ISO 4762",
            cap6,
            "A4-80 stainless steel",
            0.00071,
            "Accu catalog cold-formed/rolled-thread fastener; incoming CoC and dimensional inspection",
            "Natural A4 stainless; clean for submerged service",
            "Official mass 71 g per 100; M3 x 0.5, 5.5 mm head diameter, 3.0 mm head height.",
        ),
        "SSCF-M3-10-A4": _buy_part(
            "SSCF-M3-10-A4",
            "M3 X 10 FULL-THREAD SOCKET CAP SCREW, DIN 912 / ISO 4762",
            cap10,
            "A4-80 stainless steel",
            0.00088,
            "Accu catalog cold-formed/rolled-thread fastener; incoming CoC and dimensional inspection",
            "Natural A4 stainless; clean for submerged service",
            "Official mass 88 g per 100; M3 x 0.5, 5.5 mm head diameter, 3.0 mm head height.",
        ),
        "SSK-M3-6-A4-P80": _buy_part(
            "SSK-M3-6-A4-P80",
            "M3 X 6 SOCKET COUNTERSUNK SCREW, ISO 10642, PRECOTE 80",
            countersunk,
            "A4-80 stainless steel",
            0.00036,
            "Accu catalog ISO 10642 fastener with factory-applied precote 80; incoming CoC and dimensional inspection",
            "Natural A4 stainless with precote 80 thread locking",
            "Official mass 36 g per 100; 90 degree head, 6.72 mm nominal head diameter, 1.86 mm countersunk length.",
        ),
        "SSCA-M3-8-A4-BL": _buy_part(
            "SSCA-M3-8-A4-BL",
            "M3 X 8 CAPTIVE SOCKET CAP SCREW, DIN 912",
            captive,
            "A4-80 stainless steel",
            0.00080,
            "Accu catalog captive fastener; incoming CoC, captive-neck and dimensional inspection",
            "Matte-black A4 stainless; verify coating compatibility for submerged service",
            "Official mass 80 g per 100; 2.2 mm captive diameter x 5 mm captive length and 3 mm M3 threaded end.",
        ),
        "SSCL-M4-8-A4": _buy_part(
            "SSCL-M4-8-A4",
            "M4 X 8 FULL-THREAD LOW-HEAD SOCKET CAP SCREW, DIN 7984",
            low_head,
            "A4-80 stainless steel",
            0.00112,
            "Accu catalog DIN 7984 fastener; incoming CoC and dimensional inspection",
            "Natural A4 stainless; clean for submerged service",
            "Official mass 112 g per 100; M4 x 0.7, 7.0 mm head diameter, 2.8 mm head height.",
        ),
        "HDP-3-8-A1": _buy_part(
            "HDP-3-8-A1",
            "3 MM X 8 MM DOWEL PIN, DIN 7, M6 TOLERANCE",
            dowel,
            "316 stainless steel",
            0.00047,
            "Accu catalog DIN 7 precision pin; incoming CoC, diameter and straightness inspection",
            "Natural stainless; passivate after acceptance if required by drawing",
            "Official mass 47 g per 100; diameter tolerance +0.002/+0.008 mm and 0.45 mm radius length.",
        ),
        "HTP-3-30-A1": _buy_part(
            "HTP-3-30-A1",
            "3 MM X 30 MM TAPER PIN, DIN 1B",
            taper,
            "316 stainless steel",
            taper.Volume() * 7.90e-6,
            "Accu catalog DIN 1B taper pin; incoming CoC and blue-fit inspection in the occurrence-matched reamed bore",
            "Natural stainless; passivate after acceptance if required by drawing",
            "Nominal 3.0 mm small diameter, 3.6 mm large diameter and 30 mm length; mass from exact nominal B-rep at 7.90 g/cm3.",
        ),
        "HEC-10-A4": _buy_part(
            "HEC-10-A4",
            "10 MM EXTERNAL CIRCLIP, DIN 471",
            circlip,
            "1.4310 stainless spring steel",
            0.00041,
            "Accu catalog DIN 471 circlip; incoming CoC, free-gap and seating inspection",
            "Natural 1.4532 stainless spring material",
            "Official mass 41 g per 100; 1.0 mm thickness, 9.3 mm ID, 17 mm clearance diameter, 9.6 x 1.1 mm shaft groove.",
        ),
        "DF8-WATER-BOBBIN-SERVICE-CAP-001": g.PartDef(
            part_number="DF8-WATER-BOBBIN-SERVICE-CAP-001",
            revision="A",
            description="CAPTIVE WATER-BOBBIN THREADED/BAYONET SERVICE CAP",
            shape=service_cap,
            material="316 stainless steel",
            make_buy="MAKE",
            manufacturer="STINGRAY custom",
            cad_classification="DRAWING_DERIVED",
            mass_kg=service_cap.Volume() * 8.00e-6,
            process="Swiss turn; mill three bayonet lugs; passivate; occurrence-match to trigger housing",
            finish="ASTM A967 passivated; deburred and clean",
            notes="Controlled MAKE cap; requires integral opposite housing shoulder, positive lock and tool-access proof.",
            color_key="stainless",
        ),
    }
    for part_number, part in parts.items():
        if part.resolved_mass() is None or part.resolved_mass() <= 0.0:
            raise ValueError(f"Hardware part {part_number} lacks positive resolved mass")
    return parts


PLACEMENT_FAMILIES: tuple[dict[str, Any], ...] = (
    {
        "occurrence_ids": FWD_CARRIER_SCREW_IDS,
        "part_number": "SSK-M3-6-A4-P80",
        "mates": ("CARTRIDGE-CARRIER-FWD", "FWD-RING-01"),
        "axis": "AXIAL_Z; four inter-cartridge cardinal clocks",
        "prerequisites": "Add four carrier ears/ring lands, 90-degree countersinks and coaxial clearance/tapped holes; current 1 mm annular overlap is insufficient.",
    },
    {
        "occurrence_ids": MANIFOLD_CARRIER_SCREW_IDS,
        "part_number": "SSCF-M3-6-A4",
        "mates": ("CARTRIDGE-CARRIER-AFT", "COLLECTION-MANIFOLD-001"),
        "axis": "AXIAL_Z; four cardinal clocks between cartridge ports",
        "prerequisites": "Cut coaxial clearance/counterbores and tapped manifold lands; seat heads without positive-volume overlap.",
    },
    {
        "occurrence_ids": BOOSTER_CLAMP_SCREW_IDS,
        "part_number": "SSCF-M3-10-A4",
        "mates": ("BOOSTER-BAND-{booster}-{band}", "FWD-SHELL-001"),
        "axis": "BODY_RADIAL_OUTWARD at booster clocks 30/150/270 degrees and Z=454/650/858 mm",
        "prerequisites": "Re-cut each existing tangential band bore radially and add an internal shell boss; screw head remains inboard of the 52.6 mm OML.",
    },
    {
        "occurrence_ids": TRIGGER_MOUNT_SCREW_IDS,
        "part_number": "SSCF-M3-10-A4",
        "mates": ("WATER-TRIGGER-HSG-001", "FWD-SHELL-001"),
        "axis": "BODY_RADIAL_OUTWARD at housing-leg clocks 90/210/330 degrees near Z=508 mm",
        "prerequisites": "Retarget the false 63 mm carrier connection to the three housing legs and add internal shell bosses/clearance holes.",
    },
    {
        "occurrence_ids": ARM_STOP_SCREW_IDS,
        "part_number": "SSCA-M3-8-A4-BL",
        "mates": ("ARM-STOP-PAD-{arm}", "ARM-{arm}"),
        "axis": "ARM_LOCAL_NORMAL; two screws per arm",
        "prerequisites": "Machine the claimed dovetail, captive-neck counterbores and tapped arm lands before screw placement.",
    },
    {
        "occurrence_ids": (*FIXED_STOP_SCREW_IDS, *FIXED_STOP_DOWEL_IDS),
        "part_number": "SSCA-M3-8-A4-BL + HDP-3-8-A1",
        "mates": ("FIXED-STOP-{arm}", "PIVOT-CARRIER-{arm}"),
        "axis": "OCCURRENCE_STOP_LAND_NORMAL; two screws plus two dowels per arm",
        "prerequisites": "Complete the carrier tie-ear landing, then cut separate M3 captive holes and 3 mm H7 reamed dowel pairs with edge distance.",
    },
    {
        "occurrence_ids": BACKUP_GUIDE_SCREW_IDS,
        "part_number": "SSCF-M3-10-A4",
        "mates": ("BACKUP-SPRING-GUIDE", "FIXED-SECTOR-3"),
        "axis": "SUPPORT_TAB_NORMAL; one screw at each supported guide end",
        "prerequisites": "Complete both guide-support tabs, then add piloted clearance/tapped holes outside the moving spring envelope.",
    },
    {
        "occurrence_ids": CROSSHEAD_GUIDE_LOCK_SCREW_IDS,
        "part_number": "SSCL-M4-8-A4",
        "mates": ("CROSSHEAD-GUIDE-001", "CROSSHEAD-GUIDE-SPIDER-001"),
        "axis": "AXIAL_Z through guide shoulder/spider hub",
        "prerequisites": "The mounting spider must be one valid connected solid; add an M4 shoulder/tapped feature and low-head tool-access envelope.",
    },
    {
        "occurrence_ids": GUIDE_RAIL_SCREW_IDS,
        "part_number": "SSCA-M3-8-A4-BL",
        "mates": ("WP04-GUIDE-RAIL-{rail}", "WP04-REACTION-BULKHEAD / WP04-AFT-RAIL-SUPPORT"),
        "axis": "AXIAL_Z; FWD and AFT end per rail",
        "prerequisites": "Add an exact aft rail-support ring/bracket, then captive-neck counterbores and three forward/three aft tapped bosses.",
    },
    {
        "occurrence_ids": FIXED_SLEEVE_SCREW_IDS,
        "part_number": "SSCA-M3-8-A4-BL",
        "mates": ("WP04-FIXED-SLEEVE", "WP04-REACTION-BULKHEAD"),
        "axis": "AXIAL_Z; three equally clocked screws outside the spring ID",
        "prerequisites": "Complete the fixed-sleeve pilot/flange and add three captive holes clear of the spring wire and route passages.",
    },
    {
        "occurrence_ids": MOVING_SLEEVE_SCREW_IDS,
        "part_number": "SSCA-M3-8-A4-BL",
        "mates": ("WP04-MOVING-SLEEVE", "WP04-FOLLOWER-001"),
        "axis": "AXIAL_Z; three equally clocked screws",
        "prerequisites": "Complete the follower-facing sleeve flange, then add three captive holes outside the spring and guide-rail swept envelopes.",
    },
    {
        "occurrence_ids": LATCH_SCREW_IDS,
        "part_number": "SSCA-M3-8-A4-BL",
        "mates": ("WP04-LATCH-001", "WP04-GUIDE-RAIL-3 / LATCH-SUPPORT-BRACKET"),
        "axis": "LATCH_BRACKET_NORMAL; two screws",
        "prerequisites": "Complete the latch bracket landing, then add a piloted two-hole pattern clear of the sear and Bowden/pilot ports.",
    },
    {
        "occurrence_ids": SERVICE_THROAT_SCREW_IDS,
        "part_number": "SSK-M3-6-A4-P80",
        "mates": ("WP05-SERVICE-THROAT", "AFT-SHELL-001"),
        "axis": "AXIAL_Z; six clocked flush screws on an inward flange",
        "prerequisites": "Add an inward service flange and 90-degree countersinks clocked clear of hinge, four detents, latch window and lanyard.",
    },
    {
        "occurrence_ids": TAPER_PIN_IDS,
        "part_number": "HTP-3-30-A1",
        "mates": ("NOSE-001", "BALLAST-001"),
        "axis": "TRANSVERSE_BODY_X_OR_Y through the seated shrink-fit joint",
        "prerequisites": "Cut one occurrence-matched 3.0/3.6 x 30 mm tapered bore and prove insertion/removal tool access.",
    },
    {
        "occurrence_ids": CIRCLIP_IDS,
        "part_number": "HEC-10-A4",
        "mates": ("FULLFLOW-VALVE-001", "FWD-RING-02"),
        "axis": "VALVE_SPOOL_AXIS",
        "prerequisites": "Add the official 9.6 mm groove diameter x 1.1 mm width and a reacting axial shoulder with 17 mm plier clearance.",
    },
    {
        "occurrence_ids": SERVICE_CAP_IDS,
        "part_number": "DF8-WATER-BOBBIN-SERVICE-CAP-001",
        "mates": ("WATER-BOBBIN-001", "WATER-TRIGGER-HSG-001"),
        "axis": "TRIGGER_HOUSING_AXIS_Z",
        "prerequisites": "Add an integral opposite bobbin shoulder and occurrence-matched thread/bayonet lands plus lock and reset-tool access.",
    },
    {
        "occurrence_ids": STOW_DOG_RETURN_SPRING_IDS,
        "part_number": "DF8-R2-STOW-DOG-RETURN-SPRING-001",
        "mates": ("STOW-DOG-{arm}", "STOW-DOG-GUIDE-{arm}"),
        "axis": "BODY_RADIAL at arm clocks 0/120/240 degrees",
        "prerequisites": "SOURCE-OWNED AND ALREADY INSTALLED: retain the existing exact STOW-DOG-SPRING-1..3 occurrences and their integral end shoulders; do not add duplicates.",
    },
)


def occurrence_part_number(occurrence_id: str) -> str:
    for part_number, occurrence_ids in OCCURRENCE_IDS_BY_PART_NUMBER.items():
        if occurrence_id in occurrence_ids:
            return part_number
    raise KeyError(f"Unknown required hardware occurrence: {occurrence_id}")


INHIBIT_PIN_KEEPER_REQUIREMENTS: tuple[dict[str, Any], ...] = tuple(
    {
        "pin_occurrence_id": f"STOW-DOG-INHIBIT-PIN-{arm}",
        "guide_occurrence_id": f"STOW-DOG-GUIDE-{arm}",
        "dog_occurrence_id": f"STOW-DOG-{arm}",
        "keeper_strategy": "EXTERNAL_CRESCENT_KEEPER_IN_PIN_GROOVE",
        "keeper_occurrence_ids": [f"STOW-DOG-INHIBIT-KEEPER-{arm}"],
        "additional_discrete_keeper_required": True,
        "required_redesign": (
            "Use the source-owned occurrence-specific crescent keeper seated "
            "in the inhibit-pin external groove. The keeper translates with "
            "the headed pin; STOWED crosses the dog bore and DEPLOYED remains "
            "captured in the guide-side parking interface."
        ),
    }
    for arm in range(1, 4)
)

# Compatibility name retained for integrators that consumed the earlier
# working helper.  The keeper contract above is controlling.
INHIBIT_PIN_CAPTIVE_SLIDER_REQUIREMENTS = INHIBIT_PIN_KEEPER_REQUIREMENTS


def retained_pin_requirements(state: str = "STOWED") -> list[dict[str, Any]]:
    """Return occurrence-specific rows covering every known PIN/DOWEL candidate.

    The source inventory owns the pivot, link, actuator, recovery, hinge and
    transport-inhibit pins.  This helper adds the nose taper pin and six fixed-
    stop dowels.  The transport pin rows deliberately depend on the captive-
    physical keeper occurrences above; no unmodeled keeper or tether is assumed.
    """
    state_key = state.upper()
    if state_key not in {"STOWED", "DEPLOYED"}:
        raise ValueError("Retained-pin state must be STOWED or DEPLOYED")

    rows: list[dict[str, Any]] = []

    def add(
        pin: str,
        retention: list[str],
        support: list[str],
        basis: str,
        maximum_gap_mm: float = 0.30,
    ) -> None:
        rows.append({
            "pin_occurrence_id": pin,
            "retention_occurrence_ids": retention,
            "support_occurrence_ids": support,
            "maximum_engagement_gap_mm": maximum_gap_mm,
            "retention_basis": basis,
        })

    add(
        TAPER_PIN_IDS[0], ["NOSE-001"], ["BALLAST-001"],
        "Occurrence-matched DIN 1B taper and seated transverse bore retain the shrink-fit nose joint.",
        0.05,
    )
    for arm in range(1, 4):
        for index in range(1, 3):
            add(
                f"FIXED-STOP-DOWEL-{arm}-{index}",
                [f"FIXED-STOP-{arm}"],
                [f"PIVOT-CARRIER-{arm}"],
                "DIN 7 m6 dowel in occurrence-matched H7 reamed bores; the two captive screws provide axial clamp retention.",
                0.05,
            )
        add(
            f"PIVOT-PIN-{arm}", [f"PIVOT-CLIP-{arm}"], [f"PIVOT-CARRIER-{arm}"],
            "Headed shoulder pin retained by the modeled occurrence-specific external spiral ring.",
        )
        for end in ("BELL", "CROSSHEAD"):
            support = f"ARM-{arm}" if end == "BELL" else "CROSSHEAD-001"
            add(
                f"LINK-PIN-{arm}-{end}", [f"LINK-CLIP-{arm}-{end}"], [support],
                "Full-span headed link pin retained by the modeled occurrence-specific crescent ring.",
            )
        inhibit_support = (
            [f"STOW-DOG-{arm}"] if state_key == "STOWED"
            else [f"STOW-DOG-GUIDE-{arm}"]
        )
        add(
            f"STOW-DOG-INHIBIT-PIN-{arm}",
            [f"STOW-DOG-INHIBIT-KEEPER-{arm}"],
            inhibit_support,
            "Occurrence-specific crescent keeper seats in the pin groove; STOWED engages the dog bore and DEPLOYED parks in the guide-side interface.",
        )

    for label in ("GS19", "HBD"):
        add(
            f"{label}-PIN-FIXED", [f"{label}-CLIP-FIXED"], [f"{label}-FIXED-YOKE"],
            "Headed actuator pin retained by the modeled occurrence-specific external ring.",
        )
        add(
            f"{label}-PIN-MOVING", [f"{label}-CLIP-MOVING"], ["CROSSHEAD-001"],
            "Headed actuator pin retained by the modeled occurrence-specific external ring.",
        )

    for end, support in (
        ("BODY", "BODY-HARDPOINT-001"),
        ("HARNESS", "HARNESS-TERMINAL-001"),
    ):
        add(
            f"RECOVERY-PIN-{end}", [f"RECOVERY-PIN-CLIP-{end}"], [support],
            "Headed recovery-terminal pin retained by the modeled occurrence-specific external ring.",
        )
    add(
        "WP04-SEAR-001", ["WP04-SEAR-CLIP-001"], ["WP04-LATCH-001"],
        "Sear pin retained by the modeled occurrence-specific external clip in the latch support.",
    )
    add(
        "WP05-HINGE-PIN", ["WP05-HINGE-CLIP"], ["WP05-DOOR-001"],
        "Headed hinge pin retained by the modeled occurrence-specific crescent ring.",
    )
    return rows


def definition_of_done_scope(
    installed_occurrence_ids: list[str] | tuple[str, ...] | set[str],
    state: str = "STOWED",
    pin_candidate_ids: list[str] | tuple[str, ...] | set[str] | None = None,
) -> dict[str, Any]:
    """Build validator-ready installed scope and fail closed on missing pins.

    ``validate_r2.py`` intentionally treats ``required_hardware_occurrence_ids``
    as the complete installed-item scope, not merely the 67 hardware entries.
    Call this only after the final occurrences have been added.  If the clean
    inventory-derived PIN/DOWEL candidate list is available, pass it so any new
    unregistered candidate causes an immediate error before export.
    """
    installed = {str(value).strip() for value in installed_occurrence_ids if str(value).strip()}
    missing_hardware = sorted(REQUIRED_HARDWARE_OCCURRENCE_IDS - installed)
    if missing_hardware:
        raise ValueError(
            "Final installed scope is missing mandatory hardware occurrences: "
            f"{missing_hardware}"
        )
    pin_rows = retained_pin_requirements(state)
    declared_pins = {row["pin_occurrence_id"] for row in pin_rows}
    if pin_candidate_ids is not None:
        candidates = {str(value).strip() for value in pin_candidate_ids if str(value).strip()}
        missing_pins = sorted(candidates - declared_pins)
        if missing_pins:
            raise ValueError(
                "PIN/DOWEL candidates lack retained-pin rows: "
                f"{missing_pins}"
            )
    return {
        "required_hardware_occurrence_ids": sorted(installed),
        "retained_pin_requirements": pin_rows,
    }


def hardware_schema(state: str = "STOWED") -> dict[str, Any]:
    """Return the fail-closed, JSON-serializable 67-occurrence integration schema."""
    parts = make_part_definitions(state)
    occurrence_to_part = {
        occurrence_id: part_number
        for part_number, occurrence_ids in OCCURRENCE_IDS_BY_PART_NUMBER.items()
        for occurrence_id in occurrence_ids
    }
    return {
        "schema": "DF8_R2_HARDWARE_67_V1",
        "state": state.upper(),
        "expected_counts": dict(EXPECTED_COUNTS),
        "official_retrieval_date": OFFICIAL_RETRIEVAL_DATE,
        "official_product_urls": dict(OFFICIAL_PRODUCT_URLS),
        "mandatory_hardware_occurrence_ids": sorted(REQUIRED_HARDWARE_OCCURRENCE_IDS),
        "helper_added_hardware_occurrence_ids": sorted(HELPER_ADDED_HARDWARE_OCCURRENCE_IDS),
        "source_owned_required_hardware_occurrence_ids": sorted(
            SOURCE_OWNED_REQUIRED_HARDWARE_OCCURRENCE_IDS
        ),
        "occurrence_to_part_number": dict(sorted(occurrence_to_part.items())),
        "part_resolved_mass_kg": {
            part_number: part.resolved_mass() for part_number, part in sorted(parts.items())
        },
        "placement_families": [
            {
                **row,
                "occurrence_ids": list(row["occurrence_ids"]),
                "mates": list(row["mates"]),
            }
            for row in PLACEMENT_FAMILIES
        ],
        "retained_pin_requirements": retained_pin_requirements(state),
        "inhibit_pin_captive_slider_requirements": [
            dict(row) for row in INHIBIT_PIN_CAPTIVE_SLIDER_REQUIREMENTS
        ],
        "inhibit_pin_keeper_requirements": [
            dict(row) for row in INHIBIT_PIN_KEEPER_REQUIREMENTS
        ],
        "validator_scope_instruction": (
            "After all occurrences are installed, call definition_of_done_scope() "
            "so required_hardware_occurrence_ids covers the complete final "
            "installed scope and retained_pin_requirements covers every clean-"
            "inventory PIN/DOWEL candidate."
        ),
    }


def validate_contract() -> None:
    screw_ids = {
        occurrence_id
        for occurrence_ids in SCREW_OCCURRENCE_IDS_BY_PART_NUMBER.values()
        for occurrence_id in occurrence_ids
    }
    actual = {
        "screws": len(screw_ids),
        "dowels": len(FIXED_STOP_DOWEL_IDS),
        "taper_pins": len(TAPER_PIN_IDS),
        "circlips": len(CIRCLIP_IDS),
        "service_caps": len(SERVICE_CAP_IDS),
        "return_springs": len(STOW_DOG_RETURN_SPRING_IDS),
        "total": len(REQUIRED_HARDWARE_OCCURRENCE_IDS),
    }
    if actual != EXPECTED_COUNTS:
        raise RuntimeError(f"Hardware occurrence contract mismatch: {actual} != {EXPECTED_COUNTS}")
    flattened = [
        occurrence_id
        for occurrence_ids in OCCURRENCE_IDS_BY_PART_NUMBER.values()
        for occurrence_id in occurrence_ids
    ]
    if len(flattened) != len(set(flattened)):
        raise RuntimeError("Hardware occurrence IDs are not unique")
    if len(HELPER_ADDED_HARDWARE_OCCURRENCE_IDS) != EXPECTED_HELPER_ADDED_COUNT:
        raise RuntimeError(
            "Helper-added hardware count mismatch: "
            f"{len(HELPER_ADDED_HARDWARE_OCCURRENCE_IDS)} != "
            f"{EXPECTED_HELPER_ADDED_COUNT}"
        )
    inhibit_pin_ids = {
        row["pin_occurrence_id"] for row in INHIBIT_PIN_KEEPER_REQUIREMENTS
    }
    expected_inhibit_pin_ids = {
        f"STOW-DOG-INHIBIT-PIN-{arm}" for arm in range(1, 4)
    }
    if inhibit_pin_ids != expected_inhibit_pin_ids:
        raise RuntimeError(
            "Transport-inhibit keeper contract mismatch: "
            f"{sorted(inhibit_pin_ids)} != {sorted(expected_inhibit_pin_ids)}"
        )


validate_contract()
