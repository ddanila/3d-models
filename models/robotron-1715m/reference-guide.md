# Robotron source interpretation

Use the [evidence manifest](evidence.json), [photo inventories](reference/) and
component-specific guides for source records. This page retains distinctions that
matter when interpreting the reconstruction; dimensions and inventories already
encoded in source belong there.

## Specimen and family references

The [family manual](https://xepb.org/robotron/docs/pc_manu.pdf#page=36), printed p.35,
gives nominal system, display and keyboard envelopes. These are family dimensions,
not measurements of the museum specimen. The display envelope includes its stand.
Owner-confirmed sheet construction and keyboard measurements are distinguished
from photo estimates in the [keyboard guide](keyboard/README.md).

The ruler photograph `PXL_20261009_132938614.jpg` provides a rough independent
keyboard scale. In the reviewed 1824 × 1373 image, ruler ticks 200 and 100 mm lie
approximately at x=405 and x=1380; six key intervals span approximately 1172 pixels.
This supports roughly 20 mm pitch, with about ±1 mm uncertainty from hand-picking,
perspective and differing ruler/key heights. It is not submillimetre metrology.

The [W drawings](https://xepb.org/robotron/docs/1715w.zip) distinguish the integrated
U8272 floppy controller on the W/M motherboard from the separate controller in the
original 1715. Owner photo `PXL_20261013_150334561.jpg` appears to show marking
`1.93.310402.6 1L2` on the rear, solder-side-up display board. This does not establish
an exact match to the available `1.93.310412.6` CRT drawing. Brown drive boards
marked `05-330-0024` are connector adapters, not the floppy controller.
[Board layout](board-layout.json) owns current component and placement evidence.

The controller [evidence ledger](keyboard-controller/evidence.json) separates
published revisions, primary photographs and comparison specimens. Its museum
EPROM was transplanted and remains unread; package appearance and comparison ROM
labels cannot identify its contents. Use standard S600 only as reference firmware.

## Mechanical references

Owner drive photographs `PXL_20250212_094033966.jpg` and
`PXL_20250212_094038758.jpg` establish visible construction and different drive
labels; [drive-labels.json](drive-labels.json) retains transcriptions and locators.
They do not establish that both drives are TEAC FD-55FV-13. The
[TEAC specification](https://retrocmp.de/fdd/teac/TEAC_FD55-FV.pdf) supplies reference
body dimensions (printed pp.101–103) and head radii/track pitch (p.108). Linkage
shapes, resting poses and dynamic response remain estimates.

[Robotrontechnik's K7222.25 photographs](https://www.robotrontechnik.de/html/zubehoer/bildschirme.htm#k7222-25)
support comparative monitor internals; the exact tube and electronics in this
specimen remain unidentified. [Oldcrap's PC1715](https://oldcrap.org/2017/12/26/robotron-1715/)
and [MCbx's collection](https://oldcomputer.info/8bit/robo1715/index.htm) show other
machines. Archived board references retain credits in
[comparative-1715-boards.json](reference/comparative-1715-boards.json).

Current owner spring measurements and rubber-contact evidence live in the
[switch guide](key-switch/README.md); they supersede the earlier approximate wire
measurement. The [mandrel experiment](keycap-spring-mandrel/README.md) remains an
unvalidated tooling experiment, not a fit-qualified part.

## Import photographs

Use `python3 tools/import-photos.py /path/to/photos --append --source 'Source description'`
from this model directory (Pillow required). Keep original archives unchanged.
Inventories retain original/published hashes; published JPEGs have private metadata
removed losslessly, with decoded pixels checked. Distinguish specimens and preserve
third-party notices. Full-panel photo skins and clean geometry are different kinds
of representation; small documentary label crops retain their original source.
