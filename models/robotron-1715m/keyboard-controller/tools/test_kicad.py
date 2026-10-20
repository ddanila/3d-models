#!/usr/bin/env python3
"""Optional integration checks using KiCad's Python; never modify source boards."""
import json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
import pcbnew as pcb
from route_evidence import geometry_sha
from geometry import arc_points
R=Path(__file__).resolve().parents[1]
class KiCadExportTests(unittest.TestCase):
 def test_repeated_native_export_is_byte_identical(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp)/'board';shutil.copytree(R,r,ignore=shutil.ignore_patterns('__pycache__'))
   for source in json.loads((R/'evidence.json').read_text())['sources']:
    if not source.get('path'):continue
    photo=source['path'];(r/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,r/photo)
   def outputs():return {p.name:p.read_bytes()for p in (r/'generated').iterdir()if p.is_file()}
   subprocess.run([sys.executable,r/'tools/export.py'],check=True,stdout=subprocess.DEVNULL)
   first=outputs()
   subprocess.run([sys.executable,r/'tools/export.py'],check=True,stdout=subprocess.DEVNULL)
   second=outputs()
   self.assertEqual(set(first),set(second))
   for name in first:self.assertEqual(first[name],second[name],name+' changed on unchanged native regeneration')
 def test_routing_audit_distinguishes_pad_groups_from_floating_copper(self):
  from routing_audit import build
  b=pcb.LoadBoard(str(R/'controller.kicad_pcb'))
  components=json.loads((R/'generated/connectivity.json').read_text())['components']
  layout=json.loads((R/'generated/layout.json').read_text())
  # An isolated same-net track must not complete a pad link or a net.
  t=pcb.PCB_TRACK(b);t.SetStart(pcb.VECTOR2I(400000000,400000000));t.SetEnd(pcb.VECTOR2I(401000000,400000000));t.SetWidth(300000);t.SetLayer(pcb.F_Cu);t.SetNet(b.FindNet('/GND'));b.Add(t)
  layout['routes'].append({'id':t.m_Uuid.AsString(),'net':'/GND','evidence':{'status':'inferred'}})
  actual=build(b,components,layout,{'unconnected_items':[]})
  expected=json.loads((R/'generated/routing-audit.json').read_text())
  self.assertEqual(actual['summary']['remainingPadGroupLinks'],expected['summary']['remainingPadGroupLinks'])
  self.assertEqual(actual['summary']['fullyConnectedMultiTerminalNets'],expected['summary']['fullyConnectedMultiTerminalNets'])
  self.assertEqual(actual['summary']['floatingCopperGroups'],expected['summary']['floatingCopperGroups']+1)
  ground=next(n for n in actual['nets'] if n['net']=='/GND')
  self.assertTrue(any(set(g['terminals'])=={'R4.2:2','R7:2','R8:2'} for g in ground['islands']))
  # Local supply bridges must merge their intended pads without joining
  # the separate IC groups merely because they share a schematic net.
  for net,pairs in {
   '/+5V': [('A1:14','A2.1:14'),('A2.2:14','A2.3:14')],
   '/GND': [('A1:7','A2.1:7','C5.1:2'),('A2.2:7','A2.3:7','C5.2:2')]
  }.items():
   islands=next(n for n in actual['nets'] if n['net']==net)['islands']
   for pins in pairs:
    self.assertTrue(any(set(pins)<=set(g['terminals']) for g in islands))
   self.assertFalse(any({pairs[0][0],pairs[1][0]}<=set(g['terminals']) for g in islands))
  for net,pins in [('/D0',{'A5:14','A8:9'}),('/D2',{'A5:12','A8:11'})]:
   islands=next(n for n in actual['nets'] if n['net']==net)['islands']
   self.assertTrue(any(pins==set(g['terminals']) for g in islands))
  d1=next(n for n in actual['nets'] if n['net']=='/D1')
  self.assertFalse(any({'A5:15','A8:10'}<=set(g['terminals']) for g in d1['islands']))
  self.assertFalse(any(v['evidence'].get('group')=='cpu-rom-d1' for v in layout['routes']))

 def test_routes_via_and_pin_mismatch(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp)/'board';shutil.copytree(R,r,ignore=shutil.ignore_patterns('__pycache__'))
   for source in json.loads((R/'evidence.json').read_text())['sources']:
    if not source.get('path'):continue
    photo=source['path'];(r/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,r/photo)
   b=pcb.LoadBoard(str(r/'controller.kicad_pcb'));net=b.FindNet('/D0');v=lambda x,y:pcb.VECTOR2I(round(x*1e6),round(y*1e6))
   # Keep synthetic copper clear of the reconstructed board as real routing grows.
   arc=pcb.PCB_ARC(b);arc.SetStart(v(400,400));arc.SetMid(v(405,395));arc.SetEnd(v(410,400));arc.SetWidth(300000);arc.SetLayer(pcb.F_Cu);arc.SetNet(net);b.Add(arc)
   via=pcb.PCB_VIA(b);via.SetPosition(v(400,400));via.SetWidth(1000000);via.SetDrill(400000);via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNet(net);b.Add(via)
   pcb.SaveBoard(str(r/'controller.kicad_pcb'),b)
   result=subprocess.run([sys.executable,r/'tools/export.py'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('exactly the native copper UUIDs',result.stderr)
   items=[{'id':arc.m_Uuid.AsString(),'points':arc_points([250,-350],[255,-345],[260,-350]),'width':.3,'side':'top','net':'/D0'}, {'id':via.m_Uuid.AsString(),'position':[250,-350],'diameter':1.0,'drill':.4,'net':'/D0'}]
   source=json.loads((r/'evidence.json').read_text())['sources'][0]
   ledger={'schema':1,'items':{i['id']:{'status':'inferred','geometrySha256':geometry_sha(i),'detail':'Synthetic integration-test geometry, not historical routing.','sources':[{'id':source['id'],'sha256':source['sha256'],'locator':'D0 reference net; synthetic geometry'}]} for i in items}}
   ledger['items'].update(json.loads((r/'route-evidence.json').read_text())['items'])
   (r/'route-evidence.json').write_text(json.dumps(ledger))
   subprocess.run([sys.executable,r/'tools/export.py'],check=True,stdout=subprocess.DEVNULL)
   l=json.loads((r/'generated/layout.json').read_text());self.assertEqual(len(l['vias']),1);self.assertEqual(l['vias'][0]['position'],[250,-350]);self.assertEqual(l['vias'][0]['drill'],.4)
   points=next(a for a in l['routes']if a['id']==arc.m_Uuid.AsString())['points'];self.assertEqual(points[0],[250,-350]);self.assertEqual(points[-1],[260,-350]);self.assertGreater(max(y for x,y in points),-345.1)
   # A net-name edit must fail even when the resulting native PCB is parseable.
   f=next(f for f in b.GetFootprints() if f.GetReference()=='A1');pad=next(p for p in f.Pads() if p.GetNumber()=='1');pad.SetNet(net);pcb.SaveBoard(str(r/'controller.kicad_pcb'),b)
   result=subprocess.run([sys.executable,r/'tools/export.py'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('pad-net mismatch',result.stderr)
if __name__=='__main__':unittest.main()
