from pathlib import Path
import json, subprocess, sys, time
root=Path.cwd()
sys.path.insert(0,str(root/'tools/esp32c3_tests'))
from common import Board, require
from ota import image_info,multipart,upload,wait_image,snapshot,verify_snapshot

out=root/'.build/early-owner-public-600-01'
out.mkdir(exist_ok=False)
candidate=root/'firmware/development/esp32c3-idf-6.1-r9a97-early-owner-public/app.bin'
restore=root/'firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/app.bin'
b=Board('http://192.168.100.4')
original=b.info()
require(not b.status()['audio'],'Board must be stopped')
require(original['app_elf_sha256']==image_info(restore.read_bytes())['app_elf_sha256'],'Restore mismatch')
private=snapshot(b)
report=dict(original=original,candidate=image_info(candidate.read_bytes()))
def save():(out/'controller.json').write_text(json.dumps(report,indent=2)+'\n')
def install(path):
    current=b.info();data=path.read_bytes();expected=image_info(data)
    if current['app_elf_sha256']==expected['app_elf_sha256']:return
    code,body=upload(b.origin,multipart(data))
    require(code==200 and body==b'OK','OTA failed')
    wait_image(b,expected['app_elf_sha256'],'app1' if current['partition']=='app0' else 'app0',timeout=60)
    b.stop();time.sleep(2)
save()
try:
    install(candidate);report['installed']=b.info();save()
    print('CANDIDATE INSTALLED',flush=True)
    command=[sys.executable,'-B','-X','utf8','tools/esp32c3_tests/sustained_output.py',
        '--board',b.origin,'--firmware',str(candidate),'--output',str(out/'physical'),
        '--stream','groovesalad-32-aac','--seconds','600',
        '--aac-reference-command','.build/c3-prefill1000-public-20261010/faad-reference-command.json']
    report['command']=command;save()
    result=subprocess.run(command,check=False)
    report['test_exit_code']=result.returncode;save()
finally:
    try:b.stop()
    finally:install(restore)
    b.stop()
    report['restoration']=dict(image=b.info(),status=b.status(),**verify_snapshot(b,private))
    save();print('ORIGINAL RESTORED',flush=True)
require(report.get('test_exit_code')==0,'Sustained test failed; retain evidence')
