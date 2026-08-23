#!/usr/bin/env python3
"""Read-only, fail-closed validation of a DF8 Codex handoff ZIP.

The archive is screened before extraction, extracted member-by-member into a
private directory under /tmp, and validated without importing project Python
sources.  The mandatory CAD help smoke imports the extracted validator with an
explicit Python interpreter, but redirects writable runtime locations into the
temporary extraction and disables bytecode generation.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import tokenize
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE = ROOT / "STINGRAY_I5S_DF8_R2_CODEX_HANDOFF_CHECKPOINT.zip"
DEFAULT_CAD_PYTHON = ROOT / "work/cadenv/bin/python3"

DIRECT_ROOT_FILES = frozenset(
    {
        "HANDOFF.md",
        "CURRENT_STATE.json",
        "RESUME_COMMANDS.md",
        "SHA256SUMS.txt",
        "FILE_MANIFEST.csv",
    }
)

FINAL_STOWED = "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step"
FINAL_DEPLOYED = "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step"

EXPECTED_GATE_IDS = (
    "AP242-STOWED",
    "BREP-VALID-STOWED",
    "INTERFERENCE-STOWED",
    "INTENTIONAL-FIT-REGISTER-STOWED",
    "CLEARANCE-EVIDENCE-STOWED",
    "AP242-DEPLOYED",
    "BREP-VALID-DEPLOYED",
    "INTERFERENCE-DEPLOYED",
    "INTENTIONAL-FIT-REGISTER-DEPLOYED",
    "CLEARANCE-EVIDENCE-DEPLOYED",
    "STATE-PARITY",
    "OCCURRENCE-TRANSFORMS",
    "OCCURRENCE-BOM-RECONCILIATION",
    "DOD-REQUIRED-HARDWARE-AND-PIN-RETENTION",
    "DOD-POSITIVE-DEPLOYED-LOCKS",
    "DOD-POSITIVE-STOWED-RETENTION",
    "DOD-CLOSED-PRESSURE-SUBSYSTEMS",
    "DOD-CLOSED-ROUTE-ENDS",
    "ARM-KINEMATICS-ENDPOINTS",
    "ARM-LENGTH",
    "ARM-SURFACE-QUALITY",
    "CROSSHEAD-TRAVEL",
    "NORMAL-BODY-OML",
    "ARM-MODULE-HARD-ENVELOPE",
    "RIGID-LENGTH",
    "SYSTEM-MASS",
    "ATTACHMENT-COHESION",
    "RECOVERY-LOAD-PATH",
    "PROCUREMENT-DEFINITION",
    "MOTION-FULL-MECHANISM",
    "INTENTIONAL-FIT-REGISTER-MOTION",
)

VALID_GATE_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED"})
CREO_DISPOSITION = (
    "N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; "
    "OWNER CREO IMPORT OCCURS AFTER DELIVERY."
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

REQUIRED_LIVE_INPUTS = (
    (
        "work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/"
        "03_VENDOR_CAD_ORIGINAL/ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp"
    ),
    (
        "work/input/wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/"
        "04_VENDOR_CAD_CREO_DROP_IN/"
        "ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step"
    ),
)

REQUIRED_COMMISSION_FILES = (
    "commission/ORIGINAL_COMMISSION_20260821-031917.md",
    "commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md",
    "commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md",
    "commission/PROVENANCE.json",
)

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

INCOMPLETE_PRESENT_VALIDATION_FILES = (
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
    "xcaf_occurrences_stowed.csv",
)

INCOMPLETE_MISSING_VALIDATION_FILES = (
    "gate_results.json",
    "motion_audit_summary.json",
    "motion_kinematics_1deg.csv",
    "validation_manifest.json",
    "validation_summary.json",
)

LAST_AUDIT_FAILURE_PATH = "work/handoff_tools/LAST_AUDIT_FAILURE.json"
LAST_AUDIT_FAILURE_FIELDS = frozenset(
    {
        "schema",
        "recorded_at_utc",
        "command",
        "exit_code",
        "exception_type",
        "exception_message",
        "failure_stage",
        "completed_motion_sample_count",
        "present_validation_files",
        "missing_validation_files",
        "merged_motion_audit",
        "release_authorized",
    }
)
INCOMPLETE_RELEASE_STATUS = "NOT_RELEASED_VALIDATOR_FAILURE"
INCOMPLETE_PACKAGE_LABEL = "INCOMPLETE TERMINAL AUDIT — NOT RELEASED"
EXPECTED_MERGED_MOTION_SIZE = 22_925_903
EXPECTED_MERGED_MOTION_DATA_ROWS = 1_447_875
EXPECTED_MERGED_MOTION_FIELDS = (
    "sample_index", "angle_deg", "occurrence_a", "solid_index_a", "variant_a",
    "part_number_a", "occurrence_b", "solid_index_b", "variant_b", "part_number_b",
    "aabb_overlap", "aabb_gap_mm", "exact_common_status", "common_volume_mm3",
    "documented_positive_volume_exception", "intentional_fit_exception_id",
    "exact_distance_status", "exact_clearance_mm", "result", "error",
)
EXPECTED_MERGED_MOTION_SHA256 = (
    "4da00e87fd63199a29c0f4e97e9f9502da604ed48cf3f8875a9300778828fee6"
)
EXPECTED_FAILED_VALIDATOR_SHA256 = (
    "d11dd74a38deea99860db7f662cb484175924039de6ba86d02a216a8363deb61"
)

MANIFEST_FIELDS = (
    "payload_path",
    "source_path",
    "type",
    "size_bytes",
    "mtime_utc",
    "mtime_ns",
    "mode_octal",
    "sha256",
    "integrity_note",
)

SHA_LINE = re.compile(r"^([0-9a-f]{64})  ([^\r\n\\]+)$")
SHA_VALUE = re.compile(r"^[0-9a-f]{64}$")
MODE_VALUE = re.compile(r"^[0-7]{4}$")
OLD_WORKSPACE = re.compile(r"/workspace/scratch(?:/|$)", re.IGNORECASE)
LIVE_MOTION_SHARD = re.compile(
    r"(?:stingray_motion_angle_shards_|/tmp/[^\s\"'`]*motion[^\s\"'`]*shard)",
    re.IGNORECASE,
)
EXECUTABLE_FENCE = re.compile(
    r"^```([^\r\n]*)\r?\n(.*?)^```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
UNAVAILABLE_OPERATIONAL_PREFIXES = ("/root/", "/workspace/", "/tmp/")

MAX_MEMBER_COUNT = 100_000
MAX_SINGLE_FILE_BYTES = 4 * 1024**3
MAX_TOTAL_FILE_BYTES = 8 * 1024**3
MAX_STRUCTURED_TEXT_BYTES = 128 * 1024**2

FORBIDDEN_PAYLOAD_PARTS = frozenset(
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


class ValidationFailure(RuntimeError):
    """Expected fail-closed validation error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                f"{label} exceeds structured-text safety limit")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"{label} is unreadable or invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"{label} root must be an object")
    return value


def safe_relative_parts(value: str, label: str) -> tuple[str, ...]:
    require(isinstance(value, str) and value != "", f"{label} is blank")
    require("\\" not in value, f"{label} contains a backslash")
    require("\x00" not in value and "\r" not in value and "\n" not in value,
            f"{label} contains a control separator")
    require(not value.startswith("/"), f"{label} is absolute")
    raw_parts = value.split("/")
    require(all(part not in {"", ".", ".."} for part in raw_parts),
            f"{label} contains an empty, dot, or parent component")
    require(not re.match(r"^[A-Za-z]:", raw_parts[0]), f"{label} is drive-qualified")
    for part in raw_parts:
        require(not any(ord(character) < 32 or ord(character) == 127 for character in part),
                f"{label} contains a control character")
        require(":" not in part, f"{label} contains a colon")
    path = PurePosixPath(*raw_parts)
    require(not path.is_absolute() and ".." not in path.parts, f"{label} escapes its root")
    return tuple(path.parts)


def archive_member_parts(name: str) -> tuple[tuple[str, ...], bool]:
    require(isinstance(name, str) and name != "", "ZIP member name is blank")
    require(len(name.encode("utf-8")) <= 4096, "ZIP member name exceeds 4096 UTF-8 bytes")
    is_directory = name.endswith("/")
    trimmed = name[:-1] if is_directory else name
    require(trimmed != "", "ZIP contains an unnamed root directory")
    return safe_relative_parts(trimmed, f"ZIP member {name!r}"), is_directory


def payload_path(value: str, label: str) -> str:
    return PurePosixPath(*safe_relative_parts(value, label)).as_posix()


def member_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0xFFFF


def member_unix_mtime(info: zipfile.ZipInfo) -> int:
    offset = 0
    values: list[int] = []
    while offset < len(info.extra):
        require(offset + 4 <= len(info.extra),
                f"truncated ZIP extra-field header: {info.filename}")
        field_id, field_size = struct.unpack_from("<HH", info.extra, offset)
        offset += 4
        require(offset + field_size <= len(info.extra),
                f"truncated ZIP extra-field body: {info.filename}")
        data = info.extra[offset:offset + field_size]
        offset += field_size
        if field_id == 0x5455:
            require(field_size == 5 and data[0] & 0x1,
                    f"ZIP UT timestamp field is not exact: {info.filename}")
            values.append(struct.unpack_from("<I", data, 1)[0])
    require(len(values) == 1, f"ZIP member lacks one exact UT mtime: {info.filename}")
    return values[0]


def screen_archive(
    archive: zipfile.ZipFile,
) -> tuple[list[zipfile.ZipInfo], dict[str, zipfile.ZipInfo], int, int]:
    infos = archive.infolist()
    require(infos, "ZIP archive is empty")
    require(len(infos) <= MAX_MEMBER_COUNT, "ZIP member count exceeds safety limit")
    expected_order = sorted(
        infos,
        key=lambda info: info.filename[:-1] if info.filename.endswith("/") else info.filename,
    )
    require([info.filename for info in infos] == [info.filename for info in expected_order],
            "ZIP member order is not the canonical source-path order")

    exact_names: set[str] = set()
    collision_keys: dict[str, str] = {}
    kinds: dict[str, str] = {}
    file_infos: dict[str, zipfile.ZipInfo] = {}
    total_declared = 0

    for info in infos:
        require(info.filename not in exact_names, f"duplicate ZIP member: {info.filename!r}")
        exact_names.add(info.filename)
        parts, name_is_directory = archive_member_parts(info.filename)
        leaf_name = parts[-1]
        require(leaf_name != DEFAULT_ARCHIVE.name
                and not leaf_name.startswith(f".{DEFAULT_ARCHIVE.name}."),
                f"handoff archive/self-publication temp is recursively included: {info.filename}")
        require(not any(part.casefold() in FORBIDDEN_PAYLOAD_PARTS for part in parts),
                f"excluded runtime/cache path is present in ZIP: {info.filename}")
        require(PurePosixPath(*parts).suffix.lower() not in {".pyc", ".pyo"},
                f"compiled Python bytecode is present in ZIP: {info.filename}")
        canonical = PurePosixPath(*parts).as_posix()
        collision_key = "/".join(
            unicodedata.normalize("NFC", part).casefold() for part in parts
        )
        previous = collision_keys.get(collision_key)
        require(previous is None, f"case/Unicode-colliding ZIP members: {previous!r}, {info.filename!r}")
        collision_keys[collision_key] = info.filename

        mode = member_mode(info)
        file_type = stat.S_IFMT(mode)
        require(info.create_system == 3, f"ZIP member is not Unix-authored: {info.filename}")
        member_unix_mtime(info)
        require(not stat.S_ISLNK(mode), f"ZIP symlink is forbidden: {info.filename}")
        require(not (mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX)),
                f"ZIP member has unsafe special mode bits: {info.filename}")
        require(not (info.flag_bits & 0x1), f"encrypted ZIP member is forbidden: {info.filename}")
        require(info.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED},
                f"unsupported ZIP compression method for {info.filename}")

        if name_is_directory:
            require(file_type in {0, stat.S_IFDIR},
                    f"directory name/type mismatch: {info.filename}")
            require(info.file_size == 0, f"directory has nonzero payload: {info.filename}")
            kinds[canonical] = "directory"
        else:
            require(file_type in {0, stat.S_IFREG},
                    f"special or file/type-mismatched ZIP member: {info.filename}")
            require(info.file_size <= MAX_SINGLE_FILE_BYTES,
                    f"ZIP member exceeds safety limit: {info.filename}")
            total_declared += info.file_size
            require(total_declared <= MAX_TOTAL_FILE_BYTES,
                    "ZIP total declared file size exceeds safety limit")
            kinds[canonical] = "file"
            file_infos[canonical] = info

    for path, kind in kinds.items():
        parts = PurePosixPath(path).parts
        for index in range(1, len(parts)):
            parent = PurePosixPath(*parts[:index]).as_posix()
            require(kinds.get(parent) != "file",
                    f"ZIP file is also a parent path: {parent}")
        if kind == "file":
            require(not any(other.startswith(path + "/") for other in kinds),
                    f"ZIP file conflicts with child member path: {path}")

    for required in DIRECT_ROOT_FILES:
        require(required in file_infos, f"required direct-root file is absent: {required}")
    return infos, file_infos, total_declared, len(kinds) - len(file_infos)


