# Pressure architecture — source correction

## Retained functional path

`commercial CO2 source/head [OPEN] -> Leafield passive water authorization/servo [RETAINED CONCEPT] -> rated HP transfer -> fixed-jet GIV -> low-pressure 60 L softgood -> B10 differential relief -> local ambient`

The downstream separation between high-pressure gas and the protected low-pressure buoy remains valid. The pressure source, source valve/head, branch count, regulator decision, HP checks, and HP bus cannot be frozen until one integrated commercial source/head passes the 50.80 mm packaging and compatibility gates.

## Pressure hierarchy

| Zone | Maximum credible | Required rating/control | Gate |
|---|---:|---|---|
| Source cylinder(s) | source density and 50/65 C developed pressure, exact configuration dependent | published cylinder WP/test/burst and temperature basis with engineering margin | **Open** |
| Source valve/head | source pressure and discharge transient | manufacturer-supported passive water-actuated configuration | **Open** |
| HP transfer | source pressure | manufacturer-assembled/rated components with documented derating | Open with source |
| Fixed-jet GIV | HP source side; low-pressure buoy side | `B9116042.2` 2.2 mm development jet; exact flow by test | Cold-depth flow qualification |
| Buoy interior | 10.0 kPa provisional operating differential | residual custom 60 L softgood; physical qualification | Physical pressure qualification |
| B10 Yellow relief | 12.1 kPa nominal; max opening 14.7 kPa plus flow accumulation | factory-set B10, -30 to +65 C; no operational plug | Relief capacity/accumulation qualification |

## Corrected HP basis

The superseded 200 bar source design basis belonged to eurocylinder `130522277` and is not a frozen Architecture C value after that source's rejection. The final HP design pressure must be re-established from the selected source's maximum credible CO2 pressure at the environmental maximum and the manufacturer's rating/derating.

Published candidate screens show why no substitute can be promoted directly:

- Leland `89200`: exact cylinder pressure/burst rating is not public; compatible `65026-18Y12` puncture device is 206 bar maximum inlet but is not a water-triggered armed inflator.
- Swagelok `316L-HDF4-300`: at 171 g in 300 ml per cylinder, NIST gives 117.80 bar absolute at 50 C versus 124 bar catalog WP, an inadequate design margin.
- Swagelok `316L-50DF4-500`: pressure rating passes, but the source fails interface and mass-reserve gates.

## Low-pressure control

The Leafield GIV/B10 basis is retained. A fixed jet limits rate but not static pressure; the B10 relief and unobstructed ambient discharge remain mandatory. The provisional downstream envelope remains:

- 10.0 kPa operating differential;
- B10 Yellow 12.1 kPa nominal;
- B10 maximum opening 14.7 kPa;
- B10 minimum sealing 10.2 kPa.

`PHYSICAL PRESSURE QUALIFICATION REQUIRED`

No CAD authority is created by retaining these downstream values.
