"""Compiled unsafe cache variants, checked by real physical assertions/pixels."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[1]


def sha(path):
    """Pin every runtime mutant and the independent test inputs."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Never mutate production sources or treat compiler/loader errors as success."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--contract',type=Path,required=True)
    parser.add_argument('--library-build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    resources=args.build/'resources';original=(PROJECT/'storage/jpeg_cache.c').read_text()
    needles={
        'skip-durable-invalidation':('jpeg_cache_result_t jpeg_cache_begin(', 'c->journal_error=jpeg_journal_begin(&c->journal,slot);','c->journal_error=JPEG_JOURNAL_OK;'),
        'trust-unverified-frame':('', 'if(slot!=c->slot || frame_bytes!=c->layout->journal.frame_bytes || checkpoint(c))return -1;', 'if(frame_bytes)return 0;\n    if(slot!=c->slot || frame_bytes!=c->layout->journal.frame_bytes || checkpoint(c))return -1;'),
        'trust-metadata-source':('jpeg_cache_result_t jpeg_cache_lookup(', 'r=source_hash(c,c->source_sha256);if(r)return r;', 'memcpy(c->source_sha256,c->journal.entries[slot].source_sha256,32);'),
        'ignore-source-change':('', 'if(memcmp(source,c->source_sha256,32))','if(false)'),
        'discard-dirty-frame':('', 'c->nor_error=jpeg_nor_sync(&c->frame);','c->nor_error=JPEG_NOR_OK;'),
        'reuse-physical-read-cache':('', 'jpeg_nor_abort(&c->frame);const jpeg_cache_map_t *m=', 'if(c->frame.open)return JPEG_CACHE_OK;\n    jpeg_nor_abort(&c->frame);const jpeg_cache_map_t *m='),
        'read-before-verified':('', '!c->verified || c->writing','c->writing'),
        'read-past-source-file':('', 'offset>c->source_bytes || bytes>c->source_bytes-offset','false'),
        'trust-decoder-read':('', 'for(size_t at=0;at<bytes;)','for(size_t at=bytes;at<bytes;)'),
    }
    native=['storage/jpeg_nor.c','storage/jpeg_journal.c','tests/jpeg_cache/native_test.c']
    full=['codec/jpeg_decoder.c','codec/jpeg_memory.c','codec/jpeg_backing.c','codec/jpeg_coefficients.c','storage/jpeg_nor.c','storage/jpeg_journal.c','storage/jpeg_scratch.c','app/media/color_convert.c','tests/jpeg_cache/decoder_driver.c']
    pins=json.loads((args.build/'inputs.json').read_text());pins[str(Path(__file__).resolve())]=sha(Path(__file__))
    assert all(sha(Path(p))==h for p,h in pins.items())
    contract=json.loads((args.contract/'report.json').read_text());assert contract['passed']
    case=next(r for r in contract['positive'] if r['name']=='rich-cmyk-progressive-12.jpg')
    image=args.contract/'fixtures'/case['name'];assert sha(image)==case['fixture_sha256']
    report=dict(passed=False,cases=[],inputs_sha256=pins)
    try:
        for name,(scope,before,after) in needles.items():
            start=original.index(scope) if scope else 0
            # Limit replacement to its actual function when shared with another API.
            at=original.index(before,start);text=original[:at]+original[at:].replace(before,after,1)
            folder=(args.output/name).resolve();folder.mkdir();changed=folder/'mutant.c';exe=folder/'mutant.exe';batch=folder/'compile.cmd'
            changed.write_text(text,encoding='utf-8',newline='\n')
            real=name=='trust-decoder-read';files=[changed]+[PROJECT/n for n in (full if real else native)]
            includes=[resources.resolve(),PROJECT/'storage',PROJECT/'codec',PROJECT/'app/include']
            if real:includes += [args.library_build.resolve()/'source/src',args.library_build.resolve()/'library']
            command='cl /nologo /std:c11 /O2 /W3 /MT /DJPEG_STATIC /D_CRT_SECURE_NO_WARNINGS '+ ' '.join('/I"'+str(p)+'"' for p in includes)+' '+ ' '.join('"'+str(p)+'"' for p in files)+' /Fe"'+str(exe)+'" /link bcrypt.lib'
            if real:command += ' "'+str(args.library_build.resolve()/'library/jpeg-static.lib')+'"'
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd)+'" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\nwhere cl > compiler-path.txt\n'+command+'\nexit /b %errorlevel%\n',encoding='utf-8',newline='\r\n')
            built=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
            (folder/'compile.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,name
            if real:
                first,cold=folder/'first.rgb',folder/'cold.rgb'
                result=subprocess.run([str(exe),str(image.resolve()),str(first),str(cold),'silent','378'],capture_output=True,timeout=30)
                assert result.returncode==0,(name,result.returncode,result.stderr)
                data=json.loads(result.stdout)
                caught=data['first']['ready'] and data['first']['cache_result']==0 and sha(first)!=case['rgb565_sha256'] and sha(cold)==sha(first)
                assert caught,(name,data)
                reason='Independent oracle rejects wrong cached pixels after an actual silent source read fault'
            else:
                result=subprocess.run([str(exe),'--quick'],capture_output=True,timeout=30)
                assert result.returncode==1 and b'FAIL ' in result.stderr,(name,result.returncode,result.stdout,result.stderr)
                reason=result.stderr.decode(errors='replace').strip()
            (folder/'run.log').write_bytes(result.stdout+result.stderr)
            compiler=Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            report['cases'].append(dict(name=name,rejected=True,source_sha256=sha(changed),executable_sha256=sha(exe),compiler_sha256=sha(compiler),reason=reason))
            print('REJECTED cache mutant:',name,flush=True)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in pins.items());report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
