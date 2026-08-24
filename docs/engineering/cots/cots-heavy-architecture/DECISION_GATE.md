# Architecture decision gate

## Decision

Architecture C is **PROVISIONALLY SELECTED** for the next, separately authorized detailed-design phase. Architectures A and B remain trade evidence; none is released.

## Evidence sufficient for provisional selection

- Independent baseline lineage verified.
- Three materially different architectures evaluated.
- First-order gas balance identifies why 48 g baseline cartridge gas cannot independently support 60 L.
- Current manufacturer identities support 70 g disposable sources, automatic water inflator family, DOT sample-cylinder alternative, pressure-control components, springs, actuator/damper, locks and tether candidates.
- Weighted score constrains mission compliance, pressure risk and reset/service higher than COTS percentage alone.
- Architecture C meets the minimum projected COTS objective and avoids a custom vessel.

## Evidence insufficient for implementation or release

- Owner Creo visual acceptance of corrected baseline.
- Mission depth, minimum temperature, inflation time, buoy pressure/relief and complete qualification environment.
- Vendor confirmation that the selected inflator accepts and safely flows a 70 g cartridge.
- Source-derived packaging, mass and load analysis.
- RFQ/quote, CoC options, traceability, delivered identity and delivered-item CoC.
- Underwater, pressure, corrosion, deployment, recovery and reset test results.

## Gate status

`PHASE_4_COMPLETE = true`

`PROVISIONAL_ARCHITECTURE = C`

`CAD_AUTHORIZED = false`

`PROCUREMENT_RELEASED = false`

`PRODUCT_RELEASED = false`

## Exact next action

Owner performs the required Creo visual inspection of final-cleanup commit `8c594781e27b0597a71957082fb64f152cacfcd9`, then records architecture acceptance/rejection and supplies the missing depth/cold/time/buoy-pressure requirements. Only after that decision may a separate commission begin source-derived Architecture C packaging and detailed pressure analysis.
