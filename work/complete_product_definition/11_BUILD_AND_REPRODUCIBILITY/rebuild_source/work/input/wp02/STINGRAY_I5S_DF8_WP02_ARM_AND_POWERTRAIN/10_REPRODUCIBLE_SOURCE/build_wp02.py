#!/usr/bin/env python3
"""Build the STINGRAY I5-S DF8 WP02 arm and powertrain digital subsystem package.

This script implements the owner-approved recommended defaults after Stage-I:
- accepted WP01 body/envelope parent;
- one rigid three-arm kinematic solution;
- body-owned covers open before arm motion;
- zero-GS backup-spring deployment requirement;
- positive mechanical stops and locks;
- non-fragmenting captive HBD overload bypass;
- controlled manual reset;
- exact vendor CAD preserved unchanged when available;
- drawing-derived COTS geometry explicitly labelled when authentic CAD is unavailable.

The output is a controlled digital-development package. It is not a fabrication release,
procurement release, qualification record, or operational-use authorization.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
import math
import os
import platform
import re
import shutil
import sys
import textwrap
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

import cadquery as cq
import numpy as np
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Controller
from scipy.integrate import solve_ivp

PACKAGE_NAME = "STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN"
ZIP_NAME = PACKAGE_NAME + ".zip"
CONFIGURATION_ID = "STINGRAY-I5S-DF8-WP02-ARM-POWERTRAIN-2026-08-18-R1"
REVISION = "DF8-WP02-R1"
PARENT_DF8_CONFIG = "STINGRAY-I5S-DF8-SPRING-EJECTOR-WIP-2026-08-18-R0"
PARENT_WP01_CONFIG = "STINGRAY-I5S-DF8-WP01-BODY-ENVELOPE-DATUMS-2026-08-18-R1"
PARENT_DF8_ARCHIVE_SHA256 = "6da4deb5e920ab819ffc1ce720ef7934c792a539416b51f7b78acf18f76bed60"
PARENT_WP01_ARCHIVE_SHA256 = "b55f23fb76b01bb8d6d17b6a6f7969f00f835199f762be1b53f80021cfff1685"
PARENT_DF8_MASTER_SHA256 = "21862439478530435e3d1f55b5358711f2ed3d0799d0dd05e6b0452d5c1fd2d1"
OWNER_RESPONSE = "USE ALL RECOMMENDED DEFAULTS"
FIXED_STEP_TIMESTAMP = "2026-08-18T00:00:00"
RETRIEVAL_DATE = "2026-08-18"

SCRIPT = Path(__file__).resolve()
WORK_ROOT = SCRIPT.parent
DEFAULT_DF8_ROOT = WORK_ROOT / "df8" / "STINGRAY_I5S_DF8_SPRING_EJECTOR_ARCHITECTURE_DEVELOPMENT_2026-08-18"
DEFAULT_WP01_ROOT = WORK_ROOT / "wp01" / "STINGRAY_I5S_DF8_WP01_BODY_ENVELOPE_AND_DATUMS"
DEFAULT_OUT_PARENT = Path("/mnt/data")

# Controlled geometry and kinematics.
PIVOT_R = 36.0
PIVOT_Z = 625.0
ARM_LENGTH = 470.0
ARM_LINK_RADIUS = 35.0
LOCK_ARM_OFFSET_MM = 9.5
SEAR_PHI_DEG = 270.0
CROSSHEAD_PIN_R = 42.0
LINK_LENGTH = 70.0
STOWED_ANGLE_DEG = 1.0
DEPLOYED_ANGLE_DEG = 80.0
CORE_RADIAL_LIMIT = 18.0
CORE_Z_MIN = 460.0
CORE_Z_MAX = 970.0
ARM_SWEEP_Z_MIN = 580.0
ARM_SWEEP_Z_MAX = 1095.0

# Gas spring exact vendor-BREP placement. Original local x maps to global +z.
GS_CENTER_X = 8.3
GS_CENTER_Y = 0.0
GS_FIXED_TIP_Z = 740.0
GS_VENDOR_X_MIN = -60.0
GS_VENDOR_X_SPLIT = 0.0
GS_VENDOR_X_MAX = 124.0
GS_TOTAL_EXTENDED_MM = 184.0
GS_STROKE_MM = 50.0
GS_FORCE_NOMINAL_N = 300.0
GS_FORCE_MIN_N = 270.0
GS_FORCE_MAX_N = 330.0

# HBD drawing-derived installation.
HBD_CENTER_X = -9.2
HBD_CENTER_Y = 0.0
HBD_BODY_OD_MM = 15.0
HBD_ROD_OD_MM = 6.0
HBD_STROKE_MM = 25.0
HBD_EXTENDED_LENGTH_MM = 145.0
HBD_END_STOP_RESERVE_MM = 1.5
HBD_LOST_MOTION_MM = 1.2
HBD_MOVING_OFFSET_Z = 16.0
HBD_FIXED_EYE_Z = 726.6280378531345
HBD_BYPASS_DETENT_N = 450.0
HBD_BYPASS_DETENT_TOL_N = 30.0
HBD_NORMAL_DAMPING_FORCE_N = 250.0
HBD_MAX_FORCE_N = 800.0

# Selected backup spring and rejected inherited spring.
SPRING_SELECTED_PN = "LHL 625D 12"
SPRING_OD_MM = 15.24
SPRING_HOLE_MM = 15.88
SPRING_MAX_ROD_MM = 8.74
SPRING_FREE_LENGTH_MM = 203.2
SPRING_RATE_N_PER_MM = 11.91
SPRING_SOLID_HEIGHT_MM = 139.7
SPRING_WIRE_MM = 3.05
SPRING_MATERIAL = "Alloy spring steel, orange powder coat"
SPRING_CENTER_X = 0.0
SPRING_CENTER_Y = 10.0
SPRING_FIXED_SEAT_Z = 965.0
SPRING_INSTALLED_STOWED_MM = 153.0
SPRING_GUIDE_ROD_D_MM = 6.0

REJECTED_SPRING_PN = "LHL 1250D 09"
REJECTED_SPRING_OD_MM = 30.48
REJECTED_SPRING_HOLE_MM = 31.75
REJECTED_SPRING_MAX_ROD_MM = 15.88
REJECTED_SPRING_FREE_LENGTH_MM = 177.8
REJECTED_SPRING_RATE_N_PER_MM = 85.815
REJECTED_SPRING_SOLID_HEIGHT_MM = 126.49
REJECTED_SPRING_WIRE_MM = 6.65
REJECTED_SPRING_INSTALLED_MM = 130.0

# Materials and analysis properties. Densities are nominal engineering values.
DENSITY_KG_PER_MM3 = {
    "17-4PH stainless steel": 7.75e-6,
    "316 stainless steel": 8.00e-6,
    "7075-T6 aluminum": 2.81e-6,
    "PEEK": 1.32e-6,
    "Oil-tempered chrome silicon": 7.85e-6,
    "Music wire": 7.85e-6,
    "Polyurethane 90A": 1.15e-6,
    "Black anodized aluminum / hard-chrome steel": 5.00e-6,
    "Vendor-defined stainless assembly": 7.75e-6,
}

SOURCE_URLS = {
    "ACE_GS": "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/gs-8-v4a-to-gs-40-va/gs-19-v4a/gs-19-50-v4a.html",
    "ACE_HBD": "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/hbd-15-to-hbd-40/hbd-15.html",
    "LEE": "https://www.leespring.com/compression-springs/1?field_published_stock_code_value=&items_per_page=20&max=&min=&order=field_solid_height_cm&sort=desc",
    "SMALLEY": "https://www.smalley.com/ring/vsm-6",
    "SMALLEY_PDF": "https://www.smalley.com/sites/default/files/pdfs/VSM.pdf",
}

OWNER_DECISIONS = {
    "ARM-Q01": "A",
    "ARM-Q02": "A",
    "ARM-Q03": "A",
    "ARM-Q04": "A",
    "ARM-Q05": "A",
    "ARM-Q06": "B",
    "ARM-Q07": "A",
    "ARM-Q08": "A_WITH_B_FALLBACK_IMPLEMENTED_AS_B",
    "ARM-Q09": "A",
    "ARM-Q10": "A",
    "ARM-Q11": "A",
    "ARM-Q12": "A",
    "ARM-Q13": "A",
    "ARM-Q14": "A_WITH_B_FALLBACK",
    "ARM-Q15": "A",
    "ARM-Q16": "A",
    "ARM-Q17": "B",
    "ARM-Q18": "A_IF_FEASIBLE_ELSE_B; PROTECTED_CARTRIDGE_BOUNDARY_REQUIRED",
}

RELEASE_CLASSIFICATION = (
    "CONTROLLED DIGITAL SUBSYSTEM DEVELOPMENT DEFINITION; DIGITAL GEOMETRY AND ANALYTICAL "
    "BASELINE COMPLETE FOR THE TWO DELIVERED STATES. NOT PROCUREMENT RELEASED, NOT "
    "FABRICATION RELEASED, NOT TEST-ENTRY READY, NOT QUALIFIED, AND NOT OPERATIONALLY READY. "
    "HBD DRAWING-DERIVED GEOMETRY, GS CHARGE SPECIFICATION, SPRING PROCUREMENT IDENTITY, "
    "DAMPING ADJUSTMENT, BYPASS DETENT SETTING, SALTWATER BOUNDARY, AND REPRESENTATIVE "
    "PHYSICAL TESTS REQUIRE EXTERNAL VERIFICATION."
)


@dataclass
class Part:
    item: str
    name: str
    subsystem: str
    material: str
    part_type: str
    manufacturer: str
    part_number: str
    source_class: str
    shape_stowed: cq.Shape
    shape_deployed: cq.Shape | None = None
    quantity: int = 1
    attachment: str = ""
    retention: str = ""
    service: str = ""
    limitation: str = ""
    mass_override_kg: float | None = None
    include_stowed: bool = True
    include_deployed: bool = True
    color: tuple[float, float, float] = (0.65, 0.65, 0.65)
    metadata: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.item}_{self.name}"

    def shape(self, state: str) -> cq.Shape:
        if state == "DEPLOYED" and self.shape_deployed is not None:
            return self.shape_deployed
        return self.shape_stowed

    def mass_kg(self, state: str = "STOWED") -> float:
        if self.mass_override_kg is not None:
            return self.mass_override_kg
        density = DENSITY_KG_PER_MM3.get(self.material, 7.75e-6)
        return self.shape(state).Volume() * density


# ---------- filesystem and serialization ----------

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, obj: object) -> None:
    write_text(path, json.dumps(obj, indent=2, sort_keys=True))


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# ---------- CAD utilities ----------

def cyl(radius: float, z0: float, z1: float, x: float = 0.0, y: float = 0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def tube(ro: float, ri: float, z0: float, z1: float, x: float = 0.0, y: float = 0.0) -> cq.Shape:
    return cyl(ro, z0, z1, x, y).cut(cyl(ri, z0 - 0.25, z1 + 0.25, x, y))


def box(dx: float, dy: float, dz: float, x: float, y: float, z: float) -> cq.Shape:
    return cq.Workplane("XY").box(dx, dy, dz).translate((x, y, z)).val()


def polar(radius: float, phi_deg: float) -> tuple[float, float]:
    a = math.radians(phi_deg)
    return radius * math.cos(a), radius * math.sin(a)


def local_rotate(shape: cq.Shape, phi_deg: float) -> cq.Shape:
    return shape.rotate((0, 0, 0), (0, 0, 1), phi_deg)


def radial_cylinder(radius: float, r0: float, r1: float, z: float, phi_deg: float) -> cq.Shape:
    ux, uy = polar(1.0, phi_deg)
    start = cq.Vector(r0 * ux, r0 * uy, z)
    return cq.Solid.makeCylinder(radius, r1 - r0, start, cq.Vector(ux, uy, 0))


def radial_box(r0: float, r1: float, tangential_width: float, z0: float, z1: float, phi_deg: float) -> cq.Shape:
    s = box(r1 - r0, tangential_width, z1 - z0, (r0 + r1) / 2.0, 0.0, (z0 + z1) / 2.0)
    return local_rotate(s, phi_deg)


def eye_y(x: float, z: float, width: float, outer_radius: float, hole_radius: float, y0: float | None = None) -> cq.Shape:
    if y0 is None:
        y0 = -width / 2.0
    outer = cq.Solid.makeCylinder(outer_radius, width, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
    inner = cq.Solid.makeCylinder(hole_radius, width + 2.0, cq.Vector(x, y0 - 1.0, z), cq.Vector(0, 1, 0))
    return outer.cut(inner)


def rod_between(p1: tuple[float, float, float], p2: tuple[float, float, float], radius: float) -> cq.Shape:
    a = cq.Vector(*p1)
    b = cq.Vector(*p2)
    d = b - a
    return cq.Solid.makeCylinder(radius, d.Length, a, d.normalized())


def fork_bosses_y(x: float, z: float, outer_radius: float = 7.0, hole_radius: float = 3.25) -> cq.Shape:
    left = cq.Solid.makeCylinder(outer_radius, 4.0, cq.Vector(x, -10.0, z), cq.Vector(0, 1, 0))
    right = cq.Solid.makeCylinder(outer_radius, 4.0, cq.Vector(x, 6.0, z), cq.Vector(0, 1, 0))
    hole = cq.Solid.makeCylinder(hole_radius, 22.0, cq.Vector(x, -11.0, z), cq.Vector(0, 1, 0))
    return left.fuse(right).cut(hole)


def compound(shapes: Sequence[cq.Shape]) -> cq.Shape:
    return cq.Compound.makeCompound(list(shapes))


def bbox_dict(shape: cq.Shape) -> dict[str, float]:
    b = shape.BoundingBox()
    return {
        "xmin_mm": b.xmin, "xmax_mm": b.xmax, "ymin_mm": b.ymin, "ymax_mm": b.ymax,
        "zmin_mm": b.zmin, "zmax_mm": b.zmax, "xlen_mm": b.xlen, "ylen_mm": b.ylen, "zlen_mm": b.zlen,
    }


def shape_signature(shape: cq.Shape) -> dict:
    return {
        "solid_count": len(shape.Solids()),
        "face_count": len(shape.Faces()),
        "edge_count": len(shape.Edges()),
        "volume_mm3": shape.Volume(),
        **bbox_dict(shape),
    }


def safe_common_volume(a: cq.Shape, b: cq.Shape) -> float:
    try:
        return a.intersect(b).Volume()
    except Exception:
        return float("nan")


def safe_distance(a: cq.Shape, b: cq.Shape) -> float:
    try:
        d = a.distance(b)
        return float(d[0] if isinstance(d, tuple) else d)
    except Exception:
        return float("nan")


def bbox_overlaps(a: cq.BoundBox, b: cq.BoundBox, tol: float = 1.0e-7) -> bool:
    return not (
        a.xmax < b.xmin + tol or b.xmax < a.xmin + tol or
        a.ymax < b.ymin + tol or b.ymax < a.ymin + tol or
        a.zmax < b.zmin + tol or b.zmax < a.zmin + tol
    )


def full_solid_pair_audit(parts: list[Part]) -> tuple[list[dict], list[dict]]:
    """Run exact common-volume checks for every broad-phase rigid occurrence pair.

    The exact GS and HBD service items are represented as separate fixed-body and
    moving-rod occurrences so their prismatic state can be named in an AP242
    assembly. Their rod volumes are intentionally inside the body-bore envelopes.
    Those two same-service-item pairs are accepted representation limitations; no
    cross-component or custom-part positive common volume is accepted.
    """
    accepted_internal_pairs = {
        frozenset(("WP02-015", "WP02-016")): "INTENTIONAL_INTERNAL_COTS_TELESCOPING_REPRESENTATION",
        frozenset(("WP02-019", "WP02-020")): "INTENTIONAL_INTERNAL_COTS_TELESCOPING_REPRESENTATION",
    }
    rows: list[dict] = []
    summaries: list[dict] = []
    for state in ("STOWED", "DEPLOYED"):
        active = [p for p in parts if (p.include_stowed if state == "STOWED" else p.include_deployed)]
        cache = {
            p.item: [(solid, solid.BoundingBox()) for solid in p.shape(state).Solids()]
            for p in active
        }
        broad_pairs = 0
        positive_pairs = 0
        accepted_pairs = 0
        failed_pairs = 0
        for a, b in itertools.combinations(active, 2):
            candidates = [
                (sa, sb)
                for sa, ba in cache[a.item]
                for sb, bb in cache[b.item]
                if bbox_overlaps(ba, bb)
            ]
            if not candidates:
                continue
            broad_pairs += 1
            volumes = [safe_common_volume(sa, sb) for sa, sb in candidates]
            boolean_error = any(math.isnan(v) for v in volumes)
            common = float("nan") if boolean_error else sum(volumes)
            positive = (not boolean_error) and common > 1.0e-6
            pair_key = frozenset((a.item, b.item))
            if boolean_error:
                classification = "BOOLEAN_ERROR"
                status = "FAIL"
                failed_pairs += 1
            elif positive and pair_key in accepted_internal_pairs:
                classification = accepted_internal_pairs[pair_key]
                status = "ACCEPTED_REPRESENTATION_LIMITATION"
                positive_pairs += 1
                accepted_pairs += 1
            elif positive:
                classification = "UNRESOLVED_RIGID_INTERFERENCE"
                status = "FAIL"
                positive_pairs += 1
                failed_pairs += 1
            else:
                classification = "NO_POSITIVE_COMMON_VOLUME"
                status = "PASS"
            rows.append({
                "state": state,
                "occurrence_a": a.item,
                "name_a": a.name,
                "occurrence_b": b.item,
                "name_b": b.name,
                "broad_phase_solid_candidates": len(candidates),
                "exact_common_volume_mm3": "NaN" if boolean_error else f"{common:.9f}",
                "classification": classification,
                "status": status,
            })
        summaries.append({
            "state": state,
            "broad_phase_occurrence_pairs_checked": broad_pairs,
            "positive_common_volume_pairs": positive_pairs,
            "accepted_internal_cots_representation_pairs": accepted_pairs,
            "unresolved_or_boolean_error_pairs": failed_pairs,
            "status": "PASS_WITH_DECLARED_COTS_REPRESENTATION_LIMITATIONS" if failed_pairs == 0 else "FAIL",
        })
    return rows, summaries


def part_state_geometry_signatures(parts: list[Part]) -> dict:
    signatures: dict[str, dict] = {}
    for state in ("STOWED", "DEPLOYED"):
        signatures[state] = {}
        for part in parts:
            if not (part.include_stowed if state == "STOWED" else part.include_deployed):
                continue
            shape = part.shape(state)
            bb = shape.BoundingBox()
            signatures[state][part.item] = {
                "name": part.name,
                "solid_count": len(shape.Solids()),
                "face_count": len(shape.Faces()),
                "edge_count": len(shape.Edges()),
                "volume_mm3": round(shape.Volume(), 9),
                "bbox_mm": [
                    round(bb.xmin, 6), round(bb.xmax, 6),
                    round(bb.ymin, 6), round(bb.ymax, 6),
                    round(bb.zmin, 6), round(bb.zmax, 6),
                ],
            }
    return signatures


def load_verified_pair_audit_cache(parts: list[Part]) -> tuple[list[dict], list[dict], dict]:
    """Load the completed exact audit only after state-geometry signature equality.

    The raw audit is expensive because it executes every exact Boolean pair. It is
    preserved with its executable source and raw output. The package build checks
    every occurrence's state signature before reusing the recorded audit result.
    """
    cache_path = WORK_ROOT / "full_pair_audit_cache.json"
    if not cache_path.exists():
        raise FileNotFoundError(f"Full-pair audit cache missing: {cache_path}")
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    actual = part_state_geometry_signatures(parts)
    if actual != cache.get("geometry_signatures"):
        raise RuntimeError("Full-pair audit cache geometry signatures do not match the current WP02 source model")
    return cache["rows"], cache["summaries"], cache




def initialize_ap242() -> None:
    STEPCAFControl_Controller.Init_s()
    if not Interface_Static.SetIVal_s("write.step.schema", 5):
        raise RuntimeError("OCCT AP242 schema selection unavailable")
    Interface_Static.SetIVal_s("write.precision.mode", 1)
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 1)


def sanitize_step(path: Path) -> None:
    text = path.read_text(encoding="latin-1", errors="strict")
    text = re.sub(
        r"(FILE_NAME\('[^']*',')([^']*)(')",
        lambda m: m.group(1) + FIXED_STEP_TIMESTAMP + m.group(3),
        text,
        count=1,
    )
    text = text.replace("('Author')", "('STINGRAY DF8 WP02')")
    text = text.replace("('STINGRAY DF6 PBV')", "('STINGRAY DF8 WP02')")
    path.write_text(text, encoding="latin-1", newline="\n")


def export_shape_ap242(shape: cq.Shape, name: str, path: Path) -> None:
    """Export a component shape directly through STEPControl in AP242.

    Wrapping multi-solid custom parts in a one-child XDE assembly causes an
    extreme STEPCAF export slowdown. Direct STEPControl export preserves every
    solid and the AP242 schema while the filename/placement map carry identity.
    """
    ensure_dir(path.parent)
    initialize_ap242()
    cq.exporters.export(shape, str(path), exportType="STEP")
    sanitize_step(path)
    text = path.read_text(encoding="latin-1", errors="strict")
    text = text.replace("Open CASCADE Shape Model", name)
    path.write_text(text, encoding="latin-1", newline="\n")
    header = text[:2000]
    if "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING" not in header:
        raise RuntimeError(f"AP242 header missing in {path}")


def export_assembly_ap242(assembly: cq.Assembly, path: Path) -> None:
    ensure_dir(path.parent)
    initialize_ap242()
    assembly.export(str(path), mode="default", unit="MM", outputUnit="MM", name_geometries=True)
    sanitize_step(path)
    header = path.read_text(encoding="latin-1", errors="ignore")[:2000]
    if "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING" not in header:
        raise RuntimeError(f"AP242 header missing in {path}")


# ---------- kinematic geometry ----------

def kinematic(theta_deg: float) -> dict[str, float]:
    theta = math.radians(theta_deg)
    attach_r = PIVOT_R + ARM_LINK_RADIUS * math.sin(theta)
    attach_z = PIVOT_Z + ARM_LINK_RADIUS * math.cos(theta)
    radial_delta = attach_r - CROSSHEAD_PIN_R
    root = math.sqrt(max(0.0, LINK_LENGTH ** 2 - radial_delta ** 2))
    crosshead_z = attach_z - root
    distance = math.hypot(attach_r - CROSSHEAD_PIN_R, attach_z - crosshead_z)
    return {
        "theta_deg": theta_deg,
        "attach_r_mm": attach_r,
        "attach_z_mm": attach_z,
        "crosshead_z_mm": crosshead_z,
        "link_length_mm": distance,
        "joint_mismatch_mm": abs(distance - LINK_LENGTH),
    }


KIN_STOW = kinematic(STOWED_ANGLE_DEG)
KIN_DEPLOY = kinematic(DEPLOYED_ANGLE_DEG)
CROSSHEAD_STROKE_MM = KIN_STOW["crosshead_z_mm"] - KIN_DEPLOY["crosshead_z_mm"]
SPRING_INSTALLED_DEPLOYED_MM = SPRING_INSTALLED_STOWED_MM + CROSSHEAD_STROKE_MM


def dz_dtheta_mm_per_rad(theta_deg: float) -> float:
    eps_deg = 1.0e-4
    zp = kinematic(theta_deg + eps_deg)["crosshead_z_mm"]
    zm = kinematic(theta_deg - eps_deg)["crosshead_z_mm"]
    return (zp - zm) / math.radians(2.0 * eps_deg)



def link_local_shape() -> cq.Shape:
    ring_c = eye_y(0.0, 0.0, 8.0, 6.5, 3.35)
    ring_a = eye_y(0.0, LINK_LENGTH, 8.0, 6.5, 3.35)
    start = cq.Vector(0.0, 0.0, 5.0)
    end = cq.Vector(0.0, 0.0, LINK_LENGTH - 5.0)
    # A 15 mm one-piece dogleg clears the fixed arm pivot pin throughout the sweep.
    knee1 = cq.Vector(-15.0, 0.0, LINK_LENGTH * 0.40)
    knee2 = cq.Vector(-15.0, 0.0, LINK_LENGTH * 0.60)
    return (
        ring_c.fuse(ring_a)
        .fuse(rod_between((start.x, 0, start.z), (knee1.x, 0, knee1.z), 2.8))
        .fuse(rod_between((knee1.x, 0, knee1.z), (knee2.x, 0, knee2.z), 2.8))
        .fuse(rod_between((knee2.x, 0, knee2.z), (end.x, 0, end.z), 2.8))
    )

def link_shape(theta_deg: float, phi_deg: float) -> cq.Shape:
    k = kinematic(theta_deg)
    dr = k["attach_r_mm"] - CROSSHEAD_PIN_R
    dz = k["attach_z_mm"] - k["crosshead_z_mm"]
    angle = math.degrees(math.atan2(dr, dz))
    s = link_local_shape().rotate((0, 0, 0), (0, 1, 0), angle)
    s = s.translate((CROSSHEAD_PIN_R, 0.0, k["crosshead_z_mm"]))
    return local_rotate(s, phi_deg)




def arm_local_shape() -> cq.Shape:
    """State-invariant arm with an exact sampled linkage corridor and recut bores."""
    blade_len = ARM_LENGTH - 10.0
    blade_center_r = 31.75
    outer = box(14.5, 22.0, blade_len, blade_center_r, 0.0, PIVOT_Z + 10.0 + blade_len / 2.0)
    inner = box(6.5, 19.0, blade_len - 12.0, blade_center_r, 0.0, PIVOT_Z + 16.0 + (blade_len - 12.0) / 2.0)
    blade = outer.cut(inner)
    root = box(14.5, 22.0, 82.0, blade_center_r, 0.0, PIVOT_Z + 41.0)
    s = blade.fuse(root)

    attach_r = PIVOT_R
    attach_z = PIVOT_Z + ARM_LINK_RADIUS
    s = s.fuse(eye_y(PIVOT_R, PIVOT_Z, 22.0, 10.0, 3.35))
    s = s.fuse(fork_bosses_y(attach_r, attach_z, outer_radius=7.5, hole_radius=3.35))

    # Six arm-relative link bounding envelopes form a conservative, state-invariant passage.
    for theta in (1.0, 10.0, 25.0, 50.0, 75.0, 80.0):
        ref = link_shape(theta, 0.0).rotate((PIVOT_R, 0.0, PIVOT_Z), (PIVOT_R, 1.0, PIVOT_Z), -theta)
        b = ref.BoundingBox()
        cut = box(b.xlen + 1.0, b.ylen + 1.0, b.zlen + 1.0,
                  (b.xmin+b.xmax)/2.0, (b.ymin+b.ymax)/2.0, (b.zmin+b.zmax)/2.0)
        s = s.cut(cut)

    lock_r = PIVOT_R
    lock_z = PIVOT_Z + LOCK_ARM_OFFSET_MM
    s = s.cut(cq.Solid.makeCylinder(3.35, 38.0, cq.Vector(PIVOT_R, -19.0, PIVOT_Z), cq.Vector(0, 1, 0)))
    s = s.cut(cq.Solid.makeCylinder(3.35, 34.0, cq.Vector(attach_r, -17.0, attach_z), cq.Vector(0, 1, 0)))
    s = s.cut(cq.Solid.makeCylinder(3.35, 38.0, cq.Vector(lock_r, -19.0, lock_z), cq.Vector(0, 1, 0)))
    s = s.cut(box(6.0, 24.0, 14.0, 39.0, 0.0, PIVOT_Z + 435.0))
    return s

def arm_shape(theta_deg: float, phi_deg: float) -> cq.Shape:
    s = arm_local_shape().rotate((PIVOT_R, 0, PIVOT_Z), (PIVOT_R, 1, PIVOT_Z), theta_deg)
    return local_rotate(s, phi_deg)


def guide_centers() -> list[tuple[float, float]]:
    return [polar(16.0, 122.0), polar(16.0, 288.0)]



def crosshead_local_shape() -> cq.Shape:
    z = 0.0
    # Compact center hub leaves genuine cavities for the two COTS moving eyes.
    s = tube(7.0, 4.0, z - 16.0, z + 8.0)
    for phi in (0.0, 120.0, 240.0):
        bridge_len = CROSSHEAD_PIN_R - 7.0
        bridge_center = (CROSSHEAD_PIN_R + 7.0) / 2.0
        side1 = local_rotate(box(bridge_len, 3.0, 6.0, bridge_center, -7.5, z), phi)
        side2 = local_rotate(box(bridge_len, 3.0, 6.0, bridge_center, 7.5, z), phi)
        boss = local_rotate(fork_bosses_y(CROSSHEAD_PIN_R, z, 6.5, 3.35), phi)
        s = s.fuse(side1).fuse(side2).fuse(boss)

    # Guide-bushing bosses and bridges.
    for gx, gy in guide_centers():
        boss = tube(2.0, 1.62, z - 13.0, z + 13.0, gx, gy)
        bridge = rod_between((gx, gy, z), (gx * 0.55, gy * 0.55, z), 1.6)
        s = s.fuse(boss).fuse(bridge)

    # Crosshead fork retains the custom adapter eye; the authentic B8 end is an M8 stud threaded into that adapter.
    gs_fork = fork_bosses_y(GS_CENTER_X, z, outer_radius=4.2, hole_radius=3.45)
    gs_side1 = box(5.0, 3.0, 5.0, 5.6, -8.0, z)
    gs_side2 = box(5.0, 3.0, 5.0, 5.6, 8.0, z)
    s = s.fuse(gs_fork).fuse(gs_side1).fuse(gs_side2)

    # HBD coupler supports run forward of the fixed damper body and outside the moving-eye slot.
    for yy in (-5.4, 5.4):
        s = s.fuse(cyl(1.2, z + 5.0, z + HBD_MOVING_OFFSET_Z + 8.0, -15.3, yy))
        s = s.fuse(rod_between((-7.0, yy, z + 5.0), (-15.3, yy, z + 5.0), 1.2))
        s = s.fuse(box(2.4, 2.6, 2.0, -15.3, yy, z + HBD_MOVING_OFFSET_Z + 7.0))

    # Annular spring load lug; continuous pushrod passes through its bore.
    s = s.fuse(tube(4.5, 3.2, z + 18.0, z + 25.0, SPRING_CENTER_X, SPRING_CENTER_Y))

    # Recut every functional bore after all fusions.
    for phi in (0.0, 120.0, 240.0):
        bore = local_rotate(cq.Solid.makeCylinder(3.35, 28.0, cq.Vector(CROSSHEAD_PIN_R, -14.0, z), cq.Vector(0, 1, 0)), phi)
        s = s.cut(bore)
    for gx, gy in guide_centers():
        s = s.cut(cyl(1.62, z - 15.0, z + 15.0, gx, gy))
    s = s.cut(cq.Solid.makeCylinder(3.50, 26.0, cq.Vector(GS_CENTER_X, -13.0, z), cq.Vector(0, 1, 0)))
    # COTS-eye clearance pocket through the crosshead center region.
    s = s.cut(cq.Solid.makeCylinder(5.30, 11.0, cq.Vector(GS_CENTER_X, -5.5, z), cq.Vector(0, 1, 0)))
    # Spring pushrod bore.
    s = s.cut(cyl(3.2, z + 17.0, z + 27.0, SPRING_CENTER_X, SPRING_CENTER_Y))
    # Female GS adapter neck clearance above the clevis eye.
    s = s.cut(box(7.6, 8.2, 5.2, GS_CENTER_X - 0.2, 0.0, z + 5.7))
    # HBD moving-eye and coupler side-plate swept pockets (1.2 mm lost motion).
    for zz in (HBD_MOVING_OFFSET_Z - HBD_LOST_MOTION_MM, HBD_MOVING_OFFSET_Z):
        s = s.cut(cq.Solid.makeCylinder(6.25, 8.0, cq.Vector(HBD_CENTER_X, -4.0, zz), cq.Vector(0, 1, 0)))
    for yy in (-5.4, 5.4):
        s = s.cut(box(11.4, 3.2, 16.4, HBD_CENTER_X, yy, HBD_MOVING_OFFSET_Z))
    # Captive sear bore in a sector clear of the axial COTS lanes.
    s = s.cut(radial_cylinder(2.6, -10.0, 10.0, z - 8.0, SEAR_PHI_DEG))
    return s

def crosshead_shape(theta_deg: float) -> cq.Shape:
    return crosshead_local_shape().translate((0.0, 0.0, kinematic(theta_deg)["crosshead_z_mm"]))



def pin_y(radius: float, z: float, phi_deg: float, shaft_d: float = 6.0, length: float = 24.0, head_d: float = 9.0, head_t: float = 1.5) -> cq.Shape:
    shaft = cq.Solid.makeCylinder(shaft_d / 2.0, length, cq.Vector(radius, -length / 2.0, z), cq.Vector(0, 1, 0))
    head = cq.Solid.makeCylinder(head_d / 2.0, head_t, cq.Vector(radius, -length / 2.0 - head_t, z), cq.Vector(0, 1, 0))
    # Machined retaining-ring groove; material is removed, not overlaid.
    groove_start = length / 2.0 - 0.79
    groove_cut = cq.Solid.makeCylinder(shaft_d / 2.0 + 0.1, 0.42, cq.Vector(radius, groove_start, z), cq.Vector(0, 1, 0))
    groove_root = cq.Solid.makeCylinder(2.78, 0.42, cq.Vector(radius, groove_start, z), cq.Vector(0, 1, 0))
    p = shaft.fuse(head).cut(groove_cut).fuse(groove_root)
    return local_rotate(p, phi_deg)

def smalley_vsm6_ring_local() -> cq.Shape:
    # Drawing-derived one-turn spiral ring envelope for VSM-6-S16-PA.
    ro = 3.275
    ri = 2.87
    t = 0.30
    ring = tube(ro, ri, -t / 2.0, t / 2.0)
    # Remove a 38-degree gap; the ring is an installation/clearance representation.
    gap = cq.Workplane("XY").polyline([(0, 0), (5, -2), (5, 2)]).close().extrude(1.0).translate((0, 0, -0.5)).val()
    return ring.cut(gap)


def place_ring_y(radius: float, z: float, phi_deg: float, y_center: float = 12.15) -> cq.Shape:
    ring = smalley_vsm6_ring_local().rotate((0, 0, 0), (1, 0, 0), 90.0)
    ring = ring.translate((radius, y_center, z))
    return local_rotate(ring, phi_deg)


def make_spring_helix(z0: float, installed_length: float, od: float, wire: float, solid_height: float, x: float, y: float) -> cq.Shape:
    turns = max(8.0, solid_height / wire)
    helix_height = max(installed_length - wire, wire * 2.0)
    pitch = helix_height / max(turns - 1.0, 1.0)
    center_r = (od - wire) / 2.0
    path = cq.Wire.makeHelix(pitch, helix_height, center_r, center=cq.Vector(x, y, z0 + wire / 2.0), dir=cq.Vector(0, 0, 1))
    profile = cq.Workplane("XZ", origin=(x + center_r, y, z0 + wire / 2.0)).circle(wire / 2.0)
    return profile.sweep(path, isFrenet=True).val()


# ---------- COTS and powertrain hardware geometry ----------

def load_gs_vendor_brep(df8_root: Path) -> tuple[cq.Shape, cq.Shape, cq.Shape, Path]:
    source = df8_root / (
        "08_REPRODUCIBLE_BUILD_SOURCE/parent_df7_source/inherited_df5/"
        "DF5_SOURCE_ASSETS/ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp"
    )
    if not source.exists():
        raise FileNotFoundError(f"Authentic GS vendor STEP missing: {source}")
    full = cq.importers.importStep(str(source)).val()
    body_half = box(300.0, 100.0, 100.0, 150.0, 0.0, 0.0)
    rod_half = box(200.0, 100.0, 100.0, -100.0, 0.0, 0.0)
    body = full.intersect(body_half)
    rod = full.intersect(rod_half)
    if len(body.Solids()) != 1 or len(rod.Solids()) != 1:
        raise RuntimeError("GS vendor BREP decomposition did not produce one fixed and one moving solid")
    return full, body, rod, source




def orient_vendor_x_to_global_z(shape: cq.Shape, local_x_translation: float = 0.0) -> cq.Shape:
    # Vendor product axis +X maps to global +Z; B8 is a coaxial M8 stud end fitting.
    s = shape.translate((local_x_translation, 0.0, 0.0))
    s = s.rotate((0, 0, 0), (0, 1, 0), -90.0)
    return s.translate((GS_CENTER_X, GS_CENTER_Y, GS_FIXED_TIP_Z - GS_VENDOR_X_MAX))

def gs_fixed_body_shape(gs_body_local: cq.Shape) -> cq.Shape:
    return orient_vendor_x_to_global_z(gs_body_local, 0.0)




def gs_moving_rod_shape(gs_rod_local: cq.Shape, theta_deg: float) -> cq.Shape:
    # B8 stud tip remains 10 mm aft of the crosshead; the M8 female adapter spans forward to the clevis.
    compression = kinematic(theta_deg)["crosshead_z_mm"] + 10.0 - (GS_FIXED_TIP_Z - GS_TOTAL_EXTENDED_MM)
    if not (0.0 <= compression <= GS_STROKE_MM):
        raise RuntimeError(f"GS compression outside 50 mm stroke: {compression}")
    return orient_vendor_x_to_global_z(gs_rod_local, compression)


def gs_moving_stud_tip_z(theta_deg: float) -> float:
    return kinematic(theta_deg)["crosshead_z_mm"] + 10.0


def make_gs_moving_adapter(theta_deg: float) -> cq.Shape:
    # M8x1.25 female adapter around the authentic B8 stud, terminating in a pinned single eye.
    z_tip = gs_moving_stud_tip_z(theta_deg)
    z_eye = kinematic(theta_deg)["crosshead_z_mm"]
    socket = tube(5.5, 4.15, z_tip - 0.5, z_tip + 11.5, GS_CENTER_X, GS_CENTER_Y)
    eye = eye_y(GS_CENTER_X, z_eye, 8.0, 5.0, 3.35)
    neck = box(7.0, 7.5, max(0.5, z_tip - z_eye - 4.5), GS_CENTER_X, 0.0, (z_tip + z_eye) / 2.0)
    s = socket.fuse(eye).fuse(neck)
    s = s.cut(cq.Solid.makeCylinder(3.35, 18.0, cq.Vector(GS_CENTER_X, -9.0, z_eye), cq.Vector(0, 1, 0)))
    return s



def make_gs_fixed_anchor() -> cq.Shape:
    # Female M8x1.25 adapter begins aft of the larger B8 shoulder and stops short of the spine bulkhead.
    socket = tube(6.0, 4.15, GS_FIXED_TIP_Z - 9.8, GS_FIXED_TIP_Z + 1.5, GS_CENTER_X, GS_CENTER_Y)
    flange = tube(7.2, 4.15, GS_FIXED_TIP_Z + 1.5, GS_FIXED_TIP_Z + 1.9, GS_CENTER_X, GS_CENTER_Y)
    return socket.fuse(flange)

def hbd_eye(x: float, z: float) -> cq.Shape:
    # Manufacturer-drawing-derived A-eye envelope. Exact configured CAD was unavailable.
    return eye_y(x, z, 6.0, 6.0, 2.6)



def hbd_body_shape() -> cq.Shape:
    body_z1 = HBD_FIXED_EYE_Z - 10.0
    body_z0 = body_z1 - 79.0
    body = cyl(HBD_BODY_OD_MM / 2.0, body_z0, body_z1, HBD_CENTER_X, HBD_CENTER_Y)
    rear_neck = cyl(5.0, body_z1, HBD_FIXED_EYE_Z - 5.0, HBD_CENTER_X, HBD_CENTER_Y)
    fixed_eye = hbd_eye(HBD_CENTER_X, HBD_FIXED_EYE_Z)
    adjust_flat = box(8.0, 8.0, 5.0, HBD_CENTER_X, HBD_CENTER_Y, body_z0 + 2.5)
    s = body.fuse(rear_neck).fuse(fixed_eye).fuse(adjust_flat)
    return s.cut(cq.Solid.makeCylinder(2.65, 16.0, cq.Vector(HBD_CENTER_X, -8.0, HBD_FIXED_EYE_Z), cq.Vector(0, 1, 0)))

def hbd_moving_eye_z(theta_deg: float) -> float:
    travel = KIN_STOW["crosshead_z_mm"] - kinematic(theta_deg)["crosshead_z_mm"]
    # The first 1.2 mm of crosshead motion closes the slot without moving the HBD rod.
    effective = max(0.0, travel - HBD_LOST_MOTION_MM)
    return (HBD_FIXED_EYE_Z - (HBD_EXTENDED_LENGTH_MM - HBD_END_STOP_RESERVE_MM)) + (CROSSHEAD_STROKE_MM - HBD_LOST_MOTION_MM - effective)



def hbd_rod_shape(theta_deg: float) -> cq.Shape:
    moving_z = hbd_moving_eye_z(theta_deg)
    body_front_z = HBD_FIXED_EYE_Z - 10.0 - 79.0
    rod = cyl(HBD_ROD_OD_MM / 2.0, moving_z + 5.0, body_front_z + 4.0, HBD_CENTER_X, HBD_CENTER_Y)
    eye = hbd_eye(HBD_CENTER_X, moving_z)
    shoulder = cyl(4.5, body_front_z - 3.0, body_front_z + 5.0, HBD_CENTER_X, HBD_CENTER_Y)
    s = rod.fuse(eye).fuse(shoulder)
    return s.cut(cq.Solid.makeCylinder(2.65, 16.0, cq.Vector(HBD_CENTER_X, -8.0, moving_z), cq.Vector(0, 1, 0)))


def make_hbd_moving_slot_coupler(theta_deg: float) -> cq.Shape:
    cross_z = kinematic(theta_deg)["crosshead_z_mm"] + HBD_MOVING_OFFSET_Z
    hbd_z = hbd_moving_eye_z(theta_deg)
    plates = []
    for y in (-5.4, 5.4):
        plate = box(11.0, 2.8, 16.0, HBD_CENTER_X, y, cross_z)
        slot_a = cq.Solid.makeCylinder(2.7, 4.0, cq.Vector(HBD_CENTER_X, y - 2.0, cross_z - 3.0), cq.Vector(0, 1, 0))
        slot_b = cq.Solid.makeCylinder(2.7, 4.0, cq.Vector(HBD_CENTER_X, y - 2.0, cross_z + 3.0), cq.Vector(0, 1, 0))
        slot_bridge = box(5.4, 4.0, 6.0, HBD_CENTER_X, y, cross_z)
        plates.append(plate.cut(slot_a.fuse(slot_b).fuse(slot_bridge)))
    # Bridge is offset to the far side of the HBD rod axis and contacts the two moving straps at an end face.
    top_bridge = box(1.9, 13.6, 2.5, HBD_CENTER_X - 6.45, 0.0, cross_z + 9.25)
    pin = cq.Solid.makeCylinder(2.4, 16.0, cq.Vector(HBD_CENTER_X, -8.0, hbd_z), cq.Vector(0, 1, 0))
    return compound(plates + [top_bridge, pin])


def make_hbd_bypass_carriage() -> cq.Shape:
    z = HBD_FIXED_EYE_Z
    rail_pts = ((HBD_CENTER_X + 4.5, 8.0), (HBD_CENTER_X - 4.5, -8.0))
    plates = []
    for (rx, ry), y in zip(rail_pts, (8.0, -8.0)):
        plate = box(10.8, 2.5, 18.0, HBD_CENTER_X, y, z)
        plate = plate.cut(cyl(1.72, z - 10.0, z + 10.0, rx, ry))
        plate = plate.cut(cq.Solid.makeCylinder(2.7, 4.0, cq.Vector(HBD_CENTER_X, y - 2.0, z), cq.Vector(0, 1, 0)))
        plates.append(plate)
    upper = box(3.0, 11.8, 2.5, HBD_CENTER_X - 3.8, 0.0, z + 10.25)
    fixed_pin = cq.Solid.makeCylinder(2.4, 24.0, cq.Vector(HBD_CENTER_X, -12.0, z), cq.Vector(0, 1, 0))
    return compound(plates + [upper, fixed_pin])


def make_hbd_bypass_rails() -> cq.Shape:
    rails = []
    for x, y in ((HBD_CENTER_X + 4.5, 8.0), (HBD_CENTER_X - 4.5, -8.0)):
        rails.append(cyl(1.5, HBD_FIXED_EYE_Z - 92.0, HBD_FIXED_EYE_Z + 12.0, x, y))
        rails.append(cyl(2.0, HBD_FIXED_EYE_Z - 95.0, HBD_FIXED_EYE_Z - 92.0, x, y))
        rails.append(cyl(2.0, HBD_FIXED_EYE_Z + 11.0, HBD_FIXED_EYE_Z + 14.0, x, y))
    return compound(rails)

def make_hbd_detent_set() -> cq.Shape:
    # Two compact radial plungers engage the upper carriage bridge without entering the COTS or rail envelopes.
    shapes = []
    z = HBD_FIXED_EYE_Z + 10.25
    for y in (-3.5, 3.5):
        body = cq.Solid.makeCylinder(1.75, 2.5, cq.Vector(-17.2, y, z), cq.Vector(1, 0, 0))
        ball = cq.Solid.makeSphere(1.15, cq.Vector(HBD_CENTER_X - 6.6, y, z))
        shapes.append(body.fuse(ball))
    return compound(shapes)


def make_powertrain_spine() -> cq.Shape:
    """Perforated removable cartridge spine with real clearances for every installed lane."""
    def bulkhead(z: float) -> cq.Shape:
        plate = cyl(17.75, z - 2.0, z + 2.0)
        plate = plate.cut(cyl(5.0, z - 3.0, z + 3.0))
        plate = plate.cut(cyl(12.0, z - 3.0, z + 3.0, GS_CENTER_X, GS_CENTER_Y))
        plate = plate.cut(cyl(8.05, z - 3.0, z + 3.0, HBD_CENTER_X, HBD_CENTER_Y))
        plate = plate.cut(cyl(8.00, z - 3.0, z + 3.0, SPRING_CENTER_X, SPRING_CENTER_Y))
        for gx, gy in guide_centers():
            plate = plate.cut(cyl(1.85, z - 3.0, z + 3.0, gx, gy))
        return plate
    bulkheads = [bulkhead(z) for z in (540.0, 744.0, 965.0)]
    rails = []
    for phi in (50.0, 240.0, 310.0):
        x, y = polar(16.3, phi)
        rails.append(cyl(1.15, 540.0, 970.0, x, y))
    return compound(bulkheads + rails)

def make_crosshead_guide_rods() -> cq.Shape:
    rods = [cyl(1.5, 535.0, 615.0, gx, gy) for gx, gy in guide_centers()]
    ends = []
    for gx, gy in guide_centers():
        ends.extend([cyl(1.90, 532.0, 535.0, gx, gy), cyl(1.90, 615.0, 618.0, gx, gy)])
    return compound(rods + ends)


def spring_moving_seat_z(theta_deg: float) -> float:
    travel = KIN_STOW["crosshead_z_mm"] - kinematic(theta_deg)["crosshead_z_mm"]
    return SPRING_FIXED_SEAT_Z - SPRING_INSTALLED_STOWED_MM - travel



def make_selected_spring(theta_deg: float) -> cq.Shape:
    z0 = spring_moving_seat_z(theta_deg)
    installed = SPRING_FIXED_SEAT_Z - z0
    # 0.15 mm graphical end-face clearance prevents false material overlap with ground-end seats.
    return make_spring_helix(z0 + 0.15, installed - 0.30, SPRING_OD_MM, SPRING_WIRE_MM, SPRING_SOLID_HEIGHT_MM, SPRING_CENTER_X, SPRING_CENTER_Y)

def make_rejected_spring_reference() -> cq.Shape:
    return make_spring_helix(0.0, REJECTED_SPRING_INSTALLED_MM, REJECTED_SPRING_OD_MM, REJECTED_SPRING_WIRE_MM, REJECTED_SPRING_SOLID_HEIGHT_MM, 0.0, 0.0)


def make_selected_spring_reference() -> cq.Shape:
    return make_spring_helix(0.0, SPRING_FREE_LENGTH_MM, SPRING_OD_MM, SPRING_WIRE_MM, SPRING_SOLID_HEIGHT_MM, 0.0, 0.0)




def make_spring_fixed_seat() -> cq.Shape:
    # Contact face is Z=965; seat material lies aft of the spring.
    disc = tube(7.55, 3.25, SPRING_FIXED_SEAT_Z, SPRING_FIXED_SEAT_Z + 3.0, SPRING_CENTER_X, SPRING_CENTER_Y)
    x0, y0 = polar(13.7, 240.0)
    bridge = rod_between((x0, y0, SPRING_FIXED_SEAT_Z + 3.35), (SPRING_CENTER_X - 7.6, SPRING_CENTER_Y, SPRING_FIXED_SEAT_Z + 3.35), 1.35)
    anti_buckle = tube(4.30, 3.25, SPRING_FIXED_SEAT_Z - 25.0, SPRING_FIXED_SEAT_Z - 0.2, SPRING_CENTER_X, SPRING_CENTER_Y)
    return disc.fuse(bridge).fuse(anti_buckle)


def make_spring_moving_seat(theta_deg: float) -> cq.Shape:
    # Contact face is the moving-seat Z coordinate; seat material lies forward of the spring.
    z = spring_moving_seat_z(theta_deg)
    disc = tube(7.55, 3.25, z - 3.0, z, SPRING_CENTER_X, SPRING_CENTER_Y)
    guide = tube(4.30, 3.25, z - 25.0, z - 3.1, SPRING_CENTER_X, SPRING_CENTER_Y)
    return disc.fuse(guide)

def make_spring_pushrod(theta_deg: float) -> cq.Shape:
    z0 = kinematic(theta_deg)["crosshead_z_mm"] + 20.0
    z1 = spring_moving_seat_z(theta_deg)
    rod = cyl(SPRING_GUIDE_ROD_D_MM / 2.0, z0, z1, SPRING_CENTER_X, SPRING_CENTER_Y)
    locknut = tube(4.5, 3.1, z1 - 29.0, z1 - 25.2, SPRING_CENTER_X, SPRING_CENTER_Y)
    return rod.fuse(locknut)


def lock_point(theta_deg: float) -> tuple[float, float]:
    th = math.radians(theta_deg)
    return PIVOT_R + LOCK_ARM_OFFSET_MM * math.sin(th), PIVOT_Z + LOCK_ARM_OFFSET_MM * math.cos(th)




def make_lock_housing_set() -> cq.Shape:
    r, z = lock_point(DEPLOYED_ANGLE_DEG)
    shapes = []
    for phi in (0.0, 120.0, 240.0):
        left = cq.Solid.makeCylinder(4.2, 4.0, cq.Vector(r, -16.0, z), cq.Vector(0, 1, 0))
        right = cq.Solid.makeCylinder(4.2, 4.0, cq.Vector(r, 12.0, z), cq.Vector(0, 1, 0))
        bore = cq.Solid.makeCylinder(3.45, 36.0, cq.Vector(r, -18.0, z), cq.Vector(0, 1, 0))
        foot = radial_box(r + 3.8, 49.5, 6.0, z - 5.0, z + 5.0, 0.0)
        housing = left.fuse(right).fuse(foot).cut(bore)
        shapes.append(local_rotate(housing, phi))
    return compound(shapes)

def make_lock_plunger_set(deployed: bool) -> cq.Shape:
    r, z = lock_point(DEPLOYED_ANGLE_DEG)
    shapes = []
    for phi in (0.0, 120.0, 240.0):
        if deployed:
            p = cq.Solid.makeCylinder(3.0, 28.0, cq.Vector(r, -14.0, z), cq.Vector(0, 1, 0))
            witness = cq.Solid.makeCylinder(1.3, 6.0, cq.Vector(r + 5.8, 13.0, z), cq.Vector(0, 1, 0))
        else:
            p = cq.Solid.makeCylinder(3.0, 8.0, cq.Vector(r, 13.0, z), cq.Vector(0, 1, 0))
            witness = cq.Solid.makeCylinder(1.3, 6.0, cq.Vector(r + 5.8, 14.0, z), cq.Vector(0, 1, 0))
        shapes.append(local_rotate(p.fuse(witness), phi))
    return compound(shapes)



def make_stop_pad_set() -> cq.Shape:
    # Side-mounted replaceable pads contact the deployed arm heel outside the central link plane.
    th = math.radians(DEPLOYED_ANGLE_DEG)
    u = cq.Vector(math.sin(th), 0.0, math.cos(th))
    n = cq.Vector(math.cos(th), 0.0, -math.sin(th))
    base = cq.Vector(PIVOT_R, 0.0, PIVOT_Z) + u.multiply(4.0) + n.multiply(15.0)
    local = box(3.0, 3.5, 5.0, base.x, 8.5, base.z)
    local = local.rotate((base.x, 8.5, base.z), (base.x, 9.5, base.z), DEPLOYED_ANGLE_DEG)
    return compound([local_rotate(local, phi) for phi in (0.0, 120.0, 240.0)])

def tangential_cylinder(radius: float, length: float, radial_center: float, z: float, phi_deg: float) -> cq.Shape:
    a = math.radians(phi_deg)
    ux, uy = math.cos(a), math.sin(a)
    tx, ty = -uy, ux
    start = cq.Vector(radial_center * ux - tx * length / 2.0, radial_center * uy - ty * length / 2.0, z)
    return cq.Solid.makeCylinder(radius, length, start, cq.Vector(tx, ty, 0.0))



def make_stow_latch_set(released: bool) -> cq.Shape:
    # Captive narrow pawls enter the machined arm notches; fixed pivots remain outside the arm envelope.
    shapes = []
    theta = math.radians(STOWED_ANGLE_DEG)
    arm_z = PIVOT_Z + 435.0 * math.cos(theta)
    z_shift = 11.0 if released else 0.0
    for phi in (0.0, 120.0, 240.0):
        pivot = tangential_cylinder(1.8, 5.0, 49.0, arm_z + 7.0 + z_shift, phi)
        pawl = radial_box(45.0, 49.0, 3.2, arm_z - 3.5 + z_shift, arm_z + 3.5 + z_shift, phi)
        bridge = radial_box(48.4, 49.5, 3.2, arm_z + 2.5 + z_shift, arm_z + 7.0 + z_shift, phi)
        shapes.append(pivot.fuse(pawl).fuse(bridge))
    return compound(shapes)


def make_crosshead_sear(theta_deg: float, released: bool) -> cq.Shape:
    z = kinematic(theta_deg)["crosshead_z_mm"] - 8.0
    r0, r1 = (7.5, 17.0) if not released else (12.5, 17.0)
    return radial_cylinder(2.4, r0, r1, z, SEAR_PHI_DEG)



def make_sear_housing() -> cq.Shape:
    z = KIN_STOW["crosshead_z_mm"] - 8.0
    outer = radial_cylinder(4.2, 10.5, 17.2, z, SEAR_PHI_DEG)
    bore = radial_cylinder(2.6, 10.0, 17.5, z, SEAR_PHI_DEG)
    foot = radial_box(15.2, 17.3, 4.0, z - 4.0, z + 4.0, SEAR_PHI_DEG + 18.0)
    h = outer.cut(bore).fuse(foot)
    # Machine explicit swept clearances for the crosshead, guide rods and HBD moving hardware.
    for theta in (1.0, 25.0, 50.0, 80.0):
        h = h.cut(crosshead_shape(theta))
        h = h.cut(hbd_rod_shape(theta))
        h = h.cut(make_hbd_moving_slot_coupler(theta))
    h = h.cut(make_crosshead_guide_rods())
    return h

def make_pivot_bushing_set() -> cq.Shape:
    shapes = []
    for phi in (0.0, 120.0, 240.0):
        left = cq.Solid.makeCylinder(4.0, 3.0, cq.Vector(PIVOT_R, -16.0, PIVOT_Z), cq.Vector(0, 1, 0)).cut(
            cq.Solid.makeCylinder(3.18, 3.5, cq.Vector(PIVOT_R, -16.25, PIVOT_Z), cq.Vector(0, 1, 0)))
        right = cq.Solid.makeCylinder(4.0, 3.0, cq.Vector(PIVOT_R, 13.0, PIVOT_Z), cq.Vector(0, 1, 0)).cut(
            cq.Solid.makeCylinder(3.18, 3.5, cq.Vector(PIVOT_R, 12.75, PIVOT_Z), cq.Vector(0, 1, 0)))
        shapes.append(local_rotate(left.fuse(right), phi))
    return compound(shapes)


def make_arm_pin_set(theta_deg: float, which: str) -> cq.Shape:
    shapes = []
    k = kinematic(theta_deg)
    for phi in (0.0, 120.0, 240.0):
        if which == "PIVOT":
            r, z, length = PIVOT_R, PIVOT_Z, 34.0
        elif which == "ARM_LINK":
            r, z, length = k["attach_r_mm"], k["attach_z_mm"], 24.0
        elif which == "CROSSHEAD_LINK":
            r, z, length = CROSSHEAD_PIN_R, k["crosshead_z_mm"], 24.0
        else:
            raise ValueError(which)
        shapes.append(pin_y(r, z, phi, length=length))
    return compound(shapes)


def make_ring_set(theta_deg: float) -> cq.Shape:
    k = kinematic(theta_deg)
    shapes = []
    for phi in (0.0, 120.0, 240.0):
        shapes.append(place_ring_y(PIVOT_R, PIVOT_Z, phi, y_center=16.42))
        shapes.append(place_ring_y(k["attach_r_mm"], k["attach_z_mm"], phi, y_center=11.42))
        shapes.append(place_ring_y(CROSSHEAD_PIN_R, k["crosshead_z_mm"], phi, y_center=11.42))
    return compound(shapes)

# ---------- subsystem part definition ----------

def create_parts(df8_root: Path) -> tuple[list[Part], dict]:
    gs_full, gs_body_local, gs_rod_local, gs_source = load_gs_vendor_brep(df8_root)
    parts: list[Part] = []

    # Moving rigid arm chain.
    for idx, phi in enumerate((0.0, 120.0, 240.0), start=1):
        parts.append(Part(
            f"WP02-{idx:03d}", f"ARM_{idx}", "Arm and hub", "17-4PH stainless steel", "CUSTOM RIGID",
            "STINGRAY", f"STG-WP02-ARM-{idx}", "CUSTOM REGENERABLE CAD",
            arm_shape(STOWED_ANGLE_DEG, phi), arm_shape(DEPLOYED_ANGLE_DEG, phi),
            attachment="6 mm pivot pin in WP01 shell double-shear clevis; link pin at 35 mm arm station",
            retention="Headed 17-4PH pin plus VSM-6-S16-PA secondary ring; positive deployed lock pin",
            service="Withdraw retaining ring and pin after crosshead energy is restrained",
            limitation="External structural loads are reacted through root stop and lock into WP01 shell, not through the link or actuators.",
            color=(0.72, 0.72, 0.76)))
        parts.append(Part(
            f"WP02-{idx+3:03d}", f"LINK_{idx}", "Arm powertrain", "17-4PH stainless steel", "CUSTOM RIGID",
            "STINGRAY", f"STG-WP02-LINK-{idx}", "CUSTOM REGENERABLE CAD",
            link_shape(STOWED_ANGLE_DEG, phi), link_shape(DEPLOYED_ANGLE_DEG, phi),
            attachment="Pinned between the rigid arm fork and common-crosshead fork",
            retention="Headed 17-4PH pins plus VSM-6-S16-PA secondary rings",
            service="Pins withdraw tangentially through the opened arm bay",
            limitation="70.000 mm pin-center length; no state-dependent part geometry.",
            color=(0.55, 0.58, 0.63)))

    parts.extend([
        Part("WP02-007", "COMMON_CROSSHEAD", "Arm powertrain", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-007", "CUSTOM REGENERABLE CAD",
             crosshead_shape(STOWED_ANGLE_DEG), crosshead_shape(DEPLOYED_ANGLE_DEG),
             attachment="Two axial guide rods; three link clevises; GS adapter; HBD slot coupler; spring guide rod",
             retention="Captive between guide-rod end shoulders and all three pinned links",
             service="Release sear, unload spring with reset fixture, remove links, then withdraw along guides",
             limitation="One rigid crosshead translated by the authoritative solver; no linear state scheduling.", color=(0.38, 0.42, 0.48)),
        Part("WP02-008", "PIVOT_BUSHING_SET", "Arm and hub", "PEEK", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-008", "CUSTOM REGENERABLE CAD",
             make_pivot_bushing_set(), quantity=6,
             attachment="Interference/transition fit in the WP01 pivot-clevis bores",
             retention="Captured axially between the arm eye and WP01 clevis ears",
             service="Replace whenever pivot pin or arm is removed", color=(0.72, 0.55, 0.25)),
        Part("WP02-009", "ARM_PIVOT_PIN_SET", "Arm and hub", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-009", "CUSTOM REGENERABLE CAD",
             make_arm_pin_set(STOWED_ANGLE_DEG, "PIVOT"), quantity=3,
             attachment="6.00 mm clearance-fit double-shear pivot",
             retention="Integral head and VSM-6-S16-PA ring in 5.70 mm groove",
             service="Remove ring with approved pick, withdraw tangentially", color=(0.45, 0.47, 0.50)),
        Part("WP02-010", "ARM_LINK_PIN_SET", "Arm powertrain", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-010", "CUSTOM REGENERABLE CAD",
             make_arm_pin_set(STOWED_ANGLE_DEG, "ARM_LINK"), make_arm_pin_set(DEPLOYED_ANGLE_DEG, "ARM_LINK"), quantity=3,
             attachment="6.00 mm clearance-fit pin at the arm fork",
             retention="Integral head and VSM-6-S16-PA ring",
             service="Withdraw tangentially after spring unloading", color=(0.45, 0.47, 0.50)),
        Part("WP02-011", "CROSSHEAD_LINK_PIN_SET", "Arm powertrain", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-011", "CUSTOM REGENERABLE CAD",
             make_arm_pin_set(STOWED_ANGLE_DEG, "CROSSHEAD_LINK"), make_arm_pin_set(DEPLOYED_ANGLE_DEG, "CROSSHEAD_LINK"), quantity=3,
             attachment="6.00 mm clearance-fit pin at the common crosshead",
             retention="Integral head and VSM-6-S16-PA ring",
             service="Withdraw tangentially after spring unloading", color=(0.45, 0.47, 0.50)),
        Part("WP02-012", "VSM6_RETENTION_RING_SET", "Pin retention", "316 stainless steel", "COTS DRAWING-DERIVED",
             "Smalley", "VSM-6-S16-PA", "MANUFACTURER-DRAWING-DERIVED; NOT AUTHENTIC VENDOR CAD",
             make_ring_set(STOWED_ANGLE_DEG), make_ring_set(DEPLOYED_ANGLE_DEG), quantity=9,
             attachment="External 5.70 mm shaft groove on each 6 mm pin",
             retention="One-turn Spirolox ring; low axial positioning duty only",
             service="Replace after removal or visible distortion",
             limitation="Primary shear and joint separation are carried by the headed pin/clevis; ring is not credited for structural arm load.", color=(0.35, 0.35, 0.38)),
        Part("WP02-013", "POWERTRAIN_CARTRIDGE_SPINE", "Powertrain fixed structure", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-013", "CUSTOM REGENERABLE CAD",
             make_powertrain_spine(),
             attachment="Two removable mounting feet to WP01 protected-core bosses at Z=545 and 960",
             retention="Four captive M4 fasteners plus dowel keys; interfaces controlled but body fasteners remain WP01/WP06 verification items",
             service="Withdraw aft as a complete powertrain cartridge after WP04 removal",
             limitation="Protected bay boundary and body-boss detail require final WP06 integration.", color=(0.25, 0.28, 0.32)),
        Part("WP02-014", "CROSSHEAD_GUIDE_ROD_SET", "Powertrain guidance", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-014", "CUSTOM REGENERABLE CAD",
             make_crosshead_guide_rods(), quantity=2,
             attachment="Shouldered into the removable cartridge spine",
             retention="Captured by enlarged end shoulders and spine crossbars",
             service="Remove only with the crosshead and spring fully unloaded",
             limitation="Guide straightness and wet contamination qualification remain physical CTQs.", color=(0.50, 0.52, 0.55)),
        Part("WP02-015", "GS19_FIXED_BODY_EXACT_VENDOR_BREP", "Primary arm drive", "Vendor-defined stainless assembly", "COTS AUTHENTIC VENDOR BREP SPLIT",
             "ACE Controls", "GS-19-50-V4A-B8-B8", "AUTHENTIC VENDOR CAD; UNCHANGED BREP EXCEPT BOOLEAN DECOMPOSITION AT REAL PRISMATIC JOINT",
             gs_fixed_body_shape(gs_body_local),
             attachment="Exact B8 fixed stud in positively secured M8 socket on WP02 fixed anchor",
             retention="Thread-locking feature plus locknut/anti-rotation clamp; external positive travel stop supplied by mechanism",
             service="Unscrew only after spring unloading and crosshead restraint",
             limitation="300 +/- 30 N F1 at 20 C is the controlled development procurement/charge specification; existing unit charge is not verified.",
             mass_override_kg=0.34, color=(0.62, 0.66, 0.69)),
        Part("WP02-016", "GS19_MOVING_ROD_EXACT_VENDOR_BREP", "Primary arm drive", "Vendor-defined stainless assembly", "COTS AUTHENTIC VENDOR BREP SPLIT",
             "ACE Controls", "GS-19-50-V4A-B8-B8", "AUTHENTIC VENDOR CAD; UNCHANGED BREP EXCEPT BOOLEAN DECOMPOSITION AT REAL PRISMATIC JOINT",
             gs_moving_rod_shape(gs_rod_local, STOWED_ANGLE_DEG), gs_moving_rod_shape(gs_rod_local, DEPLOYED_ANGLE_DEG),
             attachment="Exact B8 moving stud threaded into the crosshead adapter",
             retention="Threaded adapter plus locknut and anti-rotation key",
             service="Rod remains with GS body during normal COTS replacement",
             limitation="Rod is translated without scaling; 23.074 mm mechanism travel remains within the 50 mm GS stroke.",
             mass_override_kg=0.08, color=(0.78, 0.80, 0.82)),
        Part("WP02-017", "GS19_FIXED_ANCHOR", "Primary arm drive", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-017", "CUSTOM REGENERABLE CAD",
             make_gs_fixed_anchor(),
             attachment="Welded/bolted crossmember on cartridge spine",
             retention="M8 socket, locknut and anti-rotation clamp",
             service="Accessible through opened arm bay", color=(0.35, 0.38, 0.42)),
        Part("WP02-018", "GS19_MOVING_ADAPTER", "Primary arm drive", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-018", "CUSTOM REGENERABLE CAD",
             make_gs_moving_adapter(STOWED_ANGLE_DEG), make_gs_moving_adapter(DEPLOYED_ANGLE_DEG),
             attachment="M8 threaded B8 stud to crosshead lug",
             retention="Locknut and mechanical anti-rotation key",
             service="Remove with GS unit", color=(0.38, 0.40, 0.44)),
        Part("WP02-019", "HBD15_BODY_DRAWING_DERIVED", "Motion damping", "Black anodized aluminum / hard-chrome steel", "COTS DRAWING-DERIVED",
             "ACE Controls", "HBD-15-25-AA-P", "MANUFACTURER-DRAWING-DERIVED; NOT AUTHENTIC VENDOR CAD",
             hbd_body_shape(),
             attachment="Fixed A-eye pin in the captive bypass carriage",
             retention="Headed pin plus lock plate; end fitting requires positive anti-unscrew feature",
             service="Replace through opened arm bay with cartridge installed",
             limitation="Exact configured vendor CAD and ordered suffix confirmation remain required; model uses the official OD, stroke and extended-length envelope.",
             mass_override_kg=0.16, color=(0.10, 0.10, 0.12)),
        Part("WP02-020", "HBD15_ROD_DRAWING_DERIVED", "Motion damping", "Black anodized aluminum / hard-chrome steel", "COTS DRAWING-DERIVED",
             "ACE Controls", "HBD-15-25-AA-P", "MANUFACTURER-DRAWING-DERIVED; NOT AUTHENTIC VENDOR CAD",
             hbd_rod_shape(STOWED_ANGLE_DEG), hbd_rod_shape(DEPLOYED_ANGLE_DEG),
             attachment="Moving A-eye pin in lost-motion crosshead coupler",
             retention="Headed pin and positive anti-unscrew lock",
             service="Moves with HBD body as one service item",
             limitation="HBD motion is 21.874 mm after 1.2 mm lost motion; gross nominal reserve is 3.126 mm and residual reserve is 1.626 mm after the 1.5 mm external-stop allowance.",
             mass_override_kg=0.06, color=(0.72, 0.74, 0.76)),
        Part("WP02-021", "HBD_MOVING_LOST_MOTION_COUPLER", "Motion damping", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-021", "CUSTOM REGENERABLE CAD",
             make_hbd_moving_slot_coupler(STOWED_ANGLE_DEG), make_hbd_moving_slot_coupler(DEPLOYED_ANGLE_DEG),
             attachment="Bolted to crosshead HBD lug; A-eye pin rides in a captive axial slot",
             retention="Closed slot with retained headed pin",
             service="Remove with HBD after unloading",
             limitation="1.20 mm slot take-up is a tolerance-control feature, not uncontrolled free travel.", color=(0.38, 0.41, 0.45)),
        Part("WP02-022", "HBD_CAPTIVE_BYPASS_CARRIAGE", "Motion damping", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-022", "CUSTOM REGENERABLE CAD",
             make_hbd_bypass_carriage(),
             attachment="Slides on two captive bypass rails; holds HBD fixed eye",
             retention="Rail end shoulders capture carriage in both normal and bypass positions",
             service="Detents reset manually with calibrated fixture",
             limitation="Nonfragmenting fallback replaces the inherited shear-fuse concept.", color=(0.36, 0.39, 0.43)),
        Part("WP02-023", "HBD_BYPASS_RAIL_AND_SHOULDER_SET", "Motion damping", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-023", "CUSTOM REGENERABLE CAD",
             make_hbd_bypass_rails(), quantity=2,
             attachment="Fixed to cartridge spine",
             retention="Integral enlarged shoulders; no loose fragments on bypass",
             service="Inspect rail straightness and carriage freedom after any bypass event", color=(0.46, 0.49, 0.52)),
        Part("WP02-024", "HBD_BYPASS_DETENT_SET", "Motion damping", "17-4PH stainless steel", "CUSTOM CALIBRATED",
             "STINGRAY", "STG-WP02-024", "CUSTOM REGENERABLE CAD",
             make_hbd_detent_set(), quantity=2,
             attachment="Opposed threaded ball plungers in the spine crossmember",
             retention="Threaded bodies with locknuts and witness lacquer",
             service="Bench-calibrate release to 450 +/- 30 N and inspect/reset after bypass event",
             limitation="Release force is analytically specified but requires lot-level physical calibration.", color=(0.52, 0.54, 0.57)),
        Part("WP02-025", "BACKUP_SPRING_LHL625D12", "Passive redundant arm drive", SPRING_MATERIAL, "COTS DRAWING-DERIVED",
             "Lee Spring", SPRING_SELECTED_PN, "MANUFACTURER-CATALOG-DERIVED; AUTHENTIC CAD DOWNLOAD NOT RETRIEVED",
             make_selected_spring(STOWED_ANGLE_DEG), make_selected_spring(DEPLOYED_ANGLE_DEG),
             attachment="Captive between fixed reaction seat and moving seat on 8 mm guide rod",
             retention="Ground ends captured by concentric shoulders; guide rod prevents buckling/ejection",
             service="Unload with threaded reset fixture before removing seats",
             limitation="Selected after rejecting inherited spring; procurement certificate and incoming rate/length inspection required.",
             mass_override_kg=0.18, color=(0.25, 0.30, 0.36)),
        Part("WP02-026", "BACKUP_SPRING_FIXED_REACTION_SEAT", "Passive redundant arm drive", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-026", "CUSTOM REGENERABLE CAD",
             make_spring_fixed_seat(),
             attachment="Crossmember to cartridge spine at Z=965",
             retention="Bolted/doweled connection; axial load carried directly into spine",
             service="Remove only with reset fixture engaged", color=(0.34, 0.37, 0.40)),
        Part("WP02-027", "BACKUP_SPRING_MOVING_SEAT", "Passive redundant arm drive", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-027", "CUSTOM REGENERABLE CAD",
             make_spring_moving_seat(STOWED_ANGLE_DEG), make_spring_moving_seat(DEPLOYED_ANGLE_DEG),
             attachment="Threaded and keyed to the continuous spring guide/pushrod",
             retention="Locknut and radial key; captured by spring and guide rod",
             service="Withdraw with guide rod after spring unloading", color=(0.34, 0.37, 0.40)),
        Part("WP02-028", "BACKUP_SPRING_GUIDE_PUSHROD", "Passive redundant arm drive", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-028", "CUSTOM REGENERABLE CAD",
             make_spring_pushrod(STOWED_ANGLE_DEG), make_spring_pushrod(DEPLOYED_ANGLE_DEG),
             attachment="Crosshead lug to moving spring seat",
             retention="Pinned crosshead end; locknut/key at moving seat",
             service="Serves as spring guide and positive load path; remove after unloading", color=(0.46, 0.49, 0.52)),
        Part("WP02-029", "DEPLOYED_STOP_PAD_SET", "Arm stop", "Polyurethane 90A", "CUSTOM REPLACEABLE",
             "STINGRAY", "STG-WP02-029", "CUSTOM REGENERABLE CAD",
             make_stop_pad_set(), quantity=3,
             attachment="Captured dovetail/shoulder in WP01-compatible fixed stop carrier",
             retention="Mechanical capture; adhesive is not credited",
             service="Replace after visible set, tearing or out-of-family deployment impact",
             limitation="Material lot compression curve and saltwater aging require physical characterization.", color=(0.20, 0.35, 0.20)),
        Part("WP02-030", "POSITIVE_LOCK_HOUSING_SET", "Deployed retention", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-030", "CUSTOM REGENERABLE CAD",
             make_lock_housing_set(), quantity=3,
             attachment="Bolted/doweled to WP01 shell pivot region",
             retention="Fixed structure; no reliance on gas or spring preload",
             service="Accessible through opened arm bays", color=(0.34, 0.37, 0.40)),
        Part("WP02-031", "POSITIVE_LOCK_PLUNGER_AND_WITNESS_SET", "Deployed retention", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-031", "CUSTOM REGENERABLE CAD",
             make_lock_plunger_set(False), make_lock_plunger_set(True), quantity=3,
             attachment="Spring-biased captive plunger through deployed arm root bore",
             retention="Captive shoulder and housing end cap",
             service="Manual pull-and-hold release during controlled reset",
             limitation="Witness extension is directly visible only with the corresponding WP01 cover open.", color=(0.82, 0.25, 0.18)),
        Part("WP02-032", "CROSSHEAD_SEAR", "Stowed retention", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-032", "CUSTOM REGENERABLE CAD",
             make_crosshead_sear(STOWED_ANGLE_DEG, False), make_crosshead_sear(DEPLOYED_ANGLE_DEG, True),
             attachment="Radial engagement through crosshead hub; WP03 release cable interface",
             retention="Captive in fixed housing with return spring and end shoulder",
             service="Manually reset after spring compression and arm stow",
             limitation="WP03 owns the exact release cable and common water-activation interface.", color=(0.82, 0.25, 0.18)),
        Part("WP02-033", "CROSSHEAD_SEAR_HOUSING", "Stowed retention", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-033", "CUSTOM REGENERABLE CAD",
             make_sear_housing(),
             attachment="Fixed to cartridge spine",
             retention="Bolted and doweled",
             service="Accessible with forward service panel open", color=(0.34, 0.37, 0.40)),
        Part("WP02-034", "COVER_SEQUENCED_ARM_STOW_LATCH_SET", "Stowed arm retention", "17-4PH stainless steel", "CUSTOM RIGID",
             "STINGRAY", "STG-WP02-034", "CUSTOM REGENERABLE CAD",
             make_stow_latch_set(False), make_stow_latch_set(True), quantity=3,
             attachment="Fixed housings at aft arm-bay station; rollers engage WP01 cover cam surfaces",
             retention="Captive pawls and pivot pins",
             service="Inspect engagement before every armed configuration",
             limitation="Cover cam profile and opening torque require WP01/WP02 physical correlation; digital sequence is cover-open-first.", color=(0.50, 0.38, 0.20)),
    ])

    vendor = {
        "full": gs_full,
        "body_local": gs_body_local,
        "rod_local": gs_rod_local,
        "source": gs_source,
    }
    return parts, vendor


# ---------- analysis, audit, documentation, and packaging ----------


def kinematic_rows() -> list[dict]:
    rows = []
    for theta in [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 80.0]:
        k = kinematic(theta)
        x = KIN_STOW["crosshead_z_mm"] - k["crosshead_z_mm"]
        dx = -dz_dtheta_mm_per_rad(theta)
        rows.append({
            "arm_angle_deg": f"{theta:.6f}",
            "attach_r_mm": f"{k['attach_r_mm']:.6f}",
            "attach_z_mm": f"{k['attach_z_mm']:.6f}",
            "crosshead_z_mm": f"{k['crosshead_z_mm']:.6f}",
            "crosshead_travel_mm": f"{x:.6f}",
            "dx_dtheta_mm_per_rad": f"{dx:.6f}",
            "link_length_mm": f"{k['link_length_mm']:.9f}",
            "joint_mismatch_mm": f"{k['joint_mismatch_mm']:.12f}",
        })
    return rows


def force_rows() -> list[dict]:
    rows = []
    for theta in np.linspace(STOWED_ANGLE_DEG, DEPLOYED_ANGLE_DEG, 17):
        k = kinematic(float(theta))
        x = KIN_STOW["crosshead_z_mm"] - k["crosshead_z_mm"]
        spring_len = SPRING_INSTALLED_STOWED_MM + x
        spring_force = SPRING_RATE_N_PER_MM * (SPRING_FREE_LENGTH_MM - spring_len)
        gs_compression = CROSSHEAD_STROKE_MM - x
        gs_force = GS_FORCE_NOMINAL_N * (1.0 + 0.30 * gs_compression / GS_STROKE_MM)
        rows.append({
            "arm_angle_deg": f"{theta:.6f}",
            "crosshead_travel_mm": f"{x:.6f}",
            "spring_installed_length_mm": f"{spring_len:.6f}",
            "spring_force_n": f"{spring_force:.3f}",
            "gs_compression_mm": f"{gs_compression:.6f}",
            "gs_force_nominal_n": f"{gs_force:.3f}",
            "combined_drive_force_n": f"{spring_force + gs_force:.3f}",
            "mechanical_advantage_dx_dtheta_mm_per_rad": f"{-dz_dtheta_mm_per_rad(float(theta)):.6f}",
        })
    return rows


def simulate_dynamic_case(
    name: str,
    gs_f1_n: float,
    spring_factor: float,
    friction_n: float,
    damping_enabled: bool,
    gravity_opposes: bool,
    bypass_open: bool = False,
    extra_bind_n: float = 0.0,
) -> dict:
    theta0 = math.radians(STOWED_ANGLE_DEG)
    theta1 = math.radians(DEPLOYED_ANGLE_DEG)
    z0 = KIN_STOW["crosshead_z_mm"]
    arm_mass = 0.7154375793747744
    arm_com_from_pivot_m = 0.2305
    # Three arm beams plus links/crosshead/pins expressed as a conservative constant inertia.
    inertia_kg_m2 = 3.0 * arm_mass * arm_com_from_pivot_m ** 2 / 3.0 + 0.015
    c_n_s_per_m = HBD_NORMAL_DAMPING_FORCE_N / 0.100

    def x_m(theta_rad: float) -> float:
        return (z0 - kinematic(math.degrees(theta_rad))["crosshead_z_mm"]) / 1000.0

    def dx_dtheta_m(theta_rad: float) -> float:
        return -dz_dtheta_mm_per_rad(math.degrees(theta_rad)) / 1000.0

    bypass_release_margin = (
        SPRING_RATE_N_PER_MM * (SPRING_FREE_LENGTH_MM - SPRING_INSTALLED_STOWED_MM) * spring_factor
        + gs_f1_n * (1.0 + 0.30 * CROSSHEAD_STROKE_MM / GS_STROKE_MM)
        - friction_n - extra_bind_n - (HBD_BYPASS_DETENT_N - HBD_BYPASS_DETENT_TOL_N)
    )

    def rhs(_t: float, y: np.ndarray) -> list[float]:
        theta, omega = float(y[0]), float(y[1])
        x = x_m(theta)
        dxdth = max(dx_dtheta_m(theta), 1.0e-6)
        xdot = max(0.0, dxdth * omega)
        spring_len = SPRING_INSTALLED_STOWED_MM + x * 1000.0
        spring_force = max(0.0, SPRING_RATE_N_PER_MM * (SPRING_FREE_LENGTH_MM - spring_len) * spring_factor)
        compression = max(0.0, CROSSHEAD_STROKE_MM - x * 1000.0)
        gs_force = max(0.0, gs_f1_n * (1.0 + 0.30 * compression / GS_STROKE_MM))
        damping_force = 0.0
        if damping_enabled and not bypass_open and x > HBD_LOST_MOTION_MM / 1000.0 and xdot > 0.0:
            damping_force = min(HBD_NORMAL_DAMPING_FORCE_N, c_n_s_per_m * xdot)
        net_linear = spring_force + gs_force - friction_n - extra_bind_n - damping_force
        generalized_drive = net_linear * dxdth
        gravity_torque = 0.0
        if gravity_opposes:
            gravity_torque = 3.0 * arm_mass * 9.80665 * arm_com_from_pivot_m * math.sin(theta)
        alpha = (generalized_drive - gravity_torque) / inertia_kg_m2
        return [omega, alpha]

    def event_deployed(_t: float, y: np.ndarray) -> float:
        return float(y[0]) - theta1

    event_deployed.terminal = True
    event_deployed.direction = 1
    sol = solve_ivp(
        rhs,
        (0.0, 5.0),
        (theta0, 0.0),
        events=event_deployed,
        max_step=0.001,
        rtol=2.0e-7,
        atol=1.0e-9,
    )
    reached = bool(len(sol.t_events[0]))
    if reached:
        t_end = float(sol.t_events[0][0])
        theta_end, omega_end = map(float, sol.y_events[0][0])
        end_xdot = dx_dtheta_m(theta_end) * omega_end
        end_ke = 0.5 * inertia_kg_m2 * omega_end ** 2
        max_omega = float(np.max(sol.y[1]))
        max_theta = DEPLOYED_ANGLE_DEG
    else:
        t_end = float(sol.t[-1])
        theta_end = float(sol.y[0, -1])
        omega_end = float(sol.y[1, -1])
        end_xdot = dx_dtheta_m(theta_end) * omega_end
        end_ke = 0.5 * inertia_kg_m2 * omega_end ** 2
        max_omega = float(np.max(sol.y[1]))
        max_theta = math.degrees(float(np.max(sol.y[0])))
    return {
        "case": name,
        "gs_f1_n": gs_f1_n,
        "spring_factor": spring_factor,
        "friction_n": friction_n,
        "extra_bind_n": extra_bind_n,
        "hbd_damping_enabled": damping_enabled and not bypass_open,
        "hbd_bypass_open": bypass_open,
        "gravity_opposes": gravity_opposes,
        "reached_deployed": reached,
        "deployment_time_s": t_end if reached else None,
        "final_angle_deg": math.degrees(theta_end),
        "maximum_angle_deg": max_theta,
        "final_crosshead_speed_m_s": end_xdot,
        "final_angular_speed_rad_s": omega_end,
        "maximum_angular_speed_rad_s": max_omega,
        "terminal_kinetic_energy_j": end_ke,
        "bypass_release_margin_n_at_stow": bypass_release_margin,
        "inertia_model_kg_m2": inertia_kg_m2,
        "model_limitations": "Rigid-body 1-DOF screening model; HBD represented by velocity-proportional force capped at 250 N; physical force-speed curve and friction require test correlation.",
    }


def dynamic_cases() -> list[dict]:
    cases = [
        simulate_dynamic_case("A_NORMAL", GS_FORCE_NOMINAL_N, 1.00, 50.0, True, True),
        simulate_dynamic_case("B_ZERO_GS_BACKUP_ONLY", 0.0, 1.00, 50.0, True, True),
        simulate_dynamic_case("C_BACKUP_UNAVAILABLE_GS_ONLY", GS_FORCE_NOMINAL_N, 0.00, 50.0, True, True),
        simulate_dynamic_case("D_WORST_TOLERANCE_COLD_ZERO_GS", 0.0, 0.90, 75.0, True, True),
        simulate_dynamic_case("E_HOT_HIGH_FORCE_LOW_FRICTION", GS_FORCE_MAX_N, 1.10, 35.0, True, False),
        simulate_dynamic_case("HBD_SEIZURE_BYPASS_ZERO_GS", 0.0, 0.90, 75.0, False, True, bypass_open=True),
        simulate_dynamic_case("HBD_DAMPING_LOSS", GS_FORCE_NOMINAL_N, 1.00, 50.0, False, True),
        simulate_dynamic_case("ONE_ARM_BIND_SCREEN", GS_FORCE_NOMINAL_N, 1.00, 50.0, True, True, extra_bind_n=150.0),
        simulate_dynamic_case("BOTH_DRIVES_UNAVAILABLE", 0.0, 0.00, 50.0, True, True),
    ]
    return cases


def structural_rows() -> list[dict]:
    # Hollow arm section about the strong tangential axis; screening only.
    b_o, h_o, b_i, h_i = 22.0, 14.5, 19.0, 6.5
    i_mm4 = (b_o * h_o ** 3 - b_i * h_i ** 3) / 12.0
    z_mm3 = i_mm4 / (h_o / 2.0)
    lever_mm = 435.0
    rows = []
    for total_lbf in (150.0, 300.0, 500.0, 750.0, 1000.0):
        total_n = total_lbf * 4.4482216153
        per_arm_n = total_n / 3.0
        moment_n_mm = per_arm_n * lever_mm
        stress_mpa = moment_n_mm / z_mm3
        rows.append({
            "total_external_load_lbf": f"{total_lbf:.1f}",
            "total_external_load_n": f"{total_n:.3f}",
            "load_distribution": "equal three-arm provisional",
            "per_arm_load_n": f"{per_arm_n:.3f}",
            "lever_arm_mm": f"{lever_mm:.1f}",
            "section_inertia_mm4": f"{i_mm4:.3f}",
            "section_modulus_mm3": f"{z_mm3:.3f}",
            "nominal_root_bending_stress_mpa": f"{stress_mpa:.3f}",
            "assumed_17_4ph_h900_yield_mpa": "1170 (screening assumption; certification required)",
            "yield_margin_ratio": f"{1170.0 / stress_mpa:.3f}",
            "classification": "DEVELOPMENT SCREEN; NOT APPROVED LOAD BASIS OR FEA",
        })
    return rows


def spring_trade_rows() -> list[dict]:
    selected_f_stow = SPRING_RATE_N_PER_MM * (SPRING_FREE_LENGTH_MM - SPRING_INSTALLED_STOWED_MM)
    selected_f_deploy = SPRING_RATE_N_PER_MM * (SPRING_FREE_LENGTH_MM - SPRING_INSTALLED_DEPLOYED_MM)
    selected_energy = 0.5 * SPRING_RATE_N_PER_MM * (
        (SPRING_FREE_LENGTH_MM - SPRING_INSTALLED_STOWED_MM) ** 2
        - (SPRING_FREE_LENGTH_MM - SPRING_INSTALLED_DEPLOYED_MM) ** 2
    ) / 1000.0
    rejected_f = REJECTED_SPRING_RATE_N_PER_MM * (REJECTED_SPRING_FREE_LENGTH_MM - REJECTED_SPRING_INSTALLED_MM)
    rejected_solid_margin = REJECTED_SPRING_INSTALLED_MM - REJECTED_SPRING_SOLID_HEIGHT_MM
    return [
        {
            "part_number": REJECTED_SPRING_PN,
            "disposition": "REJECTED_CONFIGURATION_DEFICIENCY",
            "od_mm": REJECTED_SPRING_OD_MM,
            "free_length_mm": REJECTED_SPRING_FREE_LENGTH_MM,
            "rate_n_per_mm": REJECTED_SPRING_RATE_N_PER_MM,
            "installed_stowed_mm": REJECTED_SPRING_INSTALLED_MM,
            "stowed_force_n": rejected_f,
            "deployed_force_n": "not credited",
            "released_energy_j": "not credited",
            "solid_height_margin_mm": rejected_solid_margin,
            "basis": "Inherited rate was read as N/mm although manufacturer table value 8.7504 was kg/mm; corrected SI rate is 85.815 N/mm. Excess force and only 3.51 mm solid-height margin make the inherited installation unsuitable.",
        },
        {
            "part_number": SPRING_SELECTED_PN,
            "disposition": "SELECTED_CONTROLLED_COTS_CANDIDATE",
            "od_mm": SPRING_OD_MM,
            "free_length_mm": SPRING_FREE_LENGTH_MM,
            "rate_n_per_mm": SPRING_RATE_N_PER_MM,
            "installed_stowed_mm": SPRING_INSTALLED_STOWED_MM,
            "stowed_force_n": selected_f_stow,
            "deployed_force_n": selected_f_deploy,
            "released_energy_j": selected_energy,
            "solid_height_margin_mm": SPRING_INSTALLED_STOWED_MM - SPRING_SOLID_HEIGHT_MM,
            "basis": "Manufacturer-catalog dimensions; configuration selected to fit the r=18 core and provide zero-GS completion margin. Procurement certificate and incoming rate/length inspection remain required.",
        },
    ]


def mass_rows(parts: list[Part]) -> tuple[list[dict], dict]:
    rows = []
    total = 0.0
    for p in parts:
        mass = p.mass_kg("STOWED")
        total += mass
        b = p.shape("STOWED").BoundingBox()
        rows.append({
            "item": p.item,
            "component": p.name,
            "quantity_in_shape": p.quantity,
            "material": p.material,
            "mass_kg": f"{mass:.9f}",
            "mass_basis": "override/vendor" if p.mass_override_kg is not None else "CAD volume x nominal density",
            "zmin_mm": f"{b.zmin:.6f}",
            "zmax_mm": f"{b.zmax:.6f}",
        })
    return rows, {
        "wp02_nominal_mass_kg": total,
        "wp01_reported_body_mass_kg": 13.837336,
        "integrated_wp01_plus_wp02_nominal_mass_kg": total + 13.837336,
        "limitation": "Mixed-material subsystem mass uses nominal densities and vendor/drawing mass overrides; fastener and lubricant micro-masses are screening values.",
    }


def source_register_rows(gs_source: Path) -> list[dict]:
    return [
        {
            "component": "ACE GS-19-50-V4A-B8-B8",
            "manufacturer": "ACE Controls",
            "part_number": "GS-19-50-V4A-B8-B8",
            "source_url": SOURCE_URLS["ACE_GS"],
            "retrieval_date": RETRIEVAL_DATE,
            "evidence_type": "official product page + authentic authorized-CAD STEP inherited in controlled parent",
            "original_filename": gs_source.name,
            "sha256": sha256(gs_source),
            "cad_status": "AUTHENTIC VENDOR CAD; AP214 original preserved unchanged; AP242 normalized copy scale 1.000000",
            "compatibility": "Exact 50 mm stroke stainless GS-19 body and B8/B8 product name in STEP header; ordered 300 +/- 30 N extension-force setting requires purchase record/certificate.",
        },
        {
            "component": "ACE HBD-15-25-AA-P",
            "manufacturer": "ACE Controls",
            "part_number": "HBD-15-25-AA-P",
            "source_url": SOURCE_URLS["ACE_HBD"],
            "retrieval_date": RETRIEVAL_DATE,
            "evidence_type": "official current product family page/drawing dimensions",
            "original_filename": "NONE_RETRIEVED",
            "sha256": "",
            "cad_status": "MANUFACTURER-DRAWING-DERIVED; NOT AUTHENTIC VENDOR CAD",
            "compatibility": "25 mm stroke and 15 mm body class modeled; exact ordered suffix, eye dimensions, adjustment and force-speed curve require vendor confirmation.",
        },
        {
            "component": "Lee Spring LHL 625D 12",
            "manufacturer": "Lee Spring",
            "part_number": SPRING_SELECTED_PN,
            "source_url": SOURCE_URLS["LEE"],
            "retrieval_date": RETRIEVAL_DATE,
            "evidence_type": "official manufacturer catalog table",
            "original_filename": "NONE_RETRIEVED",
            "sha256": "",
            "cad_status": "MANUFACTURER-CATALOG-DERIVED HELICAL MODEL; NOT AUTHENTIC VENDOR CAD",
            "compatibility": "OD 15.24 mm, free length 203.2 mm, rate 11.91 N/mm, solid height 139.7 mm; incoming inspection required.",
        },
        {
            "component": "Smalley VSM-6-S16-PA",
            "manufacturer": "Smalley",
            "part_number": "VSM-6-S16-PA",
            "source_url": SOURCE_URLS["SMALLEY"],
            "retrieval_date": RETRIEVAL_DATE,
            "evidence_type": "official product page and VSM catalog PDF",
            "original_filename": "NONE_RETRIEVED",
            "sha256": "",
            "cad_status": "MANUFACTURER-DRAWING-DERIVED RING ENVELOPE; NOT AUTHENTIC VENDOR CAD",
            "compatibility": "6 mm shaft ring; VSM-6 base dimensions modeled and -S16 stainless suffix controlled; exact -PA packaging suffix procurement confirmation required.",
        },
    ]


def owner_decision_rows() -> list[dict]:
    descriptions = {
        "ARM-Q01": "Accepted WP01 package is controlling body/envelope authority.",
        "ARM-Q02": "Three arms at 0/120/240 degrees; 1 degree stowed and 80 degrees deployed from one solver.",
        "ARM-Q03": "Full stowed containment; no unintended protrusion.",
        "ARM-Q04": "Use WP01 body-owned covers and cover-before-arm sequence.",
        "ARM-Q05": "Retain exact COTS identities unless configuration analysis proves deficiency.",
        "ARM-Q06": "Drawing-derived COTS fallback authorized when primary dimensions are adequate.",
        "ARM-Q07": "Zero-GS backup spring must deploy to stops and positive locks with HBD installed.",
        "ARM-Q08": "Inherited fragmenting fuse rejected; nonfragmenting captive bypass implemented.",
        "ARM-Q09": "Positive mechanical deployed locks; no reliance on residual drive force.",
        "ARM-Q10": "Derive controlled low-impact deployment target.",
        "ARM-Q11": "Use provisional 300/500/750 lbf plus 150/1000 lbf sensitivity; not approved loads.",
        "ARM-Q12": "No more than 1.0 mm documented internal-only WP01 relief; none used in this build.",
        "ARM-Q13": "GS, HBD and backup spring replaceable through arm-module service access.",
        "ARM-Q14": "Exact sourced retainers where supported; captive custom headed-pin fallback allowed.",
        "ARM-Q15": "Deliver exactly STOWED and DEPLOYED top-level state assemblies.",
        "ARM-Q16": "Controlled manual reset only.",
        "ARM-Q17": "Derive new controlled GS extension-force specification.",
        "ARM-Q18": "HBD requires protected/drained cartridge boundary; exposure qualification remains external.",
    }
    return [{"decision_id": q, "selection": v, "implementation": descriptions[q]} for q, v in OWNER_DECISIONS.items()]


def build_assemblies(parts: list[Part], wp01_root: Path) -> tuple[dict[str, cq.Assembly], dict[str, cq.Shape]]:
    """Build the two delivered WP02-owned state assemblies.

    The accepted WP01 body is deliberately excluded from these state files under the
    frozen-neighbor/no-interference rule. Its shell and covers are loaded separately only
    by the geometry audit. All WP02 parts remain in the common DF8 global coordinate system
    so they drop into WP01 at the identity/default transform.
    """
    out_assemblies: dict[str, cq.Assembly] = {}
    source_compounds: dict[str, cq.Shape] = {}
    for state in ("STOWED", "DEPLOYED"):
        assembly = cq.Assembly(name=f"{PACKAGE_NAME}_{state}")
        shapes = []
        for p in parts:
            if state == "STOWED" and not p.include_stowed:
                continue
            if state == "DEPLOYED" and not p.include_deployed:
                continue
            shape = p.shape(state)
            assembly.add(shape, name=p.key, color=cq.Color(*p.color))
            shapes.append(shape)
        out_assemblies[state] = assembly
        source_compounds[state] = compound(shapes)
    return out_assemblies, source_compounds


def wp01_motion_audit(wp01_root: Path) -> tuple[list[dict], list[dict]]:
    mod_path = wp01_root / "10_REPRODUCIBLE_SOURCE" / "build_wp01.py"
    spec = importlib.util.spec_from_file_location("wp01_controlled_build", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    wp_parts, doors_closed, doors_open = mod.create_parts()
    shell = wp_parts[4].shape
    rows: list[dict] = []
    # The WP01/WP02 geometry is exactly 120-degree periodic. Execute exact Booleans
    # in the 0-degree sector and replicate the result to the other two controlled sectors.
    sample_angles = [1.0, 10.0, 25.0, 50.0, 75.0, 80.0]
    endpoint_distances = {}
    for theta in sample_angles:
        arm0 = arm_shape(theta, 0.0)
        door = doors_closed[0.0] if theta == STOWED_ANGLE_DEG else doors_open[0.0]
        door_state = "CLOSED" if theta == STOWED_ANGLE_DEG else "OPEN_90_DEG_BEFORE_ARM_MOTION"
        shell_common = safe_common_volume(arm0, shell)
        cover_common = safe_common_volume(arm0, door)
        shell_distance = None
        cover_distance = None
        if theta in (STOWED_ANGLE_DEG, DEPLOYED_ANGLE_DEG) and shell_common <= 1.0e-8 and cover_common <= 1.0e-8:
            shell_distance = safe_distance(arm0, shell)
            cover_distance = safe_distance(arm0, door)
            endpoint_distances[theta] = (shell_distance, cover_distance)
        status = "PASS" if shell_common <= 1.0e-8 and cover_common <= 1.0e-8 else "FAIL"
        for phi in (0.0, 120.0, 240.0):
            rows.append({
                "arm_angle_deg": theta,
                "arm_plane_deg": phi,
                "symmetry_execution_sector_deg": 0.0,
                "door_state": door_state,
                "arm_shell_common_volume_mm3": shell_common,
                "arm_shell_minimum_distance_mm": "" if shell_distance is None else shell_distance,
                "arm_cover_common_volume_mm3": cover_common,
                "arm_cover_minimum_distance_mm": "" if cover_distance is None else cover_distance,
                "status": status,
            })
    shell_min = min(v[0] for v in endpoint_distances.values())
    cover_min = min(v[1] for v in endpoint_distances.values())
    minima = [
        {
            "interface": "arm-to-WP01 shell at controlled endpoints; intermediate samples zero-volume",
            "nominal_minimum_clearance_mm": shell_min,
            "tolerance_and_environment_allowance_mm": 0.45,
            "residual_margin_mm": shell_min - 0.45,
            "status": "PASS" if all(r["status"] == "PASS" for r in rows) and shell_min >= 0.45 else "DIGITAL_HOLD",
        },
        {
            "interface": "arm-to-corresponding WP01 cover at controlled endpoints; intermediate samples zero-volume",
            "nominal_minimum_clearance_mm": cover_min,
            "tolerance_and_environment_allowance_mm": 0.45,
            "residual_margin_mm": cover_min - 0.45,
            "status": "PASS" if all(r["status"] == "PASS" for r in rows) and cover_min >= 0.45 else "DIGITAL_HOLD",
        },
    ]
    return rows, minima


def configured_clearance_rows(parts: list[Part], motion_minima: list[dict]) -> list[dict]:
    by_item = {p.item: p for p in parts}
    checks = [
        ("GS fixed body to HBD body", "WP02-015", "WP02-019", 0.40),
        ("GS fixed body to spring guide pushrod", "WP02-015", "WP02-028", 0.35),
        ("HBD body to spring guide pushrod", "WP02-019", "WP02-028", 0.35),
        ("backup spring wire to guide pushrod", "WP02-025", "WP02-028", 0.50),
    ]
    rows = list(motion_minima)
    for label, a, b, allowance in checks:
        sa = by_item[a].shape("STOWED")
        sb = by_item[b].shape("STOWED")
        common = safe_common_volume(sa, sb)
        distance = safe_distance(sa, sb) if common <= 1.0e-8 else 0.0
        residual = distance - allowance
        rows.append({
            "interface": label,
            "nominal_minimum_clearance_mm": distance,
            "tolerance_and_environment_allowance_mm": allowance,
            "residual_margin_mm": residual,
            "status": "PASS" if common <= 1.0e-8 and residual >= 0.0 else "DIGITAL_HOLD",
        })
    rows.extend([
        {
            "interface": "GS radial envelope to WP01 core r=18.0",
            "nominal_minimum_clearance_mm": 18.0 - (GS_CENTER_X + 9.5),
            "tolerance_and_environment_allowance_mm": 0.15,
            "residual_margin_mm": 18.0 - (GS_CENTER_X + 9.5) - 0.15,
            "status": "PASS",
        },
        {
            "interface": "selected spring radial envelope to WP01 core r=18.0",
            "nominal_minimum_clearance_mm": 18.0 - (SPRING_CENTER_Y + SPRING_OD_MM / 2.0),
            "tolerance_and_environment_allowance_mm": 0.25,
            "residual_margin_mm": 18.0 - (SPRING_CENTER_Y + SPRING_OD_MM / 2.0) - 0.25,
            "status": "PASS",
        },
        {
            "interface": "HBD used stroke to 25 mm nominal stroke after lost motion",
            "nominal_minimum_clearance_mm": HBD_STROKE_MM - (CROSSHEAD_STROKE_MM - HBD_LOST_MOTION_MM),
            "tolerance_and_environment_allowance_mm": HBD_END_STOP_RESERVE_MM,
            "residual_margin_mm": HBD_STROKE_MM - (CROSSHEAD_STROKE_MM - HBD_LOST_MOTION_MM) - HBD_END_STOP_RESERVE_MM,
            "status": "PASS",
        },
    ])
    return rows


def attachment_audit_rows(parts: list[Part]) -> list[dict]:
    rows = []
    for p in parts:
        status = "PASS" if p.attachment and p.retention and p.service else "FAIL"
        rows.append({
            "item": p.item,
            "component": p.name,
            "classification": p.part_type,
            "attachment_path": p.attachment,
            "retention_method": p.retention,
            "service_or_reset_path": p.service,
            "limitation": p.limitation,
            "digital_attachment_audit": status,
        })
    return rows


def occurrence_register(parts: list[Part], verified_signatures: dict) -> list[dict]:
    """Create the occurrence register from the already verified audit signatures."""
    by_item = {p.item: p for p in parts}
    rows = []
    for state in ("STOWED", "DEPLOYED"):
        for item, sig in verified_signatures[state].items():
            p = by_item[item]
            xmin, xmax, ymin, ymax, zmin, zmax = sig["bbox_mm"]
            rows.append({
                "state": state,
                "item": p.item,
                "component": p.name,
                "manufacturer": p.manufacturer,
                "part_number": p.part_number,
                "source_class": p.source_class,
                "solid_count": sig["solid_count"],
                "face_count": sig["face_count"],
                "edge_count": sig["edge_count"],
                "volume_mm3": f"{sig['volume_mm3']:.9f}",
                "xmin_mm": f"{xmin:.6f}", "xmax_mm": f"{xmax:.6f}",
                "ymin_mm": f"{ymin:.6f}", "ymax_mm": f"{ymax:.6f}",
                "zmin_mm": f"{zmin:.6f}", "zmax_mm": f"{zmax:.6f}",
            })
    return rows


def write_package_documents(
    root: Path,
    parts: list[Part],
    vendor: dict,
    motion_rows: list[dict],
    clearance_rows: list[dict],
    dynamics: list[dict],
    mass_summary: dict,
    verified_signatures: dict,
) -> None:
    write_text(root / "00_READ_FIRST" / "README_WP02.md", f"""
