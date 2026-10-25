"""Qualify both SDK versions of timer event 11 and its real rearm function."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.rv32_link_match import branch_target, link_register, model, match

NATIVE_SHA = '9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24'
LIBRARIES = {
    'factory': 'b460bb305a8d3c5e93489a03710108a06435d58bf12410e080c0c6805a74bade',
    'native': 'c7797847c9229cc14b27194b5b7ccd63c20e2c909815d72e189973dd9f2a1aa2',
}
NAMES = {
    'factory': ('pp_timer_max_idle', 'pm_max_idle_timeout_process', 'pm_enable_max_idle_timer'),
    'native': ('pp_timer_keep_alive', 'pm_keep_alive_timeout_process', 'pm_enable_keep_alive_timer'),
}


def adapter_table(read, variant, symbols=None):
    """Bind the three actual OSI slots; validate each complete forwarding wrapper.

    Finding this initialized table does not prove its runtime registration. The
    legacy timer implementations beyond these forwarding wrappers stay external.
    """
    if variant == 'factory':
        address, version = 0x3fcb459c, 8
        targets = {224: (0x40383d52, 0x403846e8), 228: (0x403847f2, 0x4038479a),
                   240: (0x40384800, 0x40384644)}
    else:
        table = unique(symbols, 'g_wifi_osi_funcs')
        if table['st_size'] != 480:
            raise ValueError('Unexpected native OSI table size')
        address, version = table['st_value'], 9
        targets = {slot: (unique(symbols, wrapper)['st_value'], unique(symbols, target)['st_value'])
                   for slot, wrapper, target in (
                       (224, 'timer_arm_wrapper', 'ets_timer_arm'),
                       (228, 'esp_coex_common_timer_disarm_wrapper', 'ets_timer_disarm'),
                       (240, 'esp_coex_common_timer_arm_us_wrapper', 'ets_timer_arm_us'))}
    raw = read(address, 480)
    if int.from_bytes(raw[:4], 'little') != version or raw[-4:] != bytes.fromhex('afbeadde'):
        raise ValueError('Invalid OSI version/magic')
    wrappers = {}
    for slot, (start, target) in targets.items():
        if int.from_bytes(raw[slot:slot + 4], 'little') != start:
            raise ValueError('Wrong OSI timer callback')
        code = read(start, 14 if variant == 'factory' else 4, True)
        if variant == 'factory':
            if code[:4] != bytes.fromhex('411106c6') or code[8:] != bytes.fromhex('b24041018280'):
                raise ValueError('Unknown factory timer wrapper')
            call, pc, register = code[4:8], start + 4, 1
        else:
            call, pc, register = code, start, 0
        if link_register(call) != register or branch_target(call, pc) != target:
            raise ValueError('OSI wrapper forwards to wrong timer implementation')
        wrappers[str(slot)] = dict(address=start, bytes=len(code), sha256=sha(code), target=target)
    return dict(address=address, bytes=480, sha256=sha(raw), version=version, wrappers=wrappers,
                runtime_registration_proved=False, transitive_timer_semantics_proved=False)


def objects(path, variant):
    """Read only known members of the pinned archive without archive path extraction."""
    raw = path.read_bytes()
    if sha(raw) != LIBRARIES[variant]:
        raise ValueError('Unexpected event-11 SDK archive')
    found = {}
    for name, data in members(raw):
        if name in ('pm.o', 'pp_timer.o'):
            if name in found:
                raise ValueError('Duplicate SDK timer member')
            found[name] = data
    if set(found) != {'pm.o', 'pp_timer.o'}:
        raise ValueError('Missing SDK timer objects')
    return found


def unique(symbols, name):
    """Never choose an arbitrary undefined symbol or same-named local alias."""
    found = [s for s in symbols if s.name == name and s['st_value']]
    if len(found) != 1:
        raise ValueError('Missing/ambiguous linked timer symbol: ' + name)
    return found[0]


def qualify(factory, native, old_library, new_library, replacements=None):
    """Match complete wrapper/handler/rearm bodies and bind each actual data target."""
    if sha(native) != NATIVE_SHA:
        raise ValueError('Unexpected current native ELF')
    image = Image(factory)
    linked = ELFFile(io.BytesIO(native)); symbols = list(linked.get_section_by_name('.symtab').iter_symbols())
    def native_read(address, size, execute=False):
        """Read one initialized section, requiring executable bytes for code."""
        sections = [s for s in linked.iter_sections() if s['sh_type'] != 'SHT_NOBITS'
                    and s['sh_flags'] & 2 and (not execute or s['sh_flags'] & 4)
                    and s['sh_addr'] <= address < address + size <= s['sh_addr'] + s['sh_size']]
        if len(sections) != 1:
            raise ValueError('Ambiguous/uninitialized native extent')
        section = sections[0]; offset = address - section['sh_addr']
        return section.data()[offset:offset + size]
    result = {}
    for variant, library in (('factory', old_library), ('native', new_library)):
        parts = objects(library, variant)
        pm = ELFFile(io.BytesIO(parts['pm.o']))
        object_symbols = list(pm.get_section_by_name('.symtab').iter_symbols())
        sizes = {name: next(s['st_size'] for s in object_symbols if s.name == name and s['st_size'])
                 for name in ('g_pm', 'g_pm_cfg')}
        names = NAMES[variant]
        specs = {name: model(parts['pp_timer.o' if index == 0 else 'pm.o'], name)
                 for index, name in enumerate(names)}
        rows = []
        gp = startup_gp(image) if variant == 'factory' else unique(symbols, '__global_pointer$')['st_value']
        starts = {names[0]: 0x4207b08c} if variant == 'factory' else {
            name: unique(symbols, name)['st_value'] for name in names}
        for index, name in enumerate(names):
            if variant == 'factory':
                if index:
                    starts[name] = next(b['address'] for b in rows[-1]['symbol_bindings'] if b['name'] == name)
                start = starts[name]
                code = image.read(start, len(specs[name]['code']) + 64, True)
            else:
                symbol = unique(symbols, name)
                section = linked.get_section(symbol['st_shndx'])
                start = symbol['st_value']; offset = start - section['sh_addr']
                if not section['sh_flags'] & 4 or not 0 <= offset < offset + symbol['st_size'] <= section['sh_size']:
                    raise ValueError('Non-executable native timer extent')
                code = section.data()[offset:offset + symbol['st_size']]
            if replacements and (variant, name) in replacements:
                code = replacements[variant, name]
            row = match(specs[name], code, start, gp)
            if variant == 'native':
                if int(row['end'], 0) != start + symbol['st_size']:
                    raise ValueError('Incomplete native timer match')
                for binding in row['symbol_bindings']:
                    if binding['binding'] != 'STB_LOCAL' and binding['address'] != unique(symbols, binding['name'])['st_value']:
                        raise ValueError('Wrong native timer callee')
            row['linked_code_sha256'] = sha(code[:row['linked_bytes']])
            rows.append(row)
        handler, rearm = rows[1:]
        gpm = next(b['address'] for b in handler['symbol_bindings'] if b['name'] == '.LANCHOR0')
        cfg = next(b['address'] for b in rearm['symbol_bindings'] if b['binding'] == 'STB_LOCAL' and b['section'] != specs[names[2]]['section'] and b['address'] != gpm)
        osi = next(b['address'] for b in rearm['symbol_bindings'] if b['name'] == 'g_osi_funcs_p')
        if any(b['address'] != gpm for b in rearm['symbol_bindings'] if b['name'] == '.LANCHOR0'):
            raise ValueError('Rearm and handler use different PM state')
        if variant == 'native':
            for name, address in (('g_pm', gpm), ('g_pm_cfg', cfg), ('g_osi_funcs_p', osi)):
                symbol = unique(symbols, name)
                if symbol['st_value'] != address or name in sizes and symbol['st_size'] != sizes[name]:
                    raise ValueError('Native data symbol differs: ' + name)
        elif (gpm, cfg, osi) != (0x3fcc2d08, 0x3fcb4b0c, 0x3fcdfdd8):
            raise ValueError('Qualified factory data anchors differ')
        if variant == 'factory':
            table_address = 0x3fcb52f8
            entry = image.read(table_address + 11 * 8, 8)
        else:
            table = unique(symbols, 'g_pp_timer_info')
            if table['st_size'] != 120:
                raise ValueError('Unexpected native timer table extent')
            section = linked.get_section(table['st_shndx'])
            table_address = table['st_value']; offset = table_address - section['sh_addr'] + 11 * 8
            entry = section.data()[offset:offset + 8]
        if entry != (11).to_bytes(4, 'little') + starts[names[0]].to_bytes(4, 'little'):
            raise ValueError('Event 11 does not select the qualified wrapper')
        setter_name = 'pm_set_bss_max_idle'
        setter_spec = model(parts['pm.o'], setter_name)
        if variant == 'factory':
            setter_start = 0x42074c12
            setter_code = image.read(setter_start, len(setter_spec['code']) + 64, True)
        else:
            setter_symbol = unique(symbols, setter_name)
            setter_start = setter_symbol['st_value']
            setter_code = native_read(setter_start, setter_symbol['st_size'], True)
        if replacements and (variant, setter_name) in replacements:
            setter_code = replacements[variant, setter_name]
        setter = match(setter_spec, setter_code, setter_start, gp)
        if variant == 'native' and setter['linked_bytes'] != setter_symbol['st_size']:
            raise ValueError('Incomplete native configuration setter')
        setter_data = [b['address'] for b in setter['symbol_bindings'] if b['kind'] == 'data']
        if setter_data != [cfg]:
            raise ValueError('Configuration setter uses a different state anchor')
        if variant == 'factory':
            enable = next(b['address'] for b in setter['symbol_bindings'] if b['name'] == names[2])
            if enable != starts[names[2]]:
                raise ValueError('Configuration setter calls a different rearm helper')
        setter['linked_code_sha256'] = sha(setter_code[:setter['linked_bytes']])
        result[variant] = dict(functions=rows, gp=gp, g_pm=gpm, g_pm_bytes=sizes['g_pm'],
                               configuration_function=setter,
                               g_pm_cfg=cfg, g_pm_cfg_bytes=sizes['g_pm_cfg'], osi_pointer=osi,
                               timer_table_address=table_address, event_id=11,
                               osi_table=adapter_table(image.read if variant == 'factory' else native_read,
                                                       variant, symbols),
                               object_sha256={name: sha(data) for name, data in parts.items()},
                               library_sha256=sha(library.read_bytes()))
    return dict(schema='wifi-timer-event11-v1', factory_elf_sha256=sha(factory), native_elf_sha256=sha(native),
                layouts=result, semantic_equivalence_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)
