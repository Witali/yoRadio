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
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-radio-wifi-probe')
RESTORE=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/app.bin')
board=Board('http://192.168.100.4')
baseline=image_info(RESTORE.read_bytes());candidate=image_info((ART/'app.bin').read_bytes())
require(json.loads((Path('.build/c3-radio-wifi-probe/build-audit.json')).read_text())['result']=='PASS','Missing build audit')
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
specs=fixtures(Path('.build/c3-production-radio-opus/fixtures/manifest.json'))
fixture='stress-opus-48000-2ch-16bit-90s'
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
import re
import threading
import serial
from serial_lines import serial_lines
from common import check_recovery_heap

class PassiveCapture:
    def __init__(self):
        self.rows=[];self.transport=[]
        self.closed=threading.Event();self.ready=threading.Event()
        self.thread=threading.Thread(target=self.read,daemon=True);self.thread.start()
        if not self.ready.wait(5):
            self.close();require(False,'Passive USB capture unavailable')
    def read(self):
        first=True
        while not self.closed.is_set():
            port=serial.Serial(port=None,baudrate=115200,timeout=.2)
            port.dtr=port.rts=False;port.port='COM9'
            try:
                port.open()
                if first:port.reset_input_buffer();first=False
                self.ready.set()
                for line in serial_lines(port,self.closed):
                    if 'PERF ' in line:
                        self.rows.append(dict(at=time.perf_counter(),line=line))
                    elif 'serial capture interrupted' in line:
                        self.transport.append(dict(at=time.perf_counter(),event=line))
            except (OSError,serial.SerialException):
                self.transport.append(dict(at=time.perf_counter(),event='USB reopen pending'))
            finally:port.close()
            self.closed.wait(.2)
    def close(self):
        self.closed.set();self.thread.join(3)
        require(not self.thread.is_alive(),'Capture reader did not stop')

capture=None
with (OUT/'request-phases.jsonl').open('x') as trace_log:
    with TransportTrace('192.168.100.4',trace_log,capture_socket_ports=True):
        try:
            capture=PassiveCapture()
            print('INSTALL TCP/Wi-Fi diagnostic application',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),OUT,checkpoint=progress)
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                stop_control(b);suite.observe(12,'idle:initial',interval=.4)
                initial=b.health_samples[-3:]
                for cycle in range(5):
                    name='opus:'+str(cycle+1)
                    b.play('http://192.168.100.253:8772/file/'+fixture)
                    begin=len(b.health_samples);states=suite.observe(60,name,interval=.4)
                    rows=b.health_samples[begin:];steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
                    collected=evaluate(lambda:sustained_window(states,rows,60))
                    results[name]=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
                        transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback(states,specs[fixture],minimum=27,warmup=15)),
                        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)))
                    stop_control(b)
                    name='hev2-eof:'+str(cycle+1);b.play('http://192.168.100.253:8772/file/hev2-44100-stereo','aac')
                    begin=len(b.health_samples);states=suite.observe(24,name,interval=.4)
                    rows=b.health_samples[begin:]
                    def terminal():
                        require(len(states)>=15,'Sparse EOF observation')
                        require(all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in states[-5:]),'Wrong terminal state')
                        return dict(last_samples=5)
                    active=[h for s,h in zip(states,rows) if 3<=s['seconds']<=8 and s['audio']]
                    results[name]=dict(transport=dict(result='FAIL' if suite.observations[-1]['errors'] else 'PASS',errors=suite.observations[-1]['errors']),
                        format=evaluate(lambda:check_playback([s for s in states if s['seconds']<=8],specs['hev2-44100-stereo'])),
                        output=evaluate(lambda:check_output(active)),terminal=evaluate(terminal),health=check_health(rows))
                    stop_control(b);suite.observe(10,'idle:cycle:'+str(cycle+1),interval=.4)
                    results[name]['recovery']=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))
                    save('results.json',results);save('health.json',b.health_samples);save('server.json',server.events)
                    save('performance.json',list(capture.rows));save('serial-transport.json',list(capture.transport))
                    print('CYCLE',cycle+1,{k:v['result'] for k,v in results[name].items() if isinstance(v,dict) and 'result' in v},flush=True)
                save('recovery.json',dict(initial=initial,final=b.health_samples[-3:],check=evaluate(lambda:check_recovery_heap(initial,b.health_samples[-3:]))))
        except Exception as error:
            save('controller-failure.json',dict(exception_chain=exception_details(error)))
            raise
        finally:
            if capture:
                capture.close()
                save('performance.json',capture.rows);save('serial-transport.json',capture.transport)
            if 'b' in globals():save('health.json',b.health_samples)
            if 'server' in globals():save('server.json',server.events)
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
