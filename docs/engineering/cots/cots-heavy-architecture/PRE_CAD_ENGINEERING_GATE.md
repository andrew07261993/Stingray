# Pre-CAD engineering gate — owner mission closure

## Disposition

**ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION**

`CAD_AUTHORIZED = false`

## Closed

- Owner mission basis: 5 m, 0 °C, 10 s, 60 L actual usable displacement and marine repeated-use exposure.
- Useful-inflation threshold: ≥54 L measured displacement at 5 m within 10 s, stable and holding/increasing; steady-state inventory remains 60 L.
- Controlling mass: 190.06 g theoretical, 304.10 g design, 334.51 g qualification.
- Nine `86202Z` cartridges (342 g) are the first integer count passing both mass cases.
- Recovery proof-level value is 500 lbf; design/ultimate/fatigue remain separate structural verification.
- Type 3 remains unblocked at functional scale with two complete LSC `481-CG` systems.

## CAD-blocking findings

1. The exact `V95000 + 86202Z` rearm pair is published only in a life-vest/manifold context. No published pressure-rated outlet supports the proposed HP check/bus.
2. The count, inflator count, check arrangement and HP bus cannot be frozen around an undefined adapter.
3. HIKO `87640_OLV_ONE` has no published operating differential, MAWP, inlet, relief flow/set/reseat or repeated-cycle data.
4. No numeric regulator outlet or relief setting is authorized.
5. The nine-branch 0 °C/5 m/10 s transient has not been demonstrated.
6. Installed pressure-source mass and final leak-point count are unverified; the 2.489 kg value is only a procurement/shipping proxy before common hardware.

## Pressure controls retained for revision

- No direct buoy exposure to cartridge pressure.
- HP items rated/allowable at least 3,000 psig at 50 °C with manufacturer derating verified.
- Commercial regulator/pressure limitation.
- Fixed flow restriction.
- Buoy-adjacent calibrated differential relief with supplier-supported set/reseat/capacity below buoy MAWP.
- Zero custom pressure vessels, receivers or improvised adapters.

## Exact next action

Submit the focused Nordson/Leland request for a commercial rated `V95000` outlet/manifold or an approved replacement water-automatic source, and obtain HIKO pressure/cycle data or select a supplier-qualified 60 L buoy. Recalculate the count if the verified buoy differential differs from 10 kPa, then run a qualified 0 °C/5 m/10 s transient before commissioning CAD.
