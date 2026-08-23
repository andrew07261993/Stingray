# STINGRAY I5-S DF8 — Ø2.250-IN FINAL EXACT AP242 MECHANICALLY COMPLETE CAD COMMISSION

## 0. EXECUTION DIRECTIVE

You are executing the final mechanically complete **neutral-CAD build** for the STINGRAY I5-S DF8 Ø2.250-inch arm-module redesign and complete ready-to-throw system.

The required result is:

1. one fully assembled stowed AP242 STEP model;
2. one fully assembled deployed AP242 STEP model;
3. one complete build, parts, attachment, and procurement workbook;
4. one ZIP containing those three deliverables.

This is not a request for:

- native Creo `.prt` or `.asm` files;
- access to Creo Parametric;
- Codex;
- J-Link;
- a Creo license;
- rendered images;
- screenshots;
- a new engineering study;
- a new analysis report;
- presentation material;
- a concept model;
- faceted or mesh CAD;
- supporting-document proliferation.

**Creo is not required in the execution environment. Lack of Creo is not a blocker.**

The owner will import the delivered AP242 files into Creo after delivery.

Do not run a Creo preflight.

Do not search for a Creo installation.

Do not return `BLOCKED` merely because Creo is unavailable.

Build the final geometry using the available exact-solid CAD kernel, preferably CadQuery and OCP/OCCT.

Execute:

> **ingest → reconcile → redesign → model every component → assemble → audit → correct → re-audit → export exact AP242 → reimport with OCP → validate → deliver**

Do not stop after generating preliminary geometry.

Do not deliver a fallback package.

---

# 1. REQUIRED INPUTS

Use all applicable attachments supplied in this conversation:

- latest final arm-module independent-analysis ZIP;
- latest accepted WP01 body/envelope ZIP;
- latest accepted WP02 arm/powertrain ZIP;
- latest accepted WP03 water-activation/inflation ZIP;
- latest accepted WP04 spring-ejector/buoy-pack ZIP;
- latest accepted WP05 aft-closure/service/reset ZIP;
- latest accepted WP06 integration ZIP;
- CRDS01 Ø2.250-inch arm-base redesign ZIP;
- prior R1 stakeholder-review CAD ZIP;
- the Creo screenshots showing the R1 deficiencies;
- authentic vendor CAD and manufacturer drawings supplied with the commission.

Use only one accepted version of each WP.

The previous R1 model is reference and negative-example evidence only.

---

# 2. AUTHORITY HIERARCHY

Resolve conflicts using this order:

1. owner decisions in this prompt;
2. latest final independent-analysis package and its CAD Design Input Register;
3. latest accepted WP01–WP06 packages;
4. authentic manufacturer CAD and drawings;
5. CRDS01 geometry;
6. previous R1 stakeholder-review CAD;
7. older conceptual material.

Do not preserve an R1 feature merely because it already exists.

---

# 3. CLOSED OWNER DECISIONS

These decisions are final and shall not be reopened.

## 3.1 Arm length

All three arms shall be:

**733.806 mm / 28.89 in pivot-to-tip**

Use this length for:

- geometry;
- mass;
- deployed envelope;
- root design;
- inertia;
- stowed retention;
- stops;
- locks.

## 3.2 Backup spring

Use a guided central compression spring with this controlled design envelope:

- maximum OD: **15.8 mm**;
- approximate free length: **195 mm**;
- approximate stowed installed length: **145 mm**;
- deployed installed length: approximately **160.05 mm**;
- approximate rate: **16 N/mm**;
- approximate stowed force: **800 N**;
- minimum target deployed force: approximately **559 N**;
- available work target: approximately **10.2 J**;
- maximum solid height: **138 mm**;
- spring plus seat mass target: **≤0.13 kg**.

Do not force either conflicting Lee Spring part into the final model.

If no verified exact COTS part satisfies this envelope, assign a controlled custom STINGRAY part number and identify it honestly as custom.

