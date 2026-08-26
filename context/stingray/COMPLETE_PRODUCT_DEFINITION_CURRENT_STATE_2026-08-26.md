# Complete Product Definition Current State - 2026-08-26

## Controlling disposition

**MAXIMUM-COMPLETE DIGITAL DEVELOPMENT PACKAGE - NOT RELEASED FOR FABRICATION, PROCUREMENT,
QUALIFICATION, OR FIELD USE**

The dedicated branch packages the unaffected work possible from the available evidence.  Independent
package review is closed, but multiple product-release gates remain failed or not determinable.

## Source configuration

- Configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`
- Source branch: `design/df8-14in-short-forward-powertrain-external-buoy`
- Exact source/base commit: `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`
- Delivery branch: `design/stingray-complete-product-definition`
- Context authority snapshot: `engineering/stingray-context` at
  `8a63fd3c36866c1edffa245da06d8c7af2d90ee1`
- Classification: **CURRENT DEVELOPMENTAL / MAXIMUM-COMPLETE NON-RELEASE HANDOFF**

## Preserved geometry and mass

- True-forward-powertrain pivot station: 355.000 mm
- Arm length: 378.206 mm
- Rigid-body length: 1675.400 mm
- STOWED mass: 10.583165211 kg
- Reserve to 18.14 kg: 7.556834789 kg
- Named occurrences: 180 per endpoint
- Unique part definitions: 92

Frozen master SHA-256 values:

- STOWED AP242: `22342157b2ac96870bbf7cd227e729342b357fd241787be8dc03cf16a92ce7fd`
- DEPLOYED AP242: `3f33da7fc6c658c84bfad075ed9c28c9dd96087e675fc9f5d3de7562b19ee045`
- STOWED inventory: `67ae4314d128993d6ab0de761645717f704cbec47b14f33848999025a9f83765`
- DEPLOYED inventory: `7cebfb5c59d25ac148cda125ddce6094558b6fdfebc29c65f6243a1973d50498`

The separate closed STOWED and intentionally open DEPLOYED external pack states remain controlling
owner intent.  The open DEPLOYED pack is not a cleanup defect.

## Current COTS/inflation truth

The modeled custom 60 L buoy uses the Leland `81121` 12 g CO2 cartridge, a Hydro 1F / `V95000xxB`
dimension-controlled proxy, and `V80040` bobbin.  This is not a complete installed, orderable, or
application-qualified commercial module.

At 20 C and one atmosphere, the optimistic ideal-gas volume from 12 g CO2 is 6.559 L, or 10.93% of
60 L.  The ideal lower-bound CO2 mass for 60 L is 109.772 g before cooling, losses, leakage, back
pressure, or required gauge pressure.  The current inflation architecture therefore fails.

## Delivered artifact

- Archive: `STINGRAY_COMPLETE_PRODUCT_DEFINITION.zip`
- Bytes: 64,266,528
- SHA-256: `2fc9995735a6335161d18d92b32ac2ab65d517c38ed2a992e0d6ba6cb7667d49`
- ZIP members: 693
- Final manifested files: 690 plus three self-referential final manifest files
- Exact final extraction integrity: PASS, 9/9 checks, zero failures

The archive contains no released manufactured-part drawings, assembly drawings, GD&T, or qualified
work instructions because the governing requirements, tolerances, loads, allowables, and physical
evidence do not exist.  It contains explicit unreleased/prohibited registers and verification plans in
their place; those exceptions must not be treated as drawing release.
