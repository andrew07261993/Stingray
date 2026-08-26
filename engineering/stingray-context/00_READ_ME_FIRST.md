# STINGRAY — Canonical Engineering Context Archive

**Repository:** `andrew07261993/Stingray`  
**Branch:** `engineering/stingray-context`  
**Canonical requested path:** `engineering/stingray-context/`  
**Context snapshot date:** 2026-08-25

## Purpose

This directory is the top-level routing point for persistent STINGRAY engineering context. The detailed source-of-truth control records already consolidated on this same branch remain under `context/stingray/`; this directory indexes them rather than creating divergent duplicate control files.

The 2026-08-25 local consolidation also recovered and indexed local Codex/Work history, local Git history and high-value local engineering artifacts before this top-level route was added.

## Read in this order

1. `../../context/stingray/CONTEXT_INDEX.md`
2. `navigation/README.md` — browse by iteration, analysis, validation, CAD/3D, renders/photos, PowerPoint, documents/PDFs, ZIPs and COTS/vendor/BOM
3. `../../context/stingray/CURRENT_STATE.md`
4. `../../context/stingray/CAD_PROVENANCE.md`
5. `../../context/stingray/VALIDATION_STATUS.md`
6. `../../context/stingray/REQUIREMENTS.md`
7. `../../context/stingray/DECISION_REGISTER.md`
8. `../../context/stingray/COTS_MASTER_INDEX.md`
9. `CHATGPT_PROJECT_CONTEXT_SNAPSHOT_2026-08-25.md` — recovered cross-session engineering narrative and failure-prevention rules
10. `../../context/stingray/LOCAL_GIT_HISTORY.md`
11. `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`
12. `../../context/stingray/CODEX_SESSION_INDEX.md`
13. `SESSION_LEDGER.md` — additional cross-device ChatGPT session chronology
14. `GITHUB_BRANCH_AND_ARTIFACT_MANIFEST.md`
15. `FILE_LIBRARY_MANIFEST.md`
16. `SOURCE_COVERAGE_AND_GAPS.md`
17. `EXPORT_MANIFEST.json` — machine-readable snapshot/coverage manifest

## Current developmental anchor

The locally recovered source-of-truth identifies the newest committed CAD baseline as:

- configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- local CAD branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- classification: **CURRENT DEVELOPMENTAL**

The current CAD source repository itself has no remote. Exact current endpoint STEP files and the current inspection ZIP are preserved in the GitHub owner-inspection checkpoint as Package 05; local source paths, hashes, reports and additional artifacts are indexed in `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`.

## Source precedence

When sources conflict, use this order within the applicable configuration:

1. Latest direct owner correction/decision tied to that configuration.
2. Exact source artifact plus configuration ID, branch/commit, manifest and cryptographic hash.
3. Validation evidence generated from that exact source/configuration.
4. Current primary manufacturer/vendor data for the exact COTS configuration.
5. Engineering reports/calculations tied to that configuration.
6. Content-indexed session provenance.
7. Historical/superseded material for provenance only.

Do **not** select authority from filename suffix, timestamp, presentation quality or narrative confidence alone.

## What is already captured

- Current local CAD provenance, exact branch/commit and validation status.
- 79 relevant Codex rollout records representing 61 unique session IDs, content-indexed.
- Four Git repository/clone roots and 19 worktrees/checkouts indexed.
- All 12 branches in the shared local CAD repository identified; their SHAs and roles are recorded.
- 110 high-value local artifacts indexed by exact path, configuration/status, size and SHA-256.
- 74 COTS exact configurations/product families reconciled.
- Five owner-inspection CAD packages preserved in GitHub, including current Package 05 STEP endpoints and ZIP.
- Cross-device ChatGPT STINGRAY workstreams summarized in `SESSION_LEDGER.md`.
- A configuration-scoped recovered ChatGPT project narrative in `CHATGPT_PROJECT_CONTEXT_SNAPSHOT_2026-08-25.md`.
- GitHub branch/artifact and File Library manifests.
- Explicit retrieval/security gaps plus a machine-readable `EXPORT_MANIFEST.json`.

## What cannot truthfully be called a 100% byte export from this interface

1. **Cloud-only ChatGPT raw transcripts:** this interface does not expose a byte-for-byte export of every historical cloud conversation. Recovered context is indexed/summarized; unavailable message text is not invented.
2. **Local-only Git objects and large binaries:** the local CAD repository has no remote. Its 12 branch SHAs and 110 high-value artifacts are indexed, but unpushed Git objects and large local-only CAD/vendor binaries are not all present in GitHub.
3. **File Library-only binary bytes:** the File Library search interface exposes references/content previews, not a general byte-copy API to GitHub. Those items are inventoried in `FILE_LIBRARY_MANIFEST.md`; equivalents already in GitHub are cross-referenced.
4. **Secrets and unrelated personal data:** authentication stores, passwords, passkeys, API keys, tokens, cookies and unrelated personal content are intentionally excluded.

These are connector/source-access boundaries, not hidden `PASS` results. See `SOURCE_COVERAGE_AND_GAPS.md`.

## Release boundary

Nothing in this context archive is fabrication release, procurement release, pressure-charging authorization, field-test authorization, qualification evidence, flight/operational release or production release. Engineering conclusions remain tied to their exact configuration and evidence.

## Preservation rule

Do not modify or reorganize `cad/df8-owner-creo-inspection-zips/`. New context work is additive.
