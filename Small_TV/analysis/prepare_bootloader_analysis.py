"""Extract only the verified factory bootloader's initialized segments into an analysis ELF."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

EXPECTED = '5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'


def prepare(data):
    """Validate the exact local backup and the bootloader checksum/digest before extraction."""
    if len(data) != 0x400000 or hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError('Unexpected factory flash backup')
    if data[0] != 0xe9 or data[1] != 3 or data[23] != 1:
        raise ValueError('Unexpected factory bootloader header')
    cursor, checksum, segments = 24, 0xef, []
    for index in range(3):
        address, size = struct.unpack_from('<II', data, cursor)
        cursor += 8
        if not 0 < size <= 0x8000 or cursor + size > 0x8000:
            raise ValueError('Bootloader segment crosses the partition table')
        payload = data[cursor:cursor + size]
        for byte in payload:
            checksum ^= byte
        executable = 0x40380000 <= address < address + size <= 0x40400000
        if not executable and not 0x3fca0000 <= address < address + size <= 0x3fce0000:
            raise ValueError('Unexpected bootloader segment address')
        segments.append(dict(name=f'.boot.segment{index}', address=address, size=size,
            flash_offset=cursor, execute=executable, sha256=hashlib.sha256(payload).hexdigest()))
        cursor += size
    footer = ((cursor + 16) // 16) * 16 - 1
    digest = hashlib.sha256(data[:footer + 1]).digest()
    if data[footer] != checksum or data[footer + 1:footer + 33] != digest:
        raise ValueError('Factory bootloader checksum/digest mismatch')
    entry = struct.unpack_from('<I', data, 4)[0]
    if not any(s['execute'] and s['address'] <= entry < s['address'] + s['size'] for s in segments):
        raise ValueError('Bootloader entry is outside executable segments')
    names = [s['name'] for s in segments] + ['.bss', '.shstrtab']
    strings, offsets = bytearray(b'\0'), {}
    for name in names:
        offsets[name] = len(strings)
        strings.extend(name.encode() + b'\0')
    output, sections, headers = bytearray(0x1000), [(0,) * 10], []
    for segment in segments:
        output.extend(b'\0' * (-len(output) % 16))
        offset = len(output)
        payload = data[segment['flash_offset']:segment['flash_offset'] + segment['size']]
        output.extend(payload)
        flags = 2 | (4 if segment['execute'] else 1)
        sections.append((offsets[segment['name']], 1, flags, segment['address'], offset, len(payload), 0, 0, 16, 0))
        headers.append((1, offset, segment['address'], segment['address'], len(payload), len(payload),
                        5 if segment['execute'] else 6, 16))
    bss = segments[0]['address'] + segments[0]['size']
    sections.append((offsets['.bss'], 8, 3, bss, 0, 0x3fce0000 - bss, 0, 0, 4, 0))
    strings_offset = len(output)
    output.extend(strings)
    sections.append((offsets['.shstrtab'], 3, 0, 0, strings_offset, len(strings), 0, 0, 1, 0))
    output.extend(b'\0' * (-len(output) % 4))
    table_offset = len(output)
    for section in sections:
        output.extend(struct.pack('<10I', *section))
    ident = b'\x7fELF\x01\x01\x01' + b'\0' * 9
    output[:52] = struct.pack('<16sHHIIIIIHHHHHH', ident, 2, 243, 1, entry, 52, table_offset, 1,
                              52, 32, len(headers), 40, len(sections), len(sections) - 1)
    for index, header in enumerate(headers):
        struct.pack_into('<8I', output, 52 + index * 32, *header)
    report = dict(schema='small-tv-factory-bootloader-analysis-v1', dump_sha256=EXPECTED,
        bootloader_image_sha256=digest.hex(), image_bytes=footer + 33, entry_point=hex(entry),
        segments=segments, elf_sha256=hashlib.sha256(output).hexdigest(),
        synthetic_bss_is_measured_runtime_memory=False, private_settings_extracted=False,
        intended_for_flashing=False)
    return bytes(output), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve existing bootloader analysis')
    elf, report = prepare(args.dump.read_bytes())
    args.output.mkdir(parents=True)
    (args.output / 'bootloader-analysis.elf').write_bytes(elf)
    (args.output / 'image-map.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (args.output / 'known-functions.tsv').write_text(f"{report['entry_point']}\tbootloader_entry\n", encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
