"""Replay exact PCM and original physical outcomes for the LPC optimization."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-flac-predictor-20261006'
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from summarize_terminal_cpu import summarize
from summarize_sustained import summarize as sustained

def read(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()

class PredictorEvidence(unittest.TestCase):
    def test_integrity_and_sources(self):
        manifest=read(DATA/'manifest.json')
        self.assertEqual(set(manifest),{p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                       if p.is_file() and p!=DATA/'manifest.json'})
        for name,info in manifest.items():
            data=(DATA/name).read_bytes()
            self.assertEqual((len(data),sha(data)),(info['bytes'],info['sha256']),name)
        for folder in ('bounds','contiguous','matrix','real24-large','dense-host','dense-long-host'):
            for name,digest in read(DATA/folder/'report.json')['sources'].items():
                self.assertEqual(sha((DATA/folder/'sources'/name).read_bytes()),digest)

    def test_exact_arithmetic(self):
        total=0
        for folder in ('matrix','real24-large','dense-host','dense-long-host'):
            report=read(DATA/folder/'report.json')
            self.assertTrue(report['passed'])
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                for result in case['variants'].values():
                    self.assertEqual(result['result'],'PASS')
                    self.assertEqual(result['sha256'],case['reference']['sha256'])
                    total+=1
        self.assertEqual(total,387)
        for folder in ('bounds','contiguous'):
            report=read(DATA/folder/'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(report['prediction_cases'],'PASS')
            self.assertIn('predictor_cases=198',(DATA/folder/'prediction.log').read_text())

    def test_original_runtime_failure_preserved(self):
        summary=summarize(DATA/'dense-before')
        self.assertEqual(summary,read(DATA/'dense-before/summary.json'))
        self.assertEqual(summary['runtime']['result'],'FAIL')
        self.assertEqual(len(summary['streams']),2)
        for case in summary['streams']:
            self.assertEqual(case['original']['result'],'PASS')
            self.assertLess(case['diagnostic']['audio_wall_ratio'],.81)
        report=read(DATA/'dense-before/report.json')
        self.assertEqual(next(c for c in report['cases'] if c['name']=='runtime-health')['result'],'FAIL')

    def test_build_storage_unchanged(self):
        before=read(ROOT/'tests/results/esp32c3-flac-depths-20261005/verify/build.json')
        after=read(DATA/'verify/build.json')
        for name in ('.iram0.text','.dram0.data','.dram0.bss','.rtc.data'):
            self.assertEqual(before['sections'][name],after['sections'][name])
        artifact=ROOT/'firmware/development/esp32c3-flac-predictor'
        self.assertEqual(sha((artifact/'app.bin').read_bytes()),after['app_sha256'])
        self.assertEqual(sha((artifact/'sdkconfig').read_bytes()),before['sdkconfig_sha256'])
        self.assertFalse(read(artifact/'manifest.json')['production_qualified'])
        for folder in ('terminal','load16','load24','dense-load','aac-load'):
            report=read(DATA/folder/'report.json')
            self.assertEqual(report['board']['app_elf_sha256'],after['elf_sha256'])
            if 'config' in report:
                self.assertEqual(report['config']['sha256'],after['sdkconfig_sha256'])
        core='yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
        self.assertEqual(after['source_sha256'][core],read(DATA/'matrix/report.json')['sources'][core])

    def test_current_short_run_replays(self):
        result=summarize(DATA/'terminal')
        self.assertEqual(result,read(DATA/'terminal/summary.json'))
        self.assertEqual(result['runtime']['result'],'FAIL')
        self.assertEqual(len(result['streams']),6)
        for case in result['streams']:
            dense='lpc32dense' in case['name']
            self.assertEqual(case['runtime']['result'],'FAIL' if dense else 'PASS')
            ratio=case['diagnostic']['audio_wall_ratio']
            if dense:self.assertLess(ratio,.95)
            else:self.assertGreater(ratio,.99)

    def test_sustained_windows_replay_without_hiding_failures(self):
        for folder in ('load16','load24','dense-load','aac-load'):
            summary=sustained(DATA/folder)
            self.assertEqual(summary,read(DATA/folder/'summary.json'))
            self.assertEqual(len(summary['cases']),1)
            case=summary['cases'][0]
            original=next(c for c in read(DATA/folder/'report.json')['cases']
                          if c['name'].startswith('cpu-under-http-load:'))
            self.assertEqual(case['original'],original)

if __name__=='__main__':unittest.main()
