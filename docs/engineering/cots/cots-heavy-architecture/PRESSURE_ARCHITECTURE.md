# Pressure architecture — commercial marine convergence

## Frozen functional path

`commercial CO2 cylinder -> Leafield water-authorized GIS/servo -> GIS cutter/cylinder valve -> rated HP hose -> fixed-jet GIV -> low-pressure 60 L softgood -> B10 differential relief -> local ambient`

One source eliminates branch check valves and the HP collection bus. No custom pressure vessel, pressure manifold or pressure adapter is selected.

## Pressure hierarchy

| Zone | Maximum credible | Required rating/control | Gate |
|---|---:|---|---|
| 342 g CO2 in 1.0 L cylinder | 96.215 bar absolute at 50 C; 113.58 bar absolute at 65 C | eurocylinder `130522277`, 200 bar WP/300 bar TP | Closed for pressure; certified fill procedure downstream |
| Leafield cylinder valve/cutter | bounded by 200 bar cylinder boundary | D91-220 configured 25E valve and D912101 head; selected HP components >=250 bar MWP | Exact configured suffix/drawing open |
| Leafield HP hose/outlet | bounded by 200 bar source | manufacturer assembled/rated hose >=250 bar MWP with documented derating | Exact length/ends/drawing open |
| Fixed-jet GIV | HP source side; low-pressure buoy side | `B9116042.2` 2.2 mm development jet; exact flow by test | Cold-depth flow qualification |
| Buoy interior | 10.0 kPa nominal differential | residual custom 60 L softgood; commercial inlet/relief | Physical pressure qualification |
| B10 Yellow relief | 12.1 kPa nominal; max opening 14.7 kPa plus flow accumulation | factory-set B10, -30 to +65 C; no operational plug | Relief capacity/accumulation qualification |

## HP design basis

For the selected low-fill-density cylinder, the prior 760 kg/m3 cartridge proxy no longer controls. NIST at 342 kg/m3 gives about 1,381 psig at 50 C. The architecture adopts the cylinder's **200 bar (2,901 psi) working pressure** as system design pressure and requires **250 bar (3,626 psi) minimum MWP** for Leafield valve/outlet/hose components. The cylinder has **300 bar (4,351 psi) test pressure**. The 65 C GIS manual limit is also checked: NIST gives about 1,633 psig, below both boundaries.

This is a node-specific rating hierarchy, not an invented code factor. Manufacturer markings, service limits and pressure-temperature derating still control each delivered component.

## Low-pressure control

No industrial regulator is inserted into the two-phase CO2 path. Leafield's marine architecture transfers source gas through a rated hose and fixed-jet GIV into a protected compliant structure. The jet bounds rate; the high-flow B10 limits differential pressure and vents during ascent. A fixed orifice does not limit static pressure, so B10 capacity and unobstructed discharge are mandatory.

The selected provisional envelope is:

- 10.0 kPa (1.45 psi) operating differential;
- B10 Yellow 12.1 kPa (1.75 psi) nominal;
- B10 maximum opening 14.7 kPa (2.13 psi);
- B10 minimum sealing 10.2 kPa (1.48 psi).

`PHYSICAL PRESSURE QUALIFICATION REQUIRED`

The softgood must demonstrate acceptable leakage, seam behavior and repeated cycles through full relief accumulation. Final release also requires 54 L by 10 s and 60 L steady usable volume at 5 m/0 C.

## Failure behavior

- Water actuator/servo or cutter blocked: no inflation; qualified full-scale activation test required.
- Hose/GIV blocked or iced: misses 10 s; fixed-jet/cold-flow test required.
- GIV oversized or relief obstructed: buoy overpressure; B10 capacity/guard test required.
- Source overfilled/overheated: cylinder/Leafield burst-disc boundary protects source; buoy relief provides no HP credit.
- Softgood/seam leak: loss of buoyancy; pressure/leak/cycle test required.

The exact configured water actuator/servo/25E valve/hose drawing is the one remaining CAD input.
