"""Prepare a matching guarded target map and independently checked JPEG fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from jpeg_guard_layout import prepare_image


def sha(path):
    """Pin original resources and oracle data without changing either."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array(name,data):
    """Emit const flash data; no JPEG or full output image is copied into RAM."""
    lines=[f'static const uint8_t {name}[]={{']
    lines.extend('    '+','.join(f'0x{b:02x}' for b in data[i:i+24])+',' for i in range(0,len(data),24))
    return lines+['};']


def main():
    """Keep all generated assets, map, fixture bytes and hashes in one new folder."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--oracle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assets=args.assets_dir/'assets.bin';manifest=args.assets_dir/'assets-manifest.json'
    board,partitions=PROJECT/'app/include/board.h',PROJECT/'partitions.csv'
    header,plan,prepared,prepared_manifest=prepare_image(assets.read_bytes(),json.loads(manifest.read_text()),board.read_text(),partitions.read_text())
    oracle=json.loads((args.oracle/'report.json').read_text());assert oracle['passed']
    known={r['name']:r for r in oracle['positive']}
    names=['cmyk-progressive-12.jpg','full-cmyk12.jpg','lossless-rgb-16.jpg','gray-progressive-8.jpg','sampling-44-c4-12.jpg']
    paths=[assets,manifest,board,partitions,Path(__file__),PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py',args.oracle/'report.json']
    lines=['/* Actual guarded scratch and independent upstream RGB565 fixture hashes. */',
           f'#define SCRATCH_LOGICAL_BYTES {plan["backing"]["logical_bytes"]}u',
           'static const jpeg_nor_extent_t scratch_extents[]={']
    lines.extend('    {0x%xu,%du},'%(r['offset'],r['bytes']) for r in plan['backing']['extents'])
    lines+=['};','#define SCRATCH_EXTENT_COUNT ((unsigned)(sizeof(scratch_extents)/sizeof(scratch_extents[0])))',
            'typedef struct {const char *name;const uint8_t *data;uint32_t bytes;uint8_t expected[32];} probe_fixture_t;']
    for i,name in enumerate(names):
        image=args.oracle/'fixtures'/name;assert sha(image)==known[name]['fixture_sha256'];paths.append(image)
        lines+=array(f'image_{i}',image.read_bytes())
    lines+=['static const probe_fixture_t fixtures[]={']
    for i,name in enumerate(names):
        gold=','.join(f'0x{b:02x}' for b in bytes.fromhex(known[name]['rgb565_sha256']))
        lines.append(f'    {{"{name}",image_{i},sizeof(image_{i}),{{{gold}}}}},')
    lines+=['};','']
    plan['probe_inputs_sha256']={str(p.resolve()):sha(p) for p in paths}
    args.output.mkdir(parents=True,exist_ok=False)
    for name,data in (('jpeg_layout.h',header),('probe_fixture.h','\n'.join(lines))):
        (args.output/name).write_text(data,encoding='utf-8',newline='\n')
    (args.output/'assets.bin').write_bytes(prepared)
    (args.output/'assets-manifest.json').write_text(json.dumps(prepared_manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared target decoder fixtures and guarded scratch:',len(names),'images')


if __name__=='__main__':main()
