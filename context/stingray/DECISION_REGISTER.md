# STINGRAY Decision Register

As of 2026-08-25. This register captures controlling or high-value decisions recovered from available ChatGPT/project/file context. Local Codex/CAD reconciliation remains required.

| ID | Status | Decision |
|---|---|---|
| DEC-001 | CURRENT | Maximize genuinely orderable COTS content and minimize fabricated parts without forcing unsafe substitutions or sacrificing required function/validation. |
| DEC-002 | CURRENT DEVELOPMENTAL | Current physical design direction uses shortened arms, a forward-shifted arm/powertrain region and an external buoyancy pack. |
| DEC-003 | CURRENT DEVELOPMENTAL | Package 05 `TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY` is the most-forward compact completed variant on the preserved GitHub inspection branch. `SHORT14_FORWARD` has been reported as the latest shown physical CAD but its exact local Git provenance must be resolved. |
| DEC-004 | CURRENT | Rigid OD hard maximum remains 57.15 mm. Do not silently apply that value to the external soft buoy pack; softgoods envelope requires its own controlled keep-out. |
| DEC-005 | CURRENT | Ready-to-throw mass hard maximum remains 18.14 kg / 40.0 lb and rigid length hard maximum remains 2032 mm unless a later explicit owner decision supersedes them. |
| DEC-006 | CURRENT | Three-arm architecture remains 0°/120°/240° and approximately 80° deployed with positive stops/locks. |
| DEC-007 | CURRENT | ACE GS-19-50-V4A-B8-B8 remains the primary arm-drive COTS component unless a later explicit architecture change proves otherwise. |
| DEC-008 | CURRENT | ACE HBD-15-25-AA-P remains the damper. No HBD bypass/lost-motion/fuse/overload-release is required solely to survive seizure. Mechanical seizure is an owner-accepted single-point deployment failure. |
| DEC-009 | CURRENT | Configured GS-19 force is not established by the vendor maximum; use supplier configuration evidence or measured force curve. Prior development force cases were 330/300/270/230 N. |
| DEC-010 | CURRENT | Water is the established deployment authorization. Transport/rain/spray must remain inhibited against unintended actuation. |
| DEC-011 | CURRENT | Recovery load must bypass nonstructural inflator/trigger/soft-cover interfaces unless a manufacturer provides an explicit rated structural load path. |
| DEC-012 | CURRENT DEVELOPMENTAL | External equipment-oriented buoyancy is preferred over recreating a completely custom bladder/inflator if a suitable COTS system can be integrated. |
| DEC-013 | CURRENT ENGINEERING RECOMMENDATION | SECUMAR 350 N Pack Buoyancy Aid with SECUTRONIC / 75 g CO2 is the primary COTS candidate for the external-buoy branch, pending exact dimensions, mass/CG, MPN, activation configuration and structural attachment evidence. |
| DEC-014 | CURRENT ENGINEERING RECOMMENDATION | Integrate a COTS buoy/inflator through a custom STINGRAY saddle/cradle and independent structural recovery tether rather than making MOLLE/breakaway cover/hook-and-loop carry the recovery load. |
| DEC-015 | CURRENT ENGINEERING RECOMMENDATION | Use approximately 115–120 mm local external softgoods keep-out only as a provisional early CAD envelope; do not freeze it until vendor data or physical measurement exists. |
| DEC-016 | SUPERSEDED FOR SHORT-ARM DEVELOPMENT / HISTORICAL R2 | Full-length arm pivot-to-tip requirement 733.806 mm / 28.89 in remains valid for the older R2 architecture but should not be reimposed on the current short-arm branch without evidence that the shortening decision was reversed. |
| DEC-017 | CURRENT | Select authoritative files/configurations by internal configuration ID, date, manifest, branch/commit, hash, release classification and owner decisions — not simply by the numerically highest visible suffix. |
| DEC-018 | CURRENT | Final Creo-facing COTS names use actual product/component name + part number; custom parts use descriptive functional name + material initials; avoid administrative DF8/work-package names in final component names. |
| DEC-019 | CURRENT | Preserve historical CAD packages unchanged. New context/engineering work must be additive on a separate branch. |
| DEC-020 | CURRENT | No unsupported release language: physical qualification, wet/fabric testing, saltwater/fouling, shock/retention, proof load and final article verification remain separate gates. |

## Known unresolved decision/provenance questions

1. Confirm exact branch/commit/source tree for `STINGRAY_I5S_DF8_SHORT14_FORWARD`.
2. Determine whether the latest short-arm/external-buoy design retains, modifies or removes the independent backup-spring requirement from the earlier 2.250-in architecture.
3. Reconcile the staged-inflation development (`design/df8-final-staged-inflation-convergence`, measured non-pass) against the later external-pack direction.
4. Confirm whether the SECUMAR recommendation has been owner-selected for CAD integration or remains the primary research candidate.
5. Confirm exact external-pack dimensional/structural data from the manufacturer before freezing the interface.