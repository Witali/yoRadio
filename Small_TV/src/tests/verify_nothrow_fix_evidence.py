"""Replay the corrected ELF, historical NVS failure and independent network/LCD witnesses."""
import argparse
from copy import deepcopy
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.nothrow_linkage import verify as linkage
from nothrow_target import run as target_run
from nothrow_before import run as before_run
from nothrow_fix_controls import controls
from nothrow_network_qemu import network_ready
from verify_rv32_disassembly_evidence import payload


def same(actual,expected):
    """Do not trust saved success flags, case counts or function labels."""
    if actual!=expected:raise ValueError('Nothrow fix evidence differs from replay')


def observed(network,display,owners,frames):
    """Recompute clock arithmetic, raw settings and every saved LCD pixel independently."""
    assert network['passed'] and network['inputs_unchanged'] and not network['display_tested']
    assert not network['full_vm_oom_injection'] and not network['physical_hardware_tested']
    assert [p['name'] for p in network['phases']]==['configure-reboot','persistent-cold-boot','reset']
    assert [p['rom_boots'] for p in network['phases']]==[2,1,2]
    assert len(network['sessions'])==2 and all(s['exit_code']==0 for s in network['sessions'])
    for index,phase in enumerate(network['phases']):
        assert phase['http_status']==200 and phase['clocktype']==2
        net=phase['network'];ntp=net['ntp'];state=net['state']
        expected=network['sessions'][0 if index==0 else 1]['session']['web_endpoints'][1]['guest_address']
        previous=network['phases'][index-1]['network']['ntp']['response_count'] if index==2 else 0
        assert expected==net['expected_station_address']
        assert network_ready(ntp,state,previous,expected)
        actual=(ntp['boot_time_us']+ntp['systimer_ticks']*5//52+
                ntp['rtc_hrt_offset_us']+ntp['system_correction_us'])/1e6
        predicted=ntp['server_epoch']+(ntp['virtual_us']-ntp['sent_virtual_us'])/1e6
        assert abs(actual-ntp['actual_utc_seconds'])<1e-6
        assert abs(predicted-ntp['expected_utc_seconds'])<1e-6
        assert abs((actual-predicted)-ntp['difference_seconds'])<1e-6 and abs(actual-predicted)<1
        raw=bytes.fromhex(phase['raw_settings_hex']);assert len(raw)==1024
        assert raw[4:69].split(b'\0')[0]==b'yoRadio-QEMU' and int.from_bytes(raw[0x160:0x164],'little')==1
    assert display['passed'] and display['inputs_unchanged'] and not display['network']['executed']
    assert display['requested_cycles_per_variant']==1 and len(display['cycles'])==2
    for case in display['cycles']:
        assert case['passed'] and case['boot']['rom_boots']==1 and case['boot']['no_panic']
        assert case['source_integrity']['passed'] and not case['network']['executed']
        raw=frames[case['variant']];header,bounds,depth,rgb=raw.split(b'\n',3)
        assert (header,bounds,depth)==(b'P6',b'240 240',b'255') and len(rgb)==240*240*3
        assert sha(raw)==case['display']['file_sha256']
        assert sha(rgb)==case['display']['rgb_sha256']==display['expected_rgb_sha256']
        assert case['display']['differing_rgb_bytes']==0
    sessions=[s['owner'] for s in network['sessions']]+[c['session'] for c in display['cycles']]
    assert owners['all_absent'] and len(owners['owners'])==4
    assert {(s['pid'],s['name']) for s in sessions}=={(s['pid'],s['name']) for s in owners['owners']}
    assert all(s['matching_owner_present'] is False for s in owners['owners'])


def verify(proof_path,root,elf,app,object_path,nvs,old_elf,old_app):
    """Check pinned sources and rerun all CPU/static controls without starting another VM."""
    proof=json.loads(proof_path.read_bytes());assert proof['schema']=='nothrow-fix-evidence-v1' and proof['passed']
    for name,digest in proof['source_pins'].items():assert sha((root/name).read_bytes())==digest
    files={name:payload(proof_path.parent,reference) for name,reference in proof['files'].items()}
    current=elf.read_bytes();image=app.read_bytes();wrapper=object_path.read_bytes();library=nvs.read_bytes()
    old=old_elf.read_bytes();old_image=old_app.read_bytes()
    qualified=linkage(current,image,wrapper,library);same(qualified,json.loads(files['linkage']))
    run=target_run(current,image,qualified);same(run,json.loads(files['target']))
    legacy=json.loads(payload(proof_path.parent,proof['legacy_qualification']))
    before=before_run(old,old_image,files['old-nvs-object'],legacy);same(before,json.loads(files['before']))
    assert before['desired_contract_passed'] is False and run['nvs_instruction_oom_proved']
    negative=controls(current,image,wrapper,library,qualified,old,old_image);same(negative,json.loads(files['controls']))
    network=json.loads(files['network']);display=json.loads(files['display']);owners=json.loads(files['owners'])
    frames={name:files['frame:'+name] for name in ('original','reconstructed')}
    observed(network,display,owners,frames)
    assert network['inputs_sha256'][str(elf.resolve())]==qualified['elf_sha256']
    assert display['app_sha256']==qualified['app_sha256'] and display['native_elf_sha256']==qualified['elf_sha256']
    for report in (network,display):
        assert all(sha(Path(p).read_bytes())==digest for p,digest in report['inputs_sha256'].items())
    assert json.loads(files['host'])['passed'] and json.loads(files['host'])['cases']==26
    native=json.loads(files['native']);assert native['passed'] and native['checks']==6300
    privacy=json.loads(files['privacy']);assert privacy['passed'] and privacy['assertions']==3727
    artifact=json.loads(files['artifacts']);assert artifact['passed'] and artifact['app_sha256']==sha(image)
    rejected=[]
    for name in ('stale-ntp','wrong-dhcp','stale-settings','wrong-lcd','live-owner'):
        net,screen,owned=deepcopy(network),deepcopy(display),deepcopy(owners)
        if name=='stale-ntp':net['phases'][2]['network']['ntp']['response_count']=0
        elif name=='wrong-dhcp':net['phases'][0]['network']['state']['station_address']='10.0.2.15'
        elif name=='stale-settings':net['phases'][1]['raw_settings_hex']='00'*1024
        elif name=='wrong-lcd':screen['cycles'][1]['display']['differing_rgb_bytes']=1
        else:owned['owners'][0]['matching_owner_present']=True
        try:observed(net,screen,owned,frames)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('Altered runtime witness accepted')
    return dict(passed=True,target_cases=run['cases'],host_cases=26,native_assertions=6300,
                privacy_assertions=3727,linked_input_rejections=len(negative['rejected']),
                runtime_rejections=rejected,network_phases=3,exact_display_frames=2,
                desired_nothrow_oom_contract_passed=True,full_vm_oom_injection=False,
                physical_hardware_tested=False,whole_image_completeness_proved=False)


def main():
    """Use explicit current/frozen build products; never rewrite historical native identities."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','elf','app','object','nvs','old-elf','old-app'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.elf,args.app,args.object,args.nvs,args.old_elf,args.old_app)))


if __name__=='__main__':main()
