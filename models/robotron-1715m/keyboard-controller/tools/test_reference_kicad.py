#!/usr/bin/env python3
"""Check the proposed variant with native KiCad; historical files are read-only inputs."""
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import pcbnew as pcb
import reference_board

ROOT=Path(__file__).resolve().parents[1]
class NativeReferenceTests(unittest.TestCase):
    def test_package_drill_adjustments_preserve_routing_and_terminal_positions(self):
        board=pcb.LoadBoard(str(ROOT/'reference/routing/controller.kicad_pcb'))
        def terminals():
            return {(f.GetReference(),p.GetNumber()):(p.GetPosition().x,p.GetPosition().y,p.GetNetname(),p.GetSize().x,p.GetSize().y) for f in board.GetFootprints() for p in f.Pads()}
        before=terminals();tracks=len(board.GetTracks())
        reference_board.package_adjustments(board,apply=True)
        self.assertEqual(before,terminals());self.assertEqual(tracks,len(board.GetTracks()))
        r1=next(f for f in board.GetFootprints() if f.GetReference()=='R1')
        self.assertTrue(all(p.GetDrillSize().x==1100000 for p in r1.Pads()))
        reference_board.package_adjustments(board)
        next(iter(r1.Pads())).SetDrillSize(pcb.VECTOR2I(800000,800000))
        with self.assertRaisesRegex(ValueError,'Unexpected package drill'):
            reference_board.package_adjustments(board)

    def test_native_connectivity_drc_and_deterministic_exports(self):
        manifest=json.loads((ROOT/'reference/generated/manifest.json').read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'board'
            for name in manifest['sources']:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,target)
            subprocess.run([sys.executable,root/'tools/reference_board.py'],check=True,stdout=subprocess.DEVNULL)
            q=json.loads((root/'reference/generated/qualification.json').read_text())
            self.assertTrue(q['routingComplete'])
            self.assertTrue(q['drcPassed'],q['drc'])
            audit=json.loads((root/'reference/generated/routing-audit.json').read_text())['summary']
            self.assertEqual(audit['remainingPadGroupLinks'],0)
            self.assertEqual(audit['floatingCopperGroups'],0)
            for name in manifest['outputs']:
                self.assertEqual((root/name).read_bytes(),(ROOT/name).read_bytes(),name)
            # A native pin swap must fail even if the exported board still parses.
            path=root/'reference/controller.kicad_pcb'
            board=pcb.LoadBoard(str(path))
            cpu=next(f for f in board.GetFootprints() if f.GetReference()=='A5')
            next(p for p in cpu.Pads() if p.GetNumber()=='1').SetNet(board.FindNet('/GND'))
            pcb.SaveBoard(str(path),board)
            result=subprocess.run([sys.executable,root/'tools/reference_board.py'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('routing receipt',result.stderr)
            # Even a refreshed receipt must not bless a changed electrical net.
            receipt_path=root/'reference/routing-receipt.json'
            receipt=json.loads(receipt_path.read_text())
            receipt['importedBoardSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            receipt_path.write_text(json.dumps(receipt))
            result=subprocess.run([sys.executable,root/'tools/reference_board.py'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('pad-net mismatch',result.stderr)

if __name__=='__main__':unittest.main()
