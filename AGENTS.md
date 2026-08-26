# STINGRAY Repository Instructions

These instructions apply to every Codex task started anywhere in this repository. The user is not responsible for reminding an agent where the engineering context lives.

## Mandatory startup

Before analyzing, modifying, validating or reporting on STINGRAY engineering work:

1. Identify the active repository, branch, commit and worktree state. Preserve every dirty or local-only worktree; never reset, clean, stash, discard or overwrite operator work.
2. Read `engineering/stingray-context/00_READ_ME_FIRST.md` completely.
3. Read `context/stingray/CURRENT_STATE.md`, `context/stingray/CONTEXT_INDEX.md`, `context/stingray/CAD_PROVENANCE.md` and `context/stingray/VALIDATION_STATUS.md`.
4. For COTS, vendor, procurement, BOM, pressure-system or buoyancy work, also read `context/stingray/COTS_MASTER_INDEX.md` before drawing conclusions.
5. Use `engineering/stingray-context/navigation/README.md` and its chronological/type indexes to locate detailed evidence. Do not ask the user to remember or restate this reading order.

If one of these files is absent on the checked-out branch, inspect `engineering/stingray-context` on `origin/engineering/stingray-context` without overwriting the current worktree. State the missing integration as a repository gap; do not invent context.

## Engineering authority

- Treat `context/stingray/CURRENT_STATE.md` as the current-state entry point, then verify claims against the exact source path, configuration, branch, commit, artifact hash and validation checkpoint recorded in the context.
- Keep the standard cross-device ChatGPT Project `Stingray` and the local Work/Codex project `STINGRAY` as separate evidence sources. Reconcile them through the indexes; do not collapse their provenance.
- Classify engineering claims only as `CURRENT`, `CURRENT DEVELOPMENTAL`, `HISTORICAL`, `SUPERSEDED`, `REJECTED`, `UNCERTAIN` or `EVIDENCE HOLD`.
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

Report the exact source path, branch, commit SHA, configuration, validation classification, unresolved evidence gaps, whether the protected CAD packages changed, and the pushed branch/commit. Future work must be able to resume from repository evidence without a verbal handoff from the user.
