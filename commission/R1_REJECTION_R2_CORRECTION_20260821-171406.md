# STINGRAY I5-S DF8 — R1 REJECTION TO R2 MECHANICAL-COHESION CORRECTION COMMISSION

## 0. ABSOLUTE EXECUTION DIRECTIVE

You are executing the full corrective CAD rebuild of the rejected:

`STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD(1).zip`

Rejected archive SHA-256:

`19feb0336f89aa6bc8a4c7a083ea47db64311cde4fa68fd55298f885517e96c2`

The supplied ZIP and Images 1–9 are corrective inputs—not an accepted or released design.

This is not a request for:

- another critique;
- another concept study;
- an analysis-only response;
- cosmetic cleanup;
- a new validation spreadsheet attached to unchanged geometry;
- a simplified representative model;
- a faceted pseudo-CAD model;
- decorative renders;
- explanations of what should be fixed later.

You shall physically correct and rebuild the CAD, assemble it coherently, verify it, export it, reimport it, correct every remaining defect, and deliver the successor package.

Execute this loop until every applicable gate passes:

> **ingest → reconcile → rebuild → constrain → route → assemble → audit → correct → re-audit → export → clean-session reimport → re-audit → package**

Do not stop after detecting problems. Continue through actual geometry correction.

The previous workbook’s PASS results have no authority. No previous PASS status survives this commission.

---

## 1. CONFIGURATION AUTHORITY

Apply requirements in this order:

1. This corrective commission.
2. The latest owner-approved requirements and decisions supplied with the project.
3. Accepted subsystem source packages.
4. Verified manufacturer data and standards.
5. Useful geometry from the rejected R1 package.
6. The rejected R1 workbook only as a traceability aid—not as proof of correctness.

Where the rejected model conflicts with this commission, this commission controls.

Local redesign is authorized for:

- bosses;
- brackets;
- carriers;
- pivots;
- bushings;
- clevises;
- apertures;
- bulkhead penetrations;
- guides;
- seats;
- collars;
- clamps;
- retaining features;
- stops;
- locks;
- fasteners;
- fittings;
- cable and hose routing;
- arm-root geometry;
- subsystem placement;
- interface hardware.

Do not change the approved mission, basic functional architecture, external hard limits, or deployment requirements merely to make the geometry fit.

Use sound engineering defaults for minor interface details. Ask the owner only if a genuine design-authority decision would change system function or a hard requirement. Consolidate all such questions into one blocking batch.

---

## 2. HARD REQUIREMENTS THAT SHALL NOT BE WEAKENED

The successor shall preserve and verify:

- maximum stowed arm-module diameter: **57.150 mm / 2.250 in**;
- target normal-body diameter: **53.0 mm where practicable**;
- three arms clocked at **0° / 120° / 240°**;
- deployed arm angle: **80°**;
- arm pivot-to-tip length: **733.806 mm**;
- total rigid length: **no greater than 2032 mm / 80 in**;
- ready-to-throw system mass: **no greater than 18.14 kg / 40 lb**;
- crosshead travel: **at least 15.050 mm**;
- one physically continuous structural recovery load path;
- required moving parts remain captive throughout travel;
- inflation and control lines do not carry the structural recovery load;
- the structural load path does not depend on bladder film, unsupported command lines, inflator mechanisms, pack-retention fabric, or cosmetic surface contact;
- no scaling during import, repair, export, or reimport.

A measured travel of `15.049877 mm` does not satisfy a requirement of `≥15.050 mm`. Do not round a failure into compliance.

---

## 3. CONFIRMED OWNER NONCONFORMANCES

Treat the supplied screenshots as confirmed defect evidence. They are not an exhaustive defect list.

Create a controlled nonconformance register and close each item through actual CAD correction.

### NCR-01 — Uncontrolled assembly context

Image 1 shows crane hooks, generic shackles, load-cell hardware, straps, swivel-hoist rings, ORION components, duplicated-looking assemblies, and generic or ambiguous occurrence names that are not reconciled to the delivered STEP masters and BOM.

For every such occurrence:

