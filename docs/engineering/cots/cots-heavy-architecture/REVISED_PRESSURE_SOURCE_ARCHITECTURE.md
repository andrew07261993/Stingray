# Revised Architecture C pressure source

## Owner-case result

The lowest `86202Z` count satisfying the existing 5 m/0 °C/60 L design and qualification mass cases is **nine**:

`9 × 38 g = 342 g`

This is a frozen thermodynamic inventory, not a selected physical pressure-source topology.

## Published-interface finding

The earlier proposed path was:

`9 × [86202Z → V95000 → HP check] → HP bus → regulator → fixed restriction → differential relief → buoy`

Nordson’s published Hydro 1F documentation supports `V95000 + 86202Z` as a rearm configuration in a life-vest/manifold context. Its published `830011001` manifold installation uses a valve core, cap, two manifold O-rings and a cartridge gasket. No captured manufacturer drawing provides a rated threaded/tube outlet for an HP check or collection bus.

Accordingly:

- `V95000 + 86202Z` in the published PFD/manifold context: **PUBLISHED CONFIGURATION SUPPORTED**;
- the STINGRAY branch with HP check/bus: **APPLICATION APPROVAL REQUIRED / NO PUBLISHED INTERFACE**;
- the previous distributed HP-bus embodiment is rejected for CAD.

## Required revised topology

A future Architecture C revision shall use only a manufacturer-supported commercial path:

`commercial water-authorized source module(s) with rated outlet`

`→ commercial branch isolation/checks where required`

`→ rated HP collection/pressure-limiting hardware`

`→ fixed fault-flow restriction`

`→ buoy-adjacent differential relief`

`→ supplier-qualified 60 L-class buoy`

It shall remain passive, non-electrical, non-pyrotechnic, field-resettable and free of custom pressure vessels/plenums/adapters.

## Pressure boundary

The NIST isochoric proxy at 760 kg/m³ reaches approximately 2,624 psig at 50 °C. Use **3,000 psig allowable/MAWP at 50 °C** as the HP design and component-screening basis until Leland provides controlled cartridge pressure/temperature data. Every puncture device, outlet, check, tube, fitting, bus and regulator inlet must have manufacturer allowable and temperature derating at or above that basis. A nominal 3,000 psig rating at 100 °F does not close 50 °C service without derating confirmation.

## Low-pressure protection

The buoy shall never see cartridge pressure. Regulator, fixed restriction and buoy-adjacent resettable differential relief remain required functions. No numeric operating or relief setting is authorized because HIKO publishes no differential/MAWP/relief data. The 10 kPa value used in gas sizing is not a released setpoint.

## Packaging and service consequence

Nine cylinders occupy about 749.7 mL of geometric cylinder envelope before clearance. The conservative source-module procurement/shipping proxy is 2.489 kg before checks, bus, regulator, restriction, relief, holders and routing. Normal reset consumes nine cartridges, nine bobbins and all supplier-mandated seals/pins/clips. The published module seal minimum is 27. A hypothetical two connections per branch check gives at least 45 source/check interfaces before common hardware; the final leak-point count is unfreezable without the commercial outlet.

## Disposition

**ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION.** Do not create CAD around nine Hydro 1F devices or any custom adapter.
