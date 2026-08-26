#!/usr/bin/env python3
"""Create the evidence-backed maximum-complete product-definition reports.

This generator never upgrades unavailable vendor, mission-load, manufacturing,
or physical-test evidence to PASS.  It reads the frozen SHORT14 candidate and
its fresh validation outputs and writes the documentation layer used by the
final handoff package.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "short14_external_buoy"
OUT = ROOT / "work" / "complete_product_definition"
VALIDATION = SOURCE / "validation"
TODAY = date(2026, 8, 26)
STATUS = (
    "MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR "
    "FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE"
)

STOWED_STEP = SOURCE / "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step"
DEPLOYED_STEP = SOURCE / "STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step"
STOWED_INVENTORY = SOURCE / "authoring_inventory_stowed.json"
DEPLOYED_INVENTORY = SOURCE / "authoring_inventory_deployed.json"
MASS_PATH = SOURCE / "FINAL_MASS_CG_INERTIA.json"
ENDPOINT_PATH = VALIDATION / "endpoints" / "endpoint_validation_summary.json"
FIVE_PATH = (
    VALIDATION
    / "complete_product_definition_five_angle"
    / "five_angle_exact_boolean_summary.json"
)
FULL_PATH = (
    VALIDATION
    / "complete_product_definition_full_motion"
    / "full_motion_exact_boolean_summary.json"
)

SCREENSHOTS = [
    "96caba30-c2bd-4a17-b248-81ee3559dc4b.png",
    "b802781b-9a00-4332-8f65-b17b5ecf0d56.png",
    "8f568847-8298-4476-9075-19cdddbffe68.png",
    "faecb194-4586-4b54-8db3-35a258be47d1.png",
    "903443cc-222f-4c0b-816d-e5d2dc8afc1b.png",
    "1580eb42-bd8c-4640-a70e-e86d40090dd9.png",
    "27ea92db-2d39-41af-80eb-56af5a3498ee.png",
    "31a1a846-287b-442a-af1b-061c9d5c3e0b.png",
    "098fa2cc-0d1f-48f1-b46c-45b246bc5795.png",
    "07f8923d-f301-46ff-a68a-02ac5f0fb590.png",
    "555709a4-6918-4673-920b-2ef43ce1e828.png",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=False))


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
    ensure_dir(path.parent)
    if not rows and fields is None:
        raise ValueError(f"Cannot infer fields for empty CSV: {path}")
    selected = list(fields or rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=selected, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def gas_capacity() -> dict[str, float]:
    mass_g = 12.0
    molar_mass_g_per_mol = 44.0095
    gas_constant = 8.31446261815324
    ambient_pressure_pa = 101325.0
    buoy_l = 60.0
    moles = mass_g / molar_mass_g_per_mol

    def liters(temperature_k: float) -> float:
        return moles * gas_constant * temperature_k / ambient_pressure_pa * 1000.0

    nominal_l = liters(293.15)
    cold_l = liters(273.15)
    hot_l = liters(318.15)
    required_mass_g = (
        buoy_l
        / 1000.0
        * ambient_pressure_pa
        * molar_mass_g_per_mol
        / (gas_constant * 293.15)
    )
    return {
        "cartridge_mass_g": mass_g,
        "molar_mass_g_per_mol": molar_mass_g_per_mol,
        "moles": moles,
        "cold_0c_ideal_volume_l": cold_l,
        "nominal_20c_ideal_volume_l": nominal_l,
        "hot_45c_ideal_volume_l": hot_l,
        "buoy_nominal_volume_l": buoy_l,
        "nominal_fraction": nominal_l / buoy_l,
        "nominal_deficit_l": buoy_l - nominal_l,
        "ideal_required_mass_g_at_20c": required_mass_g,
        "ideal_mass_deficit_g_at_20c": required_mass_g - mass_g,
    }


def bbox_text(occurrence: dict[str, Any]) -> str:
    box = occurrence.get("global_bbox_mm", {})
    if not box:
        return "NOT DETERMINABLE"
    return (
        f"X {fmt(float(box['xmin']), 3)}..{fmt(float(box['xmax']), 3)} mm; "
        f"Y {fmt(float(box['ymin']), 3)}..{fmt(float(box['ymax']), 3)} mm; "
        f"Z {fmt(float(box['zmin']), 3)}..{fmt(float(box['zmax']), 3)} mm"
    )


def group_occurrences(inventory: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for occurrence in inventory["occurrences"]:
        grouped[occurrence["part_number"]].append(occurrence)
    return grouped


def make_bom_and_design_basis(stowed: dict[str, Any], deployed: dict[str, Any]) -> None:
    bom_dir = ensure_dir(OUT / "03_BOM_AND_REGISTERS")
    stowed_occ = group_occurrences(stowed)
    deployed_occ = group_occurrences(deployed)
    part_rows: list[dict[str, Any]] = []
    materials: list[dict[str, Any]] = []
    basis_rows: list[dict[str, Any]] = []
    procurement: list[dict[str, Any]] = []
    cots: list[dict[str, Any]] = []
    included_articulation_children = {
        "GS-19-50-V4A-B8-B8-ROD-CHILD": "GS-19-50-V4A-B8-B8",
        "HBD-15-25-AA-P-ROD-CHILD": "HBD-15-25-AA-P",
    }

    web_overrides = {
        "LELAND-81121": {
            "url": "https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas",
            "evidence": (
                "Official Leland page: 81121, puncture type, non-refillable, 3/8-24 UNF, "
                "12 g CO2, 3.250 in long, 0.735 in diameter; dimensional statements are referential."
            ),
        },
        "HALKEY-ROBERTS-HYDRO-1F-V95000XXB_PROXY": {
            "url": "https://fluid-components.nordsonmedical.com/Products/Inflation-Products/",
            "evidence": (
                "Official Nordson/Halkey-Roberts page identifies Hydro 1F V95000, 3/8 or 1/2 in "
                "cylinder-thread families, V80040 bobbin, service parts, and 1F recognition. "
                "The installed suffix and exact vendor CAD remain uncontrolled."
            ),
        },
        "V80040": {
            "url": (
                "https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/"
                "Technical%20Information/HRC/Hyrdo-1F-Manual-Automatic-Inflator-V80040-Bobbin-"
                "Instructions-For-Use.pdf"
            ),
            "evidence": (
                "Official V80040 IFU: water-sensitive bobbin intended for Halkey-Roberts products; "
                "orientation, storage, lot/date, and replacement controls apply."
            ),
        },
        "GS-19-50-V4A-B8-B8": {
            "url": (
                "https://www.acecontrols.com/us/products/motion-control/industrial-gas-springs-push-type/"
                "gs-8-v4a-to-gs-40-va/gs-19-v4a.html"
            ),
            "evidence": (
                "Official ACE family page: GS-19-50-V4A has 50 mm stroke, 164 mm extended length, "
                "and configurable force; exact delivered force and B8/B8 configuration require order control."
            ),
        },
        "HBD-15-25-AA-P": {
            "url": (
                "https://www.acecontrols.com/us/products/motion-control/hydraulic-dampers/"
                "hbd-15-to-hbd-40/hbd-15.html"
            ),
            "evidence": (
                "Official ACE family page: HBD-15-25 has 25 mm nominal stroke and 145 mm extended length; "
                "final AA-P suffix interfaces and setting require controlled order data."
            ),
        },
    }

    for part in sorted(stowed["parts"], key=lambda row: row["part_number"]):
        part_number = part["part_number"]
        occurrences = stowed_occ.get(part_number, [])
        deployed_occurrences = deployed_occ.get(part_number, [])
        quantity_stowed = len(occurrences)
        quantity_deployed = len(deployed_occurrences)
        common = {
            "part_number": part_number,
            "physical_title": part.get("final_display_name", ""),
            "description": part.get("description", ""),
            "revision": part.get("revision", ""),
            "make_buy": part.get("make_buy", ""),
            "manufacturer": part.get("manufacturer", ""),
            "quantity_stowed": quantity_stowed,
            "quantity_deployed": quantity_deployed,
            "material": part.get("material", ""),
            "finish": part.get("finish", ""),
            "mass_each_kg": part.get("mass_kg", ""),
            "cad_classification": part.get("cad_classification", ""),
            "source_url": part.get("source_url", ""),
            "purchase_url": part.get("purchase_url", ""),
            "process": part.get("process", ""),
            "notes": part.get("notes", ""),
            "verification_status": (
                "NON-RELEASE - EXACT VENDOR GEOMETRY/RATED APPLICATION NOT CONTROLLED"
                if part.get("cad_classification") == "DIMENSION_CONTROLLED_PROXY"
                else "DIGITAL DEFINITION PRESENT; RELEASE QUALIFICATION NOT ESTABLISHED"
            ),
        }
        part_rows.append(common)
        materials.append(
            {
                "part_number": part_number,
                "physical_title": part.get("final_display_name", ""),
                "material": part.get("material", ""),
                "finish": part.get("finish", ""),
                "process_or_heat_treatment": part.get("process", ""),
                "environmental_compatibility": "REQUIRES MATERIAL/FINISH AND SUBMERGENCE QUALIFICATION",
                "evidence": part.get("notes", ""),
                "release_status": "NOT RELEASED",
            }
        )
        location_rows = occurrences or deployed_occurrences
        locations = sorted(
            {
                f"{occ.get('display_parent_path', occ.get('parent_path', ''))}/"
                f"{occ.get('display_name', occ['occurrence_id'])}: {bbox_text(occ)}"
                for occ in location_rows
            }
        )
        interfaces = sorted(
            {
                f"{occ.get('joint_type', 'UNKNOWN')} (DOF {occ.get('permitted_dof', 'UNKNOWN')})"
                for occ in location_rows
            }
        )
        basis_rows.append(
            {
                "component_name": part.get("final_display_name", part_number),
                "part_number": part_number,
                "function": part.get("description", ""),
                "quantity": max(quantity_stowed, quantity_deployed),
                "exact_location": " | ".join(locations),
                "selection_basis": part.get("notes", "") or part.get("process", ""),
                "location_orientation_basis": "Occurrence transform and named parent path in both authoring inventories.",
                "load_pressure_travel_environment_requirement": (
                    "See connection register, motion-track register, and analysis applicability matrix; "
                    "unpublished mission loads remain NOT CALCULABLE."
                ),
                "rating_or_calculated_capacity": (
                    web_overrides.get(part_number, {}).get("evidence", "NOT DETERMINABLE FROM CONTROLLED INPUTS")
                ),
                "interface_and_attachment": " | ".join(interfaces),
                "clearances": "Endpoint and 0-80 degree exact-Boolean registers; occurrence-specific margin not otherwise stated.",
                "tolerance_requirements": "REQUIRES RELEASE DRAWING OR SUPPLIER DRAWING; NOT RELEASED",
                "assembly_access": "Modeled access only; physical tool-access verification required.",
                "service_reset_access": "See assembly/service/reset instructions; physical trial required.",
                "material_compatibility": part.get("material", "") + "; " + part.get("finish", ""),
                "mass_cg_effect": f"{part.get('mass_kg', 'UNKNOWN')} kg each; exact occurrence allocation in mass report.",
                "applicable_analysis": "Mass, motion/interference, interface, environment, manufacturing; additional load analysis as applicable.",
                "evidence": part.get("source_url", "") or part.get("notes", ""),
                "verification_status": common["verification_status"],
            }
        )
        included_parent = included_articulation_children.get(part_number)
        procurement.append(
            {
                "part_number": part_number,
                "description": part.get("description", ""),
                "make_buy": part.get("make_buy", ""),
                "manufacturer": part.get("manufacturer", ""),
                "quantity_per_product": 0 if included_parent else max(quantity_stowed, quantity_deployed),
                "orderable_configuration": (
                    f"INCLUDED IN PARENT ASSEMBLY {included_parent}"
                    if included_parent
                    else "INCOMPLETE" if part_number in web_overrides and "PROXY" in part_number else part_number
                ),
                "purchase_authority": "NOT AUTHORIZED",
                "qualification_status": "NOT QUALIFIED",
                "source": part.get("purchase_url", "") or part.get("source_url", ""),
                "action": (
                    "NO SEPARATE PURCHASE; CONTROL CONFIGURATION AND QUALIFICATION WITH PARENT ASSEMBLY"
                    if included_parent
                    else "Obtain controlled quote/drawing/CoC and complete application qualification"
                    if part.get("make_buy") == "BUY"
                    else "Create and approve fabrication drawing after design release"
                ),
            }
        )
        if part.get("make_buy") == "BUY":
            override = web_overrides.get(part_number, {})
            cots.append(
                {
                    "part_number": part_number,
                    "manufacturer": part.get("manufacturer", ""),
                    "catalog_name": part.get("description", ""),
                    "quantity": 0 if included_parent else max(quantity_stowed, quantity_deployed),
                    "cad_classification": part.get("cad_classification", ""),
                    "official_source": override.get("url", part.get("source_url", "")),
                    "current_verification_date": TODAY.isoformat() if override else "REPOSITORY EVIDENCE - NOT LIVE-REFRESHED",
                    "evidence_summary": override.get("evidence", part.get("notes", "")),
                    "exact_geometry_status": (
                        "NO - DIMENSION-CONTROLLED PROXY"
                        if part.get("cad_classification") == "DIMENSION_CONTROLLED_PROXY"
                        else "DRAWING-DERIVED OR ANALYTIC; SEE SOURCE AND INCOMING INSPECTION"
                    ),
                    "application_rating_status": "NOT QUALIFIED FOR THIS INSTALLATION",
                    "procurement_status": "NO PURCHASE AUTHORIZED",
                }
            )

    write_csv(bom_dir / "FULL_BOM.csv", part_rows)
    write_csv(bom_dir / "MATERIALS_AND_FINISHES_REGISTER.csv", materials)
    write_csv(bom_dir / "COMPONENT_DESIGN_BASIS_MATRIX.csv", basis_rows)
    write_csv(bom_dir / "PROCUREMENT_REGISTER.csv", procurement)
    write_csv(bom_dir / "COTS_PROVENANCE_REGISTER.csv", cots)
    write_text(
        bom_dir / "MAKE_BUY_TRADE_STUDY.md",
        f"""# MAKE/BUY Trade Study

