#!/usr/bin/env python3
"""Rebuild deterministic, self-contained geometry/source archives for the museum."""
from pathlib import Path
import json,subprocess,tempfile,zipfile,hashlib
root=Path(__file__).resolve().parents[1];dest=root/'browser/downloads';dest.mkdir(exist_ok=True)
manifest=json.loads((root/'browser/model.json').read_text())
logic=['logic-boards','logic-chips','logic-pins','logic-connectors','logic-resistors','logic-ceramics','logic-electrolytics','logic-crystals','logic-passive-leads','logic-film','logic-pads','logic-solder','logic-connector-contacts','logic-mounts']
drive=['teac_frame()','teac_mechanism()','teac_black()','teac_contacts()','teac_coils()','teac_power_socket()','teac_spindle()','teac_head()','teac_head_metal()','teac_head_arm()','teac_medium()','teac_clamp()','teac_components()','teac_cable_plug()']
# Original editable sources plus every imported KiCad geometry source and notice.
sources={}
for path in root.rglob('*'):
    rel=path.relative_to(root)
    if not path.is_file() or rel.parts[0] in ['browser','reference','display-base-ring','keycap-spring-mandrel']:continue
    if path.suffix in ['.scad','.json','.py','.md','.txt','.step'] or path.name=='LICENSE' or (rel.parts[:2]==('components','kicad') and path.suffix=='.stl'):
        sources['source/'+str(rel)]=path.read_bytes()
records=[]
with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    for name in ['motherboard','floppy-controller','drive-0','drive-1']:
        if name in ['motherboard','floppy-controller']:
            body='pcb_board='+json.dumps(name)+';\n'+''.join('shape('+json.dumps(p)+');\n' for p in logic)
        else:
            body=''.join(p+';\n' for p in drive)+f'teac_boards({"true" if name.endswith("1") else "false"});\nteac_traces({"true" if name.endswith("1") else "false"});\n'
        if name.startswith('drive-'):
            unit=int(name[-1]);body+=f'translate([{[231,77][unit]},203,-60]){{drives({unit});drive_insets({unit});drive_latches({unit});drive_led({unit});}}\n'
        wrapper='include <source/model.scad>\npart="download-only";\n'+body
        audit=temp/'export.scad';out=temp/'model.stl'
        audit.write_text(wrapper.replace('source/model.scad',str(root/'model.scad')))
        run=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="download-only"','-o',str(out),str(audit)],capture_output=True,text=True)
        if run.returncode or 'ERROR:' in run.stderr:raise RuntimeError(run.stderr)
        note=f'''Robotron 1715M reference reconstruction: {name}

model.stl is geometry only, in millimetres. Photos, materials, animation and
firmware are not part of STL. Drives use a local front-left-bottom origin;
boards retain the museum assembly coordinates. Open model.scad with OpenSCAD (Manifold backend)
to edit/rebuild it; all required included geometry sources are in source/.

Source: https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m
Evidence and limitations: source/README.md
Drive references: owner photos PXL_20250212_094033966.jpg and
PXL_20250212_094038758.jpg, referenced in that documentation.
Board reconstruction: another PC 1715 photographed by Old Crap Vintage
Computing, https://oldcrap.org/2017/12/26/robotron-1715/ . Photos are not bundled.
Dimensions, hidden parts and linkage motion remain estimated. Not a validated
manufacturing model; parts may touch or remain separate within the STL.

Original modeling code: MIT (source/LICENSE).
Imported KiCad bodies, leads and footprint data retain their file-specific
licences and exceptions; see source/components/kicad/NOTICE.txt and source/.
The editable archive includes those original STEP files and licence texts.
'''
        entries={**sources,'README.txt':note.encode(),'model.scad':wrapper.encode(),'model.stl':out.read_bytes()}
        archive=dest/(name+'.zip')
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for filename,blob in sorted(entries.items()):
                info=zipfile.ZipInfo(filename,date_time=(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,blob)
        records.append(dict(name=name,file='downloads/'+archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size))
        print(name,archive.stat().st_size,flush=True)
(root/'browser/downloads.json').write_text(json.dumps(records,indent=2)+'\n')
