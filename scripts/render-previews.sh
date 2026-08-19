#!/usr/bin/env bash
# shellcheck source-path=SCRIPTDIR
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$script_dir/lib.sh"

require_models || exit 0
openscad="$(find_openscad)"

downscale() {
    local output="$1"
    if command -v sips >/dev/null; then
        sips -z 1200 1600 "$output" >/dev/null
    elif command -v magick >/dev/null; then
        magick "$output" -resize 1600x1200 "$output"
    else
        echo "No image downscaler found; leaving $output at full size" >&2
    fi
}

while IFS= read -r -d '' scad_file; do
    model_dir="$(dirname "$scad_file")"
    model_name="$(model_name_for "$scad_file")"
    output="$model_dir/preview.png"
    echo "Rendering $model_name preview"
    # The single quotes pass OpenSCAD's special $fn variable literally.
    # shellcheck disable=SC2016
    "$openscad" -o "$output" --render --backend Manifold \
        --imgsize=3200,2400 --autocenter --viewall \
        --camera=0,0,0,55,0,25,160 --colorscheme=Monotone \
        -D '$fn=256' "$scad_file"
    downscale "$output"
done < <(find_models)
