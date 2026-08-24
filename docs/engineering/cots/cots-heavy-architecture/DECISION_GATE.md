# Architecture decision gate

## Decision

**ARCHITECTURE C PRESSURE CONCEPT REQUIRES REVISION**

Architecture C remains the COTS-heavy trade lead, but the three-cartridge implementation and incomplete pressure-control path are not acceptable for CAD implementation.

## Evidence supporting continued development

- Exact Leland `89070` catalog identity, 70 g fill, 100 mL capacity, 1.18 in diameter, 8.07 in length and 1/2-20 thread are supported.
- COTS HP check, regulator and low-pressure high-flow relief families provide a plausible commercial path.
- A modular field-reset architecture can avoid routine depot service.
- Two cross-architecture developmental article types can be purchased without committing to unsafe Type 3 pressure hardware.

## Failing / open gates

- Three 70 g cartridges fail cold qualification at the surface and fail nominal design by 3 m under declared sizing assumptions.
- No water inflator is approved for `89070`; compatibility is only **FIT APPEARS POSSIBLE — APPLICATION APPROVAL REQUIRED**.
- Owner mission values and buoy MAWP/relief data remain absent.
- The required regulator/restrictor/relief transient has not been sized or tested.
- HP puncture head rating/support and regulator submerged/two-phase CO2 use are unverified.
- Delivered identity and delivered-item CoCs remain 0.

## Gate state

`PRE_CAD_ENGINEERING_CLOSURE_COMPLETE = true`

`ARCHITECTURE_C_TRADE_LEAD = true`

`THREE_CARTRIDGE_CONCEPT_ACCEPTED = false`

`CAD_AUTHORIZED = false`

`DEVELOPMENT_PROCUREMENT_TYPE_1_2_RECOMMENDED = true`

`TYPE_3_PROCUREMENT_AUTHORIZED = false`

`PRODUCTION_PROCUREMENT_RELEASED = false`
`PRODUCT_RELEASED = false`

## Exact next action

Owner supplies the seven open mission/buoy values and approves development RFQs for two HIKO `87640_OLV_ONE` and two ACE `HBD-15-25-AA-P`; in parallel, request written `89070` application approval from Leland and the exact water-inflator manufacturer. Keep Type 3 and all CAD work held.
