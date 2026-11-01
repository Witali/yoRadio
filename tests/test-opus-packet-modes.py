"""Data-only RFC framing guards; these synthetic payloads are not synthesis tests."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('packet_modes_data', ROOT / 'tests/fixtures/opus_packet_modes/generate.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class PacketFraming(unittest.TestCase):
    def test_all_toc_durations_and_zero_frames_are_metadata_only(self):
        for config in range(32):
            toc = config << 3
            duration = g.frame_samples(toc)
            for code, count in ((0, 1), (1, 2), (2, 2), (3, 5760 // duration)):
                with self.subTest(config=config, code=code):
                    packet = g.pack(toc, [b''] * count, code, vbr=code == 2)
                    row = g.parse_packet(packet)
                    self.assertEqual(row['samples'], duration * count)
                    self.assertEqual(row['sizes'], [0] * count)
                    self.assertNotEqual(packet, b'')

    def test_length_boundaries_preserve_full_payloads(self):
        for size in (0, 1, 251, 252, 253, 254, 255, 256, 1023, 1275):
            payload = bytes((i * 137) % 256 for i in range(size))
            for frames in ([payload, b''], [b'', payload], [payload, payload]):
                packet = g.pack(0xf8, frames, 2, True)
                self.assertEqual(g.parse_packet(packet)['frames'], frames)

    def test_code3_cbr_vbr_padding_and_48_frame_boundary(self):
        for vbr in (False, True):
            for padding in (0, 1, 253, 254, 255, 510):
                for count in (1, 2, 3, 48):
                    frames = [(bytes([i]) * (i % 3)) if vbr else b'abc' for i in range(count)]
                    packet = g.pack(0xe0, frames, 3, vbr, padding)
                    row = g.parse_packet(packet)
                    self.assertEqual(row['frames'], frames)
                    self.assertEqual(row['padding'], padding)
                    self.assertLessEqual(row['samples'], 5760)

    def test_malformed_framing_is_refused(self):
        malformed = [b'', b'\xf9\x00', b'\xfa', b'\xfa\xfc', b'\xfa\x01',
                     b'\xfb', b'\xfb\x00', b'\xfb\x31', b'\xfb\x3f',
                     b'\x1b\x03', b'\xfb\x42', b'\xfb\x42\xff',
                     b'\xfb\x02\x00', b'\xfb\x82\xfc', b'\xfb\x82\x02\x00',
                     b'\xf8' + bytes(1276)]
        for packet in malformed:
            with self.subTest(packet=packet.hex()[:24]):
                with self.assertRaises(ValueError):
                    g.parse_packet(packet)

    def test_bounded_complete_stream_geometry(self):
        cases = g.cases()
        self.assertEqual(len(cases), 49)
        self.assertEqual({row['mode'] for row in cases}, {0, 1, 2})
        self.assertEqual({row['code'] for row in cases}, {0, 1, 2, 3})
        self.assertEqual({row['samples'] for row in cases}, {120, 240, 480, 960, 1920, 2880})
        self.assertTrue(all(1 <= row['count'] <= 48 and row['count'] * row['samples'] <= 5760 for row in cases))


if __name__ == '__main__':
    unittest.main()
