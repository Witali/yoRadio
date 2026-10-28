"""Replay a mailbox-gate checkpoint without attaching to any running VM."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import journal_evidence, require
from runtime_heap_topology import HeapTopology
from runtime_tcp_gate import TcpMailboxGate, tcp_gate_layout
from runtime_tcp_gate_qemu_test import snapshot_digest
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Check archived bytes before decoding or following their references."""
    return hashlib.sha256(data).hexdigest()


def validate(unit, probe, runtime, evidence, gate):
    """A successful workload alone cannot establish a safe TCP observation stop."""
    require(unit['passed'] and unit['tests'] == 15 and unit['inputs_unchanged'] and
            unit['no_vm_or_hardware_access'] and not unit['all_functionality_verified'] and
            not unit['failures'] and not unit['errors'], 'Mailbox host tests did not pass')
    require(probe['passed'] and probe['inputs_unchanged'] and not probe.get('error') and
            not probe['all_functionality_verified'] and not probe['h10_checks_passed'] and
            not probe['physical_hardware_tested'], 'Failed or overstated mailbox probe')
    require(unit['layout'] == probe['layout'] == gate.layout, 'Native mailbox ABI differs')
    require(runtime['schema_version'] == 6 and runtime['passed'] and runtime['inputs_unchanged'] and
            runtime['no_panic'] and not runtime.get('error') and not runtime.get('cleanup_error') and
            not runtime['all_functionality_verified'], 'Underlying runtime workload failed')
    require(runtime['cycles_requested'] == runtime['completed_cycles'] == evidence['cycles'] == 4 and
            runtime['outage_every_cycles'] == evidence['summary']['outages'] == 2 and
            runtime['summary'] == evidence['summary'] and runtime['journal']['sha256'] == evidence['sha256'] ==
            probe['runtime_journal_sha256'], 'Workload journal differs')
    require(runtime['rom_counter_crosscheck']['checks'] == evidence['rom_calls'] and
            evidence.get('verified_snapshots') == 5 and runtime['weather_coverage_passed'] and
            runtime['weather_observation'] == evidence['weather'], 'Incomplete heap/weather replay')
    uart = probe['uart']
    require(uart['passed'] and uart['rom_boots'] == 1 and not uart['errors'], 'UART reset or panic')
    originals, observations = evidence['summary']['snapshot_tail'], probe['snapshots']
    require(len(originals) == len(observations) == 5, 'Missing same-stop mailbox snapshots')
    for original, row in zip(originals, observations):
        require(row['label'] == original['label'] and row['guest_seconds'] == original['guest_seconds'] and
                row['runtime_snapshot_sha256'] == snapshot_digest(original), 'Mailbox sample paired with another stop')
        require(type(row['gate']['quiet']) is bool and all(type(read[0]) is type(read[1]) is int
                for read in row['gate']['reads']), 'Untyped mailbox transcript')
        require(gate.replay(row['gate']) == row['gate'], 'Mailbox transcript replay differs')
    quiet = sum(row['gate']['quiet'] for row in observations)
    require(type(probe['quiet_samples']) is int and probe['quiet_samples'] == quiet and quiet > 0,
            'No verified quiet mailbox observation')
    return {'passed': True, 'host_tests': 15, 'snapshots': 5, 'quiet_samples': quiet,
            'cycles': 4, 'outages': 2, 'http_requests': evidence['summary']['http_requests'],
            'elapsed_guest_seconds': runtime['elapsed_guest_seconds'], 'h10_checks_passed': False}


def rejections(unit, probe, runtime, evidence, gate):
    """Reject altered real observations beyond their outer content digests."""
    rejected = []
    for case in ('unit-failed', 'probe-failed', 'scope', 'layout', 'workload', 'missing-snapshot',
                 'different-stop', 'missing-read', 'extra-read', 'false-quiet-count', 'uart-reset', 'skipped-heap-replay'):
        u, p, r, e = copy.deepcopy((unit, probe, runtime, evidence))
        if case == 'unit-failed': u['passed'] = False
        elif case == 'probe-failed': p['passed'] = False
        elif case == 'scope': p['h10_checks_passed'] = True
        elif case == 'layout': p['layout']['symbols']['lwip_task']['address'] += 4
        elif case == 'workload': r['completed_cycles'] -= 1
        elif case == 'missing-snapshot': p['snapshots'].pop()
        elif case == 'different-stop': p['snapshots'][0]['runtime_snapshot_sha256'] = '00' * 32
        elif case == 'missing-read': p['snapshots'][0]['gate']['reads'].pop()
        elif case == 'extra-read': p['snapshots'][0]['gate']['reads'].append(p['snapshots'][0]['gate']['reads'][-1])
        elif case == 'false-quiet-count': p['quiet_samples'] += 1
        elif case == 'uart-reset': p['uart']['rom_boots'] = 2
        else: e.pop('verified_snapshots', None)
        try:
            validate(u, p, r, e, gate)
        except (ValueError, KeyError):
            rejected.append(case)
        else:
            raise AssertionError('Unsafe TCP mailbox evidence accepted: ' + case)
    return rejected


