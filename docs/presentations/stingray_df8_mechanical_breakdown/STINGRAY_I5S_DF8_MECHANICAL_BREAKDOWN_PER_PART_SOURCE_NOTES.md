# STINGRAY I5-S DF8 mechanical breakdown — per-part source notes

## Deliverable scope

This package contains deterministic isolated PNG renders for every qualifying unique PartDef in the current authoritative DF8 source model and a source-backed mechanical-breakdown PowerPoint. The deck is an engineering review artifact, not a release authorization.

## Source authority

1. Authoritative source tree: `C:/Users/ANDRE.ANDREWSPC/Documents/Codex/2026-08-23/stingray-i5-s-df8-state-parity`
2. Source commit: `61a58cbbccd0aae7a747b2a73046142cf1f44511` on `audit/state-parity-provenance` (2026-08-23T12:36:47-05:00)
3. Exact endpoint geometry: `work/final_release/STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step` and `work/final_release/STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step`
4. Exact geometry generator and current authoring inventories: `work/r2_source/build_r2.py`, `work/final_analysis/authoring_inventory_stowed.json`, and `work/final_analysis/authoring_inventory_deployed.json`
5. Current state and validation authority: `CURRENT_STATE.json`, the state-parity provenance audit, and the manual inspection checkpoint
6. The previous stakeholder source-notes document was used only as a structural/content reference; it was not used as geometry authority.

## Inventory and classification result

- Unique PartDef count: **121**
- Included and rendered: **116** (104 MAKE, 12 BUY)
- Excluded standard-fastener definitions: **5**
- Excluded O-ring definitions: **0**
- Included definitions without a source render: **0**

Included renders by subsystem:

- Arm deployment / activation: 39
- Body ejection / buoy extraction: 25
- Body structure: 10
- Gas / inflation path: 26
- Load path / recovery attachment: 12
- Water activation: 4

The inclusion rule is deliberately conservative. Functional pins, bushings, spiral/crescent/circlip retainers, collars, springs, dampers/actuators, routes, softgood gores, and modeled bought-out definitions are included. Only the five definitions below meet the requested standard-fastener exclusion.

| Part number | Name | Classification rationale |
|---|---|---|
| `SSCA-M3-8-A4-BL` | M3 X 8 CAPTIVE SOCKET CAP SCREW, DIN 912 | Standard threaded fastening hardware; excluded by the controlling rule. |
| `SSCF-M3-10-A4` | M3 X 10 FULL-THREAD SOCKET CAP SCREW, DIN 912 / ISO 4762 | Standard threaded fastening hardware; excluded by the controlling rule. |
| `SSCF-M3-6-A4` | M3 X 6 FULL-THREAD SOCKET CAP SCREW, DIN 912 / ISO 4762 | Standard threaded fastening hardware; excluded by the controlling rule. |
| `SSCL-M4-8-A4` | M4 X 8 FULL-THREAD LOW-HEAD SOCKET CAP SCREW, DIN 7984 | Standard threaded fastening hardware; excluded by the controlling rule. |
| `SSK-M3-6-A4-P80` | M3 X 6 SOCKET COUNTERSUNK SCREW, ISO 10642, PRECOTE 80 | Standard threaded fastening hardware; excluded by the controlling rule. |

No O-ring PartDef exists in the current 121-definition authoritative inventory.

## COTS and receiving-evidence traceability

`manifests/per_part_cots_traceability.json` and its CSV companion cover all 121 PartDefs. Each rendered part entry now states its COTS classification, vendor/manufacturer, vendor catalog part number, received-unit serial/lot/heat status, and Certificate of Conformance (CoC) status. MAKE parts are explicitly marked COTS N/A; they remain subject to drawing, material-certification, traveler, and build-record controls rather than supplier-COTS CoC control.

- COTS/BUY definition rows: **17** total; **12** rendered in the deck and **5** excluded standard-fastener definitions retained in the traceability manifest.
- Parent purchased line items: **15**; articulated child geometry rows governed by a parent purchased assembly: **2**.
- BUY rows with received serial/lot/heat evidence verified in this package: **0**.
- BUY rows with delivered-unit supplier CoC evidence verified in this package: **0**.
- Traceability-schema validation: **PASS**. This means the schema is complete and fail-closed; it does not mean COTS acceptance is complete.
- Receiving disposition: **COTS RECEIVING EVIDENCE INCOMPLETE — NOT RELEASED**. Record the supplier serial number where present, otherwise the lot/batch/heat identifier, and retain the delivered-item CoC before release.

Vendor catalog links identify the intended catalog item only. A catalog page, supplier quality-system certificate, packing slip, or generic material statement is not accepted as proof that the delivered unit came with its required CoC. The two articulated `*-ROD-CHILD` rows are not separate purchase lines; their identity and evidence inherit from the parent ACE assembly.

