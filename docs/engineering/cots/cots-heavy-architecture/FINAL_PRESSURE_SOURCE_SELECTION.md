# Final pressure-source selection

## Selected architecture

**One exchangeable 1.0 L commercial cylinder charged with 342 g net CO2, actuated by a Leafield GIS water-activated/servo system.**

- Cylinder: eurocylinder systems AG `130522277`, 1.00 L, 82.5 mm diameter, 280 mm body length, 1.7 kg empty, 25E neck, 200 bar working pressure, 300 bar test pressure, EN ISO 9809-1, CE and Pi. Source: [eurocylinder product table](https://www.eurocylinders.de/en/product/).
- Charge: 342 g net CO2; charge density 342 kg/m3.
- Source gross mass before valve/head: 2.042 kg.
- Inflation system: Leafield GIS Type, water-activated unit and servo, D912101 operating head, drawing-controlled D91-220 25E/250 bar cylinder valve.
- Transfer: rated Leafield GIS hose to fixed-jet GIV; initial jet candidate `B9116042.2` (2.2 mm) is a qualification variable, not a released flow size.
- Buoy protection: Leafield B10 Yellow relief, nominal 1.75 psi, maximum opening 2.13 psi, minimum sealing 1.48 psi. Sources: [B10 product](https://www.leafieldmarine.com/pressure-relief-valves/b10-pressure-relief-valve/) and [pressure selection chart](https://www.leafieldmarine.com/wp-content/uploads/2021/06/M-08-CI-B10-03-Rev-01-B10-Customer-Pressure-Selection-Chart.pdf).
- HP checks/bus: none; single source connects through the rated marine hose/inlet topology.
- Regulator: none. The fixed-jet GIV is the commercial flow-control element; B10 provides differential overpressure protection. The 10 s requirement must be proved at full scale.

## Inventory result

The existing 5 m/0 C/60 L model is unchanged: 190.06 g theoretical, 304.10 g design, 334.51 g qualification and 342.00 g selected. Margins are +37.90 g (+12.46%) design and +7.49 g (+2.24%) qualification. The qualification multiplier already includes cold utilization, residual/unusable gas, flow/loss, leakage and model/test reserve.

## HP pressure basis

At 342 kg/m3, the NIST CO2 isochor gives 96.215 bar absolute at 50 C (about 1,381 psig) and 113.58 bar absolute at 65 C (about 1,633 psig). The selected cylinder's 200 bar working and 300 bar test ratings bound the charge; selected Leafield valve/outlet/hose components require at least 250 bar MWP. The system HP design basis is **200 bar (2,901 psi)**, with **250 bar (3,626 psi) minimum MWP** for Leafield HP transfer components. Source: [NIST CO2 fluid data](https://webbook.nist.gov/cgi/fluid.cgi?ID=C124389&Action=Page).

## Mass and packaging

- Published cylinder plus charge: 2.042 kg and 82.5 mm x 280 mm body envelope.
- Complete pressure-system estimate: **4.3 kg**, comprising the published source plus a 2.258 kg engineering allowance for valve/head, water actuator, servo, rated hose, GIV, B10, guards and non-pressure mounts.
- Replacing the prior 2.489 kg nine-source proxy in the 14.0 kg Architecture C estimate gives about **15.81 kg ready-to-throw**, leaving about **2.33 kg** to the 18.14 kg maximum. Exact configured Leafield mass and CAD roll-up remain required.

The 82.5 mm cylinder diameter exceeds the controlled 53 mm normal-body target (which is a target, not an absolute maximum). It therefore requires a localized source bay/pod or other bounded packaging allocation. The selected pressure source is not claimed to fit the current CAD; that question is the purpose of the next bounded CAD commission after the Leafield head/servo envelope is supplied.

## Commercial cylinder screening (five maximum)

| Source | Inventory/capability | Published envelope/mass | Interface/rating | Result |
|---|---|---|---|---|
| eurocylinder `130522277`, 1.0 L | 342 g at 342 kg/m3 | 82.5 x 280 mm; 1.7 kg empty | 25E; 200 bar WP/300 bar TP | **SELECTED; smallest published 25E candidate found** |
| eurocylinder `130521790`, 1.5 L | 342 g at 228 kg/m3 | 100 x 280 mm; 2.2 kg empty | 25E; 200/300 bar | Reject: larger/heavier without mission benefit |
| eurocylinder `130521725`, 2.0 L | 342 g at 171 kg/m3 | 114.3 x 285 mm; 2.6 kg empty | 25E; 200/300 bar | Reject: larger/heavier |
| Leafield GIS 6.7 L cylinder | 342 g underfill | 140 x 560 mm; 7.0 kg empty | 25E; 300 bar test | Reject: published GIS identity but mass/envelope fail |
| Swagelok `316L-HDF4-500`, 0.5 L | 342 g at 684 kg/m3 | 50.8 x 351 mm; 1.2 kg | 1/4 FNPT; 1,800 psig WP | Reject: NIST gives about 144 bar absolute/2,074 psig at 50 C, above WP, and no Leafield valve topology |

## Final pressure/buoy combinations (three maximum)

| ID | Combination | Sources / gas | Pressure-system mass | Valves / HP seals / leak points | Reset | Custom pressure items | COTS | Packaging / qualification | Result |
|---|---|---:|---:|---:|---|---|---:|---|---|
| F1 | eurocylinder 1.0 L + Leafield GIS water/servo + STINGRAY 60 L + GIV/B10 | 1 / 342 g | 4.3 kg estimate | 3 principal valves / 8 HP seals / 10 total leak points | exchange one charged module; replace trigger consumable; repack | zero vessels/manifolds/adapters; one custom softgood | 18/23 = 78.26% | 82.5 mm source needs bounded allocation; full cold-depth and softgood qualification | **SELECTED** |
| F2 | Leafield 6.7 L GIS cylinder + same custom buoy | 1 / 342 g | about 9.3 kg estimate | 3 / 8 / 10 | same, but heavy module | zero pressure items; one custom softgood | 18/23 = 78.26% | 140 x 560 mm source and projected ready mass exceed project basis | REJECT |
| F3 | eurocylinder 1.5 L + Leafield GIS + Subsalve EFB-200 | 1 / about 544 g | about 5.0 kg source system; plus 5.4 kg buoy | 3 / 8 / 10 | exchange module; commercial buoy reset | zero custom pressure items/manifolds | projected 19/23 = 82.61% | 97.6 L buoy, 0.38 x 0.28 x 0.18 m packed; gas/mass/volume burden | REJECT |

Leak-point estimate for F1 includes cylinder neck, diaphragm/seat, penetrator seal, head flange, two servo-hose ends, valve-to-HP-hose, hose-to-GIV, GIV-to-softgood and B10-to-softgood. The exact drawing may change this count; ten is the current conservative architecture estimate.

The architecture is selected. CAD remains held only for the exact Leafield configured-assembly drawing package.
