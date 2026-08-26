# STINGRAY File Library Manifest

As of: 2026-08-25

## Scope and fidelity

This is the STINGRAY artifact inventory recovered through the ChatGPT File Library search interface during context consolidation. The File Library exposes searchable file references/content previews; it does **not** expose a general binary-copy operation from every File Library object directly into GitHub. Therefore this manifest records the surfaced artifacts, their engineering role and provenance status, while exact GitHub-resident copies are referenced where available.

The deeper local-machine recovery independently indexed **110 high-value local artifacts with exact paths, configuration/status, file size and SHA-256** in `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`. That index is the controlling catalog for recovered local artifacts.

Duplicates surfaced by multiple File Library searches are listed once here.

## A. Early transition / reference-model packages and manifests

| File | Approx. date | Role / status |
|---|---|---|
| `STINGRAY_CAD_TRANSITION_MASTER_PROMPT.md` | 2026-08-10 | Historical transition prompt; establishes `STG-REF-BL-001` and simplified release-sleeve reference-model policy |
| `STINGRAY_CAD_TRANSITION_MASTER_PROMPT.txt` | 2026-08-10 | Text duplicate/companion of historical transition prompt |
| `STINGRAY_SINGLE_PASTE_CAD_TRANSITION_PROMPT.md` | 2026-08-10 | Historical single-paste CAD transition kickoff |
| `STINGRAY_SINGLE_PASTE_CAD_TRANSITION_PROMPT.txt` | 2026-08-10 | Text companion if present in File Library |
| `00_READ_ME_FIRST.md` | 2026-08-11 | Three-step reality-to-CAD workflow instructions |
| `01_PASTE_THIS_INTO_FINAL_DESIGN_GPT.txt` | 2026-08-11 | Reality-to-CAD commission prompt |
| `STINGRAY_DIRECT_TO_CODEX_SINGLE_PASTE.txt` | 2026-08 | Historical direct-to-Codex handoff surfaced in prior searches |
| `01_INPUT_INVENTORY.md` | 2026-08-10 | Early source/input inventory; includes explicit non-STINGRAY supporting-file classifications |
| `PACKAGE_FILE_INDEX.md` | 2026-08-10 | Early package file index including CadQuery source, docs, reports and multiple STEP states |
| `PACKAGE_MANIFEST.json` | 2026-08-10 | Early package machine-readable manifest with file sizes and SHA-256 |

These materials are provenance/history. They do not supersede the current SHORT14 true-forward-powertrain configuration.

## B. Iteration-5 / DF7 corrective and continuation artifacts

| File | Approx. date | Role / status |
|---|---|---|
| `Coaxial_Pneumatic_Deployment_Master_Handoff.md` | 2026-08-07 | Historical pneumatic-architecture handoff; contains explicit cylinder/configuration verification gates |
| `STINGRAY_ITERATION5_FINAL_REMEDIATION_PROMPT.md` | 2026-08-12 | Iteration-5 corrective architecture prompt |
| `STINGRAY_ITERATION5_FINAL_REMEDIATION_PROMPT.txt` | 2026-08-12 | Text companion |
| `STINGRAY_DF7_R2_RECONCILIATION_FINDINGS_AND_REQUIRED_CHANGES.md` | 2026-08 | DF7-R2 reconciliation findings surfaced in prior search |
| `STINGRAY_DF7_R2_CORRECTIVE_CONTINUATION_PACKAGE.zip.sha256` | 2026-08-17 | SHA-256 record: `6b11d6cff5474c43e23c7d1bf521164d01de9fa8c7f061db7402c8b835974423` |
| `STINGRAY_I5S_DF7_R3_CONTROLLED_CORRECTIVE_ENGINEERING_PACKAGE_2026-08-17.sha256` | 2026-08-17 | SHA-256 record: `0cac61e827c1dfcaaa9d8aa6187972c88d08fccb8f504f422673a27981853e34` |
| `STINGRAY Iteration-5 Fresh-Thread Engineering Continuation: Evidence Reconciliation and Corrective Work Package` | 2026-08 | Historical continuation/handoff document surfaced in prior search |

An older pasted research artifact asserted incompatible Swagelok dimensions/volume as fact. Treat that artifact as **historical/superseded evidence**, not current engineering authority; later work explicitly required manufacturer dimensional verification before freezing the receiver configuration.

## C. DF8 architecture and subsystem prompts / source records

