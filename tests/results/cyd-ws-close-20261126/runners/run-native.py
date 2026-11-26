"""Unchanged strict full-stream controller against one qualified Close-fix image."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
SOURCE='95672e8f673ec977b6f61b78eeba6958d0d992ac'
backend,label=sys.argv[1:]
assert backend in ('legacy','pdm','continuous') and label.replace('-','').isalnum()
load=lambda p:json.loads(p.read_bytes())
def pin(p):
 body=p.read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
folder=BASE/'target/sdk'/backend
qualification=load(folder/'qualification.json')
assert qualification['passed'] and qualification['source_commit']==SOURCE
assert not qualification.get('physical_tested',False)
image=folder/'fixture/yoradio_cyd2usb_native.bin'
elf=folder/'compiled/yoradio_cyd2usb_native.elf'
config=folder/'fixture/config/sdkconfig.json'
assert pin(image)==qualification['image'] and pin(elf)==qualification['elf']
assert pin(config)==qualification['config']
settings=load(config)
assert settings==load(ROOT/'.build/cpbuf24/sdk'/backend/'compiled/config/sdkconfig.json')
assert settings['YORADIO_WS_STATUS_RTC_SLOW'] is False and not settings['FREERTOS_UNICORE']
assert subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==SOURCE
assert not subprocess.check_output(['git','-c','core.longpaths=true','diff','--name-only','HEAD'],cwd=ROOT)
controller=ROOT/'tests/run-cyd-full-app-openeth.py'
qemu=ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe'
assert pin(controller)['sha256']=='ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f'
assert pin(qemu)['sha256']=='28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
output=BASE/'native'/backend/label
assert not output.exists();output.parent.mkdir(parents=True,exist_ok=True)
tls=ROOT/'.build/cws24r'/('rtc-'+backend+'-workspace')
binding=dict(source_commit=SOURCE,backend=backend,label=label,physical_tested=False,
 rtc_workspace=False,pbuf_failure_probe=True,qualification=pin(folder/'qualification.json'),
 image=pin(image),elf=pin(elf),config=pin(config),controller=pin(controller),qemu=pin(qemu),
 original_tls_fixture_identity=pin(tls/'fixture-identity.json'),
 tls_date_policy=pin(ROOT/'.build/cpbuf24/tls-date-policy-20261126.json'),
 scope='Close-delivery regression; unchanged full TLS/HE-AAC, PCM hash, WebUI, two WS and zero-allocation gate through final close.')
(output.parent/(label+'-input-binding.json')).write_text(json.dumps(binding,indent=2)+'\n')
command=[sys.executable,'-B',str(controller),'--build',str(folder/'fixture'),'--qemu',str(qemu),
 '--rom','C:/Work/QEMU-ESP32/pc-bios','--output',str(output),'--tls-material',str(tls),
 '--codec','aac','--aac-profile','he','--through-eof','--full-tls-records','--websocket-clients','2']
with(output.parent/(label+'-terminal.log')).open('xb')as log:
 child=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
assert child.returncode in (0,1)
report=load(output/'report.json')
assert report['state'] in ('TERMINAL_PASS','TERMINAL_NONPASS')
assert report['config_sha256']==binding['config']['sha256']
app_parts=[part for part in report['flash_parts'] if part['file']=='yoradio_cyd2usb_native.bin']
assert len(app_parts)==1 and {key:app_parts[0][key] for key in ('bytes','sha256')}==binding['image']
assert report['qemu_sha256']==binding['qemu']['sha256'] and report['runner_sha256']==binding['controller']['sha256']
for path,key in ((image,'image'),(elf,'elf'),(config,'config'),(controller,'controller'),(qemu,'qemu')):
 assert pin(path)==binding[key], 'Qualified runtime input changed during the run'
assert subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==SOURCE
assert not subprocess.check_output(['git','-c','core.longpaths=true','diff','--name-only','HEAD'],cwd=ROOT)
assert pin(folder/'qualification.json')==binding['qualification']
assert pin(tls/'fixture-identity.json')==binding['original_tls_fixture_identity']
assert pin(ROOT/'.build/cpbuf24/tls-date-policy-20261126.json')==binding['tls_date_policy']
(output.parent/(label+'-input-verification.json')).write_text(json.dumps(dict(
 before_and_after_inputs_match=True,actual_flash_app_matches_qualified_image=True,
 actual_config_bytes_match=True,source_commit=SOURCE,report=pin(output/'report.json')),indent=2)+'\n')
health=report.get('post_eof_health') or report.get('eof_health') or report.get('last_reachable_health') or {}
print(json.dumps(dict(backend=backend,state=report['state'],reason=report.get('reason'),
 allocation_failures=health.get('allocation_failures'),minimum_heap=health.get('minimum_heap'),
 pcm_sha256=report.get('pcm_sha256'),pcm_flushes=report.get('pcm_probe_flushes'))),flush=True)
