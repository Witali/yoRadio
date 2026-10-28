"""Replay saved registration instructions and typed observations without a VM."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from timer_registration_test import run
from timer_registration_metadata import decode
from audit_factory_xrefs import sha


def runtime(runtime_report, owners, uart, qualification):
    """Reconstruct each observation from its exact, whitelisted numeric reads."""
    assert runtime_report['passed'] and runtime_report['inputs_unchanged']
    assert set(runtime_report['flows']) == {'factory', 'native'}
    assert all(not owner['present'] for owner in owners)
    assert {owner['pid'] for owner in owners} == {flow['session']['pid'] for flow in runtime_report['flows'].values()}
    for variant, flow in runtime_report['flows'].items():
        assert flow['passed'] and flow['uart_clean'] and flow['owned_stop_completed']
        assert uart[variant].count(b'ESP-ROM:esp32c2') == 1
        assert not any(word in uart[variant] for word in (b'Guru Meditation', b'assert failed', b'abort() was called'))
        recorded = deepcopy(flow['metadata']); reads = recorded.pop('raw_reads'); index = 0
        assert sum(row['size'] for row in reads) <= 1024
        def memory(address, size):
            """Consume precisely the requested read sequence, rejecting hidden extra reads."""
            nonlocal index
            row = reads[index]; index += 1
            assert (row['address'], row['size']) == (address, size)
            raw = bytes.fromhex(row['hex']); assert len(raw) == size
            return raw
        layout = qualification['layouts'][variant]
        assert decode(memory, layout) == recorded and index == len(reads)
        prior = layout['prior']
        assert recorded['osi_pointer'] == prior['osi_table']['address']
        assert recorded['osi_table_sha256'] == prior['osi_table']['sha256']
        assert recorded['post_callback'] and not recorded['post_callback'] % 2
        assert recorded['timer_word4'] == 0x12121212
        assert 0x3fca0000 <= recorded['timer_word16'] < 0x3fce0000
    return dict(passed=True, variants=2, observed_osi_versions=[8,9], original_vm_owners_absent=True)


def verify(path, root, factory, native, old_pp, new_pp, old_net, new_net):
    """Hash sources and raw records, then recompute all accepted evidence."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'wifi-timer-registration-evidence-v1' and proof['passed']
    assert not proof['full_runtime_lifecycle_proved'] and not proof['physical_hardware_tested']
    for name, expected in proof['source_pins'].items():
        file = (root / name).resolve()
        assert file.is_relative_to(root.resolve()) and sha(file.read_bytes()) == expected
    files = {}
    for name, reference in proof['files'].items():
        file = (path.parent / reference['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        compressed = file.read_bytes(); assert sha(compressed) == reference['gzip_sha256']
        assert len(compressed) < 262144
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream: raw = stream.read(2097153)
        assert len(raw) == reference['bytes'] <= 2097152 and sha(raw) == reference['sha256']
        files[name] = raw
    saved = json.loads(files['instructions'])
    assert saved.pop('inputs_unchanged') is True
    saved_inputs = saved.pop('inputs_sha256')
    # JSON object keys are strings, including numeric timer addresses. Compare
    # the same serialized representation that the producer actually archives.
    actual = json.loads(json.dumps(run(factory.read_bytes(), native.read_bytes(), old_pp, new_pp, old_net, new_net)))
    assert saved == actual
    runtime_report, owners = json.loads(files['runtime']), json.loads(files['owners'])
    for name, expected in {**saved_inputs, **runtime_report['inputs_sha256']}.items():
        assert sha(Path(name).read_bytes()) == expected, 'Original input changed: ' + name
    uart = {variant: files['uart-' + variant] for variant in ('factory', 'native')}
    measured = runtime(runtime_report, owners, uart, actual['qualification'])
    rejected = []
    for fault in ('osi-pointer', 'osi-table-bytes', 'timer-magic', 'extra-read', 'owner-still-present', 'uart-reset'):
        report, processes, logs = deepcopy(runtime_report), deepcopy(owners), dict(uart)
        metadata = report['flows']['native']['metadata']
        if fault == 'osi-pointer': metadata['osi_pointer'] += 4
        elif fault == 'osi-table-bytes': metadata['raw_reads'][-1]['hex'] = '00' * 480
        elif fault == 'timer-magic': metadata['timer_word4'] = 0
        elif fault == 'extra-read': metadata['raw_reads'].append(deepcopy(metadata['raw_reads'][0]))
        elif fault == 'owner-still-present': processes[0]['present'] = True
        else: logs['native'] += b'ESP-ROM:esp32c2'
        try: runtime(report, processes, logs, actual['qualification'])
        except (AssertionError, IndexError, ValueError): rejected.append(fault)
        else: raise AssertionError('Altered runtime evidence accepted: ' + fault)
    assert len(rejected) == 6
    return dict(passed=True, registration_cases=sum(r['registration_cases'] for r in actual['instructions'].values()),
                static_controls=actual['rejected_controls'], runtime=measured, rejected_runtime_controls=rejected,
                full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Read saved sources/records and original binaries; launch no process or VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'old-pp', 'new-pp', 'old-net', 'new-net'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native,
                            args.old_pp, args.new_pp, args.old_net, args.new_net)))


if __name__ == '__main__': main()
