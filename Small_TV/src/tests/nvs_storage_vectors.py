"""Declare independent multi-sector NVS wire images and expected public Storage read values."""
from nvs_storage_fixture import sector, ACTIVE, FULL, FREEING
from nvs_record_vectors import item, crc


def cases():
    """Cover page ordering, interrupted copying and BLOB generation publication."""
    blank = b'\xff'*4096; namespace = item(b'cfg', namespace=0, value=1)
    old = {0: namespace, 1: item(b'blob', datatype=0x42, span=2, size=1, chunk=0, data_crc=crc(b'A')),
           3: item(b'blob', datatype=0x48, value=1 | 1 << 32 | 0xffff << 48)}
    old_data = {2: b'A'}
    new = item(b'blob', datatype=0x42, span=2, size=1, chunk=128, data_crc=crc(b'B'))
    value = [(1, b'value', 1, b'\x07')]
    return [
        dict(name='empty', sectors=[blank]*3, wanted=[]),
        dict(name='page-order', sectors=[sector(FULL, 8, {0: item()}), sector(ACTIVE, 3, {0: item(b'older', value=3)}), blank],
             wanted=value+[(1, b'older', 1, b'\x03')], order=[3, 8]),
        dict(name='cross-page-duplicate', sectors=[sector(FULL, 0, {0: item()}), sector(ACTIVE, 1, {0: item(value=9)}), blank],
             wanted=[(1, b'value', 1, b'\x09')]),
        dict(name='freeing-copy', sectors=[sector(FREEING, 0, {0: item(), 1: item(b'other', value=11)}),
                                         sector(ACTIVE, 1, {0: item()}), blank],
             wanted=value+[(1, b'other', 1, b'\x0b')], erases=2),
        dict(name='freeing-before-target-initialized', sectors=[sector(FREEING, 0, {0: item()}), blank, blank],
             wanted=value, erases=1),
        dict(name='unpublished-blob-same-page', sectors=[sector(ACTIVE, 0, old | {4: new}, old_data | {5: b'B'}), blank, blank],
             wanted=[(1, b'blob', 0x41, b'A')], factory_key_loss=True),
        dict(name='unpublished-blob-next-page', sectors=[sector(FULL, 0, old, old_data), sector(ACTIVE, 1, {0: new}, {1: b'B'}), blank],
             wanted=[(1, b'blob', 0x41, b'A')]),
        dict(name='published-blob-next-page', sectors=[sector(FULL, 0, old, old_data),
             sector(ACTIVE, 1, {0: new, 2: item(b'blob', datatype=0x48, value=1 | 1 << 32 | 128 << 40 | 0xffff << 48)}, {1: b'B'}), blank],
             wanted=[(1, b'blob', 0x41, b'B')]),
        dict(name='two-chunk-blob', sectors=[sector(FULL, 0, {0: namespace, 1: old[1]}, {2: b'A'}),
             sector(ACTIVE, 1, {0: item(b'blob', datatype=0x42, span=2, size=1, chunk=1, data_crc=crc(b'B')),
                  2: item(b'blob', datatype=0x48, value=2 | 2 << 32 | 0xffff << 48)}, {1: b'B'}), blank],
             wanted=[(1, b'blob', 0x41, b'AB')]),
    ]
