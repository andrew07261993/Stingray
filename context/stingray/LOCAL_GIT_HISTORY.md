# STINGRAY Local Git History

As of: 2026-08-25. Inventory was read-only except for the isolated `engineering/stingray-context` worktree created for this consolidation.

## Controlling finding

The exact local source for the shorthand `STINGRAY_I5S_DF8_SHORT14_FORWARD` is:

- repository: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad`
- worktree: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy`
- branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- HEAD: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- commit date: `2026-08-25T16:05:28-05:00`
- exact configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- worktree status at inventory: clean
- classification: **CURRENT DEVELOPMENTAL**

It is the newest committed local CAD branch by commit time and contains the exact STOWED/DEPLOYED AP242 pair, source, validation registers and inspection ZIP. It is newer than Package 04, the commercial-module closure, staged/distributed studies, the fixed-480 Architecture C non-pass, the 480 mm forward-arm repack, targeted COTS, final detail cleanup and R2 state-parity branches. It is not fabrication/procurement release or physical qualification.

## Git repositories and clone families

| Repository root | Origin | Role | Local branch state |
|---|---|---|---|
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad` | none | Shared DF8 CAD object database and all local CAD worktrees | 12 named branches, all local-only because no remote is configured |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-docs` | `https://github.com/andrew07261993/Stingray` | Documentation/COTS repository and controlling linked-worktree family | Remote-backed; some local branches have no configured upstream even though matching remote branches exist |
| `C:\Users\ANDRE.ANDREWSPC\CodexProjects\stingray-stakeholder-powerpoint` | `https://github.com/andrew07261993/Stingray.git` | Older standalone stakeholder-deck clone | Clean; local deck branch is stale relative to the later `95766a1...` checkout |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\referenced-chatgpt-conversation-this-is-an\work\Stingray` | `https://github.com/andrew07261993/Stingray.git` | Later standalone per-part/deck clone | HEAD `95766a1...`; dirty only with untracked inspection metadata and `node_modules/` |

The non-Git source trees `C:\Users\ANDRE.ANDREWSPC\CodexProjects\STINGRAY_CODEX_COMMISSION`, `...\stingray-cad-transition`, and `...\stingray-final-delivery-work` are indexed in `LOCAL_ARTIFACT_INDEX.csv`; they are historical CONFIG-D/CQ evidence, not current DF8 Git authorities.

## Shared CAD repository branches

There is no `origin` in the shared CAD repository. Every branch in this table is therefore local-only and must not be assumed recoverable from GitHub.

| Branch | HEAD | Commit date | Disposition |
|---|---|---|---|
| `main` | `fcca6642077cf9a420e703c3f7d53b8913501f5a` | 2026-08-23 08:48 -05:00 | HISTORICAL checkpoint; occupied/dirty with one untracked audit file |
| `audit/state-parity-provenance` | `61a58cbbccd0aae7a747b2a73046142cf1f44511` | 2026-08-23 12:36 -05:00 | HISTORICAL validated R2 parity/provenance reference |
| `fix/final-cad-semantic-cleanup` | `8c594781e27b0597a71957082fb64f152cacfcd9` | 2026-08-23 21:29 -05:00 | HISTORICAL bounded detail/semantic cleanup |
| `design/df8-targeted-cots-retrofit` | `584e673a8b0490bc0b6ec1e508d5fc3426f45f5b` | 2026-08-24 12:23 -05:00 | HISTORICAL developmental targeted-COTS CAD; occupied/dirty with untracked validation evidence |
| `design/df8-forward-arm-repack` | `a31fce0e768f354b1831331bc2ed145223c8b2c4` | 2026-08-24 15:33 -05:00 | HISTORICAL 480 mm forward-arm checkpoint; source for later SHORT14 work |
| `build/arch-c-forward-packed` | `abe9d93d2dada6150daa9a652885c472a6a06464` | 2026-08-24 15:33 -05:00 | HISTORICAL developmental Architecture C/interface-proxy CAD |
| `design/df8-final-converged-cots-forward-arm` | `17870c53e3ceecbab88e28d7ccad0ae7047f1db6` | 2026-08-24 21:17 -05:00 | HISTORICAL fixed-480 architecture stop; dirty untracked 889 mm fallback evidence is EVIDENCE HOLD |
| `design/df8-final-distributed-pressure-convergence` | `7f5d06fdb83dc879b2b98094c1e498c5c9e6ff23` | 2026-08-25 07:14 -05:00 | HISTORICAL measured non-pass |
| `design/df8-final-staged-inflation-convergence` | `dce7a53643a35d80f5cd6f63f09852ab565a4165` | 2026-08-25 08:31 -05:00 | HISTORICAL Path B/measured non-pass |
| `design/df8-final-commercial-module-closure` | `f8c38b16eb3ed80a9180254f9ee8ddad5a40f3da` | 2026-08-25 09:23 -05:00 | HISTORICAL terminal fixed-480 complete-module screen; no CAD output authorized |
| `design/df8-14in-short-arm-external-buoy-pack` | `0431fe05465ba59a1714f110a07c73f146131c96` | 2026-08-25 14:24 -05:00 | HISTORICAL Package 04 precursor |
| `design/df8-14in-short-forward-powertrain-external-buoy` | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | 2026-08-25 16:05 -05:00 | CURRENT DEVELOPMENTAL; newest CAD baseline |