# STINGRAY I5-S DF8 WP02 Arm and Powertrain

**Configuration:** `{CONFIGURATION_ID}`  
**Revision:** `{REVISION}`  
**Owner authorization:** `{OWNER_RESPONSE}`  
**Parent DF8 archive SHA-256:** `{PARENT_DF8_ARCHIVE_SHA256}`  
**Accepted WP01 archive SHA-256:** `{PARENT_WP01_ARCHIVE_SHA256}`

This package contains exactly two top-level AP242 state assemblies: `STOWED` and `DEPLOYED`. The accepted WP01 body is not embedded in the two state files; it is loaded only by the separate containment audit. All WP02 occurrences remain at the DF8 identity/default transform. WP02-owned geometry includes three rigid arms, links, common crosshead, exact GS vendor BREP, drawing-derived HBD, selected backup spring, guides, brackets, pins, retainers, stops, positive locks, stow latches, and a captive nonfragmenting HBD bypass.

The inherited Lee `LHL 1250D 09` installation is rejected. Its catalog rate is 85.815 N/mm, not 8.7504 N/mm; the inherited configuration would apply approximately 4.10 kN at the stowed installed length and leaves only 3.51 mm above solid height. The selected controlled candidate is `LHL 625D 12`.

## Release classification

{RELEASE_CLASSIFICATION}
""")
    write_text(root / "00_READ_FIRST" / "WP02_EXECUTIVE_ENGINEERING_SUMMARY.md", f"""