Status: **{STATUS}**

## Result

The frozen digital configuration contains **{sum(1 for row in part_rows if row['make_buy'] == 'BUY')} BUY**
and **{sum(1 for row in part_rows if row['make_buy'] == 'MAKE')} MAKE** unique definitions.  The selected
buoy/inflation architecture is therefore not a completed COTS-heavy module.  The Hydro 1F installed
configuration remains a dimension-controlled proxy and its completed suffix, exact installed geometry,
rated interface, and 60 L application compatibility are not controlled.

The current geometry remains the maximum-complete digital baseline because no complete, orderable,
source-supported commercial module has been shown to satisfy the modeled installation and inflation
requirements.  This decision is not procurement, qualification, or acceptance authority.

## Selection hierarchy applied

1. Exact compliant catalog module - **no passing module established**.
2. Configurable catalog module - **Hydro 1F family identified; installed configuration incomplete**.
3. Standard commercial hardware - retained where source-backed.
4. Minor commercial modification - not authorized without supplier/application evidence.
5. Custom articles - retained only as developmental digital definitions and marked not released.

## Release consequence

The design cannot pass COTS accuracy, gas capacity, pressure-interface, procurement, or fabrication
gates.  Additional vendor evidence and an architecture correction are required before detailed release
drawings or procurement can be authorized.
""",
    )


def analysis_rows(gas: dict[str, float]) -> list[dict[str, str]]:
    rows = [
        ("Stored-gas sizing", "REQUIRED", "FAIL", "12 g CO2 ideal-gas upper bound is far below the modeled 60 L buoy."),
        ("CO2 phase and temperature behavior", "REQUIRED", "NOT CALCULABLE", "Ideal-gas bounding screen completed; two-phase blowdown and delivered mass require vendor/test data."),
        ("Required inflation volume", "REQUIRED", "FAIL", "Modeled nominal volume is 60 L; cartridge supports only a small fraction at ambient pressure."),
        ("Regulator behavior", "NOT REQUIRED", "NOT APPLICABLE", "Current compact inflator topology has no separate regulator."),
        ("Pressure loss and flow", "REQUIRED", "NOT CALCULABLE", "Hydro 1F internal flow path/orifice and buoy back-pressure curve are not controlled."),
        ("Cylinder force and travel", "NOT REQUIRED", "NOT APPLICABLE", "No pneumatic deployment cylinder remains in the current architecture."),
        ("Mechanical spring force and energy", "REQUIRED", "PARTIAL", "Gas-spring family and motion geometry are known; delivered force tolerance and mission loads remain uncontrolled."),
        ("Gas-spring or damper behavior", "REQUIRED", "PARTIAL", "Stroke/envelope are controlled; damping setting, thermal behavior, and cycle verification require supplier/test evidence."),
        ("Mechanism kinematics", "REQUIRED", "PASS - DIGITAL", "0-80 degree one-degree kinematics completed with exact closure residual reporting."),
        ("Mechanical advantage", "REQUIRED", "NOT CALCULABLE", "Input/output load requirements are not supplied; geometry alone is insufficient."),
        ("Deployment time and dynamics", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Static kinematics cannot establish dynamic deployment time, damping, or water loads."),
        ("Arm strength and stiffness", "REQUIRED", "NOT CALCULABLE", "Material/geometry exist but controlling arm loads and duty spectrum are absent."),
        ("Pin, latch, lock, stop, and retainer loads", "REQUIRED", "NOT CALCULABLE", "Connection inventory exists; controlling load cases are absent."),
        ("Fastener strength and thread engagement", "REQUIRED", "NOT CALCULABLE", "Fastener identities exist; complete joint loads, preload, and release drawings are absent."),
        ("Impact and handling loads", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "No controlled drop/impact requirement or qualification result is available."),
        ("Stowed retention", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Digital attachment continuity exists; retention force and environmental tests remain open."),
        ("Deployed locking", "REQUIRED", "PARTIAL", "Digital stop/contact registry passes; physical engagement and load retention remain open."),
        ("Buoyancy and reserve buoyancy", "REQUIRED", "PARTIAL", "Gross 60 L displacement is calculable; delivered gas and mission load requirements fail/remain unknown."),
        ("Flotation orientation and stability", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Hydrostatic orientation and sea-state stability have no controlled acceptance evidence."),
        ("Mass, center of gravity, and inertia", "REQUIRED", "PASS - DIGITAL", "Exact occurrence-weighted report generated for both states."),
        ("Softgood extraction and inflation", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Open/closed states modeled; folds, seams, breakaway, and wet inflation require tests."),
        ("Pressure ratings and margins", "REQUIRED", "NOT CALCULABLE", "Exact installed inflator suffix and application rating are not controlled."),
        ("Hose and tubing motion", "NOT REQUIRED", "NOT APPLICABLE", "Current compact direct inflator topology contains no hose/tube route objects."),
        ("Fitting compatibility", "REQUIRED", "FAIL", "Cartridge is 3/8-24; Hydro family supports variants, but installed suffix is incomplete."),
        ("Leakage and sealing", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "O-rings/gaskets are supplier service items; installed leak result is unavailable."),
        ("Tolerance stacks", "REQUIRED", "NOT CALCULABLE", "Digital nominal geometry passes; release drawing tolerances and supplier distributions are absent."),
        ("Wear and fatigue", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Duty spectrum, cycle target, and physical endurance data are absent."),
        ("Corrosion and galvanic compatibility", "REQUIRED", "PARTIAL", "Materials/finishes are registered; installed mixed-material qualification is absent."),
        ("Environmental exposure", "REQUIRED", "DEFERRED TO PHYSICAL VERIFICATION", "Temperature, salt, UV, humidity, contamination, and storage tests remain open."),
        ("Assembly and tool access", "REQUIRED", "PARTIAL", "Digital access is reviewable; physical assembly trial and released tooling/torque data are absent."),
        ("Service and reset", "REQUIRED", "PARTIAL", "Supplier rearm sequence and digital access are documented; installed reset demonstration is absent."),
        ("Manufacturability", "REQUIRED", "NOT CALCULABLE", "No released drawings, GD&T, process capability, or supplier review exists."),
        ("Failure modes and single-point failures", "REQUIRED", "PARTIAL", "FMEA generated; critical gas-capacity and activation-chain findings remain open."),
        ("Complete motion and interference", "REQUIRED", "PASS - DIGITAL", "Endpoint, five-angle, and full one-degree exact-Boolean gates pass."),
    ]
    return [
        {
            "analysis": name,
            "classification": classification,
            "completion_status": completion,
            "justification": justification,
            "evidence": "05_ANALYSES/TECHNICAL_ANALYSIS_REPORT.md",
        }
        for name, classification, completion, justification in rows
    ]


def make_analysis_reports(
    stowed: dict[str, Any],
    deployed: dict[str, Any],
    mass: dict[str, Any],
    endpoint: dict[str, Any],
    five: dict[str, Any],
    full: dict[str, Any],
) -> None:
    analysis_dir = ensure_dir(OUT / "05_ANALYSES")
    gas = gas_capacity()
    rows = analysis_rows(gas)
    write_csv(analysis_dir / "ANALYSIS_APPLICABILITY_MATRIX.csv", rows)
    write_json(analysis_dir / "STORED_GAS_INDEPENDENT_CALCULATION.json", gas)

    stowed_mass = mass["short14_stowed"]
    deployed_mass = mass["short14_deployed"]
    seawater_density = 1025.0
    gross_buoyant_mass_kg = 0.060 * seawater_density
    gas_table = "\n".join(
        [
            "| Condition | Ideal volume from 12 g CO2 | Fraction of 60 L |",
            "|---|---:|---:|",
            f"| 0 C | {gas['cold_0c_ideal_volume_l']:.3f} L | {gas['cold_0c_ideal_volume_l']/60:.1%} |",
            f"| 20 C | {gas['nominal_20c_ideal_volume_l']:.3f} L | {gas['nominal_fraction']:.1%} |",
            f"| 45 C | {gas['hot_45c_ideal_volume_l']:.3f} L | {gas['hot_45c_ideal_volume_l']/60:.1%} |",
        ]
    )
    report = f"""# Technical Analysis Report

