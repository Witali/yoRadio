"""Verify the final timer guard, SDK callback table and both linked ingress paths."""
import argparse
import hashlib
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match, branch_target, link_register

ROM_SHA = '289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9'


def sha(data):
    """Bind every compiled or library input to its exact bytes."""
    return hashlib.sha256(data).hexdigest()


def verify(elf_bytes, app_bytes, libraries, rom_bytes):
    """Check real caller relocations, not just the presence of a linker wrap flag."""
    elf = ELFFile(io.BytesIO(elf_bytes))
    assert elf.elfclass == 32 and elf.little_endian and elf['e_machine'] == 'EM_RISCV'
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    def symbol(name, function=False):
        """Require a unique defined native symbol, including absolute ROM globals."""
        rows = [row for row in symbols if row.name == name and row['st_value'] and
                (not function or row['st_info']['type'] == 'STT_FUNC')]
        assert len(rows) == 1, 'Missing/ambiguous timer guard symbol: ' + name
        return rows[0]
    def body(row):
        """Read the exact initialized extent of a named ELF function or object."""
        section = elf.get_section(row['st_shndx'])
        offset = row['st_value'] - section['sh_addr']
        assert 0 <= offset < offset + row['st_size'] <= section['sh_size']
        return section.data()[offset:offset + row['st_size']]
    guard = symbol('__wrap_pp_timer_do_process', True)
    vendor = symbol('pp_timer_do_process', True)
    assert guard['st_value'] != vendor['st_value'] and 0 < guard['st_size'] <= 512
    assert not any(row.name == '__real_pp_timer_do_process' and row['st_shndx'] == 'SHN_UNDEF' for row in symbols)
    assert sha(elf_bytes) == app_bytes[176:208].hex(), 'App descriptor does not bind this ELF'
    table_symbol = symbol('g_pp_timer_info')
    table = body(table_symbol)
    assert len(table) == 120 and table[-8:] == bytes(8), 'Requalify timer event count/sentinel'
    entries = []
    for event in range(14):
        offset = event * 8
        assert int.from_bytes(table[offset:offset+4], 'little') == event, 'Requalify non-dense timer IDs'
        target = int.from_bytes(table[offset+4:offset+8], 'little')
        owners = [row for row in symbols if row['st_value'] == target and row['st_info']['type'] == 'STT_FUNC']
        assert len(owners) == 1 and owners[0]['st_size'] > 0
        entries.append({'id': event, 'target': hex(target), 'name': owners[0].name})
    assert symbol('g_osi_funcs_p')['st_value'] == 0x3fcdfdd8, 'Requalify the C2 Wi-Fi adapter global'
    archive_hashes, objects, references = {}, {}, []
    for archive in sorted(libraries.glob('*.a')):
        raw = archive.read_bytes()
        archive_hashes[archive.name] = sha(raw)
        for member, data in members(raw):
            if data[:4] != b'\x7fELF':
                continue
            obj = ELFFile(io.BytesIO(data))
            table_ = obj.get_section_by_name('.symtab')
            if table_ is None:
                continue
            functions = [row for row in table_.iter_symbols() if row['st_info']['type'] == 'STT_FUNC' and isinstance(row['st_shndx'], int)]
            relevant = False
            for reloc in obj.iter_sections():
                if not isinstance(reloc, RelocationSection):
                    continue
                names = obj.get_section(reloc['sh_link'])
                for row in reloc.iter_relocations():
                    if names.get_symbol(row['r_info_sym']).name != 'pp_timer_do_process':
                        continue
                    owners = [entry.name for entry in functions if entry['st_shndx'] == reloc['sh_info'] and
                              entry['st_value'] <= row['r_offset'] < entry['st_value'] + entry['st_size']]
                    assert len(owners) == 1, 'Unqualified additional SDK timer reference'
                    references.append({'archive': archive.name, 'member': member, 'owner': owners[0],
                                       'offset': row['r_offset'], 'type': row['r_info_type']})
                    relevant = True
            if relevant or (archive.name == 'libpp.a' and member == 'pp_timer.o'):
                assert (archive.name, member) not in objects
                objects[(archive.name, member)] = data
    assert len(references) == 3 and {row['owner'] for row in references} == {'ppTask', 'wdev_funcs_init'}, 'Requalify all timer ingress references'
    gp = symbol('__global_pointer$')['st_value']
    callers = []
    for name, member, kind in (('wdev_funcs_init', 'wdev.o', 'data'),):
        native = symbol(name, True)
        spec = model(objects[('libpp.a', member)], name)
        matched = match(spec, body(native), native['st_value'], gp)
        assert int(matched['end'], 0) == native['st_value'] + native['st_size']
        targets = [row for row in matched['symbol_bindings'] if row['name'] == 'pp_timer_do_process']
        assert len(targets) == 1 and targets[0]['kind'] == kind and targets[0]['address'] == guard['st_value'], 'A linked ingress bypasses the timer guard'
        callers.append(matched)
    # ppTask's archive body is replaced by a ROM trampoline in this build.
    # Verify the actual ROM event-8 path and the table slot it uses instead.
    assert symbol('ppTask', True)['st_shndx'] == 'SHN_ABS'
    assert symbol('ppTask', True)['st_value'] == 0x40001c44
    assert sha(rom_bytes) == ROM_SHA, 'Unqualified ESP32-C2 ROM'
    rom = ELFFile(io.BytesIO(rom_bytes))
    def rom_read(address, size):
        """Read exact initialized bytes from the independently pinned ROM ELF."""
        for section in rom.iter_sections():
            offset = address - section['sh_addr']
            if section['sh_flags'] & 2 and 0 <= offset < offset + size <= section['sh_size']:
                return section.data()[offset:offset + size]
        raise ValueError('Missing qualified ROM bytes')
    trampoline = rom_read(0x40001c44, 4)
    assert link_register(trampoline) == 0 and branch_target(trampoline, 0x40001c44) == 0x40046eec
    assert rom_read(0x40046f24, 4) == bytes.fromhex('3704ce3f')  # s0 = 0x3fce0000
    assert int.from_bytes(rom_read(0x3ff4553c + 8*4, 4), 'little') == 0x40046fb8
    block = rom_read(0x40046fb8, 12)
    assert block == bytes.fromhex('8327c4dd83a7471632458297')
    assert symbol('pp_wdev_funcs')['st_value'] == 0x3fcdfddc
    wdev = callers[0]
    transfers = {row['object_offset']: row for row in wdev['transformations']}
    # These instruction offsets belong to the fully matched current SDK body.
    # Runtime instruction tests also verify its successful-allocation block
    # writes the wrapped target to the same +356 slot read by ROM.
    assert transfers[1052]['object_bytes'] == '74d3'
    rom_ingress = {'rom_sha256': ROM_SHA, 'trampoline': '0x40001c44', 'ppTask_body': '0x40046eec',
        'event_id': 8, 'event_table': '0x3ff4553c', 'block_start': '0x40046fb8', 'block_end': '0x40046fc4',
        'block_bytes': block.hex(), 'wdev_global': '0x3fcdfddc', 'wdev_timer_slot_offset': 356,
        'init_begin': transfers[62]['pc'], 'init_end': hex(int(transfers[1052]['pc'],0) + 2),
        'init_synthetic_successful_allocation_register': 10,
        'instruction_path_verified': False}
    matched = match(model(objects[('libpp.a', 'pp_timer.o')], 'pp_timer_do_process'), body(vendor), vendor['st_value'], gp)
    assert int(matched['end'], 0) == vendor['st_value'] + vendor['st_size']
    table_bindings = [row for row in matched['symbol_bindings'] if row['name'] == '.LANCHOR1' and row['kind'] == 'data']
    assert len(table_bindings) == 1 and table_bindings[0]['address'] == table_symbol['st_value']
    return {'schema': 'small-tv-wifi-timer-guard-links-v1', 'passed': True,
            'elf_sha256': sha(elf_bytes), 'app_sha256': sha(app_bytes), 'gp': hex(gp),
            'guard': {'start': hex(guard['st_value']), 'end': hex(guard['st_value'] + guard['st_size']), 'code_sha256': sha(body(guard))},
            'functions': [matched], 'table': {'address': hex(table_symbol['st_value']), 'bytes_hex': table.hex(), 'entries': entries},
            'sdk_archive_sha256': archive_hashes, 'sdk_ingress_relocations': references, 'linked_callers': callers,
            'rom_ingress': rom_ingress,
            'instruction_guard_behavior_verified': False, 'all_functionality_verified': False,
            'limitations': ['This proves selected SDK ingress linkage and table layout; guard instruction behavior needs its separate execution test.',
                'No hardware or long-duration qualification is claimed for this new build.']}


def main():
    """Write a new post-link identity report for the exact candidate firmware."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = [Path(__file__), *(Path(__file__).parent / name for name in ('reverse/elf_archive.py', 'reverse/rv32_link_match.py'))]
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in sources}
    result = verify(args.elf.read_bytes(), args.app.read_bytes(), args.sdk_libraries, args.rom.read_bytes())
    assert pins == {str(path.resolve()): sha(path.read_bytes()) for path in sources}
    result['inputs_sha256'] = pins
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'sdk_references': len(result['sdk_ingress_relocations']),
                      'linked_ingress_bodies': len(result['linked_callers']), 'guard_bytes': int(result['guard']['end'],0)-int(result['guard']['start'],0)}))


if __name__ == '__main__':
    main()
