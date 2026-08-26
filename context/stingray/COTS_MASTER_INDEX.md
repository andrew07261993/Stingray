# STINGRAY COTS Master Index

As of 2026-08-25. Status reflects recovered engineering context, not procurement release.

| Subsystem | Manufacturer | Product / P/N | Status | Notes |
|---|---|---|---|---|
| Arm drive | ACE Controls | GS-19-50-V4A-B8-B8 | SELECTED / RETAINED | Authentic vendor BREP used in prior CAD. Configured force still requires supplier/bench evidence. |
| Damping | ACE Controls | HBD-15-25-AA-P | SELECTED / RETAINED | Direct installation; no bypass. Seizure accepted as single-point deployment failure. Exact configured vendor data still required. |
| External buoyancy | SECUMAR | Pack Buoyancy Aid with SECUTRONIC, 350 N / 75 g CO2 | PRIMARY CANDIDATE | Best current equipment-oriented match. Pending exact MPN, packed dimensions, mass/CG, activation configuration and rated structural attachment. |
| External buoyancy benchmark | PECI | Auto-TFSS, NSN 8465-01-696-6409 | ALTERNATE / REFERENCE | ~356 N surface; each pouch approx. 8.5 x 2.5 x 2.25 in. Useful packaging/depth benchmark; two-pouch body-worn architecture is less attractive for DF8. |
| Inflator technology | Lifesaving Systems | 470-CG | ALTERNATE TECHNOLOGY | Appropriate only for a smaller custom bladder or manufacturer-engineered multi-inflator solution; not an ad-hoc substitute for SECUMAR's 75 g system. |
| CO2 cartridge | Leland Gas Technologies | 80121 | HISTORICAL COTS / WP03 | Used in prior water-activation/inflation work as manufacturer-web-derived COTS geometry. Relevance to external-pack branch must be re-evaluated. |
| Retaining ring | Smalley | VSM-6-S16-PA | CANDIDATE / PRIOR WP02 | Drawing-derived COTS geometry used for low axial positioning; not credited as primary structural arm retention. |
| Retaining ring | Rotor Clip | DC-4SS | CANDIDATE / RFQ | Developmental RFQ issued for PH 15-7 stainless self-finish rings; vendor data/traceability requested. |
| Pressure cylinder | Swagelok | 316L-50DF4-150 | CANDIDATE / RFQ | Developmental RFQ for two 316L cylinders; exact CAD, pressure/external-collapse, refill and certification data requested. |
| Flotation article | HIKO FLOATEK | FULL TAIL 87640_OLV_ONE | CANDIDATE / RFQ | Developmental same-lot test article candidate; requested buoyancy, seam/material, valve/inflation, attachment limits and traceability. |
| Structural fastener | BUMAX | 14583A40300688 | EVIDENCE HOLD | Prior WP01 digital package identified missing authentic CAD/procurement evidence. |
| Purchased component | Essentra | 20828400 | EVIDENCE HOLD | Prior WP01 digital package identified missing authentic CAD. |
| Buoy/inflation module | UML | MK5 | CANDIDATE / PROXY HISTORY | Used as a proxy/reference in short-arm/external-buoy development and screened as a possible commercial module. Exact applicability must be resolved locally. |
| Buoy/inflation module | UML | Pro Sensor Elite | CANDIDATE / SCREENED | Included in commercial-module screening; no supported complete module fit the 50.700 mm bore in the staged-inflation study. |
| Buoy/inflation module | V95000 complete package | CANDIDATE / SCREENED | Included in commercial-module closure screening; local result/provenance should be ingested. |

## External buoyancy research conclusions

Current highest-value candidate is the SECUMAR 350 N Pack Buoyancy Aid with SECUTRONIC because it already combines:

- equipment-oriented flotation/surfacing architecture;
- approximately 350 N / 35 L / 77 lbf surface buoyancy;
- 75 g CO2 inventory;
- automatic water/depth activation logic;
- manual pull activation;
- folded protective pack / breakaway-style deployment;
- field rearmability.

Do not assume its public MOLLE grid, Malice clips, hook-and-loop closure or cover are rated to carry STINGRAY recovery loads.

Vendor-data gate before CAD freeze:

- exact orderable model/MPN;
- packed L x W x T;
- complete packed mass and CG;
- inflated chamber geometry;
- chamber material;
- exact 75 g cartridge P/N;
- SECUTRONIC activator/rearm P/N;
- available water-contact delay / critical-depth settings;
- operating temperature range;
- buoyancy vs depth at relevant depths;
- manual pull force/stroke;
- structural attachment point and allowable load;
- STEP/IGES or dimensioned envelope drawing;
- service life/rearm procedure;
- lead time.

## COTS accounting rule

For future COTS-percentage reporting, distinguish:

- independently orderable functional COTS lines;
- standard fasteners/raw stock/consumables;
- child geometry inherited from purchased assemblies;
- custom fabricated parts.

Do not inflate the COTS percentage by manipulating the denominator or counting child geometry as separately purchased components.