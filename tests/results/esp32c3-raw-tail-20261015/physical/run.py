"""Same verified FLAC bytes over local HTTP, with explicitly unpaced delivery."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Report,require,sha,fixtures,check_recovery_heap
from ota import image_info,snapshot,verify_snapshot
from production_health import HealthBoard,check_health,check_decoder_health
from quiet_acceptance import idle_checkpoint,idle_recovery
from run import Suite,Capture
from audio_test_server.server import Server
from trace_transport import TransportTrace
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
mode=sys.argv[1];require(mode in ('control','pauses'),'Unknown control')
base=Path('.build/c3-raw-tail-20261015');trial=sys.argv[2];require(trial in ('control1','pauses','vorbis','opus'),'Invalid trial');policy='off';out=base/'physical'/trial
require(not out.exists(),'Preserve earlier evidence');out.mkdir(parents=True)
refs=Path('.build/c3-input-tail-quiet-20261015/public-references')
kind=trial if trial in ('vorbis','opus') else 'flac'
reference=json.loads((refs/'references.json').read_text())['sources'][kind]
data=(refs/'media'/(kind+('.flac' if kind=='flac' else '.ogg'))).read_bytes();require(sha(data)==reference['sha256'],'Reference bytes changed')
specs=fixtures();name='public-'+kind+'-reference'
specs[name]=dict(reference['spec'],data=data,sha256=sha(data),mime='audio/flac' if kind=='flac' else 'audio/ogg',profile=kind)
schedule=[(2097152,.1),(3670016,.25),(5242880,.5)] if mode=='pauses' else []
b=HealthBoard('http://192.168.100.4');identity=b.info()
folder='esp32c3-idf61-raw-tail-diagnostic'
image=image_info((Path('firmware/development')/folder/'app.bin').read_bytes())
require(identity['app_elf_sha256']==image['app_elf_sha256'],'Wrong diagnostic image')
before=snapshot(b);r=Report(out/'report.json',identity)
r.data.update(image=image,reference=reference,runner_sha256=sha(Path(__file__).read_bytes()),
    idle={},actions=[],unpaced_files=True,pacing_ratio=None,send_buffer_requested=4096,
    delivery_pause_schedule=[dict(after_bytes=n,seconds=s) for n,s in schedule],
    scope='Unpaced local HTTP transfer of a public codec reference; FLAC controlled host pauses. Not public HTTPS or acoustic qualification.')
suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),out)
def case(label,fn):
    start=time.perf_counter()
    try:r.case(label,fn)
    finally:
        r.data['actions'].append(dict(name=label,started_at=start,ended_at=time.perf_counter()))
        (out/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n');r.save()
with (out/'request-phases.jsonl').open('x') as log,TransportTrace('192.168.100.4',log,capture_socket_ports=True):
    with Server('192.168.100.253',8772,specs,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0,
                delivery_pauses=schedule,send_buffer_bytes=4096,tcp_nodelay=policy=='on') as server:
        try:
            case('initial-idle',lambda:idle_checkpoint(b,suite,r.data,'initial'))
            case(kind+':'+mode,lambda:suite.file(name,kind))
            r.data['server_events']=server.events;r.data['file_failure_snapshots']=suite.file_failure_snapshots;r.save()
            def delivery():
                require(len(server.events)==1,'Missing unique transfer')
                event=server.events[0]
                require(event['fixture']==name and event['complete'] and event['sent']==len(data),'Incomplete body')
                require(event['pacing_ratio'] is None,'Unexpected pacing')
                require(event['tcp_nodelay_requested']==(policy=='on') and event['tcp_nodelay_actual']==(policy=='on'),'TCP policy not applied')
                pauses=event.get('pauses',[]);require(len(pauses)==len(schedule),'Missing pause')
                for row,(offset,seconds) in zip(pauses,schedule):
                    require(row['after_bytes']==offset and row['requested_seconds']==seconds and row['completed'], 'Incomplete pause')
                    require(seconds-.005<=row['elapsed_seconds']<=seconds+.05,'Pause timing outside tolerance')
                return dict(bytes=event['sent'],pauses=pauses)
            case('delivery',delivery)
            def capacity():
                batch=next(v for v in suite.observations if v['case']==name)
                paired=[h for h in b.health_samples if batch['started_at']<=h['at']<=batch['ended_at']]
                require(len(paired)==len(batch['samples']),'Unpaired queue observations')
                residents=sorted(set(h['input_queue']['resident'] for sample,h in zip(batch['samples'],paired) if sample['seconds']>=2))
                require(residents==[8 if kind=='flac' else 4],'Unexpected steady input capacity')
                return dict(steady_residents=residents)
            case('capacity',capacity)
            r.data['web_memory']=b.json('/api/native/web-memory');r.save()
            case('final-idle',lambda:idle_checkpoint(b,suite,r.data,'final'))
            case('recovery',lambda:idle_recovery(r.data,'final'))
        finally:
            case('settings',lambda:(b.stop(),verify_snapshot(b,before))[1])
            case('health',lambda:check_health(b.health_samples))
            case('decoder',lambda:check_decoder_health(b.health_samples))
raise SystemExit(r.exit_code())
