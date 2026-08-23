"""Source-controlled exact ACE actuator geometry for the final DF8 build.

The supplied STEP components carry an older WP02 placement in their shape
coordinates.  These helpers remove only that rigid placement.  They do not
scale, heal, remesh, simplify, or otherwise regenerate the imported BREP.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq


_COMPONENT_DIR = (
    "wp02/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN/05_SUBSYSTEM_CAD/"
    "LOCAL_COMPONENTS"
)

_SOURCES = {
    "gs_body": "WP02-015_GS19_FIXED_BODY_EXACT_VENDOR_BREP_STOWED_LOCAL_AP242.step",
    "gs_rod": "WP02-016_GS19_MOVING_ROD_EXACT_VENDOR_BREP_STOWED_LOCAL_AP242.step",
    "hbd_body": "WP02-019_HBD15_BODY_DRAWING_DERIVED_STOWED_LOCAL_AP242.step",
    "hbd_rod": "WP02-020_HBD15_ROD_DRAWING_DERIVED_STOWED_LOCAL_AP242.step",
}

_EXPECTED = {
    "gs_body": {"volume": 32771.591106, "dims": (19.0, 19.0, 124.0)},
    "gs_rod": {"volume": 3008.422635, "dims": (8.0, 8.0, 60.0)},
    "hbd_body": {"volume": 14872.355109, "dims": (15.0, 15.0, 95.0)},
    "hbd_rod": {"volume": 1728.630819, "dims": (12.0000002, 9.0, 43.625610)},
}


def _source_path(input_dir: Path, key: str) -> Path:
    path = input_dir / _COMPONENT_DIR / _SOURCES[key]
    if not path.is_file():
        raise FileNotFoundError(f"Missing controlled actuator STEP source: {path}")
    return path


def _local_exact_solid(input_dir: Path, key: str) -> cq.Shape:
    imported = cq.importers.importStep(str(_source_path(input_dir, key))).val()
    solids = imported.Solids()
    if len(solids) != 1:
        raise ValueError(f"{key} must import as exactly one solid; found {len(solids)}")
    solid = solids[0]
    if not solid.isValid() or solid.Volume() <= 0.0:
        raise ValueError(
            f"{key} imported BREP is invalid/non-positive "
            f"(valid={solid.isValid()}, volume={solid.Volume():.12f})"
        )

    expected = _EXPECTED[key]
    if abs(solid.Volume() - expected["volume"]) > 1.0e-3:
        raise ValueError(
            f"{key} volume changed: {solid.Volume():.12f} vs "
            f"{expected['volume']:.12f} mm^3"
        )
    box = solid.BoundingBox()
    dims = (box.xlen, box.ylen, box.zlen)
    if any(abs(actual - target) > 1.0e-3 for actual, target in zip(dims, expected["dims"])):
        raise ValueError(f"{key} dimensions changed: {dims} vs {expected['dims']} mm")

    # Remove the prior WP02 baked placement and retain the original +Z axis.
    return solid.translate(cq.Vector(
        -(box.xmin + box.xmax) / 2.0,
        -(box.ymin + box.ymax) / 2.0,
        -box.zmin,
    ))


def gs19_exact_body_local(input_dir: Path) -> cq.Shape:
    """Authentic ACE GS-19 configured fixed-body BREP, local +Z axis."""
    return _local_exact_solid(input_dir, "gs_body")


def gs19_exact_rod_local(input_dir: Path) -> cq.Shape:
    """Authentic ACE GS-19 configured moving-rod BREP, local +Z axis."""
    return _local_exact_solid(input_dir, "gs_rod")


def hbd15_drawing_body_local(input_dir: Path) -> cq.Shape:
    """Controlled HBD-15-25 drawing-derived fixed body, local +Z axis."""
    return _local_exact_solid(input_dir, "hbd_body")


def hbd15_constant_rod_local(input_dir: Path) -> cq.Shape:
    """Constant-volume HBD-15-25 drawing-derived moving rod, local +Z axis."""
    return _local_exact_solid(input_dir, "hbd_rod")

