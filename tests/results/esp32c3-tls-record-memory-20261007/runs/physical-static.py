import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/c3-tls-records-20261007')
results=[]
image=Path('firmware/development/esp32c3-idf-6.1-memory-icy-static-profile/app.bin')
def run(name,script,args,required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500).returncode
    results.append(dict(name=name,code=code,seconds=time.monotonic()-started,command=command))
    (root/'physical-static.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise RuntimeError('Required phase failed: '+name)
try:
    run('install-static','.build/idf-upgrade/install.py',['--firmware',image,'--output',root/'install-static.json'],True)
    run('static-public','tools/esp32c3_tests/public_streams.py',
        ['--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,'--transport','https','--seconds','60',
         '--aac-reference-command','.build/idf-upgrade/faad-reference-command.json','--output',root/'static-public'])
finally:
    run('restore-icy-quiet','.build/idf-upgrade/install.py',
        ['--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore-icy-quiet.json'],True)
print('STATIC_PHYSICAL_COMPLETE',flush=True)
