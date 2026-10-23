"""Source AST/raw hashes and recorded JSON plan metadata only; no proposed imports/execution."""
import ast
import builtins
import difflib
import hashlib
import json
from pathlib import Path
import symtable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HELPERS = {
    'raw_helpers.py': ('helper-origin-raw_helpers.py', ['need','sha','Reader','prefix','unpack','quantvals','singleton_id','read_book','expected_book','table','parse_setup','parse_identification','parse_comment','interleave0','parse_audio','crc','carrier','compare_field_report','compare_audit']),
    'zero_helpers.py': ('helper-origin-zero_helpers.py', ['parse_zero_audio','unchanged_except_tokens','zero_field_report','validate_matrix_status','validate_field_report_keys']),
    'materialize_helpers.py': ('helper-origin-materialize_helpers.py', ['need','digest','recover']),
    'reference_helpers.py': ('helper-origin-reference_helpers.py', ['need','sha','decoded_pcm']),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def literal(tree, name):
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    return ast.literal_eval(node.value)


def main():
    checks, readiness = HERE / 'source-checks.json', HERE / 'readiness.json'
    if checks.exists() or readiness.exists():
        raise RuntimeError('Preserve immutable source-only receipts')
    trees = {p.name: ast.parse(p.read_bytes(), filename=p.name) for p in HERE.glob('*.py')}
    origins = json.loads((HERE / 'source-origins.json').read_bytes())
    assert len(origins['inputs']) == 10
    for x in origins['inputs']:
        old, new = Path(x['source']), HERE / x['snapshot']
        assert old.stat().st_size == new.stat().st_size == x['bytes'] and sha(old) == sha(new) == x['sha256']
    assert (HERE / 'dependency.py').read_bytes() == (HERE / 'provenance/wide-dependency.py').read_bytes()
    count = 0
    for new, (old, names) in HELPERS.items():
        source = ast.parse((HERE / 'provenance' / old).read_bytes())
        for name in names:
            assert ast.dump(function(source, name), include_attributes=False) == ast.dump(function(trees[new], name), include_attributes=False)
            count += 1
    assert count == 30
    original_protocol = (HERE / 'provenance/helper-origin-protocol.py').read_text()
    original_tree = ast.parse(original_protocol)
    for name in ('need', 'sha', 'validate_log'):
        assert ast.dump(function(original_tree, name), include_attributes=False) == ast.dump(function(trees['archive_protocol.py'], name), include_attributes=False)
    for constant, file in [('MATERIALIZE_HELPERS','materialize_helpers.py'), ('RAW_HELPERS','raw_helpers.py'),
        ('ZERO_HELPERS','zero_helpers.py'), ('REFERENCE_HELPERS','reference_helpers.py'), ('ARCHIVE_PROTOCOL','archive_protocol.py')]:
        assert literal(trees['verify.py'], constant) == sha(HERE / file)
    assert 'protocol.Path' not in (HERE / 'verify.py').read_text() and 'ArchivedPath' not in (HERE / 'verify.py').read_text()
    for name in ('pack.py', 'verify.py'):
        table = symtable.symtable((HERE / name).read_text(), name, 'exec')
        bound = {x.get_name() for x in table.get_symbols() if x.is_assigned() or x.is_imported() or x.is_namespace()}
        allowed = bound | set(dir(builtins)) | {'__file__','__name__'}
        def scan(block):
            missing = {x.get_name() for x in block.get_symbols() if x.is_referenced() and x.is_global() and x.get_name() not in allowed}
            assert not missing, (name, missing)
            for child in block.get_children():
                scan(child)
        scan(table)
    plan = json.loads((HERE / 'plan.template.json').read_bytes())
    assert plan['schema'] == 'cyd-more-singletons-selection-v1' and set(plan['roles']) == {'capture8','numeric8','host-original8','host-zero8'}
    for row in plan['roles'].values():
        assert sha(ROOT / row['path'] / 'report.json') == row['report_sha256']
        assert sha(ROOT / row['terminal']) == row['terminal_sha256']
    assert len(plan['trees']) == 11 and all((ROOT / p).is_dir() for p in plan['trees']) and len(plan['extra_receipts']) == 9
    for p in plan['extra_receipts']:
        assert sha(ROOT / p) == plan['extra_receipt_pins'][p]
    assert sha(ROOT / plan['checkpoint']['path']) == plan['checkpoint']['sha256'] == '872335e02a452a8b73080de6e4576065873883c8bfb4fcca4ba29d83be319f7f'
    assert plan['prior25_floor0_wide_record_only_not_replayed'] is True and plan['zero_target_executed'] is False
    for old, new, diff in [('provenance/wide-pack.py','pack.py','pack-adaptation.diff'), ('provenance/wide-verify.py','verify.py','verify-adaptation.diff'),
                           ('provenance/helper-origin-protocol.py','archive_protocol.py','archive-protocol-adaptation.diff')]:
        (HERE / diff).write_text(''.join(difflib.unified_diff((HERE / old).read_text().splitlines(True), (HERE / new).read_text().splitlines(True),
            fromfile=old, tofile=new)), encoding='utf-8')
    result = dict(schema='more-singletons-archive-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(trees), raw_preserved_source_origins=10, exact_pure_helper_definitions=30,
        unchanged_protocol_function_AST=['need','sha','validate_log'], explicit_archive_reader_no_global_rebinding=True,
        complete_actual_plan_roles=4, bounded_trees=11, extra_actual_receipts=9, root_checkpoint_hash_verified=True,
        target_protocol_counts=[8,112,225280,251,255], fixed_bound=2, numeric_NONPASS_preserved=True,
        original_native_failures=[4,4], zero_new_native_passes=4, original_and_zero_dual_NONPASS_preserved=True,
        prior_campaigns_replayed=False, source_only=True, proposed_code_imported_or_executed=False,
        pack_or_verify_or_PCM_or_test_or_decoder_reference_SDK_QEMU_Git_executed=False,
        canonical_destination_modified=False, numeric_or_full_G6_qualified=False)
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='more-singletons-archive-source-only-readiness-v1', runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
