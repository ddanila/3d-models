#!/usr/bin/env python3
"""Optional integration checks using KiCad's Python; never modify source boards."""
import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
import pcbnew as pcb
from route_evidence import geometry_sha
from geometry import arc_points
R=Path(__file__).resolve().parents[1]
class KiCadExportTests(unittest.TestCase):
 def test_routes_via_and_pin_mismatch(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp)/'board';shutil.copytree(R,r,ignore=shutil.ignore_patterns('__pycache__'))
   photo=json.loads((R/'photo-landmarks.json').read_text())['photo'];(r/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,r/photo)
   bottom=json.loads((R/'bottom-landmarks.json').read_text())['photo'];(r/bottom).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/bottom,r/bottom)
   b=pcb.LoadBoard(str(r/'controller.kicad_pcb'));net=b.FindNet('/D0');v=lambda x,y:pcb.VECTOR2I(round(x*1e6),round(y*1e6))
   arc=pcb.PCB_ARC(b);arc.SetStart(v(100,50));arc.SetMid(v(105,45));arc.SetEnd(v(110,50));arc.SetWidth(300000);arc.SetLayer(pcb.F_Cu);arc.SetNet(net);b.Add(arc)
   via=pcb.PCB_VIA(b);via.SetPosition(v(100,50));via.SetWidth(1000000);via.SetDrill(400000);via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNet(net);b.Add(via)
   pcb.SaveBoard(str(r/'controller.kicad_pcb'),b)
   result=subprocess.run([sys.executable,r/'tools/export.py'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('exactly the native copper UUIDs',result.stderr)
   items=[{'id':arc.m_Uuid.AsString(),'points':arc_points([-50,0],[-45,5],[-40,0]),'width':.3,'side':'top','net':'/D0'}, {'id':via.m_Uuid.AsString(),'position':[-50,0],'diameter':1.0,'drill':.4,'net':'/D0'}]
   source=json.loads((r/'evidence.json').read_text())['sources'][0]
   ledger={'schema':1,'items':{i['id']:{'status':'inferred','geometrySha256':geometry_sha(i),'detail':'Synthetic integration-test geometry, not historical routing.','sources':[{'id':source['id'],'sha256':source['sha256'],'locator':'D0 reference net; synthetic geometry'}]} for i in items}}
   ledger['items'].update(json.loads((r/'route-evidence.json').read_text())['items'])
   (r/'route-evidence.json').write_text(json.dumps(ledger))
   subprocess.run([sys.executable,r/'tools/export.py'],check=True,stdout=subprocess.DEVNULL)
   l=json.loads((r/'generated/layout.json').read_text());self.assertEqual(len(l['vias']),1);self.assertEqual(l['vias'][0]['position'],[-50,0]);self.assertEqual(l['vias'][0]['drill'],.4)
   points=next(a for a in l['routes']if a['id']==arc.m_Uuid.AsString())['points'];self.assertEqual(points[0],[-50,0]);self.assertEqual(points[-1],[-40,0]);self.assertGreater(max(y for x,y in points),4.9)
   # A net-name edit must fail even when the resulting native PCB is parseable.
   f=next(f for f in b.GetFootprints() if f.GetReference()=='A1');pad=next(p for p in f.Pads() if p.GetNumber()=='1');pad.SetNet(net);pcb.SaveBoard(str(r/'controller.kicad_pcb'),b)
   result=subprocess.run([sys.executable,r/'tools/export.py'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('pad-net mismatch',result.stderr)
if __name__=='__main__':unittest.main()
