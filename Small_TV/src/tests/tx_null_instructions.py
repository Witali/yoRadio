"""Execute complete null/quick-wake/state bodies in private bounded RV32 memory."""
from unicorn import riscv_const as rv

from keep_alive_instructions import KeepProbe


class NullProbe(KeepProbe):
    """Keep parent, reset/rearm, quick-wake and state setter instructions intact."""
    def __init__(self,layout,read):
        """Map two additional counter cells and explicit transitive platform helpers."""
        super().__init__(layout,read)
        self.counter=layout['counter_address'];self.map(self.counter+28,8)
        names={'pm_is_in_wifi_slice_threshold':('slice',3),
               'pm_offchan_execute_ready_cb':('offchan-ready',1),
               'hal_clear_rx_beacon_pti':('clear-rx-pti',0),
               'wifi_gpio_debug':('gpio',2),'ppProcessWaitingQueue':('waiting-queue',0),
               'pm_sleep':('sleep',0)}
        for row in layout['functions']:
            for binding in row['symbol_bindings']:
                if binding['name'] in names:self.extra[binding['address']]=names[binding['name']]
        self.extra[layout['osi_slots']['412']]=('osi412',1)
        for address in self.extra:
            assert not any(lo<=address<hi for lo,hi in self.ranges)
            self.map(address,2);self.cpu.mem_write(address,bytes.fromhex('8280'))

    def read(self,cpu,access,address,size,value,_):
        """Track station pointer gates and reject every undeclared memory read."""
        if size==4 and address in (self.counter+28,self.counter+32,self.OSI+412):return
        station=self.keep_layout['station_global']
        if station is not None:
            cells={(station+16,4):'station-pointer',(self.STATION+228,4):'peer-pointer',
                   (self.PEER+820,1):'peer-byte820'}
            if (address,size) in cells:self.trace['station_reads'].append(cells[address,size])
        return super().read(cpu,access,address,size,value,_)

    def write(self,cpu,access,address,size,value,_):
        """Separate actual counter stores from actual PM stores; reject other writes."""
        if size==4 and address in (self.counter+28,self.counter+32):
            self.trace['counter_writes'].append([address-self.counter,size,value]);return
        return super().write(cpu,access,address,size,value,_)

    def call_null(self,state,now,argument0=0,argument1=0,argument2=0,check=1,
                  idle=1,coex=1,slice_allowed=1,station=2,peerflag=0,
                  function='pm_tx_null_data_done_process'):
        """Initialize disposable state, invoke a real entry and check memory and ABI."""
        pm,cfg=bytearray(self.layout['g_pm_bytes']),bytearray(self.layout['g_pm_cfg_bytes'])
        for offset in (1,9,10,14,15,16,19,20,21,22,26,27,456,468,488,543):
            if offset<len(pm):pm[offset]=getattr(state,'byte'+str(offset))
        for offset,size,value in ((36,4,state.word36),(88,8,state.last88),(480,8,state.last480),
                                  (568,8,state.deadline568)):
            if offset+size<=len(pm):pm[offset:offset+size]=value.to_bytes(size,'little')
        cfg[52]=state.enabled52;cfg[72:74]=state.period72.to_bytes(2,'little')
        cfg[28:32]=state.fallback28.to_bytes(4,'little');cfg[56:60]=state.adjustment56.to_bytes(4,'little')
        counters=bytearray(state.counter28.to_bytes(4,'little')+state.counter32.to_bytes(4,'little'))
        self.cpu.mem_write(self.pm,bytes(pm));self.cpu.mem_write(self.cfg,bytes(cfg))
        self.cpu.mem_write(self.counter+28,bytes(counters));self.cpu.mem_write(self.STACK,bytes(4096))
        if self.keep_layout['station_global'] is not None:
            self.cpu.mem_write(self.keep_layout['station_global']+16,(self.STATION if station else 0).to_bytes(4,'little'))
            self.cpu.mem_write(self.STATION+228,(self.PEER if station==2 else 0).to_bytes(4,'little'))
            self.cpu.mem_write(self.PEER+820,bytes([peerflag]))
        for index in range(1,32):self.cpu.reg_write(rv.UC_RISCV_REG_X0+index,0x12340000+index)
        for register,value in ((rv.UC_RISCV_REG_SP,self.STACK+2048),(rv.UC_RISCV_REG_RA,self.RETURN),
                (rv.UC_RISCV_REG_GP,self.layout['gp']),(rv.UC_RISCV_REG_A0,argument0),
                (rv.UC_RISCV_REG_A1,argument1),(rv.UC_RISCV_REG_A2,argument2)):
            self.cpu.reg_write(register,value)
        saved={i:self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in self.SAVED}
        self.setter_mode=False;self.trace=dict(calls=[],writes=[],counter_writes=[],station_reads=[])
        self.now,self.clocks,self.instructions=now,0,0
        self.results={'check':check,'tx-idle':idle,'osi400':coex,'slice':slice_allowed}
        self.cpu.emu_start(self.entries[function],self.RETURN,count=4000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC)==self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP)==self.STACK+2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0+i)==value for i,value in saved.items())
        for offset,size,value in self.trace['writes']:pm[offset:offset+size]=value.to_bytes(size,'little')
        for offset,size,value in self.trace['counter_writes']:counters[offset-28:offset-28+size]=value.to_bytes(size,'little')
        assert bytes(self.cpu.mem_read(self.pm,len(pm)))==pm
        assert bytes(self.cpu.mem_read(self.cfg,len(cfg)))==cfg
        assert bytes(self.cpu.mem_read(self.counter+28,8))==counters
        if function=='pm_tx_null_data_done_quick_wake_process':
            self.trace['return_value']=self.cpu.reg_read(rv.UC_RISCV_REG_A0)
        return self.trace
