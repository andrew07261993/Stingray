# STINGRAY CAD Provenance

As of: 2026-08-25.

## Current developmental master

| Field | Exact value |
|---|---|
| Configuration | `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY` |
| Local source path | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy` |
| Git object database | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad` |
| Branch | `design/df8-14in-short-forward-powertrain-external-buoy` |
| HEAD | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` |
| Commit date | `2026-08-25T16:05:28-05:00` |
| Source baseline declared by report | `a31fce0e768f354b1831331bc2ed145223c8b2c4` (`design/df8-forward-arm-repack`) |
| Classification | CURRENT DEVELOPMENTAL |

The shared CAD repository has no remote. This branch and the other 11 named CAD branches are local-only and are not recoverable from `andrew07261993/Stingray` unless transferred separately.

## Exact current artifacts

| Artifact | Absolute path | SHA-256 | Size |
|---|---|---|---:|
| STOWED AP242 | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy\work\short14_external_buoy\STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_STOWED_AP242.step` | `87a6d6f2f234fe955ef6a87aa9f7ac242d28ee10e23b9b60aca94e90e68a02c0` | 9,071,324 |
| DEPLOYED AP242 | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy\work\short14_external_buoy\STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_DEPLOYED_AP242.step` | `fbb716986ce6913715a78468b29fec8ae0a1eb45f64b9a6f825407655d68d1de` | 10,575,841 |
| Inspection ZIP | `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy\work\short14_external_buoy\STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY_INSPECTION.zip` | `4d124b4bb410689071545a41c9c17c31e9393eadbf41ae6a800c5cd458b52a6c` | 6,625,392 |

The source tree, validation registers, reports and manifest are indexed separately in `LOCAL_ARTIFACT_INDEX.csv`.

## Commit chain

| Commit | Role |
|---|---|
| `a55e925db67b2720c98af5e7694c16c142a07144` | Lock true-forward arm/powertrain layout |
| `59db97570d175adff550e1cd25451708ea3e114a` | Shorten arms/body and remove internal buoy ejector |
| `0f5be86cc42147cf7f9dc502c2f562d86811b206` | Add external automatic-inflation buoy pack |
| `66ee53955d3ce7945e12949ecbc3e99d591fd5b1` | Complete bounded CAD validation gates |
| `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | Create inspection package |

## Configuration chronology

| Configuration / branch | Commit | Date | Classification / relationship |
|---|---|---|---|
| R2 state parity / `audit/state-parity-provenance` | `61a58cbbccd0aae7a747b2a73046142cf1f44511` | 2026-08-23 | HISTORICAL strong provenance reference; 279/279, but older geometry |
| Final detail cleanup / `fix/final-cad-semantic-cleanup` | `8c594781e27b0597a71957082fb64f152cacfcd9` | 2026-08-23 | HISTORICAL bounded semantic/detail correction |
| Targeted COTS / `design/df8-targeted-cots-retrofit` | `584e673a8b0490bc0b6ec1e508d5fc3426f45f5b` | 2026-08-24 | HISTORICAL developmental alternative |
| Forward arm / `design/df8-forward-arm-repack` | `a31fce0e768f354b1831331bc2ed145223c8b2c4` | 2026-08-24 | HISTORICAL 480 mm source baseline for later SHORT14 work |
| Architecture C / `build/arch-c-forward-packed` | `abe9d93d2dada6150daa9a652885c472a6a06464` | 2026-08-24 | HISTORICAL interface/proxy CAD |
| Fixed-480 convergence | `17870c53e3ceecbab88e28d7ccad0ae7047f1db6` | 2026-08-24 | HISTORICAL architecture stop; 889 mm fallback is not fixed-480 final |
| Distributed pressure | `7f5d06fdb83dc879b2b98094c1e498c5c9e6ff23` | 2026-08-25 | HISTORICAL measured non-pass |
| Staged inflation | `dce7a53643a35d80f5cd6f63f09852ab565a4165` | 2026-08-25 | HISTORICAL Path B / measured non-pass |
| Commercial module closure | `f8c38b16eb3ed80a9180254f9ee8ddad5a40f3da` | 2026-08-25 | HISTORICAL terminal fixed-480 module screen; no CAD output |
| Package 04 short arm | `0431fe05465ba59a1714f110a07c73f146131c96` | 2026-08-25 | HISTORICAL immediate predecessor |
| Package 05 true forward SHORT14 | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | 2026-08-25 | CURRENT DEVELOPMENTAL; newest committed CAD |

## Protected GitHub inspection checkpoint

Remote branch `cad/df8-owner-creo-inspection-zips`, commit `ab33ffd9c3a8cbfa7d43311634db4e465fa8185c`, preserves five owner-inspection packages. This consolidation did not add, delete, rewrite or reorganize anything under `cad/df8-owner-creo-inspection-zips/`.

Package 05 is an exact-byte transfer of the newest local inspection package under a GitHub-facing name. The preserved package is still developmental inspection evidence, not a formal release.

## Dirty/operator evidence

Dirty worktrees were recorded but never used to silently supersede committed source. The detached checkpoint reproduction, targeted-COTS untracked audits, main untracked endpoint evidence and the final-converged 889 mm fallback are classified **EVIDENCE HOLD**. See `LOCAL_GIT_HISTORY.md` and `LOCAL_ARTIFACT_INDEX.csv`.

## Provenance rule

Select CAD authority by exact configuration, branch, commit, internal manifest, hashes, owner decision chronology and validation/release classification. Filename suffixes, timestamps, screenshots, presentation claims and detailed older reports are not enough.
