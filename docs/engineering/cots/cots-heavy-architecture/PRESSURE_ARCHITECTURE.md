# Revised pressure architecture

## Required path

`5–7 × cartridge → V95000 puncture/inflator → individual HP check → HP collection bus → pressure regulator → fixed flow restriction → buoy-adjacent differential relief → buoy`

Preferred source pair: Leland `86202Z` 38 g + Nordson MEDICAL/Halkey-Roberts `V95000` Hydro 1F 1/2-20, **PUBLISHED CONFIGURATION SUPPORTED**.

## Pressure hierarchy

| Zone/node | Nominal | Maximum credible | Minimum useful | Required rating/control | Blocked/failure response |
|---|---|---|---|---|---|
| Stored cartridge | CO2 equilibrium at actual cartridge temperature | Supplier maximum pressure at maximum specified environment; **OPEN** | Vapor pressure sufficient to discharge at minimum temperature; **OPEN** | Commercial marked cartridge within supplier storage/discharge limits | Keep isolated until puncture; reject damaged/overtemperature article |
| Puncture/inflator | Transient cartridge pressure | Same maximum credible source pressure plus dynamic effects | Must puncture/seal/flow at cold condition | Exact approved pair, supported holder and reaction path | Each branch restrained and checked; unsupported pairs prohibited |
| Branch check/tube/fitting | Source pressure during discharge | Maximum credible source pressure at environment | Must pass required cold flow | Temperature-derated allowable above maximum credible pressure with required margin | Individual check prevents reverse discharge; blocked branch must not overload components |
| HP bus/regulator inlet | Highest active-branch source pressure | Maximum credible source pressure/common blocked transient | Above regulator control requirement | HP-rated bus and regulator inlet with controlled derating | HP relief/burst protection only if required by regulator/blocked-volume analysis |
| Regulator outlet/restrictor | Low controlled pressure | Regulator lockup/failure transient, bounded by restriction and relief | Ambient absolute + required buoy differential + losses | Qualified two-phase/cold CO2 performance; relief downstream | Relief must pass worst credible fault flow without exceeding buoy MAWP |
| Buoy inlet | Ambient at depth + line loss + operating differential | Limited below buoy MAWP | Sufficient to produce required volume/time | LP hose/fittings rated above relief envelope | Differential relief vents excess; check/regulator isolate source |
| Buoy differential | Required operating differential; **OPEN** | Buoy allowable/MAWP; **OPEN** | Shape/deployment differential; **OPEN** | Supplier operating/MAWP data | Resettable relief preferred; reject damaged buoy |
| Relief | No flow normally | Set/reseat/flow envelope below buoy MAWP and above required differential; **OPEN** | Must remain shut at required operating differential | Calibrated COTS differential behavior at depth/backpressure | Vents fault flow; setting locked and receiving-verified |

## HP design-pressure rule

The previous 2,500 psig assumption is not frozen. `≥3,000 psig` remains a screening criterion until the maximum storage/environment temperature and Leland pressure-temperature data are established.

For every HP component:

`P_allowable(T_environment) > P_max_credible_cartridge(T_environment)`

with the additional engineering/code margin selected for the controlled environment and failure consequences. Manufacturer pressure-temperature derating controls. A missing allowable, seal-temperature limit or two-phase CO2 statement is a design hold.

## Low-pressure protection and relief

The buoy cannot be connected directly to cartridge pressure. Regulator, fixed restriction and buoy-adjacent calibrated differential relief are mandatory functional layers. A buoy-integral relief may substitute only with supplier set, reseat, capacity, temperature, depth/backpressure and MAWP evidence. No numeric relief setting is selected until buoy required differential and MAWP are controlled.

## Development versus final

The complete LSC `481-CG` Type-3 article, containing `470-CG` + `#484`, tests the V95000/V80040 trigger and rearm architecture only. It does not qualify this full pressure path or final inventory. Final regulator/restrictor/relief sizing requires the owner inflation time and buoy data plus cold discharge tests at a qualified facility.
