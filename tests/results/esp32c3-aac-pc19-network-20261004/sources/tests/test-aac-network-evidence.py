"""Retain the scope and failures of the physical PC19 qualification run."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-aac-pc19-network-20261004'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from run_aac_fill import parse_log
from ota_diagnostic import serial_health
from public_streams import metrics


def read(name):
    return json.loads((DATA/name).read_text())


class NetworkEvidence(unittest.TestCase):
    def test_byte_provenance(self):
        manifest = read('manifest.json')
        self.assertFalse(manifest['production_qualified'])
        for name, expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(), expected, name)
        for name, expected in read('matrix/report.json')['test_sources_sha256'].items():
            self.assertEqual(hashlib.sha256((DATA/'sources'/name).read_bytes()).hexdigest(), expected, name)

    def test_physical_build_and_image(self):
        build = read('build.json')
        self.assertEqual(build['types'], {'native_aac_decoder':204, 'aac_high_owner_t':32744,
                                         'aac_high_runtime_t':160})
        config = (DATA/'physical/sdkconfig').read_text()
        for feature in build['features']:
            self.assertIn('CONFIG_YORADIO_'+feature+'=y\n', config)
        self.assertIsNone(re.search(r'^CONFIG_YORADIO_(?:QEMU\w*|DEEP_SLEEP_CLOCK)=y$', config, re.M))
        artifact = ROOT/'firmware/development/esp32c3-aac-pc19-network'
        current = json.loads((artifact/'manifest.json').read_text())
        if current['app_sha256'] == build['app_sha256']:
            self.assertEqual(hashlib.sha256((artifact/'app.bin').read_bytes()).hexdigest(), build['app_sha256'])
        before, after = read('build-delta.json')
        self.assertEqual(after['types']['native_aac_decoder']-before['types']['native_aac_decoder'],152)
        for section in ('.iram0.text','.dram0.data','.dram0.bss'):
            self.assertEqual(before['sections'][section],after['sections'][section])

    def test_qemu_pcm_continuity(self):
        parsed = parse_log((DATA/'qemu/diagnostics.log').read_text())
        saved = read('qemu/result.json')
        for key, value in parsed.items():
            self.assertEqual(saved[key], value)
        records = read('pcm-identical.json')
        self.assertEqual(sum(r['channel_samples'] for r in records),865280)
        for row in records:
            reference = gzip.decompress((ROOT/'tests/results/esp32c3-aac-fill-20261004'/
                                         (row['case']+'.pcm.gz')).read_bytes())
            self.assertEqual(row['sha256'],hashlib.sha256(reference).hexdigest())
            self.assertEqual(row['changed'],0)

    def test_physical_matrix_and_ota(self):
        cases = read('matrix/report.json')['cases']
        self.assertEqual(len(cases),20)
        self.assertEqual({r['result'] for r in cases},{'PASS'})
        switch = next(r for r in cases if r['name']=='switching-and-heap')
        self.assertEqual(switch['evidence'],{'cycles':3,'station_changes':21})
        ota = read('ota-transition/report.json')['cases'][0]
        self.assertEqual(ota['result'],'PASS')
        self.assertEqual(ota['evidence']['after']['app_elf_sha256'],read('build.json')['elf_sha256'])
        for field in ('wifi_unchanged','playlist_unchanged','settings_unchanged'):
            self.assertTrue(ota['evidence'][field])
        for folder in ('matrix','ota-transition','load','he-load-repeat'):
            rows = read(folder+'/performance.json')
            self.assertEqual(serial_health(rows)['result'],'PASS')

    def test_failed_load_gates_are_not_promoted(self):
        cases = read('load/report.json')['cases']
        failures = {r['name']:r['reason'] for r in cases if r['result']=='FAIL'}
        self.assertEqual(failures, {
            'cpu-under-http-load:he-48000-stereo':'URLError',
            **{'cpu-under-http-load:stress-'+codec+'-48000-2ch-16bit-60s':
               'Progressive heap loss during continuous playback' for codec in ('mp3','vorbis','opus')},
        })
        self.assertEqual(read('load/summary.json')['runtime_faults'],[])
        failed = next(r for r in read('load/status.json') if r['case']=='load:he-48000-stereo')
        self.assertEqual(failed['interrupted'],'URLError')
        self.assertEqual(len(failed['samples']),11)
        self.assertEqual(failed['exception_chain'],[{'type':'URLError'},{'type':'TimeoutError'}])
        repeat = read('he-load-repeat/report.json')['cases'][0]
        self.assertEqual(repeat['result'],'PASS')
        self.assertEqual(repeat['evidence']['duration'],40)

    def test_real_https_playback(self):
        report = read('public-https/report.json')
        self.assertEqual(report['seconds'],300)
        self.assertEqual({c['result'] for c in report['cases']},{'PASS'})
        case = next(c for c in report['cases'] if c['name']=='https:groovesalad-64-aac')
        name = case['name'].split(':',1)[1]
        window = report['windows'][name]
        rows = [r for r in read('public-https/performance.json')
                if window['start']<=r['at']<=window['end']]
        status = next(b['samples'] for b in read('public-https/status.json') if b['case']==name)
        actual = metrics(status,rows,case['evidence']['reference']['spec'],300,
                         window['start'],window['end'])
        for key,value in actual.items():
            self.assertEqual(case['evidence'][key],value,key)
        self.assertEqual(actual['playback']['rate'],44100)
        self.assertEqual(actual['playback']['channels'],2)
        self.assertTrue(case['evidence']['reference']['tls_verify'])


if __name__ == '__main__':
    unittest.main()
