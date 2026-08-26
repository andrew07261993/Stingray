#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, importlib.util, json, math, platform, re, shutil, sys, time, zipfile
from pathlib import Path

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

WORK=Path('/mnt/data/wp02_work')
ROOT=Path('/mnt/data/STINGRAY_I5S_DF8_WP02_ARM_AND_POWERTRAIN')
OUT=Path('/mnt/data')
BUILD_SCRIPT=WORK/'build_wp02.py'
CACHE=WORK/'full_pair_audit_cache.json'

spec=importlib.util.spec_from_file_location('wp02_build_finalize',BUILD_SCRIPT)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')


def write_json(path: Path, obj) -> None:
    write_text(path,json.dumps(obj,indent=2,sort_keys=True))


def write_csv(path: Path, fields, rows) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(fields),extrasaction='ignore',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def reimport_step(path: Path, expected: dict) -> dict:
    t0=time.time()
    r=STEPControl_Reader()
    status=r.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f'STEP ReadFile failed for {path}: {int(status)}')
    transferred=r.TransferRoots()
    shape=r.OneShape()
    exp=TopExp_Explorer(shape,TopAbs_SOLID)
    solid_count=valid_count=0; volume=0.0
    while exp.More():
        solid=exp.Current(); solid_count+=1
        if BRepCheck_Analyzer(solid).IsValid(): valid_count+=1
        props=GProp_GProps(); BRepGProp.VolumeProperties_s(solid,props); volume+=props.Mass()
        exp.Next()
    bb=Bnd_Box(); BRepBndLib.Add_s(shape,bb)
    xmin,ymin,zmin,xmax,ymax,zmax=bb.Get()
    header=path.read_text(encoding='latin-1',errors='ignore')[:30000]
    product_count=len(re.findall(r'\bPRODUCT\(',path.read_text(encoding='latin-1',errors='ignore')))
    expected_volume=sum(v['volume_mm3'] for v in expected.values())
    expected_solids=sum(v['solid_count'] for v in expected.values())
    expected_bbox=[
        min(v['bbox_mm'][0] for v in expected.values()),max(v['bbox_mm'][1] for v in expected.values()),
        min(v['bbox_mm'][2] for v in expected.values()),max(v['bbox_mm'][3] for v in expected.values()),
        min(v['bbox_mm'][4] for v in expected.values()),max(v['bbox_mm'][5] for v in expected.values()),
    ]
    bbox=[xmin,xmax,ymin,ymax,zmin,zmax]
    volume_diff=volume-expected_volume
    bbox_max_delta=max(abs(a-b) for a,b in zip(bbox,expected_bbox))
    ap242='AP242_MANAGED_MODEL_BASED_3D_ENGINEERING' in header
    units=('.MILLI.,.METRE.' in header.upper() or 'MILLIMETRE' in header.upper())
    status_txt='PASS' if (
        solid_count==expected_solids and valid_count==solid_count and
        abs(volume_diff)/max(expected_volume,1.0)<1e-6 and bbox_max_delta<1e-3 and
        ap242 and units and product_count==35
    ) else 'REVIEW'
    return {
        'state':path.stem.split('_')[-2],
        'file':path.name,
        'sha256':sha256(path),
        'read_status':'IFSelect_RetDone',
        'transferred_roots':transferred,
        'ap242_header_present':ap242,
        'units_mm':units,
        'named_product_count':product_count,
        'expected_solid_count':expected_solids,
        'reimport_solid_count':solid_count,
        'valid_solid_count':valid_count,
        'expected_volume_mm3':expected_volume,
        'reimport_volume_mm3':volume,
        'volume_difference_mm3':volume_diff,
        'expected_bbox_mm':expected_bbox,
        'reimport_bbox_mm':bbox,
        'maximum_bbox_delta_mm':bbox_max_delta,
        'reimport_seconds':time.time()-t0,
        'status':status_txt,
        'kernel_note':'Independent post-export process using OCCT 7.9 STEPControl; not a different CAD kernel and not native Creo.',
    }


