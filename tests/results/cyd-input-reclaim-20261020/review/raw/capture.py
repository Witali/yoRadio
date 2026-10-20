"""Capture a read-only source/evidence review. No build/test/tool child process."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SDK = Path('C:/Work/yoRadio/.idf/v6.0.2')
assert not (HERE / 'review.json').exists()
started = datetime.now(timezone.utc).isoformat()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
inputs, snapshots = {}, {}


def freeze(path):
    path = path.resolve()
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    target = HERE / 'snapshots' / digest
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == data
    else:
        target.write_bytes(data)
    inputs[str(path)] = digest
    snapshots[str(path)] = target.relative_to(HERE).as_posix()
    return digest


def load(relative):
    path = ROOT / relative
    freeze(path)
    return json.loads(path.read_text())


main = ROOT / 'idf/esp32-cyd2usb-native/main'
for name in ('native_input_reclaim.c', 'native_input_reclaim.h', 'audio_service.c', 'audio_service.h',
             'native_health.c', 'native_health.h', 'app_main.c', 'CMakeLists.txt', 'Kconfig.projbuild',
             'compat/input_reclaim/enable.cmake'):
    freeze(main / name)
freeze(ROOT / 'idf/esp32-cyd2usb-native/CMakeLists.txt')
for relative in ('mbedtls/port/esp_mem.c', 'mbedtls/port/include/esp_mem.h',
                 'mbedtls/port/include/mbedtls/esp_config.h', 'mbedtls/Kconfig',
                 'heap/heap_caps.c', 'heap/heap_caps_base.c', 'heap/include/esp_heap_caps.h', 'heap/Kconfig',
                 'freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos/portmacro.h',
                 'freertos/FreeRTOS-Kernel/portable/xtensa/port.c'):
    freeze(SDK / 'components' / relative)
freeze(SDK / '.git/HEAD')
sdk_commit = (SDK / '.git/HEAD').read_text().strip()
assert sdk_commit == '7101770dc6db2667b3c477cc31365dd1acd6db4e'

config = load('.build/cyd-input-reclaim-config-01/report.json')
startup = load('.build/cyd-startup-reclaim-03/report.json')
service = load('.build/cyd-input-reclaim-host-01/report.json')
lint = load('.build/lint-cyd-input-reclaim-01/report.json')
previous = load('.build/lint-cyd-output-telemetry-01/report.json')
assert config['passed'] and len(config['cases']) == 8 and all(v['passed'] for v in config['cases'].values())
assert startup['passed'] and len(startup['variants']) == 12 and len(startup['negative_controls']) == 4
assert service['passed'] and len(service['cases']) == 21 and len(service['negative_controls']) == 17
assert sha(ROOT / '.build/cyd-input-reclaim-host-01/report.json') == '44f5a70af48c15ed4021b946a9d61649eed485a9fca243119b95e5f13e2c13eb'
assert lint['complete'] and lint['units'] == 54 and lint['warnings'] == 86 and lint['errors'] == 0
assert lint['captured_input_count'] == 661 and lint['all_inputs_unchanged_after_analysis']
evidence_sources = {}
for name, report in [('config', config), ('startup_authored_by_this_reviewer', startup), ('service', service)]:
    directory = {'config': '.build/cyd-input-reclaim-config-01',
                 'startup_authored_by_this_reviewer': '.build/cyd-startup-reclaim-03',
                 'service': '.build/cyd-input-reclaim-host-01'}[name]
    evidence_sources[name] = {}
    for relative, digest in report['source_sha256'].items():
        current, snapshot = ROOT / relative, ROOT / directory / 'sources' / relative
        assert sha(current) == sha(snapshot) == digest, (name, relative)
        freeze(current)
        freeze(snapshot)
        evidence_sources[name][relative] = digest
    for path in (ROOT / directory).rglob('*'):
        if path.is_file() and (path.suffix in ('.log', '.json') or path.name == 'captured.txt'):
            freeze(path)

lint_manifest = load('.build/lint-cyd-input-reclaim-01/source-manifest.json')
post = load('.build/lint-cyd-input-reclaim-01/post-analysis-verification.json')
assert post['passed'] and all(post['inputs'].values())
lint_bindings = {}
for original, entry in lint_manifest['inputs'].items():
    frozen = ROOT / '.build/lint-cyd-input-reclaim-01' / entry['snapshot']
    assert sha(Path(original)) == sha(frozen) == entry['sha256'], original
    freeze(Path(original))
    freeze(frozen)
    lint_bindings[original] = entry['sha256']
for path in (ROOT / '.build/lint-cyd-input-reclaim-01/analysis').glob('*'):
    if path.is_file() and path.suffix in ('.log', '.json', '.yaml'):
        freeze(path)
for path in (ROOT / '.build/cyd-input-reclaim-config-01').rglob('command.json'):
    freeze(path)
for original, digest in config['tools'].items():
    assert sha(Path(original)) == digest


def normalize(value):
    value = value.replace('\\', '/')
    value = re.sub(r'^.*?/esp32-cyd-c3-review/', '', value)
    return re.sub(r'idf/esp32-cyd2usb-native/build-[^/]+/native-httpd-rfc6455/', 'httpd-overlay/', value)


def diagnostics(report):
    return Counter((normalize(unit['file']), normalize(item['file']), item['severity'], item['check'], item['message'])
                   for unit in report['results'] for item in unit['diagnostics'])


old, new = diagnostics(previous), diagnostics(lint)
assert old == new and sum(new.values()) == 86
new_unit = [v for v in lint['results'] if v['file'].endswith('/native_input_reclaim.c')]
assert len(new_unit) == 1 and not new_unit[0]['diagnostics']
config_input = next((ROOT / '.build/lint-cyd-input-reclaim-01' / value['snapshot']
                     for key, value in lint_manifest['inputs'].items() if key.endswith('config\\sdkconfig.h')), None)
assert config_input
text = config_input.read_text()
for flag in ('YORADIO_TLS_INPUT_RECLAIM', 'YORADIO_ADAPTIVE_INPUT_BUFFER', 'ESP_TLS_USING_MBEDTLS', 'MBEDTLS_INTERNAL_MEM_ALLOC'):
    assert '#define CONFIG_' + flag + ' 1' in text
for flag in ('MBEDTLS_CUSTOM_MEM_ALLOC', 'HEAP_ABORT_WHEN_ALLOCATION_FAILS'):
    assert '#define CONFIG_' + flag + ' 1' not in text

freeze(Path(__file__))
unchanged = {path: sha(Path(path)) == digest for path, digest in inputs.items()}
snapshot_unchanged = {path: sha(HERE / snapshots[path]) == digest for path, digest in inputs.items()}
assert all(unchanged.values()) and all(snapshot_unchanged.values())
report = dict(passed=True, actionable_findings=[], started_utc=started,
              finished_utc=datetime.now(timezone.utc).isoformat(), sdk_commit=sdk_commit,
              scope='Read-only independent source review of the service authored by n5_reboot and startup/CMake/Kconfig wiring authored by root. No edit, test rerun, build, Git operation, download or device access.',
              independence={'production_service_and_wiring': 'Reviewer did not author production service or integration.',
                            'startup_suite': 'This reviewer authored startup fixture/runner. Its 12/4 result is supporting evidence, not an independently authored test/review gate.',
                            'health_hook': 'Startup observe_health_failure is an explicit SDK failed-allocation callback SEAM; it does not execute actual native_health.c. Native health integration is a separate target harness gate.'},
              input_sha256=inputs, snapshot_map=snapshots, inputs_unchanged_after=unchanged,
              snapshots_unchanged_after=snapshot_unchanged, evidence_source_sha256=evidence_sources,
              evidence={'config': {'cases': 8, 'passed': True},
                        'service_host': {'cases': 21, 'semantic_controls': 17, 'passed': True, 'actual_sdk_allocator': False},
                        'startup_own_authorship': {'variants': 12, 'semantic_controls': 4, 'passed': True},
                        'opt_in_clang': {'units': 54, 'warnings': 86, 'errors': 0, 'frozen_inputs': 661,
                                        'new_service_diagnostics': [], 'previous_units': 53,
                                        'added_warning_multiset': [], 'removed_warning_multiset': []}},
              lint_input_sha256=lint_bindings,
              diagnostic_normalization='Preserve unit, logical diagnostic file, severity, check, full message and multiplicity; normalize worktree/generated HTTPD build paths and ignore line/column offsets.',
              tool_metadata={'config_tools_sha256': config['tools'], 'clang': lint_manifest['tool'],
                             'host_compiler': service['compiler'], 'no_tools_executed_by_review': True},
              reviewed_contracts=[
                  'All owner/pin/retiring accesses use one SMP portMUX. NULL/ISR bind/detach reject before that registry lock. Same active owner binds idempotently; a foreign owner or retiring owner cannot be overwritten.',
                  'Detach with active allocator pins marks retirement and closes new pin/bind admission. The last unpin leaves ownership intact; only explicit lifecycle-owner retry at zero pins clears owner/retiring. Wrong-owner calls leave state unchanged.',
                  'The SIZE_MAX pin guard prevents representable count overflow; unpin occurs exactly once after every successful pin and all retry-loop exits. Pin protects queue lifetime across stats, release/free and original allocation calls.',
                  'Original esp_mbedtls_mem_calloc is called first, with unchanged arguments. Its non-NULL result is returned unchanged even for unusual arguments. Zero/overflow/task-context checks affect retries only after a NULL result; invalid/ISR failure does not touch registry or queue.',
                  'Retry budget is captured immutable target-minus-minimum from canonical queue geometry (minimum<=target<=16); CYD startup target8/minimum4 allows at most4 reclaim/retry attempts, plus the original call. Refill/concurrent allocators cannot extend that budget.',
                  'Registry lock is released before queue stats/release or original allocator calls. Canonical release_one removes only IDLE data slots above resident minimum, marks the slot absent under queue lock, unlocks, then frees. WRITING/READY/READING/control storage is excluded.',
                  'Internal SDK allocator selection remains original heap_caps_calloc(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT), including zeroing/free semantics and its existing failure callback. The wrapper replaces no free/global calloc/failed-allocation callback and does not erase original failure records; retries can add ordinary failure observations.',
                  'Startup performs all fallible work and health task registration before READY, then optional bind of actual s_encoded, then notifications. Reject only logs a warning; no later rollback path can destroy a published pool. Current Stop/EOF/maintenance do not destroy successful adaptive input.',
                  'Default is disabled. Kconfig and actual helper reject missing adaptive/internal-mbedTLS/recoverable allocation prerequisites. Disabled/early helper adds no source/link options. Enabled helper appends only the module and precise esp_mbedtls_mem_calloc wrap/retention options after component registration.',
              ],
              limits=[
                  'No actual SDK OOM, target ABI/link resolution, target service execution, physical TLS handshake, RF or DMA is established here. The separate target harness was still pending at this review and is not recorded as passed.',
                  'Clang is static analysis, not optimized Xtensa generation or runtime proof. Identical warning counts are strengthened by exact normalized warning-multiset equality, not a clean-warning claim.',
                  'Host service models original calloc/heap capacity and pthread/ISR/RTOS. Its 10000-packet concurrency scenario does not prove ESP32 scheduling, cache/IRAM behavior, TSAN, latency, memory margin, real fragmentation recovery or performance.',
                  'The pin overflow guard is source-reviewed; no SIZE_MAX simultaneous real pins or private registry seeding is claimed.',
                  'Exclusive lifecycle ownership and live queue/control storage are caller contracts. DETACHED drains allocator pins only; all ordinary producer/consumer/restore/health users must separately quiesce before destruction. Current runtime has no successful-pool teardown.',
                  'Original SDK allocation is still called in ISR/invalid contexts before retry rejection, preserving baseline behavior; the wrapper is not a general ISR-safe allocator certification.',
              ])
(HERE / 'review.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS independent production review; no actionable findings; inputs=' + str(len(inputs)) + '; review SHA256 ' + sha(HERE / 'review.json'))