## Worktree inventory

| Worktree | Branch / HEAD | Inventory status |
|---|---|---|
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad` | `main` / `fcca664...` | Dirty: one untracked `endpoint_pair_audit_deployed.csv.gz`; preserved |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\work\checkpoint-reproduction` | detached / `1b6ba8b2e783ba42143d163d41e9a9f2afdebd77` | Dirty: five tracked CAD/manifest changes plus untracked reproduction evidence; preserved as EVIDENCE HOLD |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-final-cad-semantic-cleanup` | `fix/final-cad-semantic-cleanup` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-state-parity` | `audit/state-parity-provenance` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-state-parity-targeted-retrofit` | `design/df8-targeted-cots-retrofit` | Dirty: seven untracked validation files; preserved |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-arch-c-forward-packed` | `build/arch-c-forward-packed` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-final-converged` | `design/df8-final-converged-cots-forward-arm` | Dirty: three untracked fallback-889 paths; preserved and not treated as fixed-480 final |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-final-distributed` | `design/df8-final-distributed-pressure-convergence` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-final-staged-inflation` | `design/df8-final-staged-inflation-convergence` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-forward-arm-repack` | `design/df8-forward-arm-repack` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-arm-buoy-pack` | `design/df8-14in-short-arm-external-buoy-pack` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy` | `design/df8-14in-short-forward-powertrain-external-buoy` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-final-commercial-module` | `design/df8-final-commercial-module-closure` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-docs` | `design/df8-targeted-cots-retrofit` / `fc5d76d...` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-24\stingray-i5-s-df8-cots-heavy` | `design/df8-cots-heavy-architecture` / `974b7f0...` | Clean |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-df8-owner-creo-upload` | `cad/df8-owner-creo-inspection-zips` / `ab33ffd...` | Clean; protected inspection tree untouched |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-engineering-context` | `engineering/stingray-context`, parent `cdeb4da...` | Isolated consolidation worktree created for this task |
| `C:\Users\ANDRE.ANDREWSPC\CodexProjects\stingray-stakeholder-powerpoint` | `docs/df8-per-part-mechanical-breakdown` / `ef0ebf4...` | Clean but stale historical clone |
| `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\referenced-chatgpt-conversation-this-is-an\work\Stingray` | `docs/df8-per-part-mechanical-breakdown` / `95766a1...` | Dirty only with untracked generated inspection metadata and `node_modules/`; preserved |

Total worktrees/checkouts indexed: **19**. Occupied dirty worktrees were not reset, cleaned, stashed, discarded or overwritten.

## SHORT14_FORWARD commit chain

| Commit | Date | Role |
|---|---|---|
| `a55e925db67b2720c98af5e7694c16c142a07144` | 2026-08-25 11:47 -05:00 | Lock true forward arm/powertrain layout |
| `59db97570d175adff550e1cd25451708ea3e114a` | 2026-08-25 15:46 -05:00 | Shorten arms/body and remove buoy ejector |
| `0f5be86cc42147cf7f9dc502c2f562d86811b206` | 2026-08-25 16:05 -05:00 | Add external automatic-inflation buoy pack |
| `66ee53955d3ce7945e12949ecbc3e99d591fd5b1` | 2026-08-25 16:05 -05:00 | Complete bounded CAD validation gates |
| `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` | 2026-08-25 16:05 -05:00 | Create final owner-inspection package |

The branch report declares source baseline `a31fce0e768f354b1831331bc2ed145223c8b2c4`. The later branch moves the pivot from the 480.000 mm reference to 355.000 mm under a later explicit owner-directed true-forward-powertrain/SHORT14 commission; therefore the 480 mm pressure-packaging studies remain historical constraints for their own configuration, not authority to silently rewrite the later external-pack CAD.

## Remote-backed documentation branches

At inventory time the remote included `main`, `docs/df8-per-part-mechanical-breakdown`, `docs/stakeholder-powerpoint`, `design/df8-targeted-cots-retrofit`, `design/df8-cots-heavy-architecture`, `cad/df8-owner-creo-inspection-zips`, and `engineering/stingray-context`. The local shared CAD branches listed above are not in that remote repository.

The consolidation branch was fetched explicitly because the controlling checkout had a narrow fetch refspec, then checked out in its own worktree. No merge was performed.

## Authority rule

Newest commit time alone is not release authority. For future CAD work, begin with `CONTEXT_INDEX.md`, then inspect the exact source branch/commit, AP242 hashes, validation status and owner decision chain. Dirty/EVIDENCE HOLD artifacts must never silently supersede committed source.
