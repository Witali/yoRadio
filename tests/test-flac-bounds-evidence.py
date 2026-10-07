"""Verify the FLAC overread reproduction, repaired PCM and saved build."""
import hashlib
import gzip
import json
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-flac-bounds-20261005'
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from common import check_cpu,check_playback,check_recovery_heap,fixtures
from ota_diagnostic import serial_health


def read(path):
    return json.loads(path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes()))
def sha(data): return hashlib.sha256(data).hexdigest()


class FlacBoundsEvidence(unittest.TestCase):
    def test_105_control_switches_and_every_idle_checkpoint(self):
        folder=DATA/'switch-control'
        report=read(folder/'report.json');switch=read(folder/'switching.json')
        self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
        self.assertEqual(report['cases'][0]['evidence'],dict(cycles=15,station_changes=105))
        self.assertEqual(switch['failures'],[])
        self.assertEqual(len(switch['checkpoints']),15)
        for checkpoint in switch['checkpoints']:
            check_recovery_heap(switch['checkpoints'][0],checkpoint)
            self.assertTrue(all(v['largest']==114688 and v['tasks']==17 for v in checkpoint))
        specs=fixtures()
        windows=[w for w in read(folder/'status.json') if w['case'].startswith('switch:')]
        self.assertEqual(len(windows),105)
        for w in windows:
            check_playback(w['samples'],specs[w['case'].split(':',2)[2]])
        rows=read(folder/'performance.json')
        self.assertEqual(serial_health(rows)['result'],'PASS')
        self.assertFalse(any(r['line'].startswith(('ESP-ROM:','rst:')) for r in rows))

    def test_retained_bytes(self):
        manifest=read(DATA/'manifest.json')
        self.assertEqual(set(manifest),{p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p.name!='manifest.json'})
        for path,value in manifest.items():
            data=(DATA/path).read_bytes()
            self.assertEqual(len(data),value['bytes'],path)
            self.assertEqual(sha(data),value['sha256'],path)

    def test_reproduced_overread_and_reference_pcm(self):
        before=read(DATA/'before/report.json')
        self.assertFalse(before['passed'])
        self.assertEqual(before['cases']['full']['result'],'PASS')
        failed=[name for name,case in before['cases'].items() if case['result']=='FAIL']
        self.assertEqual(len(failed),12)
        for name in failed:
            self.assertIn('AddressSanitizer: heap-buffer-overflow',(DATA/'before'/(name+'.log')).read_text())
        for folder in ('after','arduino-all'):
            report=read(DATA/folder/'report.json')
            self.assertTrue(report['passed'])
            self.assertEqual(len(report['cases']),16)
            self.assertTrue(all(c['result']=='PASS' for c in report['cases'].values()))
            self.assertIn('frames=528000',report['cases']['full']['output'])
            for name in ('tail-1','tail-2','tail-3'):
                self.assertIn('result=-12 frames=525312',report['cases'][name]['output'])
            self.assertEqual(report['edge_cases'],'PASS')
            self.assertTrue(report['reference']['identical'])
            self.assertEqual(report['reference']['bytes'],2112000)
            self.assertEqual(report['reference']['sha256'],'a063803277ddaaac6ebb459f70c5d87a5cb35cda786a616ce43805cfb783fb20')
            self.assertEqual(report['fixture_sha256'],before['fixture_sha256'])
        for folder in ('before','after','arduino-all'):
            for path,digest in read(DATA/folder/'report.json')['sources'].items():
                self.assertEqual(sha((DATA/folder/'sources'/path).read_bytes()),digest)
        comparison=read(DATA/'pcm-comparison.json')
        self.assertEqual(comparison['before'],comparison['after'])
        self.assertEqual(comparison['before'],comparison['arduino-all'])
        self.assertEqual(comparison['after']['sha256'],read(DATA/'after/report.json')['reference']['sha256'])

    def test_ota_preserves_settings_and_installs_candidate(self):
        folder=DATA/'ota';r=read(folder/'report.json')
        self.assertTrue(all(c['result']=='PASS' for c in r['cases']))
        evidence=r['cases'][0]['evidence']
        self.assertEqual(evidence['after']['app_elf_sha256'],read(DATA/'verify/build.json')['elf_sha256'])
        for key in ('wifi_unchanged','playlist_unchanged','settings_unchanged'):self.assertTrue(evidence[key])
        self.assertEqual(serial_health(read(folder/'performance.json'))['result'],'PASS')

    def test_physical_truncation_and_natural_memory_recovery(self):
        folder=DATA/'faults';report=read(folder/'report.json')
        self.assertEqual(report['board']['app_elf_sha256'],read(DATA/'verify/build.json')['elf_sha256'])
        self.assertEqual(len(report['cases']),15)
        self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
        cases={c['name']:c for c in report['cases']}
        baseline=cases['idle-before']['evidence']['samples']
        for name in ('flac-prefix-32','flac-prefix-4096','flac-tail-1'):
            self.assertTrue(cases[name+':bounded-eof']['evidence']['truncation_reported'])
            self.assertTrue(cases[name+':bounded-eof']['evidence']['stopped'])
            values=cases[name+':natural-recovery']['evidence']['samples']
            check_recovery_heap(baseline,values)
            self.assertTrue(all(v['largest']==114688 and v['tasks']==17 for v in values))
            for codec in ('lc-48000-stereo','flac-level8'):
                self.assertEqual(cases[name+':recover:'+codec]['evidence']['rate'],48000)
                self.assertEqual(cases[name+':recover:'+codec]['evidence']['channels'],2)
        rows=read(folder/'performance.json')
        self.assertEqual(serial_health(rows)['result'],'PASS')
        self.assertGreaterEqual(sum('FLAC decode error -12' in r['line'] for r in rows),3)

    def test_load_cpu_memory_and_final_board(self):
        summary=read(DATA/'summary.json')
        for name in ('load-before','load-after'):
            folder=DATA/name;report=read(folder/'report.json')
            self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
            case=next(c for c in report['cases'] if c['name'].startswith('cpu-'))
            self.assertEqual(case,summary[name]['acceptance'])
            self.assertEqual(report['board']['app_elf_sha256'],summary[name]['image'])
            window=next(w for w in read(folder/'status.json') if w['case'].startswith('load:'))
            rows=[r for r in read(folder/'performance.json') if window['started_at']+10<=r['at']<=window['ended_at']]
            result=check_cpu(rows,start=window['started_at']+10,end=window['ended_at'])
            for key,value in result.items():self.assertAlmostEqual(value,case['evidence'][key])
            timings=[tuple(map(int,m.groups())) for r in rows
                     if (m:=re.search(r'PERF FLAC: window (\d+) ms, audio (\d+) ms, decode (\d+) ms',r['line']))]
            self.assertEqual(len(timings),summary[name]['decode_windows'])
            self.assertAlmostEqual(100*sum(t[2] for t in timings)/sum(t[1] for t in timings),summary[name]['decode_per_audio_percent'])
            check_recovery_heap(report['cases'][0]['evidence']['samples'],report['cases'][2]['evidence']['samples'])
            self.assertEqual(serial_health(read(folder/'performance.json'))['result'],'PASS')
        final=read(DATA/'board-final.json')
        self.assertEqual(final['image']['app_elf_sha256'],read(DATA/'verify/build.json')['elf_sha256'])
        self.assertTrue(final['status']['audio'])

    def test_retained_runner_dependencies(self):
        used=('common','run','diagnostic','flac_truncation','memory','ota','ota_transition','ota_diagnostic','serial_lines','server','fixtures','generate_stress')
        for folder in ('switch-control','load-before','ota','faults','load-after'):
            for path,digest in read(DATA/folder/'report.json')['test_sources_sha256'].items():
                if Path(path).stem in used:
                    self.assertEqual(sha((DATA/'runner-sources'/digest/Path(path).name).read_bytes()),digest)

    def test_candidate_identity_and_unchanged_ram_and_aac(self):
        build=read(DATA/'verify/build.json')
        control=read(ROOT/'firmware/development/esp32c3-custom-terminal/manifest.json')
        for key in ('types','features','codec_sha256','layout_sha256'):
            self.assertEqual(build[key],control[key])
        for section in ('.iram0.text','.dram0.data','.dram0.bss'):
            self.assertEqual(build['sections'][section],control['sections'][section])
        artifact=ROOT/'firmware/development/esp32c3-flac-bounds'
        app=(artifact/'app.bin').read_bytes()
        self.assertEqual(sha(app),build['app_sha256'])
        self.assertEqual(app[176:208].hex(),build['elf_sha256'])
        self.assertEqual(sha((artifact/'sdkconfig').read_bytes()),build['sdkconfig_sha256'])
        for path,digest in build['source_sha256'].items():
            self.assertEqual(sha((DATA/'verify/sources'/path).read_bytes()),digest)
        for name in ('flac_decoder.cpp','flac_decoder.h'):
            path='yoRadio/src/audioI2S/flac_decoder/'+name
            self.assertEqual(build['source_sha256'][path],read(DATA/'after/report.json')['sources'][path])


if __name__=='__main__':unittest.main()
