"""One continuous owner capture across switching, EOF, TLS and quiet idle."""
import argparse
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, Report, check_cpu, check_playback, check_recovery_heap, fixtures, matches, require, sha
from diagnostic import DiagnosticCapture
from heap_fragment import analyze
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from tls_records import capture_record_observation, record_evidence
from trace_transport import TransportTrace
from audio_test_server.server import Server
from audio_test_server.tls_records import RecordServer, OBSERVATION_TAIL_SECONDS

p=argparse.ArgumentParser(description=__doc__)
for arg in ('board','host','serial-port'):p.add_argument('--'+arg,required=True)
for arg in ('firmware','ca','cert','key','output'):p.add_argument('--'+arg,type=Path,required=True)
a=p.parse_args()
require(not a.output.exists(),'Preserve previous trial')
cfg=a.firmware.with_name('sdkconfig').read_text()
manifest=json.loads(a.firmware.with_name('manifest.json').read_text())
require(manifest.get('laboratory_only') is True and manifest.get('extra_trust_ca_sha256')==sha(a.ca.read_bytes()),'Wrong laboratory trust identity')
for key in ('YORADIO_HEAP_FRAGMENT_PROBE','HEAP_USE_HOOKS','MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL'):
    require('CONFIG_'+key+'=y' in cfg,'Required diagnostic setting missing: '+key)
for key in ('YORADIO_DEEP_SLEEP_CLOCK','YORADIO_QEMU','MBEDTLS_ALLOW_WEAK_CERTIFICATE_VERIFICATION'):
    require('CONFIG_'+key+'=y' not in cfg,'Unsupported mode: '+key)
board=Board(a.board)
identity=board.info()
require(identity['app_elf_sha256']==image_info(a.firmware.read_bytes())['app_elf_sha256'],'Wrong installed application')
before=snapshot(board)
specs=fixtures()
names=('flac-level8','he-48000-stereo','hev2-44100-stereo')
report=Report(a.output/'report.json',identity)
report.data.update(controller_sha256=sha(Path(__file__).read_bytes()),
    firmware_sha256=sha(a.firmware.read_bytes()),sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
    test_ca_sha256=sha(a.ca.read_bytes()),leaf_certificate_sha256=sha(a.cert.read_bytes()),
    fixture_hashes={n:specs[n]['sha256'] for n in names},
    note='Continuous serial owner capture changes timing; diagnostic ownership evidence, not production CPU qualification.')
capture=DiagnosticCapture(a.serial_port)
suite=Suite(board,'http://'+a.host+':8770',specs,capture,a.output,cpu_budget=None)
checkpoints={}
report.data['idle_checkpoints']=checkpoints
actions=[]
report.data['actions']=actions

def case(name,action):
    started=time.monotonic()
    try:report.case(name,action)
    finally:
        actions.append(dict(name=name,started_at=started,ended_at=time.monotonic()))
        (a.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        report.save()

def idle(name):
    checkpoints[name]=suite.idle_heap()
    return dict(samples=checkpoints[name])

def arm():
    idle('initial')
    result=analyze(capture.rows)
    require(len(result['snapshots'])>=2,'Need two complete initial owner snapshots')
    return dict(samples=checkpoints['initial'],snapshots=len(result['snapshots']),
                first_sequence=result['snapshots'][0]['seq'])

def records(server):
    name='hev2-44100-stereo'
    board.stop();time.sleep(.8)
    offset=len(server.events);started=time.monotonic()
    try:
        board.play('https://'+a.host+':8772/grow/'+name,'aac')
        samples=suite.observe(75,'tls-record:grow',interval=.1)
        observed=capture_record_observation(server.events[offset:])
        report.data['record_observation']=observed
        playback=check_playback(samples,specs[name],warmup=5)
        evidence=record_evidence(observed['events'],'grow')
        require(all(e.get('pacing_ratio')==1.0 for e in observed['events']),'Wrong pacing')
        first_pcm=next(suite.observations[-1]['started_at']+s['seconds'] for s in samples if matches(s,specs[name]))
        require(first_pcm<evidence['first_large_at'],'Large record preceded full PCM playback')
        no_runtime_faults(capture.since(started))
        cpu=check_cpu(capture.since(started),max_busy=None,start=started,end=time.monotonic())
        require(max(s['request_ms'] for s in samples)<2000,'WebUI exceeded two seconds')
        return dict(**playback,**evidence,**cpu,first_full_pcm_seconds=first_pcm-started)
    finally:board.stop()

def quiet():
    board.stop()
    require(not board.status()['audio'],'Stop required for passive idle')
    started=time.monotonic();deadline=started+60
    while time.monotonic()<deadline:time.sleep(min(5,max(0,deadline-time.monotonic())))
    window=dict(started_at=started,ended_at=time.monotonic(),http_polls=0)
    report.data['quiet_window']=window
    return window

def recovery():
    first=json.loads((a.output/'switching.json').read_text())['checkpoints'][0]
    failures=[]
    for name in ('before-records','after-records','after-quiet'):
        try:check_recovery_heap(first,checkpoints[name])
        except AssertionError as error:failures.append(dict(checkpoint=name,reason=str(error)))
    report.data['cross_phase_failures']=failures
    require(not failures,'Cross-stage contiguous-memory recovery failed')
    return dict(baseline='first-switch-cycle',checked=3)

def owners():
    result=analyze(capture.rows)
    (a.output/'owners.json').write_text(json.dumps(result,indent=2)+'\n')
    return dict(snapshots=len(result['snapshots']),peak_live=max(s['peak'] for s in result['snapshots']),
                final_live=result['snapshots'][-1]['live'])

with (a.output/'request-phases.jsonl').open('x',encoding='utf-8') as log:
    with TransportTrace(urlsplit(a.board).hostname,log):
        try:
            case('initial-idle-owner-capture',arm)
            require(report.data['cases'][-1]['result']=='PASS','Initial owner capture unavailable')
            with Server(a.host,8770,specs,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0) as http:
                case('switching-and-heap',lambda:suite.switching(names,3))
                report.data['http_events']=http.events
            with Server(a.host,8771,specs,a.cert,a.key,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0) as https:
                for name in ('flac-level8','hev2-44100-stereo'):
                    for hint in ('auto',specs[name]['codec']):
                        case('eof:https:'+name+':'+hint,lambda n=name,h=hint:suite.eof(n,h,'https://'+a.host+':8771'))
                report.data['https_events']=https.events
            case('idle-before-records',lambda:idle('before-records'))
            with RecordServer(a.host,8772,{'hev2-44100-stereo':specs['hev2-44100-stereo']},a.cert,a.key,
                              seconds=75+OBSERVATION_TAIL_SECONDS,grow_seconds=30,pacing_ratio=1.0) as server:
                case('tls-record:grow',lambda:records(server))
                report.data['record_server_events']=server.events
            case('idle-after-records',lambda:idle('after-records'))
            case('quiet-without-http',quiet)
            case('idle-after-quiet',lambda:idle('after-quiet'))
            case('cross-stage-recovery',recovery)
        finally:
            try:
                case('runtime',lambda:no_runtime_faults(capture.rows))
                def restore():
                    board.stop()
                    return dict(stopped=True,**verify_snapshot(board,before))
                case('stop-and-settings',restore)
            finally:
                capture.close()
                (a.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
                case('owners-complete',owners)
                report.save()
raise SystemExit(report.exit_code())
