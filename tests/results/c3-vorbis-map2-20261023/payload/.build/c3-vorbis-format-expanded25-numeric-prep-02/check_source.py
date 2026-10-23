"""Source/AST/hash closure only; no prepared adapter, runtime, test or PCM execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('c3-vorbis-format-expanded25-numeric-prep-01')


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def literal(tree, name):
    nodes = [node for node in tree.body if isinstance(node, ast.Assign) and
             any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(nodes) == 1, name
    return ast.literal_eval(nodes[0].value)


def create_json(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    for name, row in relation['parent_inputs'].items():
        assert fact(OLD / name) == row, name
    assert fact(OLD / 'compare_capture25.py')['sha256'] == '0454f4c7fa2cc52a0bdd3f38899b180afb934356b66f0ade438917d10d052a5f'
    old = (OLD / 'compare_capture25.py').read_bytes().decode('utf-8')
    new = (HERE / 'compare_capture25.py').read_bytes().decode('utf-8')
    old_line = "                         command['stdout_sha256']).decode()\n"
    new_line = "                         command['stdout_sha256']).decode().replace('\\r\\n', '\\n')\n"
    assert old.count(old_line) == 1
    assert old.replace(old_line, new_line, 1) == new
    diff = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile='c3-numeric-prep01/compare_capture25.py', tofile='c3-numeric-prep02/compare_capture25.py'))
    assert (HERE / 'adapter-revision02.diff').read_bytes() == diff.encode('utf-8')
    assert relation['adapted_adapter'] == fact(HERE / 'compare_capture25.py')
    modules = {'pcm_metrics.py': 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f',
               'policy25.py': '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'}
    for name, expected in modules.items():
        assert (HERE / name).read_bytes() == (OLD / name).read_bytes()
        assert fact(HERE / name)['sha256'] == expected
        assert relation['byte_identical_modules'][name] == fact(HERE / name)
    parsed = {}
    for name in ('compare_capture25.py', 'pcm_metrics.py', 'policy25.py', 'prepare_successor.py', 'check_source.py'):
        parsed[name] = ast.parse((HERE / name).read_bytes().decode('utf-8'), filename=name)
    tree = parsed['compare_capture25.py']
    runtime_facts = {}
    for name, row in relation['runtime_inputs'].items():
        assert fact(Path(row['path'])) == row
        assert literal(tree, name) == row['sha256']
        runtime_facts[name] = row
    assert literal(tree, 'RUNNER') == 'e00a30172c3b4291f080b2eee937214108adda7b6a03178e2f9833cb44d92034'
    assert literal(tree, 'PROTOCOL') == '961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba'
    assert literal(tree, 'CALLER') == '8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03'
    assert literal(tree, 'SDK_REVISION') == '9a97f6c54ec638111ce55cd36581b3c192f15207'
    old_tree = ast.parse(old)
    for name in ('SCOPE_PINS', 'COMMANDS', 'CONTRACT', 'METRICS', 'POLICY25'):
        assert literal(tree, name) == literal(old_tree, name)
    names = ('compare_capture25.py', 'pcm_metrics.py', 'policy25.py', 'prepare_successor.py', 'check_source.py',
             'README.md', 'source-relation.json', 'adapter-revision02.diff', 'terminal-records.json')
    inputs = {name: fact(HERE / name) for name in names}
    report = dict(schema='c3-expanded25-numeric-source-closure-v2', source_only=True, scope='AST_HASH_SOURCE_ONLY',
        prepared_adapter_imported_or_executed=False, metric_or_policy_executed=False,
        actual_PCM_or_target_campaign_read=False, runtime_tests_references_SDK_compiler_QEMU_Git_executed=False,
        parent_inputs_unchanged=True, one_line_only_functional_change_verified=True,
        sole_functional_change=relation['sole_functional_change'], metrics_and_policy_byte_identical=True,
        exact_cases=25, packets=350, expected_pcm_bytes=623360, events=778,
        old17_new8_bindings_unchanged=True, runtime_inputs=runtime_facts, inputs=inputs)
    create_json('source-closure.json', report)
    create_json('readiness.json', dict(schema='c3-expanded25-numeric-readiness-v2', source_only=True,
        ready_for_root_review=True, actual_runtime_qualified=False,
        closure=fact(HERE / 'source-closure.json'), inputs=inputs))
    print(json.dumps(dict(source_only=True, adapter=inputs['compare_capture25.py'],
        closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
