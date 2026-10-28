"""Replay callback/BSS producer evidence, preserving the conditional failing gate."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from wifi_producer_test import run
from audit_factory_xrefs import sha


def compare(recorded,measured):
    """Reject changes to producer effects, safety conclusions or qualified code."""
    if recorded!=measured:raise ValueError('Wi-Fi producer evidence differs from replay')


def verify(proof_path,root,factory,reference,native,app,old_pp,new_pp,old_net,new_net,sdkconfig):
    """Rehash original sources and artifacts, then independently execute both images."""
    proof=json.loads(proof_path.read_bytes())
    assert proof['schema']=='wifi-producer-evidence-v1' and proof['passed']
    assert proof['conditional_timer_defect_baseline'] is True
    for name in ('runtime_registration_proved','station_pointer_lifetime_proved','whole_image_completeness_proved','physical_hardware_tested'):
        assert proof[name] is False
    for name,digest in proof['source_pins'].items():
        path=(root/name).resolve();assert path.is_relative_to(root.resolve()) and sha(path.read_bytes())==digest
    ref=proof['report'];path=(proof_path.parent/ref['file']).resolve()
    assert path.is_relative_to(proof_path.parent.resolve())
    compressed=path.read_bytes();assert len(compressed)<262144 and sha(compressed)==ref['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(2097153)
    assert len(raw)==ref['bytes']<=2097152 and sha(raw)==ref['sha256']
    recorded=json.loads(raw);assert recorded.pop('inputs_unchanged') is True
    for name,digest in recorded.pop('inputs_sha256').items():assert sha(Path(name).read_bytes())==digest
    measured=json.loads(json.dumps(run(factory.read_bytes(),reference.read_bytes(),native.read_bytes(),app.read_bytes(),
        old_pp,new_pp,old_net,new_net,sdkconfig.read_bytes())))
    compare(recorded,measured)
    assert measured['conditional_timer_range_defects_present'] is True
    assert measured['instructions']['timer_safety_gate_passed'] is False
    rejected=[]
    for name in ('descriptor-status','descriptor-bit','peer-options','wrapped-delay','safety-claim',
                 'feature-default','body-extent','lifetime-claim'):
        changed=deepcopy(recorded);result=changed['instructions']
        if name=='descriptor-status':result['samples']['callback-flag-1']['observed']['native']['parent_ingress'][0][1]=2
        elif name=='descriptor-bit':result['samples']['callback-flag-0']['observed']['native']['parent_ingress'][0][2]=1
        elif name=='peer-options':result['samples']['period-4196']['observed']['native']['peer_writes'][1][2]=2
        elif name=='wrapped-delay':result['conditional_defect_witnesses']['native']['actual_microseconds']=4295728000
        elif name=='safety-claim':result['timer_safety_gate_passed']=True
        elif name=='feature-default':changed['archived_sdkconfig_bss_max_idle_enabled']=True
        elif name=='body-extent':changed['qualification']['layouts']['factory']['functions'][0]['linked_bytes']-=2
        else:result['station_pointer_lifetime_proved']=True
        try:compare(changed,measured)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Altered Wi-Fi producer evidence accepted: '+name)
    return dict(passed=True,executions=measured['instructions']['executions'],static_controls=measured['rejected_controls'],evidence_controls=rejected,
        conditional_timer_defect_baseline=True,timer_safety_gate_passed=False,
        archived_sdkconfig_bss_max_idle_enabled=False,production_runtime_enablement_proved=False,
        runtime_registration_proved=False,station_pointer_lifetime_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Run offline replay only; do not start a VM or alter frozen input files."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','reference','native','app','old-pp','new-pp','old-net','new-net','sdkconfig'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.reference,args.native,args.app,
        args.old_pp,args.new_pp,args.old_net,args.new_net,args.sdkconfig)))


if __name__=='__main__':main()
