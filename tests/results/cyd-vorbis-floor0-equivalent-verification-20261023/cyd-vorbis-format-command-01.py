"""Bounded owned-process command capture for the isolated public-format gate."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--record',type=Path,required=True); p.add_argument('--cwd',type=Path,required=True); p.add_argument('--timeout',type=int,required=True); p.add_argument('argv',nargs=argparse.REMAINDER); a=p.parse_args()
root=Path(__file__).resolve().parent.parent; record=a.record.resolve()
assert record.is_relative_to(root/'.build') and not record.exists() and record.parent.is_dir()
argv=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
assert argv and 1<=a.timeout<=1200
h=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
result={'status':'RUNNING','argv':argv,'cwd':str(a.cwd.resolve()),'timeout_seconds':a.timeout,'runner_sha256':h(__file__),'executable_sha256':h(argv[0])}
stdout=record.with_suffix('.stdout.log'); stderr=record.with_suffix('.stderr.log'); child=None; start=time.monotonic(); good=False
print(json.dumps({'starting':str(record),'argv0':argv[0]}),flush=True)
try:
    with stdout.open('xb') as so,stderr.open('xb') as se:
        env=os.environ.copy(); env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
        child=subprocess.Popen(argv,cwd=a.cwd,stdout=so,stderr=se,stdin=subprocess.DEVNULL,env=env,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        result['owned_pid']=child.pid
        result['returncode']=child.wait(timeout=a.timeout); result['status']='TERMINAL'; good=child.returncode==0
except BaseException as error:
    result.update(status='NONPASS',error_type=type(error).__name__)
finally:
    if child is not None and child.poll() is None:
        subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        if child.poll() is None: child.kill()
        child.wait(timeout=15)
        result['returncode_after_stop']=child.returncode
    result['elapsed_seconds']=time.monotonic()-start
    result['logs']={str(path):{'bytes':path.stat().st_size,'sha256':h(path)} for path in (stdout,stderr) if path.exists()}
    with record.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'record':str(record),'status':result['status'],'returncode':result.get('returncode')}),flush=True)
raise SystemExit(0 if good else 1)
