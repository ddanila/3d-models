# Stackable DIP-28 chip tray

A stackable storage tray for four parallel DIP-28 memory chips in a single row.
It is sized for both plastic AT28C64B EEPROMs and the larger ceramic, windowed
2764-family EPROM package.

Each chip lies in its own pocket. A raised island supports the package body so
the leads do not carry its weight, and a 10 mm hole lets the chip be pushed out
from below. Four external corner pads carry matching conical pegs and sockets
that locate the stack without entering the chip pockets. There is no separate
lid.

## Dimensions

The storage envelope uses the larger ceramic package as the limiting case:

| Parameter | Value |
| --- | ---: |
| Chip envelope | 38.10 × 18.32 × 5.71 mm |
| Clearance around chip | 0.60 mm per side |
| Clearance above chip | 2.80 mm |
| Capacity | 4 chips (1 × 4) |
| Main tray / overall footprint | 84.88 × 42.50 / 93.97 × 51.59 mm |
| Tray body / total height | 11.31 / 14.31 mm |
| Outer wall / dividers | 1.60 / 1.20 mm |
| Conical locator height | 3.00 mm |
| Peg / socket opening diameter | 4.00 / 4.50 mm |
| Stacking fit clearance | 0.25 mm |

Package sources:

- [Microchip AT28C64B package drawing](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0270.pdf)
- [ST FDIP28W ceramic package drawing](https://community.st.com/ysqtg83639/attachments/ysqtg83639/mems-sensors-forum/7357/1/M27128A_NOV2000.pdf)

The 2764 is an EPROM rather than an EEPROM. Package dimensions vary slightly
by manufacturer, so compare unusually old or nonstandard parts with the source
parameters in `dimensions.scad` before printing many trays.

## Printing

Print the tray flat as modeled. No supports are needed: the four underside
sockets narrow continuously to a point instead of ending in flat ceilings.
With a 0.4 mm nozzle, the 1.6 mm perimeter is four extrusion lines wide and
the 1.2 mm dividers are three. A small test print is sensible before making a
full stack because printer calibration and filament shrinkage affect the cone
fit.

Ordinary PLA/PETG is not ESD-safe. Do not rely on loose household aluminium
foil as the pocket liner: it can snag the leads and is not controlled
static-dissipative packaging. The simplest upgrade is to put the complete
loaded tray in a proper metallized ESD shielding bag. If the pins should remain
at the same potential, use purpose-made, noncorrosive conductive foam and adapt
the pocket depth to its thickness.

NASA's component-storage guidance specifically calls for PROMs in shielding
tubes or approved foam and shielding bags, and for temporarily staged IC leads
to be inserted into conductive foam:
[Electrostatic Discharge Control in GSE](https://extapps.ksc.nasa.gov/reliability/Documents/Preferred_Practices/3008ksc.pdf).

From the repository root:

```bash
./scripts/open.sh dip28-chip-tray
./scripts/check-render.sh
./scripts/export-stls.sh
./scripts/render-previews.sh
```

Generated printable part: `dip28-chip-tray.stl`.
