
# WP02 Full-Solid Pair Audit

Every broad-phase rigid occurrence pair was checked by exact Boolean common volume in both delivered states. The raw output and executable audit source are preserved, and the package build accepted the result only after exact equality of every occurrence's state geometry signature (solid/face/edge counts, volume, and bounding box). Custom-to-custom and custom-to-COTS pairs have zero positive common volume. The only positive volumes are the fixed-body/moving-rod decomposition pairs inside the GS-19 and HBD-15 service items. These are intentional internal telescoping representations used to preserve named AP242 prismatic occurrences, not collisions between separate physical components.

- STOWED: 85 broad-phase occurrence pairs; 2 positive pairs; 0 unresolved.
- DEPLOYED: 78 broad-phase occurrence pairs; 2 positive pairs; 0 unresolved.

The two accepted positive pairs are classified `INTENTIONAL_INTERNAL_COTS_TELESCOPING_REPRESENTATION`. No other positive rigid common volume is accepted.
