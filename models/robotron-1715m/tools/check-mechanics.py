#!/usr/bin/env python3
"""Bounded solid-intersection audit. Not a full kinematic/engineering validation."""
from pathlib import Path
import json,subprocess,tempfile,struct,math
root=Path(__file__).resolve().parents[1]
def volume(path):
    b=path.read_bytes();n=struct.unpack_from('<I',b,80)[0];v=0
    for i in range(n):
        t=struct.unpack_from('<9f',b,84+50*i+12);a=t[:3];c=t[3:6];d=t[6:]
        v+=a[0]*(c[1]*d[2]-c[2]*d[1])+a[1]*(c[2]*d[0]-c[0]*d[2])+a[2]*(c[0]*d[1]-c[1]*d[0])
    return abs(v/6)
results=[]
with tempfile.TemporaryDirectory() as folder:
    folder=Path(folder)
    for track in range(80):
        src=folder/'audit.scad';out=folder/'intersection.stl';out.unlink(missing_ok=True)
        src.write_text(f'include <{root}/model.scad>\nintersection(){{translate([0,{-35*track/79},0])union(){{teac_head();teac_head_metal();}}union(){{teac_frame();teac_mechanism();teac_black();teac_boards();teac_boards(true);teac_components();}}}}\n')
        run=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="audit"','-o',str(out),str(src)],text=True,capture_output=True)
        if run.returncode and 'Current top level object is empty' not in run.stderr:raise RuntimeError(run.stderr)
        v=volume(out) if out.exists() else 0
        results.append(dict(track=track,intersectionVolumeMm3=round(v,6)))
        if v>=.001:print(track,v,flush=True)
report=dict(scope='All 80 emulated head positions against the fixed drive frame, bridge, rails, motor, both board variants and components. Both drives share this mechanism. Intended touching surfaces are permitted; positive solid volume fails. Does not certify full linkage motion or electrical clearances.',results=results,passed=all(r['intersectionVolumeMm3']<.001 for r in results))
(root/'checks/mechanics.json').write_text(json.dumps(report,indent=2)+'\n')
print('Checked',len(results),'track positions; passed:',report['passed'])
if not report['passed']:raise SystemExit('Positive mechanical intersections found')
