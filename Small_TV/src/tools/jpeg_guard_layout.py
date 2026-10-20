"""Generate const runtime JPEG ownership descriptors from validated native assets."""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path

from jpeg_storage_layout import make_plan, parse_board, parse_partitions

PROJECT = Path(__file__).resolve().parents[1]


def c_bytes(value):
    """Use explicit byte initializers, independent of C string escaping and ABI."""
    return '{' + ','.join(f'0x{v:02x}' for v in bytes.fromhex(value)) + '}'


def partition_descriptors(text):
    """Preserve ALL supported boot records; refuse unknown types/flags/labels.

    The existing planner owns address validation. This second parser additionally
    preserves runtime type/subtype/flags, which the allocation plan does not use.
    """
    result = []
    for row in csv.reader(line for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')):
        row = [value.strip() for value in row]
        if len(row) not in (5, 6) or (len(row) == 6 and row[5] not in ('', '0')):
            raise ValueError('Unsupported partition flags/columns')
        label, kind, subtype, offset, size = row[:5]
        if not label or len(label) >= 16 or not all(c.isascii() and (c.isalnum() or c == '_') for c in label):
            raise ValueError('Unsupported partition label')
        types = {'app': 0, 'data': 1}
        subtypes = {('app', 'factory'): 0, ('data', 'nvs'): 2, ('data', 'phy'): 1}
        if kind not in types:
            raise ValueError('Unsupported partition type')
        numeric_subtype = subtypes.get((kind, subtype))
        if numeric_subtype is None:
            numeric_subtype = int(subtype, 0)
        if not 0 <= numeric_subtype <= 254:
            raise ValueError('Unsupported partition subtype')
        result.append(dict(label=label, type=types[kind], subtype=numeric_subtype,
                           offset=int(offset, 0), bytes=int(size, 0), flags=0))
    return sorted(result, key=lambda row: row['offset'])


def prepare_image(assets, manifest, board_text, partitions_text):
    """REQUESTED_CHANGE: hash immutable payloads, never mutable photos/cache.

    make_plan authenticates all records and proves ownership, including each
    last partial erase sector. Runtime verification does not require FF tails:
    scratch/cache are expected to contain data after the first successful use.
    """
    board = parse_board(board_text)
    plan = make_plan(assets, manifest, board, parse_partitions(partitions_text))
    partitions = partition_descriptors(partitions_text)
    if len(partitions) > 8 or len(plan['candidate_extents']) > 16 or len(plan['protected_extents']) > 16:
        raise ValueError('Runtime descriptor capacity exceeded')
    resources = sorted((row for row in manifest['records'] if int(row['offset'], 0) >= board['ANIMATION_BASE']),
                       key=lambda row: int(row['offset'], 0))
    if len(resources) != 27:
        raise ValueError('Expected five animations and twenty-two immutable icons')
    # A hash of known payloads alone cannot distinguish a future allocation in
    # their old unused tails. All builds enabling this storage must carry the
    # ownership identity below. Legacy/unmarked assets must fail the guard.
    # The stamp occupies existing protected final-sector padding, not new space.
    stamp_bytes = 64
    stamp_offset = None
    for row in resources[:5]:
        payload_end = int(row['offset'], 0)+row['size']
        candidate = (payload_end+15)//16*16
        sector_end = (payload_end+4095)//4096*4096
        if candidate+stamp_bytes <= sector_end:
            stamp_offset = candidate
            break
    if stamp_offset is None:
        raise ValueError('No protected animation padding for ownership stamp')
    authority = dict(schema_version=1, flash_bytes=0x400000, partitions=partitions,
        immutable=[dict(offset=int(row['offset'], 0), bytes=row['size'], sha256=row['sha256']) for row in resources],
        stamp=dict(offset=stamp_offset, bytes=stamp_bytes),
        allocation={key: plan[key] for key in ('candidate_extents', 'protected_extents',
                    'backing', 'metadata', 'caches', 'spare_extents')})
    ownership_id = hashlib.sha256(json.dumps(authority, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    stamp = b'STVOWN1\0'+bytes.fromhex(ownership_id)+b'\xff'*24
    local = stamp_offset-board['ASSETS_BASE']
    if assets[local:local+stamp_bytes] not in (b'\xff'*stamp_bytes, stamp):
        raise ValueError('Protected ownership padding is occupied or has a mismatching stamp')
    prepared = bytearray(assets)
    prepared[local:local+stamp_bytes] = stamp
    prepared = bytes(prepared)
    prepared_manifest = copy.deepcopy(manifest)
    prepared_manifest['sha256'] = hashlib.sha256(prepared).hexdigest()
    prepared_manifest['jpeg_ownership'] = dict(offset=hex(stamp_offset), bytes=stamp_bytes, ownership_id=ownership_id)
    source_layout_id = plan['layout_id']
    plan = make_plan(prepared, prepared_manifest, board, parse_partitions(partitions_text))
    plan['guard_ownership'] = dict(ownership_id=ownership_id, authority=authority,
                                  unmarked_source_layout_id=source_layout_id)
    resources = sorted([*resources, dict(offset=hex(stamp_offset), size=stamp_bytes,
                                         sha256=hashlib.sha256(stamp).hexdigest())],
                       key=lambda row: int(row['offset'], 0))
    lines = ['/* Generated from matching sanitized native assets/board/partition map. */',
             '#ifndef SMALL_TV_GENERATED_JPEG_LAYOUT_H', '#define SMALL_TV_GENERATED_JPEG_LAYOUT_H',
             '#include "jpeg_guard.h"', f'#define JPEG_LAYOUT_OWNERSHIP_STAMP_ADDRESS 0x{stamp_offset:x}u',
             'static const jpeg_guard_partition_t jpeg_layout_partitions[] = {']
    for row in partitions:
        lines.append('    {"%s",0x%xu,0x%xu,%du,%du,%du},' % (
            row['label'], row['offset'], row['bytes'], row['flags'], row['type'], row['subtype']))
    lines.append('};')
    for name, key in (('allowed', 'candidate_extents'), ('protected', 'protected_extents')):
        lines.append(f'static const jpeg_nor_extent_t jpeg_layout_{name}[] = {{')
        lines.extend('    {0x%xu,0x%xu},' % (row['offset'], row['bytes']) for row in plan[key])
        lines.append('};')
    lines.append('static const jpeg_guard_resource_t jpeg_layout_resources[] = {')
    lines.extend('    {0x%xu,%du,%s},' % (int(row['offset'], 0), row['size'], c_bytes(row['sha256'])) for row in resources)
    lines.extend(['};', 'static const jpeg_guard_layout_t jpeg_layout = {',
                  '    0x400000u,jpeg_layout_partitions,%du,%du,' % (
                      len(partitions), next(i for i, row in enumerate(partitions) if row['label'] == 'assets')),
                  '    jpeg_layout_allowed,jpeg_layout_protected,%du,%du,' % (
                      len(plan['candidate_extents']), len(plan['protected_extents'])),
                  '    jpeg_layout_resources,%du,%s' % (len(resources), c_bytes(plan['layout_id'])),
                  '};', '#endif', ''])
    return '\n'.join(lines), plan, prepared, prepared_manifest


def make_header(assets, manifest, board_text, partitions_text):
    """Expose identical descriptors to tests without publishing any writable image."""
    header, plan, _, _ = prepare_image(assets, manifest, board_text, partitions_text)
    return header, plan


def main():
    """Generate into a fresh directory, leaving firmware and input files untouched."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, required=True)
    parser.add_argument('--board', type=Path, default=PROJECT/'app/include/board.h')
    parser.add_argument('--partitions', type=Path, default=PROJECT/'partitions.csv')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assets, manifest = args.assets_dir/'assets.bin', args.assets_dir/'assets-manifest.json'
    header, plan, prepared, prepared_manifest = prepare_image(assets.read_bytes(), json.loads(manifest.read_text()),
                                                             args.board.read_text(), args.partitions.read_text())
    paths = (assets, manifest, args.board, args.partitions, Path(__file__), PROJECT/'tools/jpeg_storage_layout.py')
    plan['guard_inputs_sha256'] = {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'assets.bin').write_bytes(prepared)
    (args.output/'assets-manifest.json').write_text(json.dumps(prepared_manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
    (args.output/'jpeg_layout.h').write_text(header, encoding='utf-8', newline='\n')
    (args.output/'plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Generated immutable guard: 27 resources + ownership stamp,', len(plan['candidate_extents']), 'allowed ranges')


if __name__ == '__main__':
    main()