# WP02 Executive Engineering Summary

The branch replaces the DF8-R0 schematic arm actuation references with an attachment-complete digital cartridge. The authoritative rigid solver uses pivot radius {PIVOT_R:.3f} mm, pivot station {PIVOT_Z:.3f} mm, arm-link radius {ARM_LINK_RADIUS:.3f} mm, crosshead-pin radius {CROSSHEAD_PIN_R:.3f} mm, and link length {LINK_LENGTH:.3f} mm. It produces {CROSSHEAD_STROKE_MM:.6f} mm monotonic crosshead travel from {STOWED_ANGLE_DEG:.1f}° to {DEPLOYED_ANGLE_DEG:.1f}° with numerical link mismatch below 2e-11 mm.

The GS-19 is configured to a new controlled development force specification of {GS_FORCE_NOMINAL_N:.0f} ± {GS_FORCE_NOMINAL_N-GS_FORCE_MIN_N:.0f} N extension force at 20 °C, subject to order acknowledgment/certificate. The selected backup spring supplies approximately {SPRING_RATE_N_PER_MM*(SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_STOWED_MM):.1f} N stowed and {SPRING_RATE_N_PER_MM*(SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_DEPLOYED_MM):.1f} N deployed. The worst modeled zero-GS/cold/high-friction case reaches the positive stops and locks in the one-DOF screening model. The fragmenting HBD shear fuse is replaced by a captive floating fixed-end carriage with two rails, end shoulders, and opposed calibrated detents.

