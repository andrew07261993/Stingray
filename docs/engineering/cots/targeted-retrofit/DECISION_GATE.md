# DECISION GATE

- [x] Existing `design/df8-targeted-cots-retrofit` branch resumed; no competing branch created.
- [x] Final-cleanup commit `8c594781e27b0597a71957082fb64f152cacfcd9` verified and used read-only.
- [x] Phase-1 accounting preserved: 121 PartDefs, 104 MAKE, 17 COTS-related, 15 independent purchase lines, 10/114 functional COTS.
- [x] Twenty-five detailed candidates bounded and screened against official manufacturer evidence where available.
- [x] Forty-seven unique priority MAKE definitions screened.
- [x] Five pressure-reservoir finalists evaluated without conflating CO2 vapor pressure, vessel working pressure, downstream pressure, ambient pressure, losses, cold discharge, or relief pressure.
- [x] Seven substitutions selected for qualification, conditionally covering 17 MAKE definitions.
- [x] Field reset sequence and service levels documented.
- [x] Three underwater test item types selected at quantity two each, maximum six articles.
- [x] CoC availability, procurement evidence, and received-item CoC kept separate.
- [ ] Owner Creo visual inspection accepts final-cleanup CAD baseline.
- [ ] Certificate-bearing quotations, official CAD, exact fit, procurement, and delivered-item receiving evidence completed.
- [ ] Any selected COTS replacement implemented in CAD.
- [ ] Post-change validation completed.

Projected functional COTS coverage is **27/114 = 23.68%** only if all seven selected substitutions pass fit, procurement, and qualification. The >50% target is not supportable without larger architecture changes or unresolved configured assemblies; do not call the result mostly COTS.

Current decision: **TARGETED COTS PHASE 2/3 DECISION GATE COMPLETE — CAD IMPLEMENTATION HELD FOR OWNER ACCEPTANCE OF CLEAN CAD BASELINE**.

Exact next action: owner accepts or rejects final-cleanup commit `8c594781e27b0597a71957082fb64f152cacfcd9` after Creo visual inspection. If accepted, execute the quotation and six-article test-procurement gate in `PROCUREMENT_ACTION_LIST.md`; do not begin CAD implementation in this task.
