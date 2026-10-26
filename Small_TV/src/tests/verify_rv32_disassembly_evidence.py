"""Recompute ISA-qualified exports and all compact-call audit evidence without a VM."""
import argparse
from copy import deepcopy
import gzip
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_rv32_disassembly import audit
from audit_factory_xrefs import Image,sha
from reverse.rv32_disassembly import elf_view,ISA,tool_pins
from reverse.xref_delta import apply,digest


def unit_checks(root,objdump,dump,factory,scratch):
    """Run all tool tests, including real GNU and 2048 literal CPU instructions, with no skips."""
    suite=unittest.TestSuite();identities=[]
    for name,file in (('port_tests','test_assist_c_port.py'),('rv32_tests','test_rv32_disassembly.py')):
        path=root/'Small_TV/src/tools/tests'/file
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module;spec.loader.exec_module(module)
        module.TEMP_ROOT=scratch
        module.OPTIONS=SimpleNamespace(objdump=objdump,dump=dump,factory_elf=factory,temp_root=scratch)
        loaded=unittest.defaultTestLoader.loadTestsFromModule(module)
        def collect(tests):
            """Retain actual test identities before unittest releases completed cases."""
            for test in tests:
                if isinstance(test,unittest.TestSuite):collect(test)
                else:identities.append(test.id())
        collect(loaded);suite.addTests(loaded)
    scratch.mkdir(parents=True,exist_ok=True);log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=1).run(suite)
    if not result.wasSuccessful() or result.skipped:raise AssertionError(log.getvalue())
    return dict(passed=True,tests=result.testsRun,identities=identities,literal_cpu_encodings=2048,
                actual_gnu_encodings=2048,skipped=0,failures=0,errors=0)


def payload(root,reference):
    """Read only a hashed bounded artifact; graph ancestors are reused rather than copied."""
    path=(root/reference['file']).resolve();assert path.is_relative_to(root.resolve())
    packed=path.read_bytes();assert len(packed)<=8*1024*1024 and sha(packed)==reference['gzip_sha256']
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:raw=stream.read(16*1024*1024+1)
    assert len(raw)==reference['bytes']<=16*1024*1024 and sha(raw)==reference['sha256']
    return raw


def same(recorded,measured):
    """Reject any changed count, target or claim instead of trusting a recorded pass flag."""
    if recorded!=measured:raise ValueError('Disassembly evidence differs from complete byte/call replay')


def verify(proof_path,root,factory,before,after,objdump,dump,scratch):
    """Rebuild the exact graph, source-code audit and public command tests."""
    proof=json.loads(proof_path.read_bytes());assert proof['schema']=='rv32-disassembly-evidence-v1' and proof['passed']
    assert not proof['whole_image_completeness_proved'] and not proof['candidate_reachability_proved']
    for name,value in proof['source_pins'].items():
        path=(root/name).resolve();assert path.is_relative_to(root.resolve()) and sha(path.read_bytes())==value
    files={name:payload(proof_path.parent,reference) for name,reference in proof['files'].items()}
    graph=apply(json.loads(payload(proof_path.parent,proof['graph_before'])),json.loads(payload(proof_path.parent,proof['graph_delta'])))
    recorded=json.loads(files['audit']);assert recorded.pop('inputs_unchanged') is True
    pins=recorded.pop('inputs_sha256');roles=recorded.pop('input_roles')
    for role,path in (('elf',factory),('before',before),('after',after)):
        assert sha(path.read_bytes())==pins[roles[role]]
    assert digest(graph)==recorded['ghidra_graph_sha256']
    measured=audit(factory.read_bytes(),before.read_text(encoding='utf8'),after.read_text(encoding='utf8'),graph)
    same(recorded,measured)
    manifest=json.loads(files['export']);image=Image(factory.read_bytes())
    regions=[(r['name'],r['start'],r['data']) for r in image.sections if r['execute']]
    assert manifest['factory_elf_sha256']==sha(factory.read_bytes()) and manifest['assembly_sha256']==sha(after.read_bytes())
    assert manifest['disassembler']['isa']==ISA and manifest['disassembler']['view_sha256']==sha(elf_view(regions))
    assert manifest['disassembler']['tool_pins']==tool_pins(objdump)
    units=unit_checks(root,objdump,dump,factory,scratch);same(json.loads(files['units']),units)
    rejected=[]
    for fault in ('wrong-target','missed-call-count','missing-call','gp-count','missing-zero','graph-reference','reachability','whole-image-claim'):
        changed=deepcopy(recorded)
        if fault=='wrong-target':changed['calls'][0]['target']+=2
        elif fault=='missed-call-count':changed['compressed_call_candidates']-=1
        elif fault=='missing-call':changed['calls'].pop()
        elif fault=='gp-count':changed['gp_accesses_preserved']-=1
        elif fault=='missing-zero':changed['added_zero_bytes']=0
        elif fault=='graph-reference':changed['ghidra_matched_calls']+=1
        elif fault=='reachability':changed['candidate_reachability_proved']=True
        else:changed['whole_image_completeness_proved']=True
        try:same(changed,measured)
        except ValueError:rejected.append(fault)
        else:raise AssertionError('Altered disassembly evidence accepted: '+fault)
    text=after.read_text(encoding='utf8')
    changed,count=re.subn(r'(^420aeb6e:\s+2b71\s+c\.jal\s+)0x420af10a',r'\g<1>0x420af100',text,count=1,flags=re.MULTILINE)
    assert count==1
    try:audit(factory.read_bytes(),before.read_text(encoding='utf8'),changed,graph)
    except ValueError:rejected.append('wrong-gnu-target')
    else:raise AssertionError('Incorrect GNU call target accepted')
    return dict(passed=True,unit_tests=units['tests'],compressed_call_candidates=measured['compressed_call_candidates'],
        executable_bytes=measured['exported_code_bytes'],gp_accesses_preserved=measured['gp_accesses_preserved'],
        unmatched_candidates=measured['unmatched_candidates'],rejected_controls=rejected,
        whole_image_completeness_proved=False,candidate_reachability_proved=False,physical_hardware_tested=False)


def main():
    """Verify code-only artifacts with explicit local inputs and no QEMU/board interaction."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','before','after','objdump','dump','scratch'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.factory,args.before,args.after,args.objdump,args.dump,args.scratch)))


if __name__=='__main__':main()