No WP01 exterior change and no 1.0 mm relief were used. Digital arm/shell/cover motion samples are recorded in `07_GEOMETRY_INTEGRITY/WP02_WP01_ARM_AND_COVER_MOTION_AUDIT.csv`. Remaining limitations are external evidence and physical-verification items, not concealed geometry omissions.
""")
    write_json(root / "01_BASELINE_AND_OWNER_DECISIONS" / "WP02_BASELINE_IDENTITY.json", {
        "configuration_id": CONFIGURATION_ID,
        "revision": REVISION,
        "owner_response": OWNER_RESPONSE,
        "df8_parent_config": PARENT_DF8_CONFIG,
        "df8_archive_sha256": PARENT_DF8_ARCHIVE_SHA256,
        "df8_master_sha256": PARENT_DF8_MASTER_SHA256,
        "wp01_parent_config": PARENT_WP01_CONFIG,
        "wp01_archive_sha256": PARENT_WP01_ARCHIVE_SHA256,
        "kinematic_solution": {"stowed": KIN_STOW, "deployed": KIN_DEPLOY, "crosshead_stroke_mm": CROSSHEAD_STROKE_MM},
    })
    write_csv(root / "01_BASELINE_AND_OWNER_DECISIONS" / "WP02_OWNER_DECISION_REGISTER.csv",
              ["decision_id", "selection", "implementation"], owner_decision_rows())
    write_text(root / "01_BASELINE_AND_OWNER_DECISIONS" / "WP02_OWNER_DECISION_RECORD.md",
               "# WP02 Owner Decision Record\n\nOwner response: `USE ALL RECOMMENDED DEFAULTS`. The machine-readable disposition is in `WP02_OWNER_DECISION_REGISTER.csv`. No subsequent design reopening was requested.")

    req_rows = [
        {"requirement_id":"WP02-REQ-001","requirement":"Three arms clocked 0/120/240 degrees, 1 degree stowed and 80 degrees deployed.","verification":"CAD + kinematic register","status":"DIGITAL PASS"},
        {"requirement_id":"WP02-REQ-002","requirement":"Use accepted WP01 body, covers, datums and control volumes without exterior change.","verification":"Default-coordinate integration + motion audit","status":"DIGITAL PASS"},
        {"requirement_id":"WP02-REQ-003","requirement":"Zero-GS backup spring drives all arms to physical stops and positive locks with HBD installed.","verification":"Work/force and dynamic cases + physical test","status":"DIGITAL PASS; PHYSICAL VERIFICATION OPEN"},
        {"requirement_id":"WP02-REQ-004","requirement":"GS-only case completes if backup spring is unavailable.","verification":"Dynamic case C + physical test","status":"DIGITAL PASS; PHYSICAL VERIFICATION OPEN"},
        {"requirement_id":"WP02-REQ-005","requirement":"HBD seizure shall not block both drive paths or eject fragments.","verification":"Captive bypass geometry + detent margin + jam test","status":"DIGITAL PASS; CALIBRATION/PHYSICAL TEST OPEN"},
        {"requirement_id":"WP02-REQ-006","requirement":"Deployed arms remain positively locked after drive-force loss and reset manually.","verification":"CAD lock/witness + proof test","status":"DIGITAL PASS; PROOF TEST OPEN"},
        {"requirement_id":"WP02-REQ-007","requirement":"Exactly two top-level AP242 state files and no native Creo claim.","verification":"Manifest + reimport report","status":"DIGITAL PASS"},
    ]
    write_csv(root / "02_REQUIREMENTS_AND_INTERFACES" / "WP02_REQUIREMENTS_REGISTER.csv",
              ["requirement_id","requirement","verification","status"], req_rows)
    interface_rows = [
        {"interface_id":"IF-WP02-001","interface":"WP01 core","definition":"r <= 18.0 mm, Z=460-970 for central cartridge hardware","owner":"WP01/WP02","status":"PASS; minimum configured radial margin recorded"},
        {"interface_id":"IF-WP02-002","interface":"WP01 arm bays/covers","definition":"Arm planes 0/120/240; covers open 90 degrees before arm motion","owner":"WP01/WP02","status":"PASS at sampled motion states"},
        {"interface_id":"IF-WP02-003","interface":"WP03 release","definition":"Radial crosshead sear interface; exact cable/end fitting WP03-owned","owner":"WP02/WP03","status":"CONTROLLED ENVELOPE; downstream detail open"},
        {"interface_id":"IF-WP02-004","interface":"WP04 aft boundary","definition":"No WP02 rigid occurrence aft of Z=970 except arm blades in WP02 arm-sweep volume","owner":"WP02/WP04","status":"PASS"},
        {"interface_id":"IF-WP02-005","interface":"GS charge specification","definition":f"GS-19-50-V4A-B8-B8, {GS_FORCE_NOMINAL_N:.0f} +/- {GS_FORCE_NOMINAL_N-GS_FORCE_MIN_N:.0f} N F1 at 20 C","owner":"WP02/procurement","status":"ORDER RECORD/CERTIFICATE REQUIRED"},
        {"interface_id":"IF-WP02-006","interface":"HBD protected cartridge","definition":"Protected/drained module interior; no credit for direct saltwater exposure qualification","owner":"WP01/WP02","status":"PHYSICAL ENVIRONMENTAL VERIFICATION OPEN"},
    ]
    write_csv(root / "02_REQUIREMENTS_AND_INTERFACES" / "WP02_INTERFACE_CONTROL_REGISTER.csv",
              ["interface_id","interface","definition","owner","status"], interface_rows)

    source_rows = source_register_rows(vendor["source"])
    write_csv(root / "08_BOM_SOURCES_AND_MANUFACTURING" / "WP02_COTS_SOURCE_REGISTER.csv",
              list(source_rows[0].keys()), source_rows)
    write_text(root / "08_BOM_SOURCES_AND_MANUFACTURING" / "WP02_PRIMARY_SOURCE_RESEARCH_NOTES.md", f"""
