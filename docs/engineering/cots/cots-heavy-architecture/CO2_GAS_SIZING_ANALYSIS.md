# CO2 gas sizing analysis

Status: **OWNER-CASE MASS SIZING CLOSED — TRANSIENT AND BUOY-PRESSURE QUALIFICATION OPEN**

## Method

The existing Peng–Robinson model is retained. It calculates 60.0 L actual usable gas volume at deployment depth using 101.325 kPa atmosphere, 1,025 kg/m³ seawater, 9.80665 m/s² gravity and a provisional 10 kPa buoy differential. That differential is a sizing sensitivity, not a buoy pressure requirement.

| Scenario | Temperature | Discharge utilization | Leakage/flow/reserve adder | Design multiplier | Qualification multiplier |
|---|---:|---:|---:|---:|---:|
| Warm | 25 °C | 0.92 | 10% | 1.196 × theoretical | 1.316 × theoretical |
| Nominal | 15 °C | 0.85 | 15% | 1.353 × theoretical | 1.488 × theoretical |
| Cold | 0 °C | 0.75 | 20% | 1.600 × theoretical | 1.760 × theoretical |

Utilization bounds residual gas, flashing, line/check/regulator losses and cold/icing loss. The reserve bounds leakage, dead volume and flow-rate uncertainty. Qualification adds 10% model/test margin. Physical testing must validate these assumptions.

## Controlling owner case

At 5.0 m and 0 °C:

- ambient absolute pressure: 151.58 kPa;
- modeled buoy absolute pressure with 10 kPa sensitivity: 161.58 kPa;
- Peng–Robinson compressibility factor: 0.98847;
- theoretical minimum: **190.06 g**;
- design inventory: **304.10 g**;
- qualification inventory: **334.51 g**.

## Discrete `86202Z` result

| Count | Inventory | Design margin | Qualification margin | Gate |
|---:|---:|---:|---:|---|
| 5 | 190 g | −114.10 g | −144.51 g | FAIL |
| 6 | 228 g | −76.10 g | −106.51 g | FAIL |
| 7 | 266 g | −38.10 g | −68.51 g | FAIL |
| 8 | 304 g | −0.10 g | −30.51 g | FAIL |
| **9** | **342 g** | **+37.90 g / +12.46%** | **+7.49 g / +2.24%** | **PASS** |

Nine is the lowest integer count satisfying both controlling mass cases. No one-branch-out requirement is controlled, so a tenth is not added merely as unsourced redundancy. Nine is a thermodynamic count only; the V95000-to-HP-bus interface is not published and the architecture is not released.

## Useful-inflation criterion

Within 10.0 s of water activation, achieve at least 54 L actual displaced volume at 5 m, stable intended geometry, and displacement holding/increasing without structural leakage. Full steady-state usable displacement remains 60 L. Rated/geometric capacity or visual fullness does not pass.

## What mass sizing does not close

Static mass does not establish 10 s inflation. Two-phase flashing, regulator droop, check/orifice capacity, line heat transfer, dry ice/icing, nine-way synchronization, relief accumulation and gas dissolution/contact losses require an instrumented 0 °C/5 m test or approved equivalent. Type 3 tests only the small-scale trigger/puncture/rearm architecture.

NIST is the thermophysical source: [NIST CO2 fluid data](https://webbook.nist.gov/cgi/fluid.cgi?ID=C124389&Action=Page).
