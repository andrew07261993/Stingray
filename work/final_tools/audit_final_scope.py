#!/usr/bin/env python3
"""Diagnostic-only complete exact-distance audit of final curated attachments.

The production scope installer is fail-fast by design.  This companion keeps
the same row authoring and graph checks but records every gap exceedance in one
pass, so physical corrections can be made without weakening release logic.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import build_r2
import r2_final_scope
import r2_hardware


def audit_state(state: str) -> dict[str, Any]:
    original_installer = build_r2.r2_final_scope.install_final_scope
    build_r2.r2_final_scope.install_final_scope = lambda builder, hardware: {}
    try:
        builder = build_r2.build_state(state)
    finally:
        build_r2.r2_final_scope.install_final_scope = original_installer

    measurements: list[dict[str, Any]] = []
    original_direct = r2_final_scope._AttachmentRegistrar.direct

    def diagnostic_direct(
        self: Any,
        attachment_id: str,
        occurrence_a: str,
        occurrence_b: str,
        attachment_type: str,
        maximum_separation_mm: float,
        evidence_basis: str,
        structural_load_path: bool = False,
    ) -> None:
        row = self._base_row(
            attachment_id, occurrence_a, occurrence_b, attachment_type,
            maximum_separation_mm, evidence_basis, structural_load_path,
        )
        gap = self._distance(occurrence_a, occurrence_b)
        maximum = float(maximum_separation_mm)
        measurements.append({
            "attachment_id": attachment_id,
            "occurrence_a": occurrence_a,
            "occurrence_b": occurrence_b,
            "gap_mm": gap,
            "maximum_separation_mm": maximum,
            "margin_mm": maximum - gap,
            "accepted": bool(
                math.isfinite(gap)
                and gap <= maximum + r2_final_scope.DISTANCE_TOLERANCE_MM
            ),
        })
        self.rows.append(row)

    r2_final_scope._AttachmentRegistrar.direct = diagnostic_direct
    scope_error = None
    try:
        rows = r2_final_scope.build_attachment_requirements(builder, r2_hardware)
    except Exception as exc:  # graph/scope errors remain visible, not suppressed
        rows = []
        scope_error = f"{type(exc).__name__}: {exc}"
    finally:
        r2_final_scope._AttachmentRegistrar.direct = original_direct

    failures = [row for row in measurements if not row["accepted"]]
    failures.sort(key=lambda row: (row["margin_mm"], row["attachment_id"]))
    return {
        "state": state,
        "occurrence_count": len(builder.occurrences),
        "curated_attachment_row_count": len(rows),
        "direct_distance_measurement_count": len(measurements),
        "failed_distance_count": len(failures),
        "scope_error": scope_error,
        "failed_distances": failures,
        "measurements": sorted(measurements, key=lambda row: row["attachment_id"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = {state: audit_state(state) for state in ("STOWED", "DEPLOYED")}
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if any(value["failed_distance_count"] or value["scope_error"] for value in result.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
