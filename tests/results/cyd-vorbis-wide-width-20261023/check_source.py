"""AST/hash/recorded metadata closure only; never execute packer/verifier or payloads."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-floor0-equivalent-archive-prep-01'


def sha(data): return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    node = next(node for node in tree.body if isinstance(node, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return ast.literal_eval(node.value)


def create_json(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    trees = {path.name: ast.parse(path.read_bytes().decode('utf-8'), filename=str(path)) for path in HERE.glob('*.py')}
    assert sha((BASE / 'pack.py').read_bytes()) == '88748321cc70262e3986147559ed81d5451218c81f786dd89ce04e6264603bb3'
    assert sha((BASE / 'verify.py').read_bytes()) == '28d51642ba0e1637bea67e5bb6fef1c4c8ba788fae2cb8523fb9e12893acaba2'
    assert (HERE / 'dependency.py').read_bytes() == (BASE / 'dependency.py').read_bytes()
    assert sha((HERE / 'dependency.py').read_bytes()) == '00ada1774a46a9dcf40602bd341b23686e49acc1bf02c1c793de5cca10227892'
    for name in ('pack.py', 'verify.py'):
        old, new = (BASE / name).read_bytes().decode(), (HERE / name).read_bytes().decode()
        expected = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
            fromfile='floor31-archive/' + name, tofile='width12-archive/' + name)).encode()
        assert (HERE / (name[:-3] + '-adaptation.diff')).read_bytes() == expected
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    assert relation['source_inputs'] == {name: fact(HERE / name) for name in ('pack.py', 'verify.py', 'dependency.py')}
    plan = json.loads((HERE / 'plan.template.json').read_bytes())
    assert set(plan['roles']) == set(literal(trees['pack.py'], 'ROLES')) == {'capture12', 'numeric12', 'host-new12'}
    assert [plan['roles'][name]['expected_outer_exit'] for name in ('capture12', 'numeric12', 'host-new12')] == [0, 1, 1]
    for row in plan['roles'].values():
        assert sha((ROOT / row['path'] / 'report.json').read_bytes()) == row['report_sha256']
        assert sha((ROOT / row['terminal']).read_bytes()) == row['terminal_sha256']
    for path in plan['trees']:
        assert (ROOT / path).is_dir()
    for path in plan['extras']:
        assert (ROOT / path).is_file()
    for path in plan['extra_receipts']:
        assert sha((ROOT / path).read_bytes()) == plan['extra_receipt_pins'][path]
    checkpoint = ROOT / plan['checkpoint']['path']
    assert sha(checkpoint.read_bytes()) == plan['checkpoint']['sha256']
    dep_manifest = ROOT / 'tests/results/cyd-vorbis-map2-20261020/manifest.json'
    assert sha(dep_manifest.read_bytes()) == plan['dependency_manifest_sha256'] == 'c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c'
    declared = set(literal(trees['pack.py'], 'SELF'))
    existing = {path.name for path in HERE.iterdir() if path.is_file()}
    assert declared == existing | {'readiness.json', 'source-closure.json'}
    inputs = [fact(path) for path in sorted(HERE.iterdir()) if path.is_file()]
    closure = dict(schema='wide-width12-archive-source-closure-v1', source_only=True,
        scope='AST_HASH_RECORDED_JSON_AND_CHECKPOINT_METADATA_ONLY',
        packer_or_verifier_imported_or_executed=False, actual_PCM_read_or_compared=False,
        decoder_reference_SDK_compiler_QEMU_tests_Git_device_executed=False,
        exact_SELF_inventory_verified=True, local_source_files=len(declared),
        actual_data_dependency_only='tests/results/cyd-vorbis-map2-20261020', old31_supplemental_record_replayed=False,
        numerical_tolerance_changed=False, source_statuses_reclassified=False,
        actual_archive_result_claimed=False, inputs=inputs)
    create_json('source-closure.json', closure)
    create_json('readiness.json', dict(schema='wide-width12-archive-readiness-v1', source_only=True,
        ready_for_root_review=True, root_owns_all_execution_copy_and_Git=True,
        source_closure=fact(HERE / 'source-closure.json'), inputs=inputs))
    print(json.dumps(dict(source_only=True, pack=fact(HERE / 'pack.py'), verifier=fact(HERE / 'verify.py'),
        closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
