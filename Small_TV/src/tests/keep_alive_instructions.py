"""Execute unchanged keep-alive bodies with explicit clock/platform boundaries."""
from unicorn import riscv_const as rv

from timer_event11_instructions import Event11Probe


class KeepProbe(Event11Probe):
    """Use real reset/rearm calls; never replace the selected algorithms with stubs."""
    STATION, PEER = 0xc0000, 0xd0000
    def __init__(self, layout, read):
        """Extend the existing private CPU with qualified old/new PM bodies."""
        super().__init__(layout['prior'], read)
        self.keep_layout, self.extra = layout, {}
        self.entries = {f['name']: int(f['start'], 0) for f in layout['functions']}
        for row in layout['functions']:
            lo, hi = int(row['start'], 0), int(row['end'], 0)
            self.map(lo, hi-lo); self.cpu.mem_write(lo, read(lo, hi-lo)); self.ranges.append((lo,hi))
        names = {'pm_enable_active_timer': ('active',0), 'sta_reset_beacon_timeout': ('beacon-reset',0),
                 'ppCheckTxIdle': ('tx-idle',1), 'pm_check_state': ('check',0),
                 'pm_enable_sleep_delay_timer': ('sleep-delay',0),
                 'pm_enable_disconnected_sleep_delay_timer': ('disconnected-delay',0),
                 'pm_incr_coex_active_cnt': ('coex-increment',0), 'wifi_log': ('log',3)}
        for row in layout['functions']:
            for binding in row['symbol_bindings']:
                if binding['name'] in names: self.extra[binding['address']] = names[binding['name']]
        for slot, value in layout['osi_slots'].items():
            self.cpu.mem_write(self.OSI + int(slot), value.to_bytes(4,'little'))
            self.extra[value] = ('clock' if slot == '264' else 'osi400'), 0
        for address in self.extra:
            assert not any(lo <= address < hi for lo,hi in self.ranges)
            self.map(address,2); self.cpu.mem_write(address,bytes.fromhex('8280'))
        if layout['station_global'] is not None:
            for address,size in ((layout['station_global']+16,4),(self.STATION+228,4),(self.PEER+820,1)):
                self.map(address,size)

    def execute(self, cpu, address, size, _):
        """Return a full RV32 ABI register pair for the synthetic 64-bit clock."""
        if address not in self.extra: return super().execute(cpu,address,size,_)
        name, count = self.extra[address]
        args = [cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(count)]
        value = self.results.get(name,0)
        if name == 'clock':
            value = (self.now + self.clocks * 17) & ((1<<64)-1); self.clocks += 1
            args = [value]
        self.trace['calls'].append([name,*args])
        destination = cpu.reg_read(rv.UC_RISCV_REG_RA)
        for index in self.CALLER: cpu.reg_write(rv.UC_RISCV_REG_X0+index,0xa5000000+index)
        cpu.reg_write(rv.UC_RISCV_REG_A0,value & 0xffffffff)
        if name == 'clock': cpu.reg_write(rv.UC_RISCV_REG_A1,value >> 32)
        cpu.reg_write(rv.UC_RISCV_REG_PC,destination)

    def read(self, cpu, access, address, size, value, _):
        """Permit only the two additional, qualified OSI callback cells."""
        if size == 4 and address in (self.OSI+264,self.OSI+400): return
        if self.keep_layout['station_global'] is not None and (address,size) in (
                (self.keep_layout['station_global']+16,4),(self.STATION+228,4),(self.PEER+820,1)): return
        return super().read(cpu,access,address,size,value,_)

    def call(self, name, state, now, success=0, argument2=0, idle=1, check=0, coex=1,
             argument1=0, station=2, peerflag=0):
        """Run one isolated synthetic state and reject any unmodelled write/ABI effect."""
        pm, cfg = bytearray(self.layout['g_pm_bytes']), bytearray(self.layout['g_pm_cfg_bytes'])
        for offset in (1,9,14,15,16,21,22,26,488): pm[offset] = getattr(state,'byte'+str(offset))
        pm[36:40] = state.word36.to_bytes(4,'little')
        pm[88:96] = state.last88.to_bytes(8,'little'); pm[480:488] = state.last480.to_bytes(8,'little')
        cfg[52] = state.enabled52; cfg[72:74] = state.period72.to_bytes(2,'little')
        cfg[28:32] = state.fallback28.to_bytes(4,'little'); cfg[56:60] = state.adjustment56.to_bytes(4,'little')
        self.cpu.mem_write(self.pm,bytes(pm)); self.cpu.mem_write(self.cfg,bytes(cfg))
        if self.keep_layout['station_global'] is not None:
            self.cpu.mem_write(self.keep_layout['station_global']+16,(self.STATION if station else 0).to_bytes(4,'little'))
            self.cpu.mem_write(self.STATION+228,(self.PEER if station==2 else 0).to_bytes(4,'little'))
            self.cpu.mem_write(self.PEER+820,bytes([peerflag]))
        self.cpu.mem_write(self.STACK,bytes(4096))
        for index in range(1,32): self.cpu.reg_write(rv.UC_RISCV_REG_X0+index,0x12340000+index)
        for register,value in ((rv.UC_RISCV_REG_SP,self.STACK+2048), (rv.UC_RISCV_REG_RA,self.RETURN),
                               (rv.UC_RISCV_REG_GP,self.layout['gp']), (rv.UC_RISCV_REG_A0,success),
                               (rv.UC_RISCV_REG_A1,argument1),
                               (rv.UC_RISCV_REG_A2,argument2)):
            self.cpu.reg_write(register,value)
        saved = {i:self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in self.SAVED}
        self.setter_mode = False; self.trace = dict(calls=[],writes=[]); self.instructions = 0
        self.now,self.clocks = now,0
        self.results = {'tx-idle':idle,'check':check,'osi400':coex}
        self.cpu.emu_start(self.entries[name],self.RETURN,count=3000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == self.STACK+2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) == value for i,value in saved.items())
        for offset,size,value in self.trace['writes']: pm[offset:offset+size] = value.to_bytes(size,'little')
        assert bytes(self.cpu.mem_read(self.pm,len(pm))) == pm
        assert bytes(self.cpu.mem_read(self.cfg,len(cfg))) == cfg
        if name == 'pm_keep_alive': self.trace['return_value'] = self.cpu.reg_read(rv.UC_RISCV_REG_A0)
        return self.trace
