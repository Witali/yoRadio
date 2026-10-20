"""Seal compact component-check evidence after four scoped qualifications pass."""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'tests/results/cyd-ota-component-dependency-20261020'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
mapping = []

def put(path, name=None):
    path = Path(path).resolve()
    raw = path.read_bytes()
    digest = sha(raw)
    previous = [x for x in mapping if x['path'] == str(path)]
    if previous:
        assert len(previous) == 1 and previous[0]['sha256'] == digest and previous[0]['bytes'] == len(raw)
        return previous[0]
    stored = name or ('payload/' + digest + ('.gz' if len(raw) > 65536 else '.raw'))
    target = OUT / stored
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = gzip.compress(raw, mtime=0) if stored.endswith('.gz') else raw
    if target.exists(): assert target.read_bytes() == encoded
    else: target.write_bytes(encoded)
    row = {'path': str(path), 'bytes': len(raw), 'sha256': digest, 'stored': stored,
           'encoding': 'gzip' if stored.endswith('.gz') else 'raw'}
    if row not in mapping: mapping.append(row)
    return row

def omit(row, kind):
    if not any(x['path'] == row['path'] for x in mapping):
        mapping.append({**row, 'omission': kind})

assert not OUT.exists(), 'Never overwrite an evidence archive'
attempts = ['cyd-present-01', 'cyd-absent-01', 'c3-present-01', 'c3-absent-01']
report_names = {x: ('qualification-02.json' if x == 'cyd-present-01' else 'qualification.json') for x in attempts}
reports = [(run, json.loads((HERE / run / report_names[run]).read_bytes())) for run in attempts]
assert {r['target'] for _, r in reports} == {'esp32', 'esp32c3'}
assert all(r['status'] == 'PASS' and r['returncode'] == 0 for _, r in reports)
OUT.mkdir(parents=True)
for name in ['check.py', 'run.py', 'qualify.py', 'audit.py', 'sdk.ps1', 'probe.cmake', 'PLAN.md', 'pack.py']:
    put(HERE / name, 'tooling/' + name)
put(HERE / 'verify.py', 'verify.py')
for attempt, report in reports:
    run = HERE / attempt
    put(run / report_names[attempt], attempt + '/report.json')
    put(run / 'report.json', attempt + '/build-report.json')
    for name in ['stdout.log', 'stderr.log', 'ninja-deps.txt', 'invocation.json', 'sdkconfig']:
        put(run / name)
    for row in report['sources_before'] + report['baseline'] + report.get('isolated_project', {}).get('files', []):
        p = Path(row['path'])
        assert sha(p.read_bytes()) == row['sha256']
        put(p)
    for row in report['generated']:
        if Path(row['path']).name in ['compile_commands.json', 'build.ninja']:
            omit(row, 'large generated metadata; the raw actual compiler invocations and selected rows are retained')
        else: put(row['path'])
    for row in report['response_files']: put(row['path'])
    for row in report['sdk_cmake']: put(row['path'])
    put(report['baseline_warning_log']['path'], 'original-warning.log' if report['target'] == 'esp32' else None)
    for row in report['headers']:
        if Path(row['path']).is_relative_to(ROOT): put(row['path'])
        else: omit(row, 'installed SDK/compiler dependency header identity only')
    for row in report['tools']: omit(row, 'installed tool binary identity only')
    omit(report['library'], 'generated static archive identity only')
    for row in report['compile_results']: omit(row['object'], 'generated target object identity only')
    for row in report.get('tools_before', []): omit(row, 'installed pre-build tool binary identity only')
put(HERE / 'history/qualify-01.py', 'history/qualify-01.py')
put(HERE / 'cyd-present-01/qualification.json', 'history/qualification-01.json')
for p in sorted((HERE / 'review').iterdir()):
    if p.is_file(): put(p, 'review/' + p.name)
for row in json.loads((HERE / 'review/report.json').read_bytes())['unchanged_c3_and_ota_sources']:
    put(row['path'])
history = {'initial_qualification': {'report': 'history/qualification-01.json', 'tool': 'history/qualify-01.py',
    'scope': 'preserved failed first qualification; new read-only report records the exact harness advisory'},
    'runner_failures': []}
