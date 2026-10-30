"""Verify saved Opus task evidence as data; never build, decode or start QEMU."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-opus-20261030'
TASK_SHA = '7daa9533d45166673e55cbf4301565a0bd126a758b2dc1e87ca15f5299e30ebc'
DIRECT_SHA = '5e49b9bbf143917ee370fa1c6984ac8e96eb73b3110a89a91178176f0d7d3acc'
COMMON_SHA = '633043d1cb61a27009f655c48f42deec198b33c556a8a73712f401aa0490bf6c'
PCM_SHA = 'a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b'


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


def verify():
    manifest = json.loads((FOLDER / 'task-manifest.json').read_bytes())
    files = load_archive(manifest, 'task-captures.zip')

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
    reader = canonical_module('tests/run-cyd-espressif-opus-task-qemu.py', TASK_SHA, 'reviewed_opus_task_reader')
    direct_reader = canonical_module('tests/run-cyd-espressif-opus-qemu.py', DIRECT_SHA, 'reviewed_opus_direct_reader')

    link = manifest['direct_checkpoint']
    direct_manifest_path = FOLDER / 'direct-manifest.json'
    need(sha(direct_manifest_path.read_bytes()) == link['manifest_sha256'] and
         take('reference/direct-manifest.json') == direct_manifest_path.read_bytes(), 'separate direct checkpoint manifest binding')
    direct_manifest = json.loads(direct_manifest_path.read_bytes())
    need(direct_manifest['archive']['sha256'] == link['archive_sha256'], 'separate direct archive identity')
    direct_files = load_archive(direct_manifest, 'direct-captures.zip')
    direct_omitted = {row['path']: row for category in ('compiled_images_omitted', 'other_bytes_omitted')
                      for row in direct_manifest.get(category, [])}

    def direct_hash(name, digest):
        if name in direct_files:
            need(sha(direct_files[name]) == digest, 'published external direct-reference byte binding')
        else:
            need(name in direct_omitted and direct_omitted[name]['sha256'] == digest and
                 direct_omitted[name]['original_retained_locally'] and
                 direct_omitted[name]['byte_payload_published'] is False, 'explicit external omission hash provenance')

    direct_prefix = 'captures/direct02/'
    direct_report = json.loads(direct_files[direct_prefix + 'report.json'])
    baseline = json.loads(direct_files[direct_prefix + 'baseline.json'])
    direct_log = (direct_files[direct_prefix + 'qemu.stdout.log'] + b'\n' +
                  direct_files[direct_prefix + 'qemu.stderr.log']).decode('utf-8')
    direct_measured = direct_reader.validate_log(direct_log)
    need(direct_report['passed'] and direct_report['completed'] and direct_report['target_executed'] and
         direct_measured == direct_report['measurements'] and baseline == direct_report['baseline'] == direct_measured['reference'],
         'complete original unchanged-vendor reference transcript')
    need(baseline['pcm_bytes'] == 2115840 and baseline['pcm_sha256'] == PCM_SHA and
         baseline['input_consumed'] == 706319 and baseline['sample_rate'] == 48000 and
         baseline['channels'] == 2 and baseline['bits_per_sample'] == 16,
         'measured raw vendor PCM is distinct from logical trimmed playback')

    prefix = 'captures/task01/'
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
         row['byte_payload_published'] is False and name.endswith(('.elf', '.bin'))
         for name, row in omitted_images.items()), 'all selected compiled image byte payloads stay local')
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False and
         '/sources/compiler-dependencies/' in name for name, row in withheld.items()), 'installed header omissions are explicit')
    need(not any(name.endswith(('.elf', '.bin')) for name in files), 'archive publishes no firmware or diagnostic images')

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
         len(closure['dependencies']) == report['actual_compiler_dependencies'], 'actual GCC/Ninja closure census')
    for pin in closure['dependencies'].values():
        need(pin['manifest_original'] in bundle['sources'] and
             pin['sha256'] == bundle['sources'][pin['manifest_original']]['sha256'], 'actual dependency resolves to saved source identity')
    need({'audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'main.cpp',
          'adaptive_input.c', 'native_network_power.c'} <=
         {PurePosixPath(row['file'].replace('\\', '/')).name for row in closure['translation_units']},
         'complete production audio/state/health and actual shared RTOS queue/network sources')
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
        if row['kind'] == 'direct-checkpoint':
            direct_hash(row['logical_path'], row['sha256'])
        else:
            need(row['kind'] == 'installed-runtime-identity' and row['original_pre_post_binding_verified'] and
                 row['byte_payload_published'] is False, 'installed runtime identity only; no installed binary byte-copy claim')
    log = (take(prefix + 'qemu.stdout.log') + b'\n' + take(prefix + 'qemu.stderr.log')).decode('utf-8')
    measured = reader.validate_log(log, baseline)
    need(measured == report['measurements'] == manifest['measurements'], 'all three actual task cases and full PCM identity')

    witness_prefix = 'checks/reference-witness01/'
    witness = data(witness_prefix + 'report.json')
    stdout = take(witness_prefix + 'stdout.log')
    stderr = take(witness_prefix + 'stderr.log')
    need(witness['passed'] and witness['pid'] > 0 and witness['exit_status'] == 0 and
         sha(stdout) == witness['stdout_sha256'] and sha(stderr) == witness['stderr_sha256'] and
         json.loads(stdout) == witness['measurement'] and witness['measurement']['rejected'] == 19 and
         len(set(witness['measurement']['cases'])) == 19 and witness['measurement']['valid_native_reference_accepted'] and
         not witness['measurement']['native_process_started'] and not witness['measurement']['files_modified'],
         'actual nineteen negative reference-witness checks remain bound to original stdout and child status')
    for original, digest in witness['sources'].items():
        need(sha(take(witness_prefix + 'sources/' + original)) == digest, 'exact negative-check source snapshot')
    gap = manifest['required_pending_correctness_gap']
    need(gap == dict(vendor_raw_pcm_bytes=2115840, logical_pcm_bytes=2112000, preskip_frames=312,
                     tail_padding_frames=648, required_pending=True, resolved=False),
         'known pre-skip/end-trim correctness gap remains explicitly required and unresolved')
    return dict(passed=True, logical_files=len(files), physical_files=manifest['physical_files'],
                cases=list(measured['cases']), full_vendor_pcm_bytes=2115840, logical_pcm_bytes=2112000,
                required_trim_gap_pending=True, rejected_reference_controls=19, artifact_code_executed=False,
                actual_native_runs_repeated=False, omitted_image_files=len(omitted_images),
                omitted_installed_header_files=len(withheld), omitted_binary_bytes_verified=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
