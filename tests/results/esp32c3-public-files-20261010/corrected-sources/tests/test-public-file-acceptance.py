"""Finite-file status checks must reject early EOF and intermittent playback."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from common import Failure
from public_file_acceptance import check_finite_playback

SPEC = dict(codec='flac', rate=44100, channels=2, bits=16, label='FLAC', seconds=30.0)


def samples():
    return [dict(seconds=i / 2, request_ms=80, audio=2 <= i / 2 < 32,
                 pcm_sample_rate=44100, pcm_channels=2, bits_per_sample=16,
                 format='FLAC', channels_are_core=False) for i in range(80)]


def pending_format(row, label='FLAC'):
    row.update(audio=True, format=label, sample_rate=0, channels=0,
               bits_per_sample=0, pcm_sample_rate=0, pcm_channels=0,
               format_is_pcm=False, channels_are_core=False)


class FileTests(unittest.TestCase):
    def test_complete_file(self):
        self.assertEqual(check_finite_playback(samples(), SPEC)['observed_playback_seconds'], 30)

    def test_connection_and_container_prefix_before_pcm(self):
        rows = samples()
        pending_format(rows[2], 'connected')
        pending_format(rows[3])
        result = check_finite_playback(rows, SPEC)
        self.assertEqual(result['pending_format_samples'], 2)
        self.assertEqual(result['first_playback_seconds'], 2)
        self.assertEqual(result['observed_playback_seconds'], 30)

    def test_pending_metadata_cannot_hide_faults(self):
        for kind in ('never-ready', 'lost-metadata', 'wrong-initial-rate',
                     'wrong-container', 'partial-metadata', 'interrupted-startup',
                     'late-metadata', 'slow-startup-reply'):
            rows = samples()
            if kind == 'never-ready':
                for row in rows:
                    if row['audio']: pending_format(row)
            elif kind == 'lost-metadata': pending_format(rows[20])
            elif kind == 'wrong-initial-rate': rows[4]['pcm_sample_rate'] = 22050
            elif kind == 'wrong-container': pending_format(rows[3], 'MP3')
            elif kind == 'partial-metadata':
                pending_format(rows[3]); rows[3]['channels'] = 2
            elif kind == 'interrupted-startup': pending_format(rows[2])
            elif kind == 'late-metadata':
                for row in rows[:32]:
                    if row['audio']: pending_format(row)
            elif kind == 'slow-startup-reply':
                pending_format(rows[3]); rows[3]['request_ms'] = 2000
            with self.subTest(kind=kind), self.assertRaises(Failure):
                check_finite_playback(rows, SPEC)

    def test_missing_early_and_interrupted_playback(self):
        for kind in ('absent', 'early', 'missing-eof', 'resumed', 'late-start'):
            rows = samples()
            for row in rows:
                t = row['seconds']
                if kind == 'absent': row['audio'] = False
                elif kind == 'early' and t > 10: row['audio'] = False
                elif kind == 'missing-eof' and t >= 32: row['audio'] = True
                elif kind == 'resumed' and 12 <= t < 14: row['audio'] = False
                elif kind == 'late-start': row['seconds'] += 16
            with self.subTest(kind=kind), self.assertRaises(Failure):
                check_finite_playback(rows, SPEC)

    def test_wrong_format_slow_reply_and_bad_times(self):
        for update in ({'pcm_sample_rate':22050}, {'pcm_channels':1}, {'format':'MP3'},
                       {'bits_per_sample':32}, {'channels_are_core':True}, {'request_ms':2000},
                       {'request_ms':float('nan')}, {'request_ms':-1}, {'audio':1},
                       {'seconds':float('nan')}, {'seconds':-1}, {'seconds':3}):
            rows = samples()
            rows[20].update(update)
            with self.subTest(update=update), self.assertRaises(Failure):
                check_finite_playback(rows, SPEC)

    def test_invalid_reference_and_unconfirmed_eof(self):
        for value in (float('nan'), float('inf'), 0, 600, True):
            spec = dict(SPEC, seconds=value)
            with self.subTest(seconds=value), self.assertRaises(Failure):
                check_finite_playback(samples(), spec)
        with self.assertRaises(Failure):
            check_finite_playback(samples()[:66], SPEC)


if __name__ == '__main__':
    unittest.main()
