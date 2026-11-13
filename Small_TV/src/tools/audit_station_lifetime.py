"""Bind Small TV station and BSS lifetime sites to both SDKs and linked images."""
import argparse
import json
from pathlib import Path
import sys

from audit_behavior_entrypoints import need
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.bss_assoc import selected
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import branch_target, link_register, match, model, signed
from reverse.timer_event11_match import adapter_table
from reverse.wifi_producers import NET_SHA


# The factory entries were recovered from the linked RV32 code and matched
# against the indicated archive members. Native entries come from its ELF.
FUNCTIONS = {
    'wifi_start_process': ('ieee80211_ioctl.o', 0x42066140),
    'wifi_stop_process': ('ieee80211_ioctl.o', 0x420661ca),
    'wifi_mode_set': ('ieee80211.o', 0x42070b40),
    'wifi_create_sta': ('ieee80211.o', 0x42070a14),
    'wifi_destroy_sta': ('ieee80211.o', 0x4207078c),
    'wifi_disconnect_process': ('ieee80211_ioctl.o', 0x4206632e),
    'ieee80211_sta_disconnect': ('ieee80211_ioctl.o', 0x42064d8c),
    'ieee80211_sta_new_state': ('ieee80211_sta.o', 0x4206dc18),
    'cnx_sta_leave': ('wl_cnx.o', 0x4206c1ae),
    'cnx_sta_associated': ('wl_cnx.o', 0x4206c444),
    'cnx_bss_alloc': ('wl_cnx.o', 0x4206b542),
    'cnx_remove_rc': ('wl_cnx.o', 0x4206b09a),
    'cnx_connect_to_bss': ('wl_cnx.o', 0x42069bb0),
    'cnx_connect_op': ('wl_cnx.o', 0x420699cc),
    'ieee80211_mlme_connect_bss': ('ieee80211_proto.o', 0x4206fdea),
}

EDGES = {
    'wifi_start_process': ('wifi_mode_set',),
    'wifi_stop_process': ('wifi_destroy_sta',),
    'wifi_mode_set': ('wifi_create_sta', 'wifi_destroy_sta'),
    'wifi_disconnect_process': ('ieee80211_sta_disconnect',),
    'ieee80211_sta_disconnect': ('ieee80211_sta_new_state',),
    'ieee80211_sta_new_state': ('cnx_sta_leave', 'cnx_sta_associated'),
    'cnx_bss_alloc': ('cnx_remove_rc',),
    'cnx_connect_to_bss': ('cnx_connect_op',),
    'cnx_connect_op': ('ieee80211_mlme_connect_bss',),
}

# Instruction-relative offsets follow each matched body, so a relink can move
# the entry without invalidating the checks. Operands are checked in RV32 bytes.
SITES = (
    # label, owner, factory offset, native offset, bytes (factory/native if different)
    ('station_size', 'wifi_create_sta', 0x26, 0x26, '13058021'),
    ('station_alloc', 'wifi_create_sta', 0x2a, 0x2a, '83a747178297'),
    ('station_publish', 'wifi_create_sta', 0x4a, 0x48, '80c8'),
    ('owned_peer_size', 'wifi_create_sta', 0x4c, 0x4a, ('1305803b', '1305003d')),
    ('owned_peer_alloc', 'wifi_create_sta', 0x64, 0x62, '83a747178297'),
    ('owned_peer_publish', 'wifi_create_sta', 0x6a, 0x68, '2324a40e'),
    ('owned_peer_backpointer', 'wifi_create_sta', 0xba, 0xb2, '80c3'),
    ('owned_peer_null_check', 'wifi_create_sta', 0x94, 0x8c, ('35c9', '35c1')),
    ('creation_rollback_free', 'wifi_create_sta', 0x10e, 0xf6, '83a7070b8297'),
    ('creation_rollback_clear', 'wifi_create_sta', 0x118, 0x100, '23a80400'),
    ('destroy_lock', 'wifi_destroy_sta', 0x3c, 0x3c, 'fc4b8297'),
    ('destroy_unpublish_station', 'wifi_destroy_sta', 0x48, 0x48, '23280400'),
    ('destroy_unlock', 'wifi_destroy_sta', 0x4c, 0x4c, 'bc4f8297'),
    ('destroy_free_peer', 'wifi_destroy_sta', 0x54, 0x54, '03a5840e83a7070b8297'),
    ('destroy_free_station', 'wifi_destroy_sta', 0x62, 0x62, '268583a7070b8297'),
    ('active_peer_publish', 'ieee80211_mlme_connect_bss', 0x16, 0x16, '23a2a70e'),
    ('leave_lock', 'cnx_sta_leave', 0x240, 0x21e, 'fc4b8297'),
    ('active_peer_clear', 'cnx_sta_leave', 0x24c, 0x22a, '23a2090e'),
    ('leave_unlock', 'cnx_sta_leave', 0x250, 0x22e, 'bc4f8297'),
    ('scan_slot_stride', 'cnx_bss_alloc', 0x66, 0x62, ('1306803b', '1306003d')),
    ('scan_slot_count', 'cnx_bss_alloc', 0xb8, 0xb4, '9147'),
)

