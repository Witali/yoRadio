import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import snapshot, verify_snapshot

root = Path('.build/c3-tls-reserve-20261008/physical')
root.mkdir(exist_ok=False)
image = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve/app.bin')
trust = Path('.build/c3-tls-records-20261007/trust')
board = Board('http://192.168.100.4')
before = snapshot(board)
initial = board.status()
results = []
(root/'before.json').write_text(json.dumps(dict(info=board.info(),status=initial),indent=2)+'\n')

def run(name, script, args, required=False):
    print('START', name, flush=True)
    command = [sys.executable, '-X', 'utf8', script, *map(str,args)]
    started = time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=1800).returncode
    results.append(dict(name=name, code=code, seconds=time.monotonic()-started, command=command))
    (root/'phases.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code: raise RuntimeError('Required phase failed: '+name)

try:
    run('install','.build/idf-upgrade/install.py',['--firmware',image,'--output',root/'install.json'],True)
    run('tls-alternate','tools/esp32c3_tests/tls_records.py',[
        '--board',board.origin,'--host','192.168.100.253','--serial-port','COM9',
        '--firmware',image,'--ca',trust/'ca.pem','--cert',trust/'server.pem','--key',trust/'server.key',
        '--mode','alternate','--seconds','75','--output',root/'tls-alternate'])
finally:
    run('restore','.build/idf-upgrade/install.py',[
        '--firmware','firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin','--output',root/'restore.json'],True)
    identity = board.info()
    require(identity['app_elf_sha256']=='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0','Wrong restored image')
    if not initial['audio']: board.stop()
    samples = []
    for _ in range(3):
        time.sleep(5)
        samples.append(board.status())
    state_matches = all(s['audio']==initial['audio'] for s in samples)
    final = dict(result='PASS' if state_matches else 'FAIL',info=identity,status=samples,
        persistence=verify_snapshot(board,before),playback_state_restored=state_matches)
    (root/'final-board.json').write_text(json.dumps(final,indent=2)+'\n')
    require(state_matches,'Initial playback state not restored')
print('TLS_RESERVE_CONTROL_COMPLETE',flush=True)
