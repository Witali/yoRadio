"""Run the corrected rearm through real OSI wrappers and legacy timer backends."""
from copy import deepcopy
from unicorn import UC_MEM_WRITE

from runtime_call_instructions import Fixture,END,STACK,HEAP
from reverse.nothrow_linkage import LinkedRuntime


class RangeProbe(Fixture):
    """Leave only esp_timer public operations and nonreturning checks as boundaries."""
    OSI_A,OSI_B=0x30000,0x31000
    HANDLE=HEAP+256
    NOW=0x100000080

    def __init__(self,elf,app,qualified):
        """Map exact replacement, SDK cancellation, OSI wrappers and ms/us backends."""
        linked=LinkedRuntime(elf,app)
        rows=deepcopy([*qualified['functions'],qualified['disable'],*qualified['backends']])
        for row in rows:row['code_sha256']=row['linked_code_sha256']
        for slot,row in qualified['osi_table']['wrappers'].items():
            rows.append(dict(name='osi-'+slot,start=hex(row['address']),linked_bytes=row['bytes'],code_sha256=row['sha256']))
        super().__init__('native',dict(functions=rows,allocator_veneer=None),linked.read)
        self.initial[3]=linked.symbol('__global_pointer$')['st_value']
        self.pm,self.cfg,self.osi_pointer=(qualified[k] for k in ('g_pm','g_pm_cfg','osi_pointer'))
        for address,length in ((self.pm,584),(self.cfg,76),(self.osi_pointer,4),(self.OSI_A,480),(self.OSI_B,480)):
            self.map(address,length)
        self.osi_bytes=bytearray(480)
        self.osi_bytes[:4]=(9).to_bytes(4,'little');self.osi_bytes[-4:]=bytes.fromhex('afbeadde')
        for slot,row in qualified['osi_table']['wrappers'].items():
            self.osi_bytes[int(slot):int(slot)+4]=row['address'].to_bytes(4,'little')
        names={b['name']:b['address'] for row in qualified['backends'] for b in row['symbol_bindings'] if b['kind']=='call'}
        for name in ('esp_timer_stop','esp_timer_start_once','esp_timer_start_periodic','__assert_func','_esp_error_check_failed'):
            self.boundary(name,names[name],lambda args,name=name:self.platform(name,args))

    def memory(self,cpu,access,address,size,value,_):
        """Allow only bounded private state; every non-stack CPU write is forbidden."""
        if STACK-4096<=address<address+size<=STACK+4096:return
        assert access!=UC_MEM_WRITE,('unexpected timer write',hex(address),size)
        ranges=((self.pm,584),(self.cfg,76),(self.osi_pointer,4),(self.OSI_A,480),(self.OSI_B,480))
        assert any(lo<=address<address+size<=lo+length for lo,length in ranges),('unexpected timer read',hex(address),size)
        if size==4 and address in tuple(base+slot for base in (self.OSI_A,self.OSI_B) for slot in (224,228,240)):
            self.adapter_reads.append([address-self.OSI_A if address<self.OSI_B else address-self.OSI_B,
                                       'A' if address<self.OSI_B else 'B'])

    def platform(self,name,args):
        """Model only the public backend boundary and optional adversarial disarm side effects."""
        if name=='__assert_func':self.effects.append(['assert']);self.stop('uninitialized');return 0
        if name=='_esp_error_check_failed':self.effects.append(['error-check']);self.stop('backend-error');return 0
        assert args[0]==self.HANDLE
        if name=='esp_timer_stop':
            self.effects.append(['stop']);self.backend_alarm=0
            if not self.switched:
                self.switched=True
                if self.switch_adapter:self.word(self.osi_pointer,self.OSI_B)
                if self.mutate_config:
                    self.cfg_expected[52]=0
                    self.cfg_expected[72:74]=(1).to_bytes(2,'little')
                    self.cpu.mem_write(self.cfg,bytes(self.cfg_expected))
            return self.stop_result
        delay=args[1]|(args[2]<<32)
        self.effects.append(['once' if name=='esp_timer_start_once' else 'periodic',delay])
        if not self.start_result:self.backend_alarm=self.NOW+delay
        return self.start_result

    def call(self,enabled=1,period=1,adjustment=500000,fallback=60000000,cancel=False,
             switch_adapter=False,mutate_config=False,initialized=True,start_result=0,
             stop_result=0,backend=None,backend_delay=0,repeat=False):
        """Require real 64-bit API timeout, exact stack/ABI and immutable PM/config inputs."""
        self.effects=[];self.adapter_reads=[];self.events=[];self.stopped=None
        self.backend_alarm=self.NOW+17;self.switched=False
        self.switch_adapter,self.mutate_config=switch_adapter,mutate_config
        self.start_result,self.stop_result=start_result,stop_result
        pm=bytearray(b'\x5a'*584);cfg=bytearray(b'\xa5'*76)
        pm[496:500]=(0x12121212 if initialized else 0).to_bytes(4,'little')
        pm[508:512]=self.HANDLE.to_bytes(4,'little')
        cfg[52]=enabled;cfg[72:74]=period.to_bytes(2,'little')
        cfg[56:60]=adjustment.to_bytes(4,'little');cfg[28:32]=fallback.to_bytes(4,'little')
        self.cfg_expected=bytearray(cfg)
        self.cpu.mem_write(self.pm,bytes(pm));self.cpu.mem_write(self.cfg,bytes(cfg))
        self.cpu.mem_write(self.OSI_A,bytes(self.osi_bytes));self.cpu.mem_write(self.OSI_B,bytes(self.osi_bytes))
        self.word(self.osi_pointer,self.OSI_A)
        self.cpu.mem_write(STACK-4096,b'\xa5'*8192)
        for index,value in self.initial.items():self.reg(index,value)
        if backend:
            self.reg(10,self.pm+492);self.reg(11,backend_delay);self.reg(12,int(repeat))
            name='ets_timer_arm' if backend=='ms' else 'ets_timer_arm_us'
        else:name='small_tv_wifi_enable_keep_alive_timer'
        expected_stop='uninitialized' if not initialized else 'backend-error' if start_result else None
        self.run(name,expected_stop=expected_stop)
        if cancel and expected_stop is None:
            for index,value in self.initial.items():self.reg(index,value)
            self.run('pm_disable_keep_alive_timer')
        assert bytes(self.cpu.mem_read(self.pm,584))==pm
        assert bytes(self.cpu.mem_read(self.cfg,76))==self.cfg_expected
        assert bytes(self.cpu.mem_read(self.OSI_A,480))==self.osi_bytes
        assert bytes(self.cpu.mem_read(self.OSI_B,480))==self.osi_bytes
        assert self.word(self.osi_pointer)==(self.OSI_B if switch_adapter and self.switched else self.OSI_A)
        return dict(effects=self.effects,adapter_reads=self.adapter_reads,alarm=self.backend_alarm,
                    stopped=self.stopped,config_changed_by_platform=mutate_config and self.switched)
