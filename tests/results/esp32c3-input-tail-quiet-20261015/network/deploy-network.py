"""Bounded candidate experiment, app-only OTA, private settings remain in memory."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
base=Path('.build/c3-input-tail-quiet-20261015');out=base/'network'
require(not out.exists(),'Preserve prior evidence');out.mkdir()
candidate=Path('firmware/development/esp32c3-idf61-input-tail-quiet/app.bin').read_bytes()
original=Path('firmware/development/esp32c3-idf61-production-20261013/app.bin').read_bytes()
expected=image_info(candidate);baseline=image_info(original)
require(json.loads((base/'build-audit.json').read_text())['result']=='PASS','Missing build audit')
require(json.loads((base/'build-audit.json').read_text())['image']==expected,'Build image mismatch')
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
    identity=wait_image(b,info['app_elf_sha256'],target,timeout=60)
    b.stop()
    return dict(identity=identity,settings=verify_snapshot(b,before))
save();result=1
try:
    print('Installing continuous-confirmation candidate',flush=True)
    record['installed']=install(candidate,expected);save()
    for suite in ('transitions','network','websocket'):
        print('Running candidate '+suite,flush=True)
        rc=subprocess.call([sys.executable,'-B','-X','utf8',str(base/'run-network.py'),suite])
        record['tests'].append(dict(suite=suite,exit_code=rc));save()
        if rc: break
    else: result=0
except Exception as error:
    record['failure']=exception_details(error);save()
    print('Candidate controller failed: '+type(error).__name__,flush=True)
finally:
    print('Restoring original production image',flush=True)
    try:
        b.stop()
        current_hash=b.info()['app_elf_sha256']
        require(current_hash in (baseline['app_elf_sha256'], expected['app_elf_sha256']),
                'Unexpected image: stop before overwriting another deployment')
        if current_hash!=baseline['app_elf_sha256']:
            record['restored']=install(original,baseline)
        else:
            record['restored']=dict(identity=b.info(),settings=verify_snapshot(b,before))
        require(not b.status()['audio'],'Final playback is not stopped')
        record['restored']['stopped']=True
        print('Original image and settings restored',flush=True)
    except Exception as error:
        record['restoration_failure']=exception_details(error);result=1
        print('Restoration requires attention: '+type(error).__name__,flush=True)
    save()
sys.exit(result)
