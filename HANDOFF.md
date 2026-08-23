# STINGRAY I5-S DF8 Codex handoff checkpoint

Actual capture wall timestamp: `2026-08-22T23:26:37Z`.
Reproducibility timestamp epoch: `1787441142` (`2026-08-22T23:25:42Z`).

This is a preservation and safe-handoff checkpoint. It does not authorize a new
correction cycle, a rebuild, workbook promotion, or final release packaging.
The bounded corrective sequence was superseded operationally by the latest
**SAFE CODEX HANDOFF CHECKPOINT** directive. The latest safe-termination
directive governs runtime only; it does not rewrite the controlling engineering
commission records.

- Current execution phase: terminal validator failure preservation and atomic safe-handoff packaging.
- Latest completed checkpoint: manifest-bound final authoring masters plus 81 completed exact-motion samples merged in work/final_analysis/validation/motion_full_mechanism_audit.csv.gz; post-merge gate/NCR outputs were not computed.

## Controlling source records

- `commission/ORIGINAL_COMMISSION_20260821-031917.md` is the original controlling commission.
- `commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md` is the R1 rejection and R2 corrective direction.
- `commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md` is the latest safe-termination directive; it governs runtime only.
- `commission/PROVENANCE.json` binds the safe staged names to the uploaded filenames and hashes.

The historical files under `work/r2_metadata/` are retained as evidence only.
Their obsolete WIP/Creo dispositions are not controlling.

## Governance at handoff

- Creo environment disposition: **N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; OWNER CREO IMPORT OCCURS AFTER DELIVERY.**
- Clean-process OCP/XCAF AP242 reimport is the controlling neutral-CAD validation.
- No new correction cycle or final release packaging is authorized at handoff.
- Gate state is preserved exactly, never promoted by this utility.
- Authoritative editable source: `work/r2_source`
- Only live build-input tree carried forward: `work/input/wp02`
- `work/analysis` is preserved as source-BOM/build-data procurement reconciliation.
- `work/scripts` is historical evidence and is not runnable without original input trees intentionally omitted from this live-source handoff.
- Absolute paths copied inside historical JSON/CSV records are provenance-only. They are not resumption dependencies.
- The completed 81-sample motion sweep merged and removed temporary shards; no /tmp state is required after the sweep.

## Last successful commands

The exact observed commands and exit codes below are copied from
`work/handoff_tools/LAST_EXECUTION_RECORD.json`; they are not inferred from
file existence or shell history.

- Last command (exit `1`):

```bash
PYTHONPATH=work/r2_source work/cadenv/bin/python work/r2_source/validate_r2.py --out work/final_analysis/validation --motion-workers 8
```

- Last successful modifying command (exit `0`):

```bash
PYTHONPATH=work/r2_source work/cadenv/bin/python work/r2_source/build_r2.py
```

- Last successful audit command (process exit `0`; engineering status is the
  separate validator status shown below):

```bash
gzip -t work/final_analysis/validation/motion_full_mechanism_audit.csv.gz
```

The last successful modifying command's hash-bound output set is:

- `work/final_release/STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step`
- `work/final_release/STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step`
- `work/final_analysis/authoring_inventory_stowed.json`
- `work/final_analysis/authoring_inventory_deployed.json`
- `work/final_analysis/authoring_manifest.json`

## Terminal audit failure (incomplete validator evidence)

- Execution state: **TERMINAL_AUDIT_FAILURE**.
- Validator command exited `1` during `POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK`.
- Exact exception: `KeyError` with message **`'angle_deg'`**.
- All **81** exact-motion samples (integer angles 0° through 80°) completed and
  were merged into `work/final_analysis/validation/motion_full_mechanism_audit.csv.gz`.
- Merged evidence: `{'path': 'work/final_analysis/validation/motion_full_mechanism_audit.csv.gz', 'size_bytes': 22925903, 'sha256': '4da00e87fd63199a29c0f4e97e9f9502da604ed48cf3f8875a9300778828fee6'}`.
- The merged CSV is measured at 1,447,875 data rows (1,447,876 including the
  header), 17,875 rows per sample, with no BLOCKED result and no nonempty error row.
- Measured result counts: CLEAR_OR_CONTACT 1,445,811; DOCUMENTED_POSITIVE_VOLUME
  1,215; UNAUTHORIZED_POSITIVE_VOLUME 849.
- The 849 unauthorized observations aggregate to 39 unique solid/variant
  occurrence pairs. Of these, 681 observations/33 unique pairs are rigid
  Category-B findings; 168 observations/6 unique pairs involve a nonrigid
  occurrence and are retained separately.
- Exact present validation top-level files (23):

```json
[
  "attachment_connectivity_deployed.csv",
  "attachment_connectivity_stowed.csv",
  "attachment_geometry_deployed.csv",
  "attachment_geometry_stowed.csv",
  "connectivity_summary.json",
  "definition_of_done_audit.json",
  "endpoint_interference_register.csv",
  "endpoint_pair_audit_deployed.csv.gz",
  "endpoint_pair_audit_stowed.csv.gz",
  "endpoint_pair_summary.json",
  "key_dimensions.json",
  "leaf_solids_deployed.csv",
  "leaf_solids_stowed.csv",
  "minimum_clearance_register.csv",
  "motion_full_mechanism_audit.csv.gz",
  "occurrence_bom_reconciliation.csv",
  "occurrence_bom_reconciliation.json",
  "route_termination_audit_deployed.csv",
  "route_termination_audit_stowed.csv",
  "state_parity.csv",
  "step_text_inspection.json",
  "xcaf_occurrences_deployed.csv",
  "xcaf_occurrences_stowed.csv"
]
```

- Exact absent/uncomputed outputs (5):

```json
[
  "gate_results.json",
  "motion_audit_summary.json",
  "motion_kinematics_1deg.csv",
  "validation_manifest.json",
  "validation_summary.json"
]
```

`motion_kinematics_1deg.csv`, `motion_audit_summary.json`, `gate_results.json`,
`validation_summary.json`, and `validation_manifest.json` do not exist in this
terminal state. No stale substitute is used. Acceptance gates were **NOT_COMPUTED**;
all 31 are preserved with handoff disposition OPEN. NCR formulas were
**NOT_COMPUTED**; NCR-01 through NCR-08 are preserved with handoff disposition
OPEN. The package is **NOT RELEASED**, and release packaging is not authorized.

### Acceptance gates (not computed; handoff-open)

```json
[
  {
    "evidence": null,
    "gate_id": "AP242-STOWED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "BREP-VALID-STOWED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "INTERFERENCE-STOWED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "INTENTIONAL-FIT-REGISTER-STOWED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "CLEARANCE-EVIDENCE-STOWED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "AP242-DEPLOYED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "BREP-VALID-DEPLOYED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "INTERFERENCE-DEPLOYED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "INTENTIONAL-FIT-REGISTER-DEPLOYED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "CLEARANCE-EVIDENCE-DEPLOYED",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "STATE-PARITY",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "OCCURRENCE-TRANSFORMS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "OCCURRENCE-BOM-RECONCILIATION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "DOD-POSITIVE-DEPLOYED-LOCKS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "DOD-POSITIVE-STOWED-RETENTION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "DOD-CLOSED-ROUTE-ENDS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "ARM-KINEMATICS-ENDPOINTS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "ARM-LENGTH",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "ARM-SURFACE-QUALITY",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "CROSSHEAD-TRAVEL",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "NORMAL-BODY-OML",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "ARM-MODULE-HARD-ENVELOPE",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "RIGID-LENGTH",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "SYSTEM-MASS",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "ATTACHMENT-COHESION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "RECOVERY-LOAD-PATH",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "PROCUREMENT-DEFINITION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "MOTION-FULL-MECHANISM",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  },
  {
    "evidence": null,
    "gate_id": "INTENTIONAL-FIT-REGISTER-MOTION",
    "handoff_disposition": "OPEN",
    "measured": null,
    "note": "gate_results.json absent after terminal validator failure; no acceptance status was computed",
    "requirement": null,
    "status": "NOT_COMPUTED"
  }
]
```

### NCR-01 through NCR-08 (not computed; handoff-open)

```json
[
  {
    "controlling_gates": [
      {
        "gate_id": "AP242-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "AP242-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "STATE-PARITY",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "ATTACHMENT-COHESION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "RECOVERY-LOAD-PATH",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-01"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "STATE-PARITY",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "ATTACHMENT-COHESION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "RECOVERY-LOAD-PATH",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-02"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "PROCUREMENT-DEFINITION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-CLOSED-ROUTE-ENDS",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "CLEARANCE-EVIDENCE-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "CLEARANCE-EVIDENCE-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "MOTION-FULL-MECHANISM",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-03"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "INTERFERENCE-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "INTERFERENCE-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "CLEARANCE-EVIDENCE-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "CLEARANCE-EVIDENCE-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "MOTION-FULL-MECHANISM",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-04"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "ATTACHMENT-COHESION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-POSITIVE-DEPLOYED-LOCKS",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-POSITIVE-STOWED-RETENTION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "PROCUREMENT-DEFINITION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "MOTION-FULL-MECHANISM",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-05"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "ATTACHMENT-COHESION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "DOD-CLOSED-ROUTE-ENDS",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "PROCUREMENT-DEFINITION",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "MOTION-FULL-MECHANISM",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-06"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "AP242-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "BREP-VALID-STOWED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "AP242-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "BREP-VALID-DEPLOYED",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "ARM-SURFACE-QUALITY",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-07"
  },
  {
    "controlling_gates": [
      {
        "gate_id": "STATE-PARITY",
        "status": "NOT_COMPUTED"
      },
      {
        "gate_id": "OCCURRENCE-TRANSFORMS",
        "status": "NOT_COMPUTED"
      }
    ],
    "formula_basis": "Formula was not evaluated because gate_results.json is absent; handoff treats the NCR as open without fabricating an acceptance status",
    "formula_status": "NOT_COMPUTED",
    "handoff_disposition": "OPEN",
    "ncr_id": "NCR-08"
  }
]
```


## Latest endpoint and motion metrics

```json
{
  "endpoints": {
    "DEPLOYED": {
      "boolean_blocked_pair_count": 0,
      "broadphase_candidate_count": 1448,
      "clear_pair_count": 47168,
      "distance_blocked_pair_count": 0,
      "documented_positive_volume_pair_count": 110,
      "exact_distance_measured_pair_count": 1797,
      "intentional_fit_register_error_count": 0,
      "intentional_fit_register_valid_record_count": 110,
      "minimum_exact_noninterfering_clearance_mm": 0.0,
      "near_noninterfering_candidate_pair_count": 1797,
      "solid_count": 308,
      "step": {
        "advanced_face_count": 3387,
        "ap242_schema_detected": true,
        "brep_with_voids_count": 0,
        "closed_shell_count": 144,
        "faceted_or_tessellated_total": 0,
        "file_size_bytes": 15424087,
        "manifold_solid_brep_count": 144,
        "millimetre_length_unit_detected": true,
        "nauo_count": 288,
        "product_count": 131,
        "schema_record": "'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4 }'",
        "sha256": "0c72b5f108cc92e9c6a3dd36fbb7643fb252bc95a4b0e6f590b3e81e0053ca6e",
        "unnamed_nauo_name_count": 0,
        "unnamed_product_count": 0
      },
      "unauthorized_positive_volume_pair_count": 0,
      "unordered_pair_count": 47278,
      "unused_intentional_fit_exception_ids": []
    },
    "STOWED": {
      "boolean_blocked_pair_count": 0,
      "broadphase_candidate_count": 1389,
      "clear_pair_count": 47178,
      "distance_blocked_pair_count": 0,
      "documented_positive_volume_pair_count": 100,
      "exact_distance_measured_pair_count": 1745,
      "intentional_fit_register_error_count": 0,
      "intentional_fit_register_valid_record_count": 100,
      "minimum_exact_noninterfering_clearance_mm": 0.0,
      "near_noninterfering_candidate_pair_count": 1745,
      "solid_count": 308,
      "step": {
        "advanced_face_count": 2941,
        "ap242_schema_detected": true,
        "brep_with_voids_count": 0,
        "closed_shell_count": 144,
        "faceted_or_tessellated_total": 0,
        "file_size_bytes": 13785070,
        "manifold_solid_brep_count": 144,
        "millimetre_length_unit_detected": true,
        "nauo_count": 288,
        "product_count": 131,
        "schema_record": "'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4 }'",
        "sha256": "b1a46e1455ec89548abfb82db5c2f5a2e3a330b09efd55a7e7ec168b731f23e2",
        "unnamed_nauo_name_count": 0,
        "unnamed_product_count": 0
      },
      "unauthorized_positive_volume_pair_count": 0,
      "unordered_pair_count": 47278,
      "unused_intentional_fit_exception_ids": []
    }
  },
  "motion": {
    "angle_increment_deg": 1,
    "boolean_blocked_pair_count": 0,
    "category_b_rigid_observation_count": 681,
    "category_b_rigid_unique_pair_count": 33,
    "crosshead_travel_0_to_80_mm": null,
    "data_row_count": 1447875,
    "distance_blocked_pair_count": 0,
    "documented_positive_volume_pair_count": 1215,
    "elapsed_seconds": null,
    "exact_common_status_counts": {
      "DONE": 34314,
      "NOT_RUN_AABB_SEPARATED": 1413561
    },
    "exact_distance_status_counts": {
      "DONE": 47655,
      "NOT_RUN_OUTSIDE_NEAR_LIMIT": 1398156,
      "ZERO_BY_POSITIVE_COMMON": 2064
    },
    "execution_state": "TERMINAL_AUDIT_FAILURE",
    "execution_topology": null,
    "intentional_fit_exception_use_counts": {
      "FIT-ACTUATOR-RETAINER-GS19-MOVING": 81,
      "FIT-ACTUATOR-RETAINER-HBD-MOVING": 81,
      "FIT-CIRCLIP-FULLFLOW": 81,
      "FIT-STOW-INHIBIT-KEEPER-1": 81,
      "FIT-STOW-INHIBIT-KEEPER-2": 81,
      "FIT-STOW-INHIBIT-KEEPER-3": 81,
      "FIT-THREAD-ARM-STOP-1-1": 81,
      "FIT-THREAD-ARM-STOP-1-2": 81,
      "FIT-THREAD-ARM-STOP-2-1": 81,
      "FIT-THREAD-ARM-STOP-2-2": 81,
      "FIT-THREAD-ARM-STOP-3-1": 81,
      "FIT-THREAD-ARM-STOP-3-2": 81,
      "FIT-THREAD-WP04-MOVING-SLEEVE-1": 81,
      "FIT-THREAD-WP04-MOVING-SLEEVE-2": 81,
      "FIT-THREAD-WP04-MOVING-SLEEVE-3": 81
    },
    "intentional_fit_register_error_count": 0,
    "kinematics_artifact_available": false,
    "last_audit_failure": "work/handoff_tools/LAST_AUDIT_FAILURE.json",
    "line_count_including_header": 1447876,
    "maximum_angle_deg": 80,
    "maximum_closure_residual_abs_mm": null,
    "merged_motion_audit": {
      "path": "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz",
      "sha256": "4da00e87fd63199a29c0f4e97e9f9502da604ed48cf3f8875a9300778828fee6",
      "size_bytes": 22925903
    },
    "minimum_angle_deg": 0,
    "minimum_exact_noninterfering_clearance_mm": null,
    "motion_kinematics_status": "NOT_COMPUTED",
    "motion_summary_status": "NOT_COMPUTED",
    "nonempty_error_row_count": 0,
    "nonrigid_involved_observation_count": 168,
    "nonrigid_involved_unique_pair_count": 6,
    "pair_rows_per_sample": 17875,
    "positive_volume_pair_count": 2064,
    "result_counts": {
      "CLEAR_OR_CONTACT": 1445811,
      "DOCUMENTED_POSITIVE_VOLUME": 1215,
      "UNAUTHORIZED_POSITIVE_VOLUME": 849
    },
    "sample_count": 81,
    "source": "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz",
    "summary_artifact_available": false,
    "track_validation_error_count": null,
    "unauthorized_angle_degrees": [
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      36,
      37,
      38,
      39,
      40,
      41,
      42,
      43,
      44,
      45,
      46,
      47,
      48,
      49,
      50,
      51,
      52,
      53,
      54,
      55,
      56,
      57,
      58,
      59,
      60,
      61,
      62,
      63,
      64,
      65,
      66,
      67,
      68,
      69,
      70,
      71,
      72,
      73,
      74,
      75,
      76,
      77,
      78,
      79
    ],
    "unauthorized_classification_observation_counts": {
      "FIXED_MOVING": 516,
      "FLEXIBLE_MOVING": 168,
      "MOVING_MOVING": 165
    },
    "unauthorized_positive_volume_pair_count": 849,
    "unauthorized_unique_pair_count": 39,
    "used_intentional_fit_exception_ids": [
      "FIT-ACTUATOR-RETAINER-GS19-MOVING",
      "FIT-ACTUATOR-RETAINER-HBD-MOVING",
      "FIT-CIRCLIP-FULLFLOW",
      "FIT-STOW-INHIBIT-KEEPER-1",
      "FIT-STOW-INHIBIT-KEEPER-2",
      "FIT-STOW-INHIBIT-KEEPER-3",
      "FIT-THREAD-ARM-STOP-1-1",
      "FIT-THREAD-ARM-STOP-1-2",
      "FIT-THREAD-ARM-STOP-2-1",
      "FIT-THREAD-ARM-STOP-2-2",
      "FIT-THREAD-ARM-STOP-3-1",
      "FIT-THREAD-ARM-STOP-3-2",
      "FIT-THREAD-WP04-MOVING-SLEEVE-1",
      "FIT-THREAD-WP04-MOVING-SLEEVE-2",
      "FIT-THREAD-WP04-MOVING-SLEEVE-3"
    ]
  },
  "motion_variants": {
    "DEPLOYED": {
      "exact_brep_variant_status": "PASS",
      "exact_brep_variant_track_count": 6,
      "exact_brep_variant_tracks": [
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-1",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-1",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-2",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-2",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-3",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-3",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        }
      ],
      "mode_counts": {
        "ARM_KINEMATIC": 3,
        "AXIAL_COMPRESSION_SPRING_KINEMATIC": 1,
        "CROSSHEAD_KINEMATIC": 1,
        "HOLD_STOWED": 32,
        "KEYFRAMED_EXACT_BREP_VARIANTS": 6,
        "KEYFRAMED_TRANSFORMS": 15,
        "PARENT_RIGID": 35
      },
      "track_count": 93
    },
    "STOWED": {
      "exact_brep_variant_status": "PASS",
      "exact_brep_variant_track_count": 6,
      "exact_brep_variant_tracks": [
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-1",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-1",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-2",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-2",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 80,
            "STOWED": 1
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "STOW-DOG-SPRING-3",
          "process_basis": "The dog releases before appreciable arm travel: the exact 3.78 mm stowed B-rep is used at 0 degrees and the exact 0.28 mm retracted B-rep at every 1..80 degree sample.",
          "sample_count": 81,
          "status": "PASS"
        },
        {
          "covers_every_integer_angle_0_to_80": true,
          "endpoint_variant_counts": {
            "DEPLOYED": 1,
            "STOWED": 80
          },
          "maximum_angle_deg": 80,
          "minimum_angle_deg": 0,
          "mode": "KEYFRAMED_EXACT_BREP_VARIANTS",
          "occurrence_id": "LOCK-SPRING-3",
          "process_basis": "The lock remains retracted through 79 degrees and advances at 80 degrees: each sample audits exactly the installed-length endpoint B-rep matching the lock-dog keyframe.",
          "sample_count": 81,
          "status": "PASS"
        }
      ],
      "mode_counts": {
        "ARM_KINEMATIC": 3,
        "AXIAL_COMPRESSION_SPRING_KINEMATIC": 1,
        "CROSSHEAD_KINEMATIC": 1,
        "HOLD_STOWED": 32,
        "KEYFRAMED_EXACT_BREP_VARIANTS": 6,
        "KEYFRAMED_TRANSFORMS": 15,
        "PARENT_RIGID": 35
      },
      "track_count": 93
    }
  }
}
```

## Hierarchy, products, occurrences, envelope, length, mass, and reserve

