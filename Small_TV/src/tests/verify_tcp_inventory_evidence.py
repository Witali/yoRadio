"""Replay complete guarded TCP-attribution workloads without starting a VM."""
import argparse
import copy
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import journal_evidence, require
from runtime_heap_topology import HeapTopology
from runtime_tcp_journal import TcpCoverage
from runtime_tcp_snapshot import TcpSnapshot, canonical
from verify_photo_format_matrix_evidence import source_hashes
from verify_runtime_candidate_evidence import validate, rejections, validate_model, model_rejections, topology_rejections


def sha(raw):
    """Bind exact payloads and their deterministic numeric time series."""
    return hashlib.sha256(raw).hexdigest()


def utc(value):
    """Reject local/naive timestamps in process ownership evidence."""
    stamp = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(stamp.utcoffset() == dt.timedelta(0), 'Expected UTC process timestamp')
    return stamp


def validate_owners(record, supervisor, vm_identity):
    """PID reuse after terminal supervision is not a still-running original owner."""
    require(record['schema'] == 'runtime-owned-exit-v1' and record['passed'] and
            record['all_owned_processes_exited'] and record['vm_name'] == vm_identity['name'] and
            record['supervisor_finished_utc'] == supervisor['finished_utc'], 'Wrong owner exit record')
    finished, observed = utc(record['supervisor_finished_utc']), utc(record['observed_utc'])
    require(utc(vm_identity['started_utc']) <= finished <= observed, 'Owner check precedes VM/terminal supervision')
    rows = record['owners']
    require(len(rows) == 4 and {row['role'] for row in rows} == {'supervisor', 'workload', 'guard', 'vm'} and
            len({row['pid'] for row in rows}) == 4 and
            all(type(row['pid']) is int and row['pid'] > 0 for row in rows), 'Missing or duplicate owner identity')
    expected = {'supervisor': supervisor['supervisor_pid'], 'workload': supervisor['workload_pid'],
                'guard': supervisor['guard_pid'], 'vm': vm_identity['pid']}
    for row in rows:
        if row['role'] in expected:
            require(row['pid'] == expected[row['role']], 'Owner PID differs from retained supervisor handle')
        if row['status'] == 'absent':
            require(row['observed_process'] is None, 'False PID absence')
        else:
            current = row['observed_process']
            require(row['status'] == 'pid-reused-after-completion' and isinstance(current['name'], str) and current['name'] and
                    finished < utc(current['created_utc']) <= observed, 'Original owner may still be live')
    require(type(record['all_pid_numbers_absent']) is bool and record['all_pid_numbers_absent'] ==
            all(row['status'] == 'absent' for row in rows), 'PID absence and owner exit were conflated')


def owner_rejections(record, supervisor, vm_identity):
    """Reject false exit evidence while permitting proven later PID reuse."""
    rejected = []
    for case in ('missing-owner', 'false-absence', 'unknown-role', 'duplicate-pid', 'foreign-vm-pid',
                 'live-owner', 'no-exit', 'early-observation'):
        row = copy.deepcopy(record)
        if case == 'missing-owner': row['owners'].pop()
        elif case == 'false-absence': row['all_pid_numbers_absent'] = not row['all_pid_numbers_absent']
        elif case == 'unknown-role': row['owners'][0]['role'] = 'unrelated'
        elif case == 'duplicate-pid': row['owners'][1]['pid'] = row['owners'][0]['pid']
        elif case == 'foreign-vm-pid':
            next(owner for owner in row['owners'] if owner['role'] == 'vm')['pid'] += 100000
        elif case == 'live-owner':
            row['owners'][0].update(status='pid-reused-after-completion',
                observed_process={'name': 'pwsh.exe', 'created_utc': row['supervisor_finished_utc']})
            row['all_pid_numbers_absent'] = False
        elif case == 'no-exit': row['all_owned_processes_exited'] = False
        else: row['observed_utc'] = '1970-01-01T00:00:00Z'
        try:
            validate_owners(row, supervisor, vm_identity)
        except (ValueError, KeyError, TypeError):
            rejected.append(case)
        else:
            raise AssertionError('Unsafe owner exit record accepted: ' + case)
    return rejected


