"""Continuous capture of heavy FLAC, optionally followed by full-rate HE-AACv2."""
import argparse
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, Report, check_recovery_heap, fixtures, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info
from public_streams import no_runtime_faults
from run import Suite
from trace_transport import TransportTrace
from audio_test_server.server import Server

PAUSES = tuple((3000000*(i+1), (.05,.10,.20)[i%3]) for i in range(6))

p = argparse.ArgumentParser(description=__doc__)
for arg in ('board', 'host', 'serial-port'): p.add_argument('--'+arg, required=True)
for arg in ('firmware', 'ca', 'cert', 'key', 'output'): p.add_argument('--'+arg, type=Path, required=True)
p.add_argument('--aac', action='store_true')
p.add_argument('--seconds', type=int, default=180)
a = p.parse_args()
require(not a.output.exists(), 'Preserve evidence')
require(30 <= a.seconds <= 600, 'Bounded sustained test required')
manifest = json.loads(a.firmware.with_name('manifest.json').read_text())
require(manifest['clock_mode'] == 'integer' and manifest['laboratory_only'], 'Wrong firmware controls')
require(manifest['extra_trust_ca_sha256'] == sha(a.ca.read_bytes()), 'Wrong trust')
board = Board(a.board)
identity = board.info()
require(identity['app_elf_sha256'] == image_info(a.firmware.read_bytes())['app_elf_sha256'], 'Wrong application')
specs = fixtures(Path('.build/c3-reserve-soak-20261008/fixtures/manifest.json'))
name = 'stress-flac-48000-2ch-16bit-610s'
report = Report(a.output/'report.json', identity)
report.data.update(firmware_sha256=sha(a.firmware.read_bytes()),
    sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
    source_sha256=sha(Path(__file__).read_bytes()), fixture_sha256={n: specs[n]['sha256'] for n in (name, 'hev2-44100-stereo')})
capture = DiagnosticCapture(a.serial_port)
suite = Suite(board, 'https://'+a.host+':8771', specs, capture, a.output, cpu_budget=None)
actions, idle = [], {}
report.data.update(actions=actions, idle=idle)

def case(label, action):
    start = time.monotonic()
    try: report.case(label, action)
    finally:
        actions.append(dict(name=label, started_at=start, ended_at=time.monotonic()))
        (a.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
        report.save()
        print(label, report.data['cases'][-1]['result'], flush=True)

def checkpoint(label):
    idle[label] = suite.idle_heap()
    return dict(samples=idle[label])


def verify_pauses(events):
    selected = [e for e in events if e.get('fixture') == name and e.get('mode') == 'file']
    require(len(selected) == 1, 'Exactly one FLAC response required')
    event = selected[0]
    expected = [dict(after_bytes=n, seconds=s) for n,s in PAUSES]
    require(event.get('pause_schedule') == expected, 'Wrong pause schedule')
    rows = event.get('pauses', [])
    require(len(rows) == len(PAUSES), 'Not all pauses executed')
    require(event.get('send_buffer_requested') == 4096 and 0 < event.get('send_buffer_actual', 0) <= 8192, 'Unexpected host send buffer')
    require(event.get('pacing_ratio') is None, 'Use unpaced catch-up')
    for row, (offset, seconds) in zip(rows, PAUSES):
        require(row['after_bytes'] == offset and row['requested_seconds'] == seconds, 'Pause position changed')
        require(row['completed'] and seconds-.002 <= row['elapsed_seconds'] <= seconds+.050, 'Interrupted or mistimed pause')
    require(event.get('delivery', {}).get('finished') and not event['delivery']['dropped_windows'], 'Delivery statistics incomplete')
    return dict(pauses=rows, send_buffer_actual=event['send_buffer_actual'],
        scope='Host API writes only; in-flight and receiver data can mask a pause')

with (a.output/'request-phases.jsonl').open('x', encoding='utf-8') as log:
    with TransportTrace(urlsplit(a.board).hostname, log, capture_socket_ports=True):
        try:
            case('idle-before', lambda: checkpoint('before'))
            with Server(a.host, 8771, specs, a.cert, a.key, unpaced_files=True,
                        delivery_stats=True, pacing_ratio=1.0, delivery_pauses=PAUSES,
                        send_buffer_bytes=4096) as server:
                case('flac-https', lambda: suite.sustained(a.seconds, name, cpu=True, load=True))
                case('idle-after-flac', lambda: checkpoint('after-flac'))
                case('delivery-pause-schedule', lambda: verify_pauses(server.events))
                case('flac-heap-recovery', lambda: check_recovery_heap(idle['before'], idle['after-flac']))
                if a.aac:
                    case('hev2-https', lambda: suite.sustained(a.seconds, 'hev2-44100-stereo', cpu=True, load=True))
                    case('idle-after-aac', lambda: checkpoint('after-aac'))
                    case('aac-heap-recovery', lambda: check_recovery_heap(idle['before'], idle['after-aac']))
                report.data['server_events'] = server.events
        finally:
            try: case('stop', lambda: board.stop())
            finally:
                capture.close()
                (a.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')
                case('runtime-after-capture-close', lambda: no_runtime_faults(capture.rows))
                report.save()
raise SystemExit(report.exit_code())
