"""Run each complete TIM body with bounded PM/counter state and ABI checks."""
from unicorn import riscv_const as rv

from keep_alive_instructions import KeepProbe


class TimProbe(KeepProbe):
    """Execute real factory predicate; leave named scheduler/RF boundaries explicit."""
    def __init__(self, layout, read):
        """Add only the actual TIM counter words and its declared helper boundaries."""
        super().__init__(layout, read)
        self.counter = layout['counter_address']
        self.map(self.counter + 8, 8)
        names = {'pm_is_in_wifi_slice_threshold': ('slice', 3),
                 'pm_enable_dream_timer': ('dream-timer', 0),
                 'pm_disable_sleep_delay_timer': ('disable-sleep-delay', 0),
                 'pm_sleep': ('sleep', 0), 'pm_disable_active_timer': ('disable-active', 0),
                 'pm_active_timeout_process': ('active-timeout', 1)}
        row = next(row for row in layout['functions'] if row['name'] == 'pm_process_tim')
        for binding in row['symbol_bindings']:
            if binding['name'] in names: self.extra[binding['address']] = names[binding['name']]
        self.extra[layout['osi_slots']['408']] = ('coex408', 3)
        for address in self.extra:
            assert not any(lo <= address < hi for lo, hi in self.ranges)
            self.map(address, 2)
            self.cpu.mem_write(address, bytes.fromhex('8280'))

    def read(self, cpu, access, address, size, value, _):
        """Restrict extra data reads to two known counter words and slot 408."""
        if size == 4 and address in (self.counter+8, self.counter+12, self.OSI+408): return
        return super().read(cpu, access, address, size, value, _)

    def write(self, cpu, access, address, size, value, _):
        """Keep counter writes separate from PM state and never allow adjacent data."""
        if size == 4 and address in (self.counter+8, self.counter+12):
            self.trace['counter_writes'].append([address-self.counter, size, value])
            return
        return super().write(cpu, access, address, size, value, _)

    def call_tim(self, state, now, argument0=0, argument1=0, slice_allowed=1):
        """Initialize fresh disposable state and verify complete memory/ABI preservation."""
        pm, cfg = bytearray(self.layout['g_pm_bytes']), bytearray(self.layout['g_pm_cfg_bytes'])
        for offset in (1,9,14,15,16,20,21,22,26,27,468,488): pm[offset] = getattr(state, 'byte'+str(offset))
        for offset, size, value in ((36,4,state.word36),(60,4,state.window60),
                (88,8,state.last88),(112,8,state.deadline112),(480,8,state.last480)):
            pm[offset:offset+size] = value.to_bytes(size, 'little')
        cfg[52] = state.enabled52
        cfg[72:74] = state.period72.to_bytes(2, 'little')
        cfg[28:32] = state.fallback28.to_bytes(4, 'little')
        counters = bytearray(state.counter8.to_bytes(4,'little') + state.counter12.to_bytes(4,'little'))
        self.cpu.mem_write(self.pm, bytes(pm)); self.cpu.mem_write(self.cfg, bytes(cfg))
        self.cpu.mem_write(self.counter+8, bytes(counters)); self.cpu.mem_write(self.STACK, bytes(4096))
        for index in range(1,32): self.cpu.reg_write(rv.UC_RISCV_REG_X0+index, 0x12340000+index)
        for register,value in ((rv.UC_RISCV_REG_SP,self.STACK+2048),(rv.UC_RISCV_REG_RA,self.RETURN),
                (rv.UC_RISCV_REG_GP,self.layout['gp']),(rv.UC_RISCV_REG_A0,argument0),
                (rv.UC_RISCV_REG_A1,argument1)):
            self.cpu.reg_write(register,value)
        saved = {i:self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in self.SAVED}
        self.setter_mode = False
        self.trace = dict(calls=[],writes=[],counter_writes=[])
        self.now, self.clocks, self.instructions = now, 0, 0
        self.results = {'slice': slice_allowed}
        self.cpu.emu_start(self.entries['pm_process_tim'],self.RETURN,count=3000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == self.STACK+2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0+i)==value for i,value in saved.items())
        for offset,size,value in self.trace['writes']: pm[offset:offset+size]=value.to_bytes(size,'little')
        for offset,size,value in self.trace['counter_writes']: counters[offset-8:offset-8+size]=value.to_bytes(size,'little')
        assert bytes(self.cpu.mem_read(self.pm,len(pm))) == pm
        assert bytes(self.cpu.mem_read(self.cfg,len(cfg))) == cfg
        assert bytes(self.cpu.mem_read(self.counter+8,8)) == counters
        return self.trace
