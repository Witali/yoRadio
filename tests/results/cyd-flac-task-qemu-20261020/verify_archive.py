"""Verify this qualification archive offline; run no SDK, QEMU or board operation."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def archive_path(relative):
    path = (BASE / relative).resolve()
    assert path.is_relative_to(BASE) and path.is_file(), relative
    return path

def main():
    manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['passed'] and manifest['cases'] == ['T0', 'T1', 'T2']
    expected_files = set(manifest['files']) | {'manifest.json'}
    actual_files = {path.relative_to(BASE).as_posix() for path in BASE.rglob('*') if path.is_file()}
    assert actual_files == expected_files, (actual_files - expected_files, expected_files - actual_files)
    for name, row in manifest['files'].items():
        path = archive_path(name)
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], name
    bundle = json.loads(archive_path('raw/execution-bundle.json').read_text(encoding='utf-8'))
    report = json.loads(archive_path('raw/report.json').read_text(encoding='utf-8'))
    assert report['passed'] and report['all_bound_inputs_current']
    assert sha(archive_path('raw/execution-bundle.json')) == report['execution_bundle_sha256']
    for group, role in [('frozen_input_sha256', 'frozen_input'), ('artifact_sha256', 'artifact')]:
        for original, digest in bundle[group].items():
            row = manifest['input_artifact_mapping'][original]
            assert role in row['roles'] and row['sha256'] == digest
            assert sha(archive_path(row['archive_path'])) == digest, original
    raw_sources = json.loads(archive_path('raw/source-manifest.json').read_text(encoding='utf-8'))
    assert set(raw_sources) == set(manifest['source_mapping'])
    for original, row in raw_sources.items():
        archived = manifest['source_mapping'][original]
        assert all(archived[key] == row[key] for key in row), original
        assert sha(archive_path(archived['archive_path'])) == row['sha256'], original
    runtime = json.loads(archive_path('runtime-hashes.json').read_text(encoding='utf-8'))
    assert runtime['sha256'] == bundle['runtime_sha256']
    assert all(row['unchanged'] for group in report['post_run_verification'].values() for row in group.values())
    preflight = json.loads(archive_path('preflight/report.json').read_text(encoding='utf-8'))
    assert preflight['passed'] and len(preflight['cases']) == 15 and not preflight['build_or_qemu_started']
    terminal = json.loads(archive_path('terminal-observation.json').read_text(encoding='utf-8'))
    assert terminal['terminal'] and terminal['session_id'] == 82639 and terminal['exit_status'] == 0
    assert terminal['observed_result']['exit_code'] == 0
    print('PASS archived 3 actual-task cases; all', len(manifest['files']), 'file hashes,',
          len(manifest['input_artifact_mapping']), 'input/artifact mappings and 15 preflight cases')

if __name__ == '__main__':
    main()
