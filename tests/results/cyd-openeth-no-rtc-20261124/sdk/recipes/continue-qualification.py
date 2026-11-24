import os
import subprocess
import sys
from common import *
backend=sys.argv[1]; assert backend=='legacy'
directory=BASE/backend; status=directory/'qualification-continuation-status.json'
assert not status.exists()
assert load(directory/'execution-status.json')['state']=='TERMINAL_NONPASS'
assert load(directory/'header-comparison-diagnosis.json')['other_header_bytes_identical']
guard(load(BASE/'preflight.json'),load(directory/'baseline.json'))
report=dict(state='RUNNING',source_commit=SOURCE,reason='Continue static checks after exact CRLF-only helper correction; original failure retained.',rebuild=False)
write(status,report)
with (directory/'qualify-continuation.stdout.log').open('xb') as out,(directory/'qualify-continuation.stderr.log').open('xb') as err:
    child=subprocess.Popen([sys.executable,'-B',str(BASE/'qualify.py'),backend],cwd=ROOT,stdout=out,stderr=err)
    report['child_pid']=child.pid; write(status,report); code=child.wait()
report.update(state='TERMINAL_PASS' if code==0 else 'TERMINAL_NONPASS',exit_status=code)
write(status,report)
raise SystemExit(code)
