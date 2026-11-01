"""Verify saved long-packet Opus task evidence as data; never build, decode or start QEMU."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-opus-20261030'
TASK_SHA = 'b2d595f0111f1a091a670027f9837f63af68ec75045905c1701c0e94ce8f6a59'
DIRECT_SHA = 'cd08d66e23d973307858d02924937278c0787fe9a58cad9ae8d39d741a30384c'
COMMON_SHA = '633043d1cb61a27009f655c48f42deec198b33c556a8a73712f401aa0490bf6c'
PCM_SHA = '670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load_archive(manifest, expected_name):
    archive_path = FOLDER / manifest['archive']['path']
    need(archive_path.name == expected_name and archive_path.parent == FOLDER and
         archive_path.stat().st_size == manifest['archive']['bytes'] and
         sha(archive_path.read_bytes()) == manifest['archive']['sha256'], 'exact complete archive identity')
    rows = manifest['files']
    need(len({row['path'] for row in rows}) == len(rows) == manifest['logical_files'], 'unique logical inventory')
    blobs = {row['blob'] for row in rows}
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.infolist()) == len(blobs) == manifest['physical_files'] and
             set(archive.namelist()) == blobs, 'complete deduplicated physical members')
        physical = {}
        for name in blobs:
            need(re.fullmatch(r'blobs/[0-9a-f]{64}', name), 'canonical physical blob name')
            body = archive.read(name)
            need(name == 'blobs/' + sha(body), 'every published physical byte')
            physical[name] = body
    files = {}
    for row in rows:
        path = PurePosixPath(row['path'])
        need(path.as_posix() == row['path'] and not path.is_absolute() and '..' not in path.parts and
             '\\' not in row['path'] and ':' not in row['path'], 'canonical logical path')
        body = physical[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'every published logical byte')
        files[row['path']] = body
    return files


def canonical_module(relative, digest, name):
    path = ROOT / relative
    need(sha(path.read_bytes()) == digest, 'pinned reviewed canonical reader: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def independently_recount_resize(log):
    """Separate token reader verifies observed transitions, not summary flags."""
    prefix = 'CYD_OPUS_LONG_OBS_'
    groups = {instance: {} for instance in range(1, 6)}
    for line in log.replace('\r\n', '\n').splitlines():
        if not line.startswith(prefix):
            continue
        pieces = line.split()
        tag = pieces[0][len(prefix):]
        need(tag in ('INITIAL', 'RESIZE', 'RETRY', 'CLOSE'), 'known independently read observation')
        pairs = [piece.split('=') for piece in pieces[1:]]
        need(all(len(pair) == 2 for pair in pairs) and len({pair[0] for pair in pairs}) == len(pairs),
             'unique complete public observation fields')
        row = {key: int(value) for key, value in pairs}
        need(row['instance'] in groups and tag not in groups[row['instance']], 'one actual observation of each type per observed handle')
        groups[row['instance']][tag] = row
    handles = []
    offset = 0
    for instance in range(1, 6):
        group = groups[instance]
        need(set(group) == {'INITIAL', 'RESIZE', 'RETRY', 'CLOSE'}, 'each real handle has all four direct observations')
        initial, error, retry, close = [group[tag] for tag in ('INITIAL', 'RESIZE', 'RETRY', 'CLOSE')]
        need(initial['call'] == 1 and initial['global_call'] == offset + 1 and initial['capacity'] == 12288,
             'real initial capacity and call counter')
        need(error['call'] == (11 if instance == 1 else 10) and error['global_call'] == offset + error['call'] and
             error['len_before'] == error['raw_len'] == 2047 and error['consumed'] == error['decoded_size'] == 0 and
             error['needed_size'] == 23040 and error['capacity'] == 12288 and error['eos'] == 0 and error['result'] == -8,
             'independent actual buffer error fields on every observed handle')
        need(retry['call'] == error['call'] + 1 and retry['global_call'] == error['global_call'] + 1 and
             retry['capacity'] == 23040 and retry['raw_len'] == 2047 and retry['eos'] == 0 and
             retry['arguments_unchanged'] == 1 and retry['consumed'] == 2047 and
             retry['decoded_size'] == 23040 and retry['result'] == 0,
             'immediate real retry emits the full long PCM packet with unchanged encoded input')
        need(close['calls'] == (698 if instance == 1 else 19 if instance in (2, 4) else 697) and
             close['resizes'] == close['retries'] == 1 and close['last_capacity'] == 23040 and
             close['global_calls'] == offset + close['calls'], 'independent real close and per-handle call census')
        offset = close['global_calls']
        handles.append(dict(instance=instance, initial_capacity=initial['capacity'], resize_call=error['call'],
                            resize_global_call=error['global_call'], input_bytes_at_resize=error['raw_len'],
                            resized_capacity=retry['capacity'], retry_decoded_pcm=retry['decoded_size'],
                            public_calls=close['calls'], real_resizes=close['resizes'], real_retries=close['retries']))
    need(offset == 2130, 'independently summed native public calls')
    return dict(handles=handles, public_calls=offset, real_resizes=5, real_retries=5,
                all_observed_errors_nonterminal=True, all_error_consumed_zero=True,
                all_error_decoded_zero=True, all_immediate_retry_arguments_unchanged=True)


def reject_tampered_resize_records(reader, log, baseline):
    """Data-only contradictory controls never alter the original saved logs."""
    normalized = log.replace('\r\n', '\n')
    lines = normalized.splitlines()
    def first(tag): return next(line for line in lines if line.startswith('CYD_OPUS_LONG_OBS_' + tag + ' '))
    initial, error, retry, close = [first(tag) for tag in ('INITIAL', 'RESIZE', 'RETRY', 'CLOSE')]
    final = next(line for line in lines if line.startswith('CYD_OPUS_LONG_TASK_COMPLETE '))
    controls = [
        (error, ''),
        (error, error.replace('needed_size=23040', 'needed_size=23039')),
        (error, error.replace('consumed=0', 'consumed=1')),
        (error, error.replace('decoded_size=0', 'decoded_size=23040')),
        (retry, retry.replace('capacity=23040', 'capacity=12288')),
        (retry, retry.replace('arguments_unchanged=1', 'arguments_unchanged=0')),
        (retry, retry.replace('global_call=12', 'global_call=13')),
        (initial, initial.replace('capacity=12288', 'capacity=23040')),
        (close, ''),
        (final, final.replace('resize_requests=5', 'resize_requests=4')),
    ]
    rejected = 0
    for original, altered in controls:
        need(original != altered and normalized.count(original) == 1, 'specific unique contradictory control')
        try:
            reader.validate_log(normalized.replace(original, altered, 1), baseline)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('contradictory public resize witness unexpectedly accepted')
    return rejected


def verify():
    manifest = json.loads((FOLDER / 'long-task-manifest.json').read_bytes())
    files = load_archive(manifest, 'long-task-captures.zip')

    def take(name):
        need(name in files, 'required saved byte payload: ' + name)
        return files[name]

    def data(name):
        return json.loads(take(name))

    need(manifest['passed'] and not manifest['physical_device'] and not manifest['production_firmware'] and
         not manifest['independent_numeric_oracle'] and not manifest['radio_tls_resource_margins_qualified'],
         'bounded synthetic-transport/output integration scope')
    need(sha(take('verification/task-reader.py')) == TASK_SHA == manifest['controller_sha256'] and
         sha(take('verification/direct-reader.py')) == DIRECT_SHA and
         sha(take('verification/common-reader.py')) == COMMON_SHA and
         take('verification/verifier.py') == Path(__file__).read_bytes() and
         sha(Path(__file__).read_bytes()) == manifest['verifier_sha256'], 'exact reviewed reader/verifier identities')
    reader = canonical_module('tests/run-cyd-espressif-opus-long-task-qemu.py', TASK_SHA, 'reviewed_opus_task_reader')
    direct_reader = canonical_module('tests/run-cyd-espressif-opus-resize-stream-qemu.py', DIRECT_SHA, 'reviewed_opus_direct_reader')

    link = manifest['fragmented_checkpoint']
    direct_manifest_path = FOLDER / 'resize-stream-manifest.json'
    need(sha(direct_manifest_path.read_bytes()) == link['manifest_sha256'] and
         take('reference/resize-stream-manifest.json') == direct_manifest_path.read_bytes(), 'separate direct checkpoint manifest binding')
    direct_manifest = json.loads(direct_manifest_path.read_bytes())
    need(direct_manifest['archive']['sha256'] == link['archive_sha256'], 'separate direct archive identity')
    direct_files = load_archive(direct_manifest, 'resize-stream-captures.zip')
    direct_omitted = {row['path']: row for category in ('compiled_images_omitted', 'other_bytes_omitted')
                      for row in direct_manifest.get(category, [])}

    def direct_hash(name, digest):
        if name in direct_files:
            need(sha(direct_files[name]) == digest, 'published external direct-reference byte binding')
        else:
            need(name in direct_omitted and direct_omitted[name]['sha256'] == digest and
                 direct_omitted[name]['original_retained_locally'] and
                 direct_omitted[name]['byte_payload_published'] is False, 'explicit external omission hash provenance')

    direct_prefix = 'captures/resize-stream01/'
    direct_report = json.loads(direct_files[direct_prefix + 'report.json'])
    baseline = json.loads(direct_files[direct_prefix + 'baseline.json'])
    direct_log = (direct_files[direct_prefix + 'qemu.stdout.log'] + b'\n' +
                  direct_files[direct_prefix + 'qemu.stderr.log']).decode('utf-8')
    direct_measured = direct_reader.validate_log(direct_log)
    need(direct_report['passed'] and direct_report['completed'] and direct_report['target_executed'] and
         direct_measured == direct_report['measurements'] and baseline == direct_report['baseline'] == direct_measured['reference'],
         'complete original unchanged-vendor reference transcript')
    need(baseline['pcm_bytes'] == 2119680 and baseline['pcm_sha256'] == PCM_SHA and
         baseline['input_consumed'] == 707097 and baseline['sample_rate'] == 48000 and
         baseline['channels'] == 2 and baseline['bits_per_sample'] == 16,
         'measured raw vendor PCM is distinct from logical trimmed playback')

    prefix = 'captures/long-task01/'
    report = data(prefix + 'report.json')
    bundle = data(prefix + 'execution-bundle.json')
    need(sha(take(prefix + 'report.json')) == manifest['campaign']['original_report_sha256'] and
         sha(take(prefix + 'execution-bundle.json')) == manifest['campaign']['original_execution_bundle_sha256'],
         'exact original task report and execution bundle')
    need(report['passed'] and report['completed'] and report['target_executed'] and
         report['all_bound_inputs_current'] and not report['bound_input_failures'] and
         bundle['sources'] == data(prefix + 'source-manifest.json'), 'original terminal passing task and complete source binding')
    need(bundle['pcm_reference'] == report['pcm_reference'] == baseline, 'actual task uses the measured separate vendor reference')
    omitted_images = {row['path']: row for row in manifest['compiled_images_omitted']}
    withheld = {row['path']: row for row in manifest['installed_header_bytes_omitted']}
    privacy = data('inventory/omissions.json')
    need(privacy['installed_header_bytes_omitted'] == manifest['installed_header_bytes_omitted'] and
         privacy['compiled_images_omitted'] == manifest['compiled_images_omitted'] and
         privacy['original_reports_unchanged'] and privacy['original_images_retained_locally'],
         'complete exact omission inventory and original local retention')
    need(omitted_images and all(name not in files and row['original_retained_locally'] and
         row['byte_payload_published'] is False and row['image_format'] in ('ELF executable', 'raw binary image')
         for name, row in omitted_images.items()), 'all selected compiled image byte payloads stay local')
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False and
         '/sources/compiler-dependencies/' in name for name, row in withheld.items()), 'installed header omissions are explicit')
    need(not any(name.endswith(('.elf', '.bin')) or (body.startswith(b'\x7fELF') and int.from_bytes(body[16:18], 'little') != 1)
                 for name, body in files.items()), 'archive publishes no firmware or diagnostic executable images')

    def artifact_hash(name, digest):
        if name in omitted_images:
            need(omitted_images[name]['sha256'] == digest, 'omitted image hash provenance; omitted bytes are not read')
        else:
            need(sha(take(name)) == digest, 'published artifact byte binding')

    for original, pin in bundle['sources'].items():
        name = prefix + pin['snapshot']
        if name in withheld:
            need(withheld[name]['original_path'] == original and withheld[name]['sha256'] == pin['sha256'] and
                 withheld[name]['bytes'] == pin['bytes'], 'omitted installed header retains exact original dependency identity')
        else:
            need(sha(take(name)) == pin['sha256'] and len(take(name)) == pin['bytes'], 'every frozen source/dependency byte binding')
    for name, digest in bundle['artifacts'].items():
        artifact_hash(prefix + name, digest)
    need(sha(take(prefix + 'sources/controller.py')) == TASK_SHA, 'executed task campaign uses the reviewed controller')
    for command in report['commands']:
        need(command['state'] == 'complete' and command['pid'] > 0 and command['exit_status'] == 0, 'actual native command terminal zero')
        for stream in ('stdout', 'stderr'):
            need(sha(take(prefix + command['name'] + '.' + stream + '.log')) == command[stream + '_sha256'], 'original command log identity')
    need(len({row['name'] for row in report['commands']}) == len(report['commands']) and
         {'build', 'qemu', 'merge', 'compiler-version'} <= {row['name'] for row in report['commands']}, 'unique complete actual task command inventory')
    child = json.loads(take(prefix + 'sdk-child.json').decode('utf-8-sig'))
    need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK compiler-driver child terminal status')
    closure = data(prefix + 'actual-compiler-closure.json')
    need(len(closure['translation_units']) == report['actual_translation_units'] and
         len(closure['dependencies']) == report['actual_compiler_dependencies'] and
         report['actual_translation_units'] == 11 and report['actual_compiler_dependencies'] == 416, 'actual GCC/Ninja complete eleven-TU /416-dependency census')
    for pin in closure['dependencies'].values():
        need(pin['manifest_original'] in bundle['sources'] and
             pin['sha256'] == bundle['sources'][pin['manifest_original']]['sha256'], 'actual dependency resolves to saved source identity')
    need({'audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'main.cpp',
          'adaptive_input.c', 'native_network_power.c'} <=
         {PurePosixPath(row['file'].replace('\\', '/')).name for row in closure['translation_units']},
         'complete production audio/state/health and actual shared RTOS queue/network sources')
    expected_tus = {'icy_title.c', 'adaptive_input.c', 'native_network_power.c', 'audio_decoder_reg.c',
                    'audio_encoder_reg.c', 'simple_decoder_reg.c', 'main.cpp', 'audio_service.c',
                    'native_state.c', 'native_health.c', 'decoder_registration.c'}
    need({PurePosixPath(row['file'].replace('\\', '/')).name for row in closure['translation_units']} == expected_tus,
         'all eleven exact selected translation units are retained')
    compiler_commands = data(prefix + 'build/compile_commands.json')
    for row in closure['translation_units']:
        command_rows = [candidate for candidate in compiler_commands if candidate['file'] == row['file']]
        need(len(command_rows) == 1 and all(row.get(key) == value for key, value in command_rows[0].items()),
             'each selected TU retains its exact original compiler-command row')
        normalized = row['file'].replace('\\', '/')
        need('/sources/' in normalized, 'actual selected translation unit is a frozen source')
        snapshot = 'sources/' + normalized.split('/sources/', 1)[1]
        pins = [pin for pin in bundle['sources'].values() if pin['snapshot'] == snapshot]
        need(len(pins) == 1 and sha(take(prefix + snapshot)) == pins[0]['sha256'],
             'each actual translation unit joins to its exact published frozen bytes')
        object_name = row['output'].replace('\\', '/')
        if '/build/' in object_name:
            object_name = object_name.split('/build/', 1)[1]
        if not object_name.startswith('build/'):
            object_name = 'build/' + object_name
        need(object_name in bundle['artifacts'], 'actual selected object joins to executed artifact inventory')
        artifact_hash(prefix + object_name, bundle['artifacts'][object_name])
        actual_paths = {name.replace('\\', '/').casefold() for name in row['actual_dependency_paths']}
        dependency_paths = {name.replace('\\', '/').casefold() for name in closure['dependencies']}
        need(normalized.casefold() in actual_paths and actual_paths <= dependency_paths,
             'every selected TU and its actual Ninja dependencies resolve to retained identities')
    config = data(prefix + 'build/config/sdkconfig.json')
    need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ'] == 1000 and
         not config.get('YORADIO_HTTP_REQUEST_BUFFER_RELEASE', False) and not config.get('YORADIO_FLAC_DECODER_CUSTOM', False),
         'original dual-core scheduler and explicit diagnostic profile')
    for key in ('COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'HEAP_POISONING_LIGHT',
                'FREERTOS_CHECK_STACKOVERFLOW_CANARY', 'ESP_TASK_WDT_EN', 'ESP_TASK_WDT_INIT',
                'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1',
                'AUDIO_DECODER_OPUS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
        need(config.get(key) is True, 'actual target configuration: ' + key)
    runtime_rows = data('inventory/runtime-bindings.json')
    need(len({row['key'] for row in runtime_rows}) == len(runtime_rows) == len(bundle['runtime']), 'complete runtime and external-reference binding inventory')
    for row in runtime_rows:
        need(bundle['runtime'][row['key']] == row['sha256'], 'original runtime digest retained')
        if row['kind'] == 'fragmented-checkpoint':
            direct_hash(row['logical_path'], row['sha256'])
        else:
            need(row['kind'] == 'installed-runtime-identity' and row['original_pre_post_binding_verified'] and
                 row['byte_payload_published'] is False, 'installed runtime identity only; no installed binary byte-copy claim')
    log = (take(prefix + 'qemu.stdout.log') + b'\n' + take(prefix + 'qemu.stderr.log')).decode('utf-8')
    measured = reader.validate_log(log, baseline)
    need(measured == report['measurements'] == manifest['measurements'], 'all three actual task cases and full PCM identity')

    public_witness = independently_recount_resize(log)
    need(public_witness == manifest['independent_resize_witness'], 'independent five-handle resize and retry accounting')
    rejected = reject_tampered_resize_records(reader, log, baseline)
    need(rejected == manifest['rejected_resize_witness_controls'] == 10, 'all ten contradictory witness controls rejected')
    gap = manifest['required_pending_correctness_gap']
    need(gap == dict(vendor_raw_pcm_bytes=2119680, logical_pcm_bytes=2112000, preskip_frames=312,
                     tail_padding_frames=1608, required_pending=True, resolved=False),
         'known pre-skip/end-trim correctness gap remains explicitly required and unresolved')
    return dict(passed=True, logical_files=len(files), physical_files=manifest['physical_files'],
                cases=list(measured['cases']), full_vendor_pcm_bytes=2119680, logical_pcm_bytes=2112000,
                required_trim_gap_pending=True, verified_public_resize_handles=5, rejected_resize_witness_controls=rejected, artifact_code_executed=False,
                actual_native_runs_repeated=False, omitted_image_files=len(omitted_images),
                omitted_installed_header_files=len(withheld), omitted_binary_bytes_verified=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
