"""Source assembly / AST / raw hashes only, never imports proposed code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks, readiness = HERE / 'source-checks.json', HERE / 'readiness.json'
    if checks.exists() or readiness.exists():
        raise RuntimeError('Preserve existing source-only receipts')
    names = ['support.py', 'generate_zero.py', 'independent_zero_witness.py', 'test_zero_controls.py', 'source_checks.py']
    trees = {n: ast.parse((HERE / n).read_bytes(), filename=n) for n in names}
    controls = [n.name for n in ast.walk(trees['test_zero_controls.py']) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    assert len(controls) == len(set(controls)) == 28
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    assert pins['schema'] == 'singleton-zero-bit-source-pins-v1' and len(pins['inputs']) == 57
    for x in pins['inputs']:
        old, new = Path(x['source']), HERE / x['snapshot']
        assert old.stat().st_size == new.stat().st_size == x['bytes'] and sha(old) == sha(new) == x['sha256']
    old_path = HERE / 'provenance/prior-preparation/independent_witness.py'
    assert sha(old_path) == '1e5095929f19f68b627bc51fee369943e13f7e9bc5069ff817a6865cf39ee6ef'
    old_text, new_text = old_path.read_text(), (HERE / 'independent_zero_witness.py').read_text()
    old_tree = ast.parse(old_text)
    original = next(n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_audio')
    adapted = next(n for n in trees['independent_zero_witness.py'].body if isinstance(n, ast.FunctionDef) and n.name == 'parse_zero_audio')
    (HERE / 'zero-audio-function.diff').write_text(''.join(difflib.unified_diff(
        ast.get_source_segment(old_text, original).splitlines(True), ast.get_source_segment(new_text, adapted).splitlines(True),
        fromfile='prior-independent-witness:parse_audio-original-only', tofile='independent-zero-witness:parse_zero_audio')), encoding='utf-8')
    for name in ('generate_zero.py', 'independent_zero_witness.py', 'test_zero_controls.py', 'source_checks.py'):
        before, after = HERE / 'provenance/prep01' / name, HERE / name
        (HERE / ('prep01-' + name.replace('.py', '') + '.diff')).write_text(''.join(difflib.unified_diff(
            before.read_text().splitlines(True), after.read_text().splitlines(True),
            fromfile='prep01/' + name, tofile='prep02/' + name)), encoding='utf-8')
    for name in ('generate_zero.py', 'independent_zero_witness.py'):
        for n in ast.walk(trees[name]):
            if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                assert not any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'prior' for t in targets)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                assert n.func.id not in ('exec', 'eval', 'compile', 'setattr')
    result = dict(schema='singleton-zero-bit-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=5, raw_preserved_origins=57, proposed_control_methods=28, control_method_names=controls,
        proposed_original_map1_cases=4, proposed_additive_zero_cases=4, proposed_comparison_audio_packets=112,
        proposed_comparison_tokens=224, proposed_new_zero_tokens=112, proposed_cleared_old_one_bits=56,
        new_corpus_generation_witness_controls_reference_decoder_unit_compiler_SDK_QEMU_Git_executed=False,
        original_full_eight_case_NONPASS_preserved=True, native_outcome_or_cause_assumed=False,
        actual_PCM_equality_verified=False, target_or_full_G6_qualified=False,
        successor_changes='Exact pending status and field-report key gates; precise new zero-wire feature; four new controls')
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='singleton-zero-bit-source-only-readiness-v1', runtime_executed=False,
        files=files), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
