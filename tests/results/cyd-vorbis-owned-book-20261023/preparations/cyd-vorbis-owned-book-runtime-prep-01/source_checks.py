"""Source-only AST, immutable raw origin and revision preparation; never run unit."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output = HERE / 'source-checks.json'
    manifest = HERE / 'readiness.json'
    if output.exists() or manifest.exists():
        raise RuntimeError('Preserve the source-only preparation receipts')
    scripts = [HERE / name for name in ('run-owned-book-unit.py', 'owned_qmp.py', 'source_checks.py',
                                        'protocol.py', 'windows_compile_command.py')]
    for path in scripts:
        ast.parse(path.read_bytes(), filename=path.name)
    origins = json.loads((HERE / 'source-origins.json').read_bytes())
    for item in origins['inputs']:
        original, copied = Path(item['source']), HERE / item['snapshot']
        assert original.stat().st_size == copied.stat().st_size == item['bytes']
        assert sha(original) == sha(copied) == item['sha256']
    before, after = HERE / 'unit-source/project', HERE / 'project'
    differences = []
    changed = []
    names = {p.relative_to(base).as_posix() for base in (before, after) for p in base.rglob('*') if p.is_file()}
    for name in sorted(names):
        old, new = before / name, after / name
        old_data, new_data = old.read_bytes() if old.exists() else b'', new.read_bytes() if new.exists() else b''
        if old_data != new_data:
            changed.append(name)
            differences.extend(difflib.unified_diff(old_data.decode().splitlines(True), new_data.decode().splitlines(True),
                fromfile='unit-source/project/' + name, tofile='project/' + name))
    assert set(changed) == {'main/CMakeLists.txt', 'sdkconfig.defaults', 'partitions.csv', 'sdk-build.ps1'}
    (HERE / 'project-revision.diff').write_text(''.join(differences), encoding='utf-8', newline='')
    for old_name, new_name, destination in (
        ('predecessor/sdk-build.ps1', 'project/sdk-build.ps1', 'launcher-revision.diff'),
        ('predecessor/controller.py', 'run-owned-book-unit.py', 'controller-revision.diff')):
        old, new = HERE / old_name, HERE / new_name
        raw = ''.join(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True),
            fromfile=old_name, tofile=new_name))
        (HERE / destination).write_text(raw, encoding='utf-8', newline='')
    for name in ('main/book_unit.c', 'main/unit_data.h', 'main/pinned/production/vorbis_repair/setup.c',
                 'main/pinned/production/vorbis_repair_abi.h'):
        assert (before / name).read_bytes() == (after / name).read_bytes()
    assert (HERE / 'protocol.py').read_bytes() == (HERE / 'unit-source/protocol.py').read_bytes()
    assert (HERE / 'fixture-contract.json').read_bytes() == (HERE / 'unit-source/fixture-contract.json').read_bytes()
    assert not list(after.rglob('*.a'))
    ps = json.loads((HERE / 'powershell-source-ast.json').read_text(encoding='utf-8-sig'))
    assert ps['parser_errors'] == [] and ps['SDK_or_launcher_executed'] is False
    assert ps['script_sha256'] == sha(after / 'sdk-build.ps1')
    result = dict(schema='owned-book-runtime-source-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(scripts), raw_original_files_unchanged=len(origins['inputs']),
        changed_runtime_project_files=changed, contract_sha256=sha(HERE / 'fixture-contract.json'),
        production_setup_sha256=sha(after / 'main/pinned/production/vorbis_repair/setup.c'),
        ABI_sha256=sha(after / 'main/pinned/production/vorbis_repair_abi.h'),
        unit_sha256=sha(after / 'main/book_unit.c'), protocol_sha256=sha(HERE / 'protocol.py'),
        source_scope='actual production parser plus existing bounded public consumer; no vendor backend',
        cases=16, active_codewords=59, vector_probes=61, prospective_protocol_events=97,
        SDK_compiler_QEMU_unit_tests_decoder_or_reference_executed=False, runtime_executed=False,
        protocol_synthetic_tests_executed=False, C_compile_link_or_unit_execution_qualified=False,
        actual_terminal_facts_available=False, canonical_Git_archives_or_campaigns_modified=False,
        full_G6_qualified=False)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    manifest.write_text(json.dumps(dict(schema='owned-book-runtime-source-only-readiness-v1',
        runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(manifest),
                         C_compile_link_or_unit_execution_qualified=False)))


if __name__ == '__main__':
    main()
