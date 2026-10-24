"""Replay shared-AP bridge liveness with one DHCP acquisition deliberately stalled."""
import copy
import hashlib


def validate(report,read_code,before_failure=False):
    """Require the failing before state, healthy-peer service and later real recovery."""
    assert report['owners_stopped']
    assert report['passed'] is (not before_failure)
    assert report['expected_http_failure'] is False
    assert not any(report[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    peer=report['peer'];assert peer in (0,1)
    if before_failure:assert peer==0 and report['error'].startswith('AssertionError:')
    events=report['events'];wire=report['wire'];observed=set()
    base=int.from_bytes(read_code(report['event_base_object'],4),'little')
    for event in events:
        assert report['entries'][event['function']]==event['pc']
        assert hashlib.sha256(read_code(event['pc'],2)).hexdigest()==event['instruction_sha256']
        if 'kind' not in event:continue
        assert event['function']=='wifi_event' and event['kind']=='connected'
        assert event['base']==base and event['event_id']==wire['connected_id']
        raw=bytes.fromhex(event['event_data_hex']);assert len(raw)==wire['connected_bytes']
        offset=wire['connected_mac'];mac=':'.join(f'{v:02x}' for v in raw[offset:offset+6])
        assert mac==event['mac'] and mac not in observed;observed.add(mac)
    assert observed=={'52:54:00:43:00:02','52:54:00:43:00:03'}
    starts=[e for e in events if e['function']=='httpd_start']
    assert len(starts)==1 and starts[0]['return_value']==0 and starts[0]['server_handle']
    assert report['server_handles']==[starts[0]['server_handle']]
    assert not any(e['function']=='httpd_stop' for e in events)
    samples=report['samples'];assert samples
    previous=-1;last_count=0;first_drop=None;phase='hold';hold=[]
    for row in samples:
        assert row['guest_seconds']>=previous;previous=row['guest_seconds']
        assert row['phase'] in ('hold','recovery')
        if phase=='recovery':assert row['phase']=='recovery'
        phase=row['phase']
        assert len(row['clients'])==len(row['faults'])==3
        for index,(client,fault) in enumerate(zip(row['clients'],row['faults'])):
            assert client['index']==fault['index']==index
            assert client['online'] is (index<2)
            assert client['mac']==f'52:54:00:43:00:{index+2:02x}'
            assert len(fault['dropped'])==len(fault['last_drop_us'])==7
            for stage,count in enumerate(fault['dropped']):
                if index!=peer or stage!=3:assert count==0
        target=row['clients'][peer];healthy=row['clients'][1-peer]
        count=row['faults'][peer]['dropped'][3]
        assert type(count) is int and last_count<=count<=last_count+1;last_count=count
        if count and first_drop is None:first_drop=row['faults'][peer]['last_drop_us'][3]/1e6
        assert row['pending_mask'] in (0,1<<(peer*7+3))
        if phase=='hold':
            assert target['model_state'] in (6,8)
            assert target['offered_ipv4']=='0.0.0.0';hold.append(row)
    assert report['held_until']==hold[-1] and first_drop is not None
    held=report['held_until'];assert held['guest_seconds']-first_drop>=10
    assert held['faults'][peer]['dropped'][3]>=2
    assert held['clients'][peer]['model_state']==6
    assert held['clients'][1-peer]['model_state']==5
    assert held['clients'][1-peer]['offered_ipv4']!='0.0.0.0'
    assert report['http_done_while_held'] is (not before_failure)
    if before_failure:assert 'http_while_held' not in report
    else:assert report['http_while_held']==dict(status=200,body_hex=b'0'.hex())
    recovered=report['recovered'];assert recovered==samples[-1] and recovered['phase']=='recovery'
    assert recovered['pending_mask']==0
    clients=recovered['clients']
    assert all(c['model_state']==5 and c['offered_ipv4']!='0.0.0.0' for c in clients[:2])
    assert clients[0]['offered_ipv4']!=clients[1]['offered_ipv4']
    assert clients[peer]['dhcp_retries']==recovered['faults'][peer]['dropped'][3]
    assert clients[1-peer]['dhcp_retries']==0
    assert len({c['xid'] for c in clients[:2]})==2
    for name in ('pending_http_final','http_after_recovery'):
        assert report[name]==dict(status=200,body_hex=b'0'.hex())
    return dict(passed=True,peer=peer,before_failure=before_failure,
        http_during_stall=not before_failure,completed_after_release=True,owners_stopped=True)


def rejection_checks(report,read_code,before_failure=False):
    """Reject missing repeated loss, a ready target or a fabricated healthy response."""
    rejected=[]
    for case in ('peer-bytes','no-repeated-loss','target-not-stalled','healthy-not-ready',
                 'false-http-state','late-recovery-failed','not-reaped'):
        wrong=copy.deepcopy(report)
        if case=='peer-bytes':next(e for e in wrong['events'] if 'kind' in e)['event_data_hex']='00'*8
        elif case=='no-repeated-loss':
            for row in wrong['samples']:
                if row['phase']=='hold':row['faults'][wrong['peer']]['dropped'][3]=min(1,row['faults'][wrong['peer']]['dropped'][3])
            wrong['held_until']=copy.deepcopy([r for r in wrong['samples'] if r['phase']=='hold'][-1])
        elif case in ('target-not-stalled','healthy-not-ready'):
            row=[r for r in wrong['samples'] if r['phase']=='hold'][-1]
            index=wrong['peer'] if case=='target-not-stalled' else 1-wrong['peer']
            row['clients'][index]['model_state']=5 if case=='target-not-stalled' else 6
            wrong['held_until']=copy.deepcopy(row)
        elif case=='false-http-state':wrong['http_done_while_held']=not wrong['http_done_while_held']
        elif case=='late-recovery-failed':wrong['http_after_recovery']['status']=500
        else:wrong['owners_stopped']=False
        try:validate(wrong,read_code,before_failure)
        except (AssertionError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid bridge liveness evidence accepted: '+case)
    return rejected
