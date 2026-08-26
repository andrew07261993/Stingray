# STINGRAY Current State

As of: 2026-08-25.

## Current developmental CAD baseline

The newest committed local CAD baseline is the exact configuration:

`STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`

Source authority:

- path: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-25\stingray-i5-s-df8-14in-short-forward-powertrain-buoy`
- repository: `C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-22\stingray-i5-s-df8-codex-one\stingray-i5s-df8-cad`
- branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- HEAD: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- commit date: `2026-08-25T16:05:28-05:00`
- status at inventory: clean
- classification: **CURRENT DEVELOPMENTAL**

This resolves the previously abbreviated name `STINGRAY_I5S_DF8_SHORT14_FORWARD`. It is newer than Package 04, commercial-module closure, staged/distributed pressure convergence, the fixed-480 Architecture C non-pass, the forward-arm repack, targeted COTS, final detail cleanup and R2/state-parity work.

It is the current engineering CAD baseline, not a fabrication release, procurement release, qualified product or operational article.

## Exact geometry and mass

- source branch baseline: forward-arm commit `a31fce0e768f354b1831331bc2ed145223c8b2c4`
- source arm length: 733.806 mm
- current arm length: 378.206 mm
- exact arm/body reduction: 355.600 mm
- source nose-tip-to-pivot station: 480.000 mm
- current true-forward-powertrain pivot station: 355.000 mm
- actual pivot movement: 125.000 mm forward
- current rigid-body length: 1675.400 mm
- maximum rigid span: 56.500 mm, within the 57.150 mm rigid limit
- STOWED mass: 10.583165211 kg
- reserve to 18.14 kg: 7.556834789 kg
- STOWED CG: X 2.456132, Y 0.243630, Z 474.112916 mm
- STOWED radial CG: 2.468185 mm
- modeled occurrences: 180 per endpoint

The prior 480.000 mm station remains controlling for the pressure-packaging studies performed under that locked architecture. It must not be replaced by the 889 mm fallback. The later true-forward-powertrain/SHORT14 owner commission is a different, newer configuration and explicitly moved the pivot to 355.000 mm.

## Current CAD validation state

The branch reports CAD PASS for its bounded developmental gates:

- placement: PASS; 8.000 mm ballast-face-to-carrier-face transition; prohibited interval count 0;
- changed-part quality: PASS; 70 changed occurrences per endpoint and zero reported invalid/open/nonmanifold/sliver/tiny-edge/broken-fillet/blocked-Boolean defects;
- endpoint assemblies: PASS; 180 named occurrences and 180 exact solids per state, with zero reported unauthorized rigid intersections or floating/disconnected parts;
- external-pack function: CAD PASS with physical tests open;
- five-angle exact Boolean: 43,035 pairs, zero unauthorized/blocked/track/fit errors;
- full motion: one complete 0-80 degree sweep, 697,167 pairs, zero unauthorized/blocked/track/fit errors;
- dimensions/mass: PASS against the CAD inputs above;
- AP242: clean OCP/XCAF reimport, millimetres, named non-flattened hierarchy, exact BREP and zero `FACETED_BREP`.

These results apply to the exact branch/commit and do not close owner Creo, physical wet/fabric, structural, fall/orientation, vendor, procurement or qualification gates.

## Current external buoy/COTS truth

The current CAD models a custom 60 L external softgoods pack and three external inflation BUY/proxy identities:

- Leland `81121`, one 12 g CO2 cartridge;
- Halkey-Roberts `V95000XXB` / Hydro 1F, dimension-controlled commercial-interface proxy with internals not modeled;
- Halkey-Roberts `V80040` water-sensitive bobbin.

This is not an installed, orderable, qualified commercial buoy module. The `SECUMAR` 350 N pack remains an **UNCERTAIN research candidate**, not an owner-selected or implemented component. The `470-CG` / `V95000-1F` complete family was measured at 127.000 mm across and rejected for the 50.700 mm fixed-480 bore; UML MK5 and Pro Sensor Elite remain on evidence hold because controlled complete installed dimensions are missing.

`COTS_MASTER_INDEX.md` reconciles 74 exact configurations/product families across current, developmental, rejected and historical architectures.

## Context recovery completed

- two separate project authorities retained: standard cross-device ChatGPT Project `Stingray` (the pre-existing harvest) and local Work/Codex project `STINGRAY` (the newly recovered local side);
- 79 relevant Codex rollout records / 61 unique session IDs content-indexed, including 78 active-store and one archived-store record;
- 19 Git worktrees/checkouts indexed;
- all 12 shared-CAD repository branches identified as local-only because that repository has no remote;
- 110 high-value local artifacts indexed by exact path, configuration, status, size and SHA-256 without copying the large binaries into Git;
- no native Creo `.prt`/`.asm` sources found in the bounded STINGRAY search roots; AP242/STEP and inspection packages are the recoverable CAD authorities.

## Release boundary and next gate

The exact next engineering gate is owner Creo visual/mechanical inspection of the Package 05 AP242 pair, followed by physical fabric engagement/retention and wet inflation/breakaway testing. Vendor-exact complete module/interface data and procurement/receiving evidence remain separate COTS gates.

Do not call this baseline released, qualified, flight ready or operationally ready.
