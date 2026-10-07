"""Guard against accepting core-only AAC or an unnoticed playback reset."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_playback
from public_streams import no_runtime_faults, playback_url, probe_spec, public_url
from aac_reference import adts_frames, verified_spec


class PublicStreams(unittest.TestCase):
    def test_implicit_ps_needs_actual_reference_evidence(self):
        spec = probe_spec(dict(streams=[dict(codec_name='aac', profile='HE-AACv2',
                                            sample_rate='32000', channels=2)]))
        reference = dict(scope=0, frames=20, samples=38912, square_signal=12345,
                         rate=32000, channels=1, ps_frames=0)
        mono = verified_spec(spec, reference, 20)
        self.assertEqual((mono['profile'], mono['channels'], mono['source_channels']),
                         ('HE-AAC', 2, 1))
        states = [dict(seconds=i, audio=True, pcm_sample_rate=32000, pcm_channels=2,
                       bits_per_sample=16, format='HE-AAC 32 kHz mono', channels=1)
                  for i in range(20)]
        check_playback(states, mono)
        stereo = verified_spec(spec, dict(reference, channels=2, ps_frames=20), 20)
        with self.assertRaises(Failure):
            check_playback(states, stereo)
        with self.assertRaises(Failure):
            check_playback([dict(s, channels=2) for s in states], mono)

    def test_reference_rejects_incomplete_quantized_or_silent_decode(self):
        spec = dict(profile='HE-AACv2', rate=32000, channels=2, label='HE-AACv2 ')
        valid = dict(scope=0, frames=20, samples=38912, square_signal=12345,
                     rate=32000, channels=1, ps_frames=0)
        for change in (dict(scope=1), dict(frames=19), dict(samples=0), dict(square_signal=0),
                       dict(rate=16000), dict(channels=0), dict(ps_frames=-1),
                       dict(ps_frames=21), dict(ps_frames=1)):
            with self.subTest(change=change), self.assertRaises(Failure):
                verified_spec(spec, dict(valid, **change), 20)

    def test_reference_capture_requires_complete_adts(self):
        frame = bytes.fromhex('fff15080011ffc') + b'\0'
        self.assertEqual(adts_frames(frame*20), 20)
        for data in (b'', frame[:-1], b'\0'+frame, frame+b'\xff'):
            with self.assertRaises(Failure):
                adts_frames(data)

    def test_ps_reference_requires_full_pcm(self):
        spec = probe_spec(dict(streams=[dict(codec_name='aac', profile='HE-AACv2',
                                            sample_rate='44100', channels=2)]))
        core = [dict(seconds=i, audio=True, pcm_sample_rate=22050, pcm_channels=1,
                     bits_per_sample=16, format='AAC PCM 22.05 kHz mono') for i in range(20)]
        with self.assertRaises(Failure):
            check_playback(core, spec)
        full = [dict(row, pcm_sample_rate=44100, pcm_channels=2,
                     format='HE-AACv2 44.1 kHz stereo') for row in core]
        check_playback(full, spec)

    def test_faults_and_resets_fail_even_if_later_playback_is_good(self):
        for line in ('rst:0xc', 'ESP-ROM:esp32c3', 'assert failed: owner',
                     'serial capture interrupted', 'allocation failed size=55128',
                     'decode error', 'PANIC registers: MEPC=0x40380000',
                     'TLS failure: component=Dynamic Impl allocation_bytes=16432'):
            with self.subTest(line=line), self.assertRaises(Failure):
                no_runtime_faults([dict(at=1, line=line), dict(at=2, line='PERF CPU: busy=50')])

    def test_missing_evidence_and_unsupported_profiles_fail(self):
        with self.assertRaises(Failure):
            no_runtime_faults([])
        for profile in ('SSR', 'LTP', None):
            with self.assertRaises(Failure):
                probe_spec(dict(streams=[dict(codec_name='aac', profile=profile)]))

    def test_only_credential_free_https_urls(self):
        self.assertEqual(public_url('https://example.com/radio'), 'https://example.com/radio')
        for url in ('http://example.com/a', 'https://user:secret@example.com/a',
                    'https://example.com/a?token=secret', 'https://example.com/a#secret'):
            with self.assertRaises(Failure):
                public_url(url)

    def test_cleartext_comparison_is_explicit_and_keeps_public_origin(self):
        url = 'https://example.com/radio'
        self.assertEqual(playback_url(url, 'https'), url)
        self.assertEqual(playback_url(url, 'http'), 'http://example.com/radio')
        with self.assertRaises(Failure):
            playback_url(url, 'ftp')


if __name__ == '__main__':
    unittest.main()
