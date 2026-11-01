"""Data-only RFC6716 framing and RFC7845 complete-stream writer.

Original creator packets stay intact in their source transport. Reframing only
copies complete coded frames, explicitly records repetition/missing-frame maps,
and never edits entropy-coded bytes. Public creator APIs independently validate
and synthesize every produced packet in the reference executable.
"""
import hashlib
import struct


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def frame_samples(toc):
    config = toc >> 3
    return (480, 960, 1920, 2880)[config % 4] if config < 12 else (
        480 << (config % 2) if config < 16 else 120 << (config % 4))


def parse_packet(packet):
    need(len(packet) >= 1, 'RFC6716 R1: nonempty audio packet')
    toc, at, end = packet[0], 1, len(packet)
    code = toc & 3
    padding = 0
    vbr = code == 2
    def length():
        nonlocal at
        need(at < end, 'complete coded-frame length')
        first = packet[at]; at += 1
        if first < 252:
            return first
        need(at < end, 'complete two-byte coded-frame length')
        value = first + 4 * packet[at]; at += 1
        return value
    if code == 0:
        sizes = [end - at]
    elif code == 1:
        need((end - at) % 2 == 0, 'RFC6716 R3: code1 equal sizes')
        sizes = [(end - at) // 2] * 2
    elif code == 2:
        first = length(); sizes = [first, end - at - first]
    else:
        need(at < end, 'code3 frame-count byte')
        control = packet[at]; at += 1
        count = control & 63; vbr = bool(control & 128)
        need(1 <= count <= 48 and count * frame_samples(toc) <= 5760, 'RFC6716 R5: bounded duration')
        if control & 64:
            while True:
                need(at < end, 'complete padding length')
                value = packet[at]; at += 1
                padding += 254 if value == 255 else value
                if value != 255:
                    break
        end -= padding
        need(at <= end, 'RFC6716 R6/R7: bounded padding')
        if vbr:
            sizes = [length() for _ in range(count - 1)]
            sizes.append(end - at - sum(sizes))
        else:
            need((end - at) % count == 0, 'RFC6716 R6: complete CBR frames')
            sizes = [(end - at) // count] * count
    need(1 <= len(sizes) <= 48 and len(sizes) * frame_samples(toc) <= 5760 and
         all(0 <= size <= 1275 for size in sizes), 'RFC6716 R2/R4/R5: bounded complete frames')
    frames = []
    for size in sizes:
        need(at + size <= end, 'complete coded frame')
        frames.append(packet[at:at + size]); at += size
    need(at == end, 'exact packet extent')
    return dict(toc=toc, config=toc >> 3, mode=('SILK' if toc >> 3 < 12 else 'hybrid' if toc >> 3 < 16 else 'CELT'),
                code=code, vbr=vbr, padding=padding, sizes=sizes, frames=frames,
                frame_samples=frame_samples(toc), samples=frame_samples(toc) * len(frames))


def encoded_length(size):
    need(0 <= size <= 1275, 'representable coded-frame length')
    return bytes([size]) if size < 252 else bytes([252 + size % 4, (size - 252) // 4])


def pack(toc, frames, code, vbr=False, padding=0):
    need(1 <= len(frames) <= 48 and len(frames) * frame_samples(toc) <= 5760, 'legal output packet duration')
    head = bytes([(toc & 252) | code])
    if code == 0:
        need(len(frames) == 1 and not padding, 'code0 one unpadded frame')
    elif code == 1:
        need(len(frames) == 2 and len(frames[0]) == len(frames[1]) and not padding, 'code1 two equal frames')
    elif code == 2:
        need(len(frames) == 2 and not padding, 'code2 two frames')
        head += encoded_length(len(frames[0]))
    else:
        need(code == 3 and (vbr or len({len(frame) for frame in frames}) == 1), 'legal code3 CBR/VBR')
        head += bytes([len(frames) | (128 if vbr else 0) | (64 if padding else 0)])
        left = padding
        if padding:
            while left >= 254:
                head += bytes([255]); left -= 254
            head += bytes([left])
        if vbr:
            head += b''.join(encoded_length(len(frame)) for frame in frames[:-1])
    packet = head + b''.join(frames) + bytes(padding)
    parsed = parse_packet(packet)
    need(parsed['frames'] == frames and parsed['code'] == code and parsed['padding'] == padding, 'exact constructed complete packet')
    return packet


def transport(info, packets):
    return b'OPMODE1\0' + struct.pack('<5I', info['channels'], info['pre_skip'], info['logical_frames'],
                                       len(packets), info['packet_samples']) + b''.join(struct.pack('<I', len(p)) + p for p in packets)


def parse_transport(body):
    need(len(body) >= 28 and body[:8] == b'OPMODE1\0', 'complete public packet transport')
    channels, pre_skip, logical_frames, count, packet_samples = struct.unpack_from('<5I', body, 8)
    need(channels in (1, 2) and 0 <= pre_skip < 5760 and logical_frames > 0 and count > 0, 'bounded stream geometry')
    at, packets = 28, []
    for _ in range(count):
        need(at + 4 <= len(body), 'complete packet length')
        size = struct.unpack_from('<I', body, at)[0]; at += 4
        need(0 < size <= 61440 and at + size <= len(body), 'complete encoded packet bytes')
        packets.append(body[at:at + size]); at += size
    need(at == len(body), 'exact complete transport')
    return dict(channels=channels, pre_skip=pre_skip, logical_frames=logical_frames, packet_samples=packet_samples), packets


def cases():
    result = []
    for mode, samples in [(0, 480), (0, 960), (0, 1920), (0, 2880), (1, 480), (1, 960),
                          (2, 120), (2, 240), (2, 480), (2, 960)]:
        result.append(dict(name=f'm{mode}-s{samples}-code0', mode=mode, samples=samples, count=1, code=0, vbr=False, padding=0, missing=None))
    for mode, samples in ((0, 960), (1, 960), (2, 120)):
        for name, count, code, vbr, padding, missing in (
                ('code1-cbr', 2, 1, False, 0, None), ('code2-vbr', 2, 2, True, 0, None),
                ('code3-cbr120', 5760 // samples, 3, False, 0, None),
                ('code3-vbr120', 5760 // samples, 3, True, 0, None),
                ('code3-cbr-pad255', 5760 // samples, 3, False, 255, None),
                ('code3-vbr-pad255', 5760 // samples, 3, True, 255, None),
                ('code0-zero', 1, 0, False, 0, 'all'), ('code1-zero', 2, 1, False, 0, 'all'),
                ('code2-zero', 2, 2, True, 0, 'all'), ('code3-zero', 5760 // samples, 3, False, 0, 'all'),
                ('code2-zero-first', 2, 2, True, 0, 'first'), ('code2-zero-last', 2, 2, True, 0, 'last'),
                ('code3-zero-mixed', 3, 3, True, 0, 'middle')):
            result.append(dict(name=f'm{mode}-s{samples}-{name}', mode=mode, samples=samples, count=count,
                               code=code, vbr=vbr, padding=padding, missing=missing))
    need(len(result) == 49, 'bounded complete-stream inventory')
    return result


def reframe(body, case):
    original, source = parse_transport(body)
    parsed = [parse_packet(packet) for packet in source]
    need(len(source) == 4 * case['count'] and len({r['toc'] & 252 for r in parsed}) == 1 and
         all(len(r['frames']) == 1 and r['samples'] == case['samples'] and r['sizes'][0] > 0 for r in parsed),
         'creator emitted complete single-frame packets of the observed fixed configuration')
    frames = [r['frames'][0] for r in parsed]
    toc = parsed[0]['toc']; packets, maps, observations = [], [], []
    for packet_no in range(4):
        start = packet_no * case['count']
        indices = list(range(start, start + case['count']))
        if not case['vbr']:
            indices = [start] * case['count']
        elif case['code'] == 2 or case['code'] == 3:
            # Require actual unequal nonzero coded lengths for VBR payload cases.
            if case['missing'] is None and len({len(frames[i]) for i in indices}) == 1:
                different = next((i for i in range(len(frames)) if len(frames[i]) != len(frames[indices[0]])), None)
                need(different is not None, 'observed genuine unequal coded-frame lengths')
                indices[-1] = different
        selected = [frames[i] for i in indices]
        if packet_no == 1 and case['missing']:
            missing = range(len(selected)) if case['missing'] == 'all' else (
                [0] if case['missing'] == 'first' else [len(selected) - 1] if case['missing'] == 'last' else [1])
            for i in missing:
                selected[i] = b''; indices[i] = None
        packet = pack(toc, selected, case['code'], case['vbr'], case['padding'])
        row = parse_packet(packet)
        observations.append({key: value for key, value in row.items() if key != 'frames'})
        packets.append(packet); maps.append(indices)
    total = sum(row['samples'] for row in observations)
    info = dict(original, packet_samples=case['samples'] * case['count'], logical_frames=total - original['pre_skip'] - 13)
    return transport(info, packets), dict(info, source_frame_map=maps, observations=observations,
                                         original_transport_sha256=sha(body), source_packets_preserved=True)


def crc(body):
    value = 0
    for byte in body:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def page(packet, serial, sequence, granule, flags):
    lacing = bytes([255] * (len(packet) // 255) + [len(packet) % 255])
    need(len(lacing) <= 255, 'bounded complete packet per page')
    body = bytearray(struct.pack('<4sBBQIIIB', b'OggS', 0, flags, granule, serial, sequence, 0, len(lacing)) + lacing + packet)
    struct.pack_into('<I', body, 22, crc(body))
    return bytes(body)


def make_ogg(body, serial):
    info, packets = parse_transport(body)
    head = struct.pack('<8sBBHIhB', b'OpusHead', 1, info['channels'], info['pre_skip'], 48000, 0, 0)
    vendor = b'public-libopus-packet-mode-coverage'
    tags = b'OpusTags' + struct.pack('<I', len(vendor)) + vendor + struct.pack('<I', 0)
    output = page(head, serial, 0, 0, 2) + page(tags, serial, 1, 0, 0)
    at = 0
    for i, packet in enumerate(packets):
        at += parse_packet(packet)['samples']
        final = i == len(packets) - 1
        gp = info['pre_skip'] + info['logical_frames'] if final else at
        output += page(packet, serial, i + 2, gp, 4 if final else 0)
    need(at == info['pre_skip'] + info['logical_frames'] + 13, 'complete raw/trim accounting')
    return output
