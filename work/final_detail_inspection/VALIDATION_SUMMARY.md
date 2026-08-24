# Validation Summary

```json
{
  "checkpoint": "PASS - TARGETED INSPECTION CHECKPOINT",
  "scope": "final Creo names; continuous route bends; manifold termination; hinge cohesion",
  "clean_reimport": {
    "STOWED": {
      "sha256": "960c7ca5c25e5df230c2672358ba577c187f6eb0a1012f04b2020e5f956a608f",
      "ap242": true,
      "leaf_identity": true,
      "solid_count": 308,
      "invalid_solid_count": 0
    },
    "DEPLOYED": {
      "sha256": "efc5f8bee8927adfeb1fedc644ffc6b1424309940d7dce21176435dd3f776c2e",
      "ap242": true,
      "leaf_identity": true,
      "solid_count": 308,
      "invalid_solid_count": 0
    }
  },
  "targeted_missing": [],
  "targeted_invalid_or_multisolid": [],
  "unchanged_baseline_multisolid_definitions_outside_scope": [
    "STOWED:FWD-RING-02",
    "STOWED:CARTRIDGE-CARRIER-FWD",
    "STOWED:CARTRIDGE-CARRIER-AFT",
    "STOWED:WATER-INLET-001",
    "STOWED:FULLFLOW-VALVE-001",
    "STOWED:CROSSHEAD-001",
    "STOWED:GS19-BODY-001",
    "STOWED:HBD-BODY-001",
    "STOWED:PIVOT-CARRIER-1",
    "STOWED:PIVOT-CARRIER-2",
    "STOWED:PIVOT-CARRIER-3",
    "STOWED:WP04-REACTION-BULKHEAD",
    "STOWED:WP04-LATCH-001",
    "STOWED:BODY-HARDPOINT-001",
    "DEPLOYED:FWD-RING-02",
    "DEPLOYED:CARTRIDGE-CARRIER-FWD",
    "DEPLOYED:CARTRIDGE-CARRIER-AFT",
    "DEPLOYED:WATER-INLET-001",
    "DEPLOYED:FULLFLOW-VALVE-001",
    "DEPLOYED:CROSSHEAD-001",
    "DEPLOYED:GS19-BODY-001",
    "DEPLOYED:HBD-BODY-001",
    "DEPLOYED:PIVOT-CARRIER-1",
    "DEPLOYED:PIVOT-CARRIER-2",
    "DEPLOYED:PIVOT-CARRIER-3",
    "DEPLOYED:WP04-REACTION-BULKHEAD",
    "DEPLOYED:WP04-LATCH-001",
    "DEPLOYED:BODY-HARDPOINT-001"
  ],
  "bad_final_names": [],
  "duplicate_final_names": [],
  "mass_kg": {
    "STOWED": 11.733427548442759,
    "DEPLOYED": 11.733427548442913
  },
  "key_dimensions": {
    "stowed_rigid_length_mm": 2031.0000001,
    "deployed_rigid_length_mm": 2031.0000001,
    "arm_module_xy_span_mm": 67.4807540043152,
    "crosshead_travel_mm": 15.055034371129977
  },
  "motion_angles_run": [],
  "motion_reaudit": "NOT REQUIRED - changed geometry remains in fixed internal corridors outside the established swept arm envelope",
  "baseline_multisolid_comparison": "All listed unrelated definitions retain the exact solid count from 61a58cbb; they do not govern this bounded verdict.",
  "release_posture": "OWNER CREO VISUAL INSPECTION REQUIRED BEFORE REMAINING RELEASE VALIDATION"
}
```

This inspection checkpoint is bounded to the four authorized final-detail corrections. The 81-state sweep was not run. It is not a release PASS.
