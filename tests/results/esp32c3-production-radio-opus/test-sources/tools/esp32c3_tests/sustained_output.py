"""Bounded quiet-image public HTTPS playback with independent output gates.

The caller owns app-only OTA installation/restoration. Do not infer analog
continuity from completion-queue counters. Save failures without weakening
memory/response-time gates or stopping collection at the first slow response.
"""
import argparse
import json
import statistics
import time
from pathlib import Path
from urllib.parse import urlsplit

from common import Report, check_playback, check_recovery_heap, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import HealthBoard, check_health, output_window
from public_streams import DEFAULT_MANIFEST, probe, public_url
from run import Capture, Suite
from trace_transport import TransportTrace

WARMUP_SECONDS = 15


def sustained_window(states, health, seconds):
    require(len(states) == len(health), 'Unpaired status/health evidence')
    require(states and states[-1]['seconds'] >= seconds-2,
            'Incomplete playback observation')
    pairs = [(s,h) for s,h in zip(states,health) if s['seconds'] >= WARMUP_SECONDS]
    require(len(pairs) >= int((seconds-WARMUP_SECONDS)*.6), 'Sparse sustained observations')
    require(pairs[0][0]['seconds'] <= WARMUP_SECONDS+2, 'Missing beginning of sustained window')
    require(all(0 < b[0]['seconds']-a[0]['seconds'] <= 10
                for a,b in zip(pairs,pairs[1:])), 'Nonmonotonic or interrupted observations')
    return [s for s,h in pairs], [h for s,h in pairs]


def check_output(health):
    result = output_window(health)
    require(result['completion_queue_drops'] == 0, 'I2S completion queue overflow during sustained play')
    require(result['write_errors'] == 0, 'I2S write error during sustained play')
    return result


def check_memory(health):
    result = check_health(health)
    require(result['minimum_heap'] >= 16384 and result['minimum_largest'] >= 8192,
            'In-playback memory below existing budget')
    for key,tolerance in (('heap',2048),('largest',4096)):
        require(statistics.median(r[key] for r in health[:3])-
                statistics.median(r[key] for r in health[-3:]) <= tolerance,
                'Progressive '+key+' loss')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board',required=True)
    p.add_argument('--firmware',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stream',default='groovesalad-64-aac')
    p.add_argument('--aac-reference-command',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=600)
    a = p.parse_args()
    require(60 <= a.seconds <= 600, 'Use 60..600 seconds')
    require(not a.output.exists(), 'Preserve previous evidence')
    config = a.firmware.with_name('sdkconfig').read_text()
    for key in ('CONFIG_ESP_CONSOLE_NONE=y','CONFIG_LOG_MAXIMUM_LEVEL=0','CONFIG_ESP_TASK_WDT_EN=y'):
        require(key in config, 'Required quiet/watchdog configuration missing')
    for key in ('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y','CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y',
                'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y'):
        require(key not in config, 'Unexpected profiling, sleep or laboratory trust')
    manifest = json.loads(DEFAULT_MANIFEST.read_text())
    url = public_url(manifest['streams'][a.stream])
    reference = probe(url,'ffprobe',json.loads(a.aac_reference_command.read_text()))
    b = HealthBoard(a.board)
    identity,image = b.info(),image_info(a.firmware.read_bytes())
    require(identity['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    before = snapshot(b)
    report = Report(a.output/'report.json',identity)
    report.data.update(image=image,reference=reference,public_url=url,
        sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
        seconds=a.seconds,warmup_seconds=WARMUP_SECONDS,
        scope='Sampled status, lifetime faults, I2S completion drops and write errors; no analog continuity claim')
    last_checkpoint = 0
    def checkpoint(completed,batch):
        nonlocal last_checkpoint
        now = time.perf_counter()
        if now-last_checkpoint < 30:return
        last_checkpoint = now
        current = batch['samples'][-1]
        progress = dict(case=batch['case'],seconds=current['seconds'],samples=len(batch['samples']),
                        last_status=current,last_health=b.health_samples[-1])
        (a.output/'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
        print('OBSERVE',batch['case'],round(current['seconds']),flush=True)
    suite = Suite(b,'http://unused.invalid',{},Capture(None),a.output,checkpoint=checkpoint)

    def save_health():
        (a.output/'health.json').write_text(json.dumps(b.health_samples,indent=2)+'\n')
    def case(name,fn):
        try: report.case(name,fn)
        finally: save_health();report.save()
    def observe():
        b.play(url)
        start = len(b.health_samples)
        states = suite.observe(a.seconds,'https:'+a.stream,interval=1)
        health = b.health_samples[start:]
        steady, measured = sustained_window(states,health,a.seconds)
        report.data['output_window'] = output_window(measured)
        report.data['steady_health'] = check_health(measured)
        report.data['maximum_status_health_ms'] = max(s['request_ms'] for s in states)
        case('format',lambda:check_playback(states,reference['spec'],
             minimum=int((a.seconds-WARMUP_SECONDS)*.6),warmup=WARMUP_SECONDS))
        case('output',lambda:check_output(measured))
        case('memory',lambda:check_memory(measured))
        def response():
            maximum = max(s['request_ms'] for s in states)
            require(maximum < 2000, 'WebUI response exceeded 2 seconds')
            return dict(maximum_ms=maximum)
        case('response-time',response)
        return dict(samples=len(states),sustained_samples=len(steady))

    with (a.output/'request-phases.jsonl').open('x',encoding='utf-8') as log:
        with TransportTrace(urlsplit(a.board).hostname,log,capture_socket_ports=True):
            try:
                b.stop();suite.observe(12,'idle:initial',interval=1)
                initial = b.health_samples[-3:]
                require(all(r.get('output',{}).get('available') is True for r in initial),
                        'Missing output measurements')
                case('sustained-collection',observe)
                b.stop();suite.observe(12,'idle:final',interval=1)
                report.data['idle'] = dict(initial=initial,final=b.health_samples[-3:])
                case('recovery',lambda:check_recovery_heap(initial,b.health_samples[-3:]))
            finally:
                case('stop-and-settings',lambda:(b.stop(),verify_snapshot(b,before))[1])
                case('lifetime-health',lambda:check_health(b.health_samples))
                save_health();report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