def extract_screened_archive(
    archive: zipfile.ZipFile,
    infos: Iterable[zipfile.ZipInfo],
    destination: Path,
) -> int:
    extracted_bytes = 0
    directories: list[tuple[Path, int]] = []
    for info in infos:
        parts, is_directory = archive_member_parts(info.filename)
        target = destination.joinpath(*parts)
        require(target == destination / PurePosixPath(*parts),
                f"member target normalization changed: {info.filename}")
        try:
            target.relative_to(destination)
        except ValueError as exc:
            raise ValidationFailure(f"member target escapes extraction: {info.filename}") from exc

        mode = stat.S_IMODE(member_mode(info))
        if is_directory:
            require(not target.exists() or target.is_dir(),
                    f"directory collides with extracted file: {info.filename}")
            target.mkdir(parents=True, exist_ok=True)
            directories.append((target, mode or 0o755))
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), f"extraction target already exists: {info.filename}")
        member_bytes = 0
        try:
            with archive.open(info, "r") as source, target.open("xb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    member_bytes += len(chunk)
                    extracted_bytes += len(chunk)
                    require(member_bytes <= info.file_size,
                            f"member expands beyond declared size: {info.filename}")
                    require(extracted_bytes <= MAX_TOTAL_FILE_BYTES,
                            "extracted content exceeds safety limit")
                    output.write(chunk)
        except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
            raise ValidationFailure(f"failed CRC-checked extraction of {info.filename}") from exc
        require(member_bytes == info.file_size,
                f"member extracted size mismatch: {info.filename}")
        os.chmod(target, mode or 0o644)

    for directory, mode in sorted(directories, key=lambda row: len(row[0].parts), reverse=True):
        os.chmod(directory, mode)
    return extracted_bytes


def inventory_extracted(root: Path) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    directories: set[str] = set()
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames.sort()
        filenames.sort()
        base = Path(directory)
        for name in dirnames:
            path = base / name
            metadata = path.lstat()
            require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode),
                    f"extracted non-directory or symlink: {path.relative_to(root)}")
            directories.add(path.relative_to(root).as_posix())
        for name in filenames:
            path = base / name
            metadata = path.lstat()
            require(stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode),
                    f"extracted special file or symlink: {path.relative_to(root)}")
            files.add(path.relative_to(root).as_posix())
    return files, directories


def parse_sha256sums(path: Path) -> dict[str, str]:
    try:
        require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                "SHA256SUMS.txt exceeds structured-text safety limit")
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationFailure("SHA256SUMS.txt is unreadable or not UTF-8") from exc
    require(raw.endswith(b"\n"), "SHA256SUMS.txt lacks its final LF")
    require(b"\r" not in raw and b"\x00" not in raw,
            "SHA256SUMS.txt contains CR or NUL")
    result: dict[str, str] = {}
    order: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        require(line != "", f"SHA256SUMS.txt has a blank line at {line_number}")
        match = SHA_LINE.fullmatch(line)
        require(match is not None, f"malformed SHA256SUMS.txt line {line_number}")
        digest, raw_name = match.groups()
        name = payload_path(raw_name, f"SHA256SUMS line {line_number} path")
        require(name == raw_name, f"noncanonical SHA256SUMS path at line {line_number}")
        require(name not in result, f"duplicate SHA256SUMS path: {name}")
        result[name] = digest
        order.append(name)
    require(order == sorted(order), "SHA256SUMS paths are not strictly sorted")
    return result


def verify_sha256sums(root: Path, all_files: set[str]) -> dict[str, str]:
    sums = parse_sha256sums(root / "SHA256SUMS.txt")
    expected = all_files - {"SHA256SUMS.txt"}
    require(set(sums) == expected,
            "SHA256SUMS exact file coverage mismatch: "
            f"missing={sorted(expected - set(sums))}, extra={sorted(set(sums) - expected)}")
    for name, expected_digest in sums.items():
        actual_digest = sha256_file(root / PurePosixPath(name))
        require(actual_digest == expected_digest, f"SHA-256 mismatch: {name}")
    return sums


def parse_integer(value: str, label: str) -> int:
    require(isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]*", value) is not None,
            f"{label} is not a canonical nonnegative integer")
    return int(value)


def validate_manifest_timestamp(mtime_ns: int, mtime_utc: str, label: str) -> None:
    require(isinstance(mtime_utc, str) and mtime_utc.endswith("Z"),
            f"{label} timestamp is not UTC Z format")
    try:
        parsed = dt.datetime.fromisoformat(mtime_utc[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationFailure(f"{label} timestamp is invalid") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() == dt.timedelta(0),
            f"{label} timestamp is not UTC")
    require(int(parsed.timestamp()) == mtime_ns // 1_000_000_000,
            f"{label} timestamp disagrees with mtime_ns")


def validate_file_manifest(
    root: Path,
    all_files: set[str],
    file_infos: dict[str, zipfile.ZipInfo],
) -> int:
    path = root / "FILE_MANIFEST.csv"
    try:
        require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                "FILE_MANIFEST.csv exceeds structured-text safety limit")
        text = path.read_text(encoding="utf-8")
        csv.field_size_limit(MAX_STRUCTURED_TEXT_BYTES)
        reader = csv.DictReader(io.StringIO(text, newline=""))
        require(tuple(reader.fieldnames or ()) == MANIFEST_FIELDS,
                "FILE_MANIFEST.csv header is not exact")
        rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValidationFailure("FILE_MANIFEST.csv is unreadable or invalid") from exc

    manifest_rows: dict[str, dict[str, str]] = {}
    row_order: list[str] = []
    for index, row in enumerate(rows, start=2):
        require(None not in row, f"FILE_MANIFEST.csv row {index} has extra columns")
        require(all(value is not None for value in row.values()),
                f"FILE_MANIFEST.csv row {index} has missing columns")
        name = payload_path(row["payload_path"], f"FILE_MANIFEST.csv row {index} path")
        require(name == row["payload_path"], f"noncanonical manifest path at row {index}")
        require(name not in manifest_rows, f"duplicate FILE_MANIFEST path: {name}")
        manifest_rows[name] = row
        row_order.append(name)

    expected = all_files - {"FILE_MANIFEST.csv"}
    require(set(manifest_rows) == expected,
            "FILE_MANIFEST exact file coverage mismatch: "
            f"missing={sorted(expected - set(manifest_rows))}, "
            f"extra={sorted(set(manifest_rows) - expected)}")
    require(row_order[:-1] == sorted(expected - {"SHA256SUMS.txt"})
            and row_order[-1:] == ["SHA256SUMS.txt"],
            "FILE_MANIFEST row order/self-exclusion row is not canonical")

    for name, row in manifest_rows.items():
        require(row["type"] == "file", f"manifest type is not regular file: {name}")
        size = parse_integer(row["size_bytes"], f"manifest size for {name}")
        require((root / PurePosixPath(name)).stat().st_size == size,
                f"manifest size mismatch: {name}")
        mtime_ns = parse_integer(row["mtime_ns"], f"manifest mtime_ns for {name}")
        validate_manifest_timestamp(mtime_ns, row["mtime_utc"], f"manifest {name}")
        require(MODE_VALUE.fullmatch(row["mode_octal"]) is not None,
                f"manifest mode is invalid: {name}")
        archive_mode = stat.S_IMODE(member_mode(file_infos[name]))
        require(int(row["mode_octal"], 8) == archive_mode,
                f"manifest mode disagrees with ZIP metadata: {name}")
        require(mtime_ns // 1_000_000_000 == member_unix_mtime(file_infos[name]),
                f"manifest mtime disagrees with ZIP UT timestamp: {name}")

        source = row["source_path"]
        if source != "GENERATED":
            canonical_source = payload_path(source, f"manifest source_path for {name}")
            require(canonical_source == source, f"noncanonical source_path for {name}")

        if name == "SHA256SUMS.txt":
            require(source == "GENERATED", "SHA256SUMS source_path is not GENERATED")
            require(row["sha256"] == "", "SHA256SUMS manifest self-hash must be blank")
            normalized_note = " ".join(row["integrity_note"].casefold().split())
            require(
                all(
                    phrase in normalized_note
                    for phrase in (
                        "sha256sums excludes itself",
                        "digest intentionally blank",
                        "file_manifest omits its own row",
                    )
                ),
                "SHA256SUMS manifest note does not disclose both recursive self-exclusions",
            )
        else:
            require(SHA_VALUE.fullmatch(row["sha256"]) is not None,
                    f"manifest SHA-256 is invalid: {name}")
            require(row["sha256"] == sha256_file(root / PurePosixPath(name)),
                    f"manifest SHA-256 mismatch: {name}")
            require(row["integrity_note"] == "",
                    f"unexpected manifest integrity note: {name}")
    return len(rows)


def require_regular_file(root: Path, relative: str) -> Path:
    canonical = payload_path(relative, f"required file {relative}")
    path = root / PurePosixPath(canonical)
    require(path.is_file() and not path.is_symlink(), f"required file is absent: {relative}")
    require(path.stat().st_size > 0, f"required file is empty: {relative}")
    return path


def require_directory(root: Path, relative: str) -> Path:
    canonical = payload_path(relative, f"required directory {relative}")
    path = root / PurePosixPath(canonical)
    require(path.is_dir() and not path.is_symlink(), f"required directory is absent: {relative}")
    return path


def validate_required_tree(
    root: Path,
    audit_failure: dict[str, Any] | None,
) -> None:
    for directory in (
        "commission",
        "environment",
        "work/analysis",
        "work/r2_source",
        "work/input/wp02",
        "work/final_analysis",
        "work/final_analysis/validation",
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
    ):
        require_directory(root, directory)
    for name in (*REQUIRED_SOURCE_FILES, *REQUIRED_LIVE_INPUTS, *REQUIRED_COMMISSION_FILES):
        require_regular_file(root, name)
    validation_files = (
        INCOMPLETE_PRESENT_VALIDATION_FILES
        if audit_failure is not None
        else REQUIRED_VALIDATION_FILES
    )
    for name in validation_files:
        require_regular_file(root, f"work/final_analysis/validation/{name}")
    if audit_failure is not None:
        require_regular_file(root, LAST_AUDIT_FAILURE_PATH)
    require_regular_file(root, f"work/final_release/{FINAL_STOWED}")
    require_regular_file(root, f"work/final_release/{FINAL_DEPLOYED}")
    require_regular_file(root, "work/final_analysis/authoring_manifest.json")
    require_regular_file(root, "work/final_analysis/authoring_inventory_stowed.json")
    require_regular_file(root, "work/final_analysis/authoring_inventory_deployed.json")
    for name in (
        "environment/RUNTIME_VERSIONS.json",
        "environment/PYTHON_PACKAGES_FULLY_PINNED.json",
        "environment/PYTHON_REQUIREMENTS_FULLY_PINNED.txt",
        "environment/PYTHON_PIP_FREEZE_RAW.txt",
        "environment/NODE_PACKAGES_FULLY_PINNED.csv",
    ):
        require_regular_file(root, name)
    active_suffixes = {".py", ".mjs", ".js", ".sh"}
    actual_r2_scripts = {
        path.relative_to(root).as_posix()
        for path in (root / "work/r2_source").rglob("*")
        if path.is_file() and path.suffix.lower() in active_suffixes
    }
    expected_r2_scripts = {
        name
        for name in REQUIRED_SOURCE_FILES
        if name.startswith("work/r2_source/")
    }
    require(actual_r2_scripts == expected_r2_scripts,
            "authoritative r2_source active-script set is not exact: "
            f"missing={sorted(expected_r2_scripts - actual_r2_scripts)}, "
            f"extra={sorted(actual_r2_scripts - expected_r2_scripts)}")
    wp02_root = root / "work/input/wp02"
    for expected in REQUIRED_LIVE_INPUTS:
        basename = PurePosixPath(expected).name
        matches = sorted(path for path in wp02_root.rglob(basename) if path.is_file())
        require(len(matches) == 1 and matches[0] == root / PurePosixPath(expected),
                f"live WP02 input identity is missing or duplicated: {basename}")


