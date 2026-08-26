# CAD and 3D Files

## Current CAD first

| Field | Exact value |
|---|---|
| Configuration | `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY` |
| Source path | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy` |
| Branch | `design/df8-14in-short-forward-powertrain-external-buoy` |
| Commit | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` |
| Classification | **CURRENT DEVELOPMENTAL** |
| GitHub inspection files | [Package 05](../../../cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/) |

The two current source AP242 masters are `LA-001` and `LA-002` in [the categorized catalog](ARTIFACT_CATALOG_BY_TYPE.csv). Their source paths and SHA-256 values are also recorded in [CAD_PROVENANCE.md](../../../context/stingray/CAD_PROVENANCE.md#exact-current-artifacts).

## GitHub-preserved inspection CAD

| Iteration | GitHub directory | Files available | Classification |
|---|---|---|---|
| I11 | [01 Forward Arm 480 mm](../../../cad/df8-owner-creo-inspection-zips/01_FORWARD_ARM_480MM/) | Inspection ZIP | HISTORICAL |
| I12 | [02 Architecture C Forward Packed](../../../cad/df8-owner-creo-inspection-zips/02_ARCH_C_FORWARD_PACKED/) | Inspection ZIP | HISTORICAL |
| I13 | [03 Architecture C 889 mm Fallback](../../../cad/df8-owner-creo-inspection-zips/03_ARCH_C_889MM_FALLBACK/) | Inspection ZIP | HISTORICAL fallback; not fixed-480 final |
| I17 | [04 14-in Short Arm External Buoy](../../../cad/df8-owner-creo-inspection-zips/04_14IN_SHORT_ARM_EXTERNAL_BUOY/) | STOWED STEP, DEPLOYED STEP, inspection ZIP | HISTORICAL predecessor |
| I18 | [05 True Forward Powertrain SHORT14 External Buoy](../../../cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/) | STOWED STEP, DEPLOYED STEP, inspection ZIP | **CURRENT DEVELOPMENTAL** |

The protected directories remain in their original layout. This navigation layer links them; it does not rename or move them.

## Local indexed 3D formats

| Format | Count | Contents |
|---|---:|---|
| `.step` / STEP AP242 | 18 | Current and historical endpoint masters, reference CAD and vendor CAD |
| `.stp` | 2 | Historical Clippard `MJV-3` vendor CAD copies |
| `.stl` | **0** | No STL file found in the 110-artifact local index or observed GitHub branch trees |
| Native Creo `.prt` / `.asm` / `.xpr` / `.xas` / `.neu` | **0** | No native Creo source found in the bounded recovery roots |

Search `navigation_category=CAD_AND_3D` in [ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv) for all 20 indexed local CAD/vendor-CAD files.

## CAD by iteration

| Iteration | Artifact IDs | Configuration / role | Status |
|---|---|---|---|
| I01 | `LA-092`, `LA-093`, `LA-096`, `LA-102`–`LA-104` | Reference/config-D and vendor STEP | HISTORICAL |
| I06 | `LA-072`, `LA-073`, `LA-107`, `LA-108` | R2 parity masters plus dirty reproduction evidence | HISTORICAL rows; EVIDENCE HOLD rows |
| I07 | `LA-065`, `LA-066` | Final-detail cleanup masters | HISTORICAL |
| I09 | `LA-057`, `LA-058` | Targeted-COTS endpoint pair | HISTORICAL |
| I12 | `LA-054`, `LA-055` | Architecture C forward-packed endpoint pair | HISTORICAL |
| I17 | `LA-015`, `LA-016` | Package 04 endpoint pair | HISTORICAL |
| I18 | `LA-001`, `LA-002` | Package 05 true-forward SHORT14 endpoint pair | **CURRENT DEVELOPMENTAL** |

## Use boundary

STEP/AP242 availability does not establish physical qualification. Bind any CAD claim to the exact configuration, source commit, artifact hash and validation record. Do not generate STL derivatives merely to fill an empty format category; create them only under a separately authorized manufacturing/visualization workflow.

Return to [artifact navigation](README.md).