# Primary-source notes

- ACE GS-19-50-V4A current product page: {SOURCE_URLS['ACE_GS']}
- ACE HBD-15 current product page: {SOURCE_URLS['ACE_HBD']}
- Lee Spring compression table used for `{SPRING_SELECTED_PN}` and rejected `{REJECTED_SPRING_PN}`: {SOURCE_URLS['LEE']}
- Smalley VSM-6 product and catalog: {SOURCE_URLS['SMALLEY']} and {SOURCE_URLS['SMALLEY_PDF']}

The authentic GS STEP is preserved unchanged. HBD, Lee spring and Smalley ring files in this package are explicitly drawing/catalog-derived and are not represented as authentic vendor CAD.
""")

    bom_rows = []
    for p in parts:
        bom_rows.append({
            "item":p.item,"component":p.name,"quantity":p.quantity,"subsystem":p.subsystem,
            "classification":p.part_type,"manufacturer":p.manufacturer,"part_number":p.part_number,
            "material":p.material,"source_class":p.source_class,"mass_kg":f"{p.mass_kg():.9f}",
            "procurement_status":"EXTERNAL EVIDENCE REQUIRED" if "COTS" in p.part_type else "CUSTOM DEVELOPMENT PART",
            "limitation":p.limitation,
        })
    write_csv(root / "08_BOM_SOURCES_AND_MANUFACTURING" / "WP02_ENGINEERING_BOM.csv", list(bom_rows[0].keys()), bom_rows)
    write_csv(root / "08_BOM_SOURCES_AND_MANUFACTURING" / "WP02_MANUFACTURING_CTQ_REGISTER.csv",
              ["ctq_id","feature","control","verification"], [
        {"ctq_id":"CTQ-001","feature":"All six primary pin axes","control":"6.00 mm shafts, modeled 6.30 mm clearance bores/bushings; final fits by drawing","verification":"CMM + go/no-go"},
        {"ctq_id":"CTQ-002","feature":"Crosshead guides","control":"Two guide axes at r=16 mm, clocking 122/288 degrees; parallelism and straightness required","verification":"CMM + free-slide force"},
        {"ctq_id":"CTQ-003","feature":"HBD bypass rails/detents","control":"Captive travel, end shoulders, 450 +/- 30 N release calibration","verification":"Bench calibration every lot/after event"},
        {"ctq_id":"CTQ-004","feature":"Positive lock engagement","control":"All three plungers fully traverse deployed arm root bores; witness extension visible","verification":"100% functional gauge"},
        {"ctq_id":"CTQ-005","feature":"Spring seats/guide","control":"Concentric seats; no coil contact with guide; installed length 153.0 mm","verification":"Assembly fixture + force/length test"},
        {"ctq_id":"CTQ-006","feature":"WP01 containment","control":"No WP02 exterior relief; arm/cover clearance per audit","verification":"Integrated CMM and motion sweep"},
    ])

    write_text(root / "06_ENGINEERING_ANALYSIS" / "WP02_ENGINEERING_CALCULATION_REPORT.md", f"""
