"""Verify retained physical timeout evidence without hiding the original failures."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-station-timeout-20261007'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from connection_retry import check_runtime
from common import check_recovery_heap


def read(name):
    return json.loads((DATA/name).read_text())


class StationTimeoutEvidence(unittest.TestCase):
    def test_archive_and_runner_sources(self):
        manifest = read('manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA/'manifest.json'})
        for name, record in manifest.items():
            data = (DATA/name).read_bytes()
            self.assertEqual(dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), record)
        for folder in ('baseline','ota','ota-timeout','board-timeout','board-final-tests'):
            for name, digest in read(folder+'/report.json')['test_sources_sha256'].items():
                data = (DATA/'runner-sources'/digest/Path(name).name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_original_failures_and_final_outcomes(self):
        before = read('baseline/report.json')
        self.assertEqual(next(c for c in before['cases'] if c['name']=='recover-hev2')['result'], 'FAIL')
        self.assertEqual(len(before['server_events']['recover-hev2']), 1)
        first = read('board-timeout/report.json')
        self.assertEqual(next(c for c in first['cases'] if c['name']=='runtime')['reason'],
                         'Unexpected reboot during playback')
        final = read('board-final-tests/report.json')
        expected = {'idle-before','recover-lc','recover-hev2','watchdog-off','stop','switch',
                    'disable-pending','timeout-3','timeout-10','timeout-stall','settings-persistence',
                    'idle-after','stop-recovery','runtime','restore-board'}
        self.assertEqual({c['name'] for c in final['cases']}, expected)
        self.assertTrue(all(c['result']=='PASS' for c in final['cases']))
        self.assertEqual(check_runtime(read('board-final-tests/performance.json'), final['planned_reboots']),
                         dict(planned_software_reboots=1))
        cases = {c['name']: c['evidence'] for c in final['cases']}
        check_recovery_heap(cases['idle-before']['samples'], cases['idle-after']['samples'])
        for seconds in (3,10):
            ev = cases['timeout-'+str(seconds)]
            self.assertTrue(seconds-.5 <= ev['observed_seconds'] <= seconds+1.5)
            requests = final['server_events']['timeout-'+str(seconds)]
            self.assertTrue(all(e['requested_at']-requests[0]['requested_at'] < seconds for e in requests))

    def test_images_ota_and_final_playback(self):
        for variant in ('esp32c3-connect-retry','esp32c3-station-timeout'):
            image = (ROOT/'firmware/development'/variant/'app.bin').read_bytes()
            build = read('firmware/'+variant+'/manifest.json')
            self.assertEqual(hashlib.sha256(image).hexdigest(), build['app_sha256'])
            self.assertEqual(image[176:208].hex(), build['elf_sha256'])
            self.assertFalse(build['production_qualified'])
        for folder in ('ota','ota-timeout'):
            self.assertTrue(all(c['result']=='PASS' for c in read(folder+'/report.json')['cases']))
        self.assertEqual(read('ota-timeout/report.json')['expected_new_settings'], dict(stationtimeout=10))
        final = read('board-final.json')
        self.assertTrue(final['status']['audio'])
        self.assertEqual(final['stationtimeout'], 10)
        self.assertEqual(final['info']['app_elf_sha256'],
                         read('firmware/esp32c3-station-timeout/manifest.json')['elf_sha256'])
        self.assertTrue(final['served_script_matches_artifact'])


if __name__ == '__main__':
    unittest.main()
