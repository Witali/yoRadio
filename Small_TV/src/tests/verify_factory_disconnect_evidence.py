"""Replay the bounded factory disconnect trace without declaring recovery successful."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from pm_runtime_metadata import decode
from pm_runtime_test import run
from audit_factory_xrefs import Image, sha
from reverse.rv32_link_match import branch_target, link_register
from reverse.station_leave_match import qualify

BOUNDARIES = ('pm-stop-ret', 'pm-stop-caller', 'station-leave-tail', 'station-leave-caller',
              'crypto-call', 'crypto-return', 'sdk-callback-call', 'sdk-callback-return',
              'disconnect-post-call', 'disconnect-post-return')
PCS = (0x42076790, 0x4206c1d2, 0x4206c438, 0x4206dfa4, 0x4206dfb2,
       0x4206dfba, 0x4206dfd6, 0x4206dfd8, 0x4206e03e, 0x4206e042)


def trace(report, owner, uart, layout, image):
    """Check exact typed reads and completed boundaries, retaining the observation limit."""
    assert report['passed'] is False and report['inputs_unchanged'] is True
    assert not any(report[key] for key in
                   ('full_runtime_lifecycle_proved', 'physical_hardware_tested', 'whole_image_completeness_proved'))
    assert 'error' not in report and 'error' not in report['controller']
    assert report['owned_stop_completed'] and report['controller_stopped'] and report['uart_clean']
    assert report['observation_timeout'] is True and not report.get('observation_limit', False)
    assert owner['pid'] == report['session']['pid'] and owner['name'] == report['session']['name']
    assert owner['present'] is False
    assert uart.count(b'ESP-ROM:esp32c2') == 1
    assert not any(token in uart for token in (b'Guru Meditation', b'assert failed', b'abort() was called'))
    assert report['controller']['online'] is True
    elapsed = (report['controller']['online_counter'] - report['controller']['offline_counter']) & 0xffffffff
    assert 1000000 <= elapsed < 5000000
    for address, raw in report['code'].items(): assert image.read(int(address, 0), 8, True).hex() == raw
    assert '0x4200c602' in report['code'] and '0x4200c656' in report['code']
    assert tuple(row['boundary'] for row in report['events']) == BOUNDARIES
    assert tuple(row['pc'] for row in report['events']) == PCS
    assert report['pm_stop_caller'] == 0x4206c1d2 and report['station_leave_caller'] == 0x4206dfa4
    assert report['events'][0]['ra'] == 0x4206c1d2 and report['events'][2]['ra'] == 0x4206dfa4
    for address, target in ((0x4206c1ce, 0x4207661c), (0x4206dfa0, 0x4206c1ae), (0x4206e03e, 0x42067b46)):
        code = image.read(address, 4, True)
        assert link_register(code) == 1 and branch_target(code, address) == target
    assert report['events'][6]['indirect_target'] == 0x42085452
    assert report['events'][8]['posted_event_id'] == 5 and report['events'][8]['posted_event_bytes'] == 41
    assert report['events'][9]['post_return_value'] == 0
    rows = [report['baseline'], *report['events'], report['last']]
    metadata = []
    for row in rows:
        reads = row['raw_reads']; index = 0
        assert len(reads) <= 32 and sum(item['size'] for item in reads) <= 256
        def memory(address, size):
            """Consume the recorded request sequence exactly, without a fallback reader."""
            nonlocal index
            item = reads[index]; index += 1
            assert (item['address'], item['size']) == (address, size)
            data = bytes.fromhex(item['hex']); assert len(data) == size
            return data
        value = decode(memory, layout)
        assert value == row['metadata'] and index == len(reads)
        assert value['timer_owner_bound'] and value['rom_pm_pointer'] == layout['pm']
        assert value['osi_pointer'] == layout['osi_table'] and value['timer_armed'] is False
        assert value['station_state'] == 2
        metadata.append(value)
    assert len({row['backend_handle'] for row in metadata}) == 1
    assert [row['pm_active'] for row in metadata] == [1]+[0]*11
    assert all(b['guest_counter_us'] > a['guest_counter_us'] for a, b in zip(metadata, metadata[1:]))
    assert metadata[-1]['guest_counter_us'] > report['controller']['online_counter'] + 1000000
    return dict(observed_boundaries=10, sdk_event_post_return=0, application_callback_observed=False,
                absence_scope='Bounded observation only; not proof that a callback can never execute',
                factory_recovery_passed=False)


def verify(path, root, factory, native, old_pp, new_pp, old_net, new_net, rom):
    """Requalify full SDK bodies, replay saved reads and reject misleading alterations."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'factory-disconnect-evidence-v1' and proof['analysis_verified'] is True
    assert proof['factory_recovery_passed'] is False and proof['full_runtime_lifecycle_proved'] is False
    assert proof['physical_hardware_tested'] is False and proof['whole_image_completeness_proved'] is False
    for name, digest in proof['source_pins'].items():
        file = (root/name).resolve()
        assert file.is_relative_to(root.resolve()) and sha(file.read_bytes()) == digest
    files = {}
    for name, ref in proof['files'].items():
        file = (path.parent/ref['file']).resolve(); assert file.is_relative_to(path.parent.resolve())
        compressed = file.read_bytes()
        assert len(compressed) <= 262144 and sha(compressed) == ref['gzip_sha256']
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream: raw = stream.read(2097153)
        assert len(raw) == ref['bytes'] <= 2097152 and sha(raw) == ref['sha256']
        files[name] = raw
    static = qualify(factory.read_bytes(), native.read_bytes(), old_net, new_net)
    assert json.loads(files['bodies']) == json.loads(json.dumps(static))
    runtime, owner = json.loads(files['runtime']), json.loads(files['owner'])
    for name, digest in runtime['inputs_sha256'].items(): assert sha(Path(name).read_bytes()) == digest
    units = run(factory.read_bytes(), native.read_bytes(), old_pp, new_pp, rom.read_bytes())
    layout = units['layout']['layouts']['factory']; image = Image(factory.read_bytes())
    result = trace(runtime, owner, files['uart'], layout, image)
    rejected = []
    for fault in ('fake-recovery', 'post-error', 'wrong-event', 'wrong-caller', 'extra-read', 'short-read',
                  'missing-boundary', 'owner-present', 'uart-reset'):
        report, process, uart = deepcopy(runtime), deepcopy(owner), files['uart']
        if fault == 'fake-recovery': report['passed'] = True
        elif fault == 'post-error': report['events'][9]['post_return_value'] = 1
        elif fault == 'wrong-event': report['events'][8]['posted_event_id'] = 6
        elif fault == 'wrong-caller': report['events'][2]['ra'] += 4
        elif fault == 'extra-read': report['last']['raw_reads'].append(deepcopy(report['last']['raw_reads'][0]))
        elif fault == 'short-read': report['last']['raw_reads'][-1]['hex'] = '00'
        elif fault == 'missing-boundary': report['events'].pop(3)
        elif fault == 'owner-present': process['present'] = True
        else: uart += b'ESP-ROM:esp32c2'
        try: trace(report, process, uart, layout, image)
        except (AssertionError, ValueError, IndexError): rejected.append(fault)
        else: raise AssertionError('Altered disconnect evidence accepted: '+fault)
    return dict(analysis_verified=True, runtime=result, matched_bytes={v:r['linked_bytes'] for v,r in static['functions'].items()},
                rejected_controls=rejected, full_runtime_lifecycle_proved=False,
                physical_hardware_tested=False, whole_image_completeness_proved=False)


def main():
    """Use original immutable files and archived observations; never attach to a running VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'old-pp', 'new-pp', 'old-net', 'new-net', 'rom'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.old_pp, args.new_pp,
                            args.old_net, args.new_net, args.rom)))


if __name__ == '__main__': main()