## 3.3 HBD-15 policy

Retain:

**ACE Controls HBD-15-25-AA-P**

Use a direct installation.

Do not add:

- a bypass carriage;
- lost-motion anti-seizure mechanism;
- overload release;
- fuse pin;
- redundant damper.

Mechanical HBD seizure is an owner-accepted single-point deployment failure.

Reduced or absent damping remains a structural impact condition that the stops, locks, pins, carrier, and retainers shall survive.

---

# 4. HARD REQUIREMENTS

## 4.1 Diameter

Preferred nominal stowed arm-module OD:

**approximately 53.0 mm**

Absolute worst-case stowed OD:

**≤57.15 mm / 2.250 in**

This includes:

- arms;
- fixed sectors;
- fasteners;
- retainer heads;
- seam covers;
- shingles;
- coatings;
- tolerance growth;
- assembly eccentricity.

No hardware shall protrude beyond the hard keep-in cylinder.

## 4.2 Weight

Complete ready-to-throw system:

**≤18.14 kg / 40.0 lb**

Maintain at least:

**1.0 kg unallocated mass reserve**

after the complete detailed occurrence-level mass roll-up.

## 4.3 Length

Complete ready-to-throw rigid-body length:

**≤2032 mm / 80.0 in**

## 4.4 Arm arrangement

- three arms;
- 0°/120°/240° nominal clocking;
- approximately 80° deployed angle;
- common crosshead deployment;
- positive stowed retention;
- structural hard stops;
- automatic positive deployed locks;
- passive backup deployment.

---

# 5. EXACT-CAD METHOD — MANDATORY

Use exact boundary-representation solid modeling with:

- CadQuery;
- OCP/OCCT;
- XCAF/OCAF;
- `STEPCAFControl_Writer` or an equivalent exact assembly-capable STEP writer.

Use millimetres internally.

Use:

**1 in = 25.4 mm exactly**

The STEP files shall use actual AP242 schema and exact solid representations.

Preferred representation entities include:

- `ADVANCED_BREP_SHAPE_REPRESENTATION`;
- `MANIFOLD_SOLID_BREP`;
- analytic planes;
- analytic cylinders;
- analytic cones;
- analytic tori;
- exact NURBS surfaces;
- proper product definitions and assembly occurrences.

## 5.1 Explicitly forbidden geometry methods

Do not use:

- `trimesh` to generate final geometry;
- `extrude_polygon` through a mesh triangulator;
- `mapbox_earcut`;
- STL;
- OBJ;
- triangle meshes;
- mesh-to-STEP conversion;
- `FACETED_BREP`;
- tessellated pseudo-CAD;
- polygonal placeholder cylinders;
- flat graphics;
- zero-thickness surfaces as rigid parts.

Do not fall back to a faceted file if an exact boolean or loft fails.

Correct the exact-solid construction.

## 5.2 True assembly hierarchy

Each AP242 shall be a true named assembly, not one flattened compound.

Include:

- separate product definition for every unique part;
- separate occurrence for every installed repeated part;
- named subassemblies;
- occurrence transforms;
- stable part names;
- stable part numbers;
- material or color metadata when supported;
- no merging of unrelated parts;
- no arbitrary scaling of vendor geometry.

Use XCAF/OCAF product structure.

After export, reimport with an XCAF/OCP reader and verify:

- assembly names;
- product count;
- occurrence count;
- transforms;
- units;
- bounding dimensions;
- solid validity;
- missing-part count;
- duplicate-part count.

---

# 6. DEFINITION OF MECHANICALLY COMPLETE

High detail means mechanical completeness, not a high solid count.

Every non-integral component shall visibly answer:

1. what it is;
2. what it attaches to;
3. how it attaches;
4. what retains it;
5. what controls its axial location;
6. what controls its radial location;
7. how it moves, if movable;
8. how it is prevented from moving, if fixed;
9. how it is installed;
10. how it is removed or serviced.

