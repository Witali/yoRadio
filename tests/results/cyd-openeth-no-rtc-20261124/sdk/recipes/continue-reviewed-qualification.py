import subprocess
import sys
from common import *
directory=BASE/'legacy'; status=directory/'qualification-reviewed-continuation-status.json'
assert not status.exists()
assert load(directory/'execution-status.json')['state']=='TERMINAL_NONPASS'
assert load(directory/'qualification-continuation-status.json')['state']=='TERMINAL_NONPASS'
guard(load(BASE/'preflight.json'),load(directory/'baseline.json'))
report=dict(state='RUNNING',source_commit=SOURCE,rebuild=False,
    reviewed_exception='Unextracted SDK bootloader descriptor date_time bytes only; all original failures retained.')
write(status,report)
with (directory/'qualify-reviewed.stdout.log').open('xb') as out,(directory/'qualify-reviewed.stderr.log').open('xb') as err:
    child=subprocess.Popen([sys.executable,'-B',str(BASE/'qualify.py'),'legacy'],cwd=ROOT,stdout=out,stderr=err)
    report['child_pid']=child.pid; write(status,report); code=child.wait()
report.update(state='TERMINAL_PASS' if code==0 else 'TERMINAL_NONPASS',exit_status=code)
write(status,report)
raise SystemExit(code)
