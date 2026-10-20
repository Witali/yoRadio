"""Build small baseline JPEGs with independently named header boundaries."""


def segment(marker, payload):
    """Encode one marker segment using its actual payload length."""
    return b'\xff' + bytes([marker]) + (len(payload) + 2).to_bytes(2, 'big') + payload


def flat_jpeg(*, component_ids=(1,), quantizer=1, width=8, height=8):
    """Encode neutral gray using one-bit zero DC/EOB codes and optional Y/Cb/Cr."""
    if len(component_ids) not in (1, 3):
        raise ValueError('Fixture supports one or three components')
    one = bytes([1]) + bytes(15)
    tables = b'\0' + one + b'\0' + b'\x10' + one + b'\0'
    if len(component_ids) == 3:
        tables += b'\x01' + one + b'\0' + b'\x11' + one + b'\0'
    frame = (b'\x08' + height.to_bytes(2, 'big') + width.to_bytes(2, 'big') +
             bytes([len(component_ids)]) + b''.join(bytes([value, 0x11, 0]) for value in component_ids))
    scan = bytes([len(component_ids)]) + b''.join(
        bytes([value, 0 if index == 0 else 0x11]) for index, value in enumerate(component_ids)) + b'\0\x3f\0'
    bits = ((width + 7) // 8) * ((height + 7) // 8) * len(component_ids) * 2
    entropy = bytearray((bits + 7) // 8)
    if bits % 8:
        entropy[-1] = (1 << (8 - bits % 8)) - 1
    return (b'\xff\xd8' + segment(0xdb, b'\0' + bytes([quantizer]) * 64) +
            segment(0xc0, frame) + segment(0xc4, tables) + segment(0xda, scan) + entropy + b'\xff\xd9')


def replace_segment(data, marker, payload):
    """Replace one known fixture header without modifying entropy or later segments."""
    offset = 2
    while offset + 4 <= len(data):
        length = int.from_bytes(data[offset + 2:offset + 4], 'big')
        if data[offset:offset + 2] == b'\xff' + bytes([marker]):
            return data[:offset] + segment(marker, payload) + data[offset + 2 + length:]
        if data[offset + 1] == 0xda:
            break
        offset += length + 2
    raise ValueError('Missing fixture header')


def scan_payload(ids):
    """Encode selectors in the same order as the declared frame components."""
    return bytes([len(ids)]) + b''.join(bytes([value, 0 if index == 0 else 0x11])
        for index, value in enumerate(ids)) + b'\0\x3f\0'


def cases(*, width=8, height=8):
    """Yield valid controls and one-cause malformed DRI/SOS/SOF/DQT headers."""
    bases = {'gray': ((1,), flat_jpeg(width=width, height=height)),
             'rgb': ((1, 2, 3), flat_jpeg(component_ids=(1, 2, 3), width=width, height=height))}
    for mode, (ids, data) in bases.items():
        yield mode + '-baseline', True, data
        scan = data.index(b'\xff\xda')
        for interval in (0, 1, 65535):
            # These controls contain one MCU at the machine-gate size; no RST
            # is required after its final MCU, including interval one.
            if width == height == 8 or interval in (0, 65535):
                yield f'{mode}-dri-valid-{interval}', True, data[:scan] + segment(0xdd, interval.to_bytes(2, 'big')) + data[scan:]
        yield mode + '-quantizer-255', True, flat_jpeg(component_ids=ids, quantizer=255, width=width, height=height)
        for length in (0, 1, 3, 4, 16):
            yield f'{mode}-dri-length-{length}', False, data[:scan] + segment(0xdd, bytes(length)) + data[scan:]
        payload = scan_payload(ids)
        for length in (*range(len(payload)), *range(len(payload) + 1, len(payload) + 4)):
            changed = (payload + bytes(4))[:length]
            yield f'{mode}-sos-length-{length}', False, replace_segment(data, 0xda, changed)
        for label, position, values in (('ss', -3, (1, 255)), ('se', -2, (0, 62)), ('ahal', -1, (1, 16, 255))):
            for value in values:
                changed = bytearray(payload)
                changed[position] = value
                yield f'{mode}-sos-{label}-{value}', False, replace_segment(data, 0xda, changed)
        for index in range(len(ids)):
            changed = bytearray(payload)
            changed[1 + 2 * index] = 42
            yield f'{mode}-unknown-component-{index}', False, replace_segment(data, 0xda, changed)
    for value in (0, 17, 255):
        yield f'gray-component-id-{value}', True, flat_jpeg(component_ids=(value,), width=width, height=height)
    yield 'rgb-custom-component-ids', True, flat_jpeg(component_ids=(0, 17, 255), width=width, height=height)
    for ids in ((1, 1, 3), (1, 2, 1), (2, 2, 3)):
        yield 'duplicate-frame-' + '-'.join(map(str, ids)), False, flat_jpeg(component_ids=ids, width=width, height=height)
    for label, ids in (('duplicate-scan', (1, 1, 3)), ('reordered-scan', (2, 1, 3))):
        yield label, False, replace_segment(bases['rgb'][1], 0xda, scan_payload(ids))
    for index in range(64):
        values = bytearray([1] * 64)
        values[index] = 0
        yield 'zero-quantizer-' + str(index), False, replace_segment(bases['gray'][1], 0xdb, b'\0' + values)
