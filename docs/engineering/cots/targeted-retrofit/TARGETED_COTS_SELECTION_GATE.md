# Targeted COTS Selection Gate

> Phase-4 continuation note (2026-08-24): this file preserves the Phase-2/3 selection record. The current seven-item dispositions and recalculated practical ceiling are controlled by `SELECTED_COTS_TECHNICAL_CLOSURE.md` and `TARGETED_COTS_CAD_IMPLEMENTATION_GATE.md`. Three selections were rejected after exact duty/environment comparison; the current gated ceiling is 24/114 = 21.05%, not the provisional 27/114 below.

## Gate result

**TARGETED COTS PHASE 2/3 DECISION GATE COMPLETE — CAD IMPLEMENTATION HELD FOR OWNER ACCEPTANCE OF CLEAN CAD BASELINE**

This package uses final-cleanup CAD commit `8c594781e27b0597a71957082fb64f152cacfcd9` as a provisional, read-only research baseline. No CAD geometry, STEP, motion, state-parity, OCP, render, or presentation work was performed.

## Bounded result

- detailed vendor candidates retained: **25 / 25 maximum**;
- pressure-reservoir finalists: **5 / 5 maximum**;
- unique priority MAKE definitions screened: **47 / 104**;
- selected substitutions: **7 / 15 maximum**;
- selected substitutions conditionally cover: **17 MAKE definitions**;
- baseline functional COTS coverage: **10/114 = 8.77%**;
- projected coverage if all seven selections pass fit, procurement, and qualification: **27/114 = 23.68%**;
- delivered-item CoCs verified: **0**;
- release status: **NOT RELEASED**.

The >50% target is not honestly supportable on current evidence. The bounded targeted-retrofit practical ceiling is **23.68%**. Reaching >50% would require selecting unresolved configured tubing/Bowden/tether assemblies and/or replacing custom lock, trigger, manifold, harness, and recovery architecture with larger COTS modules. Those changes exceed an architecture-preserving targeted retrofit until exact configurations, packaging, loads, and qualification evidence exist.

## Selected for qualification, not implementation

| ID | Exact selection | MAKE definitions covered | Gate condition |
|---|---|---:|---|
| C-001 | Swagelok `316L-50DF4-150` | 3 | Exact CAD package fit, gas budget, external-pressure review, relief design, and receiving traceability. |
| C-006 | HIKO `87640_OLV_ONE` FLOATEK FULL TAIL | 8 | Two-specimen pack/inflate/seam/relief/load qualification; manufacturer page currently reports sold out. |
| C-012 | Gutekunst `VD-244` | 1 | Match manufacturer data/CAD to final-cleanup spring seats and incoming rate/length. |
| C-013 | igus `GFM-081013-08` | 1 | Press-fit, wet-wear, load/life, and exact stack verification. |
| C-014 | igus `GTM-0815-005` | 1 | 0.5 mm axial-stack and wet-thrust verification. |
| C-015 | Smalley `VSM-8-S16` | 1 | Factory confirms 316 SS suffix, groove, load, certificate options, and service policy. |
| C-016 | Rotor Clip `DC-4SS` | 2 | Existing DC-4SS groove/load equivalence for actuator and sear locations. |

`SELECTED_FOR_QUALIFICATION` is a Phase-3 research decision. It does not mean catalog fit, procurement readiness, CAD acceptance, qualification, release, or delivered-item CoC.

## Deferred architecture-value leads

- Nordson/Halkey-Roberts Hydro 1F complete inflator: exact suffix and flow duty unresolved.
- Subsalve Rapid Recovery System: high COTS-heavy reuse potential, but only as a custom-size architecture trade.
- Southco `R4-10-20-901-20`: could consolidate six latch/stop definitions, but materially changes fail-safe lock architecture.
- Swagelok tubing/fittings: catalog components are verified, but the routed/terminated line assemblies remain custom.
- Cablecraft marine control cable: no exact MPN, length, ends, pressure-ingress basis, or official evidence was established.
- Samson AmSteel-Blue: raw rope is COTS; the proof-certified finished two-eye tether remains configured/custom.
- JW Winco pin and clevis families: exact grip, shear, captive retention, and motion fit remain unresolved.

## Release boundaries

Owner Creo visual inspection remains required before remaining release validation. Accepted motion evidence remains only through 55 degrees. State-parity evidence remains 279/279. The product remains **NOT RELEASED** and all pressure articles remain **RECEIVED-ITEM COC NOT VERIFIED**.

## Exact next action

Owner accepts or rejects final-cleanup CAD baseline `8c594781e27b0597a71957082fb64f152cacfcd9` after Creo visual inspection. If accepted, procurement engineering requests certificate-bearing quotations and official CAD for the seven selections, beginning with two empty Swagelok `316L-50DF4-150` cylinders, two HIKO `87640_OLV_ONE` bags, and two ACE `HBD-15-25-AA-P` dampers; engineering then performs fit-only CAD evaluation and qualified fixture/chamber test planning. Do not begin CAD implementation before that acceptance.
