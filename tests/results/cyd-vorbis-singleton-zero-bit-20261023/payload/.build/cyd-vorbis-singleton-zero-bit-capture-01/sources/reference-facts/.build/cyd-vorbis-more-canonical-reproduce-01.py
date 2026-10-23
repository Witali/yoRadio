"""Compare the two actual canonical generations with frozen original payloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '.build/cyd-vorbis-more-canonical-reproduce-01'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def fact(path):
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def load(path):
    return json.loads(path.read_bytes())


need(not OUT.exists(), 'Fresh report output required')
OUT.mkdir()
rows = []
profiles = (
    ('mono', 'cyd-vorbis-mono-mapping-prep-01/generated01',
     'vorbis-mono-mapping-canonical-check-01', 'inputs_before', 'inputs_after',
     'generate_mono_mapping.py', 21, 294, 464640),
    ('map2', 'cyd-vorbis-map2-regression-prep-01/generated02',
     'vorbis-map2-regression-canonical-check-01', 'source_inputs_before',
     'source_inputs_after', 'generate_map2_regression.py', 8, 112, 225280),
)
for profile, original_name, generated_name, before_key, after_key, generator, count, packets, pcm in profiles:
    original, generated = (ROOT / '.build' / name for name in (original_name, generated_name))
    receipt_path = ROOT / '.build' / (generated_name + '-command.json')
    receipt = load(receipt_path)
    need(receipt['status'] == 'TERMINAL' and receipt['returncode'] == 0 and
         receipt['owned_pid'] > 0 and not receipt.get('error_type'), 'Actual completed generation required')
    for name, row in receipt['logs'].items():
        need(fact(Path(name)) == row, 'Actual command log changed')
    old_files = {p.relative_to(original).as_posix(): p for p in original.rglob('*') if p.is_file()}
    new_files = {p.relative_to(generated).as_posix(): p for p in generated.rglob('*') if p.is_file()}
    need(old_files.keys() == new_files.keys(), 'Exact generated file set required')
    same = []
    for name in sorted(old_files.keys() - {'pure-checks.json', 'manifest.json'}):
        need(old_files[name].read_bytes() == new_files[name].read_bytes(), 'Encoded payload differs: ' + name)
        same.append(dict(path=name, **fact(new_files[name])))
    old_pure, new_pure = (load(p / 'pure-checks.json') for p in (original, generated))
    need(old_pure[before_key] == old_pure[after_key] and new_pure[before_key] == new_pure[after_key],
         'Generation inputs changed during either command')
    canonical_inputs = [ROOT / 'tests/vorbis_format_corpus' / generator]
    if profile == 'mono':
        canonical_inputs += [ROOT / 'tests/vorbis_block_matrix/generate_minimal.py',
                             ROOT / 'tests/vorbis_format_corpus/README.md']
    else:
        canonical_inputs += [ROOT / 'tests/vorbis_format_corpus/README.md',
                             ROOT / 'tests/vorbis_format_corpus/generate_books.py',
                             ROOT / 'tests/vorbis_block_matrix/generate_minimal.py']
    expected_inputs = [dict(path=str(path), **fact(path)) for path in canonical_inputs]
    need(new_pure[before_key] == expected_inputs, 'Canonical provenance is not actual current input bytes')
    old_normalized = {k: v for k, v in old_pure.items() if k not in (before_key, after_key)}
    new_normalized = {k: v for k, v in new_pure.items() if k not in (before_key, after_key)}
    need(old_normalized == new_normalized and new_pure['completed'] is True and
         (new_pure['cases'], new_pure['packets']) == (count, packets), 'Nonprovenance pure-check fields differ')
    old_manifest, new_manifest = (load(p / 'manifest.json') for p in (original, generated))
    need(old_manifest['source_inputs'] == old_pure[before_key] and
         new_manifest['source_inputs'] == new_pure[before_key], 'Manifest source binding differs')
    for manifest, folder in ((old_manifest, original), (new_manifest, generated)):
        need(len(manifest['files']) == len(old_files) - 1 and
             {r['path'] for r in manifest['files']} == old_files.keys() - {'manifest.json'}, 'Manifest file set differs')
        for item in manifest['files']:
            need(fact(folder / item['path']) == {k: item[k] for k in ('bytes', 'sha256')}, 'Manifest file identity differs')
    old_norm = {k: v for k, v in old_manifest.items() if k not in ('source_inputs', 'files')}
    new_norm = {k: v for k, v in new_manifest.items() if k not in ('source_inputs', 'files')}
    need(old_norm == new_norm, 'Unexpected manifest field changes')
    need([r for r in old_manifest['files'] if r['path'] != 'pure-checks.json'] ==
         [r for r in new_manifest['files'] if r['path'] != 'pure-checks.json'], 'Unexpected file-hash differences')
    matrix = load(generated / 'matrix.json')
    need(len(matrix['cases']) == count and sum(c['packet_count'] for c in matrix['cases']) == packets and
         sum(c['expected_s16le_bytes'] for c in matrix['cases']) == pcm, 'Complete case accounting differs')
    rows.append(dict(profile=profile, cases=count, packets=packets, expected_pcm_bytes=pcm,
        original=str(original), generated=str(generated), actual_command=dict(path=str(receipt_path), **fact(receipt_path)),
        byte_identical_files=same, binary_files=sum(Path(r['path']).suffix in ('.bin', '.ogg') for r in same),
        permitted_differences=dict(pure_checks_fields=[before_key, after_key],
            manifest_fields=['source_inputs', 'files[pure-checks.json].bytes', 'files[pure-checks.json].sha256']),
        original_source_inputs=old_pure[before_key], canonical_source_inputs=expected_inputs,
        pure_checks_original=fact(original / 'pure-checks.json'), pure_checks_canonical=fact(generated / 'pure-checks.json'),
        manifest_original=fact(original / 'manifest.json'), manifest_canonical=fact(generated / 'manifest.json')))
need(sum(len(r['byte_identical_files']) for r in rows) == 149 and sum(r['binary_files'] for r in rows) == 145,
     'Expected all149 files /145 binary payloads')
result = dict(schema='vorbis-more-canonical-reproduction-v1', completed=True, profiles=rows,
    cases=29, packets=406, expected_pcm_bytes=689920, byte_identical_files=149,
    binary_files=145, provenance_only_changed_files=4, new_codec_or_target_executed=False,
    target_format_qualified=False, standard_conformance_qualified=False)
(OUT / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'profiles'}))
