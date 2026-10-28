"""Qualify event-11 OSI registration, timer initialization and event posting."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha
from reverse.elf_archive import members
from reverse.rv32_link_match import branch_target, link_register, match, model
from reverse.timer_event11_match import objects, qualify as qualify_event, unique

NET = {
    'factory': '8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558',
    'native': 'c2df6fcca4c1c19c9c6b8171f16461e52a636da90dd7f7be3b67bed4fbe71cca',
}
FACTORY = {'esp_wifi_init_internal': 0x42068a9a, 'wifi_osi_funcs_register': 0x4206819e,
           'pm_attach': 0x42076792, 'pm_max_idle_timeout': 0x42074b4a,
           'pp_timer_process': 0x4207b16e, 'pp_timer_register_post_cb': 0x4207b162}


def api_object(path, variant):
    """Read only the exact SDK API member; never extract archive-controlled paths."""
    raw = path.read_bytes()
    if sha(raw) != NET[variant]:
        raise ValueError('Unexpected net80211 SDK archive')
    found = [data for name, data in members(raw) if name == 'ieee80211_api.o']
    if len(found) != 1:
        raise ValueError('Missing/ambiguous SDK API object')
    return found[0]


def qualify(factory, native, old_pp, new_pp, old_net, new_net, replacements=None):
    """Bind complete bodies to prior state/OSI anchors and to each other's calls."""
    base = qualify_event(factory, native, old_pp, new_pp)
    image, linked = Image(factory), ELFFile(io.BytesIO(native))
    symbols = list(linked.get_section_by_name('.symtab').iter_symbols())
    def native_read(address, size, execute=False):
        """Read one allocated initialized section, requiring executable code."""
        found = [s for s in linked.iter_sections() if s['sh_type'] != 'SHT_NOBITS'
                 and s['sh_flags'] & 2 and (not execute or s['sh_flags'] & 4)
                 and s['sh_addr'] <= address < address + size <= s['sh_addr'] + s['sh_size']]
        if len(found) != 1:
            raise ValueError('Uninitialized/ambiguous native extent')
        section = found[0]; offset = address - section['sh_addr']
        return section.data()[offset:offset + size]
    result = {}
    for variant, pp_path, net_path in (('factory', old_pp, old_net), ('native', new_pp, new_net)):
        layout = base['layouts'][variant]
        parts = objects(pp_path, variant)
        api = api_object(net_path, variant)
        names = ('esp_wifi_init_internal', 'wifi_osi_funcs_register', 'pm_attach',
                 'pm_max_idle_timeout' if variant == 'factory' else 'pm_keep_alive_timeout',
                 'pp_timer_process', 'pp_timer_register_post_cb')
        starts = FACTORY if variant == 'factory' else {n: unique(symbols, n)['st_value'] for n in names}
        read = image.read if variant == 'factory' else native_read
        rows, bindings = [], {}
        for name in names:
            source = api if name in names[:2] else parts['pm.o' if name in names[2:4] else 'pp_timer.o']
            spec = model(source, name)
            start = starts[name]
            length = len(spec['code']) + 64 if variant == 'factory' else unique(symbols, name)['st_size']
            code = read(start, length, True)
            if replacements and (variant, name) in replacements:
                code = replacements[variant, name]
            row = match(spec, code, start, layout['gp'])
            if variant == 'native' and row['linked_bytes'] != length:
                raise ValueError('Incomplete native registration body')
            for binding in row['symbol_bindings']:
                if binding['binding'] != 'STB_LOCAL':
                    key = binding['name']
                    if key in bindings and binding['address'] != bindings[key]:
                        raise ValueError('Inconsistent shared registration target')
                    bindings[key] = binding['address']
                    if variant == 'native' and binding['address'] != unique(symbols, key)['st_value']:
                        raise ValueError('Wrong native registration target')
                if binding['name'] in starts and binding['address'] != starts[binding['name']]:
                    raise ValueError('Registration chain points to a different function')
            row['linked_code_sha256'] = sha(code[:row['linked_bytes']])
            rows.append(row)
        if bindings['g_osi_funcs_p'] != layout['osi_pointer']:
            raise ValueError('Registration writes a different OSI global')
        attach = rows[2]
        if next(b['address'] for b in attach['symbol_bindings'] if b['name'] == '.LANCHOR0') != layout['g_pm']:
            raise ValueError('Timer initialization uses a different PM object')
        cfg_anchors = [b for b in attach['symbol_bindings'] if b['kind'] == 'data'
                       and b['binding'] == 'STB_LOCAL' and b['address'] == layout['g_pm_cfg']]
        if len(cfg_anchors) != 1:
            raise ValueError('Timer initialization uses a different configuration')
        # Both members belong to pp_timer.o, so their local section anchors must agree.
        post = [b for b in rows[4]['symbol_bindings'] if b['kind'] == 'data']
        register = [b for b in rows[5]['symbol_bindings'] if b['kind'] == 'data']
        if len(post) != 1 or post != register:
            raise ValueError('Register and post do not share callback storage')
        table = layout['osi_table']['address']
        adapter = int.from_bytes(read(table + 236, 4), 'little')
        adapter_code = read(adapter, 14 if variant == 'factory' else 4, True)
        if variant == 'factory':
            if adapter_code[:4] != bytes.fromhex('411106c6') or adapter_code[8:] != bytes.fromhex('b24041018280'):
                raise ValueError('Unknown factory timer-setfn forwarding body')
            call, pc, rd = adapter_code[4:8], adapter + 4, 1
        else:
            wrapper = unique(symbols, 'esp_coex_common_timer_setfn_wrapper')
            if (adapter, len(adapter_code)) != (wrapper['st_value'], wrapper['st_size']):
                raise ValueError('Wrong native timer-setfn wrapper')
            call, pc, rd = adapter_code, adapter, 0
        target = branch_target(call, pc)
        if link_register(call) != rd or target != (0x4207b3f4 if variant == 'factory' else unique(symbols, 'ets_timer_setfn')['st_value']):
            raise ValueError('Timer-setfn wrapper forwards to a different function')
        adapter_row = dict(name='timer_setfn_forwarder', start=hex(adapter), end=hex(adapter + len(adapter_code)),
                           linked_bytes=len(adapter_code), linked_code_sha256=sha(adapter_code), target=target)
        result[variant] = dict(prior=layout, functions=rows, timer_setfn=adapter_row,
                               timer_timeout_name=names[3], post_callback_slot=post[0]['address'],
                               object_sha256=sha(api), net_library_sha256=sha(net_path.read_bytes()),
                               clock_slots={str(slot): int.from_bytes(read(table + slot, 4), 'little')
                                            for slot in (248, 252)})
    return dict(schema='wifi-event11-registration-v1', factory_elf_sha256=sha(factory), native_elf_sha256=sha(native),
                layouts=result, full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)
