"""Cache identities bind actual codec/policy/geometry without rewriting resources."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROJECT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PROJECT/'tools'))
from jpeg_cache_layout import prepare_cache,CODEC_INPUTS


def sha(path):
    """Record the actual generator inputs, not a manually maintained codec label."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Check deterministic identities, dependency changes and fail-closed inputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets-dir',type=Path,required=True)
    parser.add_argument('--library-build',type=Path,required=True)
    parser.add_argument('--generator-build',type=Path,required=True)
    parser.add_argument('--decoder-oracle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    assets=args.assets_dir/'assets.bin';manifest=args.assets_dir/'assets-manifest.json'
    board=PROJECT/'app/include/board.h';partitions=PROJECT/'partitions.csv';lib=args.library_build/'report.json'
    if not lib.exists():lib=args.library_build/'build.json'
    metadata=json.loads(lib.read_text());image=assets.read_bytes();m=json.loads(manifest.read_text());b=board.read_text();p=partitions.read_text()
    paths=[assets,manifest,board,partitions,lib,Path(__file__),PROJECT/'tools/jpeg_cache_layout.py',PROJECT/'tools/jpeg_guard_layout.py',PROJECT/'tools/jpeg_storage_layout.py']+[PROJECT/n for n in CODEC_INPUTS]
    generator=json.loads((args.generator_build/'build.json').read_text())
    paths += [args.generator_build/'build.json',Path(generator['executable']),PROJECT/'tests/jpeg_decoder/generate.c',PROJECT/'tests/jpeg_decoder/build-generator.ps1']
    paths += [args.decoder_oracle/'fixtures'/f'sampling-44-c4-{bits}.jpg' for bits in (8,12)]
    report=dict(passed=False,inputs_sha256={str(x.resolve()):sha(x) for x in paths},rejections=[])
    try:
        first=prepare_cache(image,m,b,p,metadata);second=prepare_cache(image,m,b,p,dict(reversed(list(metadata.items()))))
        assert first==second;plan=first[2];identity=plan['cache_codec_identity']
        assert identity['width']==identity['height']==240 and identity['format']=='RGB565-little-endian-row-major'
        assert identity['library_sha256']==metadata['library_sha256']
        assert identity['sources_sha256']=={n:sha(PROJECT/n) for n in CODEC_INPUTS}
        altered=dict(metadata,library_sha256='00'*32,executable='a different build directory')
        changed=prepare_cache(image,m,b,p,altered)
        assert changed[2]['cache_codec_id']!=plan['cache_codec_id'] and changed[2]['layout_id']==plan['layout_id']
        assert changed[0]==first[0] and changed[3:]==first[3:]
        # Resource ownership is independent of codec changes: photos/settings
        # need no destructive assets rewrite when merely changing cache identity.
        for key,value in [('upstream_commit','wrong'),('flash_tables',False),('compact_pools',False),
                          ('patch_sha256','00'*32),('flash_patch_sha256','00'*32),('pool_patch_sha256','00'*32)]:
            altered=copy.deepcopy(metadata);altered[key]=value
            try:prepare_cache(image,m,b,p,altered)
            except ValueError as error:report['rejections'].append(dict(kind=key,reason=str(error)))
            else:raise AssertionError(key)
        for name,text in [('slots',b.replace('#define PHOTO_COUNT 5','#define PHOTO_COUNT 4')),
                          ('width0',b.replace('#define LCD_WIDTH 240','#define LCD_WIDTH 0')),
                          ('height241',b.replace('#define LCD_HEIGHT 240','#define LCD_HEIGHT 241'))]:
            assert text!=b
            try:prepare_cache(image,m,text,p,metadata)
            except ValueError as error:report['rejections'].append(dict(kind=name,reason=str(error)))
            else:raise AssertionError(name)
        fake=args.output/'wrong-library';(fake/'library').mkdir(parents=True)
        (fake/'build.json').write_text(json.dumps(metadata),encoding='utf-8');(fake/'library/jpeg-static.lib').write_bytes(b'not the qualified archive')
        result=subprocess.run([sys.executable,'-B',str(PROJECT/'tools/jpeg_cache_layout.py'),'--assets-dir',str(args.assets_dir),'--library-build',str(fake),'--output',str(args.output/'must-not-exist')],capture_output=True,timeout=30)
        (args.output/'bad-archive.log').write_bytes(result.stdout+result.stderr)
        assert result.returncode!=0 and b'AssertionError' in result.stderr and b'sha(archive)' in result.stderr and not (args.output/'must-not-exist').exists()
        report['rejections'].append(dict(kind='actual-archive',reason='actual file SHA differs before output directory creation'))
        assert sha(Path(generator['executable']))==generator['executable_sha256']
        compatibility=[]
        for bits in (8,12):
            generated=args.output/f'old-argc5-{bits}.jpg';gold=args.decoder_oracle/'fixtures'/f'sampling-44-c4-{bits}.jpg'
            result=subprocess.run([generator['executable'],str(generated),'44',str(bits),'4'],capture_output=True,timeout=30)
            assert result.returncode==0 and sha(generated)==sha(gold)
            compatibility.append(dict(precision=bits,byte_identical_sha256=sha(generated)))
        invalid=args.output/'invalid-flat-argument.jpg'
        result=subprocess.run([generator['executable'],str(invalid),'44','8','4','unknown'],capture_output=True,timeout=30)
        assert result.returncode==2 and not invalid.exists()
        report['sampling_generator_compatibility']=compatibility
        report.update(passed=True,codec_id=plan['cache_codec_id'],deterministic=True,library_change_invalidates_cache=True,resources_unchanged=True)
    finally:
        report['inputs_unchanged']=all(sha(Path(x))==h for x,h in report['inputs_sha256'].items());report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS cache identity:',len(report['rejections']),'rejections, dependency/geometry/resource separation')


if __name__=='__main__':main()
