# STINGRAY ChatGPT Project Context Snapshot — 2026-08-25

## Purpose

This file preserves the high-value engineering context recovered across the cross-device ChatGPT `Stingray` project and recent STINGRAY sessions. It is a **configuration-aware narrative snapshot**, not a substitute for exact CAD/source artifacts.

Where this snapshot conflicts with a later exact source file, branch/commit/hash, manufacturer record or direct owner correction, the later exact configuration-specific evidence controls.

---

## 1. Mission and persistent system intent

STINGRAY is a manually handled recovery device intended to be thrown from an H-60 helicopter toward a parachute/canopy floating on the water and at risk of sinking. The persistent mission intent across the program is:

1. enter nose-first and penetrate/engage the parachute fabric;
2. authorize deployment through water exposure rather than electronics/pyrotechnics;
3. deploy three arms after water authorization even if fabric is present/tangled;
4. use positive hard stops/locks and a structural recovery load path;
5. bring a buoyancy/recovery element to the surface so the canopy/equipment can be recovered rather than sink;
6. remain resettable/serviceable and suitable for marine/saltwater handling;
7. avoid relying on nonstructural inflation hardware as the recovery load path.

Persistent architecture principles:

- three arms at 0° / 120° / 240°;
- deployed angle approximately 80°;
- positive stowed retention and positive deployed locks;
- water is the sole deployment authorization in the accepted analog architecture;
- transport/rain/spray cases must not cause unintended deployment;
- recovery load must bypass inflator/trigger/nonstructural soft cover unless a manufacturer provides an explicit rated structural path;
- no pyro/electric actuation is required by the baseline architecture;
- reset/service must be controlled and mechanically positive.

---

## 2. Configuration evolution — do not merge these blindly

### 2.1 Early reference-model phase

Historical reference baseline:

- baseline ID: `STG-REF-BL-001`;
- selected reference architecture: `CONFIG-D-SIMPLIFIED-RELEASE-SLEEVE` / simplified release-sleeve independent-arm configuration;
- reference arm length: 28.89 in nominal, ±2 in at that stage;
- reference body: 2.000 in OD / 1.750 in ID;
- reference body length: 63 in ±5 in;
- master origin at penetrator tip, +Z aft;
- classification was explicitly reference-modeling only, not fabrication/field-test release.

Early CadQuery packages, multi-state STEP exports and prompt packages are historical provenance only.

### 2.2 Iteration-5 / DF7 period

The DF7 lineage matured the project from conceptual/reference geometry toward controlled digital prototypes. Key historical facts include:

- DF7-R2 canonical master was identified in prior work with 176 solids, 85 occurrences and 21 states;
- nominal rigid length approximately 1300 mm; worst case approximately 1308.4 mm in that configuration;
- normal-body OD approximately 53.0 mm;
- a large localized arm-module bulge existed in the older architecture;
- red-team review found positive-volume overlaps, kinematic contradictions and insufficient drawings/PMI/COTS evidence;
- backup spring deployment was required with GS-19 force set to zero;
- positive buoy-pack extraction architecture became an explicit design gate;
- DF7-R3 was a controlled corrective engineering successor, not permission to ignore unresolved physical/procurement gates.

### 2.3 DF8 subsystem work packages

DF8 was decomposed into subsystem work packages:

- WP01 — body/envelope/datums;
- WP02 — arm/powertrain;
- WP03 — water activation/inflation;
- WP04 — spring ejector/buoy pack;
- WP05 — aft closure/service/reset;
- WP06 — integration/two-state master.

Owner approvals repeatedly authorized recommended defaults where explicitly recorded. Those approvals were configuration-bound and did not erase later owner corrections.

Historical subsystem intent included:

- body nominal OD approximately 53.0 mm;
- spring-assisted positive buoy-pack extraction rather than relying on CO2 pressure merely to push fabric out of the body;
- start inflation during/after extraction in a controlled sequence;
- avoid direct spring-to-fabric contact;
- manual service/reset force target on WP05 up to 100 N in the accepted Q-set;
- removal of safety-pin requirements where they conflicted with owner direction.

