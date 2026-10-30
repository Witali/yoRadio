"""Verify saved whole-task Vorbis evidence without builds, decoder or QEMU runs."""
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'tests/results/cyd-vorbis-task-20261030'
READER_SHA = '633043d1cb61a27009f655c48f42deec198b33c556a8a73712f401aa0490bf6c'
PCM_SHA = 'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    manifest = json.loads((FOLDER / 'native-manifest.json').read_bytes())
    archive_path = FOLDER / manifest['archive']['path']
    need(archive_path.name == 'native-captures.zip' and archive_path.parent == FOLDER and
         archive_path.stat().st_size == manifest['archive']['bytes'] and sha(archive_path.read_bytes()) == manifest['archive']['sha256'],
         'complete saved archive identity')
    rows = manifest['files']
    need(len({row['path'] for row in rows}) == len(rows) == manifest['logical_files'], 'unique complete logical inventory')
    blobs = {row['blob'] for row in rows}
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.infolist()) == len(blobs) == manifest['physical_files'] and set(archive.namelist()) == blobs,
             'exact deduplicated physical archive members')
        physical = {}
        for name in blobs:
            need(re.fullmatch(r'blobs/[0-9a-f]{64}', name), 'canonical physical blob')
            body = archive.read(name)
            need(name == 'blobs/' + sha(body), 'every physical byte')
            physical[name] = body
    files = {}
    for row in rows:
        path = PurePosixPath(row['path'])
        need(path.as_posix() == row['path'] and not path.is_absolute() and '..' not in path.parts and
             '\\' not in row['path'] and ':' not in row['path'], 'canonical logical archive path')
        body = physical[row['blob']]
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'every saved logical byte')
        files[row['path']] = body

    def take(name):
        need(name in files, 'required saved input: ' + name)
        return files[name]

    def data(name): return json.loads(take(name))

    privacy = data('inventory/privacy-views.json')
    withheld = {row['path']: row for row in manifest['installed_header_bytes_omitted']}
    need(len(withheld) == 94 and len({row['sha256'] for row in withheld.values()}) == 47 and
         privacy['installed_header_bytes_omitted'] == manifest['installed_header_bytes_omitted'],
         'explicit installed-header omissions; dependency hashes remain while contact-containing bytes stay local')
    need(all(name not in files and '/sources/compiler-dependencies/' in name for name in withheld),
         'omitted external header bytes are not published')
    omitted_images = {row['path']: row for row in manifest['compiled_images_omitted']}
    need(len(omitted_images) == 6 and privacy['compiled_images_omitted'] == manifest['compiled_images_omitted'] and
         set(omitted_images) == {'captures/task'+number+'/'+name for number in ('01','02') for name in
             ('build/cyd_espressif_vorbis_task_qemu.elf','build/cyd_espressif_vorbis_task_qemu.bin','qemu-flash.bin')} and
         all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False and
             re.fullmatch(r'[0-9a-f]{64}', row['sha256'])
             for name,row in omitted_images.items()),
         'flagged ELF/app/flash bytes stay local; published evidence retains exact original hashes only')
    removed_previous=manifest['previous_evidence_payloads_omitted']
    need(privacy['previous_evidence_payloads_omitted']==removed_previous and len(removed_previous)==4 and
         {row['historical_path'] for row in removed_previous} ==
             {'privacy-proof/pk_internal.h','privacy-proof/pkparse.c','inventory/pem-parser-markers.json','verification/verifier.py'} and
         all(row['original_sha256'] not in {pin['sha256'] for pin in rows} and row['original_retained_locally'] and
             row['byte_payload_published'] is False for row in removed_previous),
         'superseded flagged/proof payloads are absent from every published physical blob')
    need(privacy['metadata_views'] == manifest['metadata_privacy_views'] and len(privacy['metadata_views']) == 2 and
         privacy['original_reports_unchanged'] and privacy['original_elf_app_images_retained_locally'], 'explicit metadata privacy views and local image retention')
    for view in privacy['metadata_views']:
        need(view['path'] in ('captures/task01/execution-bundle.json', 'captures/task02/execution-bundle.json') and
             view['kind'] == 'runtime-identifier-key-redaction' and view['occurrences'] == 1 and
             view['replacement'] == 'runtime-path-redacted:pwsh.exe' and view['all_other_bytes_unchanged'] and
             view['runtime_digest_preserved'] and view['original_retained_locally'] and
             sha(take(view['path'])) == view['published_sha256'] and
             re.fullmatch(r'[0-9a-f]{64}', view['original_sha256']), 'original/published metadata hash provenance')
        runtime = data(view['path'])['runtime']
        need('runtime-path-redacted:pwsh.exe' in runtime and
             re.fullmatch(r'[0-9a-f]{64}',runtime['runtime-path-redacted:pwsh.exe']),
             'exact safe alias retains the installed runtime digest')

    def artifact_hash(name, digest):
        if name in omitted_images:
            need(omitted_images[name]['sha256'] == digest, 'explicit omitted-image hash provenance; no omitted bytes are read')
        else:
            need(sha(take(name)) == digest, 'published artifact byte binding')

    reader_path = ROOT / 'tests/run-cyd-espressif-vorbis-task-qemu.py'
    reader_bytes = reader_path.read_bytes()
    need(sha(reader_bytes) == READER_SHA == manifest['controller_sha256'] and
         reader_bytes == take('verification/reader.py'), 'reviewed canonical controller; no artifact code execution')
    need(Path(__file__).read_bytes() == take('verification/verifier.py'), 'saved standalone verifier identity')
    spec = importlib.util.spec_from_file_location('reviewed_whole_task_reader', reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    results = {}
    for number in ('01', '02'):
        prefix = 'captures/task' + number + '/'
        report = data(prefix + 'report.json')
        bundle = data(prefix + 'execution-bundle.json')
        need(bundle['sources'] == data(prefix + 'source-manifest.json'), 'whole source manifest bound to executed image')
        need(report['all_bound_inputs_current'] is True and not report['bound_input_failures'],
             'original campaign immutability check retained without rewriting historical input state')
        for original, pin in bundle['sources'].items():
            name = prefix + pin['snapshot']
            if name in withheld:
                excluded = withheld[name]
                need(excluded['sha256'] == pin['sha256'] and excluded['bytes'] == pin['bytes'] and
                     excluded['original_path'] == original and '/.idf/' in original.replace('\\', '/') and
                     excluded['sdk_commit'] == reader.SDK_COMMIT, 'omitted installed header retains exact original dependency/source identity')
            else:
                body = take(name)
                need(sha(body) == pin['sha256'] and len(body) == pin['bytes'], 'every published frozen source/dependency binding')
        for name, digest in bundle['artifacts'].items():
            artifact_hash(prefix + name, digest)
        for command in report['commands']:
            need(command['state'] == 'complete' and command['exit_status'] == 0, 'actual child terminal status')
            for stream in ('stdout', 'stderr'):
                need(sha(take(prefix + command['name'] + '.' + stream + '.log')) == command[stream + '_sha256'],
                     'every original command output binding')
        child = json.loads(take(prefix + 'sdk-child.json').decode('utf-8-sig'))
        need(child['pid'] > 0 and child['exit_status'] == 0, 'actual compiler-driver child status')
        closure = data(prefix + 'actual-compiler-closure.json')
        need(len(closure['translation_units']) == report['actual_translation_units'] and
             len(closure['dependencies']) == report['actual_compiler_dependencies'], 'complete actual GCC/Ninja dependency census')
        for pin in closure['dependencies'].values():
            need(pin['manifest_original'] in bundle['sources'] and
                 pin['sha256'] == bundle['sources'][pin['manifest_original']]['sha256'], 'actual dependency bound to saved bytes')
        tu_names = {Path(row['file']).name for row in closure['translation_units']}
        need({'audio_service.c', 'native_state.c', 'native_health.c', 'decoder_registration.c', 'main.cpp',
              'adaptive_input.c', 'native_network_power.c'} <= tu_names, 'complete production and actual queue/power task inputs')
        config = data(prefix + 'build/config/sdkconfig.json')
        need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ'] == 1000 and
             not config.get('YORADIO_HTTP_REQUEST_BUFFER_RELEASE', False) and not config.get('YORADIO_FLAC_DECODER_CUSTOM', False),
             'original dual-core scheduling and explicit synthetic-transport profile')
        for key in ('COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE', 'HEAP_POISONING_LIGHT',
                    'FREERTOS_CHECK_STACKOVERFLOW_CANARY', 'ESP_TASK_WDT_EN', 'ESP_TASK_WDT_INIT',
                    'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0', 'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1',
                    'AUDIO_DECODER_VORBIS_SUPPORT', 'AUDIO_SIMPLE_DEC_OGG_SUPPORT'):
            need(config.get(key) is True, 'actual native configuration: ' + key)
        reference = data(prefix + 'sources/reference/native-manifest.json')
        need(sha(take(prefix + 'sources/reference/native-manifest.json')) == reader.REFERENCE_MANIFEST_SHA and
             bundle['pcm_reference']['sha256'] == PCM_SHA and bundle['pcm_reference']['bytes'] == 2112000 and
             bundle['pcm_reference']['checkpoint_archive_sha256'] == reader.REFERENCE_ARCHIVE_SHA and
             not bundle['pcm_reference']['independent_numeric_oracle'], 'retained direct-vendor integration reference identity')
        ref_rows = {row['path']: row for row in reference['files']}
        for target in ('esp32', 'esp32c3'):
            source_prefix = 'captures/espressif-vorbis-' + target + '-20261030-04/'
            for name in ('qemu.stdout.log', 'qemu.stderr.log', 'report.json'):
                need(sha(take(prefix + 'sources/reference/' + target + '/' + name)) == ref_rows[source_prefix + name]['sha256'],
                     'selected original native reference records; ancestor archive is not duplicated')
        log = (take(prefix + 'qemu.stdout.log') + b'\n' + take(prefix + 'qemu.stderr.log')).decode('utf-8')
        if number == '01':
            need(not report['passed'] and not report['completed'] and 'CYD_VORBIS_TASK_FAILURE all_pcm_precedes_eof' in log,
                 'original EOF semantic failure remains nonpassing despite emulator exit zero')
            try: reader.validate_log(log)
            except ValueError: pass
            else: raise ValueError('original failing transcript accepted')
        else:
            measured = reader.validate_log(log)
            need(report['passed'] and report['completed'] and measured == report['measurements'] == manifest['measurements'],
                 'all successful native lifecycle records and exact PCM identity')
            need(sha(take(prefix + 'sources/controller.py')) == READER_SHA, 'passing native image uses reviewed controller')
            results = measured

    probe_prefix = 'diagnostics/eof-probe01/'
    probe = data(probe_prefix + 'report.json')
    need(not probe['qualified'] and probe['gdb_exit_status'] == 0 and probe['qemu_terminal_status'] == 1 and
         probe['bound_files_unchanged'] and b'OBSERVED_PUBLIC_EOF\n$1 = 2110464' in take(probe_prefix + 'gdb.log').replace(b'\r\n', b'\n'),
         'read-only initial public output probe stays diagnostic')
    bootstrap = data('diagnostics/public-trace01/report.json')
    need(not bootstrap['completed'] and not bootstrap['qualified'] and not bootstrap['native_child_started'] and
         sha(take('diagnostics/public-trace01/bootstrap-source.py')) == bootstrap['launcher_sha256'],
         'bootstrap path typo preserved before native execution')
    old = data('diagnostics/public-trace02/report.json')
    need(not old['completed'] and not old['qualified'] and old['failure_type'] == 'AssertionError' and
         old['gdb_exit_status'] == 0 and old['qemu_terminal_status'] == 1 and old['bound_files_unchanged'],
         'uncounted duplicate debugger hits remain an explicitly failed diagnostic reader')
    trace_prefix = 'diagnostics/public-trace03/'
    trace = data(trace_prefix + 'report.json')
    need(trace['completed'] and not trace['qualified'] and trace['gdb_exit_status'] == 0 and
         trace['qemu_terminal_status'] == 1 and trace['bound_files_unchanged'] and not trace['arguments_mutated'] and
         not trace['source_or_image_modified'] and not trace['private_vendor_state_read'], 'public trace scope and terminal debugger ownership')
    for diagnostic_prefix, diagnostic in ((probe_prefix, probe), ('diagnostics/public-trace02/', old), (trace_prefix, trace)):
        for original, digest in diagnostic['runtime'].items():
            normalized = original.replace('\\', '/')
            if '/cyd-espressif-vorbis-task-20261030-01/' in normalized:
                tail = normalized.split('/cyd-espressif-vorbis-task-20261030-01/', 1)[1]
                artifact_hash('captures/task01/' + tail,digest)
            elif normalized.endswith('/trace-cyd-vorbis-task-public.py'):
                need(sha(take(diagnostic_prefix + 'launcher.py')) == digest, 'exact historical diagnostic launcher source binding')
            elif normalized.endswith('/qemu-system-xtensa.exe'):
                need(digest == reader.QEMU_SHA, 'pinned diagnostic QEMU identity')
            elif normalized.endswith('/xtensa-esp32-elf-gdb.exe'):
                need(digest == 'a17ad420b9c7197c2832a81439428c78779bc384738b68f656467de3382f58a1', 'pinned installed GDB identity')
        for name, digest in diagnostic.get('output_sha256', {}).items():
            need(sha(take(diagnostic_prefix + name)) == digest, 'saved diagnostic command/log/source bytes')
    log = take(trace_prefix + 'gdb.log').decode('utf-8').replace('\r\n', '\n')
    fields = ('seq', 'len', 'eos', 'consumed', 'pcm', 'result')
    raw = [dict(zip(fields, map(int, row))) for row in re.findall(
        r'^PUBLIC_CALL seq=(\d+) len=(\d+) eos=(\d+) consumed=(\d+) pcm=(\d+) result=(-?\d+)$', log, re.M)]
    hits, order = {}, []
    for index, row in enumerate(raw, 1):
        if row['seq'] not in hits: hits[row['seq']] = []; order.append(row['seq'])
        need(not hits[row['seq']] or hits[row['seq']][0]['record'] == row, 'only identical records may share a native call counter')
        hits[row['seq']].append(dict(debugger_hit=index, record=row))
    need(order == list(range(1, 539)), 'every native call observed in order without gaps')
    calls = [hits[index][0]['record'] for index in order]
    repeats = [dict(native_counter=index, hits=hits[index]) for index in order if len(hits[index]) > 1]
    audit = data(trace_prefix + 'duplicate-audit.json')
    need(len(raw) == 540 and [row['native_counter'] for row in repeats] == [101, 110] and
         repeats == audit['identical_repeats'] and not audit['missing_native_counters'] and not audit['differing_repeat_records'],
         'reproducible exact debugger duplicate audit')
    need(sha(take(trace_prefix + 'gdb.log')) == audit['gdb_sha256'] and calls == data(trace_prefix + 'calls.json'), 'saved unique public trace binding')
    need(sum(row['consumed'] for row in calls) == 703584 and sum(row['pcm'] for row in calls) == 2110464 and
         all(row['result'] == 0 and row['consumed'] <= row['len'] for row in calls), 'no dropped encoded/PCM bytes at public decoder boundary')
    need(calls[-1] == dict(seq=538, len=0, eos=1, consumed=0, pcm=0, result=0) and
         calls[-2] == dict(seq=537, len=862, eos=0, consumed=862, pcm=512, result=0), 'separate empty EOF loses tail in original image')
    need(trace['public_trace']['input_consumed'] == 703584 and trace['public_trace']['decoded_pcm'] == 2110464 and
         trace['public_trace']['output_pcm'] == 2110464 and trace['public_trace']['transport_position'] == 703584,
         'original trace report agrees with independently recounted public calls')
    return dict(passed=True, physical_files=len(blobs), logical_files=len(rows), cases=list(results['cases']),
                actual_native_runs_repeated=False, artifact_code_executed=False, original_failure_preserved=True,
                public_trace_calls=538, encoded_consumed=703584, original_decoded_pcm=2110464,
                successful_pcm_bytes=2112000, full_pcm_independent_oracle=False,
                omitted_installed_header_files=len(withheld), explicit_metadata_privacy_views=2,
                omitted_compiled_image_files=len(omitted_images), omitted_binary_bytes_verified=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
