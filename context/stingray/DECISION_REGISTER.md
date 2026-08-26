# STINGRAY Decision Register

As of: 2026-08-25. Decisions are configuration-bound; a later owner-directed configuration may supersede an older geometry constraint without invalidating the older study's own result.

| ID | Classification | Decision / controlling interpretation |
|---|---|---|
| DEC-001 | CURRENT | Maximize genuinely orderable COTS content and minimize fabricated parts without forcing unsafe substitutions or weakening required interfaces, load paths or validation. |
| DEC-002 | CURRENT DEVELOPMENTAL | The newest engineering CAD is `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY` at commit `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`. |
| DEC-003 | CURRENT DEVELOPMENTAL | `STINGRAY_I5S_DF8_SHORT14_FORWARD` is resolved as shorthand for the exact configuration above; Package 05 is its owner-inspection package. |
| DEC-004 | CURRENT | The rigid geometry limit remains 57.150 mm. The newest CAD reports 56.500 mm maximum rigid span. External softgoods are not silently forced inside that rigid OD. |
| DEC-005 | CURRENT | Ready-to-throw mass maximum is 18.14 kg and rigid length maximum is 2032 mm unless a newer explicit owner decision changes them. Current CAD reports 10.583165211 kg and 1675.400 mm. |
| DEC-006 | CURRENT DEVELOPMENTAL | Current arms are exactly 378.206 mm pivot-to-tip, three arms at 0/120/240 degrees and approximately 80 degrees deployed. The older 733.806 mm full-length arm is historical for R2. |
| DEC-007 | CURRENT DEVELOPMENTAL | The current true-forward-powertrain pivot station is 355.000 mm, moved 125.000 mm forward from its 480.000 mm source branch. |
| DEC-008 | CURRENT | 480.000 mm remains fixed for the pressure-packaging studies commissioned under that architecture; this decision is configuration-bound. The 889 mm fallback is not a fixed-480 final. Do not use those older studies to rewrite the newer 355 mm SHORT14 configuration. |
| DEC-009 | CURRENT | ACE `GS-19-50-V4A-B8-B8` remains the primary arm actuator. Configured force is not established by a catalog maximum; supplier configuration or measured force evidence is required. |
| DEC-010 | CURRENT | ACE `HBD-15-25-AA-P` remains the direct damper; seizure remains an owner-accepted single-point deployment failure and no bypass/lost motion is required solely for seizure survival. |
| DEC-011 | CURRENT | Water is the established deployment authorization; transport/rain/spray must remain inhibited against unintended actuation. |
| DEC-012 | CURRENT | Recovery load must bypass inflator, trigger and nonstructural soft-cover interfaces unless a manufacturer supplies an explicit rated load path. |
| DEC-013 | CURRENT DEVELOPMENTAL | Current external pack is a custom 60 L softgoods definition using one Leland `81121`, a `V95000XXB` Hydro 1F dimensional proxy and `V80040`; it is not a complete commercial COTS module. |
| DEC-014 | UNCERTAIN | SECUMAR 350 N/SECUTRONIC remains a research candidate only. It is not owner-selected, implemented or dimensionally/structurally closed. |
| DEC-015 | REJECTED | The complete `470-CG` / `V95000-1F` family does not fit the fixed-480 50.700 mm bore; UML module families remain on evidence hold, not PASS. |
| DEC-016 | CURRENT DEVELOPMENTAL | The current true-forward report preserves GS-19, HBD-15 and the backup spring with their body/rod or seat senses trailing aft; the prior backup-spring question is resolved for this CAD source. |
| DEC-017 | CURRENT | Select authority by configuration, owner chronology, source path, branch/commit, manifest, hashes and validation/release classification—not by filename suffix, timestamp, slide or screenshot. |
| DEC-018 | CURRENT | Creo-facing COTS names use actual product/component name plus part number; custom parts use functional name plus material initials. |
| DEC-019 | CURRENT | Preserve historical CAD packages and dirty operator evidence. Do not reset, clean, stash, discard or overwrite occupied STINGRAY worktrees. |
| DEC-020 | CURRENT | No unsupported release language: owner Creo, physical wet/fabric/saltwater/shock/proof/vendor/procurement gates remain separate from developmental CAD PASS. |
| DEC-021 | CURRENT | The two source projects are distinct: cross-device ChatGPT Project `Stingray` is the pre-existing harvest; local Work/Codex project `STINGRAY` is the content-indexed local history. |
| DEC-022 | CURRENT | Do not duplicate large CAD/ZIP/vendor collections into Git; index exact local path, size, configuration, status and SHA-256. |

## Focused unresolved decisions

1. Owner acceptance or corrective direction after Creo inspection of the exact Package 05 AP242 pair.
2. Whether to procure/test a complete external buoy system or continue the custom 60 L pack using a vendor-approved exact inflator/manifold/cartridge interface.
3. Exact vendor-supported external-pack dimensions, mass/CG, activation/rearm configuration, ratings and structural attachment/load path.
4. Whether and where to create a recoverable remote backup of the 12 local-only CAD branches; this consolidation records SHAs but does not transfer their Git objects.
