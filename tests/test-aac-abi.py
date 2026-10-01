"""Verify compiler-derived AAC layout and the exact decoder refactor results."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import compact_sbr_tables as patch
import run_aac_smoothing as smoothing
import run_aac_reset as reset
import run_aac_pc16_write as pc16
import run_aac_reserve as owner

EVIDENCE=ROOT/'tests/results/esp32c3-aac-abi-20261001'
PRIOR=ROOT/'tests/results/esp32c3-aac-smoothing-20261001'
COMPILER=None
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class AbiTests(unittest.TestCase):
    def test_compiler_fields_preserve_every_patched_object(self):
        current=read(EVIDENCE/'audit.json');previous=read(PRIOR/'audit.json')
        fields=patch.read_layout((EVIDENCE/'layout.o').read_bytes())
        self.assertEqual(fields,current['compiler_layout'])
        self.assertEqual(fields['owner_size'],[55128,53240])
        self.assertEqual(fields['channel_size'],[25792,24848])
        self.assertEqual(fields['table_size'],[256,20])
        self.assertEqual(current['functions'],previous['functions'])
        patches=patch.resolve_patches(fields)
        self.assertEqual(sum(map(len,patches.values())),53)
        for name,rows in patches.items():
            for (offset,word,value,meaning),entry in zip(rows,current['functions'][name]['patches']):
                self.assertEqual(entry['offset'],hex(offset))
                self.assertEqual(entry['meaning'],meaning)
                self.assertEqual(int(entry['replacement'],16),patch.immediate(int(word,16),len(word)//2,value))

    def test_layout_rejects_wrong_architecture_or_missing_fields(self):
        original=(EVIDENCE/'layout.o').read_bytes()
        for offset,replacement in ((4,b'\x02'),(5,b'\x02'),(18,b'\x28\x00')):
            damaged=bytearray(original);damaged[offset:offset+len(replacement)]=replacement
            with self.assertRaises(Exception):patch.read_layout(damaged)
        self.assertIn(b'aac_abi_owner_size',original)
        with self.assertRaisesRegex(ValueError,'Missing/extra'):
            patch.read_layout(original.replace(b'aac_abi_owner_size',b'ignored_owner_size'))

    def test_regenerate_from_current_header_and_reject_layout_drift(self):
        if COMPILER is None:self.skipTest('Pass --compiler to compile the RV32 ABI assertions')
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);target=folder/'layout.o'
            header=ROOT/'idf/esp32c3-oled-native/main/aac_sbr_abi.h'
            copy=folder/header.name;copy.write_bytes(header.read_bytes())
            command=[str(COMPILER),'-std=c11','-Wall','-Wextra','-Werror','-march=rv32imc','-mabi=ilp32',
                     '-I',str(folder),'-c',str(ROOT/'tools/codec_benchmark/aac_abi_layout.c'),'-o',str(target)]
            subprocess.run(command,check=True,capture_output=True)
            self.assertEqual(patch.read_layout(target.read_bytes()),patch.read_layout((EVIDENCE/'layout.o').read_bytes()))
            text=copy.read_text();self.assertIn('int32_t frame_size, sync_state;',text)
            copy.write_text(text.replace('int32_t frame_size, sync_state;','int32_t frame_size, extra, sync_state;'))
            failed=subprocess.run(command,capture_output=True)
            self.assertNotEqual(failed.returncode,0)
            self.assertIn(b'static assertion failed',failed.stderr)

    def test_saved_runs_and_source_fingerprints(self):
        parsers={'synthetic':smoothing.parse_log,'abba64':smoothing.parse_log,'reset':reset.parse_log,
                 'pc16-synthetic':pc16.parse_log,'pc16-abba64':pc16.parse_log,'owner':owner.parse_log}
        for name,parser in parsers.items():
            folder=EVIDENCE/name;result=read(folder/'result.json')
            for key,value in parser((folder/'qemu.log').read_text()).items():self.assertEqual(value,result[key],(name,key))
            self.assertEqual(sha(folder/'qemu.log'),result['provenance']['qemu_log_sha256'])
            self.assertEqual(sha(folder/'sdkconfig'),result['provenance']['sdkconfig_sha256'])
        manifest=read(EVIDENCE/'implementation.json')
        for path,entry in manifest['files'].items():self.assertEqual(sha(EVIDENCE/entry['snapshot']),entry['sha256'],path)
        self.assertEqual(sha(EVIDENCE/'layout.o'),manifest['layout_sha256'])
        self.assertEqual(sha(EVIDENCE/'audit.json'),manifest['audit_sha256'])
        self.assertEqual(sha(EVIDENCE/'host-sanitizers.log'),manifest['host_sanitizers']['sha256'])
        self.assertEqual(manifest['host_sanitizers']['exit_code'],0)
        self.assertEqual(sum(line.startswith('PASS:') for line in (EVIDENCE/'host-sanitizers.log').read_text().splitlines()),7)

    def test_pcm_and_existing_quantization_are_unchanged(self):
        for name in ('synthetic','abba64'):
            result=read(EVIDENCE/name/'result.json')
            self.assertTrue(result['precision_pass']);self.assertEqual(result['precision_limit_lsb'],0)
            old=read(ROOT/'tests/results/esp32c3-aac-pc16-write-20261001'/name/'result.json')
            new=read(EVIDENCE/('pc16-'+name)/'result.json')
            self.assertEqual(len(old['runs']),len(new['runs']))
            for a,b in zip(old['runs'],new['runs']):
                for field in ('case','variant','run','frames','samples','different','max_l','max_r','over_one','over_two','over_limit'):
                    self.assertEqual(a[field],b[field],(name,field))
            if name=='abba64':self.assertEqual(old['error_statistics'],new['error_statistics'])
        result=read(EVIDENCE/'owner/result.json')['pcm']
        previous=read(ROOT/'tests/results/esp32c3-aac-pc16-cache-20261001/owner/result.json')['pcm']
        for field in ('frames','channels','rate','sample_width','pcm_sha256'):self.assertEqual(result[field],previous[field])
        self.assertEqual(result['different_samples'],0)
        self.assertEqual(result['max_pcm_error_lsb'],0)


if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--compiler',type=Path)
    args,remaining=parser.parse_known_args();COMPILER=args.compiler
    unittest.main(argv=[sys.argv[0],*remaining])