```json
{
  "dimensions_mass_reserve": {
    "arm_module_stowed_bbox_mm": {
      "xmax": 28.5,
      "xmin": -28.5,
      "ymax": 28.550301090003998,
      "ymin": -28.5,
      "zmax": 1754.3135211750873,
      "zmin": 829.6837722339836
    },
    "arm_module_stowed_od_mm": 57.050301090004,
    "crosshead_travel_independent_mm": 15.05503437113498,
    "crosshead_travel_reimported_mm": 15.055034371129977,
    "deployed_all_geometry_length_mm": 2522.25,
    "deployed_rigid_length_mm": 2031.0000001,
    "mass_invalid_occurrence_ids": [],
    "mass_reserve_kg": 6.410945597270372,
    "mass_unresolved_occurrence_ids": [],
    "normal_body_oml_xy_spans_mm": {
      "AFT-SHELL-001": 53.0000002,
      "FIXED-SECTOR-1": 24.00691983422691,
      "FIXED-SECTOR-2": 27.634148354041656,
      "FIXED-SECTOR-3": 24.006919934225674,
      "FWD-SHELL-001": 53.00000020118784
    },
    "stowed_all_geometry_length_mm": 2031.0000001,
    "stowed_rigid_length_mm": 2031.0000001,
    "system_mass_kg": 11.729054402729629
  },
  "hierarchy": {
    "DEPLOYED": {
      "assembly_path_count": 9,
      "assembly_paths": [
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY",
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY/190_MANDATORY_HARDWARE_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/331_ARM_1_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/332_ARM_2_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/333_ARM_3_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/390_MANDATORY_HARDWARE_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY/590_MANDATORY_HARDWARE_ASSY"
      ],
      "authored_leaf_occurrence_count": 279,
      "authored_occurrence_count": 279,
      "authored_part_definition_count": 121,
      "classification_counts": {
        "CONSUMED": 5,
        "FIXED": 181,
        "FLEXIBLE": 18,
        "MOVING": 67,
        "SOFTGOOD": 8
      },
      "hierarchy_audit_accepted": true,
      "hierarchy_issue_count": 0,
      "identity_transform_occurrence_count": 2,
      "imported_leaf_occurrence_count": 279,
      "millimetre_length_unit_detected": true,
      "missing_assembly_paths": [],
      "occurrence_transform_rows": 279,
      "occurrence_transforms": [
        {
          "classification": "FIXED",
          "identity_transform": true,
          "occurrence_id": "NOSE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              0.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BALLAST-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              170.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-SHELL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              340.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-RING-01",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              340.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-RING-02",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CARTRIDGE-CARRIER-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              346.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CARTRIDGE-CARRIER-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              435.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "COLLECTION-MANIFOLD-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              442.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-1",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-2",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-3",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-1",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-2",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-3",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-3",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-TRIGGER-HSG-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              500.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "WATER-BOBBIN-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              520.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-INLET-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              -1.0,
              0.0,
              5.551115123125783e-16
            ],
            [
              1.0,
              1.1102230246251565e-16,
              0.0,
              5.0
            ],
            [
              0.0,
              0.0,
              1.0,
              540.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "FULLFLOW-VALVE-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              1.0,
              1.1102230246251565e-16,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              859.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-MANIFOLD-FEED-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-1",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              600.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-2",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              700.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-3",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              800.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -10.25
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-1-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -4.75
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-1-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.75
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-1-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.9
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-1-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              5.9
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              9.45
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-1-1",
          "transform_matrix_3x4": [
            [
              0.49649919013089905,
              0.0,
              0.8680371848022188,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -1.75
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-1-2",
          "transform_matrix_3x4": [
            [
              0.49649919013089905,
              0.0,
              0.8680371848022188,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              1.75
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-1-BELL",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              27.905158843111455
            ],
            [
              0.0,
              1.0,
              0.0,
              -6.4
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-1-BELL",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              27.905158843111455
            ],
            [
              0.0,
              1.0,
              0.0,
              5.6
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-1-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -6.4
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-1-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              5.6
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.323726810063954
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              6.31503652694835
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              13.5
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-1",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              1.0,
              11.17
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              17.0
            ],
            [
              0.0,
              1.0,
              0.0,
              3.4
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              17.0
            ],
            [
              0.0,
              1.0,
              0.0,
              8.825
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.323726810063954
            ],
            [
              0.0,
              1.0,
              0.0,
              3.65
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.984807753012208,
              1.0933562422235177e-16,
              10.323726810063954
            ],
            [
              0.0,
              1.1102230246251565e-16,
              -1.0,
              6.9
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.668409523618227
            ],
            [
              0.0,
              1.0,
              0.0,
              7.15
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -8.999999999999996
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              15.588457268119896
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -8.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              15.588457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -0.12323961120949889
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              20.713457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-2-1",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -4.886379332023912
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              17.963457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-2-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -13.11362066797608
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              13.213457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-2-1",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -3.890450117671808
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              18.538457268119895
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-2-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -14.109549882328185
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              12.638457268119897
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -17.18394006576294
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              10.863457268119898
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-2-1",
          "transform_matrix_3x4": [
            [
              -0.2482495950654494,
              -0.8660254037844387,
              -0.43401859240110924,
              -7.484455543377228
            ],
            [
              0.42998091161175866,
              -0.4999999999999998,
              0.751742253468249,
              16.463457268119896
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-2-2",
          "transform_matrix_3x4": [
            [
              -0.2482495950654494,
              -0.8660254037844387,
              -0.43401859240110924,
              -10.515544456622765
            ],
            [
              0.42998091161175866,
              -0.4999999999999998,
              0.751742253468249,
              14.713457268119896
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-2-BELL",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -8.410016837335313
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              27.3665764547745
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-2-BELL",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -18.802321682748577
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              21.366576454774503
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-2-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -3.457437415779588
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              18.788457268119895
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-2-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -13.849742261192851
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              12.788457268119899
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -5.1618634050319745
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              8.94060967924587
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -3.157518263474173
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.468982058163923
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -6.749999999999997
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              11.691342951089922
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              0.0
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-2",
          "transform_matrix_3x4": [
            [
              -5.55111512312578e-17,
              -0.8660254037844387,
              -0.4999999999999998,
              -5.584999999999997
            ],
            [
              9.61481343191782e-17,
              -0.4999999999999998,
              0.8660254037844387,
              9.67350376027218
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -11.444486372867088
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              13.02243186433546
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -16.142674188397667
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              10.30993186433546
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -8.322856128845176
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              7.115609679245871
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.4924038765061039,
              0.8660254037844387,
              -11.137438691144602
            ],
            [
              0.15038373318043535,
              0.8528685319524433,
              0.4999999999999999,
              5.490609679245871
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -11.52628639886785
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.664113665429227
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -9.000000000000007
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -15.58845726811989
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -9.000000000000007
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -15.58845726811989
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -17.8767603887905
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -10.463457268119885
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-3-1",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -13.11362066797609
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -13.213457268119889
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-3-2",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -4.886379332023925
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -17.963457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-3-1",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -14.109549882328194
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -12.638457268119888
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-3-2",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -3.8904501176718203
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -18.538457268119892
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -0.8160599342370656
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -20.313457268119894
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-3-1",
          "transform_matrix_3x4": [
            [
              -0.24824959506544975,
              0.8660254037844384,
              -0.4340185924011098,
              -10.515544456622774
            ],
            [
              -0.4299809116117585,
              -0.5000000000000004,
              -0.7517422534682487,
              -14.71345726811989
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-3-2",
          "transform_matrix_3x4": [
            [
              -0.24824959506544975,
              0.8660254037844384,
              -0.4340185924011098,
              -7.48445554337724
            ],
            [
              -0.4299809116117585,
              -0.5000000000000004,
              -0.7517422534682487,
              -16.463457268119893
            ],
            [
              -0.8680371848022188,
              0.0,
              0.49649919013089905,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-3-BELL",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -19.495142005776145
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -20.966576454774486
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-3-BELL",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -9.102837160362885
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -26.96657645477449
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              895.6539870809291
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-3-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -14.542562584220413
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -12.388457268119888
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-3-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -4.150257738807152
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -18.388457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -5.161863405031981
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -8.940609679245867
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -3.1575182634741767
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -5.468982058163921
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -6.750000000000006
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -11.691342951089919
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              0.0
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-3",
          "transform_matrix_3x4": [
            [
              -5.551115123125788e-17,
              0.8660254037844384,
              -0.5000000000000004,
              -5.585000000000005
            ],
            [
              -9.614813431917817e-17,
              -0.5000000000000004,
              -0.8660254037844384,
              -9.673503760272176
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -5.555513627132917
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -16.422431864335454
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -0.8573258116023394
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -19.134931864335456
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -2.000870681218781
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -10.76560967924587
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              -0.49240387650610434,
              -0.8660254037844384,
              0.8137118810806441
            ],
            [
              -0.1503837331804353,
              -0.852868531952443,
              0.5000000000000003,
              -12.39060967924587
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              0.8578768752496173
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -12.814113665429225
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-SPIDER",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              920.2213289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-FIXED-SEAT",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              1082.7763632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-MOVING-SEAT",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              917.7213289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-GUIDE",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-BODY-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              960.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-ROD-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-BODY-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              960.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-ROD-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-FIXED-YOKE",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-PIN-FIXED",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              11.513139720814415
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              8.94134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-CLIP-FIXED",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              2.67968060221314
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              14.04134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-PIN-MOVING",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              11.513139720814415
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              8.94134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-CLIP-MOVING",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              2.67968060221314
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              14.04134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-FIXED-YOKE",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-PIN-FIXED",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              5.500000000000002
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-CLIP-FIXED",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              -4.699999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-PIN-MOVING",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              5.500000000000002
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-CLIP-MOVING",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              -4.699999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              912.9713289177334
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-GAS-MAIN-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              11.0
            ],
            [
              0.0,
              0.0,
              1.0,
              870.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-PILOT-LINE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              5.629165124598849
            ],
            [
              0.0,
              1.0,
              0.0,
              -3.2500000000000027
            ],
            [
              0.0,
              0.0,
              1.0,
              870.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "ROUTE-BOWDEN-SHEATH-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              557.5
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "ROUTE-BOWDEN-WIRE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              556.8
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-GAS-MAIN-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              2.283480459988643
            ],
            [
              0.0,
              1.0,
              0.0,
              26.100301090003732
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-GAS-MAIN-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              2.283480459988643
            ],
            [
              0.0,
              1.0,
              0.0,
              26.100301090003732
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-PILOT-LINE-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              21.46178356037158
            ],
            [
              0.0,
              1.0,
              0.0,
              -15.027702632397418
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-PILOT-LINE-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              21.46178356037158
            ],
            [
              0.0,
              1.0,
              0.0,
              -15.027702632397418
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-BOWDEN-SHEATH-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -23.74526402036023
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.07259845760632
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-BOWDEN-SHEATH-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -23.74526402036023
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.07259845760632
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-GAS-MAIN-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-PILOT-LINE-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-BOWDEN-SHEATH-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FULLFLOW-MANIFOLD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.961004211822308
            ],
            [
              0.0,
              1.0,
              0.0,
              22.414380707064275
            ],
            [
              0.0,
              0.0,
              1.0,
              1725.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-MANIFOLD-BRACKET",
          "transform_matrix_3x4": [
            [
              0.08715574274765814,
              -0.9961946980917455,
              0.0,
              1.961004211822308
            ],
            [
              0.9961946980917455,
              0.08715574274765814,
              0.0,
              22.414380707064275
            ],
            [
              0.0,
              0.0,
              1.0,
              1725.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-SHELL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1635.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-ROUTE-RING-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-REACTION-BULKHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1655.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.6
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -9.799999999999997
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              16.974097914175
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -9.80000000000001
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -16.974097914174994
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-FOLLOWER-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1830.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "WP04-EJECTOR-SPRING",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1660.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1732.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-001",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -4.685141163918161e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -21.1
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-SEAR-001",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -5.395683899678261e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -24.3
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-SEAR-CLIP-001",
          "transform_matrix_3x4": [
            [
              1.0,
              3.3306690738754696e-16,
              0.0,
              -6.389333506717776e-15
            ],
            [
              -3.3306690738754696e-16,
              1.0,
              0.0,
              -28.775000000000002
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BODY-HARDPOINT-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-SERVICE-THROAT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP05-DOOR-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              -1.0,
              27.999999999999996
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              2000.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-HINGE-PIN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              28.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -7.5
            ],
            [
              0.0,
              0.0,
              1.0,
              2028.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-HINGE-CLIP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              28.0
            ],
            [
              0.0,
              1.0,
              0.0,
              6.7
            ],
            [
              0.0,
              0.0,
              1.0,
              2028.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-1",
          "transform_matrix_3x4": [
            [
              0.7071067811865476,
              -0.7071067811865475,
              0.0,
              16.44023266258723
            ],
            [
              0.7071067811865475,
              0.7071067811865476,
              0.0,
              16.440232662587228
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-2",
          "transform_matrix_3x4": [
            [
              -0.7071067811865475,
              -0.7071067811865476,
              0.0,
              -16.440232662587228
            ],
            [
              0.7071067811865476,
              -0.7071067811865475,
              0.0,
              16.44023266258723
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-3",
          "transform_matrix_3x4": [
            [
              -0.7071067811865477,
              0.7071067811865475,
              0.0,
              -16.440232662587235
            ],
            [
              -0.7071067811865475,
              -0.7071067811865477,
              0.0,
              -16.440232662587228
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-4",
          "transform_matrix_3x4": [
            [
              0.7071067811865474,
              0.7071067811865477,
              0.0,
              16.440232662587224
            ],
            [
              -0.7071067811865477,
              0.7071067811865474,
              0.0,
              -16.440232662587235
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-01",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-02",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-03",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-04",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-05",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-06",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-07",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-08",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2276.5
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-BAND-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.1102230246251565e-16,
              -1.0,
              0.0
            ],
            [
              0.0,
              1.0,
              1.1102230246251565e-16,
              2276.5
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-BAND-2",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              1.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              2276.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HARNESS-TERMINAL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-XP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-XN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-YP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-YN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "TETHER-THIMBLE-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "TETHER-THIMBLE-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-TETHER-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.5
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-CLIP-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.7
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.5
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-CLIP-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.7
            ],
            [
              0.0,
              0.0,
              1.0,
              2018.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": true,
          "occurrence_id": "WP05-DOOR-LANYARD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              0.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.1
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              0.0
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.1
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.1083053532283548e-15
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              18.1
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.1083053532283548e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              18.1
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              2.2166107064567096e-15
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              1.0,
              0.0,
              2.2166107064567096e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -3.324916059685064e-15
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              -18.1
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -3.324916059685064e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-3",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-3",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-3",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.232595164407831e-32,
              -1.0,
              -1.1102230246251565e-16,
              2.586819647376615e-15
            ],
            [
              1.1102230246251565e-16,
              1.1102230246251565e-16,
              -1.0,
              23.3
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-2",
          "transform_matrix_3x4": [
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.17839190817742
            ],
            [
              -5.551115123125784e-17,
              -0.8660254037844386,
              0.5000000000000001,
              -11.650000000000002
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-3",
          "transform_matrix_3x4": [
            [
              9.614813431917817e-17,
              0.5000000000000004,
              -0.8660254037844384,
              20.178391908177414
            ],
            [
              -5.551115123125788e-17,
              0.8660254037844384,
              0.5000000000000004,
              -11.650000000000011
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "NOSE-BALLAST-TAPER-PIN-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              1.0,
              -15.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              170.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "FULLFLOW-VALVE-CIRCLIP-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              883.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-BOBBIN-SERVICE-CAP-001",
          "transform_matrix_3x4": [
            [
              0.984807753012208,
              -0.17364817766693033,
              0.0,
              0.0
            ],
            [
              0.17364817766693033,
              0.984807753012208,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              500.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              -0.984807753012208,
              1.0933562422235177e-16,
              9.837511912596549
            ],
            [
              0.0,
              1.1102230246251565e-16,
              1.0,
              -1.8
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              897.3422211862165
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              -0.984807753012208,
              1.0933562422235177e-16,
              10.80994170753136
            ],
            [
              0.0,
              1.1102230246251565e-16,
              1.0,
              -1.8
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              891.8272977693481
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              9.124352264812732
            ],
            [
              0.0,
              1.0,
              0.0,
              -7.8
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              9.124352264812732
            ],
            [
              0.0,
              1.0,
              0.0,
              7.8
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-1-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.534237417304098
            ],
            [
              0.0,
              1.0,
              0.0,
              -8.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-1-2",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.534237417304098
            ],
            [
              0.0,
              1.0,
              0.0,
              8.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              0.4924038765061037,
              -0.8660254037844387,
              -3.3599102294862826
            ],
            [
              0.15038373318043535,
              -0.8528685319524433,
              -0.49999999999999967,
              9.41953522634065
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              897.3422211862165
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              0.4924038765061037,
              -0.8660254037844387,
              -3.8461251269536874
            ],
            [
              0.15038373318043535,
              -0.8528685319524433,
              -0.49999999999999967,
              10.261684132151089
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              891.8272977693481
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              2.192822017112259
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              11.8019208544059
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -11.317174281924984
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              4.001920854405904
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-2-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              1.6610845216234638
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              13.12291721288192
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-2-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -12.195321938927556
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.122917212881924
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.49240387650610457,
              0.8660254037844384,
              -6.477601683110267
            ],
            [
              -0.1503837331804353,
              0.8528685319524428,
              -0.5000000000000006,
              -7.6195352263406475
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              897.3422211862165
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.49240387650610457,
              0.8660254037844384,
              -6.963816580577673
            ],
            [
              -0.1503837331804353,
              0.8528685319524428,
              -0.5000000000000006,
              -8.461684132151085
            ],
            [
              -0.984807753012208,
              -0.17364817766693041,
              1.9278820503002604e-17,
              891.8272977693481
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -11.317174281924988
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -4.0019208544058955
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              2.1928220171122503
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -11.801920854405903
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-3-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -12.19532193892756
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -5.122917212881916
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-3-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              1.6610845216234549
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -13.122917212881923
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-GUIDE-SCREW-1",
          "transform_matrix_3x4": [
            [
              5.551115123125784e-17,
              0.8660254037844386,
              -0.5000000000000001,
              12.100000000000003
            ],
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.957814771583415
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              900.75
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-GUIDE-SCREW-2",
          "transform_matrix_3x4": [
            [
              5.551115123125784e-17,
              0.8660254037844386,
              -0.5000000000000001,
              12.100000000000003
            ],
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.957814771583415
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              1082.7763633888685
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-LOCK-SCREW-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              887.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-AFT-RAIL-SUPPORT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1848.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-1-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              20.0
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              0.0
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-1-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              20.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-2-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              0.8660254037844387,
              1.0605752387249069e-16,
              -9.999999999999996
            ],
            [
              0.8660254037844387,
              0.4999999999999998,
              6.123233995736764e-17,
              17.320508075688778
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-2-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -9.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              17.320508075688778
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-3-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              -0.8660254037844384,
              -1.0605752387249065e-16,
              -10.00000000000001
            ],
            [
              -0.8660254037844384,
              0.5000000000000004,
              6.123233995736771e-17,
              -17.32050807568877
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-3-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -10.00000000000001
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -17.32050807568877
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.7
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -6.349999999999997
            ],
            [
              0.0,
              1.0,
              0.0,
              10.998522628062371
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -6.350000000000005
            ],
            [
              0.0,
              1.0,
              0.0,
              -10.998522628062366
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              7.500000000000002
            ],
            [
              0.0,
              1.0,
              0.0,
              12.990381056766578
            ],
            [
              0.0,
              0.0,
              1.0,
              1827.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -15.0
            ],
            [
              0.0,
              1.0,
              0.0,
              1.83697019872103e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              1827.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              7.500000000000002
            ],
            [
              0.0,
              1.0,
              0.0,
              -12.990381056766578
            ],
            [
              0.0,
              0.0,
              1.0,
              1827.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LATCH-SUPPORT-BRACKET",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1736.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-SCREW-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              -1.0,
              -1.2246467991473532e-16,
              -6.000000000000005
            ],
            [
              -1.0,
              2.220446049250313e-16,
              2.719262146893782e-32,
              -23.2
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1744.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-SCREW-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              -1.0,
              -1.2246467991473532e-16,
              5.999999999999995
            ],
            [
              -1.0,
              2.220446049250313e-16,
              2.719262146893782e-32,
              -23.200000000000003
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1744.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.22576396401454
            ],
            [
              0.0,
              1.0,
              0.0,
              11.099999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.359357947053562e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              22.2
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -19.22576396401454
            ],
            [
              0.0,
              1.0,
              0.0,
              11.099999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -19.225763964014536
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.100000000000001
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-5",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -4.0780738411606855e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -22.2
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-6",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.225763964014533
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.10000000000001
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        }
      ],
      "root_name": "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_ASSY",
      "step_nauo_count": 288,
      "step_product_count": 131,
      "top_level_assembly_names": [
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY"
      ],
      "unexpected_assembly_paths": []
    },
    "STOWED": {
      "assembly_path_count": 9,
      "assembly_paths": [
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY",
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY/190_MANDATORY_HARDWARE_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/331_ARM_1_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/332_ARM_2_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/333_ARM_3_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY/390_MANDATORY_HARDWARE_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY/590_MANDATORY_HARDWARE_ASSY"
      ],
      "authored_leaf_occurrence_count": 279,
      "authored_occurrence_count": 279,
      "authored_part_definition_count": 121,
      "classification_counts": {
        "CONSUMED": 5,
        "FIXED": 181,
        "FLEXIBLE": 18,
        "MOVING": 67,
        "SOFTGOOD": 8
      },
      "hierarchy_audit_accepted": true,
      "hierarchy_issue_count": 0,
      "identity_transform_occurrence_count": 2,
      "imported_leaf_occurrence_count": 279,
      "millimetre_length_unit_detected": true,
      "missing_assembly_paths": [],
      "occurrence_transform_rows": 279,
      "occurrence_transforms": [
        {
          "classification": "FIXED",
          "identity_transform": true,
          "occurrence_id": "NOSE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              0.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BALLAST-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              170.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-SHELL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              340.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-RING-01",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              340.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-RING-02",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              344.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CARTRIDGE-CARRIER-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              346.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CARTRIDGE-CARRIER-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              435.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "CO2-CARTRIDGE-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              348.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "COLLECTION-MANIFOLD-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              442.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PUNCTURE-HEAD-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -9.5
            ],
            [
              0.0,
              1.0,
              0.0,
              9.5
            ],
            [
              0.0,
              0.0,
              1.0,
              435.2
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-1",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-2",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-1-3",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -0.49999999999999994,
              0.0,
              12.124355652982143
            ],
            [
              0.49999999999999994,
              0.8660254037844387,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -12.124355652982143
            ],
            [
              0.0,
              1.0,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-1",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-2",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-2-3",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -0.49999999999999994,
              0.0,
              -12.124355652982143
            ],
            [
              0.49999999999999994,
              -0.8660254037844388,
              0.0,
              6.999999999999999
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              451.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-FWD-CLOSURE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              450.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-AFT-CLOSURE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              881.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-ISOLATION-VALVE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-COLLECTION-LINE-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -2.5717582782094417e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              444.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-BAND-3-3",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -3.1086244689504383e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -14.0
            ],
            [
              0.0,
              0.0,
              1.0,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-TRIGGER-HSG-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              500.0
            ]
          ]
        },
        {
          "classification": "CONSUMED",
          "identity_transform": false,
          "occurrence_id": "WATER-BOBBIN-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              520.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-INLET-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              -1.0,
              0.0,
              5.551115123125783e-16
            ],
            [
              1.0,
              1.1102230246251565e-16,
              0.0,
              5.0
            ],
            [
              0.0,
              0.0,
              1.0,
              540.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "FULLFLOW-VALVE-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              1.0,
              1.1102230246251565e-16,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              859.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-MANIFOLD-FEED-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              447.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-1",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              600.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-2",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              700.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-FEED-CLAMP-3",
          "transform_matrix_3x4": [
            [
              0.3420201433256689,
              -0.9396926207859083,
              0.0,
              7.182423009839047
            ],
            [
              0.9396926207859083,
              0.3420201433256689,
              0.0,
              19.733545036504076
            ],
            [
              0.0,
              0.0,
              1.0,
              800.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-SECTOR-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ARM-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -10.25
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-1-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -4.75
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-1-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.75
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-1-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.9
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-1-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              5.9
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              9.45
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-1-1",
          "transform_matrix_3x4": [
            [
              0.3007518796992481,
              0.0,
              0.9537024204946577,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -1.75
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-1-2",
          "transform_matrix_3x4": [
            [
              0.3007518796992481,
              0.0,
              0.9537024204946577,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              1.75
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-1-BELL",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -6.4
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-1-BELL",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              5.6
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-1-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -6.4
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-1-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.0
            ],
            [
              0.0,
              1.0,
              0.0,
              5.6
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              22.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              6.31503652694835
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              17.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-1",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              1.0,
              11.17
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              17.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -3.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              17.0
            ],
            [
              0.0,
              1.0,
              0.0,
              2.425
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.323726810063954
            ],
            [
              0.0,
              1.0,
              0.0,
              3.95
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.984807753012208,
              1.0933562422235177e-16,
              10.323726810063954
            ],
            [
              0.0,
              1.1102230246251565e-16,
              -1.0,
              6.9
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.668409523618227
            ],
            [
              0.0,
              1.0,
              0.0,
              7.15
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -8.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              15.588457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -8.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              15.588457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -0.12323961120949889
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              20.713457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-2-1",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -4.886379332023912
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              17.963457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-2-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -13.11362066797608
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              13.213457268119896
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-2-1",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -3.890450117671808
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              18.538457268119895
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-2-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -14.109549882328185
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              12.638457268119897
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -17.18394006576294
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              10.863457268119898
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-2-1",
          "transform_matrix_3x4": [
            [
              -0.150375939849624,
              -0.8660254037844387,
              -0.4768512102473286,
              -7.484455543377228
            ],
            [
              0.26045876805547025,
              -0.4999999999999998,
              0.8259305237990825,
              16.463457268119896
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-2-2",
          "transform_matrix_3x4": [
            [
              -0.150375939849624,
              -0.8660254037844387,
              -0.4768512102473286,
              -10.515544456622765
            ],
            [
              0.26045876805547025,
              -0.4999999999999998,
              0.8259305237990825,
              14.713457268119896
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-2-BELL",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -6.457437415779586
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              23.984609690826527
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-2-BELL",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -16.84974226119285
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              17.98460969082653
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-2-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -3.457437415779588
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              18.788457268119895
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-2-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -13.849742261192851
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              12.788457268119899
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -10.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              19.05255888325765
            ],
            [
              0.0,
              0.0,
              1.0,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -3.157518263474173
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.468982058163923
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -8.499999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              14.722431864335459
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              0.0
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-2",
          "transform_matrix_3x4": [
            [
              -5.55111512312578e-17,
              -0.8660254037844387,
              -0.4999999999999998,
              -5.584999999999997
            ],
            [
              9.61481343191782e-17,
              -0.4999999999999998,
              0.8660254037844387,
              9.67350376027218
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -5.90192378864668
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              16.22243186433546
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -10.600111604177261
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              13.50993186433546
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -8.582663749980508
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              6.965609679245871
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.4924038765061039,
              0.8660254037844387,
              -11.137438691144602
            ],
            [
              0.15038373318043535,
              0.8528685319524433,
              0.4999999999999999,
              5.490609679245871
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -11.52628639886785
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.664113665429227
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -9.000000000000007
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -15.58845726811989
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CARRIER-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -9.000000000000007
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -15.58845726811989
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-PIN-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -17.8767603887905
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -10.463457268119885
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-3-1",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -13.11362066797609
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -13.213457268119889
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-BUSH-3-2",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -4.886379332023925
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -17.963457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-3-1",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -14.109549882328194
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -12.638457268119888
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-WASHER-3-2",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -3.8904501176718203
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -18.538457268119892
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "PIVOT-CLIP-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -0.8160599342370656
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -20.313457268119894
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-3-1",
          "transform_matrix_3x4": [
            [
              -0.1503759398496242,
              0.8660254037844384,
              -0.4768512102473293,
              -10.515544456622774
            ],
            [
              -0.2604587680554702,
              -0.5000000000000004,
              -0.8259305237990822,
              -14.71345726811989
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-3-2",
          "transform_matrix_3x4": [
            [
              -0.1503759398496242,
              0.8660254037844384,
              -0.4768512102473293,
              -7.48445554337724
            ],
            [
              -0.2604587680554702,
              -0.5000000000000004,
              -0.8259305237990822,
              -16.463457268119893
            ],
            [
              -0.9537024204946577,
              0.0,
              0.3007518796992481,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-3-BELL",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -17.542562584220416
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -17.584609690826518
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-3-BELL",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -7.150257738807156
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -23.584609690826525
            ],
            [
              0.0,
              0.0,
              1.0,
              909.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-PIN-3-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -14.542562584220413
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -12.388457268119888
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LINK-CLIP-3-CROSSHEAD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -4.150257738807152
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -18.388457268119893
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-PAD-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -11.000000000000009
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -19.052558883257646
            ],
            [
              0.0,
              0.0,
              1.0,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -3.1575182634741767
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -5.468982058163921
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.2840898683195
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -8.500000000000007
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -14.722431864335451
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-GUIDE-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              0.0
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-SPRING-3",
          "transform_matrix_3x4": [
            [
              -5.551115123125788e-17,
              0.8660254037844384,
              -0.5000000000000004,
              -5.585000000000005
            ],
            [
              -9.614813431917817e-17,
              -0.5000000000000004,
              -0.8660254037844384,
              -9.673503760272176
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-PIN-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -11.098076211353323
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -13.22243186433545
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -6.399888395822744
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -15.934931864335452
            ],
            [
              0.0,
              0.0,
              1.0,
              1630.306
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "LOCK-DOG-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -1.7410630600834487
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -10.915609679245868
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "LOCK-SPRING-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              -0.49240387650610434,
              -0.8660254037844384,
              0.8137118810806441
            ],
            [
              -0.1503837331804353,
              -0.852868531952443,
              0.5000000000000003,
              -12.39060967924587
            ],
            [
              -0.984807753012208,
              0.17364817766693041,
              1.9278820503002604e-17,
              894.5847594777823
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LOCK-BUSHING-3",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              0.8578768752496173
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -12.814113665429225
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              894.6455363399657
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-SPIDER",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              935.2763632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-FIXED-SEAT",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              1082.7763632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-MOVING-SEAT",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              932.7763632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-SPRING-GUIDE",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              6.000000000000002
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              -10.392304845413264
            ],
            [
              0.0,
              0.0,
              1.0,
              900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-BODY-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              960.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-ROD-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-BODY-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              960.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-ROD-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-FIXED-YOKE",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              6.750000000000002
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              11.69134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-PIN-FIXED",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              11.513139720814415
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              8.94134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GS19-CLIP-FIXED",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              2.67968060221314
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              14.04134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              1072.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-PIN-MOVING",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              11.513139720814415
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              8.94134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "GS19-CLIP-MOVING",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              2.67968060221314
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              14.04134295108992
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-FIXED-YOKE",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              1.7757378587636622e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-PIN-FIXED",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              5.500000000000002
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "HBD-CLIP-FIXED",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              -4.699999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1062.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-PIN-MOVING",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              5.500000000000002
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HBD-CLIP-MOVING",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              -14.5
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              -4.699999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              928.0263632888684
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-GAS-MAIN-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              11.0
            ],
            [
              0.0,
              0.0,
              1.0,
              870.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-PILOT-LINE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              5.629165124598849
            ],
            [
              0.0,
              1.0,
              0.0,
              -3.2500000000000027
            ],
            [
              0.0,
              0.0,
              1.0,
              870.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "ROUTE-BOWDEN-SHEATH-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              557.5
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "ROUTE-BOWDEN-WIRE-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              556.8
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-GAS-MAIN-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              2.283480459988643
            ],
            [
              0.0,
              1.0,
              0.0,
              26.100301090003732
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-GAS-MAIN-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              2.283480459988643
            ],
            [
              0.0,
              1.0,
              0.0,
              26.100301090003732
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-PILOT-LINE-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              21.46178356037158
            ],
            [
              0.0,
              1.0,
              0.0,
              -15.027702632397418
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-PILOT-LINE-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              21.46178356037158
            ],
            [
              0.0,
              1.0,
              0.0,
              -15.027702632397418
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-BOWDEN-SHEATH-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -23.74526402036023
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.07259845760632
            ],
            [
              0.0,
              0.0,
              1.0,
              885.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GLAND-BOWDEN-SHEATH-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -23.74526402036023
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.07259845760632
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-GAS-MAIN-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-PILOT-LINE-001",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "ROUTE-LINER-BOWDEN-SHEATH-001",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              889.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FULLFLOW-MANIFOLD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.961004211822308
            ],
            [
              0.0,
              1.0,
              0.0,
              22.414380707064275
            ],
            [
              0.0,
              0.0,
              1.0,
              1725.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-MANIFOLD-BRACKET",
          "transform_matrix_3x4": [
            [
              0.08715574274765814,
              -0.9961946980917455,
              0.0,
              1.961004211822308
            ],
            [
              0.9961946980917455,
              0.08715574274765814,
              0.0,
              22.414380707064275
            ],
            [
              0.0,
              0.0,
              1.0,
              1725.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-SHELL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1635.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-ROUTE-RING-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1638.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-1",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              -0.8660254037844386,
              0.0,
              0.0
            ],
            [
              0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-2",
          "transform_matrix_3x4": [
            [
              -1.0,
              -1.2246467991473532e-16,
              0.0,
              0.0
            ],
            [
              1.2246467991473532e-16,
              -1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "AFT-LONGERON-3",
          "transform_matrix_3x4": [
            [
              0.5000000000000001,
              0.8660254037844386,
              0.0,
              0.0
            ],
            [
              -0.8660254037844386,
              0.5000000000000001,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1642.1
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-REACTION-BULKHEAD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1655.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.6
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -9.799999999999997
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              16.974097914175
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-GUIDE-RAIL-3",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -9.80000000000001
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -16.974097914174994
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-FOLLOWER-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "WP04-EJECTOR-SPRING",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1660.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1658.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1647.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-001",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -4.685141163918161e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -21.1
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-SEAR-001",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.0,
              0.0,
              -4.685141163918161e-15
            ],
            [
              -1.0,
              -2.220446049250313e-16,
              0.0,
              -21.1
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-SEAR-CLIP-001",
          "transform_matrix_3x4": [
            [
              1.0,
              3.3306690738754696e-16,
              0.0,
              -5.678790770957676e-15
            ],
            [
              -3.3306690738754696e-16,
              1.0,
              0.0,
              -25.575000000000003
            ],
            [
              0.0,
              0.0,
              1.0,
              1745.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BODY-HARDPOINT-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-SERVICE-THROAT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP05-DOOR-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              2028.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-HINGE-PIN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              28.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -7.5
            ],
            [
              0.0,
              0.0,
              1.0,
              2028.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-HINGE-CLIP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              28.0
            ],
            [
              0.0,
              1.0,
              0.0,
              6.7
            ],
            [
              0.0,
              0.0,
              1.0,
              2028.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-1",
          "transform_matrix_3x4": [
            [
              0.7071067811865476,
              -0.7071067811865475,
              0.0,
              16.44023266258723
            ],
            [
              0.7071067811865475,
              0.7071067811865476,
              0.0,
              16.440232662587228
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-2",
          "transform_matrix_3x4": [
            [
              -0.7071067811865475,
              -0.7071067811865476,
              0.0,
              -16.440232662587228
            ],
            [
              0.7071067811865476,
              -0.7071067811865475,
              0.0,
              16.44023266258723
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-3",
          "transform_matrix_3x4": [
            [
              -0.7071067811865477,
              0.7071067811865475,
              0.0,
              -16.440232662587235
            ],
            [
              -0.7071067811865475,
              -0.7071067811865477,
              0.0,
              -16.440232662587228
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "DOOR-DETENT-4",
          "transform_matrix_3x4": [
            [
              0.7071067811865474,
              0.7071067811865477,
              0.0,
              16.440232662587224
            ],
            [
              -0.7071067811865477,
              0.7071067811865474,
              0.0,
              -16.440232662587235
            ],
            [
              0.0,
              0.0,
              1.0,
              2026.5
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-01",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-02",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-03",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-04",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-05",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-06",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-07",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "SOFTGOOD",
          "identity_transform": false,
          "occurrence_id": "BUOY-GORE-08",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-BAND-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-BAND-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "HARNESS-TERMINAL-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-XP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-XN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-YP",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "HARNESS-LEG-YN",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "TETHER-THIMBLE-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "TETHER-THIMBLE-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-TETHER-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.5
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-CLIP-BODY",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.7
            ],
            [
              0.0,
              0.0,
              1.0,
              1900.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              -5.5
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "RECOVERY-PIN-CLIP-HARNESS",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              4.7
            ],
            [
              0.0,
              0.0,
              1.0,
              1916.0
            ]
          ]
        },
        {
          "classification": "FLEXIBLE",
          "identity_transform": true,
          "occurrence_id": "WP05-DOOR-LANYARD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              0.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.1
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              0.0
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              18.1
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.1083053532283548e-15
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              18.1
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.1083053532283548e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              18.1
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              2.2166107064567096e-15
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              1.0,
              0.0,
              2.2166107064567096e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FWD-CARRIER-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -3.324916059685064e-15
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              -18.1
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              346.14
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "MANIFOLD-CARRIER-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -3.324916059685064e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -18.1
            ],
            [
              0.0,
              0.0,
              1.0,
              433.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-1-3",
          "transform_matrix_3x4": [
            [
              0.8660254037844387,
              -5.551115123125782e-17,
              -0.49999999999999994,
              21.91858428704209
            ],
            [
              0.49999999999999994,
              9.61481343191782e-17,
              0.8660254037844387,
              8.035898384862243
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-2-3",
          "transform_matrix_3x4": [
            [
              -0.8660254037844388,
              -5.551115123125782e-17,
              -0.49999999999999994,
              -17.918584287042094
            ],
            [
              0.49999999999999994,
              -9.614813431917822e-17,
              -0.8660254037844388,
              14.964101615137753
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              454.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              650.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BOOSTER-CLAMP-SCREW-3-3",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              1.1102230246251565e-16,
              1.0,
              -4.000000000000005
            ],
            [
              -1.0,
              -2.465190328815662e-32,
              -2.220446049250313e-16,
              -23.0
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              858.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.232595164407831e-32,
              -1.0,
              -1.1102230246251565e-16,
              2.586819647376615e-15
            ],
            [
              1.1102230246251565e-16,
              1.1102230246251565e-16,
              -1.0,
              23.3
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-2",
          "transform_matrix_3x4": [
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.17839190817742
            ],
            [
              -5.551115123125784e-17,
              -0.8660254037844386,
              0.5000000000000001,
              -11.650000000000002
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "TRIGGER-MOUNT-SCREW-3",
          "transform_matrix_3x4": [
            [
              9.614813431917817e-17,
              0.5000000000000004,
              -0.8660254037844384,
              20.178391908177414
            ],
            [
              -5.551115123125788e-17,
              0.8660254037844384,
              0.5000000000000004,
              -11.650000000000011
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              508.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "NOSE-BALLAST-TAPER-PIN-001",
          "transform_matrix_3x4": [
            [
              1.1102230246251565e-16,
              0.0,
              1.0,
              -15.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              -1.0,
              0.0,
              1.1102230246251565e-16,
              170.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "FULLFLOW-VALVE-CIRCLIP-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              883.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WATER-BOBBIN-SERVICE-CAP-001",
          "transform_matrix_3x4": [
            [
              0.984807753012208,
              -0.17364817766693033,
              0.0,
              0.0
            ],
            [
              0.17364817766693033,
              0.984807753012208,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              500.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.2
            ],
            [
              0.0,
              1.1102230246251565e-16,
              1.0,
              -1.8
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              24.8
            ],
            [
              0.0,
              1.1102230246251565e-16,
              1.0,
              -1.8
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-1-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              9.124352264812732
            ],
            [
              0.0,
              1.0,
              0.0,
              -7.8
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-1-2",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              9.124352264812732
            ],
            [
              0.0,
              1.0,
              0.0,
              7.8
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-1-1",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.534237417304098
            ],
            [
              0.0,
              1.0,
              0.0,
              -8.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-1-2",
          "transform_matrix_3x4": [
            [
              0.17364817766693041,
              0.0,
              0.984807753012208,
              10.534237417304098
            ],
            [
              0.0,
              1.0,
              0.0,
              8.0
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -9.61481343191782e-17,
              -0.8660254037844387,
              -8.041154273188008
            ],
            [
              0.8660254037844387,
              -5.55111512312578e-17,
              -0.4999999999999998,
              17.527687752661222
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -9.61481343191782e-17,
              -0.8660254037844387,
              -10.841154273188007
            ],
            [
              0.8660254037844387,
              -5.55111512312578e-17,
              -0.4999999999999998,
              22.377430013854077
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-2-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              2.192822017112259
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              11.8019208544059
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-2-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -11.317174281924984
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              4.001920854405904
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-2-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              1.6610845216234638
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              13.12291721288192
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-2-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346517,
              -0.8660254037844387,
              -0.4924038765061038,
              -12.195321938927556
            ],
            [
              0.15038373318043535,
              -0.4999999999999998,
              0.8528685319524433,
              5.122917212881924
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              9.614813431917817e-17,
              0.8660254037844384,
              -11.158845726811997
            ],
            [
              -0.8660254037844384,
              -5.551115123125788e-17,
              -0.5000000000000004,
              -15.727687752661218
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "ARM-STOP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              9.614813431917817e-17,
              0.8660254037844384,
              -13.958845726812
            ],
            [
              -0.8660254037844384,
              -5.551115123125788e-17,
              -0.5000000000000004,
              -20.577430013854073
            ],
            [
              0.0,
              -1.0,
              1.1102230246251565e-16,
              891.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-3-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -11.317174281924988
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -4.0019208544058955
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-SCREW-3-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              2.1928220171122503
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -11.801920854405903
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              892.7485948064624
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-3-1",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              -12.19532193892756
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -5.122917212881916
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "FIXED-STOP-DOWEL-3-2",
          "transform_matrix_3x4": [
            [
              -0.08682408883346529,
              0.8660254037844384,
              -0.49240387650610445,
              1.6610845216234549
            ],
            [
              -0.1503837331804353,
              -0.5000000000000004,
              -0.8528685319524429,
              -13.122917212881923
            ],
            [
              -0.984807753012208,
              0.0,
              0.17364817766693041,
              887.9200625391181
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-GUIDE-SCREW-1",
          "transform_matrix_3x4": [
            [
              5.551115123125784e-17,
              0.8660254037844386,
              -0.5000000000000001,
              12.100000000000003
            ],
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.957814771583415
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              900.75
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "BACKUP-GUIDE-SCREW-2",
          "transform_matrix_3x4": [
            [
              5.551115123125784e-17,
              0.8660254037844386,
              -0.5000000000000001,
              12.100000000000003
            ],
            [
              -9.614813431917819e-17,
              0.5000000000000001,
              0.8660254037844386,
              -20.957814771583415
            ],
            [
              1.0,
              0.0,
              1.1102230246251565e-16,
              1082.7763633888685
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "CROSSHEAD-GUIDE-LOCK-SCREW-001",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              887.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-AFT-RAIL-SUPPORT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1848.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-1-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              20.0
            ],
            [
              0.0,
              -1.0,
              -1.2246467991473532e-16,
              0.0
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-1-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              20.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-2-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              0.8660254037844387,
              1.0605752387249069e-16,
              -9.999999999999996
            ],
            [
              0.8660254037844387,
              0.4999999999999998,
              6.123233995736764e-17,
              17.320508075688778
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-2-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              -0.4999999999999998,
              -0.8660254037844387,
              0.0,
              -9.999999999999996
            ],
            [
              0.8660254037844387,
              -0.4999999999999998,
              0.0,
              17.320508075688778
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-3-SCREW-FWD",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              -0.8660254037844384,
              -1.0605752387249065e-16,
              -10.00000000000001
            ],
            [
              -0.8660254037844384,
              0.5000000000000004,
              6.123233995736771e-17,
              -17.32050807568877
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1661.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "GUIDE-RAIL-3-SCREW-AFT",
          "transform_matrix_3x4": [
            [
              -0.5000000000000004,
              0.8660254037844384,
              0.0,
              -10.00000000000001
            ],
            [
              -0.8660254037844384,
              -0.5000000000000004,
              0.0,
              -17.32050807568877
            ],
            [
              0.0,
              0.0,
              1.0,
              1845.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              12.7
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -6.349999999999997
            ],
            [
              0.0,
              1.0,
              0.0,
              10.998522628062371
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -6.350000000000005
            ],
            [
              0.0,
              1.0,
              0.0,
              -10.998522628062366
            ],
            [
              0.0,
              0.0,
              1.0,
              1652.0
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              7.500000000000002
            ],
            [
              0.0,
              1.0,
              0.0,
              12.990381056766578
            ],
            [
              0.0,
              0.0,
              1.0,
              1742.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -15.0
            ],
            [
              0.0,
              1.0,
              0.0,
              1.83697019872103e-15
            ],
            [
              0.0,
              0.0,
              1.0,
              1742.5
            ]
          ]
        },
        {
          "classification": "MOVING",
          "identity_transform": false,
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              7.500000000000002
            ],
            [
              0.0,
              1.0,
              0.0,
              -12.990381056766578
            ],
            [
              0.0,
              0.0,
              1.0,
              1742.5
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "LATCH-SUPPORT-BRACKET",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              0.0
            ],
            [
              0.0,
              1.0,
              0.0,
              0.0
            ],
            [
              0.0,
              0.0,
              1.0,
              1736.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-SCREW-1",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              -1.0,
              -1.2246467991473532e-16,
              -6.000000000000005
            ],
            [
              -1.0,
              2.220446049250313e-16,
              2.719262146893782e-32,
              -23.2
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1744.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP04-LATCH-SCREW-2",
          "transform_matrix_3x4": [
            [
              -2.220446049250313e-16,
              -1.0,
              -1.2246467991473532e-16,
              5.999999999999995
            ],
            [
              -1.0,
              2.220446049250313e-16,
              2.719262146893782e-32,
              -23.200000000000003
            ],
            [
              0.0,
              1.2246467991473532e-16,
              -1.0,
              1744.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-1",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.22576396401454
            ],
            [
              0.0,
              1.0,
              0.0,
              11.099999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-2",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              1.359357947053562e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              22.2
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-3",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -19.22576396401454
            ],
            [
              0.0,
              1.0,
              0.0,
              11.099999999999998
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-4",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -19.225763964014536
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.100000000000001
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-5",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              -4.0780738411606855e-15
            ],
            [
              0.0,
              1.0,
              0.0,
              -22.2
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        },
        {
          "classification": "FIXED",
          "identity_transform": false,
          "occurrence_id": "WP05-THROAT-SCREW-6",
          "transform_matrix_3x4": [
            [
              1.0,
              0.0,
              0.0,
              19.225763964014533
            ],
            [
              0.0,
              1.0,
              0.0,
              -11.10000000000001
            ],
            [
              0.0,
              0.0,
              1.0,
              1928.0
            ]
          ]
        }
      ],
      "root_name": "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_ASSY",
      "step_nauo_count": 288,
      "step_product_count": 131,
      "top_level_assembly_names": [
        "100_FORWARD_PENETRATOR_WAI_AND_PRIMARY_STRUCTURE_ASSY",
        "300_TRUE_TRANSFORM_ARM_AND_POWERTRAIN_ASSY",
        "500_SPRING_EJECTOR_AFT_CLOSURE_AND_RECOVERY_ASSY"
      ],
      "unexpected_assembly_paths": []
    },
    "occurrence_bom_reconciliation": {
      "deployed_occurrence_count": 279,
      "issue_count": 0,
      "row_count": 558,
      "stowed_occurrence_count": 279
    },
    "occurrence_transform_gate": {
      "identity_occurrences_without_justification": null,
      "maximum_transform_matrix_element_error": null,
      "status": "NOT_COMPUTED",
      "transform_mismatches": null,
      "unmapped_leaf_occurrences": null
    }
  }
}
```

