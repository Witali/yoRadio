"""Replay saved receive-credit observations, including all failed load gates."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-receive-credit-20261004'
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from load_windows import summarize
from ota_diagnostic import serial_health
from common import Failure, check_recovery_heap, check_playback, check_cpu
from public_streams import metrics as public_metrics


def read(name):
    return json.loads((DATA/name).read_text())


class ReceiveCreditEvidence(unittest.TestCase):
    def test_files_and_runner_source_hashes(self):
        manifest = read('manifest.json')
        self.assertFalse(manifest['production_qualified'])
        for name,expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(),expected,name)
        for run,sources in [('baseline','baseline-sources'),('receive','sources'),('ota','sources'),
                            ('https-after-load','control-sources'),('unpaced','control-sources')]:
            for name,expected in read(run+'/report.json')['test_sources_sha256'].items():
                self.assertEqual(hashlib.sha256((DATA/sources/name).read_bytes()).hexdigest(),expected,name)

    def test_saved_summaries_recompute_inside_actual_windows(self):
        for run in ('baseline','receive'):
            result = summarize(*(read(run+'/'+name+'.json') for name in ('report','status','performance')))
            saved = read(run+'/summary.json')
            self.assertEqual(result['cases'],saved['cases'])
            for name,expected in saved['input_sha256'].items():
                self.assertEqual(hashlib.sha256((DATA/run/name).read_bytes()).hexdigest(),expected)
            for case in result['cases']:
                self.assertGreaterEqual(case['window']['seconds'],180)
                self.assertEqual(case['webui']['audio_active'],case['webui']['samples'])
                self.assertLess(case['webui']['ranges']['request_ms']['max'],2000)
                for metric in ('cpu','network','receive'):
                    for sample in case[metric]['samples']:
                        self.assertLess(sample['sample_at'],case['window']['end'])
                        self.assertGreaterEqual(sample['sample_at'],case['window']['start'])

    def test_baseline_failures_and_corrupt_cpu_line_are_preserved(self):
        cases = read('baseline/report.json')['cases']
        failures = [r for r in cases if r['name'].startswith('cpu-under-http-load:')]
        self.assertEqual(len(failures),3)
        self.assertEqual([r['result'] for r in failures],['FAIL']*3)
        self.assertEqual([r['reason'] for r in failures],[
            'Progressive heap loss during continuous playback',
            'Incomplete CPU/heap evidence',
            'Progressive heap loss during continuous playback'])
        vorbis = read('baseline/summary.json')['cases'][1]
        self.assertTrue(any('Incomplete' in issue for issue in vorbis['issues']))
        for case in read('baseline/summary.json')['cases']:
            self.assertFalse(case['receive']['available'])

    def test_idle_heap_recovery_is_separate_from_load_outcome(self):
        for run in ('baseline','receive'):
            cases = read(run+'/report.json')['cases']
            idle = [b for b in read(run+'/status.json') if b['case']=='settled-idle']
            rows = read(run+'/performance.json')
            for index,case in enumerate(c for c in cases if c['name'].startswith('load-idle-baseline:')):
                after = next(c for c in cases if c['name'] == case['name'].replace('baseline','recovery',1))
                self.assertEqual(case['result'],'PASS')
                window=idle[index*2+1]
                recovered=[]
                for row in rows:
                    match=re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)',row['line'])
                    if match and window['started_at'] <= row['at'] < window['ended_at']:
                        recovered.append(dict(zip(('heap','largest','tasks'),map(int,match.groups()))))
                try:
                    check_recovery_heap(case['evidence']['samples'],recovered)
                except Failure as error:
                    self.assertEqual(after['result'],'FAIL')
                    self.assertEqual(after['reason'],str(error))
                else:
                    self.assertEqual(after['result'],'PASS')
                    self.assertEqual(after['evidence']['samples'],recovered)
            self.assertEqual(cases[-1]['name'],'restore-board')
            self.assertEqual(cases[-1]['result'],'PASS')
            self.assertEqual(serial_health(read(run+'/performance.json'))['result'],'PASS')
        vorbis=next(c for c in read('receive/report.json')['cases']
                    if c['name']=='load-idle-recovery:stress-vorbis-48000-2ch-16bit-200s')
        self.assertEqual(vorbis['result'],'FAIL')
        self.assertEqual(vorbis['reason'],'Persistent largest loss: 55296.0 bytes')

    def test_receive_credit_exists_and_is_not_a_ram_allocation_count(self):
        for case in read('receive/summary.json')['cases']:
            self.assertTrue(case['receive']['available'])
            self.assertGreaterEqual(len(case['receive']['samples']),30)
            self.assertGreater(case['receive']['ranges']['uncredited']['max'],0)
            self.assertFalse(any('receive:' in issue for issue in case['issues']))
            for sample in case['receive']['samples']:
                self.assertEqual(sample['uncredited'],sample['maximum']-sample['window'])
        before,after = read('build-delta.json')
        for key in ('.iram0.text','.dram0.data','.dram0.bss'):
            self.assertEqual(before['sections'][key],after['sections'][key])
        self.assertEqual(after['sampler']['s_snapshot']-before['sampler']['s_snapshot'],8)

    def test_installed_image_identity_and_ota_preservation(self):
        build = read('netrx-build.json')
        self.assertEqual(read('receive/report.json')['board']['app_elf_sha256'],build['elf_sha256'])
        case = read('ota/report.json')['cases'][0]
        self.assertEqual(case['result'],'PASS')
        for key in ('wifi_unchanged','playlist_unchanged','settings_unchanged'):
            self.assertTrue(case['evidence'][key])
        self.assertEqual(case['evidence']['after']['app_elf_sha256'],build['elf_sha256'])
        self.assertEqual(build['sdkconfig_sha256'],read('baseline/report.json')['config']['sha256'])
        config = (DATA/'physical/sdkconfig').read_text()
        self.assertIn('CONFIG_YORADIO_NETWORK_HEAP_PROFILE=y',config)
        self.assertNotIn('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y',config)

    def test_https_from_fragmented_heap_preserves_failed_gate_and_recovery(self):
        report=read('https-after-load/report.json')
        self.assertEqual([c['result'] for c in report['cases']],['PASS','FAIL','PASS','PASS'])
        self.assertEqual(report['cases'][0]['evidence']['samples'][0]['largest'],59392)
        name='groovesalad-64-aac';window=report['windows'][name]
        states=next(b['samples'] for b in read('https-after-load/status.json') if b['case']==name)
        rows=read('https-after-load/performance.json')
        selected=[r for r in rows if window['start']<=r['at']<window['end']]
        spec=report['reference_probes'][name]['spec']
        check_playback(states,spec)
        self.assertEqual(spec['rate'],44100)
        self.assertEqual(spec['channels'],2)
        self.assertEqual(spec['profile'],'HE-AAC')
        with self.assertRaisesRegex(Failure,'Progressive heap loss during continuous playback'):
            public_metrics(states,selected,spec,180,window['start'],window['end'])
        check_recovery_heap(report['cases'][0]['evidence']['samples'],report['cases'][2]['evidence']['samples'])
        self.assertTrue(report['cases'][2]['evidence']['no_unexpected_resets'])
        for key in ('wifi_unchanged','playlist_unchanged','settings_unchanged','stopped_state_restored'):
            self.assertTrue(report['cases'][3]['evidence'][key])

    def test_unpaced_control_uses_same_image_files_and_unchanged_gates(self):
        report=read('unpaced/report.json');paced=read('receive/report.json')
        self.assertEqual(report['fixture_hashes'],paced['fixture_hashes'])
        self.assertEqual(report['board']['app_elf_sha256'],paced['board']['app_elf_sha256'])
        self.assertTrue(report['server_options']['unpaced_files'])
        self.assertEqual(report['load_options']['seconds'],60)
        self.assertEqual(len(report['cases']),10)
        self.assertEqual({c['result'] for c in report['cases']},{'PASS'})
        self.assertTrue(all(e['pacing_ratio'] is None for e in report['server_events']))
        rows=read('unpaced/performance.json');status=read('unpaced/status.json')
        recomputed=summarize(report,status,rows)
        self.assertEqual(recomputed['cases'],read('unpaced/summary.json')['cases'])
        for case in recomputed['cases']:
            start,end=case['window']['start']+10,case['window']['end']
            value=check_cpu([r for r in rows if start<=r['at']<end],start=start,end=end)
            for key,expected in value.items():
                self.assertAlmostEqual(case['acceptance']['evidence'][key],expected)
            self.assertEqual(case['issues'],[])
            self.assertEqual(case['webui']['samples'],case['webui']['audio_active'])
        self.assertEqual(serial_health(rows)['result'],'PASS')


if __name__ == '__main__':
    unittest.main()
