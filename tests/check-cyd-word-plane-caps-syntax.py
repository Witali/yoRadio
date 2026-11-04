"""Actual Xtensa syntax-only preparation of the NEW public-capability TU."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'tests/target/cyd_word_plane_caps_qemu/project/main/main.c'
HELPER=ROOT/'idf/components/native_stream/include/pcm_word_plane.h'
PIN='8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b'
ARGUMENTS=ROOT/'tests/windows_compile_command.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def identity(path):
    body=path.read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--recipe',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();recipe=args.recipe.resolve()
    need(sys.platform=='win32' and out.is_relative_to(ROOT/'.build') and not out.exists() and recipe.is_relative_to(ROOT/'.build'),'fresh local syntax-only capture')
    need(identity(HELPER)['sha256']==PIN,'exact separately qualified helper before syntax freeze')
    spec=importlib.util.spec_from_file_location('reviewed_windows_recipe_arguments',ARGUMENTS);arguments=importlib.util.module_from_spec(spec);spec.loader.exec_module(arguments)
    path=recipe/'build/compile_commands.json';commands=json.loads(path.read_bytes());selected=[row for row in commands if Path(row['file']).name=='audio_service.c'];need(len(selected)==1,'one actual completed SDK C recipe')
    out.mkdir();(out/'sources').mkdir();(out/'config').mkdir();(out/'tmp').mkdir()
    report=dict(passed=False,syntax_only=True,SDK_started=False,QEMU_started=False,actual_word_access_qualified=False,recipe=dict(path=str(path),**identity(path)),sources=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(source,destination):
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(source.read_bytes());report['sources'].append(dict(path=str(source),snapshot=destination.relative_to(out).as_posix(),**identity(source)))
    try:
        for source,name in ((MAIN,'main.c'),(HELPER,'pcm_word_plane.h'),(Path(__file__).resolve(),'controller.py'),(ARGUMENTS,'windows-argument-parser.py')):freeze(source,out/'sources'/name)
        for source in (recipe/'build/config').iterdir():
            if source.is_file():freeze(source,out/'config'/source.name)
        row=selected[0];argv=arguments.windows_argv(row['command']);compiler=Path(argv[0]);command=[str(compiler),'-I'+str(out/'sources'),'-I'+str(out/'config')];index=1
        while index<len(argv):
            value=argv[index]
            if value in ('-o','-MF','-MT','-MQ'):index+=2;continue
            if value in ('-c','-MD','-MMD','-MP','-fstack-usage'):index+=1;continue
            if value==row['file']:value=str(out/'sources/main.c')
            elif value.startswith('-I') and Path(value[2:]).resolve()==(recipe/'build/config').resolve():index+=1;continue
            elif value.startswith('@'):
                original=Path(value[1:]);original=original if original.is_absolute() else Path(row['directory'])/original
                relative=Path('responses')/str(index)/original.name;freeze(original,out/relative);value='@'+str(out/relative)
            command.append(value);index+=1
        command.append('-fsyntax-only');report.update(argv=command,compiler=dict(path=str(compiler),**identity(compiler)));save()
        environment=dict(os.environ,PYTHONNOUSERSITE='1',TMP=str(out/'tmp'),TEMP=str(out/'tmp'))
        start=time.monotonic()
        with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
            child=subprocess.Popen(command,cwd=Path(row['directory']),env=environment,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            report['pid']=child.pid;save()
            try:status=child.wait(timeout=60)
            except subprocess.TimeoutExpired:
                stopped=subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
                report.update(forced_stop_nonpass=True,tree_stop_returncode=stopped.returncode)
                if child.poll() is None:child.kill()
                report['exit_status']=child.wait(timeout=15);raise
        report.update(exit_status=status,elapsed_seconds=time.monotonic()-start,stdout=identity(out/'stdout.log'),stderr=identity(out/'stderr.log'))
        need(status==0 and (out/'stderr.log').stat().st_size==0,'actual installed Xtensa TU syntax has no diagnostics')
        need(all(identity(Path(pin['path']))==dict(bytes=pin['bytes'],sha256=pin['sha256']) and identity(out/pin['snapshot'])==dict(bytes=pin['bytes'],sha256=pin['sha256']) for pin in report['sources']),'all original and frozen diagnostic/helper/recipe inputs unchanged')
        report['passed']=True;print(json.dumps(dict(passed=True,actual_Xtensa_TUs=1,SDK_started=False,QEMU_started=False)));return 0
    except Exception as error:report.update(failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:save()


if __name__=='__main__':sys.dont_write_bytecode=True;raise SystemExit(main())
