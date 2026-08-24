# Selected architecture — Architecture C pressure source

## Status

The historical COTS-heavy trade lead remains Architecture C, but its previous three × 70 g and five-to-seven × 38 g pressure-source embodiments are superseded.

Formal disposition: **ARCHITECTURE C PRESSURE ARCHITECTURE REQUIRES REVISION**.

`CAD_AUTHORIZED = false`

## Frozen sizing result

For 5 m, 0 °C, 60 L actual displacement and the existing provisional 10 kPa buoy differential:

- theoretical minimum: 190.06 g;
- design requirement: 304.10 g;
- qualification requirement: 334.51 g;
- lowest passing `86202Z` count: **nine**, totaling **342 g**.

Five (190 g), six (228 g) and seven (266 g) fail both design and qualification. Eight (304 g) misses design by 0.10 g and qualification by 30.51 g. Nine passes design by 37.90 g and qualification by 7.49 g. This freezes the minimum thermodynamic inventory, not a CAD-released configuration.

## Rejected pressure-path embodiment

The previous path

`V95000 + 86202Z → HP check → HP bus → regulator → restriction → relief → buoy`

is not supported by the published `V95000` interface evidence. The exact cartridge/inflator rearm pairing is supported only in the manufacturer life-vest/manifold context; a rated outlet to an HP check/bus is not published. A custom adapter or pressure plenum is prohibited.

A revised Architecture C source must retain passive water authorization, commercial replaceable sources, HP/LP separation, a rated pressure-limiting stage, fixed flow bounding and buoy-adjacent differential relief—but only through documented commercial interfaces.

## Pressure and buoy holds

- HP design/screening basis: 3,000 psig at 50 °C, with each item’s allowable/MAWP and manufacturer derating verified above the approximately 2,624 psig maximum-credible source basis.
- Low-pressure operating differential, MAWP and relief envelope: **UNESTABLISHED** for HIKO `87640_OLV_ONE`; no numeric setting authorized.
- The 10 kPa differential remains a mass-sizing sensitivity only.
- Cold 5 m/10 s flow, synchronization and delivered-volume qualification remain physical tests.

## Field reset and development articles

Field reset remains feasible in principle but is high-burden at nine source modules and cannot be released until the commercial outlet, holder, seal and test instructions close. Type 3 remains two complete unmodified LSC `481-CG` systems with `470-CG` + `#484`, explicitly functional-scale and not representative of final inventory.

**NOT RELEASED — DO NOT PROCURE A PRODUCTION PRESSURE SOURCE — DO NOT IMPLEMENT CAD.**
