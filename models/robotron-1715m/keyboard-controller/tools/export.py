#!/usr/bin/env python3
"""Export the native KiCad authorities. Run with KiCad's Python (pcbnew).
--check needs only standard Python and checks all pinned sources and outputs.
"""
import argparse,hashlib,json,math,os,shutil,subprocess,tempfile,collections,xml.etree.ElementTree as ET
from pathlib import Path
from geometry import arc_points, outline_polygon
from connector_review import review as connector_review, placement_review
from top_registration import review as top_review
from connector_terminals import review as connector_terminals
from route_evidence import annotate as annotate_routes
from photo_registration import review as photo_review, svg as photo_svg
from bottom_registration import review as bottom_review, svg as bottom_svg, validate_registered_routes, validate_pad_placements
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 p=ROOT/'generated'/name;p.parent.mkdir(exist_ok=True);p.write_text(value if isinstance(value,str) else json.dumps(value,indent=2,sort_keys=True)+'\n')
def check():
 m=json.loads((ROOT/'generated/manifest.json').read_text())
 for group in ['sources','outputs']:
  for name,sha in m[group].items():
   p=ROOT/name
   if not p.is_file() or digest(p)!=sha:raise SystemExit('Stale or missing '+name+'; regenerate with tools/export.py')
 print('Controller sources and generated outputs match pinned hashes')
def visual_bridges(evidence,landmarks,unplaced):
 """Project observed wire endpoints without inventing numbered electrical pads."""
 from photo_registration import homography,project
 transform=homography(landmarks['photoCorners'],landmarks['modelCorners'])
 sources={source['id']:source for source in evidence['sources']}
 refs={c['ref'] for c in unplaced};result=[]
 for bridge in evidence['serviceInterfaces']['bridges']:
  observation=bridge.get('physicalEvidence',{})
  if bridge['ref'] not in refs or observation.get('status')!='photo-location-candidate':continue
  if observation['photoSource']!='photo-top':raise ValueError('Unsupported bridge photograph')
  source=sources[observation['photoSource']]
  if source['path']!=landmarks['photo']:raise ValueError('Bridge photograph differs from registration')
  ends=observation['photoEndpoints']
  if len(ends)!=2 or any(len(p)!=2 or any(not math.isfinite(v) for v in p) for p in ends):raise ValueError('Invalid bridge endpoints')
  points=[[round(v,6) for v in project(transform,p)]for p in ends]
  if math.dist(*points)<1e-6:raise ValueError('Degenerate bridge observation')
  result.append({'ref':bridge['ref'],'points':points,'side':'top',
   'status':'unassigned-wire-photo-estimate','photoSource':observation['photoSource'],
   'photoSha256':source['sha256'],'pixelUncertainty':observation['photoPixelUncertainty'],
   'scope':'Geometric endpoint order only; no numbered pads, holes, nets or continuity claim. Height and diameter are illustrative.'})
 return result
def visual_networks(component_evidence,evidence,landmarks,unplaced):
 """Visual body/raised-lead observations do not supply electrical footprints."""
 from photo_registration import homography,project
 transform=homography(landmarks['photoCorners'],landmarks['modelCorners'])
 sources={s['id']:s for s in evidence['sources']};result=[]
 for c in unplaced:
  record=component_evidence.get(c['ref'],{});candidate=record.get('visualNetworkCandidate')
  if not candidate:continue
  source=sources[candidate['photoSource']]
  if candidate['status']!='body-and-raised-leads-only' or source.get('specimenId') or source['path']!=landmarks['photo']:raise ValueError('Network body requires primary registered photo')
  observations=record['terminalReview']
  if observations['photoSource']!=candidate['photoSource']:raise ValueError('Network leads use a different photograph')
  axis=candidate['photoBodyAxis'];leads=observations['observedLeadPixels']
  if len(axis)!=2 or not leads or any(len(p)!=2 or any(not math.isfinite(v)for v in p)for p in axis+leads):raise ValueError('Invalid network observations')
  a,b=[[round(v,6)for v in project(transform,p)]for p in axis]
  length=math.dist(a,b)
  if length<1e-6:raise ValueError('Degenerate network body axis')
  dims=[candidate[k]for k in ['bodyThicknessMm','bodyHeightMm','bodyBaseHeightMm','leadRadiusMm']]
  if any(not math.isfinite(v) or v<=0 for v in dims) or dims[2]<=1.6:raise ValueError('Network body must stand above the board')
  result.append({'ref':c['ref'],'status':candidate['status'],'axis':[a,b],
   'centre':[(a[i]+b[i])/2 for i in range(2)],'length':length,
   'rotation':math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),
   'thickness':dims[0],'height':dims[1],'baseHeight':dims[2],'leadRadius':dims[3],
   'observedLeads':[[round(v,6)for v in project(transform,p)]for p in leads],
   'photoSource':candidate['photoSource'],'photoSha256':source['sha256'],'scope':candidate['scope']})
 return result
