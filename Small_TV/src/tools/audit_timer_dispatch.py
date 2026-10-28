"""Tie initialized Wi-Fi timer tables to complete dispatcher and callback bodies."""
import argparse
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from audit_factory_xrefs import Image, sha, startup_gp
from match_factory_sdk import LIBRARIES
from match_factory_timers import classify as prior_matches
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match
from reverse.native_timer_match import NATIVE_SHA

DISPATCH = ('pp_timer_do_process', 'pp_timer_register_post_cb', 'pp_timer_process')
# These are explicit observed SDK-version names, not an equivalence assertion.
NATIVE_NAMES = {'pp_timer_max_idle': 'pp_timer_keep_alive',
                'pm_max_idle_timeout_process': 'pm_keep_alive_timeout_process'}


def sdk_model(directory):
    """Read table constants and typed relocations from the exact qualified SDK object."""
    library = (directory / 'libpp.a').read_bytes()
    assert sha(library) == LIBRARIES['libpp.a'], 'Changed SDK timer archive'
    objects = [data for name, data in members(library) if name == 'pp_timer.o']
    assert len(objects) == 1
    raw = objects[0]
    elf = ELFFile(io.BytesIO(raw))
    table = elf.get_section_by_name('.data.g_pp_timer_info')
    assert table['sh_size'] == 120 and table['sh_flags'] & 3 == 3
    callbacks = {}
    for reloc in elf.iter_sections():
        if not isinstance(reloc, RelocationSection) or elf.get_section(reloc['sh_info']).name != table.name:
            continue
        symbols = elf.get_section(reloc['sh_link'])
        for row in reloc.iter_relocations():
            assert row['r_info_type'] == 1 and row['r_addend'] == 0 and row['r_offset'] not in callbacks
            callbacks[row['r_offset']] = symbols.get_symbol(row['r_info_sym']).name
    assert set(callbacks) == set(range(4, 112, 8)) and len(set(callbacks.values())) == 14
    body = table.data()
    assert [int.from_bytes(body[i:i+4], 'little') for i in range(0, 112, 8)] == list(range(14))
    assert body[112:] == bytes(8)
    specs = {name: model(raw, name) for name in (*callbacks.values(), *DISPATCH)}
    return {'object_sha256': sha(raw), 'bytes': body, 'callbacks': callbacks, 'specs': specs}


def table_entries(data, sdk, address, anchors):
    """Keep every non-relocation byte and all previously qualified callback targets exact."""
    assert len(data) == len(sdk['bytes'])
    fixed = bytearray(data)
    rows = []
    for offset, name in sorted(sdk['callbacks'].items()):
        target = int.from_bytes(data[offset:offset+4], 'little')
        assert target and target % 2 == 0
        if name in anchors:
            assert target == anchors[name], 'Known timer callback target differs'
        fixed[offset:offset+4] = bytes(4)
        rows.append({'id': int.from_bytes(data[offset-4:offset], 'little'), 'name': name,
                     'cell': hex(address + offset), 'target': hex(target)})
    assert bytes(fixed) == sdk['bytes'], 'Timer IDs, padding or sentinel differ'
    return rows


def checked_bindings(row, globals_, locals_):
    """Make shared symbol values agree; local names are scoped to this SDK object."""
    for binding in row['symbol_bindings']:
        if binding['binding'] == 'STB_LOCAL':
            key = (binding['name'], binding['section'])
            assert key not in locals_ or locals_[key] == binding['address'], 'Object-local timer anchor differs'
            locals_[key] = binding['address']
        else:
            name = binding['name']
            assert name not in globals_ or globals_[name] == binding['address'], 'Shared timer global/callee differs'
            globals_[name] = binding['address']


def search(image, spec, gp, seed, suffix=False):
    """Bound candidate decoding with actual fixed instruction bytes, then match the full body."""
    found = {}
    for section in image.sections:
        if not section['execute']:
            continue
        offset = 0
        while (offset := section['data'].find(seed, offset)) >= 0:
            address = section['start'] + offset
            offset += 2
            starts = (address + len(seed) - len(spec['code']), address + len(seed) - len(spec['code']) + 4) if suffix else (address,)
            for start in starts:
                try:
                    row = match(spec, image.read(start, len(spec['code']) + 64, True), start, gp)
                    if suffix and int(row['end'], 0) != address + len(seed):
                        continue
                except (AssertionError, ValueError):
                    continue
                found[start] = row
    return list(found.values())


