"""Negative controls for the QEMU PCM capture/comparison oracle."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1]/'tools/codec_benchmark/run_pipeline_pcm.py'
spec = importlib.util.spec_from_file_location('pipeline_pcm', path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class CaptureTest(unittest.TestCase):
    first = 'PIPE_PCM seq=0 offset=0 rate=48000 channels=2 hex=01000200\n'
    second = 'PIPE_PCM seq=1 offset=4 rate=48000 channels=2 hex=03000400\n'
    end = 'PIPE_PCM_END generation=1 bytes=8 chunks=2 flushes=1\n'

    def test_repacketization_is_not_loss(self):
        reference = m.parse_capture(self.first+self.second+self.end)
        candidate = m.parse_capture('PIPE_PCM seq=0 offset=0 rate=48000 channels=2 hex=0100020003000400\n'
            + self.end.replace('chunks=2', 'chunks=1'))
        self.assertTrue(m.compare(reference, candidate)['exact'])

    def test_corrupt_or_incomplete_capture_is_rejected(self):
        valid = self.first+self.second+self.end
        mutations = [self.first+self.end, self.second+self.first+self.end, valid+self.first,
            self.first+self.second, valid+self.end, valid.replace('offset=4','offset=8'),
            valid.replace('flushes=1','flushes=2'), valid.replace('01000200','00000000').replace('03000400','00000000'),
            valid.replace('01000200','010002'), valid.replace('rate=48000','rate=0'),
            valid.replace('channels=2','channels=0'), valid+'assert failed\n']
        for log in mutations:
            with self.subTest(log=log):
                with self.assertRaises(ValueError): m.parse_capture(log)

    def test_value_order_length_and_layout_must_match(self):
        reference = m.parse_capture(self.first+self.second+self.end)
        mutations = [(48000,2,b'\x02\x00\x02\x00\x03\x00\x04\x00'),
                     (48000,2,b'\x03\x00\x04\x00\x01\x00\x02\x00'),
                     (48000,2,b'\x01\x00\x02\x00'),
                     (44100,2,reference[0][2]), (48000,1,reference[0][2])]
        for candidate in mutations:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError): m.compare(reference,[candidate])


if __name__ == '__main__': unittest.main()
