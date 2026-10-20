"""Freeze the final static SDK-orchestration rereview; do not run builds."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SDK = Path('C:/Work/yoRadio/.idf/v6.0.2')
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.longpaths=true', *args], cwd=ROOT)
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

assert not (OUT/'review.json').exists(), 'Do not replace a completed review'
rows = {}
def capture(path):
    path = Path(path).resolve()
    key = str(path)
    if key in rows:
        return rows[key]
    raw = path.read_bytes()
    label = ('repository/'+path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT)
             else 'sdk/'+path.relative_to(SDK).as_posix())
    target = OUT/'frozen_inputs'/label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    rows[key] = {'source': key, 'snapshot': target.relative_to(OUT).as_posix(),
                 'bytes': len(raw), 'sha256': digest(raw)}
    return rows[key]

prior_root = ROOT/'.build/cyd-input-reclaim-sdk-review-01'
capture(prior_root/'inputs.json')
capture(prior_root/'review.json')
prior_inputs = json.loads((prior_root/'inputs.json').read_bytes())
for row in prior_inputs['inputs']:
    capture(row['source'])
names = ('qualify-input-reclaim-sdk.py', 'input_reclaim_sdk_contract.py',
         'run-input-reclaim-production.ps1', 'freeze-input-reclaim-production.py',
         'input-reclaim-production-preflight.py', 'prepare-input-reclaim-production.py',
         'input-reclaim-production-profiles.json', 'test-input-reclaim-sdk-contract.py')
for name in names:
    capture(ROOT/'.build'/name)
metadata_folder = ROOT/'.build/input-reclaim-sdk-contract-tests-02'
for path in metadata_folder.rglob('*'):
    if path.is_file():
        capture(path)
metadata = json.loads((metadata_folder/'report.json').read_bytes())
assert metadata['passed'] is True and metadata['metadata_only'] is True and metadata['sdk_or_device_runs'] == 0
assert metadata['inputs_unchanged_after'] is True and len(metadata['cases']) == 14
assert all(row['detected'] is True and row['predicate'] for row in metadata['cases'].values())
for source, expected in metadata['frozen_inputs'].items():
    assert digest(Path(source).read_bytes()) == expected
    assert digest((metadata_folder/Path(source).name).read_bytes()) == expected
    capture(source)

syntax = {}
for name in names:
    if name.endswith('.py'):
        ast.parse((ROOT/'.build'/name).read_bytes(), filename=name)
        syntax[name] = 'parsed without execution'

# Execute only the frozen pure metadata helper in this process. No longpaths(),
# orchestration, source marker, preflight, build, qualifier or test runner runs.
helper_row = rows[str((ROOT/'.build/input_reclaim_sdk_contract.py').resolve())]
namespace = {'__file__': str(OUT/helper_row['snapshot']), '__name__': 'frozen_contract_review'}
exec(compile((OUT/helper_row['snapshot']).read_bytes(), namespace['__file__'], 'exec'), namespace)
profiles = json.loads((ROOT/'.build/input-reclaim-production-profiles.json').read_bytes())
namespace['profiles'](ROOT, profiles)
profile_checks = []
for p in profiles:
    baseline_json = namespace['baseline'](ROOT, p, git)
    assert namespace['sha'](p['sdkconfig']) == p['prepared_sdkconfig_sha256']
    expected_evidence = namespace['evidence'](ROOT, p)
    assert len(expected_evidence) == (3 if p['custom_flac'] else 2)
    assert baseline_json['IDF_TARGET'] == 'esp32'
    profile_checks.append({'name': p['name'], 'prepared_seed_sha256': p['prepared_sdkconfig_sha256'],
                           'baseline_exact_git_bytes_and_hashes': True, 'intended_evidence': expected_evidence})
old_report = json.loads((prior_root/'review.json').read_bytes())
assert digest((ROOT/'.build/prepare-input-reclaim-production.py').read_bytes()) == old_report['reviewed_entrypoint_sha256']['prepare-input-reclaim-production.py']
assert digest((ROOT/'.build/input-reclaim-production-profiles.json').read_bytes()) == old_report['reviewed_entrypoint_sha256']['input-reclaim-production-profiles.json']
head = git('rev-parse', 'HEAD').decode().strip()
sdk_head = git('-C', str(SDK), 'rev-parse', 'HEAD').decode().strip()
sdk_status = git('-C', str(SDK), 'status', '--porcelain', '--untracked-files=no')
assert sdk_head == '7101770dc6db2667b3c477cc31365dd1acd6db4e' and not sdk_status.strip()
(OUT/'sdk-tracked-status.log').write_bytes(sdk_status)

closures = [
    {'id': 'R1', 'status': 'closed', 'references': [
        '.build/input_reclaim_sdk_contract.py:24-40', '.build/input-reclaim-production-preflight.py:15-18',
        '.build/run-input-reclaim-production.ps1:9-10', '.build/qualify-input-reclaim-sdk.py:24-28,164'],
     'reason': 'Exact seven names, bool selections, backend/custom/enabled tuples, variant and baseline identities plus unique case-folded build/config paths are mandatory before builds; the final result also requires seven variants.'},
    {'id': 'R2', 'status': 'closed', 'references': [
        '.build/input_reclaim_sdk_contract.py:42-53,76', '.build/freeze-input-reclaim-production.py:17-19',
        '.build/input-reclaim-production-preflight.py:21-23', '.build/qualify-input-reclaim-sdk.py:46,79-81'],
     'reason': 'Baseline receipt, sdkconfig and JSON must equal current committed HEAD blobs; receipt/profile hashes are enforced. Actual exporter sdkconfig_seed.source_sha256 must equal the prepared profile hash. Current real seven baselines/seeds passed the pure metadata checks.'},
    {'id': 'R3', 'status': 'closed', 'references': [
        '.build/input_reclaim_sdk_contract.py:18-22,62-76', '.build/freeze-input-reclaim-production.py:9-28',
        '.build/input-reclaim-production-preflight.py:9-20', '.build/qualify-input-reclaim-sdk.py:15-30,46,184-189'],
     'reason': 'The actual exporter source_snapshot runs with inherited core.longpaths. Complete clean included-source snapshot and content SHA match the frozen marker before and after qualification; every receipt must match content, commit, untracked and exclusions. Private profiles, six helper scripts and marker bytes are also hash-bound.'},
    {'id': 'R4', 'status': 'closed', 'references': [
        '.build/input_reclaim_sdk_contract.py:55-60,77-80', '.build/freeze-input-reclaim-production.py:28',
        '.build/input-reclaim-production-preflight.py:24', '.build/qualify-input-reclaim-sdk.py:44-46,55-56'],
     'reason': 'Exact intended README paths are derived by profile, frozen before builds, rechecked against current hashes and required as a unique exact receipt evidence set. Empty, missing, extra, changed and duplicate references fail.'},
]
checks = [
    'No new actionable findings after reviewing the final orchestration and all four prior fixes.',
    'The metadata-only report records fourteen exact assertion predicates, and all three frozen inputs match current and archived bytes; this review did not rerun that test runner.',
    'The frozen pure contract helper accepted current exact profiles and real committed Git baseline bytes/hashes; all seven prepared seed hashes match. No build/qualifier/preflight/freeze entrypoint was executed.',
    'The preparer and profile file remain byte-identical to initial review inputs.',
    'The exporter actual receipt key is sdkconfig_seed and its source_sha256 captures the existing isolated config before build. The final contract uses that exact key.',
    'Initial SDK allocator initializer/ordinary-free ELF proof, canonical module compile/link checks, image checksum/OTA/config guards and unchanged owner/core/board comparisons remain intact.',
    'The qualifier additionally forbids linked __wrap_esp_mbedtls_mem_free and tls_large_reserve_ symbols and the free wrapping linker flag.',
    'PowerShell fails before the first build when preflight fails and stops on any failed export; no board/serial/flash operations are introduced.',
    'The source marker intentionally remains pending final harness commit; a missing marker causes preflight failure and is not a readiness defect at this planning checkpoint.',
]
limits = [
    'This is planned-build orchestration approval, not seven-app build or runtime qualification. No SDK/QEMU/app/board run was started.',
    'The future freeze marker still must be produced after the final harness commit and a clean included source snapshot; production exports and final qualifier must then execute successfully.',
    'Included-source cleanliness intentionally excludes firmware/development and tests/results. The intended README references have separate frozen hash checks; excluded evolving SDK appendices are not represented as production source content.',
    'Reviewed ELF/image/IRAM/DRAM assertions are not results for the pending seven images. No physical OOM, RF, DMA, IRQ latency, audio-quality or hardware claim follows.',
    'One-time preparer retains its previously documented no-rerun workflow note; final matrix is already prepared and the preparer was not executed.',
]
for row in rows.values():
    row['after_sha256'] = digest(Path(row['source']).read_bytes())
    row['unchanged_after'] = row['sha256'] == row['after_sha256']
assert all(row['unchanged_after'] for row in rows.values())
python_path = Path(sys.executable).resolve()
python_raw = python_path.read_bytes()
write('inputs.json', {'inputs': list(rows.values()), 'all_unchanged_after': True,
                     'review_python': {'path': str(python_path), 'bytes': len(python_raw), 'sha256': digest(python_raw), 'version': sys.version}})
write('metadata-validation.json', {'passed': True, 'provided_test_report_sha256': digest((metadata_folder/'report.json').read_bytes()),
    'provided_negative_controls': 14, 'provided_three_inputs_match': True,
    'frozen_pure_helper_real_profile_baseline_checks': profile_checks, 'python_syntax': syntax,
    'orchestration_entrypoints_executed': [], 'sdk_or_device_runs': 0})
report = {'review_complete': True, 'planned_orchestration_ready': True, 'findings': [],
    'independent_orchestration_review': True, 'mode': 'read-only final rereview',
    'repository_head_at_review': head, 'pinned_sdk_commit': sdk_head, 'sdk_tracked_clean': True,
    'prior_review_sha256': digest((prior_root/'review.json').read_bytes()),
    'closures': closures, 'checks': checks, 'limitations': limits,
    'reviewed_entrypoint_sha256': {name: digest((ROOT/'.build'/name).read_bytes()) for name in names},
    'all_inputs_unchanged_after': True, 'input_count': len(rows), 'builds_started_by_review': 0,
    'inputs': 'inputs.json', 'metadata_validation': 'metadata-validation.json'}
write('review.json', report)
files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path != OUT/'manifest.json':
        raw = path.read_bytes()
        files.append({'path': path.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': digest(raw)})
write('manifest.json', {'files': files})
print(json.dumps({'review_complete': True, 'planned_orchestration_ready': True, 'findings': 0,
    'closures': 4, 'inputs': len(rows), 'files': len(files)+1,
    'review_sha256': digest((OUT/'review.json').read_bytes()),
    'manifest_sha256': digest((OUT/'manifest.json').read_bytes())}, indent=2))
