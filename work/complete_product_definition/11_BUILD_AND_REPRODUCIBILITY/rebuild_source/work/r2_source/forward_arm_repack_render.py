#!/usr/bin/env python3
"""Generate exactly five deterministic BREP-derived inspection PNGs."""

from pathlib import Path
import shutil

from PIL import Image, ImageDraw

import build_r2
import render_evidence

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "forward_arm_repack" / "inspection_views"
OUT.mkdir(parents=True, exist_ok=True)
render_evidence.OUT = OUT

baseline_source = Path(r"C:\Users\ANDRE.ANDREWSPC\Documents\Codex\2026-08-23\stingray-i5-s-df8-final-cad-semantic-cleanup\work\r2_package\stage\05_VALIDATION_EVIDENCE\before_after_views\r1_controlled_reference_views\STOWED_ISOMETRIC.png")
baseline_target = OUT / "01_BASELINE_FULL_LENGTH_OLD_PIVOT.png"
shutil.copy2(baseline_source, baseline_target)
image = Image.open(baseline_target).convert("RGB")
draw = ImageDraw.Draw(image)
x = int(image.width * 0.46)
draw.line((x, 20, x, image.height - 20), fill=(220, 35, 35), width=4)
draw.text((x + 8, 24), "OLD ARM PIVOT Z=900.0 mm", fill=(180, 20, 20))
image.save(baseline_target)

stowed = build_r2.build_state("STOWED")
deployed = build_r2.build_state("DEPLOYED")
all_stowed = sorted(stowed.global_shapes)
all_deployed = sorted(deployed.global_shapes)

render_evidence.render(stowed, all_stowed, "02_UPDATED_STOWED_FULL_LENGTH_NEW_PIVOT.png",
                       "Updated STOWED — new arm pivot Z=480.0 mm", 0, -90, 3.0)
render_evidence.render(deployed, all_deployed, "03_UPDATED_DEPLOYED_SIDE.png",
                       "Updated DEPLOYED — 80 degree endpoint", 0, -90, 3.0)
render_evidence.render(stowed, [
    "FWD-RING-01", "FWD-RING-02", "ARM-TERMINATION-RING-001", "AFT-REPACK-SHELL-001",
    *[f"BOOSTER-{i}" for i in range(1, 4)], "CG-TRIM-BALLAST-001",
    "CROSSHEAD-001", "GS19-BODY-001", "GS19-ROD-001", "HBD-BODY-001", "HBD-ROD-001",
    "BACKUP-SPRING-001", "BACKUP-SPRING-GUIDE",
], "04_FWD_RING_BAY_CUTAWAY.png", "FWD-RING-01 to aft repack bay — shell-transparent cutaway", 12, -55, 1.5)
render_evidence.render(stowed, [
    *[f"PIVOT-CARRIER-{i}" for i in range(1, 4)], *[f"ARM-{i}" for i in range(1, 4)],
    "CROSSHEAD-001", "CROSSHEAD-GUIDE-001", "GS19-BODY-001", "GS19-ROD-001", "GS19-FIXED-YOKE",
    "HBD-BODY-001", "HBD-ROD-001", "HBD-FIXED-YOKE", "BACKUP-SPRING-001",
    "BACKUP-SPRING-GUIDE", "BACKUP-SPRING-FIXED-SEAT", "BACKUP-SPRING-MOVING-SEAT",
], "05_ARM_CARRIER_GS_HBD_SPRING_CLOSEUP.png", "Forward arm carrier / GS-19 / HBD-15 / backup spring", 18, -42, 0.75,
   ((-32, 32), (-32, 32), (455, 710)))

updated = Image.open(OUT / "02_UPDATED_STOWED_FULL_LENGTH_NEW_PIVOT.png").convert("RGB")
draw = ImageDraw.Draw(updated)
x = int(updated.width * 0.30)
draw.line((x, 20, x, updated.height - 20), fill=(220, 35, 35), width=4)
draw.text((x + 8, 24), "NEW ARM PIVOT Z=480.0 mm", fill=(180, 20, 20))
updated.save(OUT / "02_UPDATED_STOWED_FULL_LENGTH_NEW_PIVOT.png")

print(f"Wrote exactly {len(list(OUT.glob('*.png')))} inspection PNGs to {OUT}")
