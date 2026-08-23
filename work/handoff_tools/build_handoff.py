#!/usr/bin/env python3
"""Build a deterministic, fail-closed DF8 Codex handoff checkpoint.

This utility is intentionally separate from the CAD authoring, validation, and
release-packaging code.  It copies a quiescent completed-validator snapshot to
a temporary staging tree, writes resumption/governance records, authenticates
the payload, and atomically publishes one ZIP archive.  It never edits the
authoritative source or CAD/evidence trees.
"""

from __future__ import annotations

import ast
import csv
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import os
import platform
import shutil
import stat
import struct
import subprocess
import tempfile
import time
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_STEM = "STINGRAY_I5S_DF8_R2_CODEX_HANDOFF_CHECKPOINT"
ARCHIVE_NAME = f"{ARCHIVE_STEM}.zip"
OUTPUT_PATH = ROOT / ARCHIVE_NAME
LOCK_PATH = ROOT / f".{ARCHIVE_STEM}.lock"

FINAL_RELEASE = Path("work/final_release")
FINAL_ANALYSIS = Path("work/final_analysis")
VALIDATION = FINAL_ANALYSIS / "validation"
CAD_PYTHON = ROOT / "work/cadenv/bin/python3"

FINAL_STOWED = "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step"
FINAL_DEPLOYED = "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step"
FINAL_WORKBOOK = "STINGRAY_I5S_DF8_MASTER_BUILD_PARTS_AND_PROCUREMENT_REGISTER.xlsx"

CREO_DISPOSITION = (
    "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; "
    "OWNER CREO IMPORT OCCURS AFTER DELIVERY."
)

COMMISSION_SOURCES = (
    (
        Path("upload/Pasted markdown(20260821-031917).md"),
        Path("commission/ORIGINAL_COMMISSION_20260821-031917.md"),
        "Original controlling commission",
    ),
    (
        Path("upload/Pasted markdown(20260821-171406).md"),
        Path("commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md"),
        "R1 rejection and R2 corrective direction",
    ),
    (
        Path("work/handoff_tools/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md"),
        Path("commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md"),
        "Latest safe-termination/runtime directive; runtime-only and non-engineering",
    ),
)

# Every final evidence file consumed by the current workbook generator, plus
# the validation manifest that authenticates them.  A failed-but-complete
# validator run is a legitimate handoff state; this utility does not promote
# gate statuses, but it does reject partial/stale validator output.
REQUIRED_VALIDATION_FILES = (
    "gate_results.json",
    "validation_summary.json",
    "step_text_inspection.json",
    "xcaf_occurrences_stowed.csv",
    "xcaf_occurrences_deployed.csv",
    "leaf_solids_stowed.csv",
    "leaf_solids_deployed.csv",
    "endpoint_pair_audit_stowed.csv.gz",
    "endpoint_pair_audit_deployed.csv.gz",
    "endpoint_interference_register.csv",
    "endpoint_pair_summary.json",
    "minimum_clearance_register.csv",
    "key_dimensions.json",
    "motion_kinematics_1deg.csv",
    "motion_full_mechanism_audit.csv.gz",
    "motion_audit_summary.json",
    "attachment_connectivity_stowed.csv",
    "attachment_connectivity_deployed.csv",
    "attachment_geometry_stowed.csv",
    "attachment_geometry_deployed.csv",
    "route_termination_audit_stowed.csv",
    "route_termination_audit_deployed.csv",
    "connectivity_summary.json",
    "definition_of_done_audit.json",
    "state_parity.csv",
    "occurrence_bom_reconciliation.csv",
    "occurrence_bom_reconciliation.json",
    "validation_manifest.json",
)

TERMINAL_AUDIT_MISSING_VALIDATION_FILES = tuple(sorted((
    "gate_results.json",
    "motion_audit_summary.json",
    "motion_kinematics_1deg.csv",
    "validation_manifest.json",
    "validation_summary.json",
)))
TERMINAL_AUDIT_PRESENT_VALIDATION_FILES = tuple(sorted(
    set(REQUIRED_VALIDATION_FILES) - set(TERMINAL_AUDIT_MISSING_VALIDATION_FILES)
))
LAST_AUDIT_FAILURE_PATH = Path("work/handoff_tools/LAST_AUDIT_FAILURE.json")
LAST_AUDIT_FAILURE_SCHEMA = "DF8_CODEX_LAST_AUDIT_FAILURE_V1"
TERMINAL_AUDIT_STAGE = "POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK"
MERGED_MOTION_AUDIT_PATH = Path(
    "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz"
)
TERMINAL_MERGED_MOTION_SIZE_BYTES = 22_925_903
TERMINAL_MERGED_MOTION_SHA256 = (
    "4da00e87fd63199a29c0f4e97e9f9502da604ed48cf3f8875a9300778828fee6"
)
TERMINAL_MOTION_DATA_ROW_COUNT = 1_447_875
TERMINAL_MOTION_LINE_COUNT = 1_447_876
TERMINAL_MOTION_ROWS_PER_SAMPLE = 17_875
TERMINAL_MOTION_RESULT_COUNTS = {
    "CLEAR_OR_CONTACT": 1_445_811,
    "DOCUMENTED_POSITIVE_VOLUME": 1_215,
    "UNAUTHORIZED_POSITIVE_VOLUME": 849,
}
TERMINAL_MOTION_COMMON_STATUS_COUNTS = {
    "DONE": 34_314,
    "NOT_RUN_AABB_SEPARATED": 1_413_561,
}
TERMINAL_MOTION_DISTANCE_STATUS_COUNT_VALUES = (2_064, 47_655, 1_398_156)
TERMINAL_MOTION_UNAUTHORIZED_UNIQUE_PAIR_COUNT = 39
TERMINAL_MOTION_CATEGORY_B_OBSERVATION_COUNT = 681
TERMINAL_MOTION_CATEGORY_B_UNIQUE_PAIR_COUNT = 33
TERMINAL_MOTION_NONRIGID_OBSERVATION_COUNT = 168
TERMINAL_MOTION_NONRIGID_UNIQUE_PAIR_COUNT = 6

COMPLETE_PHASE = "completed-validator evidence preservation and atomic safe-handoff packaging"
COMPLETE_CHECKPOINT = (
    "manifest-bound final authoring masters and completed frozen-gate validation "
    "under work/final_analysis/validation"
)
TERMINAL_PHASE = "terminal validator failure preservation and atomic safe-handoff packaging"
TERMINAL_CHECKPOINT = (
    "manifest-bound final authoring masters plus 81 completed exact-motion samples merged "
    "in work/final_analysis/validation/motion_full_mechanism_audit.csv.gz; post-merge "
    "gate/NCR outputs were not computed"
)

REQUIRED_SOURCE_FILES = (
    "work/r2_source/authoring_pair_audit.py",
    "work/r2_source/build_r2.py",
    "work/r2_source/build_workbook.mjs",
    "work/r2_source/compare_source_reimport.py",
    "work/r2_source/export_components.py",
    "work/r2_source/package_r2.py",
    "work/r2_source/per_solid_authoring_audit.py",
    "work/r2_source/r2_final_scope.py",
    "work/r2_source/r2_geometry.py",
    "work/r2_source/r2_hardware.py",
    "work/r2_source/r2_hierarchy.py",
    "work/r2_source/render_evidence.py",
    "work/r2_source/validate_r2.py",
    "work/r2_source/vendor_shapes.py",
    "work/final_tools/audit_final_scope.py",
    "work/final_tools/test_final_hierarchy.py",
    "work/final_tools/package_final.py",
    "work/scripts/build_final_cad.py",
    "work/scripts/test_crosshead_clearance.py",
    "work/scripts/validate_step.py",
    "work/r2_metadata/DEPENDENCIES.json",
    "work/spreadsheet_runtime/build_register.mjs",
    "work/handoff_tools/build_handoff.py",
    "work/handoff_tools/validate_handoff.py",
    "work/handoff_tools/LAST_EXECUTION_RECORD.json",
    "work/handoff_tools/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md",
)

LIVE_WP02_VENDOR_FILES = (
    Path(
        "work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/"
        "03_VENDOR_CAD_ORIGINAL/ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp"
    ),
    Path(
        "work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/"
        "04_VENDOR_CAD_CREO_DROP_IN/"
        "ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step"
    ),
)

REQUIRED_COPY_TREES = (
    "work/analysis",
    "work/r2_source",
    "work/input/wp02",
    "work/final_analysis",
    "work/final_release",
    "work/r2_components",
    "work/r2_analysis",
    "work/r2_release",
    "work/r2_package",
    "work/final_tools",
    "work/scripts",
    "work/r2_metadata",
    "work/spreadsheet_runtime",
    "work/handoff_tools",
    "outputs/6f4e7892e9f1",
)

