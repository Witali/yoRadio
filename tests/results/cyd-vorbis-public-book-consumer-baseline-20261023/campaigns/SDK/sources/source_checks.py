"""Source-only raw identities, JSON, AST/symtable and explicit diffs; no proposed imports."""
import ast
import builtins
import difflib
import hashlib
import json
from pathlib import Path
import symtable

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal(tree, name):
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    return ast.literal_eval(node.value)


def function(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def main():
    output, manifest = HERE / 'source-checks.json', HERE / 'readiness.json'
    if output.exists() or manifest.exists():
        raise RuntimeError('Preserve immutable source-only receipts')
    scripts = [p for p in HERE.rglob('*.py') if p.is_file()]
    trees = {p.relative_to(HERE).as_posix(): ast.parse(p.read_bytes(), filename=str(p)) for p in scripts}
    origins = json.loads((HERE / 'source-origins.json').read_bytes())
    assert origins['schema'] == 'public-book-consumer-runtime-source-origins-v1' and len(origins['inputs']) == 188
    assert len({row['snapshot'] for row in origins['inputs']}) == len(origins['inputs'])
    for row in origins['inputs']:
        original, copied = Path(row['source']), HERE / row['snapshot']
        assert copied.resolve().is_relative_to(HERE)
        assert original.stat().st_size == copied.stat().st_size == row['bytes'] and sha(original) == sha(copied) == row['sha256']
    controller = trees['run-public-book-consumer.py']
    for name, expected in literal(controller, 'PINS').items():
        assert sha(HERE / name) == expected
    assert literal(controller, 'TOOL_PINS') == literal(trees['predecessor/run-owned-book-unit.py'], 'TOOL_PINS')
    assert literal(controller, 'CONTRACT_FILE_SHA') == 'a50a9350ac681f58d18774455127714b8d2ce195430b873c746d7b2b79374c48'
    assert literal(controller, 'MODEL_SHA') == '92a9c6ba03892f6e6637b5e6cf5889e5cf0defe92e6d5357e40120acad66d8ff'
    assert literal(controller, 'RUNTIME_READINESS_SHA') == 'c5b554bc0df7c566742c0d9ceeb157fdf81116d93426c22e73adf04af9d8cc77'
    assert literal(controller, 'SOURCE_READINESS_SHA') == '6d009ae122974c4993ab88e8befc350f40077d9095d14e85f784c8a9ef40e6bc'
    for name in ('need', 'sha', 'dependency_paths', 'save', 'freeze', 'current', 'execute', 'bind_output', 'sdk_action'):
        assert ast.dump(function(controller, name), include_attributes=False) == ast.dump(function(trees['predecessor/run-owned-book-unit.py'], name), include_attributes=False)
    for new, old in [('windows_compile_command.py', 'predecessor/windows_compile_command.py'),
                     ('project/sdk-build.ps1', 'predecessor/sdk-build.ps1'),
                     ('protocol.py', 'unit-source/protocol.py'), ('oracle.py', 'unit-source/oracle.py')]:
        assert (HERE / new).read_bytes() == (HERE / old).read_bytes()
    source_readiness = json.loads((HERE / 'unit-source/readiness.json').read_bytes())
    assert {p.relative_to(HERE / 'unit-source').as_posix() for p in (HERE / 'unit-source').rglob('*') if p.is_file()} == set(source_readiness['expected_self_files'])
    for row in source_readiness['files']:
        path = HERE / 'unit-source' / row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
    runtime_readiness = json.loads((HERE / 'generated-runtime-readiness.json').read_bytes())
    assert len(runtime_readiness['files']) == 18 and runtime_readiness['source_readiness_sha256'] == literal(controller, 'SOURCE_READINESS_SHA')
    assert runtime_readiness['schema'] == 'public-book-consumer-generated-runtime-readiness-v1'
    assert all(runtime_readiness[k] is False for k in ('compiled', 'target_executed', 'host_executed'))
    for row in runtime_readiness['files']:
        path = HERE / row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
    project_members = {p.relative_to(HERE / 'project').as_posix() for p in (HERE / 'project').rglob('*') if p.is_file()}
    original_members = {row['path'][len('project/'):] for row in runtime_readiness['files'] if row['path'].startswith('project/')}
    assert project_members == original_members | {'sdk-build.ps1'}
    assert not any(p.suffix.lower() in ('.a', '.elf', '.exe', '.dll', '.o', '.obj') for p in HERE.rglob('*') if p.is_file())
    assert not any(p.suffix.lower() == '.bin' for p in (HERE / 'project').rglob('*') if p.is_file())
    model = json.loads((HERE / 'contract.json').read_bytes())
    canonical = hashlib.sha256(json.dumps(model['model'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert model['contract_sha256'] == canonical == literal(controller, 'MODEL_SHA')
    assert (model['model']['case_count'], model['model']['codeword_probes'], model['model']['vector_calls']) == (36, 123, 365)
    assert len(model['model']['cases']) == 36
    assert sum(len(c['book']['probes']) for c in model['model']['cases']) == 123
    assert sum(len(c['book']['probes']) * len(c['book']['points']) for c in model['model']['cases']) == 365
    assert 2 + 36 * 2 + 365 == 439
    assert sha(HERE / 'project/main/pinned/production/vorbis_repair/setup.c') == '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
    assert sha(HERE / 'project/main/pinned/production/vorbis_repair_abi.h') == 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
    ps = json.loads((HERE / 'powershell-source-ast.json').read_text(encoding='utf-8-sig'))
    assert ps['parser_errors'] == [] and ps['SDK_or_launcher_executed'] is False and ps['script_sha256'] == sha(HERE / 'project/sdk-build.ps1')
    for name in ('run-public-book-consumer.py', 'owned_qmp.py', 'windows_compile_command.py', 'protocol.py', 'oracle.py'):
        text = (HERE / name).read_text()
        table = symtable.symtable(text, name, 'exec')
        bound = {x.get_name() for x in table.get_symbols() if x.is_assigned() or x.is_imported() or x.is_namespace()}
        allowed = bound | set(dir(builtins)) | {'__file__', '__name__', '__doc__'}
        def scan(block):
            missing = {x.get_name() for x in block.get_symbols() if x.is_referenced() and x.is_global() and x.get_name() not in allowed}
            assert not missing, (name, missing)
            for child in block.get_children():
                scan(child)
        scan(table)
    text = (HERE / 'run-public-book-consumer.py').read_text()
    assert 'from protocol import validate_sdk' in text and 'validate_log(' not in text and 'passed=' not in text
    assert text.index("need(row['lifecycle_qualified'] is True") < text.index('observed = validate_sdk(')
    assert 'return 0 if equal else 1' in text and "host_sanitizer_facts='NOT_EVALUATED_BY_THIS_SDK_CONTROLLER'" in text
    assert "if str(original_path) not in report['inputs']:" in text
    qmp = (HERE / 'owned_qmp.py').read_text()
    assert 'PUBLIC_BOOK_CONSUMER_COMPLETE cases=36 calls=365 unequal=' in qmp and 'CYD_VORBIS_OWNED_BOOK_' not in qmp
    assert "row['stdout_eof_observed'] and row['reader_joined']" in qmp
    for old, new, diff in [('predecessor/run-owned-book-unit.py', 'run-public-book-consumer.py', 'controller-revision.diff'),
                           ('predecessor/owned_qmp.py', 'owned_qmp.py', 'qmp-revision.diff')]:
        (HERE / diff).write_text(''.join(difflib.unified_diff((HERE / old).read_text().splitlines(True), (HERE / new).read_text().splitlines(True),
            fromfile=old, tofile=new)), encoding='utf-8', newline='\n')
    (HERE / 'project-revision.diff').write_text(''.join(difflib.unified_diff([], (HERE / 'project/sdk-build.ps1').read_text().splitlines(True),
        fromfile='generated-runtime/project/sdk-build.ps1 (absent)', tofile='project/sdk-build.ps1')), encoding='utf-8', newline='\n')
    result = dict(schema='public-book-consumer-runtime-source-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(trees), raw_original_files_unchanged=188, unchanged_original_generated_runtime_members=18,
        source_preparation_readiness_sha256=literal(controller, 'SOURCE_READINESS_SHA'),
        generated_runtime_readiness_sha256=literal(controller, 'RUNTIME_READINESS_SHA'),
        contract_file_sha256=literal(controller, 'CONTRACT_FILE_SHA'), canonical_model_sha256=canonical,
        generated_project_delta='Only byte-identical reviewed sdk-build.ps1 added',
        exact_unchanged_controller_helper_AST_functions=9,
        exact_unit_public_consumer_parser_ABI_fixture_bytes=True, unchanged_pure_protocol_and_oracle=True,
        unchanged_Windows_macro_helper_and_SDK_launcher=True, retained_prior_launcher_AST_parse_only=True,
        cases=36, codeword_probes=123, prospective_point_calls=365, prospective_protocol_events=439,
        publication_Fraction_and_host_sanitizer_facts_separate=True, actual_QMP_lifecycle_and_terminal0_required=True,
        no_preemptive_arithmetic_or_production_fix=True, no_imported_global_or_function_rebinding=True,
        source_only=True, proposed_code_imported_or_executed=False,
        SDK_compiler_QEMU_unit_tests_oracle_protocol_decoder_reference_PCM_Git_executed=False,
        actual_terminal_facts_available=False, canonical_old_preps_runtime_campaigns_modified=False,
        full_G6_qualified=False, vendor_cause_diagnosed=False)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    manifest.write_text(json.dumps(dict(schema='public-book-consumer-runtime-source-only-readiness-v1', runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(manifest), runtime_executed=False)))


if __name__ == '__main__':
    main()
