"""Check the binary multipart format against explicit wire bytes."""
import unittest
from photo_protocol import multipart_chunk


class MultipartTests(unittest.TestCase):
    def test_exact_wire_bytes(self):
        payload = b'\x00\xff\r\nscan'
        body, content_type = multipart_chunk(5, 2, 3, payload, 'fixture')
        self.assertEqual(content_type, 'multipart/form-data; boundary=fixture')
        self.assertEqual(body,
            b'--fixture\r\nContent-Disposition: form-data; name="chunk"\r\n\r\n\x00\xff\r\nscan\r\n'
            b'--fixture\r\nContent-Disposition: form-data; name="file_number"\r\n\r\n5\r\n'
            b'--fixture\r\nContent-Disposition: form-data; name="chunk_index"\r\n\r\n2\r\n'
            b'--fixture\r\nContent-Disposition: form-data; name="total_chunks"\r\n\r\n3\r\n'
            b'--fixture--\r\n')

    def test_invalid_coordinates_and_lengths(self):
        for slot, index, total, block in ((0, 0, 1, b'x'), (6, 0, 1, b'x'),
                (True, 0, 1, b'x'), (1, -1, 1, b'x'), (1, 1, 1, b'x'),
                (1, 0, 26, b'x'), (1, 0, 1, b''), (1, 0, 1, b'x' * 4097)):
            with self.subTest(slot=slot, index=index, total=total, length=len(block)):
                with self.assertRaises(ValueError):
                    multipart_chunk(slot, index, total, block)

    def test_header_injection_and_payload_collision(self):
        for boundary in ('x\r\nInjected: value', 'quoted"', 'é', 'a' * 71, 'scan'):
            with self.subTest(boundary=boundary):
                with self.assertRaises(ValueError):
                    multipart_chunk(1, 0, 1, b'scan bytes', boundary)

    def test_maximum_valid_chunk(self):
        body, _ = multipart_chunk(5, 24, 25, b'\x00\xff' * 2048)
        self.assertIn(b'\x00\xff' * 2048, body)
        self.assertLess(len(body), 12288)


if __name__ == '__main__':
    unittest.main(verbosity=2)
