#!/usr/bin/env python3
"""Prepare and export the proposed reference PCB without modifying historical authorities."""
import argparse
import collections
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT/'reference'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data,str) else json.dumps(data,indent=2,sort_keys=True)+'\n')


def check():
    manifest = json.loads((REF/'generated/manifest.json').read_text())
    for group in ('sources','outputs'):
        for name,digest in manifest[group].items():
            if sha(ROOT/name) != digest:
                raise ValueError('Stale reference artifact: '+name)
    check_receipt()
    print('Reference variant sources and exports match pinned hashes')


def check_receipt():
    receipt = json.loads((REF/'routing-receipt.json').read_text())
    for name,digest in receipt['sources'].items():
        if sha(ROOT/name)!=digest: raise ValueError('Routing input changed: '+name)
    for name,digest in receipt['artifacts'].items():
        if sha(REF/'routing'/name)!=digest: raise ValueError('Routing artifact changed: '+name)
    if sha(REF/'controller.kicad_pcb')!=receipt['importedBoardSha256']:
        raise ValueError('Imported board differs from routing receipt')


def prepare(output):
    import pcbnew as pcb
    spec = json.loads((REF/'implementation.json').read_text())
    if output.resolve().parent == ROOT:
        raise ValueError('Reference preparation cannot overwrite historical authorities')
    board = pcb.LoadBoard(str(REF/'routing/historical-input.kicad_pcb'))
    found = set()
    def vector(x,y): return pcb.VECTOR2I(round(x*1e6),round(y*1e6))
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        footprint.SetFPID(pcb.LIB_ID('', 'RobotronReference_'+ref))
        if ref not in spec['placements']: continue
        found.add(ref)
        placement = spec['placements'][ref]
        x,y = placement['position']
        footprint.SetOrientationDegrees(0)
        footprint.SetPosition(vector(150+x,50-y))
        if 'padOffsets' in placement:
            if set(placement['padOffsets']) != {p.GetNumber() for p in footprint.Pads()}:
                raise ValueError('Incomplete proposed terminal mapping: '+ref)
            for pad in footprint.Pads():
                dx,dy = placement['padOffsets'][pad.GetNumber()]
                pad.SetPosition(vector(150+x+dx,50-y-dy))
    if found != set(spec['placements']): raise ValueError('Unknown proposed component')
    adjustments = {item['uuid']:item for item in spec['historicalCopperAdjustments']}
    applied = set()
    for item in list(board.GetTracks()):
        uid = item.m_Uuid.AsString()
        change = adjustments.get(uid)
        if change:
            applied.add(uid)
            if change['action'] == 'reroute':
                board.Remove(item)
                continue
            if change['action'] != 'width': raise ValueError('Unknown reference adjustment')
            item.SetWidth(pcb.FromMM(change['widthMm']))
        item.SetLocked(spec.get('preserveExistingRoutes',True))
    if applied != set(adjustments): raise ValueError('Unknown historical copper adjustment')
    output.parent.mkdir(parents=True,exist_ok=True)
    board.SetFileName(str(output))
    pcb.SaveBoard(str(output),board)
    shutil.copyfile(ROOT/'controller.kicad_pro',output.with_suffix('.kicad_pro'))
    if not pcb.ExportSpecctraDSN(board,str(output.with_suffix('.dsn'))):
        raise ValueError('Reference DSN export failed')
    dsn = output.with_suffix('.dsn')
    dsn.write_text(router_deck(dsn.read_text(),spec))


def router_deck(text,spec):
    if not spec.get('preserveExistingRoutes',True):
        # Specctra 'route' is USER_FIXED in Freerouting; 'normal' is editable.
        text = text.replace('(type route)','(type normal)')
    if '(unit um)' not in text: raise ValueError('Expected micrometre DSN units')
    width = spec['routing']['trackWidthMm']*1000
    text,count = re.subn(r'\(width [0-9.]+\)',f'(width {width:g})',text)
    if count!=2: raise ValueError('Expected global and default net-class widths')
    pattern = r'\(boundary\s+\(path pcb 0\s+([-0-9.\s]+)\)\s*\)'
    matches = list(re.finditer(pattern,text))
    if len(matches)!=1: raise ValueError('Expected one rectangular routing boundary')
    match = matches[0]
    values = list(map(float,match[1].split()))
    xs,ys = set(values[::2]),set(values[1::2])
    if len(values)!=10 or len(xs)!=2 or len(ys)!=2 or values[:2]!=values[-2:]:
        raise ValueError('Routing inset needs a closed rectangular outline')
    inset = spec['routing']['routerEnvelopeInsetMm']*1000
    if inset<0 or 2*inset>=min(max(xs)-min(xs),max(ys)-min(ys)):
        raise ValueError('Invalid routing envelope inset')
    coords = [v+(inset if v==min(xs if i%2==0 else ys) else -inset) for i,v in enumerate(values)]
    boundary = '(boundary (path pcb 0 '+' '.join(f'{v:g}' for v in coords)+'))'
    return text[:match.start()]+boundary+text[match.end():]


