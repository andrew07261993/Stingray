
# WP02 STEP Reimport Report

Both top-level AP242 state files were reopened after export in a separate OCCT STEPControl process. The check verifies AP242 schema, millimetre units, 35 named products per assembly, root transfer, solid count, individual-solid validity, aggregate volume, and bounding box against the controlled source-state signatures.

This is an independent post-export execution but not an independent CAD kernel: both export and reimport use OCCT 7.9. Native Creo validation and a genuinely different-kernel import remain external evidence requirements and are not claimed.
