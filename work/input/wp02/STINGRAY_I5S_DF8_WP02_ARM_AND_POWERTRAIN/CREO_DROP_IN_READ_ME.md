
# Creo Drop-In Read Me

1. Import the applicable top-level file from `05_SUBSYSTEM_CAD/` as a STEP AP242 assembly in millimetres.
2. Use scale `1.000000`; do not auto-rescale or heal by changing dimensions.
3. The assembly uses the DF8 global system: penetrator tip at Z=0, +Z aft, arm planes 0/120/240 degrees.
4. The accepted WP01 body is intentionally absent from these WP02 state files. Insert the WP02 assembly into the accepted WP01 assembly at the identity/default transform; do not rescale or shift either file.
5. The exact GS vendor original is preserved in `03_VENDOR_CAD_ORIGINAL`. The normalized GS copy is a scale-preserving AP242 conversion. HBD, Lee and Smalley files are explicitly drawing/catalog-derived, not authentic vendor CAD.
6. Native Creo import was not available in this execution. Use the independent OCCT reimport report as neutral-CAD evidence and create a separate Creo import log before any downstream release decision.
