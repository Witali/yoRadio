"""Independent effects model for full null completion, quick-wake and state setting."""
from dataclasses import dataclass

from keep_alive_model import KeepState, MASK64

MASK32=(1<<32)-1


@dataclass(frozen=True)
class NullState(KeepState):
    """Keep unproven protocol fields named by offset rather than guessing meanings."""
    byte10:int=0
    byte19:int=0
    byte20:int=0
    byte27:int=0
    byte456:int=0
    byte468:int=0
    byte543:int=0
    deadline568:int=0
    counter28:int=0
    counter32:int=0


def expected(variant,state,now,argument0=0,argument1=0,argument2=0,check=1,
             idle=1,coex=1,slice_allowed=1,station=2,peerflag=0,
             function='pm_tx_null_data_done_process'):
    """Model every ordered PM/counter store, platform call and guarded station read."""
    fields={offset:getattr(state,'byte'+str(offset)) for offset in
            (1,9,10,14,15,16,19,20,21,22,26,27,456,468,488,543)}
    calls,writes,counters,reads=[],[],[],[]
    clocks=0
    def put(offset,value):
        """Update private model state before later helpers consume it."""
        fields[offset]=value&255;writes.append([offset,1,value&255])
    def clock():
        """Return the complete controlled 64-bit clock pair."""
        nonlocal clocks
        value=(now+17*clocks)&MASK64;clocks+=1;calls.append(['clock',value]);return value
    def stamp(offset,value):
        """Preserve the two distinct RV32 timestamp stores."""
        writes.extend([[offset,4,value&MASK32],[offset+4,4,value>>32]])
    def rearm():
        """Model the real qualified old/new rearm bodies with their own gating."""
        if variant=='factory':
            if state.enabled52 and not state.word36:
                calls.extend([['disarm'],['arm224',state.period72<<9,0]])
        else:
            delay=(((state.period72<<10)*1000-state.adjustment56)&MASK32
                   if state.enabled52 else state.fallback28)
            if state.enabled52 or delay:calls.extend([['disarm'],['arm240',delay,0]])
    def reset():
        """Execute the old reset model rather than assuming completion always resets."""
        if fields[14]:
            stamp(88,clock())
            if not state.word36:
                calls.append(['osi400'])
                if not coex:calls.append(['active'])
    def quick(completed):
        """Describe the actual quick-wake helper, including its retry side effects."""
        if not fields[468]:return 1
        if completed:calls.append(['beacon-reset'])
        if fields[19]:
            result=fields[19];put(19,0)
            calls.extend([['osi412',0],['clear-rx-pti']]);return result
        if fields[20]:return 1
        calls.append(['tx-idle',1])
        if idle:return 1
        if not fields[22]:calls.append(['null',1])
        return 0
    def set_state(value):
        """Describe both full state setters, including debug-GPIO boundary arguments."""
        if fields[1]!=value:
            calls.extend([['gpio',(5-fields[1])&MASK32,1],['gpio',(5-value)&MASK32,0]])
        put(1,value)
    def finish():
        """Return a single canonical observation schema for both SDK variants."""
        return dict(calls=calls,writes=writes,counter_writes=counters,station_reads=reads)
    if function=='pm_tx_null_data_done_quick_wake_process':
        result=quick(argument0);out=finish();out['return_value']=result;return out
    if function=='pm_set_state':
        set_state(argument0);return finish()
    assert function=='pm_tx_null_data_done_process'
    completed=int(argument1==1)
    if variant=='factory' and completed:reset()
    if variant=='factory':
        ready=completed
        if not fields[15]:ready=1
        elif fields[16]:ready=fields[16]
        elif not argument0 and fields[9]>15:ready=fields[15]
    else:
        ready=1 if not fields[15] or fields[16] else completed
        if (not fields[15] or fields[16]) and fields[488]:ready=completed
        if not argument0 and fields[9]>15:ready=1
    calls.append(['check'])
    if not check and not fields[14]:calls.append(['offchan-ready',0]);return finish()
    if not fields[21] and not fields[22]:return finish()
    if ready:
        if fields[1]==2:calls.append(['dream'])
        if variant=='factory':
            if state.enabled52 and fields[488]:
                if state.word36:stamp(480,clock())
                else:rearm()
                put(488,0)
        elif fields[488]:
            reads.append('station-pointer')
            if station==0:calls.append(['log',1,8,4]);return finish()
            reads.append('peer-pointer')
            if station==2:
                reads.append('peer-byte820')
                if not peerflag or argument2:
                    rearm();stamp(480,clock());put(488,0);calls.append(['log',6,4096,4])
        if not argument0:
            put(9,0)
            if fields[21]:
                if fields[456]:put(456,0)
                put(21,0)
                if fields[26]:
                    if quick(completed):
                        put(20,0);set_state(0);calls.append(['active'])
                        counters.append([32,4,(state.counter32+1)&MASK32]);calls.append(['waiting-queue'])
                else:put(27,1)
        else:
            put(10,0)
            if fields[22]:
                put(22,0)
                sleep_now=False
                if fields[468]:
                    calls.append(['osi400'])
                    sleep_now=not coex or not fields[27]
                if not sleep_now:
                    sleep_now=variant=='native' and fields[543] and clock()>=state.deadline568
                calls.append(['sleep'] if sleep_now else ['sleep-delay'])
                counters.append([28,4,(state.counter28+1)&MASK32])
            calls.append(['offchan-ready',0])
    elif not argument0:
        if fields[21]:
            put(21,0);current=clock()
            calls.append(['slice',current&MASK32,current>>32,5000])
            if slice_allowed:put(9,fields[9]+1);calls.append(['null',0])
            else:put(9,0);put(27,1)
    elif argument0==1 and fields[22]:
        put(22,0)
        if fields[26]:put(10,fields[10]+1);calls.append(['null',1])
        else:
            put(10,0);put(27,1);calls.extend([['sleep-delay'],['offchan-ready',1]])
    return finish()
