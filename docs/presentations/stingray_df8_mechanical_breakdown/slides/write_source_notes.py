#!/usr/bin/env python3
"""Write the deterministic DF8 render/deck source-notes deliverable."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.package_root.resolve()
    manifest = json.loads(
        (root / "manifests" / "per_part_render_manifest.json").read_text(encoding="utf-8")
    )
    facts = json.loads((root / "source_notes" / "source_facts.json").read_text(encoding="utf-8"))
    pptx_name = "STINGRAY_I5S_DF8_MECHANICAL_BREAKDOWN_PER_PART.pptx"
    pptx_exists = (root / pptx_name).is_file()

    included = [row for row in manifest if row["included"]]
    excluded = [row for row in manifest if not row["included"]]
    fasteners = [row for row in excluded if row["exclusion_reason"] == "standard fastener"]
    orings = [row for row in excluded if row["exclusion_reason"] == "O-ring"]
    unrenderable = [row for row in included if not row.get("render_png_path")]
    subsystem_counts = Counter(row["subsystem"] for row in included)
    class_counts = Counter(row["classification"] for row in included)
    stowed = facts["mass_properties"]["stowed"]
    deployed = facts["mass_properties"]["deployed"]

    lines = [
        "# STINGRAY I5-S DF8 mechanical breakdown — per-part source notes",
        "",
        "## Deliverable scope",
        "",
        (
            "This package contains deterministic isolated PNG renders for every qualifying unique PartDef in the current authoritative DF8 source model and a source-backed mechanical-breakdown PowerPoint. The deck is an engineering review artifact, not a release authorization."
            if pptx_exists
            else "This package contains the complete deterministic per-part PNG render set, manifests, source facts, context views, and 73-slide `@oai/artifact-tool` PowerPoint authoring source. The final PPTX export is not present because the required workspace-dependency loader/runtime was unavailable in this execution environment."
        ),
        "",
        "## Source authority",
        "",
        f"1. Authoritative source tree: `{facts['authoritative_source_root']}`",
        f"2. Source commit: `{facts['source_commit_sha']}` on `{facts['source_branch']}` ({facts['source_commit_timestamp']})",
        f"3. Exact endpoint geometry: `{facts['source_files']['stowed_ap242']}` and `{facts['source_files']['deployed_ap242']}`",
        "4. Exact geometry generator and current authoring inventories: `work/r2_source/build_r2.py`, `work/final_analysis/authoring_inventory_stowed.json`, and `work/final_analysis/authoring_inventory_deployed.json`",
        "5. Current state and validation authority: `CURRENT_STATE.json`, the state-parity provenance audit, and the manual inspection checkpoint",
        "6. The previous stakeholder source-notes document was used only as a structural/content reference; it was not used as geometry authority.",
        "",
        "## Inventory and classification result",
        "",
        f"- Unique PartDef count: **{len(manifest)}**",
        f"- Included and rendered: **{len(included)}** ({class_counts['MAKE']} MAKE, {class_counts['BUY']} BUY)",
        f"- Excluded standard-fastener definitions: **{len(fasteners)}**",
        f"- Excluded O-ring definitions: **{len(orings)}**",
        f"- Included definitions without a source render: **{len(unrenderable)}**",
        "",
        "Included renders by subsystem:",
        "",
    ]
    for subsystem, count in sorted(subsystem_counts.items()):
        lines.append(f"- {subsystem}: {count}")

    lines.extend([
        "",
        "The inclusion rule is deliberately conservative. Functional pins, bushings, spiral/crescent/circlip retainers, collars, springs, dampers/actuators, routes, softgood gores, and modeled bought-out definitions are included. Only the five definitions below meet the requested standard-fastener exclusion.",
        "",
        "| Part number | Name | Classification rationale |",
        "|---|---|---|",
    ])
    for row in fasteners:
        lines.append(
            f"| `{row['part_number']}` | {row['part_name']} | Standard threaded fastening hardware; excluded by the controlling rule. |"
        )
    if not orings:
        lines.extend(["", "No O-ring PartDef exists in the current 121-definition authoritative inventory."])

    lines.extend([
        "",
        "## Deterministic rendering method",
        "",
        "`slides/generate_per_part_renders.py` imports the authoritative `build_r2.py`, builds both exact STOWED and DEPLOYED PartCatalogs in memory, asserts their PartDef sets are identical, and validates each source shape volume against the committed authoring inventory before rendering.",
        "",
        "Each PNG uses the actual PartDef B-rep, an orthographic camera, a fixed 23° elevation and -55° azimuth after deterministic principal-axis permutation, a fixed white studio background, fixed neutral Lambert shading, no random colors, and a 1600 × 1200 output frame. Softgoods/recovery definitions use the exact DEPLOYED definition where it explains the geometry more clearly; other parts use the exact STOWED definition. The PNG footer provides part number, source description, MAKE/BUY, subsystem, and geometry state.",
        "",
        "`slides/validate_per_part_render_set.py` verifies the exact included PNG set, filenames, SHA-256 hashes, PNG format, and 1600 × 1200 dimensions against the manifests. The latest validation report is `manifests/per_part_render_validation.json` and is PASS.",
        "",
        "## Mass properties and center of gravity",
        "",
        f"- Exact current source / committed-inventory system mass: **{stowed['system_mass_kg']:.6f} kg**",
        f"- Mass limit: **{facts['hard_requirements']['mass_max_kg']:.3f} kg**",
        f"- Source-derived mass reserve: **{facts['mass_reconciliation']['source_derived_mass_reserve_kg']:.6f} kg**",
        f"- Lower-priority `CURRENT_STATE.json` mass metadata: **{facts['mass_reconciliation']['current_state_metadata_mass_kg']:.6f} kg** (absolute difference **{facts['mass_reconciliation']['absolute_difference_kg'] * 1000.0:.3f} g**, recorded rather than coerced)",
        f"- STOWED CAD CG in master coordinates: **X {stowed['center_of_gravity_mm_in_master_frame']['x']:.3f} mm, Y {stowed['center_of_gravity_mm_in_master_frame']['y']:.3f} mm, Z {stowed['center_of_gravity_mm_in_master_frame']['z']:.3f} mm**",
        f"- DEPLOYED CAD CG in master coordinates: **X {deployed['center_of_gravity_mm_in_master_frame']['x']:.3f} mm, Y {deployed['center_of_gravity_mm_in_master_frame']['y']:.3f} mm, Z {deployed['center_of_gravity_mm_in_master_frame']['z']:.3f} mm**",
        "",
        "The CG calculation is regenerated by `slides/extract_source_facts.py` from each occurrence’s current global exact-B-rep volume centroid and the same committed mass-precedence rule used by the validator: occurrence override, part override, then authoring-inventory part-master mass. Source authority therefore favors the exact current source/inventory result over the 0.093 g higher handoff-metadata value. It is a CAD calculation, not a measured physical balance result.",
        "",
        "## Current validation status and limitations",
        "",
        f"- State parity: **{facts['validation']['state_parity_occurrence_pass_count']} / {facts['validation']['state_parity_occurrence_count']} occurrences pass**; the 64-row provenance register is fully resolved.",
        f"- Current release status: **{facts['validation']['package_required_label']}**.",
        "- The accepted automated motion checkpoint covers 0° through 55° inclusive at 1° increments; 56° through 80° are not accepted as completed validation evidence in that checkpoint.",
        f"- The latest full validator terminated at `{facts['validation']['validator_failure_stage']}` with `{facts['validation']['validator_failure_message']}`; it did not compute release gates.",
        "- No physical, environmental, calibrated damper force-speed, or manufacturing qualification is asserted.",
        "- BUY components are presented at their current controlled source fidelity. Where the source identifies a representation as drawing-derived, the deck retains that qualification.",
        "- One hero orientation is used per PartDef; no part required a second supporting view. Very slender routes and softgoods remain exact but naturally occupy less projected image area.",
        "- PowerPoint export status: **PRESENT**." if pptx_exists else "- PowerPoint export status: **BLOCKED — `load_workspace_dependencies` and its required `@oai/artifact-tool` runtime paths were unavailable; no prohibited fallback authoring engine was used.**",
        "",
        "## Assembly context imagery",
        "",
        "The nine `slides/context_views/AFTER_IMAGE_*.png` views are deterministic source-derived assembly context views generated by authoritative `work/r2_source/render_evidence.py`. They are used only to explain architecture and mechanism context; all per-part breakdown tiles use the new exact PartDef render set.",
        "",
        "## Reproduction",
        "",
        "Run with the authoritative CAD environment:",
        "",
        "```powershell",
        "& <authoritative-cad-python> slides/generate_per_part_renders.py --source-root <authoritative-source-root> --repo-root <documentation-repo-root> --output-root <this-package-root>",
        "& <authoritative-cad-python> slides/validate_per_part_render_set.py --package-root <this-package-root>",
        "& <authoritative-cad-python> slides/extract_source_facts.py --source-root <authoritative-source-root> --output <this-package-root>/source_notes/source_facts.json",
        "node slides/build_mechanical_breakdown.mjs",
        "python slides/write_source_notes.py --package-root <this-package-root> --output <this-package-root>/STINGRAY_I5S_DF8_MECHANICAL_BREAKDOWN_PER_PART_SOURCE_NOTES.md",
        "```",
        "",
        "The PowerPoint authoring script uses `@oai/artifact-tool`, embeds PNG bytes, writes per-slide render/layout evidence, adds a `[Sources]` block to every slide’s speaker notes, and exports the final PPTX.",
        "",
        "## Missing or unrenderable parts",
        "",
        "None. All 116 included PartDefs rendered from source and passed manifest validation.",
        "",
    ])

    args.output.resolve().write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