- classify it as required STINGRAY product hardware or external interface/test context;
- include required hardware in the controlled assembly and BOM;
- place external context in a separately named context assembly;
- establish the precise product-interface boundary;
- prove the STINGRAY structural load path reaches that boundary;
- eliminate unexplained duplicates and generic identities.

Silent omission is prohibited.

### NCR-02 — Incomplete deployed-system cohesion

Images 2 and 3 show deployed buoy, harness, tether, terminal, and body elements without a complete, credible physical connection.

Correct this by modeling the complete chain:

> buoy structural harness → harness terminal → recovery tether → swivel/shackle/terminal hardware as applicable → body hardpoint → primary structure

Every flexible member must connect to modeled termination hardware at both ends.

No deployed item may merely hover near its intended connection.

### NCR-03 — Unsupported routing and improperly placed small hardware

Image 4 shows long routed members, questionable wall transitions, incomplete support, and small hardware that appears unseated or unsupported.

Correct all:

- route origins and destinations;
- clamps and clamp fasteners;
- wall penetrations;
- fairleads;
- bushings;
- glands;
- strain relief;
- anti-chafe protection;
- bend radii;
- service slack;
- tool access;
- fastener engagement.

### NCR-04 — Wall, boss, and spring-envelope interference

Images 5, 7, and 8 show black and teal members entering the white boss and occupying the orange spring/internal-component envelope.

Redesign the physical interface so that:

- each member follows a deliberate bore, slot, guide, bearing, or bulkhead passage;
- the wall contains a real manufactured opening;
- remaining wall thickness is credible;
- the required bushing, gland, reinforcement, edge treatment, seal, or fitting is modeled;
- the members remain clear of the spring and every other moving component throughout travel;
- no part occupies another solid’s volume.

### NCR-05 — Floating or unretained mechanism components

Image 6 shows components that appear unsupported, unpinned, unguided, or unretained.

For every affected occurrence, provide:

- a real pivot, guide, rail, seat, pocket, axle, fastener, retainer, or captive condition;
- axial retention;
- radial/lateral retention;
- anti-rotation where required;
- intended degrees of freedom;
- stop and lock behavior;
- service/removal method.

Touching another component is not retention.

### NCR-06 — Open-ended line and unattached hardware

Image 9 shows an apparently open-ended cyan route, missing termination hardware, inadequate support, and an apparently unattached small component.

Every hose, cable, tube, rod, and tether shall:

- terminate at identified hardware at both ends;
- include actual fittings and engagement;
- include clamps and strain relief;
- pass through walls only through controlled penetrations;
- maintain required bend radius and movement slack;
- remain supported and collision-free in both states and throughout motion.

An open end is permitted only when explicitly designed as a vent, drain, test port, or functional free end.

### NCR-07 — Faceted arm geometry

The rejected arms contain approximately 1,004 faces each, predominantly planar patches, despite representing a curved arm.

Rebuild the arms using clean analytic or curvature-continuous B-rep geometry.

Prohibited:

- planar patch tiling used to imitate curvature;
- mesh-derived surfaces;
- tessellated or faceted proxies;
- cosmetic shading used to disguise underlying facets;
- hundreds of unnecessary planar faces;
- uncontrolled sliver faces;
- angular breaks not required by design.

The underlying exact geometry—not merely its shaded appearance—must be smooth and manufacturable.

### NCR-08 — Globally baked component geometry

The rejected STEP hierarchy uses identity occurrence transforms for nearly every component, with locations largely baked into each part’s global geometry.

Rebuild this as a genuine assembly:

- every unique part uses a stable part-local coordinate system;
- occurrences are positioned through meaningful assembly transforms;
- the editable source contains actual assembly constraints or joints;
- repeated parts reuse one controlled part definition;
- stowed and deployed states use the same controlled occurrence identities;
- moving parts change placement through the mechanism definition rather than being rebuilt at unrelated global coordinates.

---

## 4. TRUE ASSEMBLY-CONSTRUCTION REQUIREMENTS

The successor shall be a mechanically meaningful assembly, not a populated product tree containing unrelated solids.

For every occurrence provide:

