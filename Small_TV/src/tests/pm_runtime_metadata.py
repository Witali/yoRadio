"""Read only qualified numeric PM/legacy-timer/backend metadata from a stopped guest."""
RAM=((0x3fca0000,0x3fce0000),(0x4037c000,0x403c0000))


def decode(read,layout):
    """Follow only a validated legacy handle and never read timer payload or stack data."""
    requests,total=0,0
    def take(address,size):
        """Bound every typed read and reject truncated responses before interpreting them."""
        nonlocal requests,total
        requests+=1;total+=size
        if size not in (1,4,8) or requests>32 or total>256:raise ValueError('PM metadata budget exceeded')
        raw=read(address,size)
        if len(raw)!=size:raise ValueError('Short PM metadata read')
        return raw
    pm,cfg=layout['pm'],layout['config']
    word=lambda address:int.from_bytes(take(address,4),'little')
    state=take(layout['connected'],1)[0]
    if state>layout['connected_max']:raise ValueError('Invalid observed station state')
    result=dict(guest_counter_us=word(0x6004d000),rom_pm_pointer=word(layout['rom_pm_pointer']),
                osi_pointer=word(layout['osi_pointer']),application_connected_hint=state==layout['connected_value'],
                station_state=state,pm_active=take(pm+14,1)[0],pm_pending=take(pm+488,1)[0],
                pm_word36=word(pm+36),config_enabled=take(cfg+52,1)[0],fallback_us=word(cfg+28),
                last_tx_us=int.from_bytes(take(pm+480,8),'little'))
    timer=pm+layout['legacy_timer_offset']
    marker=word(timer+layout['marker_offset']);handle=word(timer+layout['handle_offset'])
    result['legacy_marker'],result['backend_handle']=marker,handle
    result['timer_owner_bound']=result['rom_pm_pointer']==pm
    result['backend_alarm_us']=None;result['timer_armed']=None
    if marker==0x12121212 and handle and result['timer_owner_bound']:
        if handle&3 or not any(lo<=handle<handle+layout['backend_min_bytes']<=hi for lo,hi in RAM):
            raise ValueError('Timer backend handle is outside aligned C2 SRAM')
        alarm=int.from_bytes(take(handle+layout['alarm_offset'],layout['alarm_bytes']),'little')
        result['backend_alarm_us']=alarm;result['timer_armed']=bool(alarm)
    return result
