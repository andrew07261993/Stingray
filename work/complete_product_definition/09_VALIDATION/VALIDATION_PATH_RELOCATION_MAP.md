# Validation Path Relocation Map

Status: **DEVELOPMENTAL EVIDENCE - NOT A PRODUCTION RELEASE**

The three validation summaries are byte-preserved copies of the frozen runs.  Some JSON fields retain
absolute source-worktree paths written at run time.  Those strings are provenance, not extraction-time
dependencies.  Use these package-relative equivalents after transfer or extraction:

| Frozen run | Package-relative evidence |
|---|---|
| endpoint | `09_VALIDATION/endpoints/` |
| five-angle | `09_VALIDATION/five_angle/` |
| full 0-80 degree | `09_VALIDATION/full_motion/` |

The copied summary, compressed pair register, transform register, and error register in each directory
belong to the same frozen run.  Do not rewrite the source summary merely to alter its recorded path;
use this relocation map and verify hashes through `12_MANIFESTS/EVIDENCE_REGISTER.csv`.

For a new extracted-run validation, use fresh output names as specified in
`11_BUILD_AND_REPRODUCIBILITY/BUILD_AND_VALIDATION_INSTRUCTIONS.md`.
