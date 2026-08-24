# Relief and overpressure trade

## Decision

Architecture C requires **pressure reduction + fixed restriction + resettable high-flow differential relief**. A burst disc is not selected as the normal buoy protection because it is non-resettable and conflicts with field reset. A burst device may remain manufacturer-integral secondary protection on a cartridge or rated HP component, but it cannot protect the low-pressure buoy by itself.

No relief setting is selected. The controlling relationship is:

`ΔP_required + dynamic margin < set pressure`, while `set pressure + tolerance + full-flow accumulation ≤ buoy MAWP`.

The valve must be referenced to local ambient water pressure. A relief vented into a sealed dry enclosure or fitted with a secondary plug does not provide the required protection.

## Retained finalists (maximum five; three retained)

| Candidate | Type / range | Reseat / flow | Materials / temperature | Seawater / certificates / drawings | Disposition |
|---|---|---|---|---|---|
| Halkey-Roberts `2110Pxxx` | Factory-calibrated resettable molded relief; 0.3, 0.5, 1.0, 1.5, 3, 5 or 7 psig springs | Individually calibrated/tested; published high-flow curves; exact suffix sets crack pressure | Glass-filled nylon body/flange, ABS internals, stainless spring, Buna-N O-ring; −40 to 85 °C | Intended for liferafts, large containers and air bladders; SOLAS relief specification claim; drawings and tech data available; CoC option UNVERIFIED | **LEAD FAMILY** after buoy MAWP and exact suffix close |
| Leafield Marine `A6PG-XXXNXXX` / `A6NP-XXXNXXX` | Factory-set resettable relief/transfer family; nominal 0.5–20 psi selections published | 100% tested for opening/closing; high flow; pressure chart gives max opening and minimum sealing | UV-resistant engineered materials; −30 to 65 °C | Commercial/military inflatable-boat/liferaft use; ISO 9650/15738 and LR type-approval evidence; tooling/drawings available; CoC option UNVERIFIED | **SECOND LEAD** after exact pressure/color/attachment selected |
| Swagelok `KVV11DE1` | Adjustable 316 SS regulator relief, 0–100 psig | Public product page lacks flow/reseat curve and underwater backpressure behavior | 316 SS, FKM; temperature rating not on public item page | Exterior seawater suitability, calibrated set certificate and submerged vent behavior UNVERIFIED; CAD view available | **BENCH REFERENCE ONLY**; range/control resolution may be unsuitable for soft buoy |

Sources: [Halkey-Roberts 2110P](https://www.halkeyroberts.com/Products/2110-hi-flo-molded-relief-valves), [Leafield A6](https://www.leafieldmarine.com/pressure-relief-valves/a6-pressure-relief-valve/), [Leafield pressure chart](https://www.leafieldmarine.com/wp-content/uploads/2020/04/M-08-CI-A6-01-REV-03-Customer-Pressure-Selection-Chart-for-the-A6-Valve-1.pdf), [Leafield LR approval](https://www.leafieldmarine.com/wp-content/uploads/2020/04/A6-Approval-Certificate-SAS-S190065.pdf), and [Swagelok KVV11DE1](https://products.swagelok.com/en/c/adjustable-relief-valve/p/KVV11DE1).

## Why a controlled orifice alone is rejected

An orifice limits rate but not final static pressure. If the buoy inlet is open and relief is blocked, the buoy will eventually approach the upstream regulator/fault pressure. The orifice is retained only to make the fail-open flow bounded and relief-sizeable.

## Why a regulator alone is rejected

Single-stage regulator failure, droop, seat contamination, two-phase CO2 and submersion reference effects remain credible. Independent relief is required at the protected volume.

## Selection gates

1. Buoy supplier provides usable volume, operating differential, differential MAWP, inlet construction and ascent/vent requirement.
2. Owner provides depth, temperature and inflation time.
3. Vendor chooses exact `2110Pxxx` or A6 suffix and provides opening tolerance, reseat, fault-flow capacity, material compatibility and installation drawing.
4. Qualified testing shows relief accumulation stays below buoy MAWP at worst regulator-fail-open/restrictor-limited flow and cold CO2.
5. Purchase order requires exact MPN, factory set, test evidence, lot trace and CoC option. Delivered-item acceptance remains zero until receipt.