- stable occurrence ID;
- unique part number and revision;
- parent assembly;
- local datum coordinate system;
- occurrence transform;
- attachment or joint type;
- permitted degrees of freedom;
- fixed, moving, flexible, captive-released, consumed, or external-context classification;
- constraint/regeneration status;
- state membership.

Identity transforms are permitted only when intentionally justified occurrence-by-occurrence.

No required component may remain:

- underconstrained without documented functional motion;
- placed only by arbitrary coordinates;
- floating;
- missing a reference;
- suppressed by error;
- hidden in the default saved representation;
- duplicated without a separate occurrence identity;
- fused into an unrelated component to conceal an interface.

Build one authoritative mechanism that generates both controlled states.

The stowed and deployed masters shall not be unrelated assemblies that merely resemble two poses.

---

## 5. COMPLETE HARDWARE AND INTERFACE DETAIL

Model every physical item required to assemble and operate the system, including as applicable:

- screws;
- nuts;
- threaded inserts;
- washers;
- rivets;
- pins;
- taper pins;
- clevis pins;
- cotters;
- retaining rings;
- clips;
- collars;
- spacers;
- bushings;
- bearings;
- seals;
- O-rings;
- gaskets;
- glands;
- fittings;
- clamps;
- clamp fasteners;
- cable barrels;
- swages;
- strap terminations;
- stitched interfaces;
- shackles;
- swivels;
- hooks;
- hard stops;
- lock dogs;
- springs;
- spring seats;
- guides;
- anti-rotation features;
- strain relief;
- edge protection.

Every fastener must engage a modeled mating feature and include its actual locking/retention method.

Every pivot must include:

- coaxial mating holes;
- pin or shaft;
- bearing or bushing where required;
- axial retention;
- side clearance;
- stop and lock relationship;
- assembly access.

Pressure-carrying connections shall include correct:

- thread form;
- size and pitch;
- engagement length;
- shoulder or seat;
- sealing feature;
- installation depth;
- anti-rotation/support provision.

Do not represent a pressure connection as overlapping cylinders.

---

## 6. PROHIBITED CORRECTIVE SHORTCUTS

You shall not satisfy any requirement by:

- hiding or suppressing a defective occurrence;
- moving it outside the assembled state;
- deleting required hardware;
- excluding an inconvenient pair from the audit;
- changing to an exploded configuration;
- making the offending geometry transparent;
- relabeling it as reference-only;
- fusing unrelated parts;
- grounding or gluing moving parts;
- subtracting one interfering part from another without designing a legitimate manufactured opening;
- creating an oversized clearance pocket solely to force PASS;
- replacing detailed geometry with a block, envelope, surface, mesh, or decorative line;
- changing units, accuracy, tolerances, datum frames, or scale;
- accepting a collision because the rejected workbook called it valid;
- labeling an undocumented overlap “intentional interference”;
- typing or copying a PASS result.

A wall crossing is acceptable only through a deliberately designed physical passage with its required interface hardware.

A part touching another surface is not considered attached.

A colored line is not an acceptable hose, cable, or tether definition.

---

## 7. ATTACHMENT, RETENTION, AND LOAD-PATH GATE

Create an occurrence-specific mechanical-connectivity graph.

For every physical occurrence identify:

- exact parent occurrence;
- mating feature IDs;
- connection type;
- permitted degrees of freedom;
- retaining hardware;
- axial retention;
- radial/lateral retention;
- anti-rotation provision;
- upstream load path;
- downstream load path;
- service/removal method;
- supporting measurement or evidence.

Generic entries such as:

- `Attached to WP04`;
- `Attached to WP05`;
- `Source-controlled interface`;
- `Translated without scaling`;
- `Located by parent assembly`

are prohibited as verification.

Release requires:

- zero unexplained isolated rigid occurrences;
- every fixed item fully retained;
- every moving item captive while retaining only its intended motion;
- every flexible item connected at both ends;
- a continuous root-connected structural load path;
- no structural load carried through prohibited nonstructural components.

---

## 8. EXACT INTERFERENCE AUDIT

Perform an exhaustive exact-kernel positive-volume intersection audit using the exported and independently reimported geometry.

Audit:

