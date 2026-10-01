#!/usr/bin/env python3
"""Validate the supplied FAAD PS patch evidence, including delayed PS activation."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_faad_ps_patch as probe
EVIDENCE=ROOT/'tests/results/faad2-ps-patch-20261001'


class FaadPsPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((EVIDENCE/'comparison.json').read_text())

    def test_complete_matrix_and_source_provenance(self):
        rows=self.data['rows']
        self.assertEqual(len(rows),11)
        self.assertEqual(len({r['input'] for r in rows}),11)
        self.assertEqual(probe.digest(probe.PATCH),self.data['patch_sha256'])
        self.assertEqual(self.data['patch_sha256'],probe.PATCH_SHA256)
        self.assertEqual(probe.digest(probe.PROBE),self.data['probe_sha256'])
        for row in rows:
            for mode,saved in row['runs'].items():
                raw=json.loads((EVIDENCE/f"{row['input']}-{mode}.log").read_text())
                for key,value in raw.items():self.assertEqual(value,saved[key])
                frames=EVIDENCE/f"{row['input']}-{mode}.frames"
                self.assertEqual(probe.digest(frames),saved['frames_sha256'])
                parsed=[list(map(int,l.split())) for l in frames.read_text().splitlines()]
                self.assertEqual(len(parsed),saved['frames'])
                self.assertEqual(sum(f[1] for f in parsed),saved['samples'])
                self.assertEqual(sum(f[5] for f in parsed),saved['ps_frames'])

    def test_disabled_patch_is_exact_and_frame_shapes_match(self):
        for row in self.data['rows']:
            runs=row['runs']
            self.assertEqual(runs['baseline']['pcm_sha256'],runs['disabled']['pcm_sha256'])
            self.assertEqual(len({r['frames_sha256'] for r in runs.values()}),1)
            self.assertEqual(runs['baseline']['ps_info_bytes']-runs['packed']['ps_info_bytes'],9600)
            self.assertEqual(runs['packed']['quantizer_equivalence_cases'],100000)

    def test_ps_precision_and_inactive_controls(self):
        for row in self.data['rows']:
            active=row['input'] in ('abba64','hev2-44100-stereo')
            self.assertEqual(row['runs']['packed']['ps_frames']>0,active)
            self.assertEqual(max(c['maximum'] for c in row['channels']),2 if active else 0)
            for c in row['channels']:
                h={int(k):v for k,v in c['histogram'].items()}
                self.assertEqual(sum(h.values()),c['samples'])
                self.assertEqual(max(h),c['maximum'])
                self.assertEqual(sum(k*k*v for k,v in h.items()),c['square_error'])
                self.assertEqual(c['over_two'],0)
                self.assertEqual(c['over_five'],0)
                self.assertAlmostEqual(c['rms_lsb'],math.sqrt(c['square_error']/c['samples']))
            self.assertEqual(sum(c['samples'] for c in row['channels']),row['runs']['packed']['samples'])
            if not active:self.assertEqual(row['runs']['baseline']['pcm_sha256'],row['runs']['packed']['pcm_sha256'])

    def test_delayed_ps_activation_is_preserved(self):
        row=next(r for r in self.data['rows'] if r['input']=='abba64')
        self.assertEqual(row['output_layouts'],[[44100,1],[44100,2]])
        self.assertEqual(row['runs']['packed']['ps_frames'],635)
        self.assertEqual([c['samples'] for c in row['channels']],[1320960,1300480])

    def test_framewise_channel_assignment_on_layout_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            a,b=Path(directory)/'a.pcm',Path(directory)/'b.pcm'
            values=array('h',[10,20,30,40,50,60]); changed=array('h',[11,20,30,42,50,63])
            if sys.byteorder!='little':values.byteswap();changed.byteswap()
            a.write_bytes(values.tobytes());b.write_bytes(changed.tobytes())
            rows=probe.compare_pcm(a,b,[[7,2,44100,1,1,0],[7,4,44100,2,1,1]])
            self.assertEqual([r['samples'] for r in rows],[4,2])
            self.assertEqual([r['square_error'] for r in rows],[1,13])
            self.assertEqual(rows[1]['over_two'],1)
            with self.assertRaises(ValueError):probe.compare_pcm(a,b,[[7,2,44100,1,1,0]])

    def test_full_output_rate_and_channel_layouts(self):
        for row in self.data['rows']:
            name=row['input']
            if name=='abba64':continue
            # FAAD's default implicit-SBR policy also upsamples low-rate AAC-LC.
            rate=32000 if name=='groovesalad16' else 48000 if '48000' in name else 44100
            channels=1 if name in ('groovesalad16','lc-22050-mono') else 2
            self.assertEqual(row['output_layouts'],[[rate,channels]])
            if name=='lc-22050-mono':
                self.assertEqual(row['runs']['packed']['sbr_frames'],0)
                self.assertGreater(row['runs']['packed']['upsampled_core_frames'],0)


if __name__=='__main__':unittest.main()
