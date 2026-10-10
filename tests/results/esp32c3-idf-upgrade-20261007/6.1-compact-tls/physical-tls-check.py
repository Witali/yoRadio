import json, subprocess, sys
from pathlib import Path
root=Path('.build/idf-upgrade')
assert json.loads((root/'physical-6.1-compact-pool-https-check/report.json').read_text())['cases'][-1]['name']=='restore'
label='6.1-compact-tls'
image=Path('firmware/development/esp32c3-idf-'+label+'-profile/app.bin')
results=[]
def run(name,script,args,required=False):
    cmd=[sys.executable,'-X','utf8',script,*map(str,args)]
    print('START',name,flush=True)
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=2400).returncode
    results.append(dict(name=name,code=code,command=cmd))
    (root/('physical-'+label+'-check.json')).write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise SystemExit(code)
run('install-'+label+'-profile','.build/idf-upgrade/install.py',
    ['--firmware',image,'--output',root/('install-'+label+'-profile.json')],True)
for transport in ('https','http'):
    name='physical-'+label+'-public-'+transport
    run(name,'tools/esp32c3_tests/public_streams.py',
        ['--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,
         '--transport',transport,'--seconds','60','--aac-reference-command',root/'faad-reference-command.json',
         '--output',root/name])
print('TLS_CHECK_COMPLETE',flush=True)
