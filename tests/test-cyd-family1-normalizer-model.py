"""Pure integer-model and strict transcript controls; no compiler/SDK/QEMU."""
from array import array
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


MODEL = ROOT / 'tests/fixtures/family1_normalizer/model.py'
RECORDS = ROOT / 'tests/fixtures/family1_normalizer/records.py'
model = load('owned_normalizer_test_model', MODEL)
records = load('owned_normalizer_test_reader', RECORDS)


def signal():
    values = array('h')
    for frame in range(9600):
        values.extend([frame % 31 - 15, 20 - frame % 41, 900, -1100,
                       frame % 401 - 200, 1600, -1900, 2300 - frame % 151])
    return values.tobytes()


def transcript(expected):
    rows = ['CYD_NORM_BOOT cases=2 enabled=1 hardware=0 release=UNRELEASED']
    for case in (1, 2):
        rows.append(f'CYD_NORM_BEGIN case={case} enabled=1 gain_db=20 target_dbfs=-20 time_ms=100 rate=48000 channels=8 volume=127 balance=0 schedule={case} page_style={case-1}')
        if case == 1:
            rows.append('CYD_NORM_CONFIG case=1 enabled=1 gain_db=20 target_dbfs=-20 time_ms=100 rate=48000 frames=0 core=1 priority=6')
        rows.append(f'CYD_NORM_RESET case={case} frames=0 phase=2 core=1 priority=6')
        if case == 1:
            rows.extend(['CYD_NORM_REQUEST case=1 frames=5448 requests=2 immediate_resets=0 config_unchanged=1 geometry_unchanged=1', 'CYD_NORM_RESET case=1 frames=5448 phase=2 core=1 priority=6'])
        rows.append(f'CYD_NORM_RESET case={case} frames=9600 phase=3 core=1 priority=6')
        rows.append(f"CYD_NORM_CASE case={case} frames=9600 mono_bytes=19200 wire_bytes=19456 padding_bytes=256 sha256={expected['cases'][case-1]['final_pcm']['sha256']} normalizer_frames=9600 wrong_api_calls=0")
    rows.append('CYD_NORM_COMPLETE cases=2 opens=10 closes=10 http_cleanup=2 flushes=2 heap_integrity=1 hardware=0')
    return '\n'.join(rows) + '\n'


def golden_metadata():
    return dict(profile=dict(model.PROFILE), decimal_precisions=[100, 160], new_tolerance=False,
        source_pcm=dict(bytes=153600, sha256='0' * 64),
        cases=[dict(case=i, reset_frames=[5448] if i == 1 else [],
                    normalized=dict(bytes=153600, sha256=character * 64),
                    final_pcm=dict(bytes=19200, frames=9600, sha256=character * 64))
               for i, character in [(1, 'a'), (2, 'b')]])


