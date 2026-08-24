# STINGRAY I5-S DF8 COTS-heavy architecture trade

> **2026-08-24 envelope correction:** eurocylinder `130522277` is rejected because its 82.5 mm OD exceeds the 57.15 mm hard maximum. The practical cylinder-body allocation is 50.80 mm. No published source simultaneously closes inventory, pressure margin, passive Leafield-compatible actuation, and this envelope; the closest geometric lead is two Leland `89200` cartridges but it is not selected. Current disposition is **ARCHITECTURE C PRESSURE SOURCE REQUIRES FURTHER REVISION** and CAD remains unauthorized. See `ARCHITECTURE_C_FINAL_PRECAD_GATE.md`; earlier alternatives remain historical evidence.

Status: **Phase 1–4 complete; provisional selection only; NOT RELEASED**.

This package is an independent architecture trade derived from documentation baseline `95766a1bfc7bcc48416b83c7b25fcbd482ac0608`. It was not branched from, and does not modify, `design/df8-targeted-cots-retrofit`. The read-only CAD authority is `fix/final-cad-semantic-cleanup` at `8c594781e27b0597a71957082fb64f152cacfcd9`.

The work stops at architecture selection. It creates no CAD, STEP, motion, render, presentation, or procurement-release artifact. The final-cleanup geometry still requires owner Creo visual inspection. Any changed architecture must receive new fit, pressure, environmental, physical, motion, and release validation; baseline validation is not inherited.

## Outcome

- Alternatives evaluated: 3 materially different architectures.
- Current source state: **Architecture C downstream marine topology retained; pressure source open**.
- Baseline functional COTS coverage: **10/114 = 8.77%**.
- Projected coverage: **unfrozen pending final source/head selection**; historical 18/23 = 78.26% is not carried forward as a current selected metric.
- Selected projected residual custom unique lines: **5**.
- Selected custom pressure vessels: **0**.
- Release disposition: **CAD implementation held**.

The 78.26% value is a projected architecture metric, not delivered hardware maturity. No candidate is beyond maturity level 3; CoC support, procurement evidence, delivered identity, and delivered-item CoC acceptance remain separate gates.

Maturity levels are used without skipping: `1 candidate identified`, `2 catalog identity verified`, `3 technical fit supported`, `4 CoC availability supported`, `5 procurement evidence`, `6 delivered identity verified`, and `7 delivered-item CoC accepted`. A higher level may be assigned only when all earlier levels are supported for the exact configuration.

## Reading order

1. `REQUIREMENTS_AND_CONSTRAINTS.csv` and `REQUIREMENTS_TRACEABILITY.csv`
2. `FUNCTIONAL_DECOMPOSITION.md`
3. `ARCHITECTURE_ALTERNATIVES.md` and `FUNCTIONAL_BLOCK_DIAGRAM.svg`
4. `PRESSURE_ARCHITECTURE_TRADE.md` and `FIELD_RESET_ARCHITECTURE_MATRIX.csv`
5. `ARCHITECTURE_DECISION_MATRIX.csv` and `SELECTED_ARCHITECTURE.md`
6. evidence, residual-risk, test, migration, and `DECISION_GATE.md` registers

## Governing caveat

Deployment depth, minimum gas temperature, required inflation time, allowable buoy pressure/relief setting, buoy certified capacity, recovery ultimate load, and environmental qualification profile are unsupported. They are recorded as **UNKNOWN — DESIGN GATE REQUIRED**. The selected gas charge is therefore a testable provisional configuration, not a released sizing result.
