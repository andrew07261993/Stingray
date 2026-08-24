# Architecture decision gate

## Decision

**ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION**

Architecture C remains the COTS-heavy trade lead, but its current distributed Hydro 1F-to-HP-bus embodiment is rejected for CAD because the rated outlet is not published and the 60 L buoy pressure envelope is absent.

## Gate state

`OWNER_MISSION_VALUES_CLOSED = true`

`THERMODYNAMIC_INVENTORY_FROZEN_G = 342`

`THERMODYNAMIC_CARTRIDGE_COUNT_86202Z = 9`

`FINAL_PHYSICAL_CARTRIDGE_COUNT_RELEASED = false`

`PAIR_CLASSIFICATION = PUBLISHED CONFIGURATION SUPPORTED IN PFD/MANIFOLD CONTEXT`

`STINGRAY_HP_BRANCH_CLASSIFICATION = APPLICATION APPROVAL REQUIRED / NO PUBLISHED INTERFACE`

`HP_COMPONENT_BASIS = 3000 PSIG AT 50 DEG C`

`BUOY_OPERATING_AND_RELIEF_ENVELOPE = UNESTABLISHED`

`TYPE_3_FUNCTIONAL_SCALE_UNBLOCKED = true`

`TOTAL_TEST_ARTICLES = 6`

`DELIVERED_ITEM_COCS_ACCEPTED = 0`

`CAD_AUTHORIZED = false`

`PRODUCTION_PROCUREMENT_RELEASED = false`

`PRODUCT_RELEASED = false`

## Exact next action

Issue the focused manufacturer application request for a rated water-automatic source outlet/topology and the HIKO pressure/cycle data request; select a supported replacement buoy if HIKO cannot respond. Re-run sizing for the verified differential and qualify 0 °C/5 m/10 s behavior before any CAD commission.
