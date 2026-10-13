#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

openscad-nightly \
    -o "$repo_root/keycap/juku-keycap.stl" \
    --export-format binstl \
    "$repo_root/keycap/juku-keycap.scad"

openscad-nightly \
    -o "$repo_root/bottom-case/juku-bottom-case.stl" \
    --export-format binstl \
    "$repo_root/bottom-case/juku-bottom-case.scad"

openscad-nightly \
    -o "$repo_root/top-case/juku-top-case.stl" \
    --export-format binstl \
    "$repo_root/top-case/juku-top-case.scad"

openscad-nightly \
    -o "$repo_root/legs/juku-leg.stl" \
    --export-format binstl \
    "$repo_root/legs/juku-leg.scad"

# 4-part split of the bottom case, for beds smaller than the 340x290 footprint
# (see bottom-case/SPLITTING.md). The one-piece STL above stays canonical.
for part in fl fr bl br; do
    openscad-nightly \
        -o "$repo_root/bottom-case/juku-bottom-case-$part.stl" \
        --export-format binstl \
        -D "split_part=\"$part\"" \
        "$repo_root/bottom-case/juku-bottom-case-split.scad"
done
