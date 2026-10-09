"""Physical TLS-record growth tests on explicitly labelled laboratory firmware."""
import argparse
import copy
import json
import math
from pathlib import Path
import time

from common import Board, Report, check_cpu, check_playback, check_recovery_heap, fixtures, matches, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, verify_snapshot
from public_streams import no_runtime_faults
from run import Suite
from audio_test_server.tls_records import (RecordServer, MAX_OBSERVATION_SECONDS,
                                         OBSERVATION_TAIL_SECONDS)


def capture_record_observation(events):
    return dict(captured_at=time.monotonic(), events=copy.deepcopy(events))


def record_evidence(events, mode):
    require(mode in ('small','large','grow','alternate'), 'Unknown record mode')
    selected = [e for e in events if e.get('mode') == mode]
    # Failed handshakes have no mode yet; count them as connections too.
    require(len(events) == 1 and len(selected) == 1, 'Expected one TLS connection, not retries')
    event = selected[0]
    require(event.get('version') == 'TLSv1.2' and event.get('cipher') == 'ECDHE-RSA-AES128-GCM-SHA256',
            'Unexpected negotiated TLS parameters')
    require(event['dropped_records'] == event['dropped_writes'] == 0, 'Truncated record evidence')
    records = [r for r in event['records'] if r['phase'].startswith('body-')]
    expected = {1048} if mode == 'small' else {16408} if mode == 'large' else {1048, 16408}
    require({r['wire_payload_bytes'] for r in records} == expected and
            all(r['type'] == 23 for r in records), 'Missing exact application record sizes')
    writes = [w for w in event['writes'] if w['phase'].startswith('body-')]
    require([w['plaintext_bytes'] + 24 for w in writes] == [r['wire_payload_bytes'] for r in records],
            'TLS writes and generated records differ')
    counts = {size:sum(r['wire_payload_bytes'] == size for r in records) for size in expected}
    require(all(n >= 2 for n in counts.values()), 'Insufficient records for each size')
    return dict(record_counts=counts, first_large_at=next((r['at'] for r in records if r['phase'] == 'body-large'), None))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--ca', type=Path, required=True)
    p.add_argument('--cert', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--case', default='hev2-44100-stereo')
    p.add_argument('--mode', choices=('small','large','grow','alternate'), action='append')
    p.add_argument('--seconds', type=int, default=75)
    p.add_argument('--pacing-ratio', type=float, default=1.02,
                   help='Audio seconds per wall second; use 1.0 for real-time delivery')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists() and 60 <= args.seconds <= MAX_OBSERVATION_SECONDS,
            f'Use fresh output and 60..{MAX_OBSERVATION_SECONDS} seconds')
    require(math.isfinite(args.pacing_ratio) and args.pacing_ratio > 0,
            'Use a finite positive pacing ratio')
    cfg = args.firmware.with_name('sdkconfig').read_text()
    manifest = json.loads(args.firmware.with_name('manifest.json').read_text())
    require(manifest.get('laboratory_only') is True and manifest.get('extra_trust_ca_sha256') == sha(args.ca.read_bytes()),
            'Firmware manifest must identify this laboratory-only CA')
    require('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y' in cfg and
            'CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y' in cfg and
            'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384' in cfg,
            'Keep full TLS capacity and normal public certificate roots')
    require(all(k+'=y' not in cfg for k in ('CONFIG_YORADIO_QEMU','CONFIG_YORADIO_DEEP_SLEEP_CLOCK','CONFIG_ESP_CONSOLE_NONE')),
            'Use awake physical profiling firmware')
    board = Board(args.board)
    identity = board.info()
    require(identity['app_elf_sha256'] == image_info(args.firmware.read_bytes())['app_elf_sha256'], 'Wrong installed image')
    settings = snapshot(board)
    specs = fixtures()
    require(args.case in specs and specs[args.case]['codec'] == 'aac', 'Use an ADTS AAC fixture')
    report = Report(args.output/'report.json', identity)
    report.data.update(firmware_sha256=sha(args.firmware.read_bytes()), sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        test_ca_sha256=sha(args.ca.read_bytes()), leaf_certificate_sha256=sha(args.cert.read_bytes()),
        fixture_hashes={args.case: specs[args.case]['sha256']}, seconds=args.seconds,
        pacing_ratio=args.pacing_ratio,
        note='Laboratory CA extends normal roots; verification stays enabled. Record lengths are observed at the server; playback/status provide separate board evidence.')
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'https://{args.host}:8772', specs, capture, args.output, cpu_budget=None)
    baseline = None

    def idle():
        nonlocal baseline
        baseline = suite.idle_heap()
        return dict(samples=baseline)

    def run_case(mode, server):
        board.stop()
        time.sleep(.8)
        before = len(server.events)
        started = time.monotonic()
        try:
            board.play(f'https://{args.host}:8772/{mode}/{args.case}', 'aac')
            samples = suite.observe(args.seconds, 'tls-record:'+mode, interval=.1)
            # Preserve the exact evidence inspected by the gate. Stop can make
            # the server generate one more record whose socket write fails;
            # that later record must not mutate a previously checked snapshot.
            observation = capture_record_observation(server.events[before:])
            report.data.setdefault('record_observations', {})[mode] = observation
            playback = check_playback(samples, specs[args.case], warmup=5)
            record = record_evidence(observation['events'], mode)
            require(all(e.get('pacing_ratio') == args.pacing_ratio for e in observation['events']),
                    'Server pacing differs from requested mode')
            first_pcm = next(suite.observations[-1]['started_at']+s['seconds'] for s in samples if matches(s,specs[args.case]))
            if mode == 'grow':
                require(first_pcm < record['first_large_at'], 'Record grew before full-rate decoder playback began')
            no_runtime_faults(capture.since(started))
            cpu = check_cpu(capture.since(started), max_busy=None, start=started, end=time.monotonic())
            require(max(s['request_ms'] for s in samples) < 2000, 'WebUI response exceeded two seconds')
            return dict(**playback, **record, **cpu, first_full_pcm_seconds=first_pcm-started)
        finally:
            board.stop()

    try:
        with RecordServer(args.host, 8772, {args.case:specs[args.case]}, args.cert, args.key,
                          seconds=args.seconds+OBSERVATION_TAIL_SECONDS, grow_seconds=30,
                          pacing_ratio=args.pacing_ratio) as server:
            report.case('idle-before', idle)
            for mode in args.mode or ('small','large','grow','alternate'):
                report.case('tls-record:'+mode, lambda m=mode: run_case(m,server))
            report.data['server_events'] = server.events
            def recovery():
                final = suite.idle_heap()
                require(baseline is not None, 'Missing baseline')
                check_recovery_heap(baseline, final)
                return dict(samples=final)
            report.case('idle-recovery', recovery)
    finally:
        report.case('runtime', lambda:no_runtime_faults(capture.rows))
        def restore():
            board.stop()
            return dict(stopped=True, **verify_snapshot(board,settings))
        report.case('restore', restore)
        capture.close()
        (args.output/'performance.json').write_text(json.dumps(capture.rows,indent=2)+'\n')
        report.save()
    return report.exit_code()


if __name__ == '__main__':
    raise SystemExit(main())
