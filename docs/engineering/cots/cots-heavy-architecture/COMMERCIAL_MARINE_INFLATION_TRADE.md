# Commercial marine inflation trade

## Decision

Select the **Leafield Marine GIS cutter-type family in its published water-activated/servo topology**, configured to fire one commercial CO2 cylinder:

`water-activated GIS unit -> servo -> D912101 GIS operating head -> D91-220 250 bar cylinder valve -> rated Leafield hose -> fixed-jet GIV -> STINGRAY 60 L softgood -> B10 Yellow differential relief`

The topology eliminates nine PFD inflators, all branch checks and the HP collection bus. It is one pressure-source branch with no custom pressure vessel, manifold or HP adapter.

Leafield publishes the original GIS as a CO2/CO2-N2/N2/air system, with a water-activated version, a servo that can fire up to four cylinders, cylinder versions up to 450 bar test pressure, internal/external source overpressure venting and ISO 15738/SOLAS/PED evidence. The current Lloyd's Register certificate `LR2557067SS` covers D91-210 operating heads, D91-220 cylinder valves and B91-160 inlet valves through 6 July 2030. Sources: [GIS product page](https://www.leafieldmarine.com/gas-inflation-systems-for-life-rafts/gas-inflation-system-gis-type/), [GIS manual LEL-20018 Rev 7b](https://www.leafieldmarine.com/wp-content/uploads/2023/12/LEL-20018-Rev-7b-INFO-ONLY-GIS-User-Manual.pdf), and [LR2557067SS](https://www.leafieldmarine.com/wp-content/uploads/2026/02/LR2557067SS-GIS-Type-Approval-expires-06Jul2030.pdf).

## Retained systems

| System | Passive water authorization | Pressure/interface evidence | Reset | Result |
|---|---|---|---|---|
| Leafield GIS water/servo | Published | Current certificate, 250 bar standard valves, rated outlet/hose/GIV | Complete module exchange in field; fired module service by qualified station | **SELECTED** |
| Leafield GIS4 | Not published | Exact 25E valve suffixes and 210/238/250/300 bar ratings; M16x1.5 outlets | Qualified service; reduced spares | Reject until water/servo compatibility is published |
| Leafield GIST | Not published | 230/250/275/300 bar variants and twin M16x1.5 outlets | Qualified service | Reject: no published passive water trigger |

## One remaining engineering input

Leafield's public material does not release the exact water-actuator/servo suffix, exact D91-220 25E valve suffix or a dimensioned installed-envelope drawing. Those comprise one drawing-controlled **configured-assembly definition**. It must identify the exact ordered part numbers, cylinder-thread variant, outlet, hose, actuation/servo interfaces, mass and keep-out envelope.

This is a fundamental dimensional/interface input for CAD, not a wait for general application advice. CoC, quote, lead time and delivered identity remain downstream procurement/receiving gates.

## Rejected embodiment

The nine `V95000 + 86202Z` arrangement remains thermodynamic evidence only. It had nine source modules, at least 27 published source seals and a hypothetical lower bound of 45 source/check interfaces before the common path. It is rejected as a physical CAD architecture.
