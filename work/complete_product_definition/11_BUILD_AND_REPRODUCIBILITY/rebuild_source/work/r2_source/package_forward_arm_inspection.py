#!/usr/bin/env python3
"""Build the bounded corrected forward-arm owner inspection archive."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "STINGRAY_I5S_DF8_FORWARD_ARM_REPACK_INSPECTION.zip"
TEMP = OUT.with_suffix(".zip.tmp")
WORK = ROOT / "work" / "forward_arm_repack"
RELEASE = ROOT / "work" / "final_release"

members = [
    (RELEASE / "STINGRAY_I5S_DF8_FINAL_STOWED_MASTER_AP242.step", "STINGRAY_I5S_DF8_FORWARD_ARM_REPACK_STOWED_AP242.step"),
    (RELEASE / "STINGRAY_I5S_DF8_FINAL_DEPLOYED_MASTER_AP242.step", "STINGRAY_I5S_DF8_FORWARD_ARM_REPACK_DEPLOYED_AP242.step"),
    (WORK / "FORWARD_ARM_REPACK_COMPARISON.md", "FORWARD_ARM_REPACK_COMPARISON.md"),
    (WORK / "mass_cg_inertia_comparison.json", "mass_cg_inertia_comparison.json"),
    (WORK / "five_angle_boolean_gate_pass2" / "five_angle_exact_boolean_summary.json", "five_angle_exact_boolean_summary.json"),
]
members.extend((path, path.name) for path in sorted((WORK / "inspection_views").glob("*.png")))

if len(members) != 10:
    raise RuntimeError(f"Inspection package requires exactly 10 members; found {len(members)}")
missing = [str(path) for path, _ in members if not path.is_file()]
if missing:
    raise FileNotFoundError("Missing package inputs: " + ", ".join(missing))

# Keep generated text evidence LF-normalized so Git and the deterministic ZIP
# carry the same platform-independent bytes.
for text_path in (
    WORK / "updated_mass_properties.json",
    WORK / "mass_cg_inertia_comparison.json",
    WORK / "targeted_validation_summary.json",
):
    text_path.write_bytes(text_path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8"))

fixed_time = (2026, 8, 24, 12, 0, 0)
with zipfile.ZipFile(TEMP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for source, name in members:
        info = zipfile.ZipInfo(name, fixed_time)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

with zipfile.ZipFile(TEMP, "r") as archive:
    if archive.testzip() is not None or archive.namelist() != [name for _, name in members]:
        raise RuntimeError("Inspection ZIP integrity or deterministic member-order check failed")

os.replace(TEMP, OUT)
result = {
    "path": str(OUT),
    "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
    "size_bytes": OUT.stat().st_size,
    "member_count": len(members),
    "members": [name for _, name in members],
}
print(json.dumps(result, indent=2))
