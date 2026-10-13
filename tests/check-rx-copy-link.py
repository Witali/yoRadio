"""Audit effective copied-RX interposition in an ESP32-C3 diagnostic ELF."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from elftools.elf.elffile import ELFFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--objdump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    checks = {}
    with args.elf.open('rb') as stream:
        elf = ELFFile(stream)
        assert elf.elfclass == 32 and elf.little_endian
        symbols = {s.name: s for s in elf.get_section_by_name('.symtab').iter_symbols()}
        for name in ('wlanif_input', 'pbuf_free', 'mem_free', 'pbuf_alloc',
                     '__wrap_wlanif_input', '__wrap_pbuf_alloc', '__wrap_mem_free',
                     'rx_buffer_diagnostic_poll', 'owners', 'copy_scope'):
            assert name in symbols and symbols[name]['st_shndx'] != 'SHN_UNDEF', name
        assert symbols['owners']['st_size'] == 512
        assert symbols['copy_scope']['st_info']['type'] == 'STT_TLS'
        checks['owner_table_bytes'] = 512
        checks['task_local_scope_bytes'] = symbols['copy_scope']['st_size']
        # Derive the member offset from this ELF's SDK debug types.
        offsets = set()
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                if die.tag != 'DW_TAG_structure_type' or not name or name.value != b'esp_netif_netstack_lwip_vanilla_config':
                    continue
                for member in die.iter_children():
                    attr = member.attributes.get('DW_AT_name')
                    if attr and attr.value == b'input_fn':
                        offsets.add(member.attributes['DW_AT_data_member_location'].value)
        assert len(offsets) == 1, offsets
        input_offset = offsets.pop()
        def symbol_data(name):
            symbol = symbols[name]
            section = elf.get_section(symbol['st_shndx'])
            start = symbol['st_value'] - section['sh_addr']
            return section.data()[start:start + symbol['st_size']]
        configurations = {}
        for kind in ('sta', 'ap', 'nan'):
            name = 's_wifi_netif_config_' + kind
            if name not in symbols:
                assert kind != 'sta', 'Station netstack missing'
                continue
            raw = symbol_data(name)
            address = int.from_bytes(raw[input_offset:input_offset + 4], 'little')
            assert address == symbols['__wrap_wlanif_input']['st_value'], name
            global_name = '_g_esp_netif_netstack_default_wifi_' + kind
            if global_name in symbols:
                assert int.from_bytes(symbol_data(global_name), 'little') == symbols[name]['st_value']
            configurations[kind] = hex(address)
        checks['netstack_input_member_offset'] = input_offset
        checks['netstack_wrapped_inputs'] = configurations
    edges = {
        '__wrap_wlanif_input': 'wlanif_input',
        'wlanif_input': '__wrap_pbuf_alloc',
        '__wrap_pbuf_alloc': 'pbuf_alloc',
        'pbuf_free': '__wrap_mem_free',
        '__wrap_mem_free': 'mem_free',
    }
    for caller, target in edges.items():
        text = subprocess.check_output([str(args.objdump), '-d', '--disassemble=' + caller,
                                        str(args.elf)], text=True)
        (args.output / (caller + '.txt')).write_text(text)
        # Match actual jump/call instructions, not headings or arbitrary strings.
        calls = re.findall(r'\b(?:jal|j|jalr)\s+[^\n]*?<([^>]+)>', text)
        assert target in calls, (caller, target, calls)
        if caller in ('wlanif_input', 'pbuf_free'):
            assert target.removeprefix('__wrap_') not in calls, (caller, calls)
        if caller.startswith('__wrap_'):
            assert caller not in calls, 'Recursive interposition: ' + caller
        checks[caller + '_calls'] = calls
    report = {'result': 'PASS', 'elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
              'checks': checks, 'scope': 'Linked SDK input pointer and allocation/final-free call edges; no hardware timing claim'}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
