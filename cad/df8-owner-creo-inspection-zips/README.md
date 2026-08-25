# DF8 Owner Creo Inspection ZIP Packages

> **THESE ARE ENGINEERING INSPECTION PACKAGES FOR OWNER CREO REVIEW. NONE SHALL BE TREATED AS FORMAL RELEASE CAD.**

These four packages preserve eight existing STOWED/DEPLOYED AP242 models for owner Creo inspection from the NASA computer. Package 04 also exposes both STEP files individually for direct download. No CAD geometry or STEP file was regenerated for this transfer.

| Package | Arm station | Arm length | Body length | Buoy architecture | Status | Creo purpose |
|---|---:|---:|---:|---|---|---|
| 480 mm Forward Arm Repack | 480 mm | — | — | mixed/original pressure architecture | preferred forward-arm geometric reference | inspect arm placement and repack |
| Architecture C Forward-Packed | forward-packed developmental | — | — | COTS-heavy | NOT RELEASED; known interference | inspect COTS-heavy packaging |
| Architecture C 889 mm Fallback | 889 mm | — | — | COTS-heavy | measured fallback | compare aft-arm packaging |
| 14-in Short-Arm / External-Buoy | 480 mm | 14.890 in | 1675.4 mm | External Cordura breakaway buoy pack / UML MK5 proxy | Developmental CAD complete | Inspect compact short-arm / short-body architecture |

**PACKAGE 04 IS CURRENTLY THE MOST AGGRESSIVE COMPACT-BODY DEVELOPMENTAL VARIANT.**

## Source, integrity, and limitation record

### 01 — 480 mm Forward Arm

- Local source branch: `design/df8-forward-arm-repack`
- Controlling commit: `a31fce0e768f354b1831331bc2ed145223c8b2c4` (validated correction includes `c303e22d39ebb4030654e5ca2bea70f552398bf1`)
- ZIP SHA-256: `e2abcd407afaaccaa5be87befde371b65d84317449dfbc127022309914cac20e`
- Contained STOWED SHA-256: `95bd31b29e1801c7a3463df043f6dbfbf98d46cec555131e55152c7395c3ca40`
- Contained DEPLOYED SHA-256: `1785b583b7ef5ed050819f5094026245647f4b0ea58fa36e8e38804c0f9b8df7`
- Known validation limitation: quantitative aerodynamic equivalence remains separately unproven; bounded geometric validation is not formal release acceptance.

### 02 — Architecture C Forward-Packed

- Local source branch: `build/arch-c-forward-packed`
- Controlling commit: `2bc9e324096148394567f4d4ab1ff7e6540ab599`
- ZIP SHA-256: `bb4b169078fd9e27840d13204feb1bc2b7204de7677d788c52fcab81fe66aceb`
- Contained STOWED SHA-256: `0d1a6ca95b4bb0acfb65ff7fc7bd7a745eaf9d0dab98161ad0a613d89bf463f2`
- Contained DEPLOYED SHA-256: `0ed06f408b8b184d23eeb49c31a4f21337dce5e733b837039611cef0a5920800`
- Known validation limitation: this controlling checkpoint retains the `50.038 mm` cylinder / inherited-longeron interference and `71` STOWED / `64` DEPLOYED unauthorized rigid-interference audit result; it is NOT RELEASED.
- Reconciliation note: the local branch has a later corrected pair at `abe9d93d2dada6150daa9a652885c472a6a06464`; this package preserves the exact hashes specified for `2bc9e324096148394567f4d4ab1ff7e6540ab599` without regeneration.

### 03 — Architecture C 889 mm Fallback

- Local source branch: `design/df8-final-converged-cots-forward-arm`
- Controlling repository checkpoint: `17870c53e3ceecbab88e28d7ccad0ae7047f1db6` (the preserved fallback artifact was local-only/untracked in that source worktree)
- ZIP SHA-256: `52b84958d7c13ae1c59930b862e23f875a083dad28f66df09ff8d25fab65d6d7`
- Contained STOWED SHA-256: `084ae63e055ecaa4844cb8b548846b27d49ace38b07e4a5bfab8ffa98c460e93`
- Contained DEPLOYED SHA-256: `564529496792f792d640eb193d924df5ea2d5802f36c2ab5605ae64d2cc95f30`
- Known validation limitation: measured non-pass checkpoint; retained aft recovery/service hard geometry exceeds the `57.15 mm` keep-in, and the architecture is not owner-accepted.

### 04 — 14-Inch Short-Arm / External-Buoy

- Local source branch: `design/df8-14in-short-arm-external-buoy-pack`
- Completed source commits: `0f21a655a3a8e0f98faba950a233ee0636a7626d`, `3ffc5c8dbc31381c2272141fa1ec827ed9532f9c`, `34f1b9e85906cd70af42219936921b145d318315`, `0431fe05465ba59a1714f110a07c73f146131c96`
- ZIP SHA-256: `fe8254034291853678ae5a1f5b3d1bb8cb9d88eacafe12676dfb89f4afa92ff2`
- STOWED AP242 SHA-256: `0e24135f35f86e5ec727bfcffa0f6d9c55195c44ab8af90c7a29b5a95cb505c7`
- DEPLOYED AP242 SHA-256: `dda7dde5140ff6a108f4e501f4a1e1d974a533b93403cc6ac13beb64f398d244`
- Known validation limitation: physical wet inflation/peel, fabric engagement, snag/retention/extraction, recovery proof-load, controlled vendor geometry/material evidence, procurement identity/CoC, and quantitative fall/orientation verification remain downstream gates.
- Status: developmental engineering inspection model; not formal release CAD.

Each package directory includes `SHA256SUMS.txt` with the ZIP hash and hashes for every contained entry.
