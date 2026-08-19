#!/usr/bin/env bash
# shellcheck source-path=SCRIPTDIR
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$script_dir/lib.sh"

require_models || exit 0
openscad="$(find_openscad)"

while IFS= read -r -d '' scad_file; do
    model_dir="$(dirname "$scad_file")"
    model_name="$(model_name_for "$scad_file")"
    output="$model_dir/$model_name.stl"
    echo "Exporting $output"
    "$openscad" -o "$output" --export-format binstl "$scad_file"
done < <(find_models)
