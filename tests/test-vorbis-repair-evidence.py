"""Recompute initialization qualification from retained target logs and artifacts."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_vorbis_lifecycle as runner
import save_vorbis_lifecycle as saver

FINAL = ROOT/'tests/results/esp32c3-vorbis-repair-20261004'
FIRST = ROOT/'tests/results/esp32c3-vorbis-repair-first-20261004'
RADIO = ROOT/'tests/results/esp32c3-vorbis-radio-build-20261004'
ARTIFACT = ROOT/'firmware/development/esp32c3-vorbis-repair'


class RetainedRepair(unittest.TestCase):
    def test_every_retained_byte_matches_manifest(self):
        for folder in (FIRST, FINAL, RADIO):
            manifest = json.loads((folder/'manifest.json').read_text())
            files = {p.relative_to(folder).as_posix() for p in folder.rglob('*')
                     if p.is_file() and p.name != 'manifest.json'}
            self.assertEqual(set(manifest), files)
            for name, expected in manifest.items():
                with self.subTest(folder=folder.name, file=name):
                    self.assertEqual((folder/name).stat().st_size, expected['bytes'])
                    self.assertEqual(runner.sha(folder/name), expected['sha256'])

    def test_replay_both_trials_and_keep_failed_trial_visible(self):
        for folder, expected in ((FIRST, {'PASS':1, 'HANDLED':201, 'UNSAFE_RETURN':1}),
                                 (FINAL, {'PASS':1, 'HANDLED':208})):
            saved = json.loads((folder/'summary.json').read_text())
            recalculated = saver.summarize(folder)
            self.assertEqual(recalculated, {k:v for k,v in saved.items()
                                           if k not in ('classifier_sha256','saver_sha256')})
            self.assertEqual(saved['counts'], expected)
            self.assertEqual(saved['initialization_gate_pass'], folder == FINAL)
            self.assertTrue(saved['original_pcm_match'])
            self.assertFalse(saved['production_qualified'])
            self.assertFalse(saved['hardware_tested'])

    def test_complete_final_gate_and_original_pcm_memory(self):
        report = json.loads((FINAL/'report.json').read_text())
        summary = json.loads((FINAL/'summary.json').read_text())
        original = json.loads((ROOT/'tests/results/esp32c3-vorbis-lifecycle-20261004/summary.json').read_text())
        self.assertTrue(report['decoder_gate_pass'])
        self.assertTrue(report['coverage_complete'])
        self.assertEqual(len(report['cases']), 209)
        self.assertEqual(summary['cycles'], 100)
        for key in ('pcm','samples','sha256','peak_requested','peak_actual','free','largest'):
            self.assertEqual(summary['baseline_reference'][key], original['baseline_reference'][key], key)
        for case in report['cases'][1:]:
            self.assertTrue(case['recovery_ok'], case['name'])
            self.assertTrue(case['decoder_gate_pass'], case['name'])

    def test_exact_build_and_validator_provenance(self):
        for folder in (FIRST, FINAL):
            report = json.loads((folder/'report.json').read_text())
            summary = json.loads((folder/'summary.json').read_text())
            for name, digest in report['source_sha256'].items():
                self.assertEqual(runner.sha(folder/'sources'/name), digest)
            for name, key in (('run_vorbis_lifecycle.py','classifier_sha256'),
                              ('save_vorbis_lifecycle.py','saver_sha256')):
                self.assertEqual(runner.sha(folder/'validation_sources'/name), summary[key])
            self.assertEqual(runner.sha(folder/'sdkconfig'), report['config_sha256'])
            self.assertEqual(runner.sha(folder/'build/yoradio_esp32c3_oled_native.bin'), report['app_sha256'])
            self.assertEqual(report['archive_sha256'], runner.ARCHIVES)

    def test_radio_contains_repair_and_preserves_aac_contract(self):
        build = json.loads((RADIO/'build.json').read_text())
        self.assertEqual(build, json.loads((ARTIFACT/'manifest.json').read_text()))
        self.assertEqual(runner.sha(ARTIFACT/'app.bin'), build['app_sha256'])
        self.assertEqual(runner.sha(ARTIFACT/'sdkconfig'), build['sdkconfig_sha256'])
        self.assertEqual((ARTIFACT/'app.bin').read_bytes()[176:208].hex(), build['elf_sha256'])
        self.assertFalse(build['hardware_tested'])
        self.assertFalse(build['production_qualified'])
        self.assertEqual(build['vorbis_operations']['callbacks'], [
            '__wrap_esp_vorbis_dec_open', 'esp_vorbis_dec_decode',
            'esp_vorbis_dec_reset', 'esp_vorbis_dec_close'])
        self.assertEqual(build['types'], {'native_aac_decoder':204,
                                         'aac_high_owner_t':32744, 'aac_high_runtime_t':160})
        config = (ARTIFACT/'sdkconfig').read_text()
        self.assertIn('CONFIG_YORADIO_VORBIS_REPAIR=y', config)
        self.assertIn('CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19=y', config)
        self.assertNotIn('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y', config)
        for name, digest in build['source_sha256'].items():
            self.assertEqual(runner.sha(RADIO/'sources'/name), digest)
            # Historical evidence binds the retained build to its snapshot;
            # subsequent repairs are allowed to change the working tree.


if __name__ == '__main__':
    unittest.main()
