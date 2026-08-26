# STINGRAY Source Coverage and Export Gaps

As of: 2026-08-25

## Executive statement

This repository now contains the **maximum faithful STINGRAY context consolidation accessible through the connected ChatGPT, File Library and GitHub interfaces plus the local/Codex recovery that had already been pushed to this branch**.

It is **not truthful to describe this as a byte-for-byte 100% export of every upstream system**, because several upstream stores are not exposed by the available connectors. Those boundaries are documented below so future agents do not silently assume missing material was captured.

## Coverage matrix

| Source / evidence class | Coverage in GitHub | Fidelity | Remaining gap |
|---|---|---|---|
| Local Codex/Work sessions | **INDEXED** | 79 relevant rollout records / 61 unique session IDs content-indexed in `../../context/stingray/CODEX_SESSION_INDEX.md` | Raw local rollout files themselves are not all duplicated into this context folder |
| Cross-device ChatGPT STINGRAY sessions | **CONTEXT RECOVERED** | Session chronology and carried-forward engineering facts in `SESSION_LEDGER.md`; pre-existing ChatGPT-side harvest retained | The platform does not expose a byte-for-byte raw transcript export for every inaccessible historical cloud conversation through this connector |
| Local Git repositories/worktrees | **INDEXED** | Four repository/clone roots and 19 worktrees/checkouts recovered; roles/status/branches documented | Shared CAD repository has no remote; local Git object database is not fully copied to GitHub |
| Local shared-CAD branches | **INDEXED** | 12 local-only branch names/SHAs and chronology documented | Git objects for all branches are not remotely backed up |
| High-value local engineering artifacts | **INDEXED** | 110 local artifacts recorded by exact path, configuration/status, size and SHA-256 in `LOCAL_ARTIFACT_INDEX.csv` | Large local binaries/vendor collections are not all duplicated into GitHub |
| Current Package 05 owner-inspection CAD | **EXACT BYTES PRESENT** | ZIP + STOWED/DEPLOYED AP242 files preserved in GitHub owner-inspection checkpoint; exact local hashes documented | Source Git objects/scripts still depend on local repository/indexed artifacts |
| Historical owner-inspection packages 01–04 | **EXACT BYTES PRESENT** | GitHub-resident ZIPs; Package 04 also exposes endpoint STEP pair | These are historical configuration checkpoints, not current release authority |
| Remote GitHub engineering branches | **PRESENT** | Exact branch refs for COTS, part-breakdown and presentation work | Branch heads can move; re-read before use |
| File Library artifacts | **INVENTORIED** | Titles, dates/roles and critical content/status captured in `FILE_LIBRARY_MANIFEST.md` | File Library connector does not provide a general arbitrary binary-to-GitHub copy operation |
| COTS/vendor evidence | **INDEXED/BRANCHED** | COTS master index reconciles 74 exact configurations/product families; remote COTS branches preserve trade/procurement records | Vendor-exact complete current-module geometry, order suffixes, quotes/CoCs/receiving evidence remain open where stated |
| Secrets/authentication stores | **INTENTIONALLY EXCLUDED** | Correct security boundary | Passwords, passkeys, API keys, tokens, cookies and credential databases are not engineering context and must not be committed |
| Unrelated personal data | **INTENTIONALLY EXCLUDED** | Correct data-minimization boundary | Not part of STINGRAY engineering context |

## What is fully represented enough for future context use

Future STINGRAY agents can recover the current engineering state without relying on chat memory alone by reading:

- `../../context/stingray/CONTEXT_INDEX.md`
- `../../context/stingray/CURRENT_STATE.md`
- `../../context/stingray/CAD_PROVENANCE.md`
- `../../context/stingray/VALIDATION_STATUS.md`
- `../../context/stingray/REQUIREMENTS.md`
- `../../context/stingray/DECISION_REGISTER.md`
- `../../context/stingray/COTS_MASTER_INDEX.md`
- `../../context/stingray/LOCAL_GIT_HISTORY.md`
- `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`
- `../../context/stingray/CODEX_SESSION_INDEX.md`
- this directory's `SESSION_LEDGER.md`, GitHub manifest and File Library manifest.

The current developmental configuration is explicitly identified as `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`, local source branch `design/df8-14in-short-forward-powertrain-external-buoy`, commit `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`.

