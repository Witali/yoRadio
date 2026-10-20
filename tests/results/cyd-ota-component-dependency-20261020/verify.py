"""Offline integrity and scope checks; never accesses the original checkout."""
from pathlib import Path
import gzip
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()
manifest = json.loads((ROOT / 'manifest.json').read_bytes())
expected = {x['path']: x for x in manifest['files']}
actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p != ROOT / 'manifest.json'}
assert len(expected) == len(manifest['files']) and set(expected) == actual
for name, row in expected.items():
    p = (ROOT / name).resolve()
    assert p.is_relative_to(ROOT)
    raw = p.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
mapping = json.loads((ROOT / 'path-map.json').read_bytes())['entries']
by_path = {}
for row in mapping:
    assert row['path'] not in by_path or by_path[row['path']] == row
    by_path[row['path']] = row
    assert re.fullmatch('[0-9a-f]{64}', row['sha256']) and row['bytes'] >= 0
    if 'stored' in row:
        p = (ROOT / row['stored']).resolve()
        assert p.is_relative_to(ROOT)
        raw = p.read_bytes()
        if row['encoding'] == 'gzip': raw = gzip.decompress(raw)
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    else: assert row['omission']

def bound(row, stored=False):
    got = by_path[row['path']]
    assert got['bytes'] == row['bytes'] and got['sha256'] == row['sha256']
    if stored: assert 'stored' in got

def original_bytes(row):
    bound(row, True)
    item = by_path[row['path']]
    raw = (ROOT / item['stored']).read_bytes()
    return gzip.decompress(raw) if item['encoding'] == 'gzip' else raw

targets = []
reports = {}
for attempt in ['cyd-present-01', 'cyd-absent-01', 'c3-present-01', 'c3-absent-01']:
    report = json.loads((ROOT / attempt / 'report.json').read_bytes())
    assert report['status'] == 'PASS' and report['returncode'] == 0
    target = report['target']
    reports[attempt] = report
    targets.append((target, report['stream']))
    expected_sdk = '7101770dc6db2667b3c477cc31365dd1acd6db4e' if target == 'esp32' else '9a97f6c54ec638111ce55cd36581b3c192f15207'
    assert report['sdk_before'] == report['sdk_after'] and report['sdk_before']['commit'] == expected_sdk
    assert report['sdk_before']['status'] == ''
    assert report['sources_before'] == report['sources_after']
    assert report['source_status_before'] == report['source_status_after']
    assert not report['full_application'] and not report['hardware_tested']
    assert report['new_source_warnings'] == []
    assert len(report['harness_advisories']) <= 1
    assert report['common_config_changes'] == {}
    assert report['new_warnings'] == [x['body'] for x in report['harness_advisories']]
    if attempt == 'cyd-present-01': assert report['harness_advisories'][0]['kind'] == 'long isolated build path'
    if attempt == 'c3-absent-01': assert report['harness_advisories'][0]['kind'] == 'isolated project omitted partition CSV'
    if attempt not in ['cyd-present-01', 'c3-absent-01']: assert report['harness_advisories'] == [] and report['new_warnings'] == []
    if target == 'esp32' and report['stream'] == 'present': assert report['normalized_config_changes'] == {}
    else: assert report['isolated_project']
    graph = report['component_graph']['native_ota']
    assert 'lwip' in graph['priv_reqs']
    props = report['target_properties']
    if report['stream'] == 'present':
        assert '__idf_native_stream' in props['LINK_LIBRARIES'].split(';')
        assert '$<LINK_ONLY:__idf_native_stream>' in props['INTERFACE_LINK_LIBRARIES'].split(';')
        assert '__idf_native_stream' not in props['INTERFACE_LINK_LIBRARIES'].split(';')
    else:
        assert report['component_graph']['native_stream'] is None and props['NATIVE_STREAM_TYPE'] == 'absent'
        assert '__idf_native_stream' not in props['LINK_LIBRARIES'] + props['INTERFACE_LINK_LIBRARIES']
    assert len(report['compile_results']) == 3
    assert {x['source']['path'].replace('\\', '/').rsplit('/', 1)[-1] for x in report['compile_results']} == {'native_ota_http.c', 'native_ota_form.c', 'native_ota_sink.c'}
    stdout = original_bytes(next(x for x in report['logs'] if x['path'].endswith('stdout.log'))).decode('utf-8')
    stderr = original_bytes(next(x for x in report['logs'] if x['path'].endswith('stderr.log'))).decode('utf-8')
    assert not re.findall(r'^.*warning:.*$', stdout + stderr, re.M | re.I)
    for row in report['compile_results']:
        assert row['elf_machine'] == (94 if target == 'esp32' else 243)
        assert row['actual_stdout_row'] and ' -c ' in row['actual_stdout_row']
        assert row['actual_stdout_row'] in stdout.splitlines()
        assert '/native_stream/include' in row['command']['command'].replace('\\', '/')
        bound(row['source'], True)
        bound(row['object'])
    for key in ['sources_before', 'baseline', 'logs', 'tools', 'headers', 'generated', 'response_files', 'sdk_cmake']:
        for row in report[key]: bound(row, key in ['sources_before', 'baseline', 'logs', 'response_files'])
    for row in report.get('tools_before', []): bound(row)
    bound(report['original_runner']['report'], True)
    bound(report['baseline_warning_log'], True)
    bound(report['qualification_tool'], True)
    bound(report['library'])
    seed = report['sdkconfig_seed']
    baseline_seed = next(x for x in report['baseline'] if x['path'].replace('\\', '/').endswith('/sdkconfig'))
    assert seed['bytes'] == baseline_seed['bytes'] and seed['sha256'] == baseline_seed['sha256']
    assert len(original_bytes(baseline_seed)) == seed['bytes']
    baseline_json = next(x for x in report['baseline'] if x['path'].replace('\\', '/').endswith('/sdkconfig.json'))
    generated_json = next(x for x in report['generated'] if x['path'].replace('\\', '/').endswith('/config/sdkconfig.json'))
    before_config = json.loads(original_bytes(baseline_json))
    after_config = json.loads(original_bytes(generated_json))
    actual_changes = {key: {'before': before_config.get(key), 'after': after_config.get(key)}
                      for key in before_config.keys() | after_config.keys()
                      if before_config.get(key) != after_config.get(key)}
    actual_common_changes = {key: value for key, value in actual_changes.items()
                             if key in before_config and key in after_config}
    assert actual_changes == report['normalized_config_changes']
    assert actual_common_changes == report['common_config_changes'] == {}
    assert after_config['IDF_TARGET'] == target
    if target == 'esp32' and report['stream'] == 'present': assert actual_changes == {}
    tracebacks = [x for x in stderr.splitlines() if 'FileNotFoundError:' in x]
    assert len(tracebacks) == report['missing_partition_tracebacks']
    if tracebacks:
        assert attempt == 'c3-absent-01' and len(tracebacks) == 5
        assert all('/c3-absent-01/project/partitions.csv' in x.replace('\\', '/') for x in tracebacks)
