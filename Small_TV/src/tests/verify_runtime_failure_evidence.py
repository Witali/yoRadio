"""Replay a terminal failed runtime without turning its valid prefix into H10."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import journal_evidence, require
from runtime_run_guard import inspect_uart
from runtime_trend import analyze_trend
from verify_photo_format_matrix_evidence import source_hashes
from verify_tcp_trend_evidence import archive_files


def validate(report, evidence, guard, supervisor, before, after):
    """Keep a completed failure, surviving observations and owner exit distinct."""
    require(report['schema_version'] == 5 and report['passed'] is False and
            report['inputs_unchanged'] is True and report['no_panic'] is True and
            report['error'] == 'timed out', 'Expected the observed terminal timeout')
    require(report['all_functionality_verified'] is False and
            report['duration_requested_guest_seconds'] == 86400 and
            report['cycles_requested'] is None and report.get('elapsed_guest_seconds') is None and
            report.get('workload_end_guest_seconds') is None,
            'False duration acceptance')
    require(report['completed_cycles'] == evidence['cycles'] and
            report['summary'] == evidence['summary'] and
            report['journal']['sha256'] == evidence['sha256'] and
            report['rom_counter_crosscheck']['checks'] == evidence['rom_calls'], 'Journal differs')
    require(guard['status'] == 'complete' and guard['passed'] is True and
            guard['workload_passed'] is False and guard['last_observation']['passed'],
            'UART success cannot imply workload success')
    require(supervisor['status'] == 'failed' and supervisor['passed'] is False and
            supervisor['sources_unchanged'] is True and supervisor['workload_exit_code'] == 1 and
            supervisor['guard_exit_code'] == 0 and supervisor['cleanup_errors'], 'Terminal supervision differs')
    expected = {row['role']: row for row in before['processes']}
    observed = {row['role']: row for row in after['processes']}
    require(len(before['processes']) == len(after['processes']) == 4 and
            set(expected) == set(observed) == {'supervisor', 'workload', 'guard', 'vm'}, 'Missing owner')
    for role, row in expected.items():
        current = observed[role]
        require(current['pid'] == row['pid'] and current['expected_name'] == row['name'] and
                current['expected_created_utc'] == row['created_utc'], 'Changed original owner')
        require(current['name'] != row['name'] or current['created_utc'] != row['created_utc'],
                'Original owner is still alive')
    start, end = report['workload_start_guest_seconds'], evidence['series'][-1]['guest_seconds']
    trend = analyze_trend(evidence['series'], start, end,
                          phase_period=math.lcm(20, report['outage_every_cycles'] or 1))
    require(end - start < report['duration_requested_guest_seconds'], 'False 24-hour coverage')
    return dict(status='terminal_failed', evidence_verified=True, workload_passed=False,
                h10_checks_passed=False, all_functionality_verified=False, root_cause='unknown',
                complete_cycles=evidence['cycles'], pending_events=evidence['pending_events'],
                http_requests=evidence['summary']['http_requests'], outages=evidence['summary']['outages'],
                elapsed_guest_seconds_observed=end - start, trend=trend)


def rejections(values):
    """Reject promotion to success, missing work and fabricated original-owner exit."""
    rejected = []
    for case in ('workload-pass', 'full-scope', 'duration', 'cycles', 'journal', 'supervisor-pass', 'live-owner'):
        r, e, g, s, b, a = copy.deepcopy(values)
        if case == 'workload-pass': r['passed'] = True
        elif case == 'full-scope': r['all_functionality_verified'] = True
        elif case == 'duration': r['elapsed_guest_seconds'] = 86400
        elif case == 'cycles': r['completed_cycles'] += 1
        elif case == 'journal': r['journal']['sha256'] = '00' * 32
        elif case == 'supervisor-pass': s['passed'] = True
        else:
            original = b['processes'][0]
            row = next(x for x in a['processes'] if x['role'] == original['role'])
            row.update(name=original['name'], created_utc=original['created_utc'])
        try: validate(r, e, g, s, b, a)
        except ValueError: rejected.append(case)
        else: raise AssertionError('Invalid failed-run evidence accepted: ' + case)
    return rejected


def verify(path, root, recheck_inputs=False):
    """Recompute archived bytes only; optionally rehash still-retained run inputs."""
    proof = json.loads(path.read_text())
    require(proof['schema'] == 'small-tv-runtime-failure-v1' and not proof['h10_checks_passed'] and
            not proof['workload_passed'] and not proof['all_functionality_verified'], 'Overstated failure archive')
    require(source_hashes(root, proof['source_pins']) == proof['source_pins'], 'Analysis sources changed')
    files = archive_files(path, proof)
    for name, digest in proof['source_pins'].items():
        require(hashlib.sha256(files['analysis-source/' + name]).hexdigest() == digest, 'Archived analysis source differs')
    read = lambda name: json.loads(files[name])
    report = read('run/report.json')
    folder = root / '.build/runtime-failure-replay' / report['journal']['sha256']
    folder.mkdir(parents=True, exist_ok=True)
    journal = folder / 'events.jsonl'; journal.write_bytes(files['run/events.jsonl'])
    chunks = (len(files['fixture/rgb-420.jpg']) + 4095) // 4096
    evidence = journal_evidence(journal, chunks, report['outage_every_cycles'],
                                allow_partial=True, require_weather=True)
    values = (report, evidence, read('run/uptime-guard.json'), read('run/supervisor.json'),
              read('run/processes.json'), read('host/owners-after.json'))
    result = validate(*values)
    require(inspect_uart(files['run/uart.log']) == values[2]['last_observation'], 'UART bytes differ')
    start = read('run/start.json')
    for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256', 'inputs_sha256', 'duration_requested_guest_seconds'):
        require(start[key] == report[key], 'Early identity differs: ' + key)
    require(report['inputs_sha256'][report['qemu_executable']] == report['qemu_sha256'], 'Unbound QEMU executable')
    require(b'TimeoutError: timed out' in files['run/workload.stderr.log'] and
            b"request('/start_upload'" in files['run/workload.stderr.log'], 'Missing observed failure location')
    result['qemu_wsa_event_select_warnings'] = files['run/qemu.log'].count(b'failed to WSAEventSelect()')
    rejected = rejections(values)
    require(result == proof['result'] and rejected == proof['rejected_controls'], 'Failure outcome differs')
    if recheck_inputs:
        for name, digest in report['inputs_sha256'].items():
            require(hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, 'Retained runtime input differs')
    require(source_hashes(root, proof['source_pins']) == proof['source_pins'], 'Analysis changed during replay')
    return dict(status=result['status'], evidence_verified=True, h10_checks_passed=False,
                complete_cycles=result['complete_cycles'], http_requests=result['http_requests'],
                elapsed_guest_seconds_observed=result['elapsed_guest_seconds_observed'],
                unsafe_controls_rejected=len(rejected), inputs_rechecked=recheck_inputs, root_cause='unknown')


def main():
    """Report a verified failure; never contact a VM or claim a completed H10."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--recheck-inputs', action='store_true', help='Rehash the original retained absolute input paths')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.recheck_inputs)))


if __name__ == '__main__':
    main()
