"""Pure evidence schema/config rules; never imports or replays campaign scripts."""
import ntpath
from pathlib import PureWindowsPath
import re

HEAD = '3a563324abdca56144a40d5759def0ccfe708b3c'
ORIGINAL_MARKER = '7a2f5ed4ca33eddbd6c55d03e38a9ae9f7b7a8c689be4c3e926a0de8301ba81b'
REPAIR_MARKER = '6eb0b9b6a3897278eeb847b188d8e12fc8ff089a9ba9f6c6b295056f8bbb2f22'
FAILED_PDM = 'c66e7671e6366714d76a5d275119286c0eaef19abc271109814d3ad1df2b9964'
ORIGINAL_SCRIPT = '9c51f8c16a47fe6d72f16875f2bc25b3aa4049f0ec375711b581080ae259b301'
WORKSPACE = 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review'
RESERVE = 'YORADIO_TLS_STATIC_RX_RESERVE'
SPECS = {'pdm': ('pdm', False, True), 'continuous': ('continuous', False, True),
         'legacy': ('legacy', False, True), 'custom-flac-pdm': ('pdm', True, True),
         'custom-flac-continuous': ('continuous', True, True),
         'custom-flac-legacy': ('legacy', True, True), 'disabled-pdm': ('pdm', False, False)}
TRANSITIONS = {
    'COMPILER_CXX_GLIBCXX_CONSTEXPR_COLD': (False, None),
    'COMPILER_CXX_GLIBCXX_CONSTEXPR_COLD_CONSTEXPR': (False, None),
    'COMPILER_CXX_GLIBCXX_CONSTEXPR_NO_CHANGE': (True, None),
    'COMPILER_NO_MERGE_CONSTANTS': (False, None), 'COMPILER_RT_LIB_CLANGRT': (None, False),
    'COMPILER_STATIC_ANALYZER': (False, None), 'IDF_TOOLCHAIN': ('gcc', 'clang'),
    'IDF_TOOLCHAIN_CLANG': (None, True), 'IDF_TOOLCHAIN_GCC': (True, None),
    'LIBC_NEWLIB': (False, True), 'LIBC_NEWLIB_NANO_FORMAT': (None, True),
    'LIBC_PICOLIBC': (True, None), 'LIBC_PICOLIBC_NEWLIB_COMPATIBILITY': (True, None),
    RESERVE: (None, True),
}


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize(path):
    return path.replace('\\', '/').lower()


def typed(value):
    return {'present': True, 'type': type(value).__name__, 'value': value}


def state(config, key):
    return typed(config[key]) if key in config else {'present': False}


def expected_clang_delta():
    return {key: {'before': {'present': False} if before is None else typed(before),
                  'after': {'present': False} if after is None else typed(after)}
            for key, (before, after) in sorted(TRANSITIONS.items())}


def config_scope(before, after, name, kind):
    require(name in SPECS and kind in ('export', 'clang'), 'Known exact profile/config scope')
    backend, custom, enabled = SPECS[name]
    require(kind == 'export' or enabled, 'No reserve-off Clang scope')
    changes = {key: {'before': state(before, key), 'after': state(after, key)}
               for key in sorted(before.keys() | after.keys()) if state(before, key) != state(after, key)}
    expected = expected_clang_delta() if kind == 'clang' else {
        RESERVE: {'before': {'present': False}, 'after': typed(enabled)}}
    require(changes == expected, 'Complete typed configuration scope mismatch')
    invariants = {'IDF_TARGET': 'esp32', 'IDF_TARGET_ARCH': 'xtensa', 'FREERTOS_UNICORE': False,
                  'YORADIO_TLS_EARLY_MPI_LOCK': True, 'YORADIO_TLS_INPUT_RECLAIM': True,
                  'MBEDTLS_SSL_IN_CONTENT_LEN': 16384, 'MBEDTLS_SSL_OUT_CONTENT_LEN': 4096,
                  'YORADIO_FLAC_DECODER_CUSTOM': custom, 'YORADIO_FLAC_DECODER_ESPRESSIF': not custom,
                  'YORADIO_NATIVE_AUDIO_OUTPUT_PDM': backend == 'pdm',
                  'YORADIO_NATIVE_AUDIO_OUTPUT_DAC': backend == 'continuous',
                  'YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC': backend == 'legacy',
                  'COMPILER_RT_LIB_GCCLIB': True, 'COMPILER_RT_LIB_NAME': 'gcc'}
    for key, value in invariants.items():
        require(state(before, key) == typed(value) and state(after, key) == typed(value),
                'Preserved hardware/profile/runtime invariant mismatch: ' + key)
    require(after['IDF_TOOLCHAIN'] == ('clang' if kind == 'clang' else 'gcc'), 'Compiler profile mismatch')
    require(after['LIBC_NEWLIB'] is (kind == 'clang'), 'Clang Newlib / production GCC Picolibc scope')
    return changes


