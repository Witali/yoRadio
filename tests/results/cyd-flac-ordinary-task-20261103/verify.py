"""Check retained text/data only. Never run captured code, SDK tools or payloads."""
import argparse
import ast
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

sys.dont_write_bytecode = True
import observe_records  # Owned, reviewed pure parser beside this verifier.

HERE = Path(__file__).resolve().parent
SOURCE_COMMIT = 'de94a304ab70e0babe7345ac249b43b8d79300ca'
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
REPORT_SHA = '79997c9a1abe9754fdbec423015a11dec9c7e2b474e163f286941c3e7ceeee7a'
POLICY = dict(ESP_TASK_WDT_EN=True, ESP_TASK_WDT_INIT=True,
              ESP_TASK_WDT_TIMEOUT_S=5, ESP_TASK_WDT_PANIC=False,
              ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=True,
              ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=True, ESP_INT_WDT=True,
              ESP_INT_WDT_TIMEOUT_MS=300, ESP_INT_WDT_CHECK_CPU1=True,
              HEAP_POISONING_DISABLED=True)


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)


def normalized(value):
    return value.replace('\\', '/')


def safe_relative(value):
    p = PurePosixPath(value)
    return value == p.as_posix() and not p.is_absolute() and '..' not in p.parts and ':' not in value


def pure_nodes(data):
    tree = ast.parse(data.decode('utf-8-sig'))
    return [ast.dump(n, include_attributes=False) for n in tree.body
            if isinstance(n, (ast.Assign, ast.FunctionDef))]


def raw_config(data):
    result = {}
    for line in data.decode('utf-8-sig').splitlines():
        m = re.fullmatch(r'CONFIG_(\w+)=(.*)', line)
        if m:
            key, value = m.groups()
            result[key] = True if value == 'y' else int(value) if value.isdecimal() else value
        m = re.fullmatch(r'# CONFIG_(\w+) is not set', line)
        if m:
            result[m[1]] = False
    return result


def header_config(data):
    result = {}
    for line in data.decode('utf-8-sig').splitlines():
        m = re.fullmatch(r'#define CONFIG_(\w+) (\d+)', line)
        if m:
            result[m[1]] = int(m[2])
    return result


