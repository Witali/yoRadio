"""Create LF-normalizing numeric source successor without running prepared code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('c3-vorbis-format-expanded25-numeric-prep-01')
OLD_ADAPTER = '0454f4c7fa2cc52a0bdd3f38899b180afb934356b66f0ade438917d10d052a5f'
OLD_CLOSURE = 'db9e910705fcac0c6f42a26ef0b3476b9ca5f4b800d50c943f4683839ebfc8cd'
OLD_READINESS = 'ecf8b2a02be6c47d518c68da9e81698d6960742dd12b09baeae21b10451d2fb2'
MODULES = {'pcm_metrics.py': 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f',
           'policy25.py': '32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6'}
OLD_LINE = "                         command['stdout_sha256']).decode()\n"
NEW_LINE = "                         command['stdout_sha256']).decode().replace('\\r\\n', '\\n')\n"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def create(name, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    with (HERE / name).open('xb') as stream:
        stream.write(data)


def main():
    old_inputs = {name: fact(OLD / name) for name in (
        'compare_capture25.py', 'pcm_metrics.py', 'policy25.py', 'source-closure.json',
        'readiness.json', 'source-relation.json', 'README.md')}
    assert old_inputs['compare_capture25.py']['sha256'] == OLD_ADAPTER
    assert old_inputs['source-closure.json']['sha256'] == OLD_CLOSURE
    assert old_inputs['readiness.json']['sha256'] == OLD_READINESS
    old = (OLD / 'compare_capture25.py').read_bytes().decode('utf-8')
    assert old.count(OLD_LINE) == 1
    new = old.replace(OLD_LINE, NEW_LINE, 1)
    ast.parse(old)
    ast.parse(new)
    create('compare_capture25.py', new)
    copied = {}
    for name, expected in MODULES.items():
        data = (OLD / name).read_bytes()
        assert sha(data) == expected
        create(name, data)
        copied[name] = fact(HERE / name)
    diff = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile='c3-numeric-prep01/compare_capture25.py', tofile='c3-numeric-prep02/compare_capture25.py'))
    create('adapter-revision02.diff', diff)
    parent_relation = json.loads((OLD / 'source-relation.json').read_bytes())
    relation = dict(schema='c3-expanded25-numeric-source-relation-v2', source_only=True,
        sole_functional_change='Normalize CRLF macro text to LF before existing anchored regex checks',
        adapter_imported_or_executed=False, metric_or_policy_executed=False,
        actual_PCM_or_target_campaign_read=False, runtime_or_test_executed=False,
        parent_inputs=old_inputs, adapted_adapter=fact(HERE / 'compare_capture25.py'),
        byte_identical_modules=copied, runtime_inputs=parent_relation['runtime_inputs'],
        original_dual_reference_scopes_unchanged=True, exact_cases=25, packets=350,
        expected_pcm_bytes=623360, events=778, metric_bound=2, optional_bound_default=None,
        root_observed_issue=dict(source='Parent root message', terminal_chunk_id='e286b5',
            macro_log_LF=1589, macro_log_CRLF=1589, actual_log_read_here=False),
        parent_sources_immutable=True, root_owns_all_actual_campaigns=True)
    create('source-relation.json', json.dumps(relation, indent=2) + '\n')
    for name, row in old_inputs.items():
        assert fact(OLD / name) == row
    print(json.dumps(dict(source_only=True, adapter=relation['adapted_adapter'],
                         sole_functional_change=relation['sole_functional_change'])))


if __name__ == '__main__':
    main()