Touching or overlapping solids are not attachments.

No floating components are permitted.

---

# 7. MODEL EVERY HARDWARE ITEM

Model every installed:

- screw;
- bolt;
- shoulder screw;
- stud;
- nut;
- locknut;
- washer;
- thrust washer;
- shim;
- spacer;
- rivet;
- pivot pin;
- clevis pin;
- dowel;
- spring pin;
- lock pin;
- retaining ring;
- circlip;
- keeper;
- bushing;
- bearing;
- sleeve;
- collar;
- gland;
- ferrule;
- fitting;
- clamp;
- bracket;
- spring;
- seal;
- gasket;
- O-ring;
- tether termination;
- closure component.

Hardware cannot exist only as a hole or BOM entry.

Repeated hardware may use patterned occurrences but every occurrence shall appear in the assembly product tree and occurrence BOM.

## 7.1 Fastener detail

Every fastener shall include relevant exterior geometry:

- head;
- head height and diameter;
- drive recess;
- shank;
- shoulder where applicable;
- threaded engagement region;
- nut or threaded receiving component;
- washer where required;
- locking or retaining feature.

Detailed helical threads are not required everywhere, but threaded hardware shall not appear as a featureless rod.

## 7.2 Pins

Every pin shall have:

- head or shoulder;
- correct grip;
- supported joint;
- washer or spacer where needed;
- actual captive retention.

No exposed E-clips or loose cotter pins in the fabric-contacting region.

## 7.3 Rivets

Where a riveted joint is selected or already controlled:

- model the rivet body;
- head;
- formed tail or controlled installed end;
- every occurrence.

Do not add arbitrary rivets merely to increase detail.

---

# 8. CORRECT THE R1 DEFICIENCIES

The following prior-model conditions shall not remain:

- open-ended generic cylinders;
- cylinders lacking heads;
- actuators lacking glands;
- rods without eyes or clevises;
- missing actuator mounting pins;
- missing pin retainers;
- missing bushings;
- missing washers and spacers;
- brackets with no fasteners;
- parts attached only by overlap;
- thin decorative plates pretending to be structure;
- unclear hard stops;
- unclear deployed locks;
- generic springs;
- incomplete crosshead joints;
- incomplete carrier machining;
- unexplained tube ends;
- meaningless component names;
- unnamed solids;
- components without part numbers.

---

# 9. COTS COMPONENT DETAIL

## 9.1 GS-19

Retain:

**ACE Controls GS-19-50-V4A-B8-B8**

Use authentic supplied vendor CAD without scaling where available.

Otherwise create source-backed exterior geometry from the verified manufacturer drawing.

Include:

- body;
- closed body head;
- body-end fitting;
- rod gland;
- rod;
- rod-end fitting;
- B8/B8 attachment geometry;
- eyes or clevises;
- mounting pins;
- bushings;
- washers/spacers;
- retainers;
- fixed bracket;
- moving bracket;
- service clearance.

Attach both ends physically.

## 9.2 HBD-15

Retain:

**ACE Controls HBD-15-25-AA-P**

Include:

- complete body exterior;
- closed end;
- head/gland;
- rod;
- both end fittings;
- mounting pins;
- bushings;
- spacers;
- retainers;
- direct mounting brackets;
- service clearance.

Do not add a seizure bypass.

## 9.3 Other purchased hardware

Use exact verified manufacturer part numbers for:

- cartridges/cylinders;
- valves;
- seals;
- O-rings;
- bearings;
- bushings;
- fasteners;
- fittings;
- recovery hardware;
- tether components.

Do not assign a part number belonging to a merely similar product.

---

# 10. ARM ROOT, PIVOT, STOP, AND LOCK DETAIL

## 10.1 Arm/root

Use the final independent-analysis package.

The prior narrow conceptual root is not final authority.

Provide a widened reinforced structural root/yoke.

Minimum preliminary net section modulus after all bores, windows, fastener holes, stop reliefs, and lock features:

