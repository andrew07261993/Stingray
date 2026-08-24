# Architecture alternatives

All mass values are architecture estimates, not CAD or measured values. All envelope assessments are packaging hypotheses. Each concept is non-electrical and non-pyrotechnic, retains three arms and a continuous structural recovery chain, and uses no custom pressure vessel.

## A — Twin marine-module 74

**Differentiator:** two independent marine automatic/manual inflator modules, each with one 70 g disposable cartridge, feed a common buoy through check valves. One branch also pilots the mechanical arm-release actuator.

**Functional block:** `water authorization → [inflator+70 g] × 2 → checked common outlet → buoy`; one outlet takeoff also drives `pilot release → springs/damper → common crosshead → arms/stops/locks`, while `buoy harness → tether → body` is the independent structural recovery path.

**Sequence:** transport inhibit removed → water dissolves either/both V80040 bobbins → Alpha mechanisms pierce Leland 89070 cartridges → check valves combine flow → pilot cylinder releases stowed lock → gas spring plus backup spring drive the common crosshead → arms seat against stops and positive locks → buoy ejector releases and buoy inflates.

**Reset:** vent low-pressure lines; verify cartridges discharged; replace both cartridges and bobbins; reset pilot actuator/crosshead/arms/locks; repack buoy; leak and functional checks.

| Attribute | Assessment |
|---|---|
| Principal exact candidates | Halkey-Roberts V95000XXB/Alpha family; V80040; Leland 89070; Swagelok SS-4C-1/3; ACE GS-19-50-V4A-B8-B8; HBD-15-25-AA-P |
| Pressure architecture | 2 × 70 g CO2, independent piercers, parallel checked discharge; 140 g installed |
| Remaining custom lines | penetrator; body/carrier; crosshead/arms; buoy enclosure; module adapter; pack-door interface |
| Estimated mass / reserve | 13.3 kg / 4.84 kg |
| Envelope | RISK: 30.0 mm × 205.0 mm cartridges fit the diameter individually; two-module axial arrangement not demonstrated |
| Functional COTS | 16/22 = 72.73% |
| Custom adapter count | 6 projected mounts/interfaces; no custom vessel |
| Custom unique lines / fabrication operations | 6 / 16 |
| Supplier count | 9 |
| CoC posture | Most at maturity 2–3; CoC availability largely unconfirmed; delivered CoCs 0 |
| Field reset | Strong; replace two sealed cartridges and two bobbins |
| Qualification burden | Moderate-high; dual-flow balance, common outlet, false activation, cold/depth performance |
| Failure tolerance | One branch may provide partial inflation; whether 70 g alone meets minimum buoyancy is unknown |
| Single-source risk | Halkey-Roberts inflator/bobbin pair |
| Physical tests | water activation, cold/depth inflation, one-branch-out deployment, reset repeatability, corrosion |

## B — DOT refillable 300

**Differentiator:** one 316L DOT-compliant 300 cm³ cylinder replaces disposable cartridges. A separate water sensor mechanically pilots an industrial valve train.

**Functional block:** `water sensor → pilot valve → DOT cylinder isolation/full-flow/relief → buoy`; the pilot also drives `release actuator → springs/damper → common crosshead → arms/stops/locks`, with a separate structural `buoy harness → tether → body` path.

**Sequence:** inhibit removed → water trigger actuates pneumatic pilot → cylinder isolation/full-flow valve opens → regulated flow inflates buoy and actuates release cylinder → springs/gas spring deploy and lock arms → buoy extracts and fills.

**Reset:** isolate and remotely depressurize through a rated service panel; remove cylinder; qualified field-maintenance station weighs/inspects/recharges or exchanges it; reset water element, valves, actuator, arms and pack; pressure-boundary leak test and proof of pre-use function.

| Attribute | Assessment |
|---|---|
| Principal exact candidates | Swagelok 316L-HDF4-300 DOT-3E cylinder; SS-4R3A1 relief; SS-4C-1/3 check; Halkey V80040 sensor element; Clippard SRR-14-4 cylinder |
| Pressure architecture | One refillable 300 cm³ 316L cylinder with isolation, relief, check and full-flow control; charge mass/configuration unapproved |
| Remaining custom lines | penetrator; body/carrier; arms/crosshead; buoy enclosure; sensor-to-pilot adapter; cylinder mount; service panel; valve linkage |
| Estimated mass / reserve | 14.7 kg / 3.44 kg |
| Envelope | PROVISIONAL: cylinder is 50.8 mm OD × 227 mm; fittings/mount and 53 mm target clearance unresolved |
| Functional COTS | 15/23 = 65.22%; below target |
| Custom adapter count | 8 projected mounts/linkages/service interfaces; no custom vessel |
| Custom unique lines / fabrication operations | 8 / 19 |
| Supplier count | 10 |
| CoC posture | Cylinder catalog states DOT-3E; material/certificate order requirements still need RFQ; delivered CoCs 0 |
| Field reset | Weakest: controlled recharge/exchange and pressure-boundary service are field-maintenance, not ordinary operator work |
| Qualification burden | High: approved CO2 fill density, valve Cv, regulator/relief settings, service station and recharge lifecycle |
| Failure tolerance | Single pressure source and main isolation valve are single-point failures |
| Single-source risk | Configured cylinder/valve train and qualified fill service |
| Physical tests | rated-system discharge, depth/cold inflation, recharge repeatability, relief behavior, corrosion |

