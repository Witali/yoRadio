"""Independently replay station events and retained/fresh raw weather publications."""
import copy
import hashlib
import json
import math
import socket
import struct


def cache(row,layout):
    """Decode the actual target cache bytes, never a copied readiness claim."""
    raw=bytes.fromhex(row['raw_hex']);assert len(raw)==layout['size']
    fields=layout['fields'];assert row['worker_state'] in (0,1,2,3)
    assert row['generation']==int.from_bytes(raw[fields['generation']:fields['generation']+4],'little')
    result=dict(valid=bool(raw[fields['valid']]))
    assert raw[fields['valid']] in (0,1)
    for name in ('temperature_c','temperature_min_c','temperature_max_c','wind_mps'):
        result[name]=struct.unpack_from('<d',raw,fields[name])[0]
    result['humidity']=struct.unpack_from('<i',raw,fields['humidity'])[0]
    for name in ('main','description','wind_direction','icon'):
        result[name]=raw[fields[name]:].split(b'\0',1)[0].decode('ascii')
    if row['worker_state']==0:assert row['weather']==result
    return result


def positive(row,layout,humidity):
    """Require all published synthetic scalars/text, including factory truncation."""
    value=cache(row,layout)
    assert row['worker_state']==0 and row['generation']>0 and value['valid']
    assert value['humidity']==humidity and value['temperature_c']==26
    for name,expected in [('temperature_min_c',21.5),('temperature_max_c',29.5),('wind_mps',3.75)]:
        assert math.isclose(value[name],expected,rel_tol=0,abs_tol=1e-8)
    assert (value['main'],value['description'],value['wind_direction'],value['icon'])==(
        'Clouds','scattered cloud','North-Northeast','02d')


