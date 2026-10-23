"""AST/raw-hash/recorded metadata closure only; never import proposed helpers."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-wide-width-runtime-prep-01'
PROJECT = 'target/cyd_vorbis_more_singletons8_qemu'
EXPECTED_ROOT = {
    'carrier.py', 'qualify.py', 'pins.json', 'qualifier-adaptation.diff', 'phaseA-readiness.json',
    'protocol.py', 'windows_compile_command.py', 'materialize.py', 'controller.template.py',
    'prepare_runtime.py', 'source-inputs.json', 'reference_binding.py', 'README.md',
    'materializer-adaptation.diff', 'controller-adaptation.diff', 'preparer-adaptation.diff',
    'binding-adaptation.diff', 'source-relation.json', 'check_source.py', 'source-closure.json', 'readiness.json'}
EXPECTED_PROJECT = {'CMakeLists.txt', 'sdkconfig.defaults', 'sdk-build.ps1', 'partitions.csv',
    'raw-enable.cmake', 'main/CMakeLists.txt', 'main/Kconfig.projbuild', 'main/data.h',
    'main/main.c', 'main/corpus_case.h'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(HERE).as_posix(), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    rows = [node for node in tree.body if isinstance(node, ast.Assign) and
        any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(rows) == 1, name
    return ast.literal_eval(rows[0].value)


def write_new(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    trees = {path.relative_to(HERE).as_posix(): ast.parse(path.read_bytes().decode('utf-8'), filename=str(path))
             for path in HERE.rglob('*.py')}
    phaseA = json.loads((HERE / 'phaseA-readiness.json').read_bytes())
    for row in phaseA['files'].values():
        path = ROOT / row['path']
        assert len(path.read_bytes()) == row['bytes'] and sha(path.read_bytes()) == row['sha256']
    for name in ('QUALIFIER_SHA', 'QUALIFIER_PINS_SHA'):
        path = HERE / ('qualify.py' if name == 'QUALIFIER_SHA' else 'pins.json')
        assert literal(trees['prepare_runtime.py'], name) == sha(path.read_bytes())
    for name in ('protocol.py', 'windows_compile_command.py', 'carrier.py'):
        assert (HERE / name).read_bytes() == (BASE / name).read_bytes()
    assert sha((HERE / 'protocol.py').read_bytes()) == '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
    assert sha((HERE / PROJECT / 'main/main.c').read_bytes()) == '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
    assert sha((HERE / PROJECT / 'main/corpus_case.h').read_bytes()) == '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
    for name in EXPECTED_PROJECT:
        assert (HERE / PROJECT / name).read_bytes() == (BASE / 'target/cyd_vorbis_wide_width12_qemu' / name).read_bytes()
    old_template = ast.parse((BASE / 'controller.template.py').read_bytes().decode())
    for name in ('save', 'freeze', 'current', 'execute'):
        before = [node for node in ast.walk(old_template) if isinstance(node, ast.FunctionDef) and node.name == name]
        after = [node for node in ast.walk(trees['controller.template.py']) if isinstance(node, ast.FunctionDef) and node.name == name]
        assert len(before) == len(after) == 1
        assert ast.dump(before[0], include_attributes=False) == ast.dump(after[0], include_attributes=False)
    proof = next(node.value for node in trees['controller.template.py'].body if isinstance(node, ast.Assign) and
        any(isinstance(target, ast.Name) and target.id == 'REFERENCE_PROOFS' for target in node.targets))
    assert isinstance(proof, ast.Name) and proof.id == '__REFERENCE_PROOFS__'
    assert not (HERE / 'run-cyd-vorbis-more-singletons8-qemu.py').exists()
    inputs = json.loads((HERE / 'source-inputs.json').read_bytes())
    for row in inputs['files']:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    matrix = json.loads((ROOT / inputs['reference']['comparison']['path']).read_bytes())
    assert inputs['expected_case_ids'] == [row['id'] for row in matrix['cases']]
    assert inputs['expected_equal_groups'] == matrix['expected_same_decoder_pcm_equal_groups']
    assert inputs['expected_different_pairs'] == matrix['expected_same_decoder_pcm_different_pairs']
    assert len(inputs['expected_case_ids']) == 8 and len(inputs['expected_equal_groups']) == 2
    assert len(inputs['expected_different_pairs']) == 4
    for source, diff in (('qualify.py','qualifier-adaptation.diff'), ('materialize.py','materializer-adaptation.diff'),
        ('controller.template.py','controller-adaptation.diff'), ('prepare_runtime.py','preparer-adaptation.diff'),
        ('reference_binding.py','binding-adaptation.diff')):
        expected = ''.join(difflib.unified_diff((BASE / source).read_bytes().decode().splitlines(True),
            (HERE / source).read_bytes().decode().splitlines(True), fromfile='wide12/' + source, tofile='singletons8/' + source))
        assert (HERE / diff).read_bytes() == expected.encode()
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    for name, row in relation['source_inputs'].items():
        assert fact(HERE / name) == row
    expected = EXPECTED_ROOT | {PROJECT + '/' + name for name in EXPECTED_PROJECT}
    actual = {path.relative_to(HERE).as_posix() for path in HERE.rglob('*') if path.is_file()}
    assert expected == actual | {'source-closure.json', 'readiness.json'}
    files = [fact(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
    write_new('source-closure.json', dict(schema='more-singletons8-runtime-source-closure-v1', source_only=True,
        allowed_scope='AST_RAW_HASH_RECORDED_METADATA_ONLY', files=files, source_inventory_count=len(expected),
        qualifier_materializer_binder_protocol_runtime_tests_reference_SDK_compiler_QEMU_Git_device_executed=False,
        actual_PCM_read_or_compared=False, phaseA_sources_unchanged=True, complete_project_byte_identical=True,
        caller_protocol_and_runtime_helper_AST_unchanged=True,
        runnable_controller_unavailable_until_actual_reviewed_qualifier_terminal0=True,
        required_derived_counts=dict(cases=8, packets=112, expected_pcm_bytes=225280, protocol_events=251,
            case_mask=255, arrays=40, full_raw_arrays=24),
        native_lookup2_refusals=4, native_packet_decode_failures=4, native_cause_diagnosed=False,
        actual_target_qualified=False))
    ready_files = files + [fact(HERE / 'source-closure.json')]
    write_new('readiness.json', dict(schema='more-singletons8-runtime-source-readiness-v1', source_only=True,
        ready_for_root_review=True, root_owns_both_execution_phases=True,
        actual_runtime_qualified=False, files=ready_files))
    assert {path.relative_to(HERE).as_posix() for path in HERE.rglob('*') if path.is_file()} == expected
    print(json.dumps(dict(source_only=True, preparer=fact(HERE / 'prepare_runtime.py'),
        binder=fact(HERE / 'reference_binding.py'), materializer=fact(HERE / 'materialize.py'),
        template=fact(HERE / 'controller.template.py'), closure=fact(HERE / 'source-closure.json'),
        readiness=fact(HERE / 'readiness.json'), exact_inventory_count=len(expected))))


if __name__ == '__main__':
    main()