def source_snapshot(value):
    require(value['commit'] == HEAD and value['dirty'] is False and value['source_dirty'] is False
            and value['untracked'] == [] and re.fullmatch('[0-9a-f]{64}', value['content_sha256']),
            'Exact frozen clean source snapshot required')


def summary(value):
    require(value['schema'] == 'cyd-static-rx-clang-qualification-repair-v1'
            and value['passed'] is True and value['exports'] == 7 and value['full_clang_runs'] == 6,
            'Complete successor seven/six closure required')
    source_snapshot(value['source_snapshot'])
    expected = {('export', 'original', name) for name in SPECS} | {
        ('clang', 'successor', name) for name in SPECS if name != 'disabled-pdm'}
    actual = []
    for row in value['reports']:
        path = normalize(row['report']['path'])
        found = [name for name in SPECS if path.endswith('/' + row['kind'] + '-' + name + '/report.json')]
        require(len(found) == 1, 'Exact report kind/profile path required')
        actual.append((row['kind'], row['origin'], found[0]))
    require(len(actual) == 13 and len(set(actual)) == 13 and set(actual) == expected,
            'Exact distinct original GCC / successor Clang report matrix')
    require(value['repair_marker']['sha256'] == REPAIR_MARKER
            and value['original_qualifier_failure']['sha256'] == FAILED_PDM,
            'Exact repair marker and retained failed qualifier required')
    require(value['physical_qualified'] is False and value['heap_saving_claimed'] is False
            and value['warning_triage_remains_explicit'] is True, 'Honest closure limitations required')


def terminal(closed, receipt, digest, expected_path, expected_repair_script):
    summary(closed)
    require(re.fullmatch('[0-9a-f]{64}', digest), 'Root raw summary SHA required')
    require(receipt['schema'] == 'cyd-static-rx-sdk-close-terminal-v1'
            and receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int
            and receipt['returncode'] == 0 and receipt['observed_by'] == 'root',
            'Separate root-observed authoritative close terminal0 required')
    require(receipt['summary_sha256'] == digest
            and normalize(receipt['summary_path']) == normalize(expected_path)
            and receipt['source_commit'] == HEAD and receipt['repair_marker_sha256'] == REPAIR_MARKER
            and receipt['original_marker_sha256'] == ORIGINAL_MARKER, 'Terminal receipt exact closure pins')
    proof = receipt['terminal_proof']
    require(isinstance(proof['tool_handle'], str) and proof['tool_handle'].strip()
            and isinstance(proof['tool_chunk'], str) and proof['tool_chunk'].strip(),
            'Actual tool terminal handle/chunk required; a report PASS alone is insufficient')
    cwd = receipt['cwd']
    require(isinstance(cwd, str) and PureWindowsPath(cwd).is_absolute()
            and normalize(ntpath.normpath(cwd)) == normalize(ntpath.normpath(WORKSPACE)),
            'Receipt must preserve the pinned execution cwd')
    argv = receipt['argv']
    require(isinstance(argv, list) and all(isinstance(value, str) for value in argv), 'Raw command argv list required')
    matches = [index for index, value in enumerate(argv)
               if ntpath.basename(value).lower() == 'repair.py']
    require(len(matches) == 1, 'Receipt must identify actual successor close command')
    # Resolve this one raw script argument lexically, without changing argv,
    # looking up filesystem paths or resolving interpreter/options/other tokens.
    script = PureWindowsPath(argv[matches[0]])
    require(not (script.drive and not script.is_absolute())
            and not (script.root and not script.drive), 'Invalid script path in raw argv')
    resolved = str(script) if script.is_absolute() else str(PureWindowsPath(cwd) / script)
    require(PureWindowsPath(expected_repair_script).is_absolute()
            and normalize(ntpath.normpath(resolved)) == normalize(ntpath.normpath(expected_repair_script))
            and normalize(ntpath.normpath(expected_repair_script)) == normalize(ntpath.normpath(
                WORKSPACE + '/.build/cyd-clang-config-repair-prep-01/repair.py')),
            'Receipt must identify actual successor close command')
    require(argv[matches[0] + 1:] == [
        'close', '--repair-marker-sha256', REPAIR_MARKER], 'Receipt must identify actual successor close command')


def historical_failure(value, digest):
    require(digest == FAILED_PDM and value['passed'] is False and value['kind'] == 'clang'
            and value['row'] == 'pdm' and value['error'].startswith(
                "RuntimeError('Unexpected complete normalized config delta:"),
            'Original rejected PDM qualifier must remain exact nonpass evidence')


def control_report(value):
    require(value['passed'] is True and value['scope'] == 'pure config policy only'
            and value['accepted'] == 7 and value['rejected'] == 74 and len(value['results']) == 81
            and value['configure_compiler_lint_export_sdk_git_device_invocations'] == 0,
            'Exact 81 pure policy controls, not a real runtime gate')
