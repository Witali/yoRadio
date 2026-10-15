import hashlib,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
from production_health import read_health
root=Path('tests/results/esp32c3-raw-tail-quiet-20261015')
artifact=Path('firmware/development/esp32c3-idf61-raw-tail-quiet');m=json.loads((artifact/'manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in m['files'].items():require(sha(artifact/name)==digest,'Artifact differs: '+name)
expected={'qualification/public-files':16,'qualification/http':28,'qualification/transitions':11,
    'qualification/network':11,'qualification/websocket':7,'qualification/ota':15,
    'public-radio/aac-heavy':7,'public-radio/other-public':10,'sustained/flac':9,
    'sustained/vorbis':9,'sustained/opus':9,'public-lc-repeat/aac-lc':7,'final-deployment/smoke':6}
reports=[]
for name,count in expected.items():
    p=root/name/'report.json';r=json.loads(p.read_text())
    require(len(r['cases'])==count and all(c['result']=='PASS' for c in r['cases']),'Report failed or incomplete: '+name)
    require(r['board']['app_elf_sha256']==m['image']['app_elf_sha256'],'Report image differs: '+name)
    reports.append(dict(report=p.as_posix(),checks=count,sha256=sha(p)))
for mode in ('fresh','cached'):
    comparison=json.loads((root/'profile-wrapper'/f'{mode}-comparison.json').read_text())
    require(not comparison['differences'] and comparison['reference_keys']==1603,'Profile mismatch')
    require(comparison['reference_sha256']==sha(artifact/'sdkconfig'),'Different reference config')
for name in ('idf/esp32c3-oled-native/sdkconfig.radio-tested.defaults','idf/esp32c3-oled-native/main/Kconfig.projbuild'):
    require(sha(Path(name))==sha(root/'profile-wrapper/sources'/name),'Configuration source changed')
for name in ('ESP32C3_PRODUCTION_ACCEPTANCE_20261015.md','ESP32C3_BEGINNERS_GUIDE.md'):
    p=Path('docs')/name
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target.startswith(('http:','https:','#')):continue
        require((p.parent/target.split('#')[0]).exists(),'Broken documentation link: '+target)
final=json.loads((root/'final-deployment/controller.json').read_text())
b=Board('http://192.168.100.4');identity=b.info();status=b.status();health=read_health(b)
require(identity['app_elf_sha256']==m['image']['app_elf_sha256'],'Wrong current board image')
require(not status['audio'],'Playback state changed')
require(all(final['final']['settings'].values()),'Settings verification failed')
require(health['boot_id']==json.loads((root/'final-deployment/audit.json').read_text())['health']['boot_id'],'Unexpected reboot')
require(health['allocation_failures']==0 and health['task_watchdog_events']==0,'Runtime fault after deployment')
record=dict(result='PASS',checks=sum(x['checks'] for x in reports),reports=reports,image=m['image'],
    board=dict(identity=identity,stopped=True,health=health),
    retained_limits=['Bounded corpus numerical evidence, not a universal PCM bound',
        'Counter-based output observation, not analog loopback',
        'Injected long network pauses can exhaust buffered audio; failed experiments retained'])
out=Path('.build/c3-raw-tail-quiet-20261015/completion-audit.json')
require(not out.exists(),'Preserve earlier audit');out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(result=record['result'],checks=record['checks'],identity=identity,stopped=True)))
