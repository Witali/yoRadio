"""Repeat the failed EOF transport check without replacing its original result."""
import json
from pathlib import Path
import subprocess
import sys
import time
root=Path('.build/idf-upgrade')
label='6.1-compact-ram'
deadline=time.monotonic()+1200
while 'Required phase failed: physical-'+label+'-matrix' not in (root/('physical-'+label+'-full.log')).read_text():
    if time.monotonic()>deadline:raise SystemExit('Original matrix has not completed/released the board')
    time.sleep(5)
report=json.loads((root/('physical-'+label+'-matrix/report.json')).read_text())
failures=[row for row in report['cases'] if row['result']!='PASS']
assert failures and all(row['name']=='eof:he-44100-stereo:auto' and
    any(error['type']=='TimeoutError' for error in row.get('exception_chain',[])) for row in failures),failures
profile=Path('firmware/development/esp32c3-idf-'+label+'-profile/sdkconfig')
def run(name,script,args,timeout=2400):
    print('START',name,flush=True)
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run([sys.executable,'-X','utf8',script,*map(str,args)],
                            stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
    print('END',name,code,flush=True)
    if code:raise SystemExit('Required phase failed: '+name)
out=root/('physical-'+label+'-eof-recheck')
run('physical-'+label+'-eof-recheck','tools/esp32c3_tests/run.py',
    ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
     '--sdkconfig',profile,'--suite','eof','--case','he-44100-stereo','--output',out])
run('physical-'+label+'-stage','.build/idf-upgrade/physical-stage.py',
    ['--version',label,'--matrix-recheck',out/'report.json'],timeout=7200)
print('RAM_RECHECK_STAGE_COMPLETE',flush=True)