def visual_axials(component_evidence,evidence,landmarks,unplaced):
 """Project raised resistor bodies independently of their unresolved hole entries."""
 from photo_registration import homography,project
 transform=homography(landmarks['photoCorners'],landmarks['modelCorners'])
 sources={s['id']:s for s in evidence['sources']};result=[]
 for c in unplaced:
  record=component_evidence.get(c['ref'],{});candidate=record.get('visualAxialCandidate')
  if not candidate:continue
  source=sources[candidate['photoSource']];leads=record['placementCandidate']
  if candidate['status']!='body-and-raised-leads-only' or source.get('specimenId') or source['path']!=landmarks['photo'] or leads['photoSource']!=candidate['photoSource']:raise ValueError('Axial observations require primary registered photo')
  axis=candidate['photoBodyAxis'];ends=leads['photoEndpoints']
  if len(axis)!=2 or len(ends)!=2 or any(len(p)!=2 or any(not math.isfinite(v)for v in p)for p in axis+ends):raise ValueError('Invalid axial observations')
  a,b=[[round(v,6)for v in project(transform,p)]for p in axis]
  length=math.dist(a,b)
  if length<1e-6:raise ValueError('Degenerate axial body axis')
  diameter,height,radius=[candidate[k]for k in ['bodyDiameterMm','bodyCentreHeightMm','leadRadiusMm']]
  if any(not math.isfinite(v)or v<=0 for v in [diameter,height,radius]) or height-diameter/2<=1.6:raise ValueError('Axial body must stand above the board')
  result.append({'ref':c['ref'],'status':candidate['status'],'axis':[a,b],
   'centre':[(a[i]+b[i])/2 for i in range(2)],'length':length,'rotation':math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),
   'diameter':diameter,'centreHeight':height,'leadRadius':radius,
   'observedLeads':[[round(v,6)for v in project(transform,p)]for p in ends],
   'blueCollarEnd':leads['blueCollarEndpoint'],'photoSource':candidate['photoSource'],'photoSha256':source['sha256'],'scope':candidate['scope']})
 return result
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 if args.check:return check()
 import pcbnew as pcb
 cli=os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
 with tempfile.TemporaryDirectory() as t:
  xml=Path(t)/'net.xml';erc=Path(t)/'erc.json';drc=Path(t)/'drc.json'
  subprocess.run([cli,'sch','export','netlist','--format','kicadxml','-o',str(xml),str(ROOT/'controller.kicad_sch')],check=True)
  subprocess.run([cli,'sch','erc','--format','json','-o',str(erc),str(ROOT/'controller.kicad_sch')],check=True)
  subprocess.run([cli,'pcb','drc','--format','json','-o',str(drc),str(ROOT/'controller.kicad_pcb')],check=True)
  drc_data=json.loads(drc.read_text())
  r=ET.parse(xml).getroot();violations=json.loads(erc.read_text())['sheets'][0]['violations']
 components={c.get('ref'):{'type':c.findtext('value'),'pins':{p.get('num'):None for p in c.findall('./units/unit/pins/pin')}} for c in r.findall('./components/comp')}
 for n in r.findall('./nets/net'):
  name=n.get('name');name=None if name.startswith('unconnected-') else name
  for node in n.findall('node'):components[node.get('ref')]['pins'][node.get('pin')]=name
 board=pcb.LoadBoard(str(ROOT/'controller.kicad_pcb'));placed=[];unplaced=[];pads=[];holes=[];mismatches=[]
 def xy(p):return [round(p.x/1e6-150,6),round(50-p.y/1e6,6)]
 def coord(p):return [round(p.x/1e6,6),round(p.y/1e6,6)]
 seen=set()
 for f in sorted(board.GetFootprints(),key=lambda x:x.GetReference()):
  ref=f.GetReference();pos=xy(f.GetPosition());in_board=-135<=pos[0]<=135 and -23<=pos[1]<=23;row={'ref':ref,'type':f.GetValue(),'position':pos,'rotation':f.GetOrientationDegrees(),'side':'bottom' if f.IsFlipped() else 'top','evidence':f.GetFieldText('Evidence') if f.HasField('Evidence') else 'photo-estimated-hole','pads':[]}
  for p in sorted(f.Pads(),key=lambda x:x.GetNumber()):
   net=p.GetNetname();net=None if not net or net.startswith('unconnected-') else net
   pin=p.GetNumber();a={'ref':ref,'pin':pin,'net':net,'position':xy(p.GetPosition()),'size':coord(p.GetSize()),'drill':coord(p.GetDrillSize())};row['pads'].append(a)
   if ref in components:
    seen.add((ref,pin))
    if pin not in components[ref]['pins'] or net!=components[ref]['pins'][pin]:mismatches.append([ref,pin,net,components[ref]['pins'].get(pin)])
   if in_board:
    pads.append(a)
    if a['drill'][0]:holes.append([*a['position'],a['drill'][0]])
  (placed if in_board else unplaced).append(row)
 for ref,c in components.items():
  for pin in c['pins']:
   if (ref,pin) not in seen:mismatches.append([ref,pin,'missing pad'])
 if mismatches:raise SystemExit('Schematic/PCB pad-net mismatch: '+repr(mismatches[:10]))
 routes=[];art=[];edges=[];vias=[]
 if board.Zones():raise SystemExit('Zone export not yet supported: refuse to omit geometry')
 for d in board.GetDrawings():
  layer=d.GetLayer()
  if layer not in (pcb.Edge_Cuts,pcb.Dwgs_User,pcb.Cmts_User):continue
  if d.GetShape()==pcb.SHAPE_T_ARC:points=arc_points(xy(d.GetStart()),xy(d.GetArcMid()),xy(d.GetEnd()))
  elif d.GetShape()==pcb.SHAPE_T_SEGMENT:points=[xy(d.GetStart()),xy(d.GetEnd())]
  else:raise SystemExit('Unsupported review/outline shape; refuse to omit geometry')
  item={'id':str(d.m_Uuid.AsString()),'points':points,'width':round(d.GetWidth()/1e6,6)}
  if d.GetLayer()==pcb.Edge_Cuts:edges.extend([[a,b] for a,b in zip(points,points[1:])])
  elif d.GetLayer() in (pcb.Dwgs_User,pcb.Cmts_User):art.append(dict(item,side='top' if d.GetLayer()==pcb.Dwgs_User else 'bottom',net=None,evidence='photo-polyline; net unresolved'))
 for d in board.GetTracks():
  if isinstance(d,pcb.PCB_VIA):
   if d.GetViaType()!=pcb.VIATYPE_THROUGH:raise SystemExit('Only through vias are supported')
   v={'id':d.m_Uuid.AsString(),'position':xy(d.GetPosition()),'diameter':d.GetWidth(pcb.F_Cu)/1e6,'drill':d.GetDrillValue()/1e6,'net':d.GetNetname()};vias.append(v);holes.append([*v['position'],v['drill']]);pads.append({'ref':v['id'],'pin':'via','position':v['position'],'size':[v['diameter']]*2,'drill':[v['drill']]*2,'net':v['net']});continue
  if d.GetLayer() not in (pcb.F_Cu,pcb.B_Cu):raise SystemExit('Internal-layer tracks are unsupported')
  points=arc_points(xy(d.GetStart()),xy(d.GetMid()),xy(d.GetEnd())) if isinstance(d,pcb.PCB_ARC) else [xy(d.GetStart()),xy(d.GetEnd())]
  routes.append({'id':d.m_Uuid.AsString(),'points':points,'width':d.GetWidth()/1e6,'net':d.GetNetname(),'side':'top' if d.GetLayer()==pcb.F_Cu else 'bottom','evidence':'KiCad route; historical provenance requires review'})
 annotate_routes(routes,vias,json.loads((ROOT/'route-evidence.json').read_text()),json.loads((ROOT/'evidence.json').read_text()))
 outline=outline_polygon(edges)
 layout={'schema':1,'coordinates':{'units':'mm','pcbOrigin':[150,50],'modelTransform':'x = pcb.x - 150; y = 50 - pcb.y; z = top height','thickness':1.6},'outline':edges,'outlinePolygon':outline,'components':placed,'unplaced':unplaced,'routes':routes,'vias':vias,'unresolvedArtwork':sorted(art,key=lambda a:a['id'])}
 bottom=bottom_review(layout);validate_registered_routes(routes,bottom,digest(ROOT/'bottom-landmarks.json'))
 top=top_review(layout);validate_registered_routes(routes,top,digest(ROOT/'top-copper-landmarks.json'),side='top')
 write('top-registration.json',top)
 bottom['padPlacements']=validate_pad_placements(layout,bottom,json.loads((ROOT/'component-evidence.json').read_text()))
 write('connectivity.json',{'schema':1,'authority':'controller.kicad_sch','components':components})
 layout['visualBridges']=visual_bridges(json.loads((ROOT/'evidence.json').read_text()),json.loads((ROOT/'photo-landmarks.json').read_text()),unplaced)
 connector=connector_review(layout,json.loads((ROOT/'component-evidence.json').read_text()),json.loads((ROOT/'evidence.json').read_text()),json.loads((ROOT/'photo-landmarks.json').read_text()),bottom)
 joints=connector['underside']
 if not joints['allJointsInsideAnchorHull'] or not joints['registrationWithinTolerance']:raise ValueError('Connector visual geometry requires bounded registration')
 terminals=connector_terminals(json.loads((ROOT/'component-evidence.json').read_text())['X1'],{'components':components})
 connector['nativePlacement']=placement_review(layout,connector,terminals)
 layout['visualConnectors']=[{'ref':'X1','status':'photo-placed-reference-terminal-order','unclassifiedContacts':connector['nativePlacement']['unclassifiedContacts'],'rows':joints['projectedJointRowsMm'],'photoSource':joints['photoSource'],'photoSha256':joints['photoSha256'],'scope':'Observed joint rows are retained independently of native reference pads. Only contacts absent from the reference schematic remain unassigned. Housing dimensions, contact heights, lead section and hole diameters remain illustrative.'}]
 layout['visualNetworks']=visual_networks(json.loads((ROOT/'component-evidence.json').read_text()),json.loads((ROOT/'evidence.json').read_text()),json.loads((ROOT/'photo-landmarks.json').read_text()),unplaced)
 layout['visualAxials']=visual_axials(json.loads((ROOT/'component-evidence.json').read_text()),json.loads((ROOT/'evidence.json').read_text()),json.loads((ROOT/'photo-landmarks.json').read_text()),unplaced)
 write('layout.json',layout)
 write('connector-review.json',connector)
 write('connector-terminals.json',terminals)
 photo=photo_review(layout);write('photo-registration.json',photo);write('photo-registration.svg',photo_svg(photo,layout))
 write('bottom-registration.json',bottom);write('bottom-registration.svg',bottom_svg(bottom,layout))
 # Semantic symbols preserve source numbered pins. ERC does not validate analog models.
 erc_summary=[{'type':v['type'],'severity':v['severity'],'description':v['description'],'items':[i['description'] for i in v['items']]} for v in violations]
 write('qualification.json',{'components':len(components),'placed':len(placed),'unplaced':len(unplaced),'padNetMismatches':mismatches,'electricalCopperSegments':len(routes),'unresolvedPhotoSegments':len(art),'erc':erc_summary,'drc':{'violations':dict(collections.Counter(v['type'] for v in drc_data['violations'])),'unconnectedItems':len(drc_data['unconnected_items'])},'limitations':['Signal pin directions are typed; power/passive terminals and analog behavior require separate review. Two isolated-label ERC warnings are RD_N (unused CPU output) and SHIELD (external cable shield).','Unrouted PCB, not fabrication ready. Photo graphics are not electrical copper.','Digital reference circuit; discrete pin numbering, specimen substitutions and analog timing remain unqualified; reset topology and bridge boundaries reviewed against Zander.']})
 scad=['// Generated from controller.kicad_pcb and package evidence. Model-local mm; no independent placement edits.', 'controller_pcb_outline='+json.dumps(outline)+';', 'controller_pcb_edges='+json.dumps(edges)+';', 'controller_pcb_holes='+json.dumps(holes)+';', 'controller_pcb_pads='+json.dumps([[*p['position'],*p['size'],p['net'],p['drill'][0]] for p in pads if p['pin']])+';']
 native_connector={p['pin']:p['position'] for c in placed if c['ref']=='X1' for p in c['pads']}
 scad+=['controller_visual_connector_contacts='+json.dumps([[*native_connector.get(pin,point),row]for row,name in enumerate(['housingFar','housingNear'])for pin,point in zip(terminals['resolvedRows'][name],layout['visualConnectors'][0]['rows'][name])])+';']
 scad+=['controller_pcb_dip_pads='+json.dumps([[*p['position'],p['drill'][0],p['ref'],p['pin']]for p in pads if p['ref'].startswith('A')])+';']
 scad+=['controller_pcb_dips='+json.dumps([[*c['position'],len(c['pads']),15.24 if len(c['pads']) in (24,40) else 7.62,c['ref'],c['rotation']] for c in placed if c['ref'].startswith('A')])+';']
 # Package dimensions are reference evidence, separate from native placements.
 packages=json.loads((ROOT/'evidence.json').read_text())['packageReferences']
 family=[next(p for p in packages if p['id']==name)for name in ['sc308-l3-12','sc236-l3-12']]
 fields=['bodyDimensionsMm','outerLeadSpanMm','leadSectionMm','flatFaceToLeadPlaneMm','backCornerRadiusMm']
 if any(family[0][key]!=family[1][key]for key in fields):raise ValueError('L3/12 family shapes differ; export separate package geometry')
 pkg=family[0];body=pkg['bodyDimensionsMm']
 for name,value in [('body',[body['width'],body['depth'],body['height']]),('lead_span',pkg['outerLeadSpanMm']),('lead_section',pkg['leadSectionMm']),('flat_offset',pkg['flatFaceToLeadPlaneMm']),('corner_radius',pkg['backCornerRadiusMm'])]:
  scad+=['controller_l3_12_'+name+'='+json.dumps(value)+';']

 # Unplaced body observations are explicitly visual, never native pad/net geometry.
 from photo_registration import homography,project
 landmarks=json.loads((ROOT/'photo-landmarks.json').read_text())
 body_projection=homography(landmarks['photoCorners'],landmarks['modelCorners'])
 component_evidence=json.loads((ROOT/'component-evidence.json').read_text())
 visual_transistors=[]
 for c in unplaced:
  candidate=component_evidence.get(c['ref'],{}).get('visualBodyCandidate')
  if candidate:
   if candidate['photoSource']!='photo-top' or candidate['status']!='body-only-photo-estimate':raise ValueError('Unsupported visual body candidate')
   a,b=[project(body_projection,p)for p in candidate['photoBodyAxis']]
   if math.dist(a,b)<1e-6:raise ValueError('Degenerate visual body axis: '+c['ref'])
   angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
   visual_transistors.append([*[round(v,6)for v in project(body_projection,candidate['photoBodyCentre'])],round(angle,6),c['ref']])
 scad+=['controller_visual_transistors='+json.dumps(visual_transistors)+';']
 scad+=['controller_visual_networks='+json.dumps([[n['centre'],n['rotation'],n['length'],n['thickness'],n['height'],n['baseHeight'],n['observedLeads'],n['leadRadius'],n['ref']]for n in layout['visualNetworks']])+';']
 scad+=['controller_visual_axials='+json.dumps([[n['centre'],n['rotation'],n['length'],n['diameter'],n['centreHeight'],n['observedLeads'],n['leadRadius'],1 if n['blueCollarEnd']=='right' else -1,n['ref']]for n in layout['visualAxials']])+';']
 resistor_evidence=json.loads((ROOT/'component-evidence.json').read_text());resistors=[]
 for c in placed:
  if c['ref'].startswith('R') and len(c['pads'])==2:
   a,b=[p['position']for p in c['pads']];resistors.append([(a[0]+b[0])/2,(a[1]+b[1])/2,math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),math.dist(a,b),c['ref'],{'1':-1,'2':1}.get(resistor_evidence.get(c['ref'],{}).get('blueCollarPin'),0)])
 scad+=['controller_pcb_resistors='+json.dumps(resistors)+';']
 scad+=['controller_pcb_resistor_pads='+json.dumps([[*p['position'],p['drill'][0],*p['size']]for p in pads if p['ref'].startswith('R')])+';']
 scad+=['controller_pcb_bridges='+json.dumps([[c['pads'][0]['position'],c['pads'][1]['position'],c['ref']]for c in placed if c['ref'].startswith('BR')])+';']
 scad+=['controller_visual_bridges='+json.dumps([[*b['points'],b['ref']]for b in layout['visualBridges']])+';']
 scad+=['controller_pcb_bridge_pads='+json.dumps([[*p['position'],p['drill'][0],*p['size']]for p in pads if p['ref'].startswith('BR')])+';']
 scad+=['controller_pcb_ceramics='+json.dumps([[c['position'],c['pads'][0]['position'],c['pads'][1]['position'],c['ref']]for c in placed if c['ref'].startswith('C5.')])+';']
 scad+=['controller_pcb_ceramic_pads='+json.dumps([[*p['position'],p['drill'][0],*p['size']]for p in pads if p['ref'].startswith('C5.')])+';']
 for side in ['top','bottom']:
  scad+=['controller_pcb_'+side+'_art='+json.dumps([[a['points'],a['width']] for a in art if a['side']==side])+';', 'controller_pcb_'+side+'_copper='+json.dumps([[a['points'],a['width']] for a in routes if a['side']==side])+';']
 write('controller.scad','\n'.join(scad).replace('null','undef')+'\n')
 # Review drawing retains both board sides and identifies unresolved artwork.
 import html
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-145 -40 290 155"><rect x="-145" y="-40" width="290" height="155" fill="#17232a"/>']
 for side,offset in [('top',0),('bottom',75)]:
  svg.append(f'<g transform="translate(0 {offset})"><text x="-135" y="-28" fill="white" font-size="4">{side}: cyan = unresolved photo artwork; pads = reference nets</text>')
  for a in art:
   if a['side']==side:svg.append('<polyline fill="none" stroke="#50b5c8" stroke-width=".35" points="'+' '.join(f'{x},{-y}' for x,y in a['points'])+'"/>')
  for a in routes:
   if a['side']==side:
    title=html.escape(a['net']+' '+a['evidence']['status']+' '+a['id'])
    svg.append('<polyline fill="none" stroke="#ffc969" stroke-width="'+str(a['width'])+'" points="'+' '.join(f'{x},{-y}'for x,y in a['points'])+'"><title>'+title+'</title></polyline>')
  for bridge in layout['visualBridges']:
   if bridge['side']==side:
    points=' '.join(f'{x},{-y}' for x,y in bridge['points'])
    svg.append('<polyline fill="none" stroke="#50b5c8" stroke-width=".5" points="'+points+'"><title>'+html.escape(bridge['ref']+' unassigned wire; terminal identity unresolved')+'</title></polyline>')
  for c in placed:
   for p in c['pads']:
    x,y=p['position'];svg.append(f'<circle cx="{x}" cy="{-y}" r=".65" fill="#ffc969"><title>{html.escape(c["ref"]+":"+p["pin"]+" "+str(p["net"]))}</title></circle>')
   x,y=c['position'];svg.append(f'<text x="{x}" y="{-y-4}" fill="white" font-size="2.8">{c["ref"]}</text>')
  svg.append('</g>')
 write('review.svg',''.join(svg)+'</svg>\n')
 inputs=['top-copper-landmarks.json','tools/top_registration.py','controller.kicad_sch','controller.kicad_pcb','controller.kicad_pro','kbd.kicad_sym','sym-lib-table','fp-lib-table','evidence.json','component-evidence.json','tools/export.py','tools/geometry.py','tools/connector_review.py','tools/connector_terminals.py','tools/route_evidence.py','route-evidence.json','tools/photo_registration.py','tools/bottom_registration.py','bottom-landmarks.json',json.loads((ROOT/'bottom-landmarks.json').read_text())['photo'],'photo-landmarks.json',json.loads((ROOT/'photo-landmarks.json').read_text())['photo']]
 outputs=sorted(p for p in (ROOT/'generated').iterdir() if p.name!='manifest.json')
 for source in json.loads((ROOT/'evidence.json').read_text())['sources']:
  if not source.get('path'):continue
  if digest(ROOT/source['path'])!=source['sha256']:raise SystemExit('Evidence source hash changed: '+source['id'])
  if source['path'] not in inputs:inputs.append(source['path'])
 write('manifest.json',{'schema':1,'tools':{'kicad':subprocess.check_output([cli,'version'],text=True).strip(),'pcbnew':pcb.GetBuildVersion()},'sources':{p:digest(ROOT/p) for p in inputs},'outputs':{str(p.relative_to(ROOT)):digest(p) for p in outputs}})
 print('Exported',len(components),'components;',len(unplaced),'unplaced;',len(art),'unresolved photo segments')
if __name__=='__main__':main()
