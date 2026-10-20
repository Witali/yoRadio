"""Source-only adaptation. Requires root-reviewed corrected runtime pins first."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / '.build/cyd-vorbis-format-checked-numeric-prep-02/compare_capture.py'
OLD_SHA = '2947be4bb0623eb22ac841d55223c317d4241b4b6ce80819440ff18c212d54d3'
METRICS_SHA = 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # This file intentionally remains unexecuted until root supplies corrected pins.
    pins = json.loads((HERE/'runtime-pins.json').read_bytes())
    assert pins['reviewed_by_root'] is True and pins['cases'] == 25
    assert pins['model_sha256'] == '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc'
    assert pins['controller_sha256'] != '3a475dd5ac3719b40c54fde068e3079da9ef479571b6a839e1c3b8b19bbfedd7'
    assert pins['data_header_sha256'] != '4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757'
    assert sha(OLD) == OLD_SHA and sha(HERE/'pcm_metrics.py') == METRICS_SHA
    runtime = (ROOT/pins['runtime_prep']).resolve()
    assert runtime.is_relative_to(ROOT/'.build') and runtime != ROOT/'.build'
    runtime_inputs = {}
    for role, key in [('controller','controller_sha256'),('contract','contract_file_sha256'),
        ('data_header','data_header_sha256'),('source_map','source_map_sha256'),
        ('reference_binding','reference_binding_sha256'),('binding_helper','binding_helper_sha256'),
        ('protocol','protocol_sha256'),('caller','caller_sha256'),('case_header','case_header_sha256')]:
        relative = Path(pins['runtime_paths'][role])
        path = (runtime/relative).resolve()
        assert not relative.is_absolute() and path.is_relative_to(runtime) and path != runtime,(role,relative)
        assert sha(path) == pins[key],(role,relative)
        runtime_inputs[role] = dict(path=str(path),bytes=path.stat().st_size,sha256=pins[key])
    binding = json.loads(Path(runtime_inputs['reference_binding']['path']).read_bytes())
    original = OLD.read_bytes().decode()
    prefix = original[:original.index('HOST =')]
    prefix = prefix.replace('checked-only17','checked-only25').replace('from pcm_metrics import alignment, bounded_policy, compare, need, relations',
        'from pcm_metrics import alignment, compare, need\nfrom policy25 import CASE_IDS, relations8, bounded_policy25, bounded_policy_books16')
    constants = dict(RUNNER=pins['controller_sha256'],PROTOCOL=pins['protocol_sha256'],CONTRACT=pins['model_sha256'],
        CONTRACT_FILE=pins['contract_file_sha256'],DATA_HEADER=pins['data_header_sha256'],CALLER=pins['caller_sha256'],
        CASE_HEADER=pins['case_header_sha256'],SOURCE_MAP=pins['source_map_sha256'],BINDING=pins['reference_binding_sha256'],
        BINDING_HELPER=pins['binding_helper_sha256'],METRICS=METRICS_SHA,POLICY25=sha(HERE/'policy25.py'),SCOPE_PINS=binding['source_scopes'])
    definitions = original[original.index('COMMANDS ='):original.index('def run(')]
    definitions = definitions.replace('checked-only17','checked-only25')
    text = prefix + ''.join(name+' = '+repr(value)+'\n' for name,value in constants.items()) + definitions
    text += (HERE/'run_body.txt').read_bytes().decode()+'\n\n'+(HERE/'main_body.txt').read_bytes().decode()
    old_ast,new_ast = ast.parse(original),ast.parse(text)
    equal = []
    for name in ('sha','relative','Inputs','wav_pcm','frame_checksums'):
        a = next(node for node in old_ast.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name == name)
        b = next(node for node in new_ast.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name == name)
        assert ast.get_source_segment(original,a).encode() == ast.get_source_segment(text,b).encode(),name
        equal.append(name)
    with (HERE/'compare_capture25.py').open('xb') as stream: stream.write(text.encode())
    with (HERE/'adapter-adaptation.diff').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=str(OLD),tofile='compare_capture25.py')))
    report = dict(schema='expanded25-numeric-source-relation-v1',source_only=True,adapter_executed=False,actual_PCM_read_or_compared=False,
        original_adapter_sha256=OLD_SHA,adapted_adapter_sha256=hashlib.sha256(text.encode()).hexdigest(),metrics_unchanged_sha256=METRICS_SHA,
        byte_identical_definitions=equal,policy25_sha256=sha(HERE/'policy25.py'),runtime_pins=pins,runtime_inputs=runtime_inputs,declared_cases=25,
        source_relations_per_decoder=8,declared_subgroup='books16_only_after_complete25_capture')
    with (HERE/'source-relation.json').open('x',encoding='utf-8',newline='\n') as stream: json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report))


if __name__ == '__main__': main()
