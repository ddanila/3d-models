# Robotron keyboard spring and rubber-contact switch

Original MIT geometry reconstructed from Danila's spring and exposed switch
photos in `Photos-1-001 (9).zip`, plus the owner's confirmation that a rubber pad
meets paired PCB contact pads, as in a remote control. The loose black keycap is
in [../keycap](../keycap/README.md).

| Part | Export | Evidence |
| --- | --- | --- |
| Free spring | [spring.stl](spring.stl) | Measured OD **13 mm**, free length **23 mm**, wire **0.4 mm** |
| Pale slotted guide | [guide.stl](guide.stl) | Photo `PXL_20261012_190054608.jpg`; dimensions estimated |
| Black mounting flange | [mount.stl](mount.stl) | Same photo; corner fixing holes, circular opening |
| Insulating moving carrier | [carrier.stl](carrier.stl) | Visible retaining features; hidden shape estimated |
| Rubber contact pad | [rubber.stl](rubber.stl) | Owner confirms rubber contact principle; 7.8 × 0.8 mm estimated |
| Paired PCB electrodes | [contacts.stl](contacts.stl) | Owner confirms paired pads; comb geometry illustrative |

[Editable OpenSCAD](model.scad) · [Shared geometry](geometry.scad) · [Mesh audit](mesh-check.json)

The spring has a 12.6 mm mean diameter and 12.2 mm inner diameter. Five active
turns and three close turns at each end follow the photograph, not a measured
turn count. End pitch is 0.405 mm to keep a closed, non-self-intersecting export;
end grinding, stiffness and wire material are not established. The STL represents
the metal spring geometry; it does not assert that a printed plastic spring will
behave the same way.

The museum uses a provisional 19.6 mm installed height and 2.2 mm travel, chosen
to seat the spring in the reconstructed cap recess and let the rubber meet the
PCB at full travel. The spring changes length during key presses; the rubber and
insulating carrier move together. In the inspection view, the spring relaxes to
23 mm and the carrier lifts separately so its rubber underside can be inspected.
The PCB opens contact-face up. Orbit below it for the solder/trace side.

The contacts STL contains **two separate conductive electrodes**, not one joined
solid. Hidden switch geometry and contact chemistry remain unverified. Separate
STLs are oriented with their lowest point at Z=0; `model.scad` can display the
assembly for reference. All small fit dimensions are editable estimates.

```sh
openscad --backend Manifold --export-format binstl -D 'part="spring"' -o spring.stl model.scad
python3 ../tools/check-key-parts.py
```