def validate_merged_motion_csv(
    path: Path,
    expected_sample_count: int,
    classification_by_occurrence: dict[str, str],
) -> dict[str, Any]:
    sample_angles: dict[int, int] = {}
    rows_per_sample: Counter[int] = Counter()
    result_counts: Counter[str] = Counter()
    common_status_counts: Counter[str] = Counter()
    distance_status_counts: Counter[str] = Counter()
    fit_id_counts: Counter[str] = Counter()
    unauthorized_pairs: set[tuple[str, str, str, str, str, str, str, str]] = set()
    rigid_unauthorized_pairs: set[tuple[str, str, str, str, str, str, str, str]] = set()
    nonrigid_unauthorized_pairs: set[tuple[str, str, str, str, str, str, str, str]] = set()
    unauthorized_classification_counts: Counter[str] = Counter()
    unauthorized_angles: set[int] = set()
    category_b_observation_count = 0
    nonrigid_observation_count = 0
    classification_join_missing_count = 0
    nonempty_error_count = 0
    row_count = 0
    try:
        with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            require(tuple(reader.fieldnames or ()) == EXPECTED_MERGED_MOTION_FIELDS,
                    "merged motion CSV header is not the exact 20-column schema")
            for row_number, row in enumerate(reader, start=2):
                require(None not in row,
                        f"merged motion CSV row {row_number} has extra columns")
                try:
                    sample_index = int(row.get("sample_index", ""))
                    angle_deg = int(row.get("angle_deg", ""))
                except (TypeError, ValueError) as exc:
                    raise ValidationFailure(
                        f"merged motion CSV row {row_number} has noninteger sample identity"
                    ) from exc
                require(1 <= sample_index <= expected_sample_count,
                        f"merged motion CSV row {row_number} sample index is out of range")
                require(angle_deg == sample_index - 1,
                        f"merged motion CSV row {row_number} sample/angle mapping is invalid")
                previous = sample_angles.setdefault(sample_index, angle_deg)
                require(previous == angle_deg,
                        f"merged motion CSV sample {sample_index} has conflicting angles")
                rows_per_sample[sample_index] += 1
                result = str(row.get("result", ""))
                result_counts[result] += 1
                common_status_counts[str(row.get("exact_common_status", ""))] += 1
                distance_status_counts[str(row.get("exact_distance_status", ""))] += 1
                fit_id = str(row.get("intentional_fit_exception_id", ""))
                if fit_id:
                    fit_id_counts[fit_id] += 1
                if str(row.get("error", "")):
                    nonempty_error_count += 1
                if result == "UNAUTHORIZED_POSITIVE_VOLUME":
                    unauthorized_angles.add(angle_deg)
                    occurrence_a = str(row.get("occurrence_a", ""))
                    occurrence_b = str(row.get("occurrence_b", ""))
                    pair_identity = (
                        occurrence_a,
                        str(row.get("solid_index_a", "")),
                        str(row.get("variant_a", "")),
                        str(row.get("part_number_a", "")),
                        occurrence_b,
                        str(row.get("solid_index_b", "")),
                        str(row.get("variant_b", "")),
                        str(row.get("part_number_b", "")),
                    )
                    unauthorized_pairs.add(pair_identity)
                    classification_a = classification_by_occurrence.get(occurrence_a)
                    classification_b = classification_by_occurrence.get(occurrence_b)
                    if classification_a is None or classification_b is None:
                        classification_join_missing_count += 1
                    else:
                        classification_key = "_".join(
                            sorted((classification_a, classification_b))
                        )
                        unauthorized_classification_counts[classification_key] += 1
                        if {classification_a, classification_b} <= {"FIXED", "MOVING"}:
                            category_b_observation_count += 1
                            rigid_unauthorized_pairs.add(pair_identity)
                        else:
                            nonrigid_observation_count += 1
                            nonrigid_unauthorized_pairs.add(pair_identity)
                row_count += 1
    except (OSError, EOFError, gzip.BadGzipFile, UnicodeError, csv.Error) as exc:
        raise ValidationFailure("merged motion CSV is unreadable, truncated, or invalid") from exc
    require(row_count > 0, "merged motion CSV contains no audit rows")
    require(row_count == EXPECTED_MERGED_MOTION_DATA_ROWS,
            "merged motion CSV row count differs from the observed completed merge")
    require(sorted(sample_angles) == list(range(1, expected_sample_count + 1)),
            "merged motion CSV does not contain every completed sample 1..81")
    require(sorted(sample_angles.values()) == list(range(expected_sample_count)),
            "merged motion CSV does not contain every exact angle 0..80 degrees")
    require(set(rows_per_sample.values()) == {17_875},
            "merged motion CSV does not contain exactly 17,875 rows per sample")
    require(dict(result_counts) == {
                "CLEAR_OR_CONTACT": 1_445_811,
                "DOCUMENTED_POSITIVE_VOLUME": 1_215,
                "UNAUTHORIZED_POSITIVE_VOLUME": 849,
            },
            "merged motion result counts differ from the observed terminal merge")
    require(dict(common_status_counts) == {
                "NOT_RUN_AABB_SEPARATED": 1_413_561,
                "DONE": 34_314,
            },
            "merged motion exact-common status counts differ from the observed merge")
    require(dict(distance_status_counts) == {
                "NOT_RUN_OUTSIDE_NEAR_LIMIT": 1_398_156,
                "DONE": 47_655,
                "ZERO_BY_POSITIVE_COMMON": 2_064,
            },
            "merged motion exact-distance status counts differ from the observed merge")
    require(nonempty_error_count == 0,
            "merged motion CSV contains unexpected nonempty error rows")
    require(len(fit_id_counts) == 15 and set(fit_id_counts.values()) == {81},
            "merged motion CSV does not use exactly 15 fit IDs at all 81 samples")
    require(len(unauthorized_pairs) == 39,
            "merged motion CSV does not preserve the exact 39 unauthorized pair identities")
    require(classification_join_missing_count == 0,
            "merged motion unauthorized rows do not all join to state-parity classifications")
    require(category_b_observation_count == 681
            and len(rigid_unauthorized_pairs) == 33,
            "merged motion Category-B rigid counts differ from observed evidence")
    require(nonrigid_observation_count == 168
            and len(nonrigid_unauthorized_pairs) == 6,
            "merged motion nonrigid unauthorized counts differ from observed evidence")
    require(dict(unauthorized_classification_counts) == {
                "FIXED_MOVING": 516,
                "MOVING_MOVING": 165,
                "FLEXIBLE_MOVING": 168,
            },
            "merged motion unauthorized classification breakdown is not exact")
    require(unauthorized_angles == set(range(3, 23)) | set(range(36, 80)),
            "merged motion unauthorized-angle set differs from observed evidence")
    return {
        "row_count": row_count,
        "sample_count": len(sample_angles),
        "rows_per_sample": 17_875,
        "result_counts": dict(sorted(result_counts.items())),
        "common_status_counts": dict(sorted(common_status_counts.items())),
        "distance_status_counts": dict(sorted(distance_status_counts.items())),
        "nonempty_error_count": nonempty_error_count,
        "fit_id_count": len(fit_id_counts),
        "fit_id_uses_each": 81,
        "unauthorized_row_count": result_counts["UNAUTHORIZED_POSITIVE_VOLUME"],
        "unauthorized_unique_pair_count": len(unauthorized_pairs),
        "category_b_observation_count": category_b_observation_count,
        "category_b_unique_pair_count": len(rigid_unauthorized_pairs),
        "nonrigid_unauthorized_observation_count": nonrigid_observation_count,
        "nonrigid_unauthorized_unique_pair_count": len(nonrigid_unauthorized_pairs),
        "classification_join_missing_count": classification_join_missing_count,
        "unauthorized_classification_counts": dict(
            sorted(unauthorized_classification_counts.items())
        ),
        "unauthorized_angle_count": len(unauthorized_angles),
        "unauthorized_angles": sorted(unauthorized_angles),
    }


def load_occurrence_classifications(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames is not None
                    and "occurrence_id" in reader.fieldnames
                    and "classification" in reader.fieldnames,
                    "state_parity.csv lacks occurrence/classification columns")
            for row_number, row in enumerate(reader, start=2):
                occurrence_id = str(row.get("occurrence_id", ""))
                classification = str(row.get("classification", "")).upper()
                require(occurrence_id and classification,
                        f"state_parity.csv row {row_number} has blank classification identity")
                require(occurrence_id not in result,
                        f"state_parity.csv duplicates occurrence {occurrence_id}")
                result[occurrence_id] = classification
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValidationFailure("state_parity.csv classification map is unreadable") from exc
    require(result, "state_parity.csv classification map is empty")
    return result


