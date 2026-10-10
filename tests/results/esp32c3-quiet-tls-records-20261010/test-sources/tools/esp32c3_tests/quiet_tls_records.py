"""Bounded TLS record stress on quiet firmware with independent health gates.

The caller owns app-only OTA and exact restoration. Reuses the measured-record
server: ciphertext record lengths establish record sizes, while board status
and counters establish separate playback evidence. No acoustic continuity claim.
"""
import argparse
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

from aac_growth import transport_config
from common import Report, check_playback, check_recovery_heap, fixtures, matches, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, check_health, output_window
from run import Capture, Suite
from sustained_output import WARMUP_SECONDS, sustained_window, check_output, check_memory
from tls_records import capture_record_observation, record_evidence
from trace_transport import TransportTrace
from audio_test_server.tls_records import RecordServer, OBSERVATION_TAIL_SECONDS


def check_record_window(observation, mode, spec, first_pcm, end):
    events = observation['events']
    evidence = record_evidence(events, mode)
    event = events[0]
    require('error' not in event and 'ended_at' not in event,
            'TLS connection ended before the playback observation')
    require(event['fixture_sha256'] == spec['sha256'] and event['pacing_ratio'] == 1.0,
            'Wrong fixture or delivery pacing')
    writes = [w for w in event['writes'] if w['phase'].startswith('body-')]
    # At real-time pacing one large record can span several audio seconds.
    # Require continuing delivery near the end, allowing that record interval.
    interval = 16384 / event['target_audio_bytes_per_second']
    require(0 <= end-writes[-1]['at'] <= interval+2, 'TLS delivery stopped early')
    require(sum(w['plaintext_bytes'] for w in writes) == event['audio_bytes'],
            'Incomplete socket-write evidence')
    if mode == 'grow':
        require(first_pcm < evidence['first_large_at'] < end,
                'TLS record growth did not occur during full-rate playback')
    return dict(**evidence, audio_bytes=event['audio_bytes'],
                last_write_age_seconds=end-writes[-1]['at'])


def check_format(states, spec, seconds):
    first = next((s['seconds'] for s in states if matches(s,spec)), None)
    require(first is not None and first <= WARMUP_SECONDS, 'Full PCM format arrived after warmup')
    return dict(first_full_pcm_seconds=first,
                **check_playback(states,spec,minimum=int((seconds-WARMUP_SECONDS)*.6),
                                 warmup=WARMUP_SECONDS))


