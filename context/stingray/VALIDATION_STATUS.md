# STINGRAY Validation Status

As of: 2026-08-25.

## Current SHORT14 true-forward-powertrain baseline

Applies only to branch `design/df8-14in-short-forward-powertrain-external-buoy`, commit `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`.

Source disposition:

**14-INCH SHORT-ARM / SHORT-BODY TRUE FORWARD-POWERTRAIN EXTERNAL-BUOY DEVELOPMENTAL CAD COMPLETE — READY FOR OWNER CREO INSPECTION**

| Gate | Source result | Evidence boundary |
|---|---|---|
| Placement | PASS | Ballast aft face Z 336.000 mm; carrier face Z 344.000 mm; pivot Z 355.000 mm; prohibited interval count 0 |
| Changed-part BREP quality | PASS | 70 changed occurrences per endpoint; zero reported invalid/open/nonmanifold/sliver/tiny-edge/broken-fillet/blocked-Boolean defects |
| STOWED endpoint | PASS | 180 named occurrences / 180 exact solids; zero reported unauthorized rigid intersections or floating/disconnected parts |
| DEPLOYED endpoint | PASS | 180 named occurrences / 180 exact solids; zero reported unauthorized rigid intersections or floating/disconnected parts |
| External-pack CAD function | CAD PASS / physical tests open | Water mesh, external pull, 18 mm slack, 25 mm travel, peel direction, deployed clearance and structural tether bypass are modeled |
| Five-angle motion | PASS | 0/20/40/55/80 degrees; 43,035 exact-Boolean pairs; zero unauthorized/blocked/track/fit errors |
| Full motion | PASS | One complete 0-80 degree, 1-degree sweep; 697,167 pairs; zero unauthorized/blocked/track/fit errors; second sweep unused |
| Dimensions / mass | PASS | 378.206 mm arms; 1675.400 mm body; 56.500 mm rigid span; 10.583165211 kg; 7.556834789 kg reserve |
| AP242 clean reimport | PASS | OCP/XCAF, millimetres, named non-flattened hierarchy, exact BREP, zero `FACETED_BREP` |

The first five-angle diagnostic failure and one focused ring-corridor correction were preserved. The accepted result is the second five-angle run. The 81-state audit used four hashed contiguous shards over two bounded stages but is one complete sweep.

## Open physical, vendor and owner gates

The CAD PASS above does not close:

- owner Creo visual/mechanical inspection of the exact two AP242 masters;
- physical fabric engagement, snag, retention and extraction;
- wet automatic activation, inflation and breakaway/peel force;
- exact inflator/cartridge/bladder-volume compatibility;
- leak, relief, structural proof-load and recovery-load tests;
- gloved manual pull force/stroke and snag retention;
- drainage, saltwater/fouling/wear, drying and repack/service cycles;
- quantitative fall/orientation equivalence;
- vendor-exact module/interface identity, ratings, application approval, CoC and receiving evidence.

Therefore fabrication release, procurement release, qualification, operational readiness and flight readiness remain **NOT ESTABLISHED**.

## COTS/application validation

The current external pack uses a custom 60 L softgoods definition and a Hydro 1F/V95000XXB dimensional proxy. It is not a complete commercial module PASS.

Fixed-480 commercial-module closure:

- UML MK5 `UMA4012/D160`: EVIDENCE HOLD; complete installed width/height/length/removal envelope and standalone support interface are unknown.
- UML Pro Sensor Elite `UMA8000-8050`: EVIDENCE HOLD; the same geometry gaps remain and the recovered certificate expired 2026-04-14.
- `470-CG` / `V95000-1F`: REJECTED for fixed-480 internal packaging; 127.000 mm installed width fails the 50.700 mm bore by 76.300 mm and the 57.150 mm rigid OD by 69.850 mm.

No complete commercial automatic module passed inventory, installed-envelope, rated-interface and application gates.

## Historical validation evidence

### R2 state parity / provenance

Resolved at commit `61a58cbbccd0aae7a747b2a73046142cf1f44511`:

- original mismatches: 64;
- Category A: 30;
- Category B: 34;
- Category C: 0;
- corrected result: 279/279 occurrences passing;
- unresolved parity issues: 0.

The root cause was a process-unstable, non-semantic serialized OCCT local-BREP digest. Common-volume geometry remained invariant on clean reimport. This is a strong historical provenance reference, but it does not validate later SHORT14 geometry.

### Forward arm

Commit `a31fce0e768f354b1831331bc2ed145223c8b2c4` passed its targeted five-angle exact Boolean and AP242/reimport checks at the 480.000 mm station. It is the source baseline for later SHORT14 work, not the newest geometry and not release acceptance.

### Pressure/inflation branches

- fixed-480 Architecture C: measured architecture non-pass; 889 mm fallback is a separate historical checkpoint;
- distributed-pressure branch `7f5d06f...`: measured non-pass;
- staged-inflation branch `dce7a536...`: thermodynamic inventory passed, but no installed branch passed the combined package/application gates;
- commercial-module branch `f8c38b16...`: terminal complete-module closure with no downstream CAD/motion/AP242 run.

### R1/WP history

R1 was rejected for mechanical non-cohesion, including floating parts, impossible overlaps/interpenetrations and incomplete assembly representation. WP01 digital acceptance and other targeted PASS records were developmental and retained external evidence holds. A 2026-08-20 WP06 failure reported no persisted integrated STOWED/DEPLOYED pair; later R2 results supersede that specific historical integration absence, not its release cautions.

## EVIDENCE HOLD rule

Uncommitted operator artifacts are hash-indexed in place but are not accepted as new authority: the dirty detached checkpoint reproduction, main/targeted validation files and final-converged 889 mm fallback. Do not clean or promote them without an explicit review/commit decision.
