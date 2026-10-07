"""Resume physical checks on the same compact defaults with the SDK length guard."""
import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/idf-upgrade')
deadline=time.monotonic()+1800
while 'Qualification held for investigation before quiet-https' not in (root/'physical-6.1-compact-ram-resumed-stage.log').read_text():
    if time.monotonic()>deadline:raise SystemExit('Previous board owner has not released the board')
    time.sleep(3)
image=Path('firmware/development/esp32c3-idf-6.1-compact-ram-http-production/app.bin')
results=json.loads((root/'physical-6.1-compact-ram-http-stage.json').read_text()) if (root/'physical-6.1-compact-ram-http-stage.json').exists() else []
def run(name,script,args,required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1800).returncode
    results.append(dict(name=name,code=code,command=command))
    (root/'physical-6.1-compact-ram-http-stage.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise SystemExit('Required phase failed: '+name)
if results:
    sys.path.insert(0,'tools/esp32c3_tests')
    from common import Board
    from ota import image_info
    assert len(results)==1 and results[0]['code']==0
    assert Board('http://192.168.100.4').info()['app_elf_sha256']==image_info(image.read_bytes())['app_elf_sha256']
    print('RETAIN verified completed guard installation',flush=True)
else:
    run('install-6.1-compact-ram-http','.build/idf-upgrade/install.py',
        ['--firmware',image,'--output',root/'install-6.1-compact-ram-http.json'],True)
run('physical-6.1-compact-ram-http-headers-recheck','tools/esp32c3_tests/http_headers.py',
    ['--board','http://192.168.100.4','--firmware',image,'--output',root/'physical-6.1-compact-ram-http-headers-recheck.json'],True)
run('physical-6.1-compact-ram-http-ota','tools/esp32c3_tests/ota.py',
    ['--board','http://192.168.100.4','--firmware',image,'--suite','negative','--suite','roundtrip',
     '--suite','slow','--output',root/'physical-6.1-compact-ram-http-ota.json'])
args=['--board','http://192.168.100.4','--host','192.168.100.253','--sdkconfig',image.with_name('sdkconfig'),
      '--suite','http','--suite','transitions','--suite','websocket','--suite','boot-time','--cycles','2',
      '--output',root/'physical-6.1-compact-ram-http-production']
for case in ('lc-48000-stereo','he-48000-stereo','hev2-44100-stereo'):
    args+=['--case',case]
run('physical-6.1-compact-ram-http-production','tools/esp32c3_tests/run.py',args)
run('physical-6.1-compact-ram-http-quiet-https','.build/idf-upgrade/quiet-public.py',
    ['--firmware',image,'--output',root/'physical-6.1-compact-ram-http-quiet-https',
     '--aac-reference-command',root/'faad-reference-command.json'])
print('GUARDED_DEFAULT_QUALIFICATION_COMPLETE',flush=True)
