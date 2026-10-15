"""Observe an exact quiet firmware image with a paced, finite local fixture.

No flashing, private settings export or analog-continuity claim. A new result
directory is mandatory. Capture failures before Stop and retain final recovery.
"""
import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlsplit

from common import Report, check_playback, check_recovery_heap, fixtures, require, sha
from ota import image_info, snapshot, verify_snapshot
from production_health import (HealthBoard, capture_failure_snapshot, check_health, output_window,
                              check_decoder_health as decoder_health)
from sustained_output import sustained_window, check_memory, check_output
from run import Capture, Suite
from trace_transport import TransportTrace
from audio_test_server.server import Server, DeliveryPauses, pause_argument


def check_delivery_pauses(events, fixture, schedule):
    """A missed or materially stretched host pause cannot qualify a matched trial."""
    require(len(events) == 1 and events[0].get('fixture') == fixture,
            'Missing unique fixture delivery')
    event = events[0]
    expected = [dict(after_bytes=n, seconds=s) for n, s in schedule]
    require(event.get('pacing_ratio') == 1.0 and event.get('pause_schedule') == expected,
            'Delivery schedule differs from requested schedule')
    rows = event.get('pauses', [])
    require(len(rows) == len(schedule), 'Not all delivery pauses executed')
    for row, (offset, seconds) in zip(rows, schedule):
        require(row.get('after_bytes') == offset and row.get('requested_seconds') == seconds
                and row.get('completed') is True, 'Missing or interrupted delivery pause')
        elapsed = row.get('elapsed_seconds', float('nan'))
        require(seconds - .005 <= elapsed <= seconds + .05, 'Host pause timing outside comparison tolerance')
    return dict(pauses=rows, scope='Host write scheduling, not board receive timing')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, default=8772)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--fixture', required=True)
    p.add_argument('--seconds', type=int, default=600)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--delivery-pause', type=pause_argument, action='append', default=[],
                   help='Pause before BYTE_OFFSET:SECONDS; repeat in increasing order')
    p.add_argument('--send-buffer-bytes', type=int,
                   help='Bound host socket buffering; actual size is recorded by the server')
    a = p.parse_args()
    schedule = DeliveryPauses.validate(a.delivery_pause)
    require(45 <= a.seconds <= 600, 'Observation must be 45..600 seconds')
    require(not a.output.exists(), 'Preserve previous evidence')
    specs = fixtures(a.fixtures)
    require(a.fixture in specs, 'Unknown fixture')
    spec = specs[a.fixture]
    require(spec['seconds'] >= a.seconds + 5, 'Fixture must outlast the observation')
    config = a.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_ESP_CONSOLE_NONE=y' in config and 'CONFIG_LOG_MAXIMUM_LEVEL=0' in config,
            'Expected quiet firmware')
    require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Disable deep sleep')
    b = HealthBoard(a.board)
    identity, image = b.info(), image_info(a.firmware.read_bytes())
    require(identity['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    initial_status = b.status()
    require(not initial_status['audio'], 'Do not interrupt unrelated active playback')
    before = snapshot(b)  # Kept only in memory.
    report = Report(a.output/'report.json', identity)
    report.data.update(image=image, initial_status=initial_status, initial_health=b.health_samples[-1],
        sdkconfig_sha256=sha(a.firmware.with_name('sdkconfig').read_bytes()),
        fixture_manifest_sha256=sha(a.fixtures.read_bytes()),
        fixture={k: spec[k] for k in ('sha256', 'seconds', 'rate', 'channels', 'bits', 'codec')},
        fixture_name=a.fixture, observation_seconds=a.seconds, pacing_ratio=1.0,
        delivery_pause_schedule=[dict(after_bytes=n, seconds=s) for n, s in schedule],
        send_buffer_requested=a.send_buffer_bytes,
        scope='Finite paced HTTP playback, sampled format/output/faults and settled memory recovery; no acoustic or CPU measurement')
    last_checkpoint = 0

    def save():
        (a.output/'health.json').write_text(json.dumps(b.health_samples, indent=2)+'\n')
        report.save()

    def checkpoint(completed, batch):
        nonlocal last_checkpoint
        now = time.perf_counter()
        if now-last_checkpoint < 30:
            return
        last_checkpoint = now
        row = batch['samples'][-1]
        (a.output/'progress.json').write_text(json.dumps(dict(case=batch['case'],
            seconds=row['seconds'], status=row, health=b.health_samples[-1]), indent=2)+'\n')
        save()
        print('OBSERVE', batch['case'], round(row['seconds']), flush=True)

    origin = f'http://{a.host}:{a.port}'
    suite = Suite(b, origin, specs, Capture(None), a.output, checkpoint=checkpoint)

    def case(name, action):
        try:
            report.case(name, action)
        finally:
            save()

    def observe():
        start = len(b.health_samples)
        try:
            b.play(origin+'/file/'+a.fixture)
            states = suite.observe(a.seconds, a.fixture, interval=1)
            rows = b.health_samples[start:]
            steady, measured = sustained_window(states, rows, a.seconds)
            # Retain the measured values even when the strict output gate fails.
            report.data['measured_output_counters'] = output_window(measured)
            # Evaluate gates before Stop; every failure receives one last snapshot.
            gates = (
                ('format', lambda: check_playback(states, spec,
                    minimum=int((a.seconds-15)*.6), warmup=15)),
                ('output', lambda: check_output(measured)),
                ('memory', lambda: check_memory(measured)),
                ('decoder-health', lambda: decoder_health(rows)),
            )
            for name, action in gates:
                def checked(fn=action, gate=name):
                    try:
                        return fn()
                    except Exception:
                        report.data.setdefault('failure_snapshots', {})[gate] = capture_failure_snapshot(b)
                        raise
                case(name, checked)
            return dict(samples=len(states), steady_samples=len(steady),
                        maximum_status_health_ms=max(s['request_ms'] for s in states))
        except Exception:
            report.data['collection_failure_snapshot'] = capture_failure_snapshot(b)
            raise

    with (a.output/'request-phases.jsonl').open('x', encoding='utf-8') as trace:
        with TransportTrace(urlsplit(a.board).hostname, trace, capture_socket_ports=True):
            with Server(a.host, a.port, specs, delivery_stats=True, pacing_ratio=1.0,
                        delivery_pauses=schedule, send_buffer_bytes=a.send_buffer_bytes) as server:
                try:
                    b.stop()
                    suite.observe(12, 'idle:initial', interval=1)
                    initial = b.health_samples[-3:]
                    report.data['idle'] = dict(initial=initial)
                    case('sustained-collection', observe)
                    if schedule:
                        case('delivery-pauses', lambda: check_delivery_pauses(server.events, a.fixture, schedule))
                    b.stop()
                    suite.observe(12, 'idle:final', interval=1)
                    report.data['idle']['final'] = b.health_samples[-3:]
                    case('recovery', lambda: check_recovery_heap(initial, b.health_samples[-3:]))
                finally:
                    case('stop-and-settings', lambda: (b.stop(), verify_snapshot(b, before))[1])
                    case('lifetime-health', lambda: check_health(b.health_samples))
                    case('all-decoder-health', lambda: decoder_health(b.health_samples))
                    report.data['server_events'] = server.events
                    save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
