"""Construct minimal JPEG byte streams for decoder and HTTP tests."""

def gray_huffman_fixture(dc_counts, dc_values, ac_counts, ac_values):
    """Encode a gray 240x240 image using only zero DC and EOB, without an image library."""
    def segment(marker, payload):
        """Frame one JPEG segment with its exact big-endian length."""
        return b'\xff' + bytes([marker]) + (len(payload) + 2).to_bytes(2, 'big') + payload
    dc_bits = next(index + 1 for index, count in enumerate(dc_counts) if count)
    ac_bits = next(index + 1 for index, count in enumerate(ac_counts) if count)
    bits = 900 * (dc_bits + ac_bits)  # 30x30 grayscale MCUs; both first codewords are zero.
    entropy = bytearray((bits + 7) // 8)
    if bits % 8:
        entropy[-1] = (1 << (8 - bits % 8)) - 1
    return (b'\xff\xd8' + segment(0xdb, b'\0' + bytes([1]) * 64) +
            segment(0xc0, b'\x08\x00\xf0\x00\xf0\x01\x01\x11\x00') +
            segment(0xc4, b'\0' + bytes(dc_counts) + bytes(dc_values) +
                    b'\x10' + bytes(ac_counts) + bytes(ac_values)) +
            segment(0xda, b'\x01\x01\x00\x00\x3f\0') + entropy + b'\xff\xd9')

