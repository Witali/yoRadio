"""Prepare journal fixtures from the real validated native JPEG allocation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from jpeg_guard_layout import prepare_image, c_bytes


def main():
    """Retain real ownership inputs; the host's cache contents are synthetic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assets, manifest = args.assets_dir/'assets.bin', args.assets_dir/'assets-manifest.json'
    board, partitions = PROJECT/'app/include/board.h', PROJECT/'partitions.csv'
    _, plan, _, _ = prepare_image(assets.read_bytes(),json.loads(manifest.read_text()),board.read_text(),partitions.read_text())
    addresses = [a for row in plan['metadata']['extents'] for a in range(row['offset'],row['offset']+row['bytes'],4096)]
    assert len(addresses) == 2
    codec = hashlib.sha256(b'journal-host-synthetic-rgb565-v1').hexdigest()
    lines = ['/* Synthetic frame contract, real native sparse mapping. */',
        'static const jpeg_journal_config_t fixture_config = {',
        '    {0x%xu,0x%xu},115200u,0x19000u,%s,%s' % (*addresses,c_bytes(plan['layout_id']),c_bytes(codec)),
        '};','static const jpeg_nor_extent_t fixture_allowed[] = {']
    lines += ['    {0x%xu,0x%xu},' % (r['offset'],r['bytes']) for r in plan['candidate_extents']]
    lines += ['};']
    for i,store in enumerate(plan['caches']):
        lines += [f'static const jpeg_nor_extent_t cache_{i}[] = {{']
        lines += ['    {0x%xu,0x%xu},' % (r['offset'],r['bytes']) for r in store['extents']]
        lines += ['};']
    lines += ['static const struct {const jpeg_nor_extent_t *extents; unsigned count;} cache_maps[] = {']
    lines += [f'    {{cache_{i},{len(s["extents"])}u}},' for i,s in enumerate(plan['caches'])]
    lines += ['};','']
    plan['journal_test_codec_id'] = codec
    paths = [assets,manifest,board,partitions,Path(__file__),PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py']
    plan['test_inputs_sha256'] = {str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'journal_fixture.h').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared journal:',[hex(a) for a in addresses],'; 5 real sparse frame stores')


if __name__ == '__main__':
    main()