## State parity, connectivity, attachment, routes, and Definition of Done

```json
{
  "connectivity_attachment_route": {
    "DEPLOYED": {
      "attachment_coverage_required_occurrence_count": 279,
      "attachment_endpoint_occurrence_count": 279,
      "attachment_result_count": 414,
      "blank_attachment_id_count": 0,
      "blank_route_id_count": 0,
      "body_hardpoint_to_harness_terminal_path": [
        "BODY-HARDPOINT-001",
        "TETHER-THIMBLE-BODY",
        "RECOVERY-TETHER-001",
        "TETHER-THIMBLE-HARNESS",
        "HARNESS-TERMINAL-001"
      ],
      "connection_count": 414,
      "continuous_recovery_load_path_found": true,
      "dangling_connection_count": 0,
      "direct_distance_status_counts": {
        "DONE": 414
      },
      "duplicate_attachment_id_count": 0,
      "duplicate_route_id_count": 0,
      "failed_route_count": 0,
      "floating_rigid_count": 0,
      "generic_or_blanket_evidence_count": 0,
      "geometric_or_fastener_unsupported_connection_count": 0,
      "graph_component_count_including_flexible_and_consumed": 1,
      "invalid_attachment_record_count": 0,
      "invalid_route_record_count": 0,
      "occurrence_count": 279,
      "route_count": 10,
      "route_status_counts": {
        "PASS": 10
      },
      "self_connection_count": 0,
      "uncovered_attachment_endpoint_occurrence_count": 0
    },
    "STOWED": {
      "attachment_coverage_required_occurrence_count": 279,
      "attachment_endpoint_occurrence_count": 279,
      "attachment_result_count": 417,
      "blank_attachment_id_count": 0,
      "blank_route_id_count": 0,
      "body_hardpoint_to_harness_terminal_path": [
        "BODY-HARDPOINT-001",
        "TETHER-THIMBLE-BODY",
        "RECOVERY-TETHER-001",
        "TETHER-THIMBLE-HARNESS",
        "HARNESS-TERMINAL-001"
      ],
      "connection_count": 417,
      "continuous_recovery_load_path_found": true,
      "dangling_connection_count": 0,
      "direct_distance_status_counts": {
        "DONE": 417
      },
      "duplicate_attachment_id_count": 0,
      "duplicate_route_id_count": 0,
      "failed_route_count": 0,
      "floating_rigid_count": 0,
      "generic_or_blanket_evidence_count": 0,
      "geometric_or_fastener_unsupported_connection_count": 0,
      "graph_component_count_including_flexible_and_consumed": 1,
      "invalid_attachment_record_count": 0,
      "invalid_route_record_count": 0,
      "occurrence_count": 279,
      "route_count": 10,
      "route_status_counts": {
        "PASS": 10
      },
      "self_connection_count": 0,
      "uncovered_attachment_endpoint_occurrence_count": 0
    }
  },
  "definition_of_done": {
    "DEPLOYED": {
      "blocked": [],
      "blocked_count": 0,
      "failure_count": 0,
      "failures": [],
      "requirements_object_present": true,
      "section_count": 4,
      "sections": {
        "closed_pressure_subsystems": {
          "actual_subsystem_ids": [
            "BOOSTER-1",
            "BOOSTER-2",
            "BOOSTER-3",
            "CO2-CARTRIDGE-1",
            "CO2-CARTRIDGE-2",
            "CO2-CARTRIDGE-3",
            "CO2-CARTRIDGE-4"
          ],
          "blocked_count": 0,
          "expected_subsystem_ids": [
            "BOOSTER-1",
            "BOOSTER-2",
            "BOOSTER-3",
            "CO2-CARTRIDGE-1",
            "CO2-CARTRIDGE-2",
            "CO2-CARTRIDGE-3",
            "CO2-CARTRIDGE-4"
          ],
          "failure_count": 0,
          "missing_subsystem_ids": [],
          "status": "PASS",
          "subsystem_count": 7,
          "topology_check_count": 7,
          "topology_failure_count": 0,
          "unexpected_subsystem_ids": []
        },
        "closed_route_ends": {
          "blank_route_definition_record_indices": [],
          "blocked_count": 0,
          "declared_closed_route_count": 10,
          "duplicate_route_definition_ids": [],
          "failure_count": 0,
          "invalid_route_definition_record_indices": [],
          "inventory_route_count": 10,
          "status": "PASS",
          "undeclared_route_occurrence_ids": []
        },
        "positive_deployed_locks": {
          "arm_indices": [
            1,
            2,
            3
          ],
          "blocked_count": 0,
          "failure_count": 0,
          "mechanism_count": 3,
          "status": "PASS"
        },
        "required_hardware_and_pin_retention": {
          "blocked_count": 0,
          "declared_hardware_count": 279,
          "failure_count": 0,
          "physical_pin_candidate_count": 17,
          "retained_pin_requirement_count": 27,
          "status": "PASS",
          "undeclared_installed_occurrence_ids": [],
          "undeclared_pin_candidate_ids": []
        }
      }
    },
    "STOWED": {
      "blocked": [],
      "blocked_count": 0,
      "failure_count": 0,
      "failures": [],
      "requirements_object_present": true,
      "section_count": 4,
      "sections": {
        "closed_pressure_subsystems": {
          "actual_subsystem_ids": [
            "BOOSTER-1",
            "BOOSTER-2",
            "BOOSTER-3",
            "CO2-CARTRIDGE-1",
            "CO2-CARTRIDGE-2",
            "CO2-CARTRIDGE-3",
            "CO2-CARTRIDGE-4"
          ],
          "blocked_count": 0,
          "expected_subsystem_ids": [
            "BOOSTER-1",
            "BOOSTER-2",
            "BOOSTER-3",
            "CO2-CARTRIDGE-1",
            "CO2-CARTRIDGE-2",
            "CO2-CARTRIDGE-3",
            "CO2-CARTRIDGE-4"
          ],
          "failure_count": 0,
          "missing_subsystem_ids": [],
          "status": "PASS",
          "subsystem_count": 7,
          "topology_check_count": 7,
          "topology_failure_count": 0,
          "unexpected_subsystem_ids": []
        },
        "closed_route_ends": {
          "blank_route_definition_record_indices": [],
          "blocked_count": 0,
          "declared_closed_route_count": 10,
          "duplicate_route_definition_ids": [],
          "failure_count": 0,
          "invalid_route_definition_record_indices": [],
          "inventory_route_count": 10,
          "status": "PASS",
          "undeclared_route_occurrence_ids": []
        },
        "positive_stowed_retention": {
          "arm_indices": [
            1,
            2,
            3
          ],
          "blocked_count": 0,
          "failure_count": 0,
          "mechanism_count": 3,
          "status": "PASS"
        },
        "required_hardware_and_pin_retention": {
          "blocked_count": 0,
          "declared_hardware_count": 279,
          "failure_count": 0,
          "physical_pin_candidate_count": 17,
          "retained_pin_requirement_count": 27,
          "status": "PASS",
          "undeclared_installed_occurrence_ids": [],
          "undeclared_pin_candidate_ids": []
        }
      }
    }
  },
  "state_parity": {
    "classification_counts": {
      "CONSUMED": 5,
      "FIXED": 181,
      "FLEXIBLE": 18,
      "MOVING": 67,
      "SOFTGOOD": 8
    },
    "flexible_exception_row_count": 26,
    "row_count": 279,
    "rows": [
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "AFT-LONGERON-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "AFT-LONGERON-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "AFT-LONGERON-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "ca4860a8bcebf3ae94cfcda1734541746ee8c128f72e31b395c8bb2d0009de71",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "95a87712716b257864ffa65aa4c2a0b5d2a161537f7b36a1705b5b7619d40b56",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "AFT-ROUTE-RING-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "95a87712716b257864ffa65aa4c2a0b5d2a161537f7b36a1705b5b7619d40b56",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "53",
        "deployed_local_brep_sha256": "3b2e817e36b10c1da85cb2a99cae108eb7de1a37182f519e74419d80a45c33d4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "AFT-SHELL-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "53",
        "stowed_local_brep_sha256": "5dae9a8ddd9037173845ae51e804a0ff9754c2fa027e93c326dab83f927b97c4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "121",
        "deployed_local_brep_sha256": "00ab6382965433b13969be890c848074950b7b1cd91dfe8fc54d00f718bacbb2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "121",
        "stowed_local_brep_sha256": "aab0d0d17fa58bd3d937c55f535726720138d745202cdc44a7f1b2b30bdf6637",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.4551915228366852e-11"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "121",
        "deployed_local_brep_sha256": "00ab6382965433b13969be890c848074950b7b1cd91dfe8fc54d00f718bacbb2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "121",
        "stowed_local_brep_sha256": "aab0d0d17fa58bd3d937c55f535726720138d745202cdc44a7f1b2b30bdf6637",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "2.1827872842550278e-11"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "121",
        "deployed_local_brep_sha256": "00ab6382965433b13969be890c848074950b7b1cd91dfe8fc54d00f718bacbb2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "121",
        "stowed_local_brep_sha256": "aab0d0d17fa58bd3d937c55f535726720138d745202cdc44a7f1b2b30bdf6637",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-2.9103830456733704e-11"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "84284d43a59916caa5cdcd9dc0eb03ca6d7ebed8ca8a9ad8bd263b87d0c4f333",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-LONGERON-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "84284d43a59916caa5cdcd9dc0eb03ca6d7ebed8ca8a9ad8bd263b87d0c4f333",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "84284d43a59916caa5cdcd9dc0eb03ca6d7ebed8ca8a9ad8bd263b87d0c4f333",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-LONGERON-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "84284d43a59916caa5cdcd9dc0eb03ca6d7ebed8ca8a9ad8bd263b87d0c4f333",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "10",
        "deployed_local_brep_sha256": "e7f3d1602e85eb629db040a937ce29f00e1a7199907ba6a70df658e5d1bd5336",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-LONGERON-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "10",
        "stowed_local_brep_sha256": "e7f3d1602e85eb629db040a937ce29f00e1a7199907ba6a70df658e5d1bd5336",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "22",
        "deployed_local_brep_sha256": "99fe785687f0d31e5e1e2376e2176f0d554163d563b974be60b920c35a29b818",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-PAD-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "22",
        "stowed_local_brep_sha256": "e3e2bc73b7500e14189fbdfa233ea6e827132205ad833df62dd4f23e35c2c105",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-2.5579538487363607e-12"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "22",
        "deployed_local_brep_sha256": "99fe785687f0d31e5e1e2376e2176f0d554163d563b974be60b920c35a29b818",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-PAD-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "22",
        "stowed_local_brep_sha256": "e3e2bc73b7500e14189fbdfa233ea6e827132205ad833df62dd4f23e35c2c105",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.9895196601282805e-12"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "22",
        "deployed_local_brep_sha256": "99fe785687f0d31e5e1e2376e2176f0d554163d563b974be60b920c35a29b818",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-PAD-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "22",
        "stowed_local_brep_sha256": "e3e2bc73b7500e14189fbdfa233ea6e827132205ad833df62dd4f23e35c2c105",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-2.0179413695586845e-12"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.4210854715202004e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.7053025658242404e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.4210854715202004e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ARM-STOP-SCREW-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-5.684341886080802e-14"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BACKUP-GUIDE-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BACKUP-GUIDE-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "f42acc1e26f50d66f48931b95770a2b4a3d2e62cb2eb69d4b007aa88ace9eb7b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "15.055034371134184",
        "occurrence_id": "BACKUP-SPRING-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "4382579e72072ede16aaff5b8eea603c555f9636b166b0360f271d7dc35ac470",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-0.00028469016615417786"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "0c2a360e97bec455d4721b06b683111a703fc8ee3d23e07be245cdcdbed4faf3",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BACKUP-SPRING-FIXED-SEAT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "0c2a360e97bec455d4721b06b683111a703fc8ee3d23e07be245cdcdbed4faf3",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "6a43937f188e76745712cac2dc9722bb428dfa469231e79d9983576f24b6566e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BACKUP-SPRING-GUIDE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "6a43937f188e76745712cac2dc9722bb428dfa469231e79d9983576f24b6566e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "419d523baacafb5b1c0cbdb6feec81d697c0588c551635fbb6aa088533611f3f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BACKUP-SPRING-MOVING-SEAT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "419d523baacafb5b1c0cbdb6feec81d697c0588c551635fbb6aa088533611f3f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "afb9dd670dc2c0127062f1dfe0608a08be1d08507b2a03aaae632bd3f2ade4eb",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BALLAST-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "afb9dd670dc2c0127062f1dfe0608a08be1d08507b2a03aaae632bd3f2ade4eb",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "50",
        "deployed_local_brep_sha256": "b45996cd3de3d5b7ec3e8d1ca80d61d96f44a3318f5000a9341e529c08ae0ce8",
        "deployed_solid_count": "3",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BODY-HARDPOINT-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "50",
        "stowed_local_brep_sha256": "b45996cd3de3d5b7ec3e8d1ca80d61d96f44a3318f5000a9341e529c08ae0ce8",
        "stowed_solid_count": "3",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5333540af30f7da03dd37c4039ee9a94594fcfc1dba9b541953a3950a4b1a197",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-AFT-CLOSURE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-AFT-CLOSURE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-AFT-CLOSURE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "772e65e1c51f94b75c84ba97c2caf1e49ac2a4fbc72df7633b083459641d619a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-1-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-2-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "23",
        "deployed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-BAND-3-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "23",
        "stowed_local_brep_sha256": "9d9f7582dd16dbb17c2a1c1ab12df9ec037ba5b6b00588cf8e4009905a4fd38a",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-1-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-2-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-CLAMP-SCREW-3-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-COLLECTION-LINE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-COLLECTION-LINE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-COLLECTION-LINE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "ad6c545a5a0b2bf2b6bb8955253d6327cd31528d7b2fc79ccb74ad28d95fdc3c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "6",
        "deployed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-FWD-CLOSURE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "6",
        "deployed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-FWD-CLOSURE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "6",
        "deployed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-FWD-CLOSURE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "23859a2a664832c873483adbce2ee8004c3c727f3dbc08069a1073c57e33d824",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "30",
        "deployed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-ISOLATION-VALVE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "30",
        "stowed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "30",
        "deployed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-ISOLATION-VALVE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "30",
        "stowed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "30",
        "deployed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "BOOSTER-ISOLATION-VALVE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "30",
        "stowed_local_brep_sha256": "e23b30781f194d5adf49f54295b371e83bab966364a73ef5b3e5c57c7ea7c0c8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "d58a4033f54646a196c79cfb72ba8b5ce47af40b4f6d93917623b90ebe11bf8e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "226.4",
        "occurrence_id": "BUOY-GORE-01",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "b5c52adfe14f71d6353bdb6c842112a6fbad8603cd252a062c218d75bcc7df49",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40858.16585679208"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "9d5bca8eb7d0feef244c4bbebf7b32e0ee0d56c3bceeb60e39289f6d5daf1b49",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-02",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "8bac9defa1268027a3dde387a6baae947ab0d51234caedb3661b669ac27eba5d",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.62470069246"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "ab5914d048bed7410a868347f442e6e593971b36b12d8f301f04deb55b35524e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-03",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "5c977ed9e85d16aa39af34541a8107c68bf7196d54d100ba480aa47a6b21d2b2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.6247007678"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "b76b93cf4696d5ef287df5c7eb0325a513d9f91ebdf552c63f1aa88305e6686b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-04",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "5190a4fc16558bce3cbbebdfdbf561b52ee8605554061ccf78a451cdfd252170",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.624700694374"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "406",
        "deployed_local_brep_sha256": "5f1c858d00513e8bfaa6c9dff30a4b302f926c25e3a5a67e9b6c01c76a04bdbc",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "233.74180911112867",
        "occurrence_id": "BUOY-GORE-05",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "3630b45d13d7790a511b0ce0f9e7f60703ba28aeac1d00f644670d2abe2e4966",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "41011.3577837879"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "e4d3dc998754d0e24139bdf8e319930d9d2676fc27cd1e854601248c41af6bcb",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-06",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "1a43409998be07c6df4aed4295f984d498e71bdd0f326bb8f443831c804793c6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.62470069245"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "5810a32c3433c06b2fabf9d91b90d6089916aa7037310653db5c2b8ef7692b0d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-07",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "ebee96b938a8b1dce16de3d623000c9ff00139462cf9080a5d571e27958970f3",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.6247007124"
      },
      {
        "classification": "SOFTGOOD",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "ab1c8155411145d29d265f6f3397590fe69652d6e0b2de7e85ff25927b30c5a7",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "246.309",
        "occurrence_id": "BUOY-GORE-08",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "8f7b8352cbd1befadff2e056cee65b2929b978d026f6f912ed46989b09e90850",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "40886.62470074924"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "43",
        "deployed_local_brep_sha256": "fddd729a2ed4282d8548840d1641dba3a3b9ad66eb5076c59f48d6c8fcc0dcb9",
        "deployed_solid_count": "5",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CARTRIDGE-CARRIER-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "43",
        "stowed_local_brep_sha256": "fddd729a2ed4282d8548840d1641dba3a3b9ad66eb5076c59f48d6c8fcc0dcb9",
        "stowed_solid_count": "5",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "43",
        "deployed_local_brep_sha256": "fddd729a2ed4282d8548840d1641dba3a3b9ad66eb5076c59f48d6c8fcc0dcb9",
        "deployed_solid_count": "5",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CARTRIDGE-CARRIER-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "43",
        "stowed_local_brep_sha256": "fddd729a2ed4282d8548840d1641dba3a3b9ad66eb5076c59f48d6c8fcc0dcb9",
        "stowed_solid_count": "5",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "CONSUMED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CO2-CARTRIDGE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "CONSUMED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CO2-CARTRIDGE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "CONSUMED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CO2-CARTRIDGE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "CONSUMED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CO2-CARTRIDGE-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0f8584d9580350680c477352bfd6914e20f1521d98d365c22e67ec95fa10ee9c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "31",
        "deployed_local_brep_sha256": "e394b019837be9dff63886be5bb9e25dc5bb5a8534baace38d8d52164812b1c1",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "COLLECTION-MANIFOLD-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "31",
        "stowed_local_brep_sha256": "e394b019837be9dff63886be5bb9e25dc5bb5a8534baace38d8d52164812b1c1",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "213",
        "deployed_local_brep_sha256": "ba3982dfd620d0505dbd11a6d84ff6d8aca597e05e28689e0a22c11db8f4a7a6",
        "deployed_solid_count": "5",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CROSSHEAD-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "213",
        "stowed_local_brep_sha256": "9d911f62d6cc740899271f45921152d29e131fccbc908e357abf0f424b4eaf7a",
        "stowed_solid_count": "5",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-4.547473508864641e-13"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "9d00d36e6d5036f925a02cc8df682a120442625ff605897958bd8ec63ef1e3f8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CROSSHEAD-GUIDE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "9d00d36e6d5036f925a02cc8df682a120442625ff605897958bd8ec63ef1e3f8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "3918137717b9fb23648356931a2711478bb9621432cbe2a6123e20e37b551b0b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CROSSHEAD-GUIDE-LOCK-SCREW-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "3918137717b9fb23648356931a2711478bb9621432cbe2a6123e20e37b551b0b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "28",
        "deployed_local_brep_sha256": "5902a0df94a18879d901c3a166c3d12c6ef532dc4effa834bc809344a1b35c48",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "CROSSHEAD-GUIDE-SPIDER",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "28",
        "stowed_local_brep_sha256": "5902a0df94a18879d901c3a166c3d12c6ef532dc4effa834bc809344a1b35c48",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "DOOR-DETENT-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "DOOR-DETENT-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "DOOR-DETENT-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "DOOR-DETENT-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "436eb3e9d506b2e019f27e28034147dd9173531ed2c121f4f3d3d17a000b277e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "34",
        "deployed_local_brep_sha256": "84f11905dd57c2aa7bdede0c37fd21269ed4df66a088e59aaf7ca1ca2c2f1c5c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-SECTOR-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "34",
        "stowed_local_brep_sha256": "84f11905dd57c2aa7bdede0c37fd21269ed4df66a088e59aaf7ca1ca2c2f1c5c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "34",
        "deployed_local_brep_sha256": "84f11905dd57c2aa7bdede0c37fd21269ed4df66a088e59aaf7ca1ca2c2f1c5c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-SECTOR-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "34",
        "stowed_local_brep_sha256": "84f11905dd57c2aa7bdede0c37fd21269ed4df66a088e59aaf7ca1ca2c2f1c5c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "d331aac85a1622dab42a943b97a583a70243dcfdd2b090dd6030c2afd5250c3e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-SECTOR-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "fe4c5c94fdee1f6e9e835e1a540dd79d328312dfeeb9ea0454792aa41088dbee",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "100",
        "deployed_local_brep_sha256": "b74d4f9702ffbe19b7c81d6393dcee51f77b9d6821eb45010f27fd64fc4f810b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "100",
        "stowed_local_brep_sha256": "f6a9f4580ab054322275936abe0fb7c5bb9d1309fb82c14af6bbc3c0cd01e349",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "100",
        "deployed_local_brep_sha256": "b74d4f9702ffbe19b7c81d6393dcee51f77b9d6821eb45010f27fd64fc4f810b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "100",
        "stowed_local_brep_sha256": "f6a9f4580ab054322275936abe0fb7c5bb9d1309fb82c14af6bbc3c0cd01e349",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "100",
        "deployed_local_brep_sha256": "b74d4f9702ffbe19b7c81d6393dcee51f77b9d6821eb45010f27fd64fc4f810b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "100",
        "stowed_local_brep_sha256": "f6a9f4580ab054322275936abe0fb7c5bb9d1309fb82c14af6bbc3c0cd01e349",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-DOWEL-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "236c558eb5be6f8336298a9c31c69a583b0dc9910bfed574613e097b00b3ab83",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FIXED-STOP-SCREW-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "53",
        "deployed_local_brep_sha256": "588e42927254158b8b3f9fbd18157772079acfbc0516c4b1b0a86bbe6295e372",
        "deployed_solid_count": "4",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FULLFLOW-VALVE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "53",
        "stowed_local_brep_sha256": "588e42927254158b8b3f9fbd18157772079acfbc0516c4b1b0a86bbe6295e372",
        "stowed_solid_count": "4",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "33",
        "deployed_local_brep_sha256": "e8e89e0a5cab96af6d6c96337dea26afdbb41c9430f0f09363f6fc09fd58c395",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FULLFLOW-VALVE-CIRCLIP-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "33",
        "stowed_local_brep_sha256": "e8e89e0a5cab96af6d6c96337dea26afdbb41c9430f0f09363f6fc09fd58c395",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-CARRIER-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-CARRIER-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-CARRIER-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-CARRIER-SCREW-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-LONGERON-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-LONGERON-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-LONGERON-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "e42b528851cba9717e83cc1458712747fd0235bf0a015fb4e710d8cf6825340f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "43",
        "deployed_local_brep_sha256": "d244eea764a0704a8013634d2e73f427074465371e914d5679682fb0c3b10277",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-RING-01",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "43",
        "stowed_local_brep_sha256": "d244eea764a0704a8013634d2e73f427074465371e914d5679682fb0c3b10277",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "68",
        "deployed_local_brep_sha256": "841d7d06ef1eba65c44f32346f1018f2009074ba67a86560f1bd75c4078654d9",
        "deployed_solid_count": "4",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-RING-02",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "68",
        "stowed_local_brep_sha256": "aaeae7a6328b51d03d2c8b0b344fd82835d8e00d136dc8242aca7a38fa6589ac",
        "stowed_solid_count": "4",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "168",
        "deployed_local_brep_sha256": "4857c21b1225c33c3444911ea0710d50d59d243ad4182992b18bcbd06617d919",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "FWD-SHELL-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "168",
        "stowed_local_brep_sha256": "4857c21b1225c33c3444911ea0710d50d59d243ad4182992b18bcbd06617d919",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "17b0a777ff2be2e82b2200412b8b68bdf1bb3ff605b7247a9e2a4fcc47dcaa1b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-BOWDEN-SHEATH-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "17b0a777ff2be2e82b2200412b8b68bdf1bb3ff605b7247a9e2a4fcc47dcaa1b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "17b0a777ff2be2e82b2200412b8b68bdf1bb3ff605b7247a9e2a4fcc47dcaa1b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-BOWDEN-SHEATH-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "17b0a777ff2be2e82b2200412b8b68bdf1bb3ff605b7247a9e2a4fcc47dcaa1b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "eb9a28c6a6e6b495fcba7669ce839a6be214f2a28c04621560b51ecefb2e66c1",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-GAS-MAIN-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "eb9a28c6a6e6b495fcba7669ce839a6be214f2a28c04621560b51ecefb2e66c1",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "eb9a28c6a6e6b495fcba7669ce839a6be214f2a28c04621560b51ecefb2e66c1",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-GAS-MAIN-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "eb9a28c6a6e6b495fcba7669ce839a6be214f2a28c04621560b51ecefb2e66c1",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "b9aab4f2f4e414e35fd0062c624c49e4f93ef54719ea180f4f2bd4e18402660f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-PILOT-LINE-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "b9aab4f2f4e414e35fd0062c624c49e4f93ef54719ea180f4f2bd4e18402660f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "b9aab4f2f4e414e35fd0062c624c49e4f93ef54719ea180f4f2bd4e18402660f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GLAND-PILOT-LINE-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "b9aab4f2f4e414e35fd0062c624c49e4f93ef54719ea180f4f2bd4e18402660f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "18",
        "deployed_local_brep_sha256": "32bc30f8a9afc2ac10b2b1b5c5940bb76d1046456aea176fd648dbc4ac3ec528",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-BODY-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "18",
        "stowed_local_brep_sha256": "32bc30f8a9afc2ac10b2b1b5c5940bb76d1046456aea176fd648dbc4ac3ec528",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-CLIP-FIXED",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-CLIP-MOVING",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-8.881784197001252e-16"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "47",
        "deployed_local_brep_sha256": "e97533b508b2962cd5de2e02bae2a4d770b3ca9da3e4f4669a39b27282833cce",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-FIXED-YOKE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "47",
        "stowed_local_brep_sha256": "e97533b508b2962cd5de2e02bae2a4d770b3ca9da3e4f4669a39b27282833cce",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-PIN-FIXED",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-PIN-MOVING",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "f5806935275815a382a44453554334959370d47f48caf76959fee8ac2dc93605",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GS19-ROD-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "f5806935275815a382a44453554334959370d47f48caf76959fee8ac2dc93605",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "4.547473508864641e-13"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-1-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-1-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-2-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-2-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-3-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "GUIDE-RAIL-3-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "0c6528d1cfeb7982907f9139d6eaf6b960711886138ab0b1d2d19cd8483c0066",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "228.71895529445",
        "occurrence_id": "HARNESS-BAND-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "1c4cad8d92b49117a97d401705eebff03c43f11359145e801e628813d7887943",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "38476.096185755814"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "64",
        "deployed_local_brep_sha256": "d2896f8d853d7b3a172c8de487c660ecefa23d4ebab0c0b8447ff5b182050493",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "229.91895529445",
        "occurrence_id": "HARNESS-BAND-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "cb4c944642962b9e3c15a269233f67ee45c441b8846db3b16e9990c6452046b6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "38904.03165419087"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "18",
        "deployed_local_brep_sha256": "d8fc280dfcc1bd200b5a9a6909a5d95a295e04f54fe0cc2681e669a7421acf9b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "150.71437792862798",
        "occurrence_id": "HARNESS-LEG-XN",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "034efdb0ad8a083cca1b10bdd11fdbc5c425982e80c30bb0ab609c2a62f27171",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "-1182.3304241488634"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "18",
        "deployed_local_brep_sha256": "08238a18932c9c126b2c7387daf9790037c41d5fae99fc3bb1abc4592fb8cae4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "150.71437792862798",
        "occurrence_id": "HARNESS-LEG-XP",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "f8e20414a131c3927d7f80934bba52fd7bf334e340561432986aebc38c2debaf",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "-1182.3304241498608"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "c15acc3995ac620e5ce17797cd61064f504ce374b76e4995f321adba4462392f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "122.83262039743629",
        "occurrence_id": "HARNESS-LEG-YN",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "f63ea10f8c3ca232fcde70a15b90a1b8519933dee39ee15eb4e602b0ff5c2adc",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-935.1553205379879"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "dcf9fc25c8dcb87211dafe983d3b8dcc62bcfbf930e49ca2662cdf13addfe6b9",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "122.83262039743865",
        "occurrence_id": "HARNESS-LEG-YP",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "b8490a74ec5b8bc689fd3519bdc1edb5c1d96ec5115ff96392ba1d19bb65cb16",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-935.1553205355915"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "43",
        "deployed_local_brep_sha256": "7ac812159e6a2844d7db5516d202489e156e65c190cb0e87d57ff9d9e6e57e78",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HARNESS-TERMINAL-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "43",
        "stowed_local_brep_sha256": "0bca2e38f8d017316896e05b8f764b54a7201b672df867c84ef1d05e66a48f4c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "4.547473508864641e-13"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "18",
        "deployed_local_brep_sha256": "c96c2aa582940a3647dc304743c0180d564977ca38b229ef2b098b1ed63bd501",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-BODY-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "18",
        "stowed_local_brep_sha256": "c96c2aa582940a3647dc304743c0180d564977ca38b229ef2b098b1ed63bd501",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-CLIP-FIXED",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-CLIP-MOVING",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "0d2e4bcfad9dbaec42097c1fab34cfd35b54f5079c2a9ca6b8e8cdf9325471d4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-8.881784197001252e-16"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "47",
        "deployed_local_brep_sha256": "4357c326002e37cecd91c8547e92e61dbbca5b8659fe241a68d750f18d05a214",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-FIXED-YOKE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "47",
        "stowed_local_brep_sha256": "4357c326002e37cecd91c8547e92e61dbbca5b8659fe241a68d750f18d05a214",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-PIN-FIXED",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-PIN-MOVING",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "9215bbb526bef03c9a44356b4b5fc5013767c6cf8905ed0dfa1a0cf54b30a9cd",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "2197aa1a6ec422f2026969b5647be519a593b04c399b395bc073042d49cd6ea8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "HBD-ROD-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "2197aa1a6ec422f2026969b5647be519a593b04c399b395bc073042d49cd6ea8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-2.2737367544323206e-13"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "15",
        "deployed_local_brep_sha256": "6e69ccb3387ca8b16dc2fd76e22e35caabfb9529408dfdf2cdfa4e0f3617bf14",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LATCH-SUPPORT-BRACKET",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "15",
        "stowed_local_brep_sha256": "6e69ccb3387ca8b16dc2fd76e22e35caabfb9529408dfdf2cdfa4e0f3617bf14",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.2789769243681803e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.2789769243681803e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-5.684341886080802e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-4.263256414560601e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-5.684341886080802e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "38",
        "deployed_local_brep_sha256": "b6f6e5920410771a497ea0718cd151aa79a424f33430bd9a4fb8eea1af3eb383",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "38",
        "stowed_local_brep_sha256": "7c3d8b4858f5395099cdf25df52ad9f688927cab788cc4555008eca05bc5d9f9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-5.684341886080802e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-1-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.7763568394002505e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-1-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "4.440892098500626e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-2-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-5.329070518200751e-15"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-2-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "8.881784197001252e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-3-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-4.440892098500626e-15"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-CLIP-3-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "bf32de5c8e1a4f06043ed87020c65a01ab6f6d66b1445f1c9df6f7a32735fdb8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-4.440892098500626e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-1-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "3.979039320256561e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-1-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-2-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.7053025658242404e-13"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-2-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "2.842170943040401e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-3-BELL",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "8.526512829121202e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LINK-PIN-3-CROSSHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "ec689d791e03ecb746b4c764571ddb536ee41965a8aa182108329d57ead6e7d8",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "5.684341886080802e-14"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-BUSHING-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-BUSHING-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-BUSHING-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "71236144d679de530f9c34084a9a415aea1e08d2bf216960794fe32bd4491e53",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-DOG-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-6.661338147750939e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-DOG-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "2.220446049250313e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "5",
        "deployed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "LOCK-DOG-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "5",
        "stowed_local_brep_sha256": "65d822413eafd2027a961cb2499cc6640d2a4f087df367bf88d659e453a36d4c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "2.220446049250313e-16"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "af1bb50a8a397620c68cfabebcb6cfa4af4b9fd1dad9802ebce50703a910197b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "0.2999999999997476",
        "occurrence_id": "LOCK-SPRING-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "f7cdc5911a8c999f17886c5ebc9201e59cf5db76d6020e674e97e306db093cde",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-6.7045401452858755e-09"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "af1bb50a8a397620c68cfabebcb6cfa4af4b9fd1dad9802ebce50703a910197b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "0.2999999999997476",
        "occurrence_id": "LOCK-SPRING-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "f7cdc5911a8c999f17886c5ebc9201e59cf5db76d6020e674e97e306db093cde",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-6.704542088176169e-09"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "af1bb50a8a397620c68cfabebcb6cfa4af4b9fd1dad9802ebce50703a910197b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "0.2999999999997476",
        "occurrence_id": "LOCK-SPRING-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "f7cdc5911a8c999f17886c5ebc9201e59cf5db76d6020e674e97e306db093cde",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-6.704541977153866e-09"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-CARRIER-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-CARRIER-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-CARRIER-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-CARRIER-SCREW-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "d839a2275389c9c4b7dad6975eca5ae76e850af5233109b5798f77a086d562b2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "15",
        "deployed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-FEED-CLAMP-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "15",
        "stowed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "15",
        "deployed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-FEED-CLAMP-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "15",
        "stowed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "15",
        "deployed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "MANIFOLD-FEED-CLAMP-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "15",
        "stowed_local_brep_sha256": "7d0813d51fc3dfeecc3c254c9934c63b7e33cc94d509d1e82ac8dca63d5f439b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "ba0c26db668ea9c73d1f211d6257d40575a7436e02a22c28ad356e68c70b55e4",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "NOSE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "ba0c26db668ea9c73d1f211d6257d40575a7436e02a22c28ad356e68c70b55e4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "c0eb7b45d7cd4b246ee9e830160ae92d9c1f85349ec33aaeb8c3424f33ebd097",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "NOSE-BALLAST-TAPER-PIN-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "c0eb7b45d7cd4b246ee9e830160ae92d9c1f85349ec33aaeb8c3424f33ebd097",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-BUSH-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "03716bf306c8670ddad86d890dbfce109ed58dcbe4dc797918592a836b3d9698",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "60",
        "deployed_local_brep_sha256": "1ecbc8636ef56be60321bfb08dbae13b5d0eca1e89b9d59f658defa69445fdd0",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CARRIER-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "60",
        "stowed_local_brep_sha256": "59daef4c91deefcf94e04d3725e29953cc978153b63afecc5696b5ac500c0351",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "60",
        "deployed_local_brep_sha256": "1ecbc8636ef56be60321bfb08dbae13b5d0eca1e89b9d59f658defa69445fdd0",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CARRIER-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "60",
        "stowed_local_brep_sha256": "59daef4c91deefcf94e04d3725e29953cc978153b63afecc5696b5ac500c0351",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "60",
        "deployed_local_brep_sha256": "1ecbc8636ef56be60321bfb08dbae13b5d0eca1e89b9d59f658defa69445fdd0",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CARRIER-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "60",
        "stowed_local_brep_sha256": "59daef4c91deefcf94e04d3725e29953cc978153b63afecc5696b5ac500c0351",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CLIP-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CLIP-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-CLIP-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "84d031a5f2bdff120426df570a4ced8bb9698c9aa6994dd605c6ec04ba78c384",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-PIN-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-PIN-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-PIN-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "ddd79c99b0b41c87f0ac065a2fdb8c0af539629a838607a12b0018d613c56942",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PIVOT-WASHER-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "3b88402d8763bdd630f6cf4d9fdb09a081e44898f449cedbf251f0e3d877d270",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "13",
        "deployed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PUNCTURE-HEAD-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "13",
        "stowed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "13",
        "deployed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PUNCTURE-HEAD-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "13",
        "stowed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "13",
        "deployed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PUNCTURE-HEAD-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "13",
        "stowed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "13",
        "deployed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "PUNCTURE-HEAD-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "13",
        "stowed_local_brep_sha256": "c6f426a5d1155b9f00e0fba441f29a2fbbbc8b5d2ce6dbcfa0da2c5a19a3b57b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "4cae15173e5477f9015422f62bde2a69e480bf045b309e4c9cc71c2b2d905f88",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "RECOVERY-PIN-BODY",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "4cae15173e5477f9015422f62bde2a69e480bf045b309e4c9cc71c2b2d905f88",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "e6915afda3b60fa0a5ce051957dba6ee57a72238b064167c4db7a8e942616fa7",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "RECOVERY-PIN-CLIP-BODY",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "e6915afda3b60fa0a5ce051957dba6ee57a72238b064167c4db7a8e942616fa7",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "e6915afda3b60fa0a5ce051957dba6ee57a72238b064167c4db7a8e942616fa7",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "RECOVERY-PIN-CLIP-HARNESS",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "e6915afda3b60fa0a5ce051957dba6ee57a72238b064167c4db7a8e942616fa7",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.2434497875801753e-14"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "4cae15173e5477f9015422f62bde2a69e480bf045b309e4c9cc71c2b2d905f88",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "RECOVERY-PIN-HARNESS",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "4cae15173e5477f9015422f62bde2a69e480bf045b309e4c9cc71c2b2d905f88",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "47181b840fbaa8c3611378da48e5c6d13e95241d7c90992cfc1ac8cbae1d074a",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "102.0",
        "occurrence_id": "RECOVERY-TETHER-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "22",
        "stowed_local_brep_sha256": "8b1e4d7207ebdd3b0533abb5a4581c49ebd40d71ffdbffc7f612e8f6907e3686",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "387.6893193991367"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "78",
        "deployed_local_brep_sha256": "10521a641ad72d52182d7cdcb05b9a49c92219fefa608e6d93a56e8dd0d3f848",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-BOWDEN-SHEATH-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "78",
        "stowed_local_brep_sha256": "10521a641ad72d52182d7cdcb05b9a49c92219fefa608e6d93a56e8dd0d3f848",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "52",
        "deployed_local_brep_sha256": "568525f58bf83e6af95f17d8937c452c5eb5704f7b7d175725e780873aa898e1",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "3.1999999999999993",
        "occurrence_id": "ROUTE-BOWDEN-WIRE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "52",
        "stowed_local_brep_sha256": "52fb29df2a0cd536caf8be95ac2cec8c61e4ac6dc6267c2b73b648bae90545e9",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.9047786847172574"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "40",
        "deployed_local_brep_sha256": "acaf0fb981c52f8c92475ef5b0060f17e4416092e5d4a9edb089e487c2b1442d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-GAS-MAIN-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "40",
        "stowed_local_brep_sha256": "acaf0fb981c52f8c92475ef5b0060f17e4416092e5d4a9edb089e487c2b1442d",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "6caeb736619cfc125dda11dddf70bc753e41764005712e53298fb77e55501a5c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-LINER-BOWDEN-SHEATH-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "6caeb736619cfc125dda11dddf70bc753e41764005712e53298fb77e55501a5c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "42d67c7bed29d51c0663f617fbb35b2b78c134fa9aeef27ee0f08a8cac9fd25f",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-LINER-GAS-MAIN-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "42d67c7bed29d51c0663f617fbb35b2b78c134fa9aeef27ee0f08a8cac9fd25f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "621d558d62d92a05c4e1e373f39c9944d9a9d369653e2e30bff077d09f4f8e1b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-LINER-PILOT-LINE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "621d558d62d92a05c4e1e373f39c9944d9a9d369653e2e30bff077d09f4f8e1b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "36",
        "deployed_local_brep_sha256": "0391c6fae5648eea244bb87b07a0d3d6afff7b74ba7457591299a67fde744c23",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-MANIFOLD-FEED-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "36",
        "stowed_local_brep_sha256": "0391c6fae5648eea244bb87b07a0d3d6afff7b74ba7457591299a67fde744c23",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "85",
        "deployed_local_brep_sha256": "257fe07440fa901899a832490f59faaf0ed714a55ce90fbed45c1b8e231bf181",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "ROUTE-PILOT-LINE-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "85",
        "stowed_local_brep_sha256": "257fe07440fa901899a832490f59faaf0ed714a55ce90fbed45c1b8e231bf181",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "7",
        "deployed_local_brep_sha256": "0244f16cca20a30326528a64958f869a4dd26e2c69f655afc4459695aa71e17b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "7",
        "stowed_local_brep_sha256": "91ba7eea09b774ad177b22506f209bc14429725797f7476dd73ae0074b471f23",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "7",
        "deployed_local_brep_sha256": "0244f16cca20a30326528a64958f869a4dd26e2c69f655afc4459695aa71e17b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "7",
        "stowed_local_brep_sha256": "91ba7eea09b774ad177b22506f209bc14429725797f7476dd73ae0074b471f23",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "7",
        "deployed_local_brep_sha256": "0244f16cca20a30326528a64958f869a4dd26e2c69f655afc4459695aa71e17b",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "7",
        "stowed_local_brep_sha256": "91ba7eea09b774ad177b22506f209bc14429725797f7476dd73ae0074b471f23",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.4210854715202004e-14"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "49",
        "deployed_local_brep_sha256": "22a4e6db0890243a7ed4001c5b6ac92ebf19fdec89cbbd7905571a0db5066660",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-GUIDE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "49",
        "stowed_local_brep_sha256": "26ebf2a2c7c8643b8e8490779b59bcd2965508262e45fc31f59deae912b30239",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "49",
        "deployed_local_brep_sha256": "22a4e6db0890243a7ed4001c5b6ac92ebf19fdec89cbbd7905571a0db5066660",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-GUIDE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "49",
        "stowed_local_brep_sha256": "26ebf2a2c7c8643b8e8490779b59bcd2965508262e45fc31f59deae912b30239",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "49",
        "deployed_local_brep_sha256": "22a4e6db0890243a7ed4001c5b6ac92ebf19fdec89cbbd7905571a0db5066660",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-GUIDE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "49",
        "stowed_local_brep_sha256": "26ebf2a2c7c8643b8e8490779b59bcd2965508262e45fc31f59deae912b30239",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "10",
        "deployed_local_brep_sha256": "aa84ae4ac4d9b45d16d8c53e2661dccd46e1511811b1c16e20e043ea12558e4d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "10",
        "stowed_local_brep_sha256": "02ee356007a5449d50f66236cba58f7ba22827124023c0db78bba4c3f6e4a97f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "8.881784197001252e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "10",
        "deployed_local_brep_sha256": "aa84ae4ac4d9b45d16d8c53e2661dccd46e1511811b1c16e20e043ea12558e4d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "10",
        "stowed_local_brep_sha256": "02ee356007a5449d50f66236cba58f7ba22827124023c0db78bba4c3f6e4a97f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "2.220446049250313e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "10",
        "deployed_local_brep_sha256": "aa84ae4ac4d9b45d16d8c53e2661dccd46e1511811b1c16e20e043ea12558e4d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "10",
        "stowed_local_brep_sha256": "02ee356007a5449d50f66236cba58f7ba22827124023c0db78bba4c3f6e4a97f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-1.1102230246251565e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-PIN-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "8.881784197001252e-16"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-PIN-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "1.7763568394002505e-15"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "STOW-DOG-INHIBIT-PIN-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "87a7475236faa39270a6a3c181669e73fd0852df867364abd2e10e03b255d9ac",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-8.881784197001252e-16"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "3e11019c76777cff42a8c05dc1705ae37c3646075142fae2b577e385f1735e31",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "3.4999999999999245",
        "occurrence_id": "STOW-DOG-SPRING-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "1bd7c74227df529ae5b5ed097bd6888831b8ad2043632757764cad145fc24ce7",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "6.557642255600182e-09"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "3e11019c76777cff42a8c05dc1705ae37c3646075142fae2b577e385f1735e31",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "3.4999999999999245",
        "occurrence_id": "STOW-DOG-SPRING-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "1bd7c74227df529ae5b5ed097bd6888831b8ad2043632757764cad145fc24ce7",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "6.557642255600182e-09"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "3e11019c76777cff42a8c05dc1705ae37c3646075142fae2b577e385f1735e31",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "3.4999999999999245",
        "occurrence_id": "STOW-DOG-SPRING-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "1bd7c74227df529ae5b5ed097bd6888831b8ad2043632757764cad145fc24ce7",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "6.557642290294652e-09"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "f343e7518c3e0dd5241fd8f283ae07962fb24e3104a1167cc28effce6c99ff17",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "TETHER-THIMBLE-BODY",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "f343e7518c3e0dd5241fd8f283ae07962fb24e3104a1167cc28effce6c99ff17",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "f343e7518c3e0dd5241fd8f283ae07962fb24e3104a1167cc28effce6c99ff17",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "TETHER-THIMBLE-HARNESS",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "f343e7518c3e0dd5241fd8f283ae07962fb24e3104a1167cc28effce6c99ff17",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "TRIGGER-MOUNT-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "TRIGGER-MOUNT-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "TRIGGER-MOUNT-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "5bc9f7585081a6b1cda8f57923bc0b289937dec50c43f4aa4946e96a2cda5bbe",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "CONSUMED",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "b75e564ea697b3a7fd71e9a85cc720b3dc567bf9c55fc9b26e9fa3eac1e5b822",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WATER-BOBBIN-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "b75e564ea697b3a7fd71e9a85cc720b3dc567bf9c55fc9b26e9fa3eac1e5b822",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "32",
        "deployed_local_brep_sha256": "0a4cb36e295fd3fc9804dbc0b5178e82983b431d83d8ac8fb4583f8ae5eb9c5c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WATER-BOBBIN-SERVICE-CAP-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "32",
        "stowed_local_brep_sha256": "0a4cb36e295fd3fc9804dbc0b5178e82983b431d83d8ac8fb4583f8ae5eb9c5c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "12",
        "deployed_local_brep_sha256": "688f15653b4f6ececb67326f5c875c0f2480807e7620bccaf3bdee91d3b92178",
        "deployed_solid_count": "3",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WATER-INLET-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "12",
        "stowed_local_brep_sha256": "688f15653b4f6ececb67326f5c875c0f2480807e7620bccaf3bdee91d3b92178",
        "stowed_solid_count": "3",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "120",
        "deployed_local_brep_sha256": "881a2c091640e916a040019db09b078366dbed1253f2e0c81776b5f3f5d98f19",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WATER-TRIGGER-HSG-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "120",
        "stowed_local_brep_sha256": "881a2c091640e916a040019db09b078366dbed1253f2e0c81776b5f3f5d98f19",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "7",
        "deployed_local_brep_sha256": "e2fff25ce45455c838b67427b37eb0473df044b42d277109d9333c62068a1fd2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-AFT-RAIL-SUPPORT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "7",
        "stowed_local_brep_sha256": "e2fff25ce45455c838b67427b37eb0473df044b42d277109d9333c62068a1fd2",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "3",
        "deployed_local_brep_sha256": "0e86a2c4f32633d752cb272c4c874f7a10e26765f0d6c6491eb9b2fa89c8a9ff",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "84.99999999999305",
        "occurrence_id": "WP04-EJECTOR-SPRING",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "3",
        "stowed_local_brep_sha256": "e73c1bfac6cb8de39bc512952c67f3544085195c2464eeca91e4ec3d2fa4dedf",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-4.264101380613283e-05"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "17",
        "deployed_local_brep_sha256": "0ce7822f6e34ed57850aee9ea20bbc98a9aa5eca52c284d5733ee003197cb522",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FIXED-SLEEVE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "17",
        "stowed_local_brep_sha256": "0ce7822f6e34ed57850aee9ea20bbc98a9aa5eca52c284d5733ee003197cb522",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "40",
        "deployed_local_brep_sha256": "ea6c4de8d11e83a5e4d16b84cac75be2705204116fbd433f588d4c8776034020",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FOLLOWER-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "40",
        "stowed_local_brep_sha256": "c810d8fdec5024645ba2c1f4a8e48c452c39433f526ea84ef3b130b00e87942b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "4",
        "deployed_local_brep_sha256": "dc3d091b8d2995d4bfe20a56d4cb6364c3be61127ea83575f289fc04c3082af6",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-FULLFLOW-MANIFOLD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "4",
        "stowed_local_brep_sha256": "dc3d091b8d2995d4bfe20a56d4cb6364c3be61127ea83575f289fc04c3082af6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-GUIDE-RAIL-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-GUIDE-RAIL-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-GUIDE-RAIL-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "a8c4452feaf5c0a886bef87f4afdd59a263d60e885d814ab50948226315154c6",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "30",
        "deployed_local_brep_sha256": "0af1f187ac6415e962cdc9f16cf13d7a01db26b48ff9ccc687ec7878746477ed",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-LATCH-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "30",
        "stowed_local_brep_sha256": "0af1f187ac6415e962cdc9f16cf13d7a01db26b48ff9ccc687ec7878746477ed",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-LATCH-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-LATCH-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "6",
        "deployed_local_brep_sha256": "0350d3afc11634e30983c6db1d8f95a560dbf336623ae8d9f4bf049787f6ba6c",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-MANIFOLD-BRACKET",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "6",
        "stowed_local_brep_sha256": "0350d3afc11634e30983c6db1d8f95a560dbf336623ae8d9f4bf049787f6ba6c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "20",
        "deployed_local_brep_sha256": "5f1368e9bd00ee92c23fd01a0a208bfdf38f5a76ae2f808fcfe20a23c257f6e2",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-MOVING-SLEEVE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "20",
        "stowed_local_brep_sha256": "803462aff3c1937d9ffb844a95e6862b95de98d1df4dd2b51aec87f709e1b57c",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "14",
        "deployed_local_brep_sha256": "9a01872b35b7a5bc476affcfa024ed236a49cabedd7e3e1c93b7ddba54d05b41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "14",
        "stowed_local_brep_sha256": "73037361b9a9c1682b56a64312533dee4f1932cc97204ae1f6a09beecb73150b",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "58",
        "deployed_local_brep_sha256": "12adde983692fb66f42bfa1e3d62462d495f60c79a0f92b85a4d06d99b06ced3",
        "deployed_solid_count": "2",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-REACTION-BULKHEAD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "58",
        "stowed_local_brep_sha256": "12adde983692fb66f42bfa1e3d62462d495f60c79a0f92b85a4d06d99b06ced3",
        "stowed_solid_count": "2",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "d916fb54623c20365b72a495cc44377c533b74dafa21b397cb377793dc1189d0",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-SEAR-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "c861ce929fd7c1858a26cf792ee46bb6cddf649a4273fda5b1af6e1b48a6749f",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "511765122036c53a0acbe99a7cec24176e69693f289e46500203804524c78d41",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP04-SEAR-CLIP-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "10cc1a1614eff86d5ddae14ccf8351d7c6743a4cfcd1946c68fd891d7d53ff19",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "MOVING",
        "deployed_face_count": "28",
        "deployed_local_brep_sha256": "7195748f9f152fe3a8a0488a6f8440a84e1ebc80b929721125ff4af1af5b2119",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-DOOR-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "28",
        "stowed_local_brep_sha256": "bd62234619121d351641f5fc45f6bb153f605bd677dfec7e01eced1ea5fef353",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "-6.366462912410498e-12"
      },
      {
        "classification": "FLEXIBLE",
        "deployed_face_count": "30",
        "deployed_local_brep_sha256": "0238b37af08e1e069a759b69a046ec9e671d0a5ab68b00aa56023673e269d1c6",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "True",
        "local_bbox_max_abs_delta_mm": "30.210000100000002",
        "occurrence_id": "WP05-DOOR-LANYARD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "19",
        "stowed_local_brep_sha256": "fa2ace43a54054498f1799eefc96fb8d1a2d6ade226ef6f58279cb4dc0659de4",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "False",
        "volume_delta_mm3": "131.01739627938727"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "8",
        "deployed_local_brep_sha256": "822c7ab2603fe8e5d28e8ac5cbc3a254cf245792b0151cebc851b3a88ba71b4d",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-HINGE-CLIP",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "8",
        "stowed_local_brep_sha256": "822c7ab2603fe8e5d28e8ac5cbc3a254cf245792b0151cebc851b3a88ba71b4d",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "9",
        "deployed_local_brep_sha256": "624e8ab778188fef4ca61bb2a14369933cdb03c11bbe87000827792d2ed9c83e",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-HINGE-PIN",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "9",
        "stowed_local_brep_sha256": "624e8ab778188fef4ca61bb2a14369933cdb03c11bbe87000827792d2ed9c83e",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "72",
        "deployed_local_brep_sha256": "9c66783da6a86e83273c0b92da417b4454996791d134e0d35880197e9059b8bd",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-SERVICE-THROAT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL",
        "stowed_face_count": "72",
        "stowed_local_brep_sha256": "340432e284c804cddac39b28585a0db683e3e69843fc7627e09b01a98ff3cebf",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-4",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-5",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      },
      {
        "classification": "FIXED",
        "deployed_face_count": "11",
        "deployed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "deployed_solid_count": "1",
        "exact_local_brep_match": "True",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "local_bbox_max_abs_delta_mm": "0.0",
        "occurrence_id": "WP05-THROAT-SCREW-6",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "PASS",
        "stowed_face_count": "11",
        "stowed_local_brep_sha256": "cea8dfa8d845acb8aa928aa8db56fa657ab5af909f8f3b28d32e2b5315064cda",
        "stowed_solid_count": "1",
        "surface_type_counts_match": "True",
        "volume_delta_mm3": "0.0"
      }
    ],
    "source": "work/final_analysis/validation/state_parity.csv",
    "status_counts": {
      "FAIL": 64,
      "PASS": 215
    },
    "unresolved_row_count": 64,
    "unresolved_rows": [
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "AFT-SHELL-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-PAD-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-PAD-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-PAD-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "ARM-STOP-SCREW-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "CROSSHEAD-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-SECTOR-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FIXED-STOP-SCREW-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "FWD-RING-02",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-1-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-1-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-2-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-2-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-3-SCREW-AFT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "GUIDE-RAIL-3-SCREW-FWD",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "HARNESS-TERMINAL-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-1-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-1-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-2-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-2-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-3-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "LINK-3-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "PIVOT-CARRIER-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "PIVOT-CARRIER-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "PIVOT-CARRIER-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-GUIDE-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-GUIDE-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-GUIDE-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-FOLLOWER-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-LATCH-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-LATCH-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-MOVING-SLEEVE",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-1",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-2",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-3",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-SEAR-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP04-SEAR-CLIP-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "MOVING",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP05-DOOR-001",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      },
      {
        "classification": "FIXED",
        "exact_local_brep_match": "False",
        "fingerprint_error": "",
        "flexible_state_geometry_exception": "False",
        "occurrence_id": "WP05-SERVICE-THROAT",
        "present_deployed": "True",
        "present_stowed": "True",
        "same_part_number": "True",
        "status": "FAIL"
      }
    ]
  }
}
```