EXCLUDED_DIR_NAMES = frozenset(
    {
        "node_modules",
        "cadenv",
        "__pycache__",
        ".cache",
        "cache",
        "caches",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
EXCLUDED_FILE_SUFFIXES = frozenset({".pyc", ".pyo"})

ACTIVE_ENTRYPOINT_DIRS = (
    Path("work/r2_source"),
    Path("work/final_tools"),
    Path("work/scripts"),
    Path("work/handoff_tools"),
)
ACTIVE_ENTRYPOINT_SUFFIXES = frozenset({".py", ".mjs", ".js", ".sh"})
RIGID_CLASSIFICATIONS = frozenset({"FIXED", "MOVING"})
VALID_GATE_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED"})
STATE_PARITY_FIELDS = (
    "occurrence_id", "classification", "present_stowed", "present_deployed",
    "same_part_number", "stowed_solid_count", "deployed_solid_count",
    "stowed_face_count", "deployed_face_count", "volume_delta_mm3",
    "stowed_local_brep_sha256", "deployed_local_brep_sha256",
    "local_bbox_max_abs_delta_mm", "surface_type_counts_match",
    "exact_local_brep_match", "fingerprint_error",
    "flexible_state_geometry_exception", "status",
)
CREO_INFORMATIONAL_ITEM = {
    "item_id": "CREO-ENVIRONMENT",
    "status": "N/A",
    "disposition": CREO_DISPOSITION,
    "included_in_acceptance_logic": False,
}

NCR_GATE_MAP = {
    "NCR-01": (
        "AP242-STOWED", "AP242-DEPLOYED", "STATE-PARITY",
        "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH",
    ),
    "NCR-02": ("STATE-PARITY", "ATTACHMENT-COHESION", "RECOVERY-LOAD-PATH"),
    "NCR-03": (
        "PROCUREMENT-DEFINITION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "DOD-CLOSED-PRESSURE-SUBSYSTEMS", "DOD-CLOSED-ROUTE-ENDS",
        "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED",
        "MOTION-FULL-MECHANISM",
    ),
    "NCR-04": (
        "INTERFERENCE-STOWED", "INTERFERENCE-DEPLOYED",
        "CLEARANCE-EVIDENCE-STOWED", "CLEARANCE-EVIDENCE-DEPLOYED",
        "MOTION-FULL-MECHANISM",
    ),
    "NCR-05": (
        "ATTACHMENT-COHESION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "DOD-POSITIVE-DEPLOYED-LOCKS", "DOD-POSITIVE-STOWED-RETENTION",
        "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM",
    ),
    "NCR-06": (
        "ATTACHMENT-COHESION", "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
        "DOD-CLOSED-PRESSURE-SUBSYSTEMS", "DOD-CLOSED-ROUTE-ENDS",
        "PROCUREMENT-DEFINITION", "MOTION-FULL-MECHANISM",
    ),
    "NCR-07": (
        "AP242-STOWED", "BREP-VALID-STOWED", "AP242-DEPLOYED",
        "BREP-VALID-DEPLOYED", "ARM-SURFACE-QUALITY",
    ),
    "NCR-08": ("STATE-PARITY", "OCCURRENCE-TRANSFORMS"),
}

COMMANDS = {
    "verify_checkpoint": "sha256sum -c SHA256SUMS.txt",
    "authoring_output_integrity": """python3 - <<'PY'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('work/final_analysis/authoring_manifest.json').read_text(encoding='utf-8'))
assert manifest['schema'] == 'AP242'
paths = {
    **{name: Path('work/final_release') / name for name in manifest['files']},
    **{name: Path('work/final_analysis') / name for name in manifest['inventories']},
}
records = {**manifest['files'], **manifest['inventories']}
for name, path in sorted(paths.items()):
    data = path.read_bytes()
    assert len(data) == records[name]['size_bytes'], name
    assert hashlib.sha256(data).hexdigest() == records[name]['sha256'], name
print('AUTHORING MANIFEST INTEGRITY: PASS')
PY""",
    "python_ast_source_parse": """python3 - <<'PY'
import ast
from pathlib import Path
roots = (Path('work/r2_source'), Path('work/final_tools'), Path('work/scripts'), Path('work/handoff_tools'))
paths = sorted(path for root in roots for path in root.rglob('*.py'))
assert paths
for path in paths:
    ast.parse(path.read_text(encoding='utf-8'), filename=path.as_posix())
print(f'PYTHON AST SOURCE PARSE: PASS ({len(paths)} files)')
PY""",
    "rebuild_both_endpoints_and_export_ap242": (
        'PYTHONPATH="$PWD/work/r2_source" '
        'work/cadenv/bin/python3 work/r2_source/build_r2.py'
    ),
    "stowed_authoring_audit": (
        'PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 '
        'work/r2_source/per_solid_authoring_audit.py STOWED '
        'work/final_analysis/per_solid_authoring_audit_stowed.json'
    ),
    "deployed_authoring_audit": (
        'PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 '
        'work/r2_source/per_solid_authoring_audit.py DEPLOYED '
        'work/final_analysis/per_solid_authoring_audit_deployed.json'
    ),
    "attachment_scope_audit": (
        'PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 '
        'work/final_tools/audit_final_scope.py '
        '--out work/final_analysis/final_scope_audit.json'
    ),
    "workbook": """mkdir -p work/spreadsheet_runtime
test -n "${CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}"
test -e work/spreadsheet_runtime/node_modules || \
  ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
install -m 0644 work/r2_source/build_workbook.mjs \
  work/spreadsheet_runtime/build_workbook.mjs
(cd work/spreadsheet_runtime && node build_workbook.mjs)""",
    "final_zip": (
        'PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 '
        'work/final_tools/package_final.py'
    ),
}


@dataclass
class SourceEntry:
    source: Path
    destination: Path
    kind: str
    mode: int
    size: int
    mtime_ns: int
    digest: str | None = None


@dataclass
class EvidenceBundle:
    validation_mode: str
    authoring: dict[str, Any]
    validation_manifest: dict[str, Any]
    validation_summary: dict[str, Any]
    gates: dict[str, Any]
    endpoint_pairs: dict[str, Any]
    motion: dict[str, Any]
    dimensions: dict[str, Any]
    step_text: dict[str, Any]
    reconciliation: dict[str, Any]
    definition_of_done: dict[str, Any]
    connectivity: dict[str, Any]
    inventories: dict[str, dict[str, Any]]
    state_parity_rows: list[dict[str, str]]
    last_execution_record: dict[str, Any]
    expected_gate_ids: tuple[str, ...]
    audit_failure: dict[str, Any] | None
    present_validation_files: tuple[str, ...]
    missing_validation_files: tuple[str, ...]


def relative_text(path: Path) -> str:
    """Return a workspace-relative POSIX path and reject path escape."""
    relative = path.relative_to(ROOT)
    if relative.is_absolute() or ".." in relative.parts:
        raise RuntimeError(f"non-relative workspace path: {path}")
    return relative.as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def base_relative_text(base: Path, path: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return str(path)


def load_object(path: Path, label: str, base: Path = ROOT) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"{label} is unreadable or invalid: {base_relative_text(base, path)}"
        ) from exc
    if not isinstance(value, dict):
        raise RuntimeError(
            f"{label} root is not an object: {base_relative_text(base, path)}"
        )
    return value


def load_csv_rows(path: Path, label: str, base: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise RuntimeError(f"{label} has a blank or duplicated header")
            if label == "state parity" and tuple(reader.fieldnames) != STATE_PARITY_FIELDS:
                raise RuntimeError("state parity CSV header does not match the frozen schema")
            return [dict(row) for row in reader]
    except OSError as exc:
        raise RuntimeError(
            f"{label} is unreadable: {base_relative_text(base, path)}"
        ) from exc


def verify_hash_record(path: Path, record: object, label: str, base: Path) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise RuntimeError(
            f"{label} missing for {base_relative_text(base, path)}"
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or not isinstance(record, dict):
        raise RuntimeError(
            f"{label} missing/invalid/non-regular for {base_relative_text(base, path)}"
        )
    if record.get("size_bytes") != path.stat().st_size:
        raise RuntimeError(
            f"{label} size mismatch for {base_relative_text(base, path)}"
        )
    if str(record.get("sha256", "")).lower() != sha256_file(path):
        raise RuntimeError(
            f"{label} SHA-256 mismatch for {base_relative_text(base, path)}"
        )


def expected_gate_ids_from_source(path: Path) -> tuple[str, ...]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    except (OSError, SyntaxError) as exc:
        raise RuntimeError("staged validate_r2.py cannot be parsed") from exc
    assignments = [
        node.value
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and (
            (isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "EXPECTED_GATE_IDS"
                for target in node.targets
            ))
            or (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "EXPECTED_GATE_IDS"
            )
        )
    ]
    if len(assignments) != 1:
        raise RuntimeError("validate_r2.py must define EXPECTED_GATE_IDS exactly once")
    try:
        value = ast.literal_eval(assignments[0])
    except (ValueError, TypeError) as exc:
        raise RuntimeError("EXPECTED_GATE_IDS is not a literal sequence") from exc
    if (
        not isinstance(value, (tuple, list))
        or len(value) != 31
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != 31
    ):
        raise RuntimeError("EXPECTED_GATE_IDS is not the exact unique frozen 31-ID set")
    creo_assignments = [
        node.value
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and (
            (isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "CREO_ENVIRONMENT_DISPOSITION"
                for target in node.targets
            ))
            or (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "CREO_ENVIRONMENT_DISPOSITION"
            )
        )
    ]
    if len(creo_assignments) != 1:
        raise RuntimeError("validate_r2.py must define CREO_ENVIRONMENT_DISPOSITION exactly once")
    try:
        staged_creo_disposition = ast.literal_eval(creo_assignments[0])
    except (ValueError, TypeError) as exc:
        raise RuntimeError("CREO_ENVIRONMENT_DISPOSITION is not a literal string") from exc
    if staged_creo_disposition != CREO_DISPOSITION:
        raise RuntimeError("staged validator Creo disposition is not the mandated informational N/A text")
    return tuple(value)


def validate_last_execution_record(value: dict[str, Any]) -> None:
    if value.get("schema") != "DF8_CODEX_LAST_EXECUTION_RECORD_V1":
        raise RuntimeError("LAST_EXECUTION_RECORD.json schema is not V1")
    recorded = value.get("recorded_at_utc")
    if not isinstance(recorded, str) or not recorded.strip():
        raise RuntimeError("LAST_EXECUTION_RECORD.json lacks recorded_at_utc")
    try:
        recorded_time = dt.datetime.fromisoformat(recorded.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("LAST_EXECUTION_RECORD.json recorded_at_utc is not ISO-8601") from exc
    if recorded_time.utcoffset() != dt.timedelta(0):
        raise RuntimeError("LAST_EXECUTION_RECORD.json recorded_at_utc is not UTC")
    for field in (
        "last_command", "last_successful_modifying_command", "last_successful_audit_command",
    ):
        record = value.get(field)
        if not isinstance(record, dict) or not isinstance(record.get("command"), str) or not record["command"].strip():
            raise RuntimeError(f"LAST_EXECUTION_RECORD.json has invalid {field}.command")
        exit_code = record.get("exit_code")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            raise RuntimeError(f"LAST_EXECUTION_RECORD.json has invalid {field}.exit_code")
        if field != "last_command" and exit_code != 0:
            raise RuntimeError(f"LAST_EXECUTION_RECORD.json {field} is not successful")
        command = record["command"]
        if any(prefix in command for prefix in (str(ROOT), "/workspace/", "/root/", "/tmp/")):
            raise RuntimeError(
                f"LAST_EXECUTION_RECORD.json {field}.command contains an unavailable absolute path"
            )
    modified = value.get("last_modified_files")
    if (
        not isinstance(modified, list)
        or any(not isinstance(item, str) or not item.strip() for item in modified)
        or any(Path(item).is_absolute() or ".." in PurePosixPath(item).parts for item in modified)
        or any(any(character in item for character in ("\\", "\n", "\r")) for item in modified)
        or len(modified) != len(set(modified))
    ):
        raise RuntimeError("LAST_EXECUTION_RECORD.json has invalid last_modified_files")


def validate_last_audit_failure(
    base: Path,
    value: dict[str, Any],
    last_execution: dict[str, Any],
) -> None:
    expected_keys = {
        "schema", "recorded_at_utc", "command", "exit_code", "exception_type",
        "exception_message", "failure_stage", "completed_motion_sample_count",
        "present_validation_files", "missing_validation_files",
        "merged_motion_audit", "release_authorized",
    }
    if set(value) != expected_keys:
        raise RuntimeError(
            "LAST_AUDIT_FAILURE.json key set is not exact; "
            f"missing={sorted(expected_keys - set(value))}, "
            f"unexpected={sorted(set(value) - expected_keys)}"
        )
    if value.get("schema") != LAST_AUDIT_FAILURE_SCHEMA:
        raise RuntimeError("LAST_AUDIT_FAILURE.json schema is not V1")
    recorded = value.get("recorded_at_utc")
    if not isinstance(recorded, str) or not recorded.endswith("Z"):
        raise RuntimeError("LAST_AUDIT_FAILURE.json recorded_at_utc is not UTC-Z")
    try:
        recorded_time = dt.datetime.fromisoformat(recorded[:-1] + "+00:00")
    except ValueError as exc:
        raise RuntimeError("LAST_AUDIT_FAILURE.json recorded_at_utc is invalid") from exc
    if recorded_time.utcoffset() != dt.timedelta(0):
        raise RuntimeError("LAST_AUDIT_FAILURE.json recorded_at_utc is not UTC")
    command = value.get("command")
    if not isinstance(command, str) or not command.strip():
        raise RuntimeError("LAST_AUDIT_FAILURE.json command is blank")
    if any(prefix in command for prefix in (str(ROOT), "/workspace/", "/root/", "/tmp/")):
        raise RuntimeError("LAST_AUDIT_FAILURE.json command contains an unavailable absolute path")
    if value.get("exit_code") != 1 or isinstance(value.get("exit_code"), bool):
        raise RuntimeError("LAST_AUDIT_FAILURE.json exit_code is not exactly 1")
    if value.get("exception_type") != "KeyError" or value.get("exception_message") != "'angle_deg'":
        raise RuntimeError("LAST_AUDIT_FAILURE.json exception is not exact KeyError 'angle_deg'")
    if value.get("failure_stage") != TERMINAL_AUDIT_STAGE:
        raise RuntimeError("LAST_AUDIT_FAILURE.json failure stage is not exact")
    if value.get("completed_motion_sample_count") != 81:
        raise RuntimeError("LAST_AUDIT_FAILURE.json completed sample count is not exactly 81")
    if value.get("present_validation_files") != list(TERMINAL_AUDIT_PRESENT_VALIDATION_FILES):
        raise RuntimeError("LAST_AUDIT_FAILURE.json present validation file set is not exact")
    if value.get("missing_validation_files") != list(TERMINAL_AUDIT_MISSING_VALIDATION_FILES):
        raise RuntimeError("LAST_AUDIT_FAILURE.json missing validation file set is not exact")
    if value.get("release_authorized") is not False:
        raise RuntimeError("LAST_AUDIT_FAILURE.json must make release_authorized false")
    merged = value.get("merged_motion_audit")
    if not isinstance(merged, dict) or set(merged) != {"path", "size_bytes", "sha256"}:
        raise RuntimeError("LAST_AUDIT_FAILURE.json merged_motion_audit object is not exact")
    if merged.get("path") != MERGED_MOTION_AUDIT_PATH.as_posix():
        raise RuntimeError("LAST_AUDIT_FAILURE.json merged audit path is not exact")
    if (
        merged.get("size_bytes") != TERMINAL_MERGED_MOTION_SIZE_BYTES
        or merged.get("sha256") != TERMINAL_MERGED_MOTION_SHA256
    ):
        raise RuntimeError("LAST_AUDIT_FAILURE.json merged audit identity is not the observed terminal file")
    verify_hash_record(
        base / MERGED_MOTION_AUDIT_PATH,
        merged,
        "LAST_AUDIT_FAILURE merged motion audit",
        base,
    )
    last_command = last_execution.get("last_command", {})
    if (
        not isinstance(last_command, dict)
        or last_command.get("command") != command
        or last_command.get("exit_code") != 1
    ):
        raise RuntimeError("LAST_AUDIT_FAILURE disagrees with LAST_EXECUTION_RECORD last_command")
    modified = set(last_execution.get("last_modified_files", []))
    required_modified = {
        (Path("work/final_analysis/validation") / name).as_posix()
        for name in TERMINAL_AUDIT_PRESENT_VALIDATION_FILES
    }
    if not required_modified <= modified:
        raise RuntimeError(
            "LAST_EXECUTION_RECORD does not enumerate every present failed-audit output: "
            f"missing={sorted(required_modified - modified)}"
        )


def load_terminal_motion_evidence(
    path: Path,
    state_parity_rows: list[dict[str, str]],
    base: Path,
) -> dict[str, Any]:
    """Derive only measured facts from the completed merged CSV after terminal failure."""
    expected_fields = (
        "sample_index", "angle_deg", "occurrence_a", "solid_index_a", "variant_a",
        "part_number_a", "occurrence_b", "solid_index_b", "variant_b", "part_number_b",
        "aabb_overlap", "aabb_gap_mm", "exact_common_status", "common_volume_mm3",
        "documented_positive_volume_exception", "intentional_fit_exception_id",
        "exact_distance_status", "exact_clearance_mm", "result", "error",
    )
    classification_by_occurrence: dict[str, str] = {}
    for row in state_parity_rows:
        occurrence = str(row.get("occurrence_id", "")).strip()
        classification = str(row.get("classification", "")).strip().upper()
        if not occurrence or not classification:
            continue
        previous = classification_by_occurrence.setdefault(occurrence, classification)
        if previous != classification:
            raise RuntimeError(
                f"state parity has conflicting classifications for {occurrence}: "
                f"{previous!r} versus {classification!r}"
            )

    sample_rows: Counter[int] = Counter()
    sample_angles: dict[int, int] = {}
    result_counts: Counter[str] = Counter()
    common_status_counts: Counter[str] = Counter()
    distance_status_counts: Counter[str] = Counter()
    fit_id_counts: Counter[str] = Counter()
    classification_observation_counts: Counter[str] = Counter()
    unauthorized_angles: set[int] = set()
    unauthorized: dict[tuple[Any, ...], dict[str, Any]] = {}
    nonempty_error_row_count = 0
    row_count = 0

    try:
        with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != expected_fields:
                raise RuntimeError(
                    "terminal merged motion CSV header is not exact; "
                    f"actual={reader.fieldnames!r}"
                )
            for row in reader:
                row_count += 1
                try:
                    sample_index = int(row["sample_index"])
                    angle_value = float(row["angle_deg"])
                    if not angle_value.is_integer():
                        raise ValueError("non-integral angle")
                    angle = int(angle_value)
                    common_volume = float(row["common_volume_mm3"])
                    solid_a = int(row["solid_index_a"])
                    solid_b = int(row["solid_index_b"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise RuntimeError(
                        f"terminal merged motion CSV has invalid numeric fields at data row {row_count}"
                    ) from exc
                sample_rows[sample_index] += 1
                previous_angle = sample_angles.setdefault(sample_index, angle)
                if previous_angle != angle:
                    raise RuntimeError(
                        f"terminal merged motion sample {sample_index} has multiple angles"
                    )
                result = str(row.get("result", ""))
                result_counts[result] += 1
                common_status_counts[str(row.get("exact_common_status", ""))] += 1
                distance_status_counts[str(row.get("exact_distance_status", ""))] += 1
                if str(row.get("error", "")).strip():
                    nonempty_error_row_count += 1
                fit_id = str(row.get("intentional_fit_exception_id", "")).strip()
                if fit_id:
                    fit_id_counts[fit_id] += 1
                if result != "UNAUTHORIZED_POSITIVE_VOLUME":
                    continue
                if common_volume <= 0.0:
                    raise RuntimeError(
                        "terminal merged motion unauthorized row lacks positive common volume"
                    )
                occurrence_a = str(row.get("occurrence_a", ""))
                occurrence_b = str(row.get("occurrence_b", ""))
                classification_a = classification_by_occurrence.get(occurrence_a)
                classification_b = classification_by_occurrence.get(occurrence_b)
                if not classification_a or not classification_b:
                    raise RuntimeError(
                        "terminal merged motion classification join is incomplete for "
                        f"{occurrence_a!r}/{occurrence_b!r}"
                    )
                relationship = "_".join(sorted((classification_a, classification_b)))
                classification_observation_counts[relationship] += 1
                unauthorized_angles.add(angle)
                key = (
                    occurrence_a, solid_a, str(row.get("variant_a", "")),
                    str(row.get("part_number_a", "")), classification_a,
                    occurrence_b, solid_b, str(row.get("variant_b", "")),
                    str(row.get("part_number_b", "")), classification_b,
                )
                aggregate = unauthorized.setdefault(
                    key,
                    {
                        "scope": "MOTION",
                        "occurrence_a": occurrence_a,
                        "solid_index_a": solid_a,
                        "variant_a": key[2],
                        "part_number_a": key[3],
                        "classification_a": classification_a,
                        "occurrence_b": occurrence_b,
                        "solid_index_b": solid_b,
                        "variant_b": key[7],
                        "part_number_b": key[8],
                        "classification_b": classification_b,
                        "classification_relationship": relationship,
                        "result": "UNAUTHORIZED_POSITIVE_VOLUME",
                        "observation_count": 0,
                        "angles_deg": [],
                        "minimum_angle_deg": angle,
                        "maximum_angle_deg": angle,
                        "maximum_common_volume_mm3": common_volume,
                    },
                )
                aggregate["observation_count"] += 1
                aggregate["angles_deg"].append(angle)
                aggregate["minimum_angle_deg"] = min(aggregate["minimum_angle_deg"], angle)
                aggregate["maximum_angle_deg"] = max(aggregate["maximum_angle_deg"], angle)
                aggregate["maximum_common_volume_mm3"] = max(
                    aggregate["maximum_common_volume_mm3"], common_volume,
                )
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        raise RuntimeError(
            f"terminal merged motion CSV is unreadable: {base_relative_text(base, path)}"
        ) from exc

    if row_count != TERMINAL_MOTION_DATA_ROW_COUNT:
        raise RuntimeError(
            f"terminal merged motion row count is not exact: {row_count}"
        )
    if sample_rows != Counter({index: TERMINAL_MOTION_ROWS_PER_SAMPLE for index in range(1, 82)}):
        raise RuntimeError("terminal merged motion does not have exactly 17,875 rows per 81 samples")
    if sample_angles != {index: index - 1 for index in range(1, 82)}:
        raise RuntimeError("terminal merged motion sample/angle coverage is not exact 0..80 degrees")
    if dict(result_counts) != TERMINAL_MOTION_RESULT_COUNTS:
        raise RuntimeError(
            f"terminal merged motion result counts disagree with observed record: {dict(result_counts)}"
        )
    if dict(common_status_counts) != TERMINAL_MOTION_COMMON_STATUS_COUNTS:
        raise RuntimeError(
            "terminal merged motion exact-common status counts disagree with observed record: "
            f"{dict(common_status_counts)}"
        )
    if tuple(sorted(distance_status_counts.values())) != TERMINAL_MOTION_DISTANCE_STATUS_COUNT_VALUES:
        raise RuntimeError(
            "terminal merged motion exact-distance status counts disagree with observed record: "
            f"{dict(distance_status_counts)}"
        )
    if nonempty_error_row_count != 0:
        raise RuntimeError("terminal merged motion has nonempty error rows")
    if len(fit_id_counts) != 15 or set(fit_id_counts.values()) != {81}:
        raise RuntimeError(
            f"terminal merged motion fit-use counts are not exact 15 IDs x 81: {dict(fit_id_counts)}"
        )
    if len(unauthorized) != TERMINAL_MOTION_UNAUTHORIZED_UNIQUE_PAIR_COUNT:
        raise RuntimeError(
            f"terminal merged motion unauthorized unique-pair count is not exact: {len(unauthorized)}"
        )
    expected_classification_observations = Counter({
        "FIXED_MOVING": 516,
        "MOVING_MOVING": 165,
        "FLEXIBLE_MOVING": 168,
    })
    if classification_observation_counts != expected_classification_observations:
        raise RuntimeError(
            "terminal merged motion classification counts disagree with observed record: "
            f"{dict(classification_observation_counts)}"
        )
    expected_unauthorized_angles = set(range(3, 23)) | set(range(36, 80))
    if unauthorized_angles != expected_unauthorized_angles:
        raise RuntimeError(
            "terminal merged motion unauthorized-angle coverage disagrees with observed record"
        )

    unauthorized_rows = []
    for aggregate in unauthorized.values():
        aggregate["angles_deg"] = sorted(set(aggregate["angles_deg"]))
        unauthorized_rows.append(aggregate)
    unauthorized_rows.sort(key=lambda row: (
        row["occurrence_a"], row["solid_index_a"], row["variant_a"],
        row["occurrence_b"], row["solid_index_b"], row["variant_b"],
    ))
    category_b_rows = [
        row for row in unauthorized_rows
        if row["classification_a"] in RIGID_CLASSIFICATIONS
        and row["classification_b"] in RIGID_CLASSIFICATIONS
    ]
    nonrigid_rows = [row for row in unauthorized_rows if row not in category_b_rows]
    if (
        len(category_b_rows) != TERMINAL_MOTION_CATEGORY_B_UNIQUE_PAIR_COUNT
        or sum(row["observation_count"] for row in category_b_rows)
        != TERMINAL_MOTION_CATEGORY_B_OBSERVATION_COUNT
        or len(nonrigid_rows) != TERMINAL_MOTION_NONRIGID_UNIQUE_PAIR_COUNT
        or sum(row["observation_count"] for row in nonrigid_rows)
        != TERMINAL_MOTION_NONRIGID_OBSERVATION_COUNT
    ):
        raise RuntimeError("terminal merged motion rigid/nonrigid split disagrees with observed record")

    return {
        "execution_state": "TERMINAL_AUDIT_FAILURE",
        "source": MERGED_MOTION_AUDIT_PATH.as_posix(),
        "summary_artifact_available": False,
        "kinematics_artifact_available": False,
        "sample_count": 81,
        "angle_increment_deg": 1,
        "minimum_angle_deg": 0,
        "maximum_angle_deg": 80,
        "data_row_count": row_count,
        "line_count_including_header": TERMINAL_MOTION_LINE_COUNT,
        "pair_rows_per_sample": TERMINAL_MOTION_ROWS_PER_SAMPLE,
        "result_counts": dict(sorted(result_counts.items())),
        "exact_common_status_counts": dict(sorted(common_status_counts.items())),
        "exact_distance_status_counts": dict(sorted(distance_status_counts.items())),
        "nonempty_error_row_count": nonempty_error_row_count,
        "positive_volume_pair_count": 2_064,
        "unauthorized_positive_volume_pair_count": 849,
        "documented_positive_volume_pair_count": 1_215,
        "boolean_blocked_pair_count": 0,
        "distance_blocked_pair_count": 0,
        "intentional_fit_register_error_count": 0,
        "used_intentional_fit_exception_ids": sorted(fit_id_counts),
        "intentional_fit_exception_use_counts": dict(sorted(fit_id_counts.items())),
        "unauthorized_unique_pair_count": len(unauthorized_rows),
        "unauthorized_unique_pairs": unauthorized_rows,
        "unauthorized_angle_degrees": sorted(unauthorized_angles),
        "unauthorized_classification_observation_counts": dict(
            sorted(classification_observation_counts.items())
        ),
        "category_b_rigid_unique_pair_count": len(category_b_rows),
        "category_b_rigid_observation_count": sum(
            row["observation_count"] for row in category_b_rows
        ),
        "nonrigid_involved_unique_pair_count": len(nonrigid_rows),
        "nonrigid_involved_observation_count": sum(
            row["observation_count"] for row in nonrigid_rows
        ),
        "minimum_exact_noninterfering_clearance_mm": None,
        "track_validation_error_count": None,
        "maximum_closure_residual_abs_mm": None,
        "crosshead_travel_0_to_80_mm": None,
        "elapsed_seconds": None,
        "execution_topology": None,
    }


def verify_creo_informational_items(value: object, label: str) -> None:
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        raise RuntimeError(f"{label} must contain exactly one Creo informational item")
    item = value[0]
    if set(item) != set(CREO_INFORMATIONAL_ITEM):
        raise RuntimeError(f"{label} Creo informational item fields are not exact")
    if (
        item.get("item_id") != "CREO-ENVIRONMENT"
        or item.get("status") != "N/A"
        or item.get("disposition") != CREO_DISPOSITION
        or item.get("included_in_acceptance_logic") is not False
    ):
        raise RuntimeError(
            f"{label} Creo informational N/A item is altered or acceptance-bearing"
        )


def verify_authoritative_source_contract(base: Path) -> None:
    missing_or_nonregular = []
    for name in REQUIRED_SOURCE_FILES:
        path = base / name
        try:
            metadata = path.lstat()
        except OSError:
            missing_or_nonregular.append(name)
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            missing_or_nonregular.append(name)
    if missing_or_nonregular:
        raise RuntimeError(
            f"required source files are absent/non-regular: {sorted(missing_or_nonregular)}"
        )
    for live_vendor in LIVE_WP02_VENDOR_FILES:
        path = base / live_vendor
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise RuntimeError(f"live WP02 vendor source is absent: {live_vendor}") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"live WP02 vendor source is not a regular file: {live_vendor}")
    build_path = base / "work/r2_source/build_r2.py"
    build_source_text = build_path.read_text(encoding="utf-8")
    for live_vendor in LIVE_WP02_VENDOR_FILES:
        if build_source_text.count(live_vendor.name) != 1:
            raise RuntimeError(
                f"build_r2.py does not reference live WP02 vendor source exactly once: {live_vendor.name}"
            )
    actual_source_scripts = {
        path.relative_to(base).as_posix()
        for path in (base / "work/r2_source").rglob("*")
        if path.is_file() and path.suffix.lower() in ACTIVE_ENTRYPOINT_SUFFIXES
    }
    required_source_scripts = {
        name for name in REQUIRED_SOURCE_FILES if name.startswith("work/r2_source/")
    }
    if not actual_source_scripts <= required_source_scripts:
        raise RuntimeError(
            "REQUIRED_SOURCE_FILES omits current r2_source script(s): "
            f"{sorted(actual_source_scripts - required_source_scripts)}"
        )


def require_workspace_inputs() -> None:
    missing_sources = [name for name in REQUIRED_SOURCE_FILES if not (ROOT / name).is_file()]
    missing_sources.extend(
        path.as_posix() for path in LIVE_WP02_VENDOR_FILES if not (ROOT / path).is_file()
    )
    for source_name, _destination, _role in COMMISSION_SOURCES:
        if not (ROOT / source_name).is_file():
            missing_sources.append(source_name.as_posix())
    if missing_sources:
        raise RuntimeError(f"required source file(s) missing: {sorted(set(missing_sources))}")

    verify_authoritative_source_contract(ROOT)

    missing_trees = [name for name in REQUIRED_COPY_TREES if not (ROOT / name).is_dir()]
    if missing_trees:
        raise RuntimeError(f"required handoff tree(s) missing: {sorted(missing_trees)}")
    preserved = sorted(path for path in (ROOT / "work").glob("preserved_*") if path.is_dir())
    if not preserved:
        raise RuntimeError("no preserved checkpoint directories were found under work/")
    candidate_outputs = sorted(
        path for path in (ROOT / "outputs/6f4e7892e9f1").rglob("*")
        if path.is_file()
        and "CANDIDATE_WIP" in path.name.upper()
        and path.suffix.lower() == ".zip"
    )
    if not candidate_outputs:
        raise RuntimeError("candidate WIP .zip package is absent from outputs/6f4e7892e9f1")


def load_evidence(base: Path) -> EvidenceBundle:
    """Load and cross-check one evidence tree; callers pass ROOT or staged root."""
    verify_authoritative_source_contract(base)
    final_release = base / FINAL_RELEASE
    final_analysis = base / FINAL_ANALYSIS
    validation_dir = base / VALIDATION
    if not validation_dir.is_dir() or validation_dir.is_symlink():
        raise RuntimeError("validation evidence directory is absent/non-regular")
    actual_validation_names = {path.name for path in validation_dir.iterdir()}
    complete_names = set(REQUIRED_VALIDATION_FILES)
    terminal_names = set(TERMINAL_AUDIT_PRESENT_VALIDATION_FILES)
    if actual_validation_names == complete_names:
        validation_mode = "COMPLETE"
        present_validation_files = tuple(sorted(complete_names))
        missing_validation_files: tuple[str, ...] = ()
    elif actual_validation_names == terminal_names:
        validation_mode = "TERMINAL_AUDIT_FAILURE"
        present_validation_files = TERMINAL_AUDIT_PRESENT_VALIDATION_FILES
        missing_validation_files = TERMINAL_AUDIT_MISSING_VALIDATION_FILES
    else:
        raise RuntimeError(
            "validation top-level file set matches neither complete nor the exact "
            "terminal-audit-failure state; "
            f"actual={sorted(actual_validation_names)}, "
            f"complete_missing={sorted(complete_names - actual_validation_names)}, "
            f"complete_unexpected={sorted(actual_validation_names - complete_names)}, "
            f"terminal_missing={sorted(terminal_names - actual_validation_names)}, "
            f"terminal_unexpected={sorted(actual_validation_names - terminal_names)}"
        )

    final_required = (
        final_release / FINAL_STOWED,
        final_release / FINAL_DEPLOYED,
        final_analysis / "authoring_inventory_stowed.json",
        final_analysis / "authoring_inventory_deployed.json",
        final_analysis / "authoring_manifest.json",
        *(validation_dir / name for name in present_validation_files),
        base / "work/handoff_tools/LAST_EXECUTION_RECORD.json",
        *((base / LAST_AUDIT_FAILURE_PATH,) if validation_mode == "TERMINAL_AUDIT_FAILURE" else ()),
    )
    absent_final: list[str] = []
    empty_final: list[str] = []
    for path in final_required:
        try:
            metadata = path.lstat()
        except OSError:
            absent_final.append(base_relative_text(base, path))
            continue
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            absent_final.append(base_relative_text(base, path))
        elif metadata.st_size == 0:
            empty_final.append(base_relative_text(base, path))
    if absent_final or empty_final:
        raise RuntimeError(
            "validator final files are incomplete; "
            f"missing_or_nonregular={absent_final}, empty={empty_final}"
        )

    for path in validation_dir.iterdir():
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(
                f"validation top-level node is not a regular file: {base_relative_text(base, path)}"
            )

    authoring_path = final_analysis / "authoring_manifest.json"
    authoring = load_object(authoring_path, "authoring manifest", base)
    if str(authoring.get("schema", "")).strip().upper() != "AP242":
        raise RuntimeError("authoring manifest schema is not AP242")
    expected_steps = {FINAL_STOWED, FINAL_DEPLOYED}
    expected_inventories = {"authoring_inventory_stowed.json", "authoring_inventory_deployed.json"}
    if set(authoring.get("files", {})) != expected_steps:
        raise RuntimeError("authoring manifest STEP set is not the exact final two-master set")
    if set(authoring.get("inventories", {})) != expected_inventories:
        raise RuntimeError("authoring manifest inventory set is not exact")
    for name in sorted(expected_steps):
        verify_hash_record(
            final_release / name, authoring["files"].get(name),
            "authoring manifest STEP record", base,
        )
    for name in sorted(expected_inventories):
        verify_hash_record(
            final_analysis / name, authoring["inventories"].get(name),
            "authoring manifest inventory record", base,
        )

    expected_gate_ids = expected_gate_ids_from_source(
        base / "work/r2_source/validate_r2.py",
    )
    last_execution = load_object(
        base / "work/handoff_tools/LAST_EXECUTION_RECORD.json",
        "last execution record", base,
    )
    validate_last_execution_record(last_execution)
    state_parity_rows = load_csv_rows(
        validation_dir / "state_parity.csv", "state parity", base,
    )

    validation: dict[str, Any] = {}
    gates: dict[str, Any] = {}
    summary: dict[str, Any] = {}
    motion: dict[str, Any] = {}
    audit_failure: dict[str, Any] | None = None
    if validation_mode == "COMPLETE":
        validation_path = validation_dir / "validation_manifest.json"
        validation = load_object(validation_path, "validation manifest", base)
        records = validation.get("files")
        if not isinstance(records, dict):
            raise RuntimeError("validation manifest has no files object")
        validation_bound: dict[str, Path] = {
            name: validation_dir / name
            for name in REQUIRED_VALIDATION_FILES if name != "validation_manifest.json"
        }
        validation_bound.update({
            FINAL_STOWED: final_release / FINAL_STOWED,
            FINAL_DEPLOYED: final_release / FINAL_DEPLOYED,
            "authoring_inventory_stowed.json": final_analysis / "authoring_inventory_stowed.json",
            "authoring_inventory_deployed.json": final_analysis / "authoring_inventory_deployed.json",
            "authoring_manifest.json": authoring_path,
            "validate_r2.py": base / "work/r2_source/validate_r2.py",
        })
        if len(validation_bound) != 33 or set(records) != set(validation_bound):
            raise RuntimeError(
                "validation manifest is not the exact 33-key set; "
                f"count={len(records)}, missing={sorted(set(validation_bound) - set(records))}, "
                f"unexpected={sorted(set(records) - set(validation_bound))}"
            )
        for name, path in sorted(validation_bound.items()):
            verify_hash_record(path, records.get(name), "validation manifest record", base)

        gates = load_object(validation_dir / "gate_results.json", "gate results", base)
        gate_rows = gates.get("gates")
        if not isinstance(gate_rows, list) or len(gate_rows) != len(expected_gate_ids):
            raise RuntimeError("completed validator does not contain the frozen 31-gate result set")
        if any(not isinstance(row, dict) for row in gate_rows):
            raise RuntimeError("completed validator gate row is not an object")
        gate_ids = tuple(str(row.get("gate_id", "")) for row in gate_rows)
        if gate_ids != expected_gate_ids:
            raise RuntimeError("gate rows do not match staged EXPECTED_GATE_IDS exactly and in order")
        statuses = [row.get("status") for row in gate_rows]
        if any(status not in VALID_GATE_STATUSES for status in statuses):
            invalid_statuses = sorted(
                {repr(status) for status in statuses if status not in VALID_GATE_STATUSES}
            )
            raise RuntimeError(f"gate row has invalid status: {invalid_statuses}")
        recomputed_counts = {
            status: Counter(statuses)[status] for status in ("PASS", "FAIL", "BLOCKED")
        }
        recomputed_release = (
            "PASS" if recomputed_counts["FAIL"] == 0 and recomputed_counts["BLOCKED"] == 0
            else "NOT_RELEASED"
        )
        recomputed_label = (
            "FINAL — RELEASED" if recomputed_release == "PASS"
            else "CORRECTIVE VALIDATION FAILED — NOT RELEASED"
        )
        gate_counts = gates.get("gate_counts")
        if (
            not isinstance(gate_counts, dict)
            or set(gate_counts) != {"PASS", "FAIL", "BLOCKED"}
            or any(
                isinstance(gate_counts.get(status), bool)
                or not isinstance(gate_counts.get(status), int)
                for status in VALID_GATE_STATUSES
            )
            or gate_counts != recomputed_counts
        ):
            raise RuntimeError("gate_results gate_counts disagrees with recomputed frozen gate rows")
        if gates.get("computed_release_status") != recomputed_release:
            raise RuntimeError("gate_results release status disagrees with recomputed frozen gate rows")
        if gates.get("package_required_label") != recomputed_label:
            raise RuntimeError("gate_results package label disagrees with recomputed frozen gate rows")
        verify_creo_informational_items(
            gates.get("informational_environment_items"), "gate_results",
        )

        summary = load_object(validation_dir / "validation_summary.json", "validation summary", base)
        required_summary_fields = {
            "validation_status", "required_package_label", "gate_counts",
            "endpoint_pair_counts", "motion", "elapsed_seconds",
            "informational_environment_items",
        }
        missing_summary_fields = sorted(required_summary_fields - set(summary))
        if missing_summary_fields:
            raise RuntimeError(
                f"completed validation summary lacks required final fields: {missing_summary_fields}"
            )
        if summary.get("validation_status") != recomputed_release:
            raise RuntimeError("validation summary status disagrees with recomputed gate results")
        if summary.get("required_package_label") != recomputed_label:
            raise RuntimeError("validation summary package label disagrees with recomputed gate results")
        summary_counts = summary.get("gate_counts")
        if (
            not isinstance(summary_counts, dict)
            or set(summary_counts) != {"PASS", "FAIL", "BLOCKED"}
            or any(
                isinstance(summary_counts.get(status), bool)
                or not isinstance(summary_counts.get(status), int)
                for status in VALID_GATE_STATUSES
            )
            or summary_counts != recomputed_counts
        ):
            raise RuntimeError("validation summary gate counts disagree with recomputed gate results")
        verify_creo_informational_items(
            summary.get("informational_environment_items"), "validation_summary",
        )
        motion = load_object(validation_dir / "motion_audit_summary.json", "motion summary", base)
    else:
        audit_failure = load_object(
            base / LAST_AUDIT_FAILURE_PATH, "last audit failure", base,
        )
        validate_last_audit_failure(base, audit_failure, last_execution)
        motion = load_terminal_motion_evidence(
            validation_dir / "motion_full_mechanism_audit.csv.gz",
            state_parity_rows,
            base,
        )

    inventories = {
        "STOWED": load_object(
            final_analysis / "authoring_inventory_stowed.json", "stowed authoring inventory", base,
        ),
        "DEPLOYED": load_object(
            final_analysis / "authoring_inventory_deployed.json", "deployed authoring inventory", base,
        ),
    }
    evidence = EvidenceBundle(
        validation_mode=validation_mode,
        authoring=authoring,
        validation_manifest=validation,
        validation_summary=summary,
        gates=gates,
        endpoint_pairs=load_object(validation_dir / "endpoint_pair_summary.json", "endpoint pair summary", base),
        motion=motion,
        dimensions=load_object(validation_dir / "key_dimensions.json", "key dimensions", base),
        step_text=load_object(validation_dir / "step_text_inspection.json", "STEP inspection", base),
        reconciliation=load_object(
            validation_dir / "occurrence_bom_reconciliation.json",
            "occurrence/BOM reconciliation", base,
        ),
        definition_of_done=load_object(
            validation_dir / "definition_of_done_audit.json", "Definition-of-Done audit", base,
        ),
        connectivity=load_object(
            validation_dir / "connectivity_summary.json", "connectivity summary", base,
        ),
        inventories=inventories,
        state_parity_rows=state_parity_rows,
        last_execution_record=last_execution,
        expected_gate_ids=expected_gate_ids,
        audit_failure=audit_failure,
        present_validation_files=present_validation_files,
        missing_validation_files=missing_validation_files,
    )
    for state in ("STOWED", "DEPLOYED"):
        if state not in evidence.endpoint_pairs or state not in evidence.step_text:
            raise RuntimeError(f"completed validator lacks {state} endpoint evidence")
        if state not in evidence.definition_of_done or state not in evidence.connectivity:
            raise RuntimeError(f"completed validator lacks {state} cohesion evidence")
    return evidence


def active_process_tokens() -> tuple[set[str], set[str], set[str]]:
    # Handoff packaging/verification processes are not geometry, source-build,
    # or engineering-audit processes.  They are serialized by the archive
    # lock and must not make their own quiescence scan self-report through
    # Work-mode's host-visible sandbox wrappers.
    handoff_entrypoints = {"build_handoff.py", "validate_handoff.py"}
    full: set[str] = set()
    bare: set[str] = set()
    modules: set[str] = set()
    for relative_dir in ACTIVE_ENTRYPOINT_DIRS:
        directory = ROOT / relative_dir
        if not directory.is_dir():
            raise RuntimeError(f"active-process entrypoint directory is absent: {relative_dir}")
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in ACTIVE_ENTRYPOINT_SUFFIXES:
                if path.name.casefold() in handoff_entrypoints:
                    continue
                relative = path.relative_to(ROOT).as_posix()
                full.add(relative.casefold())
                bare.add(path.name.casefold())
                modules.add(path.stem.casefold())
                modules.add(".".join(Path(relative).with_suffix("").parts).casefold())
    if not full:
        raise RuntimeError("no active-process entrypoints were discovered")
    return full, bare, modules


def current_process_chain() -> set[int]:
    """Return this process and its launcher ancestors for self-scan exclusion."""
    chain: set[int] = set()
    pid = os.getpid()
    while pid > 0 and pid not in chain:
        chain.add(pid)
        status_path = Path("/proc") / str(pid) / "status"
        try:
            parent_line = next(
                line for line in status_path.read_text(encoding="utf-8").splitlines()
                if line.startswith("PPid:")
            )
            parent_pid = int(parent_line.split(":", 1)[1].strip())
        except (FileNotFoundError, ProcessLookupError, StopIteration):
            break
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                f"cannot establish current launcher chain at PID {pid}"
            ) from exc
        if parent_pid <= 0:
            break
        pid = parent_pid
    return chain


def active_workspace_processes() -> list[dict[str, Any]]:
    """Find concurrent source/final/script/handoff operations in this workspace."""
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        raise RuntimeError("/proc is unavailable; cannot prove CAD/audit process quiescence")
    self_and_launchers = current_process_chain()
    root_text = str(ROOT)
    full_tokens, bare_tokens, module_tokens = active_process_tokens()
    findings: list[dict[str, Any]] = []
    for item in sorted(proc_root.iterdir(), key=lambda path: int(path.name) if path.name.isdigit() else -1):
        if not item.name.isdigit() or int(item.name) in self_and_launchers:
            continue
        pid = int(item.name)
        try:
            raw = (item / "cmdline").read_bytes()
            if not raw:
                continue
            args = [part.decode("utf-8", errors="replace") for part in raw.split(b"\0") if part]
            command = " ".join(args)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as exc:
            try:
                executable = os.readlink(item / "exe").casefold()
            except (FileNotFoundError, ProcessLookupError):
                continue
            except OSError as exe_exc:
                raise RuntimeError(
                    f"cannot inspect potentially relevant process PID {pid}"
                ) from exe_exc
            executable_name = Path(executable).name
            if (
                executable_name.startswith("python")
                or executable_name in {"node", "nodejs", "bash", "sh", "dash", "zsh", "ksh"}
            ):
                raise RuntimeError(
                    f"cannot inspect interpreter process PID {pid}; quiescence fails closed"
                ) from exc
            continue
        except OSError as exc:
            raise RuntimeError(f"cannot inspect process PID {pid}; quiescence fails closed") from exc
        try:
            cwd = os.readlink(item / "cwd")
        except (FileNotFoundError, ProcessLookupError):
            continue
        except OSError as exc:
            arg_names = {Path(arg).name.casefold() for arg in args}
            # Work-mode launches this builder through outer sandbox/bwrap
            # wrappers that are outside the inner PID namespace.  Those
            # wrappers repeat this exact builder command in their argv but
            # can deny /proc/<pid>/cwd to the inner process, so they cannot
            # appear in current_process_chain().  The archive lock still
            # excludes a second builder; ignore only a recognized wrapper
            # whose argv identifies this handoff builder, never a CAD,
            # source-build, or validation command.
            launcher_name = Path(args[0]).name.casefold() if args else ""
            command_lower = command.casefold()
            handoff_wrapper = (
                launcher_name in {"codex-linux-sandbox", "bwrap"}
                and "work/handoff_tools/build_handoff.py" in command_lower
                and "work/r2_source/validate_r2.py" not in command_lower
                and "work/r2_source/build_r2.py" not in command_lower
            )
            if handoff_wrapper:
                continue
            if arg_names & bare_tokens or set(arg.casefold() for arg in args) & module_tokens or any(
                token in command.casefold() for token in full_tokens
            ):
                raise RuntimeError(
                    f"cannot inspect cwd of relevant process PID {pid}; quiescence fails closed"
                ) from exc
            cwd = ""
        command_lower = command.casefold()
        arg_names = {Path(arg).name.casefold() for arg in args}
        workspace_related = (
            cwd == root_text or cwd.startswith(root_text + os.sep) or root_text in command
        )
        named_operation = (
            bool(arg_names & bare_tokens)
            or bool(set(arg.casefold() for arg in args) & module_tokens)
            or any(token in command_lower for token in full_tokens)
        )
        spawned_occt_worker = (
            workspace_related
            and "multiprocessing.spawn" in command_lower
            and ("cadenv" in command_lower or "python3.12" in command_lower)
        )
        captured_cad_python = workspace_related and "work/cadenv/bin/python" in command_lower
        if named_operation or (workspace_related and (spawned_occt_worker or captured_cad_python)):
            display = command.replace(root_text, ".")
            findings.append({"pid": pid, "command": display[:500]})
    return findings


def run_capture(command: list[str], label: str, timeout: int = 120) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8", "LANG": "C.UTF-8"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"dependency capture failed for {label}") from exc
    return completed.stdout.strip() or completed.stderr.strip()


def parse_os_release() -> dict[str, str]:
    result: dict[str, str] = {}
    path = Path("/etc/os-release")
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            result[key] = value.strip().strip('"')
    return dict(sorted(result.items()))


def node_module_root() -> Path:
    configured = os.environ.get("CODEX_PRIMARY_RUNTIME_NODE_MODULES", "").strip()
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(ROOT / "work/spreadsheet_runtime/node_modules")
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved.is_dir():
            return resolved
    raise RuntimeError("managed Node module root is unavailable for dependency capture")


def installed_node_packages(module_root: Path) -> list[dict[str, Any]]:
    """Inventory every installed package root, including nested node_modules."""
    packages: list[dict[str, Any]] = []
    pending = [module_root]
    seen_module_dirs: set[tuple[int, int]] = set()
    while pending:
        current_modules = pending.pop()
        try:
            identity_stat = current_modules.stat()
        except OSError as exc:
            raise RuntimeError("Node module tree changed during dependency capture") from exc
        identity = (identity_stat.st_dev, identity_stat.st_ino)
        if identity in seen_module_dirs:
            continue
        seen_module_dirs.add(identity)
        try:
            children = sorted(current_modules.iterdir(), key=lambda path: path.name)
        except OSError as exc:
            raise RuntimeError("cannot enumerate managed Node module root") from exc
        package_roots: list[Path] = []
        for child in children:
            if child.name.startswith("."):
                continue
            if child.name.startswith("@") and child.is_dir():
                package_roots.extend(
                    sorted((path for path in child.iterdir() if path.is_dir()), key=lambda path: path.name)
                )
            elif child.is_dir():
                package_roots.append(child)
        for package_root in package_roots:
            package_json = package_root / "package.json"
            if not package_json.is_file():
                raise RuntimeError(
                    f"installed Node package lacks package.json: {package_root.name}"
                )
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"invalid installed Node package manifest: {package_root.name}") from exc
            name = data.get("name")
            version = data.get("version")
            if not isinstance(name, str) or not name or not isinstance(version, str) or not version:
                raise RuntimeError(f"installed Node package is not version-pinned: {package_root.name}")
            install_path = package_root.relative_to(module_root).as_posix()
            packages.append(
                {
                    "install_path": install_path,
                    "name": name,
                    "version": version,
                    "package_json_sha256": sha256_file(package_json),
                }
            )
            for directory, dirnames, _filenames in os.walk(package_root, followlinks=False):
                dirnames.sort()
                if "node_modules" in dirnames:
                    nested = Path(directory) / "node_modules"
                    pending.append(nested)
                    dirnames.remove("node_modules")
    packages.sort(key=lambda row: (row["name"].casefold(), row["version"], row["install_path"]))
    if not packages:
        raise RuntimeError("managed Node dependency inventory is empty")
    if not any(row["name"] == "@oai/artifact-tool" for row in packages):
        raise RuntimeError("@oai/artifact-tool is absent from the managed Node dependency inventory")
    return packages


def capture_dependencies() -> dict[str, Any]:
    if not CAD_PYTHON.is_file() or not os.access(CAD_PYTHON, os.X_OK):
        raise RuntimeError("captured CAD Python is unavailable: work/cadenv/bin/python3")
    python_runtime = json.loads(
        run_capture(
            [
                str(CAD_PYTHON),
                "-c",
                (
                    "import json,platform,sys;"
                    "print(json.dumps({'python':platform.python_version(),"
                    "'implementation':platform.python_implementation(),"
                    "'compiler':platform.python_compiler(),"
                    "'cache_tag':sys.implementation.cache_tag},sort_keys=True))"
                ),
            ],
            "CAD Python runtime",
        )
    )
    cad_runtime = json.loads(
        run_capture(
            [
                str(CAD_PYTHON),
                "-c",
                (
                    "import json,cadquery,OCP;"
                    "print(json.dumps({'cadquery':cadquery.__version__,"
                    "'OCP_runtime':OCP.__version__},sort_keys=True))"
                ),
            ],
            "CadQuery/OCP runtime",
        )
    )
    pip_packages = json.loads(
        run_capture(
            [str(CAD_PYTHON), "-m", "pip", "list", "--format=json"],
            "Python package inventory",
        )
    )
    if not isinstance(pip_packages, list) or not pip_packages:
        raise RuntimeError("Python package inventory is empty")
    normalized_python: list[dict[str, str]] = []
    for row in pip_packages:
        if not isinstance(row, dict) or not row.get("name") or not row.get("version"):
            raise RuntimeError("Python dependency is not fully version-pinned")
        normalized_python.append({"name": str(row["name"]), "version": str(row["version"])})
    normalized_python.sort(key=lambda row: (row["name"].casefold(), row["version"]))
    pip_freeze = run_capture(
        [str(CAD_PYTHON), "-m", "pip", "freeze", "--all"],
        "pip freeze",
    ).splitlines()
    pip_check = run_capture([str(CAD_PYTHON), "-m", "pip", "check"], "pip check")

    module_root = node_module_root()
    node_packages = installed_node_packages(module_root)
    runtime_versions = {
        "schema": "DF8_HANDOFF_RUNTIME_VERSIONS_V1",
        "python": python_runtime,
        "cad_runtime": cad_runtime,
        "pip": run_capture([str(CAD_PYTHON), "-m", "pip", "--version"], "pip version").split()[1],
        "pip_check": pip_check,
        "node": run_capture(["node", "--version"], "Node version"),
        "npm": run_capture(["npm", "--version"], "npm version"),
        "operating_system": parse_os_release(),
        "kernel": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "libc": list(platform.libc_ver()),
        },
        "node_module_source": "managed runtime; module tree intentionally excluded from handoff payload",
    }
    return {
        "runtime_versions": runtime_versions,
        "python_packages": normalized_python,
        "python_pip_freeze": sorted(line.strip() for line in pip_freeze if line.strip()),
        "node_packages": node_packages,
    }


def excluded(relative: Path) -> bool:
    if relative.name == ARCHIVE_NAME or relative.name.startswith(f".{ARCHIVE_NAME}."):
        return True
    if relative.suffix.lower() in EXCLUDED_FILE_SUFFIXES:
        return True
    return any(part.casefold() in EXCLUDED_DIR_NAMES for part in relative.parts)


def enumerate_source_tree(source_root: Path, destination_root: Path) -> list[SourceEntry]:
    entries: list[SourceEntry] = []
    stack = [(source_root, destination_root, Path("."))]
    while stack:
        source, destination, local_relative = stack.pop()
        if local_relative != Path(".") and excluded(local_relative):
            continue
        destination_text = destination.as_posix()
        if any(character in destination_text for character in ("\\", "\n", "\r")):
            raise RuntimeError(f"payload path is unsafe for SHA256SUMS: {destination_text!r}")
        try:
            metadata = source.lstat()
        except OSError as exc:
            raise RuntimeError(f"source changed during enumeration: {relative_text(source)}") from exc
        mode = stat.S_IMODE(metadata.st_mode)
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError(f"payload symlink is forbidden: {relative_text(source)}")
        elif stat.S_ISDIR(metadata.st_mode):
            entries.append(SourceEntry(source, destination, "directory", mode, 0, metadata.st_mtime_ns))
            children = sorted(source.iterdir(), key=lambda path: path.name, reverse=True)
            for child in children:
                child_local = child.relative_to(source_root)
                stack.append((child, destination_root / child_local, child_local))
        elif stat.S_ISREG(metadata.st_mode):
            entries.append(
                SourceEntry(source, destination, "file", mode, metadata.st_size, metadata.st_mtime_ns)
            )
        else:
            raise RuntimeError(f"unsupported source node type: {relative_text(source)}")
    return entries


def gather_source_entries() -> tuple[list[SourceEntry], list[Path], list[Path], list[Path]]:
    preserved = sorted(path for path in (ROOT / "work").glob("preserved_*") if path.is_dir())
    specs = [(ROOT / name, Path(name)) for name in REQUIRED_COPY_TREES]
    specs.extend((path, Path("work") / path.name) for path in preserved)
    entries: dict[str, SourceEntry] = {}
    for source_root, destination_root in specs:
        for entry in enumerate_source_tree(source_root, destination_root):
            key = entry.destination.as_posix()
            previous = entries.get(key)
            if previous is not None and previous.source != entry.source:
                raise RuntimeError(f"handoff destination collision: {key}")
            entries[key] = entry
    for source_name, destination, _role in COMMISSION_SOURCES:
        source = ROOT / source_name
        metadata = source.lstat()
        entries[destination.as_posix()] = SourceEntry(
            source, destination, "file", stat.S_IMODE(metadata.st_mode),
            metadata.st_size, metadata.st_mtime_ns,
        )
    candidate_outputs = sorted(
        path
        for path in (ROOT / "outputs/6f4e7892e9f1").rglob("*")
        if path.is_file()
        and "CANDIDATE_WIP" in path.name.upper()
        and path.suffix.lower() == ".zip"
    )
    candidate_temps = sorted(
        path
        for path in (ROOT / "outputs/6f4e7892e9f1").rglob("*")
        if path.is_file()
        and "CANDIDATE_WIP" in path.name.upper()
        and path.suffix.lower() != ".zip"
    )
    return [entries[key] for key in sorted(entries)], preserved, candidate_outputs, candidate_temps


def copy_file_and_hash(source: Path, destination: Path) -> str:
    digest = hashlib.sha256()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_stream, destination.open("wb") as output_stream:
        for chunk in iter(lambda: input_stream.read(1024 * 1024), b""):
            digest.update(chunk)
            output_stream.write(chunk)
    shutil.copystat(source, destination, follow_symlinks=False)
    value = digest.hexdigest()
    if sha256_file(destination) != value:
        raise RuntimeError(f"staged copy hash mismatch: {relative_text(source)}")
    return value


def materialize_snapshot(entries: list[SourceEntry], stage: Path) -> dict[str, str]:
    source_map: dict[str, str] = {}
    directories: list[SourceEntry] = []
    for entry in entries:
        destination = stage / entry.destination
        source_map[entry.destination.as_posix()] = relative_text(entry.source)
        if entry.kind == "directory":
            destination.mkdir(parents=True, exist_ok=True)
            directories.append(entry)
        elif entry.kind == "file":
            entry.digest = copy_file_and_hash(entry.source, destination)
        else:
            raise AssertionError(entry.kind)
    for entry in sorted(directories, key=lambda row: len(row.destination.parts), reverse=True):
        destination = stage / entry.destination
        os.chmod(destination, entry.mode)
        os.utime(destination, ns=(entry.mtime_ns, entry.mtime_ns))
    return source_map


def verify_snapshot_sources(entries: Iterable[SourceEntry]) -> None:
    for entry in entries:
        try:
            metadata = entry.source.lstat()
        except OSError as exc:
            raise RuntimeError(f"source disappeared during snapshot: {relative_text(entry.source)}") from exc
        if metadata.st_mtime_ns != entry.mtime_ns or stat.S_IMODE(metadata.st_mode) != entry.mode:
            raise RuntimeError(f"source metadata changed during snapshot: {relative_text(entry.source)}")
        if entry.kind == "file":
            if metadata.st_size != entry.size or sha256_file(entry.source) != entry.digest:
                raise RuntimeError(f"source content changed during snapshot: {relative_text(entry.source)}")
        elif entry.kind == "symlink":
            raise RuntimeError(f"payload symlink escaped enumeration rejection: {relative_text(entry.source)}")


def generated_write(path: Path, content: str, epoch: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    os.chmod(path, 0o644)
    os.utime(path, (epoch, epoch))


def write_dependency_manifests(stage: Path, captured: dict[str, Any], epoch: int) -> list[Path]:
    environment = stage / "environment"
    environment.mkdir(parents=True, exist_ok=True)
    os.chmod(environment, 0o755)
    os.utime(environment, (epoch, epoch))
    paths = [
        Path("environment/RUNTIME_VERSIONS.json"),
        Path("environment/PYTHON_PACKAGES_FULLY_PINNED.json"),
        Path("environment/PYTHON_REQUIREMENTS_FULLY_PINNED.txt"),
        Path("environment/PYTHON_PIP_FREEZE_RAW.txt"),
        Path("environment/NODE_PACKAGES_FULLY_PINNED.csv"),
    ]
    generated_write(
        stage / paths[0],
        json.dumps(captured["runtime_versions"], indent=2, sort_keys=True) + "\n",
        epoch,
    )
    generated_write(
        stage / paths[1],
        json.dumps(
            {"schema": "DF8_HANDOFF_PINNED_PYTHON_PACKAGES_V1", "packages": captured["python_packages"]},
            indent=2,
            sort_keys=True,
        ) + "\n",
        epoch,
    )
    requirements = "".join(
        f"{row['name']}=={row['version']}\n" for row in captured["python_packages"]
    )
    generated_write(stage / paths[2], requirements, epoch)
    generated_write(stage / paths[3], "\n".join(captured["python_pip_freeze"]) + "\n", epoch)
    node_path = stage / paths[4]
    node_path.parent.mkdir(parents=True, exist_ok=True)
    with node_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("install_path", "name", "version", "package_json_sha256"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(captured["node_packages"])
    os.chmod(node_path, 0o644)
    os.utime(node_path, (epoch, epoch))
    return paths


def iso_time(epoch: int) -> str:
    return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def staged_file_record(stage: Path, relative: Path) -> dict[str, Any]:
    path = stage / relative
    metadata = path.stat()
    return {
        "path": relative.as_posix(),
        "size_bytes": metadata.st_size,
        "sha256": sha256_file(path),
        "mtime_ns": metadata.st_mtime_ns,
        "mtime_utc": iso_time(int(metadata.st_mtime)),
    }


def compact_pair(row: object) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {"invalid_row": row}
    fields = (
        "state", "sample_index", "angle_deg", "pair_index",
        "occurrence_a", "solid_index_a", "part_number_a", "classification_a",
        "occurrence_b", "solid_index_b", "part_number_b", "classification_b",
        "common_volume_mm3", "exact_common_status", "exact_distance_status",
        "exact_clearance_mm", "result", "error",
        "documented_positive_volume_exception", "intentional_fit_exception_id",
        "intentional_fit_match_status",
    )
    return {field: row.get(field) for field in fields if field in row}


def validator_command(evidence: EvidenceBundle) -> str:
    if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE":
        if not isinstance(evidence.audit_failure, dict):
            raise RuntimeError("terminal validation mode lacks LAST_AUDIT_FAILURE record")
        command = evidence.audit_failure.get("command")
        if not isinstance(command, str) or not command.strip():
            raise RuntimeError("terminal LAST_AUDIT_FAILURE command is invalid")
        return command
    topology = evidence.validation_manifest.get("execution_topology", {})
    motion_topology = topology.get("motion_audit", {}) if isinstance(topology, dict) else {}
    workers = motion_topology.get("worker_count") if isinstance(motion_topology, dict) else None
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 8:
        raise RuntimeError("validation manifest lacks an exact motion worker count inside 1..8")
    return (
        'PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 '
        'work/r2_source/validate_r2.py '
        f'--out work/final_analysis/validation --motion-workers {workers}'
    )


def gate_and_ncr_state(evidence: EvidenceBundle) -> dict[str, Any]:
    mapped_gate_ids = {gate_id for gate_ids in NCR_GATE_MAP.values() for gate_id in gate_ids}
    unknown_mapped = sorted(mapped_gate_ids - set(evidence.expected_gate_ids))
    if unknown_mapped or tuple(NCR_GATE_MAP) != tuple(f"NCR-{index:02d}" for index in range(1, 9)):
        raise RuntimeError(
            f"NCR gate formula map is not the frozen NCR-01..08 map: unknown={unknown_mapped}"
        )
    if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE":
        note = (
            "gate_results.json absent after terminal validator failure; "
            "no acceptance status was computed"
        )
        open_gates = [
            {
                "gate_id": gate_id,
                "status": "NOT_COMPUTED",
                "handoff_disposition": "OPEN",
                "requirement": None,
                "measured": None,
                "evidence": None,
                "note": note,
            }
            for gate_id in evidence.expected_gate_ids
        ]
        ncrs = []
        for ncr_id, controlling_gate_ids in NCR_GATE_MAP.items():
            ncrs.append({
                "ncr_id": ncr_id,
                "formula_status": "NOT_COMPUTED",
                "handoff_disposition": "OPEN",
                "controlling_gates": [
                    {"gate_id": gate_id, "status": "NOT_COMPUTED"}
                    for gate_id in controlling_gate_ids
                ],
                "formula_basis": (
                    "Formula was not evaluated because gate_results.json is absent; "
                    "handoff treats the NCR as open without fabricating an acceptance status"
                ),
            })
        return {
            "closed_gates": [],
            "open_gates": open_gates,
            "ncrs": ncrs,
            "ncr_counts": {
                "CLOSED": 0,
                "OPEN": 0,
                "BLOCKED": 0,
                "NOT_COMPUTED": 8,
                "HANDOFF_OPEN": 8,
            },
        }

    rows = evidence.gates.get("gates", [])
    by_id = {
        str(row.get("gate_id")): row
        for row in rows
        if isinstance(row, dict) and row.get("gate_id")
    }
    open_gates = []
    closed_gates = []
    for gate_id in sorted(by_id):
        row = by_id[gate_id]
        compact = {
            "gate_id": gate_id,
            "status": row.get("status"),
            "requirement": row.get("requirement"),
            "measured": row.get("measured"),
            "evidence": row.get("evidence"),
            "note": row.get("note"),
        }
        (closed_gates if row.get("status") == "PASS" else open_gates).append(compact)
    ncrs = []
    for ncr_id, controlling_gate_ids in NCR_GATE_MAP.items():
        statuses = [str(by_id.get(gate_id, {}).get("status", "BLOCKED")) for gate_id in controlling_gate_ids]
        if statuses and all(status == "PASS" for status in statuses):
            formula_status = "CLOSED"
        elif "FAIL" in statuses:
            formula_status = "OPEN"
        else:
            formula_status = "BLOCKED"
        ncrs.append(
            {
                "ncr_id": ncr_id,
                "formula_status": formula_status,
                "controlling_gates": [
                    {"gate_id": gate_id, "status": status}
                    for gate_id, status in zip(controlling_gate_ids, statuses)
                ],
                "formula_basis": "CLOSED iff every controlling gate PASS; else OPEN if any FAIL; else BLOCKED",
            }
        )
    return {
        "closed_gates": closed_gates,
        "open_gates": open_gates,
        "ncrs": ncrs,
        "ncr_counts": {
            status: sum(row["formula_status"] == status for row in ncrs)
            for status in ("CLOSED", "OPEN", "BLOCKED")
        },
    }


def endpoint_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    result: dict[str, Any] = {}
    pair_fields = (
        "solid_count", "unordered_pair_count", "broadphase_candidate_count",
        "clear_pair_count", "unauthorized_positive_volume_pair_count",
        "documented_positive_volume_pair_count", "boolean_blocked_pair_count",
        "distance_blocked_pair_count", "near_noninterfering_candidate_pair_count",
        "exact_distance_measured_pair_count", "minimum_exact_noninterfering_clearance_mm",
        "intentional_fit_register_valid_record_count", "intentional_fit_register_error_count",
        "unused_intentional_fit_exception_ids",
    )
    step_fields = (
        "file_size_bytes", "sha256", "schema_record", "ap242_schema_detected", "product_count",
        "unnamed_product_count", "nauo_count", "unnamed_nauo_name_count",
        "millimetre_length_unit_detected",
        "manifold_solid_brep_count", "brep_with_voids_count", "advanced_face_count",
        "closed_shell_count", "faceted_or_tessellated_total",
    )
    for state in ("STOWED", "DEPLOYED"):
        pairs = evidence.endpoint_pairs[state]
        step = evidence.step_text[state]
        if not isinstance(pairs, dict) or not isinstance(step, dict):
            raise RuntimeError(f"invalid {state} endpoint evidence root")
        result[state] = {
            **{field: pairs.get(field) for field in pair_fields},
            "step": {field: step.get(field) for field in step_fields},
        }
    return result


def motion_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE":
        fields = (
            "execution_state", "source", "summary_artifact_available",
            "kinematics_artifact_available", "sample_count", "angle_increment_deg",
            "minimum_angle_deg", "maximum_angle_deg", "data_row_count",
            "line_count_including_header", "pair_rows_per_sample", "result_counts",
            "exact_common_status_counts", "exact_distance_status_counts",
            "nonempty_error_row_count", "positive_volume_pair_count",
            "unauthorized_positive_volume_pair_count",
            "documented_positive_volume_pair_count", "boolean_blocked_pair_count",
            "distance_blocked_pair_count", "intentional_fit_register_error_count",
            "used_intentional_fit_exception_ids", "intentional_fit_exception_use_counts",
            "unauthorized_unique_pair_count", "unauthorized_angle_degrees",
            "unauthorized_classification_observation_counts",
            "category_b_rigid_unique_pair_count",
            "category_b_rigid_observation_count",
            "nonrigid_involved_unique_pair_count",
            "nonrigid_involved_observation_count",
            "minimum_exact_noninterfering_clearance_mm", "track_validation_error_count",
            "maximum_closure_residual_abs_mm", "crosshead_travel_0_to_80_mm",
            "elapsed_seconds", "execution_topology",
        )
        return {
            **{field: evidence.motion.get(field) for field in fields},
            "motion_summary_status": "NOT_COMPUTED",
            "motion_kinematics_status": "NOT_COMPUTED",
            "last_audit_failure": LAST_AUDIT_FAILURE_PATH.as_posix(),
            "merged_motion_audit": dict(
                evidence.audit_failure.get("merged_motion_audit", {})
                if isinstance(evidence.audit_failure, dict) else {}
            ),
        }
    fields = (
        "sample_count", "angle_increment_deg", "required_scope_occurrence_count",
        "tracked_scope_occurrence_count", "active_dynamic_occurrence_count",
        "pair_row_count", "broadphase_candidate_count", "positive_volume_pair_count",
        "unauthorized_positive_volume_pair_count", "documented_positive_volume_pair_count",
        "boolean_blocked_pair_count", "distance_blocked_pair_count",
        "minimum_exact_noninterfering_clearance_mm", "intentional_fit_register_error_count",
        "unused_intentional_fit_exception_ids", "track_validation_error_count",
        "maximum_closure_residual_abs_mm", "crosshead_travel_0_to_80_mm",
        "elapsed_seconds", "execution_topology",
    )
    return {field: evidence.motion.get(field) for field in fields}


def hierarchy_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    result: dict[str, Any] = {}
    imported = evidence.reconciliation.get("imported_leaf_identity_audits", {})
    hierarchy_audits = evidence.reconciliation.get("hierarchy_audits", {})
    for state in ("STOWED", "DEPLOYED"):
        inventory = evidence.inventories[state]
        authored_hierarchy = inventory.get("assembly_hierarchy", {})
        step = evidence.step_text[state]
        imported_state = imported.get(state, {}) if isinstance(imported, dict) else {}
        audit_state = hierarchy_audits.get(state, {}) if isinstance(hierarchy_audits, dict) else {}
        result[state] = {
            "root_name": authored_hierarchy.get("root_name"),
            "top_level_assembly_names": authored_hierarchy.get("top_level_assembly_names", []),
            "assembly_paths": authored_hierarchy.get("assembly_paths", []),
            "assembly_path_count": len(authored_hierarchy.get("assembly_paths", [])),
            "authored_part_definition_count": len(inventory.get("parts", [])),
            "authored_occurrence_count": len(inventory.get("occurrences", [])),
            "authored_leaf_occurrence_count": authored_hierarchy.get("leaf_occurrence_count"),
            "imported_leaf_occurrence_count": imported_state.get("leaf_row_count"),
            "step_product_count": step.get("product_count"),
            "step_nauo_count": step.get("nauo_count"),
            "hierarchy_audit_accepted": audit_state.get("accepted"),
            "hierarchy_issue_count": audit_state.get("issue_count"),
            "missing_assembly_paths": audit_state.get("missing_assembly_paths", []),
            "unexpected_assembly_paths": audit_state.get("unexpected_assembly_paths", []),
            "millimetre_length_unit_detected": step.get("millimetre_length_unit_detected"),
            "occurrence_transform_rows": len(inventory.get("occurrences", [])),
            "identity_transform_occurrence_count": sum(
                occurrence.get("identity_transform") is True
                for occurrence in inventory.get("occurrences", [])
                if isinstance(occurrence, dict)
            ),
            "classification_counts": dict(sorted(Counter(
                str(occurrence.get("classification", "UNKNOWN"))
                for occurrence in inventory.get("occurrences", [])
                if isinstance(occurrence, dict)
            ).items())),
            "occurrence_transforms": [
                {
                    "occurrence_id": occurrence.get("occurrence_id"),
                    "classification": occurrence.get("classification"),
                    "identity_transform": occurrence.get("identity_transform"),
                    "transform_matrix_3x4": occurrence.get("transform_matrix_3x4"),
                }
                for occurrence in inventory.get("occurrences", [])
                if isinstance(occurrence, dict)
            ],
        }
    result["occurrence_bom_reconciliation"] = {
        "row_count": evidence.reconciliation.get("row_count"),
        "issue_count": evidence.reconciliation.get("issue_count"),
        "stowed_occurrence_count": evidence.reconciliation.get("stowed_occurrence_count"),
        "deployed_occurrence_count": evidence.reconciliation.get("deployed_occurrence_count"),
    }
    transform_gate = next(
        (
            row for row in evidence.gates.get("gates", [])
            if isinstance(row, dict) and row.get("gate_id") == "OCCURRENCE-TRANSFORMS"
        ),
        {},
    )
    measured = transform_gate.get("measured", {}) if isinstance(transform_gate, dict) else {}
    result["occurrence_transform_gate"] = {
        "status": (
            "NOT_COMPUTED" if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE"
            else transform_gate.get("status") if isinstance(transform_gate, dict) else None
        ),
        "unmapped_leaf_occurrences": measured.get("unmapped_leaf_occurrences") if isinstance(measured, dict) else None,
        "identity_occurrences_without_justification": measured.get("identity_occurrences_without_justification") if isinstance(measured, dict) else None,
        "maximum_transform_matrix_element_error": measured.get("maximum_transform_matrix_element_error") if isinstance(measured, dict) else None,
        "transform_mismatches": measured.get("transform_mismatches") if isinstance(measured, dict) else None,
    }
    return result


def state_parity_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    rows = evidence.state_parity_rows
    statuses = Counter(str(row.get("status", "")) for row in rows)
    classifications = Counter(str(row.get("classification", "")) for row in rows)
    unresolved_fields = (
        "occurrence_id", "classification", "present_stowed", "present_deployed",
        "same_part_number", "exact_local_brep_match", "fingerprint_error",
        "flexible_state_geometry_exception", "status",
    )
    unresolved = [
        {field: row.get(field) for field in unresolved_fields}
        for row in rows if row.get("status") != "PASS"
    ]
    return {
        "source": "work/final_analysis/validation/state_parity.csv",
        "row_count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "classification_counts": dict(sorted(classifications.items())),
        "flexible_exception_row_count": sum(
            str(row.get("flexible_state_geometry_exception", "")).strip().upper() == "TRUE"
            for row in rows
        ),
        "unresolved_row_count": len(unresolved),
        "unresolved_rows": unresolved,
        "rows": rows,
    }


def connectivity_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    count_fields = (
        "occurrence_count", "connection_count", "attachment_endpoint_occurrence_count",
        "attachment_coverage_required_occurrence_count",
        "uncovered_attachment_endpoint_occurrence_count", "invalid_attachment_record_count",
        "blank_attachment_id_count", "duplicate_attachment_id_count", "floating_rigid_count",
        "dangling_connection_count", "self_connection_count", "generic_or_blanket_evidence_count",
        "geometric_or_fastener_unsupported_connection_count", "route_count",
        "invalid_route_record_count", "blank_route_id_count", "duplicate_route_id_count",
        "failed_route_count", "graph_component_count_including_flexible_and_consumed",
    )
    result: dict[str, Any] = {}
    for state in ("STOWED", "DEPLOYED"):
        source = evidence.connectivity[state]
        attachments = source.get("attachment_results", [])
        routes = source.get("route_results", [])
        result[state] = {
            **{field: source.get(field) for field in count_fields},
            "continuous_recovery_load_path_found": source.get("continuous_recovery_load_path_found"),
            "body_hardpoint_to_harness_terminal_path": source.get("body_hardpoint_to_harness_terminal_path"),
            "attachment_result_count": len(attachments),
            "direct_distance_status_counts": dict(sorted(Counter(
                str(row.get("direct_distance_status", ""))
                for row in attachments if isinstance(row, dict)
            ).items())),
            "route_status_counts": dict(sorted(Counter(
                str(row.get("status", ""))
                for row in routes if isinstance(row, dict)
            ).items())),
        }
    return result


def definition_of_done_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for state in ("STOWED", "DEPLOYED"):
        source = evidence.definition_of_done[state]
        sections = source.get("sections", {})
        result[state] = {
            "requirements_object_present": source.get("requirements_object_present"),
            "failure_count": source.get("failure_count"),
            "blocked_count": source.get("blocked_count"),
            "failures": source.get("failures", []),
            "blocked": source.get("blocked", []),
            "section_count": len(sections) if isinstance(sections, dict) else None,
            "sections": sections,
        }
    return result


def motion_variant_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for state in ("STOWED", "DEPLOYED"):
        tracks = [row for row in evidence.inventories[state].get("motion_tracks", []) if isinstance(row, dict)]
        variant_records = []
        for track in tracks:
            if track.get("mode") != "KEYFRAMED_EXACT_BREP_VARIANTS":
                continue
            samples = [row for row in track.get("samples", []) if isinstance(row, dict)]
            angles = [row.get("angle_deg") for row in samples if isinstance(row.get("angle_deg"), (int, float))]
            variants = Counter(str(row.get("endpoint_variant", "")) for row in samples)
            covers = sorted(set(angles)) == list(range(81))
            variant_records.append({
                "occurrence_id": track.get("occurrence_id"),
                "mode": track.get("mode"),
                "process_basis": track.get("process_basis"),
                "sample_count": len(samples),
                "minimum_angle_deg": min(angles) if angles else None,
                "maximum_angle_deg": max(angles) if angles else None,
                "endpoint_variant_counts": dict(sorted(variants.items())),
                "covers_every_integer_angle_0_to_80": covers,
                "status": "PASS" if len(samples) == 81 and covers and "" not in variants else "UNRESOLVED",
            })
        result[state] = {
            "track_count": len(tracks),
            "mode_counts": dict(sorted(Counter(str(row.get("mode", "")) for row in tracks).items())),
            "exact_brep_variant_track_count": len(variant_records),
            "exact_brep_variant_tracks": variant_records,
            "exact_brep_variant_status": (
                "PASS" if variant_records and all(row["status"] == "PASS" for row in variant_records)
                else "UNRESOLVED"
            ),
        }
    return result


def dimensional_metrics(evidence: EvidenceBundle) -> dict[str, Any]:
    dimensions = evidence.dimensions
    stowed = dimensions.get("stowed", {})
    deployed = dimensions.get("deployed", {})
    return {
        "arm_module_stowed_od_mm": dimensions.get("arm_module_stowed_xy_span_mm"),
        "arm_module_stowed_bbox_mm": dimensions.get("arm_module_stowed_bbox_mm"),
        "normal_body_oml_xy_spans_mm": dimensions.get("normal_body_oml_xy_spans_mm"),
        "stowed_rigid_length_mm": stowed.get("rigid_length_mm") if isinstance(stowed, dict) else None,
        "deployed_rigid_length_mm": deployed.get("rigid_length_mm") if isinstance(deployed, dict) else None,
        "stowed_all_geometry_length_mm": stowed.get("all_geometry_length_mm") if isinstance(stowed, dict) else None,
        "deployed_all_geometry_length_mm": deployed.get("all_geometry_length_mm") if isinstance(deployed, dict) else None,
        "crosshead_travel_reimported_mm": dimensions.get("crosshead_travel_from_reimported_transforms_mm"),
        "crosshead_travel_independent_mm": dimensions.get("crosshead_travel_from_independent_closure_equation_mm"),
        "system_mass_kg": dimensions.get("mass_rollup_from_authoring_inventory_kg"),
        "mass_reserve_kg": dimensions.get("mass_reserve_using_resolved_mass_only_kg"),
        "mass_unresolved_occurrence_ids": dimensions.get("mass_unresolved_occurrence_ids", []),
        "mass_invalid_occurrence_ids": dimensions.get("mass_invalid_occurrence_ids", []),
    }


def contact_and_defect_state(evidence: EvidenceBundle) -> dict[str, Any]:
    remaining_pairs: list[dict[str, Any]] = []
    authorized_pairs: list[dict[str, Any]] = []
    category_b_rows: list[dict[str, Any]] = []
    nonrigid_rows: list[dict[str, Any]] = []
    validator_defects: list[dict[str, Any]] = []
    authorized_ids: dict[str, list[str]] = {}

    def capture_positive(row: object, scope: str) -> None:
        compact = compact_pair(row)
        if isinstance(row, dict) and row.get("documented_positive_volume_exception") is True:
            authorized_pairs.append(compact)
            return
        remaining_pairs.append(compact)
        if (
            isinstance(row, dict)
            and str(row.get("classification_a", "")).upper() in RIGID_CLASSIFICATIONS
            and str(row.get("classification_b", "")).upper() in RIGID_CLASSIFICATIONS
        ):
            category_b_rows.append({
                "scope": scope,
                "condition": "unauthorized rigid positive-common-volume pair",
                "row": compact,
            })

    for state in ("STOWED", "DEPLOYED"):
        endpoint = evidence.endpoint_pairs[state]
        for row in endpoint.get("positive_rows", []):
            capture_positive(row, state)
        authorized_ids[state] = sorted(
            str(value) for value in endpoint.get("used_intentional_fit_exception_ids", [])
        )
        for row in endpoint.get("boolean_or_distance_errors", []):
            item = {"scope": state, "condition": "blocked exact Boolean/distance", "row": compact_pair(row)}
            validator_defects.append(item)
        for error in endpoint.get("intentional_fit_register_errors", []):
            item = {"scope": state, "condition": "intentional-fit register error", "detail": error}
            validator_defects.append(item)
        for field in ("boolean_blocked_pair_count", "distance_blocked_pair_count"):
            count = endpoint.get(field, 0)
            if count:
                validator_defects.append({"scope": state, "condition": field, "count": count})

    endpoint_authorized_count = len(authorized_pairs)
    if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE":
        for row in evidence.motion.get("unauthorized_unique_pairs", []):
            if not isinstance(row, dict):
                continue
            aggregate = dict(row)
            remaining_pairs.append(aggregate)
            if (
                str(row.get("classification_a", "")).upper() in RIGID_CLASSIFICATIONS
                and str(row.get("classification_b", "")).upper() in RIGID_CLASSIFICATIONS
            ):
                category_b_rows.append({
                    "scope": "MOTION",
                    "condition": "unauthorized rigid positive-common-volume pair",
                    "row": aggregate,
                })
            else:
                nonrigid_rows.append({
                    "scope": "MOTION",
                    "condition": "unauthorized positive-common-volume pair involving nonrigid occurrence",
                    "row": aggregate,
                })
    else:
        for row in evidence.motion.get("positive_rows", []):
            capture_positive(row, "MOTION")
    for row in evidence.motion.get("blocked_rows", []):
        item = {"scope": "MOTION", "condition": "blocked exact Boolean/distance", "row": compact_pair(row)}
        validator_defects.append(item)
    for error in evidence.motion.get("intentional_fit_register_errors", []):
        item = {"scope": "MOTION", "condition": "intentional-fit register error", "detail": error}
        validator_defects.append(item)
    for error in evidence.motion.get("track_validation_errors", []):
        validator_defects.append({"scope": "MOTION", "condition": "track validation error", "detail": error})
    for missing in evidence.motion.get("scope_missing", []):
        validator_defects.append({"scope": "MOTION", "condition": "scope missing", "detail": missing})
    for field in (
        "boolean_blocked_pair_count", "distance_blocked_pair_count",
        "track_validation_error_count", "intentional_fit_register_error_count",
    ):
        count = evidence.motion.get(field, 0)
        if count:
            validator_defects.append({"scope": "MOTION", "condition": field, "count": count})
    validator_limit = evidence.validation_summary.get("validator_limit")
    if validator_limit:
        validator_defects.append(
            {"scope": "VALIDATOR", "condition": "declared validator limit", "detail": validator_limit}
        )
    if evidence.validation_mode == "TERMINAL_AUDIT_FAILURE":
        validator_defects.append({
            "scope": "VALIDATOR",
            "condition": "terminal post-merge motion-kinematics schema failure",
            "execution_state": "TERMINAL_AUDIT_FAILURE",
            "exception_type": evidence.audit_failure.get("exception_type")
            if isinstance(evidence.audit_failure, dict) else None,
            "exception_message": evidence.audit_failure.get("exception_message")
            if isinstance(evidence.audit_failure, dict) else None,
            "failure_stage": evidence.audit_failure.get("failure_stage")
            if isinstance(evidence.audit_failure, dict) else None,
            "exit_code": evidence.audit_failure.get("exit_code")
            if isinstance(evidence.audit_failure, dict) else None,
            "missing_validation_files": list(evidence.missing_validation_files),
            "acceptance_gate_status": "NOT_COMPUTED",
            "release_authorized": False,
        })
    for issue in evidence.reconciliation.get("issues", []):
        validator_defects.append(
            {"scope": "OCCURRENCE_BOM", "condition": "reconciliation issue", "detail": issue}
        )
    for state in ("STOWED", "DEPLOYED"):
        invalid_count = evidence.dimensions.get(state.lower(), {}).get("invalid_solid_count", 0)
        if invalid_count:
            validator_defects.append(
                {"scope": state, "condition": "invalid exact-BREP solid", "count": invalid_count}
            )

    parity = state_parity_metrics(evidence)
    for row in parity["unresolved_rows"]:
        validator_defects.append({"scope": "STATE_PARITY", "condition": "unresolved parity row", "row": row})

    connectivity = connectivity_metrics(evidence)
    connectivity_defect_fields = (
        "uncovered_attachment_endpoint_occurrence_count", "invalid_attachment_record_count",
        "blank_attachment_id_count", "duplicate_attachment_id_count", "floating_rigid_count",
        "dangling_connection_count", "self_connection_count", "generic_or_blanket_evidence_count",
        "geometric_or_fastener_unsupported_connection_count", "invalid_route_record_count",
        "blank_route_id_count", "duplicate_route_id_count", "failed_route_count",
    )
    for state in ("STOWED", "DEPLOYED"):
        row = connectivity[state]
        for field in connectivity_defect_fields:
            if row.get(field):
                validator_defects.append({"scope": state, "condition": field, "count": row[field]})
        if row.get("continuous_recovery_load_path_found") is not True:
            validator_defects.append({"scope": state, "condition": "recovery load path not proven"})
        for status, count in row.get("direct_distance_status_counts", {}).items():
            if status != "DONE" and count:
                validator_defects.append({
                    "scope": state, "condition": "attachment direct-distance unresolved",
                    "status": status, "count": count,
                })
        for status, count in row.get("route_status_counts", {}).items():
            if status != "PASS" and count:
                validator_defects.append({
                    "scope": state, "condition": "route audit unresolved",
                    "status": status, "count": count,
                })

    dod = definition_of_done_metrics(evidence)
    for state in ("STOWED", "DEPLOYED"):
        if dod[state].get("failure_count"):
            validator_defects.append({
                "scope": state, "condition": "Definition-of-Done failures",
                "count": dod[state]["failure_count"], "detail": dod[state].get("failures", []),
            })
        if dod[state].get("blocked_count"):
            validator_defects.append({
                "scope": state, "condition": "Definition-of-Done blocked checks",
                "count": dod[state]["blocked_count"], "detail": dod[state].get("blocked", []),
            })

    transform = hierarchy_metrics(evidence)["occurrence_transform_gate"]
    if transform.get("status") != "PASS":
        validator_defects.append({
            "scope": "OCCURRENCE_TRANSFORMS",
            "condition": "occurrence-transform gate unresolved", "detail": transform,
        })
    variants = motion_variant_metrics(evidence)
    for state in ("STOWED", "DEPLOYED"):
        if variants[state].get("exact_brep_variant_status") != "PASS":
            validator_defects.append({
                "scope": state,
                "condition": "exact-BREP motion variant tracks unresolved",
                "detail": variants[state],
            })
    if variants["STOWED"] != variants["DEPLOYED"]:
        validator_defects.append({
            "scope": "MOTION",
            "condition": "endpoint motion-track/variant inventories disagree",
            "detail": variants,
        })

    return {
        "remaining_positive_pairs": remaining_pairs,
        "authorized_contacts": {
            "positive_pair_records": authorized_pairs,
            "total_positive_pair_record_count": (
                endpoint_authorized_count
                + int(evidence.motion.get("documented_positive_volume_pair_count") or 0)
            ),
            "endpoint_pair_record_count": endpoint_authorized_count,
            "motion_pair_record_count": int(
                evidence.motion.get("documented_positive_volume_pair_count") or 0
            ),
            "endpoint_used_exception_ids": authorized_ids,
            "motion_documented_positive_pair_count": evidence.motion.get(
                "documented_positive_volume_pair_count"
            ),
            "motion_used_exception_ids": sorted(
                str(value) for value in evidence.motion.get("used_intentional_fit_exception_ids", [])
            ),
        },
        "category_b_invalids": {
            "definition": (
                "Handoff Category-B invalids are only unauthorized positive-common-volume "
                "pairs for which both occurrence classifications are rigid (FIXED or MOVING). "
                "Blocked audits, track/fit/parity defects, and invalid solids are validator/audit "
                "defects, never Category-B substitutes."
            ),
            "count": len(category_b_rows),
            "observation_count": sum(
                int(item.get("row", {}).get("observation_count", 1))
                for item in category_b_rows
            ),
            "records": category_b_rows,
        },
        "invalid_interferences": {
            "definition": (
                "Unauthorized positive-common-volume endpoint or motion pairs "
                "between two rigid FIXED/MOVING occurrences"
            ),
            "count": len(category_b_rows),
            "observation_count": sum(
                int(item.get("row", {}).get("observation_count", 1))
                for item in category_b_rows
            ),
            "records": category_b_rows,
        },
        "unresolved_nonrigid_positive_pairs": {
            "definition": (
                "Unauthorized positive-common-volume motion pairs involving at least one "
                "nonrigid occurrence; retained separately and not counted as Category-B rigid invalids"
            ),
            "count": len(nonrigid_rows),
            "observation_count": sum(
                int(item.get("row", {}).get("observation_count", 1))
                for item in nonrigid_rows
            ),
            "records": nonrigid_rows,
        },
        "validator_defects": {
            "count": len(validator_defects),
            "records": validator_defects,
        },
    }


def derived_evidence_state(evidence: EvidenceBundle) -> dict[str, Any]:
    return {
        "endpoint_metrics": endpoint_metrics(evidence),
        "motion_metrics": motion_metrics(evidence),
        "hierarchy": hierarchy_metrics(evidence),
        "dimensions_mass_reserve": dimensional_metrics(evidence),
        "state_parity": state_parity_metrics(evidence),
        "connectivity_attachment_route": connectivity_metrics(evidence),
        "definition_of_done": definition_of_done_metrics(evidence),
        "motion_variants": motion_variant_metrics(evidence),
        "gates_and_ncrs": gate_and_ncr_state(evidence),
        **contact_and_defect_state(evidence),
    }


def json_block(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)


def handoff_markdown(
    evidence: EvidenceBundle, captured_at: str, reproducibility_epoch: int,
) -> str:
    gates = evidence.gates
    counts = gates.get("gate_counts", {})
    derived = derived_evidence_state(evidence)
    gate_state = derived["gates_and_ncrs"]
    validator_cmd = validator_command(evidence)
    closed_gate_ids = [row["gate_id"] for row in gate_state["closed_gates"]]
    open_gate_rows = [dict(row) for row in gate_state["open_gates"]]
    ncr_rows = [
        {
            "ncr_id": row["ncr_id"],
            "formula_status": row["formula_status"],
            "handoff_disposition": row.get("handoff_disposition"),
            "controlling_gates": row["controlling_gates"],
            "formula_basis": row.get("formula_basis"),
        }
        for row in gate_state["ncrs"]
    ]
    last = evidence.last_execution_record
    last_command = last["last_command"]
    last_modifying = last["last_successful_modifying_command"]
    last_audit = last["last_successful_audit_command"]
    terminal = evidence.validation_mode == "TERMINAL_AUDIT_FAILURE"
    phase = TERMINAL_PHASE if terminal else COMPLETE_PHASE
    checkpoint = TERMINAL_CHECKPOINT if terminal else COMPLETE_CHECKPOINT
    if terminal:
        failure = evidence.audit_failure or {}
        validator_state_markdown = f"""## Terminal audit failure (incomplete validator evidence)

- Execution state: **TERMINAL_AUDIT_FAILURE**.
- Validator command exited `1` during `POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK`.
- Exact exception: `KeyError` with message **`'angle_deg'`**.
- All **81** exact-motion samples (integer angles 0° through 80°) completed and
  were merged into `work/final_analysis/validation/motion_full_mechanism_audit.csv.gz`.
- Merged evidence: `{failure.get('merged_motion_audit')}`.
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
{json_block(list(evidence.present_validation_files))}
```

- Exact absent/uncomputed outputs (5):

```json
{json_block(list(evidence.missing_validation_files))}
```

`motion_kinematics_1deg.csv`, `motion_audit_summary.json`, `gate_results.json`,
`validation_summary.json`, and `validation_manifest.json` do not exist in this
terminal state. No stale substitute is used. Acceptance gates were **NOT_COMPUTED**;
all 31 are preserved with handoff disposition OPEN. NCR formulas were
**NOT_COMPUTED**; NCR-01 through NCR-08 are preserved with handoff disposition
OPEN. The package is **NOT RELEASED**, and release packaging is not authorized.

### Acceptance gates (not computed; handoff-open)

```json
{json_block(open_gate_rows)}
```

### NCR-01 through NCR-08 (not computed; handoff-open)

```json
{json_block(ncr_rows)}
```
"""
    else:
        validator_state_markdown = f"""## Preserved validator state

- Last successful validator status from `validation_summary.json`: `{evidence.validation_summary.get('validation_status')}`
- Computed release status: `{gates.get('computed_release_status', 'UNKNOWN')}`
- Required package label: `{gates.get('package_required_label', 'UNKNOWN')}`
- Gate counts: PASS `{counts.get('PASS', 0)}`, FAIL `{counts.get('FAIL', 0)}`, BLOCKED `{counts.get('BLOCKED', 0)}`
- Validator elapsed seconds: `{evidence.validation_summary.get('elapsed_seconds')}`
- Exact gate evidence: `work/final_analysis/validation/gate_results.json`
- Validation provenance: `work/final_analysis/validation/validation_manifest.json`

### Closed gates

```json
{json_block(closed_gate_ids)}
```

### Open gates

```json
{json_block(open_gate_rows)}
```

### NCR-01 through NCR-08 formula statuses

These statuses reproduce the exact workbook rule: CLOSED iff every controlling
gate is PASS; otherwise OPEN if any controlling gate is FAIL; otherwise BLOCKED.

```json
{json_block(ncr_rows)}
```
"""
    return f"""# STINGRAY I5-S DF8 Codex handoff checkpoint

Actual capture wall timestamp: `{captured_at}`.
Reproducibility timestamp epoch: `{reproducibility_epoch}` (`{iso_time(reproducibility_epoch)}`).

This is a preservation and safe-handoff checkpoint. It does not authorize a new
correction cycle, a rebuild, workbook promotion, or final release packaging.
The bounded corrective sequence was superseded operationally by the latest
**SAFE CODEX HANDOFF CHECKPOINT** directive. The latest safe-termination
directive governs runtime only; it does not rewrite the controlling engineering
commission records.

- Current execution phase: {phase}.
- Latest completed checkpoint: {checkpoint}.

## Controlling source records

- `commission/ORIGINAL_COMMISSION_20260821-031917.md` is the original controlling commission.
- `commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md` is the R1 rejection and R2 corrective direction.
- `commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md` is the latest safe-termination directive; it governs runtime only.
- `commission/PROVENANCE.json` binds the safe staged names to the uploaded filenames and hashes.

The historical files under `work/r2_metadata/` are retained as evidence only.
Their obsolete WIP/Creo dispositions are not controlling.

## Governance at handoff

- Creo environment disposition: **{CREO_DISPOSITION}**
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

- Last command (exit `{last_command['exit_code']}`):

```bash
{last_command['command']}
```

- Last successful modifying command (exit `{last_modifying['exit_code']}`):

```bash
{last_modifying['command']}
```

- Last successful audit command (process exit `{last_audit['exit_code']}`; engineering status is the
  separate validator status shown below):

```bash
{last_audit['command']}
```

The last successful modifying command's hash-bound output set is:

- `work/final_release/{FINAL_STOWED}`
- `work/final_release/{FINAL_DEPLOYED}`
- `work/final_analysis/authoring_inventory_stowed.json`
- `work/final_analysis/authoring_inventory_deployed.json`
- `work/final_analysis/authoring_manifest.json`

{validator_state_markdown}

## Latest endpoint and motion metrics

```json
{json_block({'endpoints': derived['endpoint_metrics'], 'motion': derived['motion_metrics'], 'motion_variants': derived['motion_variants']})}
```

## Hierarchy, products, occurrences, envelope, length, mass, and reserve

```json
{json_block({'hierarchy': derived['hierarchy'], 'dimensions_mass_reserve': derived['dimensions_mass_reserve']})}
```

## State parity, connectivity, attachment, routes, and Definition of Done

```json
{json_block({'state_parity': derived['state_parity'], 'connectivity_attachment_route': derived['connectivity_attachment_route'], 'definition_of_done': derived['definition_of_done']})}
```

## Remaining pairs, authorized contacts, invalids, and validator defects

- Remaining unauthorized positive pairs: `{len(derived['remaining_positive_pairs'])}`
- Authorized endpoint contact records: `{derived['authorized_contacts']['endpoint_pair_record_count']}`
- Motion documented positive-pair observations: `{derived['authorized_contacts']['motion_documented_positive_pair_count']}`
- Category-B unauthorized rigid positive-volume pairs: `{derived['category_b_invalids']['count']}`
- Unresolved nonrigid-involved positive-volume pairs: `{derived['unresolved_nonrigid_positive_pairs']['count']}`
- Validator-defect records: `{derived['validator_defects']['count']}`

```json
{json_block({'remaining_positive_pairs': derived['remaining_positive_pairs'], 'authorized_contacts': derived['authorized_contacts'], 'category_b_invalids': derived['category_b_invalids'], 'unresolved_nonrigid_positive_pairs': derived['unresolved_nonrigid_positive_pairs'], 'validator_defects': derived['validator_defects']})}
```

## Exact engineering commands (reference only; not authorized at handoff)

Both endpoint rebuild and AP242 export (the authoring entry point always builds
STOWED then DEPLOYED in one process):

```bash
{COMMANDS['rebuild_both_endpoints_and_export_ap242']}
```

STOWED exact-solid authoring audit:

```bash
{COMMANDS['stowed_authoring_audit']}
```

DEPLOYED exact-solid authoring audit:

```bash
{COMMANDS['deployed_authoring_audit']}
```

Clean-process AP242 reimport, endpoint audits, and full 0°–80°/1° motion audit:

```bash
{validator_cmd}
```

Workbook generation:

```bash
{COMMANDS['workbook']}
```

Final three-member ZIP packaging:

```bash
{COMMANDS['final_zip']}
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
"""


def resume_commands_markdown(evidence: EvidenceBundle) -> str:
    validator_cmd = validator_command(evidence)
    return f"""# DF8 resumption commands

Run commands from the extracted checkpoint root. All checkpoint paths below are
relative. The safe default is inspection only.

## Authorized integrity inspection

```bash
{COMMANDS['verify_checkpoint']}
python3 - <<'PY'
import json
state = json.load(open('CURRENT_STATE.json', encoding='utf-8'))
print(json.dumps(state['validation'], indent=2))
PY
```

## Non-modifying authoring-output integrity

```bash
{COMMANDS['authoring_output_integrity']}
```

## Non-modifying Python AST source parse

This parses source text without importing or executing authoring modules.

```bash
{COMMANDS['python_ast_source_parse']}
```

Read the controlling records before any engineering action:

```bash
sed -n '1,240p' commission/ORIGINAL_COMMISSION_20260821-031917.md
sed -n '1,260p' commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md
sed -n '1,260p' commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md
```

Creo is informational N/A exactly as follows:

`{CREO_DISPOSITION}`

OCP/XCAF clean-process AP242 reimport is the controlling neutral-CAD gate.
No new correction cycle or final release packaging is authorized by this
handoff.

`work/scripts` is historical/non-runnable without omitted original input trees.
The authoritative build uses the full copied `work/input/wp02` tree, including
the exact GS-19 and HBD-15 live vendor-source files required by `build_r2.py`.
Copied absolute paths inside historical evidence are provenance-only, and no
No /tmp state is required after the sweep.

## Environment restoration (reference only; requires renewed authorization)

The virtual environment and Node module tree are intentionally excluded. The
captured pins are under `environment/`.

```bash
python3.12 -m venv work/cadenv
work/cadenv/bin/python3 -m pip install \
  --requirement environment/PYTHON_REQUIREMENTS_FULLY_PINNED.txt
test -n "${{CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}}"
mkdir -p work/spreadsheet_runtime
ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
```

## Exact command catalog (reference only; not authorized at handoff)

STOWED rebuild and DEPLOYED rebuild are intentionally one command because the
state-invariant exact-BREP cache requires ordered same-process authoring. This
command also performs both final AP242 exports:

```bash
{COMMANDS['rebuild_both_endpoints_and_export_ap242']}
```

STOWED audit:

```bash
{COMMANDS['stowed_authoring_audit']}
```

DEPLOYED audit:

```bash
{COMMANDS['deployed_authoring_audit']}
```

Clean-process AP242 reimport, both endpoint audits, and exact 0°–80°/1°
motion audit:

```bash
{validator_cmd}
```

Workbook generation:

```bash
{COMMANDS['workbook']}
```

Final ZIP generation:

```bash
{COMMANDS['final_zip']}
```

## Mutating engineering sequence (reference only; not authorized at handoff)

Reproduce the latest STOWED exact-solid authoring audit:

```bash
{COMMANDS['stowed_authoring_audit']}
```

Reproduce the latest DEPLOYED exact-solid authoring audit:

```bash
{COMMANDS['deployed_authoring_audit']}
```

Reproduce the curated attachment-distance scope audit:

```bash
{COMMANDS['attachment_scope_audit']}
```

Continue the bounded sequence only if new controlling authority explicitly
reopens it. The exact rebuild/AP242-export command is:

```bash
export LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONHASHSEED=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export XDG_CACHE_HOME="${{TMPDIR:-.tmp}}/df8-r2-cache"
mkdir -p "$XDG_CACHE_HOME"

{COMMANDS['rebuild_both_endpoints_and_export_ap242']}

validation=work/final_analysis/validation
if test -e "$validation"; then
  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  mv -- "$validation" "${{validation}}.previous.${{stamp}}"
fi
mkdir -p "$validation"
{validator_cmd}

jq -e '.computed_release_status=="PASS" and
  .package_required_label=="FINAL — RELEASED" and
  .gate_counts.PASS==31 and .gate_counts.FAIL==0 and
  .gate_counts.BLOCKED==0 and all(.gates[]; .status=="PASS")' \
  "$validation/gate_results.json"

{COMMANDS['workbook']}

{COMMANDS['final_zip']}
```

Do not use the stale candidate instructions in `work/r2_metadata/` as release
authority. Do not pass `--skip-motion` for release evidence. The validator may
exit zero with failed or blocked gates, so the explicit gate-result check is
mandatory whenever a future controlling instruction authorizes validation.
"""


def commission_provenance(stage: Path, epoch: int) -> Path:
    rows = []
    for source_name, destination, role in COMMISSION_SOURCES:
        staged = stage / destination
        rows.append(
            {
                "role": role,
                "source_kind": "uploaded controlling record" if source_name.parts[0] == "upload" else "workspace runtime directive",
                "uploaded_filename": source_name.name,
                "workspace_source": source_name.as_posix(),
                "staged_path": destination.as_posix(),
                "size_bytes": staged.stat().st_size,
                "sha256": sha256_file(staged),
                "mtime_utc": iso_time(int(staged.stat().st_mtime)),
            }
        )
    path = Path("commission/PROVENANCE.json")
    generated_write(
        stage / path,
        json.dumps({"schema": "DF8_HANDOFF_COMMISSION_PROVENANCE_V1", "records": rows}, indent=2) + "\n",
        epoch,
    )
    return path


def current_state_payload(
    stage: Path,
    evidence: EvidenceBundle,
    preserved: list[Path],
    candidate_outputs: list[Path],
    candidate_temps: list[Path],
    dependencies: dict[str, Any],
    captured_at: str,
    reproducibility_epoch: int,
    entries: list[SourceEntry],
) -> dict[str, Any]:
    authoring = evidence.authoring
    gates = evidence.gates
    gate_rows = gates.get("gates", [])
    derived = derived_evidence_state(evidence)
    gate_state = derived["gates_and_ncrs"]
    last_execution = evidence.last_execution_record
    terminal = evidence.validation_mode == "TERMINAL_AUDIT_FAILURE"
    phase = TERMINAL_PHASE if terminal else COMPLETE_PHASE
    checkpoint = TERMINAL_CHECKPOINT if terminal else COMPLETE_CHECKPOINT
    last_modified_files = []
    for name in last_execution["last_modified_files"]:
        relative = Path(PurePosixPath(name))
        path = stage / relative
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"observed last-modified file is absent/non-regular in stage: {name}")
        last_modified_files.append(staged_file_record(stage, relative))
    recent_source_files = sorted(
        (entry for entry in entries if entry.kind == "file"),
        key=lambda entry: (-entry.mtime_ns, entry.destination.as_posix()),
    )[:25]
    recent_file_records = [
        {
            "path": entry.destination.as_posix(),
            "source_path": relative_text(entry.source),
            "mtime_ns": entry.mtime_ns,
            "mtime_utc": iso_time(entry.mtime_ns // 1_000_000_000),
            "size_bytes": entry.size,
            "sha256": entry.digest,
        }
        for entry in recent_source_files
    ]
    final_exact_zip = Path(
        "outputs/6f4e7892e9f1/STINGRAY_I5S_DF8_FINAL_EXACT_AP242_CAD.zip"
    )
    workbook_path = FINAL_RELEASE / FINAL_WORKBOOK
    workbook_manifest = FINAL_ANALYSIS / "workbook_build_manifest.json"
    validator_status = (
        "TERMINAL_AUDIT_FAILURE" if terminal
        else evidence.validation_summary.get("validation_status")
    )
    computed_release_status = (
        "NOT_RELEASED_VALIDATOR_FAILURE" if terminal
        else gates.get("computed_release_status")
    )
    required_package_label = (
        "INCOMPLETE TERMINAL AUDIT — NOT RELEASED" if terminal
        else gates.get("package_required_label")
    )
    final_artifact_status = {
        "validator_status": validator_status,
        "acceptance_gate_status": "NOT_COMPUTED" if terminal else "COMPUTED",
        "computed_release_status": computed_release_status,
        "package_required_label": required_package_label,
        "release_authorized": False if terminal else gates.get("computed_release_status") == "PASS",
        "final_release_packaging_authorized": False,
        "stowed_master": staged_file_record(stage, FINAL_RELEASE / FINAL_STOWED),
        "deployed_master": staged_file_record(stage, FINAL_RELEASE / FINAL_DEPLOYED),
        "workbook": (
            {"present": True, **staged_file_record(stage, workbook_path)}
            if (stage / workbook_path).is_file()
            else {"present": False, "path": workbook_path.as_posix()}
        ),
        "workbook_build_manifest": (
            {"present": True, **staged_file_record(stage, workbook_manifest)}
            if (stage / workbook_manifest).is_file()
            else {"present": False, "path": workbook_manifest.as_posix()}
        ),
        "final_three_member_zip": (
            {"present": True, **staged_file_record(stage, final_exact_zip), "handoff_verification": "not performed"}
            if (stage / final_exact_zip).is_file()
            else {"present": False, "path": final_exact_zip.as_posix()}
        ),
        "handoff_zip": {
            "path": ARCHIVE_NAME,
            "status_at_CURRENT_STATE_generation": "PENDING_ATOMIC_PUBLICATION",
        },
    }
    fragile_operations = [
        "build_r2.py overwrites final STEP/inventory/manifest files and rewrites NAUO text non-atomically",
        "STOWED and DEPLOYED must rebuild in one process because state-invariant BREP definitions share a cache",
        "validation output must be fresh because every top-level evidence file enters the manifest",
        "full motion launches 81 spawn tasks and each worker clean-reimports both endpoint masters",
        "validate_r2.py can exit zero while gates are FAIL or BLOCKED; gate_results.json controls disposition",
        "per-solid and occurrence audits require JSON inspection in addition to process exit status",
        "workbook source must be recopied to spreadsheet_runtime after every edit",
        "package_final.py refuses to overwrite an existing final archive",
        "dependency pins are an installed-version inventory, not an offline wheel/tarball cache",
    ]
    if terminal:
        fragile_operations.append(
            "the preserved validator failed after merge because post-merge kinematics schema code requested absent key angle_deg; no missing acceptance outputs may be inferred"
        )
    assumptions = [
        "LAST_EXECUTION_RECORD.json is the sole claim for observed commands and exit codes; authoring-manifest hashes bind final authoring outputs and handoff checksums bind preserved payload files",
        "Category-B invalids are only unauthorized positive-volume pairs between two rigid FIXED/MOVING occurrences",
        "NCR statuses reproduce build_workbook.mjs gate mappings and formulas rather than stale workbook cells",
        "Filesystem mtimes and manifest hashes, not version-control history, define last-modified evidence",
        "Absolute paths copied inside historical evidence are provenance-only and are not resumption dependencies",
        "The completed motion sweep merged and removed temporary shards; no /tmp state is required after the sweep",
        "work/scripts is historical/non-runnable without omitted original input trees; work/r2_source plus full WP02 is authoritative",
    ]
    if terminal:
        assumptions.append(
            "LAST_AUDIT_FAILURE.json binds the completed merged motion CSV; no completed validation manifest, summary, gate result, motion summary, or motion kinematics artifact exists"
        )
    owner_decisions_not_to_reopen = [
        CREO_DISPOSITION,
        "Do not restart source inventory or expand beyond the full WP02 live input tree unless authoritative code requires another input",
        "Do not discard preserved source geometry, checkpoints, evidence, or candidate outputs",
        "Do not begin another corrective cycle or final release packaging from this handoff",
        "Do not replace OCP/XCAF as the controlling neutral-CAD validation gate",
        "Do not treat stale work/r2_metadata WIP/Creo text as controlling governance",
        "Keep all arms at exactly 733.806 mm pivot-to-tip",
        "Keep the guided central compression spring envelope: maximum OD 15.8 mm; approximate free length 195 mm; approximate stowed installed length 145 mm; deployed installed length approximately 160.05 mm; approximate rate 16 N/mm; approximate stowed force 800 N; minimum target deployed force approximately 559 N; available work target approximately 10.2 J; maximum solid height 138 mm; spring-plus-seat mass target no more than 0.13 kg",
        "Retain direct ACE HBD-15-25-AA-P installation with mechanical seizure accepted as an owner-approved single-point deployment failure and no bypass carriage, lost-motion anti-seizure mechanism, overload release, fuse pin, or redundant damper",
    ]
    if terminal:
        validation_state = {
            "execution_state": "TERMINAL_AUDIT_FAILURE",
            "last_successful_validator_status": "UNAVAILABLE_TERMINAL_AUDIT_FAILURE",
            "last_successful_validator_exit_code": None,
            "last_validator_exit_code": 1,
            "last_audit_failure": LAST_AUDIT_FAILURE_PATH.as_posix(),
            "validator_failure": dict(evidence.audit_failure or {}),
            "present_validation_files": list(evidence.present_validation_files),
            "missing_validation_files": list(evidence.missing_validation_files),
            "artifact_availability": {
                "gate_results": False,
                "validation_summary": False,
                "validation_manifest": False,
                "motion_audit_summary": False,
                "motion_kinematics_1deg": False,
                "merged_motion_audit": True,
            },
            "validation_summary": None,
            "validator_scope": None,
            "validator_limit": None,
            "elapsed_seconds": None,
            "computed_release_status": "NOT_RELEASED_VALIDATOR_FAILURE",
            "package_required_label": "INCOMPLETE TERMINAL AUDIT — NOT RELEASED",
            "gate_counts": None,
            "handoff_open_gate_count": len(gate_state["open_gates"]),
            "expected_gate_ids": list(evidence.expected_gate_ids),
            "informational_environment_items": [dict(CREO_INFORMATIONAL_ITEM)],
            "gates": gate_state["open_gates"],
            "gate_results": None,
            "validation_manifest": None,
        }
    else:
        validation_state = {
            "execution_state": "COMPLETE",
            "last_successful_validator_status": evidence.validation_summary.get("validation_status"),
            "last_successful_validator_exit_code": last_execution["last_command"]["exit_code"],
            "last_validator_exit_code": last_execution["last_command"]["exit_code"],
            "last_audit_failure": None,
            "validator_failure": None,
            "present_validation_files": list(evidence.present_validation_files),
            "missing_validation_files": [],
            "artifact_availability": {
                "gate_results": True,
                "validation_summary": True,
                "validation_manifest": True,
                "motion_audit_summary": True,
                "motion_kinematics_1deg": True,
                "merged_motion_audit": True,
            },
            "validation_summary": "work/final_analysis/validation/validation_summary.json",
            "validator_scope": evidence.validation_summary.get("validator_scope"),
            "validator_limit": evidence.validation_summary.get("validator_limit"),
            "elapsed_seconds": evidence.validation_summary.get("elapsed_seconds"),
            "computed_release_status": gates.get("computed_release_status"),
            "package_required_label": gates.get("package_required_label"),
            "gate_counts": gates.get("gate_counts"),
            "handoff_open_gate_count": len(gate_state["open_gates"]),
            "expected_gate_ids": list(evidence.expected_gate_ids),
            "informational_environment_items": gates.get("informational_environment_items"),
            "gates": [
                {"gate_id": row.get("gate_id"), "status": row.get("status")}
                for row in gate_rows
                if isinstance(row, dict)
            ],
            "gate_results": "work/final_analysis/validation/gate_results.json",
            "validation_manifest": "work/final_analysis/validation/validation_manifest.json",
        }
    return {
        "schema": "DF8_CODEX_HANDOFF_CURRENT_STATE_V2",
        "checkpoint_timestamp": captured_at,
        "captured_at_utc": captured_at,
        "reproducibility_epoch": reproducibility_epoch,
        "reproducibility_timestamp_utc": iso_time(reproducibility_epoch),
        "checkpoint_root": ".",
        "current_execution_phase": phase,
        "latest_completed_checkpoint": checkpoint,
        "authoritative_source": "work/r2_source",
        "live_build_inputs": [path.as_posix() for path in LIVE_WP02_VENDOR_FILES],
        "last_command": last_execution["last_command"],
        "last_exit_code": last_execution["last_command"]["exit_code"],
        "last_successful_modifying_command": last_execution["last_successful_modifying_command"],
        "last_successful_audit_command": last_execution["last_successful_audit_command"],
        "last_execution_record": "work/handoff_tools/LAST_EXECUTION_RECORD.json",
        "last_execution_record_recorded_at_utc": last_execution["recorded_at_utc"],
        "last_successful_validator_status": (
            "UNAVAILABLE_TERMINAL_AUDIT_FAILURE" if terminal
            else evidence.validation_summary.get("validation_status")
        ),
        "last_modified_files": last_modified_files,
        "most_recent_snapshot_files": recent_file_records,
        "latest_stowed_metrics": derived["endpoint_metrics"]["STOWED"],
        "latest_deployed_metrics": derived["endpoint_metrics"]["DEPLOYED"],
        "latest_motion_metrics": {
            **derived["motion_metrics"],
            "motion_variants": derived["motion_variants"],
        },
        "remaining_pairs": derived["remaining_positive_pairs"],
        "authorized_contacts": derived["authorized_contacts"],
        "invalid_interferences": derived["invalid_interferences"],
        "category_b_invalids": derived["category_b_invalids"],
        "unresolved_nonrigid_positive_pairs": derived["unresolved_nonrigid_positive_pairs"],
        "validator_defects": derived["validator_defects"],
        "hierarchy": derived["hierarchy"],
        "state_parity": derived["state_parity"],
        "connectivity_attachment_route": derived["connectivity_attachment_route"],
        "definition_of_done": derived["definition_of_done"],
        "dimensions_mass_reserve": derived["dimensions_mass_reserve"],
        "open_gates": gate_state["open_gates"],
        "closed_gates": gate_state["closed_gates"],
        "open_ncrs": [row for row in gate_state["ncrs"] if row["formula_status"] != "CLOSED"],
        "ncr_formula_statuses": gate_state["ncrs"],
        "final_artifact_status": final_artifact_status,
        "dependency_versions": {
            "runtime_versions": dependencies["runtime_versions"],
            "python_packages": dependencies["python_packages"],
            "node_packages": dependencies["node_packages"],
        },
        "fragile_operations": fragile_operations,
        "assumptions": assumptions,
        "owner_decisions_not_to_reopen": owner_decisions_not_to_reopen,
        "handoff_policy": {
            "purpose": "SAFE CODEX HANDOFF CHECKPOINT",
            "new_correction_cycle_authorized": False,
            "final_release_packaging_authorized": False,
            "latest_safe_termination_directive_governs_runtime_only": True,
            "stale_r2_metadata_is_controlling": False,
        },
        "governance": {
            "creo_environment": CREO_DISPOSITION,
            "controlling_neutral_cad_gate": "Clean-process OCP/XCAF AP242 reimport",
            "controlling_source_records": [destination.as_posix() for _source, destination, _role in COMMISSION_SOURCES],
        },
        "validation": validation_state,
        "authoring": {
            "schema": authoring.get("schema"),
            "release_status": authoring.get("release_status"),
            "manifest": "work/final_analysis/authoring_manifest.json",
            "final_products": [
                staged_file_record(stage, FINAL_RELEASE / FINAL_STOWED),
                staged_file_record(stage, FINAL_RELEASE / FINAL_DEPLOYED),
            ],
            "workbook": (
                staged_file_record(stage, workbook_path)
                if (stage / workbook_path).is_file() else None
            ),
        },
        "preserved_checkpoint_directories": [relative_text(path) for path in preserved],
        "candidate_wip_outputs": [relative_text(path) for path in candidate_outputs],
        "candidate_temporary_artifacts": [relative_text(path) for path in candidate_temps],
        "dependency_capture": {
            "python_package_count": len(dependencies["python_packages"]),
            "node_package_install_count": len(dependencies["node_packages"]),
            "runtime_versions": "environment/RUNTIME_VERSIONS.json",
            "python_pins": "environment/PYTHON_REQUIREMENTS_FULLY_PINNED.txt",
            "node_pins": "environment/NODE_PACKAGES_FULLY_PINNED.csv",
        },
        "payload_exclusions": {
            "directory_names": sorted(EXCLUDED_DIR_NAMES),
            "file_suffixes": sorted(EXCLUDED_FILE_SUFFIXES),
            "handoff_archive_self_excluded": ARCHIVE_NAME,
        },
        "integrity": {
            "file_manifest": "FILE_MANIFEST.csv",
            "sha256_sums": "SHA256SUMS.txt",
            "sha256_sums_self_excluded": True,
            "sha256_sums_covers_file_manifest_and_all_other_payload_files": True,
            "file_manifest_omits_own_row_to_avoid_recursive_content": True,
            "file_manifest_sha256sums_row_has_blank_digest_because_sha256sums_is_self_excluded": True,
        },
    }


def iter_stage_nodes(stage: Path) -> list[Path]:
    result: list[Path] = []
    stack = [stage]
    while stack:
        current = stack.pop()
        children = sorted(current.iterdir(), key=lambda path: path.name, reverse=True)
        for child in children:
            if stat.S_ISLNK(child.lstat().st_mode):
                raise RuntimeError(
                    f"payload symlink is forbidden: {child.relative_to(stage).as_posix()}"
                )
            result.append(child)
            if child.is_dir():
                stack.append(child)
    return sorted(result, key=lambda path: path.relative_to(stage).as_posix())


def payload_digest(path: Path) -> str:
    if path.is_symlink():
        raise RuntimeError(f"payload symlink is forbidden: {path}")
    return sha256_file(path)


def write_file_indexes(stage: Path, source_map: dict[str, str], epoch: int) -> None:
    manifest_relative = Path("FILE_MANIFEST.csv")
    sums_relative = Path("SHA256SUMS.txt")
    existing_files = [
        path
        for path in iter_stage_nodes(stage)
        if path.is_file()
        and path.relative_to(stage) not in {manifest_relative, sums_relative}
    ]
    # SHA256SUMS will contain every current file plus FILE_MANIFEST.csv.  Its
    # byte size is independent of the digest values because SHA-256 is fixed
    # width, so the manifest can record the self-excluded index accurately.
    sum_paths = sorted(
        [path.relative_to(stage).as_posix() for path in existing_files]
        + [manifest_relative.as_posix()]
    )
    predicted_sums_size = sum(len(f"{'0' * 64}  {name}\n".encode("utf-8")) for name in sum_paths)

    manifest_path = stage / manifest_relative
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "payload_path", "source_path", "type", "size_bytes", "mtime_utc",
                "mtime_ns", "mode_octal", "sha256", "integrity_note",
            ),
            lineterminator="\n",
        )
        writer.writeheader()
        for path in existing_files:
            relative = path.relative_to(stage)
            metadata = path.lstat()
            writer.writerow(
                {
                    "payload_path": relative.as_posix(),
                    "source_path": source_map.get(relative.as_posix(), "GENERATED"),
                    "type": "file",
                    "size_bytes": metadata.st_size,
                    "mtime_utc": iso_time(int(metadata.st_mtime)),
                    "mtime_ns": metadata.st_mtime_ns,
                    "mode_octal": f"{stat.S_IMODE(metadata.st_mode):04o}",
                    "sha256": payload_digest(path),
                    "integrity_note": "",
                }
            )
        writer.writerow(
            {
                "payload_path": sums_relative.as_posix(),
                "source_path": "GENERATED",
                "type": "file",
                "size_bytes": predicted_sums_size,
                "mtime_utc": iso_time(epoch),
                "mtime_ns": epoch * 1_000_000_000,
                "mode_octal": "0644",
                "sha256": "",
                "integrity_note": (
                    "SHA256SUMS excludes itself; digest intentionally blank here. "
                    "FILE_MANIFEST omits its own row to avoid recursive content."
                ),
            }
        )
    os.chmod(manifest_path, 0o644)
    os.utime(manifest_path, (epoch, epoch))

    sums_lines = []
    for name in sum_paths:
        path = stage / PurePosixPath(name)
        sums_lines.append(f"{payload_digest(path)}  {name}\n")
    generated_write(stage / sums_relative, "".join(sums_lines), epoch)
    if (stage / sums_relative).stat().st_size != predicted_sums_size:
        raise RuntimeError("SHA256SUMS deterministic size prediction failed")

    actual_non_directory = {
        path.relative_to(stage).as_posix()
        for path in iter_stage_nodes(stage)
        if path.is_file()
    }
    listed = set(sum_paths)
    if listed != actual_non_directory - {sums_relative.as_posix()}:
        raise RuntimeError("SHA256SUMS does not cover the complete payload")


def zip_timestamp(epoch: int) -> tuple[int, int, int, int, int, int]:
    lower = 315532800  # 1980-01-01 UTC
    upper = 4354819198  # 2107-12-31 23:59:58 UTC
    value = max(lower, min(upper, epoch - (epoch % 2)))
    return time.gmtime(value)[:6]


def timestamp_extra(epoch: int) -> bytes:
    value = max(0, min(0xFFFFFFFF, int(epoch)))
    return struct.pack("<HHBI", 0x5455, 5, 1, value)


def add_zip_node(archive: zipfile.ZipFile, stage: Path, path: Path) -> None:
    relative = path.relative_to(stage).as_posix()
    arcname = relative
    metadata = path.lstat()
    info = zipfile.ZipInfo(arcname, zip_timestamp(int(metadata.st_mtime)))
    info.create_system = 3
    info.extra = timestamp_extra(int(metadata.st_mtime))
    permissions = stat.S_IMODE(metadata.st_mode)
    if path.is_symlink():
        raise RuntimeError(f"payload symlink is forbidden: {relative}")
    if path.is_dir():
        info.filename += "/"
        info.external_attr = ((stat.S_IFDIR | permissions) << 16) | 0x10
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, b"")
    elif path.is_file():
        info.external_attr = (stat.S_IFREG | permissions) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        with archive.open(info, "w", force_zip64=True) as output, path.open("rb") as source:
            shutil.copyfileobj(source, output, length=1024 * 1024)
    else:
        raise RuntimeError(f"unsupported staged node: {relative}")


