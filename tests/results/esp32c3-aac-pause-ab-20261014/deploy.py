"""Preplanned A/B/A HTTP pause comparison; restore the original image/settings."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require,exception_details,sha
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
base=Path('.build/c3-aac-pause-ab-20261014');record_path=base/'controller-02.json'
require(not record_path.exists(),'Preserve previous campaign')
paths=dict(baseline=Path('firmware/development/esp32c3-idf61-production-20261013/app.bin'),
           candidate=Path('firmware/development/esp32c3-idf61-continuous-confirm/app.bin'))
images={k:p.read_bytes() for k,p in paths.items()};info={k:image_info(v) for k,v in images.items()}
b=Board('http://192.168.100.4');initial=b.info()
require(initial['app_elf_sha256']==info['baseline']['app_elf_sha256'],'Wrong initial image')
require(not b.status()['audio'],'Board must initially be stopped')
before=snapshot(b)
record=dict(initial=initial,images=info,sequence=['baseline-before','candidate','baseline-after'],runs=[],
            controller_sha256=sha(Path(__file__).read_bytes()),
            scope='Matched finite HTTP pause experiment; not TLS or proof of the public-station failure cause')
def save():record_path.write_text(json.dumps(record,indent=2)+'\n')
def install(which):
    active=b.info()
    require(active['app_elf_sha256'] in [v['app_elf_sha256'] for v in info.values()],'Unexpected external deployment')
    if active['app_elf_sha256']!=info[which]['app_elf_sha256']:
        require(len(images[which])<=active['max_size'],'Image too large')
        status,body=upload(b.origin,multipart(images[which]))
        require(status==200 and body==b'OK','OTA failed')
        active=wait_image(b,info[which]['app_elf_sha256'],'app1' if active['partition']=='app0' else 'app0',timeout=60)
    b.stop()
    return dict(identity=active,settings=verify_snapshot(b,before))
save();result=1
try:
    for name in record['sequence']:
        which='candidate' if name=='candidate' else 'baseline'
        print('Testing '+name,flush=True)
        row=dict(name=name,installation=install(which));record['runs'].append(row);save()
        row['exit_code']=subprocess.call([sys.executable,'-B','-X','utf8',str(base/'run.py'),name,str(paths[which])]);save()
        # Output drops are the measured outcome, not a reason to suppress the A/B control.
        r=json.loads((base/name/'report.json').read_text())
        unsafe=[c for c in r['cases'] if c['result']!='PASS' and c['name']!='output']
        require(not unsafe,'Non-output campaign failure: stop before next comparison')
    result=0 if all(r['exit_code']==0 for r in record['runs']) else 1
except Exception as error:
    record['failure']=exception_details(error);save();print('Controller failed: '+type(error).__name__,flush=True)
finally:
    try:
        record['restored']=install('baseline');require(not b.status()['audio'],'Final playback not stopped')
        record['restored']['stopped']=True;print('Original image/settings restored',flush=True)
    except Exception as error:
        record['restoration_failure']=exception_details(error);result=1
    save()
sys.exit(result)