def verify(require_current=False):
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    need(manifest['schema'] == 1, 'manifest schema')
    need(manifest['source_commit'] == SOURCE_COMMIT and manifest['sdk_commit'] == SDK_COMMIT, 'source/SDK pins')
    for name, record in manifest['owned_files'].items():
        need(safe_relative(name), 'owned relative path')
        body = (HERE / name).read_bytes()
        need(len(body) == record['bytes'] and sha(body) == record['sha256'], 'owned file hash/size: ' + name)
    need(set(manifest['owned_files']) == {'README.md', 'observe_records.py', 'recorded-bindings.json', 'source-commit-inventory.json', 'verify.py'}, 'owned file inventory')
    archive = (HERE / manifest['archive']['file']).read_bytes()
    need(len(archive) == manifest['archive']['bytes'] and sha(archive) == manifest['archive']['sha256'], 'archive identity')
    retained, omissions = {}, {}
    for rows, dest in [(manifest['retained'], retained), (manifest['omitted_whole'], omissions)]:
        for row in rows:
            need(safe_relative(row['path']) and row['path'] not in dest and digest(row['sha256']) and row['bytes'] >= 0, 'record identity/unique path')
            dest[row['path']] = row
    need(not (set(retained) & set(omissions)), 'whole original cannot be both retained and omitted')
    need(omissions['report.json']['sha256'] == REPORT_SHA, 'omitted original report pin')
    need('privacy' in omissions['report.json']['reason'] and 'privacy' in omissions['execution-bundle.json']['reason'], 'whole privacy omissions')
    data = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) == manifest['archive']['members'], 'archive member census')
        need(set(names) == {r['member'] for r in retained.values()}, 'exact archive member set')
        for name in names:
            need(re.fullmatch('blobs/[0-9a-f]{64}', name), 'content-addressed member')
            body = z.read(name)
            need(sha(body) == name.split('/')[1], 'member SHA256')
            need(not body.startswith((b'MZ', b'\x7fELF', b'!<arch>')) and b'\0' not in body, 'text-only payload')
            body.decode('utf-8-sig')
            data[name] = body
    for row in retained.values():
        body = data[row['member']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'retained original hash/size')
    def get(name):
        need(name in retained, 'required clean original retained: ' + name)
        return data[retained[name]['member']]
    def load(name):
        return json.loads(get(name))
    def identity(name):
        need(name in retained or name in omissions, 'complete original identity: ' + name)
        return (retained if name in retained else omissions)[name]

    index = json.loads((HERE / 'recorded-bindings.json').read_text(encoding='utf-8'))
    need(index['schema'] == 1 and index['authority'].startswith('Author-recorded'), 'index authority limitation')
    need(index['original_report']['sha256'] == REPORT_SHA and index['original_report']['bytes'] == omissions['report.json']['bytes'], 'original report omission metadata')
    need(index['original_bundle']['sha256'] == omissions['execution-bundle.json']['sha256'] == index['execution_bundle_sha256'], 'bundle omission metadata')
    result = index['recorded_result']
    need(result['passed'] is True and result['all_bound_inputs_current'] is True, 'recorded terminal result')
    need(result['production_source_commit'] == result['repository_head_at_freeze'] == SOURCE_COMMIT and result['sdk_commit'] == SDK_COMMIT, 'recorded commit pins')
    need(result['actual_audio_service_tu'] and result['actual_rtos'], 'recorded actual TU/RTOS scope')
    need(not any(result[k] for k in ('physical_hardware', 'oom_injection', 'output_backpressure', 'performance_or_radio_resource_claim')), 'explicit scope exclusions')
    need(result['fixture_count'] == 130 and result['fixture_blob_bytes'] == identity('fixtures.bin')['bytes'] == 1549200, 'prepared fixture blob scope')
    need(result['executed_fixtures'] == list(observe_records.FIXTURES) and result['cases'] == ['T0', 'T1', 'T2'], 'native executed fixture/case scope')
    need(result['qualified_watchdog_heap'] == POLICY, 'recorded watchdog policy')
    need(result['app_bytes'] == identity('build/cyd_flac_ordinary_task_qemu.bin')['bytes'] == 901552, 'recorded app image identity')
    need(index['source_manifest_sha256'] == sha(get('source-manifest.json')), 'source manifest binding')
    for name, expected in index['prebuild_metadata_sha256'].items():
        need(sha(get(name)) == expected, 'prebuild source/config provenance binding')

    # Independent finite observations come from the clean original UART, never the omitted report.
    fixtures = load('fixture-manifest.json')
    need(len(fixtures) == 130 and len({f['name'] for f in fixtures}) == 130, 'fixture census')
    need([f['id'] for f in fixtures] == list(range(130)), 'fixture ordered IDs')
    by_name = {f['name']: f for f in fixtures}
    for f in fixtures:
        need(f['codec'] == 'flac' and f['ffmpeg_byte_oracle'] is True, 'prepared FLAC oracle')
        need(digest(f['sha256']) and digest(f['pcm_sha256']) and f['bytes'] > 0 and f['pcm_bytes'] > 0, 'fixture identities')
        for n, offset, size, expected in [('encoded', f['encoded_offset'], f['bytes'], f['sha256']), ('pcm', f['pcm_offset'], f['pcm_bytes'], f['pcm_sha256'])]:
            need(0 <= offset <= result['fixture_blob_bytes'] - size, 'fixture blob bounds: ' + n)
        phase = 'large' if 'block8192' in f['name'] else 'small'
        need(identity('fixtures/' + phase + '/' + f['file'])['sha256'] == f['sha256'], 'excluded encoded fixture identity')
        pcm = 'fixtures/' + phase + '/' + PurePosixPath(f['file']).with_suffix('.pcm').as_posix()
        need(identity(pcm)['sha256'] == f['pcm_sha256'] and identity(pcm)['bytes'] == f['pcm_bytes'], 'excluded PCM oracle identity')
    need(pure_nodes((HERE / 'observe_records.py').read_bytes()) == pure_nodes(get('sources/observer/observer.py')), 'owned parser exact recorded semantics')
    observations = observe_records.parse(get('qemu.log').decode('utf-8-sig'), fixtures)
    need(observations == load('ordinary-observations.json'), 'independent UART/observation equality')
    need(len(observations['original_cases']) == 3 and len(observations['positive_iterations']) == 382 and observations['positive_elapsed_us'] == 15033371, 'finite positive lifecycle duration/census')
    need(observations['production_watchdog_policy'] == observe_records.CONFIG, 'strict watchdog observations')
    need(not any(observations[k] for k in ('actual_output_driver', 'physical_hardware', 'full_radio_resource_claim', 'native_fault_injection')), 'UART scope flags')

    configs = [('sdkconfig', raw_config(get('sdkconfig'))), ('build/config/sdkconfig.json', load('build/config/sdkconfig.json')), ('build/config/sdkconfig.h', header_config(get('build/config/sdkconfig.h')))]
    for name, config in configs:
        need(all(config.get(k, False) == v for k, v in POLICY.items()), 'consumed native watchdog/quiet policy: ' + name)
        need(not config.get('YORADIO_NATIVE_DIAGNOSTICS', False) and not config.get('YORADIO_FLAC_DECODER_ESPRESSIF', False), 'diagnostics/vendor-FLAC disabled')
        need(not config.get('YORADIO_HTTP_REQUEST_BUFFER_RELEASE', False) and config.get('YORADIO_INPUT_PREFILL_MS', 0) == 0, 'explicit synthetic transport selectors')
        need(not config.get('FREERTOS_UNICORE', False) and config.get('FREERTOS_HZ') == 1000, 'dual-core RTOS tick policy')
        for k in ('FREERTOS_CHECK_STACKOVERFLOW_CANARY', 'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'YORADIO_FLAC_DECODER_CUSTOM', 'YORADIO_ADAPTIVE_INPUT_BUFFER', 'YORADIO_FRAME_ROUTER', 'YORADIO_STREAM_CONFIRM', 'YORADIO_INPUT_TAIL_COALESCE', 'YORADIO_OGG_TIMELINE', 'YORADIO_AAC_PLUS', 'YORADIO_AAC_DECODER_ESPRESSIF'):
            need(bool(config.get(k)), 'consumed native selector: ' + k)
    provenance = load('configuration-provenance.json')
    need(provenance['watchdog_heap'] == POLICY and provenance['historical_receipt_is_current_application_identity'] is False and provenance['production_watchdog_claim_only'] is True, 'historical policy scope')
    for name in ('sdkconfig', 'sdkconfig.json'):
        p = 'sources/provenance/production-receipt/' + name
        config = raw_config(get(p)) if name == 'sdkconfig' else load(p)
        need(all(config.get(k, False) == v for k, v in POLICY.items()), 'saved production watchdog policy')
        need(sha(get(p)) == provenance['production_receipt'][name], 'saved config receipt identity')
    need(identity('sources/provenance/production-receipt/manifest.json')['sha256'] == provenance['production_receipt']['manifest.json'], 'whole omitted policy manifest identity only')
    need(provenance['explicit_seams'] == dict(http_transport=True, immediate_output=True, real_output_driver=False, request_TX_release=False, input_prefill_ms=0), 'explicit transport/output seams')

    sm = load('source-manifest.json')
    need(len(sm) == result['bound_source_inputs'] == 506, 'frozen source binding census')
    for original, row in sm.items():
        need(identity(normalized(row['snapshot']))['sha256'] == row['sha256'], 'retained or whole-omitted source pin')
    closure = load('actual-compiler-closure.json')
    need(len(closure['translation_units']) == result['actual_translation_units'] == 14 and len(closure['dependencies']) == result['actual_compiler_dependencies'] == 438, 'actual compiler closure census')
    deps = closure['dependencies']
    for path, row in deps.items():
        need(row['manifest_original'] in sm and sm[row['manifest_original']]['sha256'] == row['sha256'], 'actual dependency/source-manifest link')
    tu_names = [normalized(t['file']).rsplit('/', 1)[-1] for t in closure['translation_units']]
    required = {'audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'main.cpp', 'custom_flac_adapter.cpp', 'flac_decoder.cpp'}
    need(required <= set(tu_names) and 'native_audio_output.c' not in tu_names, 'whole production TU/immediate output seam scope')
    for row in closure['translation_units']:
        need(row['file'] in deps and row['actual_dependency_paths'] and all(p in deps for p in row['actual_dependency_paths']), 'actual TU dependency coverage')
    commit = load('production-source-commit.json')
    need(commit['commit'] == SOURCE_COMMIT and len(commit['files']) == 103, 'production Git identity table')
    tree = {}
    for line in get('production-source-tree.log').decode().splitlines():
        mode_kind_sha, name = line.split('\t', 1)
        tree[name] = mode_kind_sha.split()[-1]
    for name, row in commit['files'].items():
        body = get('sources/repository/' + name)
        need(sha(body) == row['raw_compiler_input_sha256'] and tree.get(name) == row['canonical_git_blob'], 'raw source/canonical Git tree identities')
        canonical = body.replace(b'\r\n', b'\n')
        need(hashlib.sha1(b'blob ' + str(len(canonical)).encode() + b'\0' + canonical).hexdigest() == row['canonical_git_blob'], 'pure canonical text Git blob check')
    need(get('production-source-commit.log').decode().strip() == SOURCE_COMMIT, 'original Git source receipt')
    need(get('sdk-head.log').decode().strip() == get('sdk-head-after.log').decode().strip() == SDK_COMMIT, 'original SDK before/after receipts')
    need(not get('sdk-tracked.log').strip() and not get('sdk-tracked-after.log').strip(), 'recorded clean SDK tracked state')

    # HOST scope remains separate from native measurements and omitted HOST payloads.
    host = load('sources/provenance/ordinary-host.json')
    legacy = load('sources/provenance/legacy-host.json')
    need(host['passed'] is True and host['physical_hardware'] is False and host['sanitizers'] == ['ASan', 'UBSan'], 'HOST sanitizer scope')
    need(host['exact_pcm_comparisons'] == len(host['pcm']) == 520 and len(host['lifecycle']) == 16 and len(host['registration']) == 2 and len(host['mutants']) == 3, 'HOST receipt finite census')
    need(Counter((x['name'], x['schedule']) for x in host['pcm']) == Counter((f['name'], s) for f in fixtures for s in (0, 1, 127, 2048)), 'HOST130/four-feed coverage')
    for row in host['pcm']:
        oracle = by_name[row['name']]
        need(row['pcm_bytes'] == oracle['pcm_bytes'] and row['pcm_sha256'] == oracle['pcm_sha256'], 'HOST/native prepared oracle identity')
    need(legacy['passed'] is True and legacy['physical_hardware'] is False and len(legacy['variants']) == 6 and all(isinstance(v, str) and 'PASS' in v for v in legacy['variants'].values()), 'six historical HOST lifecycle profile receipts')
    for label, receipt in [('ordinary-host', host), ('legacy-host', legacy)]:
        need(sha(get('sources/provenance/' + label + '.json')) == provenance['production_receipt'][label], 'exact HOST provenance receipt')
        for name, expected in receipt['source_sha256'].items():
            snap = 'sources/repository/' + name
            if snap in retained:
                need(sha(get(snap)) == expected, 'HOST/native overlapping frozen source bytes')

    # These terminal/tool/status rows are explicitly author-recorded from omitted originals.
    # Retained command output hashes are independently authenticated; omitted payloads are never opened.
    commands = index['commands']
    need(len(commands) == 367 and len({c['name'] for c in commands}) == 367, 'recorded command census')
    command_names = {c['name']: c for c in commands}
    for row in commands:
        need(row['exit_status'] == 0 and row['timed_out'] is False and row['elapsed_seconds'] >= 0, 'recorded authoritative command status')
        need(digest(row['command_json_sha256']) and all(digest(s) for s in row['argument_sha256']) and len(row['argument_sha256']) == len(row['display_arguments']), 'opaque exact command identities')
        if row['original_log'] in retained:
            need(sha(get(row['original_log'])) == row['output_sha256'], 'retained actual command output identity')
        elif row['original_log']:
            need(identity(row['original_log'])['sha256'] == row['output_sha256'], 'whole omitted command output identity only')
        else:
            need(row['binary_output_is_excluded_pcm'], 'only known FFmpeg binary output lacks a text log')
    need(abs(command_names['build']['elapsed_seconds'] - 115.156) < .001 and abs(command_names['qemu']['elapsed_seconds'] - 16.360) < .001, 'original terminal build/QEMU timings')
    need(command_names['qemu']['output_sha256'] == sha(get('qemu.log')), 'real UART command output binding')
    for row in commands:
        if row['binary_output_is_excluded_pcm']:
            need(any(row['output_sha256'] == f['pcm_sha256'] for f in fixtures), 'FFmpeg command/excluded oracle hash')
    runtime = index['runtime']
    need(len(runtime) == 12 and runtime == manifest['runtime_omitted_whole'], 'recorded runtime/tool whole omissions')
    need(len({r['id'] for r in runtime}) == 12 and all(r['id'].startswith('runtime:') and digest(r['id'][8:]) for r in runtime), 'opaque runtime locators')
    for row in runtime:
        need(digest(row['sha256']) and row['sha256'] == row['recorded_after_sha256'] and row['recorded_unchanged'] and row['bytes'] > 0, 'recorded unchanged runtime/tool identity')
    need(any(r['sha256'] == '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d' for r in runtime), 'actual QEMU runtime identity')
    for group, expected_count in [('live_sources', 506), ('frozen_sources', 506), ('runtime', 12), ('inputs_and_artifacts', 791)]:
        rows = index['post_run_verification'][group]
        need(len(rows) == expected_count and len({r['id'] for r in rows}) == expected_count and all(r['unchanged'] is True and digest(r['sha256']) for r in rows), 'recorded post-run unchanged-input census: ' + group)
        if group == 'live_sources':
            expected = {'source:' + sha(p.encode()): r['sha256'] for p, r in sm.items()}
        elif group == 'frozen_sources':
            expected = {normalized(r['snapshot']): r['sha256'] for r in sm.values()}
        elif group == 'runtime':
            expected = {r['id']: r['sha256'] for r in runtime}
        else:
            expected = dict(index['frozen_input_sha256'], **index['artifact_sha256'])
        need({r['id']: r['sha256'] for r in rows} == expected, 'recorded post-run identities match original binding inventory: ' + group)
        if group in ('frozen_sources', 'inputs_and_artifacts'):
            for row in rows:
                need(identity(row['id'])['sha256'] == row['sha256'], 'retained/omitted post-run identity')
    for group in ('frozen_input_sha256', 'artifact_sha256'):
        for name, expected in index[group].items():
            need(identity(name)['sha256'] == expected, 'pre-QEMU input/artifact hash closure')

    # Re-derive optional live scope from actual consumed origins, excluding broad metadata-only snapshots.
    consumed = {d['manifest_original'] for d in deps.values()}
    extra = set()
    for original, row in sm.items():
        snap = normalized(row['snapshot'])
        if row['role'] in ('campaign runner', 'Strict native event reader; HOST controls are separately labelled') or (snap.startswith('sources/harness/') and PurePosixPath(snap).name != 'README.md') or snap == 'sources/repository/tools/audio_test_server/generate_flac_depths.py' or (row['role'] == 'repository input; actual use recorded by compiler closure' and PurePosixPath(snap).name == 'CMakeLists.txt' and '/components/' in snap):
            extra.add(original)
    consumed |= extra
    original_root = normalized(next(k for k, v in sm.items() if v['role'] == 'campaign runner')).split('/tests/run-cyd-flac-ordinary-task-qemu.py')[0]
    derived = {}
    for original in consumed:
        if normalized(original).startswith(original_root + '/'):
            path = normalized(original)[len(original_root) + 1:]
            if not path.startswith('.build/'):
                row = sm[original]
                derived[path] = dict(path=path, sha256=row['sha256'], source_snapshot=normalized(row['snapshot']), reason='consumed orchestration/build/generator input' if original in extra else 'actual compiler dependency')
    current_rows = manifest['current_inputs']
    need(len(current_rows) == len(derived) == 73 and {r['path']: r for r in current_rows} == derived, 'derived actually-consumed live source scope')
    need(not any(r['path'].endswith('/native_audio_output.c') for r in current_rows), 'output driver excluded from native currentness claim')
    if require_current:
        root = HERE.parents[2]
        for row in current_rows:
            need(safe_relative(row['path']), 'current input relative path')
            live = root / row['path']
            need(live.is_file() and sha(live.read_bytes()) == row['sha256'], 'actually consumed input changed: ' + row['path'])
    inventory = json.loads((HERE / 'source-commit-inventory.json').read_text(encoding='utf-8'))
    need(len(inventory) == 13 and len({r['path'] for r in inventory}) == 13, 'coherent source commit inventory')
    return dict(passed=True, data_only=True, require_current=require_current,
                retained_originals=len(retained), unique_text_members=len(data), omitted_whole=len(omissions),
                omitted_runtime_payloads=len(runtime), actual_translation_units=14, actual_dependencies=438,
                actually_consumed_repository_inputs=len(derived), original_lifecycle_cases=3,
                native_fixture_types=3, prepared_fixtures=130, positive_iterations=382, positive_elapsed_us=15033371,
                host_exact_pcm_checks=520, host_lifecycle_groups=16, separate_host_lifecycle_profiles=6,
                recorded_terminal_status='PASS; omitted report/status rows are author-recorded metadata',
                independent_omitted_report_or_binary_authentication=False,
                full_radio_hardware_output_driver_or_resource_margin_claim=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.require_current), sort_keys=True))
    except (ValueError, KeyError, OSError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
