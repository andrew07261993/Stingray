# Dual-source pressure architecture

## Selected developmental topology

`ONE PASSIVE WATER AUTHORIZATION`

`-> NON-PRESSURE DUAL EQUALIZER / SPRING RELEASE`

`-> TWO INDEPENDENT LELAND 89200 + 65026-18Y12 MODULES`

`-> TWO COMMERCIAL 1/8-NPT RATED OUTLET/HOSE PATHS`

`-> TWO PRESSURE-CONTROL / FIXED-RESTRICTION PATHS`

`-> LOW-PRESSURE COMMON BUOY FEED`

`-> LEAFIELD B10 YELLOW DIFFERENTIAL RELIEF`

The two raw high-pressure streams do not share a manifold. Convergence occurs only after each stream is pressure-controlled. No custom pressure vessel and no custom high-pressure adapter is permitted. Standard drawing-controlled 1/8-NPT hose ends are commercial fittings, not project-designed pressure adapters.

## Module definition

Each module contains:

1. one Leland `89200`, 200 g CO2;
2. one Leland `65026-18Y12` mountable puncture device;
3. one Leland `65027` bracket and `65028` retaining nut, or the exact drawing-controlled `18Y12` mounting kit;
4. one commercial, pressure-rated 1/8-NPT hose/fitting outlet;
5. one independent pressure-control and fixed-restriction path;
6. low-pressure connection to a common 60 L softgood inlet volume.

`65026` is a puncture boundary, not a regulator and not a valve. A blocked outlet can expose the complete upstream branch to source pressure; every item through the pressure-control inlet must therefore be rated for the maximum credible source condition. The existing 3,000 psig screen is not a final rating because the exact `89200` allowable pressure/temperature curve is not public.

## Inventory and firing

- Nominal inventory: 2 x 200 g = **400 g CO2**.
- Qualification requirement: **334.51 g**.
- Excess: **65.49 g**, or **19.58%** of the qualification requirement.
- One source alone is short by 134.51 g; both are required on every deployment.
- Simultaneous release is selected. Sequential release adds delay and a single-source transient while providing no mission reserve, because neither source can independently meet qualification inventory.
- The 65.49 g difference is the maximum aggregate additional nondelivered inventory before falling below 334.51 g; it is not a new qualification allowance and shall not be double-counted.

## Pressure hierarchy

| Node | Pressure basis | Protection / status |
|---|---|---|
| `89200` source | CO2 equilibrium/developed pressure over the controlled temperature range | Exact allowable working, proof and burst values required before pressure test/release |
| `65026-18Y12` inlet/body | Published maximum inlet 206 bar / 3,000 psi | Commercial HP boundary; exact temperature derating not public |
| 1/8-NPT outlet and branch hose | Maximum credible source pressure including blocked outlet | Commercial rated assembly only; rating frozen after exact source curve is received |
| Pressure-control inlet | Same as upstream branch | Two independent commercial devices; exact MPN/flow selected in bounded CAD/test commission |
| Restricted outlet / common feed | Controlled low pressure | No raw-HP common manifold; check/isolation downstream of control only if flow test requires it |
| 60 L softgood | Ambient plus low differential | Physical pressure qualification required |
| B10 Yellow relief | 1.75 psi nominal; max opening 2.13 psi, min sealing 1.48 psi from retained evidence | Buoy-adjacent differential relief; full dual-flow accumulation test required |

## Water authorization

The high-pressure hardware does not perform water sensing. The retained Nordson MEDICAL / Halkey-Roberts `V80040` water-sensitive bobbin releases a mechanically stored-energy, non-pressure STINGRAY latch/equalizer. The equalizer provides two positive outputs to the two cartridge advances. Nordson limits `V80040` to Halkey-Roberts products, so the retained custom-latch application is not represented as manufacturer-approved and requires physical qualification. Leafield marine GIV/B10 components remain in the low-pressure buoy architecture; a Leafield W28.8 cylinder valve is not adapted to the Leland source.

Current Leafield GIS evidence supports water activation and multi-cylinder firing as a marine topology, but does not support a 1/2-20 Leland cylinder. It is architectural precedent and downstream marine hardware evidence, not a claim that Leafield approves this HP module.

## Status

The architecture is viable for gas inventory, diameter, pressure-boundary topology, field exchange and no-custom-HP controls. Developmental CAD remains held by one manufacturer-controlled interface document: the armed `89200` + `65026-18Y12` installed/puncture definition.
