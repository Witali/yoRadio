"""Observe the mailbox gate in a separate real four-cycle Small TV VM."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_evidence import audit_run
from runtime_heap_topology import HeapTopology
import runtime_qemu
from runtime_tcp_gate import TcpMailboxGate, tcp_gate_layout


def digest(path):
    """Bind this additional host sampler independently of the unchanged workload."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_digest(row):
    """Pair extra metadata with the exact same stopped workload snapshot."""
    return hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    """Wrap only a host read callback; never alter code, PC, RAM or network state."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yoradio', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.yoradio.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    elf = root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    layout = tcp_gate_layout(elf)
    gate = TcpMailboxGate(layout)
    names = ('runtime_tcp_gate_qemu_test.py', 'runtime_tcp_gate.py', 'runtime_memory.py',
             'runtime_heap_topology.py', 'runtime_tlsf_instructions.py', 'runtime_instruction_image.py',
             'runtime_qemu.py')
    sources = [Path(__file__).with_name(name) for name in names]
    sources += [elf, root / 'Small_TV/src/tools/runtime_evidence.py']
    pins = {str(path.resolve()): digest(path) for path in sources}
    report = dict(passed=False, scope=__doc__, all_functionality_verified=False,
                  h10_checks_passed=False, physical_hardware_tested=False,
                  limitations='Mailbox gate only; no TCP list/buffer attribution, independent UART guard or leak conclusion.',
                  inputs_sha256=pins, layout=layout, snapshots=[])
    original, original_args = HeapTopology.sample, sys.argv
    records = []

    def capture(topology, reader, aggregate):
        """Keep the existing heap checks and append bounded reads at the same stop."""
        result = original(topology, reader, aggregate)
        records.append({'heap': aggregate, 'gate': gate.sample(reader.memory)})
        return result

    try:
        HeapTopology.sample = capture
        sys.argv = [runtime_qemu.__file__, '--yoradio', str(root), '--dependency-root', str(args.dependency_root.resolve()),
                    '--qemu-root', str(args.qemu_root.resolve()), '--qemu', str(args.qemu.resolve()),
                    '--output', str(out / 'runtime'), '--cycles', '4', '--interval-seconds', '1.2',
                    '--outage-every', '2', '--heap-topology']
        status = runtime_qemu.main()
        audit = audit_run(out / 'runtime', root, extra_roots=(args.dependency_root.resolve(), args.qemu.resolve().parent))
        assert status == 0 and audit['terminal'] and audit['heap_topology_verified']
        assert audit['evidence']['cycles'] == 4
        events = [json.loads(line) for line in (out / 'runtime/events.jsonl').read_text().splitlines()]
        snapshots = [event['data'] for event in events if event['kind'] == 'snapshot']
        assert len(snapshots) == len(records) == 5
        for row, extra in zip(snapshots, records):
            assert row['heap'] == extra['heap']
            observation = extra['gate']
            assert gate.replay(observation) == observation
            report['snapshots'].append({'label': row['label'], 'guest_seconds': row['guest_seconds'],
                                       'runtime_snapshot_sha256': snapshot_digest(row), 'gate': observation})
        report['quiet_samples'] = sum(row['gate']['quiet'] for row in report['snapshots'])
        assert report['quiet_samples'] > 0, 'No actual mailbox quiescence observed'
        report['uart'] = audit['uart']
        report['runtime_report_sha256'] = digest(out / 'runtime/report.json')
        report['runtime_journal_sha256'] = digest(out / 'runtime/events.jsonl')
        report['passed'] = True
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
    finally:
        HeapTopology.sample, sys.argv = original, original_args
        report['inputs_unchanged'] = all(digest(Path(path)) == sha for path, sha in pins.items())
        report['passed'] &= report['inputs_unchanged']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report.get(key) for key in ('passed', 'quiet_samples', 'inputs_unchanged', 'error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