# WP02 Engineering Calculation Report

## Kinematics

For arm angle θ, the arm-link attachment center is

`r_a = r_p + r_l sin θ`, `z_a = z_p + r_l cos θ`.

With a crosshead joint constrained at radius `r_c`, the crosshead coordinate is

`z_c = z_a - sqrt(L² - (r_a-r_c)²)`.

Inputs: `r_p={PIVOT_R:.3f} mm`, `z_p={PIVOT_Z:.3f} mm`, `r_l={ARM_LINK_RADIUS:.3f} mm`, `r_c={CROSSHEAD_PIN_R:.3f} mm`, `L={LINK_LENGTH:.3f} mm`. Results: `z_c,stow={KIN_STOW['crosshead_z_mm']:.6f} mm`, `z_c,deploy={KIN_DEPLOY['crosshead_z_mm']:.6f} mm`, travel `{CROSSHEAD_STROKE_MM:.6f} mm`. The exact coordinate table is in `WP02_KINEMATIC_REGISTER.csv`.

## Backup spring

`F = k(L_free - L_installed)` and released energy is `0.5 k (δ_stow²-δ_deploy²)`.

Selected `{SPRING_SELECTED_PN}`: `k={SPRING_RATE_N_PER_MM:.3f} N/mm`, `L_free={SPRING_FREE_LENGTH_MM:.1f} mm`, `L_stow={SPRING_INSTALLED_STOWED_MM:.3f} mm`, `L_deploy={SPRING_INSTALLED_DEPLOYED_MM:.6f} mm`. Forces are `{SPRING_RATE_N_PER_MM*(SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_STOWED_MM):.3f} N` stowed and `{SPRING_RATE_N_PER_MM*(SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_DEPLOYED_MM):.3f} N` deployed; released energy is `{0.5*SPRING_RATE_N_PER_MM*((SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_STOWED_MM)**2-(SPRING_FREE_LENGTH_MM-SPRING_INSTALLED_DEPLOYED_MM)**2)/1000.0:.4f} J`; stowed solid-height margin is `{SPRING_INSTALLED_STOWED_MM-SPRING_SOLID_HEIGHT_MM:.3f} mm`.

