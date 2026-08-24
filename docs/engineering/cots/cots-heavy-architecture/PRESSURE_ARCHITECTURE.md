# Pressure architecture — owner mission closure

## Disposition

The required functional hierarchy is retained, but no final physical path is frozen:

`commercial CO2 source → water-authorized puncture/inflator → branch isolation/check where required → HP collection → regulator → fixed restriction → buoy-adjacent differential relief → 60 L buoy`

The prior V95000-to-HP-check interface is not published. Therefore cartridge count is frozen thermodynamically at nine `86202Z` units, while inflator count, check arrangement and HP bus architecture remain **NOT FROZEN — PRESSURE ARCHITECTURE REVISION REQUIRED**.

## Pressure hierarchy

| Zone/node | Nominal or operating basis | Maximum credible | Required rating/control | Gate |
|---|---|---|---|---|
| Stored `86202Z` cartridge | CO2 equilibrium/dense-fluid pressure at actual temperature | ≈2,624 psig at 50 °C using the NIST 760 kg/m³ proxy; Leland-controlled maximum pending | Commercial source within manufacturer limits | Leland pressure/temperature and fill-density declaration required |
| Puncture/inflator/outlet | Source pressure during puncture/discharge | Same source basis plus any blocked transient | Manufacturer-approved cartridge, holder/reaction path, rated outlet and derating | V95000 published outlet absent |
| HP check and branch | Source pressure; transient two-phase flow | Maximum source/blocked-branch transient | Allowable/MAWP ≥3,000 psig at 50 °C; CO2/seal/flow suitability | Exact commercial interface not selected |
| HP collection/regulator inlet | Highest active-source pressure | Common blocked transient | Allowable/MAWP ≥3,000 psig at 50 °C; verified derating | Topology not selected |
| Regulator outlet/fixed restriction | Controlled low pressure | Regulator lockup/fail-open transient | CO2 two-phase/cold qualification; restriction bounds relief fault flow | Exact MPN/Cv not selected |
| Buoy inlet | Ambient + required operating differential + losses | Limited below supplier MAWP | Rated low-pressure connection and buoy-adjacent relief | Supplier envelope absent |
| Buoy differential | Supplier-supported shape/volume pressure | Supplier MAWP | Must achieve 60 L at 5 m without exceeding MAWP | UNESTABLISHED |
| Differential relief | Shut at required operating differential | Pass worst credible fault flow without buoy MAWP exceedance | Factory-set/calibrated, depth/backpressure-qualified, resettable preferred | No numeric set/reseat/capacity authorized |

## HP design basis

NIST CO2 isochoric calculations at 760 kg/m³ provide the documented screening series in `HP_PRESSURE_TEMPERATURE_BASIS.csv`: approximately 2,306 psig at 45 °C and 2,624 psig at 50 °C. The owner environment sets 0 °C minimum but not a lower maximum storage temperature than the recorded 49 °C / 120 °F warning; therefore use a rounded **3,000 psig at 50 °C** component basis.

For every HP item:

`manufacturer allowable/MAWP at 50 °C ≥ 3,000 psig > 2,624 psig maximum-credible screening pressure`

This does not invent a code factor. It is the bounded rating needed for component screening until Leland’s controlled pressure-temperature/fill data and the governing design-code margin are supplied. Items rated 3,000 psig only at 100 °F remain open.

## Low-pressure envelope

HIKO `87640_OLV_ONE` has no published rated volume verification, operating differential, MAWP, inlet rating, proof/burst, relief or cycle data. Consequently:

- operating differential: **UNESTABLISHED**;
- relief crack/set and tolerance: **UNESTABLISHED**;
- reseat and flow capacity: **UNESTABLISHED**;
- buoy MAWP: **UNESTABLISHED**;
- numeric regulator outlet/setpoint: **NOT AUTHORIZED**.

The 10 kPa differential in gas sizing is sensitivity only. Subsalve’s published 2.5 psig enclosed-bag relief is test-reference evidence and cannot be transferred to HIKO.

## Failure behavior

A blocked source branch must remain inside all cartridge/outlet/check ratings. A blocked HP collection volume must not depend on a low-pressure buoy relief. Regulator fail-open must be flow-bounded by a fixed restriction sized so the buoy-adjacent relief holds the buoy below MAWP at 5 m backpressure and 0 °C discharge. Full ascent must vent without overpressure as ambient pressure falls.

No custom pressure vessel, receiver, adapter or improvised manifold is authorized.
