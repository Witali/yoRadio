"""Compile new diagnostic TUs syntax-only from immutable actual SDK recipes.

No SDK activation, link, QEMU, firmware or original build-output mutation.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'tests/target/cyd_family1_playback_task_qemu/project/main'


def need(value,reason):
    if not value:raise ValueError(reason)


def identity(path):
    body=Path(path).read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())


def windows_argv(command):
    shell=ctypes.WinDLL('shell32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    shell.CommandLineToArgvW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_int)]
    shell.CommandLineToArgvW.restype=ctypes.POINTER(wintypes.LPWSTR)
    kernel.LocalFree.argtypes=[wintypes.HLOCAL];kernel.LocalFree.restype=wintypes.HLOCAL
    count=ctypes.c_int();pointer=shell.CommandLineToArgvW(command,ctypes.byref(count));need(bool(pointer),'actual Windows argv parse')
    try:return [pointer[index] for index in range(count.value)]
    finally:kernel.LocalFree(ctypes.cast(pointer,wintypes.HLOCAL))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task-recipe',required=True,type=Path)
    parser.add_argument('--reference-recipe',required=True,type=Path)
    parser.add_argument('--assets',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(sys.platform=='win32' and out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local Windows syntax capture')
    captures=[args.task_recipe.resolve(),args.reference_recipe.resolve()];assets=args.assets.resolve()
    need(all(path.is_relative_to(ROOT/'.build') and path.is_dir() for path in [*captures,assets]),'retained task-local recipes/assets')
    report=dict(passed=False,completed=False,syntax_only=True,SDK_build_started=False,QEMU_started=False,
                original_build_outputs_mutated=False,commands=[],sources=[],recipes=[])
    out.mkdir(parents=True);(out/'tmp').mkdir();(out/'sources').mkdir();(out/'config').mkdir()
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,relative):
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        report['sources'].append(dict(path=str(path),snapshot=relative.as_posix(),**identity(path)))
    save()
    try:
        recipes=[]
        for capture in captures:
            path=capture/'build/compile_commands.json';report['recipes'].append(dict(path=str(path),**identity(path)))
            recipes.append(json.loads(path.read_bytes()))
        cpp=[row for row in recipes[0] if Path(row['file']).name=='main.cpp'];need(len(cpp)==1,'one completed actual-task C++ recipe')
        c=[row for row in recipes[1] if Path(row['file']).name=='direct_reference.c'];need(len(c)==1,'one completed independent direct-reference C recipe')
        for path in TARGET.iterdir():
            if path.is_file():freeze(path,Path('sources')/path.name)
        for name in ('reference.h','asset_size.h'):freeze(assets/name,Path('sources')/name)
        for path in (captures[0]/'build/config').iterdir():
            if path.is_file():freeze(path,Path('config')/path.name)
        freeze(Path(__file__).resolve(),Path('sources/syntax-controller.py'))
        for name,row,recipe in [('main.cpp',cpp[0],captures[0]),('reference_control.c',c[0],captures[1]),('direct_reference.c',c[0],captures[1])]:
            argv=windows_argv(row['command']);compiler=Path(argv[0]);need(compiler.is_file(),'actual installed compiler')
            command=[str(compiler),'-I'+str(out/'sources'),'-I'+str(out/'config')];index=1
            while index<len(argv):
                value=argv[index]
                if value in ('-o','-MF','-MT','-MQ'):index+=2;continue
                if value in ('-c','-MD','-MMD','-MP','-fstack-usage'):index+=1;continue
                if value==row['file']:value=str(out/'sources'/name)
                elif value.startswith('-I'):
                    old=Path(value[2:]).resolve()
                    if old in ((recipe/'build/config').resolve(),Path(row['file']).parent.resolve()):index+=1;continue
                elif value.startswith('@'):
                    response=Path(value[1:]);target=Path('responses')/name/response.name;freeze(response,target);value='@'+str(out/target)
                command.append(value);index+=1
            command+=['-fsyntax-only','-fdiagnostics-color=never','-MMD','-MF',str(out/(name+'.d')),'-MT',str(out/(name+'.syntax'))]
            need('-c' not in command and '-o' not in command and str(out/'sources'/name) in command,'syntax-only new source with no original output path')
            event=dict(name=name,argv=command,cwd=str(out),compiler=identity(compiler),state='starting');report['commands'].append(event);save()
            start=time.monotonic();environment=dict(os.environ,TMP=str(out/'tmp'),TEMP=str(out/'tmp'))
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(command,cwd=out,env=environment,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);event.update(pid=child.pid,state='running');save()
                try:status=child.wait(timeout=120)
                except subprocess.TimeoutExpired:child.kill();status=child.wait();event['timed_out']=True
                event.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-start,3))
            event.update(stdout=identity(out/(name+'.stdout.log')),stderr=identity(out/(name+'.stderr.log')));save()
            need(status==0 and not event.get('timed_out'),'actual diagnostic syntax terminal zero: '+name)
            event['dependencies']=identity(out/(name+'.d'));need(identity(compiler)==event['compiler'],'installed compiler unchanged')
        need(all(identity(row['path'])=={key:row[key] for key in ('bytes','sha256')} for row in report['recipes']),'all original compile recipes unchanged')
        need(all(identity(row['path'])==identity(out/row['snapshot'])=={key:row[key] for key in ('bytes','sha256')} for row in report['sources']),'all before/after new sources and recipe inputs unchanged')
        report.update(passed=True,completed=True);print(json.dumps(dict(passed=True,syntax_only_tus=3,SDK_build_started=False,QEMU_started=False)));return 0
    except Exception as error:
        report.update(failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:save()


if __name__=='__main__':raise SystemExit(main())
