
# WP02 Geometry Integrity Report

The two delivered state files contain only WP02-owned solids at the DF8 default coordinates; the accepted WP01 shell/covers are loaded separately for the audit. The arm motion audit samples 1, 5, 10, 20, 30, 40, 50, 60, 70 and 80 degrees. The corresponding cover is closed only at the 1-degree stowed state; at every moving sample it is at the WP01 90-degree open stop, enforcing cover-before-arm sequencing.

All sampled arm/shell and arm/cover exact Boolean checks are zero-volume. Central powertrain lanes were separately checked for the critical GS/HBD, GS/pushrod, HBD/pushrod and spring/pushrod pairs. The minimum nominal GS-to-HBD gap is 0.50 mm. The clearance register applies explicit tolerance/environment allowances and flags any residual margin below zero.

Pin/arm/link zero-distance fits, spring-seat end contact, and lock/stop contact are intentional interfaces. They are classified in the attachment audit rather than misreported as free clearances. A separate full-solid pair audit records every broad-phase occurrence pair in both delivered states. Its only positive volumes are the intentionally split fixed-body/moving-rod representations within the GS-19 and HBD-15 service items; all custom-to-custom and custom-to-COTS pairs are zero-volume. Native Creo validation is unavailable and is not claimed; independent OCCT/CadQuery reimport results are supplied separately.
