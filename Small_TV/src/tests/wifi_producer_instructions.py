"""Execute real callback adapters and the BSS peer-to-PM producer chain."""
from copy import deepcopy
from unicorn import riscv_const as rv

from timer_event11_instructions import Event11Probe
from tx_null_instructions import NullProbe


class CallbackProbe(NullProbe):
    """Keep the actual callback and complete null-completion closure together."""
    PACKET,DESCRIPTOR=0x110000,0x120000
    def __init__(self,layout,read):
        """Add only the two verified callback bodies and bounded descriptor cells."""
        selected=deepcopy(layout['prior'])
        selected['functions']=[row for row in selected['functions'] if row['name'] not in ('pm_start','pm_stop','pm_process_tim')]
        selected['functions'].extend(row for row in layout['functions'] if row['name'] in
                                    ('pm_send_sleep_null_cb','pm_send_wake_null_cb'))
        super().__init__(selected,read)
        self.map(self.PACKET,40);self.map(self.DESCRIPTOR,32)

    def read(self,cpu,access,address,size,value,_):
        """Permit only packet+36, descriptor+0 and descriptor+19 producer reads."""
        cells={(self.PACKET+36,4):'packet-descriptor',(self.DESCRIPTOR,4):'descriptor-flags',
               (self.DESCRIPTOR+19,1):'descriptor-status'}
        if (address,size) in cells:self.producer_reads.append(cells[address,size]);return
        return super().read(cpu,access,address,size,value,_)

    def execute(self,cpu,address,size,_):
        """Capture the exact actual parent ingress after the adapter's tail call."""
        if address==self.entries['pm_tx_null_data_done_process']:
            self.ingress.append([cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(3)])
        return super().execute(cpu,address,size,_)

    def call_callback(self,state,now,sleep,status,flags,**kwargs):
        """Run a real adapter and prove its packet/descriptor stay read-only."""
        packet=bytearray(40);packet[36:40]=self.DESCRIPTOR.to_bytes(4,'little')
        descriptor=bytearray(32);descriptor[:4]=flags.to_bytes(4,'little');descriptor[19]=status
        self.cpu.mem_write(self.PACKET,bytes(packet));self.cpu.mem_write(self.DESCRIPTOR,bytes(descriptor))
        self.ingress=[];self.producer_reads=[]
        result=self.call_null(state,now,argument0=self.PACKET,argument2=0x12345678,
            function='pm_send_sleep_null_cb' if sleep else 'pm_send_wake_null_cb',**kwargs)
        assert bytes(self.cpu.mem_read(self.PACKET,40))==packet
        assert bytes(self.cpu.mem_read(self.DESCRIPTOR,32))==descriptor
        result['parent_ingress']=self.ingress;result['producer_reads']=self.producer_reads
        return result


