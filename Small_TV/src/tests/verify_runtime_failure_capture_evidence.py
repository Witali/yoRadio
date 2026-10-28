"""Replay the bounded native failure-capture checkpoint without contacting a VM."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import journal_evidence, require
from runtime_failure_layout import failure_layout
from runtime_run_guard import inspect_uart
from verify_photo_format_matrix_evidence import source_hashes
from verify_tcp_trend_evidence import archive_files


def sha(data):
    """Identify the exact small observation rather than trusting its filename."""
    return hashlib.sha256(data).hexdigest()


def validate(test, workload, state, evidence, uart, fixture_bytes):
    """Bind pre-cleanup ordering, a failed workload and actual read-only observations."""
    require(test['passed'] and test['inputs_unchanged'] and not test['all_functionality_verified'] and
            not test['h10_checks_passed'] and not test['physical_hardware_tested'], 'Overstated capture test')
    require(test['fault_injected'] and test['real_guest_http_status_before_fault'] == 200 and
            test['artifact_existed_before_stop'] and test['original_vm_exited'] and
            not test.get('test_fallback_cleanup_needed'), 'Missing real guest response or cleanup ordering')
    require(workload['passed'] is False and workload['inputs_unchanged'] and workload['no_panic'] and
            workload['error'] == 'Intentional diagnostic test timeout after actual HTTP 200' and
            not workload.get('cleanup_error'), 'Original failure was not preserved')
    require(state['vm_name'] == test['vm_owner']['name'] and state['target_stopped'] and
            state['app_sha256'] == workload['app_sha256'] and state['elf_sha256'] == workload['native_elf_sha256'] and
            state['qemu_sha256'] == workload['qemu_sha256'], 'Changed failure target')
    require(state['schema'] == 'small-tv-failure-state-v1' and state['status'] == 'captured' and
            not state['errors'] and state['operation'] == {'kind': 'http', 'path': '/start_upload'},
            'Incomplete selected capture')
    require(0 < state['memory_reads'] <= state['memory_call_limit'] == 192 and
            0 < state['memory_requested_bytes'] <= state['memory_read_limit'] == 32768 and
            0 <= state['elapsed_host_seconds'] < state['diagnostic_seconds_limit'] + .5 and
            state['diagnostic_seconds_limit'] == 5, 'Capture bounds differ')
    require(set(state['registers']) == {'pc', 'sp', 'ra'} and state['no_guest_memory_or_register_writes'] and
            state['no_guest_functions_called'], 'Unexpected register/payload capture')
    require(test['diagnostic_rsp_commands'] and all(command.startswith(('m', 'p'))
            for command in test['diagnostic_rsp_commands']), 'Diagnostic executes or writes guest state')
    upload = state['photo']['upload']
    require(upload['active'] == 1 and upload['received'] == 0 and upload['length'] == fixture_bytes and
            all(state['photo']['queues'][name]['address'] for name in ('jobs', 'codec_mutex', 'media_mutex')),
            'Missing actual photo/queue metadata')
    require(workload['summary'] == evidence['summary'] and workload['journal']['sha256'] == evidence['sha256'] and
            workload['completed_cycles'] == evidence['cycles'] == state['completed_cycles'] and
            workload['rom_counter_crosscheck']['checks'] == evidence['rom_calls'], 'Journal differs')
    require(uart['passed'] and uart['rom_boots'] == 1 and not uart['errors'], 'Actual UART reset or panic')
    return dict(passed=True, capture_status=state['status'], complete_cycles=evidence['cycles'],
                pending_events=evidence['pending_events'], memory_reads=state['memory_reads'],
                memory_requested_bytes=state['memory_requested_bytes'], h10_checks_passed=False)


def rejections(values):
    """Reject hidden failures, false ordering, guest execution and weakened bounds."""
    rejected = []
    for case in ('after-stop', 'live-vm', 'fallback-cleanup', 'workload-pass', 'hardware-claim', 'wrong-elf',
                 'read-count', 'read-bytes', 'timeout', 'write-command', 'continue-command'):
        t, w, s, e, u, length = copy.deepcopy(values)
        if case == 'after-stop': t['artifact_existed_before_stop'] = False
        elif case == 'live-vm': t['original_vm_exited'] = False
        elif case == 'fallback-cleanup': t['test_fallback_cleanup_needed'] = True
        elif case == 'workload-pass': w['passed'] = True
        elif case == 'hardware-claim': t['physical_hardware_tested'] = True
        elif case == 'wrong-elf': s['elf_sha256'] = '00' * 32
        elif case == 'read-count': s['memory_reads'] = 193
        elif case == 'read-bytes': s['memory_requested_bytes'] = 32769
        elif case == 'timeout': s['elapsed_host_seconds'] = 6
        elif case == 'write-command': t['diagnostic_rsp_commands'].append('P20=00000000')
        else: t['diagnostic_rsp_commands'].append('c')
        try: validate(t, w, s, e, u, length)
        except ValueError: rejected.append(case)
        else: raise AssertionError('Invalid failure capture accepted: ' + case)
    return rejected


def verify(path, root, revision=None):
    """Recompute archive, journal and native layout without reading a live process."""
    proof = json.loads(path.read_text())
    require(proof['schema'] == 'small-tv-failure-capture-v1' and proof['passed'] and
            not proof['h10_checks_passed'] and not proof['all_functionality_verified'] and
            not proof['physical_hardware_tested'], 'Overstated checkpoint')
    files = archive_files(path, proof)
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'Capture sources changed')
    for name, digest in proof['source_pins'].items():
        require(sha(files['source/' + name]) == digest, 'Archived source differs')
    app = (root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require(sha(app) == proof['app_sha256'] and sha(elf.read_bytes()) == proof['elf_sha256'] and
            app[176:208] == bytes.fromhex(proof['elf_sha256']), 'Application/ELF identity differs')
    read = lambda name: json.loads(files[name])
    test, workload, state = read('test/report.json'), read('run/report.json'), read('run/failure-state.json')
    require(state['app_sha256'] == proof['app_sha256'] and state['elf_sha256'] == proof['elf_sha256'] and
            state['qemu_sha256'] == proof['qemu_sha256'], 'Checkpoint image differs')
    require(sha(files['run/failure-state.json']) == workload['failure_capture']['sha256'] ==
            test['artifact_sha256_before_stop'], 'Artifact was replaced after cleanup')
    require(failure_layout(elf) == read('layout/photo.json'), 'Native diagnostic layout differs')
    fixture = files['source/Small_TV/src/tests/fixtures/jpeg/rgb-420.jpg']
    folder = root / '.build/failure-capture-replay' / sha(files['run/events.jsonl'])
    folder.mkdir(parents=True, exist_ok=True)
    journal = folder / 'events.jsonl'; journal.write_bytes(files['run/events.jsonl'])
    evidence = journal_evidence(journal, (len(fixture) + 4095) // 4096, 0, allow_partial=True, require_weather=True)
    values = test, workload, state, evidence, inspect_uart(files['run/uart.log']), len(fixture)
    result, rejected = validate(*values), rejections(values)
    require(result == proof['result'] and rejected == proof['rejected_controls'], 'Capture outcome differs')
    require(b'Ran 10 tests' in files['unit/deadline.log'] and b'OK' in files['unit/deadline.log'] and
            b'Ran 10 tests' in files['unit/capture.log'] and b'OK' in files['unit/capture.log'], 'Missing transport/error tests')
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'Sources changed during replay')
    return dict(**result, unsafe_controls_rejected=len(rejected))


def main():
    """Report a checked diagnostic, never an H10 or original-timeout explanation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.source_revision)))


if __name__ == '__main__':
    main()
