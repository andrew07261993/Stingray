# STINGRAY GitHub Branch and Artifact Manifest

As of: 2026-08-25

Repository: `andrew07261993/Stingray`

This manifest records the GitHub-resident STINGRAY engineering branches and the major exact-byte CAD/artifact checkpoints visible to this consolidation. It complements the deeper local index at `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv` and local Git history at `../../context/stingray/LOCAL_GIT_HISTORY.md`.

## Remote branches observed during consolidation

| Branch | Observed head | Role |
|---|---|---|
| `main` | `4093dbcf37fc4845cff49489ad6afa944681aa00` | Repository default/base at time of context consolidation |
| `cad/df8-owner-creo-inspection-zips` | `ab33ffd9c3a8cbfa7d43311634db4e465fa8185c` | Protected historical/current owner-inspection CAD packages |
| `design/df8-targeted-cots-retrofit` | `fc5d76dd9f7b15bd5975a667974869414aabd821` | Targeted COTS conversion/procurement documentation |
| `design/df8-cots-heavy-architecture` | `974b7f01ddc97d5ca43ccc595bc2f38e140ddd30` | COTS-heavy architecture/gas-source/buoy trade documentation |
| `docs/df8-per-part-mechanical-breakdown` | `95766a1bfc7bcc48416b83c7b25fcbd482ac0608` | Per-part mechanical breakdown documentation |
| `docs/stakeholder-powerpoint` | `57aad96e9ffeecdf22bd2658cdd8a7e5abe42078` | Stakeholder presentation work |
| `engineering/stingray-context` | mutable during this export | Consolidated engineering context branch and requested context directory |

Branch heads above are snapshot values, not immutable release identifiers. Always re-read the branch before basing new engineering work on it.

## Owner-inspection CAD checkpoint

Path on the preserved CAD branch/tree:

`cad/df8-owner-creo-inspection-zips/`

Do not rewrite, reorganize or normalize these packages. They are configuration/provenance evidence.

### Package 01 — Forward Arm 480 mm

- directory: `01_FORWARD_ARM_480MM/`
- ZIP: `STINGRAY_DF8_FORWARD_ARM_480MM_CREO_INSPECTION.zip`
- Git blob size observed: 10,719,588 bytes
- classification: **HISTORICAL** — inspection package

### Package 02 — Architecture C Forward Packed

- directory: `02_ARCH_C_FORWARD_PACKED/`
- ZIP: `STINGRAY_DF8_ARCH_C_FORWARD_PACKED_CREO_INSPECTION.zip`
- Git blob size observed: 7,764,201 bytes
- classification: **HISTORICAL** — developmental architecture

### Package 03 — Architecture C 889 mm Fallback

- directory: `03_ARCH_C_889MM_FALLBACK/`
- ZIP: `STINGRAY_DF8_ARCH_C_889MM_FALLBACK_CREO_INSPECTION.zip`
- Git blob size observed: 9,303,212 bytes
- classification: **HISTORICAL** — fallback; do not treat the 889 mm geometry as the fixed-480 final configuration

### Package 04 — 14-in Short Arm External Buoy

- directory: `04_14IN_SHORT_ARM_EXTERNAL_BUOY/`
- ZIP: `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_CREO_INSPECTION.zip` — 8,071,643 bytes
- STOWED STEP: `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_STOWED_AP242.step` — 15,415,537 bytes
- DEPLOYED STEP: `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_DEPLOYED_AP242.step` — 16,929,244 bytes
- classification: **HISTORICAL** — immediate predecessor to Package 05

### Package 05 — True Forward Powertrain / SHORT14 / External Buoy

- directory: `05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/`
- ZIP: `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_CREO_INSPECTION.zip` — 6,625,392 bytes
- STOWED STEP: `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_STOWED_AP242.step` — 9,071,324 bytes
- DEPLOYED STEP: `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_DEPLOYED_AP242.step` — 10,575,841 bytes
- exact local current inspection ZIP SHA-256: `4d124b4bb410689071545a41c9c17c31e9393eadbf41ae6a800c5cd458b52a6c`
- exact local current STOWED AP242 SHA-256: `87a6d6f2f234fe955ef6a87aa9f7ac242d28ee10e23b9b60aca94e90e68a02c0`
- exact local current DEPLOYED AP242 SHA-256: `fbb716986ce6913715a78468b29fec8ae0a1eb45f64b9a6f825407655d68d1de`
- source configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- local source branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- local source commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- classification: **CURRENT DEVELOPMENTAL**; not a release configuration

