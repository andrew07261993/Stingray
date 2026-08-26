# STINGRAY I5-S DF8 SHORT14 True Forward-Powertrain External-Buoy Design Report

Disposition: 14-INCH SHORT-ARM / SHORT-BODY TRUE FORWARD-POWERTRAIN EXTERNAL-BUOY DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION

This report covers the developmental branch rooted at `a31fce0e768f354b1831331bc2ed145223c8b2c4`. It is not production release, procurement authority, canopy-equivalence evidence, or physical buoy-system acceptance.

## Axial architecture

The exact source `BALLAST-001` occurrence is `Forward_Ballast_W`, legacy/source definition `DF8-R2-BALLAST-001`, tungsten heavy alloy, exact source mass 4.884227629 kg. Its geometry defines `FORWARD_BALLAST_AFT_FACE` at nose station Z=336.000 mm. No screenshot inference was used.

The final axial order is penetrator → forward ballast → 8.000 mm structural transition → arm carrier/roots at Z=344.000 mm → pivot axes at Z=355.000 mm → crosshead/links → aft-extending GS-19/HBD-15/backup spring → shortened aft body → external Cordura buoy pack. No unrelated cylinder, valve, route ring, service bulkhead, or empty preservation bay occupies the ballast-to-carrier interval.

| Datum | Exact value |
|---|---:|
| Nose tip to forward-ballast aft face | 336.000 mm |
| Ballast aft face to carrier forward face | 8.000 mm |
| Ballast aft face to pivot axis | 19.000 mm |
| Baseline nose tip to pivot | 480.000 mm |
| New nose tip to pivot | 355.000 mm |
| Actual carrier/pivot forward movement | 125.000 mm |

The carrier retains double-shear source lug geometry and is tied into a machined transition ring with six occurrence-matched lands, body shell continuity, fixed sectors/longerons, modeled retention, and motion corridors verified by the independent 1° exact-Boolean sweep.

## Arm, body, and removed architecture

All three arms measure 378.206 mm pivot-to-tip versus 733.806 mm source length. The rigid body measures 1675.400 mm versus 2031.000 mm, an exact 355.600 mm reduction. The aft stack is physically rebuilt; it is not an OML crop and contains no unused 355.6 mm void.

The deletion register contains 157 source occurrences / 79 unique definitions, with zero residual occurrences in the final BOM, tree, attachment map, or validation register. The dedicated follower/sleeve/spring/door ejector subset contains 42 occurrences / 19 unique definitions and 0.349617 kg source mass. The complete removed internal buoy inflation/ejection/recovery/route architecture accounts for 145 occurrences and 1.645191 kg.

GS-19 and HBD-15 preserve their fixed-body/moving-rod sense and trail aft from the forward carrier. HBD damping direction is unchanged. The backup spring preserves moving/fixed seat sense and trails aft with its guide. The four internal Leland cartridges and three booster reservoirs are removed; no legacy Category-C cylinder remains. One new Leland 81121 cartridge is mounted externally aft on the buoy inflation module.

## External pack, recovery path, and function

The pack has 41 registered pack/inflation/tether/collar occurrences and 91 softgoods-related modeled connections. Automatic water access, external manual pull access, lanyard travel, peel direction, deployed buoy clearance, tether exit, and pack retention pass CAD geometry inspection. Wet actuation, wet peel force, finished-article inflation, proof load, gloved pull, snag, leak, and repack testing remain physical gates.

## Exact mass properties

Ready-to-throw STOWED mass is 10.583165211 kg with 7.556834789 kg reserve to 18.14 kg. STOWED CG is X=2.456132, Y=0.243630, Z=474.112916 mm; radial CG is 2.468185 mm. Principal moments are 5957.306829, 2305090.219875, 2306239.115386 kg·mm². DEPLOYED mass is 10.583165211 kg and CG is X=9.210465, Y=-0.217862, Z=494.878511 mm.

QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM

## Validation

| Gate | Result |
|---|---|
| Placement | PASS — carrier face 8.000 mm aft of exact ballast face; no prohibited interval hardware |
| Changed-part quality | PASS — 70 changed occurrences per endpoint; zero invalid, disconnected, open, nonmanifold, sliver, tiny-edge, broken-radius/fillet, or blocked-Boolean defects |
| STOWED endpoint | PASS — 180/180 named occurrences, 180 exact solids, zero invalid, zero FACETED_BREP, zero unauthorized intersections, zero floating/disconnected parts |
| DEPLOYED endpoint | PASS — 180/180 named occurrences, 180 exact solids, zero invalid, zero FACETED_BREP, zero unauthorized intersections, zero floating/disconnected parts |
| Buoy-pack CAD function | PASS WITH PHYSICAL TESTS OPEN — water path, pull path, flap direction, clearance, tether, and retention modeled |
| Five-angle exact Boolean | PASS — 43,035 pairs, zero unauthorized, zero blocked, zero track/fit errors |
| Full 0–80° exact Boolean | PASS — 697,167 pairs, zero unauthorized, zero blocked, zero track/fit errors; one complete sweep, second sweep unused |
| Dimensional/mass | PASS — arms/body/placement exact; maximum rigid span 56.500 mm; reserve 7.556835 kg |
| AP242 clean reimport | PASS — named non-flattened hierarchy, millimetres, exact BREP, zero faceted/tessellated rigid geometry |

The first five-angle diagnostic identified transition-ring motion contact and was preserved as failure evidence. One focused ring-corridor correction produced the accepted second five-angle PASS. The 81-state gate used four hashed contiguous shards over two bounded stages but constitutes one complete sweep; no second sweep or third pass was used.

## Open physical/downstream gates

- OWNER CREO VISUAL INSPECTION OF THE TRUE FORWARD-POWERTRAIN SHORT-BODY EXTERNAL-BUOY DF8 CAD.
- PHYSICAL FABRIC-ENGAGEMENT AND RETENTION TEST REQUIRED.
- WET INFLATION / BREAKAWAY TEST REQUIRED.
- Finished-article inflator/cartridge/buoy-volume compatibility, leak, proof-load, pull, snag, drainage, and repack tests.
- QUANTITATIVE FALL/ORIENTATION EQUIVALENCE REMAINS A SEPARATE VERIFICATION ITEM.
