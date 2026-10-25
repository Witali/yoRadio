"""Characterize literal timer dispatch, including invalid-ID memory reads."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

from elftools.elf.elffile import ELFFile
import elftools
import unicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha
from audit_timer_dispatch import audit, sdk_model, table_entries
from timer_dispatch_instructions import DispatcherProbe


def instruction_cases(layout, read):
    """Exercise all byte IDs, malformed state and ownership with explicit external stubs."""
    probe = DispatcherProbe(layout, read)
    observations, examples, outside, cases = [], {}, [], 0
    for event in range(256):
        row = probe.call(event)
        valid = event < 14
        assert row['return'] == int(valid) and row['frees'] == [probe.MESSAGE]
        assert row['logs'] == int(not valid)
        assert row['callbacks'] == ([{'id': event, 'message': probe.MESSAGE}] if valid else [])
        assert len(row['out_of_table_reads']) == int(event >= 15)
        if row['out_of_table_reads']:
            outside.append(event)
            assert row['out_of_table_reads'][0]['size'] == 1
            assert int(row['out_of_table_reads'][0]['address'], 0) == probe.table + event * 8
        if event in (0, 13, 14, 15, 255):
            examples[str(event)] = row
        observations.append(row)
        cases += 1
    for event in range(15, 256):
        # Force the out-of-table prefetched byte to equal the invalid event ID;
        # the later bounds check must still reject it without calling anything.
        row = probe.call(event, poison_prefetch=True)
        assert row['return'] == 0 and not row['callbacks'] and row['frees'] == [probe.MESSAGE]
        assert row['logs'] == 1 and len(row['out_of_table_reads']) == 1
        observations.append(row)
        cases += 1
    null = probe.call(null=True)
    assert null['return'] == 0 and null['logs'] == 1 and not null['frees'] and not null['table_reads']
    shuffled = bytearray(probe.table_bytes)
    shuffled[24:32], shuffled[72:80] = shuffled[72:80], shuffled[24:32]
    fallback = probe.call(3, table=shuffled)
    assert fallback['callbacks'] == [{'id': 3, 'message': probe.MESSAGE}] and fallback['return'] == 1
    assert fallback['frees'] == [probe.MESSAGE] and not fallback['logs'] and not fallback['out_of_table_reads']
    missing = bytearray(probe.table_bytes)
    missing[36:40] = bytes(4)
    no_callback = probe.call(4, table=missing)
    assert no_callback['return'] == 1 and not no_callback['callbacks'] and no_callback['frees'] == [probe.MESSAGE]
    callback_zero = probe.call(4, callback_result=0)
    assert callback_zero['return'] == 1 and callback_zero['callbacks'] and callback_zero['frees'] == [probe.MESSAGE]
    observations.extend((null, fallback, no_callback, callback_zero))
    cases += 4
    return {'cases': cases, 'all_256_event_ids_executed': True, 'external_calls_stubbed': True,
            'invalid_ids_with_pre_bound_out_of_table_read': outside,
            'vendor_table_prefetch_defect_present': outside == list(range(15, 256)),
            'trace_sha256': hashlib.sha256(json.dumps(observations, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'examples': examples, 'null_message': null, 'permuted_table': fallback,
            'null_callback': no_callback, 'callback_zero': callback_zero}


def table_controls(report, sdk):
    """Reject corrupt initializer data independently of the image's outer digest."""
    table = report['factory']['table']
    data, address = bytes.fromhex(table['bytes_hex']), int(table['address'], 0)
    anchors = {row['name']: int(row['target'], 0) for row in table['entries']}
    rejected = []
    for case in ('truncated-table', 'wrong-event-id', 'duplicate-id', 'nonzero-sentinel',
                 'null-callback', 'real-neighbor-callback', 'misaligned-callback'):
        raw = bytearray(data)
        if case == 'truncated-table': raw = raw[:-1]
        elif case == 'wrong-event-id': raw[0] = 255
        elif case == 'duplicate-id': raw[8:12] = raw[:4]
        elif case == 'nonzero-sentinel': raw[-1] = 1
        elif case == 'null-callback': raw[36:40] = bytes(4)
        elif case == 'real-neighbor-callback': raw[36:40] = raw[44:48]
        else: raw[36] ^= 1
        try:
            table_entries(raw, sdk, address, anchors)
        except (AssertionError, ValueError, KeyError):
            rejected.append(case)
        else:
            raise AssertionError('Corrupt timer initializer accepted: ' + case)
    return rejected


def verify(factory, native, directory, saved):
    """Rebuild the static audit before executing both exact dispatcher bodies."""
    assert audit(factory, native, directory) == saved, 'Saved dispatch audit differs'
    image = Image(factory)
    elf = ELFFile(io.BytesIO(native))
    def native_read(address, size):
        """Read only the exact native executable extent selected by the verified audit."""
        for section in elf.iter_sections():
            offset = address - section['sh_addr']
            if section['sh_flags'] & 4 and 0 <= offset < offset + size <= section['sh_size']:
                return section.data()[offset:offset + size]
        raise ValueError('Missing native dispatcher code')
    result = {'factory': instruction_cases(saved['factory'], lambda address, size: image.read(address, size, True)),
              'native': instruction_cases(saved['native'], native_read)}
    result['table_rejected_controls'] = table_controls(saved, sdk_model(directory))
    result.update(passed=True, no_vm_or_hardware_access=True, production_bug_fixed=False,
                  all_functionality_verified=False, h10_checks_passed=False,
                  unicorn_version=unicorn.__version__, pyelftools_version=elftools.__version__,
                  limitations=['Literal dispatch is executed; transitive handlers, log and free are declared stubs.',
                      'Invalid-ID prefetch is a reproduced vendor defect, not an accepted production behavior.',
                      'Neither these host tests nor transient Ghidra metadata replace runtime/hardware acceptance.'])
    return result


def main():
    """Save exact host observations and source identities in a new artifact."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--factory-elf', type=Path, required=True)
    parser.add_argument('--native-elf', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = [Path(__file__), root / 'tests/timer_dispatch_instructions.py', root / 'tools/audit_timer_dispatch.py',
             *(root / 'tools' / name for name in ('audit_factory_xrefs.py', 'match_factory_sdk.py', 'match_factory_timers.py',
               'reverse/elf_archive.py', 'reverse/rv32_link_match.py', 'reverse/native_timer_match.py'))]
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in files}
    result = verify(args.factory_elf.read_bytes(), args.native_elf.read_bytes(), args.sdk_libraries,
                    json.loads(args.audit.read_bytes()))
    assert pins == {str(path.resolve()): sha(path.read_bytes()) for path in files}, 'Sources changed during replay'
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'instruction_cases': sum(result[name]['cases'] for name in ('factory','native')),
        'table_rejections': len(result['table_rejected_controls']), 'production_bug_fixed': False,
        'prefetch_defect_present': {name: result[name]['vendor_table_prefetch_defect_present'] for name in ('factory','native')}}))


if __name__ == '__main__':
    main()
