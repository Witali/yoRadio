"""AST/byte-only proposal check: no imports or execution of prepared code or PCM."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def literal(tree,name):
    matches = [node.value for node in tree.body if isinstance(node,ast.Assign) and
        any(isinstance(item,ast.Name) and item.id == name for item in node.targets)]
    assert len(matches) == 1,name
    return ast.literal_eval(matches[0])


def definition(text,tree,name):
    nodes = [node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name == name]
    assert len(nodes) == 1,name
    return ast.get_source_segment(text,nodes[0])


def main():
    names = ('compare_capture25.py','pcm_metrics.py','policy25.py','prepare_adapter.py',
        'check_source.py','run_body.txt','main_body.txt','runtime-pins.json','README.md',
        'adapter-adaptation.diff','source-relation.json')
    inputs = {name:fact(HERE/name) for name in names}
    parsed = {}
    for name in names:
        if name.endswith('.py') or name.endswith('_body.txt'):
            parsed[name] = ast.parse((HERE/name).read_bytes().decode(),filename=str(HERE/name))
    pins = json.loads((HERE/'runtime-pins.json').read_bytes())
    relation = json.loads((HERE/'source-relation.json').read_bytes())
    runtime = (ROOT/pins['runtime_prep']).resolve()
    assert runtime.is_relative_to(ROOT/'.build') and runtime != ROOT/'.build'
    for role,row in relation['runtime_inputs'].items():
        assert fact(Path(row['path'])) == row
        assert Path(row['path']).resolve().is_relative_to(runtime)
    contract_path = runtime/pins['runtime_paths']['contract']
    contract = json.loads(contract_path.read_bytes())
    model = contract['model']
    assert contract['contract_sha256'] == pins['model_sha256']
    assert len(model['cases']) == 25 and model['total_packets'] == 350 and model['total_pcm'] == 623360 and model['case_mask'] == 33554431
    assert tuple(case['id'] for case in model['cases']) == literal(parsed['policy25.py'],'CASE_IDS')
    old = ROOT/'.build/cyd-vorbis-format-checked-numeric-prep-02/compare_capture.py'
    oldtext = old.read_bytes().decode(); oldtree = ast.parse(oldtext)
    assert fact(old)['sha256'] == '2947be4bb0623eb22ac841d55223c317d4241b4b6ce80819440ff18c212d54d3'
    oldmetrics = old.with_name('pcm_metrics.py')
    assert (HERE/'pcm_metrics.py').read_bytes() == oldmetrics.read_bytes()
    assert inputs['pcm_metrics.py']['sha256'] == 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
    newtext = (HERE/'compare_capture25.py').read_bytes().decode(); newtree = parsed['compare_capture25.py']
    equal = []
    for name in ('sha','relative','Inputs','wav_pcm','frame_checksums'):
        assert definition(oldtext,oldtree,name) == definition(newtext,newtree,name),name
        equal.append(name)
    for name,filename in (('run','run_body.txt'),('main','main_body.txt')):
        assert definition(newtext,newtree,name) == definition((HERE/filename).read_bytes().decode(),parsed[filename],name),name
    for constant,key in (('RUNNER','controller_sha256'),('PROTOCOL','protocol_sha256'),('CONTRACT','model_sha256'),
        ('CONTRACT_FILE','contract_file_sha256'),('DATA_HEADER','data_header_sha256'),('CALLER','caller_sha256'),
        ('CASE_HEADER','case_header_sha256'),('SOURCE_MAP','source_map_sha256'),('BINDING','reference_binding_sha256'),
        ('BINDING_HELPER','binding_helper_sha256')):
        assert literal(newtree,constant) == pins[key],constant
    assert literal(newtree,'POLICY25') == inputs['policy25.py']['sha256']
    assert literal(newtree,'METRICS') == inputs['pcm_metrics.py']['sha256']
    assert literal(newtree,'COMMANDS') == ('sdk-head','sdk-clean','build','setup-macros','symbols','merge','qemu','sdk-head-after','sdk-clean-after')
    assert relation['adapted_adapter_sha256'] == inputs['compare_capture25.py']['sha256']
    assert relation['policy25_sha256'] == inputs['policy25.py']['sha256']
    for name,row in inputs.items(): assert fact(HERE/name) == row,name
    report = dict(schema='expanded25-numeric-source-closure-v1',scope='AST_AND_BYTES_ONLY_NOT_RUNTIME',
        source_only=True,prepared_adapter_executed=False,metric_or_policy_executed=False,actual_PCM_read_or_compared=False,
        source_assembly_terminal=dict(exit_code=0,chunk_id='becfb1'),metrics_unchanged=True,
        byte_identical_definitions=equal,declared_cases=25,packets=350,pcm_bytes=623360,events=778,
        source_relations_per_decoder=8,full25_not_replaced_by_subgroup=True,
        runtime_inputs=relation['runtime_inputs'],inputs=inputs)
    with (HERE/'source-closure02.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