def import_session(board_path, session, output):
    import pcbnew as pcb
    board = pcb.LoadBoard(str(board_path))
    def pads():
        return {(f.GetReference(),p.GetNumber()):(p.GetPosition().x,p.GetPosition().y,p.GetNetname())
                for f in board.GetFootprints() for p in f.Pads()}
    before = pads()
    if not pcb.ImportSpecctraSES(board,str(session)):
        raise ValueError('Session import failed; no output saved')
    after = pads()
    if set(before)!=set(after) or any(a[2]!=after[k][2] or max(abs(a[i]-after[k][i]) for i in (0,1))>1000 for k,a in before.items()):
        raise ValueError('Router changed reference terminals beyond 1 um interchange precision')
    if output.resolve().parent == ROOT:
        raise ValueError('Cannot overwrite historical authorities')
    pcb.SaveBoard(str(output),board)
    shutil.copyfile(board_path.with_suffix('.kicad_pro'),output.with_suffix('.kicad_pro'))


def validate_pins(components, expected, unused):
    seen = set()
    for component in components:
        ref = component['ref']
        if ref not in expected:
            if any(p['net'] for p in component['pads']): raise ValueError('Unexpected electrical component: '+ref)
            continue
        for pad in component['pads']:
            pin,net = pad['pin'],pad['net']
            if (ref,pin) in seen: raise ValueError('Duplicate reference terminal')
            seen.add((ref,pin))
            pins = expected[ref]['pins']
            if pin in unused.get(ref,[]):
                if net is not None: raise ValueError('Connected unused package pad')
            elif pin not in pins or net != pins[pin]:
                raise ValueError('Reference pad-net mismatch: '+ref+':'+pin)
    required = {(ref,pin) for ref,c in expected.items() for pin in c['pins']}
    required |= {(ref,pin) for ref,pins in unused.items() for pin in pins}
    if required != seen: raise ValueError('Missing or extra reference terminals')


