"""One-time evidence assembly. Writes only beside this script; no builds or I/O.

The only child commands read installed WSL tool versions/hashes. Bound source
trees and reports are never modified. Refuses to replace a completed manifest.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
REPOSITORY = Path('C:/Work/yoRadio')
assert OUT == ROOT / 'tests/results/cyd-output-telemetry-20261020'
assert not (OUT / 'manifest.json').exists(), 'Completed archive is immutable'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(relative, value):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


mapping, omitted, before = {}, [], {}
bindings, dependency_bindings = {}, {}


def copy(source, relative):
    source = source.resolve()
    raw = source.read_bytes()
    expected = hashlib.sha256(raw).hexdigest()
    before[str(source)] = expected
    relative = Path(relative)
    target = OUT / relative
    if len(str(target)) > 240:
        relative = Path('long-paths') / (hashlib.sha256(str(relative).encode()).hexdigest() + source.suffix)
        target = OUT / relative
    if target.exists():
        assert target.read_bytes() == raw, str(target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    assert digest(target) == expected
    mapping[str(source)] = dict(archive=relative.as_posix(), sha256=expected, bytes=len(raw))
    return relative.as_posix()


def linux_object(path):
    with path.open('rb') as stream:
        magic = stream.read(20)
    return len(magic) == 20 and magic[:4] == b'\x7fELF' and int.from_bytes(magic[18:20], 'little') == 62


def tree(name, prefix):
    directory = ROOT / '.build' / name
    for source in sorted(directory.rglob('*')):
        if not source.is_file():
            continue
        if linux_object(source):
            omitted.append(dict(original=str(source), sha256=digest(source), bytes=source.stat().st_size,
                                reason='Replaceable host Linux x86-64 executable/object; reports/logs/source retained'))
            continue
        relative = source.relative_to(directory)
        if name.startswith('lint-') and relative.parts[0] in ('sources', 'dependency-sources'):
            relative = Path('snapshots') / (digest(source) + source.suffix)
        copy(source, Path(prefix) / relative)


def verify_report(name):
    directory = ROOT / '.build' / name
    report = json.loads((directory / 'report.json').read_text())
    assert report['passed'], name
    checks = {}
    for original, expected in report.get('source_sha256', report.get('sources', {})).items():
        current = ROOT / original
        frozen = directory / 'sources' / original
        assert digest(current) == expected and digest(frozen) == expected, (name, original)
        checks[original] = dict(sha256=expected, current_before=True, frozen=True)
    bindings[name] = checks
    return report


RUNS = [
    'cyd-output-metrics-03', 'cyd-output-metrics-review-01', 'cyd-output-telemetry-01',
    'cyd-telemetry-regression-output-pause-01', 'cyd-telemetry-regression-output-gain-03',
    'cyd-telemetry-regression-normalizer-03', 'cyd-telemetry-regression-pcm-layout-03',
    'cyd-telemetry-regression-maintenance-01', 'cyd-output-telemetry-verification-01',
    'cyd-health-output-telemetry-01', 'cyd-stream-output-telemetry-03',
    'cyd-output-telemetry-independent-review-01',
]
for name in RUNS:
    tree(name, 'runs/' + name)
for name in ('cyd-stream-output-telemetry-01', 'cyd-stream-output-telemetry-02'):
    tree(name, 'history/' + name)

reports = {}
for name in RUNS:
    if name in ('cyd-output-metrics-review-01', 'cyd-output-telemetry-independent-review-01'):
        continue
    reports[name] = verify_report(name)

compile_report = json.loads((ROOT / '.build/cyd-output-metrics-review-01/compile-report.json').read_text())
assert compile_report['passed']
for variant, values in compile_report['variants'].items():
    for original, expected in values['dependency_sha256'].items():
        path = Path(original)
        assert digest(path) == expected, original
        dependency_bindings[original] = expected
        if str(path.resolve()) not in mapping:
            copy(path, Path('sdk-object-inputs') / (hashlib.sha256(original.encode()).hexdigest() + path.suffix))
for original, expected in compile_report['baseline_sha256'].items():
    path = Path(original)
    assert digest(path) == expected, original
    dependency_bindings[original] = expected
    if path.suffix == '.elf':
        omitted.append(dict(original=original, sha256=expected, bytes=path.stat().st_size,
                            reason='Existing baseline production ELF: bound by hash; full symbols/selected disassembly and map retained; not a new application build'))
    elif str(path.resolve()) not in mapping:
        copy(path, Path('sdk-object-inputs') / (hashlib.sha256(original.encode()).hexdigest() + path.suffix))
for original, expected in compile_report['tools_sha256'].items():
    assert digest(Path(original)) == expected
    dependency_bindings[original] = expected

review = json.loads((ROOT / '.build/cyd-output-telemetry-independent-review-01/review.json').read_text())
assert review['passed'] and not review['actionable_findings']
review_checks = {}
for original, expected in review['input_sha256'].items():
    assert digest(Path(original)) == expected, original
    snapshot = ROOT / '.build/cyd-output-telemetry-independent-review-01' / review['snapshot_map'][original]
    assert digest(snapshot) == expected, original
    review_checks[original] = dict(sha256=expected, current_before=True, frozen=True)
bindings['independent-review'] = review_checks

# Preserve the complete Clang closure, including raw YAML and dependency logs.
tree('lint-cyd-output-telemetry-01', 'lint/raw')
for source in sorted((ROOT / '.build').glob('output-telemetry-lint-configure-cyd-02.*.log')):
    copy(source, Path('lint/configure') / source.name)
lint_dir = ROOT / '.build/lint-cyd-output-telemetry-01'
lint = json.loads((lint_dir / 'report.json').read_text())
lint_manifest = json.loads((lint_dir / 'source-manifest.json').read_text())
assert lint['complete'] and lint['errors'] == 0 and lint['units'] == 53 and lint['warnings'] == 86
assert lint['captured_input_count'] == 656 and lint['all_inputs_unchanged_after_analysis']
lint_checks = {}
for original, entry in lint_manifest['inputs'].items():
    snapshot = lint_dir / entry['snapshot']
    assert digest(Path(original)) == entry['sha256'] and digest(snapshot) == entry['sha256'], original
    lint_checks[original] = dict(sha256=entry['sha256'], current_before=True, frozen=True,
                               archive=mapping[str(snapshot.resolve())]['archive'])
bindings['lint-656-inputs'] = lint_checks
baseline = ROOT / 'tests/results/cyd-network-settings-20261020/lint/report.json'
copy(baseline, 'lint/baseline-n5-report.json')
old = json.loads(baseline.read_text())
assert old['complete'] and old['units'] == 52 and old['warnings'] == 86 and old['errors'] == 0


def normalized(path):
    path = path.replace('\\', '/')
    path = re.sub(r'^.*?/esp32-cyd-c3-review/', '', path)
    return re.sub(r'idf/esp32-cyd2usb-native/build-[^/]+/native-httpd-rfc6455/', 'httpd-overlay/', path)


def diagnostics(report):
    counts = Counter()
    for unit in report['results']:
        for diagnostic in unit['diagnostics']:
            counts[(normalized(unit['file']), normalized(diagnostic['file']), diagnostic['severity'],
                    diagnostic['check'], diagnostic['message'])] += 1
    return counts


old_counts, new_counts = diagnostics(old), diagnostics(lint)
assert sum(old_counts.values()) == sum(new_counts.values()) == 86
assert old_counts == new_counts
metrics_units = [item for item in lint['results'] if item['file'].endswith('/native_output_metrics.c')]
assert len(metrics_units) == 1 and not metrics_units[0]['diagnostics']
comparison = dict(passed=True, baseline_sha256=digest(baseline),
                  current_report_sha256=digest(lint_dir / 'report.json'),
                  baseline_units=52, current_units=53, baseline_warnings=86, current_warnings=86,
                  added=[], removed=[], new_metrics_diagnostics=[],
                  normalization='Replace Windows separators and worktree prefix; normalize generated HTTPD build directory. Compare translation unit + diagnostic logical file + severity + check + complete message with multiplicities. Ignore line/column offsets only.',
                  normalized_multiset=[dict(unit=k[0], file=k[1], severity=k[2], check=k[3], message=k[4], count=v)
                                       for k, v in sorted(new_counts.items())])
dump('lint/diagnostic-comparison.json', comparison)

# Retrospective installed host tool metadata; original test compiler logs are
# authoritative run-time records. These probes do not rerun any test or build.
tool_records = []
commands = [('gcc-version', ['/usr/bin/gcc', '--version']),
            ('gxx-version', ['/usr/bin/g++', '--version']),
            ('host-tools-sha256', ['/usr/bin/sha256sum', '/usr/bin/gcc', '/usr/bin/g++', '/usr/bin/ld', '/usr/bin/as'])]
for name, command in commands:
    result = subprocess.run(['wsl.exe', '--exec', *command], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=30)
    assert result.returncode == 0
    destination = OUT / 'tool-metadata' / (name + '.log')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(result.stdout)
    tool_records.append(dict(command=['wsl.exe', '--exec', *command], status=result.returncode,
                             log=destination.relative_to(OUT).as_posix(), sha256=digest(destination)))
dump('tool-metadata/probes.json', dict(scope='Installed tool metadata captured during archive assembly; not historical binary identity proof for prior host runs.',
                                    probes=tool_records, python=sys.version, python_path=sys.executable,
                                    python_sha256=digest(Path(sys.executable)), clang=lint_manifest['tool'],
                                    xtensa=compile_report['tools_sha256'], sdk_commit=compile_report['sdk_commit']))

# Recheck live source/dependency bindings after every byte copy and tool probe.
for name, entries in bindings.items():
    for original, value in entries.items():
        path = Path(original) if Path(original).is_absolute() else ROOT / original
        value['current_after'] = digest(path) == value['sha256']
        assert value['current_after'], (name, original)
for original, expected in dependency_bindings.items():
    assert digest(Path(original)) == expected, original
for original, expected in before.items():
    assert digest(Path(original)) == expected, original
for entry in mapping.values():
    assert digest(OUT / entry['archive']) == entry['sha256']

dump('source-mappings.json', dict(scope='Raw byte copies; original absolute paths remain unchanged inside raw reports. This map resolves them to archive files. Long paths/Clang snapshots may use flat names.',
                                  files=mapping))
dump('omitted-artifacts.json', dict(scope='No tool executables or physical firmware image copied. Xtensa metrics object files are retained; replaceable Linux x86-64 executables/objects are omitted.',
                                   files=omitted))
dump('qualification.json', dict(passed=True, archived_utc=datetime.now(timezone.utc).isoformat(),
                               current_bindings=bindings, sdk_object_dependencies_sha256=dependency_bindings,
                               raw_copies_verified_before_after=len(before),
                               metrics=dict(cases=16, semantic_controls=7),
                               backend_telemetry=dict(cases=22, semantic_controls=8),
                               regressions=dict(pause_cases=38, pause_controls=2,
                                                gain_arithmetic_per_backend=5801300, gain_packets_per_backend=375,
                                                normalizer_packets=[239,240,239], packed_pcm_cases=[1359,1358,1358],
                                                maintenance_cases=83, maintenance_controls=9),
                               health=dict(profiles=3, maximum_json_bytes=2000, capacity_bytes=2304,
                                           all_capacity_canaries=True),
                               stream=dict(stream_cases=50, settings_requests=80, authoritative='03'),
                               independent_review=dict(passed=True, frozen_inputs=len(review['input_sha256']),
                                                       raw_logs=len(review['raw_evidence_sha256']), actionable_findings=[]),
                               clang=dict(units=53, warnings=86, errors=0, inputs=656, added_warnings=0, removed_warnings=0),
                               source_hash_notes=['The earlier SDK object compile report retains historical metrics fixture/runner hashes. The helper/config/compiler dependency closure is current; metrics03 and the final independent review provide the authoritative current host fixture hashes.',
                                                  'The original object report has an empty literal-relocation field. The final metrics review independently validates actual R_XTENSA_ASM_EXPAND call records in both ISR objects; raw disassembly is retained.'],
                               scope='Host qualification plus actual standalone Xtensa helper objects and static Clang analysis. No new target app build, final integrated callback/helper map, physical IRQ/SMP timing, DMA transmission, audio quality or overhead claim.'))

entries = {}
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name != 'manifest.json':
        entries[path.relative_to(OUT).as_posix()] = dict(sha256=digest(path), bytes=path.stat().st_size)
dump('manifest.json', dict(schema=1, scope='Every initial archive file except this self-referential manifest. Raw source reports are immutable. Later evidence must use an additive separately bound appendix.',
                          files=entries, file_count=len(entries), indexed_bytes=sum(item['bytes'] for item in entries.values())))
for relative, expected in entries.items():
    assert digest(OUT / relative) == expected['sha256']
print(json.dumps(dict(passed=True, files=len(entries)+1, indexed_bytes=sum(item['bytes'] for item in entries.values()),
                      manifest_sha256=digest(OUT / 'manifest.json'), qualification_sha256=digest(OUT / 'qualification.json'),
                      copied_raw_files=len(mapping), omitted_linux_or_baseline_binaries=len(omitted)), indent=2))