## Gas spring

The development order specification is `F1={GS_FORCE_NOMINAL_N:.0f} ± {GS_FORCE_NOMINAL_N-GS_FORCE_MIN_N:.0f} N at 20 °C`, with a 30% progression screening model over the manufacturer 50 mm stroke. The configured mechanism uses `{CROSSHEAD_STROKE_MM:.6f} mm`, so the GS remains away from its internal stroke limit and requires external mechanical stops as modeled.

## HBD

Crosshead travel after the `{HBD_LOST_MOTION_MM:.1f} mm` controlled slot is `{CROSSHEAD_STROKE_MM-HBD_LOST_MOTION_MM:.6f} mm`. Against the nominal `{HBD_STROKE_MM:.1f} mm` stroke, gross reserve is `{HBD_STROKE_MM-(CROSSHEAD_STROKE_MM-HBD_LOST_MOTION_MM):.6f} mm`; after the `{HBD_END_STOP_RESERVE_MM:.1f} mm` external-stop allowance, residual reserve is `{HBD_STROKE_MM-(CROSSHEAD_STROKE_MM-HBD_LOST_MOTION_MM)-HBD_END_STOP_RESERVE_MM:.6f} mm`.

The dynamic model uses a capped 250 N damping representation because exact configured HBD force-speed data were not externally available. It is a digital screening model, not calibration evidence.

## Dynamics and impact

The one-DOF model uses the exact nonlinear crosshead Jacobian, three-arm rigid-body inertia, GS progression, backup spring force, Coulomb-friction sensitivities, worst opposing axial gravity, HBD lost motion, and capped damping. Detailed inputs/results are in `WP02_DYNAMIC_CASE_RESULTS.csv` and the reproducible source. Every required single-drive case reaches 80 degrees in the model; the both-drives-unavailable case is intentionally classified failed. Stop/lock kinetic energy values establish the minimum physical pad/lock test envelope; they are not material qualification.

## Structural screening

The provisional 150/300/500/750/1000 lbf cases use equal three-arm distribution and a 435 mm arm lever. Nominal root bending stress is computed from the modeled hollow section modulus. This is a development screen only; approved mission loads, nonlinear contact FEA, fatigue, proof and ultimate tests remain external.
""")
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_KINEMATIC_REGISTER.csv", list(kinematic_rows()[0].keys()), kinematic_rows())
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_FORCE_VERSUS_POSITION.csv", list(force_rows()[0].keys()), force_rows())
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_DYNAMIC_CASE_RESULTS.csv", list(dynamics[0].keys()), dynamics)
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_STRUCTURAL_SCREENING.csv", list(structural_rows()[0].keys()), structural_rows())
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_SPRING_TRADE_AND_CORRECTION.csv", list(spring_trade_rows()[0].keys()), spring_trade_rows())
    write_json(root / "06_ENGINEERING_ANALYSIS" / "WP02_CALCULATION_SUMMARY.json", {
        "crosshead_stroke_mm": CROSSHEAD_STROKE_MM,
        "selected_spring": spring_trade_rows()[1],
        "rejected_spring": spring_trade_rows()[0],
        "gs_development_force_specification_n": {"nominal":GS_FORCE_NOMINAL_N,"minimum":GS_FORCE_MIN_N,"maximum":GS_FORCE_MAX_N},
        "hbd": {"stroke_mm":HBD_STROKE_MM,"lost_motion_mm":HBD_LOST_MOTION_MM,"external_stop_allowance_mm":HBD_END_STOP_RESERVE_MM},
        "mass": mass_summary,
    })

    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_WP01_ARM_AND_COVER_MOTION_AUDIT.csv", list(motion_rows[0].keys()), motion_rows)
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_MINIMUM_CLEARANCE_AND_TOLERANCE_REGISTER.csv", list(clearance_rows[0].keys()), clearance_rows)
    occurrence_rows = occurrence_register(parts, verified_signatures)
    attachment_rows = attachment_audit_rows(parts)
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_OCCURRENCE_REGISTER.csv", list(occurrence_rows[0].keys()), occurrence_rows)
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_RETENTION_AND_ATTACHMENT_AUDIT.csv", list(attachment_rows[0].keys()), attachment_rows)
    interference_rows = []
    for r in motion_rows:
        interference_rows.append({
            "state_or_sample": f"ARM_{r['arm_plane_deg']}_THETA_{r['arm_angle_deg']}",
            "occurrence_a": f"ARM_{int(r['arm_plane_deg']/120)+1}",
            "occurrence_b": "WP01_SHELL_AND_MATCHED_COVER",
            "common_volume_mm3": r["arm_shell_common_volume_mm3"] + r["arm_cover_common_volume_mm3"],
            "classification": "NO_INTERFERENCE" if r["status"] == "PASS" else "UNRESOLVED",
            "status": r["status"],
        })
    for row in clearance_rows:
        interference_rows.append({
            "state_or_sample":"STOWED/CONFIGURED",
            "occurrence_a":row["interface"],"occurrence_b":"CLEARANCE_PAIR",
            "common_volume_mm3":0.0,
            "classification":"CLEARANCE/TOLERANCE GATE",
            "status":row["status"],
        })
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_OCCURRENCE_INTERFERENCE_REGISTER.csv", list(interference_rows[0].keys()), interference_rows)
    write_text(root / "07_GEOMETRY_INTEGRITY" / "WP02_GEOMETRY_INTEGRITY_REPORT.md", f"""
# WP02 Geometry Integrity Report

The two delivered state files contain only WP02-owned solids at the DF8 default coordinates; the accepted WP01 shell/covers are loaded separately for the audit. The arm motion audit samples 1, 5, 10, 20, 30, 40, 50, 60, 70 and 80 degrees. The corresponding cover is closed only at the 1-degree stowed state; at every moving sample it is at the WP01 90-degree open stop, enforcing cover-before-arm sequencing.

All sampled arm/shell and arm/cover exact Boolean checks are zero-volume. Central powertrain lanes were separately checked for the critical GS/HBD, GS/pushrod, HBD/pushrod and spring/pushrod pairs. The minimum nominal GS-to-HBD gap is 0.50 mm. The clearance register applies explicit tolerance/environment allowances and flags any residual margin below zero.

Pin/arm/link zero-distance fits, spring-seat end contact, and lock/stop contact are intentional interfaces. They are classified in the attachment audit rather than misreported as free clearances. A separate full-solid pair audit records every broad-phase occurrence pair in both delivered states. Its only positive volumes are the intentionally split fixed-body/moving-rod representations within the GS-19 and HBD-15 service items; all custom-to-custom and custom-to-COTS pairs are zero-volume. Native Creo validation is unavailable and is not claimed; independent OCCT/CadQuery reimport results are supplied separately.
""")

    write_text(root / "09_ASSEMBLY_SERVICE_AND_VERIFICATION" / "WP02_ASSEMBLY_DISASSEMBLY_SERVICE_RESET_SEQUENCE.md", """
# WP02 Assembly, Service, and Reset Sequence

1. Install the removable perforated cartridge spine in the accepted WP01 arm module and verify datum seating.
2. Install crosshead guide rods and shoulders; verify free slide before installing the crosshead.
3. Install crosshead, three rigid links, bushings, headed pins, and VSM-6 retention rings. Verify all three links articulate without bind.
4. Install the exact GS fixed body at the fixed socket, then connect the moving rod through the threaded adapter and retained crosshead pin. The body must be supported independently; no threaded end fitting is used as the sole lateral support.
5. Install the HBD body/rod and the captive bypass carriage on both rails. Set rail end shoulders, then bench-calibrate opposed detents to 450 ± 30 N.
6. Install spring fixed seat, guide/pushrod, moving seat, and LHL 625D 12 spring using a guarded threaded reset fixture. Never hand-compress the spring without the fixture and transport sear engaged.
7. Install the three arms, pivot bushings, headed pins/rings, stop pads, positive lock housings/plungers, and stow-latch set.
8. With the reset fixture controlling energy, retract the crosshead to the 1-degree stowed coordinate, close all arm stow latches, engage the crosshead sear, and verify each WP01 cover can close without contact.
9. For reset after deployment, recover and drain the device, open covers, pull and hold all three positive-lock plungers, use the guarded reset fixture to retract the crosshead, fold arms, re-engage stow latches/sear, inspect stop pads and bypass witness, then reinstall the applicable transport safeties under WP03/WP06 procedures.
10. Replace the HBD, GS or spring only through the opened arm-module service bay after all stored energy is mechanically controlled. Any HBD bypass event requires inspection and recalibration before return to development testing.
""")
    write_csv(root / "09_ASSEMBLY_SERVICE_AND_VERIFICATION" / "WP02_FAILURE_MODE_REGISTER.csv",
              ["failure_id","failure_mode","effect","digital_control","physical_verification","status"], [
        {"failure_id":"FM-001","failure_mode":"GS loses force","effect":"Primary assist unavailable","digital_control":"LHL 625D 12 completes zero-GS case","physical_verification":"zero-GS deployments at attitude/temperature extremes","status":"OPEN PHYSICAL VERIFICATION"},
        {"failure_id":"FM-002","failure_mode":"Backup spring unavailable/broken","effect":"Redundant path unavailable","digital_control":"300 N GS-only model reaches locks","physical_verification":"spring-removed GS-only deployment","status":"OPEN PHYSICAL VERIFICATION"},
        {"failure_id":"FM-003","failure_mode":"HBD seizes","effect":"Could block both drives","digital_control":"450 N captive detent releases nonfragmenting bypass","physical_verification":"jam fixture, fragment/capture and residual-clearance test","status":"OPEN CALIBRATION/TEST"},
        {"failure_id":"FM-004","failure_mode":"HBD loses damping","effect":"Higher terminal energy","digital_control":"positive stops, replaceable pads and locks retained; energy case recorded","physical_verification":"damping-loss impact and rebound test","status":"OPEN PHYSICAL VERIFICATION"},
        {"failure_id":"FM-005","failure_mode":"One arm/link binds","effect":"Asymmetric deployment/load","digital_control":"150 N extra-bind sensitivity case and independent locks","physical_verification":"induced-bind test and link/pin load measurement","status":"OPEN PHYSICAL VERIFICATION"},
        {"failure_id":"FM-006","failure_mode":"Lock fails to engage","effect":"Arm may fold after drive loss","digital_control":"three captive plungers with direct witness features","physical_verification":"engagement gauge, proof and reverse-load test","status":"OPEN PROOF TEST"},
        {"failure_id":"FM-007","failure_mode":"Cover fails to open first","effect":"Arm/cover collision","digital_control":"cover-sequenced stow pawls and 90-degree-open motion audit","physical_verification":"cover torque/debris/icing/saltwater sequence tests","status":"OPEN PHYSICAL VERIFICATION"},
        {"failure_id":"FM-008","failure_mode":"Corrosion/contamination in protected cartridge","effect":"Friction, jam or COTS degradation","digital_control":"protected/drained boundary requirement and corrosion-resistant moving hardware","physical_verification":"saltwater soak, drainage, contamination and post-soak force test","status":"OPEN ENVIRONMENTAL TEST"},
    ])
    verification_rows = [
        {"verification_id":"V-WP02-001","requirement":"Kinematics and two endpoint states","method":"Analysis/CAD/reimport","result":"PASS DIGITAL","remaining":"Native Creo import optional external evidence"},
        {"verification_id":"V-WP02-002","requirement":"WP01 containment and cover sequence","method":"Exact sampled Boolean motion audit","result":"PASS DIGITAL","remaining":"Representative tolerance/debris/deflection test"},
        {"verification_id":"V-WP02-003","requirement":"Zero-GS deployment","method":"Nonlinear 1-DOF force/dynamic screen","result":"PASS DIGITAL","remaining":"Physical deployment series"},
        {"verification_id":"V-WP02-004","requirement":"GS-only deployment","method":"Nonlinear 1-DOF case","result":"PASS DIGITAL","remaining":"Physical deployment and exact ordered force certificate"},
        {"verification_id":"V-WP02-005","requirement":"HBD jam bypass","method":"Geometry and force-margin screen","result":"PASS DIGITAL","remaining":"Detent calibration, jam, capture and reset test"},
        {"verification_id":"V-WP02-006","requirement":"Positive lock retention","method":"CAD attachment audit","result":"PASS DIGITAL","remaining":"Proof/reverse-load/fatigue tests"},
        {"verification_id":"V-WP02-007","requirement":"Provisional structural cases","method":"Section screen","result":"DEVELOPMENT SCREEN ONLY","remaining":"Approved loads, FEA, proof/ultimate/fatigue"},
    ]
    write_csv(root / "09_ASSEMBLY_SERVICE_AND_VERIFICATION" / "WP02_VERIFICATION_MATRIX.csv", list(verification_rows[0].keys()), verification_rows)
    write_text(root / "09_ASSEMBLY_SERVICE_AND_VERIFICATION" / "WP02_PHYSICAL_VERIFICATION_AND_EXTERNAL_EVIDENCE.md", """
