"""Test flash-resident heap routines with compact AAC after the RAM-only run."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, require
from ota import image_info
root=Path('.build/idf-upgrade')
require('Qualification held for investigation before public-https' in
        (root/'physical-6.1-compact-ram-stage.log').read_text(),'Previous board owner is still running')
label='6.1-compact-heap'
image=Path('firmware/development/esp32c3-idf-'+label+'-profile/app.bin')
old=Path('firmware/development/esp32c3-idf-6.1-compact-ram-profile/app.bin')
require(Board('http://192.168.100.4').info()['app_elf_sha256']==image_info(old.read_bytes())['app_elf_sha256'],
        'Unexpected installed image')
objdump=next(Path('C:/Work/yoRadio/.idf/tools-v6.1').glob('tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'))
phases=[]
def run(name,script,args,required=False):
    if (root/('hold-'+label)).exists():raise SystemExit('Held before '+name)
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=2400).returncode
    phases.append(dict(name=name,returncode=code,command=command))
    (root/('physical-'+label+'-check.json')).write_text(json.dumps(phases,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise SystemExit('Required phase failed: '+name)
run('verify-'+label+'-profile','tools/codec_benchmark/verify_aac_network_build.py',
    ['--build','idf/esp32c3-oled-native/build-idf-'+label+'-profile','--objdump',objdump,
     '--output',root/('verify-'+label+'-profile.json')],True)
run('install-'+label+'-profile','.build/idf-upgrade/install.py',
    ['--firmware',image,'--output',root/('install-'+label+'-profile.json')],True)
for transport in ('http','https'):
    name='physical-'+label+'-public-'+transport
    run(name,'tools/esp32c3_tests/public_streams.py',
        ['--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,
         '--transport',transport,'--seconds','60','--output',root/name])
print('HEAP_CHECK_COMPLETE',flush=True)
