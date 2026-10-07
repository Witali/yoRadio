"""Validate named AAC exports without treating inferred code as executable C."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from aac_symbolic_layouts import assert_archive_layout

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import audit_aac_symbolic as audit
DATA = ROOT/'docs/audits/esp32c3-aac-symbolic-20261001'
RAW = ROOT/'docs/audits/esp32c3-aac-full-20261001/pseudocode'
COMPILER = None
def read(path): return json.loads(path.read_text())


class SymbolicTests(unittest.TestCase):
    def test_all_functions_and_remaining_candidates_are_accounted_for(self):
        result = audit.audit(RAW,DATA/'pseudocode')
        self.assertEqual(result,read(DATA/'access-review.json'))
        self.assertEqual(result['functions'],186)
        self.assertEqual(result['changed_functions'],36)
        self.assertEqual(result['before_candidates'],2256)
        self.assertEqual(result['remaining_candidates'],1733)
        self.assertEqual({r['function'] for r in result['rows'] if r['contains_warning']},
                         {'ps_bstr_decoding','sbr_reset_dec'})

    def test_exact_export_and_input_hashes(self):
        for path,digest in read(DATA/'provenance.json')['files'].items():
            self.assertEqual(hashlib.sha256((DATA/path).read_bytes()).hexdigest(),digest,path)
        meta = read(DATA/'types.json')
        self.assertEqual(meta,read(DATA/'applied-types.json'))
        for file,key in [('aac_sbr_abi.h','header_sha256'),('aac_analysis_regions.h','regions_sha256')]:
            self.assertEqual(hashlib.sha256((DATA/'implementation-snapshots'/file).read_bytes()).hexdigest(),meta[key])

    def test_pointer_to_array_and_pointer_depth_are_preserved(self):
        meta = read(DATA/'types.json'); nodes = meta['nodes']
        ps = nodes[nodes[meta['roots']['aac_ps_abi_t']]['type']]
        def field(name): return nodes[next(m['type'] for m in ps['members'] if m['name']==name)]
        qmf = field('qmf_real'); self.assertEqual(qmf['kind'],'pointer_type')
        self.assertEqual(nodes[qmf['type']]['dimensions'],[64])
        for name in ('serial_real','serial_imag'):
            serial = field(name); self.assertEqual(serial['dimensions'],[3])
            pointer = nodes[serial['type']]; self.assertEqual(pointer['kind'],'pointer_type')
            self.assertEqual(nodes[pointer['type']]['kind'],'pointer_type')
        self.assertEqual(meta['types']['aac_ps_abi_t']['bytes'],3536)
        for region in meta['analysis_regions']:
            self.assertEqual(nodes[region['original']]['bytes'],nodes[region['replacement']]['bytes'])

    def test_native_argument_positions_and_named_fields(self):
        meta = read(DATA/'types.json')
        self.assertEqual(set(meta['parameters']['sbr_applied']),{'0','7','8'})
        source = (DATA/'pseudocode/sbr_applied.c').read_text()
        # This immutable export used the wrong PS-field name. Check the corrected
        # export for its meaning; old file bytes are verified by provenance above.
        corrected = (ROOT/'docs/audits/esp32c3-aac-core-symbolic-20261001/pseudocode/sbr_applied.c').read_text()
        self.assertIn('(core->mc).ps_present', corrected)
        self.assertIn('sbr_read_data(owner,control,',source)
        self.assertNotIn('core == (aac_core_abi_t *)0x2',source)
        self.assertIn('enable_iid',(DATA/'pseudocode/ps_read_data.c').read_text())
        self.assertIn('->real_history =',(DATA/'pseudocode/ps_hybrid_filter_bank_allocation.c').read_text())

    def test_current_headers_compile_and_reproduce_layouts(self):
        if COMPILER is None: self.skipTest('Pass --compiler for fresh RV32 validation')
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([sys.executable,str(ROOT/'tools/codec_benchmark/prepare_aac_symbolic.py'),
                            '--compiler',str(COMPILER),'--output',folder],check=True,capture_output=True)
            new = read(Path(folder)/'types.json'); old = read(DATA/'types.json')
            assert_archive_layout(self, new, old)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False); parser.add_argument('--compiler',type=Path)
    args,other = parser.parse_known_args(); COMPILER = args.compiler
    unittest.main(argv=[sys.argv[0],*other])
