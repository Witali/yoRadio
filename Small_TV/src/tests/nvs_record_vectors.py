"""Build synthetic NVS wire records independently of the compiled recovery algorithms."""
import binascii
import struct

EMPTY, WRITTEN, ILLEGAL, ERASED = 3, 2, 1, 0
COLLISION_KEYS = (b'c48a1a756f2d8', b'cd6d6981499b6')


def crc(data, seed=0xffffffff):
    """Use the independently ROM-cross-checked standard reflected CRC32."""
    return binascii.crc32(data, seed) & 0xffffffff


def hash24(key, namespace=1, chunk=255):
    """Match the declared wire fields of Item's value-independent cache hash."""
    return crc(bytes([chunk]), crc(key.ljust(16, b'\0'), crc(bytes([namespace])))) & 0xffffff


def item(key=b'value', datatype=1, value=7, span=1, size=0, chunk=255, namespace=1, bad_crc=False, data_crc=0xffffffff):
    """Serialize the32-byte header, leaving the stored CRC field out of its own calculation."""
    assert 0 < len(key) <= 15
    data = bytearray(b'\xff'*32); data[:4] = bytes((namespace, datatype, span, chunk)); data[8:24] = key.ljust(16, b'\0')
    if datatype in (0x21, 0x41, 0x42):
        struct.pack_into('<H', data, 24, size); struct.pack_into('<I', data, 28, data_crc)
    else: data[24:32] = value.to_bytes(8, 'little')
    checksum = crc(data[24:32], crc(data[8:24], crc(data[:4])))
    struct.pack_into('<I', data, 4, checksum ^ int(bad_crc))
    return bytes(data)


def vectors():
    """Separate expected key retention from mere bitmap/counter consistency."""
    assert COLLISION_KEYS[0] != COLLISION_KEYS[1] and hash24(COLLISION_KEYS[0]) == hash24(COLLISION_KEYS[1]) == 0xf1b94e
    rows = []
    def add(name, entries, payloads, wanted, counter_bug=False, collision_bug=False, chunk_bug=False, invalid_headers=(), data_payloads=None):
        """Keep a complete expected wire image and explicit known-before defect labels."""
        states = entries+[EMPTY]*(126-len(entries))
        rows.append(dict(name=name, states=states, payloads=payloads, wanted=wanted,
                         counter_bug=counter_bug, collision_bug=collision_bug, chunk_bug=chunk_bug,
                         invalid_headers=tuple(invalid_headers), data_payloads=data_payloads or {}))
    add('single', [WRITTEN], {0: item()}, [(1, b'value', 255, 7)])
    add('duplicate-value', [WRITTEN]*2, {0: item(value=7), 1: item(value=9)}, [(1, b'value', 255, 9)])
    add('different-namespace', [WRITTEN]*2, {0: item(), 1: item(namespace=2, value=9)},
        [(1, b'value', 255, 7), (2, b'value', 255, 9)])
    add('different-type-replacement', [WRITTEN]*2, {0: item(), 1: item(datatype=2, value=1033)}, [(1, b'value', 255, 1033)])
    add('illegal-slot', [ILLEGAL], {0: item()}, [], counter_bug=True)
    add('bad-header-crc', [WRITTEN], {0: item(bad_crc=True)}, [], invalid_headers=(0,))
    add('bad-scalar-span', [WRITTEN], {0: item(span=0)}, [], invalid_headers=(0,))
    add('unknown-type', [WRITTEN], {0: item(datatype=0x99)}, [], invalid_headers=(0,))
    for sibling, label in ((ERASED, 'erased'), (ILLEGAL, 'illegal'), (EMPTY, 'empty')):
        add('variable-'+label+'-child', [WRITTEN, sibling], {0: item(datatype=0x21, span=2, size=1)}, [],
            counter_bug=sibling == ERASED)
    add('variable-partial-empty-child', [WRITTEN, EMPTY], {0: item(datatype=0x21, span=2, size=1)}, [],
        counter_bug=True, data_payloads={1: b'A'+b'\xff'*31})
    for chunk, label in ((1, 'chunks'), (128, 'generations')):
        add('blob-'+label, [WRITTEN]*4,
            {0: item(b'blob', datatype=0x42, span=2, size=1, chunk=0),
             2: item(b'blob', datatype=0x42, span=2, size=1, chunk=chunk)},
            [(1, b'blob', 0, 0xffffffffffff0001, 0x42), (1, b'blob', chunk, 0xffffffffffff0001, 0x42)],
            chunk_bug=True, data_payloads={1: b'A'+b'\xff'*31, 3: b'B'+b'\xff'*31})
    old_crc, new_crc = crc(b'A'), crc(b'B')
    index_data = 1 | 1 << 32 | 0xffff << 48
    add('published-index-before-new-generation', [WRITTEN]*5,
        {0: item(b'blob', datatype=0x42, span=2, size=1, chunk=0, data_crc=old_crc),
         2: item(b'blob', datatype=0x48, value=index_data),
         3: item(b'blob', datatype=0x42, span=2, size=1, chunk=128, data_crc=new_crc)},
        [(1, b'blob', 0, old_crc << 32 | 0xffff0001, 0x42),
         (1, b'blob', 255, index_data, 0x48), (1, b'blob', 128, new_crc << 32 | 0xffff0001, 0x42)],
        chunk_bug=True, data_payloads={1: b'A'+b'\xff'*31, 4: b'B'+b'\xff'*31})
    add('hash24-collision', [WRITTEN]*2, {0: item(COLLISION_KEYS[0], value=7), 1: item(COLLISION_KEYS[1], value=9)},
        [(1, COLLISION_KEYS[0], 255, 7), (1, COLLISION_KEYS[1], 255, 9)], collision_bug=True)
    add('collision-key-left-alone', [WRITTEN], {0: item(COLLISION_KEYS[0])}, [(1, COLLISION_KEYS[0], 255, 7)])
    add('collision-key-right-alone', [WRITTEN], {0: item(COLLISION_KEYS[1], value=9)}, [(1, COLLISION_KEYS[1], 255, 9)])
    close_key = b'cd6d6981499b7'
    assert hash24(close_key) != hash24(COLLISION_KEYS[0])
    add('similar-key-without-collision', [WRITTEN]*2, {0: item(COLLISION_KEYS[0]), 1: item(close_key, value=9)},
        [(1, COLLISION_KEYS[0], 255, 7), (1, close_key, 255, 9)])
    for count in (29, 30, 60, 126):
        payloads = {index: item(f'key{index:03d}'.encode(), value=index) for index in range(count)}
        add(f'cache-blocks-{count}', [WRITTEN]*count, payloads,
            [(1, f'key{index:03d}'.encode(), 255, index) for index in (0, count-1)])
    return rows
