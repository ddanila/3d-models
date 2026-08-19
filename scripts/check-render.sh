#!/usr/bin/env bash
# shellcheck source-path=SCRIPTDIR
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$script_dir/lib.sh"

require_models || exit 0
openscad="$(find_openscad)"

tmp_dir="$(mktemp -d "$repo_root/.render-check.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

while IFS= read -r -d '' scad_file; do
    printable_name="$(printable_name_for "$scad_file")"
    echo "Checking $printable_name"
    "$openscad" -o "$tmp_dir/$printable_name.stl" "$scad_file"
done < <(find_printables)
