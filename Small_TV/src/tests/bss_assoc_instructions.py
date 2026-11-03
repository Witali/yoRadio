"""Execute actual association prefixes and BSS getters/setters in private RV32 RAM."""
from unicorn import UC_MEM_WRITE,riscv_const as rv

from runtime_call_instructions import Fixture,STACK,END


class AssocProbe(Fixture):
    """Keep only ROM rate setup and logging as explicit external boundaries."""
    PEER,STATION,FRAME=0x20000,0x30000,0x40000
    INFO,PBUF=0x60000,0x61000
    INITIAL_PERIOD,INITIAL_OPTIONS=0xa55a,0xa4

    def __init__(self,variant,layout,reader):
        """Map complete matched bodies and individually checked state cells."""
        rows=[dict(row,code_sha256=row['linked_code_sha256']) for row in layout['functions']]
        self.layout=layout;self.rows_by_name={r['name']:r for r in rows}
        super().__init__(variant,dict(functions=rows,allocator_veneer=None),reader)
        for address,size in ((self.PEER,1024),(self.STATION,512),(self.FRAME,4096),(layout['menuconfig']+64,4),
            (self.INFO,48),(self.PBUF,8),(layout['osi_pointer'],4),(layout['osi_table']+412,4),(layout['hmac_counter']+14,1)):
            self.map(address,size)
        self.initial[3]=layout['gp']
        association=self.rows_by_name['sta_recv_assoc']
        for name in ('ieee80211_setup_rates','wifi_log'):
            values=[r['address'] for r in association['symbol_bindings'] if r['name']==name]
            assert len(values)==1
            self.boundary(name,values[0],lambda args,name=name:self.external(name,args))
        management=self.rows_by_name['sta_recv_mgmt']
        mac=[r['address'] for r in management['symbol_bindings'] if r['name']=='wifi_get_macaddr']
        assert len(mac)==1;self.boundary('wifi_get_macaddr',mac[0],lambda args:self.external('wifi_get_macaddr',args))
        self.inside_setter=False;self.trace={};self.literals={}

    def literal(self,address):
        """Read a bounded immutable firmware string, never packet or live host data."""
        if address not in self.literals:
            value=bytearray()
            for offset in range(256):
                byte=self.reader(address+offset,1)
                if byte==b'\0':break
                value.extend(byte)
            else:raise AssertionError('Unbounded firmware log literal')
            self.literals[address]=value.decode('ascii')
        return self.literals[address]

    def external(self,name,args):
        """Observe ordinary calls without pretending to execute the ROM rate algorithm."""
        if name=='ieee80211_setup_rates':
            assert args[0]==self.PEER and args[1]==self.FRAME+30 and args[2]==0
            self.trace['calls'].append(['rates',args[3]])
        elif name=='wifi_get_macaddr':
            assert args[0]==0 and self.reg(2)<=args[1]<args[1]+6<=STACK,(args[0],args[1],self.reg(2))
            self.cpu.mem_write(args[1],bytes.fromhex('020000000001'))
            self.trace['calls'].append(['mac',args[1]-self.reg(2)])
        else:
            assert args[:3] in ((1,1,3),(1,4,4))
            self.trace['calls'].append(['log',*args[:3]])
            if args[:3]==(1,1,3):
                # The release SDK places the format in NOLOAD rodata. Do not
                # invent readable bytes for that discarded diagnostic string.
                self.trace['bss_logs'].append(dict(period=args[4],option=self.literal(args[5])))
        return 0

    def step(self,cpu,pc,size,data):
        """Stop at the real post-BSS join; do not skip into a selected basic block."""
        if pc==self.layout['after_bss']:
            self.stop('bss-join');cpu.emu_stop();return
        if self.management and pc==self.layout['after_assoc']:
            self.stop('management-return');cpu.emu_stop();return
        if pc==self.layout['osi_412_target']:
            assert self.reg(10)==40;self.trace['calls'].append(['osi-412',40])
        if pc==int(self.rows_by_name['sta_recv_assoc']['start'],0):
            assert self.reg(10)==self.PEER and self.reg(11)==self.FRAME and self.reg(12)==self.end
            self.trace['association_ingress'].append([self.reg(13),self.reg(14)])
        if pc==int(self.rows_by_name['ieee80211_set_bss_max_idle_period']['start'],0):
            assert self.reg(10)==self.PEER
            self.ie=self.reg(11)
            if self.ie:
                assert self.FRAME<=self.ie<self.ie+2<=self.end
                self.ie_end=self.ie+2+bytes(cpu.mem_read(self.ie+1,1))[0]
                assert self.ie_end<=self.end
            self.inside_setter=bool(self.ie)
            self.trace['setter_ingress'].append(self.ie-self.FRAME if self.ie else None)
        return super().step(cpu,pc,size,data)

    def memory(self,cpu,access,address,size,value,data):
        """Reject reads outside either the packet or the selected IE, even inside a mapped page."""
        if STACK-4096<=address<address+size<=STACK+4096:return
        if self.FRAME<=address<address+size<=self.FRAME+4096:
            assert access!=UC_MEM_WRITE
            self.trace['packet_reads'].append([address-self.FRAME,size])
            packet_oob=address+size>self.end
            element_oob=self.inside_setter and not self.ie<=address<address+size<=self.ie_end
            if packet_oob or element_oob:
                self.trace['overreads'].append(dict(pc=hex(cpu.reg_read(rv.UC_RISCV_REG_PC)),
                    offset=address-self.FRAME,size=size,packet_oob=packet_oob,element_oob=element_oob))
                self.stop('input-overread');cpu.emu_stop()
            return
        cells={
            (self.PEER,4):'peer-station',(self.PEER+12,4):'peer-flags',
            (self.PEER+38,2):'peer-aid',(self.PEER+42,2):'peer-capability',
            (self.PEER+818,2):'peer-period',(self.PEER+820,1):'peer-options',
            (self.PEER+818,1):'peer-period-low',(self.PEER+819,1):'peer-period-high',
            (self.STATION+172,4):'station-time',(self.STATION+164,4):'station-flags',
            (self.STATION+300,4):'station-ht',(self.layout['menuconfig']+64,4):'feature-word',
            (self.STATION+152,4):'station-state',(self.STATION+228,4):'station-peer',
            (self.INFO+4,4):'packet-buffer',(self.PBUF+4,4):'packet-data',(self.INFO+22,2):'packet-body-size',
            (self.layout['osi_pointer'],4):'osi-pointer',(self.layout['osi_table']+412,4):'osi-release',
            (self.layout['hmac_counter']+14,1):'received-assoc-counter',
        }
        assert (address,size) in cells,('Undeclared association data access',hex(address),size)
        if access==UC_MEM_WRITE:
            if (address,size)==(self.layout['hmac_counter']+14,1):self.trace['counter_writes'].append(value)
            else:
                assert self.PEER<=address<address+size<=self.PEER+1024
                self.trace['writes'].append([address-self.PEER,size,value])
        else:self.trace['state_reads'].append(cells[address,size])

    def call(self,ies,feature_word=256,expected_stop='bss-join',management=False,subtype=16,state=3,truncate_body=None,setter_only=False):
        """Start at the real function entry with a complete fixed header and explicit IE bytes."""
        assert len(ies)<=2048
        peer=bytearray(1024);peer[:4]=self.STATION.to_bytes(4,'little')
        peer[818:820]=self.INITIAL_PERIOD.to_bytes(2,'little');peer[820]=self.INITIAL_OPTIONS
        station=bytearray(512);station[172:176]=(1).to_bytes(4,'little')
        station[152:156]=state.to_bytes(4,'little');station[228:232]=self.PEER.to_bytes(4,'little')
        header=bytearray(30);header[24:26]=(0x41).to_bytes(2,'little');header[28:30]=(0xc123).to_bytes(2,'little')
        header[0]=subtype;header[4:10]=bytes.fromhex('020000000001')
        # A valid mandatory rates element lets the real association parser reach
        # optional BSS handling. No other parser or getter is replaced by a stub.
        packet=bytes(header)+b'\x01\x01\x82'+ies
        if truncate_body is not None:
            assert 0<=truncate_body<=len(packet)-24;packet=packet[:24+truncate_body]
        self.end=self.FRAME+len(packet)
        self.cpu.mem_write(self.PEER,bytes(peer));self.cpu.mem_write(self.STATION,bytes(station))
        self.cpu.mem_write(self.FRAME,b'\x5a'*4096);self.cpu.mem_write(self.FRAME,packet)
        self.word(self.layout['menuconfig']+64,feature_word)
        self.word(self.layout['osi_pointer'],self.layout['osi_table'])
        self.word(self.layout['osi_table']+412,self.layout['osi_412_target'])
        self.cpu.mem_write(self.layout['hmac_counter']+14,b'\xfe')
        info=bytearray(48);info[4:8]=self.PBUF.to_bytes(4,'little');info[22:24]=(len(packet)-24).to_bytes(2,'little')
        pbuf=bytearray(8);pbuf[4:8]=self.FRAME.to_bytes(4,'little')
        self.cpu.mem_write(self.INFO,bytes(info));self.cpu.mem_write(self.PBUF,bytes(pbuf))
        self.cpu.mem_write(STACK-4096,b'\xa5'*8192)
        for index,value in self.initial.items():self.reg(index,value)
        arguments=((self.PEER,self.FRAME+33 if ies else 0) if setter_only else
                   (self.STATION,self.INFO,subtype,0,0) if management else (self.PEER,self.FRAME,self.end,subtype,0))
        for index,value in enumerate(arguments,10):self.reg(index,value)
        self.trace=dict(calls=[],bss_logs=[],setter_ingress=[],association_ingress=[],packet_reads=[],state_reads=[],writes=[],overreads=[],counter_writes=[])
        self.inside_setter=False;self.events=[];self.stopped=None;self.management=management
        self.run('ieee80211_set_bss_max_idle_period' if setter_only else
                 'sta_recv_mgmt' if management else 'sta_recv_assoc',expected_stop=expected_stop)
        assert bytes(self.cpu.mem_read(self.FRAME,len(packet)))==packet
        assert bytes(self.cpu.mem_read(self.STATION,512))==station
        assert bytes(self.cpu.mem_read(self.INFO,48))==info and bytes(self.cpu.mem_read(self.PBUF,8))==pbuf
        assert self.word(self.layout['osi_pointer'])==self.layout['osi_table']
        assert self.word(self.layout['osi_table']+412)==self.layout['osi_412_target']
        actual=bytes(self.cpu.mem_read(self.PEER,1024));expected=bytearray(peer)
        for offset,size,value in self.trace['writes']:expected[offset:offset+size]=value.to_bytes(size,'little')
        assert actual==expected
        self.trace.update(stop=self.stopped,return_value=self.reg(10) if self.reg(1)==END else None,
            packet_bytes=len(packet),period=int.from_bytes(actual[818:820],'little'),options=actual[820])
        return self.trace
