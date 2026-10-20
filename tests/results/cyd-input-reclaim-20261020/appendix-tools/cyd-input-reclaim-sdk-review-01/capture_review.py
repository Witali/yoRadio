"""Read-only static review capture. Never runs the reviewed orchestration."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SDK = Path('C:/Work/yoRadio/.idf/v6.0.2')
def digest(data):
    return hashlib.sha256(data).hexdigest()
def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.longpaths=true', *args], cwd=ROOT)
def write_json(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

assert not (OUT/'review.json').exists(), 'Keep initial review immutable'
inputs = {}
def capture(path, label=None):
    path = Path(path).resolve()
    key = str(path)
    if key in inputs:
        return inputs[key]
    data = path.read_bytes()
    if label is None:
        label = ('repository/'+path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT)
                 else 'sdk/'+path.relative_to(SDK).as_posix())
    target = OUT/'frozen_inputs'/label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    row = {'source': key, 'snapshot': target.relative_to(OUT).as_posix(), 'bytes': len(data), 'sha256': digest(data)}
    inputs[key] = row
    return row

reviewed = [ROOT/'.build'/name for name in (
    'prepare-input-reclaim-production.py', 'input-reclaim-production-profiles.json',
    'run-input-reclaim-production.ps1', 'qualify-input-reclaim-sdk.py')]
for path in reviewed:
    capture(path)
profiles = json.loads(reviewed[1].read_bytes())
expected = {(('custom-flac-' if custom else '')+backend, backend, custom, True)
            for custom in (False, True) for backend in ('pdm', 'continuous', 'legacy')}
expected.add(('disabled-pdm', 'pdm', False, False))
actual = {(p['name'], p['backend'], p['custom_flac'], p['enabled']) for p in profiles}
assert actual == expected and len(profiles) == 7
assert len({Path(p['build_directory']).resolve() for p in profiles}) == 7
assert len({Path(p['sdkconfig']).resolve() for p in profiles}) == 7
assert len({p['variant'] for p in profiles}) == 7
baseline_checks = []
key_pattern = re.compile(r'^(?:# )?CONFIG_YORADIO_TLS_INPUT_RECLAIM(?:=| )')
for p in profiles:
    baseline = Path(p['baseline'])
    baseline_config = capture(baseline/'sdkconfig')
    baseline_json = capture(baseline/'sdkconfig.json')
    baseline_receipt = capture(baseline/'manifest.json')
    receipt = json.loads((baseline/'manifest.json').read_bytes())
    config = json.loads((baseline/'sdkconfig.json').read_bytes())
    seed = capture(p['sdkconfig'])
    assert baseline_config['sha256'] == p['baseline_sdkconfig_sha256'] == receipt['sdkconfig_sha256']
    assert baseline_json['sha256'] == receipt['sdkconfig_json_sha256']
    assert seed['sha256'] == p['prepared_sdkconfig_sha256']
    old = [s for s in (baseline/'sdkconfig').read_text().splitlines() if not key_pattern.match(s)]
    new = [s for s in Path(p['sdkconfig']).read_text().splitlines() if not key_pattern.match(s)]
    assert old == new
    key_lines = [s for s in Path(p['sdkconfig']).read_text().splitlines() if key_pattern.match(s)]
    assert key_lines == [('CONFIG_YORADIO_TLS_INPUT_RECLAIM=y' if p['enabled'] else '# CONFIG_YORADIO_TLS_INPUT_RECLAIM is not set')]
    assert config['IDF_TARGET'] == 'esp32' and not config.get('FREERTOS_UNICORE')
    assert config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240 and config['ESPTOOLPY_FLASHSIZE_4MB']
    assert config['YORADIO_ADAPTIVE_INPUT_BUFFER'] and config['ESP_TLS_USING_MBEDTLS'] and config['MBEDTLS_INTERNAL_MEM_ALLOC']
    assert not config.get('MBEDTLS_CUSTOM_MEM_ALLOC') and not config.get('HEAP_ABORT_WHEN_ALLOCATION_FAILS')
    assert not config.get('YORADIO_NATIVE_DIAGNOSTICS')
    assert Path(p['sdkconfig']).resolve() == Path(p['build_directory']).resolve()/'sdkconfig'
    assert p['variant'] == 'esp32-cyd2usb-native-tls-input-reclaim-'+p['name']
    assert Path(p['build_directory']).resolve().is_relative_to(ROOT)
    exact_git = {}
    for name in ('manifest.json', 'sdkconfig', 'sdkconfig.json'):
        relative = (baseline/name).relative_to(ROOT).as_posix()
        blob = git('show', 'HEAD:'+relative)
        target = OUT/'git_baseline'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        exact_git[name] = {'sha256': digest(blob), 'bytes': len(blob), 'equals_current': blob == (baseline/name).read_bytes()}
        assert exact_git[name]['equals_current']
    baseline_checks.append({'name': p['name'], 'backend': p['backend'], 'custom_flac': p['custom_flac'],
        'enabled': p['enabled'], 'only_prepared_text_delta': 'CONFIG_YORADIO_TLS_INPUT_RECLAIM',
        'baseline_receipt_source_commit': receipt['source_commit'], 'baseline_source_dirty': receipt['source_dirty'],
        'baseline_receipt_sha256': baseline_receipt['sha256'], 'baseline_config_sha256': baseline_config['sha256'],
        'baseline_json_sha256': baseline_json['sha256'], 'prepared_seed_sha256': seed['sha256'], 'git_head_blobs': exact_git})

paths = (
    'AGENTS.md', 'tools/export_cyd_production.py',
    'idf/esp32-cyd2usb-native/build-production.ps1', 'idf/esp32-cyd2usb-native/build.ps1',
    'idf/esp32-cyd2usb-native/partitions.csv', 'idf/esp32-cyd2usb-native/main/CMakeLists.txt',
    'idf/esp32-cyd2usb-native/main/Kconfig.projbuild',
    'idf/esp32-cyd2usb-native/main/compat/input_reclaim/enable.cmake',
    'idf/esp32-cyd2usb-native/main/native_input_reclaim.c', 'idf/esp32-cyd2usb-native/main/native_input_reclaim.h',
    'idf/esp32-cyd2usb-native/main/audio_service.c', 'idf/esp32-cyd2usb-native/main/app_main.c',
    'idf/esp32-cyd2usb-native/main/network_runtime.c', 'idf/esp32-cyd2usb-native/main/board_config.h',
    'idf/esp32-cyd2usb-native/main/native_audio_output.c', 'idf/esp32-cyd2usb-native/main/native_output_metrics.c',
    'tests/results/cyd-input-reclaim-20261020/README.md', 'tests/results/cyd-input-reclaim-20261020/HOST.md',
    'tests/results/cyd-http-request-buffer-20261020/README.md',
    'tests/results/cyd-flac-runtime-20261019/README.md',
    'tests/results/cyd-output-telemetry-20261020/SDK.json',
    '.build/cyd-input-reclaim-config-01/report.json', '.build/cyd-input-reclaim-review-01/review.json',
    '.build/cyd-http-tx-target-01/esp_http_client.c')
for relative in paths:
    capture(ROOT/relative)
for relative in (
    'components/mbedtls/port/esp_mem.c', 'components/mbedtls/port/include/esp_mem.h',
    'components/mbedtls/port/include/mbedtls/esp_config.h',
    'components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c'):
    capture(SDK/relative)
# Preserve the executable identity only, not a binary copy.
python_path = Path(sys.executable).resolve()
python_raw = python_path.read_bytes()
python_row = {'source': str(python_path), 'bytes': len(python_raw), 'sha256': digest(python_raw)}
head = git('rev-parse', 'HEAD').decode().strip()
sdk_head = git('-C', str(SDK), 'rev-parse', 'HEAD').decode().strip()
sdk_status = git('-C', str(SDK), 'status', '--porcelain', '--untracked-files=no')
(OUT/'sdk-tracked-status.log').write_bytes(sdk_status)
assert sdk_head == '7101770dc6db2667b3c477cc31365dd1acd6db4e' and not sdk_status.strip()
write_json('prepared-profile-checks.json', {'passed': True, 'profiles': baseline_checks, 'exact_matrix': True,
    'unique_build_directories': True, 'unique_sdkconfigs': True, 'unique_variants': True,
    'all_prepared_configs_only_new_bool': True, 'all_baselines_match_current_git_head_blobs': True})

findings = [
    {'id': 'R1', 'priority': 2, 'file': '.build/qualify-input-reclaim-sdk.py', 'start': 22, 'end': 23,
     'title': 'Require the complete seven-profile matrix before declaring PASS',
     'detail': 'The qualifier trusts the profile array without asserting its exact seven expected tuples, names and variants or unique paths. An empty array skips all image checks yet reaches passed=True and the Seven-complete-exports scope; omission or duplication can similarly under-cover the promised matrix. The current seven rows are correct.',
     'requested_change': 'Assert the exact six enabled vendor/custom x three backends plus disabled vendor PDM set, exact names/variants, unique build/config/export paths and final seven checked images.'},
    {'id': 'R2', 'priority': 2, 'file': '.build/qualify-input-reclaim-sdk.py', 'start': 62, 'end': 65,
     'title': 'Bind the configuration baseline and prepared seed to immutable inputs',
     'detail': 'The sole-new-bool assertion compares output against mutable baseline sdkconfig.json. The qualifier does not verify its baseline receipt/raw-config/JSON identity, their committed Git blobs, profile baseline hash, or receipt seed source_sha256 against prepared_sdkconfig_sha256. firmware/development is excluded from exporter source-content hashing, so a changed baseline JSON could conceal an unintended non-explicit config delta. All current baseline receipts/configs and prepared seeds are valid and match their recorded hashes and current HEAD blobs.',
     'requested_change': 'Require baseline receipt/raw sdkconfig/sdkconfig.json exact HEAD blob bytes and receipt/profile hashes, and each new receipt seed_configuration.source_sha256 equal the prepared profile SHA.'},
    {'id': 'R3', 'priority': 2, 'file': '.build/qualify-input-reclaim-sdk.py', 'start': 16, 'end': 17,
     'title': 'Verify current clean source content before and after qualification',
     'detail': 'HEAD equality and historical receipt source_dirty=False do not show that the live source still equals the source built in all seven receipts. The qualifier reads several live production/overlay files but never checks current source_snapshot/content SHA or compares receipt source_content_sha256 to the prebuild marker. Same-HEAD edits after export can therefore remain outside the final qualification freshness check.',
     'requested_change': 'Use the actual exporter source_snapshot with core.longpaths in its subprocess environment; require clean source and equal source content/identity against the prebuild marker and all seven receipts before and after qualification. Preserve scope exclusions explicitly. The source marker is intentionally not created yet and its present absence is not a finding.'},
    {'id': 'R4', 'priority': 2, 'file': '.build/qualify-input-reclaim-sdk.py', 'start': 39, 'end': 40,
     'title': 'Require the intended evidence paths and frozen evidence identities',
     'detail': 'Hashing whatever evidence rows happen to be present permits an empty evidence list or a different self-consistent evidence set. The orchestration currently passes the correct two READMEs and the custom FLAC README for custom rows, but the final qualifier does not require those exact references or bind them to the prebuild frozen evidence marker. tests/results is excluded from exporter source-content hashing.',
     'requested_change': 'Require exact intended evidence path sets per profile and compare their receipt/current hashes with the frozen prebuild marker.'},
]
checks = [
    'Reviewed source statically; no reviewed generator, qualifier or build command was executed.',
    'Current seven prepared rows form the exact intended matrix with unique in-repository build/config paths and only the new bool as text delta.',
    'All six baseline receipt/config pairs match recorded hashes and current committed HEAD blob bytes; all seven prepared seeds match profile hashes.',
    'PowerShell dispatch uses intended evidence sets, captures nonzero child exit and has no flash/serial/device operations.',
    'Inherited exporter enforces source-before/after identity per export, SDK/target/GCC/image/config/OTA checks and writes manifest completion last.',
    'Planned qualifier checks actual linked ELF32 Xtensa symbols, canonical reclaim compilation row and linker wrapping flags enabled/off.',
    'ELF program-header-based initializer proof correctly reads file-backed 32-bit calloc/free globals, expects wrapper only enabled and ordinary free for every image.',
    'SDK source maps default allocator/free pointers to esp_mbedtls_mem_calloc/free; internal allocator uses MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT and ordinary free uses heap_caps_free.',
    'Planned checksum/appended SHA/chip/ELF/app descriptor/two OTA slots/flash limit checks are grounded in the actual image/partition parsers.',
    'Planned task-call/table and board comparisons retain previous dual-core owner bindings and board constants; config comparison covers existing backend/clock/DMA options once R2 is fixed.',
    'Planned metrics state/lock DRAM and PDM ISR symbol IRAM checks are target addresses only, not ISR-latency or hardware claims.',
    'SDK checkout is at the pinned 6.0.2 commit with clean tracked files during this static review.',
]
limits = [
    'No seven new production exports have been run or qualified by this review; linked object/ELF/image properties above are reviewed assertions, not new execution results.',
    'Source HEAD marker is deliberately pending final harness commit; absence is expected.',
    'No target QEMU result, physical OOM, RF, DMA, IRQ latency, audio quality or hardware qualification is inferred.',
    'The initial review does not execute malformed profile/receipt variants; vacuous acceptance paths are demonstrated directly by control flow.',
    'One-time generator checks existing profile output after config writes; do not rerun this preparation script as a dry-run. This is a workflow note, not an additional blocker for the current prepared matrix.',
]
for row in inputs.values():
    row['after_sha256'] = digest(Path(row['source']).read_bytes())
    row['unchanged_after'] = row['sha256'] == row['after_sha256']
assert all(row['unchanged_after'] for row in inputs.values())
write_json('inputs.json', {'inputs': list(inputs.values()), 'all_unchanged_after': True,
    'review_python': python_row, 'review_python_version': sys.version})
report = {'review_complete': True, 'qualification_ready': False, 'independent_production_orchestration_review': True,
    'mode': 'read-only static planned-build review', 'repository_head_at_review': head,
    'sdk_commit': sdk_head, 'sdk_tracked_clean': not sdk_status.strip(),
    'reviewed_entrypoint_sha256': {p.name: digest(p.read_bytes()) for p in reviewed},
    'findings': findings, 'checks': checks, 'limitations': limits,
    'prepared_profiles': 'prepared-profile-checks.json', 'inputs': 'inputs.json',
    'all_frozen_inputs_unchanged_after': True, 'input_count': len(inputs),
    'builds_started_by_review': 0, 'physical_operations': 0}
write_json('review.json', report)
manifest = []
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name != 'manifest.json':
        raw = p.read_bytes()
        manifest.append({'path': p.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': digest(raw)})
write_json('manifest.json', {'files': manifest})
print(json.dumps({'review_complete': True, 'qualification_ready': False, 'findings': len(findings),
    'inputs': len(inputs), 'files': len(manifest)+1, 'review_sha256': digest((OUT/'review.json').read_bytes()),
    'manifest_sha256': digest((OUT/'manifest.json').read_bytes())}, indent=2))
