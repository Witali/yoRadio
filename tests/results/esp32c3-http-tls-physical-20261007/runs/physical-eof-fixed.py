import json,subprocess,sys,time
from pathlib import Path
root=Path('.build/c3-rfc-qualification-20261007/eof-fixed')
root.mkdir(exist_ok=False)
old=Path('firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-http-guard/app.bin')
image=Path('firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx6-eof-fixed/app.bin')
trust=Path('.build/c3-tls-records-20261007/trust')
assert json.loads(Path('.build/c3-rfc-qualification-20261007/verify-http-eof-fixed.json').read_text())['result']=='PASS'
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

def framing(name,firmware,modes):
    run(name,'tools/esp32c3_tests/tls_framing.py',[
        '--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
        '--firmware',firmware,'--ca',trust/'ca.pem','--cert',trust/'server.pem','--key',trust/'server.key',
        '--output',root/name,*modes])

try:
    run('install','.build/idf-upgrade/install.py',['--firmware',image,'--output',root/'install.json'],True)
    framing('framing',image,[])
    run('public','tools/esp32c3_tests/public_streams.py',[
        '--board','http://192.168.100.4','--serial-port','COM9','--firmware',image,
        '--case','groovesalad-64-aac','--case','groovesalad-256-mp3','--seconds','60','--aac-reference-command','.build/idf-upgrade/faad-reference-command.json','--output',root/'public'])
finally:
    run('restore','.build/idf-upgrade/install.py',[
        '--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore.json'],True)
    final=Path('.build/c3-rfc-qualification-20261007/final-board.py').read_text().replace(
        "Path('.build/c3-rfc-qualification-20261007/final-board.json')", "Path('.build/c3-rfc-qualification-20261007/eof-fixed/final-board.json')")
    (root/'final-board.py').write_text(final)
    run('final-board',str(root/'final-board.py'),[],True)
print('EOF_QUALIFICATION_COMPLETE',flush=True)
