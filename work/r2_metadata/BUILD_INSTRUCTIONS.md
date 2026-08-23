# STINGRAY I5S DF8 R2 Candidate WIP — Deterministic Build Instructions

Package status: `CREO_VALIDATION_PENDING — WIP — NOT RELEASED`

These commands regenerate the current editable-source CAD, local component exports, independent OCCT/XCAF evidence, and review workbook. They do not complete or replace the required clean Creo reimport/regeneration gate.

## 1. Preconditions

In the delivered ZIP, change into `/01_EDITABLE_SOURCE/` and run every command from there. That directory contains the complete `work/r2_source` tree and the two accepted source-CAD inputs under `work/input/wp02/accepted_source_cad`. The same commands also run from the original workspace root.

The exact environment captured for this build is recorded in `DEPENDENCIES.json` and mirrored under `work/r2_metadata`. The accepted input files are read-only, byte-preserved source inputs. Do not rename or alter the ACE GS-19 or HBD files because the authoring and component-export scripts resolve those exact filenames. Their hashes and classifications are recorded beside them in `COMPONENT_AND_SOURCE_PROVENANCE.json` and `.csv`.

If `work/cadenv` is not already present, create the open scripted-B-rep runtime with the locked primary packages:

```bash
python3.12 -m venv work/cadenv
work/cadenv/bin/python3 -m pip install \
  cadquery==2.8.0 \
  cadquery-ocp==7.9.3.1.1 \
  cadquery-ocp-proxy==7.9.3.1.1
```

Set deterministic process controls before every run:

```bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export XDG_CACHE_HOME=/tmp/df8-r2-cache
mkdir -p /tmp/df8-r2-cache
```

Confirm the primary runtimes:

```bash
work/cadenv/bin/python3 --version
work/cadenv/bin/python3 -c "import cadquery, OCP; print(cadquery.__version__, OCP.__version__)"
node --version
```

Expected results are Python `3.12.13`, CadQuery `2.8.0`, OCP `7.9.3.1`, and Node.js `v24.19.0`.

## 2. Regenerate the two product AP242 masters

```bash
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/build_r2.py
```

This writes the STOWED and DEPLOYED R2 candidate AP242 masters plus the separately controlled external test-context AP242 file to `work/r2_release`. It also rewrites the authoring inventories and authoring manifest in `work/r2_analysis`.

## 3. Regenerate local component CAD and provenance

```bash
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/export_components.py work/r2_components
```

The reconciled catalog contains 90 unique part identities in each endpoint state. The command writes 180 state-explicit AP242 STEP files and 180 state-explicit OCCT BREP files. Eighteen identities have different local geometry between STOWED and DEPLOYED; both definitions are retained. `provenance.csv` and `provenance.json` lock every component file to the authoring scripts, both authoring inventories, authoring manifest, and frozen master hashes. The two accepted ACE GS-19/HBD references are copied byte-for-byte.

## 4. Run the authoring-model diagnostic audits

```bash
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/authoring_pair_audit.py STOWED
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/authoring_pair_audit.py DEPLOYED
```

These are fast authoring diagnostics only. They are not substitutes for independent AP242 reimport, exhaustive leaf-solid evidence, motion validation, or Creo validation.

## 5. Run clean-process OCCT/XCAF validation

Use a fresh, empty, narrowly scoped evidence directory to prevent stale evidence from being mistaken for current evidence:

```bash
mkdir -p work/r2_analysis/validation
find work/r2_analysis/validation -mindepth 1 -maxdepth 1 -type f -delete
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/validate_r2.py \
  --out work/r2_analysis/validation
XDG_CACHE_HOME=/tmp/df8-r2-cache \
  work/cadenv/bin/python3 work/r2_source/compare_source_reimport.py
```

Do not pass `--skip-motion` for a review build. Any Boolean failure remains BLOCKED and any undocumented positive-volume common remains a failure. `compare_source_reimport.py` must report 181/181 PASS in both states and zero overall failures. This validator intentionally leaves the Creo gate BLOCKED, and the comparison explicitly is not Creo evidence.

Mirror the current validation evidence into the analysis root used by the workbook builder:

```bash
find work/r2_analysis/validation -mindepth 1 -maxdepth 1 -type f \
  -exec cp -f '{}' work/r2_analysis/ \;
cp -f work/r2_metadata/CREO_VALIDATION.json work/r2_analysis/creo_validation.json
cp -f work/r2_components/provenance.csv work/r2_analysis/provenance.csv
```

## 6. Regenerate and visually verify the review workbook

In the captured managed runtime, the workbook dependency tree is exposed at `/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules`. Keep workbook execution isolated under `work/spreadsheet_runtime` so the editable source remains unchanged and bare module resolution is reproducible:

```bash
mkdir -p work/spreadsheet_runtime
test -L work/spreadsheet_runtime/node_modules || \
  ln -s /opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules \
  work/spreadsheet_runtime/node_modules
install -m 0644 work/r2_source/build_workbook.mjs \
  work/spreadsheet_runtime/build_workbook.mjs
(cd work/spreadsheet_runtime && node build_workbook.mjs)
```

The command must finish with no formula-error matches, render all 20 sheet previews under `work/r2_analysis/workbook_previews`, and export `work/r2_release/STINGRAY_I5S_DF8_R2_CANDIDATE_WIP_REVIEW_WORKBOOK.xlsx`.

## 7. Required clean Creo gate

No Creo executable or clean Creo session was available in this environment. Before any release promotion, both product AP242 masters must be opened in a new clean Creo session, fully regenerated, and checked for import errors, failed features, missing occurrences, geometric invalidity, exact interference, required clearances, assembly placements, and mass/envelope dimensions. The resulting Creo-native evidence must identify the exact input file hashes and Creo build.

Until that evidence exists and passes, retain `CREO_VALIDATION.json` unchanged and label every package exactly:

`CREO_VALIDATION_PENDING — WIP — NOT RELEASED`
