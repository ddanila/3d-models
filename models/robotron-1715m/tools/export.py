#!/usr/bin/env python3
"""Export OpenSCAD parts plus photo UV metadata for DAC (Python 3, OpenSCAD)."""
import hashlib, json, re, subprocess, argparse, tempfile
parser=argparse.ArgumentParser();parser.add_argument("--parts", nargs="*");args=parser.parse_args()
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'model.scad').read_text()
# Evaluate canonical SCAD dimensions instead of freezing the browser's old tilt.
with tempfile.TemporaryDirectory() as temp:
    scad=Path(temp)/'keyboard-dimensions.scad'
    scad.write_text('include <'+str(root/'model.scad')+'>\npart="metadata-only";\necho([keyboard_y,28+keyboard_z_shift,keyboard_slope,keyboard_pitch,keyboard_cable_x,keyboard_cable_y,keyboard_support_x,keyboard_controller_x,keyboard_controller_y,keyboard_controller_z,keyboard_cable_z]);\necho(cable_paths=[ribbon_folds(drive_ribbon_path(0)),ribbon_folds(drive_ribbon_path(1))]);\n')
    result=subprocess.run(['openscad','-o',str(Path(temp)/'dimensions.csg'),str(scad)],capture_output=True,text=True,check=True)
    keyboard_values=json.loads(re.search(r'ECHO: (\[.*?\])',result.stderr).group(1))
ribbon_paths=json.loads(re.search(r'ECHO: cable_paths = (\[.*\])',result.stderr).group(1))
keyboard_dimensions=dict(zip(['y','z','slope','pitch','cableX','cableY','cableSupportX','controllerX','controllerY','controllerZ','cableZ'],keyboard_values))

