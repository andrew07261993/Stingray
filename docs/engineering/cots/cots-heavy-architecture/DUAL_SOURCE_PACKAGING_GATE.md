# Dual-source packaging gate

## Controlled envelope

- DF8 hard external diameter: **57.15 mm**.
- Practical pressure-source cylinder allocation: **50.80 mm**.
- Leland `89200` catalog body diameter: **50.038 mm**.
- Diameter arithmetic: **0.762 mm total / 0.381 mm radial clearance**, before tolerance, support, and anti-chafe stack.
- Available forward pressure corridor: **545.0 mm**.
- Maximum rigid length: **2032 mm**.

The source body passes only the arithmetic diameter screen and remains tolerance-critical. No CAD was modified.

## Required axial arrangement

The frozen packaging topology is longitudinal:

`89200 + 65026-18Y12 MODULE 1 -> INTER-MODULE/OUTLET ALLOWANCE -> 89200 + 65026-18Y12 MODULE 2`

Side-by-side placement is prohibited by the DF8 diameter limit.

## Installed-length determination

The public Leland evidence does not publish the exact `89200` neck projection, usable engagement, sealing/shoulder datum, `65026-18Y12` insertion depth, SAFE/ARMED position, FIRED position, puncture travel, or outlet/bracket keep-out. Therefore:

| Packaging measure | Result |
|---|---:|
| SAFE/ARMED module length | **UNKNOWN** |
| FIRED module length | **UNKNOWN** |
| Two-module operating package | **UNKNOWN** |
| Available operating corridor | **545.0 mm** |
| Clearance or overrun | **NOT DETERMINABLE** |

The previous `560.07 mm` cylinder-plus-head arithmetic is not an installed dimension and is not evidence of a 15.07 mm overrun. It uses a different head suffix's referential exterior length, double-counts unknown cylinder/head overlap, and omits armed/fired and fitting keep-outs.

## Service envelope

**OPEN-CLOSURE AXIAL WITHDRAWAL IS AN ACCEPTABLE SERVICE BASIS, BUT ITS GEOMETRY IS NOT YET VERIFIED.**

The full removal trajectory may extend beyond the closed 545.0 mm operating corridor when an access closure is removed. The missing controlled assembly data must still identify removal direction and local disconnect/withdrawal keep-out. No field-replacement claim is based on an invented service trajectory.

## Gate result

- Diameter: **PASS — TOLERANCE-CRITICAL**.
- Inventory: **PASS**.
- Mass: **PASS BY PRE-CAD ESTIMATE**.
- Longitudinal operating fit: **C — ONE DRAWING/DIMENSION SET REQUIRED**.
- Developmental CAD: **NOT AUTHORIZED**.

The exact request and evidence trace are in `LELAND_89200_65026_INTERFACE_GATE.md`.
