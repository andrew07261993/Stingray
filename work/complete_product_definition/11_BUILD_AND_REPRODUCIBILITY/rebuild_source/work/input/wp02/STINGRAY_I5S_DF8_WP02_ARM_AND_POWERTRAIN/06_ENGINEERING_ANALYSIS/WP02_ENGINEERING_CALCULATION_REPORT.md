
# WP02 Engineering Calculation Report

## Kinematics

For arm angle θ, the arm-link attachment center is

`r_a = r_p + r_l sin θ`, `z_a = z_p + r_l cos θ`.

With a crosshead joint constrained at radius `r_c`, the crosshead coordinate is

`z_c = z_a - sqrt(L² - (r_a-r_c)²)`.

Inputs: `r_p=36.000 mm`, `z_p=625.000 mm`, `r_l=35.000 mm`, `r_c=42.000 mm`, `L=70.000 mm`. Results: `z_c,stow=590.202428 mm`, `z_c,deploy=567.128038 mm`, travel `23.074391 mm`. The exact coordinate table is in `WP02_KINEMATIC_REGISTER.csv`.

## Backup spring

`F = k(L_free - L_installed)` and released energy is `0.5 k (δ_stow²-δ_deploy²)`.

Selected `LHL 625D 12`: `k=11.910 N/mm`, `L_free=203.2 mm`, `L_stow=153.000 mm`, `L_deploy=176.074391 mm`. Forces are `597.882 N` stowed and `323.066 N` deployed; released energy is `10.6252 J`; stowed solid-height margin is `13.300 mm`.

## Gas spring

The development order specification is `F1=300 ± 30 N at 20 °C`, with a 30% progression screening model over the manufacturer 50 mm stroke. The configured mechanism uses `23.074391 mm`, so the GS remains away from its internal stroke limit and requires external mechanical stops as modeled.

## HBD

Crosshead travel after the `1.2 mm` controlled slot is `21.874391 mm`. Against the nominal `25.0 mm` stroke, gross reserve is `3.125609 mm`; after the `1.5 mm` external-stop allowance, residual reserve is `1.625609 mm`.

The dynamic model uses a capped 250 N damping representation because exact configured HBD force-speed data were not externally available. It is a digital screening model, not calibration evidence.

## Dynamics and impact

The one-DOF model uses the exact nonlinear crosshead Jacobian, three-arm rigid-body inertia, GS progression, backup spring force, Coulomb-friction sensitivities, worst opposing axial gravity, HBD lost motion, and capped damping. Detailed inputs/results are in `WP02_DYNAMIC_CASE_RESULTS.csv` and the reproducible source. Every required single-drive case reaches 80 degrees in the model; the both-drives-unavailable case is intentionally classified failed. Stop/lock kinetic energy values establish the minimum physical pad/lock test envelope; they are not material qualification.

## Structural screening

The provisional 150/300/500/750/1000 lbf cases use equal three-arm distribution and a 435 mm arm lever. Nominal root bending stress is computed from the modeled hollow section modulus. This is a development screen only; approved mission loads, nonlinear contact FEA, fatigue, proof and ultimate tests remain external.
