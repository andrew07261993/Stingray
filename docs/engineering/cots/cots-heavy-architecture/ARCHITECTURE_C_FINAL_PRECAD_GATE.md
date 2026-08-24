# Architecture C final pre-CAD gate

## Disposition

**ARCHITECTURE C PRESSURE SOURCE REQUIRES FURTHER REVISION**

## Corrected source state

The superseded path used eurocylinder systems AG `130522277`. Its 82.5 mm diameter violates the 57.15 mm hard external limit and it is rejected. The pressure source cannot consume the full hard envelope; the calculated practical body allocation is 50.80 mm.

The retained functional path is held at an open source node:

`commercial source/head <=50.80 mm OD [OPEN] -> Leafield GIS passive water authorization/servo [RETAINED] -> rated hose -> fixed-jet GIV -> 60 L STINGRAY softgood -> B10 Yellow relief`

## Evidence gate

Leafield's official `LEL-20018 Rev 7b` manual publishes standard GIS valves `D912202` and `D912205` with W28.8 x 1/14 DIN 477 cylinder threads and 250 bar MWP. No public 1/2-20 or 1/4 NPT GIS valve is identified.

The closest geometric source is two Leland `89200` 200 g cartridges. Both fit the 50.80 mm screen and supply 400 g, but they are not a supported final architecture because:

1. their 1/2-20 puncture interface is not a published Leafield GIS cylinder connection;
2. Leland's compatible `65026-18Y12` puncture device is not an armed water-triggered inflator;
3. exact `89200` cylinder pressure/burst values are not public;
4. connecting the systems would require an unsupported HP adapter or a new actuation mechanism.

The gap cannot be reclassified as `DRAWING-CONTROLLED FINAL MPN PENDING` because no supported interface family exists in the published evidence.

## Preserved downstream basis

- 5 m maximum depth, 0 C minimum source/water temperature, useful inflation by 10 s;
- 60 L actual displacement target;
- 334.51 g minimum qualification inventory;
- Leafield B9116042.2 development GIV and B10 Yellow relief basis;
- custom 60 L softgood, physical pressure qualification required;
- zero custom pressure vessels;
- field exchange/reset objective;
- Type 2 and functional-scale Type 3 development articles unchanged.

`CAD_AUTHORIZED = false`

`NO_VENDOR_EMAIL_WAIT = true`

## Downstream physical qualification gates

Once a source is selected and bounded CAD is separately authorized:

- full-scale 0 C, 5 m, 54 L-by-10 s and 60 L steady-volume test;
- fixed-jet selection, icing, hose reaction and B10 relief-flow/accumulation test;
- softgood leak, pressure, relief, repeated-cycle and salt-water/corrosion qualification;
- field source exchange/reset demonstration;
- separate 500 lbf recovery proof/load-path verification and unresolved design/ultimate structural requirement.

## Exact next action

Identify a manufacturer-released integrated marine source/head configuration meeting the 50.80 mm body allocation, at least 334.51 g inventory, published pressure ratings, passive Leafield-compatible water actuation, and no unsupported HP adapter. Do not start CAD.
