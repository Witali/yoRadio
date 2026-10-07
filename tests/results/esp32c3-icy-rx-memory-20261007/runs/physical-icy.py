"""Run only after physical-pair.py releases the board; always restore defaults."""
import json, subprocess, sys, time
from pathlib import Path
root=Path('.build/c3-memory-20261007')
results=[]
base=Path('firmware/development')
debug=base/'esp32c3-idf-6.1-compact-icy-debug/app.bin'
profile=base/'esp32c3-idf-6.1-memory-icy-rxcopy-profile/app.bin'
quiet=base/'esp32c3-idf-6.1-compact-icy-quiet/app.bin'

def run(name, script, args, required=False):
    print('START',name,flush=True)
    command=[sys.executable,'-X','utf8',script,*map(str,args)]
    started=time.monotonic()
    with (root/(name+'.log')).open('xb') as log:
        code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500).returncode
    results.append(dict(name=name,code=code,seconds=time.monotonic()-started,command=command))
    (root/'physical-icy.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,code,flush=True)
    if required and code:raise RuntimeError('Required phase failed: '+name)

def install(name,image):
    run(name,'.build/idf-upgrade/install.py',['--firmware',image,'--output',root/(name+'.json')],True)

try:
    install('install-icy-debug',debug)
    run('icy-debug','tools/esp32c3_tests/icy_metadata.py',
        ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
         '--firmware',debug,'--output',root/'icy-debug'])
    install('install-icy-rxcopy-profile',profile)
    for transport in ('http','https'):
        run('icy-rxcopy-'+transport,'tools/esp32c3_tests/public_streams.py',
            ['--board','http://192.168.100.4','--serial-port','COM9','--firmware',profile,
             '--case','groovesalad-64-aac','--transport',transport,'--seconds','60',
             '--aac-reference-command','.build/idf-upgrade/faad-reference-command.json',
             '--output',root/('icy-rxcopy-'+transport)])
    run('icy-rxcopy-soak','tools/esp32c3_tests/stream_memory_study.py',
        ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
         '--firmware',profile,'--case','hev2-44100-stereo','--seconds','600','--output',root/'icy-rxcopy-soak'])
    run('icy-rxcopy-soak-summary','tools/esp32c3_tests/summarize_sustained.py',
        ['--input',root/'icy-rxcopy-soak','--output',root/'icy-rxcopy-soak-summary.json'])
finally:
    install('install-icy-quiet',quiet)
run('icy-quiet','tools/esp32c3_tests/icy_metadata.py',
    ['--board','http://192.168.100.4','--host','192.168.100.253','--serial-port','COM9',
     '--firmware',quiet,'--output',root/'icy-quiet'])
run('icy-quiet-ota','tools/esp32c3_tests/ota.py',
    ['--board','http://192.168.100.4','--firmware',quiet,'--suite','negative',
     '--suite','roundtrip','--suite','slow','--output',root/'icy-quiet-ota.json'])
print('ICY_PHYSICAL_COMPLETE',flush=True)
