"""Bind the old keep-alive predicate to TIM, TX completion and PM lifecycle code."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha
from reverse.rv32_link_match import match, model
from reverse.timer_event11_match import objects, qualify as qualify_event, unique

FACTORY = {'pm_keep_alive': 0x40390590, 'pm_reset_keep_alive': 0x42074c5c,
           'pm_tx_data_done_process': 0x42075896, 'pm_process_tim': 0x4039061c,
           'pm_start': 0x420763d8, 'pm_stop': 0x4207661c,
           'pm_tx_null_data_done_process': 0x420759cc}
NATIVE = tuple(name for name in FACTORY if name not in ('pm_keep_alive', 'pm_reset_keep_alive'))


def qualify(factory, native, old_pp, new_pp, replacements=None):
    """Match every selected byte and shared target against the pinned SDK objects."""
    prior = qualify_event(factory, native, old_pp, new_pp)
    image, elf = Image(factory), ELFFile(io.BytesIO(native))
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    result = {}
    for variant, library in (('factory', old_pp), ('native', new_pp)):
        base = prior['layouts'][variant]
        source = objects(library, variant)['pm.o']
        names = tuple(FACTORY) if variant == 'factory' else NATIVE
        starts = FACTORY if variant == 'factory' else {name: unique(symbols, name)['st_value'] for name in names}
        anchors = {row['name']: int(row['start'], 0) for row in base['functions']}
        anchors.update(starts)
        shared, rows = {}, []
        locals_ = {(b['name'],b['section']):b['address']
                   for row in (*base['functions'][1:],base['configuration_function'])
                   for b in row['symbol_bindings'] if b['binding']=='STB_LOCAL'}
        for name in names:
            spec = model(source, name); start = starts[name]
            if variant == 'factory':
                code = image.read(start, len(spec['code']) + 64, True)
            else:
                symbol = unique(symbols, name); section = elf.get_section(symbol['st_shndx'])
                offset = start - section['sh_addr']
                if not section['sh_flags'] & 4 or not 0 <= offset < offset + symbol['st_size'] <= section['sh_size']:
                    raise ValueError('Invalid native keep-alive extent')
                code = section.data()[offset:offset + symbol['st_size']]
            if replacements and (variant, name) in replacements: code = replacements[variant, name]
            row = match(spec, code, start, base['gp'])
            if variant == 'native' and row['linked_bytes'] != symbol['st_size']:
                raise ValueError('Incomplete native keep-alive body')
            for binding in row['symbol_bindings']:
                key, address = binding['name'], binding['address']
                if key == '.LANCHOR0' and address != base['g_pm']:
                    raise ValueError('Different PM state in keep-alive body')
                if key in anchors and address != anchors[key]:
                    raise ValueError('Keep-alive chain calls a different target')
                if key == 'g_osi_funcs_p' and address != base['osi_pointer']:
                    raise ValueError('Different OSI pointer in keep-alive body')
                if binding['binding'] == 'STB_LOCAL':
                    local=(key,binding['section'])
                    if local in locals_ and locals_[local] != address:
                        raise ValueError('Inconsistent object-local keep-alive anchor')
                    locals_[local]=address
                if binding['binding'] != 'STB_LOCAL':
                    if key in shared and shared[key] != address:
                        raise ValueError('Inconsistent keep-alive shared symbol')
                    shared[key] = address
                    if variant == 'native' and address != unique(symbols, key)['st_value']:
                        raise ValueError('Wrong native keep-alive symbol')
            row['linked_code_sha256'] = sha(code[:row['linked_bytes']]); rows.append(row)
        if variant == 'native' and any(s.name in ('pm_keep_alive', 'pm_reset_keep_alive') and s['st_value'] for s in symbols):
            raise ValueError('Unexpected retained old predicate/reset in native ELF')
        table = base['osi_table']['address']
        if variant == 'factory': raw = image.read(table, 480)
        else:
            s = unique(symbols, 'g_wifi_osi_funcs'); section = elf.get_section(s['st_shndx'])
            offset = table - section['sh_addr']; raw = section.data()[offset:offset + 480]
        if sha(raw) != base['osi_table']['sha256']:
            raise ValueError('Changed OSI table for clock/coexistence callbacks')
        result[variant] = dict(prior=base, functions=rows, sdk_object_sha256=sha(source),
                               station_global=unique(symbols, 'g_ic')['st_value'] if variant == 'native' else None,
                               osi_slots={str(slot): int.from_bytes(raw[slot:slot + 4], 'little') for slot in (264,400)})
    return dict(schema='wifi-keep-alive-paths-v1', layouts=result, factory_elf_sha256=sha(factory),
                native_elf_sha256=sha(native), full_runtime_lifecycle_proved=False,
                whole_image_completeness_proved=False, physical_hardware_tested=False)
