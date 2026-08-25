# STINGRAY DF8 — True Forward-Powertrain / 14-Inch Short-Arm / External-Buoy Creo Inspection Model

> **THIS IS A DEVELOPMENTAL ENGINEERING INSPECTION MODEL.**
> **IT IS NOT FORMAL RELEASE CAD.**

## Status

**DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION**

## Source authority

Source branch: `design/df8-14in-short-forward-powertrain-external-buoy`

Source commits:

- `a55e925db67b2720c98af5e7694c16c142a07144`
- `59db97570d175adff550e1cd25451708ea3e114a`
- `0f5be86cc42147cf7f9dc502c2f562d86811b206`
- `66ee53955d3ce7945e12949ecbc3e99d591fd5b1`
- `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`

The individually uploaded STEP files are byte-identical copies of the completed local AP242 deliverables. No CAD geometry or STEP file was regenerated for this transfer.

## Key geometry

- Baseline nose-tip-to-arm-pivot: 480.000 mm
- New nose-tip-to-arm-pivot: 355.000 mm
- Actual arm-carrier forward movement: 125.000 mm
- Ballast aft face Z: 336.000 mm
- Carrier forward face Z: 344.000 mm
- Forward-ballast aft-face-to-pivot distance: 19.000 mm

## Arms

- Old arm length: 733.806 mm / 28.890 in
- New arm length: 378.206 mm / 14.890 in
- Exact arm reduction: 355.600 mm / 14.000 in
- Baseline deployed radial reach: 740.657838 mm
- New deployed radial reach: 390.460201 mm
- Reach reduction: 350.197637 mm / 47.281973%

## Body

- Old rigid length: 2031.000 mm
- New rigid length: 1675.400 mm / 65.961 in
- Exact body reduction: 355.600 mm / 14.000 in
- Ready-to-throw total length: 1675.400 mm

## Powertrain

- GS-19 fixed-body/moving-rod orientation retained
- GS-19 body Z: 415.000–533.000 mm
- HBD-15 fixed-body/moving-rod orientation retained
- HBD-15 body Z: 415.000–522.500 mm
- Backup spring and guide system extends aft from the new arm mechanism
- Crosshead travel: 15.055034371 mm

## Buoy/ejection architecture

- Legacy internal buoy-ejection/inflation architecture removed
- Dedicated ejector subset removed:
  - 19 definitions
  - 42 occurrences
  - 0.349617 kg
- Complete removed internal buoy inflation/ejection/recovery/route architecture:
  - 71 definitions
  - 145 occurrences
  - 1.645191 kg
- All deleted-source register:
  - 79 definitions
  - 157 occurrences
  - 2.801502 kg
  - Zero residuals

## External buoy pack

- Closed Cordura wrap OD: 98.000 mm
- Pull-tab maximum projection: 38.664 mm beyond 49.000 mm pack radius
- Inflator-guard maximum projection: 30.035 mm beyond 49.000 mm pack radius
- External aft Leland 81121 cartridge: Z=1384.000–1467.000 mm
- Hydro 1F inflator proxy: Z=1465.000–1512.000 mm

## Inflation subsystem

- Halkey-Roberts Hydro 1F automatic/manual inflator
- `V95000xxB_PROXY`
- V80040 water-sensitive bobbin
- Leland 81121 cartridge
- Commercial interfaces preserved
- Unavailable proprietary internals not invented

## Pack functional results

- Automatic water access while packed: CAD PASS
- Four independent mesh water paths
- Manual pull access: CAD PASS
- Visible snag-kept tab
- 18.0 mm modeled slack
- 25.0 mm unobstructed fired travel
- Pack-opening geometry: CAD PASS
- Provisional opening-pressure screen: 5.230–12.204 kPa
- **Physical wet inflation/breakaway testing remains mandatory.**

## Mass properties

- STOWED mass: 10.583165211 kg
- Mass reserve: 7.556834789 kg
- STOWED axial CG: 474.112916 mm
- STOWED radial CG: 2.468185 mm
- STOWED X: 2.456132 mm
- STOWED Y: 0.243630 mm
- DEPLOYED axial CG: 494.878511 mm
- DEPLOYED radial CG: 9.213041 mm
- STOWED principal moments: 5957.306829, 2305090.219875, 2306239.115386 kg·mm²

**QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM.**

## CAD validation

### STOWED

- PASS
- 180/180 named occurrences
- 180 exact solids
- Invalid solids: 0
- FACETED_BREP: 0
- Unauthorized rigid intersections: 0
- Blocked Booleans: 0
- Floating/disconnected parts: 0
- Clean OCP/XCAF reimport PASS

### DEPLOYED

- PASS
- 180/180 named occurrences
- 180 exact solids
- Invalid solids: 0
- FACETED_BREP: 0
- Unauthorized rigid intersections: 0
- Blocked Booleans: 0
- Floating/disconnected parts: 0
- Clean OCP/XCAF reimport PASS

## Motion validation

### Five-angle

PASS at 0°, 20°, 40°, 55°, and 80°:

- 43,035 exact pair checks
- 0 unauthorized intersections
- 0 blocked Booleans
- 0 track/fit errors

### Full motion

- PASS
- 0°–80° at 1° increments
- 697,167 exact pair checks
- 0 unauthorized intersections
- 0 blocked Booleans
- 0 track/fit errors
- One complete sweep only

## Geometry quality

- Floating parts: 0
- Broken radii/fillets: 0
- Broken routes: 0
- Route-to-nowhere: 0

## Remaining physical-test gates

- Fabric engagement and retention
- Wet inflation/breakaway
- Finished-article inflator/cartridge/buoy-volume compatibility
- Leak testing
- Recovery proof-load
- Gloved manual pull
- Snag testing
- Drainage
- Repack testing
- Quantitative fall/orientation analysis/testing

## Downloadable files

- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_STOWED_AP242.step`
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_DEPLOYED_AP242.step`
- `STINGRAY_DF8_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY_CREO_INSPECTION.zip`
