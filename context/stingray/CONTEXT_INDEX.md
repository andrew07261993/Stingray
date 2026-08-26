# STINGRAY Engineering Context Index

Status: CHATGPT-SIDE CONTEXT HARVEST — 2026-08-25

This directory is the repository-level engineering memory for STINGRAY. It is intentionally separate from `cad/df8-owner-creo-inspection-zips/`, which must remain unchanged.

## Read first

1. `CURRENT_STATE.md`
2. `REQUIREMENTS.md`
3. `DECISION_REGISTER.md`
4. `COTS_MASTER_INDEX.md`
5. `CAD_PROVENANCE.md`
6. `VALIDATION_STATUS.md`
7. `SOURCE_INDEX.md`
8. `RETRIEVAL_GAPS.md`

## Authority order

When sources conflict, use this order unless a newer explicit owner decision states otherwise:

1. Explicit current owner-approved requirements/decisions.
2. Exact current CAD source + validated configuration records.
3. Current vendor/manufacturer evidence.
4. Current engineering analysis tied to the applicable configuration.
5. Current COTS selection records.
6. Historical ChatGPT/Codex engineering work.
7. Superseded/rejected material.

Do not treat the most detailed or highest-numbered historical file as automatically authoritative. Check configuration ID, date, branch/commit, owner decisions, release classification, manifests and hashes.

## Classification vocabulary

Use these labels consistently:

- CURRENT
- CURRENT DEVELOPMENTAL
- HISTORICAL
- SUPERSEDED
- REJECTED
- UNCERTAIN
- EVIDENCE HOLD

## Immediate local-ingest task

The ChatGPT-side harvest cannot directly inspect all files and Codex session stores on ANDREWSPC. Codex Desktop should next ingest local STINGRAY repositories/worktrees, local engineering artifacts and Codex session history into this same directory without modifying the preserved CAD inspection tree. See `RETRIEVAL_GAPS.md`.