### 2.4 Ø2.250-in arm-module redesign

A major redesign was triggered by parachute snag risk around the prior arm-module bulge. The controlled limits became:

- internal rigid control target: approximately 56.00 mm;
- hard maximum rigid OD: **57.15 mm / 2.250 in**;
- complete ready-to-throw system mass hard maximum: **18.14 kg / 40.0 lb**;
- rigid length hard maximum: **2032 mm**.

For the full-length 2P25 configuration, the owner accepted:

- arm length 733.806 mm pivot-to-tip;
- common crosshead / three-link mechanism;
- crosshead travel at least 15.050 mm, design approximately 16 mm;
- positive deployed locks and structural hard stops;
- stowed retention initial design load about 0.8 kN per arm;
- primary actuator ACE `GS-19-50-V4A-B8-B8`;
- direct damper ACE `HBD-15-25-AA-P`;
- no bypass/lost-motion/fuse required solely for HBD seizure;
- HBD mechanical seizure accepted as a single-point deployment failure;
- no-damping case still required structural survival.

Historical backup-spring envelope/sizing for that full-length configuration was approximately:

- OD ≤15.8 mm;
- free length ≈195 mm;
- stowed ≈145 mm;
- deployed ≈160.05 mm;
- rate ≈16 N/mm;
- stowed force ≈800 N;
- end force ≈559 N;
- work ≈10.2 J;
- solid height ≤138 mm;
- spring + seat mass ≤0.13 kg.

These numbers are historical to that configuration; do not apply them automatically to SHORT14 without exact source confirmation.

---

## 3. Validation/correction lineage

### 3.1 Bounded correction policy

The project explicitly moved away from open-ended correction loops. A bounded continuation directive allowed at most two additional correction cycles for the final R2 convergence. Required audits included:

- exact STOWED and DEPLOYED BREP audits;
- zero invalid solids;
- zero blocked Boolean operations;
- classification of every positive-common-volume pair;
- attachment/floating-part checks;
- motion audit through the required arm range;
- non-regression of envelope, mass and mechanism requirements;
- OCP/XCAF reimport as the controlling neutral-CAD validation gate where Creo was not available.

### 3.2 State parity / provenance audit

The state-parity/provenance audit eventually resolved **64 original mismatches**:

- Category A: 30;
- Category B: 34;
- Category C: 0;
- final corrected validator result: **279 / 279 occurrences passing**, zero unresolved.

Root cause: the former validator incorrectly treated serialized OCCT local-BREP bytes as geometric identity. Reimport behavior showed the digest was process-unstable/non-semantic. Fixed occurrences retained invariant transforms; moving occurrences had mechanism-declared state changes.

This was a validator/provenance defect, not proof of a CAD geometry defect.

### 3.3 Evidence-first claim control — standing engineering rule

A later failure analysis established a cross-session corrective rule:

> Never infer artifact contents from a filename, prior narrative, visual impression, or expected architecture.

For every material engineering claim, future agents must separate at least:

1. **existence** — does the artifact/component actually exist in the inspected source?
2. **identity** — what exact part/configuration/branch/revision is it?
3. **provenance** — where did it come from and what evidence/hash/commit identifies it?
4. **geometry/packaging** — does the exact item physically fit in the stated orientation/envelope?
5. **function/capacity** — can it perform the required mechanical/pressure/buoyancy/actuation function?
6. **validation status** — was the claim measured, calculated, inferred, proxied, or physically tested?
7. **configuration applicability** — is the evidence for the same configuration now being discussed?
8. **release status** — CAD PASS is not physical/procurement/qualification/operational release.

If any layer is not confirmed, label the claim `UNCERTAIN`, `EVIDENCE HOLD`, `PROXY`, `PROVISIONAL` or equivalent instead of silently treating it as true.

This rule specifically exists to prevent a CAD model from appearing mechanically complete while containing a gas source, cylinder arrangement, buoyancy component or other subsystem that is only visually/nominally represented and cannot perform the required function.

---

## 4. Gas source / buoyancy lessons recovered from later sessions

