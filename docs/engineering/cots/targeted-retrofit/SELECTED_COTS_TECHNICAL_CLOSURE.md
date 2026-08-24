# Selected COTS Technical Closure

Status: **PHASE 4 PRE-CAD CLOSURE COMPLETE — NOT RELEASED — ZERO CAD SUBSTITUTIONS IMPLEMENTED**

Authority: documentation branch `design/df8-targeted-cots-retrofit` at controlling input `09b8e958d9b20ec2aaed9c579a48bc896677217d`; clean CAD baseline `8c594781e27b0597a71957082fb64f152cacfcd9` used read-only. No explicit owner acceptance record for that CAD commit was found, therefore: **CLEAN CAD BASELINE TECHNICALLY COMPLETE — OWNER CREO ACCEPTANCE PENDING**.

## Seven-item gate

| Candidate | Exact item | Disposition | Fit result | Closure |
|---|---|---|---|---|
| C-001 | Swagelok `316L-50DF4-150` | **C — ACCEPT FOR PHYSICAL TEST BEFORE CAD** | SIGNIFICANT INTERFACE CHANGE | Exact catalog identity, dimensions, mass, material, DOT-3A construction, rating, derating and official CAD availability are verified. External-collapse, CO2 application, fill/relief architecture, service/refill path and item-specific certificate package remain unresolved. |
| C-006 | HIKO `87640_OLV_ONE` | **C — ACCEPT FOR PHYSICAL TEST BEFORE CAD** | INSUFFICIENT CAD EVIDENCE | Exact SKU/material/color are verified. The manufacturer does not publish the prior 60 L claim, flat/packed dimensions, pressure, burst, relief, tether load, cycle rating or mass. Sold out at the manufacturer. |
| C-012 | Gutekunst `VD-244` | **E — REJECT** | DOES NOT FIT | Manufacturer maximum dynamic stroke is 31.82 mm; the clean baseline requires 85 mm installed stroke and explicitly records the catalog article as unsuitable. Retain the controlled custom spring. |
| C-013 | igus `GFM-081013-08` | **E — REJECT** | DOES NOT FIT | Official dimensions do not match the authored bushing, and igus explicitly says not to use iglide G underwater. Retain the custom PEEK-lined bushing. |
| C-014 | igus `GTM-0815-005` | **E — REJECT** | DOES NOT FIT | The 0.5 mm catalog washer does not fit the authored 0.18 mm stack, and igus explicitly says not to use iglide G underwater. Retain the custom PEEK washer. |
| C-015 | Smalley `VSM-8-S16` | **B — ACCEPT PENDING OWNER / VENDOR APPLICATION APPROVAL** | LOCAL ADAPTER REQUIRED | Exact 316 stainless suffix and ring/groove/load basis are verified. The existing pivot-pin groove is outside the catalog range and must be revised; submerged service, reuse policy and certificate options require factory confirmation. |
| C-016 | Rotor Clip `DC-4SS` | **A — ACCEPT FOR CAD IMPLEMENTATION** | LOCAL ADAPTER REQUIRED | Exact PH 15-7 stainless SKU, groove, installed envelope and load basis are verified. Both existing 4 mm mating grooves require bounded revision to the official catalog dimensions. No new adapter line is introduced. |

`LOCAL ADAPTER REQUIRED` in the fit matrix includes a known local mating-interface revision. The adapter ledger distinguishes those revisions from newly introduced custom line items.

## Pressure-reservoir separated status

- **PRESSURE-RATED:** YES, 5000 psig (344 bar) through 37 °C under the manufacturer DOT-3A basis; published temperature derating applies.
- **CO2 APPLICATION APPROVED:** UNVERIFIED.
- **FIELD REFILLABLE:** UNVERIFIED. Treat as field-replaceable by certified module exchange only until a qualified refill procedure and provider exist.
- **PROCUREMENT CERTIFICATE AVAILABLE:** UNVERIFIED; requires supplier quotation.
- **EXTERNAL-PRESSURE / COLLAPSE RATING:** UNVERIFIED.
- **PROOF/HYDRO DOCUMENTATION FOR THE ORDERED SERIAL:** availability requires supplier quotation; no delivered item exists.

The `316L-50DF4-150` remains **FOR QUALIFIED FIT / PRESSURE-SUBSYSTEM EVALUATION ONLY**. It is not automatically the production pressure architecture and no custom pressure vessel is authorized.

## Field-reset closure

The surviving targeted substitutions do not yet establish a true field reset. The small retaining rings are field-replaceable with controlled tools and incoming inspection. The HIKO bag can only be treated as field-serviceable after deflation, drying, repack, seam/port and repeated-inflation qualification. The Swagelok cylinder preserves field recovery only if the operational concept uses certified spare-module exchange; operator field refill is not established. Routine post-deployment recovery remains blocked by the unresolved gas-source recharge/replacement, relief/fill controls, bag drying/repack acceptance and received-item traceability.

Field-reset verdict: **CONDITIONAL — PRESERVED ONLY BY CERTIFIED PRESSURE-MODULE EXCHANGE AND SUCCESSFUL TWO-SPECIMEN BUOY REPACK QUALIFICATION; FIELD REFILLABILITY IS NOT ESTABLISHED.**

## Adapter and percentage accounting

- accepted COTS functions after gate: `14` MAKE definitions (3 cylinder boundary, 8 buoy gores, 1 pivot ring, 2 four-millimeter rings);
- new custom adapter lines: `4` (two pressure-package interfaces and two buoy interfaces);
- net custom line reduction: `14 - 4 = 10`;
- functional denominator: unchanged at `114` because adapter lines do not create new independent DF8 functions;
- functional COTS numerator: `10 + 14 = 24`;
- projected gated ceiling: **24/114 = 21.05%**;
- baseline: **10/114 = 8.77%**.

This is the **TARGETED-RETROFIT PRACTICAL COTS CEILING** for the current architecture and current evidence. It is conditional on the B/C items surviving approval and test; it is not implemented or released.

## Official evidence

- Swagelok: [product page](https://products.swagelok.com/en/c/dot-compliant-cylinders/p/316L-50DF4-150), [MS-01-177 Rev O catalog](https://www.swagelok.com/downloads/webcatalogs/en/ms-01-177.pdf).
- HIKO: [FLOATEK FULL TAIL](https://hikosport.com/en-eu/products/floatek-full-tail).
- Gutekunst: [`VD-244`](https://www.federnshop.com/en/products/compression_springs/vd-244.html), [compression-spring selection/certificate policy](https://www.federnshop.com/en/information/information-on-the-selection-of-the-compression-spring.html).
- igus: [iglide G official catalog](https://www.igus.com/ContentData/Products/Downloads/iglide_G300_FM_USen.pdf), [thrust-washer selector](https://www.igus.com/iglide-ibh/thrust-washers).
- Smalley: [`VSM-8`](https://www.smalley.com/ring/vsm-8), [part-number material suffixes](https://www.smalley.com/specifying-part-numbers).
- Rotor Clip: [`DC-4`](https://www.rotorclip.com/product/dc-4/).

## CAD-readiness disposition

**TARGETED COTS REQUIRES PHYSICAL TEST BEFORE CAD.**

The only item individually gated A is `DC-4SS`. Production CAD modification remains prohibited until owner acceptance of clean baseline `8c594781e27b0597a71957082fb64f152cacfcd9`. No pressure or softgood CAD substitution may begin before C-001/C-006 physical qualification and required vendor responses.
