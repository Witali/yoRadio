"""Replay an interrupted soak prefix without manufacturing a terminal H10 pass."""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import journal_evidence, require
from runtime_trend import analyze_trend
from verify_photo_format_matrix_evidence import source_hashes


def digest(data):
    """Identify archived bytes independently of paths or JSON formatting."""
    return hashlib.sha256(data).hexdigest()


def validate(report, evidence, diagnostic, strict, guard, supervisor, observation):
    """Keep verified prefix observations, owner loss and acceptance separate."""
    require(report['schema_version'] == 5 and report['passed'] is False,
            'Interrupted workload cannot pass')
    require('journal' not in report and 'inputs_unchanged' not in report,
            'Do not classify a terminal report as an interrupted prefix')
    require(report['duration_requested_guest_seconds'] == 86400 and
            report['cycles_requested'] is None, 'Changed H10 request')
    require(diagnostic['status'] == 'pending' and diagnostic['journal_prefix_only'] and
            not diagnostic['h10_checks_passed'] and diagnostic['inputs_verified'] and
            not diagnostic['all_functionality_verified'], 'Overstated diagnostic scope')
    require(strict['status'] == 'evidence_rejected' and not strict['h10_checks_passed'] and
            strict['error'] == 'Runtime workload has not finished', 'Strict acceptance must reject')
    require(guard['status'] == supervisor['status'] == 'running' and
            not guard['passed'] and not supervisor['passed'], 'Invented terminal guard')
    require(set(observation['owners']) == {'supervisor', 'workload', 'guard', 'vm'},
            'Missing owner observation')
    expected = {'supervisor': supervisor['supervisor_pid'], 'workload': supervisor['workload_pid'],
                'guard': supervisor['guard_pid'], 'vm': observation['vm_session_pid']}
    require(all(type(row['pid']) is int and row['pid'] == expected[role] and
                row['matches'] == [] for role, row in observation['owners'].items()) and
            not observation['matching_run_processes'], 'Owner absence is not established')
    require(observation['termination_reason'] == 'unknown', 'Unproven termination cause')
    require(diagnostic['complete_cycles_audited'] == evidence['cycles'] and
            diagnostic['summary'] == evidence['summary'] and
            diagnostic['weather'] == evidence['weather'] and
            diagnostic['pending_events'] == evidence['pending_events'] and
            diagnostic['trailing_partial_bytes'] == evidence['trailing_partial_bytes'] and
            diagnostic['journal_observed_sha256'] == evidence['sha256'], 'Journal evidence differs')
    start = report['workload_start_guest_seconds']
    end = evidence['series'][-1]['guest_seconds']
    require(end - start == diagnostic['elapsed_guest_seconds_observed'] and
            end - start < report['duration_requested_guest_seconds'], 'False duration coverage')
    period = math.lcm(20, report['outage_every_cycles'] or 1)
    trend = analyze_trend(evidence['series'], start, end, phase_period=period)
    require(diagnostic['trend'] == trend, 'Changed trend or suppressed warning')
    require(diagnostic['uart'] == guard['last_observation'] and diagnostic['uart']['passed'] and
            diagnostic['uart']['rom_boots'] == 1 and not diagnostic['uart']['errors'],
            'Invalid UART prefix observation')
    for name in ('app_sha256', 'qemu_sha256'):
        require(report[name] == diagnostic[name], 'Changed identity: ' + name)
    require(report['native_elf_sha256'] == diagnostic['native_elf_sha256'] and
            report['inputs_sha256'][report['qemu_executable']] == report['qemu_sha256'],
            'Unbound executable identity')
    return dict(evidence_verified=True, status='interrupted', h10_checks_passed=False,
                complete_cycles=evidence['cycles'], pending_events=evidence['pending_events'],
                elapsed_guest_seconds=end - start, http_requests=evidence['summary']['http_requests'],
                outages=evidence['summary']['outages'], trend_status=trend['status'],
                retained_loss_phases=trend['flags'], weather=evidence['weather'],
                minimum_sampled_free_heap_bytes=evidence['summary']['minimum_sampled_free_heap_bytes'])


