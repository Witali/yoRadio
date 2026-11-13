"""Replay station creation and destruction in both Small TV RV32 SDKs.

Use the verified addresses and function bodies from audit_station_lifetime.py.
Synthetic storage and ABI stubs model allocation, locking and unrelated SDK
work. The traces describe the executed instruction order in one context.
"""
import argparse
import json
from pathlib import Path
import struct

from unicorn import UC_ARCH_RISCV, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_MODE_RISCV32, Uc
from unicorn import riscv_const as rv

from audit_behavior_entrypoints import need
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.nothrow_linkage import LinkedRuntime


PAGE = 4096
STATION = 0x20010000
PEER = 0x20011000
NVS = 0x20012000
OSI = 0x20013000
STACK = 0x2001bff0
RETURN = 0x2001c000
ALLOC = RETURN + 0x10
FREE = RETURN + 0x20
LOCK = RETURN + 0x30
UNLOCK = RETURN + 0x40
LOCK_HANDLE = 0x515151
NO_MEM = 0x101
NOP = bytes.fromhex('13000000')
CASES = ('first_oom', 'second_oom', 'reuse', 'created_then_destroyed')
NOOP_CALLEES = {
    'cnx_clear_blacklist', 'ic_register_michael_mic_failure_cb', 'ic_register_rx_cb',
    'ieee80211_ht_attach', 'ieee80211_ht_deattach', 'ieee80211_phy_init', 'ieee80211_setup_pmf',
}