def publish_archive(stage: Path) -> dict[str, Any]:
    if OUTPUT_PATH.exists() or OUTPUT_PATH.is_symlink():
        raise RuntimeError(f"refusing to overwrite existing handoff archive: {ARCHIVE_NAME}")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{ARCHIVE_NAME}.", suffix=".tmp", dir=ROOT, delete=False
        ) as stream:
            temporary = Path(stream.name)
        nodes = iter_stage_nodes(stage)
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED,
            compresslevel=9, allowZip64=True,
        ) as archive:
            for path in nodes:
                add_zip_node(archive, stage, path)
        os.chmod(temporary, 0o644)
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        expected = [
            path.relative_to(stage).as_posix()
            + ("/" if path.is_dir() else "")
            for path in nodes
        ]
        with zipfile.ZipFile(temporary, "r") as archive:
            if archive.namelist() != expected:
                raise RuntimeError("handoff archive member order/set mismatch")
            required_root_members = {
                "HANDOFF.md", "CURRENT_STATE.json", "RESUME_COMMANDS.md",
                "FILE_MANIFEST.csv", "SHA256SUMS.txt",
            }
            if not required_root_members <= set(archive.namelist()):
                raise RuntimeError("handoff archive root-level document set is incomplete")
            if any(name.startswith(f"{ARCHIVE_STEM}/") for name in archive.namelist()):
                raise RuntimeError("handoff archive is incorrectly wrapped in an extra root directory")
            if len(archive.namelist()) != len(set(archive.namelist())):
                raise RuntimeError("handoff archive contains duplicate member names")
            if any(stat.S_ISLNK(info.external_attr >> 16) for info in archive.infolist()):
                raise RuntimeError("handoff archive contains a forbidden symlink member")
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f"handoff archive CRC failure: {bad}")
            try:
                archived_sums_bytes = archive.read("SHA256SUMS.txt")
                if archived_sums_bytes != (stage / "SHA256SUMS.txt").read_bytes():
                    raise RuntimeError("archived SHA256SUMS.txt bytes differ from staged index")
                sums_text = archived_sums_bytes.decode("utf-8")
            except (KeyError, UnicodeDecodeError) as exc:
                raise RuntimeError("handoff archive SHA256SUMS.txt is absent or invalid") from exc
            listed: dict[str, str] = {}
            for line_number, line in enumerate(sums_text.splitlines(), start=1):
                if len(line) < 67 or line[64:66] != "  ":
                    raise RuntimeError(f"invalid SHA256SUMS line {line_number}")
                digest, name = line[:64].lower(), line[66:]
                if any(character not in "0123456789abcdef" for character in digest):
                    raise RuntimeError(f"invalid SHA-256 token on line {line_number}")
                pure = PurePosixPath(name)
                if (
                    not name or pure.is_absolute() or ".." in pure.parts
                    or "\\" in name or "\n" in name or "\r" in name
                    or name in listed
                ):
                    raise RuntimeError(f"unsafe/duplicate SHA256SUMS member on line {line_number}")
                listed[name] = digest
            file_members = {
                info.filename for info in archive.infolist() if not info.is_dir()
            }
            if set(listed) != file_members - {"SHA256SUMS.txt"}:
                raise RuntimeError("archived SHA256SUMS does not cover every other file member exactly")
            for name, expected_digest in sorted(listed.items()):
                digest = hashlib.sha256()
                with archive.open(name, "r") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != expected_digest:
                    raise RuntimeError(f"archived member SHA-256 mismatch: {name}")
        published = False
        try:
            try:
                os.link(temporary, OUTPUT_PATH)
                published = True
            except FileExistsError as exc:
                raise RuntimeError(
                    f"refusing to overwrite existing handoff archive: {ARCHIVE_NAME}"
                ) from exc
            directory_fd = os.open(ROOT, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except BaseException:
            if published:
                try:
                    OUTPUT_PATH.unlink()
                finally:
                    recovery_fd = os.open(ROOT, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
                    try:
                        os.fsync(recovery_fd)
                    finally:
                        os.close(recovery_fd)
            raise
        temporary.unlink()
        cleanup_fd = os.open(ROOT, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(cleanup_fd)
        finally:
            os.close(cleanup_fd)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return {
        "archive": ARCHIVE_NAME,
        "size_bytes": OUTPUT_PATH.stat().st_size,
        "sha256": sha256_file(OUTPUT_PATH),
    }


def bounded_reproducibility_epoch(entries: list[SourceEntry], capture_wall_epoch: int) -> int:
    lower = 315532800  # 1980-01-01 UTC, ZIP lower bound.
    if "SOURCE_DATE_EPOCH" in os.environ:
        try:
            epoch = int(os.environ["SOURCE_DATE_EPOCH"])
        except ValueError as exc:
            raise RuntimeError("SOURCE_DATE_EPOCH must be an integer") from exc
    else:
        epoch = max(entry.mtime_ns for entry in entries) // 1_000_000_000
    if not lower <= epoch <= capture_wall_epoch:
        raise RuntimeError(
            "SOURCE_DATE_EPOCH/reproducibility epoch is outside the bounded "
            f"1980-to-capture interval: epoch={epoch}, capture={capture_wall_epoch}"
        )
    return epoch


def locked_main() -> int:
    if ROOT == Path("/") or not (ROOT / "work").is_dir():
        raise RuntimeError("workspace root resolution failed")
    if OUTPUT_PATH.exists() or OUTPUT_PATH.is_symlink():
        raise RuntimeError(f"refusing to overwrite existing handoff archive: {ARCHIVE_NAME}")
    active = active_workspace_processes()
    if active:
        raise RuntimeError(f"active geometry/audit process(es) remain: {active}")
    require_workspace_inputs()
    # Root evidence is a fail-fast preflight only. All emitted state is derived
    # exclusively from the copied, hash-verified staged evidence below.
    load_evidence(ROOT)
    dependencies = capture_dependencies()
    entries, preserved, candidate_outputs, candidate_temps = gather_source_entries()
    if not entries:
        raise RuntimeError("handoff payload enumeration is empty")

    capture_wall = dt.datetime.now(tz=dt.timezone.utc)
    capture_wall_epoch = int(capture_wall.timestamp())
    captured_at = capture_wall.isoformat(timespec="seconds").replace("+00:00", "Z")
    epoch = bounded_reproducibility_epoch(entries, capture_wall_epoch)

    with tempfile.TemporaryDirectory(
        prefix="df8_codex_handoff_stage_", dir="/tmp",
    ) as temporary_directory:
        stage = Path(temporary_directory).resolve(strict=True)
        if stage.parent != Path("/tmp") or stage == ROOT or ROOT in stage.parents:
            raise RuntimeError("handoff staging root must be a direct non-nested child of /tmp")
        os.chmod(stage, 0o755)
        os.utime(stage, (epoch, epoch))
        source_map = materialize_snapshot(entries, stage)
        verify_snapshot_sources(entries)
        # TOCTOU boundary: authoritative docs/state are loaded only from the
        # staged copy after source-content verification.
        evidence = load_evidence(stage)
        dependency_paths = write_dependency_manifests(stage, dependencies, epoch)
        for path in dependency_paths:
            source_map[path.as_posix()] = "GENERATED"
        provenance_path = commission_provenance(stage, epoch)
        source_map[provenance_path.as_posix()] = "GENERATED"

        current_state = current_state_payload(
            stage, evidence, preserved, candidate_outputs, candidate_temps,
            dependencies, captured_at, epoch, entries,
        )
        generated_write(
            stage / "CURRENT_STATE.json",
            json.dumps(current_state, indent=2, sort_keys=True) + "\n",
            epoch,
        )
        generated_write(
            stage / "HANDOFF.md", handoff_markdown(evidence, captured_at, epoch), epoch,
        )
        generated_write(stage / "RESUME_COMMANDS.md", resume_commands_markdown(evidence), epoch)
        source_map.update(
            {
                "CURRENT_STATE.json": "GENERATED",
                "HANDOFF.md": "GENERATED",
                "RESUME_COMMANDS.md": "GENERATED",
            }
        )
        write_file_indexes(stage, source_map, epoch)
        for generated_directory in (stage / "commission", stage / "environment"):
            os.chmod(generated_directory, 0o755)
            os.utime(generated_directory, (epoch, epoch))
        verify_snapshot_sources(entries)
        active = active_workspace_processes()
        if active:
            raise RuntimeError(f"geometry/audit process started during handoff snapshot: {active}")
        os.utime(stage, (epoch, epoch))
        result = publish_archive(stage)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main() -> int:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    lock_fd = os.open(LOCK_PATH, lock_flags, 0o600)
    with os.fdopen(lock_fd, "a+b") as lock_stream:
        try:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another handoff builder holds the exclusive workspace lock") from exc
        return locked_main()


if __name__ == "__main__":
    raise SystemExit(main())
