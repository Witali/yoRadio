"""Matched ICY controls on the installed production image; no flashing."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure, check_playback, fixtures, require, sha
from ota import snapshot, verify_snapshot
from production_health import HealthBoard, check_health
from sustained_output import sustained_window, check_output, check_memory
from audio_test_server.server import Server
from run import Capture, Suite

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'physical'
require(not OUT.exists(),'Preserve evidence')
b=HealthBoard('http://192.168.100.4')
identity=b.info()
require(identity['app_elf_sha256']=='73da8e2146c5b3691bcfc7a8fb46b34109e74099eac221df2b66e05a62b95245','Unexpected firmware')
raw=b.json('/api/native/status')
original=b.status()
station=raw.get('station','')  # In-memory only; never serialize metadata/settings.
with b.websocket() as ws:
    ws.send('getindex')
    deadline=time.perf_counter()+5
    current=None
    while time.perf_counter()<deadline:
        message=json.loads(ws.recv(timeout=5))
        if 'current' in message:
            current=message['current'];break
require(type(current) is int and current>0,'Cannot restore selected station')
before=snapshot(b)
specs=fixtures(Path('tests/results/esp32c3-mp3-transport-controls-20261010/fixtures/manifest.json'))
OUT.mkdir()
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
sources={}
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in Path(folder).glob('*.py'):
        sources[path.as_posix()]=sha(path.read_bytes())
save('initial.json',dict(identity=identity,status=original,test_sources=sources,controller_sha256=sha(Path(__file__).read_bytes())))
last=0
def progress(completed,batch):
    global last
    if time.perf_counter()-last>25:
        last=time.perf_counter()
        print(batch['case'],round(batch['samples'][-1]['seconds']),flush=True)
        save('progress.json',dict(case=batch['case'],status=batch['samples'][-1],health=b.health_samples[-1]))
suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),OUT,checkpoint=progress)
results={}
def check(fn):
    try: return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
try:
    suite.observe(10,'initial-current',interval=1)
    for name,fixture,interval,mode in (
        ('mp3-plain','mp3-256-44100-stereo',0,'file'),
        ('mp3-icy','mp3-256-44100-stereo',45000,'file'),
        ('hev2-icy','hev2-44100-stereo',45000,'stream')):
        b.stop();time.sleep(2)
        with Server('192.168.100.253',8772,specs,delivery_stats=True,pacing_ratio=1.0,icy_interval=interval) as server:
            b.play(f'http://192.168.100.253:8772/{mode}/{fixture}')
            start=len(b.health_samples)
            states=suite.observe(90,name)
            steady,health=sustained_window(states,b.health_samples[start:],90)
            results[name]=dict(fixture=fixture,fixture_sha256=specs[fixture]['sha256'],interval=interval,
                format=check(lambda:check_playback(states,specs[fixture],minimum=45,warmup=15)),
                output=check(lambda:check_output(health)),memory=check(lambda:check_memory(health)))
            b.stop();time.sleep(.5)
            save(name+'-server.json',server.events)
            require(len(server.events)==1,'Unexpected server request count')
            if interval:require(server.events[0].get('icy_insertions',0)>0,'ICY was not requested/delivered')
            save('results.json',results);save('health.json',b.health_samples)
            print('RESULT',name,{k:v['result'] for k,v in results[name].items() if isinstance(v,dict)},flush=True)
finally:
    b.stop()
    if original['audio']:
        with b.websocket() as ws:
            ws.send('play='+str(current))
            deadline=time.perf_counter()+5
            while time.perf_counter()<deadline:
                message=json.loads(ws.recv(timeout=5))
                if message.get('current')==current:break
    states=suite.observe(20,'restored',interval=1)
    saved=verify_snapshot(b,before)
    same_station=b.json('/api/native/status').get('station')==station if original['audio'] else True
    require(same_station and all(s['audio']==original['audio'] for s in states[-3:]),'Playback restoration failed')
    require(b.info()==identity,'Firmware identity changed')
    save('restoration.json',dict(identity=identity,persistence=saved,same_station=same_station,states=states[-3:],health=check_health(b.health_samples)))
    save('health.json',b.health_samples)
    print('Original production image, settings and playback restored',flush=True)
