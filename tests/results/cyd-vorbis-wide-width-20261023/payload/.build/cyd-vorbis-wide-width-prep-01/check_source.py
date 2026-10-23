"""AST/hash/raw-byte closure only; never import prepared generator or witness."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def literal(tree, name):
    matches = [node for node in tree.body if isinstance(node, ast.Assign) and
               any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(matches) == 1, name
    return ast.literal_eval(matches[0].value)


def write_json(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    names = ('freeze_originals.py', 'generate_width_controls.py', 'inspect_width_equivalence.py', 'check_source.py')
    trees = {name: ast.parse((HERE / name).read_bytes().decode('utf-8'), filename=name) for name in names}
    pins_bytes = (HERE / 'source-pins.json').read_bytes()
    assert sha(pins_bytes) == '75cb073a50c88b93086ebddf18a83108cdda69b46a96f3f7c1a29dadad97db96'
    pins = json.loads(pins_bytes)
    expected_ids = ('sparse_explicit_d16_seq0', 'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1')
    assert tuple(pins['original_case_ids']) == expected_ids == literal(trees['inspect_width_equivalence.py'], 'IDS')
    assert literal(trees['generate_width_controls.py'], 'WIDTHS') == (9, 16)
    for name in ('generate_width_controls.py', 'inspect_width_equivalence.py'):
        assert literal(trees[name], 'SOURCE_PINS_SHA') == sha(pins_bytes)
    assert len(pins['files']) == 21
    raw_rows = {}
    for name, row in pins['files'].items():
        data = (HERE / name).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert data == Path(row['original_path']).read_bytes()
        raw_rows[name] = fact(HERE / name)
    assert (sha((HERE / 'originals/matrix.json').read_bytes()) == pins['original_matrix_sha256'] ==
            '7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8')
    matrix = json.loads((HERE / 'originals/matrix.json').read_bytes())
    assert matrix['cases'][:4] == pins['selected_original_cases']
    helpers = literal(trees['generate_width_controls.py'], 'HELPERS')
    assert helpers == literal(trees['freeze_originals.py'], 'HELPERS')
    helper_rows = {}
    for name, expected in helpers.items():
        row = fact(ROOT / name)
        assert row['sha256'] == expected == pins['canonical_helpers'][name]['sha256']
        helper_rows[name] = row
    imports = set()
    for node in ast.walk(trees['inspect_width_equivalence.py']):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module.split('.')[0])
    assert imports == {'argparse', 'copy', 'fractions', 'hashlib', 'json', 'pathlib', 'struct'}
    assert not (HERE / 'additions8').exists() and not (HERE / 'comparison12').exists()
    source_names = (*names, 'README.md', 'source-pins.json')
    sources = {name: fact(HERE / name) for name in source_names}
    report = dict(schema='wide-width-source-closure-v1', source_only=True,
        scope='AST_HASH_AND_FROZEN_ORIGINAL_RAW_BYTES_ONLY',
        generator_or_witness_imported_or_executed=False, construction_controls_executed=False,
        codec_reference_compiler_SDK_QEMU_tests_Git_device_executed=False,
        original_raw_freeze_observed=dict(exit_code=0, terminal_chunk_id='2906a5'),
        original_cases=4, frozen_raw_files=20, frozen_original_matrix=1,
        planned_new_widths=[9, 16], planned_additions=8, planned_comparison=12,
        existing_corpora_or_failures_replaced=False, actual_PCM_read_or_compared=False,
        standard_library_only_independent_witness=True,
        canonical_helpers=helper_rows, frozen_originals=raw_rows, sources=sources)
    write_json('source-closure.json', report)
    write_json('readiness.json', dict(schema='wide-width-source-readiness-v1', source_only=True,
        ready_for_root_review=True, runtime_or_reference_qualified=False,
        root_owns_generation_witness_reference_and_target=True,
        source_closure=fact(HERE / 'source-closure.json'), sources=sources))
    print(json.dumps(dict(source_only=True, generator=sources['generate_width_controls.py'],
        witness=sources['inspect_width_equivalence.py'], closure=fact(HERE / 'source-closure.json'),
        readiness=fact(HERE / 'readiness.json'))))


if __name__ == '__main__':
    main()
