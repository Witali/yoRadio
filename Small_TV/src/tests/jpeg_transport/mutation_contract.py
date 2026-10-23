"""Require compiled unsafe transport variants to fail real contract assertions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT=Path(__file__).resolve().parents[2]


def sha(path):
    """Pin exact compiler inputs/products rather than planned command success."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Compilation/loader errors are never counted as a caught unsafe transport."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    source=PROJECT/'storage/jpeg_transport.c';test=Path(__file__).with_name('native_test.c');original=source.read_text()
    mutants={
        'bypass_guard':('if(checked!=JPEG_GUARD_OK)','if(false)'),
        'ignore_epoch':('port->epoch!=t->epoch','false'),
        'ignore_port_bounds':('!covered(address,bytes,port->extents,port->count)','false'),
        'write_readonly':("(operation!='R' && !port->writable)",'false'),
        'ignore_call_limit':('t->usage.calls>=t->limits.calls','false'),
        'ignore_read_limit':("(operation=='R' && bytes>t->limits.read_bytes-t->usage.read_bytes)",'false'),
        'ignore_program_limit':("(operation=='P' && bytes>t->limits.program_bytes-t->usage.program_bytes)",'false'),
        'ignore_erase_limit':("(operation=='E' && t->usage.erase_calls>=t->limits.erase_calls)",'false'),
        'ignore_post_deadline':('jpeg_transport_result_t result=deadline(t);return result==JPEG_TRANSPORT_OK ? 0 : -(int)result;','return 0;'),
        'ignore_final_guard_deadline':('result=deadline(t);t->verifying=NULL;t->active=false;','result=JPEG_TRANSPORT_OK;t->verifying=NULL;t->active=false;'),
        'reset_budget_per_port':('*device=(jpeg_nor_device_t){port,t->raw.flash_bytes,t->raw.page_bytes,port_read,port_program,port_erase};',
                                 'memset(&t->usage,0,sizeof(t->usage));\n    *device=(jpeg_nor_device_t){port,t->raw.flash_bytes,t->raw.page_bytes,port_read,port_program,port_erase};'),
        'retain_revoked_authority':('if(t){t->active=false;t->authorized=false;t->verifying=NULL;}',
                                    'if(t){t->active=false;t->verifying=NULL;}'),
        'ignore_io_error':('if(io_error)return -(int)stop(t,JPEG_TRANSPORT_IO);','if(false)return -(int)stop(t,JPEG_TRANSPORT_IO);'),
        'skip_cooperative_check':('    return deadline(t);','    return JPEG_TRANSPORT_OK;'),
    }
    inputs=[source,PROJECT/'storage/jpeg_transport.h',PROJECT/'storage/jpeg_guard.c',PROJECT/'storage/jpeg_guard.h',PROJECT/'storage/jpeg_provision.c',PROJECT/'storage/jpeg_provision.h',
            PROJECT/'storage/jpeg_nor.h',test,Path(__file__),args.fixtures/'jpeg_layout.h',args.fixtures/'probe_map.h',
            args.fixtures/'assets.bin',args.vs_dev_cmd]
    report=dict(passed=False,cases=[],inputs_sha256={str(p.resolve()):sha(p) for p in inputs})
    try:
        for name,(before,after) in mutants.items():
            if original.count(before)!=1:raise ValueError('Mutation anchor changed: '+name)
            folder=(args.output/name).resolve();folder.mkdir();changed=folder/'mutant.c';executable=folder/'mutant.exe'
            changed.write_text(original.replace(before,after),encoding='utf-8',newline='\n');batch=folder/'compile.cmd'
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd.resolve())+'" -arch=x64 -host_arch=x64 >nul\n'
                'if errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\nwhere cl > compiler-path.txt\n'
                'cl /nologo /std:c11 /O2 /W3 /D_CRT_SECURE_NO_WARNINGS /I"'+str(args.fixtures.resolve())+'" '
                '/I"'+str(PROJECT/'storage')+'" "'+str(test)+'" "'+str(changed)+'" "'+str(PROJECT/'storage/jpeg_guard.c')+'" "'+str(PROJECT/'storage/jpeg_provision.c')+'" '
                '/Fe"'+str(executable)+'" /link bcrypt.lib\nexit /b %errorlevel%\n',encoding='utf-8',newline='\r\n')
            compiled=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            if compiled.returncode:raise RuntimeError('Mutant did not compile: '+name)
            compiler=Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            result=subprocess.run([str(executable),str((args.fixtures/'assets.bin').resolve())],capture_output=True,timeout=60)
            (folder/'run.log').write_bytes(result.stdout+result.stderr)
            if result.returncode!=1 or b'FAIL ' not in result.stderr:raise AssertionError('Mutant escaped: '+name)
            report['cases'].append(dict(name=name,rejected=True,exit_code=result.returncode,source_sha256=sha(changed),
                executable_sha256=sha(executable),compiler_sha256=sha(compiler),assertion=result.stderr.decode('utf-8',errors='replace').strip()))
            print('REJECTED transport mutant:',name,flush=True)
        report['passed']=len(report['cases'])==len(mutants)
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    main()
