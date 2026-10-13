"""Bounded public MP3 HTTP/HTTPS observations and independent host decoding."""
import json
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
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
source='https://ice5.somafm.com/groovesalad-256-mp3'
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
                    if name.startswith('mp3:') and len(samples)>=5 and samples[-1]['seconds']>=15 and all(not s['audio'] for s in samples[-5:]):
                        batch['stopped_early']=True
                        break
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
def reference_start(url, transport):
    progress_path=OUT/(transport+'-ffmpeg-progress.log')
    error_path=ROOT/(transport+'-ffmpeg-stderr.private')
    error_log=error_path.open('xb')
    command=['ffmpeg','-nostdin','-v','error','-rw_timeout','15000000','-tls_verify','1',
        '-i',url,'-t','605','-vn','-stats_period','1','-progress',str(progress_path),'-f','null','NUL']
    process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=error_log)
    return process,error_log,error_path,progress_path

def reference_finish(ref):
    process,error_log,error_path,progress_path=ref;completed=True
    try:code=process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        completed=False;process.terminate();code=process.wait(timeout=5)
    finally:error_log.close()
    data=error_path.read_bytes();last={}
    if progress_path.exists():
        for line in progress_path.read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);last[key]=value
    decoded=float(last.get('out_time_us','0'))/1e6
    return dict(completed=completed,returncode=code,decoded_seconds=decoded,
        error_bytes=len(data),error_sha256=sha(data),
        result='PASS' if completed and code==0 and decoded>=604 and not data else 'FAIL')

with (OUT/'request-phases.jsonl').open('x') as trace_log:
    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):
        try:
            print('INSTALL candidate for public MP3',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://unused.invalid',specs,Capture(None),OUT,checkpoint=progress)
            stop_control(b);suite.observe(10,'idle:initial',interval=1)
            idle_before=b.health_samples[-3:]
            for transport in ('http','https'):
                reference=probe(source,'ffprobe')
                save(transport+'-reference.json',reference)
                url=source.replace('https://','http://',1) if transport=='http' else source
                stop_control(b);time.sleep(2)
                ref=reference_start(url,transport)
                try:
                    b.play(url);begin=len(b.health_samples)
                    try:states=suite.observe(600,'mp3:'+transport,interval=1)
                    finally:save('health.json',b.health_samples)
                    rows=b.health_samples[begin:]
                    collection=evaluate(lambda:sustained_window(states,rows,600))
                    steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
                    stopped=next((s for s in states if s['seconds']>=15 and not s['audio']),None)
                    results[transport]=dict(seconds_requested=600,seconds_observed=states[-1]['seconds'],
                        collection=dict(result=collection['result'],reason=collection.get('reason')),
                        transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback(states,reference['spec'],minimum=351,warmup=15)),
                        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)),
                        first_stopped=stopped,health=check_health(rows))
                    save('results.json',results)
                finally:
                    host=reference_finish(ref)
                    save(transport+'-host.json',host)
                    stop_control(b)
                suite.observe(10,'idle:after-'+transport,interval=1);save('health.json',b.health_samples)
                print('RESULT',transport,{k:results[transport][k]['result'] for k in ('collection','transport','format','output','memory')},'host',host['result'],flush=True)
            from common import check_recovery_heap
            save('recovery.json',dict(initial=idle_before,final=b.health_samples[-3:],check=evaluate(lambda:check_recovery_heap(idle_before,b.health_samples[-3:]))))
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
