"""Source-only AST, raw hash and recorded metadata closure; never run proposed code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.build/cyd-vorbis-owned-book-archive-prep-02'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    node = next(node for node in tree.body if isinstance(node, ast.Assign) and
        any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return ast.literal_eval(node.value)


def write_new(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    trees = {path.name: ast.parse(path.read_bytes().decode('utf-8'), filename=str(path))
             for path in HERE.glob('*.py')}
    relation = json.loads((HERE / 'source-relation.json').read_bytes())
    assert relation['source_only'] is True
    assert relation['source_inputs'] == {name: fact(HERE / name) for name in ('pack.py', 'verify.py')}
    assert relation['base_inputs'] == {name: fact(BASE / name) for name in ('pack.py', 'verify.py')}
    for name in ('pack.py', 'verify.py'):
        before, after = (BASE / name).read_bytes().decode(), (HERE / name).read_bytes().decode()
        expected = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile='owned-book-archive02/' + name, tofile='owned-floor0-archive01/' + name))
        assert (HERE / (name[:-3] + '-adaptation.diff')).read_bytes() == expected.encode()
    plan_raw = (HERE / 'plan.json').read_bytes()
    plan = json.loads(plan_raw)
    assert sha(plan_raw) == literal(trees['pack.py'], 'PLAN_SHA') == literal(trees['verify.py'], 'PLAN')
    assert plan['archive_data_dependencies'] == []
    assert [row['role'] for row in plan['roles']] == ['failed01', 'acceptance02']
    assert [row['expected_exit_code'] for row in plan['roles']] == [1, 0]
    for prep in plan['preparations']:
        directory = Path(prep['path'])
        index_raw = (directory / prep['index']).read_bytes()
        assert sha(index_raw) == prep['index_sha256']
        index = json.loads(index_raw)
        actual = {path.relative_to(directory).as_posix() for path in directory.rglob('*') if path.is_file()}
        assert actual == set(index['files']) | {prep['index']}
        for name, item in index['files'].items():
            data = (directory / name).read_bytes()
            assert len(data) == item['bytes'] and sha(data) == item['sha256']
    for role in plan['roles']:
        report_raw = (Path(role['path']) / 'report.json').read_bytes()
        terminal_raw = Path(role['terminal_path']).read_bytes()
        assert sha(report_raw) == role['report_sha256'] and sha(terminal_raw) == role['terminal_sha256']
        report, terminal = json.loads(report_raw), json.loads(terminal_raw)
        assert terminal['report_sha256'] == sha(report_raw) and terminal['exit_code'] == role['expected_exit_code']
        assert terminal['session_id'] == role['expected_session_id'] and terminal['terminal_chunk_id'] == role['expected_terminal_chunk']
        assert report['result'] == role['expected_result']
    checkpoint = Path(plan['checkpoint']['path'])
    assert sha(checkpoint.read_bytes()) == plan['checkpoint']['sha256']
    prep02 = ROOT / '.build/cyd-vorbis-owned-floor0-unit-prep-02'
    for name in ('protocol.py', 'fixture_bits.py', 'fixture_reader.py'):
        assert (HERE / name).read_bytes() == (prep02 / name).read_bytes()
    declared = set(literal(trees['pack.py'], 'SELF'))
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    assert declared == actual | {'source-checks.json', 'readiness.json'}
    inputs = {path.name: fact(path) for path in sorted(HERE.iterdir()) if path.is_file()}
    write_new('source-checks.json', dict(schema='owned-floor0-archive-source-checks-v1', source_only=True,
        allowed_scope='AST_RAW_HASH_RECORDED_METADATA_ONLY', inputs=inputs,
        packer_verifier_reader_protocol_tests_compiler_SDK_QEMU_decoder_Git_device_executed=False,
        exact_SELF_file_count=len(declared), actual_archive_result_claimed=False))
    files = {path.name: dict(bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
             for path in sorted(HERE.iterdir()) if path.is_file()}
    write_new('readiness.json', dict(schema='owned-floor0-archive-readiness-v1', source_only=True,
        ready_for_root_review=True, root_owns_actual_execution_promotion_and_Git=True,
        actual_archive_result_claimed=False, files=files))
    assert {path.name for path in HERE.iterdir() if path.is_file()} == declared
    print(json.dumps(dict(source_only=True, pack=fact(HERE / 'pack.py'), verify=fact(HERE / 'verify.py'),
        source_checks=fact(HERE / 'source-checks.json'), readiness=fact(HERE / 'readiness.json'),
        exact_SELF_file_count=len(declared))))


if __name__ == '__main__':
    main()
