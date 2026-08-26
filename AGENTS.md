# STINGRAY Repository Instructions

These instructions apply to every Codex task started anywhere in this repository. The user is not responsible for reminding an agent where the engineering context lives.

## Mandatory startup

Before analyzing, modifying, validating or reporting on STINGRAY engineering work:

1. Identify the active repository, branch, commit and worktree state. Preserve every dirty or local-only worktree; never reset, clean, stash, discard or overwrite operator work.
2. Read `context/stingray/00_CONTEXT_ISOLATION_STANDING_ORDER.md` completely and apply it before ingesting any other engineering narrative, summary, prompt or artifact.
3. Read `engineering/stingray-context/00_READ_ME_FIRST.md` completely.
4. Read `context/stingray/CURRENT_STATE.md`, `context/stingray/CONTEXT_INDEX.md`, `context/stingray/CAD_PROVENANCE.md` and `context/stingray/VALIDATION_STATUS.md`.
5. Read `context/stingray/CONTAMINATED_ARTIFACT_REGISTER.md` and exclude every registered artifact and unaudited derivative from technical authority and prompt source sets.
6. For COTS, vendor, procurement, BOM, pressure-system or buoyancy work, also read `context/stingray/COTS_MASTER_INDEX.md` before drawing conclusions.
7. Use `engineering/stingray-context/navigation/README.md` and its chronological/type indexes to locate detailed evidence. Do not ask the user to remember or restate this reading order.

If one of these files is absent on the checked-out branch, inspect `engineering/stingray-context` on `origin/engineering/stingray-context` without overwriting the current worktree. State the missing integration as a repository gap; do not invent context.

## Configuration isolation and contamination control

- Lock the target project, exact configuration/revision, authoritative source tree or artifact, branch/commit or file hash, owner decision, and release classification before technical work.
- Assign each source exactly one role: `TARGET AUTHORITY`, `SUPPORTING TARGET EVIDENCE`, `STYLE-ONLY EXEMPLAR`, `HISTORICAL/PROVENANCE ONLY`, `RESEARCH/CANDIDATE`, or `GENERATED NON-AUTHORITY`.
- A style-only source supplies wording and structure only. A generated output never becomes authority through repetition, recency, polish or reuse.
- No component, geometry, dimension, mechanism, load path, requirement, status, result or conclusion may cross configurations unless the target authority explicitly carries it forward or the owner expressly approves a documented carry-forward.
- When sources conflict, fail closed. Do not blend, reconcile, average, choose by recency, or create a hybrid. Preserve the conflict and obtain controlling target evidence or owner disposition.
- Use `VERIFIED` only for direct current target-configuration evidence. The presence of a statement in a report, script, render, filename, screenshot or non-target source does not verify target applicability.
- Quarantine contamination immediately, preserve the original hash, visibly mark the artifact, remove it from authority indexes, and treat derivatives as presumptively contaminated until audited.
- The incident audit at `context/stingray/2026-08-26_CONTEXT_PERMEATION_INCIDENT_AUDIT.md` is mandatory background for the current quarantine.

## Engineering authority

- Treat `context/stingray/CURRENT_STATE.md` as the current-state entry point, then verify claims against the exact source path, configuration, branch, commit, artifact hash and validation checkpoint recorded in the context.
- Keep the standard cross-device ChatGPT Project `Stingray` and the local Work/Codex project `STINGRAY` as separate evidence sources. Reconcile them through the indexes; do not collapse their provenance.
- Classify engineering claims only as `CURRENT`, `CURRENT DEVELOPMENTAL`, `HISTORICAL`, `SUPERSEDED`, `REJECTED`, `UNCERTAIN` or `EVIDENCE HOLD`, together with the target-bound evidence status required by the standing order.
- Newer owner decisions override older detailed work. Historical detail must never silently replace the current configuration.
- COTS remains a primary objective, but manufacturer identity, exact part number, published interface, installed geometry, rating, availability and qualification must remain evidence-backed.
- Never invent vendor geometry, rated interfaces, requirements, validation results, procurement status, certificates or PASS claims. Use `UNKNOWN`, `NOT DETERMINABLE`, `NOT RUN`, `NOT EVALUATED` or `NOT CALCULABLE` when evidence does not close a claim.
- Developmental CAD, targeted checks and owner inspection packages are not release acceptance.

## Preservation and delivery

- Do not modify, move, rename, regenerate or repackage anything under `cad/df8-owner-creo-inspection-zips/` unless the user explicitly authorizes that exact package operation.
- Do not copy large duplicate CAD, STEP, ZIP or binary collections into Git. Index large local artifacts by exact path, filename, SHA-256, configuration and relevance unless a transfer is explicitly authorized.
- If engineering work changes the actual state, provenance, validation, COTS selection or known gaps, update the corresponding files under `context/stingray/` in the same change.
- Keep `engineering/stingray-context/navigation/` usable as the GitHub browsing layer and preserve chronological iteration order.
- Do not merge branches, promote developmental work to release, procure parts or communicate externally without explicit authority.
- Exclude passwords, passkeys, API keys, tokens, cookies, credential databases and unrelated personal information.

## Required handoff

Report the exact source path, branch, commit SHA, configuration, source-role ledger, quarantined artifacts, validation classification, unresolved evidence gaps, whether the protected CAD packages changed, and the pushed branch/commit. Future work must be able to resume from repository evidence without a verbal handoff from the user.
