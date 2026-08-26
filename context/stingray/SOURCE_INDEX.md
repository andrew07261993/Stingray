# STINGRAY Source Index

As of: 2026-08-25.

## Project-source separation

- `Stingray` standard cross-device ChatGPT Project: source of the existing ChatGPT-side context harvest already present on `engineering/stingray-context` before local ingestion.
- `STINGRAY` local Work/Codex project: source of the ANDREWSPC repositories, worktrees, local session files and engineering artifacts indexed in this consolidation.

The distinction is owner-supplied and controlling. The current local Codex state database has no explicit named `projects` row for STINGRAY, so project identity is preserved through the owner statement, workspace paths, session content and repository provenance rather than invented metadata.

## Git sources

Primary local CAD object database:

`C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad`

Current CAD worktree:

`C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy`

Remote-backed documentation repository:

`C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-docs`

Remote:

`https://github.com/andrew07261993/Stingray`

Full repository/worktree/branch inventory is in `LOCAL_GIT_HISTORY.md`.

## Session sources

Content-scanned stores:

- `C:\Users\ANDRE.ANDREWSPC\.codex\sessions`
- `C:\Users\ANDRE.ANDREWSPC\.codex\archived_sessions`
- title metadata: `C:\Users\ANDRE.ANDREWSPC\.codex\session_index.jsonl`
- read-only structural metadata: `state_5.sqlite` and `thread_history_1.sqlite`

Result: 79 relevant rollout records representing 61 unique session IDs, 78 active-store records and one archived-store record. The scan matched actual message content after excluding app-injected context; it did not rely only on titles. Guardian/subagent and locally synchronized rollout forms were included where their content was STINGRAY-relevant. See `CODEX_SESSION_INDEX.md` for every source path and SHA-256.

## Local engineering artifact sources

High-value source trees include:

- all linked DF8 CAD worktrees from R2/state-parity through Package 05;
- `C:\Users\ANDRE.ANDREWSPC\CodexProjects\STINGRAY_CODEX_COMMISSION`;
- `C:\Users\ANDRE.ANDREWSPC\CodexProjects\stingray-cad-transition`;
- `C:\Users\ANDRE.ANDREWSPC\CodexProjects\stingray-final-delivery-work`;
- stakeholder/per-part deck clones and `stingray-ppt-build` source-derived images;
- local state-parity ZIP and dirty operator evidence retained in place.

`LOCAL_ARTIFACT_INDEX.csv` records 110 selected high-value files, 578,759,238 indexed bytes, exact paths, repository/worktree, branch, commit, date/configuration, relevance, classification, SHA-256 and size. The binaries were not duplicated into this context branch.

## COTS/vendor sources

Controlling local registers include:

- current external-pack component register;
- commercial automatic-module evidence/package screen;
- COTS-heavy 25-candidate BOM and final pressure-source BOM;
- targeted-COTS final BOM and technical closure/decision ledger;
- historical CONFIG-D selected-parts/vendor manifests and authentic vendor STEP files.

The consolidated result is `COTS_MASTER_INDEX.md` with 74 unique exact configurations or explicitly labeled product families.

## Bounded search scope

Searched:

- `C:\Users\ANDRE.ANDREWSPC\Documents\Codex`
- `C:\Users\ANDRE.ANDREWSPC\CodexProjects`
- actual `C:\Users\ANDRE.ANDREWSPC\.codex` (the prompt's path without the separator does not exist)
- Desktop, Documents and Downloads only through STINGRAY/I5-S/DF7/DF8/SHORT14/FORWARD/COTS/buoy/arm/powertrain/Creo/AP242/STEP-relevant names.

No broad crawl of unrelated personal/system content was used. `.venv`, `node_modules`, `.git` internals and credential/browser stores were excluded from artifact ingestion except where Git itself read repository metadata.

## Source-use rule

This directory is a control/index layer. For engineering action, open the exact source file at the recorded path and bind claims to the recorded branch/commit/hash. Session prose, screenshots and summary documents cannot substitute for controlling CAD, current vendor evidence or physical qualification.
