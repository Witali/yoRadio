"""Generate native test descriptors from the validated real Small TV layout."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]


def main():
    """Retain the complete plan and hashes; never open flash hardware for writing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('jpeg_storage_layout', PROJECT/'tools/jpeg_storage_layout.py')
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)
    assets = args.assets_dir/'assets.bin'
    manifest = args.assets_dir/'assets-manifest.json'
    board, partitions = PROJECT/'app/include/board.h', PROJECT/'partitions.csv'
    plan = planner.make_plan(assets.read_bytes(), json.loads(manifest.read_text()),
                            planner.parse_board(board.read_text()), planner.parse_partitions(partitions.read_text()))
    paths = [assets, manifest, board, partitions, Path(__file__), PROJECT/'tools/jpeg_storage_layout.py']
    plan['test_inputs_sha256'] = {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (args.output/'plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8', newline='\n')
    lines = ['/* Generated from the validated current native image, never a guessed FF scan. */',
             'static const jpeg_nor_extent_t plan_allowed[] = {']
    lines += [f'    {{0x{row["offset"]:x}u, {row["bytes"]}u}},' for row in plan['candidate_extents']]
    lines += ['};']
    stores = [plan['backing'], plan['metadata'], *plan['caches']]
    for i, store in enumerate(stores):
        lines += [f'static const jpeg_nor_extent_t plan_extents_{i}[] = {{']
        lines += [f'    {{0x{row["offset"]:x}u, {row["bytes"]}u}},' for row in store['extents']]
        lines += ['};']
    lines += ['static const struct {const jpeg_nor_extent_t *extents; unsigned count; uint32_t logical_bytes;} plan_stores[] = {']
    lines += [f'    {{plan_extents_{i}, {len(store["extents"])}u, {store["logical_bytes"]}u}},' for i, store in enumerate(stores)]
    lines += ['};']
    (args.output/'plan_fixture.h').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')
    print('Prepared real layout:', len(stores), 'stores;', plan['spare_sectors'], 'spare sectors')


if __name__ == '__main__':
    main()
