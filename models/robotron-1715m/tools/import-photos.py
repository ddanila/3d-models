#!/usr/bin/env python3
"""Losslessly strip metadata from extracted owner JPEGs; requires Pillow."""
import argparse
from pathlib import Path
import hashlib,json
from PIL import Image
parser=argparse.ArgumentParser()
parser.add_argument('directory',type=Path,help='Directory of the twelve extracted owner JPEGs')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
records=[]
for source in sorted(args.directory.glob('*.jpg')):
 raw=source.read_bytes();out=bytearray(raw[:2]);pos=2
 while pos<len(raw):
  assert raw[pos]==255
  marker=raw[pos+1]
  if marker==0xda:
   end=raw.index(b'\xff\xd9',pos)+2;out+=raw[pos:end];break
  length=int.from_bytes(raw[pos+2:pos+4],'big');segment=raw[pos:pos+2+length]
  if marker not in (0xe1,0xed,0xfe):out+=segment
  pos+=2+length
 dest=root/'reference/photos'/source.name;dest.write_bytes(out)
 a=Image.open(source);b=Image.open(dest);assert a.tobytes()==b.tobytes()
 records.append(dict(file=source.name,width=a.width,height=a.height,original_sha256=hashlib.sha256(raw).hexdigest(),sha256=hashlib.sha256(out).hexdigest()))
(root/'reference/photos.json').write_text(json.dumps(dict(archive='Photos-1-001 (2).zip',date='2026-10-09',owner='Danila',metadata='EXIF/XMP/IPTC/comments and trailing motion video removed; decoded JPEG pixels verified identical.',photos=records),indent=2)+'\n')
print('Imported',len(records),'pixel-identical photographs; metadata removed')
