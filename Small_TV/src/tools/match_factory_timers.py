"""Identify bounded factory power-management gaps and their timer wrappers."""
import argparse
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import Image, sha, startup_gp
from match_factory_sdk import classify as qualify_anchors, LIBRARIES
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match

CASES = (
    ('pm_dream_timeout_process', 'pm.o', 0x4207581e, 0x4207582e),
    ('pm_sleep_delay_timeout_process', 'pm.o', 0x4207582e, 0x4207584e),
    ('pm_disconnected_sleep_delay_timeout_process', 'pm.o', 0x4207584e, 0x4207586a),
    ('pm_coex_restart_timeout_process', 'pm.o', 0x4207586a, 0x42075896),
    ('pp_timer_coex_restart', 'pp_timer.o', 0x4207b07a, 0x4207b08c),
    ('pp_timer_disconnected_sleep_delay', 'pp_timer.o', 0x4207b0f6, 0x4207b108),
    ('pp_timer_sleep_delay', 'pp_timer.o', 0x4207b108, 0x4207b11a),
    ('pp_timer_coex_slice', 'pp_timer.o', 0x4207b11a, 0x4207b12c),
    ('pp_timer_dream', 'pp_timer.o', 0x4207b13e, 0x4207b150),
)


def load_models(directory):
    """Use named definitions from the exact previously qualified Wi-Fi archive."""
    data = (directory / 'libpp.a').read_bytes()
    assert sha(data) == LIBRARIES['libpp.a'], 'Changed SDK archive'
    wanted = {name: member for name, member, _, _ in CASES}
    result = {}
    for member, payload in members(data):
        if member not in set(wanted.values()):
            continue
        elf = ELFFile(io.BytesIO(payload))
        symbols = elf.get_section_by_name('.symtab')
        for symbol in symbols.iter_symbols():
            name = symbol.name
            if name in wanted and symbol['st_info']['type'] == 'STT_FUNC' and isinstance(symbol['st_shndx'], int):
                assert wanted[name] == member and name not in result, 'Ambiguous SDK timer symbol'
                result[name] = {'spec': model(payload, name), 'member': member, 'object_sha256': sha(payload)}
    assert set(result) == set(wanted), 'Missing SDK timer definition'
    return result


def anchored_match(spec, data, start, end, gp, global_anchors, local_anchors):
    """Reject lookalike wrappers whose relocations resolve to a different callee."""
    row = match(spec, data, start, gp)
    assert int(row['end'], 0) == end, 'Unexpected linked function boundary'
    checked = []
    for binding in row['symbol_bindings']:
        if binding['binding'] == 'STB_LOCAL':
            key = (binding['name'], binding['section'])
            expected = local_anchors.get(key)
        else:
            expected = global_anchors.get(binding['name'])
        if expected is not None:
            assert binding['address'] == expected, 'SDK symbol anchor differs: ' + binding['name']
            checked.append({'name': binding['name'], 'section': binding['section'], 'address': hex(expected)})
    assert checked, 'A relocated byte pattern alone does not identify a timer'
    row['checked_anchors'] = checked
    return row


def classify(factory, directory, replacements=None):
    """Re-qualify prior anchors before linking nine complete bounded SDK bodies."""
    image = Image(factory)
    previous = qualify_anchors(factory, directory)
    globals_ = {key: int(value, 0) for key, value in previous['shared_symbols'].items()}
    globals_.update({row['name']: int(row['start'], 0) for row in previous['functions']})
    globals_.update({name: start for name, _, start, _ in CASES})
    coex = next(row for row in previous['functions'] if row['name'] == 'pm_coex_slice_timeout_process')
    locals_ = {(row['name'], row['section']): row['address'] for row in coex['symbol_bindings'] if row['binding'] == 'STB_LOCAL'}
    models, rows = load_models(directory), []
    for name, member, start, end in CASES:
        item = models[name]
        data = image.read(start, len(item['spec']['code']) + 64, True)
        if replacements and name in replacements:
            data = replacements[name]
        row = anchored_match(item['spec'], data, start, end, startup_gp(image), globals_, locals_ if member == 'pm.o' else {})
        row.update(member=member, object_sha256=item['object_sha256'],
                   sdk_function_sha256=sha(item['spec']['code']), factory_function_sha256=sha(data[:end - start]))
        rows.append(row)
    return {'schema': 'factory-sdk-timers-v1', 'passed': True, 'factory_elf_sha256': sha(factory),
            'sdk_wifi_commit': previous['sdk_wifi_commit'], 'libraries': previous['libraries'],
            'anchor_functions': [{key: row[key] for key in ('name', 'start', 'end', 'factory_function_sha256')}
                                 for row in previous['functions']],
            'functions': rows, 'whole_image_completeness_proved': False,
            'semantic_equivalence_proved': False, 'physical_hardware_tested': False,
            'limitations': ['Nine named SDK functions are matched, not an exhaustive search over all possible library versions.',
                'Exact fixed bits, relocation permissions, local edges and shared symbol anchors are checked.',
                'No persistent Ghidra database, firmware, emulator or SDK is modified.',
                'Timer dispatch registration/reachability and equivalence with the native SDK remain separate checks.']}


def main():
    """Save a new numeric match report without overwriting prior evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--sdk-libraries', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve existing evidence'
    result = classify(args.elf.read_bytes(), args.sdk_libraries)
    sources = [Path(__file__), *(Path(__file__).parent / name for name in
               ('match_factory_sdk.py', 'audit_factory_xrefs.py', 'reverse/elf_archive.py', 'reverse/rv32_link_match.py'))]
    result['inputs_sha256'] = {str(file.resolve()): sha(file.read_bytes()) for file in sources}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': True, 'functions': [{key: row[key] for key in ('name', 'start', 'end')}
                                                   for row in result['functions']]}))


if __name__ == '__main__':
    main()
