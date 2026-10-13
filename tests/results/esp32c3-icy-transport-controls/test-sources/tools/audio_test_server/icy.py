"""Deterministic ICY framing around unchanged encoded audio bytes.

Wire layout follows FFmpeg libavformat/http.c http_read_stream(): metaint
audio bytes, a one-byte length in 16-byte units, then padded metadata.
https://ffmpeg.org/doxygen/8.0/http_8c_source.html
"""

BLOCK_BYTES = 16
MAX_METADATA_BYTES = 255 * BLOCK_BYTES
DEFAULT_METADATA = (b"StreamTitle='Synthetic ICY A';", b'',
                    b"StreamTitle='Synthetic ICY B';")


class IcyFramer:
    def __init__(self, interval, metadata=DEFAULT_METADATA):
        if type(interval) is not int or not 1 <= interval <= 2**31 - 1:
            raise ValueError('ICY interval must be an integer within [1, 2^31-1]')
        if not isinstance(metadata, (tuple, list)) or not metadata:
            raise ValueError('ICY metadata must be a nonempty sequence of bytes')
        self.blocks = []
        for value in metadata:
            if type(value) is not bytes or len(value) > MAX_METADATA_BYTES:
                raise ValueError('ICY metadata must be bytes, at most 4080 bytes')
            units = (len(value) + BLOCK_BYTES - 1) // BLOCK_BYTES
            self.blocks.append(bytes([units]) + value.ljust(units * BLOCK_BYTES, b'\0'))
        self.interval = self.remaining = interval
        self.insertions = self.metadata_bytes = 0

    def wire_length(self, audio_length):
        count = audio_length // self.interval
        cycles, tail = divmod(count, len(self.blocks))
        return audio_length + cycles * sum(map(len, self.blocks)) + sum(map(len, self.blocks[:tail]))

    def feed(self, audio):
        result = bytearray()
        offset = 0
        while offset < len(audio):
            size = min(self.remaining, len(audio) - offset)
            result.extend(audio[offset:offset+size])
            offset += size
            self.remaining -= size
            if not self.remaining:
                block = self.blocks[self.insertions % len(self.blocks)]
                result.extend(block)
                self.metadata_bytes += len(block)
                self.insertions += 1
                self.remaining = self.interval
        return bytes(result)
