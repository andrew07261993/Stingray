# Renders, Images and Photos

## Canonical GitHub render set

The historical per-part mechanical-breakdown checkpoint at commit `95766a1bfc7bcc48416b83c7b25fcbd482ac0608` contains:

- [116 deterministic per-part PNG renders](https://github.com/andrew07261993/Stingray/tree/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/renders): 104 MAKE and 12 BUY render files;
- [the context-view directory](https://github.com/andrew07261993/Stingray/tree/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views): 9 PNG views plus one evidence-index CSV.

These assets are HISTORICAL R2/mechanical-breakdown visuals. They are not renders of the current Package 05 SHORT14 geometry.

## Nine context views

1. [Product boundary](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_01_PRODUCT_BOUNDARY.png)
2. [Deployed cohesion](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_02_DEPLOYED_COHESION.png)
3. [Terminal chain](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_03_TERMINAL_CHAIN.png)
4. [Water port](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_04_WATER_PORT.png)
5. [Root/route clearance](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_05_ROOT_ROUTE_CLEARANCE.png)
6. [Crosshead retention](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_06_CROSSHEAD_RETENTION.png)
7. [Arm root](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_07_ARM_ROOT.png)
8. [Actuator/spring](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_08_ACTUATOR_SPRING.png)
9. [Route and sear](https://github.com/andrew07261993/Stingray/blob/95766a1bfc7bcc48416b83c7b25fcbd482ac0608/docs/presentations/stingray_df8_mechanical_breakdown/slides/context_views/AFTER_IMAGE_09_ROUTE_AND_SEAR.png)

Local artifact `LA-087`, `before_after_evidence_index.csv`, indexes the same nine source-derived context views with SHA-256 provenance.

## Duplicate branch copies

The per-part, targeted-COTS and COTS-heavy branches contain the same exact visual objects:

| Asset | Exact Git object shared by all three branches |
|---|---|
| 116-render directory | `d00c9719d246032f9a13fdc0f2fe967a38361ccc` |
| Context-view directory | `c553375f2ec201337476ff262665ec775f07a882` |
| Mechanical-breakdown PowerPoint | `e7886e6c0b864dfb357b36d6ffad7b7372830534` |

Only the immutable per-part checkpoint is linked above so GitHub navigation does not show three duplicate collections as separate evidence.

## File Library screenshots

These five cross-device screenshots are indexed by title in [FILE_LIBRARY_MANIFEST.md](../FILE_LIBRARY_MANIFEST.md#f-screenshots-and-visual-session-evidence):

- `E45CDA84-087F-4F61-A4DF-51F131BB6555.png`;
- `0DD29183-9DD3-4BCD-B46E-82EFA499EED2.png`;
- `IMG_4214(1).png`;
- `F7CA155B-E5BF-4914-9B96-580F4D2B7729.jpeg`;
- `IMG_4241.png`.

Their raw File Library bytes were not exposed for GitHub transfer. They remain secondary session/provenance evidence, not CAD authority.

## Current-render gap

No committed render/photo set tied to current Package 05 commit `aa186c9c...` was found. Use the [current AP242 files](02_CAD_AND_3D_FILES.md#current-cad-first) for geometry inspection; do not present the historical R2 render set as current SHORT14 imagery.

Return to [artifact navigation](README.md).
