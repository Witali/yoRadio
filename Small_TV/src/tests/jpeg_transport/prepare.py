"""Create matching stamped resources and minimal probe map, without touching firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from jpeg_guard_layout import prepare_image


def main():
    """Use fresh directories; production assets remain the authoritative inputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assets,manifest=args.assets_dir/'assets.bin',args.assets_dir/'assets-manifest.json'
    board,partitions=PROJECT/'app/include/board.h',PROJECT/'partitions.csv'
    header,plan,prepared,prepared_manifest=prepare_image(assets.read_bytes(),json.loads(manifest.read_text()),board.read_text(),partitions.read_text())
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'jpeg_layout.h').write_text(header,encoding='utf-8',newline='\n')
    (args.output/'assets.bin').write_bytes(prepared)
    (args.output/'assets-manifest.json').write_text(json.dumps(prepared_manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    scratch=plan['backing']['extents'][0]['offset'];cache=plan['caches'][0]['extents'][0]['offset']
    lines=['/* Two small target I/O scopes from the full validated native plan. */',
           f'#define PROBE_SCRATCH_ADDRESS 0x{scratch:x}u',f'#define PROBE_CACHE_ADDRESS 0x{cache:x}u',
           'static const jpeg_nor_extent_t probe_scratch[]={{PROBE_SCRATCH_ADDRESS,8192}};',
           'static const jpeg_nor_extent_t probe_cache[]={{PROBE_CACHE_ADDRESS,4096}};','']
    (args.output/'probe_map.h').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    paths=[assets,manifest,board,partitions,Path(__file__),PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py']
    plan['transport_inputs_sha256']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared transport resources:',hex(scratch),hex(cache))


if __name__=='__main__':
    main()
