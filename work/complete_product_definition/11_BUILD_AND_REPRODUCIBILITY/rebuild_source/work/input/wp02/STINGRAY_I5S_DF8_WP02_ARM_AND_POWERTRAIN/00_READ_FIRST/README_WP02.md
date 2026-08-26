
# STINGRAY I5-S DF8 WP02 Arm and Powertrain

**Configuration:** `STINGRAY-I5S-DF8-WP02-ARM-POWERTRAIN-2026-08-18-R1`  
**Revision:** `DF8-WP02-R1`  
**Owner authorization:** `USE ALL RECOMMENDED DEFAULTS`  
**Parent DF8 archive SHA-256:** `6da4deb5e920ab819ffc1ce720ef7934c792a539416b51f7b78acf18f76bed60`  
**Accepted WP01 archive SHA-256:** `b55f23fb76b01bb8d6d17b6a6f7969f00f835199f762be1b53f80021cfff1685`

This package contains exactly two top-level AP242 state assemblies: `STOWED` and `DEPLOYED`. The accepted WP01 body is not embedded in the two state files; it is loaded only by the separate containment audit. All WP02 occurrences remain at the DF8 identity/default transform. WP02-owned geometry includes three rigid arms, links, common crosshead, exact GS vendor BREP, drawing-derived HBD, selected backup spring, guides, brackets, pins, retainers, stops, positive locks, stow latches, and a captive nonfragmenting HBD bypass.

The inherited Lee `LHL 1250D 09` installation is rejected. Its catalog rate is 85.815 N/mm, not 8.7504 N/mm; the inherited configuration would apply approximately 4.10 kN at the stowed installed length and leaves only 3.51 mm above solid height. The selected controlled candidate is `LHL 625D 12`.

## Release classification

CONTROLLED DIGITAL SUBSYSTEM DEVELOPMENT DEFINITION; DIGITAL GEOMETRY AND ANALYTICAL BASELINE COMPLETE FOR THE TWO DELIVERED STATES. NOT PROCUREMENT RELEASED, NOT FABRICATION RELEASED, NOT TEST-ENTRY READY, NOT QUALIFIED, AND NOT OPERATIONALLY READY. HBD DRAWING-DERIVED GEOMETRY, GS CHARGE SPECIFICATION, SPRING PROCUREMENT IDENTITY, DAMPING ADJUSTMENT, BYPASS DETENT SETTING, SALTWATER BOUNDARY, AND REPRESENTATIVE PHYSICAL TESTS REQUIRE EXTERNAL VERIFICATION.
