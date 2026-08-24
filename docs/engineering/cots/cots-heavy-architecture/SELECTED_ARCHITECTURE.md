# Selected architecture — Architecture C source correction

## Status

Architecture C's commercial marine downstream topology is retained, but its pressure source is no longer selected.

Formal disposition: **ARCHITECTURE C PRESSURE SOURCE REQUIRES FURTHER REVISION**.

`CAD_AUTHORIZED = false`

## Retained functional path

`envelope-compliant commercial source/head [OPEN] -> water-activated Leafield GIS/servo [RETAINED] -> rated hose -> fixed-jet GIV -> 60 L STINGRAY softgood -> B10 Yellow relief`

- eurocylinder `130522277`: rejected at 82.5 mm OD.
- Hard external diameter: 57.15 mm.
- Practical cylinder-body allocation: 50.80 mm.
- Gas inventory: at least 334.51 g; preferred nominal approximately 342 g.
- Closest geometric source lead: two Leland `89200`, 400 g total; not selected because a passive Leafield-compatible armed head and exact cylinder pressure rating are not published.
- Regulator: final source-dependent; not frozen.
- Buoy: residual custom 60 L softgood; no custom pressure vessel.
- Relief: Leafield B10 Yellow basis retained.
- Functional COTS projection: unfrozen pending final source/head selection.

## Source/interface gate

Published Leafield GIS `D912202` and `D912205` valves use W28.8 x 1/14 DIN 477. Narrow candidates use 1/2-20 or 1/4 NPT. No custom HP adapter, neck modification, or unsupported outlet is permitted.

**NOT RELEASED — DO NOT PURCHASE A PRODUCTION PRESSURE SOURCE — DO NOT IMPLEMENT CAD UNTIL AN EXACT SUPPORTED SOURCE/HEAD CONFIGURATION CLOSES.**
