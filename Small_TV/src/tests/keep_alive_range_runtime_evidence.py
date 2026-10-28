"""Validate typed timer, independent network and exact panel observations offline."""
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.pm_runtime_layout import native_types
from reverse.rv32_link_match import branch_target, link_register
from verify_wifi_keep_alive import complete


def call_returns(linked, caller, callee):
    """Derive return PCs from actual matched call instructions, not saved addresses."""
    target=linked.symbol(callee)['st_value'];found=set()
    for row in caller['transformations']:
        code=bytes.fromhex(row['linked_bytes']);pc=int(row['pc'],0)
        if row['kind'].startswith('call') and link_register(code)==1 and branch_target(code,pc)==target:
            found.add(pc+len(code))
    assert found,('No qualified call',caller['name'],callee)
    return found


def timer(report, linked, qualified, libraries):
    """Reconstruct every sampled timer field from bounded raw reads and actual DWARF."""
    assert report['passed'] and report['inputs_unchanged']
    for key in ('display_tested','physical_hardware_tested','whole_image_completeness_proved'):
        assert report[key] is False
    assert report['qualification']==qualified
    abi=native_types(linked.elf);assert report['native_dwarf']==abi
    objects=dict(members((libraries/'libnet80211.a').read_bytes()))
    leave=complete(linked,objects['wl_cnx.o'],'cnx_sta_leave',{})
    getter=complete(linked,objects['ieee80211_sta.o'],'sta_is_bss_max_idle_enabled',{})
    assert report['leave']==leave and report['getter']==getter
    ms=next(r for r in qualified['backends'] if r['name']=='ets_timer_arm')
    arm_returns=call_returns(linked,ms,'esp_timer_start_once')
    cancel_returns=call_returns(linked,leave,'pm_disable_keep_alive_timer')
    pm,cfg=qualified['g_pm'],qualified['g_pm_cfg']
    menuconfig=linked.symbol('g_wifi_menuconfig')['st_value']
    rows=report['observations']
    assert [r['phase'] for r in rows]==['long-arm-return','connected-long-timer','cancel-entry','cancel-return']
    expected_delay=65535*1024000-2000000
    assert report['api_delay_us']==expected_delay and expected_delay>0xffffffff
    for index,row in enumerate(rows):
        fields={
            'marker':(pm+492+abi['_ETSTIMER_']['fields']['timer_expire']['offset'],4),
            'handle':(pm+492+abi['_ETSTIMER_']['fields']['timer_arg']['offset'],4),
            'alarm':(row['handle']+abi['esp_timer']['fields']['alarm']['offset'],8),
            'pm_active':(pm+14,1),'bss_enabled':(cfg+52,1),'period':(cfg+72,2),
            'adjustment':(cfg+56,4),'menuconfig_word':(menuconfig+64,4)}
        assert 0x3fca0000<=row['handle']<row['handle']+abi['esp_timer']['size']<=0x3fce0000
        assert row['handle']%4==0 and len(row['raw_reads'])==len(fields)
        raw={}
        for cell in row['raw_reads']:
            key=cell['address'],cell['size'];assert key not in raw
            value=bytes.fromhex(cell['hex']);assert len(value)==cell['size']
            raw[key]=int.from_bytes(value,'little')
        assert set(raw)==set(fields.values())
        for name,address in fields.items():assert row[name]==raw[address],('Derived field changed',name)
        assert row['marker']==0x12121212 and row['handle']==report['api_handle']
        assert row['period']==65535 and row['adjustment']==2000000
        assert row['bss_enabled']==row['pm_active']==(1 if index<2 else 0)
        assert not row['menuconfig_word']&256
        if index<3:assert row['alarm']>expected_delay
        else:assert row['alarm']==0
    assert rows[0]['pc'] in arm_returns
    assert rows[2]['pc']==int(qualified['disable']['start'],0)
    assert rows[3]['pc'] in cancel_returns
    assert rows[1]['alarm']==rows[2]['alarm']
    assert report['observed_feature_enabled'] is False
    calls=report['timer_api_calls'];assert 1<=len(calls)<=64
    matching=[r for r in calls if r['handle']==r['expected_handle']==report['api_handle'] and r['delay_us']==expected_delay]
    assert len(matching)==1 and matching[0]['return_pc'] in arm_returns
    config=bytes.fromhex(matching[0]['config_hex'])
    assert len(config)==24 and config[0]==1 and int.from_bytes(config[4:8],'little')==2000000
    assert int.from_bytes(config[20:22],'little')==65535
    assert report['long_timer_cancelled_by_station_leave'] is True
    assert report['exit_code']==0 and report['owned_stop_completed'] and report['uart_clean']
    assert len(report['fixture_writes'])==1
    fixture=report['fixture_writes'][0];peer=fixture['address']-818
    assert peer%4==0 and 0x3fca0000<=peer<peer+824<=0x3fce0000
    assert fixture['size']==2 and fixture['after_hex']=='ffff'
    assert len(bytes.fromhex(fixture['before_hex']))==2
    return dict(delay_us=expected_delay,raw_reads=sum(len(r['raw_reads']) for r in rows),
                cancelled=True,runtime_feature_enabled=False,synthetic_fixture_bytes=2)


