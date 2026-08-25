# Architecture C 889 mm Fallback Creo Inspection Package

**MEASURED DEVELOPMENTAL FALLBACK — OWNER CREO COMPARISON ONLY — NOT FORMAL RELEASE CAD.**

- Local source branch: `design/df8-final-converged-cots-forward-arm`
- Repository checkpoint at artifact creation/current checkout: `17870c53e3ceecbab88e28d7ccad0ae7047f1db6`
- Artifact provenance: local fallback checkpoint retained outside the Git commit at the source worktree
- Nose-tip-to-arm-pivot: `889.000 mm`
- Architecture: Architecture C measured packaging fallback
- Five-angle targeted validation: passed at the measured checkpoint
- ZIP SHA-256: `52b84958d7c13ae1c59930b862e23f875a083dad28f66df09ff8d25fab65d6d7`
- STOWED AP242 SHA-256: `084ae63e055ecaa4844cb8b548846b27d49ace38b07e4a5bfab8ffa98c460e93`
- DEPLOYED AP242 SHA-256: `564529496792f792d640eb193d924df5ea2d5802f36c2ab5605ae64d2cc95f30`

This checkpoint is not owner-accepted as the final architecture and sacrifices nearly all of the 480 mm forward-arm benefit. It is retained for Creo comparison and rollback/reference only.

Known validation limitation: the source validation classifies this as a measured non-pass checkpoint; retained aft recovery/service hard geometry exceeds the `57.15 mm` keep-in. Passing targeted geometry checks does not make this release CAD.
