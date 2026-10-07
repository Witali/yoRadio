import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board
root=Path.cwd();base=root/'.build/aac-asymmetric-production'
fw='firmware/development/esp32c3-aac-asymmetric-owner'
expected=json.loads((root/fw/'manifest.json').read_text())['image']['app_elf_sha256']
common=['--board','http://192.168.100.4','--serial-port','COM9']
py=[sys.executable,'-X','utf8']
commands={
 'candidate-load-relocated': ['tools/esp32c3_tests/diagnostic.py','run',*common,'--host','192.168.100.253','--suite','load','--case','lc-48000-stereo','--case','he-48000-stereo','--case','hev2-44100-stereo','--sdkconfig',fw+'/sdkconfig'],
 'http':['tools/esp32c3_tests/public_streams.py',*common,'--firmware',fw+'/app.bin','--seconds','60','--interval','0.1','--transport','http','--ffprobe','C:/Users/rudol/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffprobe.exe'],
 'local':['tools/esp32c3_tests/diagnostic.py','run',*common,'--host','192.168.100.253','--suite','http','--sdkconfig',fw+'/sdkconfig'],
 'ota-repeat':['tools/esp32c3_tests/ota_diagnostic.py',*common,'--host','192.168.100.253','--firmware',fw+'/app.bin','--suite','roundtrip','--suite','while-playing'],
}
for name in ('mp3-320','flac-level8','vorbis-q10','opus-510','aac-lc-320','lc-22050-mono','he-44100-stereo','he-48000-stereo','hev2-44100-stereo'):
    commands['local']+=['--case',name]
results=[]
for name in sys.argv[1:]:
    assert Board('http://192.168.100.4').info()['app_elf_sha256']==expected,'Wrong firmware before suite'
    print('BEGIN',name,flush=True)
    code=subprocess.run(py+commands[name]+['--output',str(base/name)]).returncode
    results.append(dict(suite=name,exit_code=code))
    (base/'remaining-suite-exits.json').write_text(json.dumps(results,indent=2)+'\n')
    print('END',name,'exit',code,flush=True)