def main():
    if not ROOT.exists(): raise FileNotFoundError(ROOT)
    cache=json.loads(CACHE.read_text())
    sigs=cache['geometry_signatures']
    state_files={
        'STOWED':ROOT/'05_SUBSYSTEM_CAD'/f'{m.PACKAGE_NAME}_STOWED_AP242.step',
        'DEPLOYED':ROOT/'05_SUBSYSTEM_CAD'/f'{m.PACKAGE_NAME}_DEPLOYED_AP242.step',
    }
    for p in state_files.values():
        if not p.exists(): raise FileNotFoundError(p)
    rows=[reimport_step(state_files[st],sigs[st]) for st in ('STOWED','DEPLOYED')]
    if any(r['status']!='PASS' for r in rows):
        raise RuntimeError(f'Reimport validation did not pass: {rows}')

    write_csv(ROOT/'07_GEOMETRY_INTEGRITY'/'WP02_STEP_REIMPORT_VALIDATION.csv',list(rows[0].keys()),rows)
    write_json(ROOT/'07_GEOMETRY_INTEGRITY'/'WP02_STEP_REIMPORT_VALIDATION.json',rows)
    write_text(ROOT/'07_GEOMETRY_INTEGRITY'/'WP02_STEP_REIMPORT_REPORT.md',"""
# WP02 STEP Reimport Report

Both top-level AP242 state files were reopened after export in a separate OCCT STEPControl process. The check verifies AP242 schema, millimetre units, 35 named products per assembly, root transfer, solid count, individual-solid validity, aggregate volume, and bounding box against the controlled source-state signatures.

This is an independent post-export execution but not an independent CAD kernel: both export and reimport use OCCT 7.9. Native Creo validation and a genuinely different-kernel import remain external evidence requirements and are not claimed.
""")

    write_text(ROOT/'09_ASSEMBLY_SERVICE_AND_VERIFICATION'/'WP02_TOOL_ACCESS_REVIEW.md',"""
# WP02 Digital Tool-Access Review

| Service operation | Controlled access route | Digital result | Remaining physical proof |
|---|---|---|---|
| GS-19 removal/installation | Open the associated WP01 arm-bay cover, mechanically control stored energy, remove the cartridge-side support and M8 adapter connection, then withdraw the GS axially through the service bay. | No rigid part blocks the modeled withdrawal corridor. | Verify exact purchased B8 thread length, wrench/driver head envelope, hand clearance, anti-rotation method, and torque access in a representative assembly. |
| HBD-15 removal/installation | Open the arm-bay cover, unload the crosshead, release the moving lost-motion coupler, remove the captive bypass carriage shoulders, and withdraw the HBD cartridge. | Rails, carriage, body and rod are digitally separable without shell removal. | Verify exact configured HBD suffix geometry, adjustment access, fitting clearance, drainage, and post-saltwater removal force. |
| Backup spring replacement | Install the guarded reset fixture, engage the positive sear, unload the moving seat, remove the fixed-seat retainer, and withdraw spring/guide through the opened module bay. | The selected 15.24 mm OD spring and 6 mm guide fit the controlled core and modeled service corridor. | Conduct a guarded assembly trial; verify fixture reaction path, capture during seat removal, glove/tool clearance, and no uncontrolled release. |
| Arm/link/pin/bushing service | Open all covers, control the crosshead, remove the applicable captive ring/headed pin, and withdraw the arm or link in its radial plane. | Pin axes and withdrawal paths are exposed with covers open; no custom cross-component positive common volume remains. | Verify ring plier access, pin extraction force, field-loss prevention, corrosion product allowance, and bushing replacement tooling. |
| Stop-pad and lock service | Open the matching cover, support the arm at the stop, retract the lock plunger, and remove the local pad/lock hardware. | Witness and lock features remain directly visible in the deployed state. | Verify sight line, gauge access, reverse-load release, pad replacement, fastener torque access, and wear limits. |

The review is a geometry-based access screen, not an ergonomic, maintainability, or human-factors qualification. Exact tools, torque values, fastener procurement identities, and representative gloved-service trials remain open.
""")

    # Update source and build records after all generated evidence exists.
    shutil.copy2(BUILD_SCRIPT,ROOT/'10_REPRODUCIBLE_SOURCE'/'build_wp02.py')
    shutil.copy2(Path(__file__),ROOT/'10_REPRODUCIBLE_SOURCE'/'finalize_existing_wp02.py')
    shutil.copy2(WORK/'quick_reimport.py',ROOT/'10_REPRODUCIBLE_SOURCE'/'quick_reimport.py')
    write_json(ROOT/'10_REPRODUCIBLE_SOURCE'/'WP02_FINALIZATION_ENVIRONMENT.json',{
        'python':sys.version,'platform':platform.platform(),'occt':'7.9.3.1',
        'finalizer_sha256':sha256(Path(__file__)),'geometry_audit_cache_sha256':sha256(CACHE),
        'note':'Post-export reimport/finalization; native Creo unavailable.'
    })

    mass=json.loads((ROOT/'06_ENGINEERING_ANALYSIS'/'WP02_MASS_PROPERTY_SUMMARY.json').read_text())
    pair_summary=json.loads((ROOT/'07_GEOMETRY_INTEGRITY'/'WP02_FULL_SOLID_PAIR_AUDIT_SUMMARY.json').read_text())
    change={
        'configuration_id':m.CONFIGURATION_ID,'revision':m.REVISION,
        'removed_or_superseded':['DF8 schematic arm geometry','inherited fragmenting HBD calibration fuse','LHL 1250D 09 installed configuration','unattached actuator reference mounts'],
        'added':['rigid 70 mm links',f'{m.CROSSHEAD_STROKE_MM:.6f} mm constrained crosshead solution','authentic GS vendor BREP split at its prismatic state','drawing-derived HBD with 1.2 mm lost motion','captive nonfragmenting HBD bypass','LHL 625D 12 guided redundant spring','headed pins/VSM rings/bushings','positive stops/locks/witnesses','service cartridge spine'],
        'wp01_relief_used_mm':0.0,
        'top_level_states':[p.name for p in state_files.values()],
        'full_solid_pair_audit':pair_summary,
        'reimport_status':rows,
    }
    write_json(ROOT/'01_BASELINE_AND_OWNER_DECISIONS'/'WP02_CHANGE_RECORD_AGAINST_DF8_R0.json',change)

    final_summary={
        'configuration_id':m.CONFIGURATION_ID,'revision':m.REVISION,
        'parent_df8_archive_sha256':m.PARENT_DF8_ARCHIVE_SHA256,
        'accepted_wp01_archive_sha256':m.PARENT_WP01_ARCHIVE_SHA256,
        'owner_response':m.OWNER_RESPONSE,
        'top_level_step_files':{st:{'relative_path':p.relative_to(ROOT).as_posix(),'sha256':sha256(p)} for st,p in state_files.items()},
        'top_level_step_count':2,
        'top_level_step_reimport_validation':rows,
        'authentic_vendor_gs_original_sha256':sha256(ROOT/'03_VENDOR_CAD_ORIGINAL'/'ITEM_020_ACE_GS_19_50_V4A_B8_B8_VENDOR.stp'),
        'selected_cots':[
            'ACE GS-19-50-V4A-B8-B8; development force specification F1 300 +/- 30 N at 20 C; authentic vendor BREP present',
            'ACE HBD-15-25-AA-P; drawing-derived geometry pending authentic configured CAD and force-speed evidence',
            'Lee Spring LHL 625D 12; catalog-derived geometry and configuration calculation',
            'Smalley VSM-6-S16-PA; drawing-derived retaining-ring envelope',
        ],
        'crosshead_stroke_mm':m.CROSSHEAD_STROKE_MM,
        'kinematic_endpoints':{'stowed':m.KIN_STOW,'deployed':m.KIN_DEPLOY},
        'mass_summary':mass,
        'full_solid_pair_audit':pair_summary,
        'release_classification':m.RELEASE_CLASSIFICATION,
        'native_creo_validation':'UNAVAILABLE_AND_NOT_CLAIMED',
        'different_kernel_reimport':'UNAVAILABLE_AND_NOT_CLAIMED',
    }
    write_json(ROOT/'00_READ_FIRST'/'WP02_FINAL_PACKAGE_SUMMARY.json',final_summary)

    # Create manifest after every package file except the manifest itself exists.
    manifest=ROOT/'11_MANIFESTS_AND_HASHES'/'WP02_SHA256_MANIFEST.csv'
    selfsha=ROOT/'11_MANIFESTS_AND_HASHES'/'WP02_MANIFEST_SELF_SHA256.txt'
    msummary=ROOT/'11_MANIFESTS_AND_HASHES'/'WP02_MANIFEST_SUMMARY.json'
    for p in (manifest,selfsha,msummary):
        if p.exists(): p.unlink()
    manifest_rows=[]
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p != manifest:
            manifest_rows.append({'relative_path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha256(p)})
    write_csv(manifest,['relative_path','size_bytes','sha256'],manifest_rows)
    manifest_sha=sha256(manifest)
    write_text(selfsha,manifest_sha)
    write_json(msummary,{'file_count_excluding_manifest':len(manifest_rows),'manifest_sha256':manifest_sha})

    zip_path=OUT/f'{m.PACKAGE_NAME}.zip'
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file(): zf.write(p,arcname=f'{ROOT.name}/{p.relative_to(ROOT).as_posix()}')
    with zipfile.ZipFile(zip_path) as zf:
        bad=zf.testzip(); names=zf.namelist()
        if bad: raise RuntimeError(f'ZIP CRC failure at {bad}')
    result={
        'package_directory':str(ROOT),'zip':str(zip_path),'zip_sha256':sha256(zip_path),'zip_crc':'PASS',
        'zip_member_count':len(names),'manifest':str(manifest),'manifest_sha256':manifest_sha,
        'top_level_state_files':{k:str(v) for k,v in state_files.items()},'reimport':rows,
        'mass':mass,'full_solid_pair_audit':pair_summary,'release_classification':m.RELEASE_CLASSIFICATION,
    }
    write_json(OUT/'WP02_BUILD_RESULT.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
