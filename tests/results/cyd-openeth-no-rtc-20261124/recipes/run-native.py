"""Unmodified full-app controller over the qualified exact-length RX fixtures."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
backend,label=sys.argv[1:]
assert backend in ('pdm','continuous','legacy') and label.replace('-','').isalnum()
directory=BASE/backend
qualification=json.loads((directory/'qualification.json').read_bytes())
assert qualification['passed'] and qualification['rtc_workspace'] is False
assert qualification['rtc_probe_enabled'] is True
assert qualification['effective_config_delta']=={'YORADIO_WS_STATUS_RTC_SLOW':{'before_present':True,'before':True,'after_present':True,'after':False}}
assert qualification['geometry']['rtc_slow_used_bytes']==104
assert qualification['geometry']['rtc_slow_free_bytes']==8064
qemu=ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe'
def pin(file):
    data=file.read_bytes()
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
assert pin(qemu)['sha256']=='28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
image=directory/'fixture/yoradio_cyd2usb_native.bin'
assert pin(image)==qualification['image']
out=directory/label
assert not out.exists()
controller=ROOT/'tests/run-cyd-full-app-openeth.py'
tls=ROOT/'.build/cws24r'/('rtc-'+backend+'-workspace')
controller_commit=subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
binding=dict(backend=backend,label=label,physical_tested=False,
    controller_source_commit=controller_commit,post_eof_health_required=True,
    source_commit=qualification['source_commit'],rtc_workspace=False,rtc_probe_enabled=True,qemu=pin(qemu),controller=pin(controller),
    fixture_qualification=pin(directory/'qualification.json'),image=pin(image),
    config=pin(directory/'fixture/config/sdkconfig.json'),
    original_fixture_identity=pin(tls/'fixture-identity.json'),
    scope='Strengthened full HE-AAC/TLS/two-WebSocket controller with status/health after final asset and peer closure; no QMP pause.')
(directory/(label+'-input-binding.json')).write_text(json.dumps(binding,indent=2)+'\n')
command=[sys.executable,'-B',str(controller),'--build',str(directory/'fixture'),
    '--qemu',str(qemu),'--rom','C:/Work/QEMU-ESP32/pc-bios','--output',str(out),
    '--tls-material',str(tls),'--codec','aac','--aac-profile','he',
    '--through-eof','--full-tls-records','--websocket-clients','2']
with (directory/(label+'-terminal.log')).open('xb') as log:
    child=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
assert child.returncode in (0,1)
report=json.loads((out/'report.json').read_bytes())
assert report['state'] in ('TERMINAL_PASS','TERMINAL_NONPASS')
health=report.get('post_eof_health',report.get('eof_health',report.get('last_reachable_health',{})))
if report['state']=='TERMINAL_PASS':
    assert 'post_eof_status' in report and 'post_eof_health' in report
    assert health['allocation_failures']==0
print(json.dumps(dict(backend=backend,label=label,state=report['state'],reason=report.get('reason'),
    minimum_heap=health.get('minimum_heap'),allocation_failures=health.get('allocation_failures'),
    output=health.get('output'),output_driver=health.get('output_driver'),
    pcm_sha256=report.get('pcm_sha256'),pcm_flushes=report.get('pcm_probe_flushes'))),flush=True)
