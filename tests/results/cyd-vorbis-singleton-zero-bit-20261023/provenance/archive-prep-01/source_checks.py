"""Source AST/raw hashes and recorded JSON metadata only; no proposed imports/execution."""
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
    'raw_helpers.py': ('original-independent_witness.py', ['need', 'sha', 'Reader', 'prefix', 'unpack', 'quantvals', 'singleton_id', 'read_book', 'expected_book', 'table', 'parse_setup', 'parse_identification', 'parse_comment', 'interleave0', 'parse_audio', 'crc', 'carrier', 'compare_field_report', 'compare_audit']),
    'zero_helpers.py': ('zero-independent_zero_witness.py', ['parse_zero_audio', 'unchanged_except_tokens', 'zero_field_report', 'validate_matrix_status', 'validate_field_report_keys']),
    'materialize_helpers.py': ('zero8-materialize.py', ['need', 'digest', 'recover']),
    'reference_helpers.py': ('zero8-recorded_qualification.py', ['need', 'sha', 'decoded_pcm']),
    'reference_gate.py': ('zero8-reference_binding.py', ['need', 'qualification_gate']),
    'numeric_helpers.py': ('numeric-compare_capture8.py', ['transition_counts']),
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
    assert len(origins['inputs']) == 12
    for row in origins['inputs']:
        old, new = Path(row['source']), HERE / row['snapshot']
        assert old.stat().st_size == new.stat().st_size == row['bytes'] and sha(old) == sha(new) == row['sha256']
    assert (HERE / 'dependency.py').read_bytes() == (HERE / 'provenance/mono02-dependency.py').read_bytes()
    count = 0
    for new, (old, names) in HELPERS.items():
        source = ast.parse((HERE / 'provenance' / old).read_bytes())
        for name in names:
            assert ast.dump(function(source, name), include_attributes=False) == ast.dump(function(trees[new], name), include_attributes=False)
            count += 1
    assert count == 33
    original_protocol = (HERE / 'provenance/zero8-protocol.py').read_text()
    original_tree = ast.parse(original_protocol)
    for name in ('need', 'sha', 'validate_log'):
        assert ast.dump(function(original_tree, name), include_attributes=False) == ast.dump(function(trees['archive_protocol.py'], name), include_attributes=False)
    assert literal(original_tree, 'CASE_IDS') == literal(trees['archive_protocol.py'], 'CASE_IDS') == literal(trees['reference_gate.py'], 'CASE_IDS')
    for name in ('inspect_case', 'load_contract'):
        node = function(original_tree, name)
        text = ''.join(original_protocol.splitlines(True)[node.lineno - 1:node.end_lineno])
        text = text.replace('Path(directory).resolve()', 'PureWindowsPath(ntpath.normpath(str(directory)))')
        text = text.replace('(directory / case[kind]).resolve()', 'PureWindowsPath(ntpath.normpath(str(directory / case[kind])))')
        text = text.replace('Path(source["path"]).resolve()', 'PureWindowsPath(ntpath.normpath(str(source["path"])))')
        text = text.replace('path.read_bytes()', 'read_bytes(path)')
        assert ast.dump(ast.parse(text).body[0], include_attributes=False) == ast.dump(function(trees['archive_protocol.py'], name), include_attributes=False)
    for constant, file in [('MATERIALIZE_HELPERS', 'materialize_helpers.py'), ('REFERENCE_HELPERS', 'reference_helpers.py'), ('RAW_HELPERS', 'raw_helpers.py'),
                           ('ZERO_HELPERS', 'zero_helpers.py'), ('REFERENCE_GATE', 'reference_gate.py'), ('NUMERIC_HELPERS', 'numeric_helpers.py'), ('ARCHIVE_PROTOCOL', 'archive_protocol.py')]:
        assert literal(trees['verify.py'], constant) == sha(HERE / file)
    numeric = ROOT / literal(trees['verify.py'], 'NUMERIC_ROOT')
    for constant, file in [('METRICS', 'pcm_metrics.py'), ('POLICY', 'policy8.py'), ('POLICY_PROTOCOL', 'protocol.py')]:
        assert literal(trees['verify.py'], constant) == sha(numeric / file)
    assert ast.dump(function(ast.parse((numeric / 'compare_capture8.py').read_bytes()), 'transition_counts'), include_attributes=False) == ast.dump(function(trees['numeric_helpers.py'], 'transition_counts'), include_attributes=False)
    for name in ('pack.py', 'verify.py'):
        text = (HERE / name).read_text()
        assert 'protocol.Path' not in text and 'ArchivedPath' not in text
        table = symtable.symtable(text, name, 'exec')
        bound = {x.get_name() for x in table.get_symbols() if x.is_assigned() or x.is_imported() or x.is_namespace()}
        allowed = bound | set(dir(builtins)) | {'__file__', '__name__', '__doc__'}
        def scan(block):
            missing = {x.get_name() for x in block.get_symbols() if x.is_referenced() and x.is_global() and x.get_name() not in allowed}
            assert not missing, (name, missing)
            for child in block.get_children():
                scan(child)
        scan(table)
    plan = json.loads((HERE / 'plan.template.json').read_bytes())
    assert plan['schema'] == 'cyd-singleton-zero-bit-selection-v1' and set(plan['roles']) == {'capture8', 'numeric8', 'numeric-input-failure01', 'host-zero8'}
    for name, row in plan['roles'].items():
        assert sha(ROOT / row['path'] / 'report.json') == row['report_sha256']
        assert sha(ROOT / row['terminal']) == row['terminal_sha256']
        report = json.loads((ROOT / row['path'] / 'report.json').read_bytes())
        assert (report.get('measurement_completed', report.get('completed')) is True or
                (name == 'numeric-input-failure01' and report['result'] == 'INPUT_OR_MEASUREMENT_REJECTED' and
                 report['measurement_completed'] is report['actual_reference_compared'] is False and report['cases'] == []))
    assert len(plan['trees']) == 9 and all((ROOT / name).is_dir() for name in plan['trees'])
    for name in plan['extra_receipts']:
        assert sha(ROOT / name) == plan['extra_receipt_pins'][name]
    assert sha(ROOT / plan['checkpoint']['path']) == plan['checkpoint']['sha256']
    assert plan['prior_other_numeric_NONPASS_record_only_not_replayed'] is plan['no_full8_dual_reference_pass'] is True
    diff_pairs = [('provenance/mono02-pack.py', 'pack.py', 'pack-adaptation.diff'),
                  ('provenance/mono02-verify.py', 'verify.py', 'verify-adaptation.diff'),
                  ('provenance/zero8-protocol.py', 'archive_protocol.py', 'archive-protocol-adaptation.diff')]
    diff_pairs += [('provenance/' + old, new, new.removesuffix('.py') + '-extraction.diff') for new, (old, unused) in HELPERS.items()]
    for old, new, diff in diff_pairs:
        (HERE / diff).write_text(''.join(difflib.unified_diff((HERE / old).read_text().splitlines(True), (HERE / new).read_text().splitlines(True),
            fromfile=old, tofile=new)), encoding='utf-8', newline='\n')
    result = dict(schema='singleton-zero-bit-archive-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(trees), raw_preserved_source_origins=12, exact_pure_helper_definitions=33,
        unchanged_protocol_function_AST=['need', 'sha', 'validate_log'], exact_reader_adaptations=['inspect_case', 'load_contract'],
        explicit_archive_reader_no_global_rebinding=True, exact_original_path_and_frozen_snapshot_identity=True,
        complete_actual_plan_roles=4, bounded_trees=9, extra_actual_receipts=len(plan['extra_receipts']), root_checkpoint_hash_verified=True,
        target_protocol_counts=[8, 112, 225280, 251, 255], current_reference_streams=12, actual_reference_child_receipts=16,
        original_native_packet_refusals=4, new_native_acceptances=4, predecessor_original_Xiph_streams=4,
        fixed_bound=2, complete_mixed12_required=True, no_full8_dual_pass=True,
        actual_input_rejection_history_preserved=True, numerical_NONPASS_preserved=True,
        prior_other_numeric_NONPASS_replayed=False, source_only=True, proposed_code_imported_or_executed=False,
        pack_or_verify_or_PCM_or_test_or_decoder_reference_SDK_QEMU_Git_executed=False, canonical_destination_modified=False)
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='singleton-zero-bit-archive-source-only-readiness-v1', runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
