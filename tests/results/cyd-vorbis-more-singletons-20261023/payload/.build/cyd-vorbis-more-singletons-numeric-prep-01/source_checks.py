"""AST, source diffs, raw identities, recorded JSON metadata only; no imports of proposed code."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal(tree, name):
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    return ast.literal_eval(node.value)


def definition(text, tree, name):
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    return ast.get_source_segment(text, node)


def main():
    checks, readiness = HERE / 'source-checks.json', HERE / 'readiness.json'
    if checks.exists() or readiness.exists():
        raise RuntimeError('Preserve source-only receipts')
    names = ['compare_capture8.py', 'policy8.py', 'pcm_metrics.py', 'source_checks.py']
    trees = {n: ast.parse((HERE / n).read_bytes(), filename=n) for n in names}
    pins = json.loads((HERE / 'pins.json').read_bytes()); origins = json.loads((HERE / 'source-pins.json').read_bytes())
    assert len(origins['inputs']) == 18
    for x in origins['inputs']:
        old, new = Path(x['source']), HERE / x['snapshot']
        assert old.stat().st_size == new.stat().st_size == x['bytes'] and sha(old) == sha(new) == x['sha256']
    before = (HERE / 'provenance/wide/compare_capture12.py').read_text(); old_tree = ast.parse(before)
    after = (HERE / 'compare_capture8.py').read_text(); new_tree = trees['compare_capture8.py']
    unchanged = ('sha', 'relative', 'Inputs', 'wav_pcm', 'frame_checksums', 'transition_counts')
    for name in unchanged:
        assert definition(before, old_tree, name) == definition(after, new_tree, name)
    assert sha(HERE / 'pcm_metrics.py') == literal(new_tree, 'METRICS') == 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
    assert pins['policy_sha256'] == sha(HERE / 'policy8.py')
    for constant, key in [('RUNNER', 'controller'), ('PROTOCOL', 'protocol'), ('CALLER', 'caller'), ('CONTRACT_FILE', 'contract'), ('DATA', 'data'), ('BINDING', 'binding')]:
        assert literal(new_tree, constant) == pins['runtime'][key]['sha256']
    for x in list(pins['reference'].values()) + list(pins['runtime'].values()):
        assert (ROOT / x['path']).stat().st_size == x['bytes'] and sha(ROOT / x['path']) == x['sha256']
    matrix = json.loads((HERE / 'provenance/reference/matrix.json').read_bytes())
    qualification = json.loads((HERE / 'provenance/reference/qualification.json').read_bytes())
    model = json.loads((HERE / 'provenance/runtime/contract.json').read_bytes())['model']
    assert literal(trees['policy8.py'], 'CASE_IDS') == tuple(c['id'] for c in matrix['cases']) == tuple(c['id'] for c in model['cases'])
    assert literal(trees['policy8.py'], 'TRIPLES') == matrix['expected_same_decoder_pcm_equal_groups']
    assert literal(trees['policy8.py'], 'DIFFERENT_PAIRS') == matrix['expected_same_decoder_pcm_different_pairs']
    assert (len(model['cases']), model['total_packets'], model['total_pcm'], model['case_mask']) == (8, 112, 225280, 255)
    assert qualification['profile'] == 'singletons8' and qualification['xiph_cases'] == 8
    assert qualification['native_lookup2_refusals'] == qualification['native_packet_decode_failures'] == 4
    assert qualification['dual_reference_qualified'] is False and qualification['native_cause_diagnosed'] is False
    assert '--prior-' not in after and 'exact12' not in after
    assert "choices=(2,), default=2" in after and 'actual_reference_compared' in after
    for old, new, diff in [('provenance/wide/compare_capture12.py', 'compare_capture8.py', 'adapter-from-wide12.diff'),
                           ('provenance/wide/policy12.py', 'policy8.py', 'policy-from-wide12.diff')]:
        (HERE / diff).write_text(''.join(difflib.unified_diff((HERE / old).read_text().splitlines(True), (HERE / new).read_text().splitlines(True),
            fromfile=old, tofile=new)), encoding='utf-8')
    result = dict(schema='more-singletons8-numeric-source-only-checks-v1', result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',
        AST_files=4, raw_original_snapshots=18, exact_unchanged_functions=list(unchanged), common_metrics_byteexact=True,
        declared_cases=8, declared_packets=112, declared_PCM_bytes=225280, declared_events=251, declared_case_mask=255,
        equal_triples_per_decoder=2, different_pairs_per_decoder=4, fixed_predeclared_LSB_bound=2,
        actual_target_report_and_terminal_require_CLI=True, prior25_floor0_wide_record_only=True,
        adapter_metrics_policy_protocol_or_tests_executed=False, actual_target_or_reference_PCM_read=False,
        decoder_reference_unit_compiler_SDK_QEMU_Git_device_executed=False, numeric_or_full_G6_qualified=False)
    checks.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    files = {p.relative_to(HERE).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    readiness.write_text(json.dumps(dict(schema='more-singletons8-numeric-source-only-readiness-v1', runtime_executed=False, files=files), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(result=result['result'], files=len(files), readiness_sha256=sha(readiness), runtime_executed=False)))


if __name__ == '__main__':
    main()
