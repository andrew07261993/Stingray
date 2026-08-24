# Pressure Reservoir and Booster Trade

Status: **PROVISIONAL RESEARCH / NO PRESSURE-HARDWARE RELEASE**

Authority: final-cleanup CAD commit `8c594781e27b0597a71957082fb64f152cacfcd9`, used read-only. Owner Creo visual inspection is still required. No CAD geometry was modified.

## Separated pressure quantities

| Quantity | Current evidence | Gate consequence |
|---|---|---|
| CO2 vapor/storage pressure | Temperature dependent and distinct from vessel rating. NIST reports about 34.85 bar at 0 °C, 45.02 bar at 10 °C, 57.27 bar at 20 °C, and 72.11 bar at 30 °C for liquid CO2. | Cartridge pressure must be evaluated at minimum/maximum soak temperature and during cold discharge; it is not the downstream inflation pressure. |
| Vessel rated working pressure | Candidate-specific: 344 bar for `316L-50DF4-150`; 124 bar for `316L-HDF4-500`. | Never use rated working pressure as an assumed fill pressure without a controlled gas/fill/relief design. |
| Downstream inflation pressure | **UNVERIFIED**. It must exceed local ambient plus line, valve, and buoy cracking losses while staying within all downstream limits. | Regulator/orifice/valve sizing and cold-flow test are mandatory. |
| Maximum external water pressure | Mission depth is **UNVERIFIED**; none of the retained cylinder pages publishes an external-collapse/submersion rating. | Qualified hydrostatic chamber test and manufacturer engineering review are required. |
| Pressure losses | **UNVERIFIED** through four cartridge heads, collection manifold, check valve, full-flow valve, tubing, and buoy inlet. | Instrumented discharge testing is required before freezing storage pressure. |
| Cold-discharge pressure | **UNVERIFIED**; CO2 flashing and rapid gas expansion can reduce pressure and temperature. | Test at the lower mission temperature with pressure and temperature instrumentation. |
| Relief/set pressure | **UNVERIFIED**. Swagelok directs use of the correct gas-specific pressure-relief device under DOT/CGA requirements. | The purchase configuration must include a reviewed relief device and safe vent path. |

## Gas-inventory lower-bound calculation

The baseline uses four Leland `81121` cartridges. The manufacturer identifies each as 12 g CO2 in a 14 mL cartridge, so the total nominal CO2 inventory is 48 g.

At 20 °C and 1.0 bar absolute, using an ideal-gas screening calculation:

- CO2 amount = `48 g / 44.0095 g/mol = 1.0907 mol`;
- free-gas volume = `nRT/P = 26.57 L`;
- CO2 required for a 60 L buoy at 20 °C and 1.0 bar absolute = `108.35 g`;
- minimum additional surface-equivalent gas = `33.43 L` or `60.35 g CO2-equivalent`.

This is only a lower bound. It excludes buoy overpressure, reserve gas, line dead volume, leakage, incomplete cartridge discharge, cold losses, regulator residual pressure, and mission-depth transient behavior. The exact mission depth, buoy working overpressure, inflation time, and temperature range remain **UNVERIFIED**.

For the selected lead, a 150 cm3 vessel charged with a non-liquefied gas to 344 bar gauge would contain approximately 51.75 L surface-equivalent ideal gas at 20 °C before regulator residual and real-gas corrections. Combined with the four cartridges, the screening total is approximately 78.3 L at 1 bar. This demonstrates inventory plausibility only; it does not authorize a fill pressure, gas species, or pressure assembly.

## Recommendation

Select Swagelok `316L-50DF4-150` **for qualified fit and pressure-subsystem testing only**. It is a 316L, 150 cm3, DOT-3A cylinder rated 5000 psig (344 bar), 48.2 mm OD, 203 mm long, and approximately 1.4 kg. It is preferred over `316L-HDF4-500` because it is shorter and offers higher rated pressure, not because 5000 psig is an approved DF8 charge pressure.

The recommendation remains conditional because:

1. 48.2 mm OD inside a 53 mm OML leaves only 2.4 mm nominal radial space before shell, supports, tolerances, and routing; exact fit is not established.
2. mission depth and external-collapse margin are unknown;
3. gas species, charge pressure, regulator residual, downstream pressure, and relief setting are unknown;
4. supplier CoC, material certificate, heat/serial linkage, and delivered-item documents are not verified;
5. the cylinder is not a substitute for a regulator, isolation valve, relief device, or rated distribution fittings.

If exact packaging fails, no custom pressure vessel is authorized. Escalate to an architecture trade, with the custom fabricated reservoir classified **LAST RESORT**.

## Procurement certificate hold points

Before any order, obtain a written quotation that identifies exact MPN, cylinder serial marking, DOT construction, gas compatibility, service pressure, proof/hydro record availability, relief-device configuration, material certification option, heat/lot/serial traceability, supplier CoC option, and official drawing revision. Keep status **RECEIVED-ITEM COC NOT VERIFIED** until receiving documents are physically matched to both delivered specimens.

High-energy work must be executed by a qualified pressure-system integrator using rated fixtures, shielding/remote operation as appropriate, correct relief/protection, and manufacturer limits. No improvised pressure vessel and no uncontrolled pneumatic proof test are permitted.

Sources: [Swagelok cylinder catalog](https://www.swagelok.com/downloads/webcatalogs/en/ms-01-177.pdf), [Swagelok 316L-50DF4-150 product page](https://products.swagelok.com/en/c/dot-compliant-cylinders/p/316L-50DF4-150), [Parker cylinder catalog](https://www.parker.com/literature/Literature%20Files/IPDE/cat/english/4160-SC.pdf), [HOKE 4HDY500](https://catalog.hoke.com/item/sampling-cylinders/formed-sampling-cylinders/4hdy500), [Leland 81121](https://www.lelandgas.com/product-page/81121-cartridge-small-x-xml-x-xxg-gas), [NIST CO2 vapor-pressure data](https://nvlpubs.nist.gov/nistpubs/jres/10/jresv10n3p381_A2b.pdf).
