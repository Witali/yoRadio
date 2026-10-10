"""Sequential physical qualification after the initial matrix; one board owner."""
import argparse, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board
from ota import image_info

p=argparse.ArgumentParser()
p.add_argument('--version',required=True)
a=p.parse_args()
root=Path('.build/idf-upgrade')
profile=Path(f'firmware/development/esp32c3-idf-{a.version}-profile/app.bin')
production=Path(f'firmware/development/esp32c3-idf-{a.version}-production/app.bin')
origin='http://192.168.100.4'; host='192.168.100.253'
board=Board(origin)
expected=image_info(profile.read_bytes())['app_elf_sha256']
results=[]

def run(name,script,params,timeout=1800):
    assert board.info()['app_elf_sha256']==expected,'Unexpected installed firmware; stop qualification'
    cmd=[sys.executable,'-X','utf8',script,*map(str,params)]
    print('START',name,flush=True)
    started=time.monotonic()
    with (root/f'physical-{a.version}-{name}.log').open('xb') as log:
        try: code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=timeout).returncode
        except subprocess.TimeoutExpired: code='TIMEOUT'
    results.append(dict(name=name,exit_code=code,seconds=round(time.monotonic()-started,2),command=cmd))
    (root/f'physical-{a.version}-stage.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    return code

def common(name):
    return ['--board',origin,'--host',host,'--serial-port','COM9',
            '--sdkconfig',profile.with_name('sdkconfig'),'--output',root/f'physical-{a.version}-{name}']

load=common('load')+['--suite','load','--load-seconds','60','--load-idle-recovery',
 '--fixture-manifest',root/'stress-fixtures/manifest.json']
for name in ('stress-mp3-48000-2ch-16bit-65s','stress-flac-48000-2ch-16bit-65s',
 'stress-vorbis-48000-2ch-16bit-65s','stress-opus-48000-2ch-16bit-65s',
 'lc-48000-stereo','he-48000-stereo','hev2-44100-stereo'):
    load+=['--case',name]
run('load','tools/esp32c3_tests/run.py',load)
run('load-summary','tools/esp32c3_tests/load_windows.py',
 ['--input',root/f'physical-{a.version}-load','--output',root/f'physical-{a.version}-load-summary.json'])
run('flac-truncation','tools/esp32c3_tests/flac_truncation.py',
 ['--board',origin,'--host',host,'--serial-port','COM9','--output',root/f'physical-{a.version}-flac-truncation'])
run('switch','tools/esp32c3_tests/run.py',common('switch')+['--suite','switch','--cycles','3'])
run('retry','tools/esp32c3_tests/connection_retry.py',
 ['--board',origin,'--host',host,'--serial-port','COM9','--firmware',profile,'--output',root/f'physical-{a.version}-retry'])
for transport in ('http','https'):
    name='public-'+transport
    run(name,'tools/esp32c3_tests/public_streams.py',
     ['--board',origin,'--serial-port','COM9','--firmware',profile,'--transport',transport,
      '--seconds','60','--output',root/f'physical-{a.version}-{name}'])
run('soak','tools/esp32c3_tests/run.py',common('soak')+['--suite','soak','--soak-seconds','600','--case','lc-48000-stereo'])
run('soak-summary','tools/esp32c3_tests/summarize_sustained.py',
 ['--input',root/f'physical-{a.version}-soak','--output',root/f'physical-{a.version}-soak-summary.json'])
if a.version.endswith('-compact'):
    run('hev2-soak','tools/esp32c3_tests/run.py',common('hev2-soak')+
        ['--suite','soak','--soak-seconds','600','--case','hev2-44100-stereo'])
    run('hev2-soak-summary','tools/esp32c3_tests/summarize_sustained.py',
        ['--input',root/f'physical-{a.version}-hev2-soak','--output',root/f'physical-{a.version}-hev2-soak-summary.json'])
code=run('production-transition','tools/esp32c3_tests/ota_transition.py',
 ['--board',origin,'--host',host,'--serial-port','COM9','--current-firmware',profile,
  '--firmware',production,'--output',root/f'physical-{a.version}-production-transition'])
if code: raise SystemExit('Production transition failed; inspect before recovery')
expected=image_info(production.read_bytes())['app_elf_sha256']
run('ota','tools/esp32c3_tests/ota.py',['--board',origin,'--firmware',production,
 '--suite','negative','--suite','roundtrip','--suite','slow','--output',root/f'physical-{a.version}-ota.json'])
run('http-headers','tools/esp32c3_tests/http_headers.py',
 ['--board',origin,'--firmware',production,'--output',root/f'physical-{a.version}-http-headers.json'])
run('production','tools/esp32c3_tests/run.py',['--board',origin,'--host',host,
 '--suite','http','--suite','transitions','--suite','websocket','--suite','boot-time','--cycles','2',
 '--sdkconfig',production.with_name('sdkconfig'),'--output',root/f'physical-{a.version}-production'])
run('quiet-https','.build/idf-upgrade/quiet-public.py',
 ['--firmware',production,'--output',root/f'physical-{a.version}-quiet-https'])
print('STAGE_COMPLETE',a.version,flush=True)
