"""Verify this archive offline. Reads archive files only; never runs tests/tools."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    root = parser.parse_args().root.resolve()

    def checked(relative):
        path = Path(relative)
        assert not path.is_absolute() and '..' not in path.parts, relative
        value = (root / path).resolve()
        assert root in value.parents, relative
        return value

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def load(relative):
        return json.loads(checked(relative).read_text(encoding='utf-8'))

    manifest = load('manifest.json')
    entries = manifest['files']
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    assert actual == set(entries) | {'manifest.json'}, 'Manifest coverage differs from files'
    assert manifest['file_count'] == len(entries)
    assert manifest['indexed_bytes'] == sum(v['bytes'] for v in entries.values())
    for relative, expected in entries.items():
        path = checked(relative)
        assert not path.is_symlink(), relative
        assert path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'], relative
        with path.open('rb') as stream:
            magic = stream.read(4)
        assert magic != b'\x7fELF' and not magic.startswith(b'MZ'), ('Binary executable/object copied', relative)

    mappings = load('source-mappings.json')['files']
    omitted = {k.replace('\\', '/'): v for k, v in load('omitted-artifacts.json')['files'].items()}
    for original, value in mappings.items():
        assert value['archive'] in entries, original
        assert entries[value['archive']]['sha256'] == value['sha256'], original
        assert entries[value['archive']]['bytes'] == value['bytes'], original

    def mapped(original, expected=None):
        key = original.replace('\\', '/')
        value = mappings[key]
        if expected:
            assert value['sha256'] == expected, original
        return checked(value['archive'])

    qualification = load('qualification.json')
    assert qualification['passed']
    for run in qualification['runs'].values():
        for relative, value in run.get('frozen_inputs', {}).items():
            mapped(run['origin'] + '/sources/' + relative, value['sha256'])
            assert value['current_before'] and value['current_after'], relative
    service = load('runs/service/report.json')
    startup = load('runs/startup/report.json')
    config = load('runs/config/report.json')
    assert service['passed'] and len(service['cases']) == 21 and len(service['negative_controls']) == 17
    assert service['complete_normal_module_source_matches_frozen_bytes']
    assert service['complete_canonical_queue_source_matches_frozen_bytes']
    assert not service['actual_sdk_allocator'] and not service['private_runtime_state_seeded']
    service_origin = qualification['runs']['service']['origin']
    for relative, expected in service['generated_sha256'].items():
        original = service_origin + '/' + relative
        if original in omitted:
            assert omitted[original]['sha256'] == expected
        else:
            mapped(original, expected)
    for name, value in service['negative_controls'].items():
        assert value['detected'] and value['exit_status'] == 80
        log = mapped(service_origin + '/mutants/' + name + '/run.log').read_bytes()
        assert log.startswith(('SEMANTIC_FAILURE:' + value['expected_marker'] + ':').encode()), name
        assert b'AddressSanitizer' not in log and b'runtime error:' not in log, name
    assert startup['passed'] and len(startup['variants']) == 12 and len(startup['negative_controls']) == 4
    assert all(value['passed'] and value['status'] == 0 for value in startup['variants'].values())
    startup_origin = qualification['runs']['startup']['origin']
    for name, value in startup['negative_controls'].items():
        assert value['detected'] and value['status'] == 80
        mapped(startup_origin + '/mutants/' + name + '/production.inc', value['generated_sha256'])
        log = mapped(startup_origin + '/mutants/' + name + '/test.log').read_bytes()
        assert log.startswith(('SEMANTIC_FAILURE:' + value['marker'] + ':').encode()), name
    assert config['passed'] and len(config['cases']) == 8 and all(value['passed'] for value in config['cases'].values())
    for name, value in config['cases'].items():
        mapped(qualification['runs']['config']['origin'] + '/' + name + '/configure.log', value['configure_log_sha256'])
    for name in ('startup-attempt-01', 'startup-attempt-02'):
        assert load('history/' + name + '/report.json')['passed'] is False

    lint = load('lint/raw/report.json')
    baseline = load('lint/baseline-output-telemetry-report.json')
    source_manifest = load('lint/raw/source-manifest.json')
    assert lint['complete'] and (lint['units'], lint['warnings'], lint['errors']) == (54, 86, 0)
    assert lint['captured_input_count'] == len(source_manifest['inputs']) == 661
    assert lint['all_inputs_unchanged_after_analysis']
    for original, value in source_manifest['inputs'].items():
        mapped(qualification['lint_origin'] + '/' + value['snapshot'], value['sha256'])

    def norm(value):
        value = value.replace('\\', '/')
        value = re.sub(r'^.*?/esp32-cyd-c3-review/', '', value)
        return re.sub(r'idf/esp32-cyd2usb-native/build-[^/]+/native-httpd-rfc6455/', 'httpd-overlay/', value)

    def diagnostics(report):
        return Counter((norm(unit['file']), norm(item['file']), item['severity'], item['check'], item['message'])
                       for unit in report['results'] for item in unit['diagnostics'])

    previous, current = diagnostics(baseline), diagnostics(lint)
    delta = load('lint/warning-delta.json')
    assert sum(current.values()) == 86 and current == previous
    assert delta['passed'] and not delta['added'] and not delta['removed']
    assert delta['current_report_sha256'] == sha(checked('lint/raw/report.json'))
    assert delta['baseline_report_sha256'] == sha(checked('lint/baseline-output-telemetry-report.json'))
    new_unit = [value for value in lint['results'] if value['file'].endswith('/native_input_reclaim.c')]
    assert len(new_unit) == 1 and not new_unit[0]['diagnostics']
    review = load('review/raw/review.json')
    assert review['passed'] and not review['actionable_findings']
    assert len(review['input_sha256']) == 1600
    for original, expected in review['input_sha256'].items():
        mapped(qualification['review_origin'] + '/' + review['snapshot_map'][original], expected)
        assert review['inputs_unchanged_after'][original] and review['snapshots_unchanged_after'][original]
    validation = load('review/raw/evidence-validation.json')
    assert validation['passed'] and validation['review_sha256'] == sha(checked('review/raw/review.json'))
    for original, expected in validation['checks'].items():
        key = original.replace('\\', '/')
        if key in omitted:
            assert omitted[key]['sha256'] == expected
        else:
            mapped(key, expected)
    print(json.dumps(dict(passed=True, offline=True, files=len(actual), indexed_bytes=manifest['indexed_bytes'],
                          service='21 cases / 17 controls', startup='12 configurations / 4 controls',
                          cmake_cases=8, clang='54 units / 86 warnings / 0 errors', clang_inputs=661,
                          warning_delta='empty', review_inputs=1600,
                          manifest_sha256=sha(checked('manifest.json'))), indent=2))


if __name__ == '__main__':
    main()
