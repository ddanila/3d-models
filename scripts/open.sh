#!/usr/bin/env bash
# shellcheck source-path=SCRIPTDIR
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$script_dir/lib.sh"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <model-name|path/to/model.scad>" >&2
    exit 2
fi

if [ -f "$1" ]; then
    scad_file="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
else
    scad_file="$repo_root/models/$1/model.scad"
fi

if [ ! -f "$scad_file" ]; then
    echo "Model not found: $1" >&2
    exit 1
fi

openscad="$(find_openscad)"
exec "$openscad" "$scad_file"
