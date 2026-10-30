"""Verify saved fragmented public Opus resize evidence as data; no builds or native runs."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-opus-20261030'
READER_SHA = 'cd08d66e23d973307858d02924937278c0787fe9a58cad9ae8d39d741a30384c'
FIXTURE_SHA = 'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
FIXTURE_AUDIT_SHA = 'b31791eb3ba1a4f7159db4cfb06358b7cf52e512417e40993f9bc1ca70fc76d6'
PCM_SHA = '670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def canonical_module(relative, expected, name):
    path = ROOT / relative
    need(sha(path.read_bytes()) == expected, 'pinned reviewed canonical data-only module: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    manifest = json.loads((FOLDER / 'resize-stream-manifest.json').read_bytes())
    archive_path = FOLDER / manifest['archive']['path']
    need(archive_path.name == 'resize-stream-captures.zip' and archive_path.parent == FOLDER and
         archive_path.stat().st_size == manifest['archive']['bytes'] and
         sha(archive_path.read_bytes()) == manifest['archive']['sha256'], 'complete published archive identity')
    rows = manifest['files']
    need(len({row['path'] for row in rows}) == len(rows) == manifest['logical_files'], 'complete unique logical inventory')
    blobs = {row['blob'] for row in rows}
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.infolist()) == len(blobs) == manifest['physical_files'] and
             set(archive.namelist()) == blobs, 'complete deduplicated physical inventory')
        physical = {}
        for name in blobs:
            need(re.fullmatch(r'blobs/[0-9a-f]{64}', name), 'canonical physical member name')
            body = archive.read(name)
            need(name == 'blobs/' + sha(body), 'every published physical byte')
            physical[name] = body
    files = {}
    for row in rows:
        path = PurePosixPath(row['path'])
        need(path.as_posix() == row['path'] and not path.is_absolute() and '..' not in path.parts and
             '\\' not in row['path'] and ':' not in row['path'] and path.suffix.lower() not in ('.elf', '.bin'),
             'canonical logical path without compiled image payloads')
        body = physical[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'every published logical byte')
        files[row['path']] = body

    def take(name):
        need(name in files, 'required saved byte payload: ' + name)
        return files[name]

    def data(name):
        return json.loads(take(name))

    omitted = {row['path']: row for row in manifest['compiled_images_omitted']}
    other = {row['path']: row for row in manifest['other_bytes_omitted']}
    need(omitted and len(omitted) == len(manifest['compiled_images_omitted']) and
         all(name not in files and PurePosixPath(name).suffix.lower() in ('.bin', '.elf') and
             row['bytes'] > 0 and re.fullmatch('[a-f0-9]{64}', row['sha256']) and
             row['original_retained_locally'] and row['byte_payload_published'] is False for name, row in omitted.items()),
         'explicit local-only image identities; omitted binary bytes are not verified')
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False
             for name, row in other.items()), 'explicit whole-payload publication exclusions')
    need(take('verification/verifier.py') == Path(__file__).read_bytes() and
         manifest['verifier_sha256'] == sha(Path(__file__).read_bytes()) and
         sha(take('verification/reader.py')) == READER_SHA == manifest['controller_sha256'],
         'exact standalone verifier and reviewed canonical reader')
    reader = canonical_module('tests/run-cyd-espressif-opus-resize-stream-qemu.py', READER_SHA, 'reviewed_opus_resize_reader')
    audit_reader = canonical_module('tests/fixtures/opus_ogg_long_packets/generate.py',
                                    FIXTURE_AUDIT_SHA, 'reviewed_opus_long_packet_audit')
    need(sha(take('reference/fixture/generate.py')) == FIXTURE_AUDIT_SHA, 'exact canonical independent fixture audit source')
    prefix = 'captures/resize-stream01/'
    report = data(prefix + 'report.json')
    need(report['passed'] and report['completed'] and report['observation_completed'] and report['target_executed'] and
         report['target'] == 'esp32' and report['fixture_sha256'] == FIXTURE_SHA and report['fixture_bytes'] == 707097 and
         report['vendor_revision'] == reader.REVISION and report['sdk_revision'] == reader.SDK_HEAD['esp32'] and
         report['initial_output_capacity'] == 12288 and report['baseline_output_capacity'] == 24576,
         'actual unchanged LX6 public-vendor long-packet observation')
    need(not report['production_firmware'] and not report['physical_device'] and not report['private_abi_used'] and
         not report['custom_decoder'] and not report['full_conformance_qualified'], 'bounded public diagnostic scope')
    need([row['name'] for row in report['commands']] ==
         ['vendor-head', 'vendor-clean', 'sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu'],
         'complete unique native command inventory')
    for row in report['commands']:
        need(row['state'] == 'complete' and row['pid'] > 0 and row['exit_status'] == 0, 'actual child terminal zero')
        for stream in ('stdout', 'stderr'):
            need(sha(take(prefix + row['name'] + '.' + stream + '.log')) == row[stream + '_sha256'],
                 'every original native child log byte')
    child = json.loads(take(prefix + 'sdk-child.json').decode('utf-8-sig'))
    need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK compiler-driver child terminal zero')
    for name, expected in (('sdk', reader.SDK_HEAD['esp32']), ('vendor', reader.REVISION)):
        need(take(prefix + name + '-head.stdout.log').decode('utf-8').strip() == expected and
             not take(prefix + name + '-clean.stdout.log').strip(), 'actual clean pinned repository identity: ' + name)
    mandatory = {'build/cyd_espressif_opus_resize_stream_qemu.elf', 'build/cyd_espressif_opus_resize_stream_qemu.bin',
                 'build/cyd_espressif_opus_resize_stream_qemu.map', 'qemu-flash.bin', 'sdkconfig', 'sdk-child.json',
                 'build/bootloader/bootloader.bin', 'build/partition_table/partition-table.bin',
                 'build/compile_commands.json', 'build/project_description.json', 'build/flasher_args.json'}
    need(mandatory <= set(report['build_outputs']) and report['inputs'], 'complete build and source witness inventories')
    snapshots = {pin['snapshot'] for pin in report['inputs'].values()}
    need({'sources/controller.py', 'project/main/main.c', 'project/main/CMakeLists.txt', 'project/CMakeLists.txt',
          'project/sdk-build.ps1', 'project/main/fixture.ogg', 'project/main/decoder_registration.c',
          'project/main/decoder_registration.h', 'project/main/decoder_pending_input.h', 'project/main/decoder_eof_input.h',
          'sources/vendor/esp_audio_codec/lib/esp32/libesp_audio_codec.a',
          'sources/vendor/esp_audio_codec/lib/esp32/libesp_audio_simple_dec.a'} <= snapshots,
         'required actual harness, registration, fixture and vendor source bindings')
    need(sha(take(prefix + 'sources/controller.py')) == READER_SHA, 'exact executed native campaign controller')
    for pin in report['inputs'].values():
        name = prefix + pin['snapshot']
        if name in other:
            need(other[name]['sha256'] == pin['sha256'] and other[name]['bytes'] == pin['bytes'], 'omitted source hash provenance')
        else:
            body = take(name)
            need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'every frozen published source byte')
    for name, digest in report['build_outputs'].items():
        logical = prefix + name
        if logical in omitted:
            need(omitted[logical]['sha256'] == digest, 'explicit omitted image hash binding')
        elif logical in other:
            need(other[logical]['sha256'] == digest, 'explicit omitted output hash binding')
        else:
            need(sha(take(logical)) == digest, 'every published build artifact byte binding')
    for name, digest in zip(('libesp_audio_codec.a', 'libesp_audio_simple_dec.a'), reader.ARCHIVES['esp32']):
        need(sha(take(prefix + 'sources/vendor/esp_audio_codec/lib/esp32/' + name)) == digest,
             'unchanged exact Xtensa vendor archive')
    need(report['tools']['qemu']['sha256'] == reader.QEMU_SHA['esp32'], 'pinned native emulator identity')
    build_argv = report['commands'][4]['argv']
    campaign_path = build_argv[build_argv.index('-Campaign') + 1].replace('\\', '/').rstrip('/')
    qemu_argv = report['commands'][-1]['argv']
    need(qemu_argv[0].replace('\\', '/') == report['tools']['qemu']['path'].replace('\\', '/') and
         qemu_argv[qemu_argv.index('-drive') + 1].replace('\\', '/') ==
         'file=' + campaign_path + '/qemu-flash.bin,if=mtd,format=raw' and
         qemu_argv[qemu_argv.index('-smp') + 1] == '2' and qemu_argv[qemu_argv.index('-nic') + 1] == 'none' and
         '-snapshot' in qemu_argv and '-no-reboot' in qemu_argv,
         'actual pinned QEMU invocation uses the bound local-only image without persistence or network')
    description = data(prefix + 'build/project_description.json')
    need(description['target'] == 'esp32' and description['app_elf'] == 'cyd_espressif_opus_resize_stream_qemu.elf',
         'actual ESP32 diagnostic build description')
    commands = data(prefix + 'build/compile_commands.json')
    for source in ('main.c', 'decoder_registration.c'):
        actual = [row for row in commands if row['file'].replace('\\', '/') == campaign_path + '/project/main/' + source]
        need(len(actual) == 1 and '-include' not in actual[0]['command'], 'complete unchanged compiled source: ' + source)
    symbols = take(prefix + 'symbols.stdout.log').decode('utf-8').replace('\r\n', '\n')
    for name in ('decoder_register_codecs', 'esp_opus_dec_open', 'esp_opus_dec_decode', 'esp_audio_simple_dec_process'):
        need(re.search(r'\b' + name + '$', symbols, re.M), 'actual linked public interface: ' + name)
    need(not re.search(r'\b(?:__wrap_(?:esp_vorbis_|esp_audio_|esp_ogg_|floor[01]_|media_lib_)|native_vorbis_)[A-Za-z0-9_]*$',
                       symbols, re.M), 'no private decoder wrappers or custom codec linked')
    config = data(prefix + 'build/config/sdkconfig.json')
    need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ'] == 1000, 'actual dual-core scheduler configuration')
    for key in ('COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'HEAP_POISONING_LIGHT', 'FREERTOS_CHECK_STACKOVERFLOW_CANARY',
                'ESP_TASK_WDT_EN', 'ESP_TASK_WDT_INIT', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0',
                'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1', 'AUDIO_DECODER_OPUS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
        need(config[key] is True, 'actual configuration: ' + key)
    log = (take(prefix + 'qemu.stdout.log') + b'\n' + take(prefix + 'qemu.stderr.log')).decode('utf-8')
    measured = reader.validate_log(log)
    need(measured == report['measurements'] == manifest['measurements'] and
         measured['reference'] == report['baseline'] == data(prefix + 'baseline.json'), 'original full public observation recounted')
    events = measured['resize_events']
    need(len(events) == 3 and [(row['chunk'], row['call'], row['len_before']) for row in events] ==
         [(4096, 3, 4095), (257, 63, 256), (1, 8046, 1)] and
         all(row['strategy'] == 'current_unchanged' and row['result'] == -8 and row['consumed'] == row['decoded_size'] == 0 and
             row['needed_size'] == 23040 and row['capacity'] == 12288 and row['raw_len'] == row['len_before'] and
             row['eos'] == row['advance_on_error'] == 0 for row in events),
         'three actual nonterminal public zero-consumption sizing errors, one in each fragmented schedule')
    need(measured['current_resize_qualified'] and measured['current_playback_matches'] and
         measured['current_resize_exercised'] and not measured['honor_cases'] and not measured['decoder_errors'] and
         not measured['nonzero_resize_consumption_observed'] and not measured['empty_input_retry_exercised'] and
         measured['retained_after_unregister_bytes'] == 100 and measured['heap_min'] == 220180 and
         measured['reference']['pcm_bytes'] == 2119680 and measured['reference']['pcm_sha256'] == PCM_SHA,
         'all current-policy fragmented streams preserve complete raw PCM and honest observation limits')
    need([row['chunk'] for row in measured['current_cases']] == [4096, 257, 1] and
         all(row['complete'] == row['match'] == 1 and row['fed'] == row['input'] == 707097 and
             row['pcm'] == 2119680 and row['sha256'] == PCM_SHA and row['frames'] == 92 and row['resizes'] == 1 and
             row['error_consumed'] == row['empty_retries'] == 0 and row['final_capacity'] == 23040 and
             row['before'] == row['after'] == 282920 for row in measured['current_cases']),
         'full source consumption, exact raw identity and cleanup in all split schedules')
    header_pins = {'decoder_pending_input.h': 'b2909f70834598599c479315ff110064d81ca4308c116715408134fddc81ddbb',
                   'decoder_eof_input.h': '22d8b3dbc62bc859eab3a8ac5fd233caf95f7ff02e2ad8d324411d8ca5698019'}
    for name, expected in header_pins.items():
        need(sha(take(prefix + 'project/main/' + name)) == expected and
             ('"' + name + '"').encode() in take(prefix + 'project/main/main.c'),
             'exact production input helper source is included by the real compiled diagnostic')
    selected_objects = manifest['selected_object_files']
    need(len(selected_objects) >= 2 and {'main.c', 'decoder_registration.c'} <=
         {PurePosixPath(row['source'].replace('\\', '/')).name for row in selected_objects},
         'actual compiler-selected application objects are retained')
    for row in selected_objects:
        need(sha(take(prefix + row['path'])) == row['sha256'], 'selected object byte identity')
        actual = [entry for entry in commands if entry['file'] == row['source']]
        need(len(actual) == 1 and row['path'] == 'build/' + actual[0]['output'].replace('\\', '/'),
             'selected object path binds to actual compiler command')
    interpretation = data(prefix + 'interpretation.json')
    need(interpretation['source_report_sha256'] == sha(take(prefix + 'report.json')) ==
         manifest['original_report_sha256'] == 'd3803931ea2367f964bc2c08a70e250e6b3f9d094a2b2f9e4dafbcb0f3b6953e' and
         interpretation['canonical_controller_sha256'] == READER_SHA and interpretation['observation_completed'] and
         interpretation['source_and_frozen_bytes_unchanged'] and interpretation['build_artifact_bytes_unchanged'] and
         interpretation['all_native_commands_terminal_zero'] and interpretation['schedules'] == [4096, 257, 1] and
         interpretation['real_resize_events'] == 3 and interpretation['all_resize_events_nonterminal'] and
         interpretation['all_error_consumed_zero'] and interpretation['all_error_decoded_zero'] and
         interpretation['all_current_schedules_full_raw_match'] and interpretation['current_unchanged_retry_resize_exercised'] and
         interpretation['honor_strategy_instances_executed'] == 0 and interpretation['exact_production_input_headers'] and
         interpretation['complete_raw_pcm_bytes'] == 2119680 and interpretation['complete_raw_pcm_sha256'] == PCM_SHA and
         not interpretation['nonzero_consumption_on_error_exercised'] and not interpretation['empty_input_retry_exercised'] and
         not interpretation['production_audio_task_resize_qualified'] and not interpretation['allocation_failure_injected'] and
         not interpretation['standard_complete'] and interpretation['required_opus_playback_trim_unresolved'],
         'original explicit fragmented diagnostic interpretation and remaining gates')
    link = manifest['whole_input_checkpoint']
    original_manifest = (FOLDER / 'resize-manifest.json').read_bytes()
    need(sha(original_manifest) == link['manifest_sha256'] and
         original_manifest == take('reference/whole-input/resize-manifest.json'), 'separate whole-input checkpoint manifest binding')
    whole_manifest = json.loads(original_manifest)
    need(whole_manifest['archive']['sha256'] == link['archive_sha256'] and
         sha((FOLDER / 'resize-captures.zip').read_bytes()) == link['archive_sha256'], 'exact separate whole-input archive identity')
    whole_row = next(row for row in whole_manifest['files'] if row['path'] == 'captures/resize01/report.json')
    with zipfile.ZipFile(FOLDER / 'resize-captures.zip') as archive:
        original_whole_report = archive.read(whole_row['blob'])
    need(sha(original_whole_report) == whole_row['sha256'] == interpretation['whole_input_reference_report_sha256'] and
         json.loads(original_whole_report)['measurements']['reference'] == measured['reference'],
         'complete raw reference agrees with the prior whole-input public decoder checkpoint')
    whole_verifier = canonical_module('tests/verify-cyd-opus-resize-checkpoint.py',
        'eddd1e52de1532daf28ce0c2c2a68ae5ea3c612e564185acdd9f577d645543c9', 'reviewed_whole_input_resize_verifier')
    need(whole_verifier.verify()['passed'], 'separate whole-input evidence is verified as data without native execution')
    encoded = take(prefix + 'project/main/fixture.ogg')
    need(sha(encoded) == FIXTURE_SHA and encoded == take('reference/fixture/stereo-510-120ms.ogg'), 'exact independent fixture')
    accounting = audit_reader.audit(encoded)
    need(accounting == manifest['fixture_accounting'] and accounting['audio_packet_count'] == 92 and
         accounting['raw_frames'] == 529920 and accounting['maximum_packet_pcm16_bytes'] == 23040 and
         accounting['preskip'] == 312 and accounting['tail_frames'] == 1608 and
         accounting['playback_pcm16_bytes'] == 2112000, 'independent fixture CRC/framing and unresolved playback timeline')
    need(manifest['fragmented_input_resize_qualified'] and not manifest['nonzero_consumption_on_error_exercised'] and
         not manifest['empty_input_retry_exercised'] and not manifest['honor_strategy_executed'] and
         not manifest['production_audio_task_resize_qualified'] and not manifest['output_allocation_failure_injected'] and
         manifest['required_opus_playback_trim_unresolved'] and not manifest['standard_complete'] and
         not manifest['omitted_binary_bytes_verified'], 'honest fragmented-checkpoint qualification boundaries')
    return dict(passed=True, logical_files=len(rows), physical_files=len(blobs), actual_nonterminal_resize_events=3,
                schedules=[4096,257,1], needed_size_bytes=23040, fragmented_input_resize_qualified=True,
                raw_pcm_bytes=2119680, nonzero_consumption_on_error_exercised=False, empty_input_retry_exercised=False,
                honor_strategy_executed=False, production_audio_task_resize_qualified=False,
                output_allocation_failure_injected=False, required_opus_playback_trim_unresolved=True,
                omitted_compiled_images=len(omitted), omitted_binary_bytes_verified=False,
                native_commands_repeated=False, archived_program_executed=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
