"""Validate DSE byte counts, ADTS bounds and the delayed growth fixture."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/audio_test_server'))
from generate_aac_growth import adts_frames, dse_prefix, generate, padded_frame


class GrowthTests(unittest.TestCase):
    def test_dse_all_representable_sizes(self):
        for total in (0, *range(2, 1600)):
            data = dse_prefix(total)
            self.assertEqual(len(data), total)
            pos = 0
            while pos < len(data):
                self.assertEqual(data[pos], 0x81)
                count = data[pos + 1]; pos += 2
                if count == 255:
                    count += data[pos]; pos += 1
                self.assertLessEqual(count, 510)
                self.assertEqual(data[pos:pos + count], b'\xa5' * count)
                pos += count
            self.assertEqual(pos, total)
        for total in (-1, 1, 2.5, True):
            with self.assertRaises(ValueError): dse_prefix(total)

    def test_audio_payload_and_delayed_size_are_preserved(self):
        folder = Path(__file__).resolve().parent / 'fixtures/aac_stream_format'
        for name in ('lc-48000-stereo', 'he-44100-stereo', 'hev2-44100-stereo'):
            source = (folder / (name + '.aac')).read_bytes()
            baseline, growth, info = generate(source)
            before, rate, channels = adts_frames(baseline)
            after, after_rate, after_channels = adts_frames(growth)
            self.assertEqual((rate, channels), (after_rate, after_channels))
            self.assertEqual(len(before), len(after))
            for index, (a, b) in enumerate(zip(before, after)):
                if index < info['first_growth_frame']:
                    self.assertEqual(a, b)
                else:
                    self.assertEqual(len(b), info['target_frame_bytes'])
                    self.assertTrue(b.endswith(a[7:]))
                    self.assertEqual(b[5] & 31, 31)
                    self.assertEqual(b[6], 0xfc)
            self.assertGreaterEqual(info['growth_seconds'], 15)
            self.assertGreaterEqual(info['seconds'], 35)

    def test_reject_unsupported_or_truncated_input(self):
        path = Path(__file__).resolve().parent / 'fixtures/aac_stream_format/he-44100-stereo.aac'
        source = path.read_bytes(); frame = adts_frames(source)[0][0]
        for change in ('crc', 'multiple-blocks', 'pce', 'wrong-profile', 'rate', 'sync'):
            data = bytearray(frame)
            if change == 'crc': data[1] &= ~1
            elif change == 'multiple-blocks': data[6] |= 1
            elif change == 'pce': data[2] &= ~1; data[3] &= 0x3f
            elif change == 'wrong-profile': data[2] |= 0xc0
            elif change == 'rate': data[2] |= 0x3c
            elif change == 'sync': data[0] = 0
            with self.subTest(change=change), self.assertRaises(ValueError): adts_frames(data)
        for data in (b'', frame[:6], frame[:-1]):
            with self.assertRaises(ValueError): adts_frames(data)
        for target in (len(frame) - 1, len(frame) + 1, 8191):
            with self.assertRaises(ValueError): padded_frame(frame, target)
        for seconds, after in ((10, 5), (35, 31), (35, float('nan')), (600, 15)):
            with self.assertRaises(ValueError): generate(source, seconds, after)


if __name__ == '__main__':
    unittest.main()
