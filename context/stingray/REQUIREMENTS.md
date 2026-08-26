# STINGRAY Requirements Snapshot

Status: consolidated current/historical control summary as of 2026-08-25. Local-source reconciliation is still required for the newest SHORT14/FORWARD configuration.

## System-level controls

- Ready-to-throw mass hard maximum: 18.14 kg / 40.0 lb.
- Rigid length hard maximum: 2032 mm.
- Rigid-body / arm-module OD hard maximum: 57.15 mm; nominal diameter near 53 mm where feasible.
- Three arms clocked 0° / 120° / 240°.
- Deployed arm angle approximately 80° with structural hard stops and positive deployed locks.
- Exterior in the fabric-contact/penetration region must be smooth, snag-resistant and free of forward-facing lips, exposed loose retainers and impossible discontinuities.
- Water is the sole deployment authorization in the established DF8 architecture; transport/rain/spray must not cause unintended deployment.
- Manual reset/serviceability is required.
- Recovery load must bypass trigger/inflator linkage, release cam/sear, GS-19, HBD-15 and nonstructural softgoods/cover hardware unless a specific rated load path is established.
- No unsupported qualification claims: physical wet/fabric/saltwater/shock/proof testing remains required.

## Arm length/configuration control

Historical full-length DF8/R2 requirement:

- arm pivot-centerline-to-tip: 733.806 mm / 28.89 in.

Current shortened developmental direction:

- recent Package 04/05 inspection variants use approximately 14.890-in arms.
- latest shown `SHORT14_FORWARD` model is a shortened-arm configuration.

Therefore, do not force the 733.806 mm full-length requirement back into the current short-arm branch without first proving that the short-arm owner decision was superseded.

## Arm powertrain controls

- Common centered crosshead and three links.
- Prior 2.250-in redesign analysis: crosshead travel >=15.050 mm; design target approximately 16 mm.
- GS-19 retained as primary actuation component: ACE Controls `GS-19-50-V4A-B8-B8`.
- HBD-15 retained as damping component: ACE Controls `HBD-15-25-AA-P`.
- Direct HBD installation: no bypass, fuse, overload release or lost-motion device required solely to survive HBD seizure.
- HBD mechanical seizure is an owner-accepted single-point deployment failure.
- Reduced/lost damping without seizure still requires stops/locks to survive.
- Independent backup deployment capability was required in the pre-short-arm architecture; local latest-model reconciliation must confirm how that requirement is implemented in SHORT14/FORWARD.
- Initial stowed-retention design load used in the 2.250-in analysis: 0.8 kN per arm pending controlled shock spectrum.

## GS-19 controlled data from design input register

- stroke: 50 mm
- cylinder diameter: 19 mm
- rod diameter: 8 mm
- extended length: 164 mm
- vendor mass basis: 0.144 kg in the independent input register
- configured force must not be assumed from the vendor maximum; supplier configuration or measured force curve is required.
- provisional force cases previously used: 330 N best, 300 N nominal, 270 N tolerance-low, 230 N provisional environmental-low.

## HBD-15 controlled data from design input register

- stroke: 25 mm
- body diameter: 15 mm
- rod diameter: 6 mm
- extended length: 145 mm
- initial damping test target previously used: approximately 100–150 N over expected speed range; final setting is test-derived.

## Structural/detail controls retained from analysis

- Primary arm/root loads must enter direct structural metal load paths, not fairings, softgoods, actuator rods or seam features.
- Captive double-shear pivot/link hardware preferred; no exposed loose cotter pins/E-clips in fabric-contact regions.
- Structural fasteners: use controlled marine-compatible high-strength hardware; commercial 18-8 is not automatically acceptable for primary stop/lock loads.
- Avoid uncoated 316-on-316 loaded oscillating sliding pairs because of galling risk.
- Preferred structural materials historically include Ti-6Al-4V and 17-4 PH with condition-specific allowables and corrosion review.
- Service retainers should be captive or positively controlled.

## External buoyancy controls

Current engineering direction is external equipment-oriented buoyancy rather than a tightly packed internal buoy.

- Rigid-body 57.15 mm limit remains a rigid geometry control.
- Do not assume the external soft buoy pack must remain within 57.15 mm overall.
- Current provisional external softgoods keep-out: approximately 115–120 mm local envelope, pending exact vendor drawing/physical measurement.
- Structural recovery load should use an independent rated tether/bridle path, not MOLLE, breakaway cover or hook-and-loop unless specifically load-rated.

## Naming control for final Creo-facing parts

- COTS: use product/component name + actual part number.
- Custom: use descriptive functional name + material initials.
- Do not use DF8 administrative/work-package titles as final Creo component names.