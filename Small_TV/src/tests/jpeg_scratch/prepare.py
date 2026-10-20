"""Generate the real native scratch mapping for unit and actual JPEG NOR tests."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from jpeg_guard_layout import prepare_image


def main():
    """Never modify firmware inputs; retain exact layout and generator identities."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assets,manifest=args.assets_dir/'assets.bin',args.assets_dir/'assets-manifest.json'
    board,partitions=PROJECT/'app/include/board.h',PROJECT/'partitions.csv'
    _,plan,_,_=prepare_image(assets.read_bytes(),json.loads(manifest.read_text()),board.read_text(),partitions.read_text())
    lines=['/* Real validated allocation; physical flash contents are a host model. */',
           f'#define SCRATCH_LOGICAL_BYTES {plan["backing"]["logical_bytes"]}u',
           'static const jpeg_nor_extent_t scratch_extents[]={']
    lines+=['    {0x%xu,%du},' % (r['offset'],r['bytes']) for r in plan['backing']['extents']]
    lines+=['};','#define SCRATCH_EXTENT_COUNT ((unsigned)(sizeof(scratch_extents)/sizeof(scratch_extents[0])))','']
    paths=[assets,manifest,board,partitions,Path(__file__),PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py']
    plan['scratch_inputs_sha256']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'scratch_fixture.h').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared shared scratch:',plan['backing']['logical_bytes'],'bytes in',len(plan['backing']['extents']),'extents')


if __name__=='__main__':
    main()
