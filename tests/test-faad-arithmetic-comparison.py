#!/usr/bin/env python3
"""Validate measured float/fixed differences, preserving large discrepancies."""
from array import array
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_faad_arithmetic_comparison as probe
EVIDENCE = ROOT/'tests/results/faad2-arithmetic-20261001'


class FaadArithmeticComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((EVIDENCE/'comparison.json').read_text())
        cls.rows = {r['input']:r for r in cls.data['rows']}

    def test_pinned_sources_and_only_arithmetic_build_difference(self):
        self.assertEqual(len(self.rows), 11)
        self.assertEqual(self.data['source_revision'], probe.REVISION)
        self.assertEqual(self.data['source_archive_sha256'], probe.ARCHIVE_SHA256)
        for path,key in ((probe.PROBE,'probe_sha256'), (Path(probe.__file__),'runner_sha256'),
                         (ROOT/'tools/codec_benchmark/run_faad_ps_patch.py','comparator_sha256')):
            self.assertEqual(probe.digest(path), self.data[key])
        floating = self.data['build_commands']['float'][:-2]
        fixed = self.data['build_commands']['fixed'][:-2]
        fixed.remove('-DFIXED_POINT=1')
        self.assertEqual(floating, fixed)
        self.assertNotIn('-ffast-math', floating)
        for name,row in self.rows.items():
            fixture = ROOT/f'tests/fixtures/aac_stream_format/{name}.aac'
            if fixture.exists():self.assertEqual(probe.digest(fixture), row['input_sha256'])

    def test_logs_shapes_state_and_repeatability(self):
        for name,row in self.rows.items():
            self.assertEqual(row['runs']['float']['arithmetic'], 'float32')
            self.assertEqual(row['runs']['fixed']['arithmetic'], 'fixed')
            for mode,saved in row['runs'].items():
                self.assertEqual(saved['real_bytes'], 4)
                raw = json.loads((EVIDENCE/f'{name}-{mode}.log').read_text())
                for key,value in raw.items():self.assertEqual(value, saved[key])
                for key,value in saved['repeat_hashes'].items():self.assertEqual(value,saved[key])
                for suffix in ('frames', 'state'):
                    self.assertEqual(probe.digest(EVIDENCE/f'{name}-{mode}.{suffix}'), saved[f'{suffix}_sha256'])
                frames = [list(map(int,l.split())) for l in (EVIDENCE/f'{name}-{mode}.frames').read_text().splitlines()]
                self.assertEqual(len(frames), saved['frames'])
                self.assertEqual(sum(f[1] for f in frames), saved['samples'])
                self.assertEqual(sum(f[5] for f in frames), saved['ps_frames'])
                self.assertEqual(sum(f[4] in (1,2) for f in frames), saved['sbr_frames'])
                self.assertEqual(sum(f[4] == 3 for f in frames), saved['upsampled_core_frames'])
                self.assertEqual([list(x) for x in sorted({(f[2],f[3]) for f in frames if f[1]})],row['output_layouts'])
            for kind in ('frames', 'state'):
                self.assertEqual(row['runs']['float'][f'{kind}_sha256'],row['runs']['fixed'][f'{kind}_sha256'])

    def test_fixed_baseline_matches_previous_independent_probe(self):
        prior = json.loads((ROOT/'tests/results/faad2-ps-patch-20261001/comparison.json').read_text())
        for row in prior['rows']:
            self.assertEqual(self.rows[row['input']]['runs']['fixed']['pcm_sha256'],
                             row['runs']['baseline']['pcm_sha256'])

    def test_integer_moments_histograms_and_frame_errors(self):
        for name,row in self.rows.items():
            self.assertEqual(probe.summarize(row['channels']),row['total'])
            self.assertEqual(row['total']['samples'],row['runs']['float']['samples'])
            for ch in row['channels']:
                hist = {int(k):v for k,v in ch['histogram'].items()}
                self.assertEqual(sum(hist.values()),ch['samples'])
                self.assertEqual(sum(k*k*v for k,v in hist.items()),ch['square_error'])
                self.assertEqual(sum(v for k,v in hist.items() if k>5),ch['over_five'])
                self.assertEqual(sum(v for k,v in hist.items() if k>2),ch['over_two'])
                self.assertAlmostEqual(ch['rms_lsb'], math.sqrt(ch['square_error']/ch['samples']))
            path = EVIDENCE/f'{name}.errors.json'
            self.assertEqual(probe.digest(path),row['frame_errors_sha256'])
            errors = json.loads(path.read_text())
            self.assertEqual(len(errors),row['runs']['float']['frames'])
            self.assertEqual(sum(e[0] for e in errors),row['total']['samples'])
            self.assertEqual(max(e[3] for e in errors),row['total']['maximum'])
            self.assertEqual(sum(e[4] for e in errors),row['total']['square_error'])
            self.assertEqual(sum(e[5] for e in errors),row['total']['signed_error'])

    def test_large_discrepancies_are_retained_not_hidden(self):
        maxima = {'he-44100-stereo':7233,'he-48000-stereo':5019,'hev2-44100-stereo':7678,
                  'lc-22050-mono':2,'lc-44100-stereo':2,'lc-48000-stereo':2,
                  'abba64':10211,'groovesalad16':5,'groovesalad32':6,'groovesalad64':3,'groovesalad128':2}
        for name,maximum in maxima.items():self.assertEqual(self.rows[name]['total']['maximum'],maximum)
        for name in ('he-44100-stereo','he-48000-stereo','hev2-44100-stereo'):
            errors=json.loads((EVIDENCE/f'{name}.errors.json').read_text())
            self.assertGreater(max(e[3] for e in errors[:len(errors)//2]),1000)
            self.assertEqual(sum(e[6]+e[7] for e in errors),0)
        abba = json.loads((EVIDENCE/'abba64.errors.json').read_text())
        self.assertEqual([i for i,e in enumerate(abba) if e[3]>100],[11,12])
        self.assertEqual(next(i for i,e in enumerate(abba) if e[2]),11)
        self.assertEqual(max(e[3] for e in abba[13:]),4)

    def test_full_rates_and_real_channel_transition(self):
        self.assertEqual(self.rows['abba64']['output_layouts'],[[44100,1],[44100,2]])
        self.assertEqual([c['samples'] for c in self.rows['abba64']['channels']],[1320960,1300480])
        for name,row in self.rows.items():
            if name=='abba64':continue
            rate=32000 if name=='groovesalad16' else 48000 if '48000' in name else 44100
            channels=1 if name in ('groovesalad16','lc-22050-mono') else 2
            self.assertEqual(row['output_layouts'],[[rate,channels]])
        self.assertEqual(self.rows['lc-22050-mono']['runs']['fixed']['sbr_frames'],0)
        self.assertGreater(self.rows['lc-22050-mono']['runs']['fixed']['upsampled_core_frames'],0)

    def test_diagnostics_preserve_transients_and_reject_bad_shapes(self):
        with tempfile.TemporaryDirectory() as directory:
            base,candidate=Path(directory)/'a.pcm',Path(directory)/'b.pcm'
            a,b=array('h',[10,20,30,40,50,32767]),array('h',[11,20,30,42,50,32760])
            if sys.byteorder!='little':a.byteswap();b.byteswap()
            base.write_bytes(a.tobytes());candidate.write_bytes(b.tobytes())
            frames=[[7,2,44100,1,1,0],[7,4,44100,2,1,1]]
            self.assertEqual(probe.frame_diagnostics(base,candidate,frames),
                             [[2,1,0,1,1,1,0,0],[4,2,1,7,53,-5,1,0]])
            for invalid in (frames[:1],[[7,6,44100,3,1,0]],[[7,5,44100,2,1,0]]):
                with self.assertRaises(ValueError):probe.frame_diagnostics(base,candidate,invalid)


if __name__ == '__main__':unittest.main()