Status: **{STATUS}**

Configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`

Frozen candidate hashes:

- STOWED AP242: `{sha256(STOWED_STEP)}`
- DEPLOYED AP242: `{sha256(DEPLOYED_STEP)}`
- STOWED inventory: `{sha256(STOWED_INVENTORY)}`
- DEPLOYED inventory: `{sha256(DEPLOYED_INVENTORY)}`

## 1. Scope and acceptance discipline

This report completes calculations that can be supported by the delivered geometry and controlled
manufacturer evidence.  It does not infer missing mission loads, proprietary inflator internals,
release tolerances, application ratings, or physical performance.  `NOT CALCULABLE`, `PARTIAL`, and
`DEFERRED TO PHYSICAL VERIFICATION` are release-blocking where the analysis is required.

## 2. Stored-gas capacity - FAIL

### Purpose

Screen whether the selected Leland 81121 12 g CO2 cartridge can supply the modeled 60 L buoy.

### Source-backed inputs

| Input | Value | Source |
|---|---:|---|
| CO2 mass | 12.000 g | Leland 81121 official product page |
| CO2 molar mass | 44.0095 g/mol | Standard molecular property |
| Buoy nominal volume | 60.000 L | Frozen CAD/configuration report |
| Ambient pressure | 101,325 Pa | Calculation reference condition |
| Temperature range | 0-45 C | Hydro 1F published air/water range bounds used for screen |

### Equations and substituted values

Moles:

`n = m / M = 12.000 g / 44.0095 g/mol = {gas['moles']:.6f} mol`

Optimistic ideal-gas volume at ambient pressure:

`V = n R T / P`

At 20 C:

`V = {gas['moles']:.6f} mol x 8.314462618 J/(mol K) x 293.15 K / 101325 Pa`

`V = {gas['nominal_20c_ideal_volume_l']:.3f} L`

{gas_table}

Ideal CO2 mass required for 60 L at 20 C and one atmosphere absolute:

`m_required = V P M / (R T) = {gas['ideal_required_mass_g_at_20c']:.3f} g`

This ideal lower bound already exceeds the selected cartridge by
`{gas['ideal_mass_deficit_g_at_20c']:.3f} g`.  Real delivery must also cover residual cartridge gas,
two-phase blowdown losses, inflator pressure drop, buoy back pressure, leakage, cooling, and required
gauge pressure.  Therefore the 12 g / 60 L pairing **FAILS** without needing those unavailable details.

Sensitivity: even the optimistic 45 C ideal volume is only
`{gas['hot_45c_ideal_volume_l']:.3f} L` ({gas['hot_45c_ideal_volume_l']/60:.1%} of nominal buoy volume).

### Release consequence

The inflation architecture must be reselected and requalified.  No inflator, cartridge, buoy, routing,
pressure-margin, or deployment-time release claim is permitted from the current combination.

## 3. Buoyancy and reserve buoyancy - PARTIAL

A 60 L fully displaced volume in 1025 kg/m3 seawater corresponds to a gross displaced mass of:

`m_displaced = rho V = 1025 kg/m3 x 0.060 m3 = {gross_buoyant_mass_kg:.3f} kg`

This is a geometric upper bound, not an accepted lift rating.  Delivered gas fails the volume screen,
and the required supported load, immersion, freeboard, stability, orientation, tether angle, dynamic
sea load, and softgood deformation are not controlled.  Net mission margin is **NOT CALCULABLE**.

## 4. Mass, center of gravity, and inertia - DIGITAL PASS

| State | Mass | Reserve to 18.14 kg | CG X | CG Y | CG Z |
|---|---:|---:|---:|---:|---:|
| STOWED | {stowed_mass['total_mass_kg']:.9f} kg | {stowed_mass['mass_reserve_to_18_14_kg']:.9f} kg | {stowed_mass['cg_mm']['x']:.3f} mm | {stowed_mass['cg_mm']['y']:.3f} mm | {stowed_mass['cg_mm']['z']:.3f} mm |
| DEPLOYED | {deployed_mass['total_mass_kg']:.9f} kg | {deployed_mass['mass_reserve_to_18_14_kg']:.9f} kg | {deployed_mass['cg_mm']['x']:.3f} mm | {deployed_mass['cg_mm']['y']:.3f} mm | {deployed_mass['cg_mm']['z']:.3f} mm |

The occurrence-weighted calculation resolves all {len(stowed['occurrences'])} occurrences.  This is a
digital CAD result and does not replace as-built weighing or balance verification.

## 5. Mechanism kinematics and complete motion - DIGITAL PASS

Acceptance criteria: 0-80 degree coverage in increments no greater than one degree; zero unauthorized
positive-volume pairs; zero blocked Booleans; zero track errors; zero intentional-fit register errors.

| Gate | Angles/pairs | Unauthorized overlaps | Blocked Booleans | Track errors | Result |
|---|---:|---:|---:|---:|---|
| Endpoint | {endpoint['endpoint_pairs']['STOWED']['unordered_pair_count']} pairs/state | 0 | 0 | n/a | PASS |
| Five-angle | {five['pair_row_count']} rows | {five['unauthorized_positive_volume_pair_count']} | {five['boolean_blocked_pair_count']} | {five['track_validation_error_count']} | {five['disposition']} |
| Full 0-80 degree | {full['pair_row_count']} rows | {full['unauthorized_positive_volume_pair_count']} | {full['boolean_blocked_pair_count']} | {full['track_validation_error_count']} | {full['disposition']} |

Crosshead travel from 0 to 80 degrees is `{full['crosshead_travel_0_to_80_mm']:.9f} mm`; maximum
absolute closure residual is `{full['maximum_closure_residual_abs_mm']:.3e} mm`.

The exact-Boolean audit classifies every positive-volume contact through the controlled intentional-fit
register.  It does not establish dynamic deployment, impact, fatigue, or physical lock capacity.

## 6. Envelope and state integrity - DIGITAL PASS

- Ready-to-throw rigid length: `{endpoint['dimensions']['ready_to_throw_total_length_mm']:.3f} mm`.
- Closed pack maximum OD: `{endpoint['dimensions']['closed_cordura_pack_maximum_od_mm']:.3f} mm`.
- Arm pivot station: `{endpoint['dimensions']['arm_pivot_axis_z_mm']:.3f} mm`.
- Arm pivot-to-tip: `{endpoint['dimensions']['arm_pivot_to_tip_lengths_mm']['ARM-1']:.6f} mm`.
- STOWED and DEPLOYED inventories: {len(stowed['occurrences'])} occurrences each.
- Fixed/moving/flexible identity and transforms are recorded in the two authoring inventories.

## 7. Pressure topology, flow, ratings, and leakage - NOT RELEASED

The current topology is a compact direct path: non-refillable cartridge -> Hydro 1F family inflator ->
buoy manifold/patch.  No hose or tube route is modeled.  The Leland cartridge is explicitly 3/8-24;
the Hydro 1F family supports 3/8 or 1/2 in cylinder variants, but the modeled `V95000xxB` identity does
not complete the controlling suffix.  The exact manifold interface, internal orifice, flow curve,
delivered pressure, application rating, and installed leak performance are absent.

Pressure loss, time-to-inflate, operating margin, open-port closure, and leakage are therefore
**NOT CALCULABLE**.  The gas-capacity FAIL remains controlling regardless.

## 8. Softgood opening, extraction, and retention - PHYSICAL VERIFICATION REQUIRED

The CAD includes separate closed STOWED and owner-approved open DEPLOYED pack states, individual
panels, hook-and-loop fields, seams/reinforcements, tether hardware, and attachment records.  A prior
screen assumed wet peel force of 32.1-74.9 N and inferred 5.230-12.204 kPa over the modeled area; those
are assumptions, not test data.  The inflator delivered-pressure curve is unavailable and the gas
capacity screen fails.  Opening margin is **NOT CALCULABLE**.

Required tests include wet breakaway/opening, fold/extraction repeatability, seam and webbing proof,
retention, re-pack/reset, water activation, leak, inflation-time, and environment conditioning.

## 9. Structural, fastener, impact, fatigue, tolerance, and manufacturing analyses

Nominal geometry, material assignments, occurrence interfaces, and the complete motion audit are
available.  Controlling mission loads, proof factors, dynamic impact cases, duty spectrum, joint
preload, supplier material allowables, release tolerances, process capability, and approved drawings
are not.  Strength, stiffness, pin/fastener margins, fatigue life, impact margin, and tolerance stacks
are **NOT CALCULABLE**.  Fabrication is prohibited until those inputs and calculations are controlled.

## 10. Independent calculation check

The stored-gas screen is independently recomputed in `STORED_GAS_INDEPENDENT_CALCULATION.json` from
the stated constants.  The result is insensitive to reasonable temperature variation and establishes
a large deficit.  The mass report is independently reconciled to {len(stowed['occurrences'])} positive-
mass occurrences per state.  The endpoint, five-angle, and full-motion results use separate validators
bound to the frozen STEP and inventory hashes.

## 11. Final disposition

Digital mechanism geometry, endpoint integrity, state parity, nominal envelope, mass properties, and
exact-Boolean motion are acceptable as developmental evidence.  Production release is blocked by the
gas-capacity failure, incomplete installed inflator configuration/rating, dimension-controlled proxy,
missing physical qualification, missing mission loads, and missing manufacturing definition.
"""
    write_text(analysis_dir / "TECHNICAL_ANALYSIS_REPORT.md", report)


def make_interface_documents(stowed: dict[str, Any]) -> None:
    interface_dir = ensure_dir(OUT / "04_INTERFACES")
    pressure_rows = [
        {
            "connection_id": "P-001",
            "source": "Leland 81121 12 g CO2 cartridge",
            "destination": "Hydro 1F family inflator cylinder interface",
            "source_thread": "3/8-24 UNF male puncture cartridge",
            "destination_thread": "Hydro family supports 3/8-24 or 1/2-20; installed suffix incomplete",
            "gender": "Male cartridge to supplier-defined inflator receptacle",
            "seal": "Supplier puncture/seal system - exact installed gasket not controlled",
            "pressure_rating": "NOT DETERMINABLE FOR INSTALLED CONFIGURATION",
            "material_compatibility": "Zinc-plated steel cartridge to supplier-defined stainless/polymer assembly; qualification required",
            "orientation": "Modeled external pack orientation",
            "engagement": "NOT DETERMINABLE",
            "id_length_bend_support": "Direct threaded interface; no route",
            "status": "FAIL - VARIANT/SUFFIX AND APPLICATION RATING NOT CONTROLLED",
        },
        {
            "connection_id": "P-002",
            "source": "Hydro 1F family inflator manifold",
            "destination": "60 L buoy inflation patch/manifold",
            "source_thread": "Supplier manifold with V90113 O-rings; exact port geometry not controlled",
            "destination_thread": "Custom buoy patch interface",
            "gender": "NOT DETERMINABLE",
            "seal": "Supplier manifold O-rings plus custom installed patch - unqualified",
            "pressure_rating": "NOT DETERMINABLE",
            "material_compatibility": "Supplier glass-reinforced nylon/stainless to custom softgoods; physical compatibility required",
            "orientation": "Direct mounted",
            "engagement": "NOT DETERMINABLE",
            "id_length_bend_support": "Proprietary/direct internal passage; no external route",
            "status": "NOT RELEASED",
        },
        {
            "connection_id": "P-003",
            "source": "V80040 water-sensitive bobbin",
            "destination": "Hydro 1F automatic trigger housing",
            "source_thread": "No pressure thread",
            "destination_thread": "Supplier keyed housing",
            "gender": "Supplier service interface",
            "seal": "Not a pressure boundary by itself",
            "pressure_rating": "NOT APPLICABLE",
            "material_compatibility": "Supplier-defined",
            "orientation": "White pill toward cap/housing per IFU",
            "engagement": "Per IFU; installed verification required",
            "id_length_bend_support": "Not applicable",
            "status": "SOURCE-IDENTIFIED; INSTALLED QUALIFICATION OPEN",
        },
    ]
    write_csv(interface_dir / "PORT_TO_PORT_CONNECTION_TABLE.csv", pressure_rows)
    ratings = [
        {
            "component": "Leland 81121 12 g CO2 cartridge",
            "manufacturer_part_number": "81121",
            "modeled_identity": "LELAND-81121",
            "published_interface": "3/8-24 UNF puncture; 12 g CO2; 3.250 x 0.735 in referential dimensions",
            "published_pressure_rating": "NOT PUBLISHED IN CONTROLLED PUBLIC SOURCE",
            "application_rating": "FAIL - INSUFFICIENT IDEAL GAS FOR 60 L",
            "evidence_status": "OFFICIAL PRODUCT PAGE VERIFIED 2026-08-26",
        },
        {
            "component": "Halkey-Roberts Hydro 1F inflator family",
            "manufacturer_part_number": "V95000xxB family; installed suffix incomplete",
            "modeled_identity": "HALKEY-ROBERTS-HYDRO-1F-V95000XXB_PROXY",
            "published_interface": "3/8 or 1/2 in CO2 threaded family; V90113 O-rings; V80040 bobbin",
            "published_pressure_rating": "COMPONENT RECOGNITION DOES NOT ESTABLISH THIS 60 L APPLICATION",
            "application_rating": "NOT DETERMINABLE",
            "evidence_status": "DIMENSION-CONTROLLED PROXY; EXACT INSTALLED GEOMETRY/RATING ABSENT",
        },
        {
            "component": "Custom 60 L buoy and inflation patch",
            "manufacturer_part_number": "CUSTOM DEVELOPMENTAL",
            "modeled_identity": "60 L analytic softgood definition",
            "published_interface": "No released drawing or rated patch interface",
            "published_pressure_rating": "NOT DETERMINABLE",
            "application_rating": "NOT QUALIFIED",
            "evidence_status": "PHYSICAL PROOF/BURST/LEAK/INFLATION TESTS REQUIRED",
        },
    ]
    write_csv(interface_dir / "PRESSURE_COMPONENT_RATINGS_MATRIX.csv", ratings)
    write_text(
        interface_dir / "PRESSURE_TOPOLOGY.md",
        f"""# Pressure Topology

Status: **{STATUS}**

```text
Leland 81121 non-refillable 12 g CO2 cartridge
        |
        | 3/8-24 puncture interface; matching Hydro suffix not completed
        v
