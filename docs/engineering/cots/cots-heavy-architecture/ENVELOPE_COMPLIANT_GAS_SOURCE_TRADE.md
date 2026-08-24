# Envelope-compliant gas-source trade

## Governing screen

The controlled maximum external diameter is **57.15 mm**. The previously selected eurocylinder systems AG `130522277` is **82.5 mm OD** and is therefore:

**REJECTED — EXCEEDS CONTROLLING DF8 DIAMETER**

No body enlargement, external pod, or waiver of the 57.15 mm limit is permitted.

The pre-CAD radial allocation is:

| Radial allowance, each side | Value |
|---|---:|
| Body wall | 1.250 mm |
| Mount/support | 0.750 mm |
| Anti-chafe clearance | 0.400 mm |
| Service/removal clearance | 0.500 mm |
| Manufacturing/assembly tolerance | 0.275 mm |
| **Total each side** | **3.175 mm** |

`57.15 - 2(3.175) = 50.80 mm`

The **practical cylinder OD allocation is 50.80 mm maximum** for architecture screening. The body-wall and support values are provisional pre-CAD allocations, not authorization to modify the accepted CAD. A candidate at 50.8 mm has no extra radial contingency and still requires a drawing-controlled clearance stack during bounded CAD. Valve/head keep-out must be axial or independently fit within 57.15 mm.

## Published interface closure

Leafield's GIS manual `LEL-20018 Rev 7b` publishes only these standard cylinder valves:

- `D912202` / CV2: W28.8 x 1/14 DIN 477 cylinder thread, 0.860 x 14 TPI outlet, 250 bar MWP;
- `D912205` / CV5: W28.8 x 1/14 DIN 477 cylinder thread, G3/8 flat-seat outlet, 250 bar MWP.

The same official GIS evidence supports water activation and a servo for multiple-cylinder firing, but only through Leafield's approved GIS cylinder-valve/operating-head system. It does not publish a 1/2-20 or 1/4 NPT cylinder connection.

The narrow sources that pass OD use incompatible interfaces:

- Leland `89200` and `89150`: 1/2-20 puncture cartridge neck;
- Swagelok sample cylinders: 1/4 in female NPT ports.

Thread adapters or modifications would become unsupported high-pressure outlets. They are not selected. A drawing-controlled suffix may close dimensions for an already supported connection; it cannot turn an unpublished pressure interface into a supported one.

## Candidate result

| Candidate | Sources / gas | OD x length | Published source mass | Geometry | Pressure | Leafield actuation interface | Result |
|---|---:|---|---:|---|---|---|---|
| eurocylinder `130522277` | 1 / 342 g | 82.5 x 280 mm | 2.042 kg filled | Fail | Prior pressure case passes | 25E variant drawing open | **Rejected: hard OD** |
| Leland `89440` | 1 / 440 g | 59.94 x 341.88 mm | 0.670 kg gross | Fail | Exact rating not published | None published | Rejected |
| Leland `89200` | 2 / 400 g | 50.04 x 234.95 mm each | 0.600 kg total gross | Pass | Exact cylinder rating not published | None published | **Best geometric candidate; not selectable** |
| Leland `89150` | 3 / 450 g | 50.04 x 187.96 mm each | 0.690 kg total gross | Pass | Exact cylinder rating not published | None published | Not selected; extra source |
| Swagelok `316L-HDF4-300` | 2 / 342 g | 50.8 x 227 mm each | 1.802 kg filled | Pass at allocation limit | Fail margin | None published | Rejected |
| Swagelok `316L-50DF4-500` | 1 / 342 g | 48.2 x 597 mm | 4.442 kg filled | OD pass; axial unproved | Pass | None published | Rejected: interface and mass reserve |

Sources: [Leafield GIS](https://www.leafieldmarine.com/gas-inflation-systems-for-life-rafts/gas-inflation-system-gis-type/), [Leafield GIS manual](https://www.leafieldmarine.com/wp-content/uploads/2023/12/LEL-20018-Rev-7b-INFO-ONLY-GIS-User-Manual.pdf), [Leland cylinder table](https://www.lelandltd.com/cylinders.html), [Leland 65026 puncture devices](https://www.lelandltd.com/puncture_devices.htm), [Swagelok cylinders](https://www.swagelok.com/downloads/webcatalogs/en/ms-01-177.pdf), and [NIST CO2](https://webbook.nist.gov/cgi/fluid.cgi?ID=C124389&Action=Page).

## Single/dual/triple comparison

| Arrangement | Best published candidate | Inventory | Source mass | Valves/heads | Reset actions | Certification/interface | Decision |
|---|---|---:|---:|---:|---:|---|---|
| One source | Leland `89440` | 440 g | 0.670 kg | 1 | 1 | DOT-39/NRC family, but OD and Leafield interface fail | Reject |
| Two sources | 2 x Leland `89200` | 400 g | 0.600 kg | 2 | 2 | OD/mass pass; no published water-authorized armed head or Leafield connection | Best geometric lead, not selected |
| Three sources | 3 x Leland `89150` | 450 g | 0.690 kg | 3 | 3 | Same interface gap with more branches/leak points | Reject versus dual |

The dual `89200` concept would preserve at least 334.51 g and mass margin, but selecting it would require inventing the very commercial actuation connection this task requires. It remains an **engineering lead**, not a final pressure-source architecture.

## Outcome

No commercial source passes all four gates simultaneously: inventory, 50.80 mm practical OD, pressure rating/margin, and published passive Leafield-compatible actuation. The narrow-source problem is therefore not a mere MPN suffix or vendor-document gate.

**ARCHITECTURE C PRESSURE SOURCE REQUIRES FURTHER REVISION**
