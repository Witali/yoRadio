"""Read-only selected Vorbis/Ogg binary audit; never imports benchmark verifiers."""
import datetime
import hashlib
import json
import pathlib
import re
import struct

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parent.parent
COMPONENT = pathlib.Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec')
CAPTURE = json.loads((OUT / 'capture.json').read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return sha(path.read_bytes())


assert not (OUT / 'report.json').exists(), 'Audit outputs are immutable after finalization'
extra_inputs = [
    COMPONENT / 'README.md',
    ROOT / 'idf/esp32-cyd2usb-native/build-c3-transfer/project_description.json',
    pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2/tools/cmake/version.cmake'),
    pathlib.Path(__file__).resolve(),
]
supplement = {'captured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'purpose': 'Additional metadata captured before derived analysis; original capture remains immutable.',
              'input_sha256': {}, 'snapshot_map': {}}
for path in extra_inputs:
    raw = path.read_bytes()
    digest = sha(raw)
    supplement['input_sha256'][str(path)] = digest
    snapshot = OUT / 'snapshots' / digest
    if not snapshot.exists():
        snapshot.write_bytes(raw)
    supplement['snapshot_map'][str(path)] = str(snapshot.relative_to(OUT))
save('supplement.json', supplement)


def sections(raw):
    assert raw[:6] == b'\x7fELF\x01\x01'
    offset = struct.unpack_from('<I', raw, 32)[0]
    size, count, names = struct.unpack_from('<HHH', raw, 46)
    records = [struct.unpack_from('<10I', raw, offset + i * size) for i in range(count)]
    name_entry = records[names]
    names_data = raw[name_entry[4]:name_entry[4] + name_entry[5]]
    return {names_data[e[0]:].split(b'\0', 1)[0].decode(): raw[e[4]:e[4] + e[5]]
            for e in records if e[1] != 8}  # no NOBITS payload


def member(board, basename):
    matches = [(label, item) for label, item in CAPTURE['members'].items()
               if label.startswith(board + '-') and item['member'] == basename]
    assert len(matches) == 1, (board, basename)
    return matches[0]


inventory = {'interpretation': 'Native nm output sizes are function bytes, not heap/performance measurements. All addresses are member/section relative. Undefined entries are external dependencies, not missing-symbol proof.',
             'members': {}, 'selected_wrapper_entrypoints': {}}
call_references = {'interpretation': 'Xtensa ASM_EXPAND relocation at a literal-load instruction identifies a symbolic reference; paired callx8 is retained in raw disassembly. This is a static reference graph, not a runtime trace. Function-pointer callbacks and generic dispatch require linked-target verification.',
                   'functions': {}}
for label, item in CAPTURE['members'].items():
    raw = (OUT / item['payload']).read_bytes()
    assert sha(raw) == item['sha256']
    sec = sections(raw)
    nm = (OUT / 'tool-output' / (label + '-nm.txt')).read_text()
    symbols = []
    for line in nm.splitlines():
        match = re.fullmatch(r'\s*(?:(\w+)\s+(\w+)\s+)?([A-Za-z])\s+(\S+)', line)
        if match:
            address, size, kind, name = match.groups()
            # No deferred private-owner inspection, even by symbol name.
            if 'aac' in name.lower():
                continue
            symbols.append({'name': name, 'kind': kind,
                            'section_relative_address': address,
                            'bytes': int(size, 16) if size else None})
    inventory['members'][label] = {
        'archive': item['archive'], 'member': item['member'],
        'sha256': item['sha256'], 'elf_machine': item['elf_machine'],
        'dwarf_present': item['dwarf_present'], 'symbols': symbols,
        'compiler_comment_strings': sec.get('.comment', b'').decode(errors='replace').split('\0'),
        'parser_embedded_version': sec.get('.rodata.esp_es_parser_get_version.str1.4', b'').decode(errors='replace').strip('\0') or None,
    }
    if label.startswith('esp32-'):
        asm = (OUT / 'tool-output' / (label + '-disasm.txt')).read_text()
        current = None
        for number, line in enumerate(asm.splitlines(), 1):
            start = re.fullmatch('Disassembly of section \\.text\\.(.+):', line)
            if start:
                current = start[1]
            elif line.startswith('Disassembly of section '):
                current = None
            reference = re.search(r'^\s*([0-9a-f]+): R_XTENSA_ASM_EXPAND\s+(\S+)', line)
            if current and reference and 'aac' not in reference[2].lower():
                call_references['functions'].setdefault(current, []).append({
                    'target': reference[2], 'instruction_offset': '0x' + reference[1],
                    'raw': 'tool-output/' + label + '-disasm.txt', 'line': number})

wrappers = ['esp_vorbis_dec_open', 'esp_vorbis_dec_register', 'esp_vorbis_dec_decode',
            'esp_audio_simple_dec_open', 'esp_audio_simple_dec_process', 'esp_audio_simple_dec_reset',
            'esp_es_parse_frame', 'esp_ogg_parse_frame', 'media_lib_module_realloc']
for name in wrappers:
    by_board = {}
    for board in ['esp32', 'esp32c3']:
        definitions, references = [], []
        for label, item in inventory['members'].items():
            if not label.startswith(board + '-'):
                continue
            for symbol in item['symbols']:
                if symbol['name'] == name:
                    (references if symbol['kind'] == 'U' else definitions).append({'member': label, **symbol})
        by_board[board] = {'selected_definitions': definitions, 'selected_undefined_references': references}
        if name != 'media_lib_module_realloc':
            assert len(definitions) == 1, (board, name, definitions)
        else:
            assert references, (board, name)
    inventory['selected_wrapper_entrypoints'][name] = by_board
save('symbol-inventory.json', inventory)
save('xtensa-call-references.json', call_references)

# Full selected functions, with original source-output line binding; no absolute-address patching.
selected_functions = {
    'esp_vorbis_dec.c.obj': ['esp_vorbis_dec_open', 'esp_vorbis_dec_decode', 'esp_vorbis_dec_close', 'esp_vorbis_dec_register'],
    'dsp.c.obj': ['vorbis_dsp_create', 'vorbis_dsp_destroy', 'vorbis_dsp_restart', 'vorbis_dsp_synthesis'],
    'info.c.obj': ['vorbis_info_init', 'vorbis_info_clear', '_vorbis_unpack_info', '_vorbis_unpack_books'],
    'codebook.c.obj': ['vorbis_book_clear', '_make_words', '_make_decode_table', 'decode_map'],
    'floor0.c.obj': ['floor0_free_info', 'floor0_info_unpack'],
    'floor1.c.obj': ['floor1_free_info', 'floor1_info_unpack', 'floor1_inverse1'],
    'mapping0.c.obj': ['mapping_clear_info', 'mapping_info_unpack'],
    'res012.c.obj': ['res_clear_info', 'res_unpack'],
    'bitwise.c.obj': ['tremor_oggpack_readinit', 'tremor_oggpack_read', 'tremor_oggpack_eop'],
    'esp_audio_simple_dec.c.obj': ['esp_audio_simple_dec_open', 'esp_audio_simple_dec_process', 'esp_audio_simple_dec_reset', 'esp_audio_simple_dec_close'],
    'ogg_parser.c.obj': ['parse_vorbis_header', 'append_packet', 'esp_ogg_parse_frame'],
    'esp_es_parse.c.obj': ['esp_es_parse_frame'],
}
excerpt_map = {}
for basename, wanted in selected_functions.items():
    for board in ['esp32', 'esp32c3']:
        label, _ = member(board, basename)
        original = 'tool-output/' + label + '-disasm.txt'
        lines = (OUT / original).read_text().splitlines()
        headers = [(i, re.fullmatch(r'Disassembly of section (.+):', line)[1])
                   for i, line in enumerate(lines) if re.fullmatch(r'Disassembly of section (.+):', line)]
        for function in wanted:
            matches = [(j, i, section) for j, (i, section) in enumerate(headers)
                       if section == '.text.' + function]
            assert len(matches) == 1, (board, basename, function)
            j, begin, section = matches[0]
            end = headers[j + 1][0] if j + 1 < len(headers) else len(lines)
            target = 'excerpts/' + board + '-' + function + '.txt'
            data = '\n'.join([f'{original}:{begin + 1}', *lines[begin:end]]) + '\n'
            (OUT / target).parent.mkdir(exist_ok=True)
            (OUT / target).write_text(data)
            excerpt_map[board + ':' + function] = {'payload': target, 'sha256': sha((OUT / target).read_bytes()),
                                                  'original': original, 'first_line': begin + 1, 'last_line': end}
save('excerpt-map.json', excerpt_map)

all_inputs = dict(CAPTURE['input_sha256']) | supplement['input_sha256']
unchanged = {name: sha(pathlib.Path(name).read_bytes()) == digest for name, digest in all_inputs.items()}
assert all(unchanged.values()), [name for name, ok in unchanged.items() if not ok]
snapshot_check = {name: sha((OUT / target).read_bytes()) == all_inputs[name]
                  for name, target in (CAPTURE['snapshot_map'] | supplement['snapshot_map']).items()}
assert all(snapshot_check.values())
assert all(sha((OUT / command['payload']).read_bytes()) == command['sha256'] for command in CAPTURE['commands'])
save('analysis-checks.json', {
    'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'all_input_sha256': all_inputs, 'input_unchanged_after': unchanged,
    'snapshot_checks': snapshot_check, 'command_payloads_current': True,
    'selected_elfs': len(CAPTURE['members']), 'selected_dwarf': sum(x['dwarf_present'] for x in CAPTURE['members'].values()),
    'excerpt_count': len(excerpt_map), 'scope': CAPTURE['excluded_scope'],
})
print('PASS read-only analysis:', len(all_inputs), 'inputs;', len(excerpt_map), 'excerpts;', len(CAPTURE['commands']), 'captured commands; no decoder execution/build')
