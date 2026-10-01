"""Check native AAC field labels, ABI boundaries and complete decompilation coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import audit_aac_symbolic as audit
DATA = ROOT/'docs/audits/esp32c3-aac-core-symbolic-20261001'
RAW = ROOT/'docs/audits/esp32c3-aac-full-20261001/pseudocode'
COMPILER = None

def read(path): return json.loads(path.read_text())
def source(name): return (DATA/'pseudocode'/(name+'.c')).read_text()

class CoreSymbolicTests(unittest.TestCase):
    def test_complete_inventory_and_honest_remaining_review(self):
        result = audit.audit(RAW, DATA/'pseudocode')
        self.assertEqual(result, read(DATA/'access-review.json'))
        self.assertEqual(result['functions'], 186)
        self.assertEqual(result['changed_functions'], 98)
        self.assertEqual(result['remaining_candidates'], 888)
        self.assertEqual({r['function'] for r in result['rows'] if r['contains_warning']},
                         {'ps_bstr_decoding', 'sbr_dec', 'sbr_reset_dec'})
        # Do not turn an approximate lexical inventory into a "zero offsets" claim.
        self.assertGreater(result['remaining_candidates'], 0)

    def test_sources_and_export_have_exact_provenance(self):
        for name, digest in read(DATA/'provenance.json')['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(), digest, name)
        meta = read(DATA/'types.json')
        self.assertEqual(meta, read(DATA/'applied-types.json'))
        for name,key in [('aac_sbr_abi.h','header_sha256'),
                         ('aac_analysis_regions.h','regions_sha256'),
                         ('aac_analysis_core.h','core_header_sha256')]:
            self.assertEqual(hashlib.sha256((DATA/'implementation-snapshots'/name).read_bytes()).hexdigest(), meta[key])
        log = (DATA/'headless.log').read_text()
        self.assertIn('AAC types: checked 63 layouts; annotated 94 functions', log)
        self.assertIn('AAC export: 186 functions; 0 failures', log)
        self.assertNotIn('SCRIPT ERROR', log)

    def test_native_roles_not_reference_argument_guesses(self):
        parameters = read(DATA/'types.json')['parameters']
        self.assertEqual(parameters['get_tns']['5']['type'], 'aac_analysis_tns_t *')
        self.assertNotIn('0', parameters['get_tns']) # maximum band, not a pointer
        self.assertEqual(parameters['apply_tns']['3']['type'], 'aac_analysis_tns_t *')
        self.assertNotIn('0', parameters['apply_tns']) # PCM coefficients, not TNS
        self.assertEqual(parameters['sbr_applied']['8']['type'], 'aac_analysis_core_t *')
        self.assertEqual(parameters['getics']['2']['type'], 'aac_analysis_core_t *')
        self.assertIn('tns->filter', source('apply_tns'))
        self.assertIn('mc->sample_rate_index', source('get_tns'))

    def test_lifecycle_and_bitreader_fields_are_named(self):
        init = source('PVMP4AudioDecoderInitLibrary')
        for field in ('program','long_window','short_window','sbr_stream','workspace'):
            self.assertIn('core->'+field, init)
            self.assertIn('core->'+field, source('PVMP4AudioDecoderDeInit'))
        self.assertIn('&core->spectral[0].shared', init)
        self.assertIn('core->spectral[0].mask', init)
        self.assertIn('bits->total_bits - bits->read_bits', source('GetNrBitsAvailable'))
        self.assertIn('bits->used_bits', source('decode_huff_cw_tab11'))
        self.assertIn('saved_plus_enabled', source('esp_aac_dec_reset'))
        self.assertIn('external->bitrate', source('PVMP4AudioDecodeFrame'))
        self.assertNotIn('external->object_type', source('PVMP4AudioDecodeFrame'))
        self.assertIn('(core->mc).ps_present', source('sbr_applied'))
        self.assertNotIn('core->channels', source('sbr_applied'))
        for name in ('PVMP4AudioDecodeFrame','PVMP4AudioDecoderInitLibrary','PVMP4AudioDecoderDeInit',
                     'esp_aac_dec_open','esp_aac_dec_close','esp_aac_dec_decode',
                     'get_prog_config','get_tns','get_sbr_bitstream','huffcb','hufffac',
                     'calc_auto_corr','calc_auto_corr_LC'):
            self.assertEqual(audit.candidates(source(name)), [], name)

    def test_table_labels_and_workspace_boundaries(self):
        meta = read(DATA/'types.json')
        sizes = {'aac_analysis_core_t':35460, 'aac_analysis_decoder_t':84,
                 'aac_analysis_sbr_bits_t':20, 'aac_analysis_spectral_storage_t':8192,
                 'aac_analysis_envelope_workspace_t':4096,
                 'aac_analysis_sbr_stream_t':1044, 'aac_analysis_workspace_t':12288}
        for name,size in sizes.items(): self.assertEqual(meta['types'][name]['bytes'],size)
        self.assertEqual(set(meta['data_symbols']), {'hcbbook_binary','samp_rate_info'})
        self.assertIn('hcbbook_binary.entry[uVar3].signed_codebook', source('getics'))
        self.assertIn('samp_rate_info.entry[param_1].long_bands', source('infoinit'))
        self.assertIn('scratch->gain_mantissa', source('calc_sbr_envelope'))
        self.assertIn('correlation->determinant', source('calc_auto_corr'))
        # Preserve evidence of the invalid vendor reset instead of relabeling it away.
        self.assertIn('core[2]', source('PVMP4AudioDecoderResetBuffer'))

    def test_rv32_compiler_reproduces_all_current_layouts(self):
        if COMPILER is None: self.skipTest('Pass --compiler to validate RV32 layouts')
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([sys.executable, str(ROOT/'tools/codec_benchmark/prepare_aac_symbolic.py'),
                            '--include-core','--compiler',str(COMPILER),'--output',folder],
                           check=True,capture_output=True)
            new = read(Path(folder)/'types.json'); old = read(DATA/'types.json')
            for key in ('types','nodes','parameters','data_symbols','analysis_regions'):
                self.assertEqual(new[key],old[key],key)

    def test_layout_drift_fails_compilation(self):
        if COMPILER is None: self.skipTest('Pass --compiler for the negative layout test')
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            path = ROOT/'tools/codec_benchmark/aac_analysis_core.h'
            header = path.read_text()
            old = 'uint32_t cached_bits, cache, read_bits, total_bits;'
            self.assertIn(old, header)
            (folder/path.name).write_text(header.replace(old, 'uint32_t unexpected; '+old))
            probe = folder/'probe.c'; probe.write_text('#include "aac_analysis_core.h"\n')
            run = subprocess.run([str(COMPILER),'-std=c11','-march=rv32imc','-mabi=ilp32',
                '-I',str(ROOT/'tools/codec_benchmark'),'-I',str(ROOT/'idf/esp32c3-oled-native/main'),
                '-c',str(probe),'-o',str(folder/'probe.o')],capture_output=True)
            self.assertNotEqual(run.returncode,0)
            self.assertIn(b'static assertion failed',run.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False); parser.add_argument('--compiler',type=Path)
    args,rest = parser.parse_known_args(); COMPILER = args.compiler
    unittest.main(argv=[sys.argv[0],*rest])
