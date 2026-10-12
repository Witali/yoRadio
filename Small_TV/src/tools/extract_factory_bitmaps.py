"""Extract only the identified public drawing tables from the verified dump."""
import argparse
import hashlib
import json
from pathlib import Path

DUMP_SHA256 = '5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'
# Addresses and dimensions come from display_fonts.c at 0x4200a5be/0x4200acae.
TABLES = [
    ('ascii16', 0x3c0ebde4, 8, 16, 32, 96),
    ('ascii24', 0x3c0ec3e4, 12, 24, 32, 96),
    ('ascii32', 0x3c0ed5e4, 16, 32, 32, 96),
    ('digits40', 0x3c0ea804, 20, 40, 48, 10),
    ('digits64', 0x3c0e9d04, 32, 64, 48, 11),
    ('digits80', 0x3c0eacb4, 40, 80, 48, 11),
    ('temperature_units', 0x3c0e9c74, 24, 24, 0, 2),
    ('startup_border', 0x3c0e94bc, 200, 15, 0, 1),
    ('startup_cap', 0x3c0e94b0, 5, 11, 0, 1),
    ('simple_plate', 0x3c0e9634, 100, 100, 0, 1),
    ('digit_plate', 0x3c0e9b48, 80, 30, 0, 1),
]


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', type=Path, default=root.parent / 'full-flash.bin')
    parser.add_argument('--output', type=Path, default=root / 'resources/factory')
    args = parser.parse_args()
    data = args.dump.read_bytes()
    if hashlib.sha256(data).hexdigest() != DUMP_SHA256:
        raise ValueError('Factory dump hash differs from the analyzed source')
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, address, width, height, first, count in TABLES:
        stride = (width + 7) // 8
        size = stride * height * count
        offset = 0x10020 + address - 0x3c0c0020
        bitmap = data[offset:offset + size]
        assert len(bitmap) == size and 0x10020 <= offset < 0x4ac64
        (args.output / (name + '.bin')).write_bytes(bitmap)
        records.append(dict(name=name, address=hex(address), flash_offset=hex(offset),
                            width=width, height=height, stride=stride, first=first,
                            count=count, bytes=size, sha256=hashlib.sha256(bitmap).hexdigest()))
    (args.output / 'manifest.json').write_text(json.dumps({
        'source_dump_sha256': DUMP_SHA256,
        'bit_order': 'least significant bit first, rows then bytes',
        'tables': records,
    }, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
