"""Replay the physical natural-EOF memory comparison, including its failures."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tests/results/esp32c3-custom-terminal-20261005'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from common import check_cpu, check_recovery_heap
from summarize_terminal_memory import summarize
from summarize_codec_sequence import summarize as summarize_sequence
from ota_diagnostic import serial_health


def read(path):
    data=path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes())
    return json.loads(data)
def sha(data):return hashlib.sha256(data).hexdigest()


class CustomTerminalEvidence(unittest.TestCase):
    def test_exact_bytes_and_host_ownership(self):
        manifest=read(DATA/'manifest.json')
        files={p.relative_to(DATA).as_posix() for p in DATA.rglob('*') if p.is_file() and p.name!='manifest.json'}
        self.assertEqual(files,set(manifest))
        for path,value in manifest.items():
            data=(DATA/path).read_bytes()
            self.assertEqual(len(data),value['bytes'],path)
            self.assertEqual(sha(data),value['sha256'],path)
        host=read(DATA/'host/report.json')
        self.assertTrue(host['passed']);self.assertEqual(host['cases'],17)
        for path,digest in host['source_sha256'].items():
            self.assertEqual(sha((DATA/'host/sources'/path).read_bytes()),digest)
        self.assertIn('queued PCM unchanged',(DATA/'host/run.log').read_text())

    def test_old_eof_retention_and_new_recovery(self):
        for folder in ('flac-eof-before','terminal-after'):
            report=read(DATA/folder/'report.json')
            summary=summarize(report)
            self.assertEqual(summary,read(DATA/folder/'summary.json'))
            cases={c['name']:c for c in report['cases']}
            if folder=='flac-eof-before':
                failures={c['name'] for c in report['cases'] if c['result']!='PASS'}
                self.assertEqual(failures,{'flac-level8:auto:eof-recovery','flac-level8:flac:eof-recovery'})
                self.assertEqual(len(summary['streams']),2)
                for stream in summary['streams'].values():
                    self.assertGreater(stream['eof_heap_loss'],53000)
                    self.assertEqual(stream['eof_largest_loss'],51200)
                    self.assertEqual(stream['stop_result'],'PASS')
            else:
                self.assertEqual(len(report['cases']),37)
                self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
                self.assertEqual(len(summary['streams']),6)
                for name,stream in summary['streams'].items():
                    self.assertLessEqual(stream['eof_heap_loss'],118)
                    self.assertEqual(stream['eof_largest_loss'],0)
                    self.assertEqual(stream['eof']['largest'],114688)
                    self.assertEqual(stream['eof']['tasks'],17)
                    check_recovery_heap(cases[name+':idle-before']['evidence']['samples'],
                                        cases[name+':idle-without-stop']['evidence']['samples'])
            self.assertEqual(serial_health(read(DATA/folder/'performance.json'))['result'],'PASS')

    def test_candidate_and_ota_identity(self):
        build=read(DATA/'verify/build.json')
        baseline=read(ROOT/'firmware/development/esp32c3-output-dma-prefill/manifest.json')
        for key in ('types','features'):
            self.assertEqual(build[key],baseline[key])
        for section in ('.dram0.bss','.dram0.data','.iram0.text'):
            self.assertEqual(build['sections'][section],baseline['sections'][section])
        artifact=ROOT/'firmware/development/esp32c3-custom-terminal'
        app=(artifact/'app.bin').read_bytes()
        self.assertEqual(sha(app),build['app_sha256'])
        self.assertEqual(app[176:208].hex(),build['elf_sha256'])
        self.assertEqual(sha((artifact/'sdkconfig').read_bytes()),build['sdkconfig_sha256'])
        config=(artifact/'sdkconfig').read_text()
        self.assertIn('CONFIG_YORADIO_FLAC_DECODER_CUSTOM=y',config)
        self.assertNotIn('CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y',config)
        self.assertNotIn('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y',config)
        self.assertTrue(read(artifact/'manifest.json')['hardware_tested'])
        self.assertFalse(read(artifact/'manifest.json')['production_qualified'])
        for path,digest in build['source_sha256'].items():
            self.assertEqual(sha((DATA/'verify/sources'/path).read_bytes()),digest)
        ota=read(DATA/'ota-terminal/report.json')
        self.assertTrue(all(c['result']=='PASS' for c in ota['cases']))
        row=ota['cases'][0]['evidence']
        self.assertEqual(row['after']['app_elf_sha256'],build['elf_sha256'])
        self.assertTrue(row['wifi_unchanged'] and row['settings_unchanged'] and row['playlist_unchanged'])
        self.assertEqual(serial_health(read(DATA/'ota-terminal/performance.json'))['result'],'PASS')

    def test_opus_control_retains_initial_failure(self):
        report=read(DATA/'opus-prefill-settle/report.json')
        cases={c['name']:c for c in report['cases']}
        self.assertEqual(cases['initial-load']['result'],'FAIL')
        self.assertEqual(cases['initial-load']['reason'],'Progressive heap loss during continuous playback')
        self.assertEqual(cases['settled-load']['result'],'PASS')
        window=report['windows'][-1]
        rows=[r for r in read(DATA/'opus-prefill-settle/performance.json') if window['start']<=r['at']<=window['end']]
        result=check_cpu(rows,start=window['start'],end=window['end'])
        for key,value in result.items():self.assertAlmostEqual(value,cases['settled-load']['evidence'][key])
        self.assertLess(cases['settled-load']['evidence']['max_http_ms'],150)
        check_recovery_heap(cases['idle-before']['evidence'],cases['idle-after']['evidence'])

    def test_long_sequence_retains_fragmentation(self):
        folder=DATA/'load-sequence'
        report=read(folder/'report.json')
        result=summarize_sequence(report,read(folder/'status.json'),read(folder/'performance.json'))
        self.assertEqual(result,read(DATA/'sequence-summary.json'))
        self.assertEqual(result['image'],read(DATA/'verify/build.json')['elf_sha256'])
        self.assertEqual(report['load_options'],dict(seconds=180,idle_recovery=True))
        self.assertEqual(len(result['cases']),3)
        mp3=result['cases']['stress-mp3-48000-2ch-16bit-200s']
        self.assertEqual(mp3['original_acceptance']['reason'],'Progressive heap loss during continuous playback')
        self.assertEqual(mp3['recovery_from_first']['result'],'PASS')
        vorbis=result['cases']['stress-vorbis-48000-2ch-16bit-200s']
        self.assertEqual(vorbis['original_acceptance']['result'],'PASS')
        self.assertEqual(vorbis['idle_after']['largest'],94208)
        self.assertEqual(vorbis['recovery_from_first']['result'],'FAIL')
        self.assertEqual(vorbis['recovery_from_first']['reason'],'Persistent largest loss: 20480.0 bytes')
        opus=result['cases']['stress-opus-48000-2ch-16bit-200s']
        self.assertEqual(opus['original_acceptance']['reason'],'WebUI response exceeded 2 s')
        self.assertAlmostEqual(opus['maximum_http_ms'],2204,places=3)
        self.assertEqual(opus['recovery_from_previous']['result'],'PASS')
        self.assertEqual(opus['recovery_from_first']['result'],'FAIL')
        self.assertEqual(opus['after_40_seconds']['result'],'FAIL')
        self.assertAlmostEqual(opus['observed_after_40_seconds']['audio_wall_ratio'],0.8043344136273056)
        self.assertEqual(report['cases'][-1]['name'],'restore-board')
        self.assertEqual(report['cases'][-1]['result'],'PASS')
        self.assertEqual(serial_health(read(folder/'performance.json'))['result'],'PASS')
        final=read(DATA/'board-final.json')
        self.assertEqual(final['image']['app_elf_sha256'],result['image'])
        self.assertTrue(final['status']['audio'])

    def test_retained_runtime_dependencies(self):
        used=('common','run','diagnostic','terminal_memory','pool_settle','memory','ota',
              'ota_transition','ota_diagnostic','serial_lines','server','fixtures','generate_stress')
        for folder in ('opus-prefill-settle','flac-eof-before','ota-terminal','terminal-after','load-sequence'):
            for path,digest in read(DATA/folder/'report.json')['test_sources_sha256'].items():
                if Path(path).stem in used:
                    self.assertEqual(sha((DATA/'runner-sources'/digest/Path(path).name).read_bytes()),digest)


if __name__=='__main__':unittest.main()