def validate_last_audit_failure(root: Path) -> dict[str, Any] | None:
    path = root / LAST_AUDIT_FAILURE_PATH
    if not path.exists():
        return None
    require(path.is_file() and not path.is_symlink(),
            "LAST_AUDIT_FAILURE is not a regular non-symlink file")
    record = load_json_object(path, "last audit failure")
    require(set(record) == LAST_AUDIT_FAILURE_FIELDS,
            "LAST_AUDIT_FAILURE top-level field set is not exact")
    require(record.get("schema") == "DF8_CODEX_LAST_AUDIT_FAILURE_V1",
            "LAST_AUDIT_FAILURE schema is not V1")
    recorded_at = record.get("recorded_at_utc")
    require(isinstance(recorded_at, str) and recorded_at.endswith("Z"),
            "LAST_AUDIT_FAILURE recorded_at_utc is not UTC-Z")
    try:
        parsed = dt.datetime.fromisoformat(recorded_at[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationFailure("LAST_AUDIT_FAILURE recorded_at_utc is invalid") from exc
    require(parsed.utcoffset() == dt.timedelta(0),
            "LAST_AUDIT_FAILURE recorded_at_utc is not UTC")
    command = record.get("command")
    require(isinstance(command, str) and command.strip(),
            "LAST_AUDIT_FAILURE command is blank")
    reject_unavailable_operational_paths(command, "LAST_AUDIT_FAILURE command")
    require(LIVE_MOTION_SHARD.search(command) is None,
            "LAST_AUDIT_FAILURE command relies on a live motion shard")
    require(type(record.get("exit_code")) is int and record["exit_code"] == 1,
            "LAST_AUDIT_FAILURE exit_code is not exactly 1")
    require(record.get("exception_type") == "KeyError",
            "LAST_AUDIT_FAILURE exception_type is not KeyError")
    require(record.get("exception_message") == "'angle_deg'",
            "LAST_AUDIT_FAILURE exception_message is not exact")
    require(record.get("failure_stage") ==
            "POST_MERGE_MOTION_KINEMATICS_SCHEMA_CHECK",
            "LAST_AUDIT_FAILURE stage is not exact")
    require(type(record.get("completed_motion_sample_count")) is int
            and record["completed_motion_sample_count"] == 81,
            "LAST_AUDIT_FAILURE does not prove 81 completed samples")
    require(record.get("present_validation_files") ==
            list(INCOMPLETE_PRESENT_VALIDATION_FILES),
            "LAST_AUDIT_FAILURE present-file list is not the exact sorted 23-file set")
    require(record.get("missing_validation_files") ==
            list(INCOMPLETE_MISSING_VALIDATION_FILES),
            "LAST_AUDIT_FAILURE missing-file list is not the exact sorted 5-file set")
    require(record.get("release_authorized") is False,
            "LAST_AUDIT_FAILURE incorrectly authorizes release")
    require(sha256_file(root / "work/r2_source/validate_r2.py") ==
            EXPECTED_FAILED_VALIDATOR_SHA256,
            "extracted validator source differs from the source that raised the recorded failure")
    merged = record.get("merged_motion_audit")
    require(isinstance(merged, dict)
            and set(merged) == {"path", "size_bytes", "sha256"},
            "LAST_AUDIT_FAILURE merged-motion record field set is not exact")
    merged_relative = "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz"
    require(merged.get("path") == merged_relative,
            "LAST_AUDIT_FAILURE merged-motion path is not exact relative path")
    require(merged.get("size_bytes") == EXPECTED_MERGED_MOTION_SIZE,
            "LAST_AUDIT_FAILURE merged-motion size differs from the observed merged audit")
    require(merged.get("sha256") == EXPECTED_MERGED_MOTION_SHA256,
            "LAST_AUDIT_FAILURE merged-motion SHA differs from the observed merged audit")
    merged_path = root / merged_relative
    verify_hash_record(merged_path, merged, "LAST_AUDIT_FAILURE merged motion audit")
    motion_verification = validate_merged_motion_csv(
        merged_path,
        record["completed_motion_sample_count"],
        load_occurrence_classifications(
            root / "work/final_analysis/validation/state_parity.csv"
        ),
    )
    return {"record": record, "motion_verification": motion_verification}


def validate_commission_provenance(root: Path) -> None:
    provenance = load_json_object(
        root / "commission/PROVENANCE.json", "commission provenance"
    )
    require(provenance.get("schema") == "DF8_HANDOFF_COMMISSION_PROVENANCE_V1",
            "commission provenance schema is not V1")
    records = provenance.get("records")
    require(isinstance(records, list) and len(records) == 3
            and all(isinstance(row, dict) for row in records),
            "commission provenance must contain exactly three records")
    expected_staged = set(REQUIRED_COMMISSION_FILES) - {"commission/PROVENANCE.json"}
    actual_staged = [str(row.get("staged_path", "")) for row in records]
    require(len(set(actual_staged)) == 3 and set(actual_staged) == expected_staged,
            "commission provenance staged-path set is not exact")
    for index, row in enumerate(records):
        staged = payload_path(
            str(row.get("staged_path", "")), f"commission provenance row {index} staged_path"
        )
        source = payload_path(
            str(row.get("workspace_source", "")),
            f"commission provenance row {index} workspace_source",
        )
        require(source == row["workspace_source"],
                f"commission provenance row {index} workspace_source is noncanonical")
        target = root / PurePosixPath(staged)
        verify_hash_record(target, row, f"commission provenance row {index}")
        require(isinstance(row.get("role"), str) and row["role"].strip(),
                f"commission provenance row {index} role is blank")
        require(isinstance(row.get("uploaded_filename"), str)
                and row["uploaded_filename"].strip(),
                f"commission provenance row {index} uploaded_filename is blank")


def validate_environment_manifests(root: Path) -> dict[str, Any]:
    environment = root / "environment"
    runtime = load_json_object(environment / "RUNTIME_VERSIONS.json", "runtime versions")
    require(runtime.get("schema") == "DF8_HANDOFF_RUNTIME_VERSIONS_V1",
            "runtime versions schema is not V1")
    python_manifest = load_json_object(
        environment / "PYTHON_PACKAGES_FULLY_PINNED.json", "pinned Python packages"
    )
    require(python_manifest.get("schema") == "DF8_HANDOFF_PINNED_PYTHON_PACKAGES_V1",
            "pinned Python package schema is not V1")
    python_packages = python_manifest.get("packages")
    require(isinstance(python_packages, list) and python_packages
            and all(isinstance(row, dict) for row in python_packages),
            "pinned Python package list is empty or invalid")
    expected_requirements: list[str] = []
    python_identities: set[tuple[str, str]] = set()
    for index, row in enumerate(python_packages):
        name = row.get("name")
        version = row.get("version")
        require(isinstance(name, str) and name.strip()
                and isinstance(version, str) and version.strip(),
                f"pinned Python package row {index} is incomplete")
        identity = (name.casefold(), version)
        require(identity not in python_identities,
                f"duplicate pinned Python package identity: {name}=={version}")
        python_identities.add(identity)
        expected_requirements.append(f"{name}=={version}")
    requirements_path = environment / "PYTHON_REQUIREMENTS_FULLY_PINNED.txt"
    require(requirements_path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
            "Python requirements exceeds structured-text safety limit")
    requirements = requirements_path.read_text(encoding="utf-8").splitlines()
    require(requirements == expected_requirements,
            "Python requirements do not exactly reproduce the pinned package JSON")
    freeze_path = environment / "PYTHON_PIP_FREEZE_RAW.txt"
    require(freeze_path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
            "pip-freeze record exceeds structured-text safety limit")
    require(any(line.strip() for line in freeze_path.read_text(encoding="utf-8").splitlines()),
            "pip-freeze record is empty")

    node_path = environment / "NODE_PACKAGES_FULLY_PINNED.csv"
    require(node_path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
            "Node package CSV exceeds structured-text safety limit")
    try:
        reader = csv.DictReader(io.StringIO(node_path.read_text(encoding="utf-8"), newline=""))
        require(tuple(reader.fieldnames or ()) ==
                ("install_path", "name", "version", "package_json_sha256"),
                "Node package CSV header is not exact")
        node_packages = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValidationFailure("Node package CSV is unreadable or invalid") from exc
    require(node_packages, "Node package inventory is empty")
    node_identities: set[tuple[str, str, str]] = set()
    for index, row in enumerate(node_packages):
        require(None not in row and all(isinstance(value, str) and value for value in row.values()),
                f"Node package row {index + 2} is incomplete")
        require(SHA_VALUE.fullmatch(row["package_json_sha256"]) is not None,
                f"Node package row {index + 2} has invalid package.json SHA-256")
        install_path = payload_path(
            row["install_path"], f"Node package row {index + 2} install_path"
        )
        identity = (install_path, row["name"], row["version"])
        require(identity not in node_identities,
                f"duplicate Node package inventory identity: {identity}")
        node_identities.add(identity)
    require(any(row["name"] == "@oai/artifact-tool" for row in node_packages),
            "@oai/artifact-tool is absent from the Node package inventory")
    return {
        "runtime_versions": runtime,
        "python_packages": python_packages,
        "node_packages": node_packages,
    }


def parse_all_python_sources(root: Path, all_files: set[str]) -> list[str]:
    primary_roots = (
        "work/r2_source/",
        "work/final_tools/",
        "work/scripts/",
        "work/handoff_tools/",
    )
    python_files = sorted(
        name
        for name in all_files
        if PurePosixPath(name).suffix.lower() == ".py"
        and any(name.startswith(prefix) for prefix in primary_roots)
    )
    require(python_files, "handoff contains no Python source files")
    for name in python_files:
        path = root / PurePosixPath(name)
        try:
            require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                    f"Python source exceeds AST safety limit: {name}")
            with tokenize.open(path) as stream:
                source = stream.read()
            ast.parse(source, filename=name, mode="exec", type_comments=True)
        except (OSError, UnicodeError, SyntaxError) as exc:
            raise ValidationFailure(f"Python AST parse failed for {name}: {exc}") from exc
    forbidden_bytecode = sorted(
        name for name in all_files if PurePosixPath(name).suffix.lower() in {".pyc", ".pyo"}
    )
    require(not forbidden_bytecode, f"bytecode files are forbidden: {forbidden_bytecode}")
    return python_files


def literal_module_assignment(tree: ast.Module, name: str, label: str) -> Any:
    values: list[ast.expr] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            values.append(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
        ):
            values.append(node.value)
    require(len(values) == 1, f"{label} must be defined exactly once")
    try:
        return ast.literal_eval(values[0])
    except (ValueError, TypeError) as exc:
        raise ValidationFailure(f"{label} is not a literal value") from exc


def validate_extracted_source_contract(root: Path) -> dict[str, Any]:
    validator_path = root / "work/r2_source/validate_r2.py"
    try:
        with tokenize.open(validator_path) as stream:
            validator_source = stream.read()
        validator_tree = ast.parse(
            validator_source,
            filename="work/r2_source/validate_r2.py",
            mode="exec",
            type_comments=True,
        )
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise ValidationFailure("extracted validate_r2.py source contract is unreadable") from exc

    gate_ids = literal_module_assignment(
        validator_tree, "EXPECTED_GATE_IDS", "extracted EXPECTED_GATE_IDS"
    )
    require(isinstance(gate_ids, (tuple, list)),
            "extracted EXPECTED_GATE_IDS is not a literal sequence")
    require(tuple(gate_ids) == EXPECTED_GATE_IDS,
            "extracted EXPECTED_GATE_IDS differs from the frozen handoff contract")
    creo_disposition = literal_module_assignment(
        validator_tree,
        "CREO_ENVIRONMENT_DISPOSITION",
        "extracted CREO_ENVIRONMENT_DISPOSITION",
    )
    require(creo_disposition == CREO_DISPOSITION,
            "extracted validator Creo disposition is not the controlling informational N/A text")

    build_path = root / "work/r2_source/build_r2.py"
    try:
        with tokenize.open(build_path) as stream:
            build_source = stream.read()
    except (OSError, UnicodeError) as exc:
        raise ValidationFailure("extracted build_r2.py is unreadable") from exc
    input_reference_counts: dict[str, int] = {}
    for relative in REQUIRED_LIVE_INPUTS:
        basename = PurePosixPath(relative).name
        count = build_source.count(basename)
        require(count == 1,
                f"extracted build_r2.py must reference WP02 basename exactly once: {basename}")
        input_reference_counts[basename] = count
    return {
        "expected_gate_id_count": len(gate_ids),
        "creo_disposition_bound": True,
        "wp02_build_reference_counts": input_reference_counts,
    }


def reject_unavailable_operational_paths(text: str, label: str) -> None:
    hits = [prefix for prefix in UNAVAILABLE_OPERATIONAL_PREFIXES if prefix in text]
    require(not hits, f"{label} contains unavailable operational path prefix(es): {hits}")


def validate_current_state_command_paths(state: dict[str, Any]) -> int:
    command_strings: list[tuple[str, str]] = []

    def walk(value: Any, path: tuple[str, ...], command_context: bool = False) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                walk(
                    child,
                    (*path, key_text),
                    command_context or "command" in key_text.casefold(),
                )
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, (*path, str(index)), command_context)
        elif isinstance(value, str) and command_context:
            command_strings.append((".".join(path), value))

    walk(state, ("CURRENT_STATE",))
    require(command_strings, "CURRENT_STATE contains no command strings to validate")
    for path, command in command_strings:
        reject_unavailable_operational_paths(command, path)
        require(LIVE_MOTION_SHARD.search(command) is None,
                f"{path} relies on a live motion shard")
    return len(command_strings)


def validate_executable_fenced_blocks(path: Path, label: str) -> int:
    try:
        require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                f"{label} exceeds structured-text safety limit")
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationFailure(f"{label} is unreadable or not UTF-8") from exc
    executable_count = 0
    for index, match in enumerate(EXECUTABLE_FENCE.finditer(text), start=1):
        language = match.group(1).strip().split(maxsplit=1)[0].casefold()
        if language not in {"bash", "sh", "shell", "zsh"}:
            continue
        executable_count += 1
        block = match.group(2)
        reject_unavailable_operational_paths(block, f"{label} executable block {index}")
        require(LIVE_MOTION_SHARD.search(block) is None,
                f"{label} executable block {index} relies on a live motion shard")
    require(executable_count > 0, f"{label} contains no executable fenced command blocks")
    return executable_count


def verify_hash_record(path: Path, record: object, label: str) -> None:
    require(isinstance(record, dict), f"{label} is absent or not an object")
    size = record.get("size_bytes")
    digest = record.get("sha256")
    require(type(size) is int and size >= 0, f"{label} size_bytes is invalid")
    require(isinstance(digest, str) and SHA_VALUE.fullmatch(digest) is not None,
            f"{label} SHA-256 is invalid")
    require(path.is_file() and not path.is_symlink(), f"{label} target is absent")
    require(path.stat().st_size == size, f"{label} size mismatch")
    require(sha256_file(path) == digest, f"{label} SHA-256 mismatch")


def validate_authoring_manifest(root: Path) -> dict[str, Any]:
    manifest = load_json_object(
        root / "work/final_analysis/authoring_manifest.json", "authoring manifest"
    )
    require(manifest.get("schema") == "AP242", "authoring manifest schema is not exactly AP242")
    files = manifest.get("files")
    inventories = manifest.get("inventories")
    require(isinstance(files, dict), "authoring manifest files is not an object")
    require(isinstance(inventories, dict), "authoring manifest inventories is not an object")
    expected_files = {FINAL_STOWED, FINAL_DEPLOYED}
    expected_inventories = {
        "authoring_inventory_stowed.json",
        "authoring_inventory_deployed.json",
    }
    require(set(files) == expected_files, "authoring manifest STEP set is not exact")
    require(set(inventories) == expected_inventories,
            "authoring manifest inventory set is not exact")
    for name in sorted(expected_files):
        verify_hash_record(root / "work/final_release" / name, files[name], f"STEP record {name}")
    for name in sorted(expected_inventories):
        verify_hash_record(
            root / "work/final_analysis" / name,
            inventories[name],
            f"inventory record {name}",
        )
    return manifest


