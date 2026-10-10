"""Install 6.1-compact only after completing the 6.0.3/control hardware sequence."""
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import image_info

root=Path('.build/idf-upgrade')
board=Board('http://192.168.100.4')
old=Path('firmware/development/esp32c3-idf-6.0.3-production/app.bin')
target=Path('firmware/development/esp32c3-idf-6.1-compact-profile/app.bin')
require(board.info()['app_elf_sha256']==image_info(old.read_bytes())['app_elf_sha256'],
        'Expected the tested 6.0.3 production image')
require('CONTROL_COMPLETE' in (root/'physical-6.0.2-control-stage.log').read_text(),
        'Old-SDK control has not completed')
phases=[]
def run(name,script,args,required=False,timeout=2400):
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    print('START',name,flush=True)
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as output:
        result=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT,timeout=timeout)
    phases.append(dict(name=name,returncode=result.returncode,command=command,
                       seconds=time.monotonic()-started))
    (root/'physical-6.1-compact-next.json').write_text(json.dumps(phases,indent=2)+'\n')
    print('END',name,result.returncode,flush=True)
    if required and result.returncode:
        raise SystemExit('Required phase failed: '+name)

run('install-6.1-compact-profile','.build/idf-upgrade/install.py',
    ['--firmware',target,'--output',root/'install-6.1-compact-profile.json'],True)
run('physical-6.1-compact-matrix','tools/esp32c3_tests/run.py',
    ['--board',board.origin,'--host','192.168.100.253','--serial-port','COM9',
     '--sdkconfig',target.with_name('sdkconfig'),'--suite','http','--suite','eof',
     '--suite','transitions','--suite','faults','--suite','websocket',
     '--suite','boot-time','--suite','tls-rejection','--cycles','2',
     '--https-origin','https://192.168.100.253:8771',
     '--tls-cert',root/'tls/cert.pem','--tls-key',root/'tls/key.pem',
     '--output',root/'physical-6.1-compact-matrix'])
run('physical-6.1-compact-stage','.build/idf-upgrade/physical-stage.py',
    ['--version','6.1-compact'],True,timeout=7200)
print('PHYSICAL_61_COMPLETE',flush=True)
