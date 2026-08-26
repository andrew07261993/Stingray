# STINGRAY Current State

As of: 2026-08-25

## Current developmental direction

- The latest physically shown developmental CAD direction is a shortened-arm, forward-shifted deployment architecture with an external buoyancy pack. The model name reported in the latest review was `STINGRAY_I5S_DF8_SHORT14_FORWARD`. Its exact Git provenance still needs to be resolved locally on ANDREWSPC.
- Within the preserved GitHub inspection-package branch, Package 05 — `05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY` — is the most-forward compact developmental variant currently completed there. It uses a true forward powertrain, approximately 14.890-in arms and an external buoy architecture. It is developmental engineering inspection CAD, not a released design.
- The validated DF8 R2 state-parity baseline remains an important geometric/provenance reference but is no longer assumed to be the newest geometry.

## Validated baseline reference

Local authoritative source previously identified:

`C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-state-parity`

Known reference commit:

`61a58cbbccd0aae7a747b2a73046142cf1f44511`

State-parity audit was later resolved with 279/279 occurrences passing and zero unresolved parity issues after correcting a non-semantic OCCT local-BREP digest check.

## Later staged-inflation development

A later local developmental branch was reported as:

`design/df8-final-staged-inflation-convergence`

HEAD:

`dce7a53643a35d80f5cd6f63f09852ab565a4165`

Reported status: measured non-pass / Path B, not a released configuration.

Key recorded constraints/results for that development included:

- nose-tip to pivot: 480.000 mm
- rigid OD hard limit: 57.150 mm
- rigid length limit: 2032 mm
- ready-to-throw mass limit: 18.14 kg
- staged buoyancy requirement: 15.925970 L initial at 5 m / 0 °C
- nominal surface buoyancy volume: 60 L
- CO2 qualification quantity: 229.627609 g
- no supported complete commercial automatic module was found that fit the 50.700 mm bore in that study

Treat this as developmental analysis/history unless local source inspection establishes it as controlling for the current shortened/external-buoy model.

## COTS objective

Primary design objective: maximize genuinely orderable COTS components and minimize fabricated components while preserving the required function, structural load paths, serviceability, envelope, deployment reliability and qualification evidence.

The prior documented COTS baseline contained 121 PartDefs, 104 MAKE definitions, 17 COTS-related definitions and 15 independently purchasable COTS lines. A targeted COTS retrofit was started but only Phase 1 was documented as complete. Further COTS convergence remains active work.

## External buoyancy direction

Current engineering recommendation from the 2026-08-25 external-pack study:

- Primary COTS candidate: SECUMAR Pack Buoyancy Aid with SECUTRONIC, approximately 350 N / 35 L / 77 lbf, using a 75 g CO2 system.
- Integration concept: retain the commercial bladder/inflator/rearm architecture and design only the STINGRAY structural saddle/cradle and independent structural recovery load path.
- Selection remains pending packed dimensions, total mass/CG, exact orderable MPN, activation configuration and a rated structural attachment/load path from SECUMAR.
- The external softgoods pack should not be assumed to fit inside the 57.15 mm rigid-body OD. A 115–120 mm local softgoods envelope is a provisional early CAD keep-out only, pending actual vendor dimensions.

## Release status

No current shortened/external-buoy configuration in this context should be called fabrication released, procurement released, qualified, operationally ready or flight ready.

The current task is engineering convergence: reconcile the latest local CAD, COTS sourcing, analyses and validation into one controlled source of truth.