def validate_validation_bundle(root: Path) -> dict[str, Any]:
    validation_root = root / "work/final_analysis/validation"
    actual_nodes = sorted(validation_root.iterdir(), key=lambda path: path.name)
    actual_names = {path.name for path in actual_nodes}
    expected_names = set(REQUIRED_VALIDATION_FILES)
    require(actual_names == expected_names,
            "validation top-level file set is not exact: "
            f"missing={sorted(expected_names - actual_names)}, "
            f"extra={sorted(actual_names - expected_names)}")
    for path in actual_nodes:
        metadata = path.lstat()
        require(stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode),
                f"validation top-level node is not a regular file: {path.name}")

    validation_manifest = load_json_object(
        validation_root / "validation_manifest.json", "validation manifest"
    )
    records = validation_manifest.get("files")
    require(isinstance(records, dict), "validation manifest files is not an object")
    bound_paths: dict[str, Path] = {
        name: validation_root / name
        for name in REQUIRED_VALIDATION_FILES
        if name != "validation_manifest.json"
    }
    bound_paths.update(
        {
            FINAL_STOWED: root / "work/final_release" / FINAL_STOWED,
            FINAL_DEPLOYED: root / "work/final_release" / FINAL_DEPLOYED,
            "authoring_inventory_stowed.json": (
                root / "work/final_analysis/authoring_inventory_stowed.json"
            ),
            "authoring_inventory_deployed.json": (
                root / "work/final_analysis/authoring_inventory_deployed.json"
            ),
            "authoring_manifest.json": root / "work/final_analysis/authoring_manifest.json",
            "validate_r2.py": root / "work/r2_source/validate_r2.py",
        }
    )
    require(len(bound_paths) == 33 and set(records) == set(bound_paths),
            "validation manifest is not the exact 33-key set: "
            f"missing={sorted(set(bound_paths) - set(records))}, "
            f"extra={sorted(set(records) - set(bound_paths))}")
    for name, path in sorted(bound_paths.items()):
        verify_hash_record(path, records[name], f"validation manifest record {name}")

    gates = load_json_object(validation_root / "gate_results.json", "gate results")
    rows = gates.get("gates")
    require(isinstance(rows, list) and len(rows) == len(EXPECTED_GATE_IDS),
            "gate_results does not contain the exact frozen 31-row gate set")
    require(all(isinstance(row, dict) for row in rows), "gate_results has a non-object row")
    gate_ids = tuple(str(row.get("gate_id", "")) for row in rows)
    require(gate_ids == EXPECTED_GATE_IDS,
            "gate IDs/order disagree with the frozen handoff contract")
    statuses = [row.get("status") for row in rows]
    require(all(status in VALID_GATE_STATUSES for status in statuses),
            "gate_results contains an invalid gate status")
    counts = {
        status: sum(value == status for value in statuses)
        for status in ("PASS", "FAIL", "BLOCKED")
    }
    release_status = (
        "PASS" if counts["FAIL"] == 0 and counts["BLOCKED"] == 0
        else "NOT_RELEASED"
    )
    package_label = (
        "FINAL — RELEASED" if release_status == "PASS"
        else "CORRECTIVE VALIDATION FAILED — NOT RELEASED"
    )
    require(gates.get("gate_counts") == counts,
            "gate_results gate_counts disagree with recomputed rows")
    require(gates.get("computed_release_status") == release_status,
            "gate_results release status disagrees with recomputed rows")
    require(gates.get("package_required_label") == package_label,
            "gate_results package label disagrees with recomputed rows")
    require(gates.get("informational_environment_items") == [CREO_INFORMATIONAL_ITEM],
            "Creo informational N/A item is absent, altered, duplicated, or acceptance-bearing")

    summary = load_json_object(validation_root / "validation_summary.json", "validation summary")
    require(summary.get("validation_status") == release_status,
            "validation summary status disagrees with recomputed gates")
    require(summary.get("required_package_label") == package_label,
            "validation summary package label disagrees with recomputed gates")
    require(summary.get("gate_counts") == counts,
            "validation summary counts disagree with recomputed gates")
    require(summary.get("informational_environment_items") == [CREO_INFORMATIONAL_ITEM],
            "validation summary Creo informational item is not exact")

    status_by_gate = dict(zip(EXPECTED_GATE_IDS, statuses))
    ncr_statuses: dict[str, str] = {}
    for ncr_id, controlling in NCR_GATE_MAP.items():
        controlling_statuses = [status_by_gate[gate_id] for gate_id in controlling]
        if all(status == "PASS" for status in controlling_statuses):
            ncr_statuses[ncr_id] = "CLOSED"
        elif "FAIL" in controlling_statuses:
            ncr_statuses[ncr_id] = "OPEN"
        else:
            ncr_statuses[ncr_id] = "BLOCKED"
    return {
        "execution_state": "COMPLETED_VALIDATION",
        "validation_manifest": validation_manifest,
        "gates": gates,
        "summary": summary,
        "gate_rows": rows,
        "gate_counts": counts,
        "release_status": release_status,
        "package_label": package_label,
        "ncr_statuses": ncr_statuses,
    }


def validate_incomplete_validation_bundle(
    root: Path,
    audit_failure: dict[str, Any],
) -> dict[str, Any]:
    validation_root = root / "work/final_analysis/validation"
    actual_nodes = sorted(validation_root.iterdir(), key=lambda path: path.name)
    actual_names = {path.name for path in actual_nodes}
    expected_names = set(INCOMPLETE_PRESENT_VALIDATION_FILES)
    require(actual_names == expected_names,
            "incomplete validation top-level file set is not exact: "
            f"missing={sorted(expected_names - actual_names)}, "
            f"extra={sorted(actual_names - expected_names)}")
    for path in actual_nodes:
        metadata = path.lstat()
        require(stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode),
                f"incomplete validation node is not a regular file: {path.name}")
    for name in INCOMPLETE_MISSING_VALIDATION_FILES:
        require(not (validation_root / name).exists(),
                f"fabricated post-failure validation output is present: {name}")
    require(audit_failure["present_validation_files"] == sorted(actual_names),
            "failure record present-file set disagrees with extracted validation tree")
    require(audit_failure["missing_validation_files"] ==
            list(INCOMPLETE_MISSING_VALIDATION_FILES),
            "failure record missing-file set disagrees with the incomplete contract")
    gate_rows = [
        {
            "gate_id": gate_id,
            "status": "NOT_COMPUTED",
            "handoff_disposition": "OPEN",
            "basis": "gate_results.json absent after terminal validator failure",
        }
        for gate_id in EXPECTED_GATE_IDS
    ]
    ncr_statuses = {ncr_id: "NOT_COMPUTED" for ncr_id in NCR_GATE_MAP}
    return {
        "execution_state": "TERMINAL_AUDIT_FAILURE",
        "validation_manifest": None,
        "gates": None,
        "summary": None,
        "gate_rows": gate_rows,
        "gate_counts": None,
        "release_status": INCOMPLETE_RELEASE_STATUS,
        "package_label": INCOMPLETE_PACKAGE_LABEL,
        "ncr_statuses": ncr_statuses,
        "audit_failure": audit_failure,
    }


def get_nested(value: dict[str, Any], keys: tuple[str, ...], label: str) -> Any:
    current: Any = value
    for key in keys:
        require(isinstance(current, dict) and key in current, f"CURRENT_STATE lacks {label}")
        current = current[key]
    return current


def validate_relative_resume_target(
    root: Path,
    value: object,
    label: str,
    *,
    kind: str = "file",
) -> None:
    require(isinstance(value, str), f"{label} is not a string")
    require(OLD_WORKSPACE.search(value) is None, f"{label} relies on old absolute workspace")
    require(LIVE_MOTION_SHARD.search(value) is None, f"{label} relies on a live motion shard")
    canonical = payload_path(value, label)
    require(canonical == value, f"{label} is not canonical relative path")
    path = root / PurePosixPath(canonical)
    if kind == "directory":
        require(path.is_dir() and not path.is_symlink(), f"{label} target directory is absent")
    else:
        require(path.is_file() and not path.is_symlink(), f"{label} target file is absent")


