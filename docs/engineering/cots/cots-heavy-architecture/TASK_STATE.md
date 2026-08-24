# Task state

## Terminal status

**ENVELOPE CONFLICT CORRECTED — NO SUPPORTED PRESSURE SOURCE SELECTED — CAD NOT AUTHORIZED**

## Closed this commission

- eurocylinder systems AG `130522277`, 82.5 mm OD: **REJECTED — EXCEEDS CONTROLLING DF8 DIAMETER**.
- Hard external diameter remains 57.15 mm; no body enlargement or pod is authorized.
- Practical pre-CAD cylinder-body allocation: 50.80 mm maximum after a 3.175 mm radial allowance per side.
- Owner gas case remains unchanged: 5 m, 0 C, 60 L, 10 s, at least 334.51 g qualification inventory.
- One-source Leland `89440` fails at 59.94 mm OD.
- Best geometric commercial lead is two Leland `89200` cartridges, 50.04 x 234.95 mm each, 400 g total CO2 and 0.600 kg published combined gross mass.
- The `89200` lead is not selected: no published Leafield 1/2-20 GIS cylinder valve/armed head exists, and Leland `65026-18Y12` is a manual/installation puncture device rather than a water-triggered armed inflator.
- Two Swagelok `316L-HDF4-300` cylinders fail pressure margin and Leafield interface; one `316L-50DF4-500` fails interface and 1.0 kg mass-reserve requirement.
- Retained downstream concept: Leafield GIS water authorization/servo, rated hose/GIV, B10 Yellow relief, and STINGRAY 60 L custom softgood.
- Custom pressure vessels: zero.
- Delivered-item CoCs accepted: zero.

## Engineering blocker

Published Leafield GIS standard cylinder valves `D912202` and `D912205` use W28.8 x 1/14 DIN 477. All narrow high-inventory candidates found use 1/2-20 or 1/4 NPT. No unsupported HP adapter, neck modification, or custom pressure vessel is permitted. This is a fundamental source/head compatibility gap, not a drawing-suffix or procurement-document gap.

## Preserved controls

- Branch: `design/df8-cots-heavy-architecture`.
- Read-only CAD baseline `8c594781e27b0597a71957082fb64f152cacfcd9` was not modified.
- No CAD, motion, AP242, render, purchase, physical test, RFQ, merge, or production release was performed.

## Exact next action

Identify a manufacturer-released integrated marine source/head configuration with body OD at or below 50.80 mm, at least 334.51 g CO2 in no more than three sources, published pressure/temperature ratings, passive water actuation compatible with Leafield GIS, and no custom HP adapter. Keep CAD held until that exact configuration is available.
