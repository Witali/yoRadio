"""Freeze selected already-existing valid raw bytes; no generator/codec execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = ROOT / '.build/cyd-vorbis-map2-regression-prep-01/generated02'
MATRIX_SHA = '7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8'
HELPERS = {
    'tests/vorbis_format_corpus/generate_map2_regression.py': '49015a8a849682ad886c970ea3b1a3bc06f02f21a4f01785b7d52695e23d3caa',
    'tests/vorbis_format_corpus/generate_books.py': 'de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1',
    'tests/vorbis_block_matrix/generate_minimal.py': '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1',
}
IDS = ('sparse_explicit_d16_seq0', 'dense_active_d16_seq0',
       'sparse_explicit_d16_seq1', 'dense_active_d16_seq1')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def main():
    raw = (ORIGINAL / 'matrix.json').read_bytes()
    assert sha(raw) == MATRIX_SHA
    matrix = json.loads(raw)
    helpers = {}
    for name, expected in HELPERS.items():
        data = (ROOT / name).read_bytes()
        assert sha(data) == expected
        helpers[name] = dict(bytes=len(data), sha256=expected)
    cases = matrix['cases'][:4]
    assert tuple(row['id'] for row in cases) == IDS
    files = {}
    for case in cases:
        assert case['vector_book']['dimensions'] == 16 and case['vector_book']['value_bits'] == 2
        for kind in ('identification', 'comment', 'setup', 'audio', 'ogg'):
            data = (ORIGINAL / case[kind]).read_bytes()
            expected = case['files'][kind]
            assert len(data) == expected['bytes'] and sha(data) == expected['sha256']
            name = f"originals/{case['id']}/{Path(case[kind]).name}"
            save(name, data)
            files[name] = dict(bytes=len(data), sha256=sha(data), original_path=str(ORIGINAL / case[kind]), kind=kind, id=case['id'])
    save('originals/matrix.json', raw)
    files['originals/matrix.json'] = dict(bytes=len(raw), sha256=sha(raw), original_path=str(ORIGINAL / 'matrix.json'))
    pins = dict(schema='wide-width-original-source-pins-v1', source_only=True,
        original_matrix_sha256=MATRIX_SHA, original_case_ids=list(IDS), canonical_helpers=helpers,
        files=files, selected_original_cases=cases, generator_or_witness_executed=False,
        root_owns_generation_reference_and_target=True)
    save('source-pins.json', (json.dumps(pins, indent=2) + '\n').encode())
    print(json.dumps(dict(source_only=True, selected_originals=len(cases), frozen_files=len(files),
                         source_pins_sha256=sha((HERE / 'source-pins.json').read_bytes()))))


if __name__ == '__main__':
    main()