def validate_current_state_and_resume(
    root: Path,
    validation_bundle: dict[str, Any],
    environment_bundle: dict[str, Any],
    audit_failure_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    state = load_json_object(root / "CURRENT_STATE.json", "CURRENT_STATE")
    incomplete = audit_failure_bundle is not None
    require(state.get("schema") == "DF8_CODEX_HANDOFF_CURRENT_STATE_V2",
            "CURRENT_STATE schema is not V2")
    require(state.get("checkpoint_root") == ".", "CURRENT_STATE checkpoint_root must be '.'")
    if incomplete:
        require(state.get("current_execution_phase") ==
                "terminal validator failure preservation and atomic safe-handoff packaging",
                "CURRENT_STATE does not identify terminal-audit-failure handoff packaging")
        require(state.get("latest_completed_checkpoint") ==
                "manifest-bound final authoring masters plus 81 completed exact-motion "
                "samples merged in work/final_analysis/validation/"
                "motion_full_mechanism_audit.csv.gz; post-merge gate/NCR outputs were "
                "not computed",
                "CURRENT_STATE does not identify the completed merged motion checkpoint")
    else:
        require(state.get("current_execution_phase") ==
                "completed-validator evidence preservation and atomic safe-handoff packaging",
                "CURRENT_STATE execution phase is absent or unexpected")
        require(isinstance(state.get("latest_completed_checkpoint"), str)
                and "work/final_analysis/validation" in state["latest_completed_checkpoint"],
                "CURRENT_STATE latest completed checkpoint is absent or non-specific")
    require(state.get("authoritative_source") == "work/r2_source",
            "CURRENT_STATE authoritative_source is not the exact relative source tree")
    validate_relative_resume_target(
        root, state["authoritative_source"], "CURRENT_STATE authoritative_source", kind="directory"
    )

    required_state_paths = (
        (("authoring", "manifest"), "CURRENT_STATE authoring manifest"),
        (("last_execution_record",), "CURRENT_STATE last-execution record"),
        (("dependency_capture", "runtime_versions"), "CURRENT_STATE runtime versions"),
        (("dependency_capture", "python_pins"), "CURRENT_STATE Python pins"),
        (("dependency_capture", "node_pins"), "CURRENT_STATE Node pins"),
    ) + (
        (
            (("validation", "last_audit_failure"), "CURRENT_STATE last audit failure"),
        )
        if incomplete
        else (
            (("validation", "validation_summary"), "CURRENT_STATE validation summary"),
            (("validation", "gate_results"), "CURRENT_STATE gate results"),
            (("validation", "validation_manifest"), "CURRENT_STATE validation manifest"),
        )
    )
    for keys, label in required_state_paths:
        validate_relative_resume_target(root, get_nested(state, keys, label), label)

    live_inputs = state.get("live_build_inputs")
    require(live_inputs == list(REQUIRED_LIVE_INPUTS),
            "CURRENT_STATE live_build_inputs is not the exact two-file WP02 set")
    for index, value in enumerate(live_inputs):
        validate_relative_resume_target(root, value, f"CURRENT_STATE live_build_inputs[{index}]")

    last_execution = load_json_object(
        root / "work/handoff_tools/LAST_EXECUTION_RECORD.json", "last execution record"
    )
    require(last_execution.get("schema") == "DF8_CODEX_LAST_EXECUTION_RECORD_V1",
            "LAST_EXECUTION_RECORD schema is not V1")
    for field in (
        "last_command",
        "last_successful_modifying_command",
        "last_successful_audit_command",
    ):
        record = last_execution.get(field)
        require(isinstance(record, dict), f"LAST_EXECUTION_RECORD {field} is absent")
        require(isinstance(record.get("command"), str) and record["command"].strip(),
                f"LAST_EXECUTION_RECORD {field}.command is blank")
        require(type(record.get("exit_code")) is int,
                f"LAST_EXECUTION_RECORD {field}.exit_code is not an integer")
        if field.startswith("last_successful_"):
            require(record["exit_code"] == 0,
                    f"LAST_EXECUTION_RECORD {field} does not have exit code 0")
        require(state.get(field) == record,
                f"CURRENT_STATE {field} disagrees with LAST_EXECUTION_RECORD")
    recorded_at = last_execution.get("recorded_at_utc")
    require(isinstance(recorded_at, str) and recorded_at.endswith("Z"),
            "LAST_EXECUTION_RECORD recorded_at_utc is absent or not UTC Z format")
    try:
        dt.datetime.fromisoformat(recorded_at[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationFailure("LAST_EXECUTION_RECORD recorded_at_utc is invalid") from exc
    require(state.get("last_command") == last_execution.get("last_command"),
            "CURRENT_STATE last_command disagrees with LAST_EXECUTION_RECORD")
    require(state.get("last_exit_code") == last_execution["last_command"]["exit_code"],
            "CURRENT_STATE last_exit_code disagrees with LAST_EXECUTION_RECORD")
    if incomplete:
        failure_record = audit_failure_bundle["record"]
        require(last_execution["last_command"].get("command") == failure_record["command"]
                and last_execution["last_command"].get("exit_code") == 1,
                "LAST_EXECUTION_RECORD failed command disagrees with LAST_AUDIT_FAILURE")
        require(last_execution["last_successful_audit_command"].get("command") ==
                "gzip -t work/final_analysis/validation/motion_full_mechanism_audit.csv.gz",
                "LAST_EXECUTION_RECORD does not preserve the observed gzip integrity command")
        require(last_execution["last_successful_audit_command"].get("exit_code") == 0,
                "LAST_EXECUTION_RECORD merged-motion gzip check is not successful")
    else:
        require(last_execution["last_command"].get("exit_code") == 0,
                "completed validation evidence is paired with a failed last command")
    modified = last_execution.get("last_modified_files")
    require(isinstance(modified, list) and modified,
            "LAST_EXECUTION_RECORD last_modified_files is absent or empty")
    for index, value in enumerate(modified):
        validate_relative_resume_target(
            root, value, f"LAST_EXECUTION_RECORD last_modified_files[{index}]"
        )
    if incomplete:
        required_failed_outputs = {
            f"work/final_analysis/validation/{name}"
            for name in INCOMPLETE_PRESENT_VALIDATION_FILES
        }
        require(required_failed_outputs <= set(modified),
                "LAST_EXECUTION_RECORD omits present failed-audit output files")
    state_modified = state.get("last_modified_files")
    require(isinstance(state_modified, list)
            and all(isinstance(row, dict) for row in state_modified),
            "CURRENT_STATE last_modified_files is invalid")
    require([row.get("path") for row in state_modified] == modified,
            "CURRENT_STATE last_modified_files paths disagree with LAST_EXECUTION_RECORD")
    for row in state_modified:
        path = root / PurePosixPath(row["path"])
        require(row.get("size_bytes") == path.stat().st_size,
                f"CURRENT_STATE last-modified size mismatch: {row['path']}")
        require(row.get("sha256") == sha256_file(path),
                f"CURRENT_STATE last-modified SHA-256 mismatch: {row['path']}")

    governance = state.get("governance")
    require(isinstance(governance, dict), "CURRENT_STATE governance is absent")
    require(governance.get("creo_environment") == CREO_DISPOSITION,
            "CURRENT_STATE Creo governance disposition is not exact")
    require(governance.get("controlling_neutral_cad_gate") ==
            "Clean-process OCP/XCAF AP242 reimport",
            "CURRENT_STATE controlling neutral-CAD gate is not exact")
    controlling_sources = governance.get("controlling_source_records")
    require(isinstance(controlling_sources, list) and controlling_sources,
            "CURRENT_STATE controlling source records are absent")
    for index, value in enumerate(controlling_sources):
        validate_relative_resume_target(
            root, value, f"CURRENT_STATE controlling source record {index}"
        )

    for key in ("preserved_checkpoint_directories", "candidate_wip_outputs"):
        values = state.get(key)
        require(isinstance(values, list) and values, f"CURRENT_STATE {key} is absent or empty")
        for index, value in enumerate(values):
            validate_relative_resume_target(
                root,
                value,
                f"CURRENT_STATE {key}[{index}]",
                kind="directory" if key == "preserved_checkpoint_directories" else "file",
            )
    actual_preserved = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "work").glob("preserved_*")
        if path.is_dir() and not path.is_symlink()
    )
    require(state["preserved_checkpoint_directories"] == actual_preserved,
            "CURRENT_STATE preserved checkpoint list is not exhaustive and exact")
    outputs_root = root / "outputs/6f4e7892e9f1"
    actual_candidate_outputs = sorted(
        path.relative_to(root).as_posix()
        for path in outputs_root.rglob("*")
        if path.is_file()
        and "CANDIDATE_WIP" in path.name.upper()
        and path.suffix.lower() == ".zip"
    )
    require(state["candidate_wip_outputs"] == actual_candidate_outputs,
            "CURRENT_STATE candidate WIP ZIP list is not exhaustive and exact")
    candidate_temps = state.get("candidate_temporary_artifacts", [])
    require(isinstance(candidate_temps, list),
            "CURRENT_STATE candidate_temporary_artifacts is not a list")
    for index, value in enumerate(candidate_temps):
        validate_relative_resume_target(
            root, value, f"CURRENT_STATE candidate_temporary_artifacts[{index}]"
        )
    actual_candidate_temps = sorted(
        path.relative_to(root).as_posix()
        for path in outputs_root.rglob("*")
        if path.is_file()
        and "CANDIDATE_WIP" in path.name.upper()
        and path.suffix.lower() != ".zip"
    )
    require(candidate_temps == actual_candidate_temps,
            "CURRENT_STATE candidate temporary-artifact list is not exhaustive and exact")

    command_fields = (
        ("last_command", "command"),
        ("last_successful_modifying_command", "command"),
        ("last_successful_audit_command", "command"),
    )
    for keys in command_fields:
        command = get_nested(state, keys, ".".join(keys))
        require(isinstance(command, str) and command.strip(), f"CURRENT_STATE {'.'.join(keys)} is blank")

    integrity = state.get("integrity")
    require(isinstance(integrity, dict), "CURRENT_STATE integrity object is absent")
    require(integrity.get("file_manifest") == "FILE_MANIFEST.csv",
            "CURRENT_STATE FILE_MANIFEST reference is not direct-relative")
    require(integrity.get("sha256_sums") == "SHA256SUMS.txt",
            "CURRENT_STATE SHA256SUMS reference is not direct-relative")
    require(integrity.get("sha256_sums_self_excluded") is True,
            "CURRENT_STATE does not disclose SHA256SUMS self-exclusion")
    handoff_policy = state.get("handoff_policy")
    require(isinstance(handoff_policy, dict), "CURRENT_STATE handoff_policy is absent")
    require(handoff_policy.get("purpose") == "SAFE CODEX HANDOFF CHECKPOINT",
            "CURRENT_STATE handoff policy purpose is not exact")
    require(handoff_policy.get("new_correction_cycle_authorized") is False,
            "CURRENT_STATE incorrectly authorizes a new correction cycle")
    require(handoff_policy.get("final_release_packaging_authorized") is False,
            "CURRENT_STATE incorrectly authorizes final release packaging")
    require(handoff_policy.get("latest_safe_termination_directive_governs_runtime_only") is True,
            "CURRENT_STATE runtime-directive governance flag is not exact")
    require(handoff_policy.get("stale_r2_metadata_is_controlling") is False,
            "CURRENT_STATE incorrectly makes stale R2 metadata controlling")

    dependency_capture = state.get("dependency_capture")
    require(isinstance(dependency_capture, dict),
            "CURRENT_STATE dependency_capture is absent")
    require(dependency_capture.get("python_package_count") ==
            len(environment_bundle["python_packages"]),
            "CURRENT_STATE Python package count disagrees with pinned environment")
    require(dependency_capture.get("node_package_install_count") ==
            len(environment_bundle["node_packages"]),
            "CURRENT_STATE Node package count disagrees with pinned environment")
    dependency_versions = state.get("dependency_versions")
    require(isinstance(dependency_versions, dict),
            "CURRENT_STATE dependency_versions is absent")
    require(dependency_versions.get("runtime_versions") ==
            environment_bundle["runtime_versions"],
            "CURRENT_STATE runtime versions disagree with environment manifest")
    require(dependency_versions.get("python_packages") ==
            environment_bundle["python_packages"],
            "CURRENT_STATE Python packages disagree with environment manifest")
    require(dependency_versions.get("node_packages") ==
            environment_bundle["node_packages"],
            "CURRENT_STATE Node packages disagree with environment manifest")

    validation_state = state.get("validation")
    require(isinstance(validation_state, dict), "CURRENT_STATE validation object is absent")
    if incomplete:
        failure_record = audit_failure_bundle["record"]
        motion_verification = audit_failure_bundle["motion_verification"]
        require(validation_state.get("execution_state") == "TERMINAL_AUDIT_FAILURE",
                "CURRENT_STATE validation execution_state is not terminal failure")
        require(validation_state.get("last_successful_validator_status") ==
                "UNAVAILABLE_TERMINAL_AUDIT_FAILURE"
                and validation_state.get("last_successful_validator_exit_code") is None,
                "CURRENT_STATE fabricates a successful terminal validator result")
        require(validation_state.get("artifact_availability") == {
                    "gate_results": False,
                    "validation_summary": False,
                    "validation_manifest": False,
                    "motion_audit_summary": False,
                    "motion_kinematics_1deg": False,
                    "merged_motion_audit": True,
                },
                "CURRENT_STATE terminal artifact availability is not exact")
        for field in (
            "validation_summary",
            "gate_results",
            "validation_manifest",
            "validator_scope",
            "validator_limit",
            "elapsed_seconds",
        ):
            require(validation_state.get(field) is None,
                    f"CURRENT_STATE fabricates terminal validation field: {field}")
        require(validation_state.get("present_validation_files") ==
                list(INCOMPLETE_PRESENT_VALIDATION_FILES),
                "CURRENT_STATE terminal present-file set is not exact")
        require(validation_state.get("missing_validation_files") ==
                list(INCOMPLETE_MISSING_VALIDATION_FILES),
                "CURRENT_STATE terminal missing-file set is not exact")
        require(validation_state.get("last_audit_failure") == LAST_AUDIT_FAILURE_PATH,
                "CURRENT_STATE last-audit-failure path is not exact relative path")
        require(validation_state.get("last_validator_exit_code") == 1,
                "CURRENT_STATE last validator exit code is not exactly 1")
        require(validation_state.get("validator_failure") == failure_record,
                "CURRENT_STATE validator-failure object disagrees with dedicated record")
        require(validation_state.get("expected_gate_ids") == list(EXPECTED_GATE_IDS),
                "CURRENT_STATE expected_gate_ids is not the frozen 31-ID sequence")
        require(validation_state.get("gate_counts") is None,
                "CURRENT_STATE fabricates terminal gate counts")
        require(validation_state.get("handoff_open_gate_count") ==
                len(EXPECTED_GATE_IDS),
                "CURRENT_STATE terminal handoff-open gate count is not 31")
        require(validation_state.get("computed_release_status") ==
                INCOMPLETE_RELEASE_STATUS,
                "CURRENT_STATE terminal release status is not exact")
        require(validation_state.get("package_required_label") ==
                INCOMPLETE_PACKAGE_LABEL,
                "CURRENT_STATE terminal package label is not exact")
        if "informational_environment_items" in validation_state:
            require(validation_state["informational_environment_items"] ==
                    [CREO_INFORMATIONAL_ITEM],
                    "CURRENT_STATE terminal Creo informational item is not exact")

        terminal_gate_rows = validation_state.get("gates")
        require(isinstance(terminal_gate_rows, list)
                and len(terminal_gate_rows) == len(EXPECTED_GATE_IDS)
                and all(isinstance(row, dict) for row in terminal_gate_rows),
                "CURRENT_STATE terminal gate rows are incomplete")
        require([row.get("gate_id") for row in terminal_gate_rows] ==
                list(EXPECTED_GATE_IDS),
                "CURRENT_STATE terminal gate IDs/order are not exact")
        for row in terminal_gate_rows:
            require(set(row) == {
                        "gate_id", "status", "handoff_disposition", "requirement",
                        "measured", "evidence", "note",
                    }
                    and row.get("status") == "NOT_COMPUTED"
                    and row.get("handoff_disposition") == "OPEN"
                    and row.get("requirement") is None
                    and row.get("measured") is None
                    and row.get("evidence") is None
                    and row.get("note") ==
                    "gate_results.json absent after terminal validator failure; "
                    "no acceptance status was computed",
                    f"CURRENT_STATE fabricates acceptance for gate {row.get('gate_id')}")
        require(state.get("closed_gates") == [],
                "CURRENT_STATE terminal checkpoint fabricates closed gates")
        open_gate_rows = state.get("open_gates")
        require(isinstance(open_gate_rows, list)
                and len(open_gate_rows) == len(EXPECTED_GATE_IDS)
                and [row.get("gate_id") for row in open_gate_rows] ==
                list(EXPECTED_GATE_IDS),
                "CURRENT_STATE terminal open-gate inventory is not exact")
        for row in open_gate_rows:
            require(row.get("status") == "NOT_COMPUTED"
                    and row.get("handoff_disposition") == "OPEN"
                    and row.get("note") ==
                    "gate_results.json absent after terminal validator failure; "
                    "no acceptance status was computed",
                    f"CURRENT_STATE terminal open gate is mislabeled: {row.get('gate_id')}")

        ncr_rows = state.get("ncr_formula_statuses")
        require(isinstance(ncr_rows, list)
                and all(isinstance(row, dict) for row in ncr_rows)
                and [row.get("ncr_id") for row in ncr_rows] == list(NCR_GATE_MAP),
                "CURRENT_STATE terminal NCR inventory is not exact")
        for row in ncr_rows:
            ncr_id = row.get("ncr_id")
            expected_controlling = [
                {"gate_id": gate_id, "status": "NOT_COMPUTED"}
                for gate_id in NCR_GATE_MAP[str(ncr_id)]
            ]
            require(set(row) == {
                        "ncr_id", "formula_status", "handoff_disposition",
                        "controlling_gates", "formula_basis",
                    }
                    and row.get("formula_status") == "NOT_COMPUTED"
                    and row.get("handoff_disposition") == "OPEN"
                    and row.get("controlling_gates") == expected_controlling
                    and row.get("formula_basis") ==
                    "Formula was not evaluated because gate_results.json is absent; "
                    "handoff treats the NCR as open without fabricating an acceptance status",
                    f"CURRENT_STATE fabricates NCR status for {ncr_id}")
        open_ncr_rows = state.get("open_ncrs")
        require(isinstance(open_ncr_rows, list)
                and [row.get("ncr_id") for row in open_ncr_rows] == list(NCR_GATE_MAP),
                "CURRENT_STATE terminal open-NCR inventory is not exact")
        require(open_ncr_rows == ncr_rows,
                "CURRENT_STATE terminal open-NCR rows differ from the full open NCR set")
        for row in open_ncr_rows:
            require(row.get("formula_status") == "NOT_COMPUTED"
                    and row.get("handoff_disposition") == "OPEN",
                    f"CURRENT_STATE terminal NCR is mislabeled: {row.get('ncr_id')}")

        latest_motion = state.get("latest_motion_metrics")
        require(isinstance(latest_motion, dict),
                "CURRENT_STATE terminal motion metrics are absent")
        expected_motion_values = {
            "execution_state": "TERMINAL_AUDIT_FAILURE",
            "source": "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz",
            "sample_count": 81,
            "data_row_count": motion_verification["row_count"],
            "line_count_including_header": motion_verification["row_count"] + 1,
            "pair_rows_per_sample": 17_875,
            "unauthorized_positive_volume_pair_count": 849,
            "unauthorized_unique_pair_count": 39,
            "category_b_rigid_observation_count": 681,
            "category_b_rigid_unique_pair_count": 33,
            "nonrigid_involved_observation_count": 168,
            "nonrigid_involved_unique_pair_count": 6,
            "motion_summary_status": "NOT_COMPUTED",
            "motion_kinematics_status": "NOT_COMPUTED",
            "last_audit_failure": LAST_AUDIT_FAILURE_PATH,
        }
        for field, expected in expected_motion_values.items():
            require(latest_motion.get(field) == expected,
                    f"CURRENT_STATE terminal motion metric is wrong: {field}")
        require(latest_motion.get("summary_artifact_available") is False
                and latest_motion.get("kinematics_artifact_available") is False,
                "CURRENT_STATE terminal motion availability is fabricated")
        require(latest_motion.get("result_counts") ==
                motion_verification["result_counts"],
                "CURRENT_STATE terminal motion result counts are wrong")
        require(latest_motion.get("unauthorized_classification_observation_counts") ==
                motion_verification["unauthorized_classification_counts"],
                "CURRENT_STATE terminal motion classification split is wrong")
        require(latest_motion.get("merged_motion_audit") ==
                failure_record["merged_motion_audit"],
                "CURRENT_STATE terminal merged-motion identity is wrong")
        remaining_pairs = state.get("remaining_pairs")
        require(isinstance(remaining_pairs, list) and len(remaining_pairs) == 39,
                "CURRENT_STATE does not expose all 39 open unauthorized pair identities")
        require(sum(
                    int(row.get("observation_count", 0))
                    for row in remaining_pairs if isinstance(row, dict)
                ) == 849,
                "CURRENT_STATE open unauthorized-pair observations do not total 849")
        category_b = state.get("category_b_invalids")
        require(isinstance(category_b, dict)
                and category_b.get("count") == 33
                and category_b.get("observation_count") == 681
                and isinstance(category_b.get("records"), list)
                and len(category_b["records"]) == 33,
                "CURRENT_STATE Category-B rigid invalids are not exact 681/33")
        nonrigid = state.get("unresolved_nonrigid_positive_pairs")
        require(isinstance(nonrigid, dict)
                and nonrigid.get("count") == 6
                and nonrigid.get("observation_count") == 168
                and isinstance(nonrigid.get("records"), list)
                and len(nonrigid["records"]) == 6,
                "CURRENT_STATE nonrigid unauthorized pairs are not exact 168/6")
        validator_defects = state.get("validator_defects")
        require(isinstance(validator_defects, dict)
                and isinstance(validator_defects.get("records"), list)
                and any(
                    isinstance(row, dict)
                    and row.get("execution_state") == "TERMINAL_AUDIT_FAILURE"
                    and row.get("exception_type") == "KeyError"
                    and row.get("exception_message") == "'angle_deg'"
                    and row.get("exit_code") == 1
                    and row.get("acceptance_gate_status") == "NOT_COMPUTED"
                    and row.get("release_authorized") is False
                    for row in validator_defects["records"]
                ),
                "CURRENT_STATE validator defects omit the exact terminal KeyError record")
        resume_path = root / "RESUME_COMMANDS.md"
        require(resume_path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
                "RESUME_COMMANDS.md exceeds structured-text safety limit")
        resume_text = resume_path.read_text(encoding="utf-8")
        require(OLD_WORKSPACE.search(resume_text) is None,
                "RESUME_COMMANDS.md uses the old absolute workspace")
        require(LIVE_MOTION_SHARD.search(resume_text) is None,
                "RESUME_COMMANDS.md relies on a live motion shard")
        for token in (
            "work/r2_source/build_r2.py",
            "work/r2_source/per_solid_authoring_audit.py STOWED",
            "work/r2_source/per_solid_authoring_audit.py DEPLOYED",
            "work/r2_source/validate_r2.py",
            "work/r2_source/build_workbook.mjs",
            "work/final_tools/package_final.py",
        ):
            require(token in resume_text,
                    f"RESUME_COMMANDS.md lacks required relative command target: {token}")
        return state

    require(validation_state.get("expected_gate_ids") == list(EXPECTED_GATE_IDS),
            "CURRENT_STATE expected_gate_ids is not the frozen 31-ID sequence")
    require(validation_state.get("gate_counts") == validation_bundle["gate_counts"],
            "CURRENT_STATE gate_counts disagree with extracted gate evidence")
    require(validation_state.get("computed_release_status") ==
            validation_bundle["release_status"],
            "CURRENT_STATE release status disagrees with extracted gate evidence")
    require(validation_state.get("package_required_label") ==
            validation_bundle["package_label"],
            "CURRENT_STATE package label disagrees with extracted gate evidence")
    require(validation_state.get("informational_environment_items") ==
            [CREO_INFORMATIONAL_ITEM],
            "CURRENT_STATE Creo informational item is not exact")
    compact_gate_rows = [
        {"gate_id": row["gate_id"], "status": row["status"]}
        for row in validation_bundle["gate_rows"]
    ]
    require(validation_state.get("gates") == compact_gate_rows,
            "CURRENT_STATE compact gate rows disagree with extracted gate evidence")

    status_by_gate = {
        row["gate_id"]: row["status"] for row in validation_bundle["gate_rows"]
    }
    expected_closed = sorted(
        (gate_id, status) for gate_id, status in status_by_gate.items() if status == "PASS"
    )
    expected_open = sorted(
        (gate_id, status) for gate_id, status in status_by_gate.items() if status != "PASS"
    )
    for field, expected in (("closed_gates", expected_closed), ("open_gates", expected_open)):
        rows = state.get(field)
        require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows),
                f"CURRENT_STATE {field} is invalid")
        actual = [(str(row.get("gate_id", "")), row.get("status")) for row in rows]
        require(actual == expected, f"CURRENT_STATE {field} disagrees with gate evidence")

    ncr_rows = state.get("ncr_formula_statuses")
    require(isinstance(ncr_rows, list) and all(isinstance(row, dict) for row in ncr_rows),
            "CURRENT_STATE ncr_formula_statuses is invalid")
    require([row.get("ncr_id") for row in ncr_rows] == list(NCR_GATE_MAP),
            "CURRENT_STATE NCR rows are missing, duplicated, or out of order")
    actual_ncr = {
        str(row.get("ncr_id", "")): row.get("formula_status") for row in ncr_rows
    }
    require(actual_ncr == validation_bundle["ncr_statuses"],
            "CURRENT_STATE NCR formula statuses disagree with recomputed gate mapping")
    gate_status_by_id = {
        row["gate_id"]: row["status"] for row in validation_bundle["gate_rows"]
    }
    for row in ncr_rows:
        ncr_id = row["ncr_id"]
        expected_controlling = [
            {"gate_id": gate_id, "status": gate_status_by_id[gate_id]}
            for gate_id in NCR_GATE_MAP[ncr_id]
        ]
        require(row.get("controlling_gates") == expected_controlling,
                f"CURRENT_STATE {ncr_id} controlling-gate detail is not exact")
    open_ncr_rows = state.get("open_ncrs")
    require(isinstance(open_ncr_rows, list)
            and all(isinstance(row, dict) for row in open_ncr_rows),
            "CURRENT_STATE open_ncrs is invalid")
    actual_open_ncr = {
        str(row.get("ncr_id", "")): row.get("formula_status") for row in open_ncr_rows
    }
    expected_open_ncr = {
        ncr_id: status
        for ncr_id, status in validation_bundle["ncr_statuses"].items()
        if status != "CLOSED"
    }
    require([row.get("ncr_id") for row in open_ncr_rows] == list(expected_open_ncr),
            "CURRENT_STATE open_ncrs is missing, duplicated, or out of order")
    require(actual_open_ncr == expected_open_ncr,
            "CURRENT_STATE open_ncrs disagrees with recomputed NCR formula statuses")

    resume_path = root / "RESUME_COMMANDS.md"
    require(resume_path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
            "RESUME_COMMANDS.md exceeds structured-text safety limit")
    resume_text = resume_path.read_text(encoding="utf-8")
    require(OLD_WORKSPACE.search(resume_text) is None,
            "RESUME_COMMANDS.md uses the old absolute workspace")
    require(LIVE_MOTION_SHARD.search(resume_text) is None,
            "RESUME_COMMANDS.md relies on a live motion shard")
    required_resume_tokens = (
        "work/r2_source/build_r2.py",
        "work/r2_source/per_solid_authoring_audit.py STOWED",
        "work/r2_source/per_solid_authoring_audit.py DEPLOYED",
        "work/r2_source/validate_r2.py",
        "work/r2_source/build_workbook.mjs",
        "work/final_tools/package_final.py",
    )
    for token in required_resume_tokens:
        require(token in resume_text, f"RESUME_COMMANDS.md lacks required relative command target: {token}")
    return state