## Remaining pairs, authorized contacts, invalids, and validator defects

- Remaining unauthorized positive pairs: `39`
- Authorized endpoint contact records: `210`
- Motion documented positive-pair observations: `1215`
- Category-B unauthorized rigid positive-volume pairs: `33`
- Unresolved nonrigid-involved positive-volume pairs: `6`
- Validator-defect records: `66`

```json
{
  "authorized_contacts": {
    "endpoint_pair_record_count": 210,
    "endpoint_used_exception_ids": {
      "DEPLOYED": [
        "FIT-ACTUATOR-RETAINER-GS19-FIXED",
        "FIT-ACTUATOR-RETAINER-GS19-MOVING",
        "FIT-ACTUATOR-RETAINER-HBD-FIXED",
        "FIT-ACTUATOR-RETAINER-HBD-MOVING",
        "FIT-BAYONET-WATER-BOBBIN-SERVICE-CAP",
        "FIT-CIRCLIP-FULLFLOW",
        "FIT-DETENT-THREAD-1",
        "FIT-DETENT-THREAD-2",
        "FIT-DETENT-THREAD-3",
        "FIT-DETENT-THREAD-4",
        "FIT-GLAND-BOWDEN-SHEATH-AFT-ROUTE",
        "FIT-GLAND-GAS-MAIN-AFT-ROUTE",
        "FIT-GLAND-PILOT-LINE-AFT-ROUTE",
        "FIT-HINGE-RETAINER",
        "FIT-MANIFOLD-BRACKET-WELD",
        "FIT-PILOT-LATCH-PORT",
        "FIT-PIVOT-RETAINER-1",
        "FIT-PIVOT-RETAINER-2",
        "FIT-PIVOT-RETAINER-3",
        "FIT-PRESS-LOCK-BUSHING-1",
        "FIT-PRESS-LOCK-BUSHING-2",
        "FIT-PRESS-LOCK-BUSHING-3",
        "FIT-RECOVERY-RETAINER-BODY",
        "FIT-RECOVERY-RETAINER-HARNESS",
        "FIT-RF-SEAM-01-02",
        "FIT-RF-SEAM-02-03",
        "FIT-RF-SEAM-03-04",
        "FIT-RF-SEAM-04-05",
        "FIT-RF-SEAM-05-06",
        "FIT-RF-SEAM-06-07",
        "FIT-RF-SEAM-07-08",
        "FIT-RF-SEAM-08-01",
        "FIT-STITCH-XN",
        "FIT-STITCH-XP",
        "FIT-STITCH-YN",
        "FIT-STITCH-YP",
        "FIT-STOW-INHIBIT-KEEPER-1",
        "FIT-STOW-INHIBIT-KEEPER-2",
        "FIT-STOW-INHIBIT-KEEPER-3",
        "FIT-TERMINAL-LOOP-XN",
        "FIT-TERMINAL-LOOP-XP",
        "FIT-TETHER-SPLICE-BODY",
        "FIT-TETHER-SPLICE-HARNESS",
        "FIT-THREAD-ARM-STOP-1-1",
        "FIT-THREAD-ARM-STOP-1-2",
        "FIT-THREAD-ARM-STOP-2-1",
        "FIT-THREAD-ARM-STOP-2-2",
        "FIT-THREAD-ARM-STOP-3-1",
        "FIT-THREAD-ARM-STOP-3-2",
        "FIT-THREAD-BACKUP-GUIDE-1",
        "FIT-THREAD-BACKUP-SEAT-2",
        "FIT-THREAD-BOOSTER-BAND-1-1",
        "FIT-THREAD-BOOSTER-BAND-1-2",
        "FIT-THREAD-BOOSTER-BAND-1-3",
        "FIT-THREAD-BOOSTER-BAND-2-1",
        "FIT-THREAD-BOOSTER-BAND-2-2",
        "FIT-THREAD-BOOSTER-BAND-2-3",
        "FIT-THREAD-BOOSTER-BAND-3-1",
        "FIT-THREAD-BOOSTER-BAND-3-2",
        "FIT-THREAD-BOOSTER-BAND-3-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-3",
        "FIT-THREAD-CROSSHEAD-GUIDE-LOCK",
        "FIT-THREAD-FIXED-STOP-CARRIER-1-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-1-2",
        "FIT-THREAD-FIXED-STOP-CARRIER-2-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-2-2",
        "FIT-THREAD-FIXED-STOP-CARRIER-3-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-3-2",
        "FIT-THREAD-FWD-CARRIER-1",
        "FIT-THREAD-FWD-CARRIER-2",
        "FIT-THREAD-FWD-CARRIER-3",
        "FIT-THREAD-FWD-CARRIER-4",
        "FIT-THREAD-GUIDE-RAIL-1-AFT",
        "FIT-THREAD-GUIDE-RAIL-1-FWD",
        "FIT-THREAD-GUIDE-RAIL-2-AFT",
        "FIT-THREAD-GUIDE-RAIL-2-FWD",
        "FIT-THREAD-GUIDE-RAIL-3-AFT",
        "FIT-THREAD-GUIDE-RAIL-3-FWD",
        "FIT-THREAD-LATCH-SUPPORT-1",
        "FIT-THREAD-LATCH-SUPPORT-2",
        "FIT-THREAD-MANIFOLD-CARRIER-1",
        "FIT-THREAD-MANIFOLD-CARRIER-2",
        "FIT-THREAD-MANIFOLD-CARRIER-3",
        "FIT-THREAD-MANIFOLD-CARRIER-4",
        "FIT-THREAD-TRIGGER-MOUNT-1",
        "FIT-THREAD-TRIGGER-MOUNT-2",
        "FIT-THREAD-TRIGGER-MOUNT-3",
        "FIT-THREAD-WP04-FIXED-SLEEVE-1",
        "FIT-THREAD-WP04-FIXED-SLEEVE-2",
        "FIT-THREAD-WP04-FIXED-SLEEVE-3",
        "FIT-THREAD-WP04-MOVING-SLEEVE-1",
        "FIT-THREAD-WP04-MOVING-SLEEVE-2",
        "FIT-THREAD-WP04-MOVING-SLEEVE-3",
        "FIT-THREAD-WP05-THROAT-1",
        "FIT-THREAD-WP05-THROAT-2",
        "FIT-THREAD-WP05-THROAT-3",
        "FIT-THREAD-WP05-THROAT-4",
        "FIT-THREAD-WP05-THROAT-5",
        "FIT-THREAD-WP05-THROAT-6",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-1",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-2",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-3"
      ],
      "STOWED": [
        "FIT-ACTUATOR-RETAINER-GS19-FIXED",
        "FIT-ACTUATOR-RETAINER-GS19-MOVING",
        "FIT-ACTUATOR-RETAINER-HBD-FIXED",
        "FIT-ACTUATOR-RETAINER-HBD-MOVING",
        "FIT-BAYONET-WATER-BOBBIN-SERVICE-CAP",
        "FIT-CIRCLIP-FULLFLOW",
        "FIT-DETENT-THREAD-1",
        "FIT-DETENT-THREAD-2",
        "FIT-DETENT-THREAD-3",
        "FIT-DETENT-THREAD-4",
        "FIT-GLAND-BOWDEN-SHEATH-AFT-ROUTE",
        "FIT-GLAND-GAS-MAIN-AFT-ROUTE",
        "FIT-GLAND-PILOT-LINE-AFT-ROUTE",
        "FIT-HINGE-RETAINER",
        "FIT-MANIFOLD-BRACKET-WELD",
        "FIT-PILOT-LATCH-PORT",
        "FIT-PIVOT-RETAINER-1",
        "FIT-PIVOT-RETAINER-2",
        "FIT-PIVOT-RETAINER-3",
        "FIT-PRESS-LOCK-BUSHING-1",
        "FIT-PRESS-LOCK-BUSHING-2",
        "FIT-PRESS-LOCK-BUSHING-3",
        "FIT-RECOVERY-RETAINER-BODY",
        "FIT-RECOVERY-RETAINER-HARNESS",
        "FIT-STITCH-XN",
        "FIT-STITCH-XP",
        "FIT-STITCH-YN",
        "FIT-STITCH-YP",
        "FIT-STOW-INHIBIT-KEEPER-1",
        "FIT-STOW-INHIBIT-KEEPER-2",
        "FIT-STOW-INHIBIT-KEEPER-3",
        "FIT-TETHER-SPLICE-BODY",
        "FIT-TETHER-SPLICE-HARNESS",
        "FIT-THREAD-ARM-STOP-1-1",
        "FIT-THREAD-ARM-STOP-1-2",
        "FIT-THREAD-ARM-STOP-2-1",
        "FIT-THREAD-ARM-STOP-2-2",
        "FIT-THREAD-ARM-STOP-3-1",
        "FIT-THREAD-ARM-STOP-3-2",
        "FIT-THREAD-BACKUP-GUIDE-1",
        "FIT-THREAD-BACKUP-SEAT-2",
        "FIT-THREAD-BOOSTER-BAND-1-1",
        "FIT-THREAD-BOOSTER-BAND-1-2",
        "FIT-THREAD-BOOSTER-BAND-1-3",
        "FIT-THREAD-BOOSTER-BAND-2-1",
        "FIT-THREAD-BOOSTER-BAND-2-2",
        "FIT-THREAD-BOOSTER-BAND-2-3",
        "FIT-THREAD-BOOSTER-BAND-3-1",
        "FIT-THREAD-BOOSTER-BAND-3-2",
        "FIT-THREAD-BOOSTER-BAND-3-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-1-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-2-3",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-1",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-2",
        "FIT-THREAD-BOOSTER-SHELL-LUG-3-3",
        "FIT-THREAD-CROSSHEAD-GUIDE-LOCK",
        "FIT-THREAD-FIXED-STOP-CARRIER-1-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-1-2",
        "FIT-THREAD-FIXED-STOP-CARRIER-2-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-2-2",
        "FIT-THREAD-FIXED-STOP-CARRIER-3-1",
        "FIT-THREAD-FIXED-STOP-CARRIER-3-2",
        "FIT-THREAD-FWD-CARRIER-1",
        "FIT-THREAD-FWD-CARRIER-2",
        "FIT-THREAD-FWD-CARRIER-3",
        "FIT-THREAD-FWD-CARRIER-4",
        "FIT-THREAD-GUIDE-RAIL-1-AFT",
        "FIT-THREAD-GUIDE-RAIL-1-FWD",
        "FIT-THREAD-GUIDE-RAIL-2-AFT",
        "FIT-THREAD-GUIDE-RAIL-2-FWD",
        "FIT-THREAD-GUIDE-RAIL-3-AFT",
        "FIT-THREAD-GUIDE-RAIL-3-FWD",
        "FIT-THREAD-LATCH-SUPPORT-1",
        "FIT-THREAD-LATCH-SUPPORT-2",
        "FIT-THREAD-MANIFOLD-CARRIER-1",
        "FIT-THREAD-MANIFOLD-CARRIER-2",
        "FIT-THREAD-MANIFOLD-CARRIER-3",
        "FIT-THREAD-MANIFOLD-CARRIER-4",
        "FIT-THREAD-TRIGGER-MOUNT-1",
        "FIT-THREAD-TRIGGER-MOUNT-2",
        "FIT-THREAD-TRIGGER-MOUNT-3",
        "FIT-THREAD-WP04-FIXED-SLEEVE-1",
        "FIT-THREAD-WP04-FIXED-SLEEVE-2",
        "FIT-THREAD-WP04-FIXED-SLEEVE-3",
        "FIT-THREAD-WP04-MOVING-SLEEVE-1",
        "FIT-THREAD-WP04-MOVING-SLEEVE-2",
        "FIT-THREAD-WP04-MOVING-SLEEVE-3",
        "FIT-THREAD-WP05-THROAT-1",
        "FIT-THREAD-WP05-THROAT-2",
        "FIT-THREAD-WP05-THROAT-3",
        "FIT-THREAD-WP05-THROAT-4",
        "FIT-THREAD-WP05-THROAT-5",
        "FIT-THREAD-WP05-THROAT-6",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-1",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-2",
        "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-3"
      ]
    },
    "motion_documented_positive_pair_count": 1215,
    "motion_pair_record_count": 1215,
    "motion_used_exception_ids": [
      "FIT-ACTUATOR-RETAINER-GS19-MOVING",
      "FIT-ACTUATOR-RETAINER-HBD-MOVING",
      "FIT-CIRCLIP-FULLFLOW",
      "FIT-STOW-INHIBIT-KEEPER-1",
      "FIT-STOW-INHIBIT-KEEPER-2",
      "FIT-STOW-INHIBIT-KEEPER-3",
      "FIT-THREAD-ARM-STOP-1-1",
      "FIT-THREAD-ARM-STOP-1-2",
      "FIT-THREAD-ARM-STOP-2-1",
      "FIT-THREAD-ARM-STOP-2-2",
      "FIT-THREAD-ARM-STOP-3-1",
      "FIT-THREAD-ARM-STOP-3-2",
      "FIT-THREAD-WP04-MOVING-SLEEVE-1",
      "FIT-THREAD-WP04-MOVING-SLEEVE-2",
      "FIT-THREAD-WP04-MOVING-SLEEVE-3"
    ],
    "positive_pair_records": [
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542138985,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-1",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 273,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542821345,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-2",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 579,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542204727,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-3",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 884,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.05271327920170785,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-MANIFOLD-BRACKET-WELD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-SHELL-001",
        "occurrence_b": "WP04-MANIFOLD-BRACKET",
        "pair_index": 1506,
        "part_number_a": "DF8-R2-AFT-SHELL-001",
        "part_number_b": "DF8-FINAL-WP04-MANIFOLD-BRACKET",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.479534848029117,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-1",
        "occurrence_b": "ARM-STOP-SCREW-1-1",
        "pair_index": 1534,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.409324607565027,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-1",
        "occurrence_b": "ARM-STOP-SCREW-1-2",
        "pair_index": 1535,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.479534848029397,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-2",
        "occurrence_b": "ARM-STOP-SCREW-2-1",
        "pair_index": 1837,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.409324607587255,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-2",
        "occurrence_b": "ARM-STOP-SCREW-2-2",
        "pair_index": 1838,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.479534848025739,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-3",
        "occurrence_b": "ARM-STOP-SCREW-3-1",
        "pair_index": 2139,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.409324607562397,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-3",
        "occurrence_b": "ARM-STOP-SCREW-3-2",
        "pair_index": 2140,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.180153346645108,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BACKUP-GUIDE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BACKUP-GUIDE-SCREW-1",
        "occurrence_b": "BACKUP-SPRING-GUIDE",
        "pair_index": 5954,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-BACKUP-SPRING-GUIDE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.9395736106933334,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BACKUP-SEAT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BACKUP-GUIDE-SCREW-2",
        "occurrence_b": "BACKUP-SPRING-FIXED-SEAT",
        "pair_index": 6239,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-BACKUP-SPRING-FIXED-SEAT-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737212,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-1",
        "pair_index": 10431,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372177,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-2",
        "pair_index": 10702,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372177,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-3",
        "pair_index": 10972,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-1",
        "pair_index": 11241,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372161,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-2",
        "pair_index": 11509,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372161,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-3",
        "pair_index": 11776,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-1",
        "pair_index": 12042,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-2",
        "pair_index": 12307,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-3",
        "pair_index": 12571,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453364124,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 12913,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453364142,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13174,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453389447,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13434,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381605,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13693,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381519,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13951,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381484,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14208,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453369471,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14464,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.07072245336946,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14719,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.0707224533694255,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14973,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451333,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-1",
        "pair_index": 22637,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451332,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-2",
        "pair_index": 22638,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451328,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-3",
        "pair_index": 22639,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.13590672845133,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-4",
        "pair_index": 22640,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 23.739884709821567,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-CROSSHEAD-GUIDE-LOCK",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "CROSSHEAD-GUIDE-001",
        "occurrence_b": "CROSSHEAD-GUIDE-LOCK-SCREW-001",
        "pair_index": 23843,
        "part_number_a": "DF8-R2-CROSSHEAD-GUIDE-001",
        "part_number_b": "SSCL-M4-8-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.5285044915129955,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-1",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 24694,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528513630543694,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-2",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 24906,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528504491591356,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-3",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 25117,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528513630616544,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-4",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 25327,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.048594445105096265,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-1",
        "occurrence_b": "LOCK-BUSHING-1",
        "pair_index": 26044,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.048594445107637586,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-2",
        "occurrence_b": "LOCK-BUSHING-2",
        "pair_index": 26250,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0485944450997962,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-3",
        "occurrence_b": "LOCK-BUSHING-3",
        "pair_index": 26455,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.4882127413511657,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-1-1",
        "occurrence_b": "PIVOT-CARRIER-1",
        "pair_index": 27877,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741351913,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-1-2",
        "occurrence_b": "PIVOT-CARRIER-1",
        "pair_index": 28074,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741349402,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-2-1",
        "occurrence_b": "PIVOT-CARRIER-2",
        "pair_index": 28270,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741345631,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-2-2",
        "occurrence_b": "PIVOT-CARRIER-2",
        "pair_index": 28465,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741344852,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-3-1",
        "occurrence_b": "PIVOT-CARRIER-3",
        "pair_index": 28659,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741343035,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-3-2",
        "occurrence_b": "PIVOT-CARRIER-3",
        "pair_index": 28852,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 5.274151981612108,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-CIRCLIP-FULLFLOW",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FULLFLOW-VALVE-001",
        "occurrence_b": "FULLFLOW-VALVE-CIRCLIP-001",
        "pair_index": 28946,
        "part_number_a": "DF8-R2-FULLFLOW-VALVE-001",
        "part_number_b": "HEC-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.31968989868607,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-1",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 29894,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.3196898986861125,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-2",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30079,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.319689898686151,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-3",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30263,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.319689898686114,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-4",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30446,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 0.000397770638736777,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-BOWDEN-SHEATH-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-BOWDEN-SHEATH-AFT",
        "occurrence_b": "ROUTE-BOWDEN-SHEATH-001",
        "pair_index": 32332,
        "part_number_a": "DF8-FINAL-BOWDEN-SHEATH-RING-GLAND",
        "part_number_b": "DF8-FINAL-BOWDEN-SHEATH-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0006317453020051643,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-GAS-MAIN-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-GAS-MAIN-AFT",
        "occurrence_b": "ROUTE-GAS-MAIN-001",
        "pair_index": 32677,
        "part_number_a": "DF8-FINAL-GAS-MAIN-RING-GLAND",
        "part_number_b": "DF8-FINAL-GAS-MAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.00034994188320845634,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-PILOT-LINE-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-PILOT-LINE-AFT",
        "occurrence_b": "ROUTE-PILOT-LINE-001",
        "pair_index": 33021,
        "part_number_a": "DF8-FINAL-PILOT-LINE-RING-GLAND",
        "part_number_b": "DF8-FINAL-PILOT-LINE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.1133538920148057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-GS19-FIXED",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GS19-CLIP-FIXED",
        "occurrence_b": "GS19-PIN-FIXED",
        "pair_index": 33586,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.11335389201642448,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-GS19-MOVING",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GS19-CLIP-MOVING",
        "occurrence_b": "GS19-PIN-MOVING",
        "pair_index": 33751,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343179,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-1-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-1-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 34683,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.479534848029097,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-1-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-1-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 34862,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.1598449493431797,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-2-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-2-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 34998,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.47953484802909,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-2-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-2-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 35175,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.1598449493431797,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-3-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-3-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 35309,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.47953484802909,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-3-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-3-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 35484,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 35.8982608128629,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-XN",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-1",
        "occurrence_b": "HARNESS-LEG-XN",
        "pair_index": 35499,
        "part_number_a": "DF8-R2-HARNESS-BAND-1",
        "part_number_b": "DF8-R2-HARNESS-LEG-XN",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 35.898260925047026,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-XP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-1",
        "occurrence_b": "HARNESS-LEG-XP",
        "pair_index": 35500,
        "part_number_a": "DF8-R2-HARNESS-BAND-1",
        "part_number_b": "DF8-R2-HARNESS-LEG-XP",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 50.726876246390816,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-YN",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-2",
        "occurrence_b": "HARNESS-LEG-YN",
        "pair_index": 35653,
        "part_number_a": "DF8-R2-HARNESS-BAND-2",
        "part_number_b": "DF8-R2-HARNESS-LEG-YN",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 50.72687624614491,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-YP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-2",
        "occurrence_b": "HARNESS-LEG-YP",
        "pair_index": 35654,
        "part_number_a": "DF8-R2-HARNESS-BAND-2",
        "part_number_b": "DF8-R2-HARNESS-LEG-YP",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.11335389202371621,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-HBD-FIXED",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HBD-CLIP-FIXED",
        "occurrence_b": "HBD-PIN-FIXED",
        "pair_index": 36841,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.11335389202696967,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-HBD-MOVING",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HBD-CLIP-MOVING",
        "occurrence_b": "HBD-PIN-MOVING",
        "pair_index": 36985,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343107,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-LATCH-SUPPORT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "LATCH-SUPPORT-BRACKET",
        "occurrence_b": "WP04-LATCH-SCREW-1",
        "pair_index": 37804,
        "part_number_a": "WP04-LATCH-SUPPORT-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343281,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-LATCH-SUPPORT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "LATCH-SUPPORT-BRACKET",
        "occurrence_b": "WP04-LATCH-SCREW-2",
        "pair_index": 37805,
        "part_number_a": "WP04-LATCH-SUPPORT-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.27930206921818324,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-1",
        "occurrence_b": "PIVOT-PIN-1",
        "pair_index": 43276,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.2793020692218378,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-2",
        "occurrence_b": "PIVOT-PIN-2",
        "pair_index": 43365,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.27930206921849016,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-3",
        "occurrence_b": "PIVOT-PIN-3",
        "pair_index": 43453,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.18993000381426606,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RECOVERY-RETAINER-BODY",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-PIN-BODY",
        "occurrence_b": "RECOVERY-PIN-CLIP-BODY",
        "pair_index": 44578,
        "part_number_a": "DF8-R2-RECOVERY-PIN-006",
        "part_number_b": "DF8-R2-RECOVERY-E-RING-006",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.18993000380696404,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RECOVERY-RETAINER-HARNESS",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-PIN-CLIP-HARNESS",
        "occurrence_b": "RECOVERY-PIN-HARNESS",
        "pair_index": 44723,
        "part_number_a": "DF8-R2-RECOVERY-E-RING-006",
        "part_number_b": "DF8-R2-RECOVERY-PIN-006",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 2.0451638440645596,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TETHER-SPLICE-BODY",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-TETHER-001",
        "occurrence_b": "TETHER-THIMBLE-BODY",
        "pair_index": 44887,
        "part_number_a": "AMSTEEL-BLUE-872-7-64-R2",
        "part_number_b": "DF8-R2-TETHER-THIMBLE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 2.6144001792706266,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TETHER-SPLICE-HARNESS",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-TETHER-001",
        "occurrence_b": "TETHER-THIMBLE-HARNESS",
        "pair_index": 44888,
        "part_number_a": "AMSTEEL-BLUE-872-7-64-R2",
        "part_number_b": "DF8-R2-TETHER-THIMBLE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.03241993544917625,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PILOT-LATCH-PORT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ROUTE-PILOT-LINE-001",
        "occurrence_b": "WP04-LATCH-001",
        "pair_index": 45425,
        "part_number_a": "DF8-FINAL-PILOT-LINE-001",
        "part_number_b": "WP04-LATCH-HOUSING-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.016171224265223036,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-1",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-1",
        "pair_index": 45796,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.016171224264798903,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-2",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-2",
        "pair_index": 45850,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.016171224238163466,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-3",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-3",
        "pair_index": 45903,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363226142,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-1",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46340,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363211198,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-2",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46382,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363240884,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-3",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46423,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.6498249873354216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-BAYONET-WATER-BOBBIN-SERVICE-CAP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WATER-BOBBIN-SERVICE-CAP-001",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46502,
        "part_number_a": "DF8-WATER-BOBBIN-SERVICE-CAP-001",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-1",
        "pair_index": 46751,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-2",
        "pair_index": 46752,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-3",
        "pair_index": 46753,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.295751677794314,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-1",
        "pair_index": 47108,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.2957516777943106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-2",
        "pair_index": 47109,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.295751677794314,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-3",
        "pair_index": 47110,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0751663016303427,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-HINGE-RETAINER",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-HINGE-CLIP",
        "occurrence_b": "WP05-HINGE-PIN",
        "pair_index": 47243,
        "part_number_a": "WP05-HINGE-CRESCENT-RING-R2",
        "part_number_b": "WP05-HINGE-PIN-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044967,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-1",
        "pair_index": 47258,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044969,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-2",
        "pair_index": 47259,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.75797492004497,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-3",
        "pair_index": 47260,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044967,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-4",
        "pair_index": 47261,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044964,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-5",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-5",
        "pair_index": 47262,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.75797492004497,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-6",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-6",
        "pair_index": 47263,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "STOWED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542138985,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-1",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 273,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542821345,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-2",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 579,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.42103886542204727,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-WELD-AFT-RAIL-SUPPORT-LONGERON-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-LONGERON-3",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 884,
        "part_number_a": "DF8-R2-AFT-LONGERON-001",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.05271327920170785,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-MANIFOLD-BRACKET-WELD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "AFT-SHELL-001",
        "occurrence_b": "WP04-MANIFOLD-BRACKET",
        "pair_index": 1506,
        "part_number_a": "DF8-R2-AFT-SHELL-001",
        "part_number_b": "DF8-FINAL-WP04-MANIFOLD-BRACKET",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.479534848029091,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-1",
        "occurrence_b": "ARM-STOP-SCREW-1-1",
        "pair_index": 1534,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.40932460756231,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-1",
        "occurrence_b": "ARM-STOP-SCREW-1-2",
        "pair_index": 1535,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.4795348480274,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-2",
        "occurrence_b": "ARM-STOP-SCREW-2-1",
        "pair_index": 1837,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.409324607561455,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-2",
        "occurrence_b": "ARM-STOP-SCREW-2-2",
        "pair_index": 1838,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.47953484803074,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-3",
        "occurrence_b": "ARM-STOP-SCREW-3-1",
        "pair_index": 2139,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.40932460755276,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-ARM-STOP-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ARM-3",
        "occurrence_b": "ARM-STOP-SCREW-3-2",
        "pair_index": 2140,
        "part_number_a": "DF8-R2-ARM-BLADE-001",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.180153346645108,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BACKUP-GUIDE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BACKUP-GUIDE-SCREW-1",
        "occurrence_b": "BACKUP-SPRING-GUIDE",
        "pair_index": 5954,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-BACKUP-SPRING-GUIDE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.9395736106933334,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BACKUP-SEAT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BACKUP-GUIDE-SCREW-2",
        "occurrence_b": "BACKUP-SPRING-FIXED-SEAT",
        "pair_index": 6239,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-BACKUP-SPRING-FIXED-SEAT-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737212,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-1",
        "pair_index": 10431,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372177,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-2",
        "pair_index": 10702,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372177,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-1-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-1-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-1-3",
        "pair_index": 10972,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-1",
        "pair_index": 11241,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372161,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-2",
        "pair_index": 11509,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372161,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-2-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-2-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-2-3",
        "pair_index": 11776,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.639379797372106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-1",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-1",
        "pair_index": 12042,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-2",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-2",
        "pair_index": 12307,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.63937979737216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-BAND-3-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-BAND-3-3",
        "occurrence_b": "BOOSTER-CLAMP-SCREW-3-3",
        "pair_index": 12571,
        "part_number_a": "DF8-R2-BOOSTER-BAND-001",
        "part_number_b": "SSCF-M3-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453364124,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 12913,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453364142,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13174,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453389447,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-1-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-1-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13434,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381605,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13693,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381519,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 13951,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453381484,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-2-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-2-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14208,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.070722453369471,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-1",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14464,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.07072245336946,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-2",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14719,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.0707224533694255,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-BOOSTER-SHELL-LUG-3-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BOOSTER-CLAMP-SCREW-3-3",
        "occurrence_b": "FWD-SHELL-001",
        "pair_index": 14973,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-FWD-SHELL-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643570982,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-01-02",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-01",
        "occurrence_b": "BUOY-GORE-02",
        "pair_index": 17389,
        "part_number_a": "DF8-R2-BUOY-GORE-01",
        "part_number_b": "DF8-R2-BUOY-GORE-02",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643191468,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-08-01",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-01",
        "occurrence_b": "BUOY-GORE-08",
        "pair_index": 17395,
        "part_number_a": "DF8-R2-BUOY-GORE-01",
        "part_number_b": "DF8-R2-BUOY-GORE-08",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.27246429891966,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-02-03",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-02",
        "occurrence_b": "BUOY-GORE-03",
        "pair_index": 17633,
        "part_number_a": "DF8-R2-BUOY-GORE-02",
        "part_number_b": "DF8-R2-BUOY-GORE-03",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643626425,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-03-04",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-03",
        "occurrence_b": "BUOY-GORE-04",
        "pair_index": 17876,
        "part_number_a": "DF8-R2-BUOY-GORE-03",
        "part_number_b": "DF8-R2-BUOY-GORE-04",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643031688,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-04-05",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-04",
        "occurrence_b": "BUOY-GORE-05",
        "pair_index": 18118,
        "part_number_a": "DF8-R2-BUOY-GORE-04",
        "part_number_b": "DF8-R2-BUOY-GORE-05",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643693946,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-05-06",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-05",
        "occurrence_b": "BUOY-GORE-06",
        "pair_index": 18359,
        "part_number_a": "DF8-R2-BUOY-GORE-05",
        "part_number_b": "DF8-R2-BUOY-GORE-06",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.27246431181266,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-06-07",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-06",
        "occurrence_b": "BUOY-GORE-07",
        "pair_index": 18599,
        "part_number_a": "DF8-R2-BUOY-GORE-06",
        "part_number_b": "DF8-R2-BUOY-GORE-07",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "SOFTGOOD",
        "classification_b": "SOFTGOOD",
        "common_volume_mm3": 371.2724643217516,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RF-SEAM-07-08",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "BUOY-GORE-07",
        "occurrence_b": "BUOY-GORE-08",
        "pair_index": 18838,
        "part_number_a": "DF8-R2-BUOY-GORE-07",
        "part_number_b": "DF8-R2-BUOY-GORE-08",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451333,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-1",
        "pair_index": 22637,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451332,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-2",
        "pair_index": 22638,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.135906728451328,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-3",
        "pair_index": 22639,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.13590672845133,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-MANIFOLD-CARRIER-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "COLLECTION-MANIFOLD-001",
        "occurrence_b": "MANIFOLD-CARRIER-SCREW-4",
        "pair_index": 22640,
        "part_number_a": "DF8-R2-COLLECTION-MANIFOLD-001",
        "part_number_b": "SSCF-M3-6-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 23.739884709821567,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-CROSSHEAD-GUIDE-LOCK",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "CROSSHEAD-GUIDE-001",
        "occurrence_b": "CROSSHEAD-GUIDE-LOCK-SCREW-001",
        "pair_index": 23843,
        "part_number_a": "DF8-R2-CROSSHEAD-GUIDE-001",
        "part_number_b": "SSCL-M4-8-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.5285044915129955,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-1",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 24694,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528513630543694,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-2",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 24906,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528504491591356,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-3",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 25117,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.528513630616544,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-DETENT-THREAD-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "DOOR-DETENT-4",
        "occurrence_b": "WP05-SERVICE-THROAT",
        "pair_index": 25327,
        "part_number_a": "GN-615.3-M3-KN-PFB",
        "part_number_b": "WP05-SERVICE-THROAT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.048594445105096265,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-1",
        "occurrence_b": "LOCK-BUSHING-1",
        "pair_index": 26044,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.048594445107637586,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-2",
        "occurrence_b": "LOCK-BUSHING-2",
        "pair_index": 26250,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0485944450997962,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PRESS-LOCK-BUSHING-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-3",
        "occurrence_b": "LOCK-BUSHING-3",
        "pair_index": 26455,
        "part_number_a": "DF8-R2-FIXED-STOP-001",
        "part_number_b": "DF8-R2-AUTO-LOCK-BUSHING-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.4882127413511657,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-1-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-1-1",
        "occurrence_b": "PIVOT-CARRIER-1",
        "pair_index": 27877,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741351913,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-1-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-1-2",
        "occurrence_b": "PIVOT-CARRIER-1",
        "pair_index": 28074,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741349402,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-2-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-2-1",
        "occurrence_b": "PIVOT-CARRIER-2",
        "pair_index": 28270,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741345631,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-2-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-2-2",
        "occurrence_b": "PIVOT-CARRIER-2",
        "pair_index": 28465,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741344852,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-3-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-3-1",
        "occurrence_b": "PIVOT-CARRIER-3",
        "pair_index": 28659,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 3.488212741343035,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FIXED-STOP-CARRIER-3-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FIXED-STOP-SCREW-3-2",
        "occurrence_b": "PIVOT-CARRIER-3",
        "pair_index": 28852,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 5.274151981612108,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-CIRCLIP-FULLFLOW",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FULLFLOW-VALVE-001",
        "occurrence_b": "FULLFLOW-VALVE-CIRCLIP-001",
        "pair_index": 28946,
        "part_number_a": "DF8-R2-FULLFLOW-VALVE-001",
        "part_number_b": "HEC-10-A4",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.31968989868607,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-1",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 29894,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.3196898986861125,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-2",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30079,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.319689898686151,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-3",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30263,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 4.319689898686114,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-FWD-CARRIER-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "FWD-CARRIER-SCREW-4",
        "occurrence_b": "FWD-RING-01",
        "pair_index": 30446,
        "part_number_a": "SSK-M3-6-A4-P80",
        "part_number_b": "DF8-R2-STRUCT-RING-PLAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 0.000397770638736777,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-BOWDEN-SHEATH-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-BOWDEN-SHEATH-AFT",
        "occurrence_b": "ROUTE-BOWDEN-SHEATH-001",
        "pair_index": 32332,
        "part_number_a": "DF8-FINAL-BOWDEN-SHEATH-RING-GLAND",
        "part_number_b": "DF8-FINAL-BOWDEN-SHEATH-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0006317453020051643,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-GAS-MAIN-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-GAS-MAIN-AFT",
        "occurrence_b": "ROUTE-GAS-MAIN-001",
        "pair_index": 32677,
        "part_number_a": "DF8-FINAL-GAS-MAIN-RING-GLAND",
        "part_number_b": "DF8-FINAL-GAS-MAIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.00034994188320845634,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-GLAND-PILOT-LINE-AFT-ROUTE",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GLAND-PILOT-LINE-AFT",
        "occurrence_b": "ROUTE-PILOT-LINE-001",
        "pair_index": 33021,
        "part_number_a": "DF8-FINAL-PILOT-LINE-RING-GLAND",
        "part_number_b": "DF8-FINAL-PILOT-LINE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.1133538920148057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-GS19-FIXED",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GS19-CLIP-FIXED",
        "occurrence_b": "GS19-PIN-FIXED",
        "pair_index": 33586,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.11335389202042646,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-GS19-MOVING",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GS19-CLIP-MOVING",
        "occurrence_b": "GS19-PIN-MOVING",
        "pair_index": 33751,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343179,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-1-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-1-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 34683,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.479534848029097,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-1-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-1-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 34862,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.1598449493431797,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-2-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-2-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 34998,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.47953484802909,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-2-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-2-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 35175,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.1598449493431797,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-3-AFT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-3-SCREW-AFT",
        "occurrence_b": "WP04-AFT-RAIL-SUPPORT",
        "pair_index": 35309,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-AFT-RAIL-SUPPORT-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 6.47953484802909,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-GUIDE-RAIL-3-FWD",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "GUIDE-RAIL-3-SCREW-FWD",
        "occurrence_b": "WP04-REACTION-BULKHEAD",
        "pair_index": 35484,
        "part_number_a": "SSCA-M3-8-A4-BL",
        "part_number_b": "WP04-RB-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 2,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 17.85914122713195,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-XN",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-1",
        "occurrence_b": "HARNESS-LEG-XN",
        "pair_index": 35499,
        "part_number_a": "DF8-R2-HARNESS-BAND-1",
        "part_number_b": "DF8-R2-HARNESS-LEG-XN",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 17.85914122707191,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-XP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-1",
        "occurrence_b": "HARNESS-LEG-XP",
        "pair_index": 35500,
        "part_number_a": "DF8-R2-HARNESS-BAND-1",
        "part_number_b": "DF8-R2-HARNESS-LEG-XP",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 74.70104091589648,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-YN",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-2",
        "occurrence_b": "HARNESS-LEG-YN",
        "pair_index": 35653,
        "part_number_a": "DF8-R2-HARNESS-BAND-2",
        "part_number_b": "DF8-R2-HARNESS-LEG-YN",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "FLEXIBLE",
        "common_volume_mm3": 74.70104091587775,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STITCH-YP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-BAND-2",
        "occurrence_b": "HARNESS-LEG-YP",
        "pair_index": 35654,
        "part_number_a": "DF8-R2-HARNESS-BAND-2",
        "part_number_b": "DF8-R2-HARNESS-LEG-YP",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 25.159801498878597,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TERMINAL-LOOP-XN",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-LEG-XN",
        "occurrence_b": "HARNESS-TERMINAL-001",
        "pair_index": 35806,
        "part_number_a": "DF8-R2-HARNESS-LEG-XN",
        "part_number_b": "WP04-HST-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 25.15980149889281,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TERMINAL-LOOP-XP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HARNESS-LEG-XP",
        "occurrence_b": "HARNESS-TERMINAL-001",
        "pair_index": 35956,
        "part_number_a": "DF8-R2-HARNESS-LEG-XP",
        "part_number_b": "WP04-HST-001-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.11335389202371621,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-HBD-FIXED",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HBD-CLIP-FIXED",
        "occurrence_b": "HBD-PIN-FIXED",
        "pair_index": 36841,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.11335389203098004,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-ACTUATOR-RETAINER-HBD-MOVING",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "HBD-CLIP-MOVING",
        "occurrence_b": "HBD-PIN-MOVING",
        "pair_index": 36985,
        "part_number_a": "DF8-R2-ACTUATOR-E-RING-004",
        "part_number_b": "DF8-R2-ACTUATOR-PIN-004",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343107,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-LATCH-SUPPORT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "LATCH-SUPPORT-BRACKET",
        "occurrence_b": "WP04-LATCH-SCREW-1",
        "pair_index": 37804,
        "part_number_a": "WP04-LATCH-SUPPORT-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.159844949343281,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-LATCH-SUPPORT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "LATCH-SUPPORT-BRACKET",
        "occurrence_b": "WP04-LATCH-SCREW-2",
        "pair_index": 37805,
        "part_number_a": "WP04-LATCH-SUPPORT-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.27930206921818324,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-1",
        "occurrence_b": "PIVOT-PIN-1",
        "pair_index": 43276,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.2793020692218378,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-2",
        "occurrence_b": "PIVOT-PIN-2",
        "pair_index": 43365,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.27930206921849016,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PIVOT-RETAINER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "PIVOT-CLIP-3",
        "occurrence_b": "PIVOT-PIN-3",
        "pair_index": 43453,
        "part_number_a": "DF8-R2-PIVOT-SPIRAL-RING-008",
        "part_number_b": "DF8-R2-PIVOT-PIN-008",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.18993000381426606,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RECOVERY-RETAINER-BODY",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-PIN-BODY",
        "occurrence_b": "RECOVERY-PIN-CLIP-BODY",
        "pair_index": 44578,
        "part_number_a": "DF8-R2-RECOVERY-PIN-006",
        "part_number_b": "DF8-R2-RECOVERY-E-RING-006",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.1899300038069636,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-RECOVERY-RETAINER-HARNESS",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-PIN-CLIP-HARNESS",
        "occurrence_b": "RECOVERY-PIN-HARNESS",
        "pair_index": 44723,
        "part_number_a": "DF8-R2-RECOVERY-E-RING-006",
        "part_number_b": "DF8-R2-RECOVERY-PIN-006",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.002356560783981618,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TETHER-SPLICE-BODY",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-TETHER-001",
        "occurrence_b": "TETHER-THIMBLE-BODY",
        "pair_index": 44887,
        "part_number_a": "AMSTEEL-BLUE-872-7-64-R2",
        "part_number_b": "DF8-R2-TETHER-THIMBLE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FLEXIBLE",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.0022985830219846063,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-TETHER-SPLICE-HARNESS",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "RECOVERY-TETHER-001",
        "occurrence_b": "TETHER-THIMBLE-HARNESS",
        "pair_index": 44888,
        "part_number_a": "AMSTEEL-BLUE-872-7-64-R2",
        "part_number_b": "DF8-R2-TETHER-THIMBLE-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.03241993544917625,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-PILOT-LATCH-PORT",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "ROUTE-PILOT-LINE-001",
        "occurrence_b": "WP04-LATCH-001",
        "pair_index": 45425,
        "part_number_a": "DF8-FINAL-PILOT-LINE-001",
        "part_number_b": "WP04-LATCH-HOUSING-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.01617122426522347,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-1",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-1",
        "pair_index": 45796,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.016171224265370793,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-2",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-2",
        "pair_index": 45850,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 0.016171224264994226,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-STOW-INHIBIT-KEEPER-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "STOW-DOG-INHIBIT-KEEPER-3",
        "occurrence_b": "STOW-DOG-INHIBIT-PIN-3",
        "pair_index": 45903,
        "part_number_a": "DF8-R2-STOW-DOG-INHIBIT-KEEPER-001",
        "part_number_b": "DF8-R2-STOW-DOG-INHIBIT-PIN-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363226142,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-1",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46340,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363211198,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-2",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46382,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 5.831581363240884,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-TRIGGER-MOUNT-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "TRIGGER-MOUNT-SCREW-3",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46423,
        "part_number_a": "SSCF-M3-10-A4",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.6498249873354216,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-BAYONET-WATER-BOBBIN-SERVICE-CAP",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WATER-BOBBIN-SERVICE-CAP-001",
        "occurrence_b": "WATER-TRIGGER-HSG-001",
        "pair_index": 46502,
        "part_number_a": "DF8-WATER-BOBBIN-SERVICE-CAP-001",
        "part_number_b": "DF8-R2-WATER-TRIGGER-HSG-001",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-1",
        "pair_index": 46751,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-2",
        "pair_index": 46752,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 2.4080307689771057,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-FIXED-SLEEVE-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-FIXED-SLEEVE",
        "occurrence_b": "WP04-FIXED-SLEEVE-SCREW-3",
        "pair_index": 46753,
        "part_number_a": "WP04-FIXED-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.295751677794314,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-1",
        "pair_index": 47108,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.2957516777943106,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-2",
        "pair_index": 47109,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "MOVING",
        "classification_b": "MOVING",
        "common_volume_mm3": 6.295751677794314,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP04-MOVING-SLEEVE-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP04-MOVING-SLEEVE",
        "occurrence_b": "WP04-MOVING-SLEEVE-SCREW-3",
        "pair_index": 47110,
        "part_number_a": "WP04-MOVING-GUIDE-SLEEVE-R2",
        "part_number_b": "SSCA-M3-8-A4-BL",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 0.0751663016303427,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-HINGE-RETAINER",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-HINGE-CLIP",
        "occurrence_b": "WP05-HINGE-PIN",
        "pair_index": 47243,
        "part_number_a": "WP05-HINGE-CRESCENT-RING-R2",
        "part_number_b": "WP05-HINGE-PIN-R2",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044967,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-1",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-1",
        "pair_index": 47258,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044969,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-2",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-2",
        "pair_index": 47259,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.75797492004497,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-3",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-3",
        "pair_index": 47260,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044967,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-4",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-4",
        "pair_index": 47261,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.757974920044964,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-5",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-5",
        "pair_index": 47262,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      },
      {
        "classification_a": "FIXED",
        "classification_b": "FIXED",
        "common_volume_mm3": 8.75797492004497,
        "documented_positive_volume_exception": true,
        "intentional_fit_exception_id": "FIT-THREAD-WP05-THROAT-6",
        "intentional_fit_match_status": "VALID_BOUNDED_MATCH",
        "occurrence_a": "WP05-SERVICE-THROAT",
        "occurrence_b": "WP05-THROAT-SCREW-6",
        "pair_index": 47263,
        "part_number_a": "WP05-SERVICE-THROAT-R2",
        "part_number_b": "SSK-M3-6-A4-P80",
        "solid_index_a": 1,
        "solid_index_b": 1,
        "state": "DEPLOYED"
      }
    ],
    "total_positive_pair_record_count": 1425
  },
  "category_b_invalids": {
    "count": 33,
    "definition": "Handoff Category-B invalids are only unauthorized positive-common-volume pairs for which both occurrence classifications are rigid (FIXED or MOVING). Blocked audits, track/fit/parity defects, and invalid solids are validator/audit defects, never Category-B substitutes.",
    "observation_count": 681,
    "records": [
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 3.020516668232898,
          "minimum_angle_deg": 43,
          "observation_count": 37,
          "occurrence_a": "ARM-1",
          "occurrence_b": "FIXED-STOP-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.5037459641768154,
          "minimum_angle_deg": 36,
          "observation_count": 31,
          "occurrence_a": "ARM-1",
          "occurrence_b": "FIXED-STOP-DOWEL-1-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.10584206008804309,
          "minimum_angle_deg": 39,
          "observation_count": 28,
          "occurrence_a": "ARM-1",
          "occurrence_b": "FIXED-STOP-DOWEL-1-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.156492135339753e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-1",
          "occurrence_b": "FIXED-STOP-SCREW-1-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.156492393616306e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-1",
          "occurrence_b": "FIXED-STOP-SCREW-1-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.4650625540329232,
          "minimum_angle_deg": 49,
          "observation_count": 28,
          "occurrence_a": "ARM-1",
          "occurrence_b": "LOCK-DOG-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 3.020516668187031,
          "minimum_angle_deg": 43,
          "observation_count": 37,
          "occurrence_a": "ARM-2",
          "occurrence_b": "FIXED-STOP-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.5037459641270963,
          "minimum_angle_deg": 36,
          "observation_count": 31,
          "occurrence_a": "ARM-2",
          "occurrence_b": "FIXED-STOP-DOWEL-2-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.10584206001868501,
          "minimum_angle_deg": 39,
          "observation_count": 28,
          "occurrence_a": "ARM-2",
          "occurrence_b": "FIXED-STOP-DOWEL-2-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.156492111712215e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-2",
          "occurrence_b": "FIXED-STOP-SCREW-2-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.156492314152456e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-2",
          "occurrence_b": "FIXED-STOP-SCREW-2-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.46506255401866475,
          "minimum_angle_deg": 49,
          "observation_count": 28,
          "occurrence_a": "ARM-2",
          "occurrence_b": "LOCK-DOG-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 3.020516668114248,
          "minimum_angle_deg": 43,
          "observation_count": 37,
          "occurrence_a": "ARM-3",
          "occurrence_b": "FIXED-STOP-3",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            36,
            37,
            38,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.5037459641785413,
          "minimum_angle_deg": 36,
          "observation_count": 31,
          "occurrence_a": "ARM-3",
          "occurrence_b": "FIXED-STOP-DOWEL-3-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 66,
          "maximum_common_volume_mm3": 0.10584206004294275,
          "minimum_angle_deg": 39,
          "observation_count": 28,
          "occurrence_a": "ARM-3",
          "occurrence_b": "FIXED-STOP-DOWEL-3-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "HDP-3-8-A1",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.15649209347251e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-3",
          "occurrence_b": "FIXED-STOP-SCREW-3-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 8.156492384305618e-05,
          "minimum_angle_deg": 77,
          "observation_count": 2,
          "occurrence_a": "ARM-3",
          "occurrence_b": "FIXED-STOP-SCREW-3-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "SSCA-M3-8-A4-BL",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.46506255402496516,
          "minimum_angle_deg": 49,
          "observation_count": 28,
          "occurrence_a": "ARM-3",
          "occurrence_b": "LOCK-DOG-3",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            70
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 70,
          "maximum_common_volume_mm3": 0.0019422004481271437,
          "minimum_angle_deg": 70,
          "observation_count": 1,
          "occurrence_a": "ARM-STOP-PAD-1",
          "occurrence_b": "FIXED-STOP-1",
          "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            70
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 70,
          "maximum_common_volume_mm3": 0.0019422004481164591,
          "minimum_angle_deg": 70,
          "observation_count": 1,
          "occurrence_a": "ARM-STOP-PAD-2",
          "occurrence_b": "FIXED-STOP-2",
          "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            70
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 70,
          "maximum_common_volume_mm3": 0.0019422004486452072,
          "minimum_angle_deg": 70,
          "observation_count": 1,
          "occurrence_a": "ARM-STOP-PAD-3",
          "occurrence_b": "FIXED-STOP-3",
          "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 3.328939810508383,
          "minimum_angle_deg": 43,
          "observation_count": 36,
          "occurrence_a": "ARM-STOP-SCREW-1-1",
          "occurrence_b": "FIXED-STOP-1",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 1.0784679555612218,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-1-1",
          "occurrence_b": "LOCK-DOG-1",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 0.46073286260872104,
          "minimum_angle_deg": 65,
          "observation_count": 15,
          "occurrence_a": "ARM-STOP-SCREW-1-2",
          "occurrence_b": "FIXED-STOP-1",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 3.328939810567685,
          "minimum_angle_deg": 43,
          "observation_count": 36,
          "occurrence_a": "ARM-STOP-SCREW-2-1",
          "occurrence_b": "FIXED-STOP-2",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 1.0784679555595305,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-2-1",
          "occurrence_b": "LOCK-DOG-2",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 0.4607328626168661,
          "minimum_angle_deg": 65,
          "observation_count": 15,
          "occurrence_a": "ARM-STOP-SCREW-2-2",
          "occurrence_b": "FIXED-STOP-2",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            43,
            44,
            45,
            46,
            47,
            48,
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 78,
          "maximum_common_volume_mm3": 3.3289398105299175,
          "minimum_angle_deg": 43,
          "observation_count": 36,
          "occurrence_a": "ARM-STOP-SCREW-3-1",
          "occurrence_b": "FIXED-STOP-3",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "MOVING",
          "classification_relationship": "MOVING_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 1.0784679555607513,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-3-1",
          "occurrence_b": "LOCK-DOG-3",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77,
            78,
            79
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 79,
          "maximum_common_volume_mm3": 0.4607328626142269,
          "minimum_angle_deg": 65,
          "observation_count": 15,
          "occurrence_a": "ARM-STOP-SCREW-3-2",
          "occurrence_b": "FIXED-STOP-3",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-FIXED-STOP-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 22,
          "maximum_common_volume_mm3": 0.09878833547014403,
          "minimum_angle_deg": 3,
          "observation_count": 20,
          "occurrence_a": "LINK-PIN-1-BELL",
          "occurrence_b": "PIVOT-CARRIER-1",
          "part_number_a": "DF8-R2-LINK-PIN-004",
          "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 22,
          "maximum_common_volume_mm3": 0.09878833547287766,
          "minimum_angle_deg": 3,
          "observation_count": 20,
          "occurrence_a": "LINK-PIN-2-BELL",
          "occurrence_b": "PIVOT-CARRIER-2",
          "part_number_a": "DF8-R2-LINK-PIN-004",
          "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized rigid positive-common-volume pair",
        "row": {
          "angles_deg": [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22
          ],
          "classification_a": "MOVING",
          "classification_b": "FIXED",
          "classification_relationship": "FIXED_MOVING",
          "maximum_angle_deg": 22,
          "maximum_common_volume_mm3": 0.09878833547379377,
          "minimum_angle_deg": 3,
          "observation_count": 20,
          "occurrence_a": "LINK-PIN-3-BELL",
          "occurrence_b": "PIVOT-CARRIER-3",
          "part_number_a": "DF8-R2-LINK-PIN-004",
          "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      }
    ]
  },
  "remaining_positive_pairs": [
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 3.020516668232898,
      "minimum_angle_deg": 43,
      "observation_count": 37,
      "occurrence_a": "ARM-1",
      "occurrence_b": "FIXED-STOP-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.5037459641768154,
      "minimum_angle_deg": 36,
      "observation_count": 31,
      "occurrence_a": "ARM-1",
      "occurrence_b": "FIXED-STOP-DOWEL-1-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.10584206008804309,
      "minimum_angle_deg": 39,
      "observation_count": 28,
      "occurrence_a": "ARM-1",
      "occurrence_b": "FIXED-STOP-DOWEL-1-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.156492135339753e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-1",
      "occurrence_b": "FIXED-STOP-SCREW-1-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.156492393616306e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-1",
      "occurrence_b": "FIXED-STOP-SCREW-1-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.4650625540329232,
      "minimum_angle_deg": 49,
      "observation_count": 28,
      "occurrence_a": "ARM-1",
      "occurrence_b": "LOCK-DOG-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 77,
      "maximum_common_volume_mm3": 0.10717365909245459,
      "minimum_angle_deg": 49,
      "observation_count": 29,
      "occurrence_a": "ARM-1",
      "occurrence_b": "LOCK-SPRING-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 3.020516668187031,
      "minimum_angle_deg": 43,
      "observation_count": 37,
      "occurrence_a": "ARM-2",
      "occurrence_b": "FIXED-STOP-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.5037459641270963,
      "minimum_angle_deg": 36,
      "observation_count": 31,
      "occurrence_a": "ARM-2",
      "occurrence_b": "FIXED-STOP-DOWEL-2-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.10584206001868501,
      "minimum_angle_deg": 39,
      "observation_count": 28,
      "occurrence_a": "ARM-2",
      "occurrence_b": "FIXED-STOP-DOWEL-2-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.156492111712215e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-2",
      "occurrence_b": "FIXED-STOP-SCREW-2-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.156492314152456e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-2",
      "occurrence_b": "FIXED-STOP-SCREW-2-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.46506255401866475,
      "minimum_angle_deg": 49,
      "observation_count": 28,
      "occurrence_a": "ARM-2",
      "occurrence_b": "LOCK-DOG-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 77,
      "maximum_common_volume_mm3": 0.10717347549244424,
      "minimum_angle_deg": 49,
      "observation_count": 29,
      "occurrence_a": "ARM-2",
      "occurrence_b": "LOCK-SPRING-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 3.020516668114248,
      "minimum_angle_deg": 43,
      "observation_count": 37,
      "occurrence_a": "ARM-3",
      "occurrence_b": "FIXED-STOP-3",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.5037459641785413,
      "minimum_angle_deg": 36,
      "observation_count": 31,
      "occurrence_a": "ARM-3",
      "occurrence_b": "FIXED-STOP-DOWEL-3-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 66,
      "maximum_common_volume_mm3": 0.10584206004294275,
      "minimum_angle_deg": 39,
      "observation_count": 28,
      "occurrence_a": "ARM-3",
      "occurrence_b": "FIXED-STOP-DOWEL-3-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "HDP-3-8-A1",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.15649209347251e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-3",
      "occurrence_b": "FIXED-STOP-SCREW-3-1",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 8.156492384305618e-05,
      "minimum_angle_deg": 77,
      "observation_count": 2,
      "occurrence_a": "ARM-3",
      "occurrence_b": "FIXED-STOP-SCREW-3-2",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "SSCA-M3-8-A4-BL",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.46506255402496516,
      "minimum_angle_deg": 49,
      "observation_count": 28,
      "occurrence_a": "ARM-3",
      "occurrence_b": "LOCK-DOG-3",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 77,
      "maximum_common_volume_mm3": 0.10717365909253887,
      "minimum_angle_deg": 49,
      "observation_count": 29,
      "occurrence_a": "ARM-3",
      "occurrence_b": "LOCK-SPRING-3",
      "part_number_a": "DF8-R2-ARM-BLADE-001",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        70
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 70,
      "maximum_common_volume_mm3": 0.0019422004481271437,
      "minimum_angle_deg": 70,
      "observation_count": 1,
      "occurrence_a": "ARM-STOP-PAD-1",
      "occurrence_b": "FIXED-STOP-1",
      "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        70
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 70,
      "maximum_common_volume_mm3": 0.0019422004481164591,
      "minimum_angle_deg": 70,
      "observation_count": 1,
      "occurrence_a": "ARM-STOP-PAD-2",
      "occurrence_b": "FIXED-STOP-2",
      "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        70
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 70,
      "maximum_common_volume_mm3": 0.0019422004486452072,
      "minimum_angle_deg": 70,
      "observation_count": 1,
      "occurrence_a": "ARM-STOP-PAD-3",
      "occurrence_b": "FIXED-STOP-3",
      "part_number_a": "DF8-R2-ARM-STOP-PAD-001",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 3.328939810508383,
      "minimum_angle_deg": 43,
      "observation_count": 36,
      "occurrence_a": "ARM-STOP-SCREW-1-1",
      "occurrence_b": "FIXED-STOP-1",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 1.0784679555612218,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-1-1",
      "occurrence_b": "LOCK-DOG-1",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.18217169448226095,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-1-1",
      "occurrence_b": "LOCK-SPRING-1",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 0.46073286260872104,
      "minimum_angle_deg": 65,
      "observation_count": 15,
      "occurrence_a": "ARM-STOP-SCREW-1-2",
      "occurrence_b": "FIXED-STOP-1",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 3.328939810567685,
      "minimum_angle_deg": 43,
      "observation_count": 36,
      "occurrence_a": "ARM-STOP-SCREW-2-1",
      "occurrence_b": "FIXED-STOP-2",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 1.0784679555595305,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-2-1",
      "occurrence_b": "LOCK-DOG-2",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.1821718808039585,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-2-1",
      "occurrence_b": "LOCK-SPRING-2",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 0.4607328626168661,
      "minimum_angle_deg": 65,
      "observation_count": 15,
      "occurrence_a": "ARM-STOP-SCREW-2-2",
      "occurrence_b": "FIXED-STOP-2",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 78,
      "maximum_common_volume_mm3": 3.3289398105299175,
      "minimum_angle_deg": 43,
      "observation_count": 36,
      "occurrence_a": "ARM-STOP-SCREW-3-1",
      "occurrence_b": "FIXED-STOP-3",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "MOVING",
      "classification_relationship": "MOVING_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 1.0784679555607513,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-3-1",
      "occurrence_b": "LOCK-DOG-3",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-DOG-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76
      ],
      "classification_a": "MOVING",
      "classification_b": "FLEXIBLE",
      "classification_relationship": "FLEXIBLE_MOVING",
      "maximum_angle_deg": 76,
      "maximum_common_volume_mm3": 0.18217188080427874,
      "minimum_angle_deg": 50,
      "observation_count": 27,
      "occurrence_a": "ARM-STOP-SCREW-3-1",
      "occurrence_b": "LOCK-SPRING-3",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 79,
      "maximum_common_volume_mm3": 0.4607328626142269,
      "minimum_angle_deg": 65,
      "observation_count": 15,
      "occurrence_a": "ARM-STOP-SCREW-3-2",
      "occurrence_b": "FIXED-STOP-3",
      "part_number_a": "SSCA-M3-8-A4-BL",
      "part_number_b": "DF8-R2-FIXED-STOP-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 22,
      "maximum_common_volume_mm3": 0.09878833547014403,
      "minimum_angle_deg": 3,
      "observation_count": 20,
      "occurrence_a": "LINK-PIN-1-BELL",
      "occurrence_b": "PIVOT-CARRIER-1",
      "part_number_a": "DF8-R2-LINK-PIN-004",
      "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 22,
      "maximum_common_volume_mm3": 0.09878833547287766,
      "minimum_angle_deg": 3,
      "observation_count": 20,
      "occurrence_a": "LINK-PIN-2-BELL",
      "occurrence_b": "PIVOT-CARRIER-2",
      "part_number_a": "DF8-R2-LINK-PIN-004",
      "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    },
    {
      "angles_deg": [
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ],
      "classification_a": "MOVING",
      "classification_b": "FIXED",
      "classification_relationship": "FIXED_MOVING",
      "maximum_angle_deg": 22,
      "maximum_common_volume_mm3": 0.09878833547379377,
      "minimum_angle_deg": 3,
      "observation_count": 20,
      "occurrence_a": "LINK-PIN-3-BELL",
      "occurrence_b": "PIVOT-CARRIER-3",
      "part_number_a": "DF8-R2-LINK-PIN-004",
      "part_number_b": "DF8-R2-PIVOT-CARRIER-001",
      "result": "UNAUTHORIZED_POSITIVE_VOLUME",
      "scope": "MOTION",
      "solid_index_a": 1,
      "solid_index_b": 1,
      "variant_a": "STOWED",
      "variant_b": "STOWED"
    }
  ],
  "unresolved_nonrigid_positive_pairs": {
    "count": 6,
    "definition": "Unauthorized positive-common-volume motion pairs involving at least one nonrigid occurrence; retained separately and not counted as Category-B rigid invalids",
    "observation_count": 168,
    "records": [
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 77,
          "maximum_common_volume_mm3": 0.10717365909245459,
          "minimum_angle_deg": 49,
          "observation_count": 29,
          "occurrence_a": "ARM-1",
          "occurrence_b": "LOCK-SPRING-1",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 77,
          "maximum_common_volume_mm3": 0.10717347549244424,
          "minimum_angle_deg": 49,
          "observation_count": 29,
          "occurrence_a": "ARM-2",
          "occurrence_b": "LOCK-SPRING-2",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            49,
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76,
            77
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 77,
          "maximum_common_volume_mm3": 0.10717365909253887,
          "minimum_angle_deg": 49,
          "observation_count": 29,
          "occurrence_a": "ARM-3",
          "occurrence_b": "LOCK-SPRING-3",
          "part_number_a": "DF8-R2-ARM-BLADE-001",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.18217169448226095,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-1-1",
          "occurrence_b": "LOCK-SPRING-1",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.1821718808039585,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-2-1",
          "occurrence_b": "LOCK-SPRING-2",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      },
      {
        "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
        "row": {
          "angles_deg": [
            50,
            51,
            52,
            53,
            54,
            55,
            56,
            57,
            58,
            59,
            60,
            61,
            62,
            63,
            64,
            65,
            66,
            67,
            68,
            69,
            70,
            71,
            72,
            73,
            74,
            75,
            76
          ],
          "classification_a": "MOVING",
          "classification_b": "FLEXIBLE",
          "classification_relationship": "FLEXIBLE_MOVING",
          "maximum_angle_deg": 76,
          "maximum_common_volume_mm3": 0.18217188080427874,
          "minimum_angle_deg": 50,
          "observation_count": 27,
          "occurrence_a": "ARM-STOP-SCREW-3-1",
          "occurrence_b": "LOCK-SPRING-3",
          "part_number_a": "SSCA-M3-8-A4-BL",
          "part_number_b": "DF8-R2-AUTO-LOCK-SPRING-001",
          "result": "UNAUTHORIZED_POSITIVE_VOLUME",
          "scope": "MOTION",
          "solid_index_a": 1,
          "solid_index_b": 1,
          "variant_a": "STOWED",
          "variant_b": "STOWED"
        },
        "scope": "MOTION"
      }
    ]
  },
  "validator_defects": {
    "count": 66,
    "records": [
      {
        "acceptance_gate_status": "NOT_COMPUTED",
        "condition": "terminal post-merge motion-kinematics schema failure",
        "exception_message": "'angle_deg'",
        "exception_type": "KeyError",
        "execution_state": "TERMINAL_AUDIT_FAILURE",
        "exit_code": 1,
        "failure_stage": "POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK",
        "missing_validation_files": [
          "gate_results.json",
          "motion_audit_summary.json",
          "motion_kinematics_1deg.csv",
          "validation_manifest.json",
          "validation_summary.json"
        ],
        "release_authorized": false,
        "scope": "VALIDATOR"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "AFT-SHELL-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-PAD-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-PAD-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-PAD-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-1-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-1-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-2-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-2-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-3-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "ARM-STOP-SCREW-3-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "CROSSHEAD-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-SECTOR-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-1-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-1-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-2-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-2-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-3-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FIXED-STOP-SCREW-3-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "FWD-RING-02",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-1-SCREW-AFT",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-1-SCREW-FWD",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-2-SCREW-AFT",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-2-SCREW-FWD",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-3-SCREW-AFT",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "GUIDE-RAIL-3-SCREW-FWD",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "HARNESS-TERMINAL-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-1-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-1-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-2-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-2-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-3-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "LINK-3-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "PIVOT-CARRIER-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "PIVOT-CARRIER-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "PIVOT-CARRIER-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-GUIDE-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-GUIDE-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-GUIDE-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "STOW-DOG-INHIBIT-KEEPER-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-FIXED-SLEEVE-SCREW-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-FOLLOWER-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-LATCH-SCREW-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-LATCH-SCREW-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-MOVING-SLEEVE",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-1",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-2",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-MOVING-SLEEVE-SCREW-3",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-SEAR-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP04-SEAR-CLIP-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "MOVING",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP05-DOOR-001",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "unresolved parity row",
        "row": {
          "classification": "FIXED",
          "exact_local_brep_match": "False",
          "fingerprint_error": "",
          "flexible_state_geometry_exception": "False",
          "occurrence_id": "WP05-SERVICE-THROAT",
          "present_deployed": "True",
          "present_stowed": "True",
          "same_part_number": "True",
          "status": "FAIL"
        },
        "scope": "STATE_PARITY"
      },
      {
        "condition": "occurrence-transform gate unresolved",
        "detail": {
          "identity_occurrences_without_justification": null,
          "maximum_transform_matrix_element_error": null,
          "status": "NOT_COMPUTED",
          "transform_mismatches": null,
          "unmapped_leaf_occurrences": null
        },
        "scope": "OCCURRENCE_TRANSFORMS"
      }
    ]
  }
}
```

