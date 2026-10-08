import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import snapshot, verify_snapshot
root=Path('.build/c3-retained-tls-20261008/physical')
root.mkdir(exist_ok=False)
image=Path('firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx6-retain/app.bin')
trust=Path('.build/c3-tls-records-20261007/trust')
board=Board('http://192.168.100.4')
before=snapshot(board)
initial=board.status()
(root/'before.json').write_text(json.dumps(dict(info=board.info(),status=initial),indent=2)+'\n')
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
    if required and code: raise RuntimeError('Required phase failed: '+name)
try:
    run('install','.build/idf-upgrade/install.py',['--firmware',image,'--output',root/'install.json'],True)
    shared=['--board',board.origin,'--host','192.168.100.253','--serial-port','COM9','--firmware',image,'--ca',trust/'ca.pem','--cert',trust/'server.pem','--key',trust/'server.key']
    run('framing','tools/esp32c3_tests/tls_framing.py',shared+['--output',root/'framing'])
    run('tls-soak','tools/esp32c3_tests/tls_records.py',shared+['--mode','alternate','--seconds','600','--output',root/'tls-soak'])
    run('formats','tools/esp32c3_tests/run.py',[
        '--board',board.origin,'--host','192.168.100.253','--serial-port','COM9',
        '--suite','http','--suite','https','--unpaced-files','--delivery-stats','--leave-stopped',
        '--https-origin','https://192.168.100.253:8771','--tls-cert',trust/'server.pem','--tls-key',trust/'server.key',
        '--sdkconfig',image.with_name('sdkconfig'),'--output',root/'formats'])
    run('public','tools/esp32c3_tests/public_streams.py',[
        '--board',board.origin,'--serial-port','COM9','--firmware',image,'--seconds','60',
        '--aac-reference-command','.build/idf-upgrade/faad-reference-command.json','--output',root/'public'])
finally:
    run('restore','.build/idf-upgrade/install.py',[
        '--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore.json'],True)
    identity=board.info()
    require(identity['app_elf_sha256']=='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0','Wrong restored image')
    if not initial['audio']: board.stop()
    samples=[]
    for i in range(3):
        time.sleep(5)
        samples.append(board.status())
    state_matches=all(s['audio']==initial['audio'] for s in samples)
    final=dict(result='PASS' if state_matches else 'FAIL',info=identity,status=samples,
        persistence=verify_snapshot(board,before),playback_state_restored=state_matches,
        note='Ordinary image restored; its saved-station autostart is retained when playback was initially active.')
    (root/'final-board.json').write_text(json.dumps(final,indent=2)+'\n')
    require(state_matches,'Initial playback state not restored')
print('RETained_RX_QUALIFICATION_COMPLETE',flush=True)
