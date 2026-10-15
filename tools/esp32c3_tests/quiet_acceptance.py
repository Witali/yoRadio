"""Test the exact quiet image through format, heap and lifetime-fault evidence.

Public playback checks sampled output counters; no CPU or analog continuity
claim is inferred. The caller owns any OTA
installation/restoration. Public audio and private board settings are not saved.
"""
import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlsplit

from common import Blocked, Report, check_playback, check_recovery_heap, fixtures, matches, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, capture_failure_snapshot, check_health, check_decoder_health, output_window
from public_streams import DEFAULT_MANIFEST, probe, public_url
from run import Capture, Suite
from trace_transport import TransportTrace
from sustained_output import check_memory, check_output
from audio_test_server.server import Server
from audio_test_server.fixtures import SEQUENCES


def idle_checkpoint(board, suite, data, name):
    """Only a complete, stopped observation may become a recovery baseline."""
    first = len(board.health_samples)
    # A failed repeated checkpoint must not leave an older successful baseline.
    data['idle'].pop(name, None)
    try:
        board.stop()
        states = suite.observe(12, 'idle:' + name, interval=1)
        samples = board.health_samples[first:]
        require(len(states) >= 3 and all(s.get('audio') is False for s in states[-3:]),
                'Missing confirmed idle state')
        require(len(samples) >= 3, 'Missing fresh idle health samples')
        data['idle'][name] = samples[-3:]
        return dict(samples=samples[-3:])
    except Exception:
        partial = list(board.health_samples[first:])
        data.setdefault('idle_failures', {})[name] = dict(
            partial_health=partial, snapshot=capture_failure_snapshot(board))
        raise


def idle_recovery(data, name):
    missing = [key for key in ('initial', name) if key not in data['idle']]
    if missing:
        raise Blocked('Incomplete idle checkpoint: ' + ', '.join(missing))
    check_recovery_heap(data['idle']['initial'], data['idle'][name])
    return dict(compared_with='initial', free_loss_tolerance=2048, largest_loss_tolerance=4096)


def public_window_checks(states, steady, spec, seconds, *, enforce_legacy_floor=False):
    """Retain independent failures; memory rejection must not hide output faults."""
    checks = {}

    def format_check():
        require(states and states[-1]['seconds'] >= seconds-1,
                'Incomplete playback observation')
        first = next((s['seconds'] for s in states if matches(s, spec)), None)
        require(first is not None and first <= 15, 'No matching decoded format within 15 seconds')
        return dict(first_decoded_format_seconds=first,
                    **check_playback(states, spec, minimum=int((seconds-15)*.6), warmup=15))

    def response_check():
        require(states, 'Missing status evidence')
        maximum = max(s['request_ms'] for s in states)
        require(maximum < 2000, 'WebUI response exceeded 2 seconds')
        return dict(max_status_and_health_ms=maximum)

    def memory_check():
        require(len(steady) >= 10, 'Missing steady-state health evidence')
        return check_memory(steady, enforce_legacy_floor=enforce_legacy_floor)

    # Measurement is separate from acceptance, so nonzero counters remain visible.
    for name, fn in (('format', format_check), ('response', response_check),
                     ('memory', memory_check), ('decoder', lambda: check_decoder_health(steady)),
                     ('output_measurement', lambda: output_window(steady)),
                     ('output', lambda: check_output(steady))):
        try:
            checks[name] = dict(result='PASS', evidence=fn())
        except Exception as error:
            checks[name] = dict(result='FAIL', reason=str(error), exception_type=type(error).__name__)
    return checks