OSI_SLOTS = {
    84: (0x40383d7e, 'mutex_lock_wrapper', 16),
    88: (0x40383d70, 'mutex_unlock_wrapper', 14),
    176: (0x4038e4da, 'free', 14),
    372: (0x40383d00, 'wifi_zalloc_wrapper', 18),
}


def connect_callback_sites(image, functions, factory):
    """Resolve the callback materialized into a1/a3 and the two SDK calls."""
    function = functions['cnx_connect_to_bss']
    base = function['address']
    high_offset, high_register = (0x290, 18) if factory else (0x190, 9)
    high = int.from_bytes(image.read(base + high_offset, 4, True), 'little')
    need((high & 0xfff) == (high_register << 7 | 0x37), 'Unexpected callback LUI')
    rows = {}
    for name, operand, call, register in (
        ('chm_acquire_lock', 0x296 if factory else 0x196, 0x29c if factory else 0x19c, 11),
        ('chm_start_op', 0x2c6 if factory else 0x1d8, 0x2d0 if factory else 0x1e2, 13),
    ):
        low = int.from_bytes(image.read(base + operand, 4, True), 'little')
        need((low & 0xfffff) == (high_register << 15 | register << 7 | 0x13),
             'Unexpected callback ADDI')
        callback = (high & 0xfffff000) + signed(low >> 20, 12)
        need(callback == functions['cnx_connect_op']['address'], 'Wrong indirect connect callback')
        pc = base + call
        code = image.read(pc, 4, True)
        target = selected(function['bindings'], name)['address']
        need(link_register(code) == 1 and branch_target(code, pc) == target, 'Wrong channel SDK call')
        rows[name] = dict(call=pc, sdk_target=target, callback=callback, argument_register=register)
    return rows