parts=json.loads(re.search(r'parts=(\[.*?\]);',source).group(1))
colors=json.loads(re.search(r'colors=(\[.*?\]);',source).group(1))
colors=[{'Wheat':'#b6ae93','Gray':'#767871'}.get(c,c) for c in colors]
out=root/'browser'; (out/'meshes').mkdir(exist_ok=True,parents=True)
records=[]
board_parts={'logic-visible-lands','logic-jumpers','logic-ic-sockets','logic-ic-contacts','logic-silkscreen','logic-ribbon-plug','logic-inductors','logic-artwork','logic-mounts','logic-boards','logic-connectors','logic-resistors','logic-ceramics','logic-electrolytics','logic-crystals','logic-passive-leads','logic-film','logic-pads','logic-solder','logic-connector-contacts'}
for name,color in zip(parts,colors):
    if name.startswith('keys-') or name in ['logic-chips','logic-pins','logic-pads','logic-solder']:continue
    for board in (['motherboard','display-controller'] if name in board_parts else ['']):

        if name in ['logic-visible-lands','logic-jumpers','logic-ic-sockets','logic-ic-contacts','logic-silkscreen','logic-ribbon-plug'] and board=='display-controller':continue
        if name=='logic-resistors' and board=='display-controller':continue
        if name=='logic-crystals' and board=='display-controller':continue
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
    variant=(k['width'],k['height'],k['style'],k.get('topWidth',0))
    if variant not in variants:
        name='keycap-'+str(len(variants));variants[variant]=name
        path=out/'meshes'/f'{name}.stl'
        if args.parts is None or "keycap" in args.parts or not path.exists():
            r=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="keycap"','-D',f'key_index={i}','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
            if r.returncode or 'ERROR:' in r.stderr:raise RuntimeError(r.stderr)
        key_meshes.append(dict(name=name,file=f'meshes/{name}.stl',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    k['mesh']=variants[variant]
    if k['style']==0:
        core_name=k['mesh']+'-core';core_path=out/'meshes'/f'{core_name}.stl'
        if core_name not in {p['name'] for p in key_meshes}:
            if args.parts is None or 'keycap' in args.parts or not core_path.exists():
                result=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="keycap-core"','-D',f'key_index={i}','-o',str(core_path),str(root/'model.scad')],capture_output=True,text=True)
                if result.returncode or 'ERROR:' in result.stderr:raise RuntimeError(result.stderr)
            key_meshes.append(dict(name=core_name,file=f'meshes/{core_name}.stl',sha256=hashlib.sha256(core_path.read_bytes()).hexdigest()))
        k['coreMesh']=core_name
    if k['style']==1:
        name=k['mesh']+'-insert'
        if not any(m['name']==name for m in key_meshes):
            path=out/'meshes'/f'{name}.stl'
            if args.parts is None or 'keycap' in args.parts or not path.exists():
                r=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="keycap-insert"','-D',f'key_index={i}','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
                if r.returncode or 'ERROR:' in r.stderr:raise RuntimeError(r.stderr)
            key_meshes.append(dict(name=name,file=f'meshes/{name}.stl',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        k['insertMesh']=name
# UV corners are TL, TR, BR, BL, normalized from the unmodified photographs.
def patch(name,photo,position,size,crop,rotation=[90,0,0]):
    return dict(name=name,photo='PXL_20261009_'+photo+'.jpg',position=position,size=size,rotation=rotation,uv=[[x/1824,y/1373] for x,y in crop])
# Small original markings are photographic. Enclosures and mechanisms stay geometry.
patches=[patch('brand','133022597',[-160,-209.2,48],[110,11],[(420,925),(1050,917),(1048,985),(425,990)])]
patches[0]['ink']=True
drive_labels=json.loads((root/'drive-labels.json').read_text())
patches += drive_labels['patches']
# Only the identifying label is photo-projected; jacket remains modeled geometry.
for i,x in enumerate([-231,-77]):
    patches.append(dict(name=f'drive-diskette-ink-{i}',photo='PXL_20261013_113451775.jpg',uv=[[.540,.654],[.776,.654],[.776,.878],[.540,.878]],position=[x+106,-181,90.32],size=[51,36],rotation=[0,0,0],section='interior',assembly='drives',disketteUnit=i))
materials={
    'paper':dict(roughness=.94,metalness=0,grain=.025,grainScale=3,grainRelief=.001),
    'ink':dict(roughness=.86,metalness=0),
    'paint':dict(roughness=.69,metalness=0,grain=.065,grainScale=2.2,grainRelief=.022),
    'plastic':dict(roughness=.48,metalness=0,grain=.014,grainScale=3.5,grainRelief=.006),
    'key':dict(roughness=.4,metalness=0,grain=.01,grainScale=4.0,clearcoat=.18),
    'clear-switch':dict(roughness=.25,metalness=0,clearcoat=1,ior=1.49,transparent=True,opacity=.55,depthWrite=False),
    'clear-key':dict(roughness=.12,metalness=0,grain=.002,grainScale=4.0,clearcoat=1,ior=1.49,transparent=True,opacity=.32,depthWrite=False),
    'rubber':dict(roughness=.92,metalness=0,grain=.04,grainScale=5.0,grainRelief=.012),
    'plated-steel':dict(roughness=.3,metalness=.88,grain=.012,grainScale=4.5,grainRelief=.003),
    'cast-alloy':dict(roughness=.57,metalness=.62,grain=.03,grainScale=2.2),
    'solder':dict(roughness=.46,metalness=.82,grain=.009,grainScale=5,grainRelief=.001),
    'tinned-lead':dict(roughness=.27,metalness=.9),
    'ceramic':dict(roughness=.34,metalness=0),
    'ic-moulding':dict(roughness=.72,metalness=0),
    'phenolic':dict(roughness=.68,metalness=0,grain=.018,grainScale=5,grainRelief=.001),
    'aged-plastic':dict(roughness=.74,metalness=0,grain=.026,grainScale=3.5),
    'metal':dict(roughness=.32,metalness=.86,grain=.018,grainScale=5.0,grainRelief=.002,grainStretch=[.08,1,1]),
    'lens':dict(roughness=.24,metalness=0,clearcoat=.8),
    'glass-border':dict(roughness=.07,metalness=0,clearcoat=1),
    'glass':dict(roughness=.16,metalness=.05,clearcoat=1),
    'matrix-laminate':dict(roughness=.55,metalness=0,transparent=True,opacity=.94,depthWrite=True,grain=.018,grainScale=5,grainRelief=.001),
    'controller-laminate':dict(roughness=.64,metalness=0,grain=.018,grainScale=5,grainRelief=.001),
    'pcb':dict(roughness=.61,metalness=0,grain=.012,grainScale=6,grainRelief=.001),
    'tape':dict(roughness=.93,metalness=0,grain=.016,grainScale=3.0),
}
for r in records:
    n=r.get('part',r['name']);m='paint'
    if n=='logic-visible-lands':r['section']='interior';m='tinned-lead'
    if n=='logic-inductors':r['section']='interior';m='plastic'
    if n in ['fan-retainers', 'fan-cushions', 'psu-grommets', 'drive-adapter-boards', 'drive-adapter-traces', 'drive-adapter-sockets']:r['section']='interior';m='solder' if n.endswith('traces') else 'pcb' if n.endswith('boards') else 'plated-steel' if n.endswith('retainers') else 'rubber' if n in ['psu-grommets','fan-cushions'] else 'plastic'
    if n in ['drive-adapter-edge','drive-adapter-contacts']:r['section']='interior';m='plastic' if n.endswith('edge') else 'solder'
    if n=='case-lid-inserts':m='paint'
    if n=='case-lid-fixings':m='plated-steel'
    if n.startswith(('drive-shaft-', 'drive-release-')):r['section']='interior';m='plated-steel'
    if n.startswith('keyboard-entry-'):r['section']='interior';m='plastic'
    if n=='keyboard-controller-solder':r['section']='interior';m='solder'
    if n in ['keyboard-pcb-supports','keyboard-pcb-fasteners','keyboard-entry-wires','keyboard-contact-routes']:r['section']='interior';m='metal' if n.endswith('fasteners') else 'plastic'
    if n in ['keyboard-guides','keyboard-contact-pads']:r['section']='interior';m='plastic'
    if n=='keyboard-entry-rubber':m='rubber'
    if n=='keyboard-base-insulator':m='phenolic'
    if n=='prototype-rubber':r['section']='prototype';m='rubber'
    if n in ['monitor-power-lead','monitor-signal-lead']:m='rubber'
    if n in ['monitor-plug-bodies','monitor-plug-collars']:m='plastic'
    if n=='monitor-plug-metal':m='metal'
    if n in ['drive-latch-0','drive-latch-1','drives','drive-insets','drive-latches','power','reset','keyboard-deck','keyboard-fillers','cable-plug','plug-insert']:m='plastic'
    if n in ['hardware','keyboard-feet','keyboard-grommet','cable','ring']:m='rubber'
    if n in ['keyboard-metal','plug-screws','keyboard-grommet']:m='metal'
    if n.startswith('drive-led'):m='lens'
    if n in ['crt-rim','crt-glass']:m='glass'
    if n=='crt-rim':m='glass-border'
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
        r['section']='prototype';m='rubber' if n=='prototype-rubber' else 'metal' if n in ['prototype-spring','prototype-pcb-pad','prototype-pcb-solder'] else 'plastic'
    if n in ['logic-resistors','logic-ceramics','logic-electrolytics','logic-crystals','logic-passive-leads']:
        r['section']='interior';m='metal' if n in ['logic-crystals','logic-passive-leads'] else 'plastic'
    if n in board_parts:
        r['section']='interior'
        if n in ['logic-pads','logic-solder','logic-connector-contacts']:m='metal'
        if n=='logic-film':m='plastic'
    if n=='logic-artwork':
        m='pcb'
        if r.get('board')=='motherboard':r['color']='#7d9354'
    if n=='logic-silkscreen':m='ink'
    if n in ['logic-ribbon-plug','logic-ic-sockets','logic-jumpers']:m='plastic'
    if n=='logic-ic-contacts':m='tinned-lead'
    if n=='drive-cable-contacts':r['section']='interior';m='tinned-lead'
    if n in ['ribbon-ridges','drive-cable-plugs']:
        r['section']='interior';m='rubber' if n=='ribbon-ridges' else 'plastic'
    if n in ['drive-frames','fan-frame']:m='cast-alloy'
    if n in ['drive-mechanisms','drive-bracket','psu-chassis','psu-cover','logic-mounts'] or n.startswith(('drive-head-metal-','drive-clamp-','drive-spindle-')):m='plated-steel'
    if n.startswith('drive-head-arm-'):m='plated-steel'
    if n.startswith('drive-medium-'):r['section']='interior';m='plastic'
    if n=='prototype-pcb-solder':m='solder'
    if n in ['drives','drive-cable-plugs','logic-connectors']:m='aged-plastic'
    if n.startswith('keyboard-controller-') or n in ['keyboard-insulators','keyboard-matrix-artwork']:
        r['section']='interior'
        m='metal' if n.endswith('-metal') else 'pcb' if n.endswith(('-board','-artwork')) else 'plastic'
    if n in ['system-foot-metal','monitor-stand-metal','rear-socket-contacts','rear-blanking-plates','rear-fasteners','rear-nameplate']:m='plated-steel'
    if n in ['monitor-under-controls','rear-socket-bodies','rear-power-black','rear-socket-inserts','rear-recesses']:m='plastic'
    if n in ['keyboard-pcb-metal','keyboard-controller-traces']:r['section']='interior';m='solder'
    if n=='monitor-joint-lip':m='plastic'
    if n in ['rear-legends','rear-nameplate-ink']:
        m='ink';r['color']='#57564c' if n=='rear-legends' else '#292c29'
    if n.startswith('drive-diskette'):m='plastic'
    if n.startswith('drive-direction') or n=='front-labels':m='ink'
    if n=='power':m='clear-switch'
    if n=='power-housing':m='plastic'
    if n=='keyboard-deck':m='paint'
    if n=='keyboard-grommet':m='rubber'
    if n=='keyboard-pcb':m='matrix-laminate'
    if n=='keyboard-controller-board':m='controller-laminate'
    if n=='keyboard-pcb-supports':m='plated-steel'
    if n=='keyboard-controller-mounts':m='plated-steel'
    if n=='keyboard-controller-shield':m='solder'
    if n in ['keyboard-controller-leads','keyboard-controller-solder']:m='solder'
    if n=='keyboard-internal-cable':r['section']='interior';m='rubber'
    if n=='keyboard-cable-support':m='paint'
    if n=='keyboard-entry-choke':r['section']='interior';m='plastic'
    if n in ['monitor-mount-pads','monitor-cable-clips']:r['section']='monitor-interior';m='rubber' if n.endswith('pads') else 'metal'
    if n.startswith('drive-protect-tab-'):r['section']='interior';m='tape'
    if n=='keyboard-plate':m='paint'
    if n in ['keyboard-matrix-socket','keyboard-matrix-contacts']:
        r['section']='interior';m='plastic' if n.endswith('socket') else 'solder'
    # Clean material families; no oxidation, wear or panel-photo lighting.
    if n=='drive-adapter-boards':m='phenolic'
    if n in ['keyboard-controller-ceramic','logic-ceramics']:m='ceramic'
    if n=='keyboard-controller-chips':m='ic-moulding'
    if n in ['keyboard-controller-metal','keyboard-controller-leads','keyboard-matrix-contacts','logic-passive-leads','logic-connector-contacts']:m='tinned-lead'
    if n in ['keyboard-controller-traces','keyboard-pcb-metal']:m='tinned-lead'
    if n in ['keyboard-controller-ink','keyboard-controller-rom-ink','keyboard-controller-rom-cover']:m='ink' if n.endswith('ink') else 'tape'
    r['material']=m
# Keep browser antialiased markings and CAD lettering on the same coordinates.
detail_source=(root/'specimen-details.scad').read_text()
legend_source=detail_source.split('module rear_legends(){',1)[1].split('module rear_nameplate_ink',1)[0]
rear_markings=[]
for match in re.finditer(r'for\(p=(\[.*?\])\)rear_text\(p\[0\],p\[1\],p\[2\](?:,([0-9.]+))?\);',legend_source):
    rear_markings += [dict(x=x,z=z,text=t,size=float(match[2] or 3)) for x,z,t in json.loads(match[1])]
assert len(rear_markings)==13
references=['PXL_20261009_'+n+'.jpg' for n in ['133017092','133019620','132919894','133022597','133005363','133001660','133028313','133032874','132916421.MP']]
references += ['PXL_'+n+'.jpg' for n in ['20250430_135132170','20251008_143433778','20250516_133813650','20250516_141624490','20250516_133810520']]
references += ['PXL_20261010_'+n+'.jpg' for n in ['090413483','090416759','090421901','090425989','090431122']]
references += ['PXL_20261010_131354451.jpg','PXL_20261010_131835506.jpg']
references += ['PXL_20250212_'+n+'.jpg' for n in ['094057627','094043026','094033966','094109733','094038758','094103763']]
references += ['PXL_20261012_'+n+'.jpg' for n in ['124827690','125300878','125449006','125457861','125502437','123622947','123907435','125132359.MP','125413618','125417620','131106217','123729356']]
references += ['PXL_20261012_'+n+'.jpg' for n in ['135524773','135528166','135532764']]
references += ['PXL_20261012_'+n+'.jpg' for n in ['125018215','125123660','125234638','125402713.MP']]
references += ['PXL_20261012_'+n+'.jpg' for n in ['185824256','185826600','185834871','185855185','190054608']]
references += ['PXL_20261013_084425145.jpg']
references += ['PXL_20261012_123106382.jpg', 'PXL_20261012_123109703.jpg', 'PXL_20261012_123114519.jpg', 'PXL_20261012_123122852.jpg', 'PXL_20261012_123126017.jpg', 'PXL_20261012_125012845.jpg', 'PXL_20261012_125025415.jpg']
references += ['PXL_20261013_'+n+'.jpg' for n in ['113428737','113436448','113451775','113457457','113529099','113537277']]
verification=json.loads((root.parents[1]/'model-status.json').read_text())
# Standalone inspection-only envelope is exported from the same CAD source.
specimen_meshes=[]
for name in ['specimen-sleeve','specimen-switch-guide','specimen-switch-mount','specimen-switch-contacts','specimen-switch-pcb']:
    path=out/'meshes'/f'{name}.stl'
    if args.parts is None or name in args.parts or not path.exists():
        subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D',f'part="{name}"','-o',str(path),str(root/'model.scad')],check=True)
    specimen_meshes.append(dict(name=name,file=f'meshes/{name}.stl',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
references += ['PXL_20261013_150009163.jpg', 'PXL_20261013_150037354.jpg', 'PXL_20261013_150144938.jpg', 'PXL_20261013_150242933.jpg', 'PXL_20261013_150247694.jpg', 'PXL_20261013_150303351.jpg', 'PXL_20261013_150312308.jpg', 'PXL_20261013_150334561.jpg', 'PXL_20261013_150351188.jpg', 'PXL_20261013_150416654.jpg', 'PXL_20261013_150436601.jpg', 'PXL_20261013_150516969.jpg', 'PXL_20261013_150520316.jpg', 'PXL_20261013_150549721.jpg', 'PXL_20261013_150554378.jpg', 'PXL_20261013_150605909.jpg', 'PXL_20261013_151902765.jpg', 'PXL_20261013_151912803.jpg']
references += ['PXL_20261014_072654600.jpg', 'PXL_20261014_072658072.jpg', 'PXL_20261014_072700902.jpg', 'PXL_20261014_072704307.jpg', 'PXL_20261014_072709950.jpg', 'PXL_20261014_072719957.jpg', 'PXL_20261014_072723829.jpg', 'PXL_20261014_072935298.jpg', 'PXL_20261014_072941759.jpg', 'PXL_20261014_072944002.jpg', 'PXL_20261014_073200542.jpg', 'PXL_20261014_073203748.jpg', 'PXL_20261014_073213563.jpg', 'PXL_20261014_073219091.jpg', 'PXL_20261014_073309497.jpg', 'PXL_20261014_073311162.jpg', 'PXL_20261014_073322148.jpg', 'PXL_20261014_073327415.jpg', 'PXL_20261014_073636885.jpg', 'PXL_20261014_073642069.jpg', 'PXL_20261014_073718163.jpg', 'PXL_20261014_073730822.jpg']
pcb_data=json.loads((root/"pcb-components.json").read_text())
manifest=dict(version=47,componentCounts=dict(packages=len(pcb_data["instances"]),leadHoles=len(pcb_data["footprints"])),ribbonPaths=ribbon_paths,hardwareAudit=json.loads((root/"hardware-audit.json").read_text()),reviewViews=json.loads((root/'review-views.json').read_text()),evidence=json.loads((root/"evidence.json").read_text()),annotations=json.loads((root/"inspection-labels.json").read_text()),specimenMeshes=specimen_meshes,modelVerification={k:v for k,v in verification['models'].items() if k.startswith('models/robotron-1715m/')},rearMarkings=rear_markings,cableParking=[0,18,0],pcbComponents=json.loads((root/"pcb-components.json").read_text()),keyboardMechanism=dict(spring="prototype-spring",stem="prototype-stem",rubber="prototype-rubber",installedHeight=19.6,freeHeight=23,springBase=-10.4,travel=2.2,diameter=13,wire=.4,activeTurns=5,closedTurnsPerEnd=3,status="Owner-confirmed outer diameter, free length, wire and rubber/PCB contact principle. Turns photo-estimated; installed compression, travel and hidden geometry provisional"),driveMotion=[dict(unit=i,spindle=f"drive-spindle-{i}",head=f"drive-head-{i}",headMetal=f"drive-head-metal-{i}",headArm=f"drive-head-arm-{i}",armPivot=[x+71,-48,90],medium=f"drive-medium-{i}",jacket=f"drive-diskette-{i}",disketteLabel=f"drive-diskette-label-{i}",latch=f"drive-latch-{i}",clamp=f"drive-clamp-{i}",shaft=f"drive-shaft-{i}",release=f"drive-release-{i}",latchPivot=[x+118,-211,92],pivot=[x+70,-137,88],travel=[0,-79*25.4/96,0],trackPitch=25.4/96,travelSource="TEAC FD-55FV-13 specification p.108: 96 tpi; specimen suffix unverified") for i,x in enumerate([-231,-77])],controls=dict(powerPivot=[207,-194.8,17],rockerAngle=8,resetTravel=1.2),units='mm',scale=.0025,materials=materials,parts=records,keys=keys,keyMeshes=key_meshes,keyboard=keyboard_dimensions,screen=json.loads((root/'monitor-profile.json').read_text())['glass'],patches=patches,driveLabels=drive_labels,references=references,pcbReferences=json.loads((root/'pcb-references.json').read_text()),interior=dict(status='provisional',drive='Owner specimens: Robotron K5601 / TEAC 15532064-00A and Ratan assembly / TEAC 15532092-00A; FD-55 suffix unverified',driveEnvelope=[146,203,41.3],source='https://oldcrap.org/2017/12/26/robotron-1715/',specification='https://retrocmp.de/fdd/teac/TEAC_FD55-FV.pdf',note='Drive envelopes are documented. Drive mechanisms and rear plates now follow owner photos; the nominal envelope remains a reference. Owner October 13 photos establish cover stiffeners, fan retainers, PSU cover and brown drive adapters. W/M motherboard follows the original placement drawing; display controller uses October 14 component-side photos for 39 IC positions, three memories, upright capacitors and a wound component. The 1 mm enclosures and carrier windows preserve views of internal geometry. Local dimensions and exact revision match remain provisional.'),source='https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m')
# Small, reproducible label crops: full photographs are inspection-only assets.
from PIL import Image
(out/'textures').mkdir(exist_ok=True)
for patch in patches:
    photo=Image.open(root/'reference/photos'/patch['photo'])
    uv=patch['uv'];w,h=photo.size
    left=max(0,int(min(p[0] for p in uv)*w)-2);top=max(0,int(min(p[1] for p in uv)*h)-2)
    right=min(w,int(max(p[0] for p in uv)*w)+3);bottom=min(h,int(max(p[1] for p in uv)*h)+3)
    crop=photo.crop((left,top,right,bottom));crop.thumbnail((1024,1024))
    path=out/'textures'/f"{patch['name']}.jpg";crop.save(path,quality=92)
    patch['texture']=str(path.relative_to(out));patch['textureSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    patch['textureUv']=[[(u*w-left)/(right-left),(v*h-top)/(bottom-top)] for u,v in uv]
(out/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
