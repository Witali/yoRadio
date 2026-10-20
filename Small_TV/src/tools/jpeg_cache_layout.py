"""Generate matching guarded cache maps and a codec/build/geometry identity."""
import argparse
import hashlib
import json
from pathlib import Path

from jpeg_guard_layout import prepare_image,c_bytes
from jpeg_storage_layout import parse_board

PROJECT=Path(__file__).resolve().parents[1]
CODEC_INPUTS=['codec/jpeg_decoder.c','codec/jpeg_decoder.h','codec/jpeg_decoder_internal.h','codec/jpeg_memory.c',
    'codec/jpeg_backing.c','codec/jpeg_backing.h','codec/jpeg_coefficients.c','codec/jpeg_coefficients.h',
    'app/media/color_convert.c','app/include/color_convert.h','storage/jpeg_cache.c','storage/jpeg_cache.h',
    'storage/jpeg_journal.c','storage/jpeg_journal.h','storage/jpeg_nor.c','storage/jpeg_nor.h',
    'storage/jpeg_scratch.c','storage/jpeg_scratch.h','tests/jpeg_library_probe/UPSTREAM.json',
    'tests/jpeg_library_probe/libjpeg-turbo-3.2.0-bounded.patch',
    'tests/jpeg_library_probe/libjpeg-turbo-3.2.0-flash-tables.patch',
    'tests/jpeg_library_probe/libjpeg-turbo-3.2.0-compact-pools.patch',
    'tests/jpeg_library_probe/generate_flash_tables.py']


def sha(path):
    """Use saved source bytes and the actual qualified archive, not a hand tag."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_cache(assets,manifest,board_text,partitions_text,library):
    """Bind the five-frame plan and all pixel/storage policy inputs reproducibly."""
    board=parse_board(board_text)
    if board['PHOTO_COUNT']!=5 or not 1<=board['LCD_WIDTH']<=240 or not 1<=board['LCD_HEIGHT']<=240:
        raise ValueError('Unsupported cache slot count or dimensions')
    if library['upstream_commit']!='c85e6b905bf237038faa936dab160ebfc5da0344' or not library['flash_tables'] or not library['compact_pools']:
        raise ValueError('Use qualified pinned bounded/flash-table/compact decoder')
    for key,name in (('patch_sha256','bounded'),('flash_patch_sha256','flash-tables'),('pool_patch_sha256','compact-pools')):
        if library[key]!=sha(PROJECT/f'tests/jpeg_library_probe/libjpeg-turbo-3.2.0-{name}.patch'):
            raise ValueError('Library does not match current adaptation patches')
    guard,plan,prepared,prepared_manifest=prepare_image(assets,manifest,board_text,partitions_text)
    width,height=board['LCD_WIDTH'],board['LCD_HEIGHT']
    inputs={name:sha(PROJECT/name) for name in CODEC_INPUTS}
    identity=dict(schema_version=1,format='RGB565-little-endian-row-major',width=width,height=height,
                  library_sha256=library['library_sha256'],sources_sha256=inputs)
    codec_id=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    addresses=[at for r in plan['metadata']['extents'] for at in range(r['offset'],r['offset']+r['bytes'],4096)]
    if len(addresses)!=2 or len(plan['caches'])!=5:raise ValueError('Incomplete native cache plan')
    lines=['/* REQUESTED_CHANGE: generated cache/source/codec identity, never HTTP configuration. */',
           '#ifndef SMALL_TV_GENERATED_CACHE_LAYOUT_H','#define SMALL_TV_GENERATED_CACHE_LAYOUT_H',
           '#include "jpeg_cache.h"','#include "jpeg_layout.h"']
    for i,m in enumerate(plan['caches']):
        if m['logical_bytes']!=width*height*2:raise ValueError('Frame plan/geometry mismatch')
        lines+=[f'static const jpeg_nor_extent_t jpeg_cache_map_{i}[]={{']
        lines+=['    {0x%xu,0x%xu},'%(r['offset'],r['bytes']) for r in m['extents']];lines+=['};']
    lines+=['static const jpeg_cache_layout_t jpeg_cache_layout={',
            '    {{0x%xu,0x%xu},%du,0x%xu,%s,%s},'%(*addresses,width*height*2,board['PHOTO_SLOT_BYTES'],c_bytes(plan['layout_id']),c_bytes(codec_id)),
            '    %du,%du,{%s},'%(width,height,','.join('0x%xu'%(board['ASSETS_BASE']+i*board['PHOTO_SLOT_BYTES']) for i in range(5))),
            '    {']
    lines+=['        {jpeg_cache_map_%d,%du},'%(i,len(m['extents'])) for i,m in enumerate(plan['caches'])]
    lines+=['    },','    jpeg_layout_allowed,%du'%len(plan['candidate_extents']),'};',
            'static const jpeg_nor_extent_t jpeg_cache_scratch_extents[]={']
    lines+=['    {0x%xu,0x%xu},'%(r['offset'],r['bytes']) for r in plan['backing']['extents']]
    lines+=['};',f'#define JPEG_CACHE_SCRATCH_BYTES {plan["backing"]["logical_bytes"]}u',
            f'#define JPEG_CACHE_SCRATCH_EXTENTS {len(plan["backing"]["extents"])}u','#endif','']
    plan['cache_codec_identity']=identity;plan['cache_codec_id']=codec_id
    return guard,'\n'.join(lines),plan,prepared,prepared_manifest


def main():
    """Only write a new output directory; preserve all production/user sources."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--library-build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();metadata=args.library_build/'report.json'
    archive=args.library_build/'library/libjpeg.a'
    if not metadata.exists():metadata=args.library_build/'build.json';archive=args.library_build/'library/jpeg-static.lib'
    library=json.loads(metadata.read_text());assert sha(archive)==library['library_sha256']
    assets,manifest=args.assets_dir/'assets.bin',args.assets_dir/'assets-manifest.json'
    board,partitions=PROJECT/'app/include/board.h',PROJECT/'partitions.csv'
    guard,header,plan,prepared,prepared_manifest=prepare_cache(assets.read_bytes(),json.loads(manifest.read_text()),board.read_text(),partitions.read_text(),library)
    paths=[assets,manifest,board,partitions,metadata,archive,Path(__file__),PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py']
    paths += [PROJECT/name for name in CODEC_INPUTS]
    plan['cache_inputs_sha256']={str(p.resolve()):sha(p) for p in paths}
    args.output.mkdir(parents=True,exist_ok=False)
    for name,data in (('jpeg_layout.h',guard),('jpeg_cache_layout.h',header)):
        (args.output/name).write_text(data,encoding='utf-8',newline='\n')
    (args.output/'assets.bin').write_bytes(prepared)
    (args.output/'assets-manifest.json').write_text(json.dumps(prepared_manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared cache identity:',plan['cache_codec_id'])


if __name__=='__main__':main()
