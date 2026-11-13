"""Trace Small TV HTTP and station timer entrypoints in two exact RV32 images."""
import argparse
import json
from pathlib import Path
import re
import struct
import sys

from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import branch_target, link_register, match, model, signed
from reverse.timer_event11_match import adapter_table
from reverse.wifi_producers import NET_SHA


def need(condition, message):
    if not condition:
        raise ValueError(message)


def word(image, address):
    return struct.unpack('<I', image.read(address, 4, True))[0]


def address_pair(image, pc, register, low_pc=None):
    """Recover a LUI/ADDI address in one specified argument register."""
    hi, lo = word(image, pc), word(image, pc + 4 if low_pc is None else low_pc)
    need(hi & 0xfff == (register << 7 | 0x37) and
         lo & 0xfffff == (register << 15 | register << 7 | 0x13),
         f'Unexpected callback/address materialization at {pc:#x}')
    return ((hi & 0xfffff000) + signed(lo >> 20, 12)) & 0xffffffff


def direct_call(image, pc, target):
    instruction = image.read(pc, 4, True)
    need(link_register(instruction) == 1 and branch_target(instruction, pc) == target,
         f'Unexpected direct call at {pc:#x}')


def route(image, descriptor, factory):
    pointer, method, callback, context = struct.unpack('<4I', image.read(descriptor, 16))
    uri = bytearray()
    for i in range(48):
        character = image.read(pointer + i, 1)
        if character == b'\0':
            break
        uri.extend(character)
    else:
        raise ValueError('Unterminated route')
    need(re.fullmatch(rb'/[a-zA-Z_./]*', uri) is not None and method in (1, 3),
         'Unexpected route string/method')
    need(context == 0, 'Unexpected static route context')
    if factory:
        need(image.read(descriptor + 16, 8) == bytes(8), 'Unexpected factory WebSocket fields')
    image.read(callback, 2, True)
    return ('GET' if method == 1 else 'POST', uri.decode('ascii')), callback


def http_entries(factory, linked):
    """Recover a1 at each registration, then follow the handler field used by jalr."""
    need(factory.read(0x4203baa4, 6, True) == bytes.fromhex('9c444a858297'),
         'Factory dispatch no longer loads/calls the SDK handler field at +8')
    gp = startup_gp(factory)
    sites = [0x4200fae4 + i * 14 for i in range(31)] + [0x4200fc92, 0x4200fc9c, 0x4200fca6]
    original = {}
    for i, pc in enumerate(sites):
        direct_call(factory, pc, 0x4203b848)
        if i < 31:
            descriptor = address_pair(factory, pc - 10, 11)
        else:
            instruction = word(factory, pc - 6)
            need(instruction & 0xfffff == 0x18593, 'Expected ADDI a1,gp,offset')
            descriptor = gp + signed(instruction >> 20, 12)
        key, handler = route(factory, descriptor, True)
        need(key not in original, 'Duplicate factory route')
        original[key] = dict(registration=hex(pc), descriptor=hex(descriptor), factory=hex(handler))
    table = linked.symbol('routes')
    need(table['st_size'] == 42 * 16, 'Requalify native httpd_uri_t layout or route count')
    native = {}
    for i in range(0, table['st_size'], 16):
        key, callback = route(linked, table['st_value'] + i, False)
        need(key not in native, 'Duplicate native route')
        native[key] = callback
    need(not original.keys() - native.keys(), 'Missing factory HTTP routes')
    direct_call(factory, 0x4200fcb6, 0x4203b640)
    need(address_pair(factory, 0x4200fcaa, 12) == 0x4200d4be
         and factory.read(0x4200fcb2, 2, True) == bytes.fromhex('9945'), 'Changed HTTP 404 route')
    return dict(factory_routes=len(original), native_routes=len(native),
                native_only=[f'{method} {path}' for method, path in sorted(native.keys() - original.keys())],
                error_404=dict(factory='0x4200d4be', native=hex(linked.symbol('captive_redirect')['st_value'])),
                routes=[dict(method=method, path=path, **row, native=hex(native[method, path]))
                        for (method, path), row in original.items()])


def callback_entries(factory):
    """Check callback materializations at their actual SDK registration sites."""
    rows = []
    for pc, target, address_pc, register, callback in (
        (0x4200cb54, 0x420aeab6, 0x4200cb48, 12, 0x4200c602),
        (0x4200cb74, 0x420aeab6, 0x4200cb68, 12, 0x4200c602),
        (0x4200d0c6, 0x420aeab6, 0x4200d0b4, 12, 0x4200c6e2),
        (0x4200d0e4, 0x420aeab6, 0x4200d0d2, 12, 0x4200c6e2),
        (0x42008476, 0x420ae534, 0x42008460, 15, 0x4200826a),
        (0x420093f8, 0x420385dc, 0x420093e2, 15, 0x4200917c),
        (0x4200c4d4, 0x42011c48, 0x4200c4ca, 11, 0x4200c33e),
        (0x4200c512, 0x42011fd8, 0x4200c508, 11, 0x4200c374),
        (0x42010982, 0x4203dd76, 0x42010976, 15, 0x4200fccc),
        (0x42010b24, 0x42017e90, 0x42010b1c, 10, 0x420109de),
    ):
        direct_call(factory, pc, target)
        need(address_pair(factory, address_pc, register) == callback, 'Wrong callback argument')
        rows.append(dict(registration=hex(pc), callee=hex(target), callback=hex(callback)))
    return rows


