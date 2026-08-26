# Technical Analysis Report

Status: **MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT, QUALIFICATION, OR FIELD USE**

Configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`

Frozen candidate hashes:

- STOWED AP242: `22342157b2ac96870bbf7cd227e729342b357fd241787be8dc03cf16a92ce7fd`
- DEPLOYED AP242: `3f33da7fc6c658c84bfad075ed9c28c9dd96087e675fc9f5d3de7562b19ee045`
- STOWED inventory: `67ae4314d128993d6ab0de761645717f704cbec47b14f33848999025a9f83765`
- DEPLOYED inventory: `7cebfb5c59d25ac148cda125ddce6094558b6fdfebc29c65f6243a1973d50498`

## 1. Scope and acceptance discipline

This report completes calculations that can be supported by the delivered geometry and controlled
manufacturer evidence.  It does not infer missing mission loads, proprietary inflator internals,
release tolerances, application ratings, or physical performance.  `NOT CALCULABLE`, `PARTIAL`, and
`DEFERRED TO PHYSICAL VERIFICATION` are release-blocking where the analysis is required.

## 2. Stored-gas capacity - FAIL

### Purpose

Screen whether the selected Leland 81121 12 g CO2 cartridge can supply the modeled 60 L buoy.

### Source-backed inputs

| Input | Value | Source |
|---|---:|---|
| CO2 mass | 12.000 g | Leland 81121 official product page |
| CO2 molar mass | 44.0095 g/mol | Standard molecular property |
| Buoy nominal volume | 60.000 L | Frozen CAD/configuration report |
| Ambient pressure | 101,325 Pa | Calculation reference condition |
| Temperature range | 0-45 C | Hydro 1F published air/water range bounds used for screen |

### Equations and substituted values

Moles:

`n = m / M = 12.000 g / 44.0095 g/mol = 0.272668 mol`

Optimistic ideal-gas volume at ambient pressure:

`V = n R T / P`

At 20 C:

`V = 0.272668 mol x 8.314462618 J/(mol K) x 293.15 K / 101325 Pa`

`V = 6.559 L`

| Condition | Ideal volume from 12 g CO2 | Fraction of 60 L |
|---|---:|---:|
| 0 C | 6.112 L | 10.2% |
| 20 C | 6.559 L | 10.9% |
| 45 C | 7.118 L | 11.9% |

Ideal CO2 mass required for 60 L at 20 C and one atmosphere absolute:

`m_required = V P M / (R T) = 109.772 g`

This ideal lower bound already exceeds the selected cartridge by
`97.772 g`.  Real delivery must also cover residual cartridge gas,
two-phase blowdown losses, inflator pressure drop, buoy back pressure, leakage, cooling, and required
gauge pressure.  Therefore the 12 g / 60 L pairing **FAILS** without needing those unavailable details.

Sensitivity: even the optimistic 45 C ideal volume is only
`7.118 L` (11.9% of nominal buoy volume).

### Release consequence

The inflation architecture must be reselected and requalified.  No inflator, cartridge, buoy, routing,
pressure-margin, or deployment-time release claim is permitted from the current combination.

## 3. Buoyancy and reserve buoyancy - PARTIAL

A 60 L fully displaced volume in 1025 kg/m3 seawater corresponds to a gross displaced mass of:

`m_displaced = rho V = 1025 kg/m3 x 0.060 m3 = 61.500 kg`

This is a geometric upper bound, not an accepted lift rating.  Delivered gas fails the volume screen,
and the required supported load, immersion, freeboard, stability, orientation, tether angle, dynamic
sea load, and softgood deformation are not controlled.  Net mission margin is **NOT CALCULABLE**.

## 4. Mass, center of gravity, and inertia - DIGITAL PASS

| State | Mass | Reserve to 18.14 kg | CG X | CG Y | CG Z |
|---|---:|---:|---:|---:|---:|
| STOWED | 10.583165211 kg | 7.556834789 kg | 2.456 mm | 0.244 mm | 474.113 mm |
| DEPLOYED | 10.583165211 kg | 7.556834789 kg | 9.210 mm | -0.218 mm | 494.879 mm |

The occurrence-weighted calculation resolves all 180 occurrences.  This is a
digital CAD result and does not replace as-built weighing or balance verification.

## 5. Mechanism kinematics and complete motion - DIGITAL PASS

Acceptance criteria: 0-80 degree coverage in increments no greater than one degree; zero unauthorized
positive-volume pairs; zero blocked Booleans; zero track errors; zero intentional-fit register errors.

| Gate | Angles/pairs | Unauthorized overlaps | Blocked Booleans | Track errors | Result |
|---|---:|---:|---:|---:|---|
| Endpoint | 16110 pairs/state | 0 | 0 | n/a | PASS |
| Five-angle | 43035 rows | 0 | 0 | 0 | PASS |
| Full 0-80 degree | 697167 rows | 0 | 0 | 0 | PASS |

Crosshead travel from 0 to 80 degrees is `15.055034371 mm`; maximum
absolute closure residual is `2.487e-14 mm`.

The exact-Boolean audit classifies every positive-volume contact through the controlled intentional-fit
register.  It does not establish dynamic deployment, impact, fatigue, or physical lock capacity.

## 6. Envelope and state integrity - DIGITAL PASS

- Ready-to-throw rigid length: `1675.400 mm`.
- Closed pack maximum OD: `98.000 mm`.
- Arm pivot station: `355.000 mm`.
- Arm pivot-to-tip: `378.206000 mm`.
- STOWED and DEPLOYED inventories: 180 occurrences each.
- Fixed/moving/flexible identity and transforms are recorded in the two authoring inventories.

## 7. Pressure topology, flow, ratings, and leakage - NOT RELEASED

The current topology is a compact direct path: non-refillable cartridge -> Hydro 1F family inflator ->
buoy manifold/patch.  No hose or tube route is modeled.  The Leland cartridge is explicitly 3/8-24;
the Hydro 1F family supports 3/8 or 1/2 in cylinder variants, but the modeled `V95000xxB` identity does
not complete the controlling suffix.  The exact manifold interface, internal orifice, flow curve,
delivered pressure, application rating, and installed leak performance are absent.

Pressure loss, time-to-inflate, operating margin, open-port closure, and leakage are therefore
**NOT CALCULABLE**.  The gas-capacity FAIL remains controlling regardless.

## 8. Softgood opening, extraction, and retention - PHYSICAL VERIFICATION REQUIRED

The CAD includes separate closed STOWED and owner-approved open DEPLOYED pack states, individual
panels, hook-and-loop fields, seams/reinforcements, tether hardware, and attachment records.  A prior
screen assumed wet peel force of 32.1-74.9 N and inferred 5.230-12.204 kPa over the modeled area; those
are assumptions, not test data.  The inflator delivered-pressure curve is unavailable and the gas
capacity screen fails.  Opening margin is **NOT CALCULABLE**.

Required tests include wet breakaway/opening, fold/extraction repeatability, seam and webbing proof,
retention, re-pack/reset, water activation, leak, inflation-time, and environment conditioning.

## 9. Structural, fastener, impact, fatigue, tolerance, and manufacturing analyses

Nominal geometry, material assignments, occurrence interfaces, and the complete motion audit are
available.  Controlling mission loads, proof factors, dynamic impact cases, duty spectrum, joint
preload, supplier material allowables, release tolerances, process capability, and approved drawings
are not.  Strength, stiffness, pin/fastener margins, fatigue life, impact margin, and tolerance stacks
are **NOT CALCULABLE**.  Fabrication is prohibited until those inputs and calculations are controlled.

## 10. Independent calculation check

The stored-gas screen is independently recomputed in `STORED_GAS_INDEPENDENT_CALCULATION.json` from
the stated constants.  The result is insensitive to reasonable temperature variation and establishes
a large deficit.  The mass report is independently reconciled to 180 positive-
mass occurrences per state.  The endpoint, five-angle, and full-motion results use separate validators
bound to the frozen STEP and inventory hashes.

## 11. Final disposition

Digital mechanism geometry, endpoint integrity, state parity, nominal envelope, mass properties, and
exact-Boolean motion are acceptable as developmental evidence.  Production release is blocked by the
gas-capacity failure, incomplete installed inflator configuration/rating, dimension-controlled proxy,
missing physical qualification, missing mission loads, and missing manufacturing definition.
