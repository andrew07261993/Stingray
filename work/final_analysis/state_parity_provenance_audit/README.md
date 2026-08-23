# STINGRAY I5-S DF8 state-parity/provenance audit

- Original mismatches: 64
- Category A: 30
- Category B: 34
- Category C: 0
- Same-master prior reimport hash mismatches: 64
- Fresh same-master reimport hash matches: 64
- Forced exact common-volume equivalents: 64
- Fixed transforms unchanged: 30
- Moving transforms expected and changed: 34
- Corrected validator unresolved: 0
- Gate resolved: TRUE
- Actual CAD geometry defect found: FALSE

Root cause: The original validator treated byte-for-byte OCCT local-BREP serialization as exact geometry identity. For the same current AP242 master hashes, validation_cycle2 produced 64 differing state digests while proving exact common volume, and this fresh reimport produced 64 matching state digests; therefore the digest is process-unstable and non-semantic. Fixed rows are invariant; moving rows carry authoritative expected endpoint transform or attachment changes.

No CAD geometry was changed. This audit does not replace the separate exact 0-80 degree motion audit.