| File | Approx. date | Role / status |
|---|---|---|
| `STINGRAY_DF8_ALL_SIX_SUBSYSTEM_PROMPTS_COMBINED.md` | 2026-08-18 | Combined WP01–WP06 controlled subsystem prompts |
| `06_DF8_WP06_FINAL_INTEGRATION_AND_TWO_STATE_MASTER_PROMPT.md` | 2026-08-18 | WP06 final integration/two-state master commission |
| `STINGRAY_I5S_DF8_SPRING_EJECTOR_ARCHITECTURE_DEVELOPMENT_2026-08-18.sha256` | 2026-08-18 | Parent-archive SHA-256: `6da4deb5e920ab819ffc1ce720ef7934c792a539416b51f7b78acf18f76bed60` |
| `STINGRAY_I5S_DF8_R0_ARCHITECTURE_MASTER_AP242.step` | 2026-08-18 | Historical DF8-R0 architecture master |
| `WP01_DIGITAL_ACCEPTANCE_SUMMARY.json` | 2026-08-18 | WP01 digital acceptance; zero body-owned positive common-volume pairs, external evidence holds retained |
| `build_wp02.py` | 2026-08-19 | Reproducible WP02 arm/powertrain build source; historical configuration-specific logic |
| `WP03_MODEL_INDEX_AND_MASS_PROPERTIES.json` | 2026-08-19 | WP03 configuration/component occurrence, mass and geometry index |
| `build_wp03.py` | 2026-08-19 | Reproducible WP03 build source |
| `STINGRAY_I5S_DF8_WP05_AFT_CLOSURE_SERVICE_AND_RESET_STOWED_AP242.step` | 2026-08-19 | WP05 STOWED AP242 |
| `STINGRAY_I5S_DF8_WP05_AFT_CLOSURE_SERVICE_AND_RESET_DEPLOYED_AP242.step` | 2026-08-19 | WP05 DEPLOYED AP242 |
| `STINGRAY_I5S_DF8_WP06_DELIVERY_VERIFICATION.md` | 2026-08-20 | WP06 delivery verification recorded `FAIL`; final ZIP did not exist at that checkpoint |
| `STINGRAY_I5S_DF8_R1_WP06_INTEGRATION_CHECKPOINT_2026-08-19_SHA256.txt` | 2026-08-20 | Checkpoint ZIP hash `2facf0f12e85cd800b22e0b5c83937f883072f9a6264448000e5bfd13ee4f65f`, CRC integrity PASS, 22 members |
| `README_FIRST.md` | 2026-08-20 | DF8-R1 WP06 recovered integration checkpoint; explicitly not final WP06 release |
| `README_FIRST(1).md` | 2026-08-20 | Waterjet DXF development package; explicitly not fabrication/procurement release |

## D. Ø2.250-in arm redesign and stakeholder-review CAD

| File | Approx. date | Role / status |
|---|---|---|
| `CAD_DESIGN_INPUT_REGISTER.csv` | 2026-08-20 | Controlled/provisional design-input register for envelope, arm, root, pivot, HBD, GS-19, locks, retention, materials, service, etc. |
| `Pasted markdown.md` — `STINGRAY I5-S DF8 — Ø2.250-IN FINAL STAKEHOLDER-REVIEW CAD BUILD COMMISSION` | 2026-08-20 | Final detailed CAD-build commission; historical full-length 733.806-mm configuration context |
| `STINGRAY_I5S_DF8_CRDS01_2P25_ARM_BASE_STOWED_AP242.step` | 2026-08-20 | CRDS01 redesign-study STOWED geometry |
| `STINGRAY_I5S_DF8_2P25_ARM_BASE_STOWED_AP242.step` | 2026-08-20 | 2.250-in arm-base STOWED artifact surfaced in prior search |
| `STINGRAY_I5S_DF8_2P25_ARM_MODULE_STOWED_AP242.step` | 2026-08-20 | Arm-module STOWED AP242 |
| `STINGRAY_I5S_DF8_2P25_ARM_MODULE_DEPLOYED_AP242.step` | 2026-08-20 | Arm-module DEPLOYED AP242 |
| `STINGRAY_I5S_DF8_2P25_FINAL_STOWED_MASTER_AP242.step` | 2026-08-20 | Historical 2P25 full-system STOWED master |
| `STINGRAY_I5S_DF8_2P25_FINAL_DEPLOYED_MASTER_AP242.step` | 2026-08-20 | Historical 2P25 full-system DEPLOYED master |
| `STINGRAY_I5S_DF8_R1_STOWED_MASTER_AP242.step` | 2026-08-20 | Historical R1 STOWED master |
| `STINGRAY_I5S_DF8_R1_DEPLOYED_MASTER_AP242.step` | 2026-08-20 | Historical R1 DEPLOYED master |