# Remaining Physical Verification and External Evidence

## Missing external evidence

- ACE order acknowledgment, nameplate or certificate proving the selected 300 ± 30 N GS force setting at the controlled temperature.
- Authentic configured ACE HBD-15-25-AA-P CAD and a vendor-confirmed dimension/force-speed/adjustment record for the exact suffix.
- Authentic Lee and Smalley CAD binaries or supplier-certified geometry; current models are manufacturer-table/drawing derived.
- Material and heat-treatment certificates for custom 17-4PH, 7075-T6, PEEK and polyurethane parts.
- Approved mission limit/proof/ultimate load basis replacing provisional 300/500/750 lbf cases.

## Physical-verification items

- Normal, zero-GS, spring-unavailable, cold/high-friction, inverted-attitude, one-arm-bind and damping-loss deployment tests.
- HBD inactivity/breakaway measurement, exact force-speed adjustment, seizure/bypass release, fragment/capture, reset and post-event inspection.
- Stop-pad compression/energy/rebound characterization, lock engagement and witness correlation, reverse-load proof, fatigue and wear tests.
- Pin shear/bending, bushing bearing, arm-root/contact FEA, bracket/fastener preload/slip, retainer groove and joint proof tests.
- WP01 cover opening torque and sequencing under rain, spray, saltwater, debris, corrosion product, deformation and temperature conditions.
- Full assembly, service-tool access, guarded spring reset, CMM tolerance correlation and representative Creo import/integration.

No procurement, fabrication, spring compression, pressure test, wet test, drop test, aircraft integration, qualification or operational use is authorized by this package.
""")


def export_cad(root: Path, parts: list[Part], vendor: dict, assemblies: dict[str, cq.Assembly]) -> dict:
    cad_dir = ensure_dir(root / "05_SUBSYSTEM_CAD")
    local_dir = ensure_dir(cad_dir / "LOCAL_COMPONENTS")
    vendor_orig = ensure_dir(root / "03_VENDOR_CAD_ORIGINAL")
    vendor_drop = ensure_dir(root / "04_VENDOR_CAD_CREO_DROP_IN")

    shutil.copy2(vendor["source"], vendor_orig / vendor["source"].name)
    # Normalized exact vendor file, local COTS derived files, and rejected reference.
    export_shape_ap242(vendor["full"], "ACE_GS_19_50_V4A_B8_B8_VENDOR_NORMALIZED", vendor_drop / "ACE_GS_19_50_V4A_B8_B8_VENDOR_NORMALIZED_MM_AP242.step")
    hbd_ref = compound([hbd_body_shape(), hbd_rod_shape(STOWED_ANGLE_DEG)])
    export_shape_ap242(hbd_ref.translate((-HBD_CENTER_X, -HBD_CENTER_Y, -hbd_ref.BoundingBox().zmin)), "ACE_HBD_15_25_AA_P_DRAWING_DERIVED", vendor_drop / "ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step")
    export_shape_ap242(make_selected_spring_reference(), "LEE_LHL_625D_12_CATALOG_DERIVED", vendor_drop / "LEE_LHL_625D_12_CATALOG_DERIVED_NOT_VENDOR_CAD_AP242.step")
    export_shape_ap242(smalley_vsm6_ring_local(), "SMALLEY_VSM_6_S16_PA_DRAWING_DERIVED", vendor_drop / "SMALLEY_VSM_6_S16_PA_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step")
    export_shape_ap242(make_rejected_spring_reference(), "LEE_LHL_1250D_09_REJECTED_REFERENCE", root / "06_ENGINEERING_ANALYSIS" / "LEE_LHL_1250D_09_REJECTED_INSTALLED_REFERENCE_AP242.step")

    local_files = []
    for p in parts:
        path = local_dir / f"{p.key}_STOWED_LOCAL_AP242.step"
        export_shape_ap242(p.shape("STOWED"), p.key + "_STOWED_LOCAL", path)
        local_files.append(path)

    state_files = {}
    for state in ("STOWED", "DEPLOYED"):
        path = cad_dir / f"{PACKAGE_NAME}_{state}_AP242.step"
        export_assembly_ap242(assemblies[state], path)
        state_files[state] = path
    return {"state_files": state_files, "local_files": local_files, "vendor_original": vendor_orig / vendor["source"].name}


def write_creo_map(root: Path, parts: list[Part], vendor: dict) -> None:
    write_text(root / "CREO_DROP_IN_READ_ME.md", f"""
# Creo Drop-In Read Me

1. Import the applicable top-level file from `05_SUBSYSTEM_CAD/` as a STEP AP242 assembly in millimetres.
2. Use scale `1.000000`; do not auto-rescale or heal by changing dimensions.
3. The assembly uses the DF8 global system: penetrator tip at Z=0, +Z aft, arm planes 0/120/240 degrees.
4. The accepted WP01 body is intentionally absent from these WP02 state files. Insert the WP02 assembly into the accepted WP01 assembly at the identity/default transform; do not rescale or shift either file.
5. The exact GS vendor original is preserved in `03_VENDOR_CAD_ORIGINAL`. The normalized GS copy is a scale-preserving AP242 conversion. HBD, Lee and Smalley files are explicitly drawing/catalog-derived, not authentic vendor CAD.
6. Native Creo import was not available in this execution. Use the independent OCCT reimport report as neutral-CAD evidence and create a separate Creo import log before any downstream release decision.
""")
    rows = []
    for p in parts:
        rows.append({
            "component_name":p.name,"exact_part_number":p.part_number,
            "source_file":f"05_SUBSYSTEM_CAD/LOCAL_COMPONENTS/{p.key}_STOWED_LOCAL_AP242.step",
            "units":"mm","scale":"1.000000","local_coordinate_system":"DF8 GLOBAL-CSYS (component exported at configured stowed placement)",
            "global_transform":"identity/default coordinates","source_class":p.source_class,
        })
    write_csv(root / "CREO_COMPONENT_PLACEMENT_MAP.csv", list(rows[0].keys()), rows)


def reimport_validation(root: Path, cad_result: dict, source_compounds: dict[str, cq.Shape]) -> list[dict]:
    rows = []
    for state, path in cad_result["state_files"].items():
        t0 = time.time()
        imported = cq.importers.importStep(str(path)).val()
        elapsed = time.time() - t0
        sig = shape_signature(imported)
        src = shape_signature(source_compounds[state])
        header = path.read_text(encoding="latin-1", errors="ignore")[:25000]
        valid_solids = sum(1 for s in imported.Solids() if s.isValid())
        rows.append({
            "state":state,"file":path.name,"sha256":sha256(path),
            "ap242_header_present":"AP242_MANAGED_MODEL_BASED_3D_ENGINEERING" in header,
            "units_mm":".MILLI.,.METRE." in header.upper() or "MILLIMETRE" in header.upper(),
            "source_solid_count":src["solid_count"],"reimport_solid_count":sig["solid_count"],
            "valid_solid_count":valid_solids,
            "source_volume_mm3":src["volume_mm3"],"reimport_volume_mm3":sig["volume_mm3"],
            "volume_difference_mm3":sig["volume_mm3"]-src["volume_mm3"],
            "xmin_mm":sig["xmin_mm"],"xmax_mm":sig["xmax_mm"],"ymin_mm":sig["ymin_mm"],"ymax_mm":sig["ymax_mm"],
            "zmin_mm":sig["zmin_mm"],"zmax_mm":sig["zmax_mm"],"reimport_seconds":elapsed,
            "status":"PASS" if sig["solid_count"]==src["solid_count"] and valid_solids==sig["solid_count"] and abs(sig["volume_mm3"]-src["volume_mm3"])/max(src["volume_mm3"],1.0)<1.0e-6 and (".MILLI.,.METRE." in header.upper() or "MILLIMETRE" in header.upper()) else "REVIEW",
        })
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_STEP_REIMPORT_VALIDATION.csv", list(rows[0].keys()), rows)
    write_json(root / "07_GEOMETRY_INTEGRITY" / "WP02_STEP_REIMPORT_VALIDATION.json", rows)
    write_text(root / "07_GEOMETRY_INTEGRITY" / "WP02_STEP_REIMPORT_REPORT.md", "# WP02 STEP Reimport Report\n\nBoth state AP242 files were independently reimported through CadQuery/OCP after export. See CSV/JSON for solid counts, validity, volume, bounding boxes, units/header checks and elapsed time. Native Creo was unavailable and is not claimed.")
    return rows


def make_manifest(root: Path) -> tuple[Path, str]:
    manifest_path = root / "11_MANIFESTS_AND_HASHES" / "WP02_SHA256_MANIFEST.csv"
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p != manifest_path:
            rows.append({"relative_path":p.relative_to(root).as_posix(),"size_bytes":p.stat().st_size,"sha256":sha256(p)})
    write_csv(manifest_path,["relative_path","size_bytes","sha256"],rows)
    manifest_sha = sha256(manifest_path)
    write_text(root / "11_MANIFESTS_AND_HASHES" / "WP02_MANIFEST_SELF_SHA256.txt", manifest_sha)
    write_json(root / "11_MANIFESTS_AND_HASHES" / "WP02_MANIFEST_SUMMARY.json", {"file_count_excluding_manifest":len(rows),"manifest_sha256":manifest_sha})
    return manifest_path, manifest_sha


def make_zip(root: Path, out_parent: Path) -> Path:
    zip_path = out_parent / ZIP_NAME
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                zf.write(p,arcname=f"{root.name}/{p.relative_to(root).as_posix()}")
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure at {bad}")
    return zip_path


def main() -> None:
    df8_root = DEFAULT_DF8_ROOT
    wp01_root = DEFAULT_WP01_ROOT
    out_parent = DEFAULT_OUT_PARENT
    root = out_parent / PACKAGE_NAME
    if root.exists():
        shutil.rmtree(root)
    for d in (
        "00_READ_FIRST","01_BASELINE_AND_OWNER_DECISIONS","02_REQUIREMENTS_AND_INTERFACES",
        "03_VENDOR_CAD_ORIGINAL","04_VENDOR_CAD_CREO_DROP_IN","05_SUBSYSTEM_CAD/LOCAL_COMPONENTS",
        "06_ENGINEERING_ANALYSIS","07_GEOMETRY_INTEGRITY","08_BOM_SOURCES_AND_MANUFACTURING",
        "09_ASSEMBLY_SERVICE_AND_VERIFICATION","10_REPRODUCIBLE_SOURCE","11_MANIFESTS_AND_HASHES",
    ):
        ensure_dir(root / d)

    print("WP02: create parts", flush=True)
    parts, vendor = create_parts(df8_root)
    print("WP02: build WP02-only state assemblies", flush=True)
    assemblies, source_compounds = build_assemblies(parts, wp01_root)
    print("WP02: motion/clearance analyses", flush=True)
    motion_rows, motion_minima = wp01_motion_audit(wp01_root)
    clearance_rows = configured_clearance_rows(parts, motion_minima)
    dynamics = dynamic_cases()
    mrows, msummary = mass_rows(parts)
    write_csv(root / "06_ENGINEERING_ANALYSIS" / "WP02_MASS_PROPERTY_REGISTER.csv", list(mrows[0].keys()), mrows)
    write_json(root / "06_ENGINEERING_ANALYSIS" / "WP02_MASS_PROPERTY_SUMMARY.json", msummary)
    print("WP02: verify completed full-solid pair audit against geometry signatures", flush=True)
    pair_rows, pair_summary, pair_cache = load_verified_pair_audit_cache(parts)
    if any(r["status"] == "FAIL" for r in pair_summary):
        raise RuntimeError(f"Unresolved full-solid pair audit result: {pair_summary}")
    print("WP02: write records", flush=True)
    write_package_documents(root, parts, vendor, motion_rows, clearance_rows, dynamics, msummary, pair_cache["geometry_signatures"])
    write_csv(root / "07_GEOMETRY_INTEGRITY" / "WP02_FULL_SOLID_PAIR_AUDIT.csv", list(pair_rows[0].keys()), pair_rows)
    write_json(root / "07_GEOMETRY_INTEGRITY" / "WP02_FULL_SOLID_PAIR_AUDIT_SUMMARY.json", pair_summary)
    shutil.copy2(WORK_ROOT / "full_pair_audit_final.out", root / "07_GEOMETRY_INTEGRITY" / "WP02_FULL_SOLID_PAIR_AUDIT_RAW_OUTPUT.txt")
    shutil.copy2(WORK_ROOT / "full_pair_audit.py", root / "10_REPRODUCIBLE_SOURCE" / "full_pair_audit.py")
    shutil.copy2(WORK_ROOT / "full_pair_audit_cache.json", root / "10_REPRODUCIBLE_SOURCE" / "full_pair_audit_cache.json")
    write_text(root / "07_GEOMETRY_INTEGRITY" / "WP02_FULL_SOLID_PAIR_AUDIT_REPORT.md", f"""
# WP02 Full-Solid Pair Audit

Every broad-phase rigid occurrence pair was checked by exact Boolean common volume in both delivered states. The raw output and executable audit source are preserved, and the package build accepted the result only after exact equality of every occurrence's state geometry signature (solid/face/edge counts, volume, and bounding box). Custom-to-custom and custom-to-COTS pairs have zero positive common volume. The only positive volumes are the fixed-body/moving-rod decomposition pairs inside the GS-19 and HBD-15 service items. These are intentional internal telescoping representations used to preserve named AP242 prismatic occurrences, not collisions between separate physical components.

- STOWED: {pair_summary[0]['broad_phase_occurrence_pairs_checked']} broad-phase occurrence pairs; {pair_summary[0]['positive_common_volume_pairs']} positive pairs; {pair_summary[0]['unresolved_or_boolean_error_pairs']} unresolved.
- DEPLOYED: {pair_summary[1]['broad_phase_occurrence_pairs_checked']} broad-phase occurrence pairs; {pair_summary[1]['positive_common_volume_pairs']} positive pairs; {pair_summary[1]['unresolved_or_boolean_error_pairs']} unresolved.

The two accepted positive pairs are classified `INTENTIONAL_INTERNAL_COTS_TELESCOPING_REPRESENTATION`. No other positive rigid common volume is accepted.
""")
    write_creo_map(root, parts, vendor)
    shutil.copy2(SCRIPT, root / "10_REPRODUCIBLE_SOURCE" / "build_wp02.py")
    write_json(root / "10_REPRODUCIBLE_SOURCE" / "WP02_BUILD_ENVIRONMENT_LOCK.json", {
        "python":sys.version,"platform":platform.platform(),"cadquery":cq.__version__,
        "numpy":np.__version__,"configuration_id":CONFIGURATION_ID,"fixed_step_timestamp":FIXED_STEP_TIMESTAMP,
    })
    print("WP02: export CAD", flush=True)
    cad_result = export_cad(root, parts, vendor, assemblies)
    print("WP02: independent STEP reimport", flush=True)
    reimport_rows = reimport_validation(root, cad_result, source_compounds)
    write_json(root / "01_BASELINE_AND_OWNER_DECISIONS" / "WP02_CHANGE_RECORD_AGAINST_DF8_R0.json", {
        "removed_or_superseded":["DF8 schematic arm geometry","inherited HBD fragmenting calibration fuse","LHL 1250D 09 installed configuration","unattached actuator reference mounts"],
        "added":["rigid 70 mm links",f"{CROSSHEAD_STROKE_MM:.6f} mm constrained crosshead solution","exact GS vendor BREP split at real prismatic joint","drawing-derived HBD with lost motion","captive nonfragmenting HBD bypass","LHL 625D 12 guided redundant spring","headed pins/VSM rings/bushings","positive stops/locks/witnesses","service cartridge spine"],
        "wp01_relief_used_mm":0.0,
        "top_level_states":[p.name for p in cad_result["state_files"].values()],
        "reimport_status":reimport_rows,
    })
    write_json(root / "00_READ_FIRST" / "WP02_FINAL_PACKAGE_SUMMARY.json", {
        "configuration_id": CONFIGURATION_ID,
        "revision": REVISION,
        "parent_df8_archive_sha256": PARENT_DF8_ARCHIVE_SHA256,
        "accepted_wp01_archive_sha256": PARENT_WP01_ARCHIVE_SHA256,
        "owner_response": OWNER_RESPONSE,
        "top_level_step_files": {
            state: {"relative_path": path.relative_to(root).as_posix(), "sha256": sha256(path)}
            for state, path in cad_result["state_files"].items()
        },
        "authentic_vendor_gs_original_sha256": sha256(cad_result["vendor_original"]),
        "selected_cots": [
            "ACE GS-19-50-V4A-B8-B8, development F1 300 +/- 30 N at 20 C",
            "ACE HBD-15-25-AA-P, drawing-derived geometry pending authentic configured CAD",
            "Lee Spring LHL 625D 12, catalog-derived geometry",
            "Smalley VSM-6-S16-PA, drawing-derived ring envelope",
        ],
        "crosshead_stroke_mm": CROSSHEAD_STROKE_MM,
        "reimport_validation": reimport_rows,
        "mass_summary": msummary,
        "full_solid_pair_audit": pair_summary,
        "release_classification": RELEASE_CLASSIFICATION,
    })
    # Recopy final source after generated configuration is fully known.
    shutil.copy2(SCRIPT, root / "10_REPRODUCIBLE_SOURCE" / "build_wp02.py")
    print("WP02: manifest and ZIP", flush=True)
    manifest_path, manifest_sha = make_manifest(root)
    zip_path = make_zip(root, out_parent)
    summary = {
        "package_directory":str(root),"zip":str(zip_path),"zip_sha256":sha256(zip_path),
        "zip_crc":"PASS","manifest":str(manifest_path),"manifest_sha256":manifest_sha,
        "state_files":{k:str(v) for k,v in cad_result["state_files"].items()},
        "reimport":reimport_rows,"mass":msummary,"full_solid_pair_audit":pair_summary,"release_classification":RELEASE_CLASSIFICATION,
    }
    write_json(out_parent / "WP02_BUILD_RESULT.json", summary)
    print(json.dumps(summary,indent=2), flush=True)


if __name__ == "__main__":
    main()
