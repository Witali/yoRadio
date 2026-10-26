"""Replay archived TIM effects using original factory and saved production inputs."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from tim_test import run
from audit_factory_xrefs import sha


def compare(recorded, measured):
    """Reject any changed effects, input identity, arithmetic sample or coverage."""
    if recorded != measured:raise ValueError('TIM evidence differs from instruction replay')


def verify(proof_path, root, factory, reference, native, app, old_pp, new_pp):
    """Bound and hash the archive, then independently execute all original code again."""
    proof=json.loads(proof_path.read_bytes())
    assert proof['schema']=='wifi-tim-evidence-v1' and proof['passed']
    for name in ('full_runtime_lifecycle_proved','whole_image_completeness_proved','physical_hardware_tested'):
        assert proof[name] is False
    for name,digest in proof['source_pins'].items():
        path=(root/name).resolve()
        assert path.is_relative_to(root.resolve()) and sha(path.read_bytes())==digest
    ref=proof['report'];path=(proof_path.parent/ref['file']).resolve()
    assert path.is_relative_to(proof_path.parent.resolve())
    compressed=path.read_bytes()
    assert len(compressed)<262144 and sha(compressed)==ref['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(2097153)
    assert len(raw)==ref['bytes']<=2097152 and sha(raw)==ref['sha256']
    recorded=json.loads(raw)
    assert recorded.pop('inputs_unchanged') is True
    for name,digest in recorded.pop('inputs_sha256').items():assert sha(Path(name).read_bytes())==digest
    measured=json.loads(json.dumps(run(factory.read_bytes(),reference.read_bytes(),native.read_bytes(),app.read_bytes(),old_pp,new_pp)))
    compare(recorded,measured)
    rejected=[]
    for name in ('execution-count','counter-wrap','coex-cap','pending-clear','coverage','current-pair'):
        changed=deepcopy(recorded)
        if name=='execution-count':changed['instructions']['executions']+=1
        elif name=='counter-wrap':changed['instructions']['samples']['counter-wrap']['observed']['native']['counter_writes'][0][2]=1
        elif name=='coex-cap':
            calls=changed['instructions']['samples']['coex-full-width-cap']['observed']['native']['calls']
            next(call for call in calls if call[0]=='coex408')[3]+=1
        elif name=='pending-clear':
            changed['instructions']['samples']['factory-null-native-sleep']['observed']['native']['writes'].append([488,1,0])
        elif name=='coverage':changed['instructions']['coverage']['factory']['visited']-=1
        else:changed['qualification']['native_elf_sha256']=changed['qualification']['reference_elf_sha256']
        try:compare(changed,measured)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Altered TIM evidence accepted: '+name)
    return dict(passed=True,executions=measured['instructions']['executions'],
                coverage=measured['instructions']['coverage'],static_controls=measured['rejected_controls'],
                evidence_controls=rejected,full_runtime_lifecycle_proved=False,
                whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Use local immutable inputs and a disposable CPU; launch no QEMU or board."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','reference','native','app','old-pp','new-pp'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.reference,args.native,args.app,args.old_pp,args.new_pp)))


if __name__=='__main__':main()
