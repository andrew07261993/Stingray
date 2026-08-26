# STINGRAY Requirements Snapshot

As of: 2026-08-25. Use with the exact current configuration and `DECISION_REGISTER.md`.

## Current SHORT14 true-forward configuration

- exact configuration: `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY`;
- branch/commit: `design/df8-14in-short-forward-powertrain-external-buoy` at `aa186c9c1c311c510ac34e48bd4170ef7636b7bf`;
- three arms clocked 0/120/240 degrees;
- arm pivot-to-tip length: 378.206 mm;
- arm/body reduction from source: 355.600 mm;
- current pivot station: 355.000 mm from nose tip;
- rigid-body length: 1675.400 mm;
- reported maximum rigid span: 56.500 mm;
- ready-to-throw mass: 10.583165211 kg;
- reported reserve to 18.14 kg: 7.556834789 kg;
- deployed arm angle: approximately 80 degrees with stops/locks.

The 733.806 mm arm and 480.000 mm pivot are historical/source values for prior configurations. Do not reimpose them on current SHORT14 geometry without a newer owner reversal. Conversely, pressure-packaging outputs commissioned under fixed 480 mm must not use the 889 mm fallback as a final fixed-480 geometry.

## System controls

- Ready-to-throw mass hard maximum: 18.14 kg / 40.0 lb.
- Rigid length hard maximum: 2032 mm.
- Rigid-body/arm-module hard maximum span/OD: 57.150 mm.
- Exterior in fabric-contact/penetration regions must be smooth, snag-resistant and free of exposed loose retainers, impossible discontinuities and forward-facing lips.
- Water is the established deployment authorization; transport/rain/spray must not cause unintended deployment.
- Manual reset/serviceability is required.
- Recovery load must bypass trigger/inflator linkage, release cam/sear, GS-19, HBD-15 and nonstructural cover/softgoods hardware unless an exact rated path is established.
- No physical qualification claim may be inferred from CAD, OCP/XCAF, AP242, presentation or owner visual inspection alone.

## Arm powertrain controls

- Centered crosshead with three links.
- ACE `GS-19-50-V4A-B8-B8`: 50 mm stroke, about 164.1 mm extended length, 7.9 mm rod and 0.144 kg catalog assembly basis.
- GS-19 force must come from the exact supplied configuration or measured force curve; 330/300/270/230 N remain development cases, not certified values.
- ACE `HBD-15-25-AA-P`: 24.9/25 mm stroke, 145.0 mm extended length, 15 mm body, 6.1 mm rod and 0.220 kg catalog assembly basis.
- HBD remains direct; no bypass/fuse/overload-release is required solely for seizure. Seizure remains an accepted single-point failure.
- The current source preserves the backup spring, fixed/moving seat sense and aft-trailing guide arrangement.
- Stops/locks must remain effective under reduced/lost damping.
- Structural pins/retainers and load paths must remain captive/positive and marine-compatible.

## External buoy controls

- The current pack is external softgoods; the 57.150 mm limit applies to rigid geometry, not to an invented softgoods OD.
- The source pack spans an axial region around Z 1368-1606 mm and includes custom Cordura/flaps/webbing/tether, a custom 60 L buoy definition, a Hydro 1F/V95000XXB dimensional proxy, one Leland 81121 and V80040.
- A dimension-controlled proxy does not establish vendor-exact internal geometry, rating, application approval or procurement identity.
- Automatic water access, manual pull access, peel direction and tether bypass must be physically verified on the finished article.
- The structural recovery path must not depend on hook-and-loop, pack cover, inflator body or unrated commercial holder hardware.
- Exact finished packed dimensions, mass/CG, buoy volume, cartridge inventory, relief, leak and proof evidence are required before release.

## COTS controls

- Prefer complete, orderable, manufacturer-supported modules only when installed envelope, service/removal envelope, rated interfaces, application approval and exact suffix/MPN are controlled.
- A shared thread, inflator-only length, public product family or dimensional proxy is not a complete installed module.
- Separate exact vendor CAD, manufacturer drawing-derived geometry, controlled proxy geometry and custom analytic geometry.
- An RFQ/technical-information inquiry is not purchase or qualification authority.
- Require exact order suffix, current certificate/CoC/lot/expiry data and received-item verification as applicable.
- Count independently orderable functional COTS lines; do not inflate COTS percentage with purchased-assembly child geometry.

## Physical/release gates

- owner Creo inspection of exact current STOWED/DEPLOYED AP242;
- fabric engagement, retention, snag and extraction;
- wet automatic activation, inflation and breakaway/peel;
- manual gloved pull force/stroke and snag retention;
- leak, relief, structural proof and recovery-load verification;
- drainage, saltwater/fouling/wear, drying and repack/service cycles;
- quantitative fall/orientation equivalence;
- vendor exactness, application approval, procurement/receiving evidence.

Until those gates close, status remains CURRENT DEVELOPMENTAL—not released or qualified.
