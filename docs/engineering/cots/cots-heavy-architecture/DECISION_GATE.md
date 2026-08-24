# Architecture decision gate

## Decision

**ARCHITECTURE C PRESSURE REVISION READY FOR OWNER REQUIREMENT CLOSURE**

Architecture C remains the COTS-heavy trade lead. The pressure source is now grounded in an exact published commercial automatic configuration, but mission values still prevent final count, relief setting and CAD release.

## Gate state

`PRESSURE_SOURCE_REVISION_COMPLETE = true`

`SUPPORTED_AUTOMATIC_PAIR_EXISTS = true`

`PREFERRED_PAIR = HR V95000 1/2-20 + LELAND 86202Z 38 G`

`PAIR_CLASSIFICATION = PUBLISHED CONFIGURATION SUPPORTED`

`PREFERRED_COUNT_RANGE = 5 TO 7`

`FINAL_CARTRIDGE_COUNT_ESTABLISHED = false`

`TYPE_3_FUNCTIONAL_SCALE_UNBLOCKED = true`

`TOTAL_TEST_ARTICLES = 6`

`DELIVERED_ITEM_COCS_ACCEPTED = 0`

`CAD_AUTHORIZED = false`

`PRODUCTION_PROCUREMENT_RELEASED = false`

`PRODUCT_RELEASED = false`

## Exact next action

Issue the vendor application/RFQ package and obtain the seven owner mission values; then select the final integer count, close HP derating and LP relief/fault-flow limits, and seek an explicit pre-CAD commission. Do not start CAD or merge this draft branch.