def tcp_rejections(snapshot, tcp, topology):
    """Reject altered real metadata even if ordinary scalar heap totals still agree."""
    rejected = []
    cases = ('missing-tcp', 'fake-busy', 'missing-read', 'unused-read', 'wrong-state',
             'interior-pcb', 'fake-pcb-counter', 'foreign-heap', 'double-counted-capacity', 'different-stop')
    for case in cases:
        row = copy.deepcopy(snapshot)
        data = row['tcp_topology']
        if case == 'missing-tcp': row.pop('tcp_topology')
        elif case == 'fake-busy': data['observed'] = False
        elif case == 'missing-read': data['reads'].pop()
        elif case == 'unused-read': data['reads'].append(data['reads'][-1])
        elif case in ('wrong-state', 'interior-pcb'):
            pcb = data['pcbs'][0]
            kind = 'tcp_pcb_listen' if pcb['list'] == 'listen' else 'tcp_pcb'
            if case == 'wrong-state':
                address = pcb['address'] + tcp.layout['structures'][kind]['fields']['state']['offset']
                replacement = tcp.layout['states']['TIME_WAIT'] if pcb['state'] != 'TIME_WAIT' else tcp.layout['states']['LISTEN']
            else:
                from runtime_tcp_layout import LISTS
                address = tcp.layout['symbols'][LISTS[pcb['list']]]['address']
                replacement = pcb['address'] + 4
            for read in data['reads']:
                if read[0] == address:
                    read[2] = replacement.to_bytes(read[1], 'little').hex()
                    break
            else:
                raise AssertionError('Actual PCB metadata read is missing')
        elif case == 'fake-pcb-counter':
            address = tcp.layout['symbols']['num_tcp_pcb']['address']
            for read in data['reads']:
                if read[0] == address: read[2] = 'ffffffff'
        elif case == 'foreign-heap': data['heap_inventory_sha256'] = '00' * 32
        elif case == 'double-counted-capacity':
            data['attribution']['attributed_capacity_bytes'] += 4
            data['attribution']['unclassified_capacity_bytes'] -= 4
        else: data['guest_seconds'] += 1
        try:
            tcp.validate(row, topology)
        except (ValueError, KeyError, TypeError):
            rejected.append(case)
        else:
            raise AssertionError('Invalid TCP metadata accepted: ' + case)
    return rejected


