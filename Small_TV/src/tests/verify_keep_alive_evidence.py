"""Recompute archived keep-alive boundaries without launching a firmware VM."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from keep_alive_test import run
from audit_factory_xrefs import sha


def compare(recorded, measured):
    """Reject any changed observation, coverage claim, body binding or case count."""
    if recorded != measured: raise ValueError('Keep-alive evidence differs from instruction replay')


def verify(path,root,factory,native,old_pp,new_pp):
    """Rehash bounded evidence and sources, then reexecute the original body bytes."""
    proof=json.loads(path.read_bytes())
    assert proof['schema']=='wifi-keep-alive-evidence-v1' and proof['passed']
    assert not proof['full_runtime_lifecycle_proved'] and not proof['whole_image_completeness_proved']
    assert not proof['physical_hardware_tested']
    for name,expected in proof['source_pins'].items():
        source=(root/name).resolve()
        assert source.is_relative_to(root.resolve()) and sha(source.read_bytes())==expected
    ref=proof['report'];file=(path.parent/ref['file']).resolve()
    assert file.is_relative_to(path.parent.resolve())
    compressed=file.read_bytes();assert len(compressed)<262144 and sha(compressed)==ref['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(2097153)
    assert len(raw)==ref['bytes']<=2097152 and sha(raw)==ref['sha256']
    recorded=json.loads(raw);assert recorded.pop('inputs_unchanged') is True
    inputs=recorded.pop('inputs_sha256')
    for name,expected in inputs.items():assert sha(Path(name).read_bytes())==expected
    measured=json.loads(json.dumps(run(factory.read_bytes(),native.read_bytes(),old_pp,new_pp)))
    compare(recorded,measured)
    rejected=[]
    for fault in ('execution-count','100ms-boundary','pending-clear','full-null-coverage','foreign-predicate'):
        changed=deepcopy(recorded)
        if fault=='execution-count':changed['instructions']['executions']+=1
        elif fault=='100ms-boundary':
            changed['instructions']['threshold_samples']['100000']['native']['result']['writes'].append([488,1,0])
        elif fault=='pending-clear':
            candidates=changed['instructions']['pending_samples']
            sample=next(s['native'] for s in candidates if [488,1,0] in s['native']['result']['writes'])
            sample['result']['writes'].remove([488,1,0])
        elif fault=='full-null-coverage':changed['instructions']['complete_null_completion_coverage']=True
        else:changed['qualification']['layouts']['factory']['functions'][0]['start']='0x4039061c'
        try:compare(changed,measured)
        except ValueError:rejected.append(fault)
        else:raise AssertionError('Altered keep-alive evidence accepted: '+fault)
    return dict(passed=True,executions=measured['instructions']['executions'],
                static_controls=measured['rejected_controls'],evidence_controls=rejected,
                full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Read original local artifacts and run private CPU fixtures only."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','native','old-pp','new-pp'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.native,args.old_pp,args.new_pp)))


if __name__=='__main__':main()
