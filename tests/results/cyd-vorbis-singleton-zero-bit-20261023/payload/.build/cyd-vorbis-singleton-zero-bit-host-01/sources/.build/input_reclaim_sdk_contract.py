"""Strict metadata prerequisites for the seven actual SDK export checks."""
from pathlib import Path
import hashlib
import json
import os

PREFIX = 'esp32-cyd2usb-native-tls-input-reclaim-'
BASELINE = 'esp32-cyd2usb-native-output-telemetry-'
EXPECTED = {
    **{('custom-flac-' if custom else '') + backend: (backend, custom, True)
       for custom in (False, True) for backend in ('pdm', 'continuous', 'legacy')},
    'disabled-pdm': ('pdm', False, False),
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def longpaths():
    count = int(os.environ.get('GIT_CONFIG_COUNT', '0'))
    os.environ['GIT_CONFIG_KEY_' + str(count)] = 'core.longpaths'
    os.environ['GIT_CONFIG_VALUE_' + str(count)] = 'true'
    os.environ['GIT_CONFIG_COUNT'] = str(count + 1)

def profiles(root, rows):
    assert len(rows) == 7, 'exact_seven_profiles'
    names = [row['name'] for row in rows]
    assert len(set(names)) == 7 and set(names) == set(EXPECTED), 'exact_profile_set'
    for row in rows:
        backend, custom, enabled = EXPECTED[row['name']]
        assert type(row['custom_flac']) is bool and type(row['enabled']) is bool, 'profile_bool_types'
        assert (row['backend'], row['custom_flac'], row['enabled']) == (backend, custom, enabled), 'profile_selection'
        assert row['variant'] == PREFIX + row['name'], 'profile_variant'
        suffix = ('custom-flac-' if custom else '') + backend
        assert Path(row['baseline']).resolve() == (root / 'firmware/development' / (BASELINE + suffix)).resolve(), 'baseline_selection'
        build = Path(row['build_directory']).resolve()
        assert build != root and build.is_relative_to(root), 'build_below_repository'
        assert Path(row['sdkconfig']).resolve() == build / 'sdkconfig', 'profile_sdkconfig'
    for key in ('variant', 'build_directory', 'sdkconfig'):
        values = [str(Path(row[key]).resolve()).casefold() if key != 'variant' else row[key] for row in rows]
        assert len(set(values)) == 7, 'unique_' + key

def baseline(root, row, git):
    folder = Path(row['baseline']).resolve()
    for name in ('manifest.json', 'sdkconfig', 'sdkconfig.json'):
        path = folder / name
        relative = path.relative_to(root).as_posix()
        assert path.read_bytes() == git('show', 'HEAD:' + relative), 'committed_baseline_' + name
    receipt = json.loads((folder / 'manifest.json').read_text())
    assert receipt['build_check'] == 'PASS' and receipt['source_dirty'] is False, 'qualified_baseline'
    assert receipt['target'] == 'esp32' and receipt['backend'] == row['backend'], 'baseline_target_backend'
    assert sha(folder / 'sdkconfig') == row['baseline_sdkconfig_sha256'] == receipt['sdkconfig_sha256'], 'baseline_sdkconfig_hash'
    assert sha(folder / 'sdkconfig.json') == receipt['sdkconfig_json_sha256'], 'baseline_json_hash'
    return json.loads((folder / 'sdkconfig.json').read_text())

def evidence(root, row):
    names = ['tests/results/cyd-input-reclaim-20261020/README.md',
             'tests/results/cyd-http-request-buffer-20261020/README.md']
    if row['custom_flac']:
        names.append('tests/results/cyd-flac-runtime-20261019/README.md')
    return {str((root / name).resolve()): sha(root / name) for name in names}

def source(snapshot, marker):
    assert snapshot['commit'] == marker['source_commit'], 'source_head'
    assert snapshot['source_dirty'] is False and not snapshot['untracked'], 'current_source_clean'
    assert snapshot['content_sha256'] == marker['source_content_sha256'], 'current_source_content'
    expected = {key: value for key, value in marker['source_snapshot'].items() if key != 'dirty'}
    actual = {key: value for key, value in snapshot.items() if key != 'dirty'}
    assert actual == expected, 'complete_source_snapshot'

def receipt(value, row, marker, expected_evidence):
    assert value['source_commit'] == marker['source_commit'] and value['source_dirty'] is False, 'receipt_source'
    assert not value['source_untracked'] and value['source_content_sha256'] == marker['source_content_sha256'], 'receipt_source_content'
    assert value['source_excluded_paths'] == marker['source_snapshot']['excluded_paths'], 'receipt_exclusions'
    assert value['variant'] == row['variant'] and value['backend'] == row['backend'], 'receipt_profile'
    assert Path(value['build_directory']).resolve() == Path(row['build_directory']).resolve(), 'receipt_build_directory'
    assert value['sdkconfig_seed']['source_sha256'] == row['prepared_sdkconfig_sha256'], 'actual_prepared_seed'
    refs = value['evidence']
    assert len(refs) == len(expected_evidence), 'intended_evidence_count'
    actual = {str(Path(ref['path']).resolve()): ref['sha256'] for ref in refs}
    assert len(actual) == len(refs) and actual == expected_evidence, 'intended_evidence_set'