- approximately **610 mm³ for Ti-6Al-4V**; or
- approximately **530 mm³ for 17-4 PH H1150**.

Use appropriate transition fillets and bearing ligament.

## 10.2 Pivot

Preferred preliminary arrangement:

- 8 mm pivot pin;
- double-shear support;
- replaceable bushing;
- thrust control;
- captive pin retention;
- service access;
- no exterior snag projection.

## 10.3 Hard stops

Each arm shall have real carrier-backed hard-stop contact geometry.

Use:

- paired arm-heel stop faces;
- replaceable hardened stop inserts;
- physically retained inserts;
- direct carrier load path.

Use the controlling analysis basis, including approximately:

- 10.2 kN static reaction per arm;
- 20.4 kN provisional no-damping impact screen per arm.

Do not use GS-19, HBD-15, spring solid height, or linkage binding as a hard stop.

## 10.4 Positive locks

Each arm shall have a visibly complete automatic mechanical lock.

Include:

- lock dog/pawl/hook;
- engagement face;
- pivot;
- pin;
- retainer;
- bushing where needed;
- actual helical spring;
- spring seats;
- reverse-load face;
- captive reset interface;
- inspection witness.

Use the controlling analysis basis, including approximately 13.6 kN reverse reaction per arm.

---

# 11. STOWED RETENTION

Implement positive distributed retention for all three full-length arms.

Preferred arrangement:

- common annular aft collar; or
- three captive radial dogs at aft arm features;
- root hard seating as secondary location.

Use at least:

**0.8 kN design load per arm in any direction**

until superseded by stronger controlled evidence.

Model all:

- dogs;
- collar;
- cam;
- springs;
- pivots;
- pins;
- retainers;
- brackets;
- release interface;
- transport inhibit interface.

---

# 12. CROSSHEAD AND LINKAGE

Use one axial common crosshead coordinating all three arms.

Include:

- three 120° link stations;
- actual guide lands;
- anti-rotation control where required;
- short links;
- complete link eyes or clevises;
- retained link pins;
- actuator attachment;
- HBD attachment;
- spring seat and reaction interface.

Required mechanism travel is approximately:

**15.05 mm**

Use approximately:

**16.0 mm controlled design travel**

before structural stop closure.

Do not use three unrelated pushrods.

---

# 13. BACKUP SPRING DETAIL

Model the actual helical central compression spring.

Include:

- spring geometry;
- forward seat;
- aft/moving seat;
- axial guide;
- guide clearance;
- preload reaction;
- solid-height clearance;
- retention;
- reset access;
- crosshead attachment;
- no spring contact with softgoods.

Use a controlled custom part number if no verified COTS identity exists.

---

# 14. STRUCTURAL CARRIER DETAIL

The carrier shall be a manufacturable structural component or physically assembled subassembly.

Include as applicable:

- primary carrier body;
- pivot bosses;
- double-shear ears;
- bushing shoulders;
- machined pockets;
- ribs;
- webs;
- stop-insert pockets;
- lock-pivot bosses;
- crosshead guides;
- actuator brackets;
- damper brackets;
- spring-reaction structure;
- threaded holes;
- through holes;
- dowels;
- fastener access;
- drain paths;
- service access;
- realistic fillets.

Every separate carrier piece shall be physically attached by modeled hardware.

---

# 15. COMPLETE SYSTEM INTEGRATION

Integrate the accepted WP01–WP06 hardware into both complete system states.

Include all accepted:

- penetrator;
- nose transition;
- main body;
- arm module;
- water-sensitive trigger;
- release system;
- CO₂ hardware;
- inflation components;
- valves;
- fittings;
- hoses/tubing;
- buoy ejector;
- buoy pack;
- buoy retention;
- aft closure;
- exit throat;
- hinges;
- latches;
- seals;
- drains;
- vents;
- handle;
- line exits;
- recovery tether;
- swivels/shackles/thimbles;
- reset interfaces;
- fairings;
- seam closures;
- all operational hardware.