def verify(path, root, rom, revision=None):
    """Check exact source/app/ELF/ROM and replay every snapshot in both full journals."""
    proof = json.loads(path.read_text())
    require(proof['schema_version'] == 4 and proof['passed'] and not proof['h10_checks_passed'] and
            not proof['all_functionality_verified'] and not proof['physical_hardware_tested'], 'Wrong TCP proof scope')
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent / row['file']).resolve()
        require(file.is_relative_to(path.parent.resolve()), 'Archive reference outside parity folder')
        packed = file.read_bytes()
        require(sha(packed) == row['gzip_sha256'], 'Compressed TCP evidence differs')
        raw = gzip.decompress(packed)
        require(sha(raw) == row['sha256'] and len(raw) == row['bytes'] and row['sha256'] not in blobs, 'TCP payload differs')
        blobs[row['sha256']] = raw
    files = {row['source']: blobs[row['sha256']] for row in proof['raw']}
    require(len(files) == len(proof['raw']), 'Duplicate TCP evidence label')
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'TCP sources differ')
    for name, digest in proof['source_pins'].items():
        require(sha(files['producer/' + name]) == digest, 'Archived TCP producer differs')
    app = (root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require(sha(app) == proof['app_sha256'] and sha(elf.read_bytes()) == proof['elf_sha256'] and
            app[176:208] == bytes.fromhex(proof['elf_sha256']) and sha(rom.read_bytes()) == proof['rom_sha256'], 'TCP app/ELF/ROM differs')
    validate_model(files['model/evidence.json'], proof)
    require(model_rejections(files['model/evidence.json'], proof) == proof['model_rejected_controls'], 'Model controls differ')
    prefix = proof['producer_root'].replace('\\', '/').rstrip('/') + '/'

    def check_inputs(report):
        """Tie archived units and runtime inputs to the same checked source bodies."""
        require(bool(report['inputs_sha256']), 'Missing TCP source identities')
        for name, digest in report['inputs_sha256'].items():
            normalized = name.replace('\\', '/')
            if normalized.startswith(prefix + 'Small_TV/'):
                require(proof['source_pins'][normalized[len(prefix):]] == digest, 'Unbound TCP source')
            elif normalized.endswith('/esp32c2_rev200_rom.elf'):
                require(digest == proof['rom_sha256'], 'Unbound ROM')
            elif normalized == prefix + '.build/small-tv-esp32c2/small_tv_reconstructed.elf':
                require(digest == proof['elf_sha256'], 'Unbound native ELF')

    unit = json.loads(files['unit/tcp-tests.json'])
    require(unit['passed'] and unit['tests'] == 33 and unit['inputs_unchanged'] and unit['no_vm_or_hardware_access'] and
            not unit['all_functionality_verified'] and not unit['failures'] and not unit['errors'], 'TCP host tests failed')
    check_inputs(unit)
    require(b'Ran 33 tests' in files['unit/tcp-tests.log'] and b'OK' in files['unit/tcp-tests.log'] and
            b'Ran 25 tests' in files['unit/analysis-tests.log'] and b'OK' in files['unit/analysis-tests.log'], 'Missing baseline/unit logs')
    tcp, topology = TcpSnapshot(elf), HeapTopology(rom, elf)
    require(unit['layout'] == tcp.layout, 'TCP unit ABI differs')
    results, rejected_count = [], len(proof['model_rejected_controls'])
    for run in proof['runs']:
        name = run['name'] + '/'
        read_json = lambda label: json.loads(files[name + label])
        report, supervisor = read_json('report.json'), read_json('supervisor.json')
        guard, uart, owners = read_json('uptime-guard.json'), read_json('uart-summary.json'), read_json('owners.json')
        vm_identity = read_json('vm-identity.json')
        start = read_json('start.json')
        require(start['completed_cycles_at_capture'] == 0 and start['capture_script_sha256'] == sha(files['unit/launch.ps1']), 'Missing genuine early capture')
        for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256', 'inputs_sha256', 'duration_requested_guest_seconds'):
            require(start[key] == report[key], 'TCP run differs from early identities')
        require(start['guard']['source_sha256'] == proof['source_pins']['Small_TV/src/tools/runtime_run_guard.py'], 'Guard source differs')
        require(report['app_sha256'] == proof['app_sha256'] and report['native_elf_sha256'] == proof['elf_sha256'] and
                report['qemu_sha256'] == proof['qemu_sha256'] and report['tcp_layout'] == tcp.layout and
                report['tcp_gate_layout'] == tcp.gate.layout, 'TCP runtime image or ABI differs')
        check_inputs(report)
        require(guard['vm_name'] == vm_identity['name'], 'Guard watches a different VM')
        validate_owners(owners, supervisor, vm_identity)
        require(owners['run'] == run['name'], 'Owner check belongs to another run')
        data = files[name + 'events.jsonl']
        folder = root / '.build/tcp-inventory-replay' / sha(data)
        folder.mkdir(parents=True, exist_ok=True)
        journal = folder / 'events.jsonl'
        journal.write_bytes(data)
        coverage = TcpCoverage(topology, tcp)
        evidence = journal_evidence(journal, proof['photo_chunks'], 2, require_weather=True, snapshot_check=coverage)
        evidence['tcp_coverage'] = coverage.summary()
        result = validate(report, evidence, guard, supervisor, uart, run['cycles'], 7)
        require(result == run['result'] and sha(canonical(coverage.series)) == run['tcp_series_sha256'], 'TCP coverage or attribution series differs')
        checks = {'runtime': rejections(report, evidence, guard, supervisor, uart, run['cycles'], 7),
                  'heap': topology_rejections(evidence['summary']['first_snapshot'], topology),
                  'tcp': tcp_rejections(evidence['summary']['first_snapshot'], tcp, topology),
                  'owners': owner_rejections(owners, supervisor, vm_identity)}
        require(checks == run['rejected_controls'], 'TCP rejection results differ')
        rejected_count += sum(map(len, checks.values()))
        results.append(result)
    require({row['cycles'] for row in results} == {4, 40}, 'Missing preflight or complete churn')
    return {'passed': True, 'runs': results, 'unsafe_controls_rejected': rejected_count, 'h10_checks_passed': False}


def main():
    """Inspect the selected checkpoint without connecting to a debugger or QMP."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.rom, args.source_revision)))


if __name__ == '__main__':
    main()
