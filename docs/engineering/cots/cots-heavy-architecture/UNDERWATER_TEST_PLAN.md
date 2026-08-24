# Immediate underwater development test plan

## Procurement gate

Maximum three types × two articles = six total. No equipment was purchased and delivered-item CoCs accepted remain zero.

| Type | Exact article | Qty | Architecture relevance | Procurement state |
|---|---|---:|---|---|
| 1 | HIKO `87640_OLV_ONE` FLOATEK FULL TAIL, 60 L | 2 | COMMON TO TARGETED + COTS-HEAVY | RFQ after dealer authorization/traceability confirmation |
| 2 | ACE `HBD-15-25-AA-P` | 2 | COMMON TO TARGETED + COTS-HEAVY | RFQ; exact suffix orderable on request |
| 3 | LSC `481-CG` complete automatic vest with `470-CG` (HR `V95000-1F`) + `#484` 33 g | 2 | COTS-HEAVY PRIMARY | RFQ manufacturer-direct; confirm exact installed configuration |

Type 3 is **FUNCTIONAL-SCALE TEST ARTICLE — NOT REPRESENTATIVE OF FINAL GAS INVENTORY**.

## Type 1 — buoy

Questions: packed volume, extraction/unfolding, usable displaced volume, inflation geometry, leakage, attachment integrity, drying and two repack/reset cycles.

Minimum instrumentation: depth/temperature, inlet differential pressure, timer/video, buoyant-load or displaced-volume measurement and pressure-decay/leak observation.

Fixture: non-cutting pack surrogate, supplier-approved low-energy inlet and pool/open-water restraint. A qualified pressure chamber is required for depth cases beyond open-water capability. This is hydrostatic environmental testing, not pneumatic proof testing.

Provisional pass: both articles reach at least 54 L measured usable displacement and lose no more than 5% over 30 minutes at supplier-approved differential, with no seam/attachment/valve damage and two successful dry/repack cycles. Timing, depth and load gates are **PROVISIONAL — OWNER REQUIREMENT REQUIRED**.

Source status: HIKO direct shows sold out. Exact MPN inventory/add-to-cart was observed at credible EU retailers, but authorization, export availability and lot traceability are unverified. Backup is HIKO `87901_ONE` Buoyancy RF V.2 only after HIKO confirms exact identity/specification; no generic 60 L substitution is accepted.

## Type 2 — underwater damper

Questions: dry/wet force-speed behavior, 25 mm stroke, both-direction damping, adjustment stability, leakage, water ingress, corrosion, post-immersion function and reset/service behavior.

Minimum instrumentation: load cell, displacement/speed measurement, water/part temperature, cycle counter and video.

Fixture: guarded submerged linear test stand with manufacturer-required mounting and 1–1.5 mm external positive stroke stops.

Provisional pass: no binding or visible leakage; force-speed result stays within ±20% of each article's dry baseline after 10 submerged cycles and dwell; no functional corrosion; adjustment remains fixed. Final force curve, cycles, depth and dwell are **PROVISIONAL — OWNER REQUIREMENT REQUIRED**.

Evidence limit: ACE family data support 25 mm stroke, 36–800 N HBD-15 family range, -20 to 80 °C and `P` damping in both directions. No captured evidence qualifies continuous seawater immersion; that uncertainty is the test purpose.

## Type 3 — water-activated functional branch

Questions: water activation, V80040/Super Bobbin behavior, puncture, discharge initiation, achieved functional inflation, icing, leakage and published rearm/reset repeatability.

Minimum instrumentation: water/cylinder temperature sensors, timer/video and cylinder mass before/after where the controlled procedure allows. The first unmodified-system test does not add a pressure tap.

Fixture: complete unmodified manufacturer vest/bladder/mount, soft restraint in a controlled tank/pool or qualified facility, protected/remote initiation where appropriate and personnel exclusion from cylinder/projectile paths. Pressure/flow instrumentation is deferred unless LSC provides an approved interface and a qualified facility approves it. No improvised pressure apparatus is authorized.

Provisional pass: both branches successfully activate and puncture on two controlled cycles, exhibit no structural/seal failure, pass the facility-approved post-rearm leak check and are rearmed with published parts/instructions. Numeric delay/pressure/flow criteria are **PROVISIONAL — OWNER REQUIREMENT REQUIRED**.

## Safety boundary

Open-water/pool work is limited to buoy and appropriately guarded low-energy mechanical tests. Live CO2 discharge is dry-bench or water-activation work at a qualified pressure facility; mission-depth work requires a qualified chamber. Pneumatic proof/burst is outside this commission. Manufacturer limits and facility procedures control all tests.