def layout(image, archive, variant):
    """Verify entire SDK bodies, then their selected call and data boundaries."""
    factory = variant == 'factory'
    need(sha(archive) == NET_SHA[variant], 'Unexpected station SDK archive')
    parts = dict(members(archive))
    gp = startup_gp(image) if factory else image.symbol('__global_pointer$')['st_value']
    functions = {}
    for name, (member, address) in FUNCTIONS.items():
        spec = model(parts[member], name)
        if factory:
            code = image.read(address, len(spec['code']) + 64, True)
        else:
            symbol, code = image.body(name)
            address = symbol['st_value']
        row = match(spec, code, address, gp)
        length = row['linked_bytes']
        need(factory or length == len(code), f'Incomplete native body: {name}')
        functions[name] = dict(address=address, bytes=length, code_sha256=sha(code[:length]),
                               local_branches_checked=row['local_branches_checked'],
                               bindings=row['symbol_bindings'])

    for source, targets in EDGES.items():
        for target in targets:
            binding = selected(functions[source]['bindings'], target)
            need(binding['address'] == functions[target]['address'], f'Wrong target for {source}: {target}')
            need(binding['kind'] == 'call', f'Wrong binding kind for {source}: {target}')

    def shared_anchor(symbol, owners):
        values = {selected(functions[owner]['bindings'], symbol)['address'] for owner in owners}
        need(len(values) == 1, f'Inconsistent anchor: {symbol}')
        value = values.pop()
        if not factory:
            candidates = {row['st_value'] for row in image.symbols
                          if row.name == symbol and row['st_value']}
            need(candidates == {value}, f'Wrong native anchor: {symbol}')
        return value

    station_manager = shared_anchor('g_ic', ('wifi_start_process', 'cnx_sta_leave',
                                              'ieee80211_mlme_connect_bss'))
    for owner in ('wifi_create_sta', 'wifi_destroy_sta'):
        binding = selected(functions[owner]['bindings'], '.LANCHOR5')
        need(binding['kind'] == 'data' and binding['address'] == station_manager,
             f'{owner} uses a different station manager')
    scan_manager = shared_anchor('g_cnxMgr', ('cnx_bss_alloc', 'cnx_remove_rc', 'cnx_connect_to_bss'))
    osi_pointer = shared_anchor('g_osi_funcs_p', ('wifi_create_sta', 'wifi_destroy_sta', 'cnx_sta_leave'))
    global_lock = shared_anchor('g_wifi_global_lock', ('wifi_destroy_sta', 'cnx_sta_leave'))
    table = adapter_table(image.read, variant, None if factory else image.symbols)['address']
    slots = {}
    for offset, (old_address, symbol_name, old_size) in OSI_SLOTS.items():
        address = int.from_bytes(image.read(table + offset, 4), 'little')
        expected, size = (old_address, old_size) if factory else (
            image.symbol(symbol_name)['st_value'], image.symbol(symbol_name)['st_size'])
        need(address == expected, f'Wrong {variant} OSI slot {offset}')
        code = image.read(address, size, True)
        slots[str(offset)] = dict(address=address, symbol=symbol_name, bytes=size, code_sha256=sha(code))

    sites = {}
    for label, name, old_offset, new_offset, expected in SITES:
        code = bytes.fromhex(expected if isinstance(expected, str) else expected[not factory])
        offset = old_offset if factory else new_offset
        owner = functions[name]
        address = owner['address'] + offset
        need(offset + len(code) <= owner['bytes'] and image.read(address, len(code), True) == code,
             f'Unexpected {variant} instruction at {label}: {address:#x}')
        sites[label] = dict(address=address, bytes=code.hex(), owner=name)
    return dict(functions=functions, sites=sites,
                connect_callbacks=connect_callback_sites(image, functions, factory),
                osi_table=table, osi_pointer=osi_pointer, slots=slots,
                global_lock=global_lock, g_ic=station_manager, g_cnxMgr=scan_manager,
                offsets=dict(station=16, active_peer=228, owned_peer=232, scan_slots=8),
                station_bytes=536, peer_bytes=952 if factory else 976, scan_slot_count=4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory-elf', 'native-elf', 'app', 'factory-net', 'native-net', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    factory, native, app = (path.read_bytes() for path in (args.factory_elf, args.native_elf, args.app))
    sys.setrecursionlimit(max(5000, sys.getrecursionlimit()))
    result = dict(factory_elf_sha256=sha(factory), native_elf_sha256=sha(native),
                  native_app_sha256=sha(app), factory=layout(Image(factory), args.factory_net.read_bytes(), 'factory'),
                  native=layout(LinkedRuntime(native, app), args.native_net.read_bytes(), 'native'),
                  all_concurrent_lifetimes_proved=False, physical_rf_tested=False)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Checked {len(FUNCTIONS)} complete SDK bodies per image and {len(SITES)} lifetime sites')


if __name__ == '__main__':
    main()