def verify(path, root, rom, revision=None):
    """Recompute same-stop bindings and all saved scalar/list metadata reads."""
    proof = json.loads(path.read_text())
    require(proof['schema'] == 'tcp-mailbox-gate-v1' and proof['passed'] and
            not proof['all_functionality_verified'] and not proof['h10_checks_passed'], 'Invalid mailbox proof')
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent / row['file']).resolve()
        require(file.is_relative_to(path.parent.resolve()), 'Archive reference outside parity folder')
        packed = file.read_bytes()
        require(sha(packed) == row['gzip_sha256'], 'Compressed mailbox evidence differs')
        raw = gzip.decompress(packed)
        require(sha(raw) == row['sha256'] and len(raw) == row['bytes'], 'Mailbox payload differs')
        blobs[row['sha256']] = raw
    files = {row['source']: blobs[row['sha256']] for row in proof['raw']}
    require(len(files) == len(proof['raw']), 'Duplicate mailbox payload label')
    require(source_hashes(root, proof['source_pins'], revision) == proof['source_pins'], 'Mailbox sources differ')
    for name, digest in proof['source_pins'].items():
        require(sha(files['producer/' + name]) == digest, 'Archived mailbox producer differs')
    app = (root / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin').read_bytes()
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require(sha(app) == proof['app_sha256'] and sha(elf.read_bytes()) == proof['elf_sha256'] and
            app[176:208] == bytes.fromhex(proof['elf_sha256']) and sha(rom.read_bytes()) == proof['rom_sha256'],
            'Mailbox app/ELF/ROM identity differs')
    unit, probe, runtime = [json.loads(files[name]) for name in ('unit/report.json', 'probe/report.json', 'runtime/report.json')]
    require(sha(files['runtime/report.json']) == probe['runtime_report_sha256'] and
            runtime['qemu_sha256'] == proof['qemu_sha256'] and runtime['app_sha256'] == proof['app_sha256'] and
            runtime['native_elf_sha256'] == proof['elf_sha256'], 'Mailbox executable identity differs')
    prefix = proof['producer_root'].replace('\\', '/').rstrip('/') + '/'
    for report in (unit, probe, runtime):
        for name, digest in report['inputs_sha256'].items():
            name = name.replace('\\', '/')
            if name.startswith(prefix + 'Small_TV/'):
                require(proof['source_pins'][name[len(prefix):]] == digest, 'Unbound mailbox input')
            elif name == prefix + '.build/small-tv-esp32c2/small_tv_reconstructed.elf':
                require(digest == proof['elf_sha256'], 'Unbound mailbox ELF')
    require(b'Ran 15 tests' in files['unit/tests.log'] and b'OK' in files['unit/tests.log'], 'Missing mailbox unit log')
    owners = json.loads(files['probe/processes.json'])
    require(owners['passed'] and owners['all_absent'] and owners['vm_pid'] > 0, 'Mailbox VM remains live')
    gate = TcpMailboxGate(tcp_gate_layout(elf))
    topology = HeapTopology(rom, elf)
    data = files['runtime/events.jsonl']
    folder = root / '.build/tcp-gate-replay' / sha(data)
    folder.mkdir(parents=True, exist_ok=True)
    journal = folder / 'events.jsonl'
    journal.write_bytes(data)
    evidence = journal_evidence(journal, proof['photo_chunks'], 2, require_weather=True, snapshot_check=topology.validate)
    result = validate(unit, probe, runtime, evidence, gate)
    rejected = rejections(unit, probe, runtime, evidence, gate)
    require(result == proof['result'] and rejected == proof['rejected_controls'], 'Mailbox proof conclusion differs')
    return dict(result, unsafe_controls_rejected=len(rejected))


def main():
    """Read the selected checkpoint without starting, stopping or observing a VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.rom, args.source_revision)))


if __name__ == '__main__':
    main()
