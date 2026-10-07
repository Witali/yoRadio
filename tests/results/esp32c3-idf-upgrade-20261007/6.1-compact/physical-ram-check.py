"""Single-board RAM-profile experiment after the initial matrix releases it."""
import json
from pathlib import Path
import subprocess
import sys
import time

root=Path('.build/idf-upgrade')
image=Path('firmware/development/esp32c3-idf-6.1-compact-ram-profile/app.bin')
build=Path('idf/esp32c3-oled-native/build-idf-6.1-compact-ram-profile')
deadline=time.monotonic()+2400
while True:
    previous=(root/'physical-6.1-compact-next.log').read_text()
    if 'Required phase failed: physical-6.1-compact-stage' in previous and image.exists():break
    if time.monotonic()>deadline:raise SystemExit('Prior hardware owner or build has not completed')
    time.sleep(5)
objdump=next(Path('C:/Work/yoRadio/.idf/tools-v6.1').glob('tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'))
def run(name,script,args,required=False):
    print('START',name,flush=True)
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run([sys.executable,'-X','utf8',script,*map(str,args)],
                            stdout=log,stderr=subprocess.STDOUT,timeout=1200).returncode
    print('END',name,code,flush=True)
    if required and code:raise SystemExit('Required phase failed: '+name)
run('verify-6.1-compact-ram-profile','tools/codec_benchmark/verify_aac_network_build.py',
    ['--build',build,'--objdump',objdump,'--output',root/'verify-6.1-compact-ram-profile.json'],True)
run('install-6.1-compact-ram-profile','.build/idf-upgrade/install.py',
    ['--firmware',image,'--output',root/'install-6.1-compact-ram-profile.json'],True)
run('physical-6.1-compact-ram-check','tools/esp32c3_tests/run.py',
    ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
     '--sdkconfig',image.with_name('sdkconfig'),'--suite','http','--suite','transitions',
     '--case','he-44100-stereo','--case','he-48000-stereo','--case','hev2-44100-stereo',
     '--output',root/'physical-6.1-compact-ram-check'])
print('RAM_CHECK_COMPLETE',flush=True)
