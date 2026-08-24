# Architecture C final pre-CAD gate

## Disposition

**ARCHITECTURE C REQUIRES ONE REMAINING ENGINEERING INPUT**

The pressure architecture has converged. Nine individual PFD inflators are replaced by one commercial marine source branch:

`342 g CO2 in eurocylinder 130522277 -> Leafield GIS water actuator/servo -> GIS cutter head/cylinder valve -> rated hose -> fixed-jet GIV -> 60 L STINGRAY softgood -> B10 Yellow relief`

## Closed

- 342 g selected versus 334.51 g qualification requirement.
- One gas source; zero HP checks; zero HP bus/manifold; zero custom pressure vessels.
- NIST source pressure at 50 C: 96.215 bar absolute for selected 342 kg/m3 fill density.
- HP hierarchy: 200 bar cylinder working boundary, 300 bar cylinder test, at least 250 bar Leafield valve/outlet/hose MWP.
- No regulator: manufacturer marine topology uses rated HP transfer, fixed-jet GIV and high-flow differential relief.
- Low-pressure operating basis: 10.0 kPa differential.
- B10 Yellow: 12.1 kPa nominal, 14.7 kPa maximum opening, 10.2 kPa minimum sealing.
- Residual custom 60 L softgood with commercial inlet/relief.
- Complete certified source-module field exchange; fired-module recharge/refurbishment is depot work.
- Estimated pressure-system mass 4.3 kg; projected ready-to-throw estimate 15.81 kg with 2.33 kg reserve.
- Functional COTS projection 18/23 = 78.26%.
- Known packaging risk: the selected 82.5 mm cylinder exceeds the 53 mm normal-body target; it is not claimed to fit. The target is not the 57.15 mm stowed arm-module maximum, but the bounded CAD commission must allocate a compliant localized source envelope.

## One remaining engineering input

Obtain a **Leafield drawing-controlled configured-assembly package** giving:

1. exact MPN for the water-activated GIS unit;
2. exact servo/adaptor/hose MPNs for firing one cylinder;
3. exact D91-220 25E, 250 bar cylinder-valve suffix compatible with `130522277`;
4. exact outlet/hose-end definition;
5. assembly mass, dimensions and keep-out envelope sufficient to combine with the known 82.5 x 280 mm cylinder body;
6. current drawing/manual revisions and configuration statement.

Public evidence establishes the GIS family topology and pressure capability but does not publish this dimensioned configuration. This configured source-package definition is the sole remaining **engineering CAD input**; the subsequent bounded CAD commission must prove the known 82.5 mm source can be allocated without violating hard external/stowed envelopes. General application approval, quote, lead time, CoC and delivered identity are procurement/receiving gates.

`CAD_AUTHORIZED = false`

`NO_VENDOR_EMAIL_WAIT = true`

## Downstream physical qualification gates

- full-scale 0 C, 5 m, 54 L-by-10 s and 60 L steady-volume test;
- fixed-jet selection, icing, hose reaction and B10 relief-flow/accumulation test;
- softgood leak, pressure, relief, repeated-cycle and salt-water/corrosion qualification;
- field module-exchange/reset demonstration;
- separate 500 lbf recovery proof/load-path verification and unresolved design/ultimate structural requirement.

These gates block final release, not bounded CAD after the drawing-controlled input closes.

## Exact next action

Acquire the current Leafield configured-assembly drawing package above; then commission bounded Architecture C CAD packaging/interface implementation against the read-only final-cleanup baseline. Do not purchase production hardware or release the softgood before physical qualification.
