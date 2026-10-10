"""One board owner; matched local ten-minute RX-copy controls and HTTPS probes."""
import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/c3-memory-20261007')
results=[]
def run(name,script,args,required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500).returncode
    results.append(dict(name=name,code=code,seconds=time.monotonic()-started,command=command))
    (root/'physical-pair.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise RuntimeError('Required phase failed: '+name)
try:
    for variant in ('control','rxcopy'):
        image=Path('firmware/development/esp32c3-idf-6.1-memory-'+variant+'-profile/app.bin')
        run('install-'+variant,'.build/idf-upgrade/install.py',
            ['--firmware',image,'--output',root/('install-'+variant+'.json')],True)
        run(variant+'-https','tools/esp32c3_tests/public_streams.py',
            ['--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,
             '--case','groovesalad-64-aac','--transport','https','--seconds','60',
             '--aac-reference-command','.build/idf-upgrade/faad-reference-command.json',
             '--output',root/(variant+'-https')])
        run(variant+'-soak','tools/esp32c3_tests/stream_memory_study.py',
            ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
             '--firmware',image,'--case','hev2-44100-stereo','--seconds','600',
             '--output',root/(variant+'-soak')])
        run(variant+'-soak-summary','tools/esp32c3_tests/summarize_sustained.py',
            ['--input',root/(variant+'-soak'),'--output',root/(variant+'-soak-summary.json')])
finally:
    run('restore-guarded-production','.build/idf-upgrade/install.py',
        ['--firmware','firmware/development/esp32c3-idf-6.1-compact-ram-http-production/app.bin',
         '--output',root/'restore-guarded-production.json'],True)
print('RX_PAIR_COMPLETE',flush=True)
