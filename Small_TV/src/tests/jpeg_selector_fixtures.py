"""Baseline JPEG fixtures with independent per-component DC/AC table selectors."""
from itertools import product

from jpeg_header_fixtures import segment

SELECTORS = (0x00, 0x01, 0x10, 0x11)


def selected_jpeg(selectors, *, full_tables=True, width=8, height=8, omitted=(), declared=None):
    """Encode neutral gray with different Huffman codes for table zero and one.

    DC0/AC0 use code0 for zero/EOB. DC1/AC1 use code10 for zero/EOB;
    their unused code0 represents category8/RS01. A decoder that ignores the
    SOS selector cannot obtain the same entropy interpretation by accident.
    """
    if len(selectors) not in (1, 3) or any(value not in SELECTORS for value in selectors):
        raise ValueError('One or three baseline selector pairs required')
    one = bytes([1]) + bytes(15)
    two = bytes([1, 1]) + bytes(14)
    definitions = {0x00: one + b'\0', 0x10: one + b'\0',
                   0x01: two + b'\x08\0', 0x11: two + b'\x01\0'}
    needed = {value >> 4 for value in selectors} | {0x10 | (value & 15) for value in selectors}
    tables = b''.join(bytes([table]) + data for table, data in definitions.items()
                      if table not in omitted and (full_tables or table in needed))
    ids = (1,) if len(selectors) == 1 else (0, 17, 255)
    frame = (b'\x08' + height.to_bytes(2, 'big') + width.to_bytes(2, 'big') + bytes([len(ids)]) +
             b''.join(bytes([value, 0x11, 0]) for value in ids))
    scan = bytes([len(ids)]) + b''.join(bytes([value, selector]) for value, selector in
             zip(ids, selectors if declared is None else declared)) + b'\0\x3f\0'
    block_bits = ''.join(('10' if selector >> 4 else '0') + ('10' if selector & 15 else '0')
                         for selector in selectors)
    bits = block_bits * (((width + 7) // 8) * ((height + 7) // 8))
    bits += '1' * (-len(bits) % 8)
    entropy = int(bits, 2).to_bytes(len(bits) // 8, 'big').replace(b'\xff', b'\xff\0')
    return (b'\xff\xd8' + segment(0xdb, b'\0' + bytes([1]) * 64) + segment(0xc0, frame) +
            segment(0xc4, tables) + segment(0xda, scan) + entropy + b'\xff\xd9')


def cases():
    """Cover all64RGB/four-gray selector combinations, missing tables and bounds."""
    for count in (1, 3):
        for selectors in product(SELECTORS, repeat=count):
            for full in (False, True):
                name = 'valid-' + '-'.join(f'{value:02x}' for value in selectors) + ('-full' if full else '-sparse')
                yield name, True, selected_jpeg(selectors, full_tables=full)
    for selector in SELECTORS:
        for table in (selector >> 4, 0x10 | (selector & 15)):
            yield f'missing-gray-{selector:02x}-{table:02x}', False, selected_jpeg((selector,), omitted=(table,))
    for table in (0x00, 0x01, 0x10, 0x11):
        yield f'missing-rgb-{table:02x}', False, selected_jpeg((0x00, 0x11, 0x10), omitted=(table,))
    for selectors in ((0x00,), (0x00, 0x11, 0x11)):
        for component in range(len(selectors)):
            for invalid in (0x02, 0x20, 0x12, 0x21, 0xff):
                declared = list(selectors)
                declared[component] = invalid
                yield f'out-of-range-{len(selectors)}-{component}-{invalid:02x}', False, selected_jpeg(selectors, declared=declared)


def upload_cases():
    """Use full-size valid shared/mixed tables and two missing-table upload controls."""
    for name, selectors in (('gray-table1', (0x11,)), ('rgb-shared0', (0, 0, 0)),
                            ('rgb-mixed', (0x01, 0x10, 0x11))):
        yield name, True, selected_jpeg(selectors, full_tables=False, width=240, height=240)
    for table in (0x01, 0x11):
        yield f'missing-gray-table-{table:02x}', False, selected_jpeg((0x11,), width=240, height=240, omitted=(table,))
