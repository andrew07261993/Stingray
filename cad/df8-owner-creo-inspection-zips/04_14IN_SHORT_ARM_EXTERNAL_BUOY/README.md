# STINGRAY DF8 — 14-Inch Short-Arm / External-Buoy Creo Inspection Model

> **THIS IS A DEVELOPMENTAL ENGINEERING INSPECTION MODEL.**
> **IT IS NOT FORMAL RELEASE CAD.**

## Status

**DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION**

## Source authority

Source branch: `design/df8-14in-short-arm-external-buoy-pack`

Source commits:

- `0f21a655a3a8e0f98faba950a233ee0636a7626d`
- `3ffc5c8dbc31381c2272141fa1ec827ed9532f9c`
- `34f1b9e85906cd70af42219936921b145d318315`
- `0431fe05465ba59a1714f110a07c73f146131c96`

The individually uploaded STEP files are byte-identical copies of the completed local AP242 deliverables. No CAD geometry or STEP file was regenerated for this transfer.

## Key geometry

- Baseline arm length: 733.806 mm / 28.890 in
- New arm length: 378.206 mm / 14.890 in
- Arm reduction: 355.600 mm / 14.000 in
- Deployed radial reach reduction: 350.197637 mm / 47.281973%
- Baseline rigid-body length: 2031.0000001 mm
- New rigid-body length: 1675.4000001 mm
- Body reduction: 355.600 mm / 14.000 in
- Nose-tip-to-pivot: 480.000 mm
- Rigid body OD: 57.000 mm
- Closed Cordura wrap OD: 128.000 mm
- Maximum closed external-pack envelope including accessible pull tabs: 152.400 mm
- Closed pack axial extent: 305.000 mm
- Ready-to-throw length: 1675.4000001 mm

## Buoy architecture

- Internal buoy ejector removed
- 31 unique ejector definitions removed
- 57 ejector occurrences removed
- Ejector mass removed: 0.396484760 kg
- External aft Cordura hook-and-loop breakaway pack
- UML MK5 automatic/manual inflator family
- UMA4012/D160
- Conservative proxy geometry
- Four modules
- Nominal CO2 inventory: 240 g
- Automatic water access while packed: PASS
- Manual pull access while packed: PASS
- Developmental pack peel-opening screen: PASS
- Physical wet inflation testing remains mandatory

## Mass properties

- Total mass: 13.051842931 kg
- Mass reserve: 5.088157069 kg
- Axial CG: 618.355733467 mm from nose
- Radial CG: 0.313694936 mm

## CAD validation

### STOWED

- PASS
- 336 solids
- Invalid solids: 0
- Unauthorized rigid interferences: 0
- Faceted/tessellated rigid geometry: 0

### DEPLOYED

- PASS
- 335 solids
- Invalid solids: 0
- Unauthorized rigid interferences: 0
- Faceted/tessellated rigid geometry: 0

## Motion

- Five-angle 0/20/40/55/80°: PASS
- Full 81-state 0°–80° / 1° increments: PASS
- Unauthorized rigid interference: 0
- Boolean-blocked count: 0

## Assembly quality

- Floating parts: 0
- Disconnected attachments: 0
- Broken radii/fillets: 0
- Broken routes: 0

## Download files

- `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_STOWED_AP242.step` — direct STOWED model for Creo
- `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_DEPLOYED_AP242.step` — direct DEPLOYED model for Creo
- `STINGRAY_DF8_14IN_SHORT_ARM_EXTERNAL_BUOY_CREO_INSPECTION.zip` — complete 30-entry inspection package
- `SHA256SUMS.txt` — transfer-integrity hashes

## Remaining downstream gates

- Controlled UML assembly CAD/dimensions
- Exact cylinder sub-MPN
- Holder/support geometry
- Water-entry/removal envelope
- Pull travel
- Manufacturer-compatible buoy interface
- Cordura/seam/wet hook-and-loop specifications
- Wet pack inflation/peel testing
- Gloved manual pull testing
- Fabric engagement testing
- Snag/retention/extraction testing
- Recovery proof-load testing
- Leak/function testing
- Quantitative fall/orientation analysis/testing
- Procurement
- Received-item identity
- CoC
- Incoming inspection

These downstream gates remain open. This transfer does not authorize procurement, qualification, formal release, or merge.
