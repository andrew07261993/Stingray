# Architecture C final pre-CAD gate

## Decision

**C — ONE DRAWING/DIMENSION SET REQUIRED**

The provisionally frozen architecture remains:

- 2 x Leland `89200`, 200 g CO2 each / 400 g total;
- 2 x Leland `65026-18Y12` commercial puncture devices;
- `65027` brackets and `65028` retaining nuts;
- one passive water-authorized dual mechanical release;
- two independent HP modules and pressure-control paths, converging only after pressure reduction;
- zero custom pressure vessels and zero custom HP adapters;
- certified charged-module exchange for field reset.

No architecture trade was reopened.

## Closed gates

- gas inventory: **PASS**, 400 g versus 334.51 g qualification requirement;
- diameter arithmetic: **PASS — TOLERANCE-CRITICAL**, 50.038 mm versus 50.80 mm cylinder allocation;
- source count: **PASS**, two;
- estimated mass: **PASS BY PRE-CAD ESTIMATE**;
- field-reset topology: **PASS IN CONCEPT**;
- custom pressure vessels: **0**;
- custom HP adapters: **0**.

## Sole developmental-CAD hold

The controlled installed geometry of `89200 + 65026-18Y12 + 65027 + 65028` is not publicly available. SAFE/ARMED length, FIRED length, exact cylinder/head overlap, operating keep-out, and mounting-retention envelope are therefore unknown. The two-module clearance or overrun against the 545.0 mm corridor cannot be calculated.

A single, exact technical-data request has been sent to Leland. See `LELAND_89200_65026_INTERFACE_GATE.md`.

`CAD_AUTHORIZED = false`

`DECISION = C — ONE DRAWING/DIMENSION SET REQUIRED`

`INQUIRY_SENT = true`

## Downstream gates

Procurement suffix/quote/CoC data, delivered-item identity, component pressure-temperature substantiation, and physical pressure/performance/relief/softgood/corrosion/reset qualification remain downstream gates. They do not replace the sole installed-geometry requirement before developmental CAD.

## Exact next action

On receipt of the Leland controlled assembly dimension set, compute both module operating extents plus required inter-module and outlet allowances against 545.0 mm. Issue A if the total is at or below 545.0 mm, or B with the exact overrun if it exceeds 545.0 mm. Do not run CAD until then.
