"""Reconstruct archived NOR images and independently check bootstrap preservation."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def sha(data):
    """Hash the actual bytes, including reconstructed full physical images."""
    return hashlib.sha256(data).hexdigest()


def verify(path, root):
    """Validate blobs, complete images, exact protected bytes and current sources."""
    proof = json.loads(path.read_text(encoding='utf-8'))
    assert proof['schema_version'] == 1 and proof['passed']
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent / row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        encoded = file.read_bytes()
        assert sha(encoded) == row['gzip_sha256']
        data = gzip.decompress(encoded)
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert row['sha256'] not in blobs
        blobs[row['sha256']] = data
    raw = {}
    for row in proof['raw']:
        assert row['source'] not in raw
        raw[row['source']] = blobs[row['sha256']]
    base = blobs[proof['flash_base_sha256']]
    assert len(base) == 0x400000
    images = {}
    for row in proof['images']:
        data = bytearray(base)
        previous = -4096
        for change in row['sectors']:
            offset = change['offset']
            sector = blobs[change['sha256']]
            assert offset % 4096 == 0 and previous < offset <= len(data)-4096
            assert len(sector) == 4096 and sector != base[offset:offset+4096]
            data[offset:offset+4096] = sector
            previous = offset
        assert row['source'] not in images and sha(data) == row['sha256']
        images[row['source']] = bytes(data)
    report = json.loads(raw[proof['qemu_report_source']])
    assert report == proof['qemu'] and report['passed']
    assert len(report['cases']) == 12
    cases = {'erased', 'torn', 'id-written', 'torn-header', 'occupied', 'foreign-stamp',
             'foreign-compatible', 'bad-resource', 'bad-flags', 'owned-nonempty', 'upgrade-real'}
    expected = {(case, 0) for case in cases} | {('erased', 1)}
    assert {(row['case'], row['boot']) for row in report['cases']} == expected
    assert len(images) == 24
    prefix = proof['qemu_report_source'].rsplit('/', 1)[0]
    assets = (root/'firmware/development/small-tv-esp32c2-reconstructed/assets.bin').read_bytes()
    stamp_offset = 0x28f720
    stamp = assets[stamp_offset-0x200000:stamp_offset-0x200000+64]
    assert stamp[:8] == b'STVOWN1\0' and stamp[40:] == b'\xff'*24
    for row in report['cases']:
        case, boot = row['case'], row['boot']
        before = images[f'{prefix}/{case}/before-{boot}.bin']
        after = images[f'{prefix}/{case}/after-{boot}.bin']
        assert sha(before) == row['before_sha256'] and sha(after) == row['after_sha256']
        programmed = 40 if case in ('erased', 'torn') and not boot else 8 if case in ('id-written', 'torn-header') else 0
        authorized = case in ('erased', 'torn', 'id-written', 'torn-header', 'owned-nonempty', 'upgrade-real')
        observed = row['observation']
        assert bool(observed['authorized']) == authorized
        assert observed['active'] == 0 and observed['usage']['erase_calls'] == 0
        assert observed['usage']['program_bytes'] == programmed and row['owners_stopped']
        target = bytearray(before)
        if programmed:
            target[stamp_offset:stamp_offset+64] = stamp
        assert after[:0x9000] == target[:0x9000] and after[0xf000:] == target[0xf000:]
        if boot or case == 'upgrade-real':
            assert after[0x9000:0xf000] == before[0x9000:0xf000]
    for name, digest in proof['source_pins'].items():
        assert sha((root/name).read_bytes()) == digest, name
    manifest = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    assert manifest['source_sha256'] == proof['source_sha256'] == report['source_sha256']
    assert manifest['elf_sha256'] == proof['elf_sha256'] == report['elf_sha256']
    for row in manifest['images']:
        assert sha((root/'firmware/development/small-tv-esp32c2-reconstructed'/row['file']).read_bytes()) == row['sha256']
    assert next(x['sha256'] for x in manifest['images'] if x['file'] == 'app.bin') == proof['app_sha256'] == report['app_sha256']
    return dict(passed=True, images=len(images), blobs=len(blobs), cold_processes=len(report['cases']))


def main():
    """Read evidence only; never start a VM, write flash or execute archived files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root)))


if __name__ == '__main__':
    main()
