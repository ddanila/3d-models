# Robotron keycap spring winding mandrel

Printable hand-winding **trial mandrel** (Russian: оправка) for the spring
documented in the [keyboard measurements](../README.md#keycap-spring-measurements-2026-10-10).
[Editable model](model.scad) · [Printable STL](keycap-spring-mandrel.stl) · [Preview](preview.png)

## Diameter estimate

Assume the reported 13 mm is the **outside diameter**, with 0.35 mm round
hardened music/piano wire. The desired inside diameter is then 12.30 mm and
the mean coil diameter is 12.65 mm. Wire material/temper has not been confirmed.

[Daycounter's mandrel calculator](https://www.daycounter.com/Calculators/Springs/)
publishes the Hiraoka empirical relation (referencing *Home Shop Machinist*,
May/June and July/August 1987):

```text
D = finished outside diameter - wire diameter = 12.65 mm
C = D / wire diameter = 36.14
k = 0.98425 - 0.01245 * C = 0.53427
mandrel diameter = k * D - wire diameter = 6.4085 mm
```

The model rounds this to **6.4 mm**, strictly as a first experiment.
This spring's index of about 36 is far beyond the range where this linear
relation should be trusted. [Krexil's own winding measurements and discussion](https://krexil.com/spring-mandrel-size-k-values/)
recommend measuring springback above an index of about 18; their highest-index
reported example is about 24.5. They do not validate this 6.4 mm result.
Material, temper and winding tension can change the required diameter.
The photographs alone cannot establish an exact mandrel size. This tool has
not yet been printed or used to wind a spring.

## Tool and printing

- Smooth 6.4 mm shaft with 35 mm straight working length and a 0.6 mm tip bevel.
- Hexagonal hand grip: 28 mm across corners, 6 mm thick; total height 41.6 mm.
- A 1.2 mm vertical hole in the grip holds the starting wire tail under a finger
  or a small external clamp. It is an anchor point, not a self-locking clamp.
- Raised diameter label on the grip. The spring slides off the unobstructed tip.

Print upright with the broad grip on the bed, at 0.12–0.16 mm layers, with
enough perimeters to make the shaft solid. No supports are required by the
geometry. PLA is a reasonable first trial material for this thin wire.
Remove seam bumps and measure the actual shaft diameter before winding.
Use by hand; no powered-drive interface or heat-treatment capability is provided.
Wear eye protection while handling tensioned spring wire.

## Calibrate before making the full spring

Wind a few close turns of the actual wire, release the tension carefully,
remove the sample and measure its relaxed outside diameter. Use the printed
shaft's measured diameter, not just its nominal size:

```text
measured_k = (actual_mandrel_diameter + wire_diameter)
             / (sample_outside_diameter - wire_diameter)
next_mandrel_diameter = measured_k * (13 - wire_diameter) - wire_diameter
```

This is a local correction, not an exact material constant: repeat if the
first sample is far from the target. Set `mandrel_diameter` in `model.scad`
and export again. If 13 mm meant the inside diameter instead, the target OD
in these calculations must be changed to 13.7 mm for 0.35 mm wire.

The 23 mm free spring length and photographed end windings guide later
forming; they do not set the shaft diameter. A smooth shaft deliberately
leaves pitch adjustable. The original shows roughly five open turns and
close-wound ends, but its exact total winding count is unconfirmed.
Wound turns also unwind on release, so the number of tool revolutions is
not necessarily the finished turn count. Check the relaxed spring against
the photo and keyboard before making more. No pitch or turn-count fixture
is claimed by this model.

## Export

From this directory:

```sh
openscad-nightly --backend CGAL --export-format binstl \
  -o keycap-spring-mandrel.stl model.scad
```