def main():
    public=json.loads(DEFAULT_MANIFEST.read_text())
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, default=8772)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--suite', choices=('http','public','transitions','network','websocket'), action='append', required=True)
    p.add_argument('--aac-reference-command', type=Path)
    p.add_argument('--seconds', type=int, default=60)
    p.add_argument('--public-case', choices=tuple(public['streams']), action='append',
                   help='Select public sources for a focused investigation; default tests all')
    p.add_argument('--enforce-legacy-heap-floor', action='store_true',
                   help='Reproduce the historical 16/8 KiB gate; otherwise record it as diagnostic')
    a=p.parse_args()
    public_names=a.public_case or list(public['streams'])
    require(not a.public_case or 'public' in a.suite, '--public-case requires the public suite')
    require(len(set(public_names))==len(public_names), 'Duplicate public source selection')
    require(45<=a.seconds<=600, 'Use a bounded 45..600 second public test')
    require(not a.output.exists(), 'Preserve previous evidence')
    config=a.firmware.with_name('sdkconfig').read_text()
    for key in ('CONFIG_ESP_CONSOLE_NONE=y','CONFIG_LOG_MAXIMUM_LEVEL=0','CONFIG_ESP_TASK_WDT_EN=y'):
        require(key in config, 'Required quiet/watchdog configuration missing')
    for key in ('CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y','CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y',
                'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y'):
        require(key not in config, 'Unexpected profiling, sleep or laboratory trust')
    b=HealthBoard(a.board);identity=b.info();image=image_info(a.firmware.read_bytes())
    require(identity['app_elf_sha256']==image['app_elf_sha256'], 'Wrong installed image')
    b.status();before=snapshot(b);specs=fixtures();capture=Capture(None)
    report=Report(a.output/'report.json',identity)
    report.data.update(image=image, sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
        fixture_hashes={k:v['sha256'] for k,v in specs.items()}, suites=a.suite,
        scope='Quiet format/EOF, heap, allocation/watchdog and reboot detection; public cases also check decoder faults and sampled output counters. No PCM/acoustic claim',
        public_memory_policy='legacy-absolute-floor' if a.enforce_legacy_heap_floor else 'faults-and-recovery',
        health_http_requests_per_status=1, serial_capture_enabled=False,
        public_seconds=a.seconds, idle={}, actions=[])
    suite=Suite(b,f'http://{a.host}:{a.port}',specs,capture,a.output,cpu_budget=None)

    def save_health():
        (a.output/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n')

    def case(name, fn):
        start=time.perf_counter()
        try:report.case(name,fn)
        finally:
            report.data['actions'].append(dict(name=name,started_at=start,ended_at=time.perf_counter()))
            report.data['file_failure_snapshots'] = suite.file_failure_snapshots
            save_health();report.save()

    def checkpoint(name):
        return idle_checkpoint(b, suite, report.data, name)

    def recovery(name):
        return idle_recovery(report.data, name)

    def public_case(name,url,command):
        b.stop()
        reference=probe(public_url(url),'ffprobe',command)
        report.data.setdefault('references',{})[name]=reference;report.save()
        started=time.perf_counter()
        try:
            b.play(url)
            states=suite.observe(a.seconds,'https:'+name)
            ended=time.perf_counter()
            steady=[r for r in b.health_samples if started+15<=r['at']<=ended]
            checks=public_window_checks(states,steady,reference['spec'],a.seconds,
                enforce_legacy_floor=a.enforce_legacy_heap_floor)
            report.data.setdefault('public_checks',{})[name]=dict(
                started_at=started,ended_at=ended,warmup_seconds=15,
                health_samples=len(steady),checks=checks)
            report.save()
            failures=[key+': '+row['reason'] for key,row in checks.items() if row['result']!='PASS']
            require(not failures, '; '.join(failures))
            return dict(reference=reference,playback=checks['format']['evidence'],
                health=checks['memory']['evidence'],output_window=checks['output']['evidence'],
                first_decoded_format_seconds=checks['format']['evidence']['first_decoded_format_seconds'],
                **checks['response']['evidence'])
        except Exception:
            report.data.setdefault('failure_snapshots',{})[name]=capture_failure_snapshot(b)
            report.save()
            raise
        finally:b.stop()

    with (a.output/'request-phases.jsonl').open('x',encoding='utf-8') as log:
        with TransportTrace(urlsplit(a.board).hostname,log,capture_socket_ports=True):
            try:
                case('initial-idle',lambda:checkpoint('initial'))
                with Server(a.host,a.port,specs,unpaced_files=True,delivery_stats=True,pacing_ratio=1.0) as server:
                    for group in a.suite:
                        if group=='public':
                            require(a.aac_reference_command is not None, 'Use independent AAC reference for public sources')
                            command=json.loads(a.aac_reference_command.read_text())
                            report.data['public_manifest_sha256']=sha(DEFAULT_MANIFEST.read_bytes())
                            report.data['public_urls']={n:public['streams'][n] for n in public_names}
                            for name,url in report.data['public_urls'].items():
                                case('https:'+name,lambda n=name,u=url:public_case(n,u,command))
                        elif group=='http':
                            for name,spec in specs.items():
                                if name in SEQUENCES:continue
                                for hint in ('auto',spec['codec']):
                                    case('http:'+name+':'+hint,lambda n=name,h=hint:suite.file(n,h))
                        elif group=='transitions':
                            for name,sequence in SEQUENCES.items():
                                case('transition:'+name,lambda n=name,s=sequence:suite.transition(n,s))
                            case('stop-play-generation',suite.stop_race)
                        elif group=='network':
                            for mode in ('drop','stall','error'):
                                case('network:'+mode,lambda m=mode:suite.fault(m))
                            for mode in ('redirect','jitter'):
                                case('network:'+mode,lambda m=mode:suite.file('lc-48000-stereo','aac',mode=m))
                        elif group=='websocket':case('websocket-format-and-reconnect',suite.websocket_format)
                        case('idle:'+group,lambda g=group:checkpoint(g))
                        case('recovery:'+group,lambda g=group:recovery(g))
                    report.data['server_events']=server.events
            finally:
                case('stop-and-settings',lambda:(b.stop(),verify_snapshot(b,before))[1])
                case('lifetime-health',lambda:check_health(b.health_samples))
                case('all-decoder-health',lambda:check_decoder_health(b.health_samples))
                save_health();report.save()
    return report.exit_code()


if __name__=='__main__':
    raise SystemExit(main())