class ModelControls(unittest.TestCase):
    def test_independent_limiter_goldens(self):
        for value, expected in [(0, 0), (28672, 28672), (-28672, -28672), (32768, 30719), (-32768, -30719), (327680, 32711)]:
            self.assertEqual(model.soft_limit(value), expected)

    def test_update_after_complete_block(self):
        source = array('h', [0] * 9600 * 8)
        for i in range(9600): source[i * 8 + 7] = 1000
        output, state = model.normalize(source.tobytes())
        actual = array('h'); actual.frombytes(output)
        self.assertEqual(state['updates'][0], dict(after_frame=480, gain_q12=5029, peak=1000))
        self.assertEqual(actual[479 * 8 + 7], 1000)
        self.assertEqual(actual[480 * 8 + 7], 1227)
        self.assertEqual(len(state['updates']), 20)

    def test_explicit_midstream_reset(self):
        source = signal(); original_hash = hashlib.sha256(source).hexdigest()
        a, first = model.normalize(source, (5448,)); b, second = model.normalize(source)
        self.assertNotEqual(a, b)
        self.assertEqual(len(first['updates']), 19)
        self.assertEqual(first['tail_detector_frames'], 312)
        self.assertEqual(second['tail_detector_frames'], 0)
        self.assertEqual(hashlib.sha256(source).hexdigest(), original_hash)

    def test_invalid_geometry_and_resets(self):
        for source, resets in [(b'', ()), (bytes(153600), (5448, 5448)), (bytes(153600), (9600,))]:
            with self.assertRaises(ValueError): model.normalize(source, resets)

    def test_all_fixed_mutants_change_normalized_samples(self):
        source = signal(); good, unused = model.normalize(source)
        for wrong in ('disabled', 'detector_first_two', 'process_first_two', 'gain_before_detector'):
            other, unused = model.normalize(source, wrong=wrong)
            self.assertNotEqual(good, other, wrong)

    def test_reader_contradictions(self):
        expected = golden_metadata()
        original = transcript(expected)
        self.assertTrue(records.validate_gate(original, expected)['passed'])
        mutations = [
            original.replace('enabled=1 gain_db=20', 'enabled=0 gain_db=20', 1),
            original.replace('requests=2', 'requests=1'),
            original.replace('immediate_resets=0', 'immediate_resets=1'),
            original.replace('geometry_unchanged=1', 'geometry_unchanged=0'),
            original.replace('frames=5448 phase=2', 'frames=5449 phase=2'),
            original.replace('case=2 frames=0 phase=2', 'case=2 frames=1 phase=2'),
            original.replace('priority=6', 'priority=5', 1),
            original.replace('padding_bytes=256', 'padding_bytes=255', 1),
            original.replace('wire_bytes=19456', 'wire_bytes=19200', 1),
            original.replace('normalizer_frames=9600', 'normalizer_frames=9599', 1),
            original.replace('wrong_api_calls=0', 'wrong_api_calls=1', 1),
            original.replace('sha256=' + 'a' * 64, 'sha256=' + 'c' * 64),
            original.replace('closes=10', 'closes=9'),
            original + 'CYD_NORM_UNKNOWN value=1\n',
            original + 'Task watchdog triggered\n',
            original.replace('CYD_NORM_RESET case=1 frames=9600 phase=3 core=1 priority=6\n', ''),
        ]
        request = 'CYD_NORM_REQUEST case=1 frames=5448 requests=2 immediate_resets=0 config_unchanged=1 geometry_unchanged=1\n'
        reset = 'CYD_NORM_RESET case=1 frames=5448 phase=2 core=1 priority=6\n'
        mutations.append(original.replace(request + reset, reset + request))
        mutations.append(original + 'prefix CYD_NORM_RESET case=1 frames=0 phase=2 core=1 priority=6\n')
        for index, candidate in enumerate(mutations):
            with self.assertRaises(ValueError, msg=str(index)): records.validate_gate(candidate, expected)

    def test_reader_rejects_incomplete_or_wrong_goldens(self):
        expected = golden_metadata(); original = transcript(expected)
        bad = [dict(cases=[])]
        for path, value in [
            (('cases',), expected['cases'][:1]),
            (('cases',), expected['cases'] + [expected['cases'][1]]),
            (('cases',), list(reversed(expected['cases']))),
            (('cases', 1, 'case'), 1),
            (('profile', 'enabled'), False),
            (('source_pcm', 'bytes'), 153599),
            (('cases', 0, 'normalized', 'bytes'), 153599),
            (('cases', 0, 'final_pcm', 'bytes'), 19198),
            (('cases', 0, 'final_pcm', 'frames'), 9599),
            (('cases', 0, 'final_pcm', 'sha256'), 'not-a-hash'),
            (('cases', 0, 'reset_frames'), []),
            (('decimal_precisions',), [100]),
        ]:
            candidate = copy.deepcopy(expected); parent = candidate
            for key in path[:-1]: parent = parent[key]
            parent[path[-1]] = value; bad.append(candidate)
        for candidate in bad:
            with self.assertRaises(ValueError): records.validate_gate(original, candidate)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve()
    if not out.is_relative_to(ROOT / '.build') or out.exists(): raise ValueError('fresh contained control output')
    out.mkdir(parents=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ModelControls))
    report = dict(passed=result.wasSuccessful(), pure_controls=True, tests_run=result.testsRun,
                  reader_negative_controls=18, golden_metadata_negative_controls=13, native_executed=False, compiled=False,
                  source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (MODEL, RECORDS, Path(__file__).resolve())})
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__': main()
