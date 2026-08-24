# Task state

## Terminal status

**OWNER MISSION SIZING CLOSED — ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION — CAD NOT AUTHORIZED**

## Closed this commission

- Owner basis: 5.0 m maximum depth, 0 °C minimum source/water temperature, 10 s useful-inflation time, 60 L actual usable displacement at depth and repeated fresh/salt-water marine service.
- Useful inflation: at least 54 L measured displacement at 5 m within 10 s, stable geometry and holding/increasing; full steady-state inventory remains sized to 60 L.
- Controlling 5 m/0 °C calculation: 190.06 g theoretical, 304.10 g design and 334.51 g qualification.
- Five, six and seven `86202Z` branches all fail. Nine (342 g) is the first integer count to pass both mass cases; eight fails.
- HP basis: approximately 2,624 psig maximum credible pressure at 50 °C on the documented NIST 760 kg/m³ proxy; 3,000 psig at 50 °C is the required screening/design basis pending component-specific derating acceptance.
- Type 3 remains two complete LSC `481-CG` systems with `470-CG`/HR `V95000-1F` and `#484` 33 g, functional-scale only.

## Architecture blocker

Nordson publishes `V95000 + 86202Z` as a rearm pairing for a life-vest/manifold context. The published `830011001` manifold interface has valve core, cap and O-rings; no published pressure-rated outlet supports the proposed individual HP check and collection bus. Therefore:

- pair in published PFD/manifold context: **PUBLISHED CONFIGURATION SUPPORTED**;
- STINGRAY branch feeding HP check/bus: **APPLICATION APPROVAL REQUIRED / NO PUBLISHED INTERFACE**;
- nine is the thermodynamic minimum count, not a released source architecture.

HIKO `87640_OLV_ONE` has no published operating differential, MAWP, proof/burst, relief or cycle data. No buoy operating/relief setting is authorized.

## Field reset

The service sequence remains conceptually field-resettable, but nine sources impose at least nine cartridges, nine bobbins and supplier-defined seals/pins/clips per deployment. The published source-module seal minimum is 27; an assumed two check connections per branch would raise the source/check lower bound to 45 before the common path. Final leak count cannot close until a commercial outlet/topology exists.

## Preserved controls

- Branch: `design/df8-cots-heavy-architecture`.
- Read-only CAD authority `8c594781e27b0597a71957082fb64f152cacfcd9` was not modified.
- Zero custom pressure vessels remains mandatory.
- Delivered-item CoCs accepted: zero.
- No CAD, motion, AP242, render, purchase, physical test, merge or production release was performed.
