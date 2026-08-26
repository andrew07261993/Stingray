# STINGRAY Engineering Context Index

Status: CHATGPT + LOCAL/CODEX ENGINEERING CONTEXT CONSOLIDATED — 2026-08-25

This directory is the controlled engineering memory for STINGRAY. It reconciles two separate project authorities:

- standard cross-device ChatGPT Project `Stingray`: the pre-existing ChatGPT-side harvest;
- local ChatGPT Work/Codex project `STINGRAY`: the local repositories, worktrees, content-scanned sessions and artifacts recovered on ANDREWSPC.

They are intentionally kept distinct and reconciled here. Neither source is an excuse to overwrite newer owner decisions or exact CAD evidence.

## Read first

1. `CONTEXT_INDEX.md` — authority, scope and routing.
2. `CURRENT_STATE.md` — exact newest CAD baseline and current engineering truth.
3. `CAD_PROVENANCE.md` — branch/commit/artifact chain and hashes.
4. `VALIDATION_STATUS.md` — what passed, what did not run and what remains physical.
5. `COTS_MASTER_INDEX.md` — 74 reconciled components/families and selection states.
6. `LOCAL_GIT_HISTORY.md` — all repositories, 19 worktrees/checkouts, 12 local-only CAD branches and dirty-state protections.
7. `LOCAL_ARTIFACT_INDEX.csv` — 110 exact local artifact paths, hashes and classifications.
8. `CODEX_SESSION_INDEX.md` — 79 content-indexed rollout records / 61 unique sessions, including archived history.
9. `DECISION_REGISTER.md` and `REQUIREMENTS.md` — current owner/configuration controls.
10. `RETRIEVAL_GAPS.md` — focused remaining evidence gates.

## Current anchor

Current developmental CAD:

- configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- path: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy`
- branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- classification: CURRENT DEVELOPMENTAL

This is the newest committed local CAD baseline, but it is not fabrication/procurement release or physical qualification.

## Authority order

When sources conflict, apply this order within the applicable configuration:

1. Newer explicit owner-approved requirement or decision.
2. Exact controlling source tree, branch/commit, internal manifest and artifact hashes.
3. Validation evidence generated from that exact source/configuration.
4. Current manufacturer/vendor evidence for the exact ordered configuration and installed interface.
5. Current engineering analysis and COTS selection record tied to that configuration.
6. Content-indexed session provenance and historical reports.
7. Superseded, rejected, uncertain or EVIDENCE HOLD material.

Do not use the most detailed, latest-numbered or visually impressive historical file as automatic authority. A targeted CAD PASS, owner screenshot or presentation does not establish release acceptance.

## Classification vocabulary

- CURRENT
- CURRENT DEVELOPMENTAL
- HISTORICAL
- SUPERSEDED
- REJECTED
- UNCERTAIN
- EVIDENCE HOLD

## Preservation and security controls

- `cad/df8-owner-creo-inspection-zips/` is a protected exact-byte inspection checkpoint and remains unchanged.
- Large CAD/ZIP/vendor collections were not duplicated; their exact paths, sizes and SHA-256 values are indexed.
- Dirty operator work was preserved and labeled EVIDENCE HOLD; it was not reset, cleaned, stashed, discarded or overwritten.
- Secrets, authentication stores, cookies, browser credential databases and unrelated personal content are excluded.
- No merge was performed as part of this consolidation.

## Configuration rule for 480 versus 355 mm

The 480.000 mm station is the fixed owner constraint for the pressure-packaging branches that were commissioned under that architecture; the 889 mm fallback is never a fixed-480 final geometry. The newer true-forward-powertrain/SHORT14 commission explicitly moved the pivot to 355.000 mm. Apply each constraint only to its exact configuration and never let the older fixed-480 study silently rewrite the newer owner-directed external-pack CAD.

## Practical handoff

Future agents should begin here, confirm the exact working branch/commit, then open the current source report and `VALIDATION_SUMMARY.md` in the SHORT14_FORWARD worktree. COTS work should begin with the three currently modeled BUY/proxy identities and the unresolved complete-module gate, not with broad new vendor research.
