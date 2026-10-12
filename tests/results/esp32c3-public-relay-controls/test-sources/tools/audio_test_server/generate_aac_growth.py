"""Generate delayed ADTS buffer-growth fixtures without changing audio elements.

Only single-block, unprotected, mono/stereo ADTS with explicit channel config
is accepted. DSE prefixes keep byte alignment and stay within 768 bytes per
core channel, including the original raw data block. Independent PCM decoding
must verify each generated pair before it is used for board qualification.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ADTS_HEADER_BYTES = 7
RAW_BYTES_PER_CORE_CHANNEL = 768
DSE_MAX_PAYLOAD_BYTES = 510
DSE_ESCAPE_COUNT = 255
SAMPLE_RATES = (96000, 88200, 64000, 48000, 44100, 32000, 24000,
                22050, 16000, 12000, 11025, 8000, 7350)


def adts_frames(data):
    result = []
    offset = 0
    signature = None
    while offset < len(data):
        header = data[offset:offset + ADTS_HEADER_BYTES]
        if (len(header) != ADTS_HEADER_BYTES or header[0] != 255 or
                header[1] & 0xf6 != 0xf0 or not header[1] & 1 or header[6] & 3):
            raise ValueError('Require complete unprotected single-block ADTS')
        rate_index = (header[2] >> 2) & 15
        channels = ((header[2] & 1) << 2) | (header[3] >> 6)
        size = ((header[3] & 3) << 11) | (header[4] << 3) | (header[5] >> 5)
        current = ((header[2] >> 6) + 1, rate_index, channels, header[1] & 8)
        if (rate_index >= len(SAMPLE_RATES) or channels not in (1, 2) or
                current[0] != 2 or size <= ADTS_HEADER_BYTES or
                size > ADTS_HEADER_BYTES + channels * RAW_BYTES_PER_CORE_CHANNEL or
                offset + size > len(data) or (signature is not None and current != signature)):
            raise ValueError('Require one consistent LC-core mono/stereo configuration within its bit budget')
        signature = current
        result.append(data[offset:offset + size])
        offset += size
    if not result:
        raise ValueError('Empty ADTS input')
    return result, SAMPLE_RATES[signature[1]], signature[2]


def dse_prefix(size):
    """Encode exactly size bytes of byte-aligned, same-tag ancillary data."""
    if type(size) is not int or size < 0 or size == 1:
        raise ValueError('A byte-aligned DSE needs at least two bytes')
    output = bytearray()
    while size:
        # Total DSE sizes 2..256 and 258..513 are representable directly.
        part = min(size, DSE_MAX_PAYLOAD_BYTES + 3)
        while part == 257 or size - part == 1:
            part -= 1
        header_bytes = 3 if part >= 258 else 2
        payload = part - header_bytes
        output.extend((0x81, min(payload, DSE_ESCAPE_COUNT)))  # ID_DSE=4, tag=0, align=1
        if payload >= DSE_ESCAPE_COUNT:
            output.append(payload - DSE_ESCAPE_COUNT)
        output.extend(b'\xa5' * payload)
        size -= part
    return bytes(output)


def padded_frame(frame, total_size):
    frames, _, channels = adts_frames(frame)
    if len(frames) != 1 or type(total_size) is not int:
        raise ValueError('Expected one frame and an integer target size')
    if total_size > ADTS_HEADER_BYTES + channels * RAW_BYTES_PER_CORE_CHANNEL:
        raise ValueError('Target exceeds the core channel bit budget')
    prefix = dse_prefix(total_size - len(frame))
    header = bytearray(frame[:ADTS_HEADER_BYTES])
    header[3] = (header[3] & 0xfc) | (total_size >> 11)
    header[4] = (total_size >> 3) & 255
    # Signal VBR: added ancillary data does not retain the original CBR reservoir.
    header[5] = ((total_size & 7) << 5) | 31
    header[6] = 0xfc
    return bytes(header) + prefix + frame[ADTS_HEADER_BYTES:]


def generate(data, seconds=35, grow_after=15):
    if (not all(type(x) in (int, float) and math.isfinite(x) for x in (seconds, grow_after)) or
            not 5 <= grow_after < seconds - 5 or not 15 <= seconds <= 570):
        raise ValueError('Require bounded duration and at least five seconds around growth')
    frames, rate, channels = adts_frames(data)
    count = math.ceil(seconds * rate / 1024)
    first_growth = math.ceil(grow_after * rate / 1024)
    target = ADTS_HEADER_BYTES + channels * RAW_BYTES_PER_CORE_CHANNEL
    # Every late frame grows to the limit; no decoder reset or format transition.
    selected = [frames[i % len(frames)] for i in range(count)]
    late = [padded_frame(frame, target) if i >= first_growth else frame
            for i, frame in enumerate(selected)]
    metadata = dict(frames=count, core_rate=rate, core_channels=channels,
        seconds=count * 1024 / rate, first_growth_frame=first_growth,
        growth_seconds=first_growth * 1024 / rate,
        original_max_frame_bytes=max(map(len, frames)), target_frame_bytes=target,
        expected_capacity_bytes=(target + 127) & ~127,
        scope='Single raw block with DSE ancillary prefix inside the core channel bit budget; requires independent decode')
    return b''.join(selected), b''.join(late), metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=35)
    parser.add_argument('--grow-after', type=float, default=15)
    args = parser.parse_args()
    source = args.input.read_bytes()
    baseline, growth, metadata = generate(source, args.seconds, args.grow_after)
    args.output.mkdir(parents=True, exist_ok=False)
    metadata['source_sha256'] = hashlib.sha256(source).hexdigest()
    metadata['generator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    metadata['files'] = {}
    for name, data in (('baseline.aac', baseline), ('growth.aac', growth)):
        (args.output / name).write_bytes(data)
        metadata['files'][name] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    (args.output / 'manifest.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
