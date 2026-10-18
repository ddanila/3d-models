// Detailed museum controller assembly, using the current shared model geometry.
// Open in OpenSCAD and press F5, then Home to fit the board.
// Dimensions, unplaced components and unresolved artwork remain estimates;
// see README.md and evidence.json for qualification and specimen provenance.
include <../model.scad>

// Suppress the full computer assembly emitted by model.scad.
part="controller-review";
side="top"; // [top,bottom]
show_mounts=false;
show_shield=false;
$fn=24;
controller_parts=[
    "keyboard-controller-board", "keyboard-controller-chips",
    "keyboard-controller-ceramic", "keyboard-controller-rom-cover",
    "keyboard-controller-connectors", "keyboard-controller-networks", "keyboard-controller-caps",
    "keyboard-controller-metal", "keyboard-controller-ink",
    "keyboard-controller-traces", "keyboard-controller-solder",
    "keyboard-controller-leads", "keyboard-controller-resistors",
    "keyboard-controller-resistor-bands", "keyboard-controller-rom-ink",
    "keyboard-controller-mounts", "keyboard-controller-shield"
];

rotate(side=="bottom"?[180,0,0]:[0,0,0])
translate([-keyboard_controller_x,-keyboard_y-keyboard_controller_y,-keyboard_controller_z])
for(i=[0:len(parts)-1])
    if(len([for(p=controller_parts)if(p==parts[i])p])>0)
        if((show_mounts || parts[i]!="keyboard-controller-mounts") &&
           (show_shield || parts[i]!="keyboard-controller-shield"))
            color(colors[i]) shape(parts[i]);
