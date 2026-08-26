# STINGRAY Artifact Navigation

This directory is the GitHub browsing layer for the consolidated STINGRAY engineering record. It organizes evidence by artifact type and by chronological design iteration without moving, renaming or duplicating protected CAD packages.

## Current engineering anchor

| Field | Current value |
|---|---|
| Configuration | `STINGRAY_I5S_DF8_SHORT14_FORWARD_POWERTRAIN_EXTERNAL_BUOY` |
| Local source branch | `design/df8-14in-short-forward-powertrain-external-buoy` |
| Source commit | `aa186c9c1c311c510ac34e48bd4170ef7636b7bf` |
| Classification | **CURRENT DEVELOPMENTAL** |
| GitHub inspection checkpoint | [Package 05](../../../cad/df8-owner-creo-inspection-zips/05_TRUE_FORWARD_POWERTRAIN_SHORT14_EXTERNAL_BUOY/) |

The current anchor is developmental CAD, not fabrication, procurement, qualification or operational release.

## Browse by type

| Order | Category | What it contains | Indexed local artifacts |
|---:|---|---|---:|
| 1 | [Iterations in chronological order](01_ITERATION_TIMELINE.md) | Reference work through Package 05, with branch/commit/status boundaries | 18 ordered stages |
| 2 | [CAD and 3D files](02_CAD_AND_3D_FILES.md) | STEP/AP242, STP/vendor CAD, Creo status and STL status | 20 |
| 3 | [Analyses and validation](03_ANALYSES_AND_VALIDATION.md) | Design reports, calculations, screens, audits, validation evidence and the remaining data/name-map row | 45 |
| 4 | [Renders, images and photos](04_RENDERS_IMAGES_AND_PHOTOS.md) | 116 part renders, 9 context views, screenshot references and visual-evidence rules | 1 local index + 125 GitHub PNGs |
| 5 | [PowerPoints and presentations](05_POWERPOINTS_AND_PRESENTATIONS.md) | GitHub-resident mechanical breakdown deck and File Library presentation references | 2 local copies |
| 6 | [Documents, PDFs and prompts](06_DOCUMENTS_PDFS_AND_PROMPTS.md) | Control documents, Markdown reports, commissions/prompts and explicit PDF/DOCX gaps | 1 primary document row; other Markdown is grouped by engineering role |
| 7 | [ZIPs and packages](07_ZIPS_AND_PACKAGES.md) | Five protected GitHub inspection packages plus indexed local archives | 11 |
| 8 | [COTS, vendor data and BOMs](08_COTS_VENDOR_AND_BOMS.md) | COTS master register, vendor evidence, BOMs, trade studies and procurement boundaries | 30 |

## Complete sortable catalog

[ARTIFACT_CATALOG_BY_TYPE.csv](ARTIFACT_CATALOG_BY_TYPE.csv) contains all **110** indexed local artifacts exactly once. It adds:

- `navigation_category`;
- `iteration_order`;
- `iteration_label`;
- the original path, branch, commit, date, classification, SHA-256, relevance and notes.

The original canonical evidence table remains [LOCAL_ARTIFACT_INDEX.csv](../../../context/stingray/LOCAL_ARTIFACT_INDEX.csv).

## GitHub-resident visual and CAD assets

- Five protected inspection ZIPs and four endpoint STEP files are already present under [the owner-inspection checkpoint](../../../cad/df8-owner-creo-inspection-zips/).
- The canonical historical mechanical-breakdown branch contains 116 per-part renders, 9 context-view PNGs and one PowerPoint. The same exact Git objects also appear on the targeted-COTS and COTS-heavy branches; the navigation pages link one immutable copy to avoid duplicate browsing.
- No `.stl`, `.pdf`, `.docx`, native Creo `.prt`/`.asm`, or current Package 05 render set was found in the bounded local artifact index or the observed GitHub branch trees. These absences are recorded explicitly; no placeholder files were invented.

## Authority rule

Organization does not change authority. Select engineering truth by exact configuration, owner chronology, source path, branch/commit, hashes and validation status. Historical renders, decks and detailed reports do not override the current source configuration.

Return to [the canonical read-first page](../00_READ_ME_FIRST.md).
