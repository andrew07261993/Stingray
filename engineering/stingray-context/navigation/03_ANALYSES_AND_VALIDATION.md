# Analyses and Validation

The categorized local catalog contains **13 analysis/report artifacts** and **31 validation/test artifacts**. These are indexed in place; large source packages were not duplicated into this directory.

## Current Package 05 evidence

| Artifact ID | File | Role | Classification |
|---|---|---|---|
| `LA-004` | `VALIDATION_SUMMARY.md` | Human-readable current validation disposition | CURRENT DEVELOPMENTAL |
| `LA-005` | `VALIDATION_SUMMARY.json` | Machine-readable current validation summary | CURRENT DEVELOPMENTAL |
| `LA-006` | `SHORT14_FORWARD_POWERTRAIN_DESIGN_REPORT.md` | Current design report | CURRENT DEVELOPMENTAL |
| `LA-007` | `SHORT_ARM_MISSION_ENVELOPE_COMPARISON.md` | Mission-envelope comparison | CURRENT DEVELOPMENTAL |
| `LA-008` | `FINAL_MASS_CG_INERTIA.json` | Current mass/CG/inertia | CURRENT DEVELOPMENTAL |
| `LA-009` | `FINAL_MOTION_AUDIT_SUMMARY.csv` | Full motion register summary | CURRENT DEVELOPMENTAL |
| `LA-010` | `full_motion_exact_boolean_summary.json` | Exact-Boolean sweep summary | CURRENT DEVELOPMENTAL |
| `LA-011` | `endpoint_validation_summary.json` | STOWED/DEPLOYED endpoint validation | CURRENT DEVELOPMENTAL |
| `LA-014` | `authoring_manifest.json` | Current source/artifact manifest | CURRENT DEVELOPMENTAL |

Use [VALIDATION_STATUS.md](../../../context/stingray/VALIDATION_STATUS.md) for the controlling interpretation. CAD PASS is not physical or release acceptance.

## Analysis/report groups

| Iteration | Artifact IDs | Subject | Classification |
|---|---|---|---|
| I01 | `LA-101` | Early source-provenance report | HISTORICAL |
| I11 | `LA-025` | Forward-arm repack comparison | HISTORICAL |
| I13 | `LA-050`, `LA-051` | Fixed-480 and distributed-source packaging screens | HISTORICAL |
| I14 | `LA-045`, `LA-047` | Distributed-pressure convergence and path register | HISTORICAL measured non-pass |
| I15 | `LA-037`, `LA-040`, `LA-041` | Staged-inflation convergence, buoyancy calculation and layout screen | HISTORICAL measured non-pass |
| I17 | `LA-020`, `LA-021` | Package 04 short-arm design/envelope reports | HISTORICAL |
| I18 | `LA-006`, `LA-007` | Current true-forward SHORT14 design/envelope reports | CURRENT DEVELOPMENTAL |

## Validation groups

| Iteration | Artifact IDs | Subject | Classification |
|---|---|---|---|
| I01 | `LA-088`, `LA-094`, `LA-095`, `LA-097`, `LA-098` | Early reference/config-D manifests and geometry validation | HISTORICAL |
| I06 | `LA-069`–`LA-071`, `LA-105`, `LA-106`, `LA-109`, `LA-110` | R2 state parity, archive and dirty audit evidence | HISTORICAL entries and EVIDENCE HOLD entries |
| I07 | `LA-067` | Final cleanup validation summary | HISTORICAL |
| I08 | `LA-086` | Deck delivery validation | HISTORICAL |
| I09 | `LA-060`, `LA-061`, `LA-063` | Targeted-COTS validation/delta/connectivity | HISTORICAL entries and EVIDENCE HOLD entries |
| I11 | `LA-026`–`LA-028` | Forward-arm five-angle, mass/CG and targeted validation | HISTORICAL |
| I13 | `LA-052` | 889 mm fallback validation | EVIDENCE HOLD |
| I14 | `LA-046`, `LA-049` | Distributed non-pass validation/package manifest | HISTORICAL |
| I15 | `LA-038`, `LA-039` | Staged-inflation validation | HISTORICAL |
| I17 | `LA-018`, `LA-019`, `LA-022`, `LA-023` | Package 04 validation/mass/package manifest | HISTORICAL |
| I18 | `LA-004`, `LA-005`, `LA-008`–`LA-011`, `LA-014` | Current Package 05 validation | CURRENT DEVELOPMENTAL |

## Data and manifest navigation

The one remaining primary `DATA_AND_MANIFESTS` row is `LA-068`, `final_cad_name_map.csv`, from I07 final cleanup. Other CSV/JSON files are grouped under their actual engineering role—validation, COTS, analysis or package evidence—rather than separated only by extension.

For every artifact's exact path, branch, commit, date, SHA-256 and notes, use [ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv).

Return to [artifact navigation](README.md).
