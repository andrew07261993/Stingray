# Mission requirements closure

Status: **OWNER MISSION VALUES CLOSED — VENDOR PRESSURE DATA AND STRUCTURAL VERIFICATION REMAIN**
Authority date: 2026-08-24

The owner has closed the mission basis needed for gas-mass sizing: 5.0 m maximum activation depth, 0 °C minimum water/cartridge/source temperature, 10 s maximum to useful inflation, 60 L actual usable buoy displacement at operating depth, and fresh/salt-water repeated-use marine exposure. These values supersede the earlier sensitivity-only status.

| Requirement | Classification | Controlled value or treatment | Remaining verification |
|---|---|---|---|
| Maximum deployment depth | CONTROLLED VALUE FOUND | 5.0 m / 16.4 ft below the water surface | Verify actual depth during qualification. |
| Minimum gas/cartridge/water temperature | CONTROLLED VALUE FOUND; PHYSICAL TEST REQUIRED | 0 °C / 32 °F | Cold-soak and discharge test at the controlling condition. |
| Maximum inflation time | CONTROLLED VALUE FOUND; PHYSICAL TEST REQUIRED | 10.0 s from water activation to useful inflation | Demonstrate the measurable threshold below. |
| Required usable buoy volume | CONTROLLED VALUE FOUND; PHYSICAL TEST REQUIRED | 60 L actual displaced volume at 5 m; rated/geometric or surface volume is not sufficient | Calibrated displaced-volume or buoyant-force measurement. |
| Recovery proof load | CONTROLLED VALUE FOUND | 500 lbf / 2,224.111 N proof-level requirement | Preserve as proof-level only. |
| Recovery design/ultimate load | STRUCTURAL VERIFICATION REQUIRED | Not established by controlled source evidence | Define governing load cases, design/ultimate criteria and factors without inventing them. This does not block pressure sizing. |
| Buoy differential/MAWP/relief | VENDOR DATA REQUIRED; PHYSICAL TEST REQUIRED | No numeric value is authorized for HIKO `87640_OLV_ONE` | Obtain supplier operating differential, MAWP, inlet and relief set/reseat/flow data or select a qualified replacement. |
| Environmental profile | CONTROLLED VALUE FOUND; PHYSICAL TEST REQUIRED | Fresh water, salt water, repeated immersion/reset/repack, 0 °C minimum, 5 m maximum depth, marine-corrosion exposure | Component-specific storage/operating limits and qualification cycles remain supplier/test controlled. |

## Useful-inflation threshold

Useful inflation is achieved when, within 10.0 s of water activation, the buoy displaces **at least 54 L at 5 m** (90% of the required 60 L), has reached its stable intended geometry, and the displacement is holding or increasing without structural leakage. Measure displacement directly or infer it from calibrated in-water buoyant force corrected for measured water density. Visual fullness, rated capacity and surface volume do not satisfy this threshold.

The steady-state gas-inventory criterion remains **60 L actual usable displacement at 5 m**. The 54 L threshold defines transient usefulness; it does not reduce the inventory requirement.

## Derived sizing basis

Using the controlled seawater sizing density of 1,025 kg/m³, ambient absolute pressure at 5 m is 151.58 kPa. The existing 10 kPa differential remains a **provisional sizing sensitivity**, producing 161.58 kPa absolute buoy pressure. Because HIKO has not published an allowable differential, this assumption may size gas inventory but cannot set a regulator or relief.

## Recovery-load reconciliation

The WP02 500 lbf row is a development screen, not an approved design or FEA basis. Separate R2 tether/harness proof values are component/process evidence and do not establish a complete-system ultimate factor. The controlled result is therefore 500 lbf proof-level, with system design/ultimate/fatigue requirements still subject to the structural verification documented in `RECOVERY_LOAD_RECONCILIATION.md`.

## Closure conclusion

Owner mission inputs are no longer a blocker to integer gas sizing. They do not close the commercial pressure path, the 10 s transient, or the buoy pressure envelope. Those vendor/test gates control CAD authorization.
