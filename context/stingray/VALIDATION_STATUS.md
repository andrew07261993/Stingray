# STINGRAY Validation Status

As of 2026-08-25.

## R2 state parity / provenance

Resolved.

- Original mismatches: 64
- Category A: 30
- Category B: 34
- Category C: 0
- Corrected result: 279/279 occurrences passing
- Unresolved parity issues: 0

Root cause: the former validator treated serialized OCCT local-BREP bytes as geometric identity. Clean reimport demonstrated that the digest was process-unstable/non-semantic while common-volume geometry remained invariant. `validate_r2.py` was updated accordingly.

This resolution supersedes older 2026-08-23 presentation slides that still listed state parity/provenance as unresolved.

## R2 mechanical quality history

R1 was rejected for mechanical non-cohesion, including visible floating parts, impossible overlaps/interpenetrations and incomplete physical assembly representation. R2 corrective work therefore required exact STOWED/DEPLOYED AP242, reimport checks, interference classification, component attachment audits, hierarchy parity and mechanical correction.

At the later checkpoint:

- both STOWED and DEPLOYED built successfully;
- 279/279 named hierarchy leaves round-tripped;
- stowed audit reported 0 invalid solids and 0 blocked Boolean operations;
- remaining common-volume pairs had been reduced substantially and were being classified/corrected;
- no Creo-only validation was allowed to substitute for OCP/XCAF controls.

## Known physical/release gates that remain applicable unless a later test closes them

- owner visual/mechanical inspection of the exact latest CAD;
- exact final AP242 reimport of the actual controlling configuration;
- complete motion/interference validation for the latest geometry;
- no floating/missing attachments or invalid rigid interferences;
- exact final BOM/procurement workbook from the controlling model;
- actual system mass measurement/reconciliation;
- parachute/fabric penetration and deployment tests;
- wet/dry/slack/tensioned fabric interaction;
- saltwater/fouling/wear testing;
- positive lock/stop cycling;
- backup/failure-case deployment as applicable to the current architecture;
- 50-g retention/shock basis verification;
- structural proof loading;
- buoy wet inflation, breakaway/extraction and repack tests;
- actual inflator/cartridge/buoy compatibility;
- leak testing and recovery-load verification;
- final vendor identity/CoC/material evidence where required.

## WP01 historical digital acceptance

WP01 body/envelope/datums package previously reported digital PASS for its custom geometry with explicit external-evidence holds. It was not procurement released, fabrication released, test-entry ready, qualified or operationally ready.

## WP06 historical integration failure

A WP06 build attempt dated 2026-08-20 reported FAIL because no persisted integrated STOWED/DEPLOYED STEP pair was found and silent regeneration from subsystem masters was intentionally refused. Do not confuse that historical failure with later R2/state-parity results.

## Latest shortened/external-buoy geometry

Validation status must be resolved locally. The latest shown `SHORT14_FORWARD` model is not automatically covered by the R2 279/279 parity result. Reuse of R2 validation conclusions is allowed only where the exact geometry/provenance demonstrates applicability.