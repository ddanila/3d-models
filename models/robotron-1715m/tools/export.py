#!/usr/bin/env python3
"""Export OpenSCAD parts plus photo UV metadata for DAC (Python 3, OpenSCAD)."""
import hashlib, json, re, subprocess, argparse
parser=argparse.ArgumentParser();parser.add_argument("--parts", nargs="*");args=parser.parse_args()
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'model.scad').read_text()
parts=json.loads(re.search(r'parts=(\[.*?\]);',source).group(1))
colors=json.loads(re.search(r'colors=(\[.*?\]);',source).group(1))
colors=[{'Wheat':'#b6ae93','Gray':'#767871'}.get(c,c) for c in colors]
out=root/'browser'; (out/'meshes').mkdir(exist_ok=True,parents=True)
records=[]
board_parts={'logic-mounts','logic-boards','logic-connectors','logic-resistors','logic-ceramics','logic-electrolytics','logic-crystals','logic-passive-leads','logic-film','logic-pads','logic-solder','logic-connector-contacts'}
for name,color in zip(parts,colors):
    if name.startswith('keys-') or name in ['logic-chips','logic-pins','logic-pads','logic-solder']:continue
    for board in (['motherboard','floppy-controller'] if name in board_parts else ['']):
        if name=='logic-film' and board=='motherboard':continue
        export_name=name+('-'+board if board else '')
        path=out/'meshes'/f'{export_name}.stl'
        if args.parts is None or name in args.parts or not path.exists():
            result=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D',f'part="{name}"','-D',f'pcb_board="{board}"','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
            if result.returncode or 'ERROR:' in result.stderr: raise RuntimeError(result.stderr)
        assert path.stat().st_size>84,export_name
        record=dict(name=export_name,file=f'meshes/{export_name}.stl',color=color,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        if board:record.update(board=board,part=name)
        records.append(record)
        print(export_name,path.stat().st_size,flush=True)
# Delete obsolete aggregate board exports; canonical assembly remains combined.
for name in board_parts:
    (out/'meshes'/f'{name}.stl').unlink(missing_ok=True)
for name in ['logic-pads','logic-solder']:
    for path in (out/'meshes').glob(name+'-*.stl'):path.unlink()
keys=json.loads((root/'keyboard-layout.json').read_text())
key_meshes=[];variants={}
for i,k in enumerate(keys):
    variant=(k['width'],k['height'],k['style'])
    if variant not in variants:
        name='keycap-'+str(len(variants));variants[variant]=name
        path=out/'meshes'/f'{name}.stl'
        if args.parts is None or not path.exists():
            r=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="keycap"','-D',f'key_index={i}','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
            if r.returncode or 'ERROR:' in r.stderr:raise RuntimeError(r.stderr)
        key_meshes.append(dict(name=name,file=f'meshes/{name}.stl',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    k['mesh']=variants[variant]
# UV corners are TL, TR, BR, BL, normalized from the unmodified photographs.
def patch(name,photo,position,size,crop,rotation=[90,0,0]):
    return dict(name=name,photo='PXL_20261009_'+photo+'.jpg',position=position,size=size,rotation=rotation,uv=[[x/1824,y/1373] for x,y in crop])
# Small original markings are photographic. Enclosures and mechanisms stay geometry.
patches=[patch('brand','133022597',[-160,-209.2,48],[110,11],[(420,925),(1050,917),(1048,985),(425,990)])]
patches[0]['ink']=True
drive_labels=json.loads((root/'drive-labels.json').read_text())
patches += drive_labels['patches']
materials={
    'paint':dict(roughness=.78,metalness=.08,grain=.028,grainScale=2.7),
    'plastic':dict(roughness=.68,metalness=0,grain=.022,grainScale=3.5),
    'key':dict(roughness=.4,metalness=0,grain=.01,grainScale=4.0,clearcoat=.18),
    'clear-key':dict(roughness=.29,metalness=0,grain=.006,grainScale=4.0,clearcoat=.65),
    'rubber':dict(roughness=.92,metalness=0,grain=.015,grainScale=4.0),
    'plated-steel':dict(roughness=.43,metalness=.72,grain=.016,grainScale=4.5),
    'cast-alloy':dict(roughness=.57,metalness=.62,grain=.03,grainScale=2.2),
    'solder':dict(roughness=.48,metalness=.66,grain=.009,grainScale=5),
    'aged-plastic':dict(roughness=.74,metalness=0,grain=.026,grainScale=3.5),
    'metal':dict(roughness=.38,metalness=.72,grain=.008,grainScale=5.0),
    'lens':dict(roughness=.24,metalness=0,clearcoat=.8),
    'glass':dict(roughness=.16,metalness=.05,clearcoat=1),
    'pcb':dict(roughness=.61,metalness=.05),
    'tape':dict(roughness=.93,metalness=0,grain=.016,grainScale=3.0),
}
for r in records:
    n=r.get('part',r['name']);m='paint'
    if n in ['drive-latch-0','drive-latch-1','drives','drive-insets','drive-latches','power','reset','keyboard-deck','keyboard-fillers','cable-plug','plug-insert']:m='plastic'
    if n in ['hardware','keyboard-feet','keyboard-grommet','cable','ring']:m='rubber'
    if n in ['keyboard-metal','plug-screws','keyboard-grommet']:m='metal'
    if n.startswith('drive-led'):m='lens'
    if n in ['crt-rim','crt-glass']:m='glass'
    if n=='monitor-tape':m='tape'
    if n in ['drive-frames','drive-mechanisms','drive-contacts','drive-bracket','logic-pins','psu-chassis','psu-cover','fan-frame']:m='metal'
    if n in ['drive-boards','logic-boards','keyboard-pcb']:m='pcb'
    if n in ['drive-motors','logic-chips','logic-connectors','logic-capacitors','fan-rotor','keyboard-switches']:m='plastic'
    if n.startswith('power-wires') or n.startswith('ribbon-'):m='rubber'
    if n=='drive-coils':m='metal'
    if n in ['drive-frames', 'drive-mechanisms', 'drive-motors', 'drive-boards', 'drive-contacts', 'drive-coils', 'drive-bracket', 'logic-boards', 'logic-chips', 'logic-pins', 'logic-connectors', 'logic-capacitors', 'psu-chassis', 'psu-cover', 'fan-frame', 'fan-rotor', 'ribbon-cables', 'ribbon-stripes', 'power-wires-red', 'power-wires-black', 'power-wires-yellow', 'keyboard-pcb', 'keyboard-switches']:r['section']='interior'
    if n in ['tube-funnel', 'tube-neck', 'monitor-yoke', 'monitor-coils', 'monitor-chassis', 'monitor-boards', 'monitor-components', 'monitor-capacitors', 'monitor-shield', 'monitor-wires']:r['section']='monitor-interior'
    if n in ['monitor-chassis','monitor-shield']:m='metal'
    if n=='tube-neck':m='glass'
    if n in ['monitor-yoke','monitor-components','tube-funnel']:m='plastic'
    if n in ['monitor-boards']:m='pcb'
    if n=='monitor-wires':m='rubber'
    if n=='monitor-coils':m='metal'
    if n in ['drive-power-sockets','drive-traces','drive-label-plates']:
        r['section']='interior'
        m='plastic' if n=='drive-power-sockets' else 'pcb' if n=='drive-traces' else 'metal'
    if n.startswith('drive-spindle-') or n.startswith('drive-head-'):
        r['section']='interior';m='metal' if 'spindle' in n else 'plastic'
    if n in ['logic-mounts','chassis-fasteners','keyboard-plate'] or n.startswith(('drive-clamp-','drive-head-metal-','drive-board-components')):
        r['section']='interior';m='plastic' if n=='drive-board-components' else 'metal'
    if n in ['monitor-fasteners','monitor-passives','monitor-socket']:
        r['section']='monitor-interior';m='metal' if n=='monitor-fasteners' else 'plastic'
    if n.startswith('prototype-'):
        r['section']='prototype';m='metal' if n in ['prototype-spring','prototype-pcb-pad','prototype-pcb-solder'] else 'plastic'
    if n in ['logic-resistors','logic-ceramics','logic-electrolytics','logic-crystals','logic-passive-leads']:
        r['section']='interior';m='metal' if n in ['logic-crystals','logic-passive-leads'] else 'plastic'
    if n in board_parts:
        r['section']='interior'
        if n in ['logic-pads','logic-solder','logic-connector-contacts']:m='metal'
        if n=='logic-film':m='plastic'
    if n in ['ribbon-ridges','drive-cable-plugs']:
        r['section']='interior';m='rubber' if n=='ribbon-ridges' else 'plastic'
    if n in ['drive-frames','fan-frame']:m='cast-alloy'
    if n in ['drive-mechanisms','drive-bracket','psu-chassis','psu-cover','logic-mounts'] or n.startswith(('drive-head-metal-','drive-clamp-','drive-spindle-')):m='plated-steel'
    if n.startswith('drive-head-arm-'):m='plated-steel'
    if n.startswith('drive-medium-'):r['section']='interior';m='plastic'
    if n=='prototype-pcb-solder':m='solder'
    if n in ['drives','drive-cable-plugs','logic-connectors','keyboard-deck']:m='aged-plastic'
    if n.startswith('keyboard-controller-') or n in ['keyboard-insulators','keyboard-matrix-artwork']:
        r['section']='interior'
        m='metal' if n.endswith('-metal') else 'pcb' if n.endswith(('-board','-artwork')) else 'plastic'
    if n in ['system-foot-metal','monitor-stand-metal','rear-socket-contacts','rear-blanking-plates']:m='plated-steel'
    if n in ['monitor-under-controls','rear-socket-bodies','rear-power-black']:m='plastic'
    r['material']=m
references=['PXL_20261009_'+n+'.jpg' for n in ['133017092','133019620','132919894','133022597','133005363','133001660','133028313','133032874','132916421.MP']]
references += ['PXL_'+n+'.jpg' for n in ['20250430_135132170','20251008_143433778','20250516_133813650','20250516_141624490','20250516_133810520']]
references += ['PXL_20261010_'+n+'.jpg' for n in ['090413483','090416759','090421901','090425989','090431122']]
references += ['PXL_20261010_131354451.jpg','PXL_20261010_131835506.jpg']
references += ['PXL_20250212_'+n+'.jpg' for n in ['094057627','094043026','094033966','094109733','094038758','094103763']]
references += ['PXL_20261012_'+n+'.jpg' for n in ['123622947','123907435','125132359.MP','125413618','125417620','131106217','123729356']]
manifest=dict(version=15,cableParking=[0,18,0],pcbComponents=json.loads((root/"pcb-components.json").read_text()),keyboardMechanism=dict(spring="prototype-spring",stem="prototype-stem",installedHeight=12,freeHeight=23,travel=2.2,diameter=13,wire=.35,status="Owner spring dimensions; installed height, travel and hidden switch geometry estimated"),driveMotion=[dict(unit=i,spindle=f"drive-spindle-{i}",head=f"drive-head-{i}",headMetal=f"drive-head-metal-{i}",headArm=f"drive-head-arm-{i}",armPivot=[x+71,-55,90],medium=f"drive-medium-{i}",latch=f"drive-latch-{i}",clamp=f"drive-clamp-{i}",latchPivot=[x+118,-209,92],pivot=[x+70,-144,88],travel=[0,-79*25.4/96,0],trackPitch=25.4/96,travelSource="TEAC FD-55FV-13 specification p.108: 96 tpi; specimen suffix unverified") for i,x in enumerate([-231,-77])],units='mm',scale=.0025,materials=materials,parts=records,keys=keys,keyMeshes=key_meshes,keyboard=dict(y=-355,z=28,slope=6,pitch=20.0),screen=json.loads((root/'monitor-profile.json').read_text())['glass'],patches=patches,driveLabels=drive_labels,references=references,pcbReferences=json.loads((root/'pcb-references.json').read_text()),interior=dict(status='provisional',drive='Owner specimens: Robotron K5601 / TEAC 15532064-00A and Ratan assembly / TEAC 15532092-00A; FD-55 suffix unverified',driveEnvelope=[146,203,41.3],source='https://oldcrap.org/2017/12/26/robotron-1715/',specification='https://retrocmp.de/fdd/teac/TEAC_FD55-FV.pdf',note='Drive envelopes are documented. Drive mechanisms and rear plates now follow owner photos; the nominal envelope remains a reference. Logic-board population, mounting and wiring still use comparative evidence.'),source='https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m')
(out/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
