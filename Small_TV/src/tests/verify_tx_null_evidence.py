"""Replay full null-completion evidence and reject altered effects or coverage."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from tx_null_test import run
from audit_factory_xrefs import sha


def compare(recorded,measured):
    """Treat any changed identity, trace, field access or coverage as a failed replay."""
    if recorded!=measured:raise ValueError('Null-completion evidence differs from instruction replay')


def verify(proof_path,root,factory,reference,native,app,old_pp,new_pp):
    """Hash bounded saved inputs and independently reexecute both real instruction sets."""
    proof=json.loads(proof_path.read_bytes())
    assert proof['schema']=='wifi-null-completion-evidence-v1' and proof['passed']
    for name in ('full_runtime_lifecycle_proved','whole_image_completeness_proved','physical_hardware_tested'):
        assert proof[name] is False
    for name,digest in proof['source_pins'].items():
        path=(root/name).resolve()
        assert path.is_relative_to(root.resolve()) and sha(path.read_bytes())==digest
    ref=proof['report'];path=(proof_path.parent/ref['file']).resolve()
    assert path.is_relative_to(proof_path.parent.resolve())
    compressed=path.read_bytes();assert len(compressed)<262144 and sha(compressed)==ref['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(2097153)
    assert len(raw)==ref['bytes']<=2097152 and sha(raw)==ref['sha256']
    recorded=json.loads(raw);assert recorded.pop('inputs_unchanged') is True
    for name,digest in recorded.pop('inputs_sha256').items():assert sha(Path(name).read_bytes())==digest
    measured=json.loads(json.dumps(run(factory.read_bytes(),reference.read_bytes(),native.read_bytes(),app.read_bytes(),old_pp,new_pp)))
    compare(recorded,measured)
    rejected=[]
    for name in ('execution-count','ready-branch','missing-station-read','deadline-call',
                 'counter-wrap','quick-byte-result','coverage','lifetime-claim'):
        changed=deepcopy(recorded);result=changed['instructions']
        if name=='execution-count':result['executions']+=1
        elif name=='ready-branch':result['samples']['pending-changes-ready']['observed']['native']['writes'].append([9,1,0])
        elif name=='missing-station-read':result['samples']['missing-station-return']['observed']['native']['station_reads'].append('peer-byte820')
        elif name=='deadline-call':
            calls=result['samples']['sleep-deadline-difference']['observed']['native']['calls']
            calls[calls.index(['sleep'])]=['sleep-delay']
        elif name=='counter-wrap':result['samples']['counter32-wrap']['observed']['native']['counter_writes'][0][2]=1
        elif name=='quick-byte-result':result['samples']['quick-returns-original-byte']['observed']['native']['return_value']=1
        elif name=='coverage':result['coverage']['factory'][0]['visited']-=1
        else:result['station_pointer_lifetime_proved']=True
        try:compare(changed,measured)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Altered null-completion evidence accepted: '+name)
    return dict(passed=True,executions=measured['instructions']['executions'],counts=measured['instructions']['counts'],
        coverage=measured['instructions']['coverage'],static_controls=measured['rejected_controls'],evidence_controls=rejected,
        station_pointer_lifetime_proved=False,full_runtime_lifecycle_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Run offline CPU replay without starting a VM or contacting physical hardware."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','reference','native','app','old-pp','new-pp'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.reference,args.native,args.app,args.old_pp,args.new_pp)))


if __name__=='__main__':main()
