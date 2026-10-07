"""Replay retained FLAC source-depth, allocation and physical evidence."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-flac-depths-20261005'
def read(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()


class DepthEvidence(unittest.TestCase):
    def test_manifest(self):
        manifest=read(DATA/'manifest.json')
        actual={p.relative_to(DATA).as_posix() for p in DATA.rglob('*') if p.is_file() and p!=DATA/'manifest.json'}
        self.assertEqual(actual,set(manifest))
        for name,identity in manifest.items():
            data=(DATA/name).read_bytes()
            self.assertEqual((len(data),sha(data)),(identity['bytes'],identity['sha256']),name)

    def test_426_pcm_comparisons(self):
        for folder,count in [('final-matrix',120),('large-result',10),('real24-result',4),('real24-large-result',4),('physical-host',4)]:
            report=read(DATA/folder/'report.json');self.assertTrue(report['passed'])
            self.assertEqual(len(report['cases']),count)
            for case in report['cases']:
                self.assertTrue(case['reference']['known_pcm_identical'])
                self.assertEqual(set(case['variants']),{'segmented','contiguous','adapter'})
                for result in case['variants'].values():
                    self.assertEqual(result['result'],'PASS',case['name'])
                    self.assertEqual((result['sha256'],result['bytes']),
                        (case['reference']['sha256'],case['reference']['bytes']))
            for name,digest in report['sources'].items():
                self.assertEqual(sha((DATA/folder/'sources'/name).read_bytes()),digest)

    def test_fixture_bytes(self):
        expected={s['file']:s for name in ('matrix-fixtures','large-fixtures')
                  for s in read(DATA/'fixtures'/(name+'.json'))['fixtures']}
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress((DATA/'fixtures/small-fixtures.tar.gz').read_bytes()))) as archive:
            self.assertEqual(set(archive.getnames()),set(expected))
            for name,spec in expected.items():self.assertEqual(sha(archive.extractfile(name).read()),spec['sha256'])

    def test_oom_and_old_failures(self):
        report=read(DATA/'oom/report.json');self.assertTrue(report['passed'])
        total=0
        for case in report['cases']:
            result=case['allocation_failures'];self.assertEqual(result['result'],'PASS')
            match=re.search(r'persistent_oom_cases=(\d+) recovery_cases=(\d+)',result['output'])
            self.assertEqual(match[1],match[2]);total+=int(match[1])
        self.assertEqual(total,46)
        baseline=read(DATA/'baseline/report.json')
        self.assertFalse(baseline['passed']);self.assertEqual(baseline['failures'],12)
        control=next(c for c in baseline['cases'] if c['name']=='flac-16bit-mid-lpc32')
        self.assertTrue(all(v['result']=='PASS' for v in control['variants'].values()))

    def test_bounds_and_build(self):
        for folder in ('final-bounds','final-contiguous'):
            report=read(DATA/folder/'report.json')
            self.assertTrue(report['passed'] and report['reference']['identical'])
            self.assertEqual(len(report['cases']),16)
        artifact=ROOT/'firmware/development/esp32c3-flac-depths'
        manifest=read(artifact/'manifest.json');app=(artifact/'app.bin').read_bytes()
        self.assertEqual(sha(app),manifest['app_sha256'])
        self.assertEqual(sha((artifact/'sdkconfig').read_bytes()),manifest['sdkconfig_sha256'])
        before=read(ROOT/'tests/results/esp32c3-flac-bounds-20261005/verify/build.json')
        after=read(DATA/'verify/build.json')
        for section in ('.iram0.text','.dram0.data','.dram0.bss','.rtc.data'):
            self.assertEqual(before['sections'][section],after['sections'][section])
        for name in ('yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
                     'idf/esp32c3-oled-native/components/custom_flac/custom_flac_adapter.cpp'):
            self.assertEqual(after['source_sha256'][name],read(DATA/'final-matrix/report.json')['sources'][name])

    def test_hardware_failures_are_retained(self):
        report=read(DATA/'terminal/report.json')
        cases=report['cases']
        playback=[c for c in cases if c['name'].endswith(':play-to-eof')]
        self.assertEqual(len(playback),16)
        self.assertEqual(sum(c['result']=='FAIL' for c in playback),4)
        self.assertTrue(all('side-block8192' in c['name'] for c in playback if c['result']=='FAIL'))
        for suffix in (':eof-recovery',':stop-recovery'):
            recovery=[c for c in cases if c['name'].endswith(suffix)]
            self.assertEqual(len(recovery),16)
            self.assertTrue(all(c['result']=='PASS' for c in recovery))
        self.assertEqual(next(c for c in cases if c['name']=='runtime-health')['result'],'FAIL')
        rows=json.loads(gzip.decompress((DATA/'terminal/performance.json.gz').read_bytes()))
        self.assertTrue(any('allocation failed:' in r['line'] for r in rows))
        self.assertTrue(any('MCAUSE=0xdeadc0de' in r['line'] for r in rows))
        self.assertTrue(any('busy=100.0%' in r['line'] for r in rows))
        self.assertFalse(any(re.match(r'^(ESP-ROM:|rst:)',r['line']) for r in rows))
        ota=read(DATA/'ota/report.json')
        self.assertTrue(all(c['result']=='PASS' for c in ota['cases']))
        artifact=read(ROOT/'firmware/development/esp32c3-flac-depths/manifest.json')
        self.assertTrue(artifact['hardware_tested'])
        self.assertFalse(artifact['production_qualified'])


if __name__=='__main__':unittest.main()
