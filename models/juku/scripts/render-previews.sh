#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Find the OpenSCAD binary (Snap on Linux, app bundle on macOS).
if command -v openscad-nightly >/dev/null; then
    openscad=openscad-nightly
elif command -v openscad >/dev/null; then
    openscad=openscad
elif [ -x /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD ]; then
    openscad=/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
else
    echo "OpenSCAD not found" >&2
    exit 1
fi

# Render at 8x the target size, then downscale to 1600x1200 for antialiasing
# (OpenSCAD's CLI renders without antialiasing).
downscale() {
    local out="$1"
    if command -v sips >/dev/null; then
        sips -z 1200 1600 "$out" >/dev/null
    elif command -v magick >/dev/null; then
        magick "$out" -resize 1600x1200 "$out"
    else
        echo "no downscaler found, leaving $out at full size" >&2
    fi
}

# Use the Manifold backend so coincident/edge-on faces render cleanly
# (the old CGAL backend can leave hairlines on edge-on geometry).
render() {
    local scad_file="$1" out="$2" camera="$3" width="$4" height="$5"
    "$openscad" -o "$out" --render --backend Manifold --imgsize="$width,$height" \
        --autocenter --viewall \
        --camera="$camera" --colorscheme=Monotone -D '$fn=256' "$scad_file"
    downscale "$out"
}

# Like render(), but frames an explicit camera target/distance instead of
# fitting the whole part, for zoomed-in detail shots.
render_zoom() {
    local scad_file="$1" out="$2" camera="$3" width="$4" height="$5"
    "$openscad" -o "$out" --render --backend Manifold --imgsize="$width,$height" \
        --camera="$camera" --colorscheme=Monotone -D '$fn=256' "$scad_file"
    downscale "$out"
}

render \
    "$repo_root/keycap/juku-keycap.scad" \
    "$repo_root/keycap/preview-top.png" \
    0,0,0,55,0,25,140 \
    12800 9600

render \
    "$repo_root/keycap/juku-keycap.scad" \
    "$repo_root/keycap/preview-bottom.png" \
    0,0,0,235,0,205,140 \
    12800 9600

render \
    "$repo_root/bottom-case/juku-bottom-case.scad" \
    "$repo_root/bottom-case/preview.png" \
    0,0,0,55,0,25,160 \
    3200 2400

render \
    "$repo_root/top-case/juku-top-case.scad" \
    "$repo_root/top-case/preview.png" \
    0,0,0,55,0,25,180 \
    3200 2400

render \
    "$repo_root/top-case/juku-top-case.scad" \
    "$repo_root/top-case/preview-bottom.png" \
    0,0,0,235,0,205,180 \
    3200 2400

render \
    "$repo_root/legs/juku-leg.scad" \
    "$repo_root/legs/preview.png" \
    0,0,0,55,0,25,50 \
    3200 2400

# Zoomed underside detail of the recessed logo and serial plate.
render_zoom \
    "$repo_root/bottom-case/juku-bottom-case.scad" \
    "$repo_root/bottom-case/preview-logo.png" \
    170,55,0,235,0,25,210 \
    3200 2400

# Zoomed rear-edge detail showing the PCB guide rails and support
# bosses from inside the case.
render_zoom \
    "$repo_root/bottom-case/juku-bottom-case.scad" \
    "$repo_root/bottom-case/preview-supports.png" \
    325,280,9,60,0,325,136 \
    3200 2400

# 4-part split previews (see bottom-case/SPLITTING.md). Like render(), but with
# a split_part override so each panel - and the exploded overview - is framed
# from the same isometric angle as the one-piece preview.
render_split() {
    local out="$1" part="$2"
    "$openscad" -o "$out" --render --backend Manifold --imgsize=3200,2400 \
        --autocenter --viewall \
        --camera=0,0,0,55,0,25,160 --colorscheme=Monotone \
        -D '$fn=256' -D "split_part=\"$part\"" \
        "$repo_root/bottom-case/juku-bottom-case-split.scad"
    downscale "$out"
}

render_split "$repo_root/bottom-case/preview-split.png" all
for part in fl fr bl br; do
    render_split "$repo_root/bottom-case/preview-split-$part.png" "$part"
done
