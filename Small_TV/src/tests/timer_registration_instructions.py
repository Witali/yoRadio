"""Execute real OSI registration, timer initialization and posting instructions."""
from unicorn import riscv_const as rv

from timer_event11_instructions import Event11Probe


class RegistrationProbe(Event11Probe):
    """Keep the real call chain; isolate only declared backend/platform boundaries."""
    CONFIG, POST = 0x80000, 0x90000

    def __init__(self, layout, read):
        """Add qualified code and the initialized OSI table to the existing private CPU."""
        super().__init__(layout['prior'], read)
        self.registration = layout
        self.post_slot = layout['post_callback_slot']
        self.table = layout['prior']['osi_table']['address']
        self.table_data = read(self.table, 480)
        self.entries = {f['name']: int(f['start'], 0) for f in layout['functions']}
        for row in (*layout['functions'], layout['timer_setfn']):
            lo, hi = int(row['start'], 0), int(row['end'], 0)
            self.map(lo, hi - lo); self.cpu.mem_write(lo, read(lo, hi - lo))
            self.ranges.append((lo, hi))
        for address, size in ((self.CONFIG, 160), (self.table, 480), (self.post_slot, 4)):
            self.map(address, size)
        names = {'puts': ('puts', 1), 'net80211_printf': ('printf', 3),
                 'wifi_api_lock': ('lock', 0), 'memset': ('memset', 3),
                 'pm_set_state': ('set-state', 1), 'ppRegisterTxCallback': ('tx-callback', 3),
                 'hal_set_sta_tsf_wakeup': ('tsf-wake', 1),
                 'hal_clear_sta_tsf_active_state': ('tsf-clear', 0)}
        self.extensions = {}
        for row in layout['functions']:
            for binding in row['symbol_bindings']:
                if binding['name'] in names:
                    self.extensions[binding['address']] = names[binding['name']]
        self.extensions[layout['timer_setfn']['target']] = 'setfn', 3
        self.extensions.update({value: ('clock' + slot, 0) for slot, value in layout['clock_slots'].items()})
        self.extensions[self.POST] = 'post', 3
        for address in self.extensions:
            assert not any(lo <= address < hi for lo, hi in self.ranges)
            self.map(address, 2); self.cpu.mem_write(address, bytes.fromhex('8280'))
        self.map(self.OSI + 236, 4)
        self.cpu.mem_write(self.OSI + 236, int(layout['timer_setfn']['start'], 0).to_bytes(4, 'little'))
        for slot, value in layout['clock_slots'].items():
            self.cpu.mem_write(self.OSI + int(slot), value.to_bytes(4, 'little'))
        self.lock_return, self.post_return = 0x1234, 0
        self.timer_bindings = {}
        self.reset()

    def reset(self, registered=0, version=None, magic=None):
        """Create a disposable initial state; no credentials or live guest RAM are read."""
        raw = bytearray(self.table_data)
        if version is not None: raw[:4] = version.to_bytes(4, 'little')
        if magic is not None: raw[-4:] = magic.to_bytes(4, 'little')
        self.cpu.mem_write(self.table, bytes(raw))
        self.cpu.mem_write(self.osi_global, registered.to_bytes(4, 'little'))
        self.cpu.mem_write(self.post_slot, bytes(4))
        self.cpu.mem_write(self.CONFIG, self.table.to_bytes(4, 'little') + bytes(156))
        self.cpu.mem_write(self.pm, bytes([0xa5]) * self.layout['g_pm_bytes'])
        self.cpu.mem_write(self.cfg, bytes(range(self.layout['g_pm_cfg_bytes'])))
        self.timer_bindings = {}

    def execute(self, cpu, address, size, _):
        """Run selected bodies, recording only explicit external backend effects."""
        if address not in self.extensions:
            return super().execute(cpu, address, size, _)
        name, count = self.extensions[address]
        args = [cpu.reg_read(rv.UC_RISCV_REG_A0 + i) for i in range(count)]
        self.trace['calls'].append([name, *args])
        value = 0
        if name == 'lock': value = self.lock_return
        elif name == 'post': value = self.post_return
        elif name == 'memset':
            assert args == [self.pm, 0, self.layout['g_pm_bytes']]
            self.cpu.mem_write(self.pm, bytes(args[2])); value = self.pm
        elif name == 'setfn':
            timer, callback, argument = args
            assert self.pm <= timer < timer + 20 <= self.pm + self.layout['g_pm_bytes']
            assert timer not in self.timer_bindings
            self.timer_bindings[timer] = callback, argument
        destination = cpu.reg_read(rv.UC_RISCV_REG_RA)
        for index in self.CALLER:
            cpu.reg_write(rv.UC_RISCV_REG_X0 + index, 0xa5000000 + index)
        cpu.reg_write(rv.UC_RISCV_REG_A0, value)
        cpu.reg_write(rv.UC_RISCV_REG_PC, destination)

    def read(self, cpu, access, address, size, value, _):
        """Allow only additional registration fields; preserve the base access guard."""
        if any(lo <= address < address + size <= lo + extent for lo, extent in (
                (self.table, 480), (self.post_slot, 4), (self.CONFIG, 160),
                (self.OSI + 236, 4), (self.OSI + 248, 8))):
            return
        return super().read(cpu, access, address, size, value, _)

    def write(self, cpu, access, address, size, value, _):
        """Capture the exact OSI/post stores; reject writes to the supplied table."""
        if address in (self.osi_global, self.post_slot) and size == 4:
            self.trace['globals'].append([address, value]); return
        return super().write(cpu, access, address, size, value, _)

    def invoke(self, name, *args):
        """Execute one real entry while retaining its SRAM effects for the next call."""
        self.setter_mode = False
        self.trace = dict(calls=[], writes=[], globals=[]); self.instructions = 0
        self.cpu.mem_write(self.STACK, bytes(4096))
        for index in range(1, 32):
            self.cpu.reg_write(rv.UC_RISCV_REG_X0 + index, 0x12340000 + index)
        self.cpu.reg_write(rv.UC_RISCV_REG_GP, self.layout['gp'])
        self.cpu.reg_write(rv.UC_RISCV_REG_SP, self.STACK + 2048)
        self.cpu.reg_write(rv.UC_RISCV_REG_RA, self.RETURN)
        for index, argument in enumerate(args):
            self.cpu.reg_write(rv.UC_RISCV_REG_A0 + index, argument)
        saved = {i: self.cpu.reg_read(rv.UC_RISCV_REG_X0 + i) for i in self.SAVED}
        self.cpu.emu_start(self.entries[name] if isinstance(name, str) else name, self.RETURN, count=3000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == self.STACK + 2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0 + i) == value for i, value in saved.items())
        self.trace['return_value'] = self.cpu.reg_read(rv.UC_RISCV_REG_A0)
        return self.trace

    def word(self, address):
        """Read a fixture result only; this is not a live-guest memory interface."""
        return int.from_bytes(self.cpu.mem_read(address, 4), 'little')
