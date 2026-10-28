"""Execute the compiled Wi-Fi timer guard and vendor body against every byte ID."""
import argparse
import io
import json
from pathlib import Path
import sys

from elftools.elf.elffile import ELFFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from verify_wifi_timer_guard import verify, sha
from timer_dispatch_instructions import DispatcherProbe
from wifi_timer_guard_rom import verify_rom_path


class GuardedProbe(DispatcherProbe):
    """Execute both real bodies; preserve the original fixture's explicit external stubs."""
    def __init__(self, layout, read):
        """Add the exact linked guard bytes without changing the vendor dispatcher."""
        super().__init__(layout, read)
        self.vendor_range = (self.start, self.end)
        self.start, self.end = (int(layout['guard'][key], 0) for key in ('start', 'end'))
        self.map(self.start, self.end-self.start)
        self.cpu.mem_write(self.start, read(self.start, self.end-self.start))

    def execute(self, cpu, address, size, context):
        """Count real vendor entries, then use the qualified guard/stub allowlist."""
        if self.vendor_range[0] <= address < self.vendor_range[1]:
            self.trace['instructions'] += 1
            if address == self.vendor_range[0]:
                self.trace['vendor_entries'] = self.trace.get('vendor_entries', 0) + 1
            return
        super().execute(cpu, address, size, context)


def verify_behavior(elf_bytes, app_bytes, libraries, rom_bytes):
    """Require correct linkage and zero table reads for every rejected event."""
    layout = verify(elf_bytes, app_bytes, libraries, rom_bytes)
    elf = ELFFile(io.BytesIO(elf_bytes))
    def read(address, size):
        """Copy exactly one initialized executable range into the private test CPU."""
        for section in elf.iter_sections():
            offset = address - section['sh_addr']
            if section['sh_flags'] & 4 and 0 <= offset < offset + size <= section['sh_size']:
                return section.data()[offset:offset + size]
        raise ValueError('Missing compiled timer guard code')
    probe = GuardedProbe(layout, read)
    traces = []
    for event in range(256):
        row = probe.call(event)
        valid = event < 14
        assert row['return'] == int(valid) and row['frees'] == [probe.MESSAGE]
        assert not row['logs'] and not row['out_of_table_reads']
        assert row.get('vendor_entries', 0) == int(valid)
        assert row['callbacks'] == ([{'id': event, 'message': probe.MESSAGE}] if valid else [])
        if not valid:
            assert not row['table_reads'], 'Rejected ID reached the vendor table prefetch'
        traces.append(row)
    null = probe.call(null=True)
    assert null.get('vendor_entries') == 1 and null['return'] == 0 and null['logs'] == 1
    assert not null['frees'] and not null['table_reads']
    returned_zero = probe.call(4, callback_result=0)
    assert returned_zero['return'] == 1 and returned_zero['frees'] == [probe.MESSAGE]
    assert returned_zero.get('vendor_entries') == 1 and not returned_zero['out_of_table_reads']
    # This real vendor body is the failure control. The test must still detect
    # the exact unguarded prefetch reproduced before the fix.
    unprotected = DispatcherProbe(layout, read).call(255)
    assert len(unprotected['out_of_table_reads']) == 1 and unprotected['return'] == 0
    initialized_data = [(section['sh_addr'], section.data()) for section in elf.iter_sections()
                        if section['sh_flags'] & 2 and not section['sh_flags'] & 4 and
                        section['sh_type'] != 'SHT_NOBITS' and section['sh_size']]
    beacon = [row for row in elf.get_section_by_name('.symtab').iter_symbols() if row.name == 'ptr_beacon_offset_funcs' and row['st_value']]
    assert len(beacon) == 1 and beacon[0]['st_size'] == 4
    rom = verify_rom_path(layout, read, GuardedProbe, initialized_data, beacon[0]['st_value'])
    return {'passed': True, 'elf_sha256': layout['elf_sha256'], 'app_sha256': layout['app_sha256'],
            'all_256_ids_executed': True, 'behavior_cases': 518, 'rom_ingress': rom,
            'invalid_ids_rejected_before_vendor_entry': 242, 'rejected_message_frees_each': 1,
            'guarded_out_of_table_reads': 0, 'unguarded_vendor_control_defect_detected': True,
            'trace_sha256': sha(json.dumps(traces, sort_keys=True, separators=(',', ':')).encode()),
            'null_message': null, 'callback_zero': returned_zero, 'unguarded_control': unprotected,
            'linked_sdk_ingress_verified': True, 'instruction_guard_behavior_verified': True,
            'no_vm_or_hardware_access': True, 'all_functionality_verified': False, 'h10_checks_passed': False,
            'limitations': ['Guard and vendor instructions are exact; transitive callback/log/free calls are explicit host stubs.',
                'Actual network boot/churn, final full suite and hardware acceptance remain separate requirements.']}


def main():
    """Save one new result for the exact compiled candidate and checker source identities."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    src = Path(__file__).resolve().parents[1]
    files = [Path(__file__), src / 'tests/wifi_timer_guard_rom.py', src / 'tests/timer_dispatch_instructions.py', src / 'tools/verify_wifi_timer_guard.py',
             src / 'tools/reverse/elf_archive.py', src / 'tools/reverse/rv32_link_match.py',
             src / 'app/network/wifi_timer.c', src / 'app/CMakeLists.txt']
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in files}
    result = verify_behavior(args.elf.read_bytes(), args.app.read_bytes(), args.sdk_libraries, args.rom.read_bytes())
    assert pins == {str(path.resolve()): sha(path.read_bytes()) for path in files}
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('passed', 'behavior_cases', 'guarded_out_of_table_reads', 'linked_sdk_ingress_verified')}))


if __name__ == '__main__':
    main()