## Package 05 source commit chain recovered locally

| Commit | Role |
|---|---|
| `a55e925db67b2720c98af5e7694c16c142a07144` | Lock true-forward arm/powertrain layout |
| `59db97570d175adff550e1cd25451708ea3e114a` | Shorten arms/body and remove internal buoy ejector |
| `0f5be86cc42147cf7f9dc502c2f562d86811b206` | Add external automatic-inflation buoy pack |
| `66ee53955d3ce7945e12949ecbc3e99d591fd5b1` | Complete bounded CAD validation gates |
| `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | Create current inspection package |

The source CAD repository holding this branch has **no Git remote**. The exact Package 05 endpoint STEP files and inspection ZIP are GitHub-resident, but this GitHub repository is not yet a complete backup of every local source Git object.

## Other recovered configuration chronology

| Configuration/workstream | Local commit | Classification |
|---|---|---|
| R2 state-parity/provenance | `61a58cbbccd0aae7a747b2a73046142cf1f44511` | HISTORICAL — strong validation/provenance reference; older geometry |
| Final semantic/detail cleanup | `8c594781e27b0597a71957082fb64f152cacfcd9` | HISTORICAL — correction checkpoint |
| Targeted COTS local source | `584e673a8b0490bc0b6ec1e508d5fc3426f45f5b` | HISTORICAL — developmental alternative |
| Forward-arm repack | `a31fce0e768f354b1831331bc2ed145223c8b2c4` | HISTORICAL — source baseline for SHORT14 |
| Architecture C forward packed | `abe9d93d2dada6150daa9a652885c472a6a06464` | HISTORICAL — interface/proxy CAD |
| Fixed-480 convergence | `17870c53e3ceecbab88e28d7ccad0ae7047f1db6` | HISTORICAL — architecture stop |
| Distributed-pressure development | `7f5d06fdb83dc879b2b98094c1e498c5c9e6ff23` | HISTORICAL — measured non-pass |
| Staged-inflation convergence | `dce7a53643a35d80f5cd6f63f09852ab565a4165` | HISTORICAL — Path B / measured non-pass |
| Commercial-module closure | `f8c38b16eb3ed80a9180254f9ee8ddad5a40f3da` | HISTORICAL — terminal module screen |
| Package 04 short-arm configuration | `0431fe05465ba59a1714f110a07c73f146131c96` | HISTORICAL — predecessor |
| Package 05 true-forward SHORT14 | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | CURRENT DEVELOPMENTAL |

## Targeted COTS branch artifact families

`design/df8-targeted-cots-retrofit` contains the following classes of engineering records under `docs/engineering/cots/targeted-retrofit/`:

- CAD change register;
- COTS conversion ledger (CSV/JSON);
- custom-adapter and custom-remainder registers;
- procurement requirements and action lists;
- selected COTS BOM, fit matrix, certification matrix and technical closure;
- rejected/deferred candidate register;
- pressure-reservoir/booster trade and candidate data;
- Phase 2 candidate screening;
- targeted COTS final BOM and selection/CAD-implementation gates;
- RFQ package and transmission log;
- underwater test-article shortlist;
- validation summary and task-state records.

These records are context and development evidence; status/release classifications inside the exact files control.

## COTS-heavy branch artifact families

`design/df8-cots-heavy-architecture` contains the following classes of records under `docs/engineering/cots/cots-heavy-architecture/`:

- architecture alternatives/decision matrix and revision gates;
- buoy candidate and pressure/relief trades;
- cartridge family/count matrices;
- CO2 gas-sizing analysis;
- commercial marine inflation trade;
- COTS candidate BOM;
- dual-release and dual-source pressure/packaging architecture;
- envelope-compliant gas-source trade;
- failure-mode register;
- field-reset architecture/procedure/service matrix;
- final gas-source selection and mission-sizing gates;
- procurement and release-data gates.

## Local-only source preservation gap

The local consolidation identified **12 branches in the shared CAD repository with no remote**. Their exact SHAs, worktree paths, dirty-state protections and roles are recorded in:

- `../../context/stingray/LOCAL_GIT_HISTORY.md`
- `../../context/stingray/CAD_PROVENANCE.md`
- `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`

Do not interpret the presence of the Package 05 ZIP/STEP pair as proof that every source script, historical Git object, vendor binary or dirty engineering checkpoint has been independently backed up to GitHub.