| PartDef | Vendor | Vendor catalog P/N | Serial / lot / heat | Delivered-item CoC | Receiving disposition |
|---|---|---|---|---|---|
| `GN-615.3-M3-KN-PFB` | JW Winco / Ganter | `GN 615.3-M3-KN-PFB` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `GS-19-50-V4A-B8-B8` | ACE Controls | `GS-19-50-V4A-B8-B8` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `GS-19-50-V4A-B8-B8-ROD-CHILD` | ACE Controls | `GS-19-50-V4A-B8-B8` | NOT PROVIDED — inherit from parent received assembly | NOT VERIFIED — inherit parent assembly CoC evidence | HOLD WITH PARENT — do not treat as a separately orderable line |
| `HBD-15-25-AA-P` | ACE Controls | `HBD-15-25-AA-P` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `HBD-15-25-AA-P-ROD-CHILD` | ACE Controls | `HBD-15-25-AA-P` | NOT PROVIDED — inherit from parent received assembly | NOT VERIFIED — inherit parent assembly CoC evidence | HOLD WITH PARENT — do not treat as a separately orderable line |
| `HDP-3-8-A1` | Accu | `HDP-3-8-A1` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `HEC-10-A4` | Accu | `HEC-10-A4` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `HTP-3-30-A1` | Accu | `HTP-3-30-A1` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `LELAND-81121` | Leland Gas Technologies | `81121` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `ROTOR-CLIP-DC-4SS` | Rotor Clip | `DC-4SS` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SS-CHS2-1` | Swagelok | `SS-CHS2-1` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SSCA-M3-8-A4-BL` | Accu | `SSCA-M3-8-A4-BL` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SSCF-M3-10-A4` | Accu | `SSCF-M3-10-A4` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SSCF-M3-6-A4` | Accu | `SSCF-M3-6-A4` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SSCL-M4-8-A4` | Accu | `SSCL-M4-8-A4` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `SSK-M3-6-A4-P80` | Accu | `SSK-M3-6-A4-P80` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |
| `V80040` | Nordson MEDICAL / Halkey-Roberts | `V80040` | NOT PROVIDED — capture supplier serial, lot, batch, or heat ID at receiving | NOT VERIFIED — no delivered-unit supplier CoC is present in this package | HOLD — verify received item identity and retain supplier CoC before release |

## Deterministic rendering method

`slides/generate_per_part_renders.py` imports the authoritative `build_r2.py`, builds both exact STOWED and DEPLOYED PartCatalogs in memory, asserts their PartDef sets are identical, and validates each source shape volume against the committed authoring inventory before rendering.

Each PNG uses the actual PartDef B-rep, an orthographic camera, a fixed 23° elevation and -55° azimuth after deterministic principal-axis permutation, a fixed white studio background, fixed neutral Lambert shading, no random colors, and a 1600 × 1200 output frame. Softgoods/recovery definitions use the exact DEPLOYED definition where it explains the geometry more clearly; other parts use the exact STOWED definition. The PNG footer provides part number, source description, MAKE/BUY, subsystem, and geometry state.

`slides/validate_per_part_render_set.py` verifies the exact included PNG set, filenames, SHA-256 hashes, PNG format, and 1600 × 1200 dimensions against the manifests. The latest validation report is `manifests/per_part_render_validation.json` and is PASS.

## Mass properties and center of gravity

- Exact current source / committed-inventory system mass: **11.728961 kg**
- Mass limit: **18.140 kg**
- Source-derived mass reserve: **6.411039 kg**
- Lower-priority `CURRENT_STATE.json` mass metadata: **11.729054 kg** (absolute difference **0.093 g**, recorded rather than coerced)
- STOWED CAD CG in master coordinates: **X -0.096 mm, Y 0.041 mm, Z 581.834 mm**
- DEPLOYED CAD CG in master coordinates: **X -0.037 mm, Y 0.039 mm, Z 584.403 mm**

The CG calculation is regenerated by `slides/extract_source_facts.py` from each occurrence’s current global exact-B-rep volume centroid and the same committed mass-precedence rule used by the validator: occurrence override, part override, then authoring-inventory part-master mass. Source authority therefore favors the exact current source/inventory result over the 0.093 g higher handoff-metadata value. It is a CAD calculation, not a measured physical balance result.

## Current validation status and limitations

- State parity: **279 / 279 occurrences pass**; the 64-row provenance register is fully resolved.
- Current release status: **INCOMPLETE TERMINAL AUDIT — NOT RELEASED**.
- The accepted automated motion checkpoint covers 0° through 55° inclusive at 1° increments; 56° through 80° are not accepted as completed validation evidence in that checkpoint.
- The latest full validator terminated at `POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK` with `'angle_deg'`; it did not compute release gates.
- No physical, environmental, calibrated damper force-speed, or manufacturing qualification is asserted.
- BUY components are presented at their current controlled source fidelity. Where the source identifies a representation as drawing-derived, the deck retains that qualification.
- No received-unit serial/lot/heat identifier or delivered-item supplier CoC is present in the current package; all BUY receiving-evidence claims remain fail-closed.
- One hero orientation is used per PartDef; no part required a second supporting view. Very slender routes and softgoods remain exact but naturally occupy less projected image area.
- PowerPoint export status: **PRESENT**.

## Assembly context imagery

The nine `slides/context_views/AFTER_IMAGE_*.png` views are deterministic source-derived assembly context views generated by authoritative `work/r2_source/render_evidence.py`. They are used only to explain architecture and mechanism context; all per-part breakdown tiles use the new exact PartDef render set.

## Reproduction

Run with the authoritative CAD environment:

```powershell
& <authoritative-cad-python> slides/generate_per_part_renders.py --source-root <authoritative-source-root> --repo-root <documentation-repo-root> --output-root <this-package-root>
& <authoritative-cad-python> slides/validate_per_part_render_set.py --package-root <this-package-root>
& <authoritative-cad-python> slides/extract_source_facts.py --source-root <authoritative-source-root> --output <this-package-root>/source_notes/source_facts.json
node slides/generate_cots_traceability.mjs
node slides/build_mechanical_breakdown.mjs
python slides/write_source_notes.py --package-root <this-package-root> --output <this-package-root>/STINGRAY_I5S_DF8_MECHANICAL_BREAKDOWN_PER_PART_SOURCE_NOTES.md
```

The PowerPoint authoring script uses `@oai/artifact-tool`, embeds PNG bytes, writes per-slide render/layout evidence, adds a `[Sources]` block to every slide’s speaker notes, and exports the final PPTX.

## Missing or unrenderable parts

None. All 116 included PartDefs rendered from source and passed manifest validation.
