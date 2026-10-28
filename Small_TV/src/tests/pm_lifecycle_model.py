"""Independent models of direct start/stop instructions and selected cancellation bodies."""
MASK64=(1<<64)-1


def expected(variant, name, initial_pm, initial_cfg, args, env):
    """Keep opaque platform calls explicit and model every direct state store in order."""
    pm,cfg=bytearray(initial_pm),bytearray(initial_cfg)
    calls,writes,config,globals_=[],[],[],[]
    clocks,coex_index=0,0
    def word(offset):
        """Read a current RV32 PM word after earlier model stores."""
        return int.from_bytes(pm[offset:offset+4],'little')
    def write(offset,size,value):
        """Apply RV32 truncation while recording the exact store width."""
        value &= (1<<(size*8))-1;pm[offset:offset+size]=value.to_bytes(size,'little')
        writes.append([offset,size,value])
    def clock():
        """Supply the same controlled clock sequence as the external fixture."""
        nonlocal clocks
        value=(env['now']+17*clocks)&MASK64;clocks+=1;calls.append(['clock',value]);return value
    def stamp(offset,value):
        """Represent a 64-bit value as the two real RV32 stores."""
        write(offset,4,value);write(offset+4,4,value>>32)
    def coex():
        """Return distinct successive coexistence observations, without modelling RF."""
        nonlocal coex_index
        value=env['coex'][coex_index];coex_index+=1;calls.append(['coex',value]);return value
    if name=='pm_start' and not pm[14]:
        # JALR uses a5 for the callback address, after the original argument was
        # saved in s4. Record incoming registers, not an assumed callback type.
        if env['beacon48']:calls.append(['beacon48',*args[:5],env['beacon_target'],args[6]])
        calls.append(['log-start',word(36)])
        write(15,1,1);write(16,1,0);write(28,2,args[1]);write(448,1,0);write(2,1,args[0])
        calls.append(['memcpy',3,env['mac'].hex(),6]);pm[3:9]=env['mac']
        write(152,4,0);write(156,4,0)
        for offset,size in ((21,1),(22,1),(488,1),(9,1),(10,1),(72,4),(76,4)):write(offset,size,0)
        for offset in (144,128,136,88):stamp(offset,clock())
        write(52,4,(args[3]<<10) if args[3] else 0x19000)
        if coex():calls.append(['osi436',word(52)//100])
        write(11,1,1);calls.append(['scale-listen']);write(26,2,1);write(288,1,0)
        write(13,1,coex());write(456,1,0);write(104,4,args[5]);write(108,4,args[6]);write(18,1,1)
        calls.append(['tsf-wake',1])
        for offset in ((100,96) if variant=='factory' else (96,100)):write(offset,4,0)
        write(464,4,0);write(540,1,0);calls.append(['debug-reset'])
        calls.append(['next-tbtt',args[4],args[5],args[6],0])
        if variant=='factory':calls.extend([['osi424',0],['rx-pti',env['pti']]])
        else:calls.append(['coex-beacon',1])
        interval=int.from_bytes(cfg[24:28],'little')
        calls.extend([['rx-time',word(60),interval],['log-beacon',env['pti'],word(60),env['pti'],interval],
                      ['beacon-monitor'],['active'],['coex-status',4]])
        write(457,1,1)
        if pm[289]:write(289,1,1)
        calls.extend([['gpio',3,1],['gpio',4,1],['gpio',5,0]])
        write(14,1,1)
        if variant=='factory':
            globals_.extend([[-8,0],[-4,0]]);write(542,1,0)
        else:
            write(542,1,0);write(576,1,0);globals_.extend([[-8,0],[-4,0]])
        calls.append(['connectionless'])
    elif name=='pm_stop' and pm[14]:
        calls.append(['unblock'])
        # The real ROM sleep-delay body and SDK active cancellation run in the CPU.
        write(440,1,0);calls.extend([['disarm',260],['disarm',200],['disable-tbtt'],['tsf-wake',0],['tsf-clear']])
        if cfg[2]:calls.append(['disable-filter'])
        calls.append(['rx-pti',0] if variant=='factory' else ['coex-beacon',0])
        calls.append(['disarm',180]);write(28,2,0)
        if pm[1]:calls.extend([['dream'],['set-state',0],['waiting-queue']])
        elapsed=(clock()-int.from_bytes(pm[144:152],'little'))&MASK64
        calls.append(['log-stop',word(152),word(156),elapsed&0xffffffff,elapsed>>32])
        if pm[16]:calls.append(['wake-done'])
        for offset,size,value in ((11,1,1),(26,2,1),(388,4,0x30000),(16,2,0),(14,1,0),
                                  (360,1,0),(385,1,0),(449,1,0),(456,1,0)):write(offset,size,value)
        calls.extend([['coex-power'],['coex-status',0]])
        if coex():calls.append(['coex-restart'])
        if env['beacon52']:calls.append(['beacon52'])
        if pm[289]:
            write(289,1,2)
            if not word(292):calls.append(['disconnected-delay'])
        calls.append(['connectionless']);cfg[52]=0;config.append([52,1,0])
        if variant=='factory':calls.append(['disarm',492]);write(449,1,0)
    elif name not in ('pm_start','pm_stop'):raise ValueError('Unknown lifecycle entry')
    return dict(trace=dict(calls=calls,writes=writes,cfg_writes=config,global_writes=globals_),pm=bytes(pm),cfg=bytes(cfg))
