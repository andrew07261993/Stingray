# STINGRAY — Canonical Engineering Context Archive

**Repository:** `andrew07261993/Stingray`  
**Branch:** `engineering/stingray-context`  
**Canonical path:** `engineering/stingray-context/`  
**Context snapshot date:** 2026-08-25

## Purpose

This directory is the canonical persistent context location for future STINGRAY engineering, CAD, COTS, procurement, analysis, validation and configuration-management work.

It consolidates every STINGRAY project/session fact, decision, artifact reference and repository source that was actually accessible from the ChatGPT-side environment during the 2026-08-25 harvest. It also explicitly records material that is known to exist but could not be byte-exported from this environment, so future agents do not silently assume that an inaccessible artifact was captured.

## Read in this order

1. `control/CURRENT_STATE.md`
2. `control/REQUIREMENTS.md`
3. `control/DECISION_REGISTER.md`
4. `control/CAD_PROVENANCE.md`
5. `control/VALIDATION_STATUS.md`
6. `GITHUB_BRANCH_AND_ARTIFACT_MANIFEST.md`
7. `FILE_LIBRARY_MANIFEST.md`
8. `SESSION_LEDGER.md`
9. `CHATGPT_CONTEXT_SNAPSHOT_2026-08-25.md`
10. `SOURCE_COVERAGE_AND_GAPS.md`
11. `LOCAL_RECOVERY_HANDOFF.md`

The earlier seed directory `context/stingray/` is preserved on this branch as source evidence. The files under `engineering/stingray-context/control/` are copied from that seed so this requested location is self-contained for its controlling context.

## Source precedence

When sources conflict, use this order unless a later explicit owner decision states otherwise:

1. Latest direct owner correction/decision tied to the same configuration.
2. Exact source artifact plus configuration ID, branch/commit, manifest and cryptographic hash.
3. Current validated CAD/source tree for the exact configuration being discussed.
4. Current primary manufacturer/vendor data for COTS facts.
5. Engineering reports/calculations that identify their source configuration.
6. Recovered ChatGPT session summaries and File Library excerpts.
7. Historical/superseded packages for provenance only.

Do **not** select authority from filename suffix, timestamp or narrative confidence alone.

## Completeness statement

This archive is a **maximum-fidelity export of the material exposed to this ChatGPT session**, not a claim that the platform exposed 100% of every raw byte ever created for STINGRAY.

Captured here or already preserved on this branch/repository:

- recovered STINGRAY project/session context and decisions;
- current requirements and open gates;
- CAD provenance and validation history;
- repository branch heads and major branch artifact inventories;
- preserved owner-inspection CAD ZIP/STEP packages already on `cad/df8-owner-creo-inspection-zips`;
- File Library artifact inventory, including CAD, reports, scripts, prompts, presentations, screenshots and research surfaced by the available search interface;
- explicit local-only/Codex gaps and a bounded recovery handoff.

Not byte-for-byte retrievable through the current ChatGPT/GitHub connector path:

- full raw ChatGPT conversation transcripts for every historical session;
- File Library binary bytes that are only exposed as File Library references rather than mounted files;
- local-only ANDREWSPC repositories/worktrees, unpushed commits and local Codex session/archive stores;
- any file that exists outside the connected GitHub repository/File Library and was never exposed to this session.

Those limitations are enumerated in `SOURCE_COVERAGE_AND_GAPS.md`; they must not be silently converted into `PASS`, `PRESENT`, or `VERIFIED` claims.

## Release boundary

Nothing in this context archive is fabrication release, procurement release, pressure-charging authorization, field-test authorization, qualification evidence, flight/operational release, or production release. Engineering conclusions remain tied to their identified configuration and evidence.

## Preservation rule

Do not modify or reorganize the historical CAD inspection packages under `cad/df8-owner-creo-inspection-zips/`. New context work is additive.