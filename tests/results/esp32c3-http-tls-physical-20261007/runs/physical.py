import json,subprocess,sys,time
from pathlib import Path
root=Path('.build/c3-rfc-qualification-20261007')
image=Path('firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-http-guard/app.bin')
trust=Path('.build/c3-tls-records-20261007/trust')
results=[]
def run(name,script,args,required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1800).returncode
    results.append(dict(name=name,code=code,seconds=time.monotonic()-started,command=command))
    (root/'physical.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise RuntimeError('Required phase failed: '+name)
try:
    run('install','.build/idf-upgrade/install.py',['--firmware',image,'--output',root/'install.json'],True)
    run('public','tools/esp32c3_tests/public_streams.py',[
        '--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,
        '--seconds','60','--aac-reference-command','.build/idf-upgrade/faad-reference-command.json','--output',root/'public'])
    run('formats','tools/esp32c3_tests/run.py',[
        '--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
        '--suite','http','--suite','https','--unpaced-files','--delivery-stats','--leave-stopped',
        '--https-origin','https://192.168.100.253:8771','--tls-cert',trust/'server.pem','--tls-key',trust/'server.key',
        '--sdkconfig',image.with_name('sdkconfig'),'--output',root/'formats'])
    run('tls-soak','tools/esp32c3_tests/tls_records.py',[
        '--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
        '--firmware',image,'--ca',trust/'ca.pem','--cert',trust/'server.pem','--key',trust/'server.key',
        '--mode','alternate','--seconds','600','--output',root/'tls-soak'])
finally:
    run('restore','.build/idf-upgrade/install.py',[
        '--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore.json'],True)
    run('final-board',str(root/'final-board.py'),[],True)
print('QUALIFICATION_COMPLETE',flush=True)
