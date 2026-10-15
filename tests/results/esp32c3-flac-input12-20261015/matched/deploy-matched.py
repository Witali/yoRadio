"""Matched buffer target, app-only OTA, restore private settings in finally."""
import copy,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from memory import set_audio_buffer
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
base=Path('.build/c3-flac-input12-20261015');out=base/'matched'
require(not out.exists(),'Preserve earlier evidence');out.mkdir()
art=Path('firmware/development')
original=(art/'esp32c3-idf61-production-20261013/app.bin').read_bytes()
images={key:(art/folder/'app.bin').read_bytes() for key,folder in (
    ('slots8','esp32c3-idf61-flac-output-diagnostic'),
    ('slots11','esp32c3-idf61-flac-input12-diagnostic'))}
baseline=image_info(original);identities={k:image_info(v) for k,v in images.items()}
b=Board('http://192.168.100.4');initial=b.info()
require(initial['app_elf_sha256']==baseline['app_elf_sha256'],'Unexpected initial firmware')
require(not b.status()['audio'],'Expected stopped board')
before=snapshot(b);blocks=before['settings']['getsystem']['abuff']
temporary=copy.deepcopy(before);temporary['settings']['getsystem']['abuff']=14
record=dict(initial=initial,original=baseline,images=identities,tests=[],
    original_audio_buffer_blocks=blocks,temporary_audio_buffer_blocks=14,
    controller_sha256=sha(Path(__file__).read_bytes()))
def save(): (out/'controller.json').write_text(json.dumps(record,indent=2)+'\n')
def install(data,identity,settings):
    active=b.info();target='app1' if active['partition']=='app0' else 'app0'
    require(len(data)<=active['max_size'],'OTA slot too small')
    code,body=upload(b.origin,multipart(data))
    require(code==200 and body==b'OK','OTA upload failed')
    info=wait_image(b,identity['app_elf_sha256'],target,timeout=60);b.stop()
    return dict(identity=info,settings=verify_snapshot(b,settings))
save();result=0
try:
    set_audio_buffer(b,14)
    record['temporary_settings']=verify_snapshot(b,temporary);save()
    for key in ('slots8','slots11'):
        print('Installing '+key+' with equal 14-block saved target',flush=True)
        record['installed_'+key]=install(images[key],identities[key],temporary);save()
        for suite in ('control','pauses'):
            print('Running '+key+' '+suite,flush=True)
            rc=subprocess.call([sys.executable,'-B','-X','utf8',str(base/'run-matched.py'),suite,key])
            record['tests'].append(dict(variant=key,suite=suite,exit_code=rc));save()
            # Expected output failures under imposed pauses remain failures, but
            # permit the paired measurement only after safe recovery is proven.
            report=json.loads((out/key/suite/'report.json').read_text())
            for name in ('final-idle','recovery','settings','health','decoder','capacity','delivery'):
                require(any(c['name']==name and c['result']=='PASS' for c in report['cases']),
                        'Unsafe or invalid experiment: '+name)
            if rc:result=1
except Exception as error:
    record['failure']=exception_details(error);result=1;save()
    print('Experiment failed: '+type(error).__name__,flush=True)
finally:
    print('Restoring original settings and firmware',flush=True)
    try:
        b.stop();current=b.info()
        require(current['app_elf_sha256'] in [baseline['app_elf_sha256']]+[i['app_elf_sha256'] for i in identities.values()],
                'Unexpected third-party firmware; stop restoration')
        set_audio_buffer(b,blocks)
        # Always reboot through app-only OTA, recreating the original queue.
        record['restored']=install(original,baseline,before)
        require(not b.status()['audio'],'Final playback not stopped')
        record['restored']['stopped']=True
        print('Original image and settings restored',flush=True)
    except Exception as error:
        record['restoration_failure']=exception_details(error);result=1
        print('Restoration requires attention: '+type(error).__name__,flush=True)
    save()
sys.exit(result)