def factory_dispatch(factory, directory, sdk):
    """Anchor the full initialized table and connect register/post/dispatch to all 14 callbacks."""
    image, prior = Image(factory), prior_matches(factory, directory)
    gp = startup_gp(image)
    anchors = {row['name']: int(row['start'], 0) for row in prior['functions']}
    table_offset = next(offset for offset, name in sdk['callbacks'].items() if name == 'pp_timer_coex_slice')
    needle = anchors['pp_timer_coex_slice'].to_bytes(4, 'little')
    tables = []
    for section in image.sections:
        if section['execute']:
            continue
        offset = 0
        while (offset := section['data'].find(needle, offset)) >= 0:
            address = section['start'] + offset - table_offset
            offset += 4
            try:
                data = image.read(address, 120)
                entries = table_entries(data, sdk, address, anchors)
            except (AssertionError, ValueError):
                continue
            tables.append((address, data, entries))
    assert len(tables) == 1, 'Missing/ambiguous initialized timer table'
    address, data, entries = tables[0]
    dispatcher = search(image, sdk['specs'][DISPATCH[0]], gp, sdk['specs'][DISPATCH[0]]['code'][:6])
    dispatcher = [row for row in dispatcher if any(binding['section'] == 39 and binding['address'] == address
                   for binding in row['symbol_bindings'] if binding['binding'] == 'STB_LOCAL')]
    assert len(dispatcher) == 1, 'Dispatcher does not bind to this timer table'
    processes = search(image, sdk['specs'][DISPATCH[2]], gp, sdk['specs'][DISPATCH[2]]['code'][-4:], True)
    registers = search(image, sdk['specs'][DISPATCH[1]], gp, sdk['specs'][DISPATCH[1]]['code'][-4:], True)
    pairs = [(register, process) for register in registers for process in processes
             if register['symbol_bindings'] == process['symbol_bindings']]
    assert len(pairs) == 1, 'Register/post callback storage is not uniquely paired'
    register, process = pairs[0]
    globals_, locals_ = {}, {}
    for row in prior['functions']:
        for binding in row['symbol_bindings']:
            if binding['binding'] != 'STB_LOCAL':
                globals_[binding['name']] = binding['address']
    functions = []
    for entry in entries:
        start = int(entry['target'], 0)
        spec = sdk['specs'][entry['name']]
        functions.append(match(spec, image.read(start, len(spec['code']) + 64, True), start, gp))
    functions.extend((dispatcher[0], register, process))
    for row in functions:
        checked_bindings(row, globals_, locals_)
        row['factory_function_sha256'] = sha(image.read(int(row['start'], 0), row['linked_bytes'], True))
    return {'factory_elf_sha256': sha(factory), 'gp': hex(gp), 'functions': functions,
            'table': {'address': hex(address), 'bytes_hex': data.hex(), 'entries': entries, 'sentinel_offset': 112},
            'post_callback_slot': hex(register['symbol_bindings'][0]['address']),
            'register_shape_candidates': len(registers), 'post_shape_candidates': len(processes)}


def native_dispatch(data, directory, sdk):
    """Resolve each native table callback and dispatcher relocation through the real symbol table."""
    assert sha(data) == NATIVE_SHA
    elf = ELFFile(io.BytesIO(data))
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    def symbol(name):
        """Reject undefined or ambiguous targets instead of choosing the first symbol."""
        actual = NATIVE_NAMES.get(name, name)
        if actual != name:
            assert not any(row.name == name and row['st_value'] for row in symbols), 'Unexpected retained old SDK name'
        rows = [row for row in symbols if row.name == actual and row['st_value']]
        assert len(rows) == 1, 'Missing/ambiguous native timer symbol: ' + name
        return rows[0]
    def body(row):
        """Read only an exact initialized ELF extent."""
        section = elf.get_section(row['st_shndx'])
        offset = row['st_value'] - section['sh_addr']
        assert 0 <= offset < offset + row['st_size'] <= section['sh_size']
        return section.data()[offset:offset + row['st_size']]
    gp = symbol('__global_pointer$')['st_value']
    table = symbol('g_pp_timer_info')
    anchors = {name: symbol(name)['st_value'] for name in sdk['callbacks'].values()}
    raw = body(table)
    entries = table_entries(raw, sdk, table['st_value'], anchors)
    globals_, locals_, functions = {}, {('.LANCHOR1', 39): table['st_value']}, []
    for name in sdk['specs']:
        native = symbol(name)
        row = match(sdk['specs'][name], body(native), native['st_value'], gp)
        assert int(row['end'], 0) == native['st_value'] + native['st_size']
        for binding in row['symbol_bindings']:
            if binding['binding'] != 'STB_LOCAL':
                assert binding['address'] == symbol(binding['name'])['st_value'], 'Wrong native timer target'
        checked_bindings(row, globals_, locals_)
        row['native_function_sha256'] = sha(body(native))
        row['native_symbol_name'] = native.name
        functions.append(row)
    return {'native_elf_sha256': sha(data), 'gp': hex(gp), 'functions': functions,
            'table': {'address': hex(table['st_value']), 'bytes_hex': raw.hex(), 'entries': entries, 'sentinel_offset': 112},
            'post_callback_slot': hex(locals_[('.LANCHOR3', 38)]),
            'explicit_sdk_version_names': NATIVE_NAMES,
            'renamed_callee_semantic_equivalence_proved': False}


def audit(factory, native, directory):
    """Keep initial registration structure separate from transitive runtime reachability."""
    sdk = sdk_model(directory)
    return {'schema': 'wifi-timer-dispatch-v1', 'passed': True, 'sdk_object_sha256': sdk['object_sha256'],
            'factory': factory_dispatch(factory, directory, sdk), 'native': native_dispatch(native, directory, sdk),
            'whole_image_completeness_proved': False, 'semantic_equivalence_proved': False,
            'physical_hardware_tested': False,
            'limitations': ['Initialized table identity and complete selected bodies are verified, not every runtime mutation.',
                'Callback callees and event producers still require transitive reachability analysis.',
                'No firmware, emulator, SDK or persistent Ghidra database is changed.']}


def main():
    """Save a new reproducible numeric report without writing to any device."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--factory-elf', type=Path, required=True)
    parser.add_argument('--native-elf', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.factory_elf.read_bytes(), args.native_elf.read_bytes(), args.sdk_libraries)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'factory_callbacks': len(result['factory']['table']['entries']),
                      'factory_bodies': len(result['factory']['functions']), 'native_bodies': len(result['native']['functions'])}))


if __name__ == '__main__':
    main()
