"""Bind final reports to actual files and preserve selected final link metadata."""
from pathlib import Path
import json
import re
import check

ROOT, HERE = check.ROOT, check.HERE
identity, git, require = check.identity, check.git, check.require
out = HERE / 'review'
require(not out.exists(), 'Fresh review directory required')
out.mkdir()
attempts = ['cyd-present-01', 'cyd-absent-01', 'c3-present-01', 'c3-absent-01']
report = {'schema': 'ota-component-audit-v1', 'status': 'RUNNING', 'source_commit': git('rev-parse', 'HEAD').decode().strip(),
          'full_application': False, 'hardware_tested': False, 'cases': [], 'tool': identity(__file__)}
try:
    changed = git('diff', '--name-only').decode().splitlines()
    require(changed == ['idf/components/native_ota/CMakeLists.txt'], 'Only authorized CMake source change')
    require(not git('diff', '--cached', '--name-only').decode().strip(), 'Agent made no index changes')
    (out / 'source.patch').write_bytes(git('diff', '--', changed[0]))
    report['source_patch'] = identity(out / 'source.patch')
    report['source_change'] = identity(ROOT / changed[0])
    report['unchanged_c3_and_ota_sources'] = []
    stable = ['idf/esp32c3-oled-native/CMakeLists.txt', 'idf/esp32c3-oled-native/main/CMakeLists.txt',
              'idf/esp32c3-oled-native/main/adaptive_input.c', 'idf/esp32c3-oled-native/main/icy_title.c']
    stable += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'idf/components/native_ota').rglob('*') if p.suffix in ['.c', '.h']]
    for name in stable:
        p = ROOT / name
        require(p.read_bytes().replace(b'\r\n', b'\n') == git('show', report['source_commit'] + ':' + name), 'Unchanged source: ' + name)
        report['unchanged_c3_and_ota_sources'].append(identity(p))
    baseline_c3 = json.loads((ROOT / 'firmware/development/esp32c3-oled-native-ap-timeout/project_description.json').read_bytes())
    require('native_stream' not in baseline_c3['build_component_info'], 'Actual C3 baseline does not discover stream component')
    for name in attempts:
        run = HERE / name
        p = run / ('qualification-02.json' if name == 'cyd-present-01' else 'qualification.json')
        q = json.loads(p.read_bytes())
        require(q['status'] == 'PASS' and q['returncode'] == 0 and not q['new_source_warnings'], 'Terminal scoped qualification PASS')
        require(q['source_commit'] == report['source_commit'] and identity(q['qualification_tool']['path']) == q['qualification_tool'], 'Current commit/qualifier identity')
        for key in ['sources_before', 'sources_after', 'baseline', 'logs', 'tools', 'headers', 'generated', 'response_files', 'sdk_cmake']:
            for row in q[key]: require(identity(row['path']) == row, 'Current frozen artifact: ' + row['path'])
        for row in q['compile_results']:
            for key in ['source', 'object']: require(identity(row[key]['path']) == row[key], 'Actual OTA source/object')
        require(identity(q['library']['path']) == q['library'], 'Actual OTA static archive')
        build = Path(json.loads((run / 'invocation.json').read_bytes())['build'])
        ninja = build / 'build.ninja'
        raw = ninja.read_bytes()
        selected = [(offset, line) for offset, line in []]
        offset = 0
        for line in raw.splitlines(keepends=True):
            if line.startswith(b'  LINK_LIBRARIES = '): selected.append((offset, line))
            offset += len(line)
        relevant = [(offset, line) for offset, line in selected if b'libnative_ota.a' in line]
        require(len(relevant) == 1, 'One actual final app link metadata row')
        offset, line = relevant[0]
        selected_path = out / (name + '-link-row.txt')
        selected_path.write_bytes(line)
        whole = False
        stream_archives = []
        for token in line.decode().split():
            if '--no-whole-archive' in token: whole = False
            elif '--whole-archive' in token: whole = True
            if 'libnative_stream.a' in token: stream_archives.append({'token': token, 'whole_archive': whole})
        require(not any(x['whole_archive'] for x in stream_archives), 'No forced whole-archive stream linking')
        require(bool(stream_archives) == (q['stream'] == 'present'), 'Generated link metadata follows component presence')
        stderr = (run / 'stderr.log').read_text(encoding='utf-8')
        traces = [x for x in stderr.splitlines() if 'FileNotFoundError:' in x]
        require(len(traces) == q['missing_partition_tracebacks'], 'Exact traceback count')
        if traces:
            require(name == 'c3-absent-01' and len(traces) == 5, 'Only accepted historical missing partition diagnostics')
            require(all(str(run / 'project/partitions.csv').replace('\\', '/') in x.replace('\\', '/') for x in traces), 'All tracebacks concern only the omitted isolated partition CSV')
        report['cases'].append({'attempt': name, 'qualification': identity(p), 'target': q['target'], 'stream': q['stream'],
            'ota_translation_units': len(q['compile_results']), 'common_config_changes': len(q['common_config_changes']),
            'unavailable_symbols': len(q['normalized_config_changes']), 'new_source_warnings': len(q['new_source_warnings']),
            'baseline_diagnostic_bodies': len(q['baseline_warnings']), 'harness_advisories': q['harness_advisories'],
            'partition_tracebacks': traces, 'generated_link_metadata': {'original': identity(ninja), 'offset_bytes': offset,
                'selected_row': identity(selected_path), 'native_stream_archives': stream_archives,
                'scope': 'configuration-generated metadata; full application linker not executed'}})
    require(len(report['cases']) == 4 and sum(x['ota_translation_units'] for x in report['cases']) == 12, 'Complete four-case actual component matrix')
    report['status'] = 'PASS'
except Exception as exc:
    report['status'], report['failure'] = 'FAIL', repr(exc)
    raise
finally:
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'report': identity(out / 'report.json')}))