Halkey-Roberts Hydro 1F V95000 family automatic/manual inflator
        |-- V80040 water-sensitive bobbin / manual pull activation
        |-- V90113 manifold O-rings identified by supplier
        v
Custom 60 L buoy inflation patch/manifold
        v
Buoy internal volume / no separately modeled vent or exhaust
```

The current architecture has no separate fill interface, regulator, gauge, sensor, tee, hose, rigid
tube, or pneumatic actuator.  It therefore has zero CAD route objects.  This removes the historical
broken-line geometry family from the current model, but it does not prove the compact supplier-internal
flow path or the custom patch interface.

The topology is non-release because the cartridge/volume sizing fails, the exact Hydro suffix and
installed vendor geometry are absent, and the application pressure/flow/leak evidence is unavailable.
""",
    )
    write_text(
        interface_dir / "CAD_ROUTING_AND_SWEPT_AUDIT.md",
        f"""# CAD Routing and Swept Audit

- Route objects in STOWED authoring inventory: **{len(stowed.get('routes', []))}**.
- Pressure topology: direct cartridge/inflator/buoy installation; no external pressure hose or tube.
- Historical open, malformed, coincident, fused, or externally looping line solids are absent from the
  current configuration because the prior internal pressure architecture was removed.
- Full mechanism motion: **PASS**, 0-80 degrees at one-degree increments.
- Unauthorized positive-volume pairs: **0**.
- Hose/tube bend radius and swept routing: **NOT APPLICABLE to the current no-route topology**.
- Supplier-internal flow continuity and custom manifold/patch continuity: **NOT DETERMINABLE**.

This report is not a pressure-system release.  See `PORT_TO_PORT_CONNECTION_TABLE.csv`,
`PRESSURE_COMPONENT_RATINGS_MATRIX.csv`, and the gas-capacity section of the technical report.
""",
    )


def make_screenshot_report(full: dict[str, Any]) -> None:
    out_dir = ensure_dir(OUT / "07_RENDERING_AND_SCREENSHOTS")
    defect_families = {
        1: "Mechanism interfaces",
        2: "Mechanism interfaces",
        3: "Broken/malformed pressure routing",
        4: "Broken/malformed pressure routing",
        5: "Mandatory open-line/branch regression",
        6: "External routing loop",
        7: "Distorted line geometry",
        8: "Distorted line geometry",
        9: "Unconnected stubs/bulkhead penetrations",
        10: "Owner-approved open pack",
        11: "Owner-approved open pack",
    }
    rows = []
    for index, filename in enumerate(SCREENSHOTS, start=1):
        open_pack = index >= 10
        rows.append(
            {
                "image_number": index,
                "filename": filename,
                "input_presence": "MISSING FROM ATTACHMENT AND BOUNDED WORKSPACE SEARCH",
                "defect_family_or_intent": defect_families[index],
                "affected_occurrences": (
                    "Open pack softgoods/inflator/tether occurrences; exact image mapping not possible"
                    if open_pack
                    else "NOT DETERMINABLE FROM ABSENT IMAGE"
                ),
                "actual_inspection_result": (
                    "Current DEPLOYED master contains the required open pack; mechanical credibility remains physical-test dependent"
                    if open_pack
                    else "Global current-model family audit completed; exact pictured root cause cannot be reconstructed"
                ),
                "root_cause": (
                    "Controlling owner intent, not a defect"
                    if open_pack
                    else "Historical image unavailable; no unsupported root cause assigned"
                ),
                "correction": (
                    "Preserved separate closed STOWED and open DEPLOYED configurations"
                    if open_pack
                    else "Current architecture contains no route objects; exact-Boolean mechanism audit passes"
                ),
                "before_rendering": "NOT AVAILABLE - SOURCE SCREENSHOT MISSING",
                "after_rendering": (
                    "07_RENDERING_AND_SCREENSHOTS/system_views/open_pack_overview.png"
                    if open_pack
                    else "07_RENDERING_AND_SCREENSHOTS/system_views/current CAD inspection views"
                ),
                "stowed_result": "Closed pack digitally represented; endpoint gate PASS",
                "deployed_result": "Open pack digitally represented; endpoint gate PASS",
                "motion_result": f"{full['disposition']}; 0-80 degree one-degree sweep",
                "validator_evidence": "09_VALIDATION/full_motion/full_motion_exact_boolean_summary.json",
                "independent_review_disposition": "PENDING FRESH-CONTEXT REVIEW",
            }
        )
    write_csv(out_dir / "SCREENSHOT_CLOSURE_REPORT.csv", rows)
    write_text(
        out_dir / "SCREENSHOT_INPUT_EXCEPTION.md",
        """# Screenshot Input Exception

All eleven filenames specified by the commission were searched below the supplied attachment root,
Codex attachment store, Documents/Codex work areas, and CodexProjects.  None was supplied.  The closure
register therefore distinguishes the mandatory current-model defect-family audit from the impossible
image-specific before/after reconstruction.  No image content, location, or root cause is invented.

Images 10-11 are still treated as controlling text-level owner intent: the open DEPLOYED pack remains
open and is not classified as a cleanup defect.  Exact visual comparison remains unavailable.
""",
    )


def make_manufacturing_and_verification(stowed: dict[str, Any]) -> None:
    manufacturing = ensure_dir(OUT / "06_MANUFACTURING_AND_SERVICE")
    part_counts = Counter(occ["part_number"] for occ in stowed["occurrences"])
    drawing_rows = []
    for part in sorted(stowed["parts"], key=lambda row: row["part_number"]):
        if part.get("make_buy") != "MAKE":
            continue
        drawing_rows.append(
            {
                "part_number": part["part_number"],
                "physical_title": part.get("final_display_name", ""),
                "quantity": part_counts[part["part_number"]],
                "material": part.get("material", ""),
                "finish": part.get("finish", ""),
                "neutral_cad": "SEE 02_PART_DEFINITIONS",
                "dimensioned_drawing": "NOT RELEASED",
                "datums_gdt_tolerances": "NOT DETERMINABLE - LOAD/TOLERANCE BASIS ABSENT",
                "threads_fits_edge_surface_notes": "SOURCE NOTES ONLY; RELEASE DRAWING REQUIRED",
                "inspection_characteristics": "NOMINAL CAD PRESENT; CRITICAL CHARACTERISTICS NOT APPROVED",
                "drawing_to_cad_verification": "NOT RUN - NO RELEASE DRAWING",
                "fabrication_authority": "PROHIBITED",
            }
        )
    write_csv(manufacturing / "MANUFACTURED_PART_DRAWING_REGISTER.csv", drawing_rows)
    assembly_drawing_rows = [
        {
            "assembly_identifier": identifier,
            "assembly_title": title,
            "state": state,
            "cad_authority": authority,
            "assembly_drawing": "NOT RELEASED",
            "exploded_view": "NOT RELEASED",
            "ballooned_bom": "NOT RELEASED",
            "interface_dimensions_and_tolerances": "NOT DETERMINABLE - LOAD/TOLERANCE/INTERFACE BASIS ABSENT",
            "assembly_and_inspection_notes": "DEVELOPMENTAL SEQUENCE ONLY; RELEASED WORK INSTRUCTIONS ABSENT",
            "drawing_to_cad_verification": "NOT RUN - NO RELEASE DRAWING",
            "release_authority": "PROHIBITED",
            "blocking_basis": blocking,
        }
        for identifier, title, state, authority, blocking in (
            (
                "STINGRAY-ROOT-STOWED",
                "COMPLETE PRODUCT ASSEMBLY - STOWED",
                "STOWED",
                "01_CAD_MASTERS/STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step",
                "Governing loads, released interfaces, GD&T, approved processes, and physical assembly proof absent",
            ),
            (
                "STINGRAY-ROOT-DEPLOYED",
                "COMPLETE PRODUCT ASSEMBLY - DEPLOYED",
                "DEPLOYED",
                "01_CAD_MASTERS/STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step",
                "Governing loads, released interfaces, GD&T, approved processes, and physical deployment proof absent",
            ),
            (
                "FORWARD-BODY-AND-BALLAST",
                "FORWARD PENETRATOR, BALLAST, AND TRANSITION",
                "FIXED",
                "01_CAD_MASTERS; 03_BOM_AND_REGISTERS/COMPONENT_DESIGN_BASIS_MATRIX.csv",
                "Material allowables, weld/joint definition, tolerances, and inspection acceptance absent",
            ),
            (
                "ARM-POWERTRAIN",
                "THREE-ARM DEPLOYMENT POWERTRAIN",
                "STOWED/DEPLOYED",
                "01_CAD_MASTERS; 09_VALIDATION",
                "Digital kinematics pass; loads, fatigue, lock capacity, assembly tooling, and physical proof absent",
            ),
            (
                "EXTERNAL-BUOY-PACK-STOWED",
                "EXTERNAL BUOY SOFTGOODS PACK - CLOSED",
                "STOWED",
                "01_CAD_MASTERS; 07_RENDERING_AND_SCREENSHOTS/system_views",
                "Developmental softgoods envelopes; patterns, seams, reinforcement, retention, and wet proof absent",
            ),
            (
                "EXTERNAL-BUOY-PACK-DEPLOYED",
                "EXTERNAL BUOY SOFTGOODS PACK - OWNER-APPROVED OPEN STATE",
                "DEPLOYED",
                "01_CAD_MASTERS; 07_RENDERING_AND_SCREENSHOTS/system_views/open_pack_overview.png",
                "Owner intent is controlled, but deployed fabric shape, retention, breakaway, and wet proof remain physical",
            ),
            (
                "PRESSURE-INFLATION-TOPOLOGY",
                "CARTRIDGE, INFLATOR, PATCH, AND BUOY INFLATION ASSEMBLY",
                "STOWED/DEPLOYED",
                "04_INTERFACES/PRESSURE_TOPOLOGY.md; 04_INTERFACES/PORT_TO_PORT_TABLE.csv",
                "12 g/60 L capacity fails; exact suffix, installed thread, geometry, ratings, flow, and leak evidence absent",
            ),
            (
                "STRUCTURAL-RECOVERY-LOAD-PATH",
                "HARDPOINT, RETAINED PIN, THIMBLE, HMPE TETHER, AND BUOY HARNESS",
                "STOWED/DEPLOYED",
                "01_CAD_MASTERS; 03_BOM_AND_REGISTERS/SOURCE_PACKAGE05_REGISTERS/FINAL_ATTACHMENT_CONNECTIVITY.csv",
                "Nominal hard load path is modeled; governing loads, splice qualification, strength, breakaway, and proof tests absent",
            ),
        )
    ]
    write_csv(manufacturing / "ASSEMBLY_DRAWING_REGISTER.csv", assembly_drawing_rows)
    write_text(
        manufacturing / "ASSEMBLY_SERVICE_RESET_INSTRUCTIONS.md",
        f"""# Assembly, Service, and Reset Instructions - Developmental

Status: **{STATUS}**

These instructions preserve the digitally represented sequence but are not released work instructions.
Torque, locking compounds, lubrication, seal installation, acceptance gauges, and tolerance-dependent
steps remain unavailable and must not be invented.

## Assembly sequence

1. Verify all BUY and MAKE identities against the BOM and incoming evidence.
2. Assemble the forward structure, arm carrier, three arm mechanisms, common crosshead, gas springs,
   dampers, pins, bushings, washers, and retainers in the named hierarchy.
3. Confirm free arm travel and stop/guide engagement before installing the aft softgoods package.
4. Install the aft structural tether load path from hardpoint ring through retained pin/thimble, HMPE
   tether, and buoy harness; do not route primary load through hook-and-loop fields or the inflator patch.
5. Install the Cordura cradle, closed-pack panels, seams/reinforcements, and both retained flaps.
6. Install the completed, qualified inflator configuration and compatible cartridge only after the gas
   architecture is corrected and released.  The current 12 g / 60 L pairing is prohibited.
7. Install the water-sensitive bobbin in the supplier-required orientation and verify the service
   indicator only under the current supplier IFU and approved work instruction.
8. Conduct dimensional, attachment, motion, access, and leak/inflation acceptance inspections.

## Service/reset sequence

1. Make the gas source safe and discard any punctured/non-reusable cartridge per supplier instructions.
2. Open the pack without cutting structural tether or load-path hardware.
3. Remove and inspect the inflator cap/bobbin/cartridge in the supplier-defined order.
4. Dry and inspect all softgoods, hook-and-loop, seams, webbing, tether, hardware, and corrosion-prone
   interfaces.  Reject damage against an approved inspection standard (not yet available).
5. Re-pack with controlled fold pattern, panel order, flap overlap, and retained pull/manual access.
6. Install only an in-date bobbin and an approved compatible cartridge; verify the service indicator.
7. Perform the released leak, trigger, breakaway, and functional checks before return to service.

## Tool and access disposition

Nominal access is visible in CAD, but realistic tool clearance and physical assembly/reset trials have
not been completed.  No torque value, adhesive, lubricant, locking method, or acceptance dimension not
explicitly present in controlled supplier evidence is authorized by this document.
""",
    )

    physical_plan = """# Physical Verification Plan

Status: **REQUIRED BEFORE ANY PRODUCTION RELEASE OR FIELD USE**

| ID | Test | Purpose | Minimum evidence | Release effect |
|---|---|---|---|---|
| PV-001 | Inflation architecture qualification | Demonstrate correct gas mass, inflator, patch, time, and final pressure for 60 L | Controlled articles, instrumented cold/nominal/hot tests, repeatability, failure inspection | Close gas-capacity, flow, pressure, and compatibility gates |
| PV-002 | Hydro/inflator installed leak and rearm | Verify exact suffix, threads, seals, indicator, bobbin, and service sequence | Supplier-approved configuration and leak/function records | Close pressure continuity and service gates |
| PV-003 | Wet opening/breakaway | Measure wet hook-and-loop release and panel extraction | Conditioned articles, force/pressure/time traces, video, pass criteria | Close softgood opening margin |
| PV-004 | Buoy proof/burst/leak | Establish operating and proof pressure, leakage, seam/patch strength | Approved drawing/material lot and proof/burst protocol | Close pressure rating and softgood structural gates |
| PV-005 | Buoyancy/orientation/stability | Demonstrate supported load, freeboard, orientation, tether angle, and recovery stability | Worst-case mass/CG and water conditions | Close mission buoyancy/stability gates |
| PV-006 | Static structural proof | Validate arms, pins, locks, stops, hardpoint, and tether load path | Controlled mission loads and proof factors | Close structural margin gates |
| PV-007 | Dynamic deployment/impact | Measure deployment time, damping, stop loads, bounce, and overtravel | Instrumented deployment at environmental extremes | Close dynamic and impact gates |
| PV-008 | Durability/fatigue/wear | Demonstrate cycle life of mechanism and softgoods | Approved duty cycle and post-test inspection | Close life/wear gates |
| PV-009 | Corrosion/environment | Salt, humidity, UV, temperature, storage, contamination, and galvanic exposure | Qualified procedure and material/finish lots | Close environmental gates |
| PV-010 | Assembly/tool/service trial | Prove realistic tools, order, torque, access, repack, replacement, and inspection | Released prototype build record with findings closed | Close manufacturing/service gates |
| PV-011 | Drop/handling | Validate retention and no hazardous damage | Controlled drop/handling requirement and test | Close handling gate |
| PV-012 | As-built mass/CG/dimensions | Reconcile hardware to digital master | Calibrated measurements on representative builds | Close as-built conformity gate |
"""
    write_text(manufacturing / "PHYSICAL_VERIFICATION_PLAN.md", physical_plan)


def make_risk_and_fmea(gas: dict[str, float]) -> None:
    review = ensure_dir(OUT / "10_REVIEWS")
    risks = [
        ("R-001", "Inflation gas capacity", "12 g cartridge cannot fill 60 L", "No/partial buoy inflation", "CRITICAL", "OPEN", f"Ideal volume {gas['nominal_20c_ideal_volume_l']:.3f} L vs 60 L", "Reselect complete qualified inflation architecture and test"),
        ("R-002", "Inflator configuration", "V95000 suffix/exact geometry/rated interface incomplete", "Thread/seal/fit/function incompatibility", "CRITICAL", "OPEN", "Dimension-controlled proxy and family-level evidence", "Obtain supplier-controlled installed configuration and application approval"),
        ("R-003", "Softgoods opening", "Wet peel, folds, seams, patch, and breakaway not tested", "Failure to deploy or damaged buoy", "CRITICAL", "OPEN", "CAD states only", "Execute PV-003/PV-004"),
        ("R-004", "Structural load path", "Mission loads/proof factors absent", "Arm/pin/lock/hardpoint/tether failure", "CRITICAL", "OPEN", "Nominal geometry only", "Control loads, complete FEA/hand checks, and proof test"),
        ("R-005", "Buoyancy/stability", "Required supported load and stability cases absent", "Insufficient lift or adverse orientation", "CRITICAL", "OPEN", "60 L gross displacement only", "Define mission cases and execute hydrostatic/physical tests"),
        ("R-006", "Automatic activation", "Water trigger and installed rearm behavior unqualified", "No automatic deployment or inadvertent activation", "MAJOR", "OPEN", "Supplier family IFU only", "Install exact qualified parts and environmental functional test"),
        ("R-007", "Manufacturing definition", "No released drawings/GD&T/process controls", "Unbuildable or nonconforming product", "CRITICAL", "OPEN", "79 MAKE definitions; drawing register not released", "Complete structural/tolerance basis and release drawings"),
        ("R-008", "AP242 reproducibility", "Presentation-style entity order varies across identical builds", "Byte-identical master cannot be reproduced", "MAJOR", "OPEN", "Geometry/inventories/mass stable; STEP hashes vary", "Correct exporter ordering or adopt controlled semantic reproducibility acceptance"),
        ("R-009", "Screenshot evidence", "Eleven required reference images were not supplied", "Image-specific defects cannot be mapped/closed", "MAJOR", "OPEN", "Bounded search found zero images", "Provide exact images and repeat closure review"),
        ("R-010", "Primary editable-source authority", "Named source ZIP/decision filenames remained placeholders", "Potential newer source/decision omitted", "MAJOR", "OPEN", "Repository/context baseline used", "Provide and reconcile exact attachments"),
        ("R-011", "COTS-first objective", "79 MAKE vs 13 BUY unique definitions", "Cost/schedule/qualification burden", "MAJOR", "OPEN", "BOM classification", "Resume only a bounded complete-module screen after controlling requirements are fixed"),
        ("R-012", "Dynamic mechanism", "Static motion PASS lacks time/load/impact evidence", "Overtravel, bounce, lock failure", "MAJOR", "OPEN", "0-80 degree Boolean/kinematic PASS", "Execute instrumented dynamic deployment"),
        ("R-013", "Corrosion/environment", "Mixed materials/finishes not system-qualified", "Seizure, leakage, loss of strength", "MAJOR", "OPEN", "Materials register only", "Compatibility review plus environmental tests"),
        ("R-014", "Naming", "Root assembly retains administrative configuration tokens", "Release naming nonconformance", "MINOR", "OPEN", "Authoring inventory root_name", "Rename root in a new frozen build and rerun targeted regressions"),
    ]
    rows = [
        {
            "risk_id": rid,
            "function": function,
            "failure_mode_or_cause": cause,
            "effect": effect,
            "severity": severity,
            "status": status,
            "evidence": evidence,
            "required_control": control,
            "residual_risk": "NOT EVALUATED UNTIL CONTROL IS VERIFIED",
        }
        for rid, function, cause, effect, severity, status, evidence, control in risks
    ]
    write_csv(review / "RISK_REGISTER_AND_FMEA.csv", rows)


def make_governance_and_release(
    stowed: dict[str, Any], endpoint: dict[str, Any], five: dict[str, Any], full: dict[str, Any]
) -> None:
    release = ensure_dir(OUT / "00_RELEASE_INDEX")
    gas = gas_capacity()
    input_rows = [
        {
            "required_input": "Primary editable source ZIP",
            "requested_name": "[INSERT EXACT NEWEST EDITABLE SOURCE ZIP FILENAME]",
            "result": "PLACEHOLDER IN COMMISSION; NO ZIP ATTACHED",
            "disposition": "Repository Package 05 procedural source selected as newest controlled baseline; attachment gap remains open",
        },
        {
            "required_input": "Controlling owner-decision file 1",
            "requested_name": "[INSERT EXACT DECISION FILE 1 FILENAME]",
            "result": "PLACEHOLDER IN COMMISSION; NO FILE ATTACHED",
            "disposition": "Context-branch decisions used; possible newer attachment remains open",
        },
        {
            "required_input": "Controlling owner-decision file 2",
            "requested_name": "[INSERT EXACT DECISION FILE 2 FILENAME]",
            "result": "PLACEHOLDER IN COMMISSION; NO FILE ATTACHED",
            "disposition": "Context-branch decisions used; possible newer attachment remains open",
        },
    ]
    for filename in SCREENSHOTS:
        input_rows.append(
            {
                "required_input": "Visual reference screenshot",
                "requested_name": filename,
                "result": "MISSING FROM ATTACHMENT AND BOUNDED WORKSPACE SEARCH",
                "disposition": "Global defect-family audit completed; exact image-specific closure remains open",
            }
        )
    write_csv(release / "INPUT_GAP_REGISTER.csv", input_rows)

    decisions = [
        ("D-001", "Use the newest Package 05 current configuration as the CAD anchor", "Context CURRENT_STATE and newest local branch/commit", "Preserves newer owner decisions over historical branches"),
        ("D-002", "Create isolated design/stingray-complete-product-definition branch", "Commission section 25", "Protects all occupied/dirty historical worktrees"),
        ("D-003", "Preserve protected owner inspection packages unchanged", "Repository governance", "No transfer package is modified or merged"),
        ("D-004", "Preserve owner-approved open DEPLOYED pack and separate closed STOWED state", "Commission section 15", "Open pack is controlling intent, not a cleanup defect"),
        ("D-005", "Do not invent Hydro 1F internals, suffix, ratings, or vendor CAD", "Evidence discipline", "Proxy remains explicit and blocks release"),
        ("D-006", "Freeze the second clean-build AP242 pair for validation", "First/second rebuild comparison", "Prevents later evidence from binding to an intermediate master"),
        ("D-007", "Record AP242 byte nondeterminism as a release exception", "Identical seeded builds changed only STEP presentation/style ordering and hashes", "Inventories/mass are stable; byte PASS is not claimed"),
        ("D-008", "Reject the 12 g / 60 L inflation pairing", "Independent ideal-gas calculation", "Architecture correction is mandatory"),
        ("D-009", "Deliver maximum-complete non-release package", "Commission terminal exception clause", "All unaffected digital/documentary work continues without invented evidence"),
        ("D-010", "No procurement, fabrication, qualification, or main-branch merge", "Authority boundary", "Final branch is evidence only"),
    ]
    write_csv(
        release / "AUTONOMOUS_DECISION_REGISTER.csv",
        [
            {
                "decision_id": row[0],
                "decision": row[1],
                "basis": row[2],
                "effect": row[3],
                "authority": "COMMISSION-BOUNDED AUTONOMOUS ENGINEERING JUDGMENT",
            }
            for row in decisions
        ],
    )

    gates = [
        ("Zero invalid solids", "PASS - DIGITAL", "Endpoint and motion validators reimport valid solids"),
        ("Zero failed modeling features", "PASS - PROCEDURAL BUILD", "Clean procedural build exited zero; native feature-tree audit not applicable"),
        ("Zero broken references", "PASS - DELIVERED SOURCE", "Clean build resolved delivered source dependencies"),
        ("Zero missing dependencies", "PASS - CURRENT ENVIRONMENT", "Build completed; clean extracted rebuild must reconfirm"),
        ("Zero missing BOM parts", "NOT DETERMINABLE", "Authoring BOM reconciles, but physical completeness/vendor internals are not qualified"),
        ("Zero unmatched CAD occurrences", "PASS - DIGITAL", f"{len(stowed['occurrences'])} named occurrences in each state"),
        ("Zero unintended duplicate occurrences", "PASS - DIGITAL", "Inventory and endpoint validator found no uncontrolled duplicate occurrences"),
        ("Zero floating components", "PASS - DIGITAL NOMINAL", "Attachment/connection registers and endpoint distances pass; physical proof remains open"),
        ("Zero omitted hardware", "NOT DETERMINABLE", "No released assembly drawing or physical build review"),
        ("Zero placeholder components", "FAIL", "Hydro 1F is a dimension-controlled proxy; packed softgoods include developmental envelopes"),
        ("Zero unexplained line breaks", "PASS - CURRENT TOPOLOGY", "No pressure route objects; historical broken route architecture removed"),
        ("Zero open required ports", "NOT DETERMINABLE", "Exact inflator/manifold internal and installed interfaces absent"),
        ("Zero incompatible pressure connections", "FAIL", "3/8-24 cartridge known; exact matching Hydro suffix not completed"),
        ("Zero unsupported cylinder configurations", "FAIL", f"12 g ideal volume {gas['nominal_20c_ideal_volume_l']:.3f} L vs 60 L"),
        ("Zero invalid rigid interferences", "PASS - DIGITAL", f"Full sweep {full['pair_row_count']} rows; zero unauthorized overlaps"),
        ("Zero unclassified collision pairs", "PASS - DIGITAL", "Intentional-fit register errors zero"),
        ("Zero unexplained state-parity mismatches", "PASS - DIGITAL", f"{len(stowed['occurrences'])} occurrences per endpoint; fixed/moving/flexible records controlled"),
        ("Zero naming violations", "FAIL", "Root assembly retains administrative I5S/DF8/SHORT14 configuration tokens"),
        ("Zero unresolved controlling requirements", "FAIL", "Gas, loads, ratings, drawings, physical tests, and attachments remain open"),
        ("Zero untraced attached decisions", "FAIL", "Required decision filenames remained placeholders and were not attached"),
        ("Zero unreviewed COTS components", "FAIL", "Family-level/drawing-derived definitions are not application-qualified; one explicit proxy"),
        ("Zero unresolved arithmetic discrepancies", "PASS FOR COMPLETED CALCULATIONS", "Independent gas and mass checks reconcile; unavailable calculations remain marked"),
        ("Zero cross-document contradictions", "TEMPLATE - PENDING INTERNAL REVIEW", "Generated pre-review template; controlled evidence-state transition required"),
        ("Zero unresolved internal-review findings", "TEMPLATE - PENDING", "Internal review not yet frozen"),
        ("Zero unresolved independent-review findings", "TEMPLATE - PENDING", "Fresh-context review not yet commissioned"),
        ("100% BOM-to-CAD reconciliation", "PASS - AUTHORED INVENTORY", "92 unique definitions and 180 occurrences per state"),
        ("100% requirement-to-evidence traceability", "FAIL", "Traceability identifies external evidence and physical-test gaps"),
        ("100% applicable-analysis completion", "FAIL", "Required safety/manufacturing analyses remain NOT CALCULABLE or physical"),
        ("Clean build", "PASS WITH REPRODUCIBILITY EXCEPTION", "Build exits zero; inventories/mass repeat; AP242 bytes vary"),
        ("Export/reimport", "PASS - DIGITAL SEMANTIC", "Endpoint/motion validators use clean OCP reimport; byte reproduction fails"),
        ("Fabrication/production release", "FAIL - NOT RELEASED", "Multiple critical gates remain open"),
    ]
    gate_rows = [
        {"release_gate": name, "disposition": disposition, "evidence_or_reason": evidence}
        for name, disposition, evidence in gates
    ]
    write_csv(release / "OBJECTIVE_RELEASE_GATE_TABLE.csv", gate_rows)

    section_status = {
        0: ("PARTIAL", "Maximum-complete non-release outcome"),
        1: ("PASS", "Repository and branch authority inspected"),
        2: ("PASS", "Mandatory context reading completed"),
        3: ("PASS", "Current Package 05 anchor selected"),
        4: ("FAIL", "Named source/decision placeholders and 11 screenshots absent"),
        5: ("PASS", "No unsupported claim promoted"),
        6: ("PASS", "Autonomous decision register supplied"),
        7: ("PASS", "Bounded root-cause/retry control applied"),
        8: ("PASS", "Current architecture preserved except evidence outputs"),
        9: ("FAIL", "No complete qualified commercial inflation module"),
        10: ("PARTIAL", "Applicability complete; required unavailable analyses block release"),
        11: ("PARTIAL", "Design-basis matrix supplied; ratings/loads open"),
        12: ("FAIL", "One explicit COTS proxy and developmental softgood envelopes"),
        13: ("FAIL", "Root assembly name contains prohibited administrative tokens"),
        14: ("FAIL", "Gas capacity/interface/rating/continuity not released"),
        15: ("PARTIAL", "Global audit complete; exact images missing"),
        16: ("PASS - DIGITAL", "Parity and full one-degree motion pass"),
        17: ("PARTIAL", "Readable analyses supplied; safety-critical unknowns remain"),
        18: ("FAIL", "No released drawings/GD&T/approved work instructions"),
        19: ("PARTIAL", "System and part render catalogs generated from CAD"),
        20: ("TEMPLATE - PENDING ARTIFACT GENERATION", "PPTX/PDF must be generated and verified before status transition"),
        21: ("FAIL", "Objective gate table contains open failures"),
        22: ("PARTIAL", "Clean semantic build/reimport pass; AP242 bytes nondeterministic"),
        23: ("TEMPLATE - PENDING INTERNAL REVIEW", "Internal artifact review requires a frozen artifact set"),
        24: ("TEMPLATE - PENDING INDEPENDENT REVIEW", "Fresh-context independent review requires a manifest-bound packet"),
        25: ("PASS", "Dedicated branch; protected packages preserved"),
        26: ("TEMPLATE - PENDING EXTRACTION", "Final ZIP assembly/extraction test requires the finalized candidate"),
        27: ("TEMPLATE - PENDING DELIVERY", "Terminal exception path invoked; delivery evidence not yet present"),
    }
    trace_rows = [
        {
            "commission_section": index,
            "status": section_status[index][0],
            "evidence": section_status[index][1],
            "release_effect": "SEE EVIDENCE" if section_status[index][0].startswith("PASS") else "BLOCKS RELEASE",
        }
        for index in range(28)
    ]
    write_csv(release / "REQUIREMENT_TRACEABILITY_MATRIX.csv", trace_rows)

    non_release = f"""# Non-Release Exception Report

## Controlling disposition

**{STATUS}**

The frozen candidate is a coherent developmental digital assembly, not a production release.  The
following exceptions are evidence limitations or verified failures; none is reclassified as acceptable.

## Critical verified failure

The selected Leland 81121 cartridge contains 12 g CO2.  At 20 C and one atmosphere, the optimistic
ideal-gas upper bound is **{gas['nominal_20c_ideal_volume_l']:.3f} L**, only
**{gas['nominal_fraction']:.1%}** of the modeled 60 L buoy.  The ideal lower-bound mass for 60 L is
**{gas['ideal_required_mass_g_at_20c']:.3f} g**, before losses, cooling, buoy back pressure, leakage, or
required gauge pressure.  The current inflation architecture therefore **FAILS**.

## Irreducible external evidence limitations

1. The exact installed Hydro 1F suffix, vendor-exact geometry, rated interface, flow curve, application
   approval, and custom patch/manifold definition are absent.
2. The primary source ZIP and two owner-decision filenames remained placeholders; no such attachments
   were supplied.
3. All eleven required reference screenshots were absent, preventing image-specific before/after closure.
4. Mission loads, proof factors, duty spectrum, impact/drop cases, and approved material allowables are
   absent; structural/fastener/fatigue margins are not calculable.
5. No wet inflation, breakaway, leak, proof/burst, stability, environmental, durability, dynamic, or
   assembly/service qualification evidence exists.
6. No released manufactured-part drawings, GD&T, tolerances, inspection plans, torque/locking data, or
   approved work instructions exist.
7. Identical seeded builds reproduce inventories and mass byte-for-byte but OCCT varies AP242
   presentation-style entity ordering, so the STEP masters are not byte-reproducible.

## Unaffected work completed

- Fresh endpoint, five-angle, and full one-degree exact-Boolean validation on frozen AP242 hashes.
- State parity, nominal envelope, occurrence identity, attachment/connection, mass/CG/inertia, BOM,
  materials/finishes, COTS provenance, procurement, design-basis, interface, risk/FMEA, applicability,
  physical-verification, manufacturing-readiness, and screenshot exception records.
- Per-part neutral/native exports and CAD-derived render catalogs (generated separately).
- Executive PPTX/PDF, internal review, fresh-context review, and extraction audit are post-generation
  evidence.  They may be added only after their checks run and the controlled status-transition
  procedure is completed; this generator does not pre-claim them.

## Required path to release

Correct and qualify the inflation architecture; control exact supplier configurations and rated
interfaces; define mission/load/environment requirements; release drawings and work instructions;
complete all required calculations and physical tests; correct export reproducibility or approve a
controlled semantic acceptance method; rerun full validation/review; then evaluate production release.

This package authorizes no purchase, fabrication, field use, qualification acceptance, or merge to main.
"""
    write_text(release / "NON_RELEASE_EXCEPTION_REPORT.md", non_release)

    authority = f"""# Ingestion, Authority, and Baseline Register

## Selected CAD source

- Local source branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- Exact source commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- Product-definition branch: `design/stingray-complete-product-definition`
- Product-definition baseline commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- Configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- Context authority branch: `origin/engineering/stingray-context`
- Context authority commit read: `8a63fd3c36866c1edffa245da06d8c7af2d90ee1`

## Frozen candidate

- STOWED AP242 SHA-256: `{sha256(STOWED_STEP)}`
- DEPLOYED AP242 SHA-256: `{sha256(DEPLOYED_STEP)}`
- STOWED inventory SHA-256: `{sha256(STOWED_INVENTORY)}`
- DEPLOYED inventory SHA-256: `{sha256(DEPLOYED_INVENTORY)}`

## Protected evidence

The `cad/df8-owner-creo-inspection-zips` remote branch and its three historical owner inspection ZIPs
were inspected as evidence sources and were not modified, copied over, merged, or rewritten.

## Conflict rule applied

Newest direct owner decisions and the current context branch controlled over older work-package detail.
Historical fixed-480 and 889 mm studies were not substituted for the newer 355 mm pivot configuration.
No missing attachment, vendor property, rated interface, validation claim, or physical result was invented.
"""
    write_text(release / "INGESTION_AND_AUTHORITY_REGISTER.md", authority)

    release_index = f"""# STINGRAY Complete Product Definition - Release Index

Status: **{STATUS}**

## Executive result

The frozen current configuration passes digital solid, endpoint, state-parity, mass, five-angle, and
full 0-80 degree one-degree exact-Boolean motion gates.  It does **not** pass production release because
the 12 g cartridge cannot fill the modeled 60 L buoy, the installed inflator configuration/rating is
incomplete, the exact COTS geometry is a proxy, safety/manufacturing analyses lack controlling inputs,
physical qualification is absent, and AP242 bytes are not reproducible across identical builds.

## Primary evidence

- CAD masters and inventories: `01_CAD_MASTERS/`
- Per-part CAD and render catalog: `02_PART_DEFINITIONS/`
- BOM/design basis/COTS/procurement: `03_BOM_AND_REGISTERS/`
- Pressure topology and interfaces: `04_INTERFACES/`
- Applicability and readable calculations: `05_ANALYSES/`
- Manufacturing/service/physical plan: `06_MANUFACTURING_AND_SERVICE/`
- CAD-derived renders and screenshot closure: `07_RENDERING_AND_SCREENSHOTS/`
- Executive PPTX/PDF: `08_EXECUTIVE/`
- Frozen validation evidence: `09_VALIDATION/`
- Risk/internal/independent review: `10_REVIEWS/`
- Build/dependency/environment instructions: `11_BUILD_AND_REPRODUCIBILITY/`
- Hashes and package audit: `12_MANIFESTS/`

## Release decision

**NO RELEASE.**  The package is suitable for controlled engineering review and architecture correction
only.  It authorizes no fabrication, procurement, qualification acceptance, field use, main-branch
merge, or modification of protected historical evidence.
"""
    write_text(release / "RELEASE_INDEX.md", release_index)


def make_build_records() -> None:
    build_dir = ensure_dir(OUT / "11_BUILD_AND_REPRODUCIBILITY")
    sources = sorted(
        path
        for path in (ROOT / "work" / "r2_source").iterdir()
        if path.is_file() and path.suffix.lower() in {".py", ".mjs"}
    )
    source_rows = [
        {
            "path": rel(path),
            "source_kind": "PYTHON" if path.suffix.lower() == ".py" else "NODE_ESM",
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sources
    ]
    dependencies = {
        "status": STATUS,
        "python_runtime_observed": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "source_inventory_scope": "Every direct .py and .mjs file delivered under work/r2_source; refreshed again during staging.",
        "source_inventory_file_count": len(source_rows),
        "delivered_source_inventory": source_rows,
        "authoring_sources": source_rows,
        "required_python_modules": ["cadquery", "OCP", "numpy", "matplotlib"],
        "required_python_modules_by_scope": {
            "cad_build_and_validation": ["cadquery", "OCP", "numpy", "matplotlib"],
            "package_audit_and_extraction": ["Pillow", "pypdf"],
            "executive_pdf_authoring": ["reportlab"],
        },
        "required_node_modules_by_scope": {
            "executive_presentation_authoring": ["@oai/artifact-tool"],
            "historical_workbook_authoring": ["@oai/artifact-tool"],
        },
        "required_native_tools_by_scope": {
            "pptx_render_and_overflow_qa": ["LibreOffice-compatible headless renderer"],
            "pdf_inspection_and_render_qa": ["Poppler pdfinfo", "Poppler pdftoppm"],
        },
        "required_source_trees": ["work/r2_source", "work/input", "work/forward_arm_repack"],
        "reviewed_status_transition_procedure": "11_BUILD_AND_REPRODUCIBILITY/CONTROLLED_STATUS_TRANSITION_PROCEDURE.md",
        "manifest_refresh_status": "PASS - ALL DELIVERED PIPELINE SOURCES HASH-BOUND",
        "reproducibility_exception": (
            "Inventories and mass properties reproduce byte-for-byte; OCCT AP242 presentation-style "
            "entity ordering changes file bytes across identical seeded builds."
        ),
    }
    try:
        import cadquery  # type: ignore

        dependencies["cadquery_version"] = getattr(cadquery, "__version__", "UNKNOWN")
    except Exception as exc:  # pragma: no cover - recorded instead of hidden
        dependencies["cadquery_version"] = f"NOT IMPORTABLE: {exc}"
    try:
        import OCP  # type: ignore

        dependencies["ocp_version"] = getattr(OCP, "__version__", "UNKNOWN")
    except Exception as exc:  # pragma: no cover
        dependencies["ocp_version"] = f"NOT IMPORTABLE: {exc}"
    write_json(build_dir / "DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json", dependencies)
    write_text(
        build_dir / "BUILD_AND_VALIDATION_INSTRUCTIONS.md",
        """# Build and Validation Instructions

Status: **DEVELOPMENTAL - NOT A PRODUCTION RELEASE**

## Rebuild-source location

The extracted handoff is self-contained under:

- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/r2_source/`
- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/input/`
- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/forward_arm_repack/`

