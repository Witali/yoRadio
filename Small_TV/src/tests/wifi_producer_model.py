"""Independent adapter/IE expectations, using already checked PM effect models."""
from timer_event11_model import configured
from tx_null_model import expected as null_expected

MASK32=(1<<32)-1


def callback_expected(variant,state,now,sleep,status,flags,**kwargs):
    """Model the actual descriptor fields and forward them to the full parent model."""
    third=flags&1 if variant=='native' else 0x12345678
    result=null_expected(variant,state,now,argument0=int(sleep),argument1=status,argument2=third,**kwargs)
    result['parent_ingress']=[[int(sleep),status,third]]
    result['producer_reads']=['packet-descriptor']
    if variant=='native':result['producer_reads'].append('descriptor-flags')
    result['producer_reads'].append('descriptor-status')
    return result


def bss_expected(variant,state,period,options,present=True,connect=True,feature_word=None):
    """Model peer stores retained through the connection-to-PM producer path."""
    result=dict(calls=[],writes=[],cfg_writes=[],peer_writes=[])
    if feature_word is not None:
        result['feature_return']=(feature_word>>8)&1;return result
    if present:
        result['peer_writes']=[[818,2,period],[820,1,options&1]]
        result['calls']=[['bss-log',1,1,3]]
    if connect:
        actual=period if present else 54321
        result['calls'].append(['pm-start',0,0x123,0xd0004,100,0x10203040,0x01020304,0x05060708])
        final,changes=configured(variant,state,actual)
        result['cfg_writes']=changes['cfg_writes'];result['calls'].extend(changes['calls'])
        if variant=='native':
            delay=(((final.period72<<10)*1000-final.adjustment56)&MASK32
                   if final.enabled52 else final.fallback28)
            if final.enabled52 or delay:result['calls'].extend([['disarm'],['arm240',delay,0]])
    return result


def period_domain():
    """Inventory mathematical timer-range failures; do not call this CPU execution."""
    native=[];factory_zero=[]
    for period in range(1,65536):
        expected=period*1024*1000-(500000 if period<=3 else 2000000)
        if expected>MASK32:native.append(period)
        encoded=period if period<=4 else max(period,2*(period-4))&65535
        if not encoded:factory_zero.append(period)
    return dict(periods_inventoried=65535,native_wrapped_periods=len(native),
        native_first_wrapped_period=native[0],factory_zero_encoded_periods=factory_zero,
        native_first_expected_microseconds=4197*1024*1000-2000000,
        native_first_actual_microseconds=(4197*1024*1000-2000000)&MASK32,
        exhaustive_cpu_execution=False,production_runtime_enablement_proved=False)
