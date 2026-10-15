#!/usr/bin/env python3
"""Small, repeatable solid-clearance audit of selected assembly interfaces."""
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
 'controller-resistors-vs-components': ('keyboard_controller_resistors();','union(){keyboard_controller_chips();keyboard_controller_caps();keyboard_controller_connectors();}'),
 'plug-springs-vs-housing': ('plug_screws();','cable_plug();'),
 'controller-shield-vs-components': ('keyboard_controller_shield();','union(){keyboard_controller_chips();keyboard_controller_caps();}'),
 'controller-mounts-vs-board': ('keyboard_controller_mounts();','keyboard_controller_board();'),
 'controller-mounts-vs-matrix': ('keyboard_controller_mounts();','keyboard_pcb();'),
 'controller-shield-vs-board': ('keyboard_controller_shield();','keyboard_controller_board();'),
 'ic-sockets-vs-chip-plastic': ('logic_ic_sockets();','logic_chips();'),
 'ic-sockets-vs-chip-leads': ('logic_ic_sockets();','logic_pins();'),
 'ic-socket-contacts-vs-board': ('logic_ic_contacts();','logic_boards();'),
 'board-connectors-vs-chip-bodies': ('logic_connectors();','logic_chips();'),
 'motherboard-ribbon-plug-vs-chip-bodies': ('logic_ribbon_plug();','logic_chips();'),
 'motherboard-ribbon-plug-vs-socket': ('logic_ribbon_plug();','logic_connectors();'),
 'keyboard-discrete-leads-vs-board': ('keyboard_controller_leads();','keyboard_controller_board();'),
 'keyboard-imported-leads-vs-board': ('keyboard_controller_pose()for(p=concat(controller_dips,[[114,8,24,15.24]]))owner_dip_pins(p);','keyboard_controller_board();'),
 'keyboard-cable-vs-chip-bodies': ('keyboard_internal_cable();','keyboard_controller_chips();'),
 'keyboard-chips-vs-caps': ('keyboard_controller_chips();','keyboard_controller_caps();'),
 'keyboard-transistor-lead-holes': ('keyboard_controller_pose()for(p=controller_transistors)controller_transistor_pose(p)for(x=[-1.27,0,1.27])translate([x,0,-1.6])cylinder(d=.6,h=1.6,$fn=12);','keyboard_controller_board();'),
 'matrix-socket-vs-board': ('keyboard_matrix_socket();','keyboard_pcb();'),
 'matrix-socket-vs-controller-connector': ('keyboard_matrix_socket();','keyboard_controller_connectors();'),
 'keyboard-controller-vs-matrix-board': ('union(){keyboard_controller_chips();keyboard_controller_caps();keyboard_controller_ceramic();keyboard_controller_connectors();}','keyboard_pcb();'),
 'keyboard-entry-rubber-vs-lid': ('keyboard_entry_rubber();','keyboard_bottom();'),
 'matrix-socket-vs-controller': ('keyboard_matrix_socket();','keyboard_controller_board();'),
 'keyboard-guide-vs-moving-carrier-rest': ('switch_guide();','translate([0,0,11.3])contact_carrier();'),
 'keyboard-guide-vs-moving-carrier-pressed': ('switch_guide();','translate([0,0,9.1])contact_carrier();'),
 'ribbon-plugs-vs-socket-plastic': ('drive_ribbon_plugs();','drive_adapter_sockets();'),
 'ribbon-plugs-vs-adapter-board': ('drive_ribbon_plugs();','drive_adapter_boards();'),
 'fan-rotor-vs-frame': ('fan_rotor();','fan_frame();'),
 'fan-airway-vs-psu-wall': ('translate([93,109,67])rotate([0,90,0])cylinder(d=77,h=4,$fn=48);','psu_chassis();'),
 'board-mounts-vs-chip-bodies': ('logic_mounts();','logic_chips();'),
 'keyboard-open-end-holes-vs-components': ('keyboard_controller_pose()for(p=controller_end_holes)translate(concat(p,[0]))cylinder(d=3.2,h=12,$fn=24);','union(){keyboard_controller_chips();keyboard_controller_caps();keyboard_controller_ceramic();}'),
 'board-mounting-hole-clearance': ('for(p=pcb_mounts)translate([p[0],p[1],p[3]-1.6])cylinder(d=3,h=1.6,$fn=20);','logic_boards();'),
 'drive-rotors-vs-carrier': ('for(x=[-231,-77])translate([x,-203,60])teac_spindle();','drive_bracket();'),
 'lever-open-vs-inserted-diskette': ('drive_latches(0);','translate([-231,-203,60])teac_diskette_jacket();'),
 'lever-closed-vs-inserted-diskette': ('translate([-113,-211,92])rotate([0,90,0])translate([113,211,-92])drive_latches(0);','translate([-231,-203,60])teac_diskette_jacket();'),
 'keyboard-cable-vs-controller-board': ('keyboard_internal_cable();','keyboard_controller_board();'),
 'keyboard-cable-vs-shield-clamp': ('keyboard_internal_cable();','keyboard_controller_metal();'),
 'cable-grommet-vs-sheet-support': ('keyboard_grommet();','keyboard_cable_support();'),
 'board-vs-drive-bracket': ('logic_boards();','drive_bracket();'),
 'board-vs-psu-shield': ('logic_boards();','psu_chassis();'),
 'new-resistors-vs-chip-bodies': ('logic_discretes("logic-resistors");','logic_chips();'),
 'bypass-caps-vs-chip-bodies': ('logic_discretes("logic-ceramics");','logic_chips();'),
 'film-caps-vs-chip-bodies': ('logic_discretes("logic-film");','logic_chips();'),
 'electrolytic-caps-vs-chip-bodies': ('logic_discretes("logic-electrolytics");','logic_chips();'),
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
(root/'checks/assembly.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['passed']:raise SystemExit('Assembly intersections found')
