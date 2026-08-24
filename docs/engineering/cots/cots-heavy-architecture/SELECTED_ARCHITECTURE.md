# Selected architecture — Architecture C commercial marine source

## Status

The historical Architecture C trade lead is retained, but distributed three-cartridge and nine-PFD-inflator pressure paths are superseded.

Formal disposition: **ARCHITECTURE C REQUIRES ONE REMAINING ENGINEERING INPUT**.

`CAD_AUTHORIZED = false`

## Selected source path

`water-activated Leafield GIS unit -> servo -> one 342 g CO2 cylinder -> GIS cutter/valve -> rated hose -> fixed-jet GIV -> 60 L STINGRAY softgood -> B10 Yellow relief`

- Cylinder: eurocylinder systems AG `130522277`, one 1.0 L/25E/200 bar WP/300 bar TP vessel.
- Charge: 342 g net CO2.
- Source branches: one.
- HP checks/bus/manifold: none.
- Regulator: none; Leafield fixed-jet GIV is the control element and B10 is the differential overpressure device.
- Buoy: residual custom 60 L softgood; no custom pressure vessel.
- Functional COTS projection: 18/23 = 78.26%.

## Frozen sizing and pressure hierarchy

- 5 m/0 C design requirement 304.10 g; qualification 334.51 g; 342 g passes both.
- At 342 kg/m3, NIST pressure is 96.215 bar absolute at 50 C and 113.58 bar absolute at 65 C.
- Cylinder boundary: 200 bar working, 300 bar test.
- Leafield valve/outlet/hose: at least 250 bar MWP.
- Buoy operating differential: provisional 10.0 kPa.
- Relief: B10 Yellow, 12.1 kPa nominal, 14.7 kPa maximum opening and 10.2 kPa minimum sealing.

## Remaining input and release boundary

Before CAD, obtain the drawing-controlled exact-MPN Leafield configured assembly for water actuator, servo, D91-220 25E valve and hose/outlet, including dimensions, mass and keep-out. Physical 0 C/5 m/10 s flow, relief accumulation, softgood pressure/leak/cycle and marine-reset testing remain required before release.

**NOT RELEASED — DO NOT PURCHASE A PRODUCTION PRESSURE SOURCE — DO NOT IMPLEMENT CAD UNTIL THE CONFIGURED DRAWING INPUT CLOSES.**
