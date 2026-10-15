"""Bounded decoder diagnostic; restore original application/settings in finally."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
base=Path('.build/c3-decode-probe-20261015');out=base/'physical'
require(not out.exists(),'Preserve prior evidence');out.mkdir()
candidate=Path('firmware/development/esp32c3-idf61-decode-probe-diagnostic/app.bin').read_bytes()
original=Path('firmware/development/esp32c3-idf61-production-20261013/app.bin').read_bytes()
expected=image_info(candidate);baseline=image_info(original)
audit=json.loads((base/'build-audit.json').read_text())
require(audit['result']=='PASS' and audit['image']==expected,'Build audit mismatch')
b=Board('http://192.168.100.4');initial=b.info()
require(initial['app_elf_sha256']==baseline['app_elf_sha256'],'Unexpected original image')
require(not b.status()['audio'],'Expected idle board')
before=snapshot(b)
record=dict(initial=initial,candidate=expected,original=baseline,tests=[],controller_sha256=sha(Path(__file__).read_bytes()))
def save(): (out/'controller.json').write_text(json.dumps(record,indent=2)+'\n')
def install(image,info):
    active=b.info();target='app1' if active['partition']=='app0' else 'app0'
    require(len(image)<=active['max_size'],'OTA slot too small')
    status,body=upload(b.origin,multipart(image))
    require(status==200 and body==b'OK','OTA upload failed')
    identity=wait_image(b,info['app_elf_sha256'],target,timeout=60);b.stop()
    return dict(identity=identity,settings=verify_snapshot(b,before))
save();result=1
try:
    print('Installing decoder diagnostic',flush=True)
    record['installed']=install(candidate,expected);save();result=0
    for trial in ('control1','control2','pauses','control3'):
        mode='pauses' if trial=='pauses' else 'control'
        print('Running '+trial,flush=True)
        with (out/(trial+'.log')).open('wb') as log:
            rc=subprocess.call([sys.executable,'-B','-X','utf8',str(base/'run.py'),mode,trial],stdout=log,stderr=subprocess.STDOUT)
        record['tests'].append(dict(trial=trial,exit_code=rc));save()
        report=json.loads((out/trial/'report.json').read_text())
        for name in ('final-idle','recovery','settings','health','decoder','capacity','delivery'):
            require(any(c['name']==name and c['result']=='PASS' for c in report['cases']),
                    'Invalid or unsafe experiment: '+name)
        print(trial+' completed; exit='+str(rc),flush=True)
        if rc:result=1
except Exception as error:
    record['failure']=exception_details(error);result=1;save()
    print('Candidate controller failed: '+type(error).__name__,flush=True)
finally:
    print('Restoring original production image',flush=True)
    try:
        b.stop();current=b.info()['app_elf_sha256']
        require(current in (baseline['app_elf_sha256'],expected['app_elf_sha256']),
                'Unexpected image: stop before overwriting another deployment')
        record['restored']=(install(original,baseline) if current!=baseline['app_elf_sha256']
                            else dict(identity=b.info(),settings=verify_snapshot(b,before)))
        require(not b.status()['audio'],'Final playback is not stopped')
        record['restored']['stopped']=True
        print('Original image and settings restored',flush=True)
    except Exception as error:
        record['restoration_failure']=exception_details(error);result=1
        print('Restoration requires attention: '+type(error).__name__,flush=True)
    save()
sys.exit(result)
