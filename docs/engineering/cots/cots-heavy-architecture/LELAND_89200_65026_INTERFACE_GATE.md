# Leland 89200 / 65026-18Y12 interface gate

## Result

**C — ONE DRAWING/DIMENSION SET REQUIRED**

No authoritative public Leland drawing, CAD model, or written dimension set was located that establishes the installed geometry of `89200` with `65026-18Y12`. The 545.0 mm packaging gate therefore cannot be resolved as either a fit or an overrun without inventing thread engagement, neck insertion, puncture advance, or keep-out dimensions.

`CAD_AUTHORIZED = false`

## Evidence search

The repository-first search covered the STINGRAY source, handoff, vendor-CAD, procurement, and Architecture C evidence for `89200`, `65026`, `65026-18Y12`, `65027`, `65028`, installed length, thread engagement, puncture advance, armed length, and fired length. It found no hidden controlled drawing or CAD model. Existing project documents contain only the previously recorded catalog dimensions and the non-authoritative 560.07 mm cylinder-plus-head arithmetic.

The bounded manufacturer search found:

- Leland's official cylinder table identifies `89200` as 200 g CO2, 1.97 in OD, 9.25 in overall length, 300 cc water capacity, and a 1/2-20 neck. The same page directs users to Sales/Engineering for accurate drawings and specifications: [Leland cylinder table](https://www.lelandltd.com/cylinders.html).
- Leland's official puncture-device listing identifies exact `65026-18Y12` as the mountable 1/2-20 inlet / 1/8 NPT outlet configuration, describes the clean-puncture seal and disengagement-relief function, and identifies `65027` and `65028`. It publishes no installed length, insertion, travel, or mounting dimensions: [Leland puncture-device listing](https://www.lelandltd.com/puncture_devices.htm).
- Leland's current `65026-18N12` page confirms the current commercial family and publishes referential exterior dimensions for a different exact suffix; it does not establish the `65026-18Y12` installed assembly: [current Leland 65026-18N12 page](https://www.lelandgas.com/product-page/65026-18n12-puncture-device-mountable-1-2-20unf-inlet-1-8npt-outlet).
- Leland's current resources page routes detailed engineering data through its controlled-access process: [Leland resources](https://www.lelandgas.com/resources).

No manufacturer-controlled drawing or CAD file was located, so there is no file to preserve or checksum under this gate. Public product photographs and referential dimension images were not treated as controlled geometry.

## Geometry status

| Required item | Authoritative status |
|---|---|
| `89200` body OD | 50.038 mm catalog value (1.97 in), referential |
| `89200` body overall length | 234.95 mm catalog value (9.25 in), referential |
| `89200` neck/interface | 1/2-20 published |
| Neck projection / threaded length / seat / shoulder datum | **NOT PUBLISHED** |
| `65026-18Y12` inlet / outlet | 1/2-20 inlet / 1/8 NPT outlet published |
| Head body length / insertion depth / nominal engagement | **NOT PUBLISHED FOR EXACT SUFFIX** |
| SAFE/ARMED installed module length | **NOT DETERMINABLE** |
| FIRED installed module length | **NOT DETERMINABLE** |
| Puncture-pin travel and operating keep-outs | **NOT PUBLISHED** |
| `65027` / `65028` mounting-retention envelope | **NOT PUBLISHED** |
| Two-module operating package | **NOT DETERMINABLE** |

The prior value `560.07 mm = 2 x (234.95 + 45.085)` is explicitly rejected as an installed-length determination. It combines a cylinder catalog overall length with a referential dimension from a different puncture-head suffix, double-counts unknown overlap, and omits unknown armed/fired travel and outlet keep-out.

## Operating and service envelopes

- Available operating corridor: **545.0 mm**.
- SAFE/ARMED operating package length: **UNKNOWN**.
- FIRED operating package length: **UNKNOWN**.
- Clearance or overrun: **NOT DETERMINABLE**.
- Service envelope: **NOT DETERMINABLE FROM PUBLISHED DATA**.

Open-closure axial withdrawal remains an acceptable service concept; the complete removal trajectory need not remain inside the 545.0 mm operating corridor. The controlled drawing must nevertheless establish removal direction and the local disconnect/withdrawal keep-out so developmental CAD can provide practical access.

## Single manufacturer request

One technical request was sent to Leland Technical Sales at `sales4c@lelandgas.com`, copied to `engineering@lelandltd.com`, with subject:

> Dimensional drawing request: 89200 + 65026-18Y12 + 65027/65028 installed assembly

The request asks for one controlled assembly drawing, STEP/IGES model, or written controlled dimension set containing:

- `89200`: neck projection, usable threaded length, sealing-seat location/geometry, and shoulder datum;
- `65026-18Y12`: body length, cylinder insertion depth, nominal thread engagement, SAFE/ARMED installed length, FIRED installed length, puncture-pin travel, forward/rear keep-outs, and 1/8-NPT outlet location/orientation/fitting keep-out;
- `65027` / `65028`: mounting and retention envelope relative to the installed head and cylinder;
- drawing/model number, revision, and whether each supplied dimension is controlled or referential.

Gmail transmission status: **SENT**, message/thread ID `1a034941149fc4f8`. This was a technical-data request only; it was not an RFQ and did not authorize a purchase.

## Exact next action

Receive the single Leland controlled assembly dimension set, calculate SAFE/ARMED, FIRED, and two-module operating lengths against 545.0 mm, and issue A or B. Do not begin developmental CAD before that calculation.
