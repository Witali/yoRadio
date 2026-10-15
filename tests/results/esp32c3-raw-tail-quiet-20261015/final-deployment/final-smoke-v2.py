"""Verify installed full-rate HE-AAC and PS, then leave the board stopped."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common  # Adds the shared tools directory before server imports.
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
from common import Report,fixtures,require,check_recovery_heap
from production_health import HealthBoard,check_health,check_decoder_health
from ota import image_info,snapshot,verify_snapshot
from run import Capture,Suite
from audio_test_server.server import Server
base=Path('.build/c3-raw-tail-quiet-20261015');out=base/'final-deployment-repeat'/'smoke'
require(not out.exists(),'Preserve previous evidence')
b=HealthBoard('http://192.168.100.4');identity=b.info()
image=image_info(Path('firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin').read_bytes())
require(identity['app_elf_sha256']==image['app_elf_sha256'],'Unexpected installed application')
require(not b.status()['audio'],'Expected stopped board')
before=snapshot(b);specs=fixtures()
report=Report(out/'report.json',identity);report.data.update(image=image,
    scope='Post-install format/EOF, output and recovery smoke; no acoustic claim')
suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),out,cpu_budget=None)
def save():
    report.save();(out/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n')
def case(name,fn):
    try:report.case(name,fn)
    finally:save()
with Server('192.168.100.253',8772,specs,delivery_stats=True,pacing_ratio=1.0) as server:
    try:
        suite.observe(12,'idle:initial',interval=1);initial=b.health_samples[-3:]
        for name in ('he-48000-stereo','hev2-44100-stereo'):
            case(name,lambda name=name:suite.file(name,'auto'))
        b.stop();suite.observe(12,'idle:final',interval=1)
        case('recovery',lambda:check_recovery_heap(initial,b.health_samples[-3:]))
    finally:
        case('settings',lambda:(b.stop(),verify_snapshot(b,before))[1])
        case('health',lambda:check_health(b.health_samples))
        case('decoder-health',lambda:check_decoder_health(b.health_samples))
        report.data['server_events']=server.events;save()
raise SystemExit(report.exit_code())