## Exact engineering commands (reference only; not authorized at handoff)

Both endpoint rebuild and AP242 export (the authoring entry point always builds
STOWED then DEPLOYED in one process):

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/build_r2.py
```

STOWED exact-solid authoring audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py STOWED work/final_analysis/per_solid_authoring_audit_stowed.json
```

DEPLOYED exact-solid authoring audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py DEPLOYED work/final_analysis/per_solid_authoring_audit_deployed.json
```

Clean-process AP242 reimport, endpoint audits, and full 0°–80°/1° motion audit:

```bash
PYTHONPATH=work/r2_source work/cadenv/bin/python work/r2_source/validate_r2.py --out work/final_analysis/validation --motion-workers 8
```

Workbook generation:

```bash
mkdir -p work/spreadsheet_runtime
test -n "${CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}"
test -e work/spreadsheet_runtime/node_modules ||   ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
install -m 0644 work/r2_source/build_workbook.mjs   work/spreadsheet_runtime/build_workbook.mjs
(cd work/spreadsheet_runtime && node build_workbook.mjs)
```

Final three-member ZIP packaging:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/final_tools/package_final.py
```

## Fragile operations

- `build_r2.py` overwrites final STEP/inventory/manifest files and rewrites STEP
  NAUO text non-atomically; it must run STOWED then DEPLOYED in one process so
  the shared state-invariant BREP cache remains valid.