for attempt, report in reports:
    if report['original_runner']['status'] == 'FAIL':
        history['runner_failures'].append({'attempt': attempt, 'report': attempt + '/build-report.json',
            'status': 'FAIL', 'actual_sdk_launcher_returncode': report['returncode'],
            'failure': report['original_runner']['failure'], 'qualification': attempt + '/report.json'})
(OUT / 'history.json').write_text(json.dumps(history, indent=2) + '\n', encoding='utf-8')
baseline_log = ROOT / 'firmware/development/esp32-cyd2usb-native-early-mpi-pdm/build-2.log'
put(baseline_log, 'original-warning.log')
readme = '''# Native OTA component dependency

This archive records fresh actual ESP-IDF 6.0.2 ESP32 CYD configuration and
native_ota component compilation, plus isolated actual ESP-IDF 6.0.2/6.1
component-present and component-absent projects. The shared component uses an
optional PRIVATE native_stream target dependency when already present. When
absent it keeps the existing private header fallback without discovering or
compiling native_stream. All three actual OTA translation units compile in all
four cases. The earlier SDK include-owner warning is in original-warning.log.

The complete CYD present-case normalized sdkconfig is preserved. The C3 checks copy
the baseline sdkconfig and actual main Kconfig definitions, but run an isolated
component project: full donor configuration would execute an excluded codec
patcher. Differences for unavailable full-radio symbols are reported; this is
not a full C3 app/configuration qualification. Existing C3 component discovery
and compatibility translation units are unchanged. Full application linking is
not qualified by this component check.

The first two SDK builds succeeded, while their initial Python runner later
failed on a cache-parser bug. Their original FAIL reports remain byte-exact;
separate read-only qualification reports inspect the original pre-build markers,
logs, three compiled objects, headers and static archives without rebuilding.
One CYD harness object-path advisory and one C3 missing isolated-partition CSV
advisory are explicitly retained. The latter also has partition-inspection
tracebacks. Neither is treated as OTA/compiler evidence or full app/partition
qualification. Five existing SDK6.1 Wi-Fi include-owner warnings match the
immutable C3 baseline. The gate requires zero new source/compiler warnings;
it does not claim zero total warnings. The two remaining combinations use fresh
short build directories and exact copied partition CSVs.

The initial builds identify installed tools after the build, comparing the
actual compiler to the immutable earlier firmware manifest. They do not claim
a newly captured pre-build identity for every tool. The two fresh builds also
capture before/after tool identities. All original SDK tracked-state pins and
scoped source snapshots are preserved.

review/report.json preserves a final read-only audit and four byte-exact selected
Ninja application link metadata rows with offsets and original database hashes.
Those rows show optional stream archives outside whole-archive spans; the full
application linker was not executed. history.json keeps the two original runner
errors separate from actual successful SDK builds and later qualifications.
The original failing check.py and first failed qualification tool are retained
as provenance; run.py and qualify.py record the later workflow. These are
checkout-bound evidence tools; only verify.py is a standalone offline command.

No application image, hardware operation, OTA update, decoder behavior, core
binding, or memory saving is qualified here. Ninja builds the native_ota static
archive and its ordinary build prerequisites; full application linking is not run.

Reports and logs are copied byte-for-byte. Payload names are content addressed;
large textual payloads use lossless gzip. SDK headers, installed tools, generated
objects/libraries and large command/graph databases have explicit byte/SHA-256
identities rather than duplicate binary copies. The three actual compiler rows,
selected generated metadata, source snapshots and header identities are retained.

Run `python -B verify.py` from any directory for an offline integrity and scoped
evidence check. This verifier does not rebuild or assert full application/runtime
equivalence. Root manifest excludes itself, lists every other archive file, and
binds exact stored bytes. path-map.json binds original bytes after decompression.
'''
(OUT / 'README.md').write_text(readme, encoding='utf-8')
(OUT / '.gitattributes').write_text('* -text\n** -text\n', encoding='utf-8')
(OUT / 'path-map.json').write_text(json.dumps({'schema': 'ota-component-map-v1', 'entries': mapping}, indent=2) + '\n', encoding='utf-8')
files = []
for p in sorted(OUT.rglob('*')):
    if p.is_file():
        raw = p.read_bytes()
        files.append({'path': p.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
(OUT / 'manifest.json').write_text(json.dumps({'schema': 'ota-component-archive-v1', 'files': files}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'archive': str(OUT), 'files': len(files) + 1, 'manifest_sha256': sha((OUT / 'manifest.json').read_bytes())}))
