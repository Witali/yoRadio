import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
from ota import image_info,snapshot,verify_snapshot

root=Path('.build/c3-flac-rice-20261008/physical')
require(not root.exists(),'Keep previous physical results')
require(Path('.build/c3-flac-rice-20261008/config-difference.json').exists(),'Matched build audit missing')
root.mkdir(parents=True)
board=Board('http://192.168.100.4')
quiet=Path('firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin')
quiet_elf=image_info(quiet.read_bytes())['app_elf_sha256']
initial=board.status();settings=snapshot(board)
require(board.info()['app_elf_sha256']==quiet_elf,'Expected the restored quiet image')
trust=Path('.build/c3-tls-records-20261007/trust')
radio=Path('C:/Work/yoRadio/.worktree/aac-storage18/.build/radio-flac-20261006/recordings/manifest.json')
phases=[]

def run(name,script,args,required=False):
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    label=name.replace('/','-')
    print('START',name,flush=True);start=time.monotonic()
    with (root/(label+'.log')).open('xb') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=900)
    phases.append(dict(name=name,command=command,code=result.returncode,seconds=time.monotonic()-start))
    (root/'phases.json').write_text(json.dumps(phases,indent=2)+'\n')
    print('END',name,result.returncode,flush=True)
    require(not required or result.returncode==0,'Required phase failed: '+name)

def flac(mode,case,manifest,protocol,image):
    label=mode+'/'+case+'-'+protocol
    args=['--runner','diagnostic','--','run','--board',board.origin,
        '--host','192.168.100.253','--serial-port','COM9','--suite','load',
        '--load-seconds','60','--load-idle-recovery','--case',case,
        '--fixture-manifest',manifest,'--sustained-protocol',protocol,
        '--unpaced-files','--delivery-stats','--leave-stopped',
        '--sdkconfig',image.with_name('sdkconfig'),'--output',root/label]
    if protocol=='https':
        args+=['--https-origin','https://192.168.100.253:8771',
               '--tls-cert',trust/'server.pem','--tls-key',trust/'server.key']
    run(label,'tools/esp32c3_tests/trace_transport.py',args)

try:
    for mode in ('control','bytewise'):
        image=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-'+mode+'/app.bin')
        run(mode+'/install','.build/idf-upgrade/install.py',
            ['--firmware',image,'--output',root/(mode+'-install.json')],True)
        require(board.info()['app_elf_sha256']==image_info(image.read_bytes())['app_elf_sha256'],'Wrong test image')
        # Reverse the two radio cases across variants to reduce ordering bias.
        radio_cases=['radio-bossa-lpc32','radio-groovesalad-lpc12']
        if mode=='bytewise':radio_cases.reverse()
        for case in radio_cases:flac(mode,case,radio,'http',image)
        flac(mode,'stress-flac-48000-2ch-16bit-610s',
            '.build/c3-reserve-soak-20261008/fixtures/manifest.json','https',image)
        run(mode+'/aac-alternate-90','tools/esp32c3_tests/trace_transport.py',[
            '--runner','tls_records','--','--board',board.origin,'--host','192.168.100.253',
            '--serial-port','COM9','--firmware',image,'--ca',trust/'ca.pem',
            '--cert',trust/'server.pem','--key',trust/'server.key','--mode','alternate',
            '--seconds','90','--output',root/mode/'aac-alternate-90'])
finally:
    run('restore','.build/idf-upgrade/install.py',['--firmware',quiet,'--output',root/'restore.json'],True)
    identity=board.info();require(identity['app_elf_sha256']==quiet_elf,'Wrong restored image')
    if not initial['audio']:board.stop()
    statuses=[]
    for _ in range(3):
        time.sleep(5);statuses.append(board.status())
    state_matches=all(s['audio']==initial['audio'] for s in statuses)
    final=dict(result='PASS' if state_matches else 'FAIL',info=identity,status=statuses,
               persistence=verify_snapshot(board,settings),playback_state_restored=state_matches)
    (root/'final-board.json').write_text(json.dumps(final,indent=2)+'\n')
    require(state_matches,'Initial playback state was not restored')
print('RICE_PHYSICAL_COMPLETE',flush=True)