## Exact current CAD files already remotely preserved

Under `cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/`:

- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_CREO_INSPECTION.zip`
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_STOWED_AP242.step`
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_DEPLOYED_AP242.step`
- `README.md`
- `SHA256SUMS.txt`

Local source-derived hashes are documented in `GITHUB_BRANCH_AND_ARTIFACT_MANIFEST.md` and `../../context/stingray/CAD_PROVENANCE.md`.

## Remaining engineering evidence gates — not export defects

These are genuine unresolved engineering/evidence items, not missing-context artifacts:

1. Owner visual/mechanical inspection of the exact current AP242 pair in Creo.
2. Physical short-arm mission tests: fabric engagement/retention/extraction, snag, wet deployment, fall/orientation equivalence and recovery behavior.
3. External buoy finished-article evidence: actual buoy volume, packed dimensions, mass/CG, wet inflation/breakaway, leakage, relief, proof-load, drainage, fouling, drying and repack.
4. Complete commercial COTS-module evidence for the current external-pack architecture.
5. Exact current Hydro 1F/V95000 suffix and final cartridge/manifold/holder/bladder interfaces replacing dimensional proxies before release.
6. Procurement/receiving evidence: exact order suffixes, quotes, certificates/CoC, lot/expiry controls, received-item dimensions/materials and application approvals.
7. Owner-authorized disposition of dirty `EVIDENCE HOLD` local work.

## Export/source-access gaps that still prevent a literal 100% byte export

### G-001 — Cloud ChatGPT raw transcripts

The available interface does not expose all historical STINGRAY conversations as downloadable raw transcript files. The context that was actually available was carried into the project summary/session ledger and is preserved. Missing raw message text is not reconstructed from memory or invented.

**Closure path:** use an account-level ChatGPT data export or another platform-supported conversation-export mechanism if/when accessible, then add the raw STINGRAY conversation export files to this directory with a manifest and hashes.

### G-002 — Local CAD Git object database

The recovered shared CAD repository has no remote. Twelve branches are indexed with exact SHAs, but the branch Git objects are local-only.

**Closure path:** from ANDREWSPC/Codex, create a sanitized Git bundle or push the controlled source branches to an approved GitHub location. Do not include secrets, caches or unrelated content.

### G-003 — Local large engineering/vendor binaries

The local artifact index records 110 high-value files by exact path/size/SHA. Not every large ZIP/STEP/vendor binary was copied, partly to avoid unnecessary duplication and partly because this connector does not have direct access to the local filesystem.

**Closure path:** run an owner-authorized local transfer using `LOCAL_ARTIFACT_INDEX.csv` as the inclusion list, deduplicate by SHA-256, and use Git LFS or Releases if normal Git blob limits/size make that appropriate.

### G-004 — File Library-only objects

File Library search exposes content references/previews but not a general raw-file export API to the GitHub connector.

**Closure path:** retrieve File Library-only binaries through a platform-supported download/export path or re-upload/mount them into a tool environment that can write raw bytes, then add them by hash without replacing newer authoritative files.

## Data not to export

Even in a future exhaustive transfer, exclude unless separately and explicitly required:

- API keys, passwords, passkeys, tokens and session cookies;
- browser credential/history databases;
- operating-system secrets;
- unrelated personal files;
- third-party copyrighted/vendor packages whose redistribution terms prohibit repository storage.

For restricted vendor material, store a source/provenance record and hash rather than redistributing protected bytes.

## Completion definition for a future literal full archive

A future archive may be called byte-complete only after all of the following are demonstrated:

1. raw STINGRAY ChatGPT transcripts exported and hashed;
2. all intended local CAD Git branches backed up with reachable objects and verified refs;
3. all included local engineering artifacts reconciled against `LOCAL_ARTIFACT_INDEX.csv` by SHA-256;
4. File Library-only STINGRAY files either copied or explicitly classified as duplicates/excluded/restricted;
5. GitHub branch/package inventories reconciled;
6. no secret or unrelated-personal-data leakage;
7. an automated manifest proves included/excluded counts and hashes.

Until then, describe this archive as **maximum-fidelity consolidated STINGRAY context with explicit retrieval gaps**, not as a literal byte-for-byte export of every upstream store.