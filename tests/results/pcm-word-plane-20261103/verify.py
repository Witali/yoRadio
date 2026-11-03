"""Authenticate recorded word-plane evidence as data; never execute captures."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
DENIED_SUFFIXES = {'.a', '.bin', '.elf', '.exe', '.o', '.obj', '.pcm', '.pyc', '.zip'}
CURRENT_SOURCES = {
    'idf/components/native_stream/include/pcm_word_plane.h',
    'tests/native/pcm_word_plane_host.c',
    'tests/native/pcm_word_plane_xtensa_probe.c',
    'tests/run-pcm-word-plane-host.py',
    'tests/check-pcm-word-plane-xtensa.py',
    'tests/fixtures/pcm_word_plane/inspect_xtensa.py',
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def contained(name):
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and
         path.as_posix() == name and path.parts, 'contained canonical record path')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((FOLDER/'manifest.json').read_bytes())
    scope = manifest['scope']
    need(scope == dict(HOST_ASan_UBSan=True, Xtensa_compile_and_disassembly=True,
        Xtensa_object_execution=False, SDK_build=False, QEMU_execution=False,
        native_IRAM_allocation_qualified=False, full_application_fit_qualified=False,
        physical_hardware_qualified=False), 'bounded qualification scope')
    rows = manifest['files']
    need(len(rows) == len({row['path'] for row in rows}), 'unique retained records')
    data = {}
    origins = {}
    for row in rows:
        name = row['path']
        path = FOLDER/contained(name)
        need(path.resolve().is_relative_to(FOLDER) and not path.is_symlink(), 'local regular record')
        body = path.read_bytes()
        need(path.suffix.lower() not in DENIED_SUFFIXES and b'\0' not in body and
             not body.startswith((b'MZ', b'\x7fELF', b'!<arch>\n')), 'text-only published payload')
        body.decode('utf-8')
        need(len(body) == row['bytes'] and sha(body) == row['sha256'], 'exact retained bytes '+name)
        need(row['original_path'] not in origins, 'unique retained original locator')
        data[name] = body
        origins[row['original_path']] = row
    actual = {path.relative_to(FOLDER).as_posix() for path in FOLDER.rglob('*') if path.is_file()}
    need(actual == set(data) | {'README.md', 'manifest.json', 'verify.py'}, 'complete package census')
    omitted = {row['original_path']:row for row in manifest['omitted_local_files']}
    need(len(omitted) == len(manifest['omitted_local_files']) and not set(omitted) & set(origins),
         'unique complete omissions')
    need(all(row['original_retained_locally'] and row['byte_payload_published'] is False and
             row['bytes'] >= 0 and len(row['sha256']) == 64 for row in omitted.values()),
         'whole originals explicitly retained outside publication')

    def take(name):
        need(name in data, 'required retained record '+name)
        return data[name]

    def identity(original, digest, size=None):
        locator = original.replace('\\', '/')
        need(locator in origins or locator in omitted, 'original provenance is accounted for')
        row = origins.get(locator, omitted.get(locator))
        need(row['sha256'] == digest and (size is None or row['bytes'] == size),
             'exact original record identity')

    sources = manifest['canonical_sources']
    need({row['repository_path'] for row in sources} == CURRENT_SOURCES and len(sources) == 6,
         'all six current component sources')
    source_pins = {}
    for row in sources:
        name = row['repository_path']
        need(name in CURRENT_SOURCES, 'expected current source')
        body = take(row['payload'])
        need(sha(body) == row['sha256'] and len(body) == row['bytes'], 'canonical source binding')
        source_pins[name] = row['sha256']
        if args.require_current:
            path = ROOT/contained(name)
            need(path.resolve().is_relative_to(ROOT) and sha(path.read_bytes()) == row['sha256'],
                 'current source '+name)
    need(source_pins['idf/components/native_stream/include/pcm_word_plane.h'] ==
         '8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b', 'qualified helper revision')

    captures = {row['label']:row for row in manifest['captures']}
    need(set(captures) == {'host01', 'host02', 'xtensa01', 'xtensa02', 'xtensa03', 'xtensa-current'},
         'complete selected history and current evidence')
    reports = {}
    for label, capture in captures.items():
        report = json.loads(take(capture['report']))
        reports[label] = report
        need(('PASS' if report['passed'] else 'NONPASS') == capture['status'], 'original outcome retained')
        need(not report['SDK_started'] and not report['QEMU_started'], 'no SDK/QEMU in these captures')
        for row in report['sources']:
            identity(capture['original_root']+'/'+row['snapshot'], row['sha256'], row['bytes'])
        for command in report['commands']:
            need(command['state'] == 'complete' and command['pid'] > 0 and command['exit_status'] == 0 and
                 not command.get('timed_out'), 'actual terminal compiler/reader/HOST commands')
            for stream in ('stdout', 'stderr'):
                row = command[stream]
                identity(capture['original_root']+'/'+row['path'], row['sha256'], row['bytes'])
        if 'binary' in report:
            row = report['binary']
            identity(capture['original_root']+'/'+row['path'], row['sha256'], row['bytes'])
            need(capture['original_root']+'/'+row['path'] in omitted, 'HOST executable bytes omitted')
        for profile in report.get('probes', {}).values():
            row = profile['object']
            identity(capture['original_root']+'/'+row['path'], row['sha256'], row['bytes'])
            need(capture['original_root']+'/'+row['path'] in omitted, 'compiled object bytes omitted')

    host = reports['host02']
    need(host['passed'] and host['HOST_only'] and host['all_source_bindings_unchanged'] and
         not host['native_memory_access_qualified'], 'current HOST-only contract')
    measurements = dict(passed=True, groups=127, exhaustive_bit_patterns=65536,
        checked_samples=468228, immutable_DRAM=True, word_canaries=True,
        timer_dependency=False, native_memory_access_qualified=False)
    need(host['measurements'] == measurements and
         json.loads(take('captures/host02/test.stdout.log')) == measurements and
         not take('captures/host02/test.stderr.log'), 'all exact HOST checks and clean sanitizer output')
    commands = {row['name']:row for row in host['commands']}
    need('-fsanitize=address,undefined' in commands['build']['argv'] and
         'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1' in commands['test']['argv'] and
         'UBSAN_OPTIONS=halt_on_error=1' in commands['test']['argv'], 'actual ASan/UBSan invocation')
    for row in host['sources']:
        need(source_pins[row['path']] == row['sha256'], 'current HOST inputs bound to canonical bytes')

    current = reports['xtensa-current']
    need(current['passed'] and current['all_source_tool_bindings_unchanged'] and
         not current['linked'] and not current['object_executed'] and
         current['historical_reinspection_requested'] is False and
         'historical01_readonly_literal_reinspection' not in current and
         not any(row['name'].startswith('historical') for row in current['commands']),
         'current standalone check does not require old captures or execute objects')
    commands = {row['name']:row for row in current['commands']}
    for label in ('O2', 'O3'):
        need('-'+label in commands[label+'-compile']['argv'] and
             '-c' in commands[label+'-compile']['argv'] and
             '-fno-lto' in commands[label+'-compile']['argv'], 'actual standalone optimization profile')
        profile = current['probes'][label]
        need(profile['object']['bytes'] == 1728 and profile['object']['sha256'] ==
             '709320d78df7a5eff7f28b11befbb84ab49aea91ca61b1d76eba4859bdbde96a',
             'exact recorded current relocatable object identity')
        need(set(profile['inspection']) == {'pcm_word_probe_clear', 'pcm_word_probe_store', 'pcm_word_probe_load'},
             'every named actual helper probe')
        need(all(row['word_memory_operands'] and all(op in ('l32i','l32i.n','s32i','s32i.n')
             for op in row['word_memory_operands']) for row in profile['inspection'].values()),
             'recorded integer word accesses')
    controls = current['forbidden_width_controls']
    need([row['probe'] for row in controls] == ['forbidden_byte','forbidden_half','forbidden_float'] and
         all(row['rejected'] for row in controls) and
         all(mnemonic in row['reason'] for row,mnemonic in zip(controls,('l8ui','s16i','lsi'))),
         'three actual byte/halfword/FP-memory controls rejected')
    disassembly = take('captures/xtensa-current/forbidden-disassemble.stdout.log').decode()
    need(all(name in disassembly for name in ('forbidden_byte','forbidden_half','forbidden_float','l8ui','s16i','lsi')),
         'original negative-control instruction data retained')
    for row in current['sources']:
        matched = [name for name in CURRENT_SOURCES if row['path'].replace('\\','/').endswith('/'+name)]
        need(len(matched) == 1 and source_pins[matched[0]] == row['sha256'], 'current Xtensa source graph')

    need(not reports['xtensa01']['passed'] and
         reports['xtensa01']['error'] == 'ValueError: no narrow/FP/literal/unknown load: l32r',
         'original overstrict literal-inspector NONPASS remains NONPASS')
    need(not reports['xtensa02']['passed'] and
         reports['xtensa02']['error'] == 'AssertionError: Forbidden-width object was accepted: forbidden_float',
         'original optimized-to-safe-integer control NONPASS remains NONPASS')
    need(b'l32r' in take('captures/xtensa01/O2-disassemble.stdout.log') and
         b'forbidden_float' in take('captures/xtensa02/forbidden-disassemble.stdout.log') and
         b'l32i' in take('captures/xtensa02/forbidden-disassemble.stdout.log') and
         b'forbidden_float' in take('captures/xtensa02/sources/forbidden_width_probe.c'),
         'decisive unchanged historical instruction/control records retained')
    need(reports['host01']['passed'] and reports['xtensa03']['passed'], 'historical passing captures remain historical')
    need(next(row for row in reports['host01']['sources'] if row['path'].endswith('pcm_word_plane.h'))['sha256'] !=
         source_pins['idf/components/native_stream/include/pcm_word_plane.h'], 'old HOST helper is not current proof')
    need(reports['xtensa03']['historical01_readonly_literal_reinspection']['original_status'] == 'NONPASS',
         'later literal reinspection does not relabel original failure')

    attestation = json.loads(take('tools/original-payload-attestation.json'))
    tool_current = json.loads(take('tools/current-payload-currentness.json'))
    need(tool_current['actual_payload_hashes_current'] and not tool_current['compiler_reexecuted'] and
         tool_current['current_report_sha256'] == sha(take(captures['xtensa-current']['report'])) and
         tool_current['attestation_sha256'] == sha(take('tools/original-payload-attestation.json')) and
         attestation['report03_sha256'] == sha(take(captures['xtensa03']['report'])) and
         tool_current['installed_payload_identities'] == attestation['installed_payload_identities'] and
         len(attestation['installed_payload_identities']) == 4, 'actual installed driver/assembler/compiler payload receipts')
    for row in attestation['installed_payload_identities']:
        identity(row['path'], row['sha256'], row['bytes'])
        need(row['path'].replace('\\','/') in omitted, 'actual tool executable bytes omitted')
    for path, row in current['tools'].items():
        identity(path, row['sha256'], row['bytes'])

    print(json.dumps(dict(checkpoint_verified=True, current_sources_required=args.require_current,
        HOST_groups=127, exact_sample_checks=468228, exhaustive_bit_patterns=65536,
        HOST_sanitizers=['ASan','UBSan'], Xtensa_compile_profiles=['O2','O3'],
        actual_forbidden_width_controls=3, historical_NONPASS=['xtensa01','xtensa02'],
        historical_capture_required=False, objects_executed=False, SDK_or_QEMU_executed=False,
        native_IRAM_allocation_qualified=False, full_application_fit_qualified=False,
        physical_hardware_qualified=False, omitted_original_bytes_read=False)))


if __name__ == '__main__':
    main()