- Validation evidence must use a fresh directory; stale top-level files enter
  the validation manifest.
- Full motion starts 81 spawn tasks and each worker clean-reimports both masters;
  reduce `--motion-workers` inside the supported 1..8 range if memory is tight.
- `validate_r2.py` returns process exit zero even when gates FAIL or BLOCKED; gate
  results, not exit code, determine engineering disposition.
- In this terminal checkpoint, `validate_r2.py` exited 1 after merging all 81
  motion samples because its post-merge kinematics schema check requested the
  absent `angle_deg` key. Missing summaries/gates/manifests must not be inferred.
- Per-solid and occurrence authoring audits also require explicit JSON result
  inspection; their process exit alone is insufficient.
- The workbook source must be recopied into `work/spreadsheet_runtime` after any
  edit so bare managed-runtime module resolution uses the current file.
- `package_final.py` is fail-closed and refuses to overwrite an existing final ZIP.
- Dependency manifests pin installed versions but the excluded virtual
  environment and Node tree are not an offline wheel/tarball cache.
- `SHA256SUMS.txt` excludes only itself and authenticates `FILE_MANIFEST.csv`
  plus every other payload file. `FILE_MANIFEST.csv` omits its own row to avoid
  recursive content and lists `SHA256SUMS.txt` with a blank digest because that
  checksum file uses the standard self-exclusion.

