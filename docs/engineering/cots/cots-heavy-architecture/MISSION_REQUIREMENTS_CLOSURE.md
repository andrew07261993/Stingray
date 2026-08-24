# Mission requirements closure

Status: **PRE-CAD BOUNDING COMPLETE — OWNER VALUES REMAIN REQUIRED**
Authority date: 2026-08-24

The controlled repository was searched before assigning assumptions. The final-cleanup baseline controls the 57.150 mm stowed arm-module envelope, 2032 mm rigid length, 18.14 kg ready-to-throw mass, 1.0 kg mass reserve, three-arm geometry, and provisional 0.8 kN per-arm design floor. It does not contain numeric mission values for deployment depth, minimum gas/water temperature, inflation time, buoy MAWP/relief, system recovery ultimate load, or the complete environment.

| Requirement | Classification | Closed value or bounded treatment | CAD consequence |
|---|---|---|---|
| Maximum deployment depth | OWNER DECISION REQUIRED | No controlled numeric value. Gas sizing covers 0, 3, 5, 7.5, 10 and 15 m seawater. | Architecture C cannot be frozen until an owner depth is selected. |
| Minimum gas/cartridge/water temperature | OWNER DECISION REQUIRED; PHYSICAL TEST REQUIRED | No controlled numeric value. Sensitivity cases are 25 °C warm, 15 °C nominal and 0 °C cold. | Cold discharge/icing qualification is mandatory. |
| Maximum inflation time | OWNER DECISION REQUIRED; PHYSICAL TEST REQUIRED | No controlled numeric value. Mass balance cannot establish transient flow. | Regulator/orifice/Cv and cartridge count remain provisional. |
| Required usable buoy volume at depth | CONTROLLED VALUE FOUND only as approximate baseline; OWNER DECISION REQUIRED | Approximately 60 L is controlled as a trade basis, not a certified usable volume. Calculations require 60 L at deployment depth. | Obtain supplier usable-volume and packing basis. |
| Required recovery ultimate load | OWNER DECISION REQUIRED | 0.8 kN per arm is a controlled provisional design floor, not a system ultimate recovery load. | No recovery-chain release claim. |
| Exact buoy MAWP / relief pressure | OWNER DECISION REQUIRED; PHYSICAL TEST REQUIRED | No controlled value. Relief must be selected inside the supplier MAWP/required operating differential envelope. | No relief MPN/set point can be released. |
| Environmental exposure profile | OWNER DECISION REQUIRED; PHYSICAL TEST REQUIRED | Seawater/corrosion suitability is a controlled intent; salinity, immersion duration, storage, shock, vibration, fouling and cycles are absent. | Qualification matrix remains open. |

## Derived pressure basis

Seawater ambient absolute pressure is derived as `101.325 kPa + 1025 kg/m³ × 9.80665 m/s² × depth`. A **10 kPa buoy differential** is used only as a transparent sensitivity assumption; it is not a requirement. The relief envelope is therefore expressed symbolically until the buoy supplier provides MAWP and operating differential.

## Fail-closed conclusion

Sensitivity analysis permits an engineering disposition without inventing mission values. It does not authorize CAD. The exact owner decisions are recorded in `MISSION_REQUIREMENTS_CLOSURE.csv` and `PRE_CAD_ENGINEERING_GATE.md`.
