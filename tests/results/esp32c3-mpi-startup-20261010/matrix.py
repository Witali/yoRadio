"""All baseline HTTPS fixtures, EOF, and repeated full-rate AAC/FLAC switching."""
import argparse,json,sys,time
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,Report,check_recovery_heap,fixtures,require,sha
from diagnostic import DiagnosticCapture
from ota import image_info,snapshot,verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from trace_transport import TransportTrace
from audio_test_server.server import Server
from audio_test_server.fixtures import SEQUENCES
p=argparse.ArgumentParser(description=__doc__)
for arg in ('board','host','serial-port'):p.add_argument('--'+arg,required=True)
for arg in ('firmware','ca','cert','key','output'):p.add_argument('--'+arg,type=Path,required=True)
a=p.parse_args();require(not a.output.exists(),'Preserve evidence')
m=json.loads(a.firmware.with_name('manifest.json').read_text());require(m['early_mpi_lock'] and m['laboratory_only'],'Wrong firmware')
require(m['extra_trust_ca_sha256']==sha(a.ca.read_bytes()),'Wrong trust')
board=Board(a.board);identity=board.info();require(identity['app_elf_sha256']==image_info(a.firmware.read_bytes())['app_elf_sha256'],'Wrong app')
before=snapshot(board);specs=fixtures();names=[n for n in specs if n not in SEQUENCES]
report=Report(a.output/'report.json',identity)
report.data.update(firmware_sha256=sha(a.firmware.read_bytes()),sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
    controller_sha256=sha(Path(__file__).read_bytes()),fixture_hashes={n:s['sha256'] for n,s in specs.items()},
    test_ca_sha256=sha(a.ca.read_bytes()),leaf_certificate_sha256=sha(a.cert.read_bytes()),pacing_ratio=1.0)
capture=DiagnosticCapture(a.serial_port);suite=Suite(board,'https://'+a.host+':8771',specs,capture,a.output,cpu_budget=None)
idle={};actions=[];report.data.update(idle=idle,actions=actions)
def case(name,action):
    started=time.perf_counter()
    try:report.case(name,action)
    finally:
        actions.append(dict(name=name,started_at=started,ended_at=time.perf_counter()))
        (a.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n');report.save()
def checkpoint(name):
    idle[name]=suite.idle_heap();return dict(samples=idle[name])
with (a.output/'request-phases.jsonl').open('x',encoding='utf-8') as log:
    with TransportTrace(urlsplit(a.board).hostname,log,capture_socket_ports=True):
        try:
            case('initial-idle',lambda:checkpoint('initial'))
            with Server(a.host,8771,specs,a.cert,a.key,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0) as server:
                for name in names:
                    for hint in ('auto',specs[name]['codec']):case('https:'+name+':'+hint,lambda n=name,h=hint:suite.file(n,h))
                case('after-matrix-idle',lambda:checkpoint('matrix'))
                case('matrix-recovery',lambda:check_recovery_heap(idle['initial'],idle['matrix']))
                case('https-switching-and-heap',lambda:suite.switching(('flac-level8','he-48000-stereo','hev2-44100-stereo'),3))
                case('after-switch-idle',lambda:checkpoint('switch'))
                case('switch-recovery',lambda:check_recovery_heap(idle['initial'],idle['switch']))
                for name,sequence in SEQUENCES.items():case('https-transition:'+name,lambda n=name,s=sequence:suite.transition(n,s))
                case('after-transitions-idle',lambda:checkpoint('transitions'))
                case('transition-recovery',lambda:check_recovery_heap(idle['initial'],idle['transitions']))
                report.data['server_events']=server.events
        finally:
            try:case('stop-and-settings',lambda:(board.stop(),verify_snapshot(board,before))[1])
            finally:
                capture.close();(a.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
                case('runtime-after-capture-close',lambda:no_runtime_faults(capture.rows));report.save()
raise SystemExit(report.exit_code())
