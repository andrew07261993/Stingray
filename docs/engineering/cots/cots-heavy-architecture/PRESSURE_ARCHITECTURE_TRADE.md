# Pressure architecture trade

> Historical Phase 3/4 screening. Superseded for the pre-CAD pressure decision by `CO2_GAS_SIZING_ANALYSIS.md`, `PRESSURE_ARCHITECTURE.md`, and `PRE_CAD_ENGINEERING_GATE.md`. The three-cartridge embodiment now requires revision.

## First-order gas sizing

For a nominal 60 L flexible buoy, the ideal-gas screening equation is:

`m_CO2 = M_CO2 × P_absolute × V / (R × T)`

At 20 °C and sea-level pressure this gives approximately **0.110 kg CO2** before allowance for residual unusable gas, cold cartridge effects, two-phase flow, dissolution, restrictions, valve losses, leakage, inflation-rate needs, or buoy relief. A 20% screening allowance gives **0.132 kg at the surface**. In seawater the ideal demand rises by roughly 9.9% per metre: approximately **0.197 kg at 5 m** and **0.263 kg at 10 m**, each including the same 20% allowance.

These are screening calculations, not qualified sizing. Depth, temperature, inflation time, buoy working pressure, relief setting, and residual fraction are unknown.

## Baseline check

Four Leland 81121 cartridges provide 48 g total. At 20 °C and 1 atm, 48 g corresponds to only about 26 L ideal free-gas volume. The baseline supplemental booster architecture is therefore material to its claimed 60 L function and cannot be discarded without a new gas budget. Its custom booster reservoirs are not selected merely because they exist.

## Compared sources

| Strategy | Candidate | Nominal gas/storage | Packaging evidence | Advantages | Major holds | Disposition |
|---|---|---:|---|---|---|---|
| Multiple small cartridges | 4 × Leland 81121 | 48 g CO2 | 18.7 mm × 82.6 mm each | Existing identity; easy replacement | Grossly short of 60 L surface ideal screen without supplemental gas | REJECT as sole source |
| Twin larger cartridges | 2 × Leland 89070 | 140 g CO2 | 30.0 mm × 205.0 mm each | Surface screening margin; dual branches; direct 1/2-20 thread family | 5 m/cold margin inadequate; 70 g inflator application approval unverified | Architecture A |
| Triple larger cartridges | 3 × Leland 89070 | 210 g CO2 | distributed 30.0 mm × 205.0 mm | Modular, no refill, branch tolerance; covers 5 m screen with modest margin; 1/2-20 | 10 m/cold may fail; simultaneous release/relief/opening shock | Architecture C selected |
| One disposable cylinder | Leland 89150 | 150 g CO2 | 50.0 mm × 188.0 mm | One orderable source; nominal surface margin | Single point; near body target; compatible piercer/flow unverified | DEFERRED |
| Refillable DOT cylinder | Swagelok 316L-HDF4-300 | 300 cm³ internal; CO2 charge TBD | 50.8 mm × 227 mm; 0.73 kg | 316L; DOT-3E catalog basis; CAD/drawing offered | Approved fill mass, valve protection, recharge process, 53 mm integration | Architecture B |
| Complete marine module | Halkey-Roberts Alpha/V95000XXB + cartridge | Configurable 3/8-24 or 1/2-20 | Vendor drawing/family page | Water sensing, piercer, manual backup and service parts combined | Exact suffix, rated cylinder mass, flow, pressure and CoC need vendor confirmation | A/C trigger/full-flow candidate |
| Custom booster vessel | Baseline custom tubes/reservoirs | Undefined qualified capacity | Fits legacy CAD only | Can be tailored | Major certification, NDE, proof, CoC, maintenance and lifecycle burden | REJECTED absent no-COTS proof |

## Selected pressure-source strategy

Architecture C uses **three sealed Leland 89070 70 g disposable CO2 cartridges** as independently replaceable sources, each with its own commercial piercer/inflator and check valve, combined only through catalog-rated fittings. A catalog relief device protects the low-pressure buoy side. There are **zero custom pressure vessels**. Any custom mount remains non-pressure-bearing; any unavoidable custom flow adapter must be minimized, proof-tested, and treated as a custom pressure boundary rather than hidden.

## Pressure gates before detailed design

1. Owner specifies maximum activation depth and allowable inflation time.
2. Buoy supplier specifies usable volume, maximum working pressure, relief requirement, inlet, and low-temperature limits.
3. Vendor confirms exact 70 g cartridge/inflator compatibility, discharge impulse, 1/2-20 thread/seal, temperature range, and lifecycle.
4. A transient/two-phase CO2 model sets cartridge count and orifice/Cv; ideal gas alone is insufficient.
5. Rated underwater tests verify cold full-charge and one-branch-out performance.
6. Relief selection and pressure-boundary test plan receive responsible pressure-system approval.

High-energy work must use rated fixtures and remote/protected operation. This trade contains no improvised pressure-test procedure.