The pinned CadQuery/OCP runtime itself is not embedded; use the exact runtime described in
`DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json`.

## Build

First change directory to the delivered rebuild-source root, then invoke the pinned CAD Python runtime:

```powershell
Set-Location 11_BUILD_AND_REPRODUCIBILITY/rebuild_source
$env:PYTHONHASHSEED='0'
<CAD_PYTHON> work/r2_source/short14_external_buoy_build.py --state PAIR --render
```

## Frozen-candidate validation

```powershell
<CAD_PYTHON> work/r2_source/short14_validate_endpoints.py
<CAD_PYTHON> work/r2_source/short14_motion_gate.py --mode five --workers 2 --output-name extraction_test_five_angle
<CAD_PYTHON> work/r2_source/short14_motion_gate.py --mode full --workers 2 --output-name extraction_test_full_motion
```

Use fresh output names; never overwrite historical accepted or failed evidence directories.

## Acceptance discipline

The build must exit zero; both inventories and mass properties must reconcile; OCP/XCAF reimport,
endpoint, five-angle, and full-motion semantic results must pass.  Do not claim byte-identical AP242
reproduction: identical seeded builds currently vary in presentation-style entity order and SHA-256.
That defect remains a non-release exception.
""",
    )
    write_text(
        build_dir / "CONTROLLED_STATUS_TRANSITION_PROCEDURE.md",
        """# Controlled Post-Generation Status Transition Procedure

