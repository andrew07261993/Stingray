# Architecture C pressure-source revision gate

## Disposition

**ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION**

CAD implementation is not authorized.

## Final sizing result

At 5 m, 0 °C, 60 L and provisional 10 kPa differential:

| Count | CO2 | Design result | Qualification result |
|---:|---:|---:|---:|
| 5 | 190 g | FAIL by 114.10 g | FAIL by 144.51 g |
| 6 | 228 g | FAIL by 76.10 g | FAIL by 106.51 g |
| 7 | 266 g | FAIL by 38.10 g | FAIL by 68.51 g |
| 8 | 304 g | FAIL by 0.10 g | FAIL by 30.51 g |
| 9 | 342 g | PASS by 37.90 g | PASS by 7.49 g |

Nine is the lowest passing mass count. It is not a released pressure source.

## Why the architecture is not ready for CAD

- Pair compatibility: `V95000 + 86202Z` is **PUBLISHED CONFIGURATION SUPPORTED** in its published PFD/manifold application.
- STINGRAY interface: `V95000 + 86202Z + HP check + bus` is **APPLICATION APPROVAL REQUIRED / NO PUBLISHED INTERFACE**.
- HIKO low-pressure operating/MAWP/relief data are absent.
- The 3,000 psig at 50 °C HP basis is credible for screening, but every exact component’s derating and outlet rating remain open.
- Nine-way cold/depth activation, discharge and 10 s useful volume are untested.
- A custom pressure adapter/plenum would violate the architecture constraint.

## Development articles

- Type 1: two HIKO `87640_OLV_ONE`, development-only and supplier-data gated.
- Type 2: two ACE `HBD-15-25-AA-P`, immersion behavior developmental.
- Type 3: two complete LSC `481-CG` with `470-CG`/HR `V95000-1F` + `#484` 33 g; functional-scale only.
- Total articles: six; delivered-item CoCs accepted: zero.

## Exact next action

Obtain a manufacturer-supported commercial pressure outlet/source topology and a source-supported 60 L buoy pressure envelope. Only then freeze physical branch/check/bus/regulator/restriction/relief MPNs and perform the 0 °C/5 m/10 s qualified transient. Do not start CAD.