Do not reduce accepted detailed WP geometry to blocks or simple cylinders.

---

# 16. PART TITLES AND PART NUMBERS

Every unique part shall have:

- unique part number;
- exact descriptive title;
- revision;
- subsystem;
- quantity;
- material;
- finish;
- mass;
- make/buy classification;
- manufacturer when purchased.

Preserve existing controlled numbers where available.

For new custom parts use:

`STG-DF8-[SUBSYSTEM]-[SEQUENCE]`

Examples:

- `STG-DF8-ARM-001 — ARM`
- `STG-DF8-ROOT-001 — STRUCTURAL ARM ROOT`
- `STG-DF8-CAR-001 — ARM MODULE STRUCTURAL CARRIER`
- `STG-DF8-SPR-001 — BACKUP COMPRESSION SPRING`
- `ACE-GS-19-50-V4A-B8-B8 — INDUSTRIAL GAS SPRING`
- `ACE-HBD-15-25-AA-P — HYDRAULIC DAMPER`

Do not use names such as:

- `SOLID001`;
- `BLOCK`;
- `CYLINDER`;
- `PLATE`;
- `GENERIC_FASTENER`;
- `PART_COPY`;
- `MESH`.

---

# 17. INTERNAL VALIDATION

Perform all validation internally.

Do not produce separate reports.

Record only final status in the workbook.

## 17.1 Motion/interference

Evaluate the arm mechanism from:

**0° through 80° at intervals no greater than 1°**

Use exact BREP common-volume testing.

Check every moving component against:

- shell;
- carrier;
- adjacent arms;
- links;
- crosshead;
- GS-19;
- HBD-15;
- spring;
- stops;
- locks;
- fasteners;
- retainers;
- fairings;
- tubing;
- other subsystem hardware.

Correct every invalid rigid interference.

Intentional contacts shall be explicitly limited to:

- bearings;
- guides;
- stop seating;
- lock engagement;
- stowed latch engagement;
- seals;
- controlled spring seats.

## 17.2 Mechanical attachment

Verify every non-integral occurrence has:

- modeled attachment;
- modeled hardware;
- identified mating part;
- attachment-map entry.

Required result:

**100% accounted for**

## 17.3 Assembly/BOM reconciliation

Required results:

- unnamed parts: 0;
- unnumbered parts: 0;
- missing CAD occurrences: 0;
- missing occurrence-BOM rows: 0;
- floating parts: 0;
- unexplained duplicates: 0;
- parts lacking material: 0;
- parts lacking mass: 0.

## 17.4 Envelope

Verify:

- nominal arm-module OD approximately 53 mm;
- worst-case OD ≤57.15 mm;
- rigid-body length ≤2032 mm.

## 17.5 Mass

Verify:

- complete system ≤18.14 kg;
- unallocated reserve ≥1.0 kg;
- no zero-mass placeholders;
- workbook and CAD mass reconcile.

## 17.6 AP242 reimport

After each export, reimport through OCP/XCAF.

Verify:

- AP242 schema declaration;
- exact solid BREP;
- closed valid solids;
- part count;
- occurrence count;
- names;
- transforms;
- units;
- bounding box;
- no missing products;
- no flattened compound;
- no `FACETED_BREP`.

---

# 18. MASTER WORKBOOK

Create:

`STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx`

This is the only supporting document.

It shall account for 100% of the build.

Required worksheets:

## `01_OCCURRENCE_BOM`

One row per installed physical occurrence.

Include:

- occurrence ID;
- parent assembly;
- assembly path;
- subsystem;
- part number;
- title;
- revision;
- quantity;
- stowed status;
- deployed status;
- make/buy;
- manufacturer;
- manufacturer part number;
- material;
- finish;
- unit mass;
- extended mass;
- attachment method;
- mating part;
- retaining hardware.

## `02_UNIQUE_PARTS`

One row per unique part number.

