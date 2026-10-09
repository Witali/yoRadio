"""Compare explicit reboot during full TLS audio with reboot after settled Stop.

Requires an already installed diagnostic application. Does not flash or change
saved stations. The caller must restore its original firmware/playback afterward.
TLS errors stay REVIEW_REQUIRED even when they precede an intentional reset.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import time

from common import (Board, Report, check_playback, check_recovery_heap,
                    exception_details, fixtures, matches, require, sha)
from diagnostic import DiagnosticCapture
from ota import image_info, snapshot, timed_action, verify_snapshot, wait_image
from run import Suite
from audio_test_server.server import Server


FAULT = re.compile(r'allocation failed|decode (?:error|failed)|assert failed|'
                   r'Guru Meditation|CORRUPT HEAP|PANIC|serial capture interrupted|'
                   r'Runtime watchdog timeout|PERF watchdog: task_timeouts=[1-9]|'
                   r'TCP_POOL:.*\baction=invalid-free|waiting for download')
SOFTWARE_RESET = re.compile(r'^rst:0xc \(RTC_SW_CPU_RST\),boot:')


def review_trial(trial, rows):
    """Preserve all TLS messages and require a completed, bounded software reset."""
    start, reboot, end = (trial[k] for k in ('started_at', 'reboot_started_at', 'ended_at'))
    require(start < reboot < end, 'Invalid trial timing')
    selected = [r for r in rows if start <= r['at'] <= end]
    resets = [r for r in selected if r['line'].startswith('rst:')]
    faults = [r for r in selected if FAULT.search(r['line'])]
    reset_ok = (len(resets) == 1 and reboot <= resets[0]['at'] <= end
                and SOFTWARE_RESET.match(resets[0]['line']) is not None)
    tls = []
    for row in selected:
        if not row['line'].startswith('TLS failure:'):
            continue
        phase = 'playback' if row['at'] >= trial.get('play_started_at', start) else 'baseline'
        if row['at'] >= reboot:
            phase = 'reboot'
        elif trial.get('stop_started_at') is not None and row['at'] >= trial['stop_started_at']:
            phase = 'stop-and-settle'
        reset = next((r for r in resets if r['at'] >= row['at']), None)
        tls.append(dict(row=row, phase=phase,
                        seconds_before_reset=reset['at']-row['at'] if reset else None))
    return dict(result='PASS' if reset_ok and not faults else 'FAIL',
                runtime_review='REVIEW_REQUIRED' if tls or faults or not reset_ok else 'PASS',
                resets=resets, faults=faults, tls=tls, records=len(selected))


def stopped(samples):
    require(len(samples) >= 3 and all(not r['audio'] and r.get('pcm_sample_rate') == 0
            and r.get('pcm_channels') == 0 for r in samples[-3:]),
            'Stop did not clear PCM state')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--ca', type=Path, required=True)
    p.add_argument('--cert', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--cycles', type=int, default=3)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    require(not args.output.exists() and args.cycles >= 2, 'Use fresh output and at least two cycles')
    manifest = json.loads(args.firmware.with_name('manifest.json').read_text())
    require(manifest.get('laboratory_only') is True and
            manifest.get('extra_trust_ca_sha256') == sha(args.ca.read_bytes()),
            'Use firmware with the matching additional laboratory CA')
    board = Board(args.board)
    identity = board.info()
    expected = image_info(args.firmware.read_bytes())
    require(identity['app_elf_sha256'] == expected['app_elf_sha256'], 'Unexpected installed image')
    before = snapshot(board)
    report = Report(args.output/'report.json', identity)
    specs = fixtures()
    name = 'hev2-44100-stereo'
    spec = specs[name]
    report.data.update(firmware=expected, cycles=args.cycles, fixture_sha256=spec['sha256'],
        ca_sha256=sha(args.ca.read_bytes()), leaf_sha256=sha(args.cert.read_bytes()),
        pacing_ratio=1.0, trials=[], transport='https')
    capture = DiagnosticCapture(args.serial_port)
    suite = Suite(board, f'https://{args.host}:8771', {name:spec}, capture, args.output)

    def action(label, fn):
        return timed_action(report, label, fn)

    def save():
        report.save()
        (args.output/'performance.json').write_text(json.dumps(capture.rows, indent=2)+'\n')

    try:
        with Server(args.host, 8771, {name:spec}, args.cert, args.key,
                    delivery_stats=True, pacing_ratio=1.0) as server:
            for cycle in range(args.cycles):
                # Reverse the pair in alternate cycles to reduce fixed-order bias.
                modes = ('active', 'stopped') if cycle % 2 == 0 else ('stopped', 'active')
                for mode in modes:
                    label = f'{cycle+1}:{mode}'
                    trial = dict(name=label, mode=mode, started_at=time.monotonic())
                    report.data['trials'].append(trial)
                    save()
                    print('START', label, flush=True)
                    try:
                        trial['baseline'] = action(label+':baseline', suite.idle_heap)
                        stopped(suite.observations[-1]['samples'])
                        first_event = len(server.events)
                        trial['play_started_at'] = time.monotonic()
                        action(label+':play', lambda:board.play(suite.url('stream',name),'aac'))
                        samples = action(label+':playback', lambda:suite.observe(12,label+':playback'))
                        trial['playback'] = check_playback(samples,spec,warmup=3)
                        trial['last_playback_state'] = board.status()
                        require(matches(trial['last_playback_state'],spec), 'Full SBR/PS playback lost before control')
                        trial['server_before_control'] = copy.deepcopy(server.events[first_event:])
                        require(len(trial['server_before_control']) == 1 and
                                trial['server_before_control'][0].get('tls_version') == 'TLSv1.2' and
                                trial['server_before_control'][0]['sent'] > 0,
                                'Expected one delivering TLS stream')
                        if mode == 'stopped':
                            trial['stop_started_at'] = time.monotonic()
                            action(label+':stop', board.stop)
                            trial['settled'] = action(label+':settle',lambda:suite.idle_heap(stop=False))
                            stopped(suite.observations[-1]['samples'])
                            check_recovery_heap(trial['baseline'],trial['settled'])
                        trial['reboot_started_at'] = time.monotonic()
                        action(label+':reboot',board.reboot)
                        time.sleep(3)
                        trial['boot'] = action(label+':verify-boot',lambda:wait_image(
                            board, expected['app_elf_sha256'],identity['partition'],timeout=45))
                        trial['ended_at'] = time.monotonic()
                        trial['review'] = review_trial(trial,capture.rows)
                        require(trial['review']['result'] == 'PASS', 'Runtime fault or missing/unexpected reset')
                        trial['result'] = 'PASS'
                        print('END',label,'PASS TLS rows',len(trial['review']['tls']),flush=True)
                    except BaseException as error:
                        trial.update(result='FAIL',exception_chain=exception_details(error),
                                     ended_at=time.monotonic())
                        raise
                    finally:
                        save()
            report.data['server_events'] = copy.deepcopy(server.events)
    finally:
        # Do not rewrite settings or silently restart a failed trial.
        try:
            action('cleanup:stop',board.stop)
            report.data['persistence'] = action('cleanup:settings',lambda:verify_snapshot(board,before))
        finally:
            capture.close()
            save()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
