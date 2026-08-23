#!/usr/bin/env python3
"""Fail-closed final attachment and Definition-of-Done scope for DF8.

This module owns no geometry.  It is called only after ``build_r2`` and
``r2_hardware`` have installed the complete endpoint occurrence inventory.
Every attachment below names a bounded, occurrence-specific physical pair.
The public installer calculates the exact authoring distance for every direct
pair and refuses to serialize an incomplete or unsupported scope.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import math
import re
from typing import Any, Iterable


DISTANCE_TOLERANCE_MM = 1.0e-7


class FinalScopeError(RuntimeError):
    """Raised when final authoring scope is incomplete or not exact-supported."""


class _AttachmentRegistrar:
    def __init__(self, builder: Any, hardware: Any):
        self.builder = builder
        self.hardware = hardware
        self.state = str(builder.state).upper()
        if self.state not in {"STOWED", "DEPLOYED"}:
            raise FinalScopeError(f"Unsupported builder state: {builder.state!r}")
        self.known = set(builder.global_shapes)
        if not self.known:
            raise FinalScopeError("Final occurrence inventory is empty")
        self.rows: list[dict[str, Any]] = []
        self.ids: set[str] = set()
        self.logical_hardware_membership: Counter[str] = Counter()

    def _distance(self, occurrence_a: str, occurrence_b: str) -> float:
        try:
            value = float(
                self.builder.global_shapes[occurrence_a].distance(
                    self.builder.global_shapes[occurrence_b]
                )
            )
        except Exception as exc:
            raise FinalScopeError(
                f"Exact distance blocked for {occurrence_a} <> {occurrence_b}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        if not math.isfinite(value) or value < 0.0:
            raise FinalScopeError(
                f"Non-finite/negative distance for {occurrence_a} <> {occurrence_b}: {value}"
            )
        return value

    def _base_row(
        self,
        attachment_id: str,
        occurrence_a: str,
        occurrence_b: str,
        attachment_type: str,
        maximum_separation_mm: float,
        evidence_basis: str,
        structural_load_path: bool,
        hardware_occurrence_ids: Iterable[str] = (),
    ) -> dict[str, Any]:
        hardware_ids = tuple(hardware_occurrence_ids)
        if not attachment_id or attachment_id in self.ids:
            raise FinalScopeError(f"Blank or duplicate attachment ID: {attachment_id!r}")
        if occurrence_a == occurrence_b:
            raise FinalScopeError(f"Self attachment is forbidden: {attachment_id}")
        missing = sorted(
            ({occurrence_a, occurrence_b} | set(hardware_ids)) - self.known
        )
        if missing:
            raise FinalScopeError(
                f"Attachment {attachment_id} names missing occurrences: {missing}"
            )
        if not attachment_type.strip() or not evidence_basis.strip():
            raise FinalScopeError(f"Attachment {attachment_id} lacks type/process evidence")
        maximum = float(maximum_separation_mm)
        if not math.isfinite(maximum) or maximum < 0.0:
            raise FinalScopeError(f"Attachment {attachment_id} has invalid gap limit {maximum}")
        self.ids.add(attachment_id)
        return {
            "attachment_id": attachment_id,
            "state": self.state,
            "occurrence_a": occurrence_a,
            "occurrence_b": occurrence_b,
            "attachment_type": attachment_type,
            "maximum_separation_mm": maximum,
            "hardware_occurrence_ids": list(hardware_ids),
            "evidence_basis": evidence_basis,
            "structural_load_path": bool(structural_load_path),
        }

    def direct(
        self,
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
        if gap > float(maximum_separation_mm) + DISTANCE_TOLERANCE_MM:
            raise FinalScopeError(
                f"Attachment {attachment_id} exceeds its design gap: "
                f"{occurrence_a} <> {occurrence_b} = {gap:.9f} mm > "
                f"{float(maximum_separation_mm):.9f} mm"
            )
        self.rows.append(row)

    def bridge(
        self,
        attachment_id: str,
        occurrence_a: str,
        occurrence_b: str,
        hardware_occurrence_ids: Iterable[str],
        attachment_type: str,
        maximum_separation_mm: float,
        evidence_basis: str,
        structural_load_path: bool = False,
    ) -> None:
        hardware_ids = tuple(hardware_occurrence_ids)
        if not hardware_ids:
            raise FinalScopeError(f"Hardware bridge {attachment_id} is empty")
        row = self._base_row(
            attachment_id, occurrence_a, occurrence_b, attachment_type,
            maximum_separation_mm, evidence_basis, structural_load_path,
            hardware_ids,
        )
        self.rows.append(row)
        for hardware_id in hardware_ids:
            self.logical_hardware_membership[hardware_id] += 1
            self.direct(
                f"{attachment_id}--{hardware_id}--A",
                hardware_id, occurrence_a,
                "HARDWARE_SEATED_TO_FIRST_MATE",
                maximum_separation_mm,
                evidence_basis,
                structural_load_path,
            )
            self.direct(
                f"{attachment_id}--{hardware_id}--B",
                hardware_id, occurrence_b,
                "HARDWARE_ENGAGED_WITH_SECOND_MATE",
                maximum_separation_mm,
                evidence_basis,
                structural_load_path,
            )

    def finish(self, route_ids: set[str]) -> list[dict[str, Any]]:
        helper_added = set(self.hardware.HELPER_ADDED_HARDWARE_OCCURRENCE_IDS)
        mandatory = set(self.hardware.REQUIRED_HARDWARE_OCCURRENCE_IDS)
        missing_mandatory = sorted(mandatory - self.known)
        if missing_mandatory:
            raise FinalScopeError(
                f"Mandatory final hardware not installed: {missing_mandatory}"
            )
        bad_membership = {
            occurrence_id: self.logical_hardware_membership[occurrence_id]
            for occurrence_id in sorted(helper_added)
            if self.logical_hardware_membership[occurrence_id] != 1
        }
        if bad_membership:
            raise FinalScopeError(
                "Each helper-added hardware occurrence must belong to exactly "
                f"one logical bridge: {bad_membership}"
            )
        endpoints = {
            occurrence_id
            for row in self.rows
            for occurrence_id in (row["occurrence_a"], row["occurrence_b"])
        }
        uncovered = sorted(self.known - endpoints)
        if uncovered:
            raise FinalScopeError(
                f"Installed occurrences lack direct attachment degree: {uncovered}"
            )
        uncovered_routes = sorted(route_ids - endpoints)
        if uncovered_routes:
            raise FinalScopeError(
                f"Route occurrences lack direct attachment degree: {uncovered_routes}"
            )
        # Connectivity is checked here as well as by the neutral-CAD validator;
        # this catches a locally supported but system-floating island early.
        graph: dict[str, set[str]] = defaultdict(set)
        for row in self.rows:
            a, b = row["occurrence_a"], row["occurrence_b"]
            graph[a].add(b)
            graph[b].add(a)
        anchor = "FWD-SHELL-001"
        if anchor not in self.known:
            raise FinalScopeError(f"System attachment anchor is missing: {anchor}")
        seen = {anchor}
        queue = deque([anchor])
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        disconnected = sorted(self.known - seen)
        if disconnected:
            raise FinalScopeError(
                f"Exact-supported attachment graph has floating components: {disconnected}"
            )
        return sorted(self.rows, key=lambda row: row["attachment_id"])


def _subset(prefix: str, values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(value for value in values if value.startswith(prefix)))


def build_attachment_requirements(builder: Any, hardware: Any) -> list[dict[str, Any]]:
    """Build the complete curated exact-supported attachment register."""
    r = _AttachmentRegistrar(builder, hardware)
    structural = "Qualified occurrence-specific joint; exact mating geometry and controlled process inspection."
    fitted = "Occurrence-specific exact shoulder, pilot, guide, seat, or retained fitting; dimensional inspection required."
    flexible = "Occurrence-specific finished-article seam, stitch, splice, or closed eye; controlled traveler and proof inspection."

    # Forward structural spine and primary longerons.
    r.bridge("ATT-NOSE-BALLAST", "NOSE-001", "BALLAST-001", hardware.TAPER_PIN_IDS,
             "TAPER_PINNED_STRUCTURAL_JOINT", 0.05, structural, True)
    for aid, a, b, limit in (
        ("ATT-BALLAST-RING-01", "BALLAST-001", "FWD-RING-01", 0.02),
        ("ATT-RING-01-SHELL", "FWD-RING-01", "FWD-SHELL-001", 0.06),
        ("ATT-SHELL-RING-02", "FWD-SHELL-001", "FWD-RING-02", 0.02),
    ):
        r.direct(aid, a, b, "STRUCTURAL_SHOULDER_OR_WELD", limit, structural, True)
    for index in range(1, 4):
        for end, ring in (("FWD", "FWD-RING-01"), ("AFT", "FWD-RING-02")):
            r.direct(
                f"ATT-FWD-LONGERON-{index}-{end}", f"FWD-LONGERON-{index}", ring,
                "WELDED_PRIMARY_LONGERON_END", 0.02, structural, True,
            )

    r.bridge("ATT-CARRIER-FWD", "CARTRIDGE-CARRIER-FWD", "FWD-RING-01",
             hardware.FWD_CARRIER_SCREW_IDS, "FOUR_SCREW_PILOTED_CARRIER", 0.05, structural, True)
    r.bridge("ATT-CARRIER-AFT", "CARTRIDGE-CARRIER-AFT", "COLLECTION-MANIFOLD-001",
             hardware.MANIFOLD_CARRIER_SCREW_IDS, "FOUR_SCREW_PILOTED_MANIFOLD", 0.05, structural, True)
    for index in range(1, 5):
        r.direct(f"ATT-CARTRIDGE-CARRIER-{index}", f"CO2-CARTRIDGE-{index}",
                 "CARTRIDGE-CARRIER-FWD", "CAPTURED_CARTRIDGE_SEAT", 0.23, fitted)
        r.direct(f"ATT-CARTRIDGE-PUNCTURE-{index}", f"CO2-CARTRIDGE-{index}",
                 f"PUNCTURE-HEAD-{index}", "SEALED_PRESSURE_TERMINAL", 0.15, fitted)
        r.direct(f"ATT-PUNCTURE-MANIFOLD-{index}", f"PUNCTURE-HEAD-{index}",
                 "COLLECTION-MANIFOLD-001", "THREADED_PRESSURE_PORT", 0.16, fitted)

    # Closed booster pressure reservoirs, isolation valves, and supported bands.
    for booster in range(1, 4):
        r.direct(f"ATT-BOOSTER-FWD-CLOSURE-{booster}", f"BOOSTER-{booster}",
                 f"BOOSTER-FWD-CLOSURE-{booster}", "ORBITAL_WELDED_PRESSURE_CLOSURE", 0.02, fitted)
        r.direct(f"ATT-BOOSTER-AFT-CLOSURE-{booster}", f"BOOSTER-{booster}",
                 f"BOOSTER-AFT-CLOSURE-{booster}", "ORBITAL_WELDED_PRESSURE_CLOSURE", 0.02, fitted)
        r.direct(f"ATT-BOOSTER-VALVE-{booster}", f"BOOSTER-FWD-CLOSURE-{booster}",
                 f"BOOSTER-ISOLATION-VALVE-{booster}", "TUBE_FITTED_ISOLATION_VALVE", 0.05, fitted)
        r.direct(f"ATT-BOOSTER-LINE-VALVE-{booster}", f"BOOSTER-ISOLATION-VALVE-{booster}",
                 f"BOOSTER-COLLECTION-LINE-{booster}", "FERRULED_PRESSURE_LINE_END", 0.05, fitted)
        r.direct(f"ATT-BOOSTER-LINE-MANIFOLD-{booster}", f"BOOSTER-COLLECTION-LINE-{booster}",
                 "COLLECTION-MANIFOLD-001", "FERRULED_MANIFOLD_PORT", 0.06, fitted)
        for band in range(1, 4):
            band_id = f"BOOSTER-BAND-{booster}-{band}"
            r.direct(f"ATT-BOOSTER-{booster}-BAND-{band}", f"BOOSTER-{booster}", band_id,
                     "CONTROLLED_PEEK_CLAMP_CLEARANCE", 0.16, fitted)
            r.bridge(f"ATT-BOOSTER-BAND-SHELL-{booster}-{band}", band_id, "FWD-SHELL-001",
                     [f"BOOSTER-CLAMP-SCREW-{booster}-{band}"], "RADIAL_CLAMP_SCREW", 0.05, structural)

    # Water trigger/service access and full-flow spool retention.
    r.bridge("ATT-TRIGGER-SHELL", "WATER-TRIGGER-HSG-001", "FWD-SHELL-001",
             hardware.TRIGGER_MOUNT_SCREW_IDS, "THREE_SCREW_TRIGGER_MOUNT", 0.05, structural, True)
    r.bridge("ATT-BOBBIN-TRIGGER", "WATER-BOBBIN-001", "WATER-TRIGGER-HSG-001",
             hardware.SERVICE_CAP_IDS, "CAPTIVE_BAYONET_SERVICE_CAP", 0.05, fitted)
    r.direct("ATT-WATER-INLET-SHELL", "WATER-INLET-001", "FWD-SHELL-001",
             "BRAZED_RADIAL_PENETRATION", 0.16, fitted)
    r.direct("ATT-WATER-INLET-TRIGGER", "WATER-INLET-001", "WATER-TRIGGER-HSG-001",
             "O_RING_NIPPLE_TERMINATION", 0.11, fitted)
    r.bridge("ATT-FULLFLOW-RING", "FULLFLOW-VALVE-001", "FWD-RING-02",
             hardware.CIRCLIP_IDS, "SHOULDER_AND_EXTERNAL_CIRCLIP", 0.05, fitted)

    # Arm primary structure and all occurrence-specific moving hardware.
    for arm in range(1, 4):
        r.direct(f"ATT-SECTOR-LONGERON-{arm}", f"FIXED-SECTOR-{arm}", f"ARM-LONGERON-{arm}",
                 "WELDED_FIXED_SECTOR", 0.02, structural, True)
        r.direct(f"ATT-ARM-LONGERON-{arm}-FWD", f"ARM-LONGERON-{arm}", "FWD-RING-02",
                 "WELDED_PRIMARY_LONGERON_END", 0.02, structural, True)
        r.direct(f"ATT-ARM-LONGERON-{arm}-AFT", f"ARM-LONGERON-{arm}", "AFT-ROUTE-RING-001",
                 "WELDED_PRIMARY_LONGERON_END", 0.02, structural, True)
        r.direct(f"ATT-PIVOT-PIN-{arm}-ARM", f"PIVOT-PIN-{arm}", f"ARM-{arm}",
                 "GROUND_PIN_IN_REAMED_ARM_BORE", 0.20, fitted, True)
        r.direct(f"ATT-PIVOT-PIN-{arm}-CARRIER", f"PIVOT-PIN-{arm}", f"PIVOT-CARRIER-{arm}",
                 "GROUND_PIN_IN_DOUBLE_SHEAR_CARRIER", 0.16, fitted, True)
        r.direct(f"ATT-PIVOT-CLIP-{arm}", f"PIVOT-CLIP-{arm}", f"PIVOT-PIN-{arm}",
                 "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)
        for side in (1, 2):
            r.direct(f"ATT-PIVOT-BUSH-{arm}-{side}", f"PIVOT-BUSH-{arm}-{side}", f"ARM-{arm}",
                     "PRESS_FIT_PIVOT_BUSHING", 0.04, fitted)
            r.direct(f"ATT-PIVOT-WASHER-{arm}-{side}", f"PIVOT-WASHER-{arm}-{side}", f"ARM-{arm}",
                     "CAPTIVE_THRUST_WASHER", 0.02, fitted)
        for link in (1, 2):
            link_id = f"LINK-{arm}-{link}"
            for end, support in (("BELL", f"ARM-{arm}"), ("CROSSHEAD", "CROSSHEAD-001")):
                pin = f"LINK-PIN-{arm}-{end}"
                r.direct(f"ATT-{link_id}-{end}-PIN", link_id, pin,
                         "PIN_THROUGH_LINK_BORE", 0.20, fitted, True)
                # The common full-span pin is intentionally shared by both link plates.
                if link == 1:
                    r.direct(f"ATT-LINK-PIN-{arm}-{end}-SUPPORT", pin, support,
                             "PIN_THROUGH_DOUBLE_SHEAR_CLEVIS", 0.20, fitted, True)
                    r.direct(f"ATT-LINK-CLIP-{arm}-{end}", f"LINK-CLIP-{arm}-{end}", pin,
                             "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)
        arm_stop_screws = tuple(
            f"ARM-STOP-SCREW-{arm}-{index}" for index in range(1, 3)
        )
        r.bridge(f"ATT-ARM-PAD-{arm}", f"ARM-STOP-PAD-{arm}", f"ARM-{arm}",
                 arm_stop_screws, "DOVETAIL_AND_TWO_CAPTIVE_SCREWS", 0.05, structural, True)
        fixed_stop_hardware = tuple(
            [f"FIXED-STOP-SCREW-{arm}-{index}" for index in range(1, 3)]
            + [f"FIXED-STOP-DOWEL-{arm}-{index}" for index in range(1, 3)]
        )
        r.bridge(f"ATT-FIXED-STOP-{arm}", f"FIXED-STOP-{arm}", f"PIVOT-CARRIER-{arm}",
                 fixed_stop_hardware, "TWO_SCREW_TWO_DOWEL_STOP_LAND", 0.05, structural, True)

        r.direct(f"ATT-STOW-GUIDE-RING-{arm}", f"STOW-DOG-GUIDE-{arm}", "AFT-ROUTE-RING-001",
                 "STRUCTURAL_GUIDE_MOUNT", 0.02, structural, True)
        r.direct(f"ATT-STOW-DOG-GUIDE-{arm}", f"STOW-DOG-{arm}", f"STOW-DOG-GUIDE-{arm}",
                 "CAPTIVE_RADIAL_GUIDE", 0.06, fitted)
        r.direct(f"ATT-STOW-SPRING-DOG-{arm}", f"STOW-DOG-SPRING-{arm}", f"STOW-DOG-{arm}",
                 "CAPTURED_MOVING_SPRING_SEAT", 0.06, fitted)
        r.direct(f"ATT-STOW-SPRING-GUIDE-{arm}", f"STOW-DOG-SPRING-{arm}", f"STOW-DOG-GUIDE-{arm}",
                 "CAPTURED_FIXED_SPRING_SEAT", 0.10, fitted)
        r.direct(f"ATT-STOW-INHIBIT-GUIDE-{arm}", f"STOW-DOG-INHIBIT-PIN-{arm}", f"STOW-DOG-GUIDE-{arm}",
                 "CAPTIVE_SLIDER_IN_CLOSED_GUIDE", 0.06, fitted)
        if r.state == "STOWED":
            r.direct(f"ATT-STOW-INHIBIT-DOG-{arm}", f"STOW-DOG-INHIBIT-PIN-{arm}", f"STOW-DOG-{arm}",
                     "TRANSPORT_INHIBIT_PIN_THROUGH_DOG", 0.06, fitted)
            r.direct(f"ATT-STOW-DOG-ARM-{arm}", f"STOW-DOG-{arm}", f"ARM-{arm}",
                     "POSITIVE_STOWED_ARM_STRIKE", 0.20, fitted, True)
        r.direct(f"ATT-STOW-INHIBIT-KEEPER-{arm}", f"STOW-DOG-INHIBIT-KEEPER-{arm}",
                 f"STOW-DOG-INHIBIT-PIN-{arm}", "EXTERNAL_GROOVE_KEEPER", 0.02, fitted)
        r.direct(f"ATT-STOW-KEEPER-GUIDE-{arm}", f"STOW-DOG-INHIBIT-KEEPER-{arm}",
                 f"STOW-DOG-GUIDE-{arm}", "CLOSED_KEEPER_CAGE", 0.10, fitted)

        r.direct(f"ATT-LOCK-DOG-GUIDE-{arm}", f"LOCK-DOG-{arm}", f"FIXED-STOP-{arm}",
                 "CAPTIVE_GUIDED_LOCK_DOG", 0.16, fitted)
        r.direct(f"ATT-LOCK-SPRING-DOG-{arm}", f"LOCK-SPRING-{arm}", f"LOCK-DOG-{arm}",
                 "CAPTURED_MOVING_LOCK_SPRING_SEAT", 0.06, fitted)
        r.direct(f"ATT-LOCK-SPRING-STOP-{arm}", f"LOCK-SPRING-{arm}", f"FIXED-STOP-{arm}",
                 "CAPTURED_FIXED_LOCK_SPRING_SEAT", 0.11, fitted)
        r.direct(f"ATT-LOCK-BUSHING-STOP-{arm}", f"LOCK-BUSHING-{arm}", f"FIXED-STOP-{arm}",
                 "PRESS_FIT_LOCK_RETAINER_BUSHING", 0.02, fitted)
        if r.state == "DEPLOYED":
            r.direct(f"ATT-LOCK-DOG-PAD-{arm}", f"LOCK-DOG-{arm}", f"ARM-STOP-PAD-{arm}",
                     "POSITIVE_DEPLOYED_LOCK_ENGAGEMENT", 0.16, fitted, True)

    # Crosshead, backup spring, and articulated actuator installations.
    r.direct("ATT-CROSSHEAD-GUIDE-RUNNING", "CROSSHEAD-001", "CROSSHEAD-GUIDE-001",
             "GUIDED_RUNNING_CLEARANCE", 0.36, fitted)
    r.bridge("ATT-CROSSHEAD-GUIDE-SPIDER", "CROSSHEAD-GUIDE-001", "CROSSHEAD-GUIDE-SPIDER",
             hardware.CROSSHEAD_GUIDE_LOCK_SCREW_IDS, "LOW_HEAD_GUIDE_LOCK_SCREW", 0.05, structural, True)
    r.direct("ATT-SPIDER-RING", "CROSSHEAD-GUIDE-SPIDER", "FWD-RING-02",
             "QUALIFIED_PERMANENT_SPIDER_JOINT", 0.03, structural, True)
    r.direct("ATT-BACKUP-SPRING-FIXED", "BACKUP-SPRING-001", "BACKUP-SPRING-FIXED-SEAT",
             "CAPTURED_FIXED_SPRING_SEAT", 0.02, fitted)
    r.direct("ATT-BACKUP-SPRING-MOVING", "BACKUP-SPRING-001", "BACKUP-SPRING-MOVING-SEAT",
             "CAPTURED_MOVING_SPRING_SEAT", 0.02, fitted)
    r.direct("ATT-BACKUP-MOVING-SEAT-CROSSHEAD", "BACKUP-SPRING-MOVING-SEAT", "CROSSHEAD-001",
             "PILOTED_PERMANENT_MOVING_SEAT", 0.02, structural, True)
    r.bridge("ATT-BACKUP-GUIDE-LONGERON", "BACKUP-SPRING-GUIDE", "ARM-LONGERON-3",
             ["BACKUP-GUIDE-SCREW-1"], "PILOTED_GUIDE_SUPPORT_SCREW", 0.05, structural, True)
    r.bridge("ATT-BACKUP-SEAT-LONGERON", "BACKUP-SPRING-FIXED-SEAT", "ARM-LONGERON-3",
             ["BACKUP-GUIDE-SCREW-2"], "PILOTED_FIXED_SEAT_SCREW", 0.05, structural, True)
    r.direct("ATT-BACKUP-GUIDE-SEAT", "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT",
             "GUIDE_SHOULDER_IN_FIXED_SEAT", 0.06, fitted)

    for label, sector, body, rod in (
        ("GS19", "ARM-LONGERON-1", "GS19-BODY-001", "GS19-ROD-001"),
        ("HBD", "ARM-LONGERON-2", "HBD-BODY-001", "HBD-ROD-001"),
    ):
        r.direct(f"ATT-{label}-YOKE-SECTOR", f"{label}-FIXED-YOKE", sector,
                 "QUALIFIED_FIXED_YOKE_LAND", 0.05, structural, True)
        for end, article, support in (
            ("FIXED", body, f"{label}-FIXED-YOKE"),
            ("MOVING", rod, "CROSSHEAD-001"),
        ):
            pin = f"{label}-PIN-{end}"
            r.direct(f"ATT-{label}-{end}-PIN-ARTICLE", pin, article,
                     "ACTUATOR_PIN_THROUGH_END_EYE", 0.20, fitted)
            r.direct(f"ATT-{label}-{end}-PIN-SUPPORT", pin, support,
                     "ACTUATOR_PIN_THROUGH_CLEVIS", 0.20, fitted, True)
            r.direct(f"ATT-{label}-{end}-CLIP", f"{label}-CLIP-{end}", pin,
                     "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)

    # Complete formed routes: endpoints, structural glands, and long-span liners.
    endpoint_specs = (
        ("MANIFOLD-FEED-ORIGIN", "ROUTE-MANIFOLD-FEED-001", "COLLECTION-MANIFOLD-001", 0.02),
        ("MANIFOLD-FEED-DEST", "ROUTE-MANIFOLD-FEED-001", "FULLFLOW-VALVE-001", 0.02),
        ("GAS-ORIGIN", "ROUTE-GAS-MAIN-001", "FULLFLOW-VALVE-001", 0.21),
        ("GAS-DEST", "ROUTE-GAS-MAIN-001", "WP04-FULLFLOW-MANIFOLD", 0.11),
        ("PILOT-ORIGIN", "ROUTE-PILOT-LINE-001", "FULLFLOW-VALVE-001", 0.16),
        ("PILOT-DEST", "ROUTE-PILOT-LINE-001", "WP04-LATCH-001", 0.02),
        ("SHEATH-ORIGIN", "ROUTE-BOWDEN-SHEATH-001", "WATER-TRIGGER-HSG-001", 0.06),
        ("SHEATH-DEST", "ROUTE-BOWDEN-SHEATH-001", "WP04-LATCH-001", 0.06),
        ("WIRE-ORIGIN", "ROUTE-BOWDEN-WIRE-001", "WATER-TRIGGER-HSG-001", 0.06),
        ("WIRE-DEST", "ROUTE-BOWDEN-WIRE-001", "WP04-SEAR-001", 0.02),
        ("WIRE-SHEATH", "ROUTE-BOWDEN-WIRE-001", "ROUTE-BOWDEN-SHEATH-001", 0.13),
    )
    for suffix, route, mate, limit in endpoint_specs:
        r.direct(f"ATT-ROUTE-{suffix}", route, mate, "CONTROLLED_ROUTE_TERMINATION", limit, fitted)
    for index in range(1, 4):
        clip = f"MANIFOLD-FEED-CLAMP-{index}"
        r.direct(f"ATT-MANIFOLD-FEED-CLAMP-{index}-ROUTE", clip,
                 "ROUTE-MANIFOLD-FEED-001", "SPRING_ROUTE_CAPTURE", 0.06, fitted)
        r.direct(f"ATT-MANIFOLD-FEED-CLAMP-{index}-SHELL", clip,
                 "FWD-SHELL-001", "LASER_WELDED_SUPPORT_TAB", 0.02, structural, True)
    for route_name, sector in (
        ("GAS-MAIN", "FIXED-SECTOR-1"),
        ("PILOT-LINE", "FIXED-SECTOR-3"),
        ("BOWDEN-SHEATH", "FIXED-SECTOR-2"),
    ):
        route = f"ROUTE-{route_name}-001"
        liner = f"ROUTE-LINER-{route_name}-001"
        r.direct(f"ATT-{route_name}-LINER", route, liner, "CONTINUOUS_SPLIT_GUIDE_LINER", 0.11, fitted)
        r.direct(f"ATT-{route_name}-LINER-SECTOR", liner, sector, "CAPTURED_LINER_IN_BORED_SECTOR", 0.02, fitted)
        for station, ring in (("FWD", "FWD-RING-02"), ("AFT", "AFT-ROUTE-RING-001")):
            gland = f"GLAND-{route_name}-{station}"
            r.direct(f"ATT-{route_name}-{station}-GLAND-ROUTE", route, gland,
                     "SWAGED_OR_BRAZED_GLANDLESS_TERMINATION", 0.09, fitted)
            r.direct(f"ATT-{route_name}-{station}-GLAND-RING", gland, ring,
                     "CAPTURED_BULKHEAD_GLAnd", 0.05, fitted)

    # Aft fixed structure, ejector, service closure, and recovery load path.
    r.direct("ATT-WP04-MANIFOLD-BRACKET", "WP04-FULLFLOW-MANIFOLD", "WP04-MANIFOLD-BRACKET",
             "PILOTED_MANIFOLD_SADDLE", 0.02, structural, True)
    r.direct("ATT-WP04-BRACKET-SHELL", "WP04-MANIFOLD-BRACKET", "AFT-SHELL-001",
             "QUALIFIED_STRUCTURAL_WELD_LAND", 0.02, structural, True)
    r.direct("ATT-AFT-SHELL-RING", "AFT-SHELL-001", "AFT-ROUTE-RING-001",
             "CIRCUMFERENTIAL_STRUCTURAL_WELD", 0.02, structural, True)
    for index in range(1, 4):
        r.direct(f"ATT-AFT-LONGERON-{index}-FWD", f"AFT-LONGERON-{index}", "AFT-ROUTE-RING-001",
                 "WELDED_PRIMARY_LONGERON_END", 0.11, structural, True)
        r.direct(f"ATT-AFT-LONGERON-{index}-AFT", f"AFT-LONGERON-{index}", "BODY-HARDPOINT-001",
                 "WELDED_PRIMARY_LONGERON_END", 0.11, structural, True)
    r.direct("ATT-REACTION-SHELL", "WP04-REACTION-BULKHEAD", "AFT-SHELL-001",
             "QUALIFIED_PERMANENT_BULKHEAD_JOINT", 0.05, structural, True)

    aft_rail_support = (
        "WP04-AFT-RAIL-SUPPORT"
        if "WP04-AFT-RAIL-SUPPORT" in r.known else "BODY-HARDPOINT-001"
    )
    if aft_rail_support == "WP04-AFT-RAIL-SUPPORT":
        for longeron in range(1, 4):
            r.direct(
                f"ATT-AFT-RAIL-SUPPORT-LONGERON-{longeron}",
                aft_rail_support, f"AFT-LONGERON-{longeron}",
                "QUALIFIED_AFT_RAIL_SUPPORT_WELD", 0.02, structural, True,
            )
    for rail in range(1, 4):
        r.bridge(f"ATT-RAIL-{rail}-FWD", f"WP04-GUIDE-RAIL-{rail}", "WP04-REACTION-BULKHEAD",
                 [f"GUIDE-RAIL-{rail}-SCREW-FWD"], "PILOTED_FORWARD_RAIL_SCREW", 0.05, structural, True)
        r.bridge(f"ATT-RAIL-{rail}-AFT", f"WP04-GUIDE-RAIL-{rail}", aft_rail_support,
                 [f"GUIDE-RAIL-{rail}-SCREW-AFT"], "PILOTED_AFT_RAIL_SCREW", 0.05, structural, True)
        r.direct(f"ATT-FOLLOWER-RAIL-{rail}", "WP04-FOLLOWER-001", f"WP04-GUIDE-RAIL-{rail}",
                 "GUIDED_RUNNING_CLEARANCE", 0.11, fitted)
    r.direct("ATT-EJECTOR-SPRING-FIXED", "WP04-EJECTOR-SPRING", "WP04-FIXED-SLEEVE",
             "CAPTURED_FIXED_SPRING_SEAT", 0.02, fitted)
    r.direct("ATT-EJECTOR-SPRING-MOVING", "WP04-EJECTOR-SPRING", "WP04-MOVING-SLEEVE",
             "CAPTURED_MOVING_SPRING_SEAT", 0.10, fitted)
    r.bridge("ATT-FIXED-SLEEVE", "WP04-FIXED-SLEEVE", "WP04-REACTION-BULKHEAD",
             hardware.FIXED_SLEEVE_SCREW_IDS, "THREE_SCREW_PILOTED_FIXED_SLEEVE", 0.05, structural, True)
    r.bridge("ATT-MOVING-SLEEVE", "WP04-MOVING-SLEEVE", "WP04-FOLLOWER-001",
             hardware.MOVING_SLEEVE_SCREW_IDS, "THREE_SCREW_PILOTED_MOVING_SLEEVE", 0.05, structural, True)

    latch_support = next(
        (
            occurrence_id
            for occurrence_id in ("WP04-LATCH-SUPPORT", "LATCH-SUPPORT-BRACKET")
            if occurrence_id in r.known
        ),
        "WP04-GUIDE-RAIL-3",
    )
    if latch_support != "WP04-GUIDE-RAIL-3":
        r.direct("ATT-LATCH-BRACKET-RAIL", latch_support, "WP04-GUIDE-RAIL-3",
                 "STRUCTURAL_LATCH_BRACKET_LAND", 0.02, structural, True)
    r.bridge("ATT-LATCH-SUPPORT", "WP04-LATCH-001", latch_support,
             hardware.LATCH_SCREW_IDS, "TWO_SCREW_PILOTED_LATCH_MOUNT", 0.05, structural, True)
    r.direct("ATT-SEAR-LATCH", "WP04-SEAR-001", "WP04-LATCH-001",
             "CAPTIVE_GUIDED_SEAR", 0.20, fitted)
    r.direct("ATT-SEAR-CLIP", "WP04-SEAR-CLIP-001", "WP04-SEAR-001",
             "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)
    r.direct("ATT-HARDPOINT-SHELL", "BODY-HARDPOINT-001", "AFT-SHELL-001",
             "STRUCTURAL_RING_WELD", 0.02, structural, True)
    r.bridge("ATT-SERVICE-THROAT-SHELL", "WP05-SERVICE-THROAT", "AFT-SHELL-001",
             hardware.SERVICE_THROAT_SCREW_IDS, "SIX_SCREW_PILOTED_SERVICE_JOINT", 0.05, structural, True)
    r.direct("ATT-DOOR-THROAT", "WP05-DOOR-001", "WP05-SERVICE-THROAT",
             "HINGED_SERVICE_DOOR_CLEARANCE", 0.11, fitted)
    r.direct("ATT-HINGE-PIN-DOOR", "WP05-HINGE-PIN", "WP05-DOOR-001",
             "GROUND_PIN_IN_DOOR_KNUCKLE", 0.11, fitted)
    r.direct("ATT-HINGE-PIN-THROAT", "WP05-HINGE-PIN", "WP05-SERVICE-THROAT",
             "GROUND_PIN_IN_FIXED_HINGE_EARS", 0.11, fitted)
    r.direct("ATT-HINGE-CLIP", "WP05-HINGE-CLIP", "WP05-HINGE-PIN",
             "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)
    for index in range(1, 5):
        r.direct(f"ATT-DOOR-DETENT-{index}", f"DOOR-DETENT-{index}", "WP05-SERVICE-THROAT",
                 "THREADED_BALL_DETENT", 0.02, fitted)
    r.direct("ATT-LANYARD-DOOR", "WP05-DOOR-LANYARD", "WP05-DOOR-001",
             "CLOSED_SWAGED_DOOR_EYE", 0.20, flexible)
    r.direct("ATT-LANYARD-THROAT", "WP05-DOOR-LANYARD", "WP05-SERVICE-THROAT",
             "CLOSED_SWAGED_BODY_EYE", 0.20, flexible)

    # Buoy RF seams, two deliberate harness-capture patches, sewn legs, and tether terminals.
    for index in range(1, 9):
        nxt = index % 8 + 1
        r.direct(f"ATT-BUOY-RF-SEAM-{index:02d}", f"BUOY-GORE-{index:02d}", f"BUOY-GORE-{nxt:02d}",
                 "QUALIFIED_RF_WELDED_GORE_SEAM", 0.05, flexible, True)
    # These are two controlled capture patches, not the former blanket eight-row fallback.
    r.direct("ATT-BUOY-HARNESS-CAPTURE-1", "BUOY-GORE-01", "HARNESS-BAND-1",
             "RF_WELDED_HARNESS_CAPTURE_PATCH", 0.10, flexible, True)
    r.direct("ATT-BUOY-HARNESS-CAPTURE-2", "BUOY-GORE-05", "HARNESS-BAND-2",
             "RF_WELDED_HARNESS_CAPTURE_PATCH", 0.10, flexible, True)
    for leg, band in (("XP", 1), ("XN", 1), ("YP", 2), ("YN", 2)):
        r.direct(f"ATT-HARNESS-LEG-{leg}-BAND", f"HARNESS-LEG-{leg}", f"HARNESS-BAND-{band}",
                 "STRUCTURAL_STITCHED_LAP", 0.02, flexible, True)
        r.direct(f"ATT-HARNESS-LEG-{leg}-TERMINAL", f"HARNESS-LEG-{leg}", "HARNESS-TERMINAL-001",
                 "STITCHED_TERMINAL_LOOP", 0.10, flexible, True)
    for end, yoke in (("BODY", "BODY-HARDPOINT-001"), ("HARNESS", "HARNESS-TERMINAL-001")):
        thimble = f"TETHER-THIMBLE-{end}"
        pin = f"RECOVERY-PIN-{end}"
        clip = f"RECOVERY-PIN-CLIP-{end}"
        r.direct(f"ATT-RECOVERY-THIMBLE-{end}-YOKE", thimble, yoke,
                 "DOUBLE_SHEAR_THIMBLE_TERMINAL", 0.26, fitted, True)
        r.direct(f"ATT-RECOVERY-PIN-{end}-THIMBLE", pin, thimble,
                 "PIN_THROUGH_THIMBLE_EYE", 0.16, fitted, True)
        r.direct(f"ATT-RECOVERY-PIN-{end}-YOKE", pin, yoke,
                 "PIN_THROUGH_DOUBLE_SHEAR_YOKE", 0.21, fitted, True)
        r.direct(f"ATT-RECOVERY-CLIP-{end}", clip, pin,
                 "EXTERNAL_GROOVE_RETAINER", 0.05, fitted)
        r.direct(f"ATT-TETHER-THIMBLE-{end}", "RECOVERY-TETHER-001", thimble,
                 "CONTROLLED_BURIED_EYE_SPLICE", 0.02, flexible, True)

    route_ids = {
        str(row.get("route_occurrence_id", "")).strip()
        for row in builder.routes
        if str(row.get("route_occurrence_id", "")).strip()
    }
    return r.finish(route_ids)


def _pin_candidates(builder: Any) -> set[str]:
    parts = builder.catalog.parts
    result: set[str] = set()
    for occurrence in builder.occurrences:
        part = parts.get(occurrence.part_number)
        description = "" if part is None else str(part.description)
        occurrence_name = occurrence.occurrence_id.upper()
        description = description.upper()
        # Keep this discovery logic bit-for-bit semantically aligned with the
        # independent validator: DOWEL in an occurrence ID is an installed
        # item, while description prose must say the noun phrase DOWEL PIN.
        # This prevents descriptions such as DOWEL-LOCATED FIXED STOP from
        # being false-classified as retained-pin occurrences.
        names_pin = bool(
            re.search(r"(?:^|[^A-Z0-9])(PIN|DOWEL)(?:$|[^A-Z0-9])", occurrence_name)
            or re.search(r"(?:^|[^A-Z0-9])(PIN|DOWEL[ _-]+PIN)(?:$|[^A-Z0-9])", description)
        )
        searchable = f"{occurrence_name} {description}"
        names_retainer = bool(re.search(
            r"(?:^|[^A-Z0-9])(CLIP|RETAINER|RETAINING[ _-]RING|CIRCLIP)(?:$|[^A-Z0-9])",
            searchable,
        ))
        if names_pin and not names_retainer:
            result.add(occurrence.occurrence_id)
    return result


def _retained_pin_requirements(builder: Any, hardware: Any) -> list[dict[str, Any]]:
    state = str(builder.state).upper()
    rows: list[dict[str, Any]] = []

    def add(pin: str, retention: Iterable[str], support: Iterable[str], limit: float, basis: str) -> None:
        retention_ids, support_ids = list(retention), list(support)
        missing = sorted(({pin} | set(retention_ids) | set(support_ids)) - set(builder.global_shapes))
        if missing:
            raise FinalScopeError(f"Retained-pin row {pin} names missing occurrences: {missing}")
        if not retention_ids or not support_ids or not basis.strip():
            raise FinalScopeError(f"Retained-pin row {pin} is incomplete")
        rows.append({
            "pin_occurrence_id": pin,
            "retention_occurrence_ids": retention_ids,
            "support_occurrence_ids": support_ids,
            "maximum_engagement_gap_mm": float(limit),
            "retention_basis": basis,
        })

    add(hardware.TAPER_PIN_IDS[0], ["NOSE-001"], ["BALLAST-001"], 0.05,
        "Occurrence-matched DIN 1B taper in the reamed transverse structural bore.")
    for arm in range(1, 4):
        for index in range(1, 3):
            add(f"FIXED-STOP-DOWEL-{arm}-{index}", [f"FIXED-STOP-{arm}"],
                [f"PIVOT-CARRIER-{arm}"], 0.05,
                "DIN 7 m6 dowel in occurrence-matched H7 stop/carrier bores.")
        add(f"PIVOT-PIN-{arm}", [f"PIVOT-CLIP-{arm}"],
            [f"ARM-{arm}", f"PIVOT-CARRIER-{arm}"], 0.25,
            "Headed shoulder pin retained by the occurrence-specific external ring.")
        for end in ("BELL", "CROSSHEAD"):
            support = [f"LINK-{arm}-1", f"LINK-{arm}-2",
                       f"ARM-{arm}" if end == "BELL" else "CROSSHEAD-001"]
            add(f"LINK-PIN-{arm}-{end}", [f"LINK-CLIP-{arm}-{end}"], support, 0.25,
                "Full-span headed link pin retained by its occurrence-specific crescent ring.")
        inhibit_support = [f"STOW-DOG-GUIDE-{arm}"]
        if state == "STOWED":
            inhibit_support.append(f"STOW-DOG-{arm}")
        add(f"STOW-DOG-INHIBIT-PIN-{arm}", [f"STOW-DOG-INHIBIT-KEEPER-{arm}"],
            inhibit_support, 0.20,
            "Grooved inhibit slider is loss-prevented by its crescent keeper inside the closed guide cage.")
    for label, article_fixed, article_moving in (
        ("GS19", "GS19-BODY-001", "GS19-ROD-001"),
        ("HBD", "HBD-BODY-001", "HBD-ROD-001"),
    ):
        add(f"{label}-PIN-FIXED", [f"{label}-CLIP-FIXED"],
            [article_fixed, f"{label}-FIXED-YOKE"], 0.25,
            "Headed actuator pin retained by its occurrence-specific external ring.")
        add(f"{label}-PIN-MOVING", [f"{label}-CLIP-MOVING"],
            [article_moving, "CROSSHEAD-001"], 0.25,
            "Headed actuator pin retained by its occurrence-specific external ring.")
    for end, yoke in (("BODY", "BODY-HARDPOINT-001"), ("HARNESS", "HARNESS-TERMINAL-001")):
        add(f"RECOVERY-PIN-{end}", [f"RECOVERY-PIN-CLIP-{end}"],
            [f"TETHER-THIMBLE-{end}", yoke], 0.30,
            "Headed recovery pin retained by its occurrence-specific external ring.")
    add("WP04-SEAR-001", ["WP04-SEAR-CLIP-001"], ["WP04-LATCH-001"], 0.25,
        "Guided sear/pin is retained by the occurrence-specific external ring.")
    add("WP05-HINGE-PIN", ["WP05-HINGE-CLIP"],
        ["WP05-DOOR-001", "WP05-SERVICE-THROAT"], 0.20,
        "Headed hinge pin is supported in both knuckle families and retained by its crescent ring.")

    declared = [row["pin_occurrence_id"] for row in rows]
    duplicates = sorted(value for value, count in Counter(declared).items() if count > 1)
    missing = sorted(_pin_candidates(builder) - set(declared))
    if duplicates or missing:
        raise FinalScopeError(
            f"Retained-pin scope mismatch: duplicates={duplicates}, undeclared={missing}"
        )
    return sorted(rows, key=lambda row: row["pin_occurrence_id"])


def build_definition_of_done_requirements(
    builder: Any,
    hardware: Any,
    attachment_requirements: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the validator-ready complete installed-item/DoD declaration."""
    state = str(builder.state).upper()
    installed = sorted(builder.global_shapes)
    attachment_ids = {row["attachment_id"] for row in attachment_requirements}
    route_ids = sorted(
        str(row.get("route_occurrence_id", "")).strip()
        for row in builder.routes
        if str(row.get("route_occurrence_id", "")).strip()
    )
    if len(route_ids) != len(set(route_ids)):
        raise FinalScopeError("Route occurrence IDs are blank or duplicated")

    pressure_rows: list[dict[str, Any]] = []
    for index in range(1, 5):
        pressure_rows.append({
            "subsystem_id": f"CO2-CARTRIDGE-{index}",
            "reservoir_occurrence_id": f"CO2-CARTRIDGE-{index}",
            "closure_occurrence_ids": [f"PUNCTURE-HEAD-{index}"],
            "maximum_closure_gap_mm": 0.15,
            "manifold_occurrence_id": "COLLECTION-MANIFOLD-001",
            "isolation_valve_occurrence_ids": ["FULLFLOW-VALVE-001"],
            "collection_route_occurrence_ids": [
                "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001",
            ],
            "required_attachment_ids": [
                f"ATT-CARTRIDGE-PUNCTURE-{index}",
                f"ATT-PUNCTURE-MANIFOLD-{index}",
                "ATT-FULLFLOW-RING",
                "ATT-ROUTE-MANIFOLD-FEED-ORIGIN",
                "ATT-ROUTE-MANIFOLD-FEED-DEST",
                "ATT-ROUTE-GAS-ORIGIN",
            ],
            "required_route_ids": [
                "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001",
            ],
        })
    for index in range(1, 4):
        pressure_rows.append({
            "subsystem_id": f"BOOSTER-{index}",
            "reservoir_occurrence_id": f"BOOSTER-{index}",
            "closure_occurrence_ids": [
                f"BOOSTER-FWD-CLOSURE-{index}",
                f"BOOSTER-AFT-CLOSURE-{index}",
            ],
            "maximum_closure_gap_mm": 0.05,
            "manifold_occurrence_id": "COLLECTION-MANIFOLD-001",
            "isolation_valve_occurrence_ids": [
                f"BOOSTER-ISOLATION-VALVE-{index}", "FULLFLOW-VALVE-001",
            ],
            "collection_route_occurrence_ids": [
                f"BOOSTER-COLLECTION-LINE-{index}",
                "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001",
            ],
            "required_attachment_ids": [
                f"ATT-BOOSTER-FWD-CLOSURE-{index}",
                f"ATT-BOOSTER-AFT-CLOSURE-{index}",
                f"ATT-BOOSTER-VALVE-{index}",
                f"ATT-BOOSTER-LINE-VALVE-{index}",
                f"ATT-BOOSTER-LINE-MANIFOLD-{index}",
                "ATT-ROUTE-MANIFOLD-FEED-ORIGIN",
                "ATT-ROUTE-MANIFOLD-FEED-DEST",
                "ATT-ROUTE-GAS-ORIGIN",
            ],
            "required_route_ids": [
                f"BOOSTER-COLLECTION-LINE-{index}",
                "ROUTE-MANIFOLD-FEED-001", "ROUTE-GAS-MAIN-001",
            ],
        })

    stow_rows = [{
        "mechanism_id": f"STOW-RETENTION-{arm}",
        "arm_index": arm,
        "required_occurrence_ids": [
            f"ARM-{arm}", f"STOW-DOG-{arm}", f"STOW-DOG-GUIDE-{arm}",
            f"STOW-DOG-SPRING-{arm}", f"STOW-DOG-INHIBIT-PIN-{arm}",
            f"STOW-DOG-INHIBIT-KEEPER-{arm}",
        ],
        "required_attachment_ids": [
            f"ATT-STOW-GUIDE-RING-{arm}", f"ATT-STOW-DOG-GUIDE-{arm}",
            f"ATT-STOW-SPRING-DOG-{arm}", f"ATT-STOW-SPRING-GUIDE-{arm}",
            f"ATT-STOW-INHIBIT-GUIDE-{arm}", f"ATT-STOW-INHIBIT-DOG-{arm}",
            f"ATT-STOW-INHIBIT-KEEPER-{arm}", f"ATT-STOW-KEEPER-GUIDE-{arm}",
            f"ATT-STOW-DOG-ARM-{arm}",
        ],
        "required_motion_track_ids": [
            f"ARM-{arm}", f"STOW-DOG-{arm}", f"STOW-DOG-SPRING-{arm}",
            f"STOW-DOG-INHIBIT-PIN-{arm}", f"STOW-DOG-INHIBIT-KEEPER-{arm}",
        ],
        "stowed_engagement_pair": [f"STOW-DOG-{arm}", f"ARM-{arm}"],
        "maximum_stowed_gap_mm": 0.20,
    } for arm in range(1, 4)]
    lock_rows = [{
        "mechanism_id": f"DEPLOYED-LOCK-{arm}",
        "arm_index": arm,
        "required_occurrence_ids": [
            f"ARM-{arm}", f"ARM-STOP-PAD-{arm}", f"FIXED-STOP-{arm}",
            f"LOCK-DOG-{arm}", f"LOCK-SPRING-{arm}", f"LOCK-BUSHING-{arm}",
        ],
        "required_attachment_ids": [
            f"ATT-ARM-PAD-{arm}", f"ATT-FIXED-STOP-{arm}",
            f"ATT-LOCK-DOG-GUIDE-{arm}", f"ATT-LOCK-SPRING-DOG-{arm}",
            f"ATT-LOCK-SPRING-STOP-{arm}", f"ATT-LOCK-BUSHING-STOP-{arm}",
            f"ATT-LOCK-DOG-PAD-{arm}",
        ],
        "required_motion_track_ids": [
            f"ARM-{arm}", f"ARM-STOP-PAD-{arm}", f"LOCK-DOG-{arm}", f"LOCK-SPRING-{arm}",
        ],
        "deployed_engagement_pair": [f"LOCK-DOG-{arm}", f"ARM-STOP-PAD-{arm}"],
        "maximum_deployed_gap_mm": 0.16,
    } for arm in range(1, 4)]

    active_stow_rows = stow_rows if state == "STOWED" else []
    active_lock_rows = lock_rows if state == "DEPLOYED" else []
    requirements: dict[str, Any] = {
        "required_hardware_occurrence_ids": installed,
        "retained_pin_requirements": _retained_pin_requirements(builder, hardware),
        "pressure_subsystems": pressure_rows,
        "required_closed_route_ids": route_ids,
        "integral_joint_eliminations": [],
    }
    if active_stow_rows:
        requirements["stowed_retention_mechanisms"] = active_stow_rows
    if active_lock_rows:
        requirements["positive_lock_mechanisms"] = active_lock_rows
    required_attachment_ids = {
        attachment_id
        for section in (pressure_rows, active_stow_rows, active_lock_rows)
        for row in section
        for attachment_id in row.get("required_attachment_ids", [])
    }
    missing_attachments = sorted(required_attachment_ids - attachment_ids)
    if missing_attachments:
        raise FinalScopeError(
            f"DoD rows name unknown curated attachments: {missing_attachments}"
        )
    route_set = set(route_ids)
    missing_routes = sorted(
        route_id
        for row in pressure_rows
        for route_id in row["required_route_ids"] + row["collection_route_occurrence_ids"]
        if route_id not in route_set
    )
    if missing_routes:
        raise FinalScopeError(f"DoD pressure rows name unknown routes: {missing_routes}")
    return requirements


def install_final_scope(builder: Any, hardware: Any | None = None) -> dict[str, Any]:
    """Install the final curated records after all endpoint occurrences exist.

    Integration order is intentionally strict:
    ``build geometry -> add all hardware -> add motion tracks/connections ->
    install_final_scope -> serialize/export``.
    """
    if hardware is None:
        import r2_hardware as hardware  # local import avoids a build-time cycle
    attachments = build_attachment_requirements(builder, hardware)
    requirements = build_definition_of_done_requirements(builder, hardware, attachments)
    builder.attachment_requirements = attachments
    builder.definition_of_done_requirements = requirements
    return {
        "attachment_requirements": attachments,
        "definition_of_done_requirements": requirements,
    }


__all__ = [
    "FinalScopeError",
    "build_attachment_requirements",
    "build_definition_of_done_requirements",
    "install_final_scope",
]
