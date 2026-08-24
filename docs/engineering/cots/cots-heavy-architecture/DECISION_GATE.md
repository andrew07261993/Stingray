# Architecture decision gate

## Decision

**ARCHITECTURE C PRESSURE SOURCE REQUIRES FURTHER REVISION**

The 82.5 mm eurocylinder selection is rejected. The retained Leafield marine topology has no published pressure source that simultaneously fits the 50.80 mm practical cylinder allocation, supplies at least 334.51 g CO2, carries adequate pressure/temperature ratings, and connects to the passive GIS water-actuated system without an unsupported HP adapter.

## Gate state

`OWNER_MISSION_VALUES_CLOSED = true`

`QUALIFICATION_GAS_INVENTORY_G = 334.51`

`PREFERRED_NOMINAL_GAS_INVENTORY_G = 342`

`HARD_EXTERNAL_DIAMETER_MM = 57.15`

`PRACTICAL_CYLINDER_OD_ALLOCATION_MM = 50.80`

`REJECTED_CYLINDER = EUROCYLINDER 130522277 — 82.5 MM OD`

`FINAL_GAS_SOURCE_SELECTED = false`

`CLOSEST_GEOMETRIC_LEAD = 2 X LELAND 89200 — 400 G CO2`

`CLOSEST_LEAD_STATUS = NOT SELECTED — PASSIVE LEAFIELD-COMPATIBLE ACTUATION NOT PUBLISHED`

`SELECTED_MARINE_INFLATION_FAMILY = LEAFIELD GIS WATER-ACTIVATED/SERVO — RETAINED CONCEPT`

`BUOY = STINGRAY 60 L CUSTOM MARINE SOFTGOOD`

`RELIEF = LEAFIELD B10 YELLOW 1.75 PSI NOMINAL`

`CUSTOM_PRESSURE_VESSELS = 0`

`PROJECTED_FUNCTIONAL_COTS = UNFROZEN PENDING SOURCE SELECTION`

`DELIVERED_ITEM_COCS_ACCEPTED = 0`

`CAD_AUTHORIZED = false`

`PRODUCTION_PROCUREMENT_RELEASED = false`

`PRODUCT_RELEASED = false`

## Exact next action

Obtain or identify one exact manufacturer-controlled narrow marine source/head assembly meeting the inventory, 50.80 mm OD, pressure, passive-water-actuation, and no-adapter gates. Then repeat only the source-package mass/interface gate before commissioning bounded CAD.
