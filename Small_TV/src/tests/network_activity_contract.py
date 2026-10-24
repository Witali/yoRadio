"""Replay real scan/photo/theme requests and their nested AP event boundaries."""
import copy
import hashlib
import json


STEPS = [('scan','esp_wifi_scan_start',2),('start','photo_upload_start_detailed',3),
         ('chunk','photo_upload_chunk',1),('finish','photo_upload_finish_detailed',3),
         ('theme','settings_select_theme',2),('reselect','settings_select_theme',3)]
MACS = ('52:54:00:43:00:02','52:54:00:43:00:03')


def wanted(mask):
    """Derive peer identities from the external presence mask."""
    return {mac for i,mac in enumerate(MACS) if mask & (1 << i)}


def validate(report, wire, fixture, read_code, base):
    """Require actual pending requests, SDK transitions, returns and photo readback."""
    assert report['passed'] and report['owners_stopped'] and report['cycles']==2
    assert not any(report[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    assert report['wire']==wire
    events=report['events'];active={};nested=0
    entries={**report['entries'],**report['activity_entries']}
    for index,event in enumerate(events):
        assert entries[event['function']]==event['pc']
        assert hashlib.sha256(read_code(event['pc'],2)).hexdigest()==event['instruction_sha256']
        assert index<event['return_event_index']<=len(events)
    def replay(begin,end):
        for event in events[begin:end]:
            if 'kind' not in event:continue
            kind=event['kind'];assert kind in ('connected','disconnected')
            assert event['function']=='wifi_event' and event['base']==base
            assert event['event_id']==wire[kind+'_id']
            raw=bytes.fromhex(event['event_data_hex'])
            assert len(raw)==wire[kind+'_bytes']
            offset=wire[kind+'_mac'];mac=':'.join(f'{v:02x}' for v in raw[offset:offset+6])
            assert mac==event['mac'] and mac in MACS
            aid=raw[wire[kind+'_aid']];assert 1<=aid<=3
            if kind=='connected':
                assert mac not in active and aid not in active.values();active[mac]=aid
            else:
                assert active.pop(mac)==aid
                reason=wire['disconnected_reason']
                assert int.from_bytes(raw[reason:reason+wire['reason_bytes']],'little')==3
    operations=report['operations'];assert len(operations)==2*len(STEPS)
    cursor=operations[0]['event_range'][0];replay(0,cursor);assert set(active)==wanted(3)
    mask=3
    for number,operation in enumerate(operations):
        action,function,new_mask=STEPS[number%len(STEPS)]
        assert operation['cycle']==number//len(STEPS)
        assert operation['action']==action and operation['function']==function
        assert operation['fired'] and operation['http_pending_at_entry']
        assert operation['mask']==new_mask and operation['mask_before']==mask
        assert set(operation['active_before'])==set(active)==wanted(mask)
        begin,end=operation['event_range'];assert begin==cursor<end<=len(events)
        target_index=operation['event_index'];assert begin<=target_index<end
        target=events[target_index]
        assert target['function']==function and target['pc']==operation['entry_pc']
        assert target['return_value']==0 and target['return_event_index']<=end
        peers=[(i,event) for i,event in enumerate(events[begin:end],begin) if 'kind' in event]
        assert len(peers)==1 and peers[0][0]>target_index
        nested+=peers[0][0]<target['return_event_index']
        replay(begin,end);assert set(active)==wanted(new_mask)==set(operation['active_after'])
        arguments=operation['arguments']
        if action=='scan':assert arguments[1]==1
        elif action=='start':assert arguments[:3]==[4,len(fixture),1]
        elif action=='chunk':assert arguments[:3]==[4,0,1] and arguments[4]==len(fixture)
        elif action=='finish':assert arguments[0]==4
        else:assert arguments[0]==1
        assert operation['http']['status']==200
        body=bytes.fromhex(operation['http']['body_hex'])
        if action=='scan':
            networks=json.loads(body)
            assert {r['ssid'] for r in networks}=={'yoRadio-QEMU','QEMU-2','QEMU-3'}
            assert all(-127<=r['rssi']<0 for r in networks)
        else:assert body==b'OK'
        ready={r['mac']:r for r in operation['ready_clients']}
        for mac in active:
            assert ready[mac]['online'] and ready[mac]['model_state']==5
            assert ready[mac]['offered_ipv4']!='0.0.0.0'
        cursor=end;mask=new_mask
    assert cursor==len(events)
    starts=[e for e in events if e['function']=='httpd_start']
    assert len(starts)==1 and starts[0]['return_value']==0
    assert report['server_handles']==[starts[0]['server_handle']] and starts[0]['server_handle']
    assert not any(e['function']=='httpd_stop' for e in events)
    assert [r['cycle'] for r in report['readbacks']]==[0,1]
    for row in report['readbacks']:
        assert row['theme_status']==row['photo_status']==200
        assert bytes.fromhex(row['theme_hex'])==b'1'
        assert bytes.fromhex(row['photo_hex'])==fixture
    return dict(passed=True,cycles=2,activity_requests=len(operations),
        sdk_peer_events=sum('kind' in e for e in events),nested_peer_callbacks=nested,
        readbacks=2,http_server_starts=1,http_server_stops=0,network_lifecycle_complete=False)


def rejection_checks(report, wire, fixture, read_code, base):
    """Reject a completed request, fabricated peer, lost response or altered image."""
    rejected=[]
    for case in ('completed-request','peer-bytes','return-boundary','missing-network',
                 'altered-photo','duplicate-server','not-reaped','finish-error'):
        wrong=copy.deepcopy(report)
        if case=='completed-request':wrong['operations'][0]['http_pending_at_entry']=False
        elif case=='peer-bytes':
            next(e for e in wrong['events'] if e.get('kind')=='disconnected')['event_data_hex']='00'*10
        elif case=='return-boundary':wrong['events'][wrong['operations'][0]['event_index']]['return_event_index']=len(wrong['events'])+1
        elif case=='missing-network':
            row=wrong['operations'][0];data=json.loads(bytes.fromhex(row['http']['body_hex']))
            row['http']['body_hex']=json.dumps(data[:1]).encode().hex()
        elif case=='altered-photo':wrong['readbacks'][0]['photo_hex']='00'
        elif case=='duplicate-server':wrong['server_handles']*=2
        elif case=='not-reaped':wrong['owners_stopped']=False
        else:wrong['operations'][3]['http']['status']=400
        try:validate(wrong,wire,fixture,read_code,base)
        except (AssertionError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid network activity evidence accepted: '+case)
    return rejected