def check_response(states):
    maximum = max(s['request_ms'] for s in states)
    require(maximum < 2000, 'WebUI response exceeded two seconds')
    return dict(maximum_ms=maximum)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('board','host'):
        p.add_argument('--'+name,required=True)
    for name in ('firmware','ca','cert','key','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--case',action='append',dest='names')
    p.add_argument('--mode',action='append',choices=('small','large','grow','alternate'))
    p.add_argument('--seconds',type=int,default=75)
    p.add_argument('--port',type=int,default=8772)
    a = p.parse_args()
    require(not a.output.exists() and 60 <= a.seconds <= 600, 'Use fresh output and 60..600 seconds')
    config = a.firmware.with_name('sdkconfig').read_text()
    manifest = json.loads(a.firmware.with_name('manifest.json').read_text())
    transport_config(config,manifest,a.ca,a.cert,a.key)
    for key in ('CONFIG_ESP_CONSOLE_NONE=y','CONFIG_LOG_MAXIMUM_LEVEL=0','CONFIG_ESP_TASK_WDT_EN=y'):
        require(key in config, 'Required quiet/watchdog configuration missing')
    for key in ('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y','CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y'):
        require(key not in config, 'Unexpected sleep or CPU profiling')
    names = a.names or ['he-44100-stereo','hev2-44100-stereo']
    modes = a.mode or ['small','large','grow','alternate']
    require(len(set(names)) == len(names) and len(set(modes)) == len(modes), 'Duplicate cases')
    available = fixtures()
    require(all(n in available and available[n].get('profile') in ('AAC-LC','HE-AAC','HE-AACv2')
                for n in names), 'Use known ADTS AAC fixtures')
    specs = {n:available[n] for n in names}
    b = HealthBoard(a.board)
    identity,image = b.info(),image_info(a.firmware.read_bytes())
    require(identity['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    settings = snapshot(b)
    report = Report(a.output/'report.json',identity)
    report.data.update(image=image,seconds=a.seconds,modes=modes,names=names,
        sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
        test_ca_sha256=sha(a.ca.read_bytes()),leaf_certificate_sha256=sha(a.cert.read_bytes()),
        fixture_hashes={n:s['sha256'] for n,s in specs.items()},
        pacing_ratio=1.0,warmup_seconds=WARMUP_SECONDS,record_observations={},windows={})
    last_checkpoint = 0
    def checkpoint(completed,batch):
        nonlocal last_checkpoint
        now = time.perf_counter()
        if now-last_checkpoint < 20:return
        last_checkpoint = now
        progress = dict(case=batch['case'],last_status=batch['samples'][-1],last_health=b.health_samples[-1])
        (a.output/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
        print('OBSERVE',batch['case'],round(batch['samples'][-1]['seconds']),flush=True)
    suite = Suite(b,f'https://{a.host}:{a.port}',specs,Capture(None),a.output,checkpoint=checkpoint)
    def save():
        (a.output/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n')
        report.save()
    def case(name,fn):
        try:report.case(name,fn)
        finally:save()
    def observe(name,mode,server):
        key = name+':'+mode
        offset = len(server.events)
        b.play(suite.url(mode,name),'aac')
        health_start = len(b.health_samples)
        states = suite.observe(a.seconds,key,interval=1)
        health = b.health_samples[health_start:]
        observation = capture_record_observation(server.events[offset:])
        report.data['record_observations'][key] = observation
        steady,measured = sustained_window(states,health,a.seconds)
        report.data['windows'][key] = dict(output=output_window(measured),health=check_health(measured),
            maximum_status_health_ms=max(s['request_ms'] for s in states))
        case(key+':format',lambda:check_format(states,specs[name],a.seconds))
        first = next((suite.observations[-1]['started_at']+s['seconds']
                      for s in states if matches(s,specs[name])),float('inf'))
        case(key+':records',lambda:check_record_window(observation,mode,specs[name],first,observation['captured_at']))
        case(key+':output',lambda:check_output(measured))
        case(key+':memory',lambda:check_memory(measured))
        case(key+':response',lambda:check_response(states))
        return dict(samples=len(states),sustained_samples=len(steady))
    with (a.output/'request-phases.jsonl').open('x',encoding='utf-8') as trace:
        with TransportTrace(urlsplit(a.board).hostname,trace,capture_socket_ports=True):
            try:
                b.stop();suite.observe(12,'idle:initial',interval=1)
                initial = b.health_samples[-3:]
                require(all(r.get('output',{}).get('available') is True for r in initial), 'Missing output health')
                report.data['idle'] = dict(initial=initial)
                with RecordServer(a.host,a.port,specs,a.cert,a.key,
                                  seconds=a.seconds+OBSERVATION_TAIL_SECONDS,grow_seconds=30,
                                  pacing_ratio=1.0) as server:
                    try:
                        for name in names:
                            for mode in modes:
                                case(name+':'+mode+':collection',lambda n=name,m=mode:observe(n,m,server))
                                b.stop();suite.observe(12,'idle:'+name+':'+mode,interval=1)
                                final = b.health_samples[-3:]
                                report.data['idle'][name+':'+mode] = final
                                case(name+':'+mode+':recovery',lambda:check_recovery_heap(initial,final))
                    finally:
                        report.data['server_events_after_stop'] = capture_record_observation(server.events)
            finally:
                case('stop-and-settings',lambda:(b.stop(),verify_snapshot(b,settings))[1])
                case('lifetime-health',lambda:check_health(b.health_samples))
                save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
