"""One-time byte-copy assembly; no test, build, Git, network or tool execution."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
assert OUT == ROOT / 'tests/results/cyd-input-reclaim-20261020'
assert not (OUT / 'manifest.json').exists(), 'Completed archive cannot be replaced'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
mapping, omitted, before = {}, {}, {}


def dump(relative, value):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def binary(path):
    with path.open('rb') as stream:
        data = stream.read(4)
    return data == b'\x7fELF' or data.startswith(b'MZ')


def copy(source, destination):
    source = source.resolve()
    original = source.as_posix()
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    before[original] = digest
    if binary(source):
        omitted[original] = dict(sha256=digest, bytes=len(data), reason='Executable/object binary omitted; raw reports, source, commands and logs retained')
        return
    destination = Path(destination)
    target = OUT / destination
    if len(str(target)) > 240:
        destination = Path('long-paths') / (hashlib.sha256(str(destination).encode()).hexdigest() + source.suffix)
        target = OUT / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == data, str(target)
    else:
        target.write_bytes(data)
    mapping[original] = dict(archive=destination.as_posix(), sha256=digest, bytes=len(data))
    assert sha(target) == digest


def tree(original, prefix, flatten=False):
    directory = ROOT / original
    for source in sorted(directory.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(directory)
        if flatten and relative.parts[0] in ('sources', 'dependency-sources'):
            relative = Path('snapshots') / (sha(source) + source.suffix)
        copy(source, Path(prefix) / relative)


run_dirs = {'service': '.build/cyd-input-reclaim-host-01',
            'startup': '.build/cyd-startup-reclaim-03',
            'config': '.build/cyd-input-reclaim-config-01'}
runs = {}
reports = {}
for name, directory in run_dirs.items():
    origin = ROOT / directory
    tree(directory, 'runs/' + name)
    report = json.loads((origin / 'report.json').read_text())
    assert report['passed']
    reports[name] = report
    inputs = {}
    for relative, digest in report['source_sha256'].items():
        assert sha(ROOT / relative) == sha(origin / 'sources' / relative) == digest, (name, relative)
        inputs[relative] = dict(sha256=digest, current_before=True)
    runs[name] = dict(origin=origin.as_posix(), report_sha256=sha(origin / 'report.json'), frozen_inputs=inputs)
for number in ('01', '02'):
    directory = '.build/cyd-startup-reclaim-' + number
    tree(directory, 'history/startup-attempt-' + number)
    assert json.loads((ROOT / directory / 'report.json').read_text())['passed'] is False

lint_origin = ROOT / '.build/lint-cyd-input-reclaim-01'
tree('.build/lint-cyd-input-reclaim-01', 'lint/raw', flatten=True)
lint = json.loads((lint_origin / 'report.json').read_text())
lint_manifest = json.loads((lint_origin / 'source-manifest.json').read_text())
assert lint['complete'] and (lint['units'], lint['warnings'], lint['errors']) == (54, 86, 0)
assert lint['captured_input_count'] == len(lint_manifest['inputs']) == 661
lint_inputs = {}
for original, value in lint_manifest['inputs'].items():
    assert sha(Path(original)) == sha(lint_origin / value['snapshot']) == value['sha256'], original
    lint_inputs[original] = value['sha256']
baseline = ROOT / '.build/lint-cyd-output-telemetry-01/report.json'
copy(baseline, 'lint/baseline-output-telemetry-report.json')
old = json.loads(baseline.read_text())


def normalized(value):
    value = value.replace('\\', '/')
    value = re.sub(r'^.*?/esp32-cyd-c3-review/', '', value)
    return re.sub(r'idf/esp32-cyd2usb-native/build-[^/]+/native-httpd-rfc6455/', 'httpd-overlay/', value)


def diagnostics(report):
    return Counter((normalized(unit['file']), normalized(item['file']), item['severity'], item['check'], item['message'])
                   for unit in report['results'] for item in unit['diagnostics'])


previous, current = diagnostics(old), diagnostics(lint)
assert previous == current and sum(current.values()) == 86
assert (old['units'], old['warnings'], old['errors']) == (53, 86, 0)
new_unit = [v for v in lint['results'] if v['file'].endswith('/native_input_reclaim.c')]
assert len(new_unit) == 1 and not new_unit[0]['diagnostics']
dump('lint/warning-delta.json', dict(passed=True, baseline_units=53, current_units=54,
                                  baseline_warnings=86, current_warnings=86, added=[], removed=[],
                                  baseline_report_sha256=sha(baseline), current_report_sha256=sha(lint_origin / 'report.json'),
                                  normalization='Preserve unit/logical diagnostic file/severity/check/full message/multiplicity; normalize worktree and generated HTTPD build paths; ignore line/column offsets.',
                                  current_multiset=[dict(unit=k[0], file=k[1], severity=k[2], check=k[3], message=k[4], count=v)
                                                    for k,v in sorted(current.items())]))

review_origin = ROOT / '.build/cyd-input-reclaim-review-01'
tree('.build/cyd-input-reclaim-review-01', 'review/raw')
review = json.loads((review_origin / 'review.json').read_text())
assert review['passed'] and not review['actionable_findings'] and len(review['input_sha256']) == 1600
for original, digest in review['input_sha256'].items():
    assert sha(Path(original)) == sha(review_origin / review['snapshot_map'][original]) == digest, original
validation = json.loads((review_origin / 'evidence-validation.json').read_text())
for original, digest in validation['checks'].items():
    source = Path(original)
    assert sha(source) == digest
    if source.resolve().as_posix() not in mapping and source.resolve().as_posix() not in omitted:
        copy(source, Path('review/validation-inputs') / (digest + source.suffix))

# Capture configure stdout/stderr/helpers when available, without inferring a
# successful build or changing the completed analysis evidence.
for source in sorted((ROOT / '.build').glob('*input-reclaim*')):
    if source.is_file() and source.suffix in ('.log', '.py', '.ps1'):
        copy(source, Path('lint/configure-context') / source.name)

assert sha(OUT / 'README.md') == 'fefbb20380ddb9068d25a216e51530bd612d9277aeaaec4a3ad65a5187ccc710'
assert sha(OUT / 'HOST.md') == '193371849ad4bcc2e110c54c98b9421b7736c8ee1290c564ac0a6eaa350d104f'
for name, run in runs.items():
    for relative, value in run['frozen_inputs'].items():
        value['current_after'] = sha(ROOT / relative) == value['sha256']
        assert value['current_after'], (name, relative)
for original, digest in lint_inputs.items():
    assert sha(Path(original)) == digest, original
for original, digest in before.items():
    assert sha(Path(original)) == digest, original
for value in mapping.values():
    assert sha(OUT / value['archive']) == value['sha256']
dump('source-mappings.json', dict(scope='Raw byte mappings; original paths in raw reports are unchanged. Mappings resolve those originals to archive paths, including flattened long paths.', files=mapping))
dump('omitted-artifacts.json', dict(scope='Executable/object binaries are intentionally absent. Hash records preserve identities; offline verification does not require originals.', files=omitted))
dump('qualification.json', dict(passed=True, captured_utc=datetime.now(timezone.utc).isoformat(), runs=runs,
                               lint_origin=lint_origin.as_posix(), review_origin=review_origin.as_posix(),
                               lint_input_sha256=lint_inputs, copied_raw_files_verified_before_after=len(mapping),
                               pending_at_host_checkpoint=['Actual target QEMU allocator/OOM/health integration', 'Production SDK application exports and final linker evidence'],
                               source_revision_context_from_parent={'integration':'ef3204b2c', 'docs_status':'7e770a83d'},
                               historical_failures={'01':'Frozen include closure omitted transitive stream_tags.h',
                                                    '02':'Stale fixture ESP_ERR_TIMEOUT and native_audio_output_request_pause seams'},
                               boundaries=['Host service models SDK calloc/heap/RTOS, not actual SDK OOM.',
                                           'Reviewer authored startup tests; production-service/root-wiring review is independently authored.',
                                           'Startup observe_health_failure is an SDK failed-allocation callback SEAM, not execution of actual native_health.c.',
                                           'Clang is static analysis. No target ABI/link/wrapper execution, physical/RF/DMA/latency/performance claim.'],
                               readme_sha256=sha(OUT / 'README.md'), host_sha256=sha(OUT / 'HOST.md')))
entries = {}
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path != OUT / 'manifest.json':
        entries[path.relative_to(OUT).as_posix()] = dict(sha256=sha(path), bytes=path.stat().st_size)
dump('manifest.json', dict(schema=1, scope='Every archive file except this manifest. Raw evidence and frozen README/HOST remain unchanged; later SDK appendices need manifest coverage.',
                          files=entries, file_count=len(entries), indexed_bytes=sum(v['bytes'] for v in entries.values())))
print(json.dumps(dict(passed=True, files=len(entries)+1, indexed_bytes=sum(v['bytes'] for v in entries.values()),
                      copied_raw_files=len(mapping), omitted_binaries=len(omitted),
                      manifest_sha256=sha(OUT / 'manifest.json'), qualification_sha256=sha(OUT / 'qualification.json'),
                      verifier_sha256=sha(OUT / 'verify.py')), indent=2))