def rejections(values):
    """Reject false completion, fabricated owner loss and hidden memory findings."""
    rejected = []
    for case in ('workload-pass', 'h10-pass', 'unverified-inputs', 'cycles', 'duration',
                 'terminal-guard', 'live-owner', 'missing-owner', 'hidden-trend', 'uart-reset'):
        r, e, d, s, g, p, o = copy.deepcopy(values)
        if case == 'workload-pass': r['passed'] = True
        elif case == 'h10-pass': d['h10_checks_passed'] = True
        elif case == 'unverified-inputs': d['inputs_verified'] = False
        elif case == 'cycles': d['complete_cycles_audited'] += 1
        elif case == 'duration': d['elapsed_guest_seconds_observed'] = 86400
        elif case == 'terminal-guard': g['status'] = 'complete'; g['passed'] = True
        elif case == 'live-owner': o['owners']['vm']['matches'] = [{'pid': o['vm_session_pid']}]
        elif case == 'missing-owner': del o['owners']['guard']
        elif case == 'hidden-trend': d['trend']['flags'] = []
        else: d['uart']['rom_boots'] = 2
        try: validate(r, e, d, s, g, p, o)
        except ValueError: rejected.append(case)
        else: raise AssertionError('Invalid interrupted evidence accepted: ' + case)
    return rejected


def verify(path, root, revision=None):
    """Recompute the complete archived numeric prefix; never access a live VM."""
    proof = json.loads(path.read_text())
    require(proof['evidence_verified'] and not proof['h10_checks_passed'] and
            not proof['workload_passed'] and not proof['all_functionality_verified'], 'Overstated proof')
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent / row['file']).resolve()
        require(file.is_relative_to(path.parent.resolve()), 'Payload outside evidence directory')
        packed = file.read_bytes(); data = gzip.decompress(packed)
        require(digest(packed) == row['gzip_sha256'] and digest(data) == row['sha256'] and
                len(data) == row['bytes'], 'Payload digest differs')
        blobs[row['sha256']] = data
    files = {row['source']: blobs[row['sha256']] for row in proof['raw']}
    require(len(files) == len(proof['raw']), 'Duplicate evidence name')
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'Producer sources differ')
    for name, expected in proof['source_pins'].items():
        require(digest(files['producer/' + name]) == expected, 'Archived source differs')
    read = lambda name: json.loads(files[name])
    report, diagnostic = read('run/report.json'), read('analysis/diagnostic.json')
    fixture = files['producer/Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg']
    require(proof['photo_chunks'] == (len(fixture) + 4095) // 4096, 'Changed photo workload')
    app = (root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf = (root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    require(digest(app) == report['app_sha256'] == proof['app_sha256'] and
            digest(elf) == report['native_elf_sha256'] == proof['elf_sha256'] and
            app[176:208] == bytes.fromhex(proof['elf_sha256']), 'Firmware identity differs')
    start = read('run/start.json')
    for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256', 'inputs_sha256',
                'duration_requested_guest_seconds'):
        require(start[key] == report[key], 'Early identity differs: ' + key)
    folder = root / '.build/interrupted-runtime-replay' / digest(files['run/events.jsonl'])
    folder.mkdir(parents=True, exist_ok=True)
    journal = folder / 'events.jsonl'; journal.write_bytes(files['run/events.jsonl'])
    chunks = proof['photo_chunks']
    evidence = journal_evidence(journal, chunks, report['outage_every_cycles'],
                                allow_partial=True, require_weather=True)
    values = (report, evidence, diagnostic, read('analysis/strict.json'), read('run/uptime-guard.json'),
              read('run/supervisor.json'), read('host/owners.json'))
    result = validate(*values); rejected = rejections(values)
    # Corrupt actual event bytes, rather than only mutating a derived success flag.
    data = files['run/events.jsonl']
    first = json.loads(data.splitlines()[0]); first['data']['heap']['free_bytes'] += 1
    mutations = {'heap-total': json.dumps(first).encode() + b'\n' + data.split(b'\n', 1)[1],
                 'http-status': data.replace(b'"status":200', b'"status":503', 1)}
    for case, changed in mutations.items():
        require(changed != data, 'Mutation did not change the journal')
        journal.write_bytes(changed)
        try: journal_evidence(journal, chunks, report['outage_every_cycles'], allow_partial=True, require_weather=True)
        except ValueError: rejected.append(case)
        else: raise AssertionError('Invalid journal accepted: ' + case)
    journal.write_bytes(data)
    require(result == proof['result'] and rejected == proof['rejected_controls'], 'Proof outcome differs')
    return {**result, 'unsafe_controls_rejected': len(rejected)}


def main():
    """Report verified interruption evidence without returning an H10 acceptance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.source_revision)))


if __name__ == '__main__':
    main()