- every rigid-solid occurrence pair in STOWED;
- every rigid-solid occurrence pair in DEPLOYED;
- every relevant rigid/softgood pair;
- all pins, fasteners, springs, retainers, fittings, clamps, and small hardware;
- every mechanism position through the complete motion path;
- swept envelopes for cables, hoses, straps, springs, and tethers.

Do not exclude pairs merely because they:

- share a subassembly;
- appear adjacent;
- are small;
- are flexible;
- use the same material;
- were previously declared acceptable.

For every detected intersection record:

- configuration;
- mechanism position;
- both complete occurrence paths;
- both part numbers;
- common volume in mm³;
- penetration depth where available;
- location/centroid;
- classification;
- source authority for any intended fit;
- corrective action;
- recheck result;
- evidence reference.

Permitted intentional interference is limited to genuine engineered interfaces such as:

- thread engagement;
- controlled press fits;
- swages;
- O-ring compression;
- bonded overlap;
- specifically defined seal compression.

Every allowed exception requires a separate controlled register entry defining its intended interference range and source requirement.

Release criterion:

> **Zero undocumented positive-volume intersections beyond the declared numerical tolerance.**

---

## 9. MOTION-SWEEP AND CLEARANCE GATE

Validate the entire mechanism path, not only the endpoints.

The sweep must include:

- release;
- initial movement;
- maximum-obliquity conditions;
- full crosshead travel;
- complete arm travel;
- actuator and damper travel;
- spring compression/extension;
- stop engagement;
- lock engagement;
- cable, hose, strap, and tether movement;
- deployed buoy/tether condition;
- reverse reset/service movement.

Use continuous collision detection when available.

Otherwise use increments no larger than:

- **1° rotational**, or
- **1 mm translational**,

with refinement to **0.1° or 0.1 mm** around minimum-clearance and event regions.

Create a minimum-clearance register containing:

- complete occurrence paths;
- feature IDs;
- mechanism position;
- nominal minimum clearance;
- required minimum clearance;
- tolerance basis;
- coating/corrosion/contamination allowance where applicable;
- worst-case clearance;
- calculated margin;
- automatically derived status;
- evidence reference.

Zero-gap coincidence is acceptable only for an identified intended-contact interface.

Blank requirements, assumed clearance, or `TBD` are failures.

Release requires:

- zero motion-path collisions;
- zero wall penetrations;
- zero unresolved clearance violations;
- positive worst-case clearance for every required noncontact pair.

---

## 10. CONFIGURATION-PARITY GATE

Create a state-delta register matching every occurrence between STOWED and DEPLOYED by stable occurrence ID.

No required part may disappear merely to make the deployed state fit.

A released cover, door, pin, restraint, or closure shall remain modeled in its physically correct:

- captive;
- tethered;
- released;
- consumed;
- displaced;
- service-removed

condition.

Flexible articles may use different state geometry, but their part number, function, attachment points, and occurrence identity must remain traceable.

Every state-count or body-topology difference must be explicitly explained.

---

## 11. PROCUREMENT AND SOURCE-CAD RECONCILIATION

Reconcile CAD, BOM, and procurement identity one-to-one.

Every purchased identity shall include:

- exact manufacturer;
- exact manufacturer part number;
- exact ordered configuration;
- quantity;
- material;
- mass;
- direct manufacturer URL;
- direct purchase/RFQ URL where available;
- source drawing;
- vendor CAD source;
- CAD authenticity classification;
- procurement/release status.

Use only these classifications:

- `AUTHENTIC_VENDOR_CAD`;
- `DRAWING_DERIVED`;
- `PROVISIONAL — BLOCKS FINAL RELEASE`.

Do not call drawing-derived or generic geometry authentic vendor CAD.

Do not scale or silently modify vendor geometry.

Resolve all critical:

- `TBD` hardware;
- unidentified hoses;
- unidentified fittings;
- provisional springs;
- generic fasteners;
- inconsistent MAKE/BUY identities;
- duplicate part numbers with different descriptions, masses, or geometry.

Where authentic vendor CAD is unavailable, create an exact controlled drawing-derived installation model and cite the authoritative dimensional source. Do not invent missing dimensions or falsely claim vendor provenance.