class StationReplay:
    """Execute matched bodies with memory and function boundaries made explicit."""

    def __init__(self, image, layout, gp, case):
        self.case = case
        self.layout = layout
        self.gp = gp
        self.cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
        self.pages = set()
        self.trace = []
        self.allocations = 0
        self.live = set()
        self.bodies = {}
        self.calls = {}
        self.previous_pc = None
        self.null_check = layout['sites']['owned_peer_null_check']['address']
        self.station_ptr = layout['g_ic'] + layout['offsets']['station']
        self.owned_peer_ptr = STATION + layout['offsets']['owned_peer']

        for name in ('wifi_create_sta', 'wifi_destroy_sta'):
            function = layout['functions'][name]
            start, length = function['address'], function['bytes']
            code = image.read(start, length, True)
            need(sha(code) == function['code_sha256'], f'Changed station body: {name}')
            self.write(start, code)
            self.bodies[name] = (start, start + length)
            for binding in function['bindings']:
                if binding['kind'] == 'call':
                    address, target = binding['address'], binding['name']
                    need(self.calls.setdefault(address, target) == target, 'Ambiguous call stub')

        for address in self.calls:
            need(not self.in_body(address), 'Unexpected call into a replayed body')
            self.write(address, NOP)
        for address in (RETURN, ALLOC, FREE, LOCK, UNLOCK):
            self.write(address, NOP)

        self.write(layout['g_ic'], bytes(PAGE))
        nvs_bindings = [binding['address']
                        for binding in layout['functions']['wifi_create_sta']['bindings']
                        if binding['name'] == 'g_wifi_nvs' and binding['kind'] == 'data']
        need(len(nvs_bindings) == 1, 'Missing synthetic NVS boundary')
        peer_constants = [binding['address']
                          for binding in layout['functions']['wifi_create_sta']['bindings']
                          if binding['name'] == '.LC5' and binding['kind'] == 'data']
        need(len(peer_constants) == 1, 'Missing peer constant boundary')
        self.write(peer_constants[0], bytes(6))
        self.write(NVS, bytes(PAGE))
        self.put(nvs_bindings[0], NVS)
        self.put(layout['osi_pointer'], OSI)
        self.put(layout['global_lock'], LOCK_HANDLE)
        for slot, stub in ((372, ALLOC), (176, FREE), (84, LOCK), (88, UNLOCK)):
            need(str(slot) in layout['slots'], f'Missing verified OSI slot: {slot}')
            self.put(OSI + slot, stub)

        self.write(STATION, bytes(layout['station_bytes']))
        self.write(PEER, bytes(layout['peer_bytes']))
        self.write(STACK - PAGE, bytes(PAGE))
        if case == 'reuse':
            self.live.update((STATION, PEER))
            self.put(self.station_ptr, STATION)
            self.put(self.owned_peer_ptr, PEER)

        self.cpu.hook_add(UC_HOOK_CODE, self.on_code)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.on_store)

    def in_body(self, address):
        return any(start <= address < end for start, end in self.bodies.values())

    def write(self, address, data):
        for page in range(address & -PAGE, (address + len(data) + PAGE - 1) & -PAGE, PAGE):
            if page not in self.pages:
                self.cpu.mem_map(page, PAGE)
                self.pages.add(page)
        self.cpu.mem_write(address, data)

    def put(self, address, value):
        self.write(address, struct.pack('<I', value))

    def get(self, address):
        return struct.unpack('<I', self.cpu.mem_read(address, 4))[0]

    def on_store(self, cpu, _access, address, size, value, _user):
        event = {self.station_ptr: 'station_store', self.owned_peer_ptr: 'owned_peer_store',
                 PEER: 'owner_store'}.get(address)
        if event:
            need(size == 4, 'Unexpected station pointer store width')
            self.trace.append((event, cpu.reg_read(rv.UC_RISCV_REG_PC), value))

    def on_code(self, cpu, pc, _size, _user):
        if self.in_body(pc):
            self.previous_pc = pc
            if pc == self.null_check:
                self.trace.append(('owned_peer_test', pc, self.get(self.owned_peer_ptr)))
            return
        if pc == RETURN:
            cpu.emu_stop()
            return
        need(self.previous_pc is not None, 'Stub entered without a caller')

        a0 = cpu.reg_read(rv.UC_RISCV_REG_A0)
        if pc == ALLOC:
            self.allocations += 1
            need(self.allocations <= 2, 'Unexpected station allocation')
            failing = self.case == ('first_oom' if self.allocations == 1 else 'second_oom')
            allocation = 0 if failing else (STATION if self.allocations == 1 else PEER)
            if allocation:
                self.live.add(allocation)
            self.trace.append(('alloc', self.previous_pc, a0, allocation, self.get(self.station_ptr)))
            cpu.reg_write(rv.UC_RISCV_REG_A0, allocation)
        elif pc == FREE:
            need(a0 in self.live, 'Unexpected free in station lifetime')
            self.live.remove(a0)
            self.trace.append(('free', self.previous_pc, a0, self.get(self.station_ptr)))
        elif pc in (LOCK, UNLOCK):
            kind = 'lock' if pc == LOCK else 'unlock'
            self.trace.append((kind, self.previous_pc, a0, self.get(self.station_ptr)))
        else:
            name = self.calls.get(pc)
            if name == 'ic_set_interface':
                self.trace.append(('set_interface', self.previous_pc, a0, cpu.reg_read(rv.UC_RISCV_REG_A1)))
            elif name == 'memcpy':
                source = cpu.reg_read(rv.UC_RISCV_REG_A1)
                size = cpu.reg_read(rv.UC_RISCV_REG_A2)
                self.write(a0, bytes(cpu.mem_read(source, size)))
            elif name == 'chm_get_current_band':
                cpu.reg_write(rv.UC_RISCV_REG_A0, 1)
            elif name == 'cnx_remove_all_rc':
                self.trace.append(('clear_rc', self.previous_pc))
            else:
                need(name in NOOP_CALLEES, f'Unexpected SDK boundary at {pc:#x}: {name}')
        cpu.reg_write(rv.UC_RISCV_REG_PC, cpu.reg_read(rv.UC_RISCV_REG_RA))

    def call(self, name):
        self.previous_pc = None
        self.cpu.reg_write(rv.UC_RISCV_REG_GP, self.gp)
        self.cpu.reg_write(rv.UC_RISCV_REG_SP, STACK)
        self.cpu.reg_write(rv.UC_RISCV_REG_RA, RETURN)
        self.cpu.emu_start(self.bodies[name][0], RETURN, count=1000)
        need(self.cpu.reg_read(rv.UC_RISCV_REG_PC) == RETURN, f'{name} did not return')
        return self.cpu.reg_read(rv.UC_RISCV_REG_A0)


