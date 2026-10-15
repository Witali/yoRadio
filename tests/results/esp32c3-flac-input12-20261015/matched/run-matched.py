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
base=Path('.build/c3-flac-input12-20261015');out=base/'matched'/sys.argv[2]/mode
require(not out.exists(),'Preserve earlier evidence');out.mkdir(parents=True)
refs=Path('.build/c3-input-tail-quiet-20261015/public-references')
reference=json.loads((refs/'references.json').read_text())['sources']['flac']
data=(refs/'media/flac.flac').read_bytes();require(sha(data)==reference['sha256'],'Reference bytes changed')
specs=fixtures();name='public-flac-reference'
specs[name]=dict(reference['spec'],data=data,sha256=sha(data),mime='audio/flac',profile='flac')
schedule=[(2097152,.1),(3670016,.25),(5242880,.5)] if mode=='pauses' else []
b=HealthBoard('http://192.168.100.4');identity=b.info()
artifact={'slots8':'esp32c3-idf61-flac-output-diagnostic','slots11':'esp32c3-idf61-flac-input12-diagnostic'}[sys.argv[2]]
image=image_info((Path('firmware/development')/artifact/'app.bin').read_bytes())
require(identity['app_elf_sha256']==image['app_elf_sha256'],'Wrong diagnostic image')
before=snapshot(b);require(before['settings']['getsystem']['abuff']==14,'Expected temporary 14-block target');r=Report(out/'report.json',identity)
r.data.update(image=image,reference=reference,runner_sha256=sha(Path(__file__).read_bytes()),
    idle={},actions=[],unpaced_files=True,pacing_ratio=None,send_buffer_requested=4096,
    delivery_pause_schedule=[dict(after_bytes=n,seconds=s) for n,s in schedule],
    scope='Unpaced local HTTP transfer of the public FLAC reference; controlled host pauses. Not public HTTPS or acoustic qualification.')
suite=Suite(b,'http://192.168.100.253:8772',specs,Capture(None),out)
def case(label,fn):
    start=time.perf_counter()
    try:r.case(label,fn)
    finally:
        r.data['actions'].append(dict(name=label,started_at=start,ended_at=time.perf_counter()))
        (out/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n');r.save()
with (out/'request-phases.jsonl').open('x') as log,TransportTrace('192.168.100.4',log,capture_socket_ports=True):
    with Server('192.168.100.253',8772,specs,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0,
                delivery_pauses=schedule,send_buffer_bytes=4096) as server:
        try:
            case('initial-idle',lambda:idle_checkpoint(b,suite,r.data,'initial'))
            case('flac:'+mode,lambda:suite.file(name,'flac'))
            r.data['server_events']=server.events;r.data['file_failure_snapshots']=suite.file_failure_snapshots;r.save()
            def delivery():
                require(len(server.events)==1,'Missing unique transfer')
                event=server.events[0]
                require(event['fixture']==name and event['complete'] and event['sent']==len(data),'Incomplete body')
                require(event['pacing_ratio'] is None,'Unexpected pacing')
                pauses=event.get('pauses',[]);require(len(pauses)==len(schedule),'Missing pause')
                for row,(offset,seconds) in zip(pauses,schedule):
                    require(row['after_bytes']==offset and row['requested_seconds']==seconds and row['completed'], 'Incomplete pause')
                    require(seconds-.005<=row['elapsed_seconds']<=seconds+.05,'Pause timing outside tolerance')
                return dict(bytes=event['sent'],pauses=pauses)
            case('delivery',delivery)
            def capacity():
                expected={'slots8':8,'slots11':11}[sys.argv[2]]
                residents=[h['input_queue']['resident'] for h in b.health_samples]
                require(max(residents)==expected,'Requested resident capacity not observed')
                return dict(requested_blocks=14,expected_resident=expected,observed_max=max(residents))
            case('capacity',capacity)
            case('final-idle',lambda:idle_checkpoint(b,suite,r.data,'final'))
            case('recovery',lambda:idle_recovery(r.data,'final'))
        finally:
            case('settings',lambda:(b.stop(),verify_snapshot(b,before))[1])
            case('health',lambda:check_health(b.health_samples))
            case('decoder',lambda:check_decoder_health(b.health_samples))
raise SystemExit(r.exit_code())
