# ZIPs and Packages

## Protected GitHub inspection packages

| Order | Package | ZIP | Classification |
|---:|---|---|---|
| I11 | [01 Forward Arm 480 mm](../../../cad/df8-owner-creo-inspection-zips/01_FORWARD_ARM_480MM/) | [Download/view ZIP](../../../cad/df8-owner-creo-inspection-zips/01_FORWARD_ARM_480MM/STINGRAY_DF8_FORWARD_ARM_480MM_CREO_INSPECTION.zip) | HISTORICAL |
| I12 | [02 Architecture C Forward Packed](../../../cad/df8-owner-creo-inspection-zips/02_ARCH_C_FORWARD_PACKED/) | [Download/view ZIP](../../../cad/df8-owner-creo-inspection-zips/02_ARCH_C_FORWARD_PACKED/STINGRAY_DF8_ARCH_C_FORWARD_PACKED_CREO_INSPECTION.zip) | HISTORICAL |
| I13 | [03 Architecture C 889 mm Fallback](../../../cad/df8-owner-creo-inspection-zips/03_ARCH_C_889MM_FALLBACK/) | [Download/view ZIP](../../../cad/df8-owner-creo-inspection-zips/03_ARCH_C_889MM_FALLBACK/STINGRAY_DF8_ARCH_C_889MM_FALLBACK_CREO_INSPECTION.zip) | HISTORICAL fallback |
| I17 | [04 14-in Short Arm External Buoy](../../../cad/df8-owner-creo-inspection-zips/04_14IN_SHORT_ARM_EXTERNAL_BUOY/) | [Download/view ZIP](../../../cad/df8-owner-creo-inspection-zips/04_14IN_SHORT_ARM_EXTERNAL_BUOY/STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_CREO_INSPECTION.zip) | HISTORICAL predecessor |
| I18 | [05 True Forward Powertrain SHORT14 External Buoy](../../../cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/) | [Download/view ZIP](../../../cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_CREO_INSPECTION.zip) | **CURRENT DEVELOPMENTAL** |

Each package directory includes a README and SHA-256 manifest. Package 04 and Package 05 also expose their STOWED/DEPLOYED STEP files separately.

The protected directory was not reorganized. Its Git tree identity at the start of this navigation task was `85499abeba73783c4e309449087db00ae0e97e0c`.

## Local archive index

The categorized catalog contains 11 archive/package records:

| Artifact IDs | Contents | Classification |
|---|---|---|
| `LA-003` | Current Package 05 inspection ZIP | CURRENT DEVELOPMENTAL |
| `LA-017`, `LA-024`, `LA-064`, `LA-105` | Package 04, forward-arm, final-cleanup and state-parity archives | HISTORICAL |
| `LA-035`, `LA-036`, `LA-044` | Commercial-module, staged-inflation and distributed-pressure non-pass packages | HISTORICAL |
| `LA-053` | 889 mm fallback inspection archive | EVIDENCE HOLD |
| `LA-062`, `LA-106` | Compressed endpoint-audit CSV evidence | EVIDENCE HOLD |

Exact local paths, byte sizes and SHA-256 values are in [ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv). Large local-only archives were not copied again into Git.

## Package-use rule

An inspection ZIP is a configuration checkpoint, not automatic release authority. Verify its README, SHA-256 manifest, exact source branch/commit and validation classification before use.

Return to [artifact navigation](README.md).
