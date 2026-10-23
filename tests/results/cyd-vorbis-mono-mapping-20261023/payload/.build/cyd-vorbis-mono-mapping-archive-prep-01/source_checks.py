"""AST/raw-source/recorded JSON metadata checks only; never import proposed code."""
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
    'materialize_helpers.py': ('mono-materialize.py', ['need', 'digest', 'recover']),
    'reference_helpers.py': ('mono-recorded_qualification.py', ['need', 'sha', 'decoded_pcm']),
    'numeric_helpers.py': ('mono-compare_capture21.py', ['transition_counts']),
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
    assert len(origins['inputs']) == 7
    for row in origins['inputs']:
        old, new = Path(row['source']), HERE / row['snapshot']
        assert old.stat().st_size == new.stat().st_size == row['bytes'] and sha(old) == sha(new) == row['sha256']
    assert (HERE / 'dependency.py').read_bytes() == (HERE / 'provenance/singleton-dependency.py').read_bytes()
    count = 0
    for new, (old, names) in HELPERS.items():
        source = ast.parse((HERE / 'provenance' / old).read_bytes())
        for name in names:
            assert ast.dump(function(source, name), include_attributes=False) == ast.dump(function(trees[new], name), include_attributes=False)
            count += 1
    assert count == 7
    original_protocol = (HERE / 'provenance/mono-protocol.py').read_text()
    original_tree = ast.parse(original_protocol)
    for name in ('need', 'sha', 'channel_nonzero', 'validate_log'):
        assert ast.dump(function(original_tree, name), include_attributes=False) == ast.dump(function(trees['archive_protocol.py'], name), include_attributes=False)
    for name in ('inspect_case', 'load_contract'):
        node = function(original_tree, name)
        text = ''.join(original_protocol.splitlines(True)[node.lineno - 1:node.end_lineno])
        text = text.replace('Path(directory).resolve()', 'PureWindowsPath(ntpath.normpath(str(directory)))')
        text = text.replace('(directory / case[kind]).resolve()', 'PureWindowsPath(ntpath.normpath(str(directory / case[kind])))')
        text = text.replace('Path(source["path"]).resolve()', 'PureWindowsPath(ntpath.normpath(str(source["path"])))')
        text = text.replace('path.read_bytes()', 'read_bytes(path)')
        assert ast.dump(ast.parse(text).body[0], include_attributes=False) == ast.dump(function(trees['archive_protocol.py'], name), include_attributes=False)
    for constant, file in [('MATERIALIZE_HELPERS', 'materialize_helpers.py'), ('REFERENCE_HELPERS', 'reference_helpers.py'),
                           ('NUMERIC_HELPERS', 'numeric_helpers.py'), ('ARCHIVE_PROTOCOL', 'archive_protocol.py')]:
        assert literal(trees['verify.py'], constant) == sha(HERE / file)
    numeric = ROOT / '.build/cyd-vorbis-mono-mapping-numeric-prep-02'
    for constant, file in [('METRICS', 'pcm_metrics.py'), ('MONO_METRICS', 'mono_metrics.py'), ('POLICY', 'policy21.py')]:
        assert literal(trees['verify.py'], constant) == sha(numeric / file)
    assert sha(numeric / 'readiness.json') == '0f7ce1d76f5a3541fbe7f7e798fe1eca7b85d27f57e6f8ac44bdd74aa4ea0950'
    assert (numeric / 'compare_capture21.py').read_bytes() == (HERE / 'provenance/mono-compare_capture21.py').read_bytes()
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
    assert plan['schema'] == 'cyd-mono-mapping-selection-v1' and set(plan['roles']) == {'capture21', 'numeric21', 'numeric-input-failure01', 'host21'}
    for row in plan['roles'].values():
        assert sha(ROOT / row['path'] / 'report.json') == row['report_sha256']
        assert sha(ROOT / row['terminal']) == row['terminal_sha256']
        report = json.loads((ROOT / row['path'] / 'report.json').read_bytes())
        assert (report.get('measurement_completed', report.get('completed')) is True or
                (row['path'].endswith('numeric-measurement-01') and report['result'] == 'INPUT_OR_MEASUREMENT_REJECTED' and
                 report['measurement_completed'] is report['actual_reference_compared'] is False))
    assert len(plan['trees']) == 9 and all((ROOT / name).is_dir() for name in plan['trees'])
    for name in plan['extra_receipts']:
        assert sha(ROOT / name) == plan['extra_receipt_pins'][name]
    assert sha(ROOT / plan['checkpoint']['path']) == plan['checkpoint']['sha256']
    assert plan['prior8_floor0_wide_record_only_not_replayed'] is True
    for old, new, diff in [('provenance/singleton-pack.py', 'pack.py', 'pack-adaptation.diff'),
                           ('provenance/singleton-verify.py', 'verify.py', 'verify-adaptation.diff'),
                           ('provenance/mono-protocol.py', 'archive_protocol.py', 'archive-protocol-adaptation.diff')]:
        (HERE / diff).write_text(''.join(difflib.unified_diff((HERE / old).read_text().splitlines(True), (HERE / new).read_text().splitlines(True),
            fromfile=old, tofile=new)), encoding='utf-8', newline='\n')
    result = dict(schema='mono-mapping-archive-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=len(trees), raw_preserved_source_origins=7, exact_pure_helper_definitions=7,
        unchanged_protocol_function_AST=['need', 'sha', 'channel_nonzero', 'validate_log'],
        exact_explicit_reader_adaptations=['inspect_case', 'load_contract'], explicit_archive_reader_no_global_rebinding=True,
        complete_actual_plan_roles=4, bounded_trees=9, extra_actual_receipts=len(plan['extra_receipts']), root_checkpoint_hash_verified=True,
        target_protocol_counts=[21, 294, 464640, 654, 2097151], mono_cases=9, stereo_cases=12, actual_reference_streams=42,
        fixed_bound=2, both_existing_references_required=True, actual_NONPASS_preserved=True,
        prior_campaigns_replayed=False, source_only=True, proposed_code_imported_or_executed=False,
        pack_or_verify_or_PCM_or_test_or_decoder_reference_SDK_QEMU_Git_executed=False,
        canonical_destination_modified=False, numeric_or_full_G6_qualified=False)
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='mono-mapping-archive-source-only-readiness-v1', runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
