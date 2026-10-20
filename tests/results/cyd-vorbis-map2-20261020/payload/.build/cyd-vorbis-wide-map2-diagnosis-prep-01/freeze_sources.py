"""Freeze audit source identities only; no unit, decoder or PCM execution."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if (HERE / 'source-pins.json').exists() or (HERE / 'source-checks.json').exists():
        raise RuntimeError('Preserve frozen source audit')
    capture = ROOT / '.build/cyd-vorbis-format-expanded25-capture-02'
    matrix_root = '.build/cyd-vorbis-map2-regression-prep-01/generated02'
    paths = [
        'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c',
        'idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h',
        'tests/vorbis_format_corpus/generate_map2_regression.py',
        'tests/vorbis_format_corpus/generate_books.py',
        'tests/vorbis_block_matrix/generate_minimal.py',
        '.build/cyd-vorbis-format-expanded25-capture-02/sources/candidate/vorbis_repair/setup.c',
        '.build/cyd-vorbis-format-expanded25-capture-02/sources/candidate/vorbis_repair_abi.h',
        '.build/cyd-vorbis-format-expanded25-capture-02/report.json',
        '.build/cyd-vorbis-format-expanded25-capture-02-terminal.json',
        '.build/cyd-vorbis-format-expanded25-capture-02/sources/corpus/contract.json',
        '.build/cyd-vorbis-format-expanded25-numeric-measurement-01/report.json',
        '.build/cyd-vorbis-map2-regression-qualified-01/qualification.json',
        '.build/cyd-vorbis-map2-regression-host-01/report.json',
        matrix_root + '/matrix.json', matrix_root + '/bitfields.json', matrix_root + '/manifest.json',
    ]
    matrix = json.loads((ROOT / matrix_root / 'matrix.json').read_bytes())
    assert len(matrix['cases']) == 8
    for case in matrix['cases'][:4]:
        for key in ('setup', 'audio'):
            paths.append(matrix_root + '/' + case[key])
    report = json.loads((capture / 'report.json').read_bytes())
    consumed = [row['snapshot'] for row in report['inputs'].values()
                if row['snapshot'].replace('\\', '/').endswith('inputs/books16/matrix.json')]
    assert len(consumed) == 1
    paths.append((capture / consumed[0]).relative_to(ROOT).as_posix())
    rows = []
    for path in paths:
        raw = (ROOT / path).read_bytes()
        rows.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
    assert rows[0]['sha256'] == rows[5]['sha256'] == '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
    assert rows[1]['sha256'] == rows[6]['sha256']
    assert rows[10]['sha256'] == '8d3c6ff5ae60590b457a833cbf4eb208ed44fae2dd6d7802cc908d455fd2934a'
    numeric = json.loads((ROOT / paths[10]).read_bytes())
    assert numeric['measurement_completed'] is True and numeric['bounded_corpus_pcm_qualified'] is False
    assert len(numeric['cases']) == 25 and numeric['policy']['max_abs_error'] == 2
    assert all(c['comparison']['zero_lag_direct_LR']['max_abs_error'] == 65535 for c in numeric['cases'][8:12])
    assert all(c['comparison']['zero_lag_direct_LR']['max_abs_error'] == 1 for c in numeric['cases'][12:16])
    relations = numeric['metamorphic_relations']
    assert len(relations['xiph']) == len(relations['target']) == 8
    assert all(r['expected_relation_observed'] is True for r in relations['xiph'])
    assert all(r['expected_relation_observed'] is False for r in relations['target'][4:6])
    assert all(r['expected_relation_observed'] is True for r in relations['target'][6:8])
    base = 'https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/'
    pins = dict(schema='wide-map2-public-source-audit-v1', local_inputs=rows, primary_sources=[
        dict(url='https://xiph.org/vorbis/doc/Vorbis_I_spec.html', revision='July4 2020', sections=['3.2.1', '3.3']),
        dict(url=base + 'codebook.c', revision='0ad0141e864cfbb130db4f22e279d421832e7336',
            gitiles_reported_blob='35aaeff81ed884aa02cd9232747bb7d8db5ec5d2',
            functions=['decpack', 'vorbis_book_unpack', 'decode_map']),
        dict(url=base + 'codebook.h', revision='0ad0141e864cfbb130db4f22e279d421832e7336',
            gitiles_reported_blob='7519597ce7925373db219da74d1ad7d7cd6513c8', declarations=['codebook'])],
        web_raw_bytes_snapshotted=False, concrete_new_correction_supported=False,
        numeric_report_metadata_only=True, actual_PCM_read_or_recomputed=False,
        proposed_unit_developed_or_run=False, original25_NONPASS_and_failed_pairs_preserved=True)
    with (HERE / 'source-pins.json').open('xb') as stream:
        stream.write((json.dumps(pins, indent=2) + '\n').encode())
    ast.parse(Path(__file__).read_bytes())
    for row in rows:
        raw = (ROOT / row['path']).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in HERE.iterdir() if p.is_file()}
    checks = dict(result='SOURCE_ONLY_AUDIT_READY', AST_files=1, local_raw_identities_checked=len(rows), files=files,
        no_new_correction_supported=True, numeric_report_metadata_only=True, actual_PCM_read_or_recomputed=False,
        proposed_unit_developed_or_run=False, SDK_compiler_codec_QEMU_reference_Git_device_invoked=False,
        live_control_read_or_modified=False, canonical_or_campaign_modified=False, full_G6_qualified=False)
    with (HERE / 'source-checks.json').open('xb') as stream:
        stream.write((json.dumps(checks, indent=2) + '\n').encode())
    print(json.dumps(dict(result=checks['result'], source_checks_sha256=sha((HERE / 'source-checks.json').read_bytes()),
        proposed_unit_developed_or_run=False)))


if __name__ == '__main__':
    main()
