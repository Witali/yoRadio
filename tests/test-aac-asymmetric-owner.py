"""Check asymmetric SBR extents, exact native patches and retained PCM/lifetimes."""
import argparse,gzip,hashlib,io,json,re,subprocess,sys,tempfile,unittest,wave
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import compact_asymmetric_owner as patch
import compact_sbr_tables as base
import run_aac_asymmetric_owner as runner
import run_aac_low_workspace as low

EVIDENCE=ROOT/'tests/results/esp32c3-aac-asymmetric-owner-20261003'
PRIOR=ROOT/'tests/results/esp32c3-aac-low-production-20261003/qemu'
RUNS=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')
COMPILER=None
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def layout(data):
    previous=base.PATCH_SPECS
    try:
        base.PATCH_SPECS=patch.SPECS
        return base.read_layout(data)
    finally:base.PATCH_SPECS=previous

class AsymmetricTests(unittest.TestCase):
    def test_compiler_offsets_separate_reset_sentinel_and_ps_object(self):
        fields=layout((EVIDENCE/'layout.o').read_bytes())
        self.assertEqual(fields,read(EVIDENCE/'audit.json')['compiler_layout'])
        self.assertEqual(fields['channel_size'][1],14776)
        self.assertEqual(fields['left_frame'][1],96)
        self.assertEqual(fields['right_frame'][1],14776+96)
        self.assertEqual(fields['frame_cursor_end'][1],2*14776+96)
        self.assertEqual(fields['ps_data'][1],32740)
        self.assertNotEqual(fields['frame_cursor_end'][1],fields['ps_data'][1])
        self.assertEqual(fields['ps_flag'][1],14776+17956)
        for n in range(4):self.assertEqual(fields[f'frame_table_{n}'][1],(1<<32)-80+n*20)

    def test_each_changed_instruction_matches_the_pinned_native_object(self):
        audit=read(EVIDENCE/'audit.json')
        for symbol,entry in audit['functions'].items():
            member=base.MEMBERS[symbol]
            original=(EVIDENCE/'native'/member).read_bytes()
            changed=(EVIDENCE/'patched'/member).read_bytes()
            self.assertEqual(hashlib.sha256(original).hexdigest(),entry['input_sha256'])
            self.assertEqual(hashlib.sha256(changed).hexdigest(),entry['output_sha256'])
            before=ELFFile(io.BytesIO(original)).get_section_by_name('.text.'+symbol).data()
            after=ELFFile(io.BytesIO(changed)).get_section_by_name('.text.'+symbol).data()
            expected=bytearray(before)
            for change in entry['patches']:
                offset=int(change['offset'],16);width=len(change['original'])//2
                self.assertEqual(int.from_bytes(before[offset:offset+width],'little'),int(change['original'],16))
                expected[offset:offset+width]=int(change['replacement'],16).to_bytes(width,'little')
            self.assertEqual(after,expected,symbol)

    def test_zero_upper_base_is_same_width_and_register(self):
        for rd in range(1,32):
            instruction=0x6001|(rd<<7)|(6<<2)
            if rd==2:
                with self.assertRaises(ValueError):patch.prefix_immediate(instruction,2,0)
            else:
                self.assertEqual(patch.prefix_immediate(instruction,2,0),0x4001|(rd<<7))
                self.assertEqual(patch.prefix_immediate(instruction,2,6),instruction)
        with self.assertRaises(ValueError):patch.prefix_immediate(0x6001,2,0)

    def test_target_layout_compiles_and_prefix_drift_fails(self):
        if COMPILER is None:self.skipTest('Pass --compiler for RV32 layout checks')
        main=ROOT/'idf/esp32c3-oled-native/main'
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);target=folder/'layout.o'
            command=[str(COMPILER),'-std=c11','-Wall','-Wextra','-Werror','-march=rv32imc','-mabi=ilp32',
                '-DAAC_SMOOTHING_HISTORY_FOUR=1','-DAAC_LOW_WORKSPACE=1',
                '-I',str(folder),'-I',str(main),'-c',str(ROOT/'tools/codec_benchmark/aac_asymmetric_owner_layout.c'),
                '-o',str(target),'-DAAC_ASYMMETRIC_OWNER=1']
            subprocess.run(command,check=True,capture_output=True)
            self.assertEqual(layout(target.read_bytes()),layout((EVIDENCE/'layout.o').read_bytes()))
            header=(main/'aac_high_history_abi.h').read_text()
            marker='AAC_HIGH_PREFIX;\n    aac_high_frame_t frame;'
            self.assertIn(marker,header)
            (folder/'aac_high_history_abi.h').write_text(header.replace(marker,'AAC_HIGH_PREFIX;\n    int32_t wrong_stride;\n    aac_high_frame_t frame;'))
            failure=subprocess.run(command,capture_output=True)
            self.assertNotEqual(failure.returncode,0)
            self.assertIn(b'static assertion failed',failure.stderr)

    def test_six_runs_keep_complete_pcm_and_exact_pointer_coverage(self):
        elfs=set()
        for name in RUNS:
            folder=EVIDENCE/name;result=read(folder/'result.json')
            self.assertEqual(result['baseline_sha256'],sha(PRIOR/name/'result.json'))
            for key,value in runner.parse_log((folder/'qemu.log').read_text()).items():
                self.assertEqual(result[key],value)
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['pcm_vs_previous']['different'],0)
            self.assertEqual(result['pcm_vs_previous']['samples'],657540)
            self.assertEqual(result['measured_owner_block_saving_bytes'],4096)
            self.assertFalse(result['production_qualified'])
            self.assertEqual(result['provenance']['sdkconfig_sha256'],sha(EVIDENCE/'sdkconfig'))
            self.assertEqual(result['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))
            elfs.add(result['provenance']['elf_sha256'])
            if name!='synthetic':self.assertTrue(result['capture_identical'])
        self.assertEqual(len(elfs),1)
        image=read(EVIDENCE/'linked-symbols.json')
        self.assertIn(image['elf_sha256'],elfs)
        self.assertFalse(image['native_symmetric_open_linked'])
        self.assertTrue(image['typed_open_linked'])

    def test_wave_samples_equal_previous_decoder(self):
        audio=[]
        for p in (PRIOR/'control-candidate.wav.gz',EVIDENCE/'control-candidate.wav.gz'):
            with wave.open(io.BytesIO(gzip.decompress(p.read_bytes()))) as stream:
                self.assertEqual((stream.getnchannels(),stream.getsampwidth(),stream.getframerate()),(2,2,48000))
                self.assertEqual(stream.getnframes()*2,657540)
                audio.append(stream.readframes(stream.getnframes()))
        self.assertEqual(audio[0],audio[1])

    def test_missing_wrong_or_failed_reports_are_rejected(self):
        log=(EVIDENCE/'synthetic/qemu.log').read_text()
        marker=re.search(r'AAC_ASYMMETRIC_OWNER_PASS[^\n]*',log).group()
        for damaged in (log.replace(marker,''),log+'\n'+marker,
                        log.replace('left_bytes=14776','left_bytes=14780'),
                        log.replace('frame_offset=96','frame_offset=16'),
                        log.replace('owner_bytes=32744','owner_bytes=32740'),
                        log+'\nassert failed: invalid owner pointer'):
            with self.assertRaises(ValueError):runner.parse_log(damaged)

    def test_disabled_profile_preserves_previous_storage_and_pcm(self):
        folder=EVIDENCE/'disabled-control';result=read(folder/'result.json')
        for key,value in low.parse_log((folder/'qemu.log').read_text()).items():self.assertEqual(result[key],value)
        self.assertEqual(result['pcm_vs_previous']['different'],0)
        config=(folder/'sdkconfig').read_text()
        self.assertNotIn('CONFIG_YORADIO_QEMU_AAC_ASYMMETRIC_OWNER=y',config)

    def test_retained_sources_and_evidence_hashes(self):
        manifest=read(EVIDENCE/'implementation.json')
        for name,entry in manifest['files'].items():self.assertEqual(sha(EVIDENCE/entry['snapshot']),entry['sha256'],name)
        for name,digest in manifest['evidence'].items():self.assertEqual(sha(EVIDENCE/name),digest,name)

if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--compiler',type=Path)
    args,remaining=parser.parse_known_args();COMPILER=args.compiler
    unittest.main(argv=[sys.argv[0],*remaining])