Every BUY item must have a valid identity and sourcing link before procurement completeness may pass.

---

## 12. EVIDENCE-BASED VALIDATION ONLY

No PASS result may be manually typed, copied forward, or prepopulated.

Every validation gate shall include:

- frozen requirement ID;
- exact acceptance criterion;
- comparison operator;
- units;
- measured value at full precision;
- calculated margin;
- model state;
- occurrence IDs;
- tool and version;
- run timestamp;
- source-file SHA-256;
- raw evidence path;
- automatically calculated `PASS`, `FAIL`, or `BLOCKED/NOT TESTED`.

Missing evidence means `BLOCKED/NOT TESTED`, never PASS.

Do not round before comparison.

Do not weaken or reinterpret a requirement after measurement.

The absence of detected errors is not proof unless the required search was exhaustive and its raw results are included.

---

## 13. INDEPENDENT EXPORT AND REIMPORT VALIDATION

Validation shall be performed on newly reimported AP242 files—not solely on the authoring model or in-memory geometry.

Required sequence:

1. Fully regenerate or rebuild the editable source.
2. Run source geometry and assembly checks.
3. Export the STOWED AP242 master.
4. Export the DEPLOYED AP242 master.
5. Close and clear the authoring session.
6. Start a clean validation process/session.
7. Reimport each exported master from disk.
8. Recount products, occurrences, solids, shells, and state inventory.
9. Verify assembly hierarchy and occurrence transforms.
10. Rerun interference, clearance, mass, envelope, volume, centroid, and bounding-box checks.
11. Compare source geometry against reimported geometry.
12. Correct any translation, placement, healing, topology, or naming defect.
13. Repeat until clean.

Open CASCADE/XCAF validation is permitted as an intermediate gate but may not be represented as Creo validation.

---

## 14. TARGET-CAD CREO GATE

Open each final AP242 master in a clean Creo Parametric session independent of the authoring session.

Perform:

- import;
- full regeneration;
- geometry checks;
- unresolved-reference review;
- model-tree review;
- occurrence-count comparison;
- solid-count comparison;
- transform/placement review;
- mass/volume/center-of-gravity comparison;
- global interference review;
- critical minimum-clearance review;
- section inspection of every corrected NCR location.

Deliver:

- Creo version/build;
- import settings;
- model accuracy;
- import/regeneration log;
- Creo trail/session evidence where available;
- screenshots of the complete assembly tree;
- screenshots of both complete states;
- section views of every corrected critical interface;
- source-versus-Creo comparison results;
- Creo-generated interference evidence.

Do not stop the geometry-repair work merely because Creo is unavailable. Complete all real B-rep corrective work and independent validation first.

However, if an actual Creo session cannot be executed, the package shall be labeled:

`CREO_VALIDATION_PENDING — WIP — NOT RELEASED`

and the response shall state:

> **BLOCKED — REQUIRED CREO REIMPORT/REGENERATION GATE NOT COMPLETED**

Do not use `FINAL`, `RELEASED`, `MECHANICALLY COMPLETE`, or `CREO VERIFIED` until the Creo gate actually passes.

---

## 15. REQUIRED EDITABLE SOURCE

Deliver the source needed to continue correcting and regenerating the assembly.

Acceptable source is:

- native Creo `.ASM`/`.PRT` files if Creo is the authoring system; or
- a complete editable scripted B-rep source project if a real solid-modeling kernel is used.

The source shall include:

- every part and subassembly;
- no missing external dependencies;
- deterministic build instructions;
- dependency/version record;
- state-generation logic;
- assembly-placement definitions;
- validation scripts;
- no hidden proprietary source required to regenerate the model.

A STEP-only package without editable/regenerable source is not acceptable for this corrective revision.

---

## 16. REQUIRED DELIVERY PACKAGE

If every gate—including Creo—passes, deliver:

`STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD_R2.zip`

If Creo remains pending, deliver:

`STINGRAY_I5S_DF8_AP242_COHESION_CORRECTION_R2_CANDIDATE_WIP.zip`

The ZIP shall contain at minimum:

### `/01_EDITABLE_SOURCE/`

