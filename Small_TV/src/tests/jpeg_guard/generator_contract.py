"""Check generated ownership inputs, privacy boundaries and fail-closed CLI output."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT/'tools'))
from jpeg_guard_layout import make_header, prepare_image, partition_descriptors, c_bytes


def main():
    """Independently compare every generated resource with the packed manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    asset_path, manifest_path = args.assets_dir/'assets.bin', args.assets_dir/'assets-manifest.json'
    board_path, partitions_path = PROJECT/'app/include/board.h', PROJECT/'partitions.csv'
    assets, manifest = asset_path.read_bytes(), json.loads(manifest_path.read_text())
    board, partitions = board_path.read_text(), partitions_path.read_text()
    header, plan = make_header(assets, manifest, board, partitions)
    assert plan['guard_ownership']['unmarked_source_layout_id'] == '4508149b7701de9fbd945b6f9fe7145b5f2dbe93de9760e56fe2437f51ad9ca6'
    assert header.count('static const jpeg_guard_resource_t ') == 1
    immutable = manifest['records'][5:]
    assert len(immutable) == 27
    expected_hash_counts = Counter(row['sha256'] for row in immutable)
    for row in immutable:
        begin = int(row['offset'], 0)-0x200000
        assert hashlib.sha256(assets[begin:begin+row['size']]).hexdigest() == row['sha256']
        # FIXED_TEST: distinct icon slots may intentionally contain identical
        # payloads. Their descriptors still each need the matching digest.
        assert header.count(c_bytes(row['sha256'])) == expected_hash_counts[row['sha256']]
    for row in manifest['records'][:5]:
        assert c_bytes(row['sha256']) not in header
    _, _, prepared, prepared_manifest = prepare_image(assets, manifest, board, partitions)
    ownership = plan['guard_ownership']
    independently_encoded = json.dumps(ownership['authority'], sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(independently_encoded).hexdigest() == ownership['ownership_id']
    stamp_offset = ownership['authority']['stamp']['offset']-0x200000
    stamp = prepared[stamp_offset:stamp_offset+64]
    assert stamp == b'STVOWN1\0'+bytes.fromhex(ownership['ownership_id'])+b'\xff'*24
    assert assets[stamp_offset:stamp_offset+64] == b'\xff'*64
    assert prepared[:stamp_offset] == assets[:stamp_offset] and prepared[stamp_offset+64:] == assets[stamp_offset+64:]
    assert hashlib.sha256(prepared).hexdigest() == prepared_manifest['sha256']
    # Regenerating from an already correctly stamped image is idempotent.
    again, again_plan, again_assets, _ = prepare_image(prepared, prepared_manifest, board, partitions)
    assert again == header and again_assets == prepared and again_plan['layout_id'] == plan['layout_id']
    # A coherent future allocation change can leave all 27 payloads unchanged.
    # Its different stamp must still distinguish it from the old ownership.
    _, alternate_plan, alternate_assets, _ = prepare_image(assets, manifest, board,
        partitions.replace('0x177000', '0x176000'))
    assert alternate_plan['guard_ownership']['ownership_id'] != ownership['ownership_id']
    assert alternate_assets[stamp_offset:stamp_offset+64] != stamp
    for row in immutable:
        start = int(row['offset'], 0)-0x200000
        assert alternate_assets[start:start+row['size']] == assets[start:start+row['size']]
    assert partition_descriptors(partitions) == [
        dict(label='nvs', type=1, subtype=2, offset=0x9000, bytes=0x6000, flags=0),
        dict(label='phy_init', type=1, subtype=1, offset=0xf000, bytes=0x1000, flags=0),
        dict(label='factory', type=0, subtype=0, offset=0x10000, bytes=0x177000, flags=0),
        dict(label='assets', type=1, subtype=0x40, offset=0x200000, bytes=0x1e7000, flags=0)]
    rejected = []

    def reject(name, operation):
        """Reject unsupported descriptors without silently dropping a table field."""
        try:
            operation()
        except (ValueError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError('Accepted invalid guard input: '+name)

    reject('encrypted-partition', lambda: partition_descriptors(partitions.replace('0x6000,','0x6000, encrypted')))
    reject('unknown-flags', lambda: partition_descriptors(partitions.replace('0x6000,','0x6000, 2')))
    reject('extra-column', lambda: partition_descriptors(partitions.replace('0x6000,','0x6000,,extra')))
    reject('unsupported-type', lambda: partition_descriptors(partitions.replace('nvs, data,','nvs, custom,')))
    reject('unencodable-subtype', lambda: partition_descriptors(partitions.replace('data, nvs,','data, 0x100,')))
    reject('unterminated-label', lambda: partition_descriptors(partitions.replace('nvs, data,','abcdefghijklmnop, data,')))
    reject('label-injection', lambda: partition_descriptors(partitions.replace('nvs, data,','bad"name, data,')))
    reject('partition-gap-owned', lambda: make_header(assets, manifest, board,
        partitions+'other,data,0x41,0x1f0000,0x1000,\n'))
    reject('stale-image', lambda: make_header(bytes([assets[0]^1])+assets[1:], manifest, board, partitions))
    changed = copy.deepcopy(manifest); changed['records'].pop()
    reject('missing-immutable', lambda: make_header(assets, changed, board, partitions))
    changed = copy.deepcopy(manifest); changed['records'][0]['offset'] = '0x290000'
    reject('photo-promoted-to-scratch', lambda: make_header(assets, changed, board, partitions))
    corrupted = bytearray(prepared); corrupted[stamp_offset+10] ^= 1
    corrupted_manifest = copy.deepcopy(prepared_manifest)
    corrupted_manifest['sha256'] = hashlib.sha256(corrupted).hexdigest()
    reject('stale-or-corrupt-ownership-stamp', lambda: make_header(bytes(corrupted), corrupted_manifest, board, partitions))
    # Input record/table order is not an identity; descriptors sort by address.
    changed = copy.deepcopy(manifest); changed['records'].reverse()
    reordered, reordered_plan = make_header(assets, changed, board, partitions)
    assert reordered == header and reordered_plan['layout_id'] == plan['layout_id']
    command = [sys.executable, '-B', str(PROJECT/'tools/jpeg_guard_layout.py'),
               '--assets-dir', str(args.assets_dir), '--output', str(args.output)]
    created = subprocess.run(command, capture_output=True, timeout=30)
    assert created.returncode == 0, created.stderr
    assert (args.output/'jpeg_layout.h').read_text() == header
    assert (args.output/'assets.bin').read_bytes() == prepared
    before = {p.name: p.read_bytes() for p in args.output.iterdir()}
    repeated = subprocess.run(command, capture_output=True, timeout=30)
    assert repeated.returncode != 0
    assert {p.name: p.read_bytes() for p in args.output.iterdir()} == before
    assert asset_path.read_bytes() == assets and json.loads(manifest_path.read_text()) == manifest
    assert board_path.read_text() == board and partitions_path.read_text() == partitions
    inputs = [asset_path, manifest_path, board_path, partitions_path, Path(__file__),
              PROJECT/'tools/jpeg_guard_layout.py', PROJECT/'tools/jpeg_storage_layout.py']
    report = dict(passed=True, immutable_payloads=27, ownership_stamps=1, rejected_inputs=rejected,
                  controls=['hash-each-immutable', 'exclude-five-photos', 'all-partition-fields',
                            'sorted-resource-order', 'matching-cli-header', 'refuse-existing-output',
                            'ownership-id-complete-allocation', 'stamp-only-protected-padding',
                            'stamp-generation-idempotent', 'matching-cli-stamped-assets',
                            'new-layout-new-stamp-same-payloads', 'inputs-unchanged'],
                  layout_id=plan['layout_id'],
                  inputs_sha256={str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS guard generator:', len(rejected), 'rejected inputs, 12 controls')


if __name__ == '__main__':
    main()