## `03_PURCHASED_ITEMS`

For every purchased item include:

- exact manufacturer;
- exact manufacturer part number;
- exact description;
- quantity;
- clickable manufacturer product hyperlink;
- clickable direct manufacturer or authorized-distributor purchase hyperlink;
- link verification date;
- vendor CAD status.

Do not use generic search-result pages.

Do not invent URLs.

## `04_CUSTOM_PARTS`

Identify every custom fabricated item.

For purchase URL state:

`CUSTOM FABRICATED — NO DIRECT PURCHASE LINK`

A raw-material source may be listed separately.

## `05_ATTACHMENT_MAP`

One row for every non-integral occurrence:

- component;
- mating component;
- attachment type;
- fastener/pin;
- retainer;
- fixed/sliding/rotating;
- captive status;
- service-removal method.

## `06_CONFIGURATION_MATRIX`

State whether every occurrence is:

- stowed;
- deployed;
- repositioned;
- removed;
- retained but displaced;
- service-only.

## `07_CONSUMABLES`

Include exact controlled:

- lubricant;
- sealant;
- adhesive;
- thread locker;
- anti-seize;
- coating;
- passivation;
- markings.

Include clickable exact product/purchase links.

## `08_FINAL_VALIDATION`

Show concise PASS/FAIL values for:

- exact AP242;
- OCP reimport;
- true assembly hierarchy;
- valid solids;
- occurrence reconciliation;
- attachment completeness;
- 1° motion audit;
- invalid interference count;
- stowed OD;
- worst-case OD;
- system length;
- total mass;
- mass reserve;
- unnamed parts;
- unnumbered parts;
- floating parts;
- missing vendor links.

---

# 19. REQUIRED DELIVERABLES

Create exactly one ZIP:

`STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD.zip`

It shall contain only:

1. `STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step`
2. `STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step`
3. `STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx`

Do not include:

- images;
- renderings;
- screenshots;
- analysis reports;
- validation reports;
- source registers;
- scripts;
- logs;
- CSV duplicates;
- JSON files;
- checksum files;
- concept models;
- intermediate models;
- arm-module-only duplicate exports;
- native Creo files.

---

# 20. DEFINITION OF DONE

Do not call the build complete unless:

- both exact AP242 files exist;
- both are exact BREP, not faceted;
- both contain a named assembly product tree;
- all three arms are 733.806 mm pivot-to-tip;
- every component is physically attached;
- every required fastener exists;
- every required rivet exists;
- every pin has retention;
- every joint has bushings/bearings/spacers where required;
- GS-19 has complete exterior end geometry and both attachments;
- HBD-15 has complete exterior end geometry and direct attachments;
- backup spring is actual helical geometry with seats and guide;
- hard stops are real structural contact pairs;
- deployed locks are complete mechanisms;
- stowed retention is complete and distributed;
- carrier detail is manufacturable;
- no generic open-ended cylinders remain;
- no floating solids remain;
- every part has a part number and descriptive title;
- every purchased item has a verified exact product/purchase link;
- every custom item is clearly identified as custom;
- occurrence BOM accounts for 100% of installed items;
- attachment map accounts for 100% of non-integral occurrences;
- 0–80° exact motion audit passes at ≤1° increments;
- invalid rigid interference count is zero;
- worst-case stowed OD is ≤57.15 mm;
- rigid-body length is ≤2032 mm;
- total mass is ≤18.14 kg;
- unallocated mass reserve is ≥1.0 kg;
- OCP/XCAF reimport passes;
- `FACETED_BREP` count is zero.

---

# 21. FINAL RESPONSE

Return only:

1. the download link to `STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD.zip`;
2. one sentence confirming whether every Definition-of-Done gate passed;
3. if a genuine exact-CAD gate failed, name that exact gate.

Do not respond with:

- a proposal;
- a future-work plan;
- a Creo requirement;
- a Codex recommendation;
- renderings;
- another study;
- a fallback package.