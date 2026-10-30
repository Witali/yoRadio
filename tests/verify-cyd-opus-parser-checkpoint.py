"""Verify saved public parser-observation evidence; no native program is run."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-opus-20261030'
READER_SHA = 'fb51458e6307955d03ea2083af48a050bbf6f8a6d241604b5dc6cbe8f87fad88'
MAIN_SHA = 'b26bb63b981f3ff6a6b7543959f9684130977d47e38ee4f22075742d252669aa'
SHORT_AUDIT_SHA = '50bb1a2b372629dbe720ba612cbbbcf90977598258278c741192ec0d4ded815c'
LONG_AUDIT_SHA = 'b31791eb3ba1a4f7159db4cfb06358b7cf52e512417e40993f9bc1ca70fc76d6'
WINDOW_SHA = dict(F20='b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f',
                  F120='4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def canonical_module(relative, digest, name):
    path = ROOT / relative
    need(sha(path.read_bytes()) == digest, 'pinned reviewed canonical data-only reader: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parser_records(log):
    """Re-read every successful callback field from the original transcript."""
    records = {'F20observed': [], 'F120observed': []}
    names = ('seq', 'len', 'bos', 'eos', 'result', 'sample_num', 'duration', 'padding_start_size',
             'padding_end_pos', 'frame_size', 'skipped_size', 'total_size', 'extra_present', 'dec_type',
             'extra_is_opus', 'opus_rate', 'opus_channels', 'opus_frame_duration', 'opus_self_delimited')
    pattern = (r'EOPP_PARSE case=(F20observed|F120observed) seq=(\d+) len=(\d+) bos=([01]) eos=([01]) result=(0) '
               r'sample_num=(-?\d+) duration=(-?\d+) padding_start_size=(\d+) padding_end_pos=(\d+) frame_size=(\d+) skipped_size=(\d+) total_size=(\d+) '
               r'extra_present=([01]) dec_type=(\d+) extra_is_opus=([01]) opus_rate=(\d+) opus_channels=(\d+) opus_frame_duration=(-?\d+) opus_self_delimited=([01])')
    for line in log.replace('\r\n', '\n').splitlines():
        if not line.startswith('EOPP_PARSE'):
            continue
        match = re.fullmatch(pattern, line)
        need(match, 'complete exact public parser callback record')
        case, *values = match.groups()
        records[case].append(dict(zip(names, map(int, values))))
    return records


def verify():
    manifest = json.loads((FOLDER / 'parser-manifest.json').read_bytes())
    archive_path = FOLDER / manifest['archive']['path']
    need(archive_path.parent == FOLDER and archive_path.name == 'parser-captures.zip' and
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
             'canonical logical path without image payloads')
        body = physical[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'every published logical byte')
        files[row['path']] = body

    def take(name):
        need(name in files, 'required saved byte payload: ' + name)
        return files[name]

    def data(name):
        return json.loads(take(name))

    omitted = {row['path']: row for row in manifest['compiled_images_omitted']}
    excluded = {row['path']: row for row in manifest['other_bytes_omitted']}
    need(omitted and len(omitted) == len(manifest['compiled_images_omitted']) and
         all(name not in files and PurePosixPath(name).suffix.lower() in ('.bin', '.elf') and
             row['bytes'] > 0 and re.fullmatch('[a-f0-9]{64}', row['sha256']) and
             row['original_retained_locally'] and row['byte_payload_published'] is False for name, row in omitted.items()),
         'explicit local-only image hashes; omitted bytes are not verified')
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False
             for name, row in excluded.items()), 'explicit whole-payload publication omissions')
    need(take('verification/verifier.py') == Path(__file__).read_bytes() and
         manifest['verifier_sha256'] == sha(Path(__file__).read_bytes()) and
         sha(take('verification/reader.py')) == READER_SHA == manifest['controller_sha256'],
         'exact reviewed reader and standalone verifier identities')
    reader = canonical_module('tests/run-cyd-espressif-opus-parser-qemu.py', READER_SHA, 'reviewed_parser_observation_reader')
    short_auditor = canonical_module('tests/verify-cyd-opus-direct-checkpoint.py', SHORT_AUDIT_SHA, 'reviewed_short_fixture_auditor')
    long_auditor = canonical_module('tests/fixtures/opus_ogg_long_packets/generate.py', LONG_AUDIT_SHA, 'reviewed_long_fixture_auditor')
    direct_manifest_bytes = (FOLDER / 'direct-manifest.json').read_bytes()
    link = manifest['linked_direct_checkpoint']
    need(take('reference/direct-manifest.json') == direct_manifest_bytes and
         sha(direct_manifest_bytes) == link['manifest_sha256'] and
         json.loads(direct_manifest_bytes)['archive']['sha256'] == link['archive_sha256'] and
         json.loads(direct_manifest_bytes)['fixture_accounting'] == manifest['fixture_audits']['short'],
         'same independently audited short-fixture checkpoint identity')
    short_manifest = data('reference/short-fixture-manifest.json')
    need(any(row['codec'] == 'opus' and row['bytes'] == 706319 and row['sha256'] == reader.FIXTURE_SHA
             for row in short_manifest['fixtures']), 'linked original recovered short-fixture identity')
    long_manifest = data('reference/long-fixture/manifest.json')
    long_generation = take('reference/long-fixture/evidence/generation-report.json')
    need(long_manifest['fixture']['sha256'] == reader.LONG_SHA and long_manifest['generator_sha256'] == LONG_AUDIT_SHA and
         sha(take('reference/long-fixture/generate.py')) == LONG_AUDIT_SHA and
         sha(long_generation) == long_manifest['generation_report_sha256'] and
         json.loads(long_generation)['audit'] == manifest['fixture_audits']['long'],
         'linked independent long-fixture generation and timeline audit')
    reports = {}
    for number in ('01', '02'):
        prefix = 'captures/parser' + number + '/'
        report = data(prefix + 'report.json')
        reports[number] = report
        need(report['target'] == 'esp32' and report['fixture_sha256'] == reader.FIXTURE_SHA and
             report['fixture_bytes'] == 706319 and report['vendor_revision'] == reader.REVISION and
             report['sdk_revision'] == reader.SDK_HEAD['esp32'] and report['output_capacity'] == 24576 and
             not report['production_firmware'] and not report['physical_device'] and not report['private_abi_used'] and
             not report['custom_decoder'] and not report['full_conformance_qualified'], 'bounded unchanged public diagnostic scope')
        expected = ['vendor-head', 'vendor-clean', 'sdk-head', 'sdk-clean', 'build']
        if number == '02':
            expected += ['symbols', 'merge', 'qemu']
        need([row['name'] for row in report['commands']] == expected, 'complete unique native command inventory')
        for row in report['commands']:
            status = 1 if number == '01' and row['name'] == 'build' else 0
            need(row['state'] == 'complete' and row['pid'] > 0 and row['exit_status'] == status,
                 'actual original native child terminal status')
            for stream in ('stdout', 'stderr'):
                need(sha(take(prefix + row['name'] + '.' + stream + '.log')) == row[stream + '_sha256'],
                     'every original native command log byte')
        child = json.loads(take(prefix + 'sdk-child.json').decode('utf-8-sig'))
        need(child['pid'] > 0 and child['exit_status'] == (2 if number == '01' else 0), 'actual SDK child terminal status')
        for name, expected_head in (('sdk', reader.SDK_HEAD['esp32']), ('vendor', reader.REVISION)):
            need(take(prefix + name + '-head.stdout.log').decode('utf-8').strip() == expected_head and
                 not take(prefix + name + '-clean.stdout.log').strip(), 'actual clean pinned repository: ' + name)
        snapshots = {pin['snapshot'] for pin in report['inputs'].values()}
        need({'sources/controller.py', 'project/main/main.c', 'project/main/CMakeLists.txt', 'project/CMakeLists.txt',
              'project/sdk-build.ps1', 'project/main/fixture20.ogg', 'project/main/fixture120.ogg',
              'project/main/decoder_registration.c', 'project/main/decoder_registration.h',
              'sources/fixture-auditors/short.py', 'sources/fixture-auditors/long.py',
              'sources/vendor/esp_audio_codec/lib/esp32/libesp_audio_codec.a',
              'sources/vendor/esp_audio_codec/lib/esp32/libesp_audio_simple_dec.a'} <= snapshots,
             'required complete harness, fixtures, public registration, auditors and vendor archive bindings')
        for pin in report['inputs'].values():
            name = prefix + pin['snapshot']
            if name in excluded:
                need(excluded[name]['sha256'] == pin['sha256'] and excluded[name]['bytes'] == pin['bytes'], 'omitted source hash binding')
            else:
                body = take(name)
                need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'every frozen published source byte')
        need(sha(take(prefix + 'sources/controller.py')) == READER_SHA and
             sha(take(prefix + 'sources/fixture-auditors/short.py')) == SHORT_AUDIT_SHA and
             sha(take(prefix + 'sources/fixture-auditors/long.py')) == LONG_AUDIT_SHA, 'exact executed controller and linked fixture auditors')
        encoded_short = take(prefix + 'project/main/fixture20.ogg')
        encoded_long = take(prefix + 'project/main/fixture120.ogg')
        need(sha(encoded_short) == reader.FIXTURE_SHA and sha(encoded_long) == reader.LONG_SHA,
             'both complete unchanged encoded fixtures')
        audits = dict(short=short_auditor.fixture_accounting(encoded_short), long=long_auditor.audit(encoded_long))
        need(audits == report['fixture_audits'] == manifest['fixture_audits'], 'independent CRC, packet and granule timeline recount')
        header = (b'#pragma once\n#define SHORT_WINDOW_BEGIN UINT64_C(312)\n#define SHORT_WINDOW_END UINT64_C(528312)\n'
                  b'#define LONG_WINDOW_BEGIN UINT64_C(312)\n#define LONG_WINDOW_END UINT64_C(528312)\n')
        actual_header = take(prefix + 'project/main/window_ranges.h')
        need(actual_header.replace(b'\r\n', b'\n') == header and sha(actual_header) == report['generated_header_sha256'],
             'derived read-only emission-position window constants')
        for name, digest in zip(('libesp_audio_codec.a', 'libesp_audio_simple_dec.a'), reader.ARCHIVES['esp32']):
            need(sha(take(prefix + 'sources/vendor/esp_audio_codec/lib/esp32/' + name)) == digest, 'unchanged exact LX6 vendor archive')
        if number == '01':
            need(not report['passed'] and not report['completed'] and not report['target_executed'] and
                 report['failure_type'] == 'ValueError' and report['failure'] == 'command terminal0: build' and
                 not report.get('build_outputs') and prefix + 'qemu.stdout.log' not in files and
                 b'fatal error: esp_ogg_dec.h: No such file or directory' in take(prefix + 'sdk-build.stdout.log'),
                 'original missing-public-include build failure preserved before QEMU')
            continue
        need(report['passed'] and report['completed'] and report['target_executed'] and report['all_bound_inputs_current'] and
             report['public_parser_callback_only'] and not report['padding_units_assumed'] and
             not report['production_trim_implemented'], 'fresh successful public-observation campaign without trim claims')
        mandatory = {'build/cyd_espressif_opus_parser_qemu.elf', 'build/cyd_espressif_opus_parser_qemu.bin',
                     'build/cyd_espressif_opus_parser_qemu.map', 'qemu-flash.bin', 'sdkconfig', 'sdk-child.json',
                     'build/bootloader/bootloader.bin', 'build/partition_table/partition-table.bin',
                     'build/compile_commands.json', 'build/project_description.json', 'build/flasher_args.json'}
        need(mandatory <= set(report['build_outputs']), 'complete actual build artifact inventory')
        for name, digest in report['build_outputs'].items():
            logical = prefix + name
            if logical in omitted:
                need(omitted[logical]['sha256'] == digest, 'explicit omitted image hash binding')
            elif logical in excluded:
                need(excluded[logical]['sha256'] == digest, 'explicit omitted artifact hash binding')
            else:
                need(sha(take(logical)) == digest, 'every published build artifact byte')
        symbols = take(prefix + 'symbols.stdout.log').decode('utf-8').replace('\r\n', '\n')
        for name in ('decoder_register_codecs', 'esp_opus_dec_open', 'esp_opus_dec_decode', 'esp_audio_simple_dec_process',
                     'esp_ogg_parse_frame', 'observe_ogg', 'observe_free'):
            need(re.search(r'\b' + name + '$', symbols, re.M), 'actual linked public interface or application callback: ' + name)
        need(not re.search(r'\b(?:__wrap_(?:esp_vorbis_|esp_audio_|esp_ogg_|floor[01]_|media_lib_)|native_vorbis_)[A-Za-z0-9_]*$',
                           symbols, re.M), 'no private decoder wrappers or custom synthesis linked')
        config = data(prefix + 'build/config/sdkconfig.json')
        need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ'] == 1000, 'dual-core native scheduler configuration')
        for key in ('COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'HEAP_POISONING_LIGHT', 'FREERTOS_CHECK_STACKOVERFLOW_CANARY',
                    'ESP_TASK_WDT_EN', 'ESP_TASK_WDT_INIT', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0',
                    'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1', 'AUDIO_DECODER_OPUS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
            need(config[key] is True, 'actual native configuration: ' + key)
        build_argv = report['commands'][4]['argv']
        campaign_path = build_argv[build_argv.index('-Campaign') + 1].replace('\\', '/').rstrip('/')
        qemu_argv = report['commands'][-1]['argv']
        need(report['tools']['qemu']['sha256'] == reader.QEMU_SHA['esp32'] and
             qemu_argv[0].replace('\\', '/') == report['tools']['qemu']['path'].replace('\\', '/') and
             qemu_argv[qemu_argv.index('-drive') + 1].replace('\\', '/') ==
             'file=' + campaign_path + '/qemu-flash.bin,if=mtd,format=raw' and
             qemu_argv[qemu_argv.index('-smp') + 1] == '2' and qemu_argv[qemu_argv.index('-nic') + 1] == 'none' and
             '-snapshot' in qemu_argv and '-no-reboot' in qemu_argv, 'actual pinned QEMU uses the exact bound local-only image')
        compile_commands = data(prefix + 'build/compile_commands.json')
        for name in ('main.c', 'decoder_registration.c'):
            compiled = [row for row in compile_commands if row['file'].replace('\\', '/') == campaign_path + '/project/main/' + name]
            need(len(compiled) == 1 and '-include' not in compiled[0]['command'], 'complete compiled translation unit: ' + name)
        log = (take(prefix + 'qemu.stdout.log') + b'\n' + take(prefix + 'qemu.stderr.log')).decode('utf-8')
        measured = reader.validate_log(log)
        need(measured == report['measurements'] == manifest['measurements'], 'original paired cases and public-field summaries recounted')
        observed = parser_records(log)
        need(observed == data('observations/successful-parser-records.json') and
             sum(map(len, observed.values())) == measured['successful_parser_records'] == 682,
             'all 682 exact original successful callback records retained')
        for name, count in (('F20observed', 574), ('F120observed', 108)):
            case = measured['cases'][name]
            records = observed[name]
            need(case['parse_calls'] == case['successful_parses'] == len(records) == count and
                 case['free_calls'] == 1 and [row['seq'] for row in records] == list(range(1, count + 1)),
                 'every successful callback in native order and exactly one delegated free per observed instance')
            need(all(row['result'] == 0 and row['sample_num'] == row['duration'] == row['padding_start_size'] ==
                     row['padding_end_pos'] == row['total_size'] == 0 for row in records), 'observed public timeline fields all zero')
            opus = [row for row in records if row['extra_is_opus']]
            need(opus and all(row['extra_present'] == 1 and row['opus_rate'] == 48000 and row['opus_channels'] == 2 and
                             row['opus_frame_duration'] == row['opus_self_delimited'] == 0 for row in opus),
                 'typed public Opus configuration values observed without duration/unit inference')
        for stem, pcm, raw_sha in (('F20', 2115840, 'a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b'),
                                   ('F120', 2119680, '670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684')):
            for suffix in ('plain', 'observed'):
                row = measured['cases'][stem + suffix]
                need(row['pcm'] == pcm and row['sha256'] == raw_sha and row['window_begin'] == 312 and
                     row['window_end'] == 528312 and row['window_bytes'] == 2112000 and
                     row['window_sha256'] == WINDOW_SHA[stem], 'complete unchanged raw PCM and same-vendor emission-position reference')
    first, second = reports['01']['inputs'], reports['02']['inputs']
    need(set(first) == set(second), 'same original source inventory between attempts')
    changed = [pin['snapshot'] for original, pin in first.items() if pin != second[original]]
    need(changed == ['project/main/main.c'], 'only the public include-path source correction changed')
    old = take('captures/parser01/project/main/main.c')
    corrected = old.replace(b'#include "esp_ogg_dec.h"', b'#include "impl/esp_ogg_dec.h"').replace(
        b'#include "esp_ogg_parse.h"', b'#include "impl/esp_ogg_parse.h"')
    need(old != corrected == take('captures/parser02/project/main/main.c') and sha(corrected) == MAIN_SHA,
         'exact two public impl/ include-path corrections, no other native harness change')
    post = data('observations/post-run-binding.json')
    need(post['passed'] and post['source_bindings'] == 72 and post['build_artifact_bindings'] == 11 and
         post['tool_bindings'] == 5 and not post['native_process_started'] and not post['files_modified'] and
         post['original_report_sha256'] == sha(take('captures/parser02/report.json')) and
         post['controller_sha256'] == READER_SHA and post['harness_main_sha256'] == MAIN_SHA,
         'original independent data-only post-run binding audit')
    need(manifest['raw_vendor_pairs_equal'] and manifest['original_compile_failure_preserved'] and
         manifest['public_parser_callback_only'] and not manifest['padding_units_assumed'] and
         not manifest['production_trim_implemented'] and manifest['fixture_window_reference_only'] and
         not manifest['independent_alignment_proof'] and manifest['required_opus_playback_trim_unresolved'] and
         not manifest['standard_complete'] and not manifest['omitted_binary_bytes_verified'], 'explicit honest qualification limits')
    return dict(passed=True, logical_files=len(rows), physical_files=len(blobs), stock_observed_pairs=2,
                successful_parser_records=682, delegated_free_per_observed_instance=1,
                timeline_fields_all_zero=True, fixture_window_bytes_each=2112000,
                fixture_window_reference_only=True, independent_alignment_proof=False,
                padding_units_assumed=False, production_trim_implemented=False,
                original_compile_failure_preserved=True, omitted_compiled_images=len(omitted),
                omitted_binary_bytes_verified=False, native_commands_repeated=False, archived_program_executed=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
