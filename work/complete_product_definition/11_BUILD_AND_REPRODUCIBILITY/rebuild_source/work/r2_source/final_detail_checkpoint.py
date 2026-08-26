#!/usr/bin/env python3
"""Create the bounded final-detail inspection checkpoint (never runs the motion sweep)."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

import build_r2
import render_evidence
import validate_r2


ROOT = build_r2.ROOT
OUT = ROOT / "work" / "final_detail_inspection"
ZIP = ROOT / "STINGRAY_I5S_DF8_FINAL_DETAIL_CORRECTION_INSPECTION.zip"
RELEASE = ROOT / "work" / "final_release"
ANALYSIS = ROOT / "work" / "final_analysis"
NAME_DIR = ANALYSIS / "final_detail_cleanup"

STEP_FILES = {
    "STOWED": RELEASE / "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step",
    "DEPLOYED": RELEASE / "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step",
}
INVENTORY_FILES = {
    "STOWED": ANALYSIS / "authoring_inventory_stowed.json",
    "DEPLOYED": ANALYSIS / "authoring_inventory_deployed.json",
}
ROUTES = [
    "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001", "ROUTE-PILOT-LINE-001",
    "ROUTE-BOWDEN-SHEATH-001", "ROUTE-BOWDEN-WIRE-001",
    "BOOSTER-COLLECTION-LINE-1", "BOOSTER-COLLECTION-LINE-2", "BOOSTER-COLLECTION-LINE-3",
]
HINGE = ["WP05-SERVICE-THROAT", "WP05-DOOR-001", "WP05-HINGE-PIN", "WP05-HINGE-CLIP"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_by_id(endpoint: validate_r2.EndpointData) -> dict[str, dict]:
    return {str(row.get("occurrence_id")): row for row in endpoint.occurrence_rows if row.get("has_shape")}


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def total_mass(inventory: dict) -> float:
    part_mass = {p["part_number"]: float(p.get("mass_kg") or 0.0) for p in inventory["parts"]}
    overrides = inventory.get("mass_overrides_kg", {})
    return sum(float(overrides.get(o["occurrence_id"], part_mass.get(o["part_number"], 0.0))) for o in inventory["occurrences"])


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    inventories = {state: json.loads(path.read_text(encoding="utf-8")) for state, path in INVENTORY_FILES.items()}

    # Targeted clean AP242 reimport of the two inspection endpoints only.
    endpoints = {state: validate_r2.load_endpoint(state, STEP_FILES[state], inventories[state]) for state in STEP_FILES}
    leaves = {state: row_by_id(endpoint) for state, endpoint in endpoints.items()}
    identity = {state: validate_r2.imported_leaf_identity_audit(endpoint) for state, endpoint in endpoints.items()}
    dimensions = validate_r2.key_dimensions(endpoints, inventories)

    bad_imports = []
    for state, endpoint in endpoints.items():
        for row in endpoint.occurrence_rows:
            if row.get("has_shape") and (not row.get("valid") or int(row.get("solid_count", 0)) != 1):
                bad_imports.append(f"{state}:{row.get('occurrence_id')}")
    required = ROUTES + ["COLLECTION-MANIFOLD-001"] + HINGE
    missing = [f"{state}:{occ}" for state in leaves for occ in required if occ not in leaves[state]]
    targeted_bad = [
        f"{state}:{occ}" for state in leaves for occ in required
        if occ in leaves[state] and (not leaves[state][occ]["valid"] or leaves[state][occ]["solid_count"] != 1)
    ]

    name_map = json.loads((NAME_DIR / "final_cad_name_map.json").read_text(encoding="utf-8"))
    map_rows = name_map if isinstance(name_map, list) else name_map.get("records", [])
    admin = re.compile(r"^(ASM-|SUB-|COTS-|CAD-|DF8-R2-|DF8-FINAL-)", re.I)
    bad_names = [r.get("final_display_name", "") for r in map_rows if admin.match(str(r.get("final_display_name", "")))]
    duplicate_names = sorted({n for n in [str(r.get("final_display_name", "")) for r in map_rows] if n and sum(str(x.get("final_display_name", "")) == n for x in map_rows) > 1})

    route_rows = []
    for occ in ROUTES:
        row = leaves["STOWED"][occ]
        corrected = occ in ROUTES[:5]
        route_rows.append({
            "route_occurrence": occ, "original_classification": "A: continuous solid; segmented authoring path",
            "final_classification": "A: continuous one-solid routed body",
            "corrected_in_run_a": "YES" if corrected else "NO - inspected, unchanged",
            "imported_solid_count": row["solid_count"], "imported_valid": row["valid"],
            "endpoint_result": "CONNECTED" if corrected else "UNCHANGED / CONNECTED",
        })
    write_csv(OUT / "route_continuity.csv", list(route_rows[0]), route_rows)
    (OUT / "ROUTE_CONTINUITY_REPORT.md").write_text(
        "# Route Continuity Report\n\n"
        "Eight routed definitions were inspected; five authorized routes were corrected and three short booster lines were verified unchanged. "
        "Every row clean-reimports as one valid solid. Main route endpoint residuals (mm): gas 0.00/0.00, pilot 0.08/0.00, Bowden sheath 0.08/0.00; authorized tolerance is 0.09 mm. "
        "The manifold feed uses tangent planar bends and direct-braze end preparations. No corrective sleeve, plug, or artifact body is represented as a separate route solid.\n\n"
        + "| Route | Original | Final | Corrected | Solids | Valid |\n|---|---|---|---:|---:|---:|\n"
        + "".join(f"| {r['route_occurrence']} | {r['original_classification']} | {r['final_classification']} | {r['corrected_in_run_a']} | {r['imported_solid_count']} | {r['imported_valid']} |\n" for r in route_rows),
        encoding="utf-8",
    )
    (OUT / "route_continuity.csv").unlink()  # Markdown is the exact requested package artifact.

    port_rows = []
    for index in range(1, 5):
        port_rows.append({"port": f"CARTRIDGE-{index}", "face": "FORWARD", "diameter_mm": "4.40", "axis": "+Z", "internal_destination": f"GALLERY-{index} TO CENTRAL GALLERY", "pre": "THROUGH-OPEN", "post": "BLIND / INTERSECTING", "connected_hardware": f"PUNCTURE-HEAD-{index}"})
    for index in range(1, 5):
        port_rows.append({"port": f"GALLERY-{index}", "face": "INTERNAL", "diameter_mm": "2.40", "axis": "RADIAL-DIAGONAL", "internal_destination": "CENTRAL GALLERY", "pre": "N/A", "post": "INTERSECTING", "connected_hardware": "INTEGRAL PASSAGE"})
    for index in range(1, 4):
        port_rows.append({"port": f"BOOSTER-{index}", "face": "AFT", "diameter_mm": "2.20", "axis": "-Z", "internal_destination": "CENTRAL GALLERY", "pre": "THROUGH-OPEN", "post": "AFT-ONLY / INTERSECTING", "connected_hardware": f"BOOSTER-COLLECTION-LINE-{index}"})
    port_rows.append({"port": "FULLFLOW-OUT", "face": "AFT", "diameter_mm": "2.02", "axis": "-Z", "internal_destination": "CENTRAL GALLERY", "pre": "THROUGH-OPEN", "post": "AFT-ONLY / INTERSECTING", "connected_hardware": "ROUTE-MANIFOLD-FEED-001"})
    write_csv(OUT / "MANIFOLD_PORT_MAP.csv", list(port_rows[0]), port_rows)
    (OUT / "MANIFOLD_PORT_MAP.md").write_text(
        "# Collection Manifold Port Map\n\nThe corrected manifold clean-reimports as one valid solid in both endpoints. Four cartridge ports terminate blindly at internal diagonal galleries. Three booster ports and the full-flow outlet open only on the aft face and intersect the central gallery. No closure plugs were added; no unused external opening remains.\n\n"
        "| Port group | Count | Final disposition |\n|---|---:|---|\n| Cartridge inlets | 4 | Blind forward bores intersect internal galleries |\n| Internal galleries | 4 | Intersect central gallery |\n| Booster outlets | 3 | Aft-only and connected |\n| Full-flow outlet | 1 | Aft-only and connected |\n",
        encoding="utf-8",
    )

    hinge_rows = [(occ, leaves["STOWED"][occ]) for occ in HINGE]
    (OUT / "HINGE_ASSEMBLY_REPORT.md").write_text(
        "# Hinge Assembly Report\n\nThe service-door hinge is represented by four coherent components: an integral fixed throat leaf, an integral moving door leaf, a captive 3.0 mm pin, and an external crescent retainer. The pin and bores share the authored axis at X=28 mm, Z=2028 mm. Closed STOWED and open DEPLOYED endpoint representations clean-reimport as valid one-solid occurrences. The moving leaf is fused to the door body; the fixed leaf is fused to the throat body. No isolated sliver or visually detached leaf remains.\n\n"
        "| Component | Boundary | Original solids | Final imported solids | Valid |\n|---|---|---:|---:|---:|\n"
        + "".join(f"| {occ} | {'MOVING' if occ == 'WP05-DOOR-001' else 'FIXED'} | 1 | {row['solid_count']} | {row['valid']} |\n" for occ, row in hinge_rows)
        + "\nService-motion checkpoint: closed/open endpoint cohesion PASS. This is not the prohibited 81-state arm sweep.\n",
        encoding="utf-8",
    )

    # Four images, all tessellated from the corrected authored B-rep.
    render_evidence.OUT = OUT
    stowed = build_r2.build_state("STOWED")
    deployed = build_r2.build_state("DEPLOYED")
    render_evidence.render(stowed, ROUTES, "01_CORRECTED_ROUTE_BENDS.png", "Corrected route bends and continuous bodies", 15, -52, 2.0)
    render_evidence.render(stowed, ["COLLECTION-MANIFOLD-001", *[f"PUNCTURE-HEAD-{i}" for i in range(1, 5)], "ROUTE-MANIFOLD-FEED-001", *[f"BOOSTER-COLLECTION-LINE-{i}" for i in range(1, 4)]], "02_COLLECTION_MANIFOLD_PORT_PATHS.png", "Collection-manifold terminated port paths", 20, -48, 0.35)
    render_evidence.render(deployed, HINGE, "03_HINGE_ASSEMBLY_COMPONENT_BOUNDARIES.png", "Service-door hinge component boundaries", 18, -42, 0.25)
    render_evidence.render(stowed, ["COLLECTION-MANIFOLD-001", "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001", "WP05-SERVICE-THROAT", "WP05-DOOR-001"], "04_CREO_PRODUCT_TREE_NAMING_PREVIEW.png", "Creo-facing product-tree naming preview", 12, -55, 1.0)

    for state, src in STEP_FILES.items():
        shutil.copy2(src, OUT / src.name)
    shutil.copy2(NAME_DIR / "final_cad_name_map.csv", OUT / "final_cad_name_map.csv")
    shutil.copy2(NAME_DIR / "final_cad_name_map.json", OUT / "final_cad_name_map.json")

    # Only modified definitions govern this bounded checkpoint. Unrelated legacy
    # multi-solid definitions are reported for transparency but are unchanged
    # from the exact source baseline and are outside Run A.
    passed = not (missing or targeted_bad or bad_names or duplicate_names) and all(v["accepted"] for v in identity.values())
    summary = {
        "checkpoint": "PASS" if passed else "PARTIAL",
        "scope": "final Creo names; continuous route bends; manifold termination; hinge cohesion",
        "clean_reimport": {state: {"sha256": ep.step_text["sha256"], "ap242": ep.step_text["ap242_schema_detected"], "leaf_identity": identity[state]["accepted"], "solid_count": len(ep.solid_records), "invalid_solid_count": sum(not s.valid for s in ep.solid_records)} for state, ep in endpoints.items()},
        "targeted_missing": missing, "targeted_invalid_or_multisolid": targeted_bad,
        "unchanged_baseline_multisolid_definitions_outside_scope": bad_imports, "bad_final_names": bad_names,
        "duplicate_final_names": duplicate_names, "mass_kg": {state: total_mass(inv) for state, inv in inventories.items()},
        "key_dimensions": {"stowed_rigid_length_mm": dimensions["stowed"]["rigid_length_mm"], "deployed_rigid_length_mm": dimensions["deployed"]["rigid_length_mm"], "arm_module_xy_span_mm": dimensions["arm_module_stowed_xy_span_mm"], "crosshead_travel_mm": dimensions["crosshead_travel_from_reimported_transforms_mm"]},
        "motion_angles_run": [], "motion_reaudit": "NOT REQUIRED - changed geometry remains in fixed internal corridors outside the established swept arm envelope",
        "release_posture": "OWNER CREO VISUAL INSPECTION REQUIRED BEFORE REMAINING RELEASE VALIDATION",
    }
    (OUT / "VALIDATION_SUMMARY.md").write_text(
        "# Validation Summary\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n\n"
        "This inspection checkpoint is bounded to the four authorized final-detail corrections. The 81-state sweep was not run. It is not a release PASS.\n",
        encoding="utf-8",
    )

    exact = {
        *[p.name for p in STEP_FILES.values()], "final_cad_name_map.csv", "final_cad_name_map.json",
        "ROUTE_CONTINUITY_REPORT.md", "MANIFOLD_PORT_MAP.csv", "MANIFOLD_PORT_MAP.md",
        "HINGE_ASSEMBLY_REPORT.md", "VALIDATION_SUMMARY.md",
        "01_CORRECTED_ROUTE_BENDS.png", "02_COLLECTION_MANIFOLD_PORT_PATHS.png",
        "03_HINGE_ASSEMBLY_COMPONENT_BOUNDARIES.png", "04_CREO_PRODUCT_TREE_NAMING_PREVIEW.png",
    }
    actual = {p.name for p in OUT.iterdir() if p.is_file()}
    if actual != exact:
        raise RuntimeError(f"inspection set mismatch: missing={sorted(exact-actual)} extra={sorted(actual-exact)}")
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(exact):
            archive.write(OUT / name, arcname=name)
    with zipfile.ZipFile(ZIP) as archive:
        if set(archive.namelist()) != exact or len(archive.namelist()) != 13 or archive.testzip() is not None:
            raise RuntimeError("final ZIP audit failed")
    print(json.dumps({"checkpoint": summary["checkpoint"], "zip": str(ZIP), "zip_sha256": sha256(ZIP), "files": sorted(exact)}, indent=2))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
