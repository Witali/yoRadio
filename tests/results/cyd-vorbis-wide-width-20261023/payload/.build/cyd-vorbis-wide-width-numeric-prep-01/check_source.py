"""Source/AST/hash/JSON metadata closure only; no adapter, metrics or payload execution."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data): return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=path.relative_to(HERE).as_posix(), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    node = next(node for node in tree.body if isinstance(node, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return ast.literal_eval(node.value)


def definition(text, tree, name):
    node = next(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
    return ast.get_source_segment(text, node)


def create(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    adapter = (HERE / 'compare_capture12.py').read_bytes().decode('utf-8')
    tree = ast.parse(adapter)
    assert (HERE / 'compare_capture12.py').read_bytes() == (HERE / 'helpers.source.txt').read_bytes() + (HERE / 'numeric.body.txt').read_bytes()
    base_path = ROOT / '.build/cyd-vorbis-format-expanded25-numeric-prep-01/compare_capture25.py'
    base_bytes = base_path.read_bytes()
    assert sha(base_bytes) == '2fe6ca486c0031101f15c787a84c39c419840b914ae0c829c95bd4095ec37a08'
    base = base_bytes.decode()
    base_tree = ast.parse(base)
    helpers = ('sha', 'relative', 'Inputs', 'wav_pcm', 'frame_checksums')
    for name in helpers:
        assert definition(base, base_tree, name) == definition(adapter, tree, name)
    assert (HERE / 'pcm_metrics.py').read_bytes() == base_path.with_name('pcm_metrics.py').read_bytes()
    assert sha((HERE / 'pcm_metrics.py').read_bytes()) == literal(tree, 'METRICS') == 'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f'
    pins = json.loads((HERE / 'pins.json').read_bytes())
    assert pins['policy_sha256'] == sha((HERE / 'policy12.py').read_bytes())
    for row in list(pins['reference'].values()) + list(pins['runtime'].values()) + [pins['original_pair_declaration_source']]:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    for name, key in (('RUNNER', 'run-cyd-vorbis-wide-width12-qemu.py'), ('PROTOCOL', 'protocol.py'),
                      ('CONTRACT_FILE', 'contract.json'), ('DATA', 'materialized01/data.h'), ('BINDING', 'reference-binding12.json')):
        assert literal(tree, name) == pins['runtime'][key]['sha256']
    policy = (HERE / 'policy12.py').read_bytes().decode()
    policy_tree = ast.parse(policy)
    matrix = json.loads((ROOT / pins['reference']['matrix']['path']).read_bytes())
    assert literal(policy_tree, 'CASE_IDS') == tuple(case['id'] for case in matrix['cases'])
    assert literal(policy_tree, 'TRIPLES') == pins['three_width_groups'] == matrix['expected_same_decoder_pcm_equal_groups']
    original = json.loads((ROOT / pins['original_pair_declaration_source']['path']).read_bytes())
    pairs = original['expected_same_decoder_pcm_equal_groups'][:2]
    assert pairs == pins['original_sparse_dense_pairs']
    expected_pairs = [pair if width == 2 else [name + f'_qbits{width}' for name in pair] for width in (2, 9, 16) for pair in pairs]
    assert literal(policy_tree, 'SHAPE_PAIRS') == expected_pairs
    expected_policy = '"""Predeclared exact12 numerical policy and source-derived equivalence relations."""\nfrom pcm_metrics import need\n'
    expected_policy += (HERE / 'policy.constants.txt').read_bytes().decode() + (HERE / 'policy.body.txt').read_bytes().decode()
    assert expected_policy == policy
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes().decode('utf-8'), filename=str(path))
    ast.parse((HERE / 'numeric.body.txt').read_bytes().decode('utf-8'))
    ast.parse((HERE / 'policy.body.txt').read_bytes().decode('utf-8'))
    files = [fact(path) for path in sorted(HERE.iterdir()) if path.is_file()]
    report = dict(schema='wide-width12-numeric-source-closure-v1', source_only=True,
        scope='AST_HASH_AND_RECORDED_JSON_METADATA_ONLY',
        adapter_metrics_policy_protocol_imported_or_executed=False,
        actual_PCM_read_or_compared=False, decoder_reference_SDK_compiler_QEMU_tests_Git_executed=False,
        immutable_metric_source=True, exact_unchanged_helper_definitions=list(helpers),
        exact_cases=12, packets=168, expected_pcm_bytes=337920, events=375,
        declared_triples=4, sparse_dense_pairs_derived_from_original_declarations=6,
        metric_bound=2, optional_bound_default=None, numerical_result_claimed=False, files=files)
    create('source-closure.json', report)
    create('readiness.json', dict(schema='wide-width12-numeric-readiness-v1', source_only=True,
        ready_for_root_review=True, actual_numeric_qualified=False,
        closure=fact(HERE / 'source-closure.json'), files=files))
    print(json.dumps(dict(source_only=True, adapter=fact(HERE / 'compare_capture12.py'), policy=fact(HERE / 'policy12.py'),
        closure=fact(HERE / 'source-closure.json'), readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
