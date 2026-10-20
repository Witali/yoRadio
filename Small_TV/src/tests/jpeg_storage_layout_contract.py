"""Prove sparse JPEG stores cannot claim upload slots, active resources or settings."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'tools'))
from jpeg_storage_layout import make_plan, parse_board, parse_partitions, SECTOR, FLASH_BYTES, digest


def sectors(extents):
    """Expand the public physical mapping for independent ownership comparisons."""
    return {address for row in extents for address in range(row['offset'], row['offset'] + row['bytes'], SECTOR)}


def main():
    """Reject coherent but unsafe manifests as well as simple hash/size corruption.

    FIXED_TEST: the owned-padding control changes only the last byte of its
    photo slot; a longer replacement would corrupt the adjacent photo payload.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    image_path, manifest_path = args.assets_dir / 'assets.bin', args.assets_dir / 'assets-manifest.json'
    assets = image_path.read_bytes()
    manifest = json.loads(manifest_path.read_text())
    board_path, partition_path = PROJECT / 'app/include/board.h', PROJECT / 'partitions.csv'
    original = dict(assets=assets, manifest=manifest, board=parse_board(board_path.read_text()),
                    partitions=parse_partitions(partition_path.read_text()), backing_bytes=460800)
    plan = make_plan(**original)
    assert (plan['available_sectors'], plan['allocated_sectors'], plan['spare_sectors']) == (262, 260, 2)
    assert plan['backing']['sector_count'] == 113 and plan['backing']['logical_bytes'] == 460800
    assert len(plan['caches']) == 5 and all(v['sector_count'] == 29 and v['logical_bytes'] == 115200 for v in plan['caches'])
    groups = [plan['backing'], plan['metadata'], *plan['caches']]
    assigned = set()
    for group in groups:
        selected = sectors(group['extents'])
        assert len(selected) == group['sector_count'] and not assigned & selected
        assigned |= selected
    free = sectors(plan['candidate_extents'])
    owned = sectors(plan['protected_extents'])
    spare = sectors(plan['spare_extents'])
    assert len(assigned) == 260 and len(spare) == 2 and not assigned & spare
    assert assigned | spare == free and not owned & free
    assert owned | free == set(range(0, FLASH_BYTES, SECTOR))
    # Full upload slots stay protected even though most default-image bytes are FF.
    assert set(range(0x200000, 0x27d000, SECTOR)) <= owned
    assert set(range(0x3e7000, 0x400000, SECTOR)) <= owned
    rejected, controls = [], []

    def state():
        """Give each mutation independent metadata without copying immutable image bytes."""
        return copy.deepcopy(original)

    def reject(name, mutation, message):
        """Require the intended safety guard, not an unrelated early parse failure."""
        values = state()
        mutation(values)
        try:
            make_plan(**values)
        except ValueError as error:
            assert message in str(error), (name, str(error))
            rejected.append(dict(name=name, error=str(error)))
        else:
            raise AssertionError('Unsafe plan accepted: ' + name)

    def patch(values, address, data, refresh_record=False):
        """Keep the global hash coherent so structural/payload guards are exercised."""
        raw = bytearray(values['assets'])
        start = address - values['board']['ASSETS_BASE']
        raw[start:start + len(data)] = data
        values['assets'] = bytes(raw)
        values['manifest']['sha256'] = digest(raw)
        if refresh_record:
            for row in values['manifest']['records']:
                offset = int(row['offset'], 0) - values['board']['ASSETS_BASE']
                row['sha256'] = digest(raw[offset:offset + row['size']])

    reject('truncated-image', lambda s: s.update(assets=s['assets'][:-1]), 'hash/size')
    reject('manifest-size', lambda s: s['manifest'].update(size=len(assets) + 1), 'hash/size')
    reject('manifest-hash', lambda s: s['manifest'].update(sha256='0' * 64), 'hash/size')
    reject('manifest-base', lambda s: s['manifest'].update(offset='0x201000'), 'base mismatch')
    reject('payload-hash', lambda s: patch(s, 0x200000, b'xx'), 'payload hash')
    reject('missing-photo', lambda s: s['manifest']['records'].pop(0), 'Incomplete resource')
    reject('missing-status', lambda s: s['manifest']['records'].pop(), 'Incomplete resource')
    reject('duplicate-resource', lambda s: s['manifest']['records'].append(s['manifest']['records'][0].copy()), 'unexpected resource')
    reject('unknown-resource', lambda s: s['manifest']['records'][0].update(offset='0x201000'), 'unexpected resource')
    reject('oversized-resource', lambda s: s['manifest']['records'][0].update(size=0x19001), 'unexpected resource')
    reject('empty-resource', lambda s: s['manifest']['records'][0].update(size=0), 'unexpected resource')
    reject('animation-magic', lambda s: patch(s, 0x27d000, b'BAD', True), 'container length/header')
    reject('animation-length', lambda s: patch(s, 0x27d003, struct.pack('<I', 75544), True), 'container length/header')
    reject('frame-header-overlap', lambda s: patch(s, 0x27d00f, struct.pack('<I', 1023), True), 'frame exceeds')
    reject('frame-overflow', lambda s: patch(s, 0x27d00b, struct.pack('<I', 0xffffffff), True), 'frame exceeds')
    reject('nonempty-animation-tail', lambda s: patch(s, 0x290000, b'X'), 'tail contains data')
    reject('nonempty-media-tail', lambda s: patch(s, 0x3e6fff, b'X'), 'tail contains data')
    reject('missing-board-value', lambda s: s['board'].pop('PHOTO_SLOT_BYTES'), 'Missing numeric')
    reject('wrong-geometry', lambda s: s['board'].update(LCD_WIDTH=241), 'Unsupported board')
    reject('wrong-photo-count', lambda s: s['board'].update(PHOTO_COUNT=4), 'Unsupported board')
    reject('bank-boundary', lambda s: s['board'].update(PHOTO_SLOT_BYTES=0x18000), 'bank boundary')
    reject('duplicate-partition', lambda s: s['partitions'].append(s['partitions'][0].copy()), 'duplicate partition')
    reject('partition-overlap', lambda s: s['partitions'][-1].update(offset=0x180000), 'Overlapping')
    reject('partition-alignment', lambda s: s['partitions'][-1].update(size=0x1e7001), 'unaligned')
    reject('partition-outside-flash', lambda s: s['partitions'].append(dict(name='extra',kind='data',subtype='0x41',offset=0x400000,size=SECTOR)), 'beyond flash')
    reject('occupied-gap', lambda s: s['partitions'].append(dict(name='other',kind='data',subtype='0x41',offset=0x1f0000,size=SECTOR)), 'owns the application/media gap')
    reject('asset-partition-size', lambda s: s['partitions'][-1].update(size=0x1e6000), 'partition ownership')
    reject('zero-backing', lambda s: s.update(backing_bytes=0), 'Non-positive')
    reject('backing-does-not-fit', lambda s: s.update(backing_bytes=460800 + 3 * SECTOR), 'Insufficient safe space')

    def grow_animation(values, extra):
        """Grow an authenticated container into its own tail without moving frames."""
        row = next(v for v in values['manifest']['records'] if int(v['offset'], 0) == 0x27d000)
        row['size'] += extra
        patch(values, 0x27d003, struct.pack('<I', row['size']), True)

    values = state()
    grow_animation(values, 2 * SECTOR)
    larger = make_plan(**values)
    assert larger['available_sectors'] == larger['allocated_sectors'] == 260
    assert larger['spare_sectors'] == 0 and larger['layout_id'] != plan['layout_id']
    controls.append('two-sector-animation-growth-replanned')
    reject('three-sector-animation-growth', lambda s: grow_animation(s, 3 * SECTOR), 'Insufficient safe space')
    values = state()
    patch(values, 0x218fff, b'X')
    nonempty_photo_tail = make_plan(**values)
    assert nonempty_photo_tail['candidate_extents'] == plan['candidate_extents']
    assert nonempty_photo_tail['layout_id'] != plan['layout_id']
    controls.append('nonempty-upload-padding-stays-owned')

    args.output.mkdir(parents=True, exist_ok=False)
    tool = PROJECT / 'tools/jpeg_storage_layout.py'
    command = [sys.executable, '-B', str(tool), '--assets-dir', str(args.assets_dir), '--output', str(args.output / 'plan.json')]
    result = subprocess.run(command, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    cli = json.loads((args.output / 'plan.json').read_text())
    assert cli['layout_id'] == plan['layout_id']
    before = (args.output / 'plan.json').read_bytes()
    result = subprocess.run(command, capture_output=True, timeout=30)
    assert result.returncode != 0 and (args.output / 'plan.json').read_bytes() == before
    controls.append('existing-plan-not-overwritten')
    rejected_output = args.output / 'rejected-plan.json'
    command[-1] = str(rejected_output)
    result = subprocess.run([*command, '--backing-bytes', str(460800 + 3 * SECTOR)], capture_output=True, timeout=30)
    assert result.returncode != 0 and not rejected_output.exists()
    controls.append('failed-plan-does-not-create-output')
    assert image_path.read_bytes() == assets
    assert json.loads(manifest_path.read_text()) == manifest
    inputs = (image_path, manifest_path, board_path, partition_path, tool, Path(__file__))
    report = dict(status='readonly_layout_contract_passed', all_functionality_verified=False,
                  available_sectors=262, allocated_sectors=260, spare_sectors=2,
                  rejected_cases=rejected, controls=controls, layout_id=plan['layout_id'],
                  inputs_sha256={str(path.resolve()): digest(path.read_bytes()) for path in inputs},
                  scope='Native sanitized image read-only capacity/ownership and CLI output guards. No flash writes, NOR/power-loss/wear or full JPEG bound acceptance.')
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Read-only layout passed:', len(rejected), 'unsafe cases rejected,', len(controls), 'controls; images unchanged.')


if __name__ == '__main__':
    main()
