# CO2 gas sizing analysis

Status: **ENGINEERING SENSITIVITY — NOT A QUALIFIED TRANSIENT MODEL**

## Method and assumptions

The required low-pressure CO2 gas state was calculated with the Peng–Robinson equation of state, not an ideal-only surface conversion. Inputs are 60.0 L usable volume **at deployment depth**, 101.325 kPa atmosphere, 1025 kg/m³ seawater, 9.80665 m/s² gravity, and a provisional 10 kPa buoy differential. Low-pressure compressibility factors range from 0.981 to 0.994 in the evaluated cases, so real-gas correction is small but retained.

The strict theoretical lower bound with zero buoy differential ranges from 108.5 g (25 °C, surface) to 298.5 g (0 °C, 15 m). The CSV uses the more useful 10 kPa differential sensitivity; its theoretical range is 119.3–310.6 g.

| Scenario | Temperature | Discharge utilization | Leakage/flow/reserve adder | Design multiplier | Qualification multiplier |
|---|---:|---:|---:|---:|---:|
| Warm | 25 °C | 0.92 | 10% | 1.196 × theoretical | 1.316 × theoretical |
| Nominal | 15 °C | 0.85 | 15% | 1.353 × theoretical | 1.488 × theoretical |
| Cold | 0 °C | 0.75 | 20% | 1.600 × theoretical | 1.760 × theoretical |

Discharge utilization bounds residual/unusable gas, flashing, line/check/regulator losses and cold/icing loss. The reserve adder bounds leakage, dead volume and rate uncertainty. Qualification adds 10% model/test margin. These are declared assumptions, not hidden requirements; transient tests must replace them.

## Inventory result

| Inventory | Result |
|---|---|
| 2 × 70 g = 140 g | Fails even warm surface design with the provisional 10 kPa differential. |
| 3 × 70 g = 210 g | Passes warm design through 5.18 m, nominal design through 2.82 m, and cold design only through 0.07 m. Qualification limits are 3.72 m warm, 1.56 m nominal, and **not supported at the cold surface case**. |
| 4 × 70 g = 280 g | Passes warm qualification through 7.5 m, nominal qualification through 5 m, and cold qualification only below about 2.3 m; it still fails 10 m qualification in every evaluated temperature. |

At the specified grid points, 3 × 70 g passes warm design at 0, 3 and 5 m but fails warm qualification at 5 m; passes nominal design/qualification at the surface but fails at 3 m; and passes cold design only at the surface by 1.25 g while failing cold qualification there.

## Cartridge-count recommendation

Three cartridges are **not retained as a general mission solution**. No fixed release count can be selected without owner depth, minimum temperature, usable volume, differential pressure and inflation time. For the next architecture trade/CAD packaging study, reserve space and interfaces for **at least four 70 g-class sources**, but do not label four sufficient: cold/deep cases require five to eight cartridges on mass alone (before packaging and flow gates). At 10 m the qualification demand is approximately 300 g warm, 352 g nominal and 440 g cold, equivalent to 5, 6 and 7 nominal 70 g cartridges after rounding up.

## What mass sizing does not close

Mass sufficiency does not establish inflation time. Liquid/vapor behavior inside the cartridge, two-phase flashing, regulator droop, check/orifice Cv, line heat transfer, dry ice/icing, simultaneous branch discharge and relief accumulation require instrumented cold discharge. CO2 dissolution in water is not credited as useful gas and any contact loss is inside the utilization factors. Full-volume ascent also requires controlled venting because ambient pressure falls.

CO2 storage-pressure references are separated in `PRESSURE_ARCHITECTURE.md`. NIST is the thermophysical source: [NIST CO2 data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C124389&Mask=4) and [NIST vapor-pressure publication](https://nvlpubs.nist.gov/nistpubs/jres/10/jresv10n3p381_A2b.pdf).
