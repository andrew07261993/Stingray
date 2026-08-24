# Pressure architecture

Status: **CONCEPT DEFINED — COMMERCIAL PATH IDENTIFIED — REVISION / VENDOR APPROVAL REQUIRED BEFORE CAD**

## Required pressure path

```text
[89070 cartridge × N]
  → [manufacturer-approved supported water puncture/inflator × N]
  → [HP branch check × N]
  → [HP collection bus + service pressure indication]
  → [pressure-reducing regulator]
  → [fixed flow restrictor / anti-icing transition]
  → [buoy-adjacent high-flow differential relief]
  → [60 L-class buoy]
```

The earlier concept of a check-valve bus plus unspecified relief is not sufficient. Architecture C requires both pressure reduction/flow control and buoy-adjacent relief. The regulator controls normal delivery; the fixed restriction bounds regulator-fail-open flow; the relief protects the buoy and ascent condition. No low-pressure buoy may be connected directly to cartridge equilibrium pressure.

## A. Stored-cartridge pressure

CO2 is two-phase through much of the storage range and pressure is strongly temperature dependent. NIST data gives approximately 35.5 bar absolute at 0 °C, 51.1 bar at 15 °C, 57.4 bar at 20 °C and 64.4 bar at 25 °C for saturation. `89070` is 70 g in 100 mL (700 kg/m³ nominal fill density). Above the two-phase crossover, pressure rises faster than vapor pressure; a Peng–Robinson constant-density bound is approximately 131 bar / 1,895 psia at 40 °C and 163 bar / 2,365 psia at Leland's 120 °F heat limit. These are engineering estimates, not Leland ratings.

Therefore the high-pressure design basis is **2,500 psig minimum design pressure, with every wetted HP component rated at least 3,000 psig throughout its temperature range**. If Leland's application pressure or maximum service temperature produces a higher value, that value controls and the architecture must be uprated. The cartridge itself remains a separately approved disposable pressure receptacle; transport approval does not approve the device application.

## B. High-pressure branch design pressure

The puncture head, cartridge support, branch check, tube, fittings, bus and regulator inlet see the stored/transient source pressure. Nominal pressure is temperature-dependent (roughly 500–1,100 psia over 0–30 °C); the maximum credible controlled-temperature pressure is bounded at approximately 2,400 psia at 120 °F. Minimum useful pressure is whatever maintains regulator flow above `Pambient + required buoy differential + losses` through end-of-discharge; it is a transient test result.

Candidate component ratings:

- Swagelok `SS-4C-1/3`: 316 SS, 1/3 psig crack, Cv 0.47, 3,000 psig at 100 °F.
- Swagelok `KPR1DRB412A20000`: 316 SS, 3,600 psig inlet, 0–25 psig outlet range, Cv 0.06, 80 °C maximum.
- Leland `65026-18N12`: 1/2-20 inlet, 1/8 NPT outlet, stainless, CO2-compatible; public working-pressure and 70 g application limits are unavailable.

The first two provide a credible catalog rating path, but neither is publicly approved for submerged, flashing-liquid CO2 duty. The Leland puncture head lacks public pressure/mass approval. These are CAD-entry blockers.

## C. Downstream buoy pressure

Required buoy inlet absolute pressure is:

`Pbuoy,in = Patmosphere + rho_water*g*depth + ΔP_operating + ΔP_line/check/inlet`

`ΔP_operating`, inlet loss and regulator reference behavior are unknown. The 10 kPa value in gas sizing is only sensitivity. The regulator must either reference local ambient water pressure or be selected/configured on a demonstrated absolute-pressure basis. A standard dry-gas regulator cannot be presumed to regulate correctly while externally submerged.

## D. Buoy differential pressure

`ΔPbuoy = Pinternal − Pambient`. This, not cartridge pressure, loads the flexible buoy. Required differential must be high enough to unfold and establish usable geometry while remaining below supplier MAWP at every depth and during ascent. HIKO publishes no MAWP for `87640_OLV_ONE` and does not describe direct CO2 inflation; it is a developmental softgoods article only.

## E. Relief pressure

The required differential setting envelope is:

`ΔP_required + line/dynamic allowance < ΔP_relief,set`

and

`ΔP_relief,set + positive tolerance + full-flow accumulation ≤ buoy differential MAWP`.

The valve must vent to local ambient, pass the regulator-fail-open/restrictor-limited CO2 flow without exceeding MAWP, reseat after discharge/ascent, tolerate cold CO2 and seawater, and be installed adjacent to the buoy. No numeric set point is selected.

## F. Proof / component rating

- HP wetted components: catalog MAWP ≥3,000 psig at temperature, with manufacturer pressure/leak/proof documentation; design basis ≥2,500 psig pending Leland data.
- Regulator outlet and LP fittings: catalog MAWP at least the regulator maximum outlet plus fault/relief accumulation, never less than buoy MAWP.
- Buoy/relief: supplier MAWP, production test and relief flow evidence are mandatory.
- Proof/burst testing is outside this commission and may only be performed by a qualified facility under an approved procedure. Hydrostatic depth testing is not pneumatic proof.

## Blocked-flow and relief behavior

| Location blocked | Result | Required control |
|---|---|---|
| Piercer outlet / HP check | Branch remains at cartridge pressure; no buoy gas | HP rating; supported cartridge; branch-out detection/test |
| HP bus / regulator inlet | All fired sources remain at storage pressure | 2,500 psig design basis; ≥3,000 psig catalog rating; temperature control |
| Regulator closed | No inflation | independent functional check; sufficient cartridge count does not cure this single-point failure |
| Regulator fails open | Excess downstream pressure/flow | fixed restrictor plus high-flow differential relief sized for fault flow |
| Relief blocked | Buoy can overpressure even with an orifice | relief inspection; debris guard; supplier-approved redundant/integral protection where required |
| Buoy inlet blocked | LP train pressurizes to regulator setting and relief opens | relief adjacent to inlet; all LP parts rated above accumulation |

Sources: [Swagelok KPR1DRB412A20000](https://products.swagelok.com/en/c/single-stage/p/KPR1DRB412A20000), [Swagelok SS-4C-1/3](https://products.swagelok.com/en/c/fixed-pressure/p/SS-4C-1%252F3), [Leland 65026-18N12](https://www.lelandgas.com/product-page/copy-of-65026-18n12-puncture-device-in-line-non-mountable), and [NIST CO2](https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=4).