def station_bodies(factory, linked, old, new):
    """Verify full wlan object bodies, then resolve OSI calls and their two callbacks."""
    factory_roots = {'cnx_sta_leave': 0x4206c1ae, 'cnx_sta_associated': 0x4206c444}
    rows = {}
    for variant, image, path in (('factory', factory, old), ('native', linked, new)):
        archive = path.read_bytes()
        need(sha(archive) == NET_SHA[variant], 'Wrong station SDK archive')
        parts = [data for name, data in members(archive) if name == 'wl_cnx.o']
        need(len(parts) == 1, 'Missing/duplicate wl_cnx.o')
        gp = startup_gp(image) if variant == 'factory' else linked.symbol('__global_pointer$')['st_value']
        anchors, functions = factory_roots.copy(), {}
        for name in ('cnx_sta_leave', 'cnx_sta_associated', 'ic_set_sta',
                     'cnx_beacon_timeout', 'cnx_handshake_timeout'):
            spec = model(parts[0], name)
            if variant == 'factory':
                start = anchors[name]
                data = factory.read(start, len(spec['code']) + 64, True)
            else:
                symbol, data = linked.body(name)
                start = symbol['st_value']
            result = match(spec, data, start, gp)
            if variant == 'native':
                need(result['linked_bytes'] == len(data), 'Incomplete native station body')
            bindings = {row['name']: row['address'] for row in result['symbol_bindings']}
            if name == 'cnx_sta_associated':
                for callee in ('ic_set_sta', 'cnx_beacon_timeout', 'cnx_handshake_timeout'):
                    if variant == 'native':
                        need(bindings[callee] == linked.symbol(callee)['st_value'], 'Wrong native callback/callee')
                    anchors[callee] = bindings[callee]
                need(bindings['ic_set_sta'] == functions['cnx_sta_leave']['bindings']['ic_set_sta'],
                     'Leave/associate use different station state helpers')
            if name == 'ic_set_sta':
                need(bindings['g_ic'] == functions['cnx_sta_associated']['bindings']['g_ic']
                     == functions['cnx_sta_leave']['bindings']['g_ic'],
                     'Station bodies use different g_ic objects')
                if variant == 'native':
                    need(bindings['g_ic'] == linked.symbol('g_ic')['st_value'], 'Wrong native g_ic')
            functions[name] = dict(start=hex(start), end=result['end'], bytes=result['linked_bytes'],
                                   code_sha256=sha(data[:result['linked_bytes']]), bindings=bindings)
        table = adapter_table(image.read, variant, linked.symbols)
        slots = {offset: struct.unpack('<I', image.read(table['address'] + offset, 4))[0]
                 for offset in (84, 88, 224, 228, 232, 236)}
        for address in slots.values():
            image.read(address, 2, True)
        setfn = slots[236]
        if variant == 'factory':
            for pc, load_pc, high, low, callback in (
                (0x4206c48c, 0x4206c482, 0x4206c47c, 0x4206c488, 'cnx_beacon_timeout'),
                (0x4206c4e6, 0x4206c4dc, 0x4206c4d6, 0x4206c4e0, 'cnx_handshake_timeout'),
            ):
                need(image.read(pc, 2, True) == bytes.fromhex('8297') and word(image, load_pc) == 0x0ec7a783,
                     'Expected indirect call through OSI slot 236')
                need(address_pair(image, high, 11, low) == anchors[callback],
                     'Unbound factory timer callback')
            need(setfn == 0x420962d0, 'Unexpected factory setfn wrapper')
            backend = 0x4207b3f4
            direct_call(factory, setfn + 4, backend)
        else:
            need(setfn == linked.symbol('esp_coex_common_timer_setfn_wrapper')['st_value'],
                 'Unexpected native setfn wrapper')
            backend = linked.symbol('ets_timer_setfn')['st_value']
            tail = linked.read(setfn, 4, True)
            need(link_register(tail) == 0 and branch_target(tail, setfn) == backend,
                 'Unexpected native setfn backend')
        rows[variant] = dict(functions=functions, osi_table=hex(table['address']),
                             osi_slots={str(k): hex(v) for k, v in slots.items()}, setfn_backend=hex(backend))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory-elf', 'native-elf', 'app', 'factory-net', 'native-net', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    factory_elf, native_elf, app = (p.read_bytes() for p in (args.factory_elf, args.native_elf, args.app))
    factory, linked = Image(factory_elf), LinkedRuntime(native_elf, app)
    sys.setrecursionlimit(max(4000, sys.getrecursionlimit()))
    result = dict(factory_elf_sha256=sha(factory_elf), native_elf_sha256=linked.digest,
                  native_app_sha256=sha(app), http=http_entries(factory, linked),
                  factory_callbacks=callback_entries(factory),
                  station=station_bodies(factory, linked, args.factory_net, args.native_net),
                  whole_image_completeness_proved=False, station_peer_lifetime_proved=False)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"Compared {result['http']['factory_routes']} factory HTTP routes and 5 full station SDK bodies per image")


if __name__ == '__main__':
    main()
