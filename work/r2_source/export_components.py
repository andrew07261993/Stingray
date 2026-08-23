#!/usr/bin/env python3
"""Export both R2 endpoint part catalogs as controlled local component CAD.

Every controlled PartDef is rebuilt independently for STOWED and DEPLOYED and
written in part-local coordinates as both AP242 STEP and native Open CASCADE
BREP with an explicit state token in its filename.  This preserves the local
definitions for flexible/state-dependent articles instead of silently keeping
only the STOWED representation.  Authentic/reference source CAD is copied
byte-for-byte into a separate directory and is never substituted for the
authored R2 installation geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cadquery as cq

import build_r2


STATUS = "CREO_VALIDATION_PENDING — WIP — NOT RELEASED"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_to_root(path: Path) -> str:
    try:
        return path.relative_to(build_r2.ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def locate_exactly_one(root: Path, filename: str) -> Path:
    matches = sorted(root.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one {filename!r} below {root}, found {len(matches)}: "
            f"{[p.as_posix() for p in matches]}"
        )
    return matches[0]


def export_part_ap242(part: Any, state: str, path: Path) -> None:
    assembly = cq.Assembly(
        name=(
            f"{build_r2.slug(part.part_number, 96)}__REV_{build_r2.slug(part.revision, 32)}"
            f"__STATE_{state}"
        )
    )
    assembly.add(
        part.shape,
        name=f"{build_r2.slug(part.part_number, 96)}__STATE_{state}__LOCAL_PART_DEFINITION",
        color=build_r2.g.COLORS.get(part.color_key, build_r2.g.COLORS["steel"]),
    )
    build_r2.export_ap242(assembly, path)
    # A one-part assembly normally has a NAUO.  Naming it improves target-CAD
    # browsing; schema export remains valid even if a future exporter writes a
    # flat product without any NAUO.
    try:
        build_r2.name_assembly_usage_occurrences(path)
    except RuntimeError:
        pass


def part_record(part: Any, state: str, step_path: Path, brep_path: Path, output_dir: Path) -> dict[str, Any]:
    return {
        "record_type": "CONTROLLED_PART_DEFINITION",
        "state": state,
        "part_number": part.part_number,
        "revision": part.revision,
        "description": part.description,
        "material": part.material,
        "make_buy": part.make_buy,
        "manufacturer": part.manufacturer,
        "cad_classification": part.cad_classification,
        "source_url": part.source_url,
        "purchase_url": part.purchase_url,
        "process": part.process,
        "finish": part.finish,
        "notes": part.notes,
        "mass_kg": part.resolved_mass(),
        "volume_mm3": part.shape.Volume(),
        "solid_count": len(part.shape.Solids()),
        "face_count": len(part.shape.Faces()),
        "step_schema": "AP242",
        "step_path": step_path.relative_to(output_dir).as_posix(),
        "step_size_bytes": step_path.stat().st_size,
        "step_sha256": sha256(step_path),
        "brep_path": brep_path.relative_to(output_dir).as_posix(),
        "brep_size_bytes": brep_path.stat().st_size,
        "brep_sha256": sha256(brep_path),
        "source_path": "",
        "source_sha256": "",
        "copied_byte_for_byte": "",
    }


def copy_source_reference(
    source: Path,
    destination_dir: Path,
    output_dir: Path,
    classification: str,
    part_identity: str,
    note: str,
) -> dict[str, Any]:
    destination = destination_dir / source.name
    shutil.copyfile(source, destination)
    source_hash = sha256(source)
    destination_hash = sha256(destination)
    if source_hash != destination_hash or source.stat().st_size != destination.stat().st_size:
        raise RuntimeError(f"Byte-preserving copy verification failed for {source}")
    return {
        "record_type": "SOURCE_CAD_REFERENCE",
        "state": "AS_RECEIVED",
        "part_number": part_identity,
        "revision": "SOURCE-AS-RECEIVED",
        "description": note,
        "material": "",
        "make_buy": "BUY",
        "manufacturer": "ACE Controls",
        "cad_classification": classification,
        "source_url": "",
        "purchase_url": "",
        "process": "BYTE-FOR-BYTE COPY; NO TRANSLATION OR SCALING",
        "finish": "",
        "notes": note,
        "mass_kg": "",
        "volume_mm3": "",
        "solid_count": "",
        "face_count": "",
        "step_schema": "AS_RECEIVED",
        "step_path": destination.relative_to(output_dir).as_posix(),
        "step_size_bytes": destination.stat().st_size,
        "step_sha256": destination_hash,
        "brep_path": "",
        "brep_size_bytes": "",
        "brep_sha256": "",
        "source_path": relative_to_root(source),
        "source_sha256": source_hash,
        "copied_byte_for_byte": True,
    }


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames = list(records[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": relative_to_root(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "mtime_ns": path.stat().st_mtime_ns,
    }


def clear_prior_component_exports(parts_dir: Path) -> None:
    """Remove only exporter-owned CAD files; retain unknown user artifacts."""
    if not parts_dir.exists():
        return
    for path in parts_dir.iterdir():
        if path.is_file() and path.suffix.lower() in {".step", ".stp", ".brep"}:
            path.unlink()


def frozen_basis() -> dict[str, Any]:
    analysis = build_r2.ROOT / "work" / "r2_analysis"
    release = build_r2.ROOT / "work" / "r2_release"
    manifest_path = analysis / "authoring_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release_status") != STATUS:
        raise RuntimeError("Authoring manifest does not carry the exact candidate-WIP status")

    master_records: dict[str, Any] = {}
    for name in (build_r2.STOWED_FILE, build_r2.DEPLOYED_FILE, build_r2.EXTERNAL_CONTEXT_FILE):
        path = release / name
        record = file_record(path)
        expected = manifest.get("files", {}).get(name, {}).get("sha256")
        if record["sha256"] != expected:
            raise RuntimeError(f"Frozen master/authoring-manifest hash mismatch: {name}")
        master_records[name] = record

    source_paths = [
        Path(build_r2.__file__).resolve(),
        Path(build_r2.g.__file__).resolve(),
        Path(__file__).resolve(),
    ]
    inventory_paths = [
        analysis / "authoring_inventory_stowed.json",
        analysis / "authoring_inventory_deployed.json",
    ]
    return {
        "authoring_sources": {path.name: file_record(path) for path in source_paths},
        "authoring_manifest": file_record(manifest_path),
        "authoring_inventories": {path.name: file_record(path) for path in inventory_paths},
        "frozen_masters": master_records,
    }


def export_catalog(output_dir: Path) -> dict[str, Any]:
    parts_dir = output_dir / "controlled_part_definitions"
    source_dir = output_dir / "source_cad_as_received"
    parts_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    clear_prior_component_exports(parts_dir)

    basis = frozen_basis()
    builders = {state: build_r2.build_state(state) for state in ("STOWED", "DEPLOYED")}
    controlled_by_state = {
        state: sorted(
            (part for part in builder.catalog.parts.values() if not part.external_context),
            key=lambda part: (part.part_number, part.revision),
        )
        for state, builder in builders.items()
    }
    if any(not parts for parts in controlled_by_state.values()):
        raise RuntimeError("An R2 endpoint authoring catalog contains no controlled part definitions")
    state_identities = {
        state: {(part.part_number, part.revision) for part in parts}
        for state, parts in controlled_by_state.items()
    }
    if state_identities["STOWED"] != state_identities["DEPLOYED"]:
        raise RuntimeError("STOWED and DEPLOYED controlled part identities do not reconcile")

    records: list[dict[str, Any]] = []
    used_stems: set[str] = set()
    total_definitions = sum(len(parts) for parts in controlled_by_state.values())
    index = 0
    for state in ("STOWED", "DEPLOYED"):
        for part in controlled_by_state[state]:
            index += 1
            stem = build_r2.slug(f"{part.part_number}__REV_{part.revision}__STATE_{state}", 128)
            if stem in used_stems:
                raise RuntimeError(f"Component filename collision after slugging: {stem}")
            used_stems.add(stem)
            step_path = parts_dir / f"{stem}__LOCAL_AP242.step"
            brep_path = parts_dir / f"{stem}__LOCAL_OCCT.brep"
            export_part_ap242(part, state, step_path)
            cq.exporters.export(part.shape, str(brep_path), exportType="BREP")
            records.append(part_record(part, state, step_path, brep_path, output_dir))
            print(f"[{index:03d}/{total_definitions:03d}] {state} {part.part_number}", flush=True)

    wp02 = build_r2.INPUT_DIR / "wp02"
    ace_gs = locate_exactly_one(wp02, "ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp")
    hbd = locate_exactly_one(wp02, "ACE_HBD_15_25_AA_P_DRAWING_DERIVED_NOT_VENDOR_CAD_AP242.step")
    records.append(
        copy_source_reference(
            ace_gs,
            source_dir,
            output_dir,
            "AUTHENTIC_VENDOR_CAD — UNMODIFIED SOURCE",
            "GS-19-50-V4A-B8-B8",
            "Unmodified authentic ACE GS-19 vendor STEP retained for reference; the R2 articulated installation model is separately classified DRAWING_DERIVED.",
        )
    )
    records.append(
        copy_source_reference(
            hbd,
            source_dir,
            output_dir,
            "DRAWING_DERIVED — NOT AUTHENTIC VENDOR CAD",
            "HBD-15-25-AA-P",
            "Unmodified as-received HBD drawing-derived AP242 reference; exact vendor configuration remains a final-release blocker.",
        )
    )

    component_records = [record for record in records if record["record_type"] == "CONTROLLED_PART_DEFINITION"]
    records_by_identity_state = {
        (record["part_number"], record["revision"], record["state"]): record
        for record in component_records
    }
    state_dependent: list[str] = []
    for part_number, revision in sorted(state_identities["STOWED"]):
        stowed_record = records_by_identity_state[(part_number, revision, "STOWED")]
        deployed_record = records_by_identity_state[(part_number, revision, "DEPLOYED")]
        if stowed_record["brep_sha256"] != deployed_record["brep_sha256"]:
            state_dependent.append(part_number)

    provenance = {
        "package_status": STATUS,
        "catalog_states": ["STOWED", "DEPLOYED"],
        "catalog_generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "authoring_source": relative_to_root(Path(build_r2.__file__).resolve()),
        "geometry_source": relative_to_root(Path(build_r2.g.__file__).resolve()),
        "authoring_kernel": f"CadQuery {cq.__version__} / Open CASCADE",
        "catalog_basis": basis,
        "controlled_unique_part_count": len(state_identities["STOWED"]),
        "controlled_state_definition_count": len(component_records),
        "state_definition_counts": {
            state: len(controlled_by_state[state]) for state in ("STOWED", "DEPLOYED")
        },
        "controlled_step_count": len(component_records),
        "controlled_brep_count": len(component_records),
        "state_dependent_part_count": len(state_dependent),
        "state_dependent_part_numbers": state_dependent,
        "source_reference_count": 2,
        "records": records,
    }
    provenance_json = output_dir / "provenance.json"
    provenance_csv = output_dir / "provenance.csv"
    write_csv(provenance_csv, records)
    provenance["provenance_files"] = {
        provenance_csv.name: {"sha256": sha256(provenance_csv), "size_bytes": provenance_csv.stat().st_size},
    }
    provenance_json.write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        default=build_r2.ROOT / "work" / "r2_components",
        help="Output directory (default: work/r2_components)",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result = export_catalog(output_dir)
    print(
        json.dumps(
            {
                "output_dir": output_dir.as_posix(),
                "controlled_unique_part_count": result["controlled_unique_part_count"],
                "controlled_state_definition_count": result["controlled_state_definition_count"],
                "controlled_step_count": result["controlled_step_count"],
                "controlled_brep_count": result["controlled_brep_count"],
                "state_dependent_part_count": result["state_dependent_part_count"],
                "source_reference_count": result["source_reference_count"],
                "status": STATUS,
            },
            indent=2,
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
