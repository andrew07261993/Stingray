# External Buoy Pack Definition

Assembly: `Aft_Buoy_Breakaway_Wrap_CORDURA`

Status: CAD FUNCTION AND ACCESS GEOMETRY PASS; PHYSICAL WET INFLATION/BREAKAWAY ACCEPTANCE OPEN.

## Measured closed and deployed envelope

| Metric | Exact CAD result |
|---|---:|
| Closed Cordura maximum OD | 98.000 mm |
| Closed pack axial length | 238.000 mm |
| Pack axial range | 1368.000–1606.000 mm |
| Forward-facing shoulder above 53.0 mm body OML | 22.500 mm radial |
| Pull-tab maximum projection beyond closed-pack radius | 38.664 mm |
| Inflator/guard maximum projection beyond closed-pack radius | 30.035 mm |
| Structural tether maximum packed radial bbox corner | 46.872 mm; within the 49.0 mm Cordura radius |
| Maximum rigid component transverse span | 56.500 mm; requirement ≤ 57.150 mm |
| Ready-to-throw total length | 1675.400 mm |
| Deployed overall axial envelope | 2173.309 mm |
| Deployed buoy proxy | 60 L, radius 242.859 mm |

Cordura and folded buoy panels are thin closed solids with controlled thickness, radiused/bound edges, seam allowances, webbing solids, hook-and-loop solids, a packed buoy envelope, and deployed buoy gores. Random wrinkles and unverified vendor internals are not modeled.

## Buoy-mounted inflation

Selected configuration: Halkey-Roberts Hydro 1F automatic/manual inflator `V95000xxB` as a dimension-controlled `_PROXY`, source-supported Leland `81121` cartridge, and source-supported `V80040` water-sensitive bobbin. The proxy preserves the commercial installation envelope and interfaces but does not invent internal geometry. Exact vendor CAD, completed order suffix, cartridge/buoy-volume compatibility, and finished-article proof remain acceptance gates.

The reinforced open-mesh water-entry window overlaps the V80040 element while the wrap is closed. The automatic element therefore has a direct modeled water path without requiring flap opening. The manual lanyard has 18.0 mm modeled slack and 25.0 mm unobstructed fired travel; its visible external tab is held by a low-force snag keeper and is outside the hook-and-loop seam.

## Peel-opening sensitivity screen

| Screen item | Provisional value |
|---|---:|
| Controlled hook-and-loop overlap | 16.0° / 13.214 mm arc |
| Active axial strip length | 214.000 mm |
| Estimated overlap area | 2827.847 mm² |
| Assumed wet peel line-load range | 1.500–3.500 N/cm; sensitivity assumption only |
| Estimated wet peel force range | 32.100–74.900 N |
| Initial projected inflation area | 6137.541 mm² |
| Provisional opening pressure range | 5.230–12.204 kPa |
| Opening-force margin | NOT CALCULABLE — no source-supported wet delivered-pressure curve is available for the packed finished assembly |

The modeled sequence is water access → automatic/manual actuation → buoy expansion → peel-dominant flap opening → buoy unfolding/inflation. Both flaps remain attached to the cradle. The pack remains attached to the two low-profile body collars. The ultimate recovery load travels through the structural hardpoint ring, retained pin/thimble, HMPE tether, and multi-gore buoy harness; it bypasses Velcro, Cordura flaps, seams, and the inflator patch.

WET INFLATION / BREAKAWAY TEST REQUIRED