A recurring failure mode was assuming a cylinder arrangement from schematic or incomplete CAD without proving the exact physical pressure-vessel geometry and required gas capacity.

Required corrective practice:

- determine required gas mass/volume/pressure from the buoyancy and arm-actuation duty;
- identify the exact commercially available pressure vessel(s), including OD, length, working pressure, internal volume, porting and mass;
- confirm orientation and count against the actual body ID/available bay geometry;
- do not call a pack of multiple parallel cylinders equivalent to a single longitudinal cylinder unless the exact installed geometry proves it;
- do not use a vendor family name or approximate capacity as a dimensional substitute;
- treat a CAD placeholder/proxy as a proxy in BOM, deck, renders and validation reports.

The historical Swagelok miniature-cylinder work contained a dimensional/capacity ambiguity and therefore remains a verification example, not unquestioned authority.

---

## 5. External buoy / equipment-flotation direction

The owner clarified that the relevant product class is **equipment-oriented automatic/command inflatable flotation**, not personal PFD/LPU products.

U.S.-based research later screened analogues and suppliers including Subsalve, Airborne Systems and Halkey-Roberts/Nordson technologies. That research is useful for sourcing/architecture evidence but does not constitute component selection or release.

The current SHORT14 CAD does **not** implement a complete commercial SECUMAR system. Current context identifies:

- custom external softgoods buoy pack, approximately 60 L modeled capacity;
- Leland `81121`, one 12 g CO2 cartridge;
- Halkey-Roberts Hydro 1F-family `V95000XXB` dimensional proxy;
- Halkey-Roberts `V80040` water-sensitive bobbin.

Current classification:

- the complete external-pack implementation is developmental;
- `SECUMAR` 350 N/SECUTRONIC remains an `UNCERTAIN` research candidate only;
- a complete `470-CG` / `V95000-1F` family was measured at 127 mm across and rejected for the fixed-480 50.700-mm bore;
- UML module families remain on evidence hold where exact complete installed geometry is missing.

---

## 6. COTS / procurement program direction

The owner favors genuinely orderable COTS where it reduces fabrication burden without weakening safety, packaging or verification.

Key persistent selection rules:

- COTS must be real and orderable, not merely a representative vendor family;
- exact suffix/configuration matters;
- configured performance must not be inferred from catalog maximums;
- exact CAD/drawing envelope and mounting interfaces matter;
- procurement evidence, application approval, CoC/certification and received-item verification are separate gates from design selection;
- custom adapters are acceptable where necessary, but the trade should be explicit;
- no COTS substitution may silently invalidate the recovery load path, water trigger authorization, 57.15-mm rigid envelope or mass/length constraints.

The current context index reconciles 74 COTS exact configurations/product families across current, developmental, historical, rejected and evidence-hold states.

---

## 7. Current developmental configuration — controlling engineering anchor

The newest recovered committed local CAD baseline is:

`STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`

Exact source:

- local path: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy`;
- branch: `design/df8-14in-short-forward-powertrain-external-buoy`;
- HEAD: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`;
- classification: **CURRENT DEVELOPMENTAL**.

Current exact geometry/mass reported by that source:

- source full-length arm: 733.806 mm;
- current arm: **378.206 mm pivot-to-tip**;
- exact arm/body reduction: 355.600 mm;
- source pivot station: 480.000 mm;
- current true-forward pivot station: **355.000 mm**;
- pivot movement: 125.000 mm forward;
- rigid body length: **1675.400 mm**;
- maximum rigid span: **56.500 mm** ≤57.150-mm hard rigid limit;
- STOWED mass: **10.583165211 kg**;
- reserve to 18.14 kg: **7.556834789 kg**;
- modeled occurrences: **180 per endpoint**.

Important configuration rule:

- 480.000 mm remains fixed for the pressure-packaging studies explicitly commissioned under the fixed-480 architecture;
- the 889-mm fallback is not the fixed-480 final;
- the later SHORT14/true-forward-powertrain commission is a newer configuration and explicitly moved the pivot to 355.000 mm.

Do not combine these stations without configuration qualification.

---

## 8. Current CAD validation state

