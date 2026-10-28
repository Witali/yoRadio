"""Replay typed PM observations, preserving the failed factory recovery result."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile

from pm_runtime_test import run
from pm_runtime_metadata import decode
from audit_factory_xrefs import sha
from reverse.timer_event11_match import unique
from reverse.rv32_link_match import branch_target, link_register


def cancellation_caller(native):
    """Resolve the observed return address and both adjacent real caller instructions."""
    elf = ELFFile(io.BytesIO(native))
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    caller = unique(symbols, 'cnx_sta_leave')
    stop = unique(symbols, 'pm_stop')
    cancel = unique(symbols, 'pm_disable_keep_alive_timer')
    assert (caller['st_value'], caller['st_size']) == (0x42070aac, 628)
    calls = []
    for address, target in ((0x42070acc, stop), (0x42070ad0, cancel)):
        sections = [s for s in elf.iter_sections() if s['sh_flags'] & 4 and
                    s['sh_addr'] <= address < address + 4 <= s['sh_addr'] + s['sh_size']]
        assert len(sections) == 1
        section = sections[0]; offset = address - section['sh_addr']
        code = section.data()[offset:offset+4]
        assert link_register(code) == 1 and branch_target(code, address) == target['st_value']
        assert caller['st_value'] <= address < address + 4 <= caller['st_value'] + caller['st_size']
        calls.append(dict(address=address, target=target['st_value'], bytes_hex=code.hex()))
    return dict(name='cnx_sta_leave', start=caller['st_value'], size=caller['st_size'],
                calls=calls, cancel_return=0x42070ad4)


def observations(report, owners, uart, qualification, caller):
    """Reconstruct metadata from exact read order and require the actual observed outcomes."""
    assert report['passed'] is False and report['inputs_unchanged'] is True
    for key in ('full_runtime_lifecycle_proved', 'physical_hardware_tested', 'whole_image_completeness_proved'):
        assert report[key] is False
    assert report['qualification'] == qualification
    assert set(report['flows']) == {'factory', 'native'}
    assert len(owners) == 2 and all(not row['present'] for row in owners)
    assert {row['pid'] for row in owners} == {f['session']['pid'] for f in report['flows'].values()}
    decoded = {}
    for variant, flow in report['flows'].items():
        layout = qualification['layout']['layouts'][variant]
        assert flow['owned_stop_completed'] is True and flow['uart_clean'] is True
        assert flow['stop_exit_observed'] is True and flow['http_statuses'] == [200, 200, 200]
        assert uart[variant].count(b'ESP-ROM:esp32c2') == 1
        assert not any(token in uart[variant] for token in
                       (b'Guru Meditation', b'assert failed', b'abort() was called', b'Task watchdog'))
        rows = []
        for row in flow['observations']:
            reads = row['raw_reads']; index = 0
            assert len(reads) <= 32 and sum(item['size'] for item in reads) <= 256
            def memory(address, size):
                """Consume exactly the permitted decoder sequence, including pointer checks."""
                nonlocal index
                item = reads[index]; index += 1
                assert (item['address'], item['size']) == (address, size)
                data = bytes.fromhex(item['hex']); assert len(data) == size
                return data
            measured = decode(memory, layout)
            assert measured == row['metadata'] and index == len(reads)
            assert measured['timer_owner_bound'] is True
            assert measured['rom_pm_pointer'] == layout['pm']
            assert measured['osi_pointer'] == layout['osi_table']
            assert measured['legacy_marker'] == 0x12121212
            rows.append(measured)
        assert len({row['backend_handle'] for row in rows}) == 1
        assert all(b['guest_counter_us'] > a['guest_counter_us'] for a, b in zip(rows, rows[1:]))
        assert flow['observations'][1]['pc'] == layout['stop_exit']
        assert [row['pm_active'] for row in rows[:2]] == [1, 0]
        decoded[variant] = rows

    factory, native = report['flows']['factory'], report['flows']['native']
    assert [row['phase'] for row in factory['observations']] == ['connected', 'stop-return', 'disconnected', 'failure']
    assert factory['passed'] is False and 'TimeoutError' in factory['error'] and '/getclocktype' in factory['error']
    assert factory['cancellation_conclusion'] == 'inactive-before-stop'
    assert all(row['timer_armed'] is False for row in decoded['factory'])
    assert all(row['station_state'] == 2 for row in decoded['factory'])
    assert [row['pm_active'] for row in decoded['factory']] == [1, 0, 0, 0]
    assert [row['phase'] for row in native['observations']] == [
        'connected', 'stop-return', 'cancel-entry', 'cancel-return', 'disconnected', 'reconnected']
    assert native['passed'] is True and 'error' not in native
    assert native['cancellation_conclusion'] == 'still-armed-at-stop-exit'
    assert native['cancel_caller_return'] == caller['cancel_return']
    assert native['observations'][2]['pc'] == qualification['layout']['layouts']['native']['cancel_entry']
    assert native['observations'][3]['pc'] == caller['cancel_return']
    assert [row['timer_armed'] for row in decoded['native']] == [True, True, True, False, False, True]
    assert [row['pm_active'] for row in decoded['native']] == [1, 0, 0, 0, 0, 1]
    assert [row['station_state'] for row in decoded['native']] == [1, 1, 1, 1, 0, 1]
    assert len({row['backend_alarm_us'] for row in decoded['native'][:3]}) == 1
    assert decoded['native'][2]['backend_alarm_us'] > decoded['native'][3]['guest_counter_us']
    return dict(native_cancellation_observed=True, native_recovery_observed=True,
                factory_recovery_passed=False, factory_inactive_baseline_inconclusive=True,
                cancel_caller=caller)


def verify(path, root, factory, native, old_pp, new_pp, rom):
    """Hash raw reports and inputs, repeat host probes and reject altered conclusions."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'wifi-pm-runtime-evidence-v1' and proof['analysis_verified'] is True
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
    units, runtime = json.loads(files['units']), json.loads(files['runtime'])
    assert units.pop('inputs_unchanged') is True
    pins = {**units.pop('inputs_sha256'), **runtime['inputs_sha256']}
    for name, digest in pins.items(): assert sha(Path(name).read_bytes()) == digest, 'Changed input: '+name
    measured = json.loads(json.dumps(run(factory.read_bytes(), native.read_bytes(), old_pp, new_pp, rom.read_bytes())))
    assert units == measured
    owners = json.loads(files['owners'])
    uart = {variant: files['uart-'+variant] for variant in ('factory', 'native')}
    caller = cancellation_caller(native.read_bytes())
    result = observations(runtime, owners, uart, measured, caller)
    rejected = []
    for fault in ('fake-factory-pass', 'missing-cancel', 'wrong-caller', 'changed-alarm', 'unbound-rom',
                  'extra-read', 'owner-present', 'uart-reset', 'full-lifecycle-claim'):
        report, processes, logs = deepcopy(runtime), deepcopy(owners), dict(uart)
        rows = report['flows']['native']['observations']
        if fault == 'fake-factory-pass': report['flows']['factory']['passed'] = True
        elif fault == 'missing-cancel': rows[3]['metadata']['timer_armed'] = True
        elif fault == 'wrong-caller': report['flows']['native']['cancel_caller_return'] += 4
        elif fault == 'changed-alarm': rows[3]['raw_reads'][-1]['hex'] = '01'+'00'*7
        elif fault == 'unbound-rom': rows[2]['metadata']['rom_pm_pointer'] = 0
        elif fault == 'extra-read': rows[2]['raw_reads'].append(deepcopy(rows[2]['raw_reads'][0]))
        elif fault == 'owner-present': processes[0]['present'] = True
        elif fault == 'uart-reset': logs['native'] += b'ESP-ROM:esp32c2'
        else: report['full_runtime_lifecycle_proved'] = True
        try: observations(report, processes, logs, measured, caller)
        except (AssertionError, ValueError, IndexError): rejected.append(fault)
        else: raise AssertionError('Altered PM runtime evidence accepted: '+fault)
    return dict(analysis_verified=True, runtime=result, rejected_controls=rejected,
                predicate_cases=len(measured['predicates']), metadata_cases=len(measured['metadata']['cases']),
                full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False, physical_hardware_tested=False)


def main():
    """Replay archived read-only observations without launching or attaching a VM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    for name in ('proof', 'factory', 'native', 'old-pp', 'new-pp', 'rom'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.proof, args.root, args.factory, args.native, args.old_pp, args.new_pp, args.rom)))


if __name__ == '__main__': main()
