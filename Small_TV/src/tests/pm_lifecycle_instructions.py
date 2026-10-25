"""Execute full PM start/stop bodies and selected SDK/ROM cancellation helpers."""
from unicorn import riscv_const as rv

from keep_alive_instructions import KeepProbe


class LifecycleProbe(KeepProbe):
    """Use explicit platform boundaries while preserving real state and cancellation code."""
    MAC,BEACON,CALL48,CALL52=0xa0000,0xb0000,0xe0000,0xe1000

    def __init__(self,layout,read):
        """Add exact helper/ROM code and private callback-table metadata."""
        super().__init__(layout['prior'],read)
        self.lifecycle=layout
        for row in layout['helpers']:
            start=int(row['start'],0);size=row['linked_bytes']
            self.map(start,size);self.cpu.mem_write(start,read(start,size));self.ranges.append((start,start+size))
        for row in layout['rom']['functions']:
            start=int(row['start'],0);raw=bytes.fromhex(row['bytes_hex'])
            self.map(start,len(raw));self.cpu.mem_write(start,raw);self.ranges.append((start,start+len(raw)))
        for address,size in ((self.MAC,6),(self.BEACON,56),(layout['beacon_pointer'],4),
                             (self.pm-8,8),(layout['rom']['pointer'],4)):
            self.map(address,size)
        self.cpu.mem_write(layout['rom']['pointer'],self.pm.to_bytes(4,'little'))
        names={'memcpy':('memcpy',3),'wifi_log':('lifecycle-log',0),
               'pm_scale_listen_interval':('scale-listen',0),'hal_set_sta_tsf_wakeup':('tsf-wake',1),
               'dbg_lmac_ps_statis_reset':('debug-reset',0),'pm_update_next_tbtt':('next-tbtt',3),
               'hal_set_rx_beacon_pti':('rx-pti',1),'hal_set_rx_beacon_time':('rx-time',2),
               'pm_beacon_monitor_init':('beacon-monitor',0),'pm_on_coex_schm_status_config':('coex-status',1),
               'wifi_gpio_debug':('gpio',2),'pm_update_by_connectionless_status':('connectionless',0),
               'hal_pm_unblock_txq':('unblock',0),'hal_disable_sta_tbtt':('disable-tbtt',0),
               'hal_clear_sta_tsf_active_state':('tsf-clear',0),'hal_disable_sta_beacon_filter':('disable-filter',0),
               'pm_set_state':('set-state',1),'ppProcessWaitingQueue':('waiting-queue',0),
               'pm_dream':('dream',0),'pm_wake_done':('wake-done',0),'pm_coex_pwr_update':('coex-power',0),
               'pm_coex_schm_process_restart':('coex-restart',0),'pm_coex_update_rx_beacon_pti':('coex-beacon',1)}
        for row in layout['prior']['functions']:
            if row['name'] not in ('pm_start','pm_stop'):continue
            for binding in row['symbol_bindings']:
                if binding['name'] in names:self.extra[binding['address']]=names[binding['name']]
        for slot,value in layout['osi_slots'].items():
            self.cpu.mem_write(self.OSI+int(slot),value.to_bytes(4,'little'))
            self.extra[value]=({'228':'disarm-any','424':'osi424','436':'osi436'}[slot],1 if slot!='424' else 2)
        self.extra[layout['prior']['osi_slots']['400']]='coex',0
        self.extra[self.CALL48]='beacon48',7;self.extra[self.CALL52]='beacon52',0
        for address in self.extra:
            assert not any(lo<=address<hi for lo,hi in self.ranges)
            self.map(address,2);self.cpu.mem_write(address,bytes.fromhex('8280'))

    def prepare(self,pm,cfg,env):
        """Supply disposable state once; later invocations retain their real stores."""
        assert len(pm)==self.layout['g_pm_bytes'] and len(cfg)==self.layout['g_pm_cfg_bytes']
        self.cpu.mem_write(self.pm,pm);self.cpu.mem_write(self.cfg,cfg)
        self.cpu.mem_write(self.pm-8,bytes.fromhex('78563412efcdab89'))
        self.cpu.mem_write(self.MAC,env['mac'])
        self.cpu.mem_write(self.lifecycle['beacon_pointer'],self.BEACON.to_bytes(4,'little'))
        self.cpu.mem_write(self.BEACON,bytes(56))
        for offset,present,target in ((48,env['beacon48'],self.CALL48),(52,env['beacon52'],self.CALL52)):
            self.cpu.mem_write(self.BEACON+offset,(target if present else 0).to_bytes(4,'little'))

    def word(self,address):
        """Read one private fixture result; never contact a live guest."""
        return int.from_bytes(self.cpu.mem_read(address,4),'little')

    def execute(self,cpu,address,size,_):
        """Normalize only declared platform calls; execute all selected code unchanged."""
        if address not in self.extra:return super().execute(cpu,address,size,_)
        name,count=self.extra[address]
        if name=='clock':return super().execute(cpu,address,size,_)
        args=[cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(count)];value=0
        if name=='coex':
            value=self.env['coex'][self.coex_index];self.coex_index+=1;args=[value]
        elif name=='memcpy':
            assert args==[self.pm+3,self.MAC,6]
            raw=bytes(cpu.mem_read(self.MAC,6));cpu.mem_write(self.pm+3,raw)
            args=[3,raw.hex(),6];value=self.pm+3
        elif name=='next-tbtt':
            a0,pointer,a2=args
            assert self.STACK<=pointer<pointer+8<=self.STACK+4096
            raw=bytes(cpu.mem_read(pointer,8));args=[a0,int.from_bytes(raw[:4],'little'),int.from_bytes(raw[4:],'little'),a2]
        elif name=='osi424':
            request,pointer=args;assert request==0 and self.STACK<=pointer<self.STACK+4096
            cpu.mem_write(pointer,bytes([self.env['pti']]));args=[request]
        elif name=='coex-beacon':value=self.env['pti']
        elif name=='disarm-any':
            offset=args[0]-self.pm;assert offset in (180,200,260,492)
            name,args='disarm',[offset]
        elif name=='lifecycle-log':
            label=self.lifecycle['log_formats'].get(str(cpu.reg_read(rv.UC_RISCV_REG_A3)))
            assert label in ('start','beacon','stop')
            prefix=[cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(3)]
            assert prefix==([1,1,3] if label=='beacon' else [6,4096,3])
            name='log-'+label;args=[cpu.reg_read(rv.UC_RISCV_REG_A4+i) for i in range(1 if label=='start' else 4)]
        self.trace['calls'].append([name,*args])
        destination=cpu.reg_read(rv.UC_RISCV_REG_RA)
        for index in self.CALLER:cpu.reg_write(rv.UC_RISCV_REG_X0+index,0xa5000000+index)
        cpu.reg_write(rv.UC_RISCV_REG_A0,value);cpu.reg_write(rv.UC_RISCV_REG_PC,destination)

    def read(self,cpu,access,address,size,value,_):
        """Allow only extra table, ROM-binding and known private-data reads."""
        if (address,size) in ((self.lifecycle['beacon_pointer'],4),(self.BEACON+48,4),(self.BEACON+52,4),
                             (self.lifecycle['rom']['pointer'],4),(self.OSI+424,4),(self.OSI+436,4)):return
        return super().read(cpu,access,address,size,value,_)

    def write(self,cpu,access,address,size,value,_):
        """Record real configuration/global stores in addition to the base PM guard."""
        if self.cfg<=address<address+size<=self.cfg+self.layout['g_pm_cfg_bytes']:
            self.trace['cfg_writes'].append([address-self.cfg,size,value]);return
        if size==4 and address in (self.pm-8,self.pm-4):
            self.trace['global_writes'].append([address-self.pm,value]);return
        return super().write(cpu,access,address,size,value,_)

    def invoke(self,name,args,env):
        """Run an entire start/stop entry, preserving state for repeated/lifecycle tests."""
        self.trace=dict(calls=[],writes=[],cfg_writes=[],global_writes=[])
        self.setter_mode=False;self.instructions=0;self.env=env
        self.now,self.clocks,self.coex_index=env['now'],0,0
        self.results={}
        self.cpu.mem_write(self.STACK,bytes(4096))
        for index in range(1,32):self.cpu.reg_write(rv.UC_RISCV_REG_X0+index,0x12340000+index)
        self.cpu.reg_write(rv.UC_RISCV_REG_SP,self.STACK+2048)
        self.cpu.reg_write(rv.UC_RISCV_REG_RA,self.RETURN);self.cpu.reg_write(rv.UC_RISCV_REG_GP,self.layout['gp'])
        for index,value in enumerate(args):self.cpu.reg_write(rv.UC_RISCV_REG_A0+index,value)
        saved={i:self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in self.SAVED}
        self.cpu.emu_start(self.entries[name],self.RETURN,count=5000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC)==self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP)==self.STACK+2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0+i)==value for i,value in saved.items())
        return dict(trace=self.trace,pm=bytes(self.cpu.mem_read(self.pm,self.layout['g_pm_bytes'])),
                    cfg=bytes(self.cpu.mem_read(self.cfg,self.layout['g_pm_cfg_bytes'])))
