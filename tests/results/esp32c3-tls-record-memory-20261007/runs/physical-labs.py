import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/c3-tls-records-20261007')
results=[]
def run(name,script,args,required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500).returncode
    results.append(dict(name=name,code=code,seconds=time.monotonic()-started,command=command))
    (root/'physical-labs.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise RuntimeError('Required phase failed: '+name)
try:
    run('bundle-audit',str(root/'audit-bundles.py'),[],True)
    for mode in ('dynamic','static'):
        image=Path(f'firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-{mode}/app.bin')
        run('install-lab-'+mode,'.build/idf-upgrade/install.py',
            ['--firmware',image,'--output',root/f'install-lab-{mode}.json'],True)
        run('physical-lab-'+mode,'tools/esp32c3_tests/tls_records.py',
            ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
             '--firmware',image,'--ca',root/'trust/ca.pem','--cert',root/'trust/server.pem','--key',root/'trust/server.key',
             '--seconds','75','--output',root/f'physical-lab-{mode}'])
    run('install-negative-control','.build/idf-upgrade/install.py',
        ['--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-debug/app.bin','--output',root/'install-negative-control.json'],True)
    run('negative-control',str(root/'physical-reject-ca.py'),[])
finally:
    run('restore-after-labs','.build/idf-upgrade/install.py',
        ['--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore-after-labs.json'],True)
print('TLS_LAB_PHYSICAL_COMPLETE',flush=True)