def network(report):
    """Recompute SNTP from sampled clock values and require fresh per-boot responses."""
    assert report['passed'] and report['inputs_unchanged'] and report['display_tested'] is False
    assert report['physical_hardware_tested'] is False and report['full_vm_oom_injection'] is False
    assert len(report['sessions'])==2 and all(r['exit_code']==0 for r in report['sessions'])
    phases=report['phases']
    assert [r['name'] for r in phases]==['configure-reboot','persistent-cold-boot','reset']
    for index,row in enumerate(phases):
        assert row['http_status']==200 and row['clocktype']==2
        assert row['rom_boots']==(1 if index==1 else 2)
        net=row['network'];state,ntp=net['state'],net['ntp']
        session=report['sessions'][0 if index==0 else 1]['session']
        expected=next(r['guest_address'] for r in session['web_endpoints'] if r['name']=='station')
        assert net['passed'] and net['expected_station_address']==state['station_address']==expected
        assert state['connected'] and state['time_synced'] and not state['ap_active']
        previous=phases[1]['network']['ntp']['response_count'] if index==2 else 0
        assert ntp['response_count']>previous
        since=ntp['systimer_ticks']*5//52+ntp['rtc_hrt_offset_us']+ntp['system_correction_us']
        actual=(ntp['boot_time_us']+since)/1e6
        predicted=ntp['server_epoch']+(ntp['virtual_us']-ntp['sent_virtual_us'])/1e6
        assert since==ntp['since_boot_us']
        assert abs(actual-ntp['actual_utc_seconds'])<1e-6
        assert abs(predicted-ntp['expected_utc_seconds'])<1e-6
        assert abs((actual-predicted)-ntp['difference_seconds'])<1e-6 and abs(actual-predicted)<1
    return dict(phases=len(phases),display_tested=False)


def display(report, frames):
    """Compare all RGB bytes to the factory reference without consulting network state."""
    assert report['passed'] and report['inputs_unchanged'] and report['network']['executed'] is False
    assert report['all_functionality_verified'] is False and report['requested_cycles_per_variant']==1
    assert len(report['cycles'])==2 and {r['variant'] for r in report['cycles']}=={'original','reconstructed'}
    expected=frames['reference'].split(b'\n',3)[-1]
    assert len(expected)==240*240*3 and sha(expected)==report['expected_rgb_sha256']
    for row in report['cycles']:
        assert row['passed'] and row['boot']['passed'] and row['boot']['rom_boots']==1
        assert row['boot']['bootloader_entry'] and row['boot']['no_panic'] and row['network']['executed'] is False
        assert row['source_integrity']==dict(passed=True,direct_raw_backing=True,protected_flash_unchanged=True)
        raw=frames[row['variant']];header,bounds,depth,pixels=raw.split(b'\n',3)
        assert (header,bounds,depth)==(b'P6',b'240 240',b'255') and pixels==expected
        screen=row['display'];assert screen['passed'] and screen['differing_rgb_bytes']==0
        assert screen['rgb_sha256']==sha(pixels)==report['expected_rgb_sha256']
        assert screen['file_sha256']==sha(raw)
    return dict(frames=2,pixels_per_frame=240*240,network_tested=False)


def owners(report, net, screen, long_timer):
    """Require absence records for the exact five test-owned process identities."""
    expected=[r['owner'] for r in net['sessions']]+[r['session'] for r in screen['cycles']]+[long_timer['owner']]
    assert report['all_absent'] is True and len(report['owners'])==len(expected)==5
    assert {(r['pid'],r['name']) for r in expected}=={(r['pid'],r['name']) for r in report['owners']}
    for row in report['owners']:
        assert row['matching_owner_present'] is False
        source=next(r for r in expected if r['pid']==row['pid'] and r['name']==row['name'])
        assert {k:v for k,v in row.items() if k!='matching_owner_present'}==source
