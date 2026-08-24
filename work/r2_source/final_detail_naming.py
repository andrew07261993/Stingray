#!/usr/bin/env python3
"""Final Creo-facing naming layer with reversible legacy traceability."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ADMIN_TOKEN = re.compile(r"(?:^|_)(?:DF8|R2|WP0[1-5]|FINAL)(?:_|$)", re.I)

ASSEMBLY_SEGMENT_NAMES = {
    "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY": "Forward_Body_Assembly",
    "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY/190_MANDATORY_HARDWARE_ASSY": "Forward_Mandatory_Hardware_Assembly",
    "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY": "Arm_Activation_Powertrain_Assembly",
    "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/331_ARM_1_ASSY": "Arm_Deployment_Assembly_01",
    "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/332_ARM_2_ASSY": "Arm_Deployment_Assembly_02",
    "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/333_ARM_3_ASSY": "Arm_Deployment_Assembly_03",
    "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/390_MANDATORY_HARDWARE_ASSY": "Powertrain_Mandatory_Hardware_Assembly",
    "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY": "Aft_Service_Closure_Assembly",
    "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY/590_MANDATORY_HARDWARE_ASSY": "Aft_Mandatory_Hardware_Assembly",
}

EXPLICIT_CUSTOM_NAMES = {
    "DF8-R2-NOSE-001": "Penetrator_Nose_W",
    "DF8-R2-BALLAST-001": "Forward_Ballast_W",
    "DF8-R2-FWD-SHELL-001": "Forward_Shell_TI",
    "DF8-R2-COLLECTION-MANIFOLD-001": "Collection_Manifold_SS",
    "DF8-R2-CROSSHEAD-001": "Common_Crosshead_SS",
    "DF8-R2-ARM-BLADE-001": "Arm_Blade_TI",
    "DF8-R2-PIVOT-CARRIER-001": "Pivot_Carrier_TI",
    "DF8-R2-WATER-TRIGGER-HSG-001": "Water_Trigger_Housing_AC",
    "DF8-FINAL-MANIFOLD-FULLFLOW-FEED-001": "Collection_Manifold_Fullflow_Feed_SS",
    "DF8-R2-BOOSTER-COLLECTION-LINE-001": "Booster_Collection_Line_SS",
    "DF8-FINAL-GAS-MAIN-001": "Gas_Main_SS",
    "DF8-FINAL-PILOT-LINE-001": "Pilot_Line_SS",
    "DF8-FINAL-BOWDEN-SHEATH-001": "Bowden_Sheath",
    "DF8-FINAL-BOWDEN-WIRE-001": "Bowden_Wire_SS",
    "WP05-SERVICE-THROAT-R2": "Fixed_Hinge_Leaf_Service_Throat_TI",
    "WP05-DOOR-R2": "Moving_Hinge_Leaf_Aft_Door_TI",
    "WP05-HINGE-PIN-R2": "Aft_Door_Hinge_Pin_SS",
    "WP05-HINGE-CRESCENT-RING-R2": "Aft_Door_Hinge_Retainer_SS",
}


def _words(value: str) -> str:
    cooked = value.replace("—", " ").replace("–", " ").replace("/", " ")
    cooked = re.sub(r"\b(?:DF8|R2|WP0[1-5]|FINAL)\b", " ", cooked, flags=re.I)
    cooked = re.sub(r"[^A-Za-z0-9.+-]+", "_", cooked).strip("_")
    return "_".join(part.capitalize() if not part.isupper() else part for part in cooked.split("_") if part)


def _material_code(material: str) -> str:
    key = material.upper()
    if "TPU" in key:
        return "TPU"
    if "UHMWPE" in key or "HMPE" in key:
        return "HMPE"
    if "PTFE" in key:
        return "PTFE"
    if "PEEK" in key:
        return "PEEK"
    if "ACETAL" in key:
        return "AC"
    if "TUNGSTEN" in key:
        return "W"
    if "TITANIUM" in key or "TI-" in key:
        return "TI"
    if "ALUMIN" in key:
        return "AL"
    if "STAINLESS" in key or "17-4" in key or "1.4310" in key or "316" in key:
        return "SS"
    if "STEEL" in key:
        return "ST"
    return ""


def _actual_part_number(part_number: str) -> str:
    return re.sub(r"-ROD-CHILD$", "", part_number, flags=re.I)


def _cots_name(part: Any) -> str:
    pn = _actual_part_number(part.part_number)
    if part.part_number == "LELAND-81121":
        return "Leland_CO2_Cartridge_81121"
    if part.part_number == "V80040":
        return "Halkey_Roberts_Water_Bobbin_V80040"
    if part.part_number == "SS-CHS2-1":
        return "Swagelok_Check_Valve_SS-CHS2-1"
    if part.part_number == "ROTOR-CLIP-DC-4SS":
        return "Rotor_Clip_Retaining_Ring_DC-4SS"
    if part.part_number.startswith("GS-19-50-V4A-B8-B8"):
        kind = "Gas_Spring_Rod" if part.part_number.endswith("ROD-CHILD") else "Gas_Spring"
        return f"ACE_{kind}_{pn}"
    if part.part_number.startswith("HBD-15-25-AA-P"):
        kind = "Hydraulic_Damper_Rod" if part.part_number.endswith("ROD-CHILD") else "Hydraulic_Damper"
        return f"ACE_{kind}_{pn}"
    if part.part_number == "GN-615.3-M3-KN-PFB":
        return "JW_Winco_Ball_Plunger_GN-615.3-M3-KN-PFB"
    maker = _words(part.manufacturer).split("_")[0] or "COTS"
    return f"{maker}_{pn}"


def _creo_safe(full_name: str) -> tuple[str, str]:
    if len(full_name) <= 31:
        return full_name, ""
    digest = hashlib.sha256(full_name.encode("utf-8")).hexdigest()[:8].upper()
    return f"{full_name[:22].rstrip('_')}_{digest}", "Deterministic 31-character Creo filename limit"


def display_assembly_path(legacy_path: str) -> str:
    legacy_path = legacy_path.strip().strip("/")
    if legacy_path in ASSEMBLY_SEGMENT_NAMES:
        if "/" not in legacy_path:
            return ASSEMBLY_SEGMENT_NAMES[legacy_path]
        parent = legacy_path.rsplit("/", 1)[0]
        return f"{display_assembly_path(parent)}/{ASSEMBLY_SEGMENT_NAMES[legacy_path]}"
    raise KeyError(f"No final assembly name for legacy path: {legacy_path}")


def apply_final_names(builder: Any) -> None:
    used: Counter[str] = Counter()
    for part in builder.catalog.parts.values():
        if part.make_buy == "BUY":
            full = _cots_name(part)
            actual = _actual_part_number(part.part_number)
        else:
            full = EXPLICIT_CUSTOM_NAMES.get(part.part_number, "")
            if not full:
                base = _words(part.description)
                code = _material_code(part.material)
                full = f"{base}_{code}" if code else base
            actual = ""
        full = re.sub(r"_+", "_", full).strip("_")
        used[full] += 1
        if used[full] > 1:
            full = f"{full}_{used[full]:02d}"
        if ADMIN_TOKEN.search(full):
            raise ValueError(f"Administrative token escaped into final display name: {full}")
        safe, reason = _creo_safe(full)
        part.final_display_name = full
        part.creo_safe_name = safe
        part.actual_part_number = actual
        part.traceability_property = f"LEGACY_ID={part.part_number};SOURCE_ID={part.part_number}"
        part.abbreviation_reason = reason

    grouped: dict[str, list[Any]] = defaultdict(list)
    for occurrence in builder.occurrences:
        grouped[occurrence.part_number].append(occurrence)
    for part_number, occurrences in grouped.items():
        part = builder.catalog.parts[part_number]
        ordered = sorted(occurrences, key=lambda item: item.occurrence_id)
        for index, occurrence in enumerate(ordered, start=1):
            suffix = f"_{index:02d}" if len(ordered) > 1 else ""
            occurrence.display_name = f"{part.final_display_name}{suffix}"
            occurrence.display_parent_path = display_assembly_path(occurrence.parent_path)


def name_records(builder: Any) -> list[dict[str, Any]]:
    subsystem_by_part: dict[str, set[str]] = defaultdict(set)
    count_by_part: Counter[str] = Counter()
    for occurrence in builder.occurrences:
        subsystem_by_part[occurrence.part_number].add(occurrence.display_parent_path.split("/", 1)[0])
        count_by_part[occurrence.part_number] += 1
    rows = []
    for part in sorted(builder.catalog.parts.values(), key=lambda item: item.final_display_name):
        count = count_by_part[part.part_number]
        rows.append({
            "legacy_id": part.part_number,
            "final_full_display_name": part.final_display_name,
            "creo_safe_name": part.creo_safe_name,
            "actual_part_number": part.actual_part_number,
            "make_buy": part.make_buy,
            "material": part.material,
            "subsystem": "; ".join(sorted(subsystem_by_part[part.part_number])),
            "occurrence_naming_rule": "base name" if count == 1 else f"base name + _01.._{count:02d}",
            "traceability_property": part.traceability_property,
            "abbreviation_reason": part.abbreviation_reason,
        })
    return rows


def write_name_maps(builder: Any, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = name_records(builder)
    csv_path = out_dir / "final_cad_name_map.csv"
    json_path = out_dir / "final_cad_name_map.json"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({"records": rows}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return csv_path, json_path


__all__ = [
    "ADMIN_TOKEN", "ASSEMBLY_SEGMENT_NAMES", "apply_final_names",
    "display_assembly_path", "name_records", "write_name_maps",
]