class BssProbe(Event11Probe):
    """Execute the real IE setter, connection producer, PM setter and rearm code."""
    PEER,INFO=0xd0000,0xe0000
    def __init__(self,layout,read):
        """Leave only PM start and log/platform operations as named boundaries."""
        super().__init__(layout['prior']['prior'],read)
        self.producer_layout=layout;self.entries={}
        for row in layout['functions']:
            if row['name'] not in ('ieee80211_set_bss_max_idle_period','cnx_sta_pm.part.0','sta_is_bss_max_idle_enabled'):continue
            start=int(row['start'],0);length=row['linked_bytes']
            self.entries[row['name']]=start;self.map(start,length)
            self.cpu.mem_write(start,read(start,length));self.ranges.append((start,start+length))
        self.map(self.PEER,824);self.map(self.INFO,5);self.map(layout['menuconfig']+64,4)
        cnx=next(row for row in layout['functions'] if row['name']=='cnx_sta_pm.part.0')
        self.start_boundary=next(b['address'] for b in cnx['symbol_bindings'] if b['name']=='pm_start')
        setter=next(row for row in layout['functions'] if row['name']=='ieee80211_set_bss_max_idle_period')
        self.log_boundary=next(b['address'] for b in setter['symbol_bindings'] if b['name']=='wifi_log')
        for address in (self.start_boundary,self.log_boundary):
            assert not any(lo<=address<hi for lo,hi in self.ranges)
            self.map(address,2);self.cpu.mem_write(address,bytes.fromhex('8280'))

    def execute(self,cpu,address,size,_):
        """Record actual PM-start/log inputs; preserve all selected algorithm bodies."""
        if address not in (self.start_boundary,self.log_boundary):return super().execute(cpu,address,size,_)
        if address==self.start_boundary:
            self.trace['calls'].append(['pm-start',*[cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(7)]])
        else:
            args=[cpu.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(3)]
            assert args==[1,1,3];self.trace['calls'].append(['bss-log',*args])
        destination=cpu.reg_read(rv.UC_RISCV_REG_RA)
        for index in self.CALLER:cpu.reg_write(rv.UC_RISCV_REG_X0+index,0xa5000000+index)
        cpu.reg_write(rv.UC_RISCV_REG_PC,destination)

    def read(self,cpu,access,address,size,value,_):
        """Reject unbounded IE/peer reads; each extra field is individually declared."""
        cells=((self.PEER+24,4),(self.PEER+28,4),(self.PEER+32,4),(self.PEER+38,2),
               (self.PEER+40,2),(self.PEER+818,2),(self.INFO+2,1),(self.INFO+3,1),
               (self.INFO+4,1),(self.producer_layout['menuconfig']+64,4))
        if (address,size) in cells:return
        return super().read(cpu,access,address,size,value,_)

    def write(self,cpu,access,address,size,value,_):
        """Limit producer writes to the verified period/options fields."""
        if (address,size) in ((self.PEER+818,2),(self.PEER+820,1)):
            self.trace['peer_writes'].append([address-self.PEER,size,value]);return
        return super().write(cpu,access,address,size,value,_)

    def invoke(self,function,argument0,argument1=0):
        """Invoke one real entry while retaining all state from previous invocations."""
        self.cpu.mem_write(self.STACK,bytes(4096))
        for index in range(1,32):self.cpu.reg_write(rv.UC_RISCV_REG_X0+index,0x12340000+index)
        for register,value in ((rv.UC_RISCV_REG_SP,self.STACK+2048),(rv.UC_RISCV_REG_RA,self.RETURN),
                (rv.UC_RISCV_REG_GP,self.layout['gp']),(rv.UC_RISCV_REG_A0,argument0),(rv.UC_RISCV_REG_A1,argument1)):
            self.cpu.reg_write(register,value)
        saved={i:self.cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in self.SAVED}
        self.cpu.emu_start(self.entries[function],self.RETURN,count=2000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC)==self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP)==self.STACK+2048
        assert all(self.cpu.reg_read(rv.UC_RISCV_REG_X0+i)==value for i,value in saved.items())
        return self.cpu.reg_read(rv.UC_RISCV_REG_A0)

    def call_chain(self,state,period,options,present=True,connect=True,feature_word=None):
        """Retain real IE writes through the connection producer and actual PM rearm."""
        pm,cfg=bytearray(self.layout['g_pm_bytes']),bytearray(self.layout['g_pm_cfg_bytes'])
        pm[36:40]=state.word36.to_bytes(4,'little')
        cfg[52]=state.enabled52;cfg[72:74]=state.period72.to_bytes(2,'little')
        cfg[28:32]=state.fallback28.to_bytes(4,'little');cfg[56:60]=state.adjustment56.to_bytes(4,'little')
        peer=bytearray(824)
        for offset,value in ((24,0x01020304),(28,0x05060708),(32,0x10203040)):
            peer[offset:offset+4]=value.to_bytes(4,'little')
        peer[38:40]=(0xc123).to_bytes(2,'little');peer[40:42]=(100).to_bytes(2,'little')
        peer[818:820]=(54321).to_bytes(2,'little');peer[820]=255
        info=bytes([90,3,period&255,period>>8,options])
        self.cpu.mem_write(self.pm,bytes(pm));self.cpu.mem_write(self.cfg,bytes(cfg))
        self.cpu.mem_write(self.PEER,bytes(peer));self.cpu.mem_write(self.INFO,info)
        self.setter_mode=True;self.trace=dict(calls=[],writes=[],cfg_writes=[],peer_writes=[]);self.instructions=0
        if feature_word is not None:
            self.cpu.mem_write(self.producer_layout['menuconfig']+64,feature_word.to_bytes(4,'little'))
            self.trace['feature_return']=self.invoke('sta_is_bss_max_idle_enabled',0)
        else:
            self.invoke('ieee80211_set_bss_max_idle_period',self.PEER,self.INFO if present else 0)
            if connect:self.invoke('cnx_sta_pm.part.0',self.PEER)
        for offset,size,value in self.trace['writes']:pm[offset:offset+size]=value.to_bytes(size,'little')
        for offset,size,value in self.trace['cfg_writes']:cfg[offset:offset+size]=value.to_bytes(size,'little')
        for offset,size,value in self.trace['peer_writes']:peer[offset:offset+size]=value.to_bytes(size,'little')
        assert bytes(self.cpu.mem_read(self.pm,len(pm)))==pm
        assert bytes(self.cpu.mem_read(self.cfg,len(cfg)))==cfg
        assert bytes(self.cpu.mem_read(self.PEER,len(peer)))==peer
        assert bytes(self.cpu.mem_read(self.INFO,5))==info
        return self.trace
