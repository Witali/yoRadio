"""Replay the factory handler-lifetime defect and the native recovery correction."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from event_lifetime_test import run
from event_delivery_metadata import decode as decode_event
from pm_runtime_metadata import decode as decode_pm
from audit_factory_xrefs import sha
from reverse.pm_runtime_layout import qualify as qualify_pm
from verify_pm_runtime_evidence import cancellation_caller


def replay(row, field, decoder, layout, reads_field):
    """Consume exact typed read order, rejecting additions, truncation and altered decoded data."""
    saved = deepcopy(row[field]); reads = saved.pop(reads_field) if reads_field in saved else row[reads_field]
    assert len(reads) <= 32 and sum(r['size'] for r in reads) <= 256
    index = 0
    def memory(address, size):
        """No general memory lookup or hidden fallback is allowed during reconstruction."""
        nonlocal index
        item = reads[index]; index += 1
        assert (item['address'], item['size']) == (address, size)
        data = bytes.fromhex(item['hex']); assert len(data) == size
        return data
    value = decoder(memory, layout)
    assert value == saved and index == len(reads)
    return value


def runtime(factory, native, owners, uart, layout, pm, caller):
    """Require successful teardown, actual queue delivery and a separate successful native recovery."""
    assert factory['passed'] is False and native['passed'] is True
    assert factory['inputs_unchanged'] and native['inputs_unchanged']
    for report in (factory, native):
        for name in ('full_runtime_lifecycle_proved','whole_image_completeness_proved','physical_hardware_tested'):
            assert report[name] is False
    assert len(owners) == 2 and all(not row['present'] for row in owners)
    flow = native['flows']['native']; assert set(native['flows']) == {'native'}
    assert {row['pid'] for row in owners} == {factory['session']['pid'],flow['session']['pid']}
    for variant in ('factory','native'):
        assert uart[variant].count(b'ESP-ROM:esp32c2') == 1
        assert not any(token in uart[variant] for token in (b'Guru Meditation',b'assert failed',b'abort() was called'))
    assert factory['event_layout'] == layout
    assert factory['owned_stop_completed'] and factory['controller_stopped'] and factory['uart_clean']
    assert factory['observation_timeout'] and not factory.get('observation_limit')
    assert not factory.get('error') and not factory['controller'].get('error')
    f = layout['factory']; startup = factory['startup_teardown']
    assert [r['pc'] for r in startup] == [0x4200cdae,0x4200cdb2,0x4200cdc0,0x4200cdc4]
    assert startup[0]['arguments'] == [f['ip_base'],0,f['callback']]
    assert startup[2]['arguments'] == [f['wifi_base'],0xffffffff,f['callback']]
    assert startup[1]['arguments'][0] == startup[3]['arguments'][0] == 0
    for row in startup: replay(row,'metadata',decode_pm,pm['layouts']['factory'],'raw_reads')
    events = factory['events']
    assert [r['boundary'] for r in events] == ['post-to-entry','queue-send-return','driver-post-return','handler-call','handler-return']
    assert [r['pc'] for r in events] == [0x420af6f2,0x420af74e,0x4206e042,0x420aeb96,0x420aeb98]
    assert (events[0]['posted_base'],events[0]['posted_id'],events[0]['posted_bytes']) == (f['wifi_base'],5,41)
    assert events[1]['queue_return'] == 1 and events[2]['post_return'] == 0
    assert (events[3]['event_base'],events[3]['event_id'],events[3]['target']) == (f['wifi_base'],5,0x420456ea)
    assert events[4]['returned_handler'] == dict(target=0x420456ea,base=f['wifi_base'],id=5)
    assert factory['pending_handlers'] == {}
    rows = [factory['baseline'],*events,factory['last']]
    queues = [replay(r,'event_loop',decode_event,f,'reads') for r in rows]
    metadata = [replay(r,'metadata',decode_pm,pm['layouts']['factory'],'raw_reads') for r in rows]
    assert [q['count'] for q in queues] == [0,0,1,1,0,0,0]
    assert len({q['queue'] for q in queues}) == len({q['task'] for q in queues}) == len({q['loop'] for q in queues}) == 1
    assert all(q['current'] == q['task'] == q['running'] for q in queues[4:6])
    assert queues[-1]['running'] == 0
    assert [m['pm_active'] for m in metadata] == [1,0,0,0,0,0,0]
    assert all(m['station_state'] == 2 and m['timer_owner_bound'] for m in metadata)
    assert all(b['guest_counter_us'] > a['guest_counter_us'] for a,b in zip(metadata,metadata[1:]))
    assert factory['controller']['online'] is True
    elapsed = (factory['controller']['online_counter']-factory['controller']['offline_counter']) & 0xffffffff
    assert 1000000 <= elapsed < 5000000
    assert metadata[-1]['guest_counter_us'] > factory['controller']['online_counter']+1000000
    assert flow['passed'] and flow['uart_clean'] and flow['owned_stop_completed'] and 'error' not in flow
    assert flow['http_statuses'] == [200,200,200] and flow['cancel_caller_return'] == caller['cancel_return']
    assert [r['phase'] for r in flow['observations']] == ['connected','stop-return','cancel-entry','cancel-return','disconnected','reconnected']
    nm = [replay(r,'metadata',decode_pm,pm['layouts']['native'],'raw_reads') for r in flow['observations']]
    assert [r['station_state'] for r in nm] == [1,1,1,1,0,1]
    assert [r['pm_active'] for r in nm] == [1,0,0,0,0,1]
    assert [r['timer_armed'] for r in nm] == [True,True,True,False,False,True]
    return dict(factory_unregister_successes=2,queue_delivery_observed=True,system_handler_returned=True,
                application_handler_removed_after_first_lease=True,native_recovery_passed=True,
                factory_recovery_passed=False)


def verify(path, root, factory, native, old_pp, new_pp, dependencies):
    """Hash sources/records, execute the private instruction tests and replay both actual VMs."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'event-lifetime-evidence-v1' and proof['analysis_verified']
    for name in ('full_runtime_lifecycle_proved','whole_image_completeness_proved','physical_hardware_tested'):
        assert proof[name] is False
    for name,digest in proof['source_pins'].items():
        file=(root/name).resolve(); assert file.is_relative_to(root.resolve()) and sha(file.read_bytes())==digest
    files={}
    for name,reference in proof['files'].items():
        file=(path.parent/reference['file']).resolve(); assert file.is_relative_to(path.parent.resolve())
        compressed=file.read_bytes(); assert len(compressed)<=262144 and sha(compressed)==reference['gzip_sha256']
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream: raw=stream.read(2097153)
        assert len(raw)==reference['bytes']<=2097152 and sha(raw)==reference['sha256']; files[name]=raw
    units=json.loads(files['units']); assert units.pop('inputs_unchanged') is True
    pins=units.pop('inputs_sha256')
    measured=json.loads(json.dumps(run(factory,native,dependencies))); assert units==measured
    observed_factory,observed_native=json.loads(files['factory']),json.loads(files['native'])
    pins.update(observed_factory['inputs_sha256']); pins.update(observed_native['inputs_sha256'])
    for name,digest in pins.items(): assert sha(Path(name).read_bytes())==digest,'Changed input: '+name
    rom=dependencies/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    pm=qualify_pm(factory.read_bytes(),native.read_bytes(),old_pp,new_pp,rom.read_bytes())
    caller=cancellation_caller(native.read_bytes()); owners=json.loads(files['owners'])
    uart={v:files['uart-'+v] for v in ('factory','native')}
    result=runtime(observed_factory,observed_native,owners,uart,measured['layout'],pm,caller)
    rejected=[]
    for fault in ('wrong-unregister-handler','unregister-error','queue-send-failure','wrong-system-handler',
                  'fake-empty-queue','wrong-event-task','stale-native-connection','extra-read','owner-present','uart-reset','full-lifecycle-claim'):
        f,n,o,logs=deepcopy(observed_factory),deepcopy(observed_native),deepcopy(owners),dict(uart)
        if fault=='wrong-unregister-handler':f['startup_teardown'][2]['arguments'][2]+=2
        elif fault=='unregister-error':f['startup_teardown'][1]['arguments'][0]=1
        elif fault=='queue-send-failure':f['events'][1]['queue_return']=0
        elif fault=='wrong-system-handler':f['events'][3]['target']=measured['layout']['factory']['callback']
        elif fault=='fake-empty-queue':
            q=f['events'][1]['event_loop'];q['count']=0;q['reads'][-3]['hex']='00000000'
        elif fault=='wrong-event-task':
            q=f['events'][3]['event_loop'];q['current']+=4;q['reads'][1]['hex']=q['current'].to_bytes(4,'little').hex()
        elif fault=='stale-native-connection':
            row=n['flows']['native']['observations'][4];row['metadata']['station_state']=1
            row['metadata']['application_connected_hint']=True;row['raw_reads'][0]['hex']='01'
        elif fault=='extra-read':f['last']['event_loop']['reads'].append(deepcopy(f['last']['event_loop']['reads'][0]))
        elif fault=='owner-present':o[0]['present']=True
        elif fault=='uart-reset':logs['native']+=b'ESP-ROM:esp32c2'
        else:f['full_runtime_lifecycle_proved']=True
        try:runtime(f,n,o,logs,measured['layout'],pm,caller)
        except (AssertionError,ValueError,IndexError):rejected.append(fault)
        else:raise AssertionError('Altered event lifetime evidence accepted: '+fault)
    return dict(analysis_verified=True,runtime=result,dispatch_cases=len(measured['dispatch']['cases']),
                teardown_cases=len(measured['teardown']),metadata_controls=measured['metadata']['rejected_controls'],
                rejected_runtime_controls=rejected,full_runtime_lifecycle_proved=False,
                whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Read archived evidence and immutable ELF files; launch no QEMU instance."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','native','old-pp','new-pp','dependency-root'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.native,args.old_pp,args.new_pp,args.dependency_root)))


if __name__=='__main__':main()
