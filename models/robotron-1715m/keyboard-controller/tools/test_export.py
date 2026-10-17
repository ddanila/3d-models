#!/usr/bin/env python3
"""Fast consistency and handedness checks; no KiCad install required."""
import importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from geometry import arc_points,outline_polygon
from photo_registration import homography,project,rigid_fit,selected_fits,review
R=Path(__file__).resolve().parents[1]
class ControllerExportTests(unittest.TestCase):
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
   photo=json.loads((R/'photo-landmarks.json').read_text())['photo'];(d/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,d/photo)
   bottom=json.loads((R/'bottom-landmarks.json').read_text())['photo'];(d/bottom).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/bottom,d/bottom)
   subprocess.run([sys.executable,d/'tools/export.py','--check'],check=True)
   for name in ['controller.kicad_sch','controller.kicad_pcb','generated/controller.scad']:
    p=d/name;before=p.read_bytes();p.write_bytes(before+b'\n')
    r=subprocess.run([sys.executable,d/'tools/export.py','--check'],capture_output=True)
    self.assertNotEqual(r.returncode,0,name);p.write_bytes(before)
if __name__=='__main__':unittest.main()
