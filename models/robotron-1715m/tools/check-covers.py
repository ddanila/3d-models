#!/usr/bin/env python3
"""Bounded cover interface audit; complements check-assembly.py."""
from pathlib import Path
import json, subprocess, tempfile, struct
root=Path(__file__).resolve().parents[1]
def volume(path):
    b=path.read_bytes(); total=0
    for i in range(struct.unpack_from('<I',b,80)[0]):
        a,bv,c= [struct.unpack_from('<3f',b,84+i*50+12+j*12) for j in range(3)]
        total+=a[0]*(bv[1]*c[2]-bv[2]*c[1])+a[1]*(bv[2]*c[0]-bv[0]*c[2])+a[2]*(bv[0]*c[1]-bv[1]*c[0])
    return abs(total/6)
checks={
 'system-lid-vs-base': ('case_lid();','case_base();'),
 'keyboard-shell-vs-bottom': ('keyboard_shell();','keyboard_bottom();'),
 'monitor-upper-vs-lower': ('shape("monitor-shell-upper");','shape("monitor-shell-lower");'),
}
results=[]
with tempfile.TemporaryDirectory() as tmp:
 for name,(a,b) in checks.items():
    src=Path(tmp)/'check.scad';out=Path(tmp)/'check.stl';out.unlink(missing_ok=True)
    src.write_text(f'include <{root}/model.scad>\nintersection(){{union(){{{a}}}union(){{{b}}}}}')
    run=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="audit"','-o',str(out),str(src)],capture_output=True,text=True)
    if run.returncode and 'Current top level object is empty' not in run.stderr: raise RuntimeError(run.stderr)
    v=volume(out) if out.exists() else 0
    results.append(dict(interface=name,intersectionMm3=round(v,6),passed=v<.001));print(name,round(v,6),flush=True)
report=dict(scope='Static nominal geometry only. Contacts intentionally enter plug bodies; electrical contact force, cable flex, fastener threads, and all unlisted part pairs are outside this audit. Zero volume permits touching surfaces. This is not physical verification.',toleranceMm3=.001,results=results,passed=all(r['passed'] for r in results))
(root/'checks/covers.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:raise SystemExit('Assembly intersections found')