def replay(image, layout, gp, case):
    machine = StationReplay(image, layout, gp, case)
    address = {label: site['address'] for label, site in layout['sites'].items()}
    def call_site(label):
        site = layout['sites'][label]
        code = bytes.fromhex(site['bytes'])
        need(code.endswith(bytes.fromhex('8297')), f'Expected indirect call: {label}')
        return site['address'] + len(code) - 2

    station_alloc = ('alloc', call_site('station_alloc'), layout['station_bytes'])
    peer_alloc = ('alloc', call_site('owned_peer_alloc'), layout['peer_bytes'])
    station_publish = ('station_store', address['station_publish'], STATION)
    owned_peer_store = ('owned_peer_store', address['owned_peer_publish'])
    installed = {STATION, PEER}
    returned = machine.call('wifi_create_sta')
    need(returned == (NO_MEM if case.endswith('_oom') else 0), f'Unexpected create result: {case}')

    if case == 'first_oom':
        expected = [station_alloc + (0, 0)]
        need(machine.get(machine.station_ptr) == 0 and not machine.live, 'First OOM retained storage')
    elif case == 'second_oom':
        expected = [station_alloc + (STATION, 0), station_publish, peer_alloc + (0, STATION),
                    owned_peer_store + (0,), ('owned_peer_test', address['owned_peer_null_check'], 0),
                    ('free', call_site('creation_rollback_free'), STATION, STATION),
                    ('station_store', address['creation_rollback_clear'], 0)]
        need(machine.get(machine.station_ptr) == 0 and not machine.live, 'Second OOM retained storage')
    else:
        need(machine.get(machine.station_ptr) == STATION and machine.live == installed,
             'Station storage was not retained')
        need(machine.get(machine.owned_peer_ptr) == PEER, 'Wrong dedicated peer')
        if case == 'reuse':
            expected = []
        else:
            need(machine.get(PEER) == STATION, 'Wrong dedicated peer owner')
            expected = [station_alloc + (STATION, 0), station_publish, peer_alloc + (PEER, STATION),
                        owned_peer_store + (PEER,), ('owned_peer_test', address['owned_peer_null_check'], PEER),
                        ('owner_store', address['owned_peer_backpointer'], STATION)]
            machine.call('wifi_destroy_sta')
            expected += [('lock', call_site('destroy_lock'), LOCK_HANDLE, STATION),
                         ('station_store', address['destroy_unpublish_station'], 0),
                         ('unlock', call_site('destroy_unlock'), LOCK_HANDLE, 0),
                         ('free', call_site('destroy_free_peer'), PEER, 0),
                         ('free', call_site('destroy_free_station'), STATION, 0)]
            need(machine.get(machine.station_ptr) == 0 and not machine.live, 'Destroy retained station storage')

    relevant = [event for event in machine.trace if event[0] not in ('clear_rc', 'set_interface')]
    need(relevant == expected, f'Unexpected {case} lifetime trace: {relevant!r}')
    return dict(create_result=returned, trace=machine.trace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory-elf', 'native-elf', 'app', 'station-audit', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()

    audit = json.loads(args.station_audit.read_text(encoding='utf-8'))
    factory, native, app = (path.read_bytes() for path in (args.factory_elf, args.native_elf, args.app))
    hashes = dict(factory_elf_sha256=sha(factory), native_elf_sha256=sha(native), native_app_sha256=sha(app))
    for key, digest in hashes.items():
        need(audit[key] == digest, f'Station audit does not match {key}')

    original = Image(factory)
    reconstructed = LinkedRuntime(native, app)
    result = dict(**hashes, station_audit_sha256=sha(args.station_audit.read_bytes()),
                  all_concurrent_lifetimes_proved=False, physical_rf_tested=False)
    for variant, image, gp in (('factory', original, startup_gp(original)),
                               ('native', reconstructed, reconstructed.symbol('__global_pointer$')['st_value'])):
        result[variant] = {case: replay(image, audit[variant], gp, case) for case in CASES}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Checked {2 * len(CASES)} isolated RV32 station lifetime scenarios')


if __name__ == '__main__':
    main()
