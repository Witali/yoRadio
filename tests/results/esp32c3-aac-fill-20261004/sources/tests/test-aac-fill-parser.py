"""Retained native FIL comparison, bounded-read sanitizers and verified RV32 ABI."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-aac-fill-20261004'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_aac_fill import parse_log
COMPILER=None


class FillTests(unittest.TestCase):
    def test_real_native_comparisons_and_full_runs(self):
        for variant in ('plain','pc19'):
            actual=parse_log((DATA/variant/'diagnostics.log').read_text(),plain=variant=='plain')
            saved=json.loads((DATA/variant/'result.json').read_text())
            for key,value in actual.items():self.assertEqual(value,saved[key],(variant,key))
            self.assertEqual(actual['valid_comparisons'],69376)
            self.assertEqual(actual['native_overrun_bits'],2148)
            self.assertEqual(set(saved['linked_hooks']),
                             {'aac_fill_skip','aac_fill_sbr','__wrap_getfill','__wrap_get_sbr_bitstream'})

    def test_reject_incomplete_or_false_success(self):
        log=(DATA/'pc19/diagnostics.log').read_text()
        for changed in (
            log.replace('AAC_FIL_PARSER_PASS','missing'),
            log.replace('valid_cases=69376','valid_cases=69375'),
            log.replace('checked_cursor=16','checked_cursor=2164'),
            log.replace('QEMU_SMOKE_PASS','missing'),
            log+'\nAAC_FIL_PARSER_PASS duplicate\n',
            log+'\nassert failed: bad input\n',
        ):
            with self.assertRaises(ValueError):parse_log(changed)

    def test_host_sanitizer_evidence(self):
        result=json.loads((DATA/'host/result.json').read_text())
        self.assertEqual(result['exit_code'],0)
        self.assertEqual(result['valid_cases'],69376)
        self.assertEqual(result['truncated_cases'],343475)
        self.assertEqual(result['invalid_state_cases'],4)
        self.assertIn('-fsanitize=address,undefined',result['command'])
        self.assertEqual(result['stdout'],(DATA/'host/test.log').read_text())
        for path,digest in result['hashes'].items():
            self.assertEqual(hashlib.sha256((DATA/'sources'/path).read_bytes()).hexdigest(),digest)

    def test_pcm_unchanged_and_instruction_totals(self):
        result=json.loads((DATA/'comparison.json').read_text())
        self.assertEqual(sum(r['channel_samples'] for r in result['pcm']),865280)
        for row in result['pcm']:
            pcm=gzip.decompress((DATA/(row['case']+'.pcm.gz')).read_bytes())
            self.assertEqual(pcm,gzip.decompress((ROOT/row['baseline']).read_bytes()))
            self.assertEqual(hashlib.sha256(pcm).hexdigest(),row['pcm_sha256'])
            self.assertEqual(row['different'],0)
        work=result['work']
        self.assertAlmostEqual(work['delta_percent'],100*(work['candidate_instructions']/work['reference_instructions']-1))

    def test_saved_physical_image(self):
        result=json.loads((DATA/'production-build.json').read_text())
        artifact=ROOT/'firmware/development/esp32c3-aac-fill-network'
        # Unreleased artifacts can be replaced later; only verify this image if
        # its current manifest still refers to the retained build.
        current=json.loads((artifact/'manifest.json').read_text())
        if current['app_sha256']==result['app_sha256']:
            self.assertEqual(hashlib.sha256((artifact/'app.bin').read_bytes()).hexdigest(),result['app_sha256'])
        self.assertFalse(result['hardware_tested'])
        self.assertFalse(result['production_qualified'])
        self.assertFalse(result['deep_sleep'])

    def test_exact_rv32_layout(self):
        if not COMPILER:self.skipTest('Supply --compiler for the RV32 ABI check')
        with tempfile.TemporaryDirectory() as directory:
            command=[str(COMPILER),'-std=c11','-march=rv32imc','-mabi=ilp32',
                     '-I',str(ROOT/'tools/codec_benchmark'),
                     '-I',str(ROOT/'idf/esp32c3-oled-native/main'),'-c',
                     str(ROOT/'tests/native/aac_fill_abi_test.c'),'-o',str(Path(directory)/'abi.o')]
            subprocess.run(command,capture_output=True,check=True)

    def test_manifest(self):
        manifest=json.loads((DATA/'manifest.json').read_text())
        for name,digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(),digest,name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--compiler',type=Path)
    args,rest=parser.parse_known_args();COMPILER=args.compiler
    unittest.main(argv=[sys.argv[0],*rest])
