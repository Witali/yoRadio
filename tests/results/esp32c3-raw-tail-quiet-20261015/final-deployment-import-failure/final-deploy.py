"""Install the exact qualified application; roll back on failed smoke checks."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
base=Path('.build/c3-raw-tail-quiet-20261015');out=base/'final-deployment'
require(not out.exists(),'Preserve previous deployment evidence')
candidate=Path('firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin').read_bytes()
original=Path('firmware/development/esp32c3-idf61-production-20261013/app.bin').read_bytes()
expected,baseline=image_info(candidate),image_info(original)
promotion=json.loads((base/'profile-promotion.json').read_text())
require(promotion['image']==expected,'Promoted image differs')
for name,digests in promotion['files'].items():
    require(sha(Path(name).read_bytes())==digests['candidate_sha256'],'Promoted source changed')
for item in promotion['evidence']:
    path=Path(item['report']);require(sha(path.read_bytes())==item['sha256'],'Evidence changed')
    require(all(c['result']=='PASS' for c in json.loads(path.read_text())['cases']),'A physical gate failed')
wrapper=json.loads((base/'profile-wrapper/summary.json').read_text())
require([r['mode'] for r in wrapper]==['fresh','cached'] and all(r['result']=='PASS' for r in wrapper),
    'Fresh/cached production profile is not verified')
for row in wrapper:
    compared=json.loads(Path(row['comparison']).read_text())
    require(not compared['differences'],'Configuration differs')
    require(sha(Path(compared['actual']).read_bytes())==compared['actual_sha256'],'Verified configuration changed')
b=Board('http://192.168.100.4');initial=b.info()
require(initial['app_elf_sha256']==baseline['app_elf_sha256'],'Unexpected existing image')
require(not b.status()['audio'],'Do not interrupt unrelated playback')
before=snapshot(b);out.mkdir()
record=dict(initial=initial,candidate=expected,original=baseline,tests=[],controller_sha256=sha(Path(__file__).read_bytes()),
    smoke_sha256=sha((base/'final-smoke.py').read_bytes()))
def save():(out/'controller.json').write_text(json.dumps(record,indent=2)+'\n')
def install(image,info):
    active=b.info();target='app1' if active['partition']=='app0' else 'app0'
    require(len(image)<=active['max_size'],'Application does not fit OTA partition')
    status,body=upload(b.origin,multipart(image))
    require(status==200 and body==b'OK','OTA rejected application')
    identity=wait_image(b,info['app_elf_sha256'],target,timeout=60)
    b.stop();return dict(identity=identity,settings=verify_snapshot(b,before))
save();result=1
try:
    print('Installing exact tested production candidate',flush=True)
    record['installed']=install(candidate,expected);save()
    rc=subprocess.call([sys.executable,'-B','-X','utf8',str(base/'final-smoke.py')])
    record['tests'].append(dict(suite='he-aac-and-ps-smoke',exit_code=rc));save()
    require(rc==0,'Post-install smoke failed')
    require(not b.status()['audio'],'Expected stopped playback')
    record['final']=dict(identity=b.info(),settings=verify_snapshot(b,before),stopped=True)
    require(record['final']['identity']['app_elf_sha256']==expected['app_elf_sha256'],'Wrong final image')
    result=0;save();print('Tested application installed; settings unchanged; stopped',flush=True)
except Exception as error:
    record['failure']=exception_details(error);save()
    print('Final deployment failed; restoring original image',flush=True)
finally:
    if result:
        try:
            b.stop();current=b.info()['app_elf_sha256']
            require(current in (baseline['app_elf_sha256'],expected['app_elf_sha256']),
                'Unexpected third-party deployment; do not overwrite it')
            record['restored']=install(original,baseline) if current!=baseline['app_elf_sha256'] else dict(identity=b.info(),settings=verify_snapshot(b,before))
            require(not b.status()['audio'],'Rollback playback not stopped')
            record['restored']['stopped']=True
        except Exception as error:record['restoration_failure']=exception_details(error)
    save()
raise SystemExit(result)