## Assumptions used by this handoff

- `LAST_EXECUTION_RECORD.json` is the sole claim for observed last commands and
  process exit codes. The authoring manifest binds the final masters/inventories;
  in terminal mode, `LAST_AUDIT_FAILURE.json` independently binds the merged
  motion file while the handoff checksums bind every preserved evidence file.
- Category-B invalids mean only unauthorized positive-volume pairs between two
  rigid (FIXED/MOVING) occurrences. Blocked evaluations, track errors, fit errors,
  parity defects, and invalid solids are validator/audit defects instead.
- NCR statuses are calculated from the same gate sets and Boolean formula used
  by `build_workbook.mjs`; they are not copied from a stale workbook cell.
- File modification history is derived from captured filesystem mtimes and
  manifest hashes, not from a version-control commit claim.

## Owner decisions not to reopen without new controlling authority

- Do not reopen Creo as an acceptance blocker; owner Creo import occurs after delivery.
- Do not restart source inventory or expand beyond the full WP02 live input tree
  unless the authoritative code proves another input is required.
- Do not discard preserved source geometry, checkpoints, evidence, or candidate outputs.
- Do not begin another corrective cycle or final release packaging from this handoff.
- Do not replace OCP/XCAF as the controlling neutral-CAD validation gate.
- Do not treat stale `work/r2_metadata/` WIP/Creo text as controlling governance.
- Keep each arm at the owner-frozen pivot-to-tip length of exactly **733.806 mm**.
- Keep the guided central compression spring envelope: maximum OD **15.8 mm**,
  approximate free length **195 mm**, approximate stowed installed length **145 mm**,
  deployed installed length approximately **160.05 mm**, approximate rate **16 N/mm**,
  approximate stowed force **800 N**, minimum target deployed force approximately
  **559 N**, available work target approximately **10.2 J**, maximum solid height
  **138 mm**, and spring-plus-seat mass target **≤0.13 kg**.
- Retain direct **ACE HBD-15-25-AA-P** installation with mechanical seizure accepted
  as an owner-approved single-point deployment failure; do not add a bypass carriage,
  lost-motion anti-seizure mechanism, overload release, fuse pin, or redundant damper.

Read `CURRENT_STATE.json`, verify `SHA256SUMS.txt`, and then read
`RESUME_COMMANDS.md`. Commands that mutate CAD/evidence or create release
artifacts remain reference-only unless a new controlling instruction explicitly
authorizes them.
