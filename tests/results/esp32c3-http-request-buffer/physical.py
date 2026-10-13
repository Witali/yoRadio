"""Compare fixed HE-AAC and public HTTPS with/without request-buffer release."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,Failure,check_playback,fixtures,require,sha
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
from production_health import HealthBoard,check_health
from sustained_output import sustained_window,check_memory,check_output
from public_streams import probe
from run import Suite,Capture
from audio_test_server.server import Server

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'physical'
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease')
RESTORE=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/app.bin')
board=Board('http://192.168.100.4')
baseline=image_info(RESTORE.read_bytes());candidate=image_info((ART/'app.bin').read_bytes())
require(json.loads((ROOT/'quiet-http-txrelease/build-audit.json').read_text())['result']=='PASS','Missing build audit')
require(board.info()['app_elf_sha256']==baseline['app_elf_sha256'],'Unexpected initial image')
require(not OUT.exists(),'Preserve evidence')
original=board.status();station=board.json('/api/native/status')['station']
with board.websocket() as ws:
    ws.send('getindex');current=None;deadline=time.perf_counter()+5
    while time.perf_counter()<deadline:
        message=json.loads(ws.recv(timeout=5))
        if 'current' in message:current=message['current'];break
require(type(current) is int and current>0,'Cannot restore station')
before=snapshot(board)
specs=fixtures()
reference_command=json.loads(Path('.build/c3-prefill1000-public-20261010/faad-reference-command.json').read_text())
source='https://ice5.somafm.com/groovesalad-64-aac'
OUT.mkdir()
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
sources={}
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in Path(folder).glob('*.py'):
        sources[path.as_posix()]=sha(path.read_bytes())
        dest=ROOT/'test-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
save('initial.json',dict(baseline=baseline,candidate=candidate,original=original,test_sources=sources,controller_sha256=sha(Path(__file__).read_bytes())))
def install(path):
    raw=path.read_bytes();expected=image_info(raw);active=board.info()
    require(len(raw)<=active['max_size'],'OTA slot too small')
    board.stop();target='app1' if active['partition']=='app0' else 'app0'
    code,body=upload(board.origin,multipart(raw));require(code==200 and body==b'OK','OTA failed')
    return wait_image(board,expected['app_elf_sha256'],target,timeout=60)
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
results={};last=0
def progress(completed,batch):
    global last
    if time.perf_counter()-last>25:
        last=time.perf_counter();print(batch['case'],round(batch['samples'][-1]['seconds']),flush=True)
        save('progress.json',dict(case=batch['case'],status=batch['samples'][-1]))
try:
    for variant in ('baseline','released'):
        if variant=='released':
            print('INSTALL experimental application',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
        b=HealthBoard(board.origin)
        folder=OUT/variant;folder.mkdir()
        suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),folder,checkpoint=progress)
        b.stop();suite.observe(8,variant+':idle',interval=1)
        with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
            for local in (True,False):
                name=variant+(':local-he' if local else ':public-he')
                reference=dict(spec=specs['he-44100-stereo']) if local else probe(source,'ffprobe',reference_command)
                b.stop();time.sleep(2)
                b.play('http://192.168.100.253:8772/stream/he-44100-stereo' if local else source)
                begin=len(b.health_samples)
                states=suite.observe(60,name)
                steady,health=sustained_window(states,b.health_samples[begin:],60)
                results[name]=dict(variant=variant,local=local,
                    spec={k:v for k,v in reference['spec'].items() if k!='data'},
                    format=evaluate(lambda:check_playback(states,reference['spec'],minimum=27,warmup=15)),
                    output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
                if not local:save(variant+'-public-reference.json',reference)
                b.stop();suite.observe(5,name+':idle',interval=1)
                save('results.json',results);(folder/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n')
                print('RESULT',name,{k:results[name][k]['result'] for k in ('format','output','memory')},flush=True)
            (folder/'server.json').write_text(json.dumps(server.events,indent=2)+'\n')
finally:
    print('RESTORE original production application',flush=True)
    if board.info()['app_elf_sha256']!=baseline['app_elf_sha256']:install(RESTORE)
    board.stop()
    if original['audio']:
        with board.websocket() as ws:
            ws.send('play='+str(current));deadline=time.perf_counter()+5
            while time.perf_counter()<deadline:
                message=json.loads(ws.recv(timeout=5))
                if message.get('current')==current:break
    b=HealthBoard(board.origin);states=[]
    for _ in range(5):time.sleep(4);states.append(b.status())
    persisted=verify_snapshot(board,before)
    same_station=board.json('/api/native/status')['station']==station if original['audio'] else True
    require(same_station and all(s['audio']==original['audio'] for s in states[-3:]),'Playback restore failed')
    require(board.info()['app_elf_sha256']==baseline['app_elf_sha256'],'Image restoration failed')
    save('restoration.json',dict(identity=board.info(),persistence=persisted,same_station=same_station,states=states,health=check_health(b.health_samples)))
    print('Original firmware, settings and station restored',flush=True)
