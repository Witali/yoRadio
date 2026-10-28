"""Compile unsafe bootstrap variants and require a real contract assertion."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT=Path(__file__).resolve().parents[2]

def sha(path):
    """Pin compiled bytes and exact inputs; loader errors never count as rejection."""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    """Exercise independent immutable, vacancy, torn-write and budget invariants."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    core=PROJECT/'storage/jpeg_provision.c';transport=PROJECT/'storage/jpeg_transport.c'
    mutants={
        'ignore_vacancy':(core,'if(bytes[j]!=0xff)','if(false)'),
        'ignore_stamp_zeros':(core,'(current[i]&stamp->bytes[i])!=stamp->bytes[i]','false'),
        'single_candidate_read':(core,
            'if(!diagnostic->io_error)diagnostic->io_error=device->read(device->context,address,second,bytes);',
            'if(!diagnostic->io_error)memcpy(second,data,bytes);'),
        'ignore_stamp_descriptor_hash':(core,'diagnostic->guard=stamp_identity(resource,stamp,sha256);','diagnostic->guard=JPEG_GUARD_OK;'),
        'ignore_phase_readback':(core,'memcmp(actual,data,bytes)','false'),
        'ignore_ordered_state':(core,
            'if(!header_erased && memcmp(current+JPEG_PROVISION_HEADER_BYTES,\n        stamp->bytes+JPEG_PROVISION_HEADER_BYTES,JPEG_PROVISION_ID_BYTES))return JPEG_PROVISION_STAMP;',
            '(void)header_erased;'),
        'ignore_final_physical_guard':(core,
            'diagnostic->guard=jpeg_guard_verify(layout,observed,observed_count,device,sha256);\n    diagnostic->status=diagnostic->guard==JPEG_GUARD_OK ?',
            'diagnostic->guard=JPEG_GUARD_OK;\n    diagnostic->status=diagnostic->guard==JPEG_GUARD_OK ?'),
        'reset_budget_at_program':(transport,"jpeg_transport_result_t result=charge(t,'P',bytes);",
            "memset(&t->usage,0,sizeof(t->usage));jpeg_transport_result_t result=charge(t,'P',bytes);")}
    inputs=[core,transport,PROJECT/'storage/jpeg_guard.c',PROJECT/'storage/jpeg_guard.h',
        PROJECT/'storage/jpeg_transport.h',PROJECT/'storage/jpeg_provision.h',PROJECT/'storage/jpeg_nor.h',
        Path(__file__).with_name('native_test.c'),Path(__file__),args.fixtures/'jpeg_layout.h',args.fixtures/'assets.bin']
    report=dict(passed=False,cases=[],inputs_sha256={str(p.resolve()):sha(p) for p in inputs})
    try:
        for name,(source,before,after) in mutants.items():
            text=source.read_text();assert text.count(before)==1,name
            folder=args.output/name;folder.mkdir();changed=(folder/'mutant.c').resolve();changed.write_text(text.replace(before,after),newline='\n')
            executable=(folder/'mutant.exe').resolve();batch=(folder/'compile.cmd').resolve()
            sources=[Path(__file__).with_name('native_test.c'),PROJECT/'storage/jpeg_guard.c',
                changed if source==core else core,changed if source==transport else transport]
            command='cl /nologo /std:c11 /O2 /W3 /D_CRT_SECURE_NO_WARNINGS /I"'+str(args.fixtures.resolve())+'" /I"'+str(PROJECT/'storage')+'" '
            command+=' '.join('"'+str(p.resolve())+'"' for p in sources)+' /Fe"'+str(executable)+'" /link bcrypt.lib'
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd)+'" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "'+str(folder.resolve())+'"\n'+command+'\nexit /b %errorlevel%\n',newline='\r\n')
            compiled=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=90)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            assert compiled.returncode==0,'Compilation failure is not rejection: '+name
            ran=subprocess.run([str(executable),str((args.fixtures/'assets.bin').resolve())],capture_output=True,timeout=120)
            (folder/'run.log').write_bytes(ran.stdout+ran.stderr)
            assert ran.returncode==1 and b'FAIL ' in ran.stderr,'Unsafe variant escaped or crashed: '+name
            report['cases'].append(dict(name=name,rejected=True,executable_sha256=sha(executable),source_sha256=sha(changed),assertion=ran.stderr.decode(errors='replace').strip()))
            print('REJECTED provision mutant:',name,flush=True)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==digest for p,digest in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':main()
