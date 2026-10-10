"""Test the exact quiet image through format, heap and lifetime-fault evidence.

No CPU, DMA or analog continuity claim is inferred. The caller owns any OTA
installation/restoration. Public audio and private board settings are not saved.
"""
import argparse
import json
import statistics
import time
from pathlib import Path
from urllib.parse import urlsplit

from common import Report, check_playback, check_recovery_heap, fixtures, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, check_health
from public_streams import DEFAULT_MANIFEST, probe, public_url
from run import Capture, Suite
from trace_transport import TransportTrace
from audio_test_server.server import Server
from audio_test_server.fixtures import SEQUENCES


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, default=8772)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--suite', choices=('http','public','transitions','network','websocket'), action='append', required=True)
    p.add_argument('--aac-reference-command', type=Path)
    p.add_argument('--seconds', type=int, default=60)
    a=p.parse_args()
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
        scope='Quiet format/EOF, sampled heap, allocation/watchdog counters and reboot detection; no DMA/PCM/acoustic claim',
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
            save_health();report.save()

    def checkpoint(name):
        b.stop();suite.observe(12,'idle:'+name,interval=1)
        samples=b.health_samples[-3:]
        report.data['idle'][name]=samples
        return dict(samples=samples)

    def recovery(name):
        check_recovery_heap(report.data['idle']['initial'],report.data['idle'][name])
        return dict(compared_with='initial',free_loss_tolerance=2048,largest_loss_tolerance=4096)

    def public_case(name,url,command):
        b.stop()
        reference=probe(public_url(url),'ffprobe',command)
        report.data.setdefault('references',{})[name]=reference;report.save()
        started=time.perf_counter()
        try:
            b.play(url)
            states=suite.observe(a.seconds,'https:'+name)
            first=next((s['seconds'] for s in states if s['audio']),None)
            require(first is not None and first<=15, 'No full PCM playback within 15 seconds')
            playback=check_playback(states,reference['spec'],minimum=int((a.seconds-15)*.6),warmup=15)
            require(max(s['request_ms'] for s in states)<2000, 'WebUI response exceeded 2 seconds')
            steady=[r for r in b.health_samples if r['at']>=started+15]
            require(len(steady)>=10, 'Missing steady-state health evidence')
            require(min(r['heap'] for r in steady)>=16384 and min(r['largest'] for r in steady)>=8192,
                    'In-playback memory below existing budget')
            for key,tolerance in (('heap',2048),('largest',4096)):
                require(statistics.median(r[key] for r in steady[:3])-
                        statistics.median(r[key] for r in steady[-3:])<=tolerance,
                        'Progressive '+key+' loss in public playback')
            return dict(reference=reference,playback=playback,health=check_health(steady),
                first_pcm_seconds=first,max_status_and_health_ms=max(s['request_ms'] for s in states))
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
                            public=json.loads(DEFAULT_MANIFEST.read_text())
                            report.data['public_manifest_sha256']=sha(DEFAULT_MANIFEST.read_bytes())
                            report.data['public_urls']=public['streams']
                            for name,url in public['streams'].items():
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
                save_health();report.save()
    return report.exit_code()


if __name__=='__main__':
    raise SystemExit(main())
