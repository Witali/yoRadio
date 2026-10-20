"""Compile unsafe adapter variants; require runtime assertions, not build failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]


def sha(path):
    """Identify source, compiler and executable for each rejected variant."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Keep production sources intact while testing real NOR/adapter behavior."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    source=PROJECT/'codec/jpeg_backing.c';original=source.read_text()
    mutants={
        'prepare-before-prefix-validation': [('if(bytes && (offset>r->initialized || (!writing && bytes>r->initialized-offset)))','if(false)')],
        'erase-initialized-neighbor': [('if(b->fresh[sector/8u]&mask)continue;','if(false)continue;')],
        'ignore-ram-checkpoint': [('if(b->scratch.check(b->scratch.check_context))','if(false)')],
        'mix-raw-and-packed': [('(b->mode && b->mode!=mode)','false')],
        'reuse-stale-id': [('b->active=false;b->mode=0;','b->active=false;b->mode=0;b->scratch.next_id=0;')],
        'checkpoint-cleanup': [('return b->last_error=jpeg_scratch_close(&file);','if(checkpoint(b))return b->last_error=JPEG_SCRATCH_STOP;\n    return b->last_error=jpeg_scratch_close(&file);')],
    }
    names=['codec/jpeg_backing.h','codec/jpeg_coefficients.c','codec/jpeg_coefficients.h','codec/jpeg_decoder.h','storage/jpeg_scratch.c','storage/jpeg_scratch.h','storage/jpeg_nor.c','storage/jpeg_nor.h','tests/jpeg_backing/native_test.c','tests/jpeg_scratch/nor_model.c','tests/jpeg_scratch/nor_model.h']
    paths=[PROJECT/n for n in names]+[source,Path(__file__),args.fixtures/'scratch_fixture.h',args.vs_dev_cmd]
    report=dict(passed=False,cases=[],inputs_sha256={str(p.resolve()):sha(p) for p in paths})
    try:
        for name,replacements in mutants.items():
            text=original
            for before,after in replacements:
                assert text.count(before)==1,(name,before);text=text.replace(before,after)
            folder=(args.output/name).resolve();folder.mkdir()
            changed,exe,batch=[folder/n for n in ('mutant.c','mutant.exe','compile.cmd')]
            changed.write_text(text,encoding='utf-8',newline='\n')
            includes=[PROJECT/'codec',PROJECT/'storage',PROJECT/'tests/jpeg_scratch',args.fixtures.resolve()]
            files=[changed]+[PROJECT/n for n in names if n.endswith('.c')]
            command='cl /nologo /std:c11 /O2 /W3 '+ ' '.join('/I"'+str(p)+'"' for p in includes)+' '+ ' '.join('"'+str(p)+'"' for p in files)+' /Fe"'+str(exe)+'"'
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd)+'" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\nwhere cl > compiler-path.txt\n'+command+'\nexit /b %errorlevel%\n',encoding='utf-8',newline='\r\n')
            built=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
            (folder/'compile.log').write_bytes(built.stdout+built.stderr);assert built.returncode==0,name
            result=subprocess.run([str(exe)],capture_output=True,timeout=30)
            (folder/'run.log').write_bytes(result.stdout+result.stderr)
            assert result.returncode==1 and b'FAIL ' in result.stderr,(name,result.returncode,result.stdout,result.stderr)
            compiler=Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            report['cases'].append(dict(name=name,rejected=True,source_sha256=sha(changed),executable_sha256=sha(exe),compiler_sha256=sha(compiler),assertion=result.stderr.decode(errors='replace').strip()))
            print('REJECTED adapter mutant:',name,flush=True)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in report['inputs_sha256'].items());report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