These are important historical geometry/provenance, but the current local source-of-truth is the later SHORT14/true-forward-powertrain/external-buoy configuration identified in `../../context/stingray/CURRENT_STATE.md`.

## E. Presentations, part breakdown and review artifacts

| File | Approx. date | Role / status |
|---|---|---|
| `STINGRAY_DF8_Stakeholder_System_Briefing.pptx` | 2026-08-21 | Stakeholder briefing with detailed source/vendor appendices; historical status statements must be interpreted at its date/configuration |
| `STINGRAY_I5S_DF8_STAKEHOLDER_SYSTEM_REVIEW_FINAL.pptx` | 2026-08-23 | Stakeholder system review presentation; historical full-length geometry values |
| `STINGRAY_I5S_DF8_MECHANICAL_BREAKDOWN_REVIEW.pptx` | 2026-08-23 | Mechanical breakdown review deck |
| `Pasted markdown (4).md` | 2026-08-24 | Per-part deck/render status: 116 deterministic renders, 104 MAKE + 12 BUY, validation PASS for render set; raw status includes superseded motion-validation limitation |
| `Pasted markdown (6).md` | 2026-08-24 | Stakeholder deck quality/repository-delivery instructions and execution status |

Presentation content is explanatory evidence, not automatic design authority. Where a deck conflicts with a later source branch or validation report, use the later exact source/configuration.

## F. Screenshots and visual session evidence

| File | Approx. date | Role / status |
|---|---|---|
| `E45CDA84-087F-4F61-A4DF-51F131BB6555.png` | 2026-08-13 | Mobile screenshot of STINGRAY remediation/COTS research workflow |
| `0DD29183-9DD3-4BCD-B46E-82EFA499EED2.png` | 2026-08-13 | Mobile screenshot documenting Perplexity-vs-Codex research/CAD workflow guidance |
| `IMG_4214(1).png` | 2026-08-23 | Mobile screenshot of STOWED/DEPLOYED computational audit progress |
| `F7CA155B-E5BF-4914-9B96-580F4D2B7729.jpeg` | 2026-08-22 | Safe Codex handoff/checkpoint screenshot |
| `IMG_4241.png` | 2026-08-23 | Mobile Remote session/file list showing multiple STINGRAY/COTS/deck sessions |

Screenshots are secondary provenance/UX evidence. They are not a substitute for exact source files or repository history.

## G. COTS / external-buoy / research artifacts

| File | Approx. date | Role / status |
|---|---|---|
| `STINGRAY DF8 External Pack Buoyancy Aid Selection and Configuration` | 2026-08 | External-pack buoyancy selection/configuration research surfaced in prior search |
| `U.S.-Based Alternatives and Analogues to the SECUMAR Pack Buoyancy Aid with SECUTRONIC` | 2026-08-25/26 UTC | U.S. equipment-flotation alternatives research; Subsalve/Airborne/Halkey etc.; not a component-selection release |
| `Pasted text.txt` | 2026-08-21 | Search/retrieval instructions for WP03/WP04/WP05/WP06, CRDS01 and R1 evidence |

Current CAD truth is narrower than these research files: the current branch models an external 60 L custom softgoods pack with Leland `81121`, Halkey-Roberts Hydro 1F-family proxy and `V80040` bobbin. SECUMAR remains an uncertain research candidate, not an installed owner-selected module.

## H. Known complete package content represented by manifests

The early `PACKAGE_MANIFEST.json` / `PACKAGE_FILE_INDEX.md` explicitly index a CadQuery package containing, among other things:

- Python source tree under `stingray-cadquery/src/stingray/`;
- design/baseline/interface/load-path/operating-state/Creo-handoff/open-RFI documentation;
- machine-readable export/build/test/validation reports;
- multiple STEP assembly states such as armed/stowed, release initiation, penetration, initial separation, partial deployment, deployed/locked, exploded and cutaway/reference states.

Those early files are historical reference-model evidence and should not be merged blindly into later DF8 geometry.

## I. File Library byte-transfer limitation

The File Library objects above remain part of the user's ChatGPT File Library. This context consolidation can search and cite them, but the available interface does not provide a general operation to stream every arbitrary File Library binary into a GitHub commit. Accordingly:

- exact local equivalents already recovered are indexed by path/hash in `../../context/stingray/LOCAL_ARTIFACT_INDEX.csv`;
- exact GitHub-resident CAD checkpoint binaries are preserved under `cad/df8-owner-creo-inspection-zips/`;
- File Library-only items are retained here by exact title/role and should be fetched from the File Library when their full binary/content is required;
- no missing bytes are fabricated or reconstructed from snippets.