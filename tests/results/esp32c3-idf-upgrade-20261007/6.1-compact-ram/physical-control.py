"""Matched old-SDK load control, then restore the tested 6.0.3 production app."""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board
from ota import image_info
root=Path('.build/idf-upgrade')
production=Path('firmware/development/esp32c3-idf-6.0.3-production/app.bin')
profile=Path('firmware/development/esp32c3-idf-6.0.2-profile/app.bin')
new_profile=Path('firmware/development/esp32c3-idf-6.0.3-profile/app.bin')
b=Board('http://192.168.100.4')
assert b.info()['app_elf_sha256']==image_info(production.read_bytes())['app_elf_sha256']
def run(name,script,args,required=False):
 command=[sys.executable,'-X','utf8',script,*map(str,args)]
 with (root/(name+'.log')).open('xb') as f:
  code=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=1800).returncode
 print(name,code,flush=True)
 if required:assert code==0,'Control installation failed; inspect the retained report'
 return code
run('physical-6.0.3-http-headers','tools/esp32c3_tests/http_headers.py',
 ['--board',b.origin,'--firmware',production,'--output',root/'physical-6.0.3-http-headers.json'])
run('install-6.0.3-switch-recheck','.build/idf-upgrade/install.py',
 ['--firmware',new_profile,'--output',root/'install-6.0.3-switch-recheck.json'],True)
def switching(version,firmware):
 run(f'physical-{version}-switch-recheck','tools/esp32c3_tests/run.py',
  ['--board',b.origin,'--host','192.168.100.253','--serial-port','COM9',
   '--suite','switch','--cycles','3','--sdkconfig',firmware.with_name('sdkconfig'),
   '--output',root/f'physical-{version}-switch-recheck'])
switching('6.0.3',new_profile)
run('install-6.0.2-control','.build/idf-upgrade/install.py',
 ['--firmware',profile,'--output',root/'install-6.0.2-control.json'],True)
args=['--board',b.origin,'--host','192.168.100.253','--serial-port','COM9',
 '--suite','load','--load-seconds','60','--load-idle-recovery',
 '--fixture-manifest',root/'stress-fixtures/manifest.json','--sdkconfig',profile.with_name('sdkconfig'),
 '--output',root/'physical-6.0.2-load-control']
for name in ('stress-mp3-48000-2ch-16bit-65s','stress-flac-48000-2ch-16bit-65s',
 'stress-vorbis-48000-2ch-16bit-65s','stress-opus-48000-2ch-16bit-65s','lc-48000-stereo'):
 args+=['--case',name]
run('physical-6.0.2-load-control','tools/esp32c3_tests/run.py',args)
run('physical-6.0.2-load-summary','tools/esp32c3_tests/load_windows.py',
 ['--input',root/'physical-6.0.2-load-control','--output',root/'physical-6.0.2-load-summary.json'])
switching('6.0.2',profile)
run('restore-6.0.3-production','.build/idf-upgrade/install.py',
 ['--firmware',production,'--output',root/'restore-6.0.3-production.json'],True)
run('physical-6.0.3-quiet-https','.build/idf-upgrade/quiet-public.py',
 ['--firmware',production,'--output',root/'physical-6.0.3-quiet-https'])
print('CONTROL_COMPLETE',flush=True)
