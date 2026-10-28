"""Qualify PM start/stop boundaries and their real small cancellation helpers."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha
from reverse.rv32_link_match import branch_target, link_register, match, model
from reverse.timer_event11_match import objects, unique
from reverse.timer_keep_alive import qualify as qualify_keep

ROM_SHA = '289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9'


def read_allocated(elf, address, size, execute=False):
    """Read exactly one initialized section; reject ambiguous or non-code extents."""
    found = [s for s in elf.iter_sections() if s['sh_type'] != 'SHT_NOBITS' and s['sh_flags'] & 2
             and (not execute or s['sh_flags'] & 4)
             and s['sh_addr'] <= address < address + size <= s['sh_addr'] + s['sh_size']]
    if len(found) != 1: raise ValueError('Unknown/ambiguous initialized lifecycle extent')
    section = found[0]; offset = address - section['sh_addr']
    return section.data()[offset:offset + size]


def qualify(factory, native, old_pp, new_pp, rom_data):
    """Bind helper code, actual ROM trampoline and all additional state/table addresses."""
    if sha(rom_data) != ROM_SHA: raise ValueError('Unexpected C2 rev200 ROM')
    keep = qualify_keep(factory, native, old_pp, new_pp)
    image, elf, rom = Image(factory), ELFFile(io.BytesIO(native)), ELFFile(io.BytesIO(rom_data))
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    rom_symbols = list(rom.get_section_by_name('.symtab').iter_symbols())
    body, entry = (unique(rom_symbols, name) for name in
                   ('pm_disable_sleep_delay_timer', '__call_pm_disable_sleep_delay_timer'))
    if (entry['st_value'], body['st_value'], body['st_size']) != (0x40001b74,0x40043cae,30):
        raise ValueError('Changed ROM sleep-delay function')
    trampoline = read_allocated(rom, entry['st_value'], 4, True)
    if link_register(trampoline) != 0 or branch_target(trampoline, entry['st_value']) != body['st_value']:
        raise ValueError('ROM sleep-delay trampoline targets another implementation')
    body_code = read_allocated(rom, body['st_value'], body['st_size'], True)
    pointer = unique(rom_symbols, 'g_pm_ptr')['st_value']
    if pointer != 0x3fcdfd7c: raise ValueError('Changed ROM PM binding')
    layouts = {}
    for variant, library in (('factory', old_pp), ('native', new_pp)):
        layout = keep['layouts'][variant]; base = layout['prior']
        source = objects(library, variant)['pm.o']
        helpers = {'pm_disable_active_timer':0x42074ad6}
        if variant == 'factory': helpers['pm_disable_max_idle_timer'] = 0x42074aac
        rows = []
        for name, address in helpers.items():
            if variant == 'native': address = unique(symbols, name)['st_value']
            spec = model(source, name)
            code = (image.read(address,len(spec['code'])+64,True) if variant == 'factory'
                    else read_allocated(elf,address,unique(symbols,name)['st_size'],True))
            row = match(spec,code,address,base['gp'])
            if row['linked_bytes'] != 22: raise ValueError('Unexpected small cancellation extent')
            for binding in row['symbol_bindings']:
                if binding['name'] == 'g_osi_funcs_p' and binding['address'] != base['osi_pointer']:
                    raise ValueError('Cancellation uses different OSI pointer')
                if binding['binding'] == 'STB_LOCAL' and binding['address'] != base['g_pm']:
                    raise ValueError('Cancellation uses different PM state')
            row['linked_code_sha256'] = sha(code[:row['linked_bytes']]); rows.append(row)
        start, stop = (next(f for f in layout['functions'] if f['name'] == name) for name in ('pm_start','pm_stop'))
        beacon = next(b['address'] for b in start['symbol_bindings'] if b['name'] == 'ptr_beacon_offset_funcs')
        if next(b['address'] for b in stop['symbol_bindings'] if b['name']=='ptr_beacon_offset_funcs') != beacon:
            raise ValueError('Start/stop use different beacon tables')
        before = [b['address'] for b in start['symbol_bindings'] if b['address'] in (base['g_pm']-8,base['g_pm']-4)]
        if sorted(before) != [base['g_pm']-8,base['g_pm']-4]: raise ValueError('Unqualified lifecycle globals')
        formats = {}
        for f in (start,stop):
            values = [b['address'] for b in f['symbol_bindings'] if b['kind']=='data' and 0x3c000000 <= b['address'] < 0x3d000000]
            if len(values) != (2 if f is start else 1): raise ValueError('Unexpected lifecycle log anchors')
            for address, label in zip(values, ('start','beacon') if f is start else ('stop',)):
                formats[str(address)] = label
        table = (image.read(base['osi_table']['address'],480) if variant=='factory'
                 else read_allocated(elf,base['osi_table']['address'],480))
        if sha(table) != base['osi_table']['sha256']: raise ValueError('Changed lifecycle OSI table')
        layouts[variant] = dict(prior=layout, helpers=rows, beacon_pointer=beacon,
            log_formats=formats, globals_before_pm=before,
            osi_slots={str(slot):int.from_bytes(table[slot:slot+4],'little') for slot in (228,424,436)},
            rom=dict(pointer=pointer,functions=[
                dict(name='rom_sleep_delay_entry',start=hex(entry['st_value']),linked_bytes=4,bytes_hex=trampoline.hex()),
                dict(name='rom_disable_sleep_delay',start=hex(body['st_value']),linked_bytes=30,bytes_hex=body_code.hex())]))
    return dict(schema='wifi-pm-lifecycle-v1',layouts=layouts,rom_sha256=sha(rom_data),
                full_runtime_lifecycle_proved=False,transitive_platform_effects_proved=False,
                physical_hardware_tested=False,whole_image_completeness_proved=False)
