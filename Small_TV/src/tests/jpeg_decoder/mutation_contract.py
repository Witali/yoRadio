"""Require compiled decoder defects to fail resource/error/cleanup/pixel contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[1]


def sha(path):
    """Bind actual compiler inputs and outputs to the checks."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Compile errors/crashes do not count as caught mutations."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--contract',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    build=json.loads((args.build/'build.json').read_text());inputs=json.loads((args.build/'inputs.json').read_text())
    assert all(sha(Path(p))==h for p,h in inputs.items())
    library=Path(build['library_build']);contract=json.loads((args.contract/'report.json').read_text())
    golds={c['name']:c['rgb565_sha256'] for c in contract['positive']}
    fixtures=args.contract/'fixtures';full=fixtures/'full-cmyk12.jpg';small=fixtures/'cmyk-progressive-12.jpg'
    report=dict(passed=False,cases=[],controls=[],inputs_sha256=inputs,runner_sha256=sha(Path(__file__)))

    def exercise(executable,folder,case):
        """One independent gate detects either an assertion or the wrong public result."""
        first,second=folder/'first.rgb',folder/'second.rgb'
        image=fixtures/'sampling-44-c4-12.jpg' if case=='padded' else fixtures/'oversize.jpg' if case=='width' else small if case=='orphan' else full
        pool=262144 if case=='padded' else 1 if case=='pool' else 65536
        backing=0 if case=='preflight' else 460800
        command=[str(executable),str(image.resolve()),str(first),str(second),'240',str(pool),str(backing)]
        if case=='orphan':command+=['time','6']
        result=subprocess.run(command,capture_output=True,timeout=30)
        (folder/'run.log').write_bytes(result.stdout+result.stderr)
        assert result.returncode in (0,1),(case,result.returncode,result.stderr)
        if result.returncode:
            assert b'FAIL ' in result.stderr,(case,result.stderr)
            return False,dict(exit_code=result.returncode,assertion=result.stderr.decode(errors='replace').strip())
        record=json.loads(result.stdout);d=record['first'];ok=True
        if case in ('preflight','padded'):
            required=524288 if case=='padded' else 460800
            ok=d['status']=='backing-capacity' and d['required']==required and d['available']==backing and d['opened']==0 and d['visits']['open']==0
        elif case=='pool':ok=d['status']=='library-pool-limit' and d['required']>1 and d['available']==1
        elif case=='width':ok=d['status']=='image-dimensions' and d['required']==65535 and d['available']==240
        elif case=='orphan':
            ok=d['status']=='time-limit' and d['opened']==d['closed']==1 and record['recovery']['status']=='ok' and sha(second)==golds[small.name]
        elif case=='reuse':
            ok=d['status']==record['recovery']['status']=='ok' and record['recovery']['reused_object'] and sha(first)==sha(second)==golds[full.name]
        return ok,record

    mutations={
        'skip_whole_preflight':('memory','if(s->diagnostic.backing_required>s->config.backing.capacity)','if(false)','preflight'),
        'wrong_padded_size':('memory','account(s,columns,rows,access,sizeof(JBLOCK));','account(s,columns,rows,access,sizeof(JBLOCK)-1);','padded'),
        'allocation_is_bad_jpeg':('decoder','status=s->allocation_status ? s->allocation_status : JPEG_DECODE_ALLOCATION;','status=JPEG_DECODE_INVALID;','pool'),
        'leak_post_open_orphan':('decoder','    jpeg_decoder_release_backing(s);','    (void)s;','orphan'),
        'forget_job_reset':('decoder','s->diagnostic=(jpeg_decode_diagnostic_t){0};','/* retain stale diagnosis */','reuse'),
        'oversize_is_bad_jpeg':('decoder','status=JPEG_DECODE_DIMENSIONS;s->diagnostic.width','status=JPEG_DECODE_INVALID;s->diagnostic.width','width'),
    }
    for name,(kind,before,after,case) in mutations.items():
        folder=(args.output/name).resolve();folder.mkdir()
        good,control=exercise(Path(build['executable']),folder,case);assert good,(name,control)
        report['controls'].append(dict(name=case,result=control))
        path=PROJECT/('codec/jpeg_'+kind+'.c');original=path.read_text();assert original.count(before)==1,(name,before)
        changed=folder/'mutant.c';changed.write_text(original.replace(before,after),encoding='utf-8',newline='\n')
        sources=[changed if kind=='decoder' else PROJECT/'codec/jpeg_decoder.c',changed if kind=='memory' else PROJECT/'codec/jpeg_memory.c',PROJECT/'app/media/color_convert.c',HERE/'driver.c']
        includes=[PROJECT/'codec',PROJECT/'app/include',library/'source/src',library/'library']
        exe=folder/'mutant.exe';batch=folder/'compile.cmd'
        command=['cl','/nologo','/std:c11','/O2','/W3','/MT','/DJPEG_STATIC','/D_CRT_SECURE_NO_WARNINGS']
        command+=['/I"'+str(p)+'"' for p in includes]+['"'+str(p)+'"' for p in sources]
        command+=['/Fe"'+str(exe)+'"','/link','"'+str(library/'library/jpeg-static.lib')+'"']
        batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd)+'" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\n'+' '.join(command)+'\nexit /b %errorlevel%\n',encoding='utf-8',newline='\r\n')
        compiled=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
        (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr);assert compiled.returncode==0,(name,compiled.stdout,compiled.stderr)
        good,record=exercise(exe,folder,case);assert not good,(name,'unsafe mutant escaped',record)
        report['cases'].append(dict(name=name,rejected=True,source_sha256=sha(changed),executable_sha256=sha(exe),result=record))
        print('REJECTED native decoder mutant:',name,flush=True)
    report['inputs_unchanged']=all(sha(Path(p))==h for p,h in inputs.items());report['passed']=report['inputs_unchanged'] and len(report['cases'])==len(mutations)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