## C — Distributed three-cartridge mechanical bus (provisional selection)

**Differentiator:** three physically separated 70 g disposable cartridge/inflator branches feed a catalog-fitting bus. Primary arm energy remains in replaceable mechanical modules, decoupling arm deployment from full buoy inflation.

**Functional block:** `water authorization → [inflator+70 g+check] × 3 → COTS fitting bus+relief → 60 L-class buoy`; pilot takeoff drives `release cylinder → gas spring+backup spring+damper → common crosshead → three arms/stops/locks`; `buoy harness → tether → body/penetrator` remains the separate recovery load path. The rendered form is in `FUNCTIONAL_BLOCK_DIAGRAM.svg`.

**Sequence:** inhibit removed → water element initiates three independent piercers (or a mechanically synchronized set) → each branch discharges through its own check valve → pilot takeoff retracts release plunger → gas spring and backup compression spring drive common crosshead → damper bounds speed → arms engage replaceable stops and positive locks → ejector spring releases buoy → checked bus inflates buoy; relief path protects the bladder.

**Reset:** verify pressure absent at indicator/vent; replace three cartridges and water elements as a keyed service kit; inspect/replace branch check modules; reset pneumatic release actuator; reverse-reset crosshead/arms/springs/locks; repack buoy and ejector; close service door; inspect pressure connections; low-energy inert-gas leak test in a rated fixture; pre-use mechanical witness and inhibited functional check.

| Attribute | Assessment |
|---|---|
| Principal exact candidates | 3 × Leland 89070; Halkey-Roberts V95000XXB family/V80040; Swagelok SS-4C-1/3 and SS-400-3 fittings; KVV11DE1 relief; Clippard SRR-14-4; ACE GS-19-50-V4A-B8-B8; HBD-15-25-AA-P; Lee Spring LHL 625D 12; Gutekunst VD-244; GN 817/GN 615.3; Samson AmSteel-Blue 872 7/64 |
| Pressure architecture | 3 × 70 g CO2 branches, individually checked into COTS fitting bus; 210 g total; no custom vessel |
| Remaining custom lines | penetrator; primary body/carrier; common crosshead/three-arm set; buoy pack enclosure/door; small interface-adapter set |
| Estimated mass / reserve | 14.0 kg / 4.14 kg |
| Envelope | PROVISIONAL: each cartridge is about 30.0 mm × 205.0 mm; distributed axial packaging is plausible but unproven |
| Functional COTS | 18/23 = 78.26%; truthful ceiling without denominator manipulation |
| Custom adapter count | 5 projected non-pressure mounts/yokes/seats; no custom vessel |
| Custom unique lines / fabrication operations | 5 / 14 |
| Supplier count | 11; multisource fittings/fasteners excluded from metric |
| CoC posture | Maturity 2–3; no procurement evidence or delivered identity; delivered CoCs 0 |
| Field reset | Strongest: keyed cartridge/bobbin/check service kit; no refill station or custom vessel lifecycle |
| Qualification burden | Moderate-high: simultaneous initiation, branch isolation, 70 g inflator compatibility, relief, depth/cold sizing |
| Failure tolerance | Three branches; one blocked branch leaves 140 g, two blocked leave 70 g. Minimum safe partial buoyancy remains a design gate |
| Single-source risk | Leland 89070 and Halkey-compatible 70 g piercer configuration; alternatives require interface requalification |
| Physical tests | water-trigger repeatability, full/one-branch-out cold-depth inflation, pneumatic release/damper cycles, field reset demonstration, corrosion |

## Common conclusion

Architecture B is below 70% and carries the largest field-service and recharge burden. A meets the minimum but couples more function to two marine inflators. C has the highest compliant COTS projection and best modular reset/failure tolerance, but it is only provisional because the unknown mission depth and temperature can invalidate the 210 g charge, and no retained inflator is yet vendor-confirmed for a 70 g cylinder.
