"""Candidate OTA regression and bounded HE-AAC HTTPS playback, with restoration."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import ota
from common import Board,Failure,check_playback,fixtures,require,sha,exception_details
from ota import image_info,multipart,snapshot,upload,verify_snapshot,wait_image
from production_health import HealthBoard,check_health
from sustained_output import sustained_window,check_memory,check_output
from public_streams import probe
from run import Suite as OriginalSuite,Capture
from trace_transport import TransportTrace
from audio_test_server.server import Server

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'physical'
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease')
RESTORE=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/app.bin')
board=Board('http://192.168.100.4')
baseline=image_info(RESTORE.read_bytes());candidate=image_info((ART/'app.bin').read_bytes())
require(json.loads((Path('.build/c3-http-request-buffer/quiet-http-txrelease/build-audit.json')).read_text())['result']=='PASS','Missing build audit')
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

class Suite(OriginalSuite):
    def observe(self, seconds, name, interval=.4):
        start=time.perf_counter();samples=[];errors=[]
        batch=dict(case=name,started_at=start,samples=samples,errors=errors)
        try:
            while time.perf_counter()-start<seconds:
                requested=time.perf_counter()
                try:
                    state=self.board.status()
                    samples.append(dict(seconds=time.perf_counter()-start,request_ms=(time.perf_counter()-requested)*1000,**state))
                    progress(None,batch)
                except (OSError,TimeoutError) as error:
                    errors.append(dict(seconds=requested-start,exception_chain=exception_details(error)))
                time.sleep(interval)
        finally:
            batch['ended_at']=time.perf_counter();self.observations.append(batch)
            (self.output/'status.json').write_text(json.dumps(self.observations,indent=2)+'\n')
        return samples

def stop_control(b):
    for attempt in range(3):
        try:return b.stop()
        except (OSError,TimeoutError) as error:
            control_errors.append(dict(operation='stop',attempt=attempt,exception_chain=exception_details(error)))
            save('control-errors.json',control_errors)
            if attempt==2:raise
            time.sleep(1)
control_errors=[]

results={};last=0
def progress(completed,batch):
    global last
    if time.perf_counter()-last>25:
        last=time.perf_counter();print(batch['case'],round(batch['samples'][-1]['seconds']),flush=True)
        save('progress.json',dict(case=batch['case'],status=batch['samples'][-1],health=b.health_samples[-1] if 'b' in globals() else None))
with (OUT/'request-phases.jsonl').open('x') as trace_log:
    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):
        try:
            print('INSTALL candidate for OTA regression',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                saved_args=sys.argv
                try:
                    sys.argv=['ota.py','--board',board.origin,'--firmware',str(ART/'app.bin'),
                        '--suite','negative','--suite','roundtrip','--suite','while-playing','--suite','slow',
                        '--play-url','http://192.168.100.253:8772/stream/he-44100-stereo',
                        '--play-fixture','he-44100-stereo','--output',str(OUT/'ota.json')]
                    result=ota.main()
                    save('ota-exit.json',dict(exit_code=result))
                finally:
                    sys.argv=saved_args
                    save('server.json',server.events)
            require(board.info()['app_elf_sha256']==candidate['app_elf_sha256'],'Wrong image after OTA regression')
            reference=probe(source,'ffprobe',reference_command)
            save('public-reference.json',reference)
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://unused.invalid',specs,Capture(None),OUT,checkpoint=progress)
            stop_control(b);suite.observe(10,'idle:before-soak',interval=1)
            idle_before=b.health_samples[-3:]
            b.play(source);begin=len(b.health_samples)
            try:
                states=suite.observe(600,'public-he-https-600s',interval=1)
            finally:save('health.json',b.health_samples)
            steady,health=sustained_window(states,b.health_samples[begin:],600)
            result=dict(seconds=600,transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                format=evaluate(lambda:check_playback(states,reference['spec'],minimum=351,warmup=15)),
                output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)),
                health=check_health(health),maximum_response_ms=max(s['request_ms'] for s in states))
            save('soak.json',result)
            print('SOAK', {k:result[k]['result'] for k in ('transport','format','output','memory')},flush=True)
            stop_control(b);suite.observe(10,'idle:after-soak',interval=1)
            from common import check_recovery_heap
            save('soak-recovery.json',dict(initial=idle_before,final=b.health_samples[-3:],
                check=evaluate(lambda:check_recovery_heap(idle_before,b.health_samples[-3:]))))
            save('health.json',b.health_samples)
        finally:
            print('RESTORE original production application',flush=True)
            if board.info()['app_elf_sha256']!=baseline['app_elf_sha256']:install(RESTORE)
            stop_control(board)
            if original['audio']:
                with board.websocket() as ws:
                    ws.send('play='+str(current));deadline=time.perf_counter()+5
                    while time.perf_counter()<deadline:
                        if json.loads(ws.recv(timeout=5)).get('current')==current:break
            b=HealthBoard(board.origin);states=[]
            for _ in range(5):time.sleep(4);states.append(b.status())
            persisted=verify_snapshot(board,before)
            same_station=board.json('/api/native/status')['station']==station if original['audio'] else True
            require(same_station and all(s['audio']==original['audio'] for s in states[-3:]),'Playback restore failed')
            require(not original['audio'] or all(s['pcm_sample_rate']>0 for s in states[-3:]),'No decoded playback after restoration')
            require(board.info()['app_elf_sha256']==baseline['app_elf_sha256'],'Image restoration failed')
            save('restoration.json',dict(identity=board.info(),persistence=persisted,same_station=same_station,states=states,health=check_health(b.health_samples)))
            print('Original firmware, settings and station restored',flush=True)
