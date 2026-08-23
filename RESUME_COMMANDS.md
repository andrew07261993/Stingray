# DF8 resumption commands

Run commands from the extracted checkpoint root. All checkpoint paths below are
relative. The safe default is inspection only.

## Authorized integrity inspection

```bash
sha256sum -c SHA256SUMS.txt
python3 - <<'PY'
import json
state = json.load(open('CURRENT_STATE.json', encoding='utf-8'))
print(json.dumps(state['validation'], indent=2))
PY
```

## Non-modifying authoring-output integrity

```bash
python3 - <<'PY'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('work/final_analysis/authoring_manifest.json').read_text(encoding='utf-8'))
assert manifest['schema'] == 'AP242'
paths = {
    **{name: Path('work/final_release') / name for name in manifest['files']},
    **{name: Path('work/final_analysis') / name for name in manifest['inventories']},
}
records = {**manifest['files'], **manifest['inventories']}
for name, path in sorted(paths.items()):
    data = path.read_bytes()
    assert len(data) == records[name]['size_bytes'], name
    assert hashlib.sha256(data).hexdigest() == records[name]['sha256'], name
print('AUTHORING MANIFEST INTEGRITY: PASS')
PY
```

## Non-modifying Python AST source parse

This parses source text without importing or executing authoring modules.

```bash
python3 - <<'PY'
import ast
from pathlib import Path
roots = (Path('work/r2_source'), Path('work/final_tools'), Path('work/scripts'), Path('work/handoff_tools'))
paths = sorted(path for root in roots for path in root.rglob('*.py'))
assert paths
for path in paths:
    ast.parse(path.read_text(encoding='utf-8'), filename=path.as_posix())
print(f'PYTHON AST SOURCE PARSE: PASS ({len(paths)} files)')
PY
```

Read the controlling records before any engineering action:

```bash
sed -n '1,240p' commission/ORIGINAL_COMMISSION_20260821-031917.md
sed -n '1,260p' commission/R1_REJECTION_R2_CORRECTION_20260821-171406.md
sed -n '1,260p' commission/SAFE_CODEX_HANDOFF_RUNTIME_DIRECTIVE.md
```

Creo is informational N/A exactly as follows:

`N/A — NOT REQUIRED BY THE CONTROLLING COMMISSION; OWNER CREO IMPORT OCCURS AFTER DELIVERY.`

OCP/XCAF clean-process AP242 reimport is the controlling neutral-CAD gate.
No new correction cycle or final release packaging is authorized by this
handoff.

`work/scripts` is historical/non-runnable without omitted original input trees.
The authoritative build uses the full copied `work/input/wp02` tree, including
the exact GS-19 and HBD-15 live vendor-source files required by `build_r2.py`.
Copied absolute paths inside historical evidence are provenance-only, and no
No /tmp state is required after the sweep.

## Environment restoration (reference only; requires renewed authorization)

The virtual environment and Node module tree are intentionally excluded. The
captured pins are under `environment/`.

```bash
python3.12 -m venv work/cadenv
work/cadenv/bin/python3 -m pip install   --requirement environment/PYTHON_REQUIREMENTS_FULLY_PINNED.txt
test -n "${CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}"
mkdir -p work/spreadsheet_runtime
ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
```

## Exact command catalog (reference only; not authorized at handoff)

STOWED rebuild and DEPLOYED rebuild are intentionally one command because the
state-invariant exact-BREP cache requires ordered same-process authoring. This
command also performs both final AP242 exports:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/build_r2.py
```

STOWED audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py STOWED work/final_analysis/per_solid_authoring_audit_stowed.json
```

DEPLOYED audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py DEPLOYED work/final_analysis/per_solid_authoring_audit_deployed.json
```

Clean-process AP242 reimport, both endpoint audits, and exact 0°–80°/1°
motion audit:

```bash
PYTHONPATH=work/r2_source work/cadenv/bin/python work/r2_source/validate_r2.py --out work/final_analysis/validation --motion-workers 8
```

Workbook generation:

```bash
mkdir -p work/spreadsheet_runtime
test -n "${CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}"
test -e work/spreadsheet_runtime/node_modules ||   ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
install -m 0644 work/r2_source/build_workbook.mjs   work/spreadsheet_runtime/build_workbook.mjs
(cd work/spreadsheet_runtime && node build_workbook.mjs)
```

Final ZIP generation:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/final_tools/package_final.py
```

## Mutating engineering sequence (reference only; not authorized at handoff)

Reproduce the latest STOWED exact-solid authoring audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py STOWED work/final_analysis/per_solid_authoring_audit_stowed.json
```

Reproduce the latest DEPLOYED exact-solid authoring audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/per_solid_authoring_audit.py DEPLOYED work/final_analysis/per_solid_authoring_audit_deployed.json
```

Reproduce the curated attachment-distance scope audit:

```bash
PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/final_tools/audit_final_scope.py --out work/final_analysis/final_scope_audit.json
```

Continue the bounded sequence only if new controlling authority explicitly
reopens it. The exact rebuild/AP242-export command is:

```bash
export LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONHASHSEED=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export XDG_CACHE_HOME="${TMPDIR:-.tmp}/df8-r2-cache"
mkdir -p "$XDG_CACHE_HOME"

PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/r2_source/build_r2.py

validation=work/final_analysis/validation
if test -e "$validation"; then
  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  mv -- "$validation" "${validation}.previous.${stamp}"
fi
mkdir -p "$validation"
PYTHONPATH=work/r2_source work/cadenv/bin/python work/r2_source/validate_r2.py --out work/final_analysis/validation --motion-workers 8

jq -e '.computed_release_status=="PASS" and
  .package_required_label=="FINAL — RELEASED" and
  .gate_counts.PASS==31 and .gate_counts.FAIL==0 and
  .gate_counts.BLOCKED==0 and all(.gates[]; .status=="PASS")'   "$validation/gate_results.json"

mkdir -p work/spreadsheet_runtime
test -n "${CODEX_PRIMARY_RUNTIME_NODE_MODULES:-}"
test -e work/spreadsheet_runtime/node_modules ||   ln -s "$CODEX_PRIMARY_RUNTIME_NODE_MODULES" work/spreadsheet_runtime/node_modules
install -m 0644 work/r2_source/build_workbook.mjs   work/spreadsheet_runtime/build_workbook.mjs
(cd work/spreadsheet_runtime && node build_workbook.mjs)

PYTHONPATH="$PWD/work/r2_source" work/cadenv/bin/python3 work/final_tools/package_final.py
```

Do not use the stale candidate instructions in `work/r2_metadata/` as release
authority. Do not pass `--skip-motion` for release evidence. The validator may
exit zero with failed or blocked gates, so the explicit gate-result check is
mandatory whenever a future controlling instruction authorizes validation.
