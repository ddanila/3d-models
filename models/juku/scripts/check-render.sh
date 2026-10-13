#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d "$repo_root/.render-check.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

openscad-nightly \
    -o "$tmp_dir/juku-keycap.stl" \
    "$repo_root/keycap/juku-keycap.scad"

openscad-nightly \
    -o "$tmp_dir/juku-bottom-case.stl" \
    "$repo_root/bottom-case/juku-bottom-case.scad"

openscad-nightly \
    -o "$tmp_dir/juku-bottom-case-split.stl" \
    "$repo_root/bottom-case/juku-bottom-case-split.scad"

openscad-nightly \
    -o "$tmp_dir/juku-leg.stl" \
    "$repo_root/legs/juku-leg.scad"

openscad-nightly \
    -o "$tmp_dir/juku-bottom-with-legs.stl" \
    "$repo_root/assembly/juku-bottom-with-legs.scad"
