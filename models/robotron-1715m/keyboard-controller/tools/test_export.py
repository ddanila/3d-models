#!/usr/bin/env python3
"""Fast consistency and handedness checks; no KiCad install required."""
import importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class ControllerExportTests(unittest.TestCase):
 def test_pinned_sources(self):subprocess.run([sys.executable,R/'tools/export.py','--check'],check=True)
 def test_asymmetric_landmarks(self):
  layout=json.loads((R/'generated/layout.json').read_text());cs={c['ref']:c for c in layout['components']}
  # CPU and ROM are deliberately not interchangeable; pad 1 fixes handedness.
  self.assertEqual(cs['A5']['position'],[62,8]);self.assertEqual(cs['A8']['position'],[114,8])
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
   for name in ['controller.kicad_sch','controller.kicad_pcb','generated/controller.scad']:
    p=d/name;before=p.read_bytes();p.write_bytes(before+b'\n')
    r=subprocess.run([sys.executable,d/'tools/export.py','--check'],capture_output=True)
    self.assertNotEqual(r.returncode,0,name);p.write_bytes(before)
if __name__=='__main__':unittest.main()
