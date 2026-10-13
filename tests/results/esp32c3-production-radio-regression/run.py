"""Quiet-image codec/HTTP regression; app-only OTA and original-state restoration."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,Report,fixtures,require,sha,check_playback,check_recovery_heap
from ota import image_info,multipart,upload,wait_image,snapshot,verify_snapshot
from production_health import HealthBoard,check_health
from sustained_output import check_output,check_memory
from run import Suite,Capture
from audio_test_server.server import Server
from audio_test_server.fixtures import SEQUENCES
from trace_transport import TransportTrace

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'physical'
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-radio')
RESTORE=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/app.bin')
board=Board('http://192.168.100.4')
baseline=image_info(RESTORE.read_bytes());candidate=image_info((ART/'app.bin').read_bytes())
require(board.info()['app_elf_sha256']==baseline['app_elf_sha256'],'Unexpected initial firmware')
require(not OUT.exists(),'Preserve evidence')
require(json.loads(Path('.build/c3-production-radio/production-radio/build-audit.json').read_text())['result']=='PASS','Build audit missing')
original=board.status();station=board.json('/api/native/status')['station']
with board.websocket() as ws:
    ws.send('getindex');current=None;deadline=time.perf_counter()+5
    while time.perf_counter()<deadline:
        message=json.loads(ws.recv(timeout=5))
        if 'current' in message:current=message['current'];break
require(type(current) is int and current>0,'Cannot restore station')
before=snapshot(board);specs=fixtures();names=[n for n in specs if n not in SEQUENCES]
OUT.mkdir()
save=lambda name,value:(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
report=Report(OUT/'report.json',board.info())
report.data.update(candidate=candidate,baseline=baseline,fixture_specs={n:{k:v for k,v in specs[n].items() if k!='data'} for n in names},
    controller_sha256=sha(Path(__file__).read_bytes()),scope='HTTP fixture format, EOF, fault recovery, sampled health and output counters. No analog/PCM comparison or HTTPS qualification.')
save('initial.json',dict(original=original,baseline=baseline,candidate=candidate))
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for source in Path(folder).glob('*.py'):
        dest=ROOT/'test-sources'/source;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())

def install(path):
    raw=path.read_bytes();expected=image_info(raw);active=board.info()
    require(len(raw)<=active['max_size'],'Image too large')
    board.stop();target='app1' if active['partition']=='app0' else 'app0'
    code,body=upload(board.origin,multipart(raw));require(code==200 and body==b'OK','OTA failed')
    return wait_image(board,expected['app_elf_sha256'],target,timeout=60)

last=0
def progress(completed,batch):
    global last
    if time.perf_counter()-last>25:
        last=time.perf_counter();print('OBSERVE',batch['case'],round(batch['samples'][-1]['seconds']),flush=True)
        save('progress.json',dict(case=batch['case'],status=batch['samples'][-1]))

def case(name,fn):
    try:report.case(name,fn)
    finally:
        save('health.json',b.health_samples)
        save('server.json',server.events)

def file_terminal(name,hint):
    spec=specs[name];suite.start(name,hint=hint)
    try:
        start=len(b.health_samples)
        states=suite.observe(max(7,spec['seconds']-3),name+':'+hint+':playing')
        health=b.health_samples[start:]
        evidence=check_playback(states,spec)
        require(len(health)==len(states),'Unpaired health samples')
        steady=[h for s,h in zip(states,health) if s['seconds']>=4]
        output=check_output(steady);memory=check_memory(steady)
        tail=suite.observe(10,name+':'+hint+':terminal')
        stopped=next((i for i,s in enumerate(tail) if not s['audio']),None)
        require(stopped is not None and len(tail)-stopped>=2,'No confirmed EOF')
        require(all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in tail[stopped:]),'Stale format or decoder error after EOF')
        with b.websocket() as ws:
            ws.send('getindex');deadline=time.perf_counter()+5
            while time.perf_counter()<deadline:
                message=json.loads(ws.recv(timeout=5));values={p['id']:p['value'] for p in message.get('payload',[])}
                if 'fmt' in values:
                    require(values['fmt']=='stream ended' and values.get('playerwrap')!='playing','Stale WebSocket EOF')
                    break
            else:raise AssertionError('No WebSocket EOF snapshot')
        return dict(format=evidence,output=output,memory=memory,terminal_samples=len(tail)-stopped,websocket_stopped=True)
    finally:b.stop()

with (OUT/'request-phases.jsonl').open('x') as trace:
    with TransportTrace('192.168.100.4',trace,capture_socket_ports=True):
        try:
            print('INSTALL experimental application',flush=True)
            save('installed.json',dict(identity=install(ART/'app.bin'),persistence=verify_snapshot(board,before)))
            b=HealthBoard(board.origin)
            suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),OUT,checkpoint=progress)
            with Server('192.168.100.253',8772,specs,pacing_ratio=1.0,delivery_stats=True) as server:
                b.stop();suite.observe(10,'idle:initial',interval=1);initial_heap=b.health_samples[-3:]
                for name in names:
                    for hint in ('auto',specs[name]['codec']):case('file-eof:'+name+':'+hint,lambda n=name,h=hint:file_terminal(n,h))
                for name,sequence in SEQUENCES.items():case('transition:'+name,lambda n=name,s=sequence:suite.transition(n,s))
                case('stop-play-generation',suite.stop_race)
                for mode in ('drop','stall','error'):case('network:'+mode,lambda m=mode:suite.fault(m))
                for mode in ('redirect','jitter'):case('network:'+mode,lambda m=mode:suite.file('lc-48000-stereo','aac',mode=m))
                case('websocket-format-reconnect',suite.websocket_format)
                b.stop();suite.observe(10,'idle:final',interval=1)
                case('settled-heap',lambda:dict(result=check_recovery_heap(initial_heap,b.health_samples[-3:]),initial=initial_heap,final=b.health_samples[-3:]))
                case('lifetime-health',lambda:check_health(b.health_samples))
                save('server.json',server.events)
        finally:
            print('RESTORE original production application',flush=True)
            if board.info()['app_elf_sha256']!=baseline['app_elf_sha256']:install(RESTORE)
            board.stop()
            if original['audio']:
                with board.websocket() as ws:
                    ws.send('play='+str(current));deadline=time.perf_counter()+5
                    while time.perf_counter()<deadline:
                        if json.loads(ws.recv(timeout=5)).get('current')==current:break
            restored=HealthBoard(board.origin);states=[]
            for _ in range(5):time.sleep(4);states.append(restored.status())
            same_station=board.json('/api/native/status')['station']==station if original['audio'] else True
            require(same_station and all(s['audio']==original['audio'] for s in states[-3:]),'Playback restore failed')
            require(not original['audio'] or all(s['pcm_sample_rate']>0 for s in states[-3:]),'No decoded playback after restoration')
            identity=board.info();require(identity['app_elf_sha256']==baseline['app_elf_sha256'],'Image restore failed')
            save('restoration.json',dict(identity=identity,persistence=verify_snapshot(board,before),same_station=same_station,states=states,health=check_health(restored.health_samples)))
            report.save();print('Original production, settings and station restored',flush=True)
sys.exit(report.exit_code())
