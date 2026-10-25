"""Run the real event-11 wrapper, handler and rearm body in a private RV32 CPU."""
from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import riscv_const as rv


class Event11Probe:
    """Copy exact code; stub only named transitive helpers and OSI callbacks."""
    STACK, OSI, MESSAGE, RETURN = 0x10000, 0x30000, 0x50000, 0x60000
    SAVED = (3, 4, 8, 9, *range(18, 28))
    CALLER = (1, 5, 6, 7, *range(10, 18), *range(28, 32))

    def __init__(self, layout, read):
        """Map only bounded selected instructions and disposable input state."""
        self.layout = layout
        self.pm, self.cfg, self.osi_global = (layout[k] for k in ('g_pm', 'g_pm_cfg', 'osi_pointer'))
        self.cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
        self.pages, self.visited, self.ext = set(), set(), {}
        self.ranges = [(int(f['start'], 0), int(f['end'], 0))
                       for f in (*layout['functions'], layout['configuration_function'])]
        self.setter_start = self.ranges[-1][0]
        self.start = self.ranges[0][0]
        for lo, hi in self.ranges:
            self.map(lo, hi - lo)
            self.cpu.mem_write(lo, read(lo, hi - lo))
        for start, size in ((self.STACK, 4096), (self.OSI, 480), (self.MESSAGE, 8),
                            (self.RETURN, 2), (self.pm, layout['g_pm_bytes']),
                            (self.cfg, layout['g_pm_cfg_bytes']), (self.osi_global, 4)):
            self.map(start, size)
        names = {'pm_go_to_wake': ('wake', 2), 'pm_dream': ('dream', 0),
                 'pm_send_nullfunc': ('null', 1), 'wifi_log': ('log', 3),
                 'pm_disable_max_idle_timer': ('disable', 0)}
        for binding in (*layout['functions'][1]['symbol_bindings'],
                        *layout['configuration_function']['symbol_bindings']):
            if binding['name'] in names:
                self.ext[binding['address']] = names[binding['name']]
        assert {'wake', 'dream', 'null'} <= {name for name, _ in self.ext.values()}
        self.cpu.mem_write(self.osi_global, self.OSI.to_bytes(4, 'little'))
        self.timer_slots = []
        for slot, name, count in ((224, 'arm224', 3), (228, 'disarm', 1), (240, 'arm240', 3)):
            callback = layout['osi_table']['wrappers'][str(slot)]['address']
            self.ext[callback] = name, count
            self.timer_slots.append(self.OSI + slot)
            self.cpu.mem_write(self.OSI + slot, callback.to_bytes(4, 'little'))
        for address in self.ext:
            assert not any(lo <= address < hi for lo, hi in self.ranges)
            self.map(address, 2)
            # Declared host-only external stub; all selected bodies stay intact.
            self.cpu.mem_write(address, bytes.fromhex('8280'))
        self.cpu.hook_add(UC_HOOK_CODE, self.execute)
        self.cpu.hook_add(UC_HOOK_MEM_READ, self.read)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.write)

    def map(self, start, size):
        """Map each private page once; this never connects to a live QEMU VM."""
        for page in range(start & ~4095, (start + size + 4095) & ~4095, 4096):
            if page not in self.pages:
                self.cpu.mem_map(page, 4096)
                self.pages.add(page)

    def execute(self, cpu, address, size, _):
        """Record literal body coverage; poison caller-saved state at each helper."""
        if any(lo <= address < address + size <= hi for lo, hi in self.ranges):
            self.visited.add(address)
            self.instructions += 1
            return
        if address not in self.ext:
            raise ValueError('Event 11 left qualified code/stubs: ' + hex(address))
        name, count = self.ext[address]
        args = [cpu.reg_read(rv.UC_RISCV_REG_A0 + i) for i in range(count)]
        if name in ('arm224', 'arm240', 'disarm'):
            assert args.pop(0) == self.pm + 492
        if name == 'log':
            log_anchor = next(b['address'] for b in self.layout['functions'][1]['symbol_bindings']
                              if b['name'] == '.LANCHOR15')
            assert cpu.reg_read(rv.UC_RISCV_REG_A3) == log_anchor
        self.trace['calls'].append([name, *args])
        destination = cpu.reg_read(rv.UC_RISCV_REG_RA)
        for index in self.CALLER:
            cpu.reg_write(rv.UC_RISCV_REG_X0 + index, 0xa5000000 + index)
        cpu.reg_write(rv.UC_RISCV_REG_PC, destination)

    def read(self, cpu, access, address, size, value, _):
        """Reject data reads outside the known state, message, table and stack."""
        ranges = [(self.STACK, 4096), (self.pm, self.layout['g_pm_bytes']),
                  (self.cfg, self.layout['g_pm_cfg_bytes']), (self.MESSAGE, 8),
                  (self.osi_global, 4), *((slot, 4) for slot in self.timer_slots)]
        if not any(lo <= address < address + size <= lo + extent for lo, extent in ranges):
            raise ValueError('Unexpected event-11 data read: ' + hex(address))

    def write(self, cpu, access, address, size, value, _):
        """Track every body PM write; only stack writes may be ignored."""
        if self.STACK <= address < address + size <= self.STACK + 4096:
            return
        if self.setter_mode and self.cfg <= address < address + size <= self.cfg + self.layout['g_pm_cfg_bytes']:
            self.trace['cfg_writes'].append([address - self.cfg, size, value])
            return
        if not self.pm <= address < address + size <= self.pm + self.layout['g_pm_bytes']:
            raise ValueError('Unexpected event-11 data write: ' + hex(address))
        self.trace['writes'].append([address - self.pm, size, value])

    def call(self, state, period=None):
        """Execute a wrapper or setter; verify stack, ABI and every SRAM write."""
        self.setter_mode = period is not None
        pm, cfg = bytearray(self.layout['g_pm_bytes']), bytearray(self.layout['g_pm_cfg_bytes'])
        for offset in (1, 14, 15, 16, 488):
            pm[offset] = getattr(state, 'byte' + str(offset))
        pm[36:40] = state.word36.to_bytes(4, 'little')
        cfg[52] = state.enabled52
        cfg[72:74] = state.period72.to_bytes(2, 'little')
        cfg[28:32] = state.fallback28.to_bytes(4, 'little')
        cfg[56:60] = state.adjustment56.to_bytes(4, 'little')
        self.cpu.mem_write(self.pm, bytes(pm)); self.cpu.mem_write(self.cfg, bytes(cfg))
        self.cpu.mem_write(self.MESSAGE, self.pm.to_bytes(4, 'little') + bytes(4))
        self.cpu.mem_write(self.STACK, bytes(4096))
        for index in range(1, 32):
            self.cpu.reg_write(rv.UC_RISCV_REG_X0 + index, 0x12340000 + index)
        self.cpu.reg_write(rv.UC_RISCV_REG_SP, self.STACK + 2048)
        self.cpu.reg_write(rv.UC_RISCV_REG_RA, self.RETURN)
        self.cpu.reg_write(rv.UC_RISCV_REG_GP, self.layout['gp'])
        self.cpu.reg_write(rv.UC_RISCV_REG_A0, period if self.setter_mode else self.MESSAGE)
        saved = {i: self.cpu.reg_read(rv.UC_RISCV_REG_X0 + i) for i in self.SAVED}
        self.trace = dict(calls=[], writes=[]); self.instructions = 0
        if self.setter_mode:
            self.trace['cfg_writes'] = []
        self.cpu.emu_start(self.setter_start if self.setter_mode else self.start, self.RETURN, count=1000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == self.STACK + 2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0 + i) == value for i, value in saved.items())
        for offset, size, value in self.trace['writes']:
            pm[offset:offset + size] = value.to_bytes(size, 'little')
        for offset, size, value in self.trace.get('cfg_writes', []):
            cfg[offset:offset + size] = value.to_bytes(size, 'little')
        assert bytes(self.cpu.mem_read(self.pm, len(pm))) == pm
        assert bytes(self.cpu.mem_read(self.cfg, len(cfg))) == cfg
        if not self.setter_mode:
            self.trace['return_value'] = self.cpu.reg_read(rv.UC_RISCV_REG_A0)
        return self.trace
