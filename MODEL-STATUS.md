# Physical print verification

This distinction is independent of visual review, render checks and valid STL geometry.

| Model / part | Physical status |
| --- | --- |
| [dip28-chip-tray/model.scad](models/dip28-chip-tray/model.scad) | Not physically verified |
| [oral-b-five-brush-stand/model.scad](models/oral-b-five-brush-stand/model.scad) | **Printed and verified** |
| [pk8010-korvet/pk8010-korvet-button/model.scad](models/pk8010-korvet/pk8010-korvet-button/model.scad) | **Printed and verified** |
| [pk8010-korvet/pk8010-korvet-keycap/model.scad](models/pk8010-korvet/pk8010-korvet-keycap/model.scad) | **Printed and verified** |
| [pk8010-korvet/pk8010-korvet-keycap/part-fit-minus-0-2.scad](models/pk8010-korvet/pk8010-korvet-keycap/part-fit-minus-0-2.scad) | Not physically verified |
| [pk8010-korvet/pk8010-korvet-shift-keycap/model.scad](models/pk8010-korvet/pk8010-korvet-shift-keycap/model.scad) | Not physically verified |
| [pk8010-korvet/pk8010-korvet-shift-keycap/part-fit-minus-0-2.scad](models/pk8010-korvet/pk8010-korvet-shift-keycap/part-fit-minus-0-2.scad) | Not physically verified |
| [pk8010-korvet/pk8010-korvet-side-lid/model.scad](models/pk8010-korvet/pk8010-korvet-side-lid/model.scad) | **Printed and verified** |
| [rg1n-loopback-case/model.scad](models/rg1n-loopback-case/model.scad) | **Printed and verified** |
| [rg1n-loopback-case/part-lid.scad](models/rg1n-loopback-case/part-lid.scad) | **Printed and verified** |
| [robotron-1715m/display-base-ring/model.scad](models/robotron-1715m/display-base-ring/model.scad) | Not physically verified |
| [robotron-1715m/key-switch/model.scad](models/robotron-1715m/key-switch/model.scad) | Not physically verified |
| [robotron-1715m/keyboard/model.scad](models/robotron-1715m/keyboard/model.scad) | Not physically verified |
| [robotron-1715m/keycap/model.scad](models/robotron-1715m/keycap/model.scad) | Not physically verified |
| [robotron-1715m/keycap-spring-mandrel/model.scad](models/robotron-1715m/keycap-spring-mandrel/model.scad) | Not physically verified |
| [robotron-1715m/model.scad](models/robotron-1715m/model.scad) | Not physically verified |
| [usb-serial-adapter-case/model.scad](models/usb-serial-adapter-case/model.scad) | **Printed and verified** |
| [usb-serial-adapter-case/part-lid.scad](models/usb-serial-adapter-case/part-lid.scad) | **Printed and verified** |
| [juku/keycap/model.scad](models/juku/keycap/model.scad) | **Printed and verified** |
| [juku/bottom-case/model.scad](models/juku/bottom-case/model.scad) | Not physically verified |
| [juku/bottom-case/part-bl.scad](models/juku/bottom-case/part-bl.scad) | Not physically verified |
| [juku/bottom-case/part-br.scad](models/juku/bottom-case/part-br.scad) | Not physically verified |
| [juku/bottom-case/part-fl.scad](models/juku/bottom-case/part-fl.scad) | Not physically verified |
| [juku/bottom-case/part-fr.scad](models/juku/bottom-case/part-fr.scad) | Not physically verified |
| [juku/legs/model.scad](models/juku/legs/model.scad) | Not physically verified |
| [juku/top-case/model.scad](models/juku/top-case/model.scad) | Not physically verified |

“Not physically verified” means no recorded confirmation for this version; it does not claim nobody has printed it.

To promote a part, record who printed and checked it, the date, fit/function result, and SHA-256 hashes of the exact tested files in `model-status.json`. A changed verified file must be rechecked or returned to unverified. Sibling parts do not inherit verification.

Run `python3 scripts/model-status.py` after adding models or recording evidence. CAD remains canonical; downstream museum exports carry this status rather than inventing their own.
