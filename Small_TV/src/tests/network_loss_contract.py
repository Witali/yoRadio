"""Replay exact packet-loss counters, real SDK peers and DHCP before/after results."""
import copy
import hashlib


STAGES=('probe','authentication','association','discover','request','offer','ack')


def validate(report,read_code):
    """Separate expected before failures from actual protocol recovery acceptance."""
    assert report['passed'] and report['owners_stopped'] and report['invalid_mask_rejected']
    assert not any(report[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    stages=list(range(7)) if report['stage']=='all' else [STAGES.index(report['stage'])]
    peer=report['peer'];assert peer in (0,1)
    assert report['drop_bit']==sum(1<<(peer*7+stage) for stage in stages)
    before=report['before_control'];assert not before or len(stages)==1 and stages[0]>=3
    assert report['recovery_acceptance'] is (not before)
    events=report['events'];wire=report['wire'];macs=set()
    base=int.from_bytes(read_code(report['event_base_object'],4),'little')
    for event in events:
        assert report['entries'][event['function']]==event['pc']
        assert hashlib.sha256(read_code(event['pc'],2)).hexdigest()==event['instruction_sha256']
        if 'kind' not in event:continue
        assert event['function']=='wifi_event' and event['kind']=='connected'
        assert event['base']==base and event['event_id']==wire['connected_id']
        raw=bytes.fromhex(event['event_data_hex']);assert len(raw)==wire['connected_bytes']
        offset=wire['connected_mac'];mac=':'.join(f'{b:02x}' for b in raw[offset:offset+6])
        assert mac==event['mac'] and mac not in macs;macs.add(mac)
    assert macs=={'52:54:00:43:00:02','52:54:00:43:00:03'}
    starts=[e for e in events if e['function']=='httpd_start']
    assert len(starts)==1 and starts[0]['return_value']==0 and starts[0]['server_handle']
    assert report['server_handles']==[starts[0]['server_handle']]
    assert not any(e['function']=='httpd_stop' for e in events)
    assert report['http']==dict(status=200,body_hex=b'0'.hex())
    samples=report['samples'];assert samples
    previous=-1;ids=[set(),set()]
    for sample in samples:
        assert sample['guest_seconds']>=previous;previous=sample['guest_seconds']
        clients=sample['clients'];faults=sample['faults']
        assert len(clients)==len(faults)==3
        for index,(client,loss) in enumerate(zip(clients,faults)):
            assert client['index']==loss['index']==index
            assert client['mac']==f'52:54:00:43:00:{index+2:02x}'
            assert client['online'] is (index<2)
            assert len(loss['dropped'])==len(loss['last_drop_us'])==7
            for number,count in enumerate(loss['dropped']):
                assert type(count) is int and count in (0,1)
                if index!=peer or number not in stages:assert count==0
            if index<2 and client.get('xid','00000000')!='00000000':
                assert len(bytes.fromhex(client['xid']))==4;ids[index].add(client['xid'])
        remaining=sum(1<<(peer*7+stage) for stage in stages if not faults[peer]['dropped'][stage])
        assert sample['pending']==remaining
    last=samples[-1];clients=last['clients'];loss=last['faults'][peer]
    assert all(loss['dropped'][stage]==1 for stage in stages)
    assert sum(sum(x['dropped']) for x in last['faults'])==len(stages)
    assert clients[1-peer]['model_state']==5 and clients[1-peer]['offered_ipv4']!='0.0.0.0'
    if before:
        stage=stages[0]
        assert clients[peer]['model_state']==(6 if stage in (3,5) else 7)
        assert last['guest_seconds']-loss['last_drop_us'][stage]/1e6>=12
    else:
        assert clients[peer]['model_state']==5 and clients[peer]['offered_ipv4']!='0.0.0.0'
        assert clients[0]['offered_ipv4']!=clients[1]['offered_ipv4']
        # Older before-build management runs lack the newer XID observations.
        if 'xid' in clients[0]:
            assert all(len(values)==1 for values in ids) and ids[0]!=ids[1]
            assert clients[1-peer]['dhcp_retries']==0
            assert clients[peer]['dhcp_retries']==sum(stage>=3 for stage in stages)
            assert all(c['dhcp_next_retry_us']==c['dhcp_nominal_seconds']==0 for c in clients[:2])
    if len(stages)>1:
        # wait_http completed before the first sample: the healthy peer served
        # it while the selected peer was still acquiring its lease.
        assert samples[0]['clients'][peer]['model_state']!=5
        assert samples[0]['clients'][1-peer]['model_state']==5
    result=dict(stage=report['stage'],before_control=before,
        recovery_acceptance=report['recovery_acceptance'],unaffected_peer_http=True,owners_stopped=True)
    if len(stages)==1:result['one_actual_loss']=True
    else:result['actual_losses']=len(stages)
    return result


def rejection_checks(report,read_code):
    """Reject fabricated peers, unconsumed faults, false recovery and service loss."""
    rejected=[]
    for case in ('peer-bytes','no-fault','pending-fault','healthy-peer-offline',
                 'http-error','wrong-recovery','mask-not-validated','not-reaped'):
        wrong=copy.deepcopy(report);final=wrong['samples'][-1]
        if case=='peer-bytes':next(e for e in wrong['events'] if 'kind' in e)['event_data_hex']='00'*8
        elif case=='no-fault':final['faults'][wrong['peer']]['dropped'][0 if wrong['stage']=='all' else STAGES.index(wrong['stage'])]=0
        elif case=='pending-fault':final['pending']=wrong['drop_bit']
        elif case=='healthy-peer-offline':final['clients'][1-wrong['peer']]['model_state']=0
        elif case=='http-error':wrong['http']['status']=500
        elif case=='wrong-recovery':wrong['recovery_acceptance']=not wrong['recovery_acceptance']
        elif case=='mask-not-validated':wrong['invalid_mask_rejected']=False
        else:wrong['owners_stopped']=False
        try:validate(wrong,read_code)
        except (AssertionError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid packet loss evidence accepted: '+case)
    return rejected
