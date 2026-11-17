"""Exercise the EOF and progress predicates against diagnostic DAC output."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


runner = Path(__file__).with_name('run-cyd-full-app-openeth.py')
spec = importlib.util.spec_from_file_location('cyd_openeth', runner)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class PcmObserverTests(unittest.TestCase):
    def test_http_timeout_names_the_request(self):
        with patch.object(probe.http.client, 'HTTPConnection') as connection:
            connection.return_value.getresponse.side_effect = TimeoutError
            with self.assertRaisesRegex(TimeoutError, 'GET /script.js timed out'):
                probe.request(1234, '/script.js')
            connection.assert_called_once_with('127.0.0.1', 1234, timeout=8)
            connection.return_value.close.assert_called_once()

    def test_static_asset_has_its_own_timeout_and_exact_body_check(self):
        asset = (probe.ROOT / 'yoRadio/data/www/script.js.gz').read_bytes()
        with patch.object(probe, 'request', return_value=asset) as request:
            self.assertEqual(probe.check_asset(1234)['bytes'], len(asset))
            request.assert_called_once_with(1234, '/script.js', timeout=probe.WEB_ASSET_TIMEOUT_SECONDS)
        with patch.object(probe, 'request', return_value=asset[:-1]):
            with self.assertRaisesRegex(RuntimeError, 'exact packaged SPIFFS asset'):
                probe.check_asset(1234)

    def test_dac_progress_excludes_driver_bytes(self):
        health = {'output_driver': {'written_bytes': 1024}}
        self.assertEqual(probe.output_progress(health, '', True), 0)
        self.assertEqual(probe.output_progress(health, '', False), 1024)
        self.assertEqual(probe.output_progress(health, 'bad CYD_OPENETH_PCM_PROGRESS frames=960\n', True), 0)
        log = 'CYD_OPENETH_PCM_PROGRESS frames=648\r\nCYD_OPENETH_PCM_PROGRESS frames=5448\r\n'
        self.assertEqual(probe.output_progress(health, log, True), 5448)

    def test_pdm_counts_pcm_for_flac_and_family1(self):
        self.assertFalse(probe.uses_pcm_probe('pdm', {'codec': 'opus'}))
        self.assertTrue(probe.uses_pcm_probe('pdm', {'codec': 'flac'}))
        self.assertTrue(probe.uses_pcm_probe('pdm', {'codec': 'opus', 'family1': {}}))
        self.assertTrue(probe.uses_pcm_probe('dac', {'codec': 'opus'}))

    def test_family1_checks_order_and_both_channel_metrics(self):
        reference = [dict(energy=1000 + 500 * channel, crossings=100 + 20 * channel)
                     for channel in range(8)]
        rows = [f'CYD_OPENETH_PCM_CHANNEL index={channel} energy={row["energy"]} crossings={row["crossings"]}\n'
                for channel, row in enumerate(reference)]
        self.assertEqual(probe.require_family1_metrics(''.join(rows), reference), reference)
        for changed in (rows[::-1], rows[:-1], rows + rows[:1]):
            with self.subTest(changed=changed), self.assertRaisesRegex(RuntimeError, 'ordered PCM metrics'):
                probe.require_family1_metrics(''.join(changed), reference)
        for replacement in ('index=0 energy=1051 crossings=100', 'index=0 energy=1000 crossings=103'):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(RuntimeError, 'channel 0 disagrees'):
                probe.require_family1_metrics('CYD_OPENETH_PCM_CHANNEL ' + replacement + '\n' + ''.join(rows[1:]),
                                              reference)

    def observe_eof(self, uart, *, allocations=0, backend='dac', codec='opus',
                    pcm_md5=None, pcm_frames=528000, pcm_sha256=None):
        report = {'audio_backend': backend, 'observed': []}
        health = dict(output_driver=dict(requested_bytes=528000, written_bytes=528000, errors=0,
                                         timeouts=0, short_writes=0, saturated=False),
                      decoder_failure={'sequence': 0}, stream_failure={'sequence': 0},
                      output={'failures': 0}, allocation_failures=allocations)
        status = json.dumps(dict(generation=1, audio=False, connecting=False, format='stream ended'))
        server = SimpleNamespace(fixtures={'station': dict(data=b'123', codec=codec,
                                                           pcm_frames=pcm_frames, pcm_md5=pcm_md5,
                                                           pcm_sha256=pcm_sha256)})
        guest = SimpleNamespace(poll=lambda: None)
        with patch.object(probe, 'request', return_value=status), patch.object(probe, 'sample', return_value=health), \
             patch.object(probe, 'guest_log', return_value=uart), patch.object(probe, 'check_asset', return_value={'bytes': 13588}):
            if allocations:
                with self.assertRaisesRegex(RuntimeError, 'Unexpected allocation failure'):
                    probe.observe_eof(0, server, dict(complete=True, sent=3), guest, runner, 1, report)
            else:
                probe.observe_eof(0, server, dict(complete=True, sent=3), guest, runner, 1, report)
        self.assertEqual(report['web_asset_after_eof']['bytes'], 13588)
        return report

    def test_exact_ordered_flush(self):
        self.observe_eof('CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n')

    def test_memory_failure_preserves_post_eof_webui_evidence(self):
        self.observe_eof('CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n', allocations=1)

    def test_truncated_failed_or_duplicate_flush_rejected(self):
        good = 'CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n'
        for uart in ('', 'CYD_OPENETH_PCM_FLUSH frames=40008 status=0\n',
                     'CYD_OPENETH_PCM_FLUSH frames=528000 status=-1\n', good + good):
            with self.subTest(uart=uart), self.assertRaisesRegex(RuntimeError, 'Unexpected decoded PCM frame count'):
                self.observe_eof(uart)

    def test_flac_streaminfo_contains_independently_verified_pcm(self):
        fixture = probe.station_fixture('flac')
        self.assertEqual(fixture['pcm_frames'], 528000)
        self.assertEqual(fixture['pcm_md5'], '7e7636f603770391913d2d7521b969ea')
        with self.assertRaisesRegex(ValueError, 'Missing FLAC STREAMINFO'):
            probe.flac_streaminfo(fixture['data'][:41])

    def test_exact_flac_pcm_on_pdm_uses_the_probe(self):
        md5 = '7e7636f603770391913d2d7521b969ea'
        flush = 'CYD_OPENETH_PCM_FLUSH frames=5448 status=0\n'
        checksum = f'CYD_OPENETH_PCM_MD5 {md5}\n'
        args = dict(backend='pdm', codec='flac', pcm_md5=md5, pcm_frames=5448)
        self.assertEqual(self.observe_eof(flush + checksum, **args)['pcm_md5'], md5)
        for log in (flush, flush + checksum.replace('7e76', '8e76'), flush + checksum * 2):
            with self.subTest(log=log), self.assertRaisesRegex(RuntimeError, 'FLAC STREAMINFO MD5'):
                self.observe_eof(log, **args)

    def test_vorbis_requires_the_entire_pcm_identity_on_all_outputs(self):
        fixture = probe.station_fixture('vorbis')
        self.assertEqual(len(fixture['data']), 703584)
        self.assertEqual(fixture['pcm_frames'], 528000)
        sha256 = fixture['pcm_sha256']
        self.assertEqual(sha256, 'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910')
        flush = 'CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n'
        checksum = f'CYD_OPENETH_PCM_SHA256 {sha256}\n'
        for backend in ('pdm', 'dac', 'legacy_dac'):
            args = dict(backend=backend, codec='vorbis', pcm_sha256=sha256)
            with self.subTest(backend=backend):
                self.assertTrue(probe.uses_pcm_probe(backend, fixture))
                self.assertEqual(self.observe_eof(flush + checksum, **args)['pcm_sha256'], sha256)
                for log in (flush, flush + checksum * 2, flush + checksum.replace('e2c3', 'f2c3'),
                            flush + 'CYD_OPENETH_PCM_MD5 ' + '0' * 32 + '\n'):
                    with self.assertRaisesRegex(RuntimeError, 'complete public decoder SHA-256'):
                        self.observe_eof(log, **args)

    def test_helix_mp3_checks_eof_for_mono_and_stereo_builds(self):
        mono = probe.helix_mp3_fixture(True)
        stereo = probe.helix_mp3_fixture(False)
        self.assertEqual(mono['data'], stereo['data'])
        self.assertEqual((mono['source_channels'], mono['pcm_channels']), (2, 1))
        self.assertEqual((stereo['source_channels'], stereo['pcm_channels']), (2, 2))
        self.assertEqual(mono['pcm_frames'], stereo['pcm_frames'])
        flush = f'CYD_OPENETH_PCM_FLUSH frames={mono["pcm_frames"]} status=0\n'
        checksum = 'c4ca4238a0b923820dcc509a6f75849b'
        args = dict(backend='pdm', codec='mp3', pcm_frames=mono['pcm_frames'])
        self.assertEqual(self.observe_eof(flush + f'CYD_OPENETH_PCM_MD5 {checksum}\n',
                                          **args)['pcm_md5'], checksum)
        with self.assertRaisesRegex(RuntimeError, 'Expected a single PCM MD5'):
            self.observe_eof(flush, **args)


if __name__ == '__main__':
    unittest.main()
