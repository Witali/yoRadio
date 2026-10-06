"""Replay radio LPC statistics, exact PCM evidence and unmodified board outcomes."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
import gzip

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-radio-flac-20261006'
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from summarize_radio_flac import read, summarize
from analyze_radio_flac import summarize_trace


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RadioEvidence(unittest.TestCase):
    def test_integrity_and_excluded_music(self):
        manifest=read(DATA/'manifest.json')
        files={p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
               if p.is_file() and p != DATA/'manifest.json'}
        self.assertEqual(set(manifest),files)
        for name,info in manifest.items():
            path=DATA/name
            self.assertEqual((path.stat().st_size,sha(path)),(info['bytes'],info['sha256']),name)
            self.assertNotIn(path.suffix,('.aac','.wav','.flac','.pcm','.bin'))
        for name,digest in read(DATA/'provenance.json')['tools_sha256'].items():
            self.assertEqual(sha(DATA/'sources'/name),digest)

    def test_twenty_identical_pcm_pairs_and_sources(self):
        manifest=read(DATA/'recordings/manifest.json')
        self.assertFalse(manifest['failures'])
        self.assertEqual(len(manifest['captures']),10)
        self.assertEqual(len(manifest['fixtures']),20)
        groups={}
        for spec in manifest['fixtures']:
            groups.setdefault(spec['station'],{})[spec['max_lpc_order']]=spec
            self.assertEqual((spec['seconds'],spec['rate'],spec['channels'],spec['bits']),
                             (120,44100,2,24))
        self.assertEqual(len(groups),10)
        for pair in groups.values():
            self.assertEqual(set(pair),{12,32})
            for key in ('pcm24_sha256','pcm24_bytes','pcm_sha256','pcm_bytes','source_capture_sha256'):
                self.assertEqual(pair[12][key],pair[32][key])
        experiment=read(DATA/'board/experiment.json')
        self.assertEqual(sha(DATA/'recordings/manifest.json'),experiment['fixture_manifest_sha256'])

    def test_bitstream_orders_and_sixty_exact_decodes(self):
        fixtures={s['name']:s for s in read(DATA/'recordings/manifest.json')['fixtures']}
        analysis=read(DATA/'analysis/report.json')
        host=read(DATA/'host-pcm/report.json')
        build=read(DATA/'firmware/build.json')
        for folder,report in (('analysis',analysis),('host-pcm',host)):
            self.assertTrue(report['passed'] and report['sanitizers'])
            for name,digest in report['sources'].items():
                self.assertEqual(sha(DATA/folder/'sources'/name),digest)
                if name in build['source_sha256']:
                    self.assertEqual(digest,build['source_sha256'][name])
        self.assertEqual(sha(DATA/'analysis/observed.cpp'),analysis['observed_source_sha256'])
        self.assertEqual({c['name'] for c in analysis['cases']},set(fixtures))
        for case in analysis['cases']:
            spec=fixtures[case['name']]
            stats=summarize_trace(gzip.decompress((DATA/'analysis'/(case['name']+'.log.gz')).read_bytes()).decode())
            # JSON stores histogram keys as strings; the parser uses integers.
            self.assertEqual(json.loads(json.dumps(stats)),{key:case[key] for key in stats})
            self.assertLessEqual(stats['max_order'],spec['max_lpc_order'])
            self.assertEqual(stats['channel_samples'],spec['pcm_bytes']//2)
            self.assertEqual(case['pcm_sha256'],spec['pcm_sha256'])
            self.assertEqual(case['fixture_sha256'],spec['sha256'])
        total=0
        self.assertEqual({c['name'] for c in host['cases']},set(fixtures))
        for case in host['cases']:
            self.assertTrue(case['reference']['known_pcm_identical'])
            self.assertEqual(set(case['variants']),{'segmented','contiguous','adapter'})
            for variant in case['variants'].values():
                self.assertEqual(variant['result'],'PASS')
                self.assertTrue(variant['identical'])
                self.assertEqual((variant['sha256'],variant['bytes']),
                                 (fixtures[case['name']]['pcm_sha256'],fixtures[case['name']]['pcm_bytes']))
                total+=1
        self.assertEqual(total,60)

    def test_physical_statistics_replay_and_original_outcomes(self):
        fixtures=read(DATA/'recordings/manifest.json')
        analysis=read(DATA/'analysis/report.json')
        build=read(DATA/'firmware/build.json')
        for folder in read(DATA/'provenance.json')['board_folders']:
            report=read(DATA/folder/'report.json')
            self.assertEqual(report['board']['app_elf_sha256'],build['elf_sha256'])
            self.assertEqual(report['config']['sha256'],sha(DATA/'firmware/sdkconfig'))
            for name,digest in report['test_sources_sha256'].items():
                self.assertEqual(sha(DATA/'sources'/name),digest)
            result=summarize(DATA/folder,fixtures,analysis)
            self.assertEqual(result,read(DATA/folder/'summary.json'))
            original={c['name']:c for c in report['cases']}
            loads={n for n in original if n.startswith('cpu-under-http-load:')}
            self.assertEqual({'cpu-under-http-load:'+c['name'] for c in result['cases']},loads)
            if folder=='board':
                self.assertEqual(len(loads),20)
                self.assertEqual(len(result['pairs']),10)
            for case in result['cases']:
                self.assertEqual(case['original'],original['cpu-under-http-load:'+case['name']])
                self.assertFalse(case['malformed_cpu'])
                for gap in case['suspected_gaps']:
                    self.assertNotIn(gap['at'],[w['at'] for w in case['cpu_intervals']])
                self.assertEqual(case['cpu']['excluded_gap_seconds'],sum(g['seconds'] for g in case['suspected_gaps']))
                self.assertGreater(case['cpu']['observed_seconds'],85)
            self.assertEqual(original['restore-board']['result'],'PASS')


if __name__ == '__main__':
    unittest.main()
