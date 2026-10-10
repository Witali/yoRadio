import itertools
from pathlib import Path
import sys
import unittest
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audio_test_server.icy import IcyServer, metadata_block, stream_blocks, PROGRAMS


class IcyTests(unittest.TestCase):
    def test_metadata_length_and_padding(self):
        for length in (0, 1, 15, 16, 17, 4079, 4080):
            wire = metadata_block(b'x' * length)
            self.assertEqual(len(wire), 1 + wire[0] * 16)
            self.assertEqual(wire[1:1+length], b'x' * length)
            self.assertEqual(wire[1+length:], b'\0' * (len(wire)-length-1))
        with self.assertRaises(ValueError):
            metadata_block(b'x' * 4081)

    def test_audio_is_byte_exact_across_loops(self):
        data = b'1234567'
        chunks = list(itertools.islice(stream_blocks(data, b"StreamTitle='';", 11), 20))
        self.assertEqual(b''.join(a for a, _ in chunks), (data * 32)[:220])
        self.assertTrue(all(m == metadata_block(b"StreamTitle='';") for _, m in chunks[2:]))
        with self.assertRaises(ValueError):
            next(stream_blocks(b'', b''))

    def test_http_headers_and_framing(self):
        fixture = dict(codec='aac', mime='audio/aac', data=b'abc' * 500, seconds=.1)
        with IcyServer('127.0.0.1', 0, fixture) as server:
            port = server.http.server_port
            request = Request(f'http://127.0.0.1:{port}/long', headers={'Icy-MetaData':'1'})
            with urlopen(request, timeout=5) as response:
                self.assertEqual(response.headers['icy-metaint'], '1024')
                expected = stream_blocks(fixture['data'], PROGRAMS['long'][0])
                for _ in range(5):
                    audio, metadata = next(expected)
                    self.assertEqual(response.read(1024), audio)
                    size = response.read(1)
                    self.assertEqual(size + response.read(size[0] * 16), metadata)
            self.assertTrue(server.events[0]['metadata_requested'])


if __name__ == '__main__':
    unittest.main()
