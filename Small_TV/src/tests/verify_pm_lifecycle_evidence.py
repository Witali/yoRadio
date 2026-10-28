"""Replay bounded PM start/stop evidence from the original ELF, SDK and ROM."""
import argparse
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path

from pm_lifecycle_test import run
from audit_factory_xrefs import sha


def compare(recorded,measured):
    """Require exact recomputed state/calls/coverage, not a saved passed flag."""
    if recorded != measured:raise ValueError('PM lifecycle evidence differs from instruction replay')


def verify(path,root,factory,native,old_pp,new_pp,rom):
    """Rehash sources and bounded data, then rerun the complete instruction matrix."""
    proof=json.loads(path.read_bytes())
    assert proof['schema']=='wifi-pm-lifecycle-evidence-v1' and proof['passed']
    assert not proof['full_runtime_lifecycle_proved'] and not proof['transitive_platform_effects_proved']
    assert not proof['physical_hardware_tested'] and not proof['whole_image_completeness_proved']
    for name,digest in proof['source_pins'].items():
        file=(root/name).resolve();assert file.is_relative_to(root.resolve()) and sha(file.read_bytes())==digest
    ref=proof['report'];file=(path.parent/ref['file']).resolve()
    assert file.is_relative_to(path.parent.resolve())
    compressed=file.read_bytes();assert len(compressed)<262144 and sha(compressed)==ref['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(2097153)
    assert len(raw)==ref['bytes']<=2097152 and sha(raw)==ref['sha256']
    recorded=json.loads(raw);assert recorded.pop('inputs_unchanged') is True
    for name,digest in recorded.pop('inputs_sha256').items():assert sha(Path(name).read_bytes())==digest
    measured=json.loads(json.dumps(run(factory.read_bytes(),native.read_bytes(),old_pp,new_pp,rom.read_bytes())))
    compare(recorded,measured)
    rejected=[]
    for fault in ('missing-492-disarm','idempotence','rom-binding','coverage','platform-claim'):
        changed=deepcopy(recorded)
        if fault=='missing-492-disarm':
            changed['instructions']['stop_samples']['factory']['trace']['calls'].remove(['disarm',492])
        elif fault=='idempotence':
            changed['instructions']['sequences'][0][1]['trace']['writes'].append([14,1,0])
        elif fault=='rom-binding':changed['qualification']['layouts']['native']['rom']['pointer']+=4
        elif fault=='coverage':changed['instructions']['coverage']['native'][0]['visited']-=1
        else:changed['transitive_platform_effects_proved']=True
        try:compare(changed,measured)
        except ValueError:rejected.append(fault)
        else:raise AssertionError('Altered lifecycle evidence accepted: '+fault)
    return dict(passed=True,executions=measured['instructions']['executions'],
                static_controls=measured['rejected_controls'],evidence_controls=rejected,
                full_runtime_lifecycle_proved=False,transitive_platform_effects_proved=False,
                physical_hardware_tested=False,whole_image_completeness_proved=False)


def main():
    """Read saved artifacts and private CPU fixtures; never launch or attach a VM."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','native','old-pp','new-pp','rom'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.factory,args.native,args.old_pp,args.new_pp,args.rom)))


if __name__=='__main__':main()