def validate(report,read_code):
    """Require two real disconnect/GOT_IP pairs and successful fresh HTTP recovery."""
    assert report['passed'] and report['owners_stopped'] and report['rom_boots']==1
    assert not any(report[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    station=report['station_layout'];layout=report['weather_layout'];events=report['events']
    constants=station['constants'];objects=station['objects']
    ip_base=int.from_bytes(read_code(objects['IP_EVENT']['address'],4),'little')
    wifi_base=int.from_bytes(read_code(objects['WIFI_EVENT']['address'],4),'little')
    kinds=[]
    expected_address=int.from_bytes(socket.inet_aton('10.0.2.15'),'little')
    for index,event in enumerate(events):
        assert report['entries'][event['function']]==event['pc']
        assert hashlib.sha256(read_code(event['pc'],2)).hexdigest()==event['instruction_sha256']
        assert index<event['return_event_index']<=len(events)
        if 'station_kind' not in event:continue
        kind=event['station_kind'];kinds.append(kind);state=event['station_after']
        assert event['function']=='wifi_event' and not state['ap_active']
        assert state['last_station_address']==expected_address
        if kind=='got_ip':
            assert event['base']==ip_base and event['event_id']==constants['IP_EVENT_STA_GOT_IP']
            raw=bytes.fromhex(event['payload_hex']);assert len(raw)==station['got_ip']['bytes']
            offset=station['ip_offset']
            assert socket.inet_ntoa(raw[offset:offset+4])==event['ipv4']=='10.0.2.15'
            assert state['connected']==1 and state['station_retries']==0
        else:
            assert kind=='disconnected' and event['base']==wifi_base
            assert event['event_id']==constants['WIFI_EVENT_STA_DISCONNECTED']
            assert state['connected']==0 and state['station_retries']==1
    assert kinds==['got_ip','disconnected','got_ip','disconnected','got_ip']
    starts=[e for e in events if e['function']=='httpd_start']
    assert len(starts)==1 and starts[0]['return_value']==0 and starts[0]['server_handle']
    assert report['server_handles']==[starts[0]['server_handle']]
    assert not any(e['function']=='httpd_stop' for e in events)
    cases=report['cases'];assert [row['status'] for row in cases]==[200,503]
    assert len(report['restorations'])==2
    positive(report['initial'],layout,67);previous=report['initial'];retained=0
    requests=report['requests']
    assert all(r['method']=='GET' and r['resource']=='/data/2.5/weather' and
               r['synthetic_key'] and r['synthetic_location'] for r in requests)
    for index,row in enumerate(cases):
        assert row['before']['raw_hex']==previous['raw_hex']
        assert row['held']['worker_state'] & 1
        assert row['held']['raw_hex']==row['before']['raw_hex']
        assert 0<=row['held_host_seconds']<30
        begin,end=row['events_begin'],row['events_end'];assert 0<=begin<end<=len(events)
        paired=[e['station_kind'] for e in events[begin:end] if 'station_kind' in e]
        assert paired==['disconnected','got_ip']
        restoration=report['restorations'][index]
        assert begin<=restoration['event_index']<end
        assert events[restoration['event_index']]['station_kind']=='disconnected'
        assert restoration['external_before'] is False and restoration['external_after'] is True
        assert row['reconnected']==events[end-1]['station_after']
        assert row['reconnected']['connected'] and row['reconnected']['station_retries']==0
        for name in ('before','held','before_release','settled','recovered'):cache(row[name],layout)
        assert row['settled']['worker_state']==0 and row['settled']['weather']['valid']
        if row['settled']['raw_hex']==row['before']['raw_hex']:retained+=1
        else:assert row['status']==200 and row['settled']['weather']['humidity']==41
        if row['status']==503:assert row['settled']['raw_hex']==row['before']['raw_hex']
        for name in ('refresh_http','recovery_http'):
            assert row[name]==dict(status=200,body_hex=b'OK'.hex())
        assert row['theme_http']==dict(status=200,body_hex=b'0'.hex())
        body=row['recovery_body'];assert body['main']['humidity']==78+index
        digest=hashlib.sha256(json.dumps(body,separators=(',',':')).encode()).hexdigest()
        assert any(r['status']==200 and r['body_sha256']==digest for r in requests[row['requests_before']:])
        assert requests[row['requests_before']-1]['status']==row['status']
        positive(row['recovered'],layout,78+index)
        assert row['recovered']['generation']>row['settled']['generation']
        previous=row['recovered']
    return dict(passed=True,station_outages=2,got_ip_events=3,retained_cache_cases=retained,
        fresh_weather_publications=2,http_server_starts=1,http_server_stops=0,rom_boots=1,
        network_lifecycle_complete=False)


def rejection_checks(report,read_code):
    """Reject fabricated reconnection, stale cache, duplicate service or reboot."""
    rejected=[]
    for case in ('missing-disconnect','wrong-ip','retry-not-reset','early-publication',
                 'stale-recovery','error-cache-overwrite','duplicate-server','extra-boot','not-reaped'):
        wrong=copy.deepcopy(report)
        if case=='missing-disconnect':next(e for e in wrong['events'] if e.get('station_kind')=='disconnected').pop('station_kind')
        elif case=='wrong-ip':next(e for e in wrong['events'] if e.get('station_kind')=='got_ip')['ipv4']='10.0.2.2'
        elif case=='retry-not-reset':next(e for e in wrong['events'] if e.get('station_kind')=='got_ip')['station_after']['station_retries']=4
        elif case=='early-publication':wrong['cases'][0]['held']['raw_hex']=wrong['cases'][0]['recovered']['raw_hex']
        elif case=='stale-recovery':wrong['cases'][0]['recovered']['raw_hex']=wrong['cases'][0]['before']['raw_hex']
        elif case=='error-cache-overwrite':wrong['cases'][1]['settled']['raw_hex']=wrong['cases'][1]['recovered']['raw_hex']
        elif case=='duplicate-server':wrong['server_handles']*=2
        elif case=='extra-boot':wrong['rom_boots']=2
        else:wrong['owners_stopped']=False
        try:validate(wrong,read_code)
        except (AssertionError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid station weather evidence accepted: '+case)
    return rejected