Status: **REQUIRED FOR REVIEWED HANDOFF REPRODUCTION**

`complete_product_definition_reports.py` is deliberately a **pre-review template generator**.  It
creates conservative `TEMPLATE - PENDING` states and must never be used by itself to claim that the
executive artifacts, reviews, extraction, or delivery have passed.

## Ordered evidence states

1. Generate reports and per-part artifacts, stage the byte-verified source/CAD/validation trees, then
   generate and render-check the PPTX and PDF.
2. Run `validate_complete_product_definition.py`.  Only a zero-exit audit may transition the internal
   package-review rows to PASS for the non-release package.
3. Run `freeze_independent_review_packet.py`; provide that manifest-bound packet to a fresh-context
   reviewer.  Record the review result and findings without changing the frozen candidate.
4. Correct every package CRITICAL/MAJOR/MINOR finding, rerun affected checks, regenerate the dependency
   inventory via `stage_complete_product_definition.py`, re-audit, re-freeze, and return it for closure.
5. Run `finalize_complete_product_definition.py` to create a preliminary ZIP.  Extract it to a new clean
   directory and run `verify_extracted_complete_product_definition.py` before any rebuild output is made.
6. From the extracted `11_BUILD_AND_REPRODUCIBILITY/rebuild_source` root, rebuild the PAIR and rerun
   endpoint, five-angle, and full-motion gates with fresh output names.  Compare the rebuilt inventories,
   mass properties, occurrence counts, and semantic gate results to the frozen evidence.  Do not claim
   AP242 byte identity.
