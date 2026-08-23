# STINGRAY I5-S DF8 — SAFE CODEX HANDOFF CHECKPOINT AND CONTROLLED TERMINATION

Preserve the exact newest active state.

Do not restart the commission, repeat inventory, revert source files, discard current edits, regenerate unaffected work, begin another correction cycle, export a premature final release, or replace the latest source with an older checkpoint.

Complete only the atomic command, source-file write, or geometry patch that is currently in progress.

Then stop beginning new geometry corrections and create:

`STINGRAY_I5S_DF8_R2_CODEX_HANDOFF_CHECKPOINT.zip`

The handoff ZIP shall contain every file required to reproduce and continue the current execution state in a local Codex working directory, including:

1. the newest complete editable source tree;
2. all current CadQuery, OCP/OCCT, XCAF, Python, workbook, validation, audit, hierarchy, packaging, and utility scripts;
3. all current configuration files;
4. dependency manifests and environment information;
5. Python version and installed package versions;
6. all source-backed component and assembly definitions;
7. all current STOWED and DEPLOYED build inputs;
8. all current occurrence, transform, hierarchy, attachment, procurement, and BOM source data;
9. the newest audit results;
10. the newest per-solid STOWED and DEPLOYED results;
11. the newest positive-common-volume occurrence-pair register;
12. all authorized-contact classification data;
13. all open invalid-interference data;
14. all current NCR and gate status data;
15. all workbook-generation source data;
16. the latest candidate-WIP package;
17. the latest exact-solid intermediate files needed to reproduce the current state;
18. the current output directory;
19. all files presently stored only under `/tmp` that are required to reproduce or continue the work;
20. a complete file manifest;
21. SHA-256 hashes for every handoff file.

Do not leave any required resumption file solely in `/tmp` or another ephemeral directory.

Create the following root-level handoff documents inside the ZIP:

## A. HANDOFF.md

Record:

- controlling commission;
- current execution phase;
- latest completed checkpoint;
- exact source directory that is authoritative;
- exact last successful modifying command;
- exact last successful audit command;
- exact commands required to rebuild STOWED;
- exact commands required to rebuild DEPLOYED;
- exact commands required to rerun endpoint audits;
- exact command required to run the 0°–80° motion audit;
- exact commands required for AP242 export;
- exact commands required for clean OCP/XCAF reimport;
- exact command required to regenerate the workbook;
- exact command required to produce the final three-file ZIP;
- latest measured interference/contact counts;
- remaining unresolved occurrence pairs;
- all open non-Creo gates;
- all closed gates;
- all current NCRs;
- current hierarchy/product/occurrence counts;
- current measured OD, length, mass, and mass reserve where available;
- known fragile scripts or operations;
- all assumptions still active;
- all owner decisions that must not be reopened.

## B. CURRENT_STATE.json

Include machine-readable fields for:

- checkpoint timestamp;
- authoritative source path;
- last command;
- last exit code;
- last modified files;
- latest stowed audit metrics;
- latest deployed audit metrics;
- latest motion-audit metrics;
- remaining positive pairs;
- authorized intentional contacts;
- invalid rigid interferences;
- validator defects;
- hierarchy counts;
- open gates;
- open NCRs;
- final-artifact status;
- dependency versions.

## C. RESUME_COMMANDS.md

Provide copy-and-paste commands that a fresh local environment can use to:

1. install dependencies;
2. verify the checkpoint;
3. run a non-modifying source integrity check;
4. reproduce the latest STOWED audit;
5. reproduce the latest DEPLOYED audit;
6. continue the bounded corrective sequence.

## D. SHA256SUMS.txt

Hash every file included in the handoff package.

## HANDOFF VALIDATION

Before terminating:

1. extract the handoff ZIP into a clean temporary directory;
2. verify every SHA-256 entry;
3. verify `HANDOFF.md`, `CURRENT_STATE.json`, and `RESUME_COMMANDS.md` exist;
4. verify no required file points only to an unavailable absolute or ephemeral path;
5. verify the authoritative source tree is present;
6. verify the primary Python files parse successfully;
7. verify the checkpoint can at least begin a non-modifying validation command;
8. record the handoff ZIP SHA-256.

After the handoff ZIP is verified:

- stop all subagents;
- stop all geometry-editing processes;
- stop all audit rerun loops;
- do not begin final packaging;
- preserve all existing Work files;
- leave the execution at the verified handoff checkpoint.

Return only:

1. the download link to `STINGRAY_I5S_DF8_R2_CODEX_HANDOFF_CHECKPOINT.zip`;
2. its SHA-256;
3. the authoritative source path included in the ZIP;
4. the last successful modifying command;
5. confirmation that all subagents and active correction processes have stopped.
