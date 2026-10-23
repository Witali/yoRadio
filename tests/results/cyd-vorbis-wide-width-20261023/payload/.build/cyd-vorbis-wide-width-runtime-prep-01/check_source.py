"""AST/hash/metadata-only source closure; never import qualifier/materializer/runtime."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE25 = ROOT / '.build/cyd-vorbis-format-expanded25-prep-02'
BASE31 = ROOT / '.build/cyd-vorbis-format-expanded31-prep-01'


def sha(data): return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(HERE).as_posix(), bytes=len(data), sha256=sha(data))


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
    py_files = [path for path in HERE.rglob('*.py')]
    trees = {path.relative_to(HERE).as_posix(): ast.parse(path.read_bytes().decode('utf-8'), filename=str(path))
             for path in py_files}
    assert sha((HERE / 'qualify.py').read_bytes()) == '4549ae75b4ef127504425dfe936997c53cb428de2fced6bf2e555bcdda4b8ebc'
    assert sha((HERE / 'pins.json').read_bytes()) == '4da23aa4fe0810c9cc4dbd0d896e42cc3025863f14bafd558e9d7702f7bcc3f5'
    assert sha((HERE / 'carrier.py').read_bytes()) == '6cf4f49de61cf94184578fe753272606b1ef8e0225b1444ede4c73d4c549712b'
    assert (HERE / 'protocol.py').read_bytes() == (BASE25 / 'protocol.py').read_bytes()
    assert sha((HERE / 'protocol.py').read_bytes()) == '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
    assert (HERE / 'windows_compile_command.py').read_bytes() == (BASE25 / 'windows_compile_command.py').read_bytes()
    project = HERE / 'target/cyd_vorbis_wide_width12_qemu'
    assert sha((project / 'main/main.c').read_bytes()) == '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
    assert sha((project / 'main/corpus_case.h').read_bytes()) == '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
    old_template = ast.parse((BASE31 / 'controller.template.py').read_bytes().decode('utf-8'))
    new_template = trees['controller.template.py']
    for name in ('save', 'freeze', 'current', 'execute'):
        old = [node for node in ast.walk(old_template) if isinstance(node, ast.FunctionDef) and node.name == name]
        new = [node for node in ast.walk(new_template) if isinstance(node, ast.FunctionDef) and node.name == name]
        assert len(old) == len(new) == 1 and ast.dump(old[0], include_attributes=False) == ast.dump(new[0], include_attributes=False)
    proof = next(node.value for node in new_template.body if isinstance(node, ast.Assign) and
                 any(isinstance(target, ast.Name) and target.id == 'REFERENCE_PROOFS' for target in node.targets))
    assert isinstance(proof, ast.Name) and proof.id == '__REFERENCE_PROOFS__'
    assert not (HERE / 'run-cyd-vorbis-wide-width12-qemu.py').exists()
    for name in ('QUALIFIER_SHA', 'QUALIFIER_PINS_SHA'):
        assert literal(trees['prepare_runtime.py'], name) == sha((HERE / ('qualify.py' if name == 'QUALIFIER_SHA' else 'pins.json')).read_bytes())
    inputs = json.loads((HERE / 'source-inputs.json').read_bytes())
    for row in inputs['files']:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    assert (len(inputs['expected_case_ids']) == 12 and len(inputs['expected_equal_groups']) == 4 and
            all(len(group) == 3 for group in inputs['expected_equal_groups']))
    for old, new, diff, old_label, new_label in (
        (BASE31 / 'controller.template.py', HERE / 'controller.template.py', 'controller-adaptation.diff', 'expanded31/controller.template.py', 'wide-width12/controller.template.py'),
        (BASE31 / 'materialize.py', HERE / 'materialize.py', 'materializer-adaptation.diff', 'expanded31/materialize.py', 'wide-width12/materialize.py')):
        expected = ''.join(difflib.unified_diff(old.read_bytes().decode().splitlines(True), new.read_bytes().decode().splitlines(True),
            fromfile=old_label, tofile=new_label)).encode()
        assert (HERE / diff).read_bytes() == expected
    files = [fact(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
    closure = dict(schema='wide-width12-runtime-source-closure-v1', source_only=True,
        scope='AST_HASH_AND_RECORDED_JSON_METADATA_ONLY',
        qualifier_materializer_protocol_runtime_imported_or_executed=False,
        decoder_reference_SDK_compiler_QEMU_tests_Git_device_executed=False,
        actual_PCM_read_or_compared=False, actual_qualification_not_run_by_this_agent=True, phase_B_materialization_pending=True,
        unchanged_caller_protocol_and_runtime_helper_AST=True,
        runnable_controller_unavailable_until_actual_reviewed_qualifier_terminal0=True,
        required_derived_counts=dict(cases=12, packets=168, expected_pcm_bytes=337920, protocol_events=375, case_mask=4095,
            arrays=60, full_raw_arrays=36), files=files)
    create_json('source-closure.json', closure)
    ready_files = files + [fact(HERE / 'source-closure.json')]
    create_json('readiness.json', dict(schema='wide-width12-runtime-source-readiness-v1', source_only=True,
        ready_for_root_review=True, actual_runtime_qualified=False,
        root_owns_both_execution_phases=True, files=ready_files))
    print(json.dumps(dict(source_only=True, qualifier=fact(HERE / 'qualify.py'), preparer=fact(HERE / 'prepare_runtime.py'),
        template=fact(HERE / 'controller.template.py'), closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
