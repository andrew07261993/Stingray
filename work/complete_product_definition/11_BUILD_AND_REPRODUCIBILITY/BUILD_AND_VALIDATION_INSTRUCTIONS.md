# Build and Validation Instructions

Status: **DEVELOPMENTAL - NOT A PRODUCTION RELEASE**

## Rebuild-source location

The extracted handoff is self-contained under:

- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/r2_source/`
- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/input/`
- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/forward_arm_repack/`
- `11_BUILD_AND_REPRODUCIBILITY/rebuild_source/work/final_analysis/authoring_inventory_stowed.json`
  (the exact source-state inventory required by the post-render comparison)

On Windows, extract the ZIP to a short absolute root (for example `C:\STINGRAY_CPD`) so that CadQuery,
OCCT, rendering, and legacy support-source paths remain within native tool limits. Package enumeration,
hashing, and ZIP verification are long-path safe, but not every third-party CAD/rendering API accepts
extended-path prefixes.

The pinned CadQuery/OCP runtime itself is not embedded; use the exact runtime described in
`DEPENDENCY_AND_ENVIRONMENT_MANIFEST.json`.

Package audit/extraction additionally requires Pillow and pypdf; executive PDF authoring requires
reportlab; executive presentation authoring requires Node.js with `@oai/artifact-tool`; PPTX/PDF visual
QA requires a LibreOffice-compatible headless renderer and Poppler.  These scopes are enumerated in the
dependency/environment manifest.

## Build

First change directory to the delivered rebuild-source root, then invoke the pinned CAD Python runtime:

```powershell
Set-Location 11_BUILD_AND_REPRODUCIBILITY/rebuild_source
$env:PYTHONHASHSEED='0'
<CAD_PYTHON> work/r2_source/short14_external_buoy_build.py --state PAIR --render
```

## Frozen-candidate validation

```powershell
<CAD_PYTHON> work/r2_source/short14_validate_endpoints.py
<CAD_PYTHON> work/r2_source/short14_motion_gate.py --mode five --workers 2 --output-name extraction_test_five_angle
<CAD_PYTHON> work/r2_source/short14_motion_gate.py --mode full --workers 2 --output-name extraction_test_full_motion
```

Use fresh output names; never overwrite historical accepted or failed evidence directories.

## Acceptance discipline

The build must exit zero; both inventories and mass properties must reconcile; OCP/XCAF reimport,
endpoint, five-angle, and full-motion semantic results must pass.  Do not claim byte-identical AP242
reproduction: identical seeded builds currently vary in presentation-style entity order and SHA-256.
That defect remains a non-release exception.

## Reviewed-package status reproduction

The report generator emits conservative pre-review template states.  Follow
`CONTROLLED_STATUS_TRANSITION_PROCEDURE.md` to generate, audit, freeze, review, extract, rebuild, and
transition status rows only after their evidence exists.
