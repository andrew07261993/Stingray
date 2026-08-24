# Forward Arm Repack Comparison

Status: **OWNER INSPECTION CHECKPOINT — MOTION BOOLEAN GATE INCOMPLETE; NOT FORMAL RELEASE**

| Metric | Baseline `8c594781` | Forward-arm checkpoint | Result |
|---|---:|---:|---|
| Arm pivot axial position / nose-tip-to-pivot | 900.000 mm | 480.000 mm | 420.000 mm forward |
| FWD-RING-01 to arm pivot | 560.000 mm | 140.000 mm | 75.0% shorter station offset |
| Fabric-travel proxy reduction | — | 46.6667% | 420 / 900 |
| Total mass | 11.733427548 kg | 12.189027826 kg | PASS vs 18.14 kg |
| Unallocated mass reserve | 6.406572452 kg | 5.950972174 kg | PASS vs 1.0 kg target |
| Axial CG from nose tip | 581.932620 mm | 581.932620 mm | Restored by retained aft trim ballast |
| Radial CG | 0.106197 mm | 0.128306 mm | +0.022109 mm; remains tightly controlled |
| Principal moments, kg mm^2 | 4324.161 / 3607524.537 / 3607561.810 | 4440.179 / 3611661.523 / 3611716.834 | transverse moments +0.115%; axial +2.68% |
| Rigid length | 2031.0000001 mm | 2031.0000001 mm | PASS vs 2032 mm |
| Stowed external arm/body OML | controlled 57.15 mm hard limit | arm/fixed-sector OML unchanged; ring OD 57.0 mm | PASS by unchanged OML definitions |
| AP242 reimport | 308 solids, zero invalid | 311 solids, zero invalid; leaf identity accepted | PASS; FACETED_BREP 0 |

## Selected arrangement

The coordinated arm station moves from Z=900 mm to Z=480 mm, immediately aft of the retained cartridge/manifold package. The pivot carriers, three arm roots and axes, common crosshead, guide, links, stops, locks, GS-19, HBD-15, backup spring, seats, guide, and local carrier structure retain their relative mechanism geometry and translate as one package. A new aft arm termination ring and transition shell close the structural path.

The three 430 mm booster reservoirs, closures, isolation valves, support bands, water-trigger hardware, full-flow valve, and associated stationary pressure/control lines move aft into the vacated corridor. A 0.351133873 kg centered retained tungsten trim mass at Z=1335 mm restores the baseline axial CG and transverse inertia.

GS-19 and HBD-15 retain the baseline axial installation sense: fixed body ends remain on fixed yokes and moving rod ends remain pinned to the common crosshead. The HBD-15-25-AA-P was not reversed, so the controlled damping direction is not altered. The backup spring retains its moving/fixed seat sense.

Routes changed only where required by the axial repack: the three booster collection lines became supported long stationary feeds, and the gas main, pilot line, Bowden sheath/wire, glands, and support stations were updated for the aft component stations. The cleaned tangent-route construction and terminated endpoint standard were retained.

## Validation result and limitation

Both endpoint masters clean-reimport as AP242 with 311 solids, zero invalid solids, accepted hierarchy/leaf identity, and zero FACETED_BREP. The fail-closed authored attachment graph passed with 282 occurrences; the trim ballast is one valid solid and is retained by six integral shell arms. Kinematic closure at 0, 20, 40, 55, and 80 degrees preserves the baseline 15.055034371 mm crosshead travel.

The exact Boolean five-angle motion audit was invoked for 0, 20, 40, 55, and 80 degrees but was stopped safely before completion at the bounded execution limit. Therefore unauthorized-motion interference remains **UNRESOLVED** and no motion PASS is claimed. No quantitative prior aerodynamic fall model or accepted center-of-pressure metric was found in the controlling repository; aerodynamic equivalence cannot be claimed. The checkpoint instead restores baseline axial CG exactly and holds transverse inertia within +0.12% as the strongest source-supported fall-orientation comparison available.

Owner Creo inspection and completion of the bounded five-angle Boolean audit are required before this checkpoint can be called forward-arm CAD complete or enter formal release validation.
