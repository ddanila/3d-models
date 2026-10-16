#!/usr/bin/env python3
"""Fast consistency and handedness checks; no KiCad install required."""
import importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from geometry import arc_points,outline_polygon
from photo_registration import homography,project,rigid_fit
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
   if c['ref']!='A4':self.assertLessEqual(c['maxResidualMm'],report['toleranceMm'],c['ref'])
  self.assertFalse(report['withinPhotoTolerance']) # A4 still requires review.
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
   subprocess.run([sys.executable,d/'tools/export.py','--check'],check=True)
   for name in ['controller.kicad_sch','controller.kicad_pcb','generated/controller.scad']:
    p=d/name;before=p.read_bytes();p.write_bytes(before+b'\n')
    r=subprocess.run([sys.executable,d/'tools/export.py','--check'],capture_output=True)
    self.assertNotEqual(r.returncode,0,name);p.write_bytes(before)
if __name__=='__main__':unittest.main()
