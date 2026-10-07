"""Qualify the RAM correction after the isolated HE-AAC check releases the board."""
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, require
from ota import image_info

root=Path('.build/idf-upgrade')
label='6.1-compact-ram'
profile=Path('firmware/development/esp32c3-idf-'+label+'-profile/app.bin')
deadline=time.monotonic()+900
while 'RAM_CHECK_COMPLETE' not in (root/'physical-6.1-compact-ram-check-stage.log').read_text():
    if time.monotonic()>deadline:raise SystemExit('RAM check has not released the board')
    time.sleep(5)
prior=json.loads((root/'physical-6.1-compact-ram-check/report.json').read_text())
require(all(row['result']=='PASS' for row in prior['cases']),'Isolated HE-AAC RAM checks failed')
board=Board('http://192.168.100.4')
require(board.info()['app_elf_sha256']==image_info(profile.read_bytes())['app_elf_sha256'],
        'RAM profile is not installed')
phases=[]
def run(name,script,args,timeout=2400):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
    phases.append(dict(name=name,returncode=code,seconds=time.monotonic()-started,command=command))
    (root/('physical-'+label+'-full.json')).write_text(json.dumps(phases,indent=2)+'\n')
    print('END',name,code,flush=True)
    if code:raise SystemExit('Required phase failed: '+name)
run('physical-'+label+'-matrix','tools/esp32c3_tests/run.py',
    ['--board',board.origin,'--host','192.168.100.253','--serial-port','COM9',
     '--sdkconfig',profile.with_name('sdkconfig'),'--suite','http','--suite','eof',
     '--suite','transitions','--suite','faults','--suite','websocket',
     '--suite','boot-time','--suite','tls-rejection','--cycles','2',
     '--https-origin','https://192.168.100.253:8771',
     '--tls-cert',root/'tls/cert.pem','--tls-key',root/'tls/key.pem',
     '--output',root/('physical-'+label+'-matrix')])
run('physical-'+label+'-stage','.build/idf-upgrade/physical-stage.py',
    ['--version',label],timeout=7200)
print('FULL_RAM_COMPLETE',flush=True)