For the exact SHORT14 current source branch/commit, the recovered validation reports:

- placement PASS; 8.000-mm ballast/carrier transition; prohibited interval count 0;
- changed-part quality PASS; 70 changed occurrences per endpoint; zero reported invalid/open/nonmanifold/sliver/tiny-edge/broken-fillet/blocked-Boolean defects;
- endpoint assembly PASS; 180 named occurrences and 180 exact solids per state; zero reported unauthorized rigid intersections or floating/disconnected parts;
- external-pack function: CAD PASS with physical tests open;
- five-angle exact Boolean audit: 43,035 pairs, zero unauthorized/blocked/track/fit errors;
- full 0–80° motion audit: 697,167 pairs, zero unauthorized/blocked/track/fit errors;
- dimensions/mass: PASS against current CAD inputs;
- AP242: clean OCP/XCAF reimport, millimetres, named non-flattened hierarchy, exact BREP, zero `FACETED_BREP`.

These are **developmental CAD validation results for the exact source**, not physical qualification.

---

## 9. Current open gates

Do not close these from CAD alone:

1. owner Creo visual/mechanical inspection of the current Package 05 AP242 pair;
2. physical fabric engagement/retention/extraction and snag testing;
3. wet deployment/inflation/breakaway testing;
4. fall/orientation equivalence and recovery behavior;
5. structural/proof/shock/environmental/saltwater tests as applicable;
6. finished external-buoy article dimensions, mass/CG, leak/relief/drain/dry/repack evidence;
7. exact vendor-supported Hydro 1F/V95000 suffix and cartridge/manifold/holder/bladder interfaces;
8. complete commercial-module application/rating evidence if a COTS module is selected;
9. procurement quotes, exact order suffixes, CoC/certs, lot/expiry and receiving inspection;
10. remote backup/disposition of the 12 local-only CAD branches and dirty `EVIDENCE HOLD` work.

---

## 10. Current exact owner-inspection artifacts remotely preserved

GitHub path:

`cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/`

Files:

- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_CREO_INSPECTION.zip`;
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_STOWED_AP242.step`;
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_DEPLOYED_AP242.step`;
- `README.md`;
- `SHA256SUMS.txt`.

Local source-derived hashes are recorded in `GITHUB_BRANCH_AND_ARTIFACT_MANIFEST.md` and `../../context/stingray/CAD_PROVENANCE.md`.

---

## 11. Workflow/context preservation rules for future agents

1. Start from `engineering/stingray-context/00_READ_ME_FIRST.md` and the linked `context/stingray/*` control files.
2. Resolve the exact configuration before reusing a number, component, validation result or CAD statement.
3. Never infer artifact contents; inspect exact source/provenance first.
4. Preserve historical branches/packages and dirty operator evidence; do not silently clean or overwrite them.
5. Prefer bounded monothreads with explicit correction limits rather than indefinite loops.
6. Treat current Package 05 as developmental inspection CAD, not release CAD.
7. When discussing COTS, distinguish selected exact part, proxy, candidate, rejected family and evidence hold.
8. Do not force external softgoods into the 57.15-mm rigid-body limit unless the applicable requirement explicitly says so.
9. Do not call a research product (including SECUMAR) implemented merely because it resembles the mission architecture.
10. Keep security data out of engineering-context commits.

---

## 12. Context recovery state

The local consolidation recovered:

- 79 relevant Codex rollout records / 61 unique session IDs;
- four Git repository/clone roots;
- 19 worktrees/checkouts;
- 12 local-only branches in the shared CAD repository;
- 110 high-value local artifacts indexed by exact path/status/size/SHA-256;
- 74 COTS exact configurations/product families;
- no native Creo `.prt`/`.asm` source in the bounded recovered engineering roots.

The cross-device ChatGPT session chronology is preserved in `SESSION_LEDGER.md`. File Library artifacts are inventoried in `FILE_LIBRARY_MANIFEST.md`.

Raw cloud transcript byte completeness and all local-only Git/binary bytes remain explicitly unresolved retrieval gaps; see `SOURCE_COVERAGE_AND_GAPS.md`.