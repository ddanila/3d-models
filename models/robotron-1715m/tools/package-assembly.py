#!/usr/bin/env python3
"""Keep the full-resolution combined STL distributable below GitHub's per-file limit."""
from pathlib import Path
import zipfile,hashlib,json
root=Path(__file__).resolve().parents[1]
stl=root/'robotron-1715m.stl'
with zipfile.ZipFile(root/'robotron-1715m.stl.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    info=zipfile.ZipInfo(stl.name,date_time=(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
    archive.writestr(info,stl.read_bytes())
(root/'assembly-export.json').write_text(json.dumps({'file':'robotron-1715m.stl.zip','member':stl.name,'uncompressedBytes':stl.stat().st_size,'stlSha256':hashlib.sha256(stl.read_bytes()).hexdigest(),'note':'Lossless ZIP of complete visual-reference assembly; standalone component STLs retain direct downloads.'},indent=2)+'\n')
print((root/'robotron-1715m.stl.zip').stat().st_size)
