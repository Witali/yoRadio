"""AST/hash/read-only source closure; never execute packers, verifiers or payloads."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-map2-archive-prep-03'


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def create_json(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    expected = {'pack.py': '404b541ad58d62499166a1711d95beef73060b3d2fa31ca8bdc6d20d7d2f7722',
                'verify.py': '74afcd06807e0377e0645069bdc1667ca0674aa1523139678fa27562c12059f4'}
    base_inputs = {name: fact(BASE / name) for name in expected}
    for name, digest in expected.items():
        assert base_inputs[name]['sha256'] == digest
    names = ('pack.py', 'verify.py', 'dependency.py', 'check_source.py')
    for name in names:
        ast.parse((HERE / name).read_bytes().decode('utf-8'), filename=name)
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    assert relation['base_inputs'] == base_inputs
    for name in ('pack.py', 'verify.py'):
        old, new = (BASE / name).read_bytes().decode('utf-8'), (HERE / name).read_bytes().decode('utf-8')
        diff = ''.join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile='cyd-archive-prep03/' + name, tofile='c3-archive-prep01/' + name))
        assert (HERE / (name[:-3] + '-adaptation.diff')).read_bytes() == diff.encode('utf-8')
        assert relation['adapted_inputs'][name] == fact(HERE / name)
    assert relation['adapted_inputs']['dependency.py'] == fact(HERE / 'dependency.py')
    plan = json.loads((HERE / 'plan.template.json').read_bytes())
    assert set(plan['roles']) == {'baseline', 'acceptance', 'numeric'}
    assert [plan['roles'][name]['expected_outer_exit'] for name in ('baseline', 'acceptance', 'numeric')] == [1, 0, 1]
    assert plan['dependency_manifest_sha256'] == 'c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c'
    dependency_manifest = ROOT / 'tests/results/cyd-vorbis-map2-20261020/manifest.json'
    assert fact(dependency_manifest)['sha256'] == plan['dependency_manifest_sha256']
    dependency = json.loads(dependency_manifest.read_bytes())
    assert set(('host-old17', 'host-new8', 'capture25', 'numeric-expanded25')) <= set(dependency['roles'])
    # Source/metadata inspection only. Actual campaign logs/PCM and stored
    # reference blobs remain unread by this check.
    all_names = (*names, 'README.md', 'plan.template.json', 'source-relation.json',
                 'pack-adaptation.diff', 'verify-adaptation.diff')
    inputs = {name: fact(HERE / name) for name in all_names}
    closure = dict(schema='c3-map2-archive-source-closure-v1', source_only=True,
        scope='AST_HASH_SOURCE_AND_COMMITTED_MANIFEST_METADATA_ONLY',
        packer_or_verifier_imported_or_executed=False, prepared_protocol_metric_policy_executed=False,
        actual_payload_PCM_read=False, SDK_compiler_QEMU_reference_tests_Git_executed=False,
        base_inputs=base_inputs, inputs=inputs, explicit_dependency_manifest=fact(dependency_manifest),
        exact_scope_roles=['baseline', 'acceptance', 'numeric'],
        actual_archive_or_offline_verification_result_claimed=False)
    create_json('source-closure.json', closure)
    create_json('readiness.json', dict(schema='c3-map2-archive-readiness-v1', source_only=True,
        ready_for_root_review=True, root_owns_all_execution_and_promotion=True,
        source_closure=fact(HERE / 'source-closure.json'), inputs=inputs))
    print(json.dumps(dict(source_only=True, pack=fact(HERE / 'pack.py'), verify=fact(HERE / 'verify.py'),
        closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
