"""Guard against accepting core-only AAC or an unnoticed playback reset."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_playback
from public_streams import no_runtime_faults, playback_url, probe_spec, public_url


class PublicStreams(unittest.TestCase):
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
