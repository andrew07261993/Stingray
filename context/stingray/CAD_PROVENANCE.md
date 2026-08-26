# STINGRAY CAD Provenance

As of 2026-08-25.

## Preserved GitHub inspection checkpoint

Source branch:

`cad/df8-owner-creo-inspection-zips`

This branch is a preserved owner-inspection checkpoint. Do not modify the existing CAD package directories.

Packages present:

1. `01_FORWARD_ARM_480MM`
2. `02_ARCH_C_FORWARD_PACKED`
3. `03_ARCH_C_889MM_FALLBACK`
4. `04_14IN_SHORT_ARM_EXTERNAL_BUOY`
5. `05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY`

Package 05 is explicitly identified in its README as the most-forward arm-powertrain / compact-body developmental variant currently completed on that checkpoint.

## Package 05 known provenance

Source branch:

`design/df8-14in-short-forward-powertrain-external-buoy`

Recorded completed commits:

- `a55e925db67b2720c98af5e7694c16c142a07144`
- `59db97570d175adff550e1cd25451708ea3e114a`
- `0f5be86cc42147cf7f9dc502c2f562d86811b206`
- `66ee53955d3ce7945e12949ecbc3e99d591fd5b1`
- `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`

Package ZIP SHA-256:

`4d124b4bb410689071545a41c9c17c31e9393eadbf41ae6a800c5cd458b52a6c`

STOWED AP242 SHA-256:

`87a6d6f2f234fe955ef6a87aa9f7ac242d28ee10e23b9b60aca94e90e68a02c0`

DEPLOYED AP242 SHA-256:

`fbb716986ce6913715a78468b29fec8ae0a1eb45f64b9a6f825407655d68d1de`

Status: developmental engineering inspection model; not formal release CAD.

## Validated R2/state-parity source

Previously identified authoritative local source:

`C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-state-parity`

Reference branch:

`audit/state-parity-provenance`

Reference commit:

`61a58cbbccd0aae7a747b2a73046142cf1f44511`

Later audit result: 279/279 occurrences passing after validator correction. This is a strong validation/provenance baseline but should not be assumed to contain the latest shortened/external-buoy geometry.

## Targeted COTS work

Documentation branch:

`design/df8-targeted-cots-retrofit`

Known documentation commit:

`c345782ea3a733ac8338fbd7f206001a18b6f8a8`

Reported status: Phase 1 only / not released; next work was Phase 2.

Earlier baseline documentation commit used for the COTS retrofit:

`95766a1bfc7bcc48416b83c7b25fcbd482ac0608`

## Later staged-inflation development

Local branch reported:

`design/df8-final-staged-inflation-convergence`

HEAD:

`dce7a53643a35d80f5cd6f63f09852ab565a4165`

Status reported: Path B / measured non-pass.

Treat as developmental evidence until local inspection establishes its relationship to the current shortened/external-pack architecture.

## Latest shown physical model — unresolved local provenance

Name reported in the latest ChatGPT review:

`STINGRAY_I5S_DF8_SHORT14_FORWARD`

Reported characteristics:

- shortened approximately 14-in-class arms;
- arm/deployment assembly shifted forward;
- external orange buoy pack;
- newer geometrically than the validated R2 baseline.

The exact source repository, branch, commit, hashes and validation state were not available to this ChatGPT-side harvest. Codex Desktop must resolve these from ANDREWSPC before this model is treated as the definitive current CAD authority.

## Provenance rule

Never select CAD authority because a filename has the highest suffix or latest visible timestamp. Inspect configuration ID, branch/commit, internal manifest, hash record, owner decisions, release classification and actual contents.