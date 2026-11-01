"""Fresh syntax-only SDK preflight using an unchanged failed campaign solely as an include/flag recipe."""
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
TARGET=ROOT/'tests/target/cyd_opus_family1_playback_qemu/main'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def windows_argv(command):
    shell=ctypes.WinDLL('shell32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    shell.CommandLineToArgvW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_int)];shell.CommandLineToArgvW.restype=ctypes.POINTER(wintypes.LPWSTR)
    kernel.LocalFree.argtypes=[wintypes.HLOCAL];kernel.LocalFree.restype=wintypes.HLOCAL;count=ctypes.c_int();pointer=shell.CommandLineToArgvW(command,ctypes.byref(count));need(bool(pointer),'actual Windows command-line parse')
    try:return [pointer[i] for i in range(count.value)]
    finally:kernel.LocalFree(ctypes.cast(pointer,wintypes.HLOCAL))
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--recipe',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    recipe=args.recipe.resolve();out=args.output.resolve();need(sys.platform=='win32' and recipe.is_relative_to(ROOT/'.build') and out.is_relative_to(ROOT/'.build') and not out.exists(),'new Windows-only preflight from read-only retained recipe')
    original=recipe/'build/compile_commands.json';rows=[r for r in json.loads(original.read_bytes()) if '/project/main/' in r['file'].replace('\\','/')];need({Path(r['file']).name for r in rows}=={'main.c','direct_reference.c'},'both actual diagnostic TUs in recipe')
    out.mkdir(parents=True);(out/'tmp').mkdir();(out/'sources').mkdir();report=dict(passed=False,completed=False,commands=[],sources=[],syntax_only=True,native_linked=False,target_executed=False,old_recipe=dict(path=str(original),**pin(original)))
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(source,destination):
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(source.read_bytes());report['sources'].append(dict(path=str(source.resolve()),snapshot=destination.relative_to(out).as_posix(),**pin(source)))
    save()
    try:
        for p in (recipe/'build/config').rglob('*'):
            if p.is_file():freeze(p,out/'config'/p.relative_to(recipe/'build/config'))
        for p in (recipe/'project/main').glob('*.h'):
            if p.name!='probe.h':freeze(p,out/'sources'/p.name)
        for name in ('main.c','direct_reference.c','probe.h'):freeze(TARGET/name,out/'sources'/name)
        freeze(Path(__file__),out/'sources/controller.py')
        environment=dict(os.environ,TMP=str(out/'tmp'),TEMP=str(out/'tmp'));compilers=set()
        for row in rows:
            name=Path(row['file']).name;argv=windows_argv(row['command']);compiler=Path(argv[0]);need(compiler.is_file(),'actual installed pinned compiler');compilers.add(compiler)
            result=[str(compiler)];at=1
            while(at<len(argv)):
                value=argv[at]
                if value in ('-o','-MF','-MT','-MQ'):
                    at+=2;continue
                if value in ('-c','-MD','-MMD','-MP','-fstack-usage'):
                    at+=1;continue
                if value==row['file']:value=str(out/'sources'/name)
                elif value.startswith('-I') and Path(value[2:]).resolve()==(recipe/'project/main').resolve():value='-I'+str(out/'sources')
                elif value.startswith('-I') and Path(value[2:]).resolve()==(recipe/'build/config').resolve():value='-I'+str(out/'config')
                elif value.startswith('@'):
                    response=Path(value[1:]);freeze(response,out/'response'/response.name);value='@'+str(out/'response'/response.name)
                result.append(value);at+=1
            result+=['-fsyntax-only','-fdiagnostics-color=never','-MMD','-MF',str(out/(name+'.d')),'-MT',str(out/(name+'.syntax'))]
            need('-c' not in result and '-o' not in result and str(out/'sources'/name) in result,'no old output/object path in syntax-only command')
            command=dict(name=name,argv=result,cwd=str(out),state='starting',compiler=pin(compiler));report['commands'].append(command);save();started=time.monotonic()
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(result,cwd=out,env=environment,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);command.update(pid=child.pid,state='running');save()
                try:status=child.wait(timeout=120)
                except subprocess.TimeoutExpired:child.kill();status=child.wait();command['timed_out']=True
                command.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-started,3))
            command['stdout']=pin(out/(name+'.stdout.log'));command['stderr']=pin(out/(name+'.stderr.log'));save();need(status==0 and not command.get('timed_out'),'actual syntax-only terminal zero '+name)
            command['dependencies']=pin(out/(name+'.d'));need(pin(compiler)==command['compiler'],'unchanged compiler')
        need(pin(original)=={k:report['old_recipe'][k] for k in ('bytes','sha256')},'old compile recipe unchanged')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])=={k:row[k] for k in ('bytes','sha256')},'all actual before/after source/include recipe bytes unchanged')
        report.update(passed=True,completed=True);print(json.dumps(dict(passed=True,syntax_only_tus=2,target_executed=False,old_outputs_mutated=False,capture=out.relative_to(ROOT).as_posix())));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