def export():
    check_receipt()
    import pcbnew as pcb
    from geometry import arc_points, outline_polygon
    from route_evidence import geometry_sha
    from routing_audit import build as routing_audit
    board_path = REF/'controller.kicad_pcb'
    board = pcb.LoadBoard(str(board_path))
    spec = json.loads((REF/'implementation.json').read_text())
    expected = json.loads((ROOT/'generated/connectivity.json').read_text())['components']
    evidence = json.loads((ROOT/'component-evidence.json').read_text())
    unused = {ref:e['physicalUnusedPads'] for ref,e in evidence.items() if e.get('physicalUnusedPads')}
    historical = json.loads((ROOT/'generated/layout.json').read_text())
    original = {r['id']:r for r in historical['routes']+historical['vias']}
    def xy(point): return [round(point.x/1e6-150,6),round(50-point.y/1e6,6)]
    def size(point): return [round(point.x/1e6,6),round(point.y/1e6,6)]
    components = []
    for footprint in sorted(board.GetFootprints(),key=lambda f:f.GetReference()):
        ref = footprint.GetReference()
        proposed = ref in spec['placements'] or ref in spec['referenceOnlyExistingPlacements']
        component = {'ref':ref,'type':footprint.GetValue(),'position':xy(footprint.GetPosition()),
                     'rotation':footprint.GetOrientationDegrees(),'side':'bottom' if footprint.IsFlipped() else 'top',
                     'classification':'proposed' if proposed else 'inherited-historical-estimate','pads':[]}
        for pad in sorted(footprint.Pads(),key=lambda p:p.GetNumber()):
            net = pad.GetNetname()
            component['pads'].append({'ref':ref,'pin':pad.GetNumber(),'net':None if not net or net.startswith('unconnected-') else net,
                                     'position':xy(pad.GetPosition()),'size':size(pad.GetSize()),'drill':size(pad.GetDrillSize())})
        components.append(component)
    validate_pins(components,expected,unused)
    if board.Zones(): raise ValueError('Reference zones are not supported')
    routes,vias,edges = [],[],[]
    for item in board.GetTracks():
        if isinstance(item,pcb.PCB_VIA):
            if item.GetViaType()!=pcb.VIATYPE_THROUGH: raise ValueError('Unsupported reference via')
            row = {'id':item.m_Uuid.AsString(),'position':xy(item.GetPosition()),'diameter':item.GetWidth(pcb.F_Cu)/1e6,'drill':item.GetDrillValue()/1e6,'net':item.GetNetname()}
            vias.append(row)
        else:
            if item.GetLayer() not in (pcb.F_Cu,pcb.B_Cu): raise ValueError('Unsupported reference layer')
            points = arc_points(xy(item.GetStart()),xy(item.GetMid()),xy(item.GetEnd())) if isinstance(item,pcb.PCB_ARC) else [xy(item.GetStart()),xy(item.GetEnd())]
            row = {'id':item.m_Uuid.AsString(),'points':points,'width':item.GetWidth()/1e6,'side':'top' if item.GetLayer()==pcb.F_Cu else 'bottom','net':item.GetNetname()}
            routes.append(row)
        inherited = original.get(row['id'])
        row['classification'] = 'inherited-historical-geometry' if inherited and geometry_sha(row)==geometry_sha(inherited) else 'proposed'
        row['evidence'] = inherited['evidence'] if row['classification'].startswith('inherited') else {'status':'proposed','detail':'Reference implementation only; no historical routing claim.'}
    for item in board.GetDrawings():
        if item.GetLayer()!=pcb.Edge_Cuts: continue
        if item.GetShape()==pcb.SHAPE_T_ARC:
            points = arc_points(xy(item.GetStart()),xy(item.GetArcMid()),xy(item.GetEnd()))
        elif item.GetShape()==pcb.SHAPE_T_SEGMENT: points = [xy(item.GetStart()),xy(item.GetEnd())]
        else: raise ValueError('Unsupported reference outline')
        edges.extend([[a,b] for a,b in zip(points,points[1:])])
    layout = {'schema':1,'variant':'proposed-reference','scope':spec['scope'], 'coordinates':historical['coordinates'],
              'outline':edges,'outlinePolygon':outline_polygon(edges),'components':components,'unplaced':[],
              'routes':sorted(routes,key=lambda r:r['id']),'vias':sorted(vias,key=lambda r:r['id']),'unresolvedArtwork':[]}
    cli = os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)/'drc.json'
        subprocess.run([cli,'pcb','drc','--format','json','-o',str(path),str(board_path)],check=True,stdout=subprocess.DEVNULL)
        drc = json.loads(path.read_text())
    audit = routing_audit(board,expected,layout,drc)
    qualification = {'variant':'proposed-reference','padNetMismatches':[],
                     'drc':{'violations':dict(collections.Counter(v['type'] for v in drc['violations'])), 'unconnectedItems':len(drc['unconnected_items'])},
                     'routingComplete':not drc['unconnected_items'], 'drcPassed':not drc['violations'],
                     'electricallyQualified':False,'historicallyVerified':False,'fabricationReady':False,
                     'scope':spec['scope']}
    write(REF/'generated/layout.json',layout)
    write(REF/'generated/qualification.json',qualification)
    write(REF/'generated/routing-audit.json',audit)
    pads = [pad for c in components for pad in c['pads']]
    scad = '// Generated proposed reference geometry. No historical or fabrication claim.\n'
    for key,value in [('outline',layout['outlinePolygon']),('pads',[[*p['position'],*p['size'],p['drill'][0]] for p in pads]),
                      ('routes',[[r['points'],r['width'],r['side']=='top',r['classification']=='proposed'] for r in layout['routes']]),
                      ('vias',[[*v['position'],v['diameter'],v['drill']] for v in layout['vias']])]:
        scad += 'reference_'+key+'='+json.dumps(value)+';\n'
    write(REF/'generated/controller.scad',scad)
    sources = ['controller.kicad_pcb','controller.kicad_sch','generated/connectivity.json','generated/layout.json','component-evidence.json','route-evidence.json',
               'tools/reference_board.py','tools/geometry.py','tools/routing_audit.py','tools/route_evidence.py',
               'reference/implementation.json','reference/controller.kicad_pcb','reference/controller.kicad_pro',
               'reference/review.scad','reference/routing-receipt.json']
    sources += [name for name in json.loads((REF/'routing-receipt.json').read_text())['sources'] if name not in sources]
    sources += [str(p.relative_to(ROOT)) for p in sorted((REF/'routing').iterdir()) if p.is_file()]
    outputs = [p for p in (REF/'generated').iterdir() if p.name!='manifest.json']
    write(REF/'generated/manifest.json',{'schema':1,'variant':'proposed-reference','tools':{'pcbnew':pcb.GetBuildVersion()},
                                      'sources':{name:sha(ROOT/name) for name in sources},
                                      'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)}})
    print(json.dumps(qualification,indent=2))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--import-session',type=Path)
    parser.add_argument('--input-board',type=Path)
    parser.add_argument('--output-board',type=Path)
    parser.add_argument('--prepare',type=Path,help='Write a proposed placement board and routing DSN outside the historical directory')
    args = parser.parse_args()
    if args.check: check()
    elif args.prepare: prepare(args.prepare)
    elif args.import_session:
        if not args.input_board or not args.output_board: parser.error('Session import requires input and output boards')
        import_session(args.input_board,args.import_session,args.output_board)
    else: export()
