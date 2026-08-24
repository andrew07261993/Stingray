# Architecture decision gate

## Decision

**C — ONE DRAWING/DIMENSION SET REQUIRED**

`SELECTED_SOURCE = 2 X LELAND 89200`

`SELECTED_PUNCTURE_HEAD = 2 X LELAND 65026-18Y12`

`SELECTED_MOUNTING = 2 X 65027 + 2 X 65028`

`NOMINAL_CO2_G = 400`

`QUALIFICATION_REQUIREMENT_G = 334.51`

`HARD_EXTERNAL_DIAMETER_MM = 57.15`

`PRACTICAL_CYLINDER_OD_ALLOCATION_MM = 50.80`

`PUBLISHED_CYLINDER_OD_MM = 50.038`

`PUBLISHED_CYLINDER_LENGTH_MM_EACH = 234.95`

`AVAILABLE_OPERATING_CORRIDOR_MM = 545.0`

`SAFE_ARMED_MODULE_LENGTH_MM = UNKNOWN`

`FIRED_MODULE_LENGTH_MM = UNKNOWN`

`TWO_MODULE_OPERATING_PACKAGE_MM = UNKNOWN`

`CLEARANCE_OR_OVERRUN_MM = NOT DETERMINABLE`

`SERVICE_ENVELOPE = OPEN-CLOSURE AXIAL WITHDRAWAL ACCEPTABLE IN PRINCIPLE; GEOMETRY UNVERIFIED`

`CUSTOM_PRESSURE_VESSELS = 0`

`CUSTOM_HP_ADAPTERS = 0`

`INQUIRY_SENT = true`

`CAD_AUTHORIZED = false`

`PRODUCT_RELEASED = false`

## Exact single missing manufacturer dimension set

Controlled `89200 + 65026-18Y12 + 65027 + 65028` assembly geometry giving `89200` neck/seat/shoulder datums; exact head insertion/engagement; SAFE/ARMED and FIRED installed lengths; puncture travel; operating, outlet, and removal keep-outs; and bracket/nut retention envelope, with drawing/model number and revision.

## Exact next action

Use Leland's response to calculate the two-module operating package. Issue A for `<= 545.0 mm` or B with the exact overrun for `> 545.0 mm`; do not begin CAD before that decision.
