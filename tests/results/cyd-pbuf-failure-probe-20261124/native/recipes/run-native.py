"""Strict original controller over root-released pbuf diagnostic fixtures."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
SOURCE='f7dee344fb30ce109f2d30a01f0325d353e3b2eb'
backend,label=sys.argv[1:]
assert backend in ('legacy','pdm','continuous') and label.replace('-','').isalnum()

def load(path):return json.loads(path.read_bytes())
def pin(path):
    body=path.read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
release=load(BASE/'runtime-release.json')
assert release['source_commit']==SOURCE and release['all_sdk_passed'] is True
row=release['profiles'][backend]
folder=BASE/'sdk'/backend
assert pin(folder/'qualification.json')==row['qualification']
qualification=load(folder/'qualification.json')
assert qualification['passed'] is True and qualification['source_commit']==SOURCE
image=folder/'fixture/yoradio_cyd2usb_native.bin'
config=folder/'fixture/config/sdkconfig.json'
assert pin(image)==row['image'] and pin(config)==row['config']
settings=load(config)
assert settings['YORADIO_WS_STATUS_RTC_SLOW'] is False and not settings['FREERTOS_UNICORE']
assert subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==SOURCE
controller=ROOT/'tests/run-cyd-full-app-openeth.py'
qemu=ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe'
assert pin(controller)['sha256']=='ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f'
assert pin(qemu)['sha256']=='28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
output=BASE/'native'/backend/label
assert not output.exists();output.parent.mkdir(parents=True,exist_ok=True)
tls=ROOT/'.build/cws24r'/('rtc-'+backend+'-workspace')
binding=dict(source_commit=SOURCE,controller_source_commit=SOURCE,backend=backend,label=label,
    physical_tested=False,rtc_workspace=False,pbuf_failure_probe=True,qualification=row['qualification'],
    image=pin(image),config=pin(config),controller=pin(controller),qemu=pin(qemu),
    original_tls_fixture_identity=pin(tls/'fixture-identity.json'),runtime_release=pin(BASE/'runtime-release.json'),
    scope='Observer attribution, not a memory fix. Strict original allocation gate unchanged; preserve all terminal NONPASS outcomes.')
(output.parent/(label+'-input-binding.json')).write_text(json.dumps(binding,indent=2)+'\n')
command=[sys.executable,'-B',str(controller),'--build',str(folder/'fixture'),'--qemu',str(qemu),
    '--rom','C:/Work/QEMU-ESP32/pc-bios','--output',str(output),'--tls-material',str(tls),
    '--codec','aac','--aac-profile','he','--through-eof','--full-tls-records','--websocket-clients','2']
with(output.parent/(label+'-terminal.log')).open('xb')as log:
    child=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
assert child.returncode in(0,1)
report=load(output/'report.json')
assert report['state'] in('TERMINAL_PASS','TERMINAL_NONPASS')
health=report.get('post_eof_health')or report.get('eof_health')or report.get('last_reachable_health')or{}
print(json.dumps(dict(backend=backend,state=report['state'],reason=report.get('reason'),
    allocation_failures=health.get('allocation_failures'),minimum_heap=health.get('minimum_heap'),
    pcm_sha256=report.get('pcm_sha256'),pcm_flushes=report.get('pcm_probe_flushes'))),flush=True)
