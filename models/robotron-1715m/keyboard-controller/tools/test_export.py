#!/usr/bin/env python3
"""Fast consistency and handedness checks; no KiCad install required."""
import importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from geometry import arc_points,outline_polygon
from photo_registration import homography,project,rigid_fit,selected_fits,review
R=Path(__file__).resolve().parents[1]
class ControllerExportTests(unittest.TestCase):
 def test_ceramic_body_and_bent_lead_endpoints_remain_distinct(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  c=next(c for c in layout['components']if c['ref']=='C5.1')
  self.assertEqual({p['pin']:p['net']for p in c['pads']},{'1':'/+5V','2':'/GND'})
  self.assertNotIn('C5.1',[c['ref']for c in layout['unplaced']])
  # The photographed disc is offset from the lead-entry line; centering it on
  # the pads would erase the bent-lead geometry this migration must preserve.
  midpoint=[sum(p['position'][i]for p in c['pads'])/2 for i in range(2)]
  self.assertGreater(c['position'][1]-midpoint[1],2.5)
  scad=(R/'generated/controller.scad').read_text()
  ceramics=json.loads(scad.split('controller_pcb_ceramics=')[1].split(';')[0])
  self.assertEqual(next(x for x in ceramics if x[3]=='C5.1'),[c['position'],c['pads'][0]['position'],c['pads'][1]['position'],'C5.1'])
  self.assertEqual({x[3]for x in ceramics},{'C5.1','C5.2','C5.3','C5.4'})
  for row in ceramics:
   native=next(x for x in layout['components']if x['ref']==row[3])
   self.assertEqual(row[:3],[native['position'],*[p['position']for p in native['pads']]])
 def test_curves_and_outline_errors(self):
  points=arc_points([10,0],[0,10],[-10,0])
  self.assertEqual(points[0],[10,0]);self.assertEqual(points[-1],[-10,0])
  self.assertGreater(max(y for x,y in points),9.9)
  for x,y in points:self.assertAlmostEqual(x*x+y*y,100,places=4)
  reverse=arc_points([-10,0],[0,10],[10,0]);self.assertGreater(max(y for x,y in reverse),9.9)
  with self.assertRaises(ValueError):outline_polygon([[[0,0],[1,0]],[[1,0],[1,1]]])
  with self.assertRaises(ValueError):arc_points([0,0],[1,0],[2,0])
 def test_photo_registration(self):
  h=homography([[0,0],[2,0],[2,1],[0,1]],[[4,3],[4,7],[2,7],[2,3]])
  self.assertEqual(project(h,[1,.5]),[3,5])
  angle,transform=rigid_fit([[0,0],[1,0],[0,1]],[[4,3],[4,4],[3,3]])
  self.assertAlmostEqual(angle,1.57079632679)
  self.assertAlmostEqual(transform([1,1])[0],3);self.assertAlmostEqual(transform([1,1])[1],4)
  report=json.loads((R/'generated/photo-registration.json').read_text())
  for c in report['components']:
   self.assertLessEqual(c['maxResidualMm'],report['toleranceMm'],c['ref'])
  self.assertTrue(report['withinPhotoTolerance'])
  self.assertEqual(len(next(c for c in report['components']if c['ref']=='A4')['checkPins']),4)
 def test_underside_registration_uses_independent_pads(self):
  from bottom_registration import review as bottom_review
  from unittest.mock import patch
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout)
  self.assertEqual(sum(p['heldOut']for p in report['pins']),6)
  self.assertFalse(report['withinPhotoTolerance']);self.assertFalse(report['copperAssignmentQualified'])
  self.assertGreater(report['maxCheckResidualMm'],report['toleranceMm'])
  self.assertEqual(len(report['crossPhoto']['checks']),6)
  cross={p['ref']+':'+p['pin']:p for p in report['crossPhoto']['checks']}
  self.assertLess(cross['A1:7']['nominalResidualMm'],.5)
  self.assertGreater(report['crossPhoto']['maxCheckResidualMm'],report['toleranceMm'])
  e=json.loads((R/'bottom-landmarks.json').read_text());e['checks'][0]=e['anchors'][0]
  with patch('bottom_registration.Path.read_text',return_value=json.dumps(e)):
   with self.assertRaisesRegex(ValueError,'unique'):bottom_review(layout)
 def test_fit_rejects_held_out_error_and_unknown_refs(self):
  from unittest.mock import patch
  evidence={'photoCorners':[[0,0],[2,0],[2,2],[0,2]],'modelCorners':[[0,0],[2,0],[2,2],[0,2]],'scope':'test','photo':'unused','maxResidualMm':1.25,'components':{'A1':{'pins':{'1':[0,0],'2':[1,0],'3':[0,1]},'checkPins':{'4':[1,4]}}}}
  layout={'components':[{'ref':'A1','position':[0,0],'pads':[{'pin':str(i+1),'position':p} for i,p in enumerate([[0,0],[1,0],[0,1],[1,1]])]}]}
  with patch('photo_registration.Path.read_text',return_value=json.dumps(evidence)),patch('photo_registration.Path.read_bytes',return_value=b'photo'):
   r=review(layout)
  self.assertEqual(r['components'][0]['fitMaxResidualMm'],3)
  with self.assertRaisesRegex(ValueError,'inconsistent'):selected_fits(r,['A1'])
  with self.assertRaisesRegex(ValueError,'Unknown'):selected_fits(r,['TYPO'])
 def test_reset_and_service_bridge_topology(self):
  c=json.loads((R/'generated/connectivity.json').read_text())['components']
  n=lambda ref,pin:c[ref]['pins'][pin]
  self.assertEqual(n('BR1','1'),n('A7','8'));self.assertEqual(n('BR1','2'),n('A5','6'));self.assertNotEqual(n('BR1','1'),n('BR1','2'))
  self.assertEqual(n('BR2','1'),n('V4.9','C'));self.assertEqual(n('BR2','2'),n('A5','26'));self.assertNotEqual(n('BR2','1'),n('BR2','2'))
  self.assertEqual(n('C1','2'),n('V4.9','C'));self.assertNotEqual(n('C1','2'),n('C4','1'))
  self.assertEqual(n('V3.1','C'),'/+5V');self.assertEqual(n('V3.2','C'),n('V4.9','B'))
  self.assertEqual(n('R5','2'),n('V3.2','B'));self.assertEqual(n('V1.2','A'),n('C2','1'))
  self.assertEqual(n('X1','A9'),n('A5','25'));self.assertEqual(n('R6.5','2'),n('A5','25'));self.assertNotEqual(n('A5','25'),n('A5','24'))
 def test_cable_filter_pin_mapping(self):
  c=json.loads((R/'generated/connectivity.json').read_text())['components']
  for choke,signal,cable,pin in [('L1.1','/TA_TAKT','/CABLE_TAKT','B2'),('L1.2','/GND','/CABLE_GND','A3'),('L1.3','/+5V','/CABLE_5V','B4'),('L1.4','/TA_DATEN','/CABLE_DATEN','A1')]:
   self.assertEqual(c[choke]['pins'],{'1':signal,'2':cable});self.assertEqual(c['XT1']['pins'][pin],cable)
 def test_local_registration_does_not_qualify_extrapolated_copper(self):
  from bottom_registration import review as bottom_review,local_reviews
  report=bottom_review(json.loads((R/'generated/layout.json').read_text()))
  region=report['localRegions'][0]
  self.assertEqual(len(region['checks']),4);self.assertLess(region['maxCheckResidualMm'],.4)
  self.assertTrue(region['withinPhotoTolerance']);self.assertFalse(region['copperAssignmentQualified'])
  self.assertTrue(all(p['outsideAnchorBounds']for p in region['candidates']))
  self.assertLess(region['candidates'][0]['nominalResidualMm'],.3)
  self.assertGreater(region['extrapolationChecks'][0]['nominalResidualMm'],2)
  bad={'localRegions':[{'anchors':[{'ref':'A4','pin':'1'}]*4,'checks':[{'ref':'A4','pin':'1'}]}]}
  with self.assertRaisesRegex(ValueError,'unique'):local_reviews(bad,{},[])
 def test_cpu_region_limits_and_withdrawn_clock_assignment(self):
  from bottom_registration import review as bottom_review,validate_registered_routes,pcb_regions,inside_hull
  from copy import deepcopy
  import hashlib
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout);region=report['pcbRegions'][0]
  self.assertTrue(region['copperAssignmentQualified']);self.assertFalse(report['copperAssignmentQualified'])
  self.assertEqual(len(region['checks']),6);self.assertLess(region['maxCheckResidualMm'],.67)
  self.assertTrue(any(p['ref']=='A5'and p['pin']=='6'for p in region['checks']))
  self.assertFalse(any(r['evidence']['group']=='cpu-clock-bottom-partial'for r in layout['routes']))
  self.assertEqual(len([r for r in layout['routes']if r['net']=='/CLK']),1)
  conflict=json.loads((R/'evidence.json').read_text())['routeReviews'][0]
  self.assertEqual(conflict['status'],'assignment-withdrawn')
  self.assertFalse(set(conflict['withdrawnNativeTrackIds'])&{r['id']for r in layout['routes']})
  # Synthetic geometry exercises the registration guard without asserting a net.
  pixels=[[1328,2678],[1360,2706]]
  route={'side':'bottom','points':[project(region['photoToModel'],p)for p in pixels],
   'evidence':{'status':'observed','registration':{'region':'cpu-a4','landmarksSha256':''},
    'sources':[{'id':'photo-bottom','locator':{'pixelSegment':pixels}}]}}
  routes=[deepcopy(route),deepcopy(route)]
  digest=hashlib.sha256((R/'bottom-landmarks.json').read_bytes()).hexdigest()
  for route in routes:route['evidence']['registration']['landmarksSha256']=digest
  validate_registered_routes(routes,report,digest)
  with self.assertRaisesRegex(ValueError,'Stale'):validate_registered_routes(routes,report,'changed')
  bad=deepcopy(routes);bad[1]['evidence']['sources'][0]['locator']['pixelSegment'][0]=[1600,3700]
  with self.assertRaisesRegex(ValueError,'hull'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['points'][0][0]+=1
  with self.assertRaisesRegex(ValueError,'projection'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['evidence']['status']='inferred';bad[1]['points'][0]=[1000,1000]
  with self.assertRaisesRegex(ValueError,'hull'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['evidence']['status']='inferred';bad[1]['points'][0][0]+=2
  with self.assertRaisesRegex(ValueError,'tolerance'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(report);bad['pcbRegions'][0]['copperAssignmentQualified']=False
  with self.assertRaisesRegex(ValueError,'not locally'):validate_registered_routes(routes,bad,digest)
  evidence=json.loads((R/'bottom-landmarks.json').read_text());pads={(c['ref'],p['pin']):p['position']for c in layout['components']for p in c['pads']}
  evidence['pcbRegions'][0]['checks'][-1]['photoPixel'][0]+=100
  self.assertFalse(pcb_regions(evidence,pads)[0]['copperAssignmentQualified'])
  self.assertFalse(inside_hull([0,0],region['anchorHull']))
 def test_a2_factory_identity_and_placement(self):
  components=json.loads((R/'generated/connectivity.json').read_text())['components']
  review=json.loads((R/'evidence.json').read_text())['referenceVariants'][0]
  self.assertEqual(review['status'],'reconstruction-placement-error-corrected')
  self.assertEqual(sum(len(g)for g in review['schematicGateReview'].values()),12)
  for ref,gates in review['schematicGateReview'].items():
   for gate in gates:
    for pin in gate['inputs']:self.assertEqual(components[ref]['pins'][pin],gate['inputNet'])
    self.assertEqual(components[ref]['pins'][gate['output']],gate['outputNet'])
  placed={c['ref']:c for c in json.loads((R/'generated/layout.json').read_text())['components']}
  self.assertLess(placed['A2.1']['position'][0],0)
  self.assertGreater(placed['A2.1']['position'][1],0)
  self.assertGreater(placed['A2.2']['position'][0],0)
  self.assertLess(placed['A2.2']['position'][1],0)
  self.assertGreater(placed['A2.3']['position'][0],0)
  self.assertGreater(placed['A2.3']['position'][1],0)
 def test_native_output_pullups_replace_unplaced_estimates(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  for ref,signal in [('R10.1','/TA_TAKT'),('R10.2','/TA_DATEN')]:
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual(pads['1']['net'],'/+5V');self.assertEqual(pads['2']['net'],signal)
   self.assertGreater(pads['1']['position'][0],pads['2']['position'][0])
   self.assertNotIn(ref,[c['ref']for c in layout['unplaced']])
  report=json.loads((R/'generated/photo-registration.json').read_text())
  self.assertTrue({'R10.1','R10.2'} <= {r['ref']for r in report['discretes']})
  for row in report['discretes']:
   self.assertFalse(row['independentValidation']);self.assertLess(row['maxResidualMm'],.00001)
  self.assertIn('controller_pcb_resistors=',(R/'generated/controller.scad').read_text())
 def test_sensing_bank_native_order_and_photo_finish(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  refs=['R9.'+str(i)for i in range(1,9)];rows=[7,6,0,5,1,2,3,4]
  self.assertEqual([placed[r]['position'][1]for r in refs],sorted(placed[r]['position'][1]for r in refs))
  for ref,row in zip(refs,rows):
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual(pads['1']['net'],'/ROW'+str(row));self.assertEqual(pads['2']['net'],'/BASE'+str(row))
   self.assertGreater(pads['1']['position'][0],pads['2']['position'][0])
  evidence=json.loads((R/'component-evidence.json').read_text())
  self.assertEqual([evidence[r]['blueCollarPin']for r in refs],['2']*6+['1','2'])
  text=(R/'generated/controller.scad').read_text();line=next(s for s in text.splitlines()if s.startswith('controller_pcb_resistors='))
  exported=json.loads(line.split('=',1)[1].rstrip(';'));self.assertEqual(len(exported),24)
  self.assertEqual(next(r[5]for r in exported if r[4]=='R9.7'),-1)
  self.assertEqual(next(r[5]for r in exported if r[4]=='R9.8'),1)
 def test_reset_resistor_common_strip_terminal_order(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  evidence=json.loads((R/'component-evidence.json').read_text());nets=[]
  for ref,signal in [('R4.2','RESET_OUT'),('R7','RESET_EMITTERS'),('R8','RESET_RC')]:
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual({n:p['net']for n,p in pads.items()},{'1':'/'+signal,'2':'/GND'})
   self.assertLess(pads['2']['position'][1],pads['1']['position'][1])
   self.assertLess(evidence[ref]['photoPins']['2'][0],evidence[ref]['photoPins']['1'][0])
   self.assertNotIn('placementCandidate',evidence[ref]);nets.append({p['net']for p in pads.values()})
  self.assertEqual(set.intersection(*nets),{'/GND'})
 def test_led_resistor_inner_leads_face_adjacent_connector_rows(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  a,b=[{p['pin']:p for p in placed[r]['pads']}for r in ['R11.1','R11.2']]
  self.assertLess(a['1']['position'][0],a['2']['position'][0])
  self.assertLess(a['2']['position'][0],b['2']['position'][0])
  self.assertLess(b['2']['position'][0],b['1']['position'][0])
  for pads,name in [(a,'SISO'),(b,'CAPS')]:
   self.assertEqual(pads['1']['net'],'/LED_'+name+'_N');self.assertEqual(pads['2']['net'],'/LED_'+name)
 def test_partial_a1_route_keeps_endpoint_unresolved(self):
  from route_evidence import annotate
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=layout['routes'];self.assertEqual(len(routes),25)
  annotate(routes,layout['vias'],json.loads((R/'route-evidence.json').read_text()),json.loads((R/'evidence.json').read_text()))
  routes=[r for r in routes if r['net']=='/WR_N'];self.assertEqual(len(routes),8)
  self.assertEqual({r['net']for r in routes},{'/WR_N'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),7)
  self.assertEqual(sum(r['evidence']['status']=='inferred'for r in routes),1)
  self.assertFalse(layout['vias'])
  self.assertEqual(json.loads((R/'generated/qualification.json').read_text())['drc']['violations'],{'track_dangling':1})
  self.assertIn('magenta',(R/'generated/photo-registration.svg').read_text())
 def test_reset_pair_supply_route_connects_only_reviewed_pads(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence'].get('group')=='reset-pair-supply-top']
  self.assertEqual(len(routes),5);self.assertEqual({r['net']for r in routes},{'/+5V'})
  self.assertEqual({r['side']for r in routes},{'top'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),3)
  self.assertEqual(sum(r['evidence']['status']=='inferred'for r in routes),2)
  # Check actual exported copper reaches both numbered supply pads, with no branches.
  from collections import Counter
  ends=Counter(tuple(p)for r in routes for p in r['points'])
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R3','R4.1']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  self.assertTrue(all(n in [1,2]for n in ends.values()))
  self.assertEqual(json.loads((R/'generated/qualification.json').read_text())['drc']['unconnectedItems'],229)
 def test_reset_supply_tree_reaches_four_resistors(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence']['group'].startswith('reset-')]
  self.assertEqual(len(routes),13)
  from collections import Counter,defaultdict
  ends=Counter();edges=defaultdict(set)
  for r in routes:
   a,b=map(tuple,r['points']);ends.update([a,b]);edges[a].add(b);edges[b].add(a)
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R3','R4.1','R5','R6.1']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  seen=set();pending=[pads[0]]
  while pending:
   point=pending.pop()
   if point in seen:continue
   seen.add(point);pending.extend(edges[point]-seen)
  self.assertEqual(seen,set(ends));self.assertEqual(sum(n==3 for n in ends.values()),2)
  r5=next(c for c in layout['components']if c['ref']=='R5');pads={p['pin']:p for p in r5['pads']}
  self.assertEqual(pads['2']['net'],'/RESET_BIAS')
  self.assertGreater(pads['1']['position'][1],pads['2']['position'][1])
 def test_a4_pullup_supply_link_preserves_separate_island(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence']['group']=='a4-pullup-supply-top']
  self.assertEqual(len(routes),3);self.assertEqual({r['net']for r in routes},{'/+5V'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),1)
  from collections import Counter
  ends=Counter(tuple(p)for r in routes for p in r['points'])
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R6.3','R9.9']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  reset_points={tuple(p)for r in layout['routes']if r['evidence']['group'].startswith('reset-')for p in r['points']}
  self.assertFalse(set(ends)&reset_points)
 def test_br1_reference_sides_and_inferred_local_clock_route(self):
  layout=json.loads((R/'generated/layout.json').read_text());parts={c['ref']:c for c in layout['components']}
  bridge={p['pin']:p for p in parts['BR1']['pads']};pullup={p['pin']:p for p in parts['R10.3']['pads']}
  self.assertEqual(bridge['1']['net'],'/OSC_OUT');self.assertEqual(bridge['2']['net'],'/CLK')
  self.assertEqual(pullup['2']['net'],'/CLK');self.assertEqual(pullup['1']['net'],'/+5V')
  routes=[r for r in layout['routes']if r['evidence']['group']=='br1-r103-local-clock'];self.assertEqual(len(routes),1)
  route=routes[0];self.assertEqual(route['side'],'bottom');self.assertEqual(route['evidence']['status'],'inferred')
  self.assertEqual({tuple(p)for p in route['points']},{tuple(bridge['2']['position']),tuple(pullup['2']['position'])})
  self.assertFalse(json.loads((R/'generated/bottom-registration.json').read_text())['copperAssignmentQualified'])
  text=(R/'generated/controller.scad').read_text();line=next(s for s in text.splitlines()if s.startswith('controller_pcb_bridges='))
  exported=json.loads(line.split('=',1)[1].rstrip(';'));self.assertEqual(exported,[[bridge['1']['position'],bridge['2']['position'],'BR1']])
 def test_route_evidence_rejects_stale_or_unsupported_claims(self):
  from route_evidence import annotate,geometry_sha
  from copy import deepcopy
  route={'id':'track-1','points':[[0,0],[1,0]],'width':.3,'side':'top','net':'/TA_TAKT'}
  sources={'sources':[{'id':'photo-top','sha256':'abc'},{'id':'schematic','sha256':'def'}]}
  record={'status':'observed','geometrySha256':geometry_sha(route),'detail':'Visible section, hidden continuation unresolved.','sources':[{'id':'photo-top','sha256':'abc','locator':'original pixels: (10,20) to (30,40)'}]}
  ledger={'schema':1,'items':{'track-1':record}}
  routes=[deepcopy(route)];annotate(routes,[],ledger,sources)
  self.assertEqual(routes[0]['evidence'],record)
  for field,value in [('net','/D0'),('side','bottom'),('width',.4),('points',[[0,0],[2,0]])]:
   changed=dict(route,**{field:value})
   with self.assertRaisesRegex(ValueError,'geometry changed'):annotate([changed],[],ledger,sources)
  with self.assertRaisesRegex(ValueError,'exactly'):annotate([],[],ledger,sources)
  for change,message in [({'status':'verified'},'status'),({'detail':''},'explanation'),({'sources':[]},'source references'),({'sources':[{'id':'photo-top','sha256':'old','locator':'p1'}]},'stale'),({'sources':[{'id':'schematic','sha256':'def','locator':'p1'}]},'photographs')]:
   bad=deepcopy(ledger);bad['items']['track-1'].update(change)
   with self.assertRaisesRegex(ValueError,message):annotate([deepcopy(route)],[],bad,sources)
  via={'id':'via-1','position':[0,0],'diameter':1,'drill':.5,'net':'/TA_TAKT'}
  vrecord=dict(record,geometrySha256=geometry_sha(via))
  with self.assertRaisesRegex(ValueError,'board sides'):annotate([],[via],{'schema':1,'items':{'via-1':vrecord}},sources)
 def test_pinned_sources(self):subprocess.run([sys.executable,R/'tools/export.py','--check'],check=True)
 def test_asymmetric_landmarks(self):
  layout=json.loads((R/'generated/layout.json').read_text());cs={c['ref']:c for c in layout['components']}
  # CPU and ROM are deliberately not interchangeable; pad 1 fixes handedness.
  self.assertLess(cs['A5']['position'][0],cs['A8']['position'][0]);self.assertGreater(cs['A5']['position'][1],0)
  pads={p['pin']:p for p in cs['A5']['pads']}
  self.assertLess(pads['1']['position'][0],pads['20']['position'][0]);self.assertLess(pads['1']['position'][1],pads['40']['position'][1])
  self.assertEqual(pads['1']['net'],'/A11');self.assertEqual(pads['40']['net'],'/A10')
  polygon=layout['outlinePolygon'];self.assertEqual(len(polygon),4)
  area=abs(sum(x*polygon[(i+1)%4][1]-y*polygon[(i+1)%4][0] for i,(x,y) in enumerate(polygon)))/2
  self.assertEqual(area,270*46)
 def test_unresolved_artwork_is_not_copper(self):
  l=json.loads((R/'generated/layout.json').read_text());self.assertTrue(l['unresolvedArtwork'])
  self.assertTrue(all(x['net'] is None for x in l['unresolvedArtwork']))
  self.assertTrue(all(c['evidence']=='unplaced' for c in l['unplaced']))
 def test_stale_source_and_output_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)/'board';shutil.copytree(R,d,ignore=shutil.ignore_patterns('__pycache__'))
   photos=[source['path'] for source in json.loads((R/'evidence.json').read_text())['sources'] if source.get('path')]
   for photo in photos:
    (d/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,d/photo)
   subprocess.run([sys.executable,d/'tools/export.py','--check'],check=True)
   for name in ['controller.kicad_sch','controller.kicad_pcb','generated/controller.scad']+photos:
    p=d/name;before=p.read_bytes();p.write_bytes(before+b'\n')
    r=subprocess.run([sys.executable,d/'tools/export.py','--check'],capture_output=True)
    self.assertNotEqual(r.returncode,0,name);p.write_bytes(before)
if __name__=='__main__':unittest.main()
