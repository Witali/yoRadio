"""AST/hash/source-only closure; never import prepared adapter or read actual PCM."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-format-expanded25-numeric-prep-01'
RUNTIME = ROOT / '.build/c3-vorbis-format-expanded25-prep-02'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    nodes = [node for node in tree.body if isinstance(node, ast.Assign) and
             any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(nodes) == 1, name
    return ast.literal_eval(nodes[0].value)


def definition(text, tree, name):
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name]
    assert len(nodes) == 1, name
    return ast.get_source_segment(text, nodes[0])


def replace_one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def write_json(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    py_names = ('compare_capture25.py', 'pcm_metrics.py', 'policy25.py', 'prepare_adapter.py',
                'prepare_adapter01-failed.py', 'check_source.py')
    texts = {name: (HERE / name).read_bytes().decode('utf-8') for name in py_names}
    trees = {name: ast.parse(text, filename=name) for name, text in texts.items()}
    original = (BASE / 'compare_capture25.py').read_bytes()
    assert sha(original) == '2fe6ca486c0031101f15c787a84c39c419840b914ae0c829c95bd4095ec37a08'
    old_text = original.decode('utf-8')
    old_tree = ast.parse(old_text)
    text, tree = texts['compare_capture25.py'], trees['compare_capture25.py']
    assert (HERE / 'pcm_metrics.py').read_bytes() == (BASE / 'pcm_metrics.py').read_bytes()
    assert (HERE / 'policy25.py').read_bytes() == (BASE / 'policy25.py').read_bytes()
    assert sha((HERE / 'pcm_metrics.py').read_bytes()) == 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
    assert sha((HERE / 'policy25.py').read_bytes()) == '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'
    template = trees['prepare_adapter.py']
    pins = literal(template, 'PINS')
    function_text = literal(template, 'PLATFORM_FUNCTION')
    assert definition(text, tree, 'c3_platform') == function_text.strip()
    assert literal(tree, 'SDK_REVISION') == '9a97f6c54ec638111ce55cd36581b3c192f15207'
    runtime_inputs = {}
    for name, (path, expected) in pins.items():
        assert fact(RUNTIME / path)['sha256'] == literal(tree, name) == expected, name
        runtime_inputs[name] = fact(RUNTIME / path)
    immutable = ('sha', 'relative', 'Inputs', 'complete_capture', 'wav_pcm', 'frame_checksums')
    for name in immutable:
        assert definition(old_text, old_tree, name) == definition(text, tree, name), name
    expected_run = definition(old_text, old_tree, 'run')
    expected_run = replace_one(expected_run, '    complete_capture(target)\n',
        "    complete_capture(target)\n    need((target.get('platform'), target.get('sdk_revision'), target.get('elf_machine'),\n          target.get('coordinator_core'), target.get('worker_core')) ==\n         ('esp32c3', SDK_REVISION, 243, 0, 0), 'Only reviewed C3 capture platform supported')\n")
    anchor = "    inputs.read('target/controller', target_root / 'sources/helpers/run.py', RUNNER)\n"
    expected_run = replace_one(expected_run, anchor,
        "    result['target_platform'] = c3_platform(inputs, target_root, target)\n    result['target_platform_verified'] = True\n" + anchor)
    assert expected_run == definition(text, tree, 'run')
    expected_main = replace_one(definition(old_text, old_tree, 'main'),
        "    result = dict(result='INCOMPLETE',checked_only=True,",
        "    result = dict(result='INCOMPLETE',target_platform_verified=False,checked_only=True,")
    assert expected_main == definition(text, tree, 'main')
    expected = old_text
    for name in ('RUNNER', 'PROTOCOL', 'CALLER'):
        expected = replace_one(expected, name + ' = ' + repr(literal(old_tree, name)),
                               name + ' = ' + repr(literal(tree, name)))
    expected = replace_one(expected, 'import sys\n', 'import struct\nimport sys\n')
    expected = replace_one(expected, 'sys.dont_write_bytecode = True\n',
        "sys.dont_write_bytecode = True\nSDK_REVISION = '9a97f6c54ec638111ce55cd36581b3c192f15207'\n")
    expected = replace_one(expected, 'def wav_pcm(data, rate, frames):', function_text + 'def wav_pcm(data, rate, frames):')
    expected = replace_one(expected, definition(old_text, old_tree, 'run'), expected_run)
    expected = replace_one(expected, definition(old_text, old_tree, 'main'), expected_main)
    assert expected == text, 'Only declared source changes allowed'
    assert literal(tree, 'SCOPE_PINS') == literal(old_tree, 'SCOPE_PINS')
    assert literal(tree, 'COMMANDS') == literal(old_tree, 'COMMANDS')
    contract = json.loads((RUNTIME / 'contract.json').read_bytes())
    model = contract['model']
    assert contract['contract_sha256'] == literal(tree, 'CONTRACT')
    assert (len(model['cases']), model['total_packets'], model['total_pcm'], model['case_mask']) == (25, 350, 623360, 33554431)
    assert tuple(case['id'] for case in model['cases']) == literal(trees['policy25.py'], 'CASE_IDS')
    assert literal(tree, 'METRICS') == sha((HERE / 'pcm_metrics.py').read_bytes())
    assert literal(tree, 'POLICY25') == sha((HERE / 'policy25.py').read_bytes())
    diff = ''.join(difflib.unified_diff(old_text.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile='cyd-numeric-prep01/compare_capture25.py', tofile='c3-numeric-prep01/compare_capture25.py'))
    assert (HERE / 'adapter-adaptation.diff').read_bytes() == diff.encode('utf-8')
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    assert relation['original_adapter'] == fact(BASE / 'compare_capture25.py')
    assert relation['adapted_adapter'] == fact(HERE / 'compare_capture25.py')
    assert relation['runtime_inputs'] == runtime_inputs
    assert relation['byte_identical_modules'] == {name: fact(HERE / name) for name in ('pcm_metrics.py', 'policy25.py')}
    names = (*py_names, 'README.md', 'source-relation.json', 'adapter-adaptation.diff', 'terminal-records.json')
    inputs = {name: fact(HERE / name) for name in names}
    report = dict(schema='c3-expanded25-numeric-source-closure-v1', scope='AST_HASH_SOURCE_ONLY', source_only=True,
        prepared_adapter_imported_or_executed=False, metric_or_policy_executed=False, protocol_executed=False,
        actual_PCM_or_target_campaign_read=False, SDK_compiler_QEMU_reference_tests_Git_executed=False,
        immutable_definitions=list(immutable), exact_permitted_adapter_diff_verified=True,
        metrics_and_policy_byte_identical=True, exact_cases=25, packets=350, expected_pcm_bytes=623360, events=778,
        actual_C3_runtime_result_claimed=False, source_setup_identity_bound_dynamically_to_target_report=True,
        assumed_CYD_binary_equivalence=False, runtime_inputs=runtime_inputs, inputs=inputs)
    write_json('source-closure.json', report)
    write_json('readiness.json', dict(schema='c3-expanded25-numeric-readiness-v1', source_only=True,
        ready_for_root_review=True, actual_runtime_qualified=False,
        closure=fact(HERE / 'source-closure.json'), inputs=inputs))
    print(json.dumps(dict(source_only=True, adapter=inputs['compare_capture25.py'],
                         closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