assert set(targets) == {('esp32', 'present'), ('esp32', 'absent'), ('esp32c3', 'present'), ('esp32c3', 'absent')}
audit = json.loads((ROOT / 'review/report.json').read_bytes())
assert audit['status'] == 'PASS' and not audit['full_application'] and not audit['hardware_tested']
assert len(audit['cases']) == 4 and sum(x['ota_translation_units'] for x in audit['cases']) == 12
bound(audit['tool'], True)
bound(audit['source_change'], True)
bound(audit['source_patch'], True)
for row in audit['unchanged_c3_and_ota_sources']: bound(row, True)
for row in audit['cases']:
    q = reports[row['attempt']]
    bound(row['qualification'], True)
    selected = row['generated_link_metadata']
    bound(selected['original'])
    link = original_bytes(selected['selected_row']).decode('utf-8')
    whole = False
    archives = []
    for token in link.split():
        if '--no-whole-archive' in token: whole = False
        elif '--whole-archive' in token: whole = True
        if 'libnative_stream.a' in token: archives.append({'token': token, 'whole_archive': whole})
    assert archives == selected['native_stream_archives']
    assert bool(archives) == (q['stream'] == 'present') and not any(x['whole_archive'] for x in archives)
history = json.loads((ROOT / 'history.json').read_bytes())
first = json.loads((ROOT / history['initial_qualification']['report']).read_bytes())
old_tool = (ROOT / history['initial_qualification']['tool']).read_bytes()
assert first['status'] == 'FAIL' and first['qualification_tool']['sha256'] == sha(old_tool)
assert len(history['runner_failures']) == 2
for row in history['runner_failures']:
    old = json.loads((ROOT / row['report']).read_bytes())
    assert old['status'] == row['status'] == 'FAIL' and old['returncode'] == row['actual_sdk_launcher_returncode'] == 0
    assert old['failure'] == row['failure'] == "KeyError('PYTHON')"
    assert reports[row['attempt']]['original_runner']['status'] == 'FAIL'
assert b'belongs to component native_stream' in (ROOT / 'original-warning.log').read_bytes()
print(json.dumps({'status': 'PASS', 'targets': targets, 'files': len(expected) + 1,
                  'scope': 'archived actual SDK component compile/dependency evidence only'}))