7. Add the extraction/rebuild audit only after it passes; update traceability/review ledgers to the actual
   evidence state; re-run the internal audit and independent status closure; then regenerate final hashes
   and the deterministic ZIP.  A final clean integrity extraction must match every manifest entry exactly.

All status edits are evidence transitions, not product-release waivers.  Product release remains FAIL
while the non-release exception report lists open external, manufacturing, and physical gates.
""",
    )


def make_review_placeholders() -> None:
    review = ensure_dir(OUT / "10_REVIEWS")
    write_text(
        review / "INTERNAL_REVIEW_REPORT.md",
        """# Internal Overall Review

Status: **PENDING CANDIDATE ARTIFACT FREEZE**

The internal review is performed after CAD, reports, part exports, renderings, and executive artifacts
are assembled.  Findings and closure evidence are written here before package freeze.
""",
    )
    write_text(
        review / "INDEPENDENT_REVIEW_REPORT.md",
        """# Independent Fresh-Context Review

Status: **PENDING**

A separate fresh-context agent receives only the neutral frozen review packet after the candidate is
assembled.  Its findings and closure disposition replace this placeholder before final package freeze.
""",
    )


def main() -> None:
    for required in (
        STOWED_STEP,
        DEPLOYED_STEP,
        STOWED_INVENTORY,
        DEPLOYED_INVENTORY,
        MASS_PATH,
        ENDPOINT_PATH,
        FIVE_PATH,
        FULL_PATH,
    ):
        if not required.is_file():
            raise FileNotFoundError(required)

    stowed = load_json(STOWED_INVENTORY)
    deployed = load_json(DEPLOYED_INVENTORY)
    mass = load_json(MASS_PATH)
    endpoint = load_json(ENDPOINT_PATH)
    five = load_json(FIVE_PATH)
    full = load_json(FULL_PATH)
    if endpoint.get("disposition") != "PASS":
        raise RuntimeError("Frozen endpoint gate is not PASS")
    if five.get("disposition") != "PASS" or full.get("disposition") != "PASS":
        raise RuntimeError("Frozen motion gate is not PASS")
    if len(stowed["occurrences"]) != len(deployed["occurrences"]):
        raise RuntimeError("Endpoint occurrence counts do not match")

    make_bom_and_design_basis(stowed, deployed)
    make_analysis_reports(stowed, deployed, mass, endpoint, five, full)
    make_interface_documents(stowed)
    make_screenshot_report(full)
    make_manufacturing_and_verification(stowed)
    make_risk_and_fmea(gas_capacity())
    make_governance_and_release(stowed, endpoint, five, full)
    make_build_records()
    make_review_placeholders()
    print(
        json.dumps(
            {
                "status": STATUS,
                "output": rel(OUT),
                "unique_parts": len(stowed["parts"]),
                "occurrences_per_state": len(stowed["occurrences"]),
                "stowed_step_sha256": sha256(STOWED_STEP),
                "deployed_step_sha256": sha256(DEPLOYED_STEP),
                "files_written": len(list(OUT.rglob("*"))),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
