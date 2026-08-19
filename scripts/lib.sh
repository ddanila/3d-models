#!/usr/bin/env bash

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find_openscad() {
    if command -v openscad-nightly >/dev/null; then
        command -v openscad-nightly
    elif command -v openscad >/dev/null; then
        command -v openscad
    elif [ -x /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD ]; then
        printf '%s\n' /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
    else
        echo "OpenSCAD not found (tried openscad-nightly, openscad, and the macOS app)" >&2
        return 1
    fi
}

find_models() {
    find "$repo_root/models" -mindepth 2 -maxdepth 2 -type f \
        -name model.scad -print0 | sort -z
}

require_models() {
    if ! find "$repo_root/models" -mindepth 2 -maxdepth 2 -type f \
        -name model.scad -print -quit | grep -q .; then
        echo "No models found; add models/<name>/model.scad" >&2
        return 1
    fi
}

model_name_for() {
    basename "$(dirname "$1")"
}
