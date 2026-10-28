"""Verify archived complete LCD pixels and reconstructed physical flash images."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import zlib

from photo_cache_frame_contract import validate, rejection_checks


def sha(data):
    """Identify exact encoded, physical-image or complete RGB surface bytes."""
    return hashlib.sha256(data).hexdigest()


def rgb(encoded):
    """Decode this fixture writer's strict RGB8/filter-zero PNGs, checking CRCs."""
    assert encoded[:8] == b'\x89PNG\r\n\x1a\n'
    cursor = 8;compressed = bytearray();kinds = []
    while cursor < len(encoded):
        length = struct.unpack_from('>I', encoded, cursor)[0]
        kind = encoded[cursor+4:cursor+8];payload = encoded[cursor+8:cursor+8+length]
        assert len(payload) == length
        assert struct.unpack_from('>I', encoded, cursor+8+length)[0] == zlib.crc32(kind+payload)
        kinds.append(kind)
        if kind == b'IHDR':assert payload == struct.pack('>IIBBBBB', 240, 240, 8, 2, 0, 0, 0)
        elif kind == b'IDAT':compressed.extend(payload)
        else:assert kind == b'IEND' and not payload
        cursor += length+12
    assert cursor == len(encoded) and kinds == [b'IHDR', b'IDAT', b'IEND']
    rows = zlib.decompress(compressed)
    assert len(rows) == 240*721 and all(rows[y*721] == 0 for y in range(240))
    return b''.join(rows[y*721+1:(y+1)*721] for y in range(240))


def verify(path, root):
    """Reject checksum-only success: also check every RGB pixel and protected byte."""
    proof = json.loads(path.read_text(encoding='utf-8'));assert proof['passed']
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent/row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        encoded = file.read_bytes();assert sha(encoded) == row['gzip_sha256']
        data = gzip.decompress(encoded)
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
        assert row['sha256'] not in blobs;blobs[row['sha256']] = data
    raw = {row['source']:blobs[row['sha256']] for row in proof['raw']}
    report = json.loads(raw[proof['report_source']]);assert report == proof['display']
    validate(report);assert rejection_checks(report) == report['contract_rejections']
    prefix = proof['report_source'].rsplit('/', 1)[0]
    count = 0
    for name, flow in report['flows']['reconstructed'].items():
        for index, row in enumerate(flow['samples']):
            pixels = rgb(raw[f'{prefix}/reconstructed-{name}/{index}-complete.png'])
            assert len(pixels) == 57600*3
            assert sha(pixels) == row['qemu_rgb_sha256'] == row['replayed_rgb_sha256']
            count += 1
    assert count == 54
    base = blobs[proof['flash_base_sha256']];assert len(base) == 0x400000
    images = {}
    for row in proof['images']:
        data = bytearray(base);previous = -4096
        for change in row['sectors']:
            offset = change['offset'];sector = blobs[change['sha256']]
            assert offset % 4096 == 0 and previous < offset <= len(data)-4096 and len(sector) == 4096
            data[offset:offset+4096] = sector;previous = offset
        assert sha(data) == row['sha256'];key = (row['profile'], row['when'])
        assert key not in images;images[key] = bytes(data)
    assert len(images) == 6
    plan = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/jpeg-cache-plan.json').read_text())
    mutable = sorted([(0x9000, 0xf000), (0x3e7000, 0x3e8000)]+
        [(r['offset'], r['offset']+r['bytes']) for r in plan['candidate_extents']])
    for name in report['flows']['reconstructed']:
        before, after = images[name, 'before'], images[name, 'after']
        prepared = json.loads(raw[f'{prefix}/reconstructed-{name}/prepared.json'])
        assert sha(before) == prepared['prepared_flash_sha256']
        cursor = 0
        for start, end in mutable:
            assert before[cursor:start] == after[cursor:start];cursor = end
        assert before[cursor:] == after[cursor:]
    for name, digest in proof['source_pins'].items():assert sha((root/name).read_bytes()) == digest, name
    manifest = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    assert manifest['source_sha256'] == report['source_sha256']
    assert manifest['elf_sha256'] == report['native_elf_sha256']
    assert next(r['sha256'] for r in manifest['images'] if r['file'] == 'app.bin') == report['app_sha256']
    return dict(passed=True, frames=count, compared_pixels=count*57600, physical_images=len(images),
                startup_latency_matches_factory=proof['startup_latency_matches_factory'])


def main():
    """Perform a read-only archive check without starting an emulator or loading an ELF."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args();print(json.dumps(verify(args.proof, args.root)))


if __name__ == '__main__':
    main()
