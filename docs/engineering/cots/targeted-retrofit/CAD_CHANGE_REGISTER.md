# Targeted-COTS CAD change register

CAD source branch: `design/df8-targeted-cots-retrofit`
Validation commit: `584e673a8b0490bc0b6ec1e508d5fc3426f45f5b`

- Replaced three occurrences of `DF8-R2-PIVOT-SPIRAL-RING-008` with Smalley `VSM-8-S16`; revised pivot-pin groove to 7.60 mm diameter by 0.46 mm width.
- Replaced four GS-19/HBD-15 actuator-ring occurrences with Rotor Clip `DC-4SS`; revised actuator-pin groove to the controlled catalog geometry.
- Retained the custom WP04 sear ring and baseline sear groove after Bowden-path interference was detected.
- Retained all custom pressure-reservoir and buoy definitions after the Swagelok/HIKO fit gate failed.
- No custom adapter lines survive the final gate.
- Generated alternative-specific STOWED and DEPLOYED AP242 masters; the cleanup baseline files were not overwritten.