def validate_handoff_markdown(
    root: Path,
    validation_bundle: dict[str, Any],
) -> None:
    path = root / "HANDOFF.md"
    require(path.stat().st_size <= MAX_STRUCTURED_TEXT_BYTES,
            "HANDOFF.md exceeds structured-text safety limit")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationFailure("HANDOFF.md is unreadable or not UTF-8") from exc
    require(OLD_WORKSPACE.search(text) is None,
            "HANDOFF.md contains an old absolute workspace operational path")
    require(LIVE_MOTION_SHARD.search(text) is None,
            "HANDOFF.md relies on a live motion shard")
    required_sections = (
        "## Controlling source records",
        "## Governance at handoff",
        "## Last successful commands",
        "## Latest endpoint and motion metrics",
        "## Hierarchy, products, occurrences, envelope, length, mass, and reserve",
        "## State parity, connectivity, attachment, routes, and Definition of Done",
        "## Remaining pairs, authorized contacts, invalids, and validator defects",
        "## Exact engineering commands (reference only; not authorized at handoff)",
        "## Fragile operations",
        "## Assumptions used by this handoff",
        "## Owner decisions not to reopen without new controlling authority",
    )
    for section in required_sections:
        require(section in text, f"HANDOFF.md lacks required section: {section}")
    if validation_bundle["execution_state"] == "TERMINAL_AUDIT_FAILURE":
        for section in (
            "## Terminal audit failure (incomplete validator evidence)",
            "### Acceptance gates (not computed; handoff-open)",
            "### NCR-01 through NCR-08 (not computed; handoff-open)",
        ):
            require(section in text, f"HANDOFF.md lacks terminal section: {section}")
        for token in (
            "TERMINAL_AUDIT_FAILURE",
            "KeyError",
            "'angle_deg'",
            "81",
            "work/final_analysis/validation/motion_full_mechanism_audit.csv.gz",
            "NOT RELEASED",
            "Authoritative editable source: `work/r2_source`",
            "no /tmp state is required after the sweep",
            "work/r2_source/build_r2.py",
            "work/r2_source/per_solid_authoring_audit.py",
            "work/r2_source/validate_r2.py",
            "work/final_tools/package_final.py",
            CREO_DISPOSITION,
        ):
            require(token in text,
                    f"HANDOFF.md lacks terminal failure/source token: {token}")
        normalized = " ".join(text.casefold().split())
        require("gates" in normalized and "not computed" in normalized
                and "ncr" in normalized,
                "HANDOFF.md does not disclose that gates/NCRs were not computed")
        require("849" in text and "39" in text and "33" in text and "681" in text,
                "HANDOFF.md omits observed open motion-interference counts")
        return
    for section in (
        "## Preserved validator state",
        "### Closed gates",
        "### Open gates",
        "### NCR-01 through NCR-08 formula statuses",
    ):
        require(section in text, f"HANDOFF.md lacks completed-validation section: {section}")
    counts = validation_bundle["gate_counts"]
    required_tokens = (
        "Authoritative editable source: `work/r2_source`",
        "no /tmp state is required after the sweep",
        f"Computed release status: `{validation_bundle['release_status']}`",
        f"Gate counts: PASS `{counts['PASS']}`, FAIL `{counts['FAIL']}`, "
        f"BLOCKED `{counts['BLOCKED']}`",
        CREO_DISPOSITION,
        "work/r2_source/build_r2.py",
        "work/r2_source/per_solid_authoring_audit.py",
        "work/r2_source/validate_r2.py",
        "work/final_tools/package_final.py",
    )
    for token in required_tokens:
        require(token in text, f"HANDOFF.md lacks required status/source/command token: {token}")


