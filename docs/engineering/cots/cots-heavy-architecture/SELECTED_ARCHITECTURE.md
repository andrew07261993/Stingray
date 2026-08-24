# Selected architecture — Architecture C dual-source closure

## Status

Architecture C's developmental source path is selected as two Leland `89200` cylinders with two Leland `65026-18Y12` commercial puncture heads and independent HP control paths.

Formal disposition: **C. ONE SPECIFIC MANUFACTURER INTERFACE VALUE REQUIRED BEFORE CAD**.

`CAD_AUTHORIZED = false`

## Retained functional path

`V80040 WATER AUTHORIZATION -> NON-PRESSURE DUAL RELEASE -> 2 X 89200/65026-18Y12 -> 2 X RATED HP CONTROL PATH -> LOW-PRESSURE COMMON FEED -> GIV -> 60 L STINGRAY SOFTGOOD -> B10 YELLOW`

- eurocylinder `130522277`: rejected at 82.5 mm OD.
- Hard external diameter: 57.15 mm.
- Practical cylinder-body allocation: 50.80 mm.
- Gas inventory: at least 334.51 g; preferred nominal approximately 342 g.
- Selected developmental source: two Leland `89200`, 400 g total, 65.49 g / 19.58% over qualification inventory.
- Commercial HP boundary: two Leland `65026-18Y12`, 1/2-20 to 1/8 NPT, published 206 bar maximum inlet.
- Compatibility: **COMPATIBLE WITH PUBLISHED COMMERCIAL INTERFACE**; an armed water-triggered application is not manufacturer-approved.
- Water authorization: one `V80040` bobbin in the retained custom non-pressure latch; application qualification required because Nordson limits the bobbin to Halkey-Roberts products.
- Pressure control: two independent commercial paths; exact MPN/flow remains downstream test/procurement controlled.
- Buoy: residual custom 60 L softgood; no custom pressure vessel.
- Relief: Leafield B10 Yellow basis retained.
- Functional COTS projection: unfrozen pending bounded source-interface CAD/BOM reconciliation.

## Single pre-CAD source/interface gate

Obtain the Leland drawing-controlled `89200` + `65026-18Y12` armed interface definition, including installed safe/fired overall length and puncture advance/torque/retention. No custom HP adapter, neck modification or raw-HP manifold is permitted.

**NOT RELEASED — DO NOT PURCHASE A PRODUCTION PRESSURE SOURCE — DO NOT IMPLEMENT CAD UNTIL THE ONE DRAWING-CONTROLLED ARMED INTERFACE CLOSES.**