- complete native or scripted B-rep source;
- all dependent part/subassembly files;
- build/regeneration instructions;
- dependency manifest.

### `/02_FINAL_AP242/`

- corrected STOWED AP242 master;
- corrected DEPLOYED AP242 master.

### `/03_COMPONENT_AND_VENDOR_CAD/`

- controlled individual component files;
- unmodified authentic vendor CAD where redistributable;
- drawing-derived installation models where authentic CAD is unavailable;
- provenance and source references.

### `/04_MASTER_BUILD_REGISTER/`

One consolidated workbook containing at least:

1. occurrence BOM;
2. unique-part master;
3. purchased-items register;
4. custom-parts register;
5. attachment/retention matrix;
6. configuration matrix;
7. consumables;
8. occurrence-transform register;
9. interference register;
10. intentional-fit exception register;
11. minimum-clearance register;
12. mechanism-sweep register;
13. state-delta register;
14. routing/termination register;
15. owner NCR closure register;
16. final validation.

All validation status cells shall be calculated from measured data.

### `/05_VALIDATION_EVIDENCE/`

- raw interference results;
- raw clearance results;
- motion-sweep results;
- connectivity/load-path results;
- source-versus-reimport comparison;
- Creo evidence if executed;
- before/after views for Images 1–9;
- section views of every corrected critical interface.

### `/06_MANIFEST/`

- configuration manifest;
- software/tool versions;
- source-file provenance;
- SHA-256 hashes for every controlled deliverable;
- exact release status.

Do not include decorative renders or unrelated analysis reports.

---

## 17. BINARY RELEASE CONDITIONS

The package passes only if all of the following are true:

- 100% occurrence reconciliation;
- zero required hidden or suppressed components;
- zero missing references;
- zero unexplained underconstrained rigid parts;
- zero floating or unretained rigid occurrences;
- zero open-ended unintended routes;
- zero undocumented positive-volume intersections;
- zero wall penetrations;
- zero motion-path collisions;
- zero unresolved minimum-clearance violations;
- every wall crossing has a modeled passage and complete hardware;
- every fastener has a mating feature and locking/retention method;
- every cable, hose, tether, strap, and line is terminated at both ends;
- the structural recovery load path is continuous;
- the same authoritative mechanism produces both states;
- all state differences are explained;
- all required small hardware is modeled and present;
- intended smooth surfaces are truly smooth B-rep geometry;
- the arm module remains within Ø57.150 mm;
- total rigid length remains within 2032 mm;
- ready-to-throw mass remains within 18.14 kg;
- crosshead travel is at least 15.050 mm;
- CAD and BOM map one-to-one;
- critical purchased identities are resolved;
- validation statuses are computed rather than asserted;
- the exported masters pass clean-session reimport;
- the final label accurately reflects whether the Creo gate passed.

---

## 18. MANDATORY FAILURE BEHAVIOR

If any gate remains open:

- continue correcting it when technically possible;
- label all outputs `WIP — NOT RELEASED`;
- mark the gate `FAIL` or `BLOCKED/NOT TESTED`;
- identify the exact affected occurrence;
- give the measured result;
- identify the required correction or missing input;
- do not issue a success statement;
- do not use `FINAL`, `EXACT`, `MECHANICALLY COMPLETE`, `FABRICATION-READY`, `PROCUREMENT-READY`, or `TEST-ENTRY-READY`.

If real B-rep CAD authoring and Boolean validation are unavailable, state:

> **BLOCKED — REAL B-REP CAD AUTHORING/VALIDATION CAPABILITY IS NOT AVAILABLE. NO FINAL PACKAGE GENERATED.**

A spreadsheet assertion, screenshot, filename, closed-shell count, or named assembly does not override failed geometry.

---

## 19. REQUIRED FINAL RESPONSE

Do not return a long narrative, another proposal, or instructions telling the owner to rebuild the model.

After completing the work, respond only with:

- exact package status;
- completed ZIP filename;
- download link;
- number of closed NCRs;
- number of remaining failed or blocked gates;
- whether the clean Creo gate actually passed.

Do not claim completion unless the delivered evidence proves it.