def run_mandatory_cad_help(
    extracted_root: Path,
    cad_python: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    require(cad_python.is_file() and os.access(cad_python, os.X_OK),
            f"CAD Python is absent or not executable: {cad_python}")
    runtime = extracted_root.parent / "runtime"
    runtime_home = runtime / "home"
    runtime_cache = runtime / "cache"
    runtime_tmp = runtime / "tmp"
    for directory in (runtime_home, runtime_cache, runtime_tmp):
        directory.mkdir(parents=True, exist_ok=True)
    environment = {
        **os.environ,
        "HOME": str(runtime_home),
        "XDG_CACHE_HOME": str(runtime_cache),
        "TMPDIR": str(runtime_tmp),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONPYCACHEPREFIX": str(runtime_cache / "pycache"),
        "MPLCONFIGDIR": str(runtime_cache / "matplotlib"),
        "PYTHONHASHSEED": "0",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
        "PYTHONPATH": str(extracted_root / "work/r2_source"),
    }
    command = [
        str(cad_python),
        "-B",
        str(extracted_root / "work/r2_source/validate_r2.py"),
        "--help",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=extracted_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValidationFailure("extracted validate_r2.py --help could not run") from exc
    require(completed.returncode == 0,
            "extracted validate_r2.py --help failed: " + completed.stderr[-2000:])
    require("usage:" in completed.stdout.lower(),
            "extracted validate_r2.py --help did not emit argparse usage")
    return {
        "ran": True,
        "cad_python": str(cad_python),
        "returncode": completed.returncode,
    }


def validate_archive(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    requested_path = Path(args.archive).expanduser()
    if not requested_path.is_absolute():
        requested_path = Path.cwd() / requested_path
    require(requested_path.name == DEFAULT_ARCHIVE.name,
            f"handoff ZIP basename must be exactly {DEFAULT_ARCHIVE.name}")
    requested_metadata = requested_path.lstat()
    require(not stat.S_ISLNK(requested_metadata.st_mode),
            "handoff ZIP path must not be a symlink")
    archive_path = requested_path.resolve(strict=True)
    metadata_before = archive_path.lstat()
    require(stat.S_ISREG(metadata_before.st_mode) and not stat.S_ISLNK(metadata_before.st_mode),
            "handoff ZIP path is not a regular non-symlink file")
    zip_size = metadata_before.st_size
    zip_digest = sha256_file(archive_path)

    temporary_container = Path(
        tempfile.mkdtemp(prefix="df8_handoff_validate_", dir="/tmp")
    )
    os.chmod(temporary_container, 0o700)
    extracted_root = temporary_container / "payload"
    extracted_root.mkdir(mode=0o700)
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            infos, file_infos, declared_bytes, directory_member_count = screen_archive(archive)
            free_bytes = shutil.disk_usage(temporary_container).free
            require(free_bytes >= declared_bytes + 64 * 1024**2,
                    "insufficient /tmp free space for guarded extraction")
            extracted_bytes = extract_screened_archive(archive, infos, extracted_root)
        require(extracted_bytes == declared_bytes,
                "total extracted bytes disagree with ZIP declarations")

        all_files, extracted_directories = inventory_extracted(extracted_root)
        require(set(file_infos) == all_files,
                "extracted regular-file set disagrees with screened ZIP members")
        require(DIRECT_ROOT_FILES <= all_files,
                "required direct-root handoff files are not regular extracted files")

        sums = verify_sha256sums(extracted_root, all_files)
        manifest_row_count = validate_file_manifest(extracted_root, all_files, file_infos)
        audit_failure_bundle = validate_last_audit_failure(extracted_root)
        validate_required_tree(extracted_root, audit_failure_bundle)
        validate_commission_provenance(extracted_root)
        environment_bundle = validate_environment_manifests(extracted_root)
        python_files = parse_all_python_sources(extracted_root, all_files)
        source_contract = validate_extracted_source_contract(extracted_root)
        authoring_manifest = validate_authoring_manifest(extracted_root)
        validation_bundle = (
            validate_incomplete_validation_bundle(
                extracted_root, audit_failure_bundle["record"]
            )
            if audit_failure_bundle is not None
            else validate_validation_bundle(extracted_root)
        )
        current_state = validate_current_state_and_resume(
            extracted_root,
            validation_bundle,
            environment_bundle,
            audit_failure_bundle,
        )
        current_state_command_count = validate_current_state_command_paths(current_state)
        validate_handoff_markdown(extracted_root, validation_bundle)
        executable_block_count = sum(
            (
                validate_executable_fenced_blocks(
                    extracted_root / "HANDOFF.md", "HANDOFF.md"
                ),
                validate_executable_fenced_blocks(
                    extracted_root / "RESUME_COMMANDS.md", "RESUME_COMMANDS.md"
                ),
            )
        )

        cad_help = run_mandatory_cad_help(
            extracted_root,
            # Preserve the venv launcher path.  Resolving this symlink to the
            # base interpreter discards pyvenv.cfg discovery and therefore
            # the installed CadQuery/OCP environment used by the smoke test.
            (
                Path(args.cad_python).expanduser().absolute()
                if not Path(args.cad_python).expanduser().is_absolute()
                else Path(args.cad_python).expanduser()
            ),
            args.cad_help_timeout,
        )
        files_after_help, directories_after_help = inventory_extracted(extracted_root)
        require(files_after_help == all_files and directories_after_help == extracted_directories,
                "mandatory CAD help smoke mutated the extracted payload tree")
        verify_sha256sums(extracted_root, all_files)

        metadata_after = archive_path.lstat()
        require(
            (
                metadata_after.st_dev,
                metadata_after.st_ino,
                metadata_after.st_size,
                metadata_after.st_mtime_ns,
            )
            == (
                metadata_before.st_dev,
                metadata_before.st_ino,
                metadata_before.st_size,
                metadata_before.st_mtime_ns,
            ),
            "handoff ZIP changed during validation",
        )
        require(sha256_file(archive_path) == zip_digest,
                "handoff ZIP content changed during validation")

        result = {
            "status": "PASS",
            "schema": "DF8_HANDOFF_POST_BUILD_VALIDATION_V1",
            "zip_path": str(archive_path),
            "zip_sha256": zip_digest,
            "zip_size_bytes": zip_size,
            "member_count": len(infos),
            "file_count": len(all_files),
            "directory_member_count": directory_member_count,
            "extracted_directory_count": len(extracted_directories),
            "declared_uncompressed_file_bytes": declared_bytes,
            "sha256_verified_file_count": len(sums),
            "file_manifest_row_count": manifest_row_count,
            "python_ast_file_count": len(python_files),
            "extracted_source_contract": source_contract,
            "current_state_command_string_count": current_state_command_count,
            "executable_command_block_count": executable_block_count,
            "authoring_manifest_step_count": len(authoring_manifest["files"]),
            "authoring_manifest_inventory_count": len(authoring_manifest["inventories"]),
            "gate_counts": validation_bundle["gate_counts"],
            "computed_release_status": validation_bundle["release_status"],
            "ncr_formula_statuses": validation_bundle["ncr_statuses"],
            "validation_execution_state": validation_bundle["execution_state"],
            "terminal_audit_failure": (
                {
                    "record": audit_failure_bundle["record"],
                    "motion_verification": audit_failure_bundle["motion_verification"],
                }
                if audit_failure_bundle is not None
                else None
            ),
            "current_state_schema": current_state.get("schema"),
            "cad_help": cad_help,
            "authoritative_source_in_archive": "work/r2_source",
            "extracted_source_path": str(extracted_root / "work/r2_source"),
            "extraction_retained": bool(args.keep_extracted),
        }
        return result, temporary_container
    except Exception:
        shutil.rmtree(temporary_container, ignore_errors=True)
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "archive",
        nargs="?",
        default=DEFAULT_ARCHIVE,
        help=f"handoff ZIP to validate (default: {DEFAULT_ARCHIVE})",
    )
    parser.add_argument(
        "--cad-python",
        default=DEFAULT_CAD_PYTHON,
        help=f"Python for mandatory extracted validate_r2.py --help smoke (default: {DEFAULT_CAD_PYTHON})",
    )
    parser.add_argument(
        "--cad-help-timeout",
        type=int,
        default=120,
        metavar="SECONDS",
        help="timeout for mandatory extracted validate_r2.py --help smoke (default: 120)",
    )
    extraction_group = parser.add_mutually_exclusive_group()
    extraction_group.add_argument(
        "--keep-extracted",
        dest="keep_extracted",
        action="store_true",
        help="retain the validated extraction under /tmp (default)",
    )
    extraction_group.add_argument(
        "--cleanup-extracted",
        dest="keep_extracted",
        action="store_false",
        help="remove the validated extraction after printing PASS JSON",
    )
    parser.set_defaults(keep_extracted=True)
    args = parser.parse_args(argv)
    if args.cad_help_timeout < 1 or args.cad_help_timeout > 1800:
        parser.error("--cad-help-timeout must be inside 1..1800 seconds")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    extraction: Path | None = None
    try:
        result, extraction = validate_archive(args)
        print(json.dumps(result, sort_keys=True, allow_nan=False), flush=True)
        return 0
    except (ValidationFailure, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
                allow_nan=False,
            ),
            file=sys.stderr,
            flush=True,
        )
        return 1
    finally:
        if extraction is not None and not args.keep_extracted:
            shutil.rmtree(extraction, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
