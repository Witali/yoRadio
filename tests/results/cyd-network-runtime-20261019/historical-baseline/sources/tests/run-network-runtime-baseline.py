"""Preserve executable historical Wi-Fi defects before runtime replacement.

This is negative evidence from exact Git source bodies, not a current-runtime
regression gate or a full historical firmware reconstruction. Actual startup,
AP setup, event, retry and C3 selection/RSSI/power functions run unchanged with
deterministic SDK, RTOS, active-profile loader and state-publication seams.
No radio, driver binary, actual RTOS scheduling, SMP or audio interleaving runs.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '048a5c42df67a24b6e99396aae382f91d3b4ef49'
FIXTURE = Path('tests/native/network_runtime_baseline')
TARGETS = {
    'cyd': ('idf/esp32-cyd2usb-native/main/network_service.c', [
        'station_lost_ip', 'event_handler', 'start_access_point',
        'network_service_start', 'network_service_retry_client']),
    'c3': ('idf/esp32c3-oled-native/main/network_service.c', [
        'rssi_task', 'select_credential', 'event_handler',
        'softap_reboot_callback', 'start_access_point',
        'network_service_set_streaming', 'network_service_start',
        'network_service_retry_client']),
}
SAFETY_CASES = {
    'late-fallback': 'late_failure_requires_portal',
    'manual-apsta': 'manual_retry_preserves_portal_until_reply',
    'stale-state': 'disconnect_invalidates_client_and_ip',
    'failed-config': 'failed_config_keeps_applied_selection',
    'stale-rssi': 'failed_rssi_query_invalidates_sample',
    'last-profile': 'late_cycle_wraps_to_earlier_profiles',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT)


def function(source, name):
    """Return one exact function span, ignoring braces in strings/comments."""
    match = re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+' +
                      re.escape(name) + r'\s*\(', source, re.M)
    if not match:
        raise ValueError('Historical function missing: ' + name)
    opening = source.index('{', match.start())
    depth = 1
    position = opening + 1
    while depth:
        if source.startswith('//', position):
            position = source.index('\n', position) + 1
        elif source.startswith('/*', position):
            position = source.index('*/', position + 2) + 2
        elif source[position] in ('"', "'"):
            quote = source[position]
            position += 1
            while source[position] != quote:
                position += 2 if source[position] == '\\' else 1
            position += 1
        else:
            depth += (source[position] == '{') - (source[position] == '}')
            position += 1
    return source[match.start():position], match.start(), position


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', '--output', dest='out', type=Path, required=True)
    parser.add_argument('--revision', default=BASELINE,
                        help='Historical commit; current moving working files are never inputs')
    parser.add_argument('--target', choices=['all', *TARGETS], default='all')
    args = parser.parse_args()
    revision = git('rev-parse', '--verify', args.revision + '^{commit}').decode().strip()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {
        'passed': False, 'historical_revision': revision,
        'scope': __doc__, 'evidence_kind': 'historical_baseline_negative',
        'current_runtime_tested': False, 'physical_hardware': False,
        'actual_audio_generation_interleaving': False,
        'source_sha256': {}, 'source_origin': {}, 'targets': {},
        'seams': [
            'SDK APIs accept/reject synchronously and expose modeled driver state',
            'event-group wait delivers GOT_IP through actual handler, or returns timeout',
            'task creation records admission; RSSI loop is explicitly executed until second delay',
            'loader supplies two synthetic active profiles; storage/parsing is outside this suite',
            'native_state setters expose a single-threaded field model without lock/ABI claims',
            'netifs, event registration, timer creation, power and restart are deterministic seams',
            'no complete application reconstruction, RF/TCP delivery or scheduler qualification',
        ],
    }
    selected = list(TARGETS) if args.target == 'all' else [args.target]
    historical = {}
    # Freeze every selected original and every harness input before compiling.
    for target in selected:
        relative = TARGETS[target][0]
        historical[relative] = git('show', revision + ':' + relative)
    current_inputs = [Path(__file__).resolve().relative_to(ROOT), FIXTURE / 'platform.h',
                      FIXTURE / 'test.c', FIXTURE / 'README.md',
                      Path('tools/codec_benchmark/run_output_dma_host.py')]
    for relative in [*map(Path, historical), *current_inputs]:
        key = relative.as_posix()
        data = historical[key] if key in historical else (ROOT / relative).read_bytes()
        destination = out / 'sources' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        report['source_sha256'][key] = sha(data)
        report['source_origin'][key] = ('git:' + revision if key in historical else
                                         'working_tree_harness_snapshot')
    helper_path = out / 'sources/tools/codec_benchmark/run_output_dma_host.py'
    spec = importlib.util.spec_from_file_location('frozen_network_host', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

    def execute(command, log_path):
        result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        log_path.write_bytes(result.stdout)
        return result

    compiler = execute(['gcc', '--version'], out / 'compiler.log')
    assert compiler.returncode == 0, compiler.stdout.decode(errors='replace')
    for target in selected:
        relative, names = TARGETS[target]
        source = (out / 'sources' / relative).read_bytes().decode('utf-8')
        directory = out / target
        directory.mkdir()
        functions = []
        bodies = []
        for name in names:
            body, start, end = function(source, name)
            bodies.append(body)
            functions.append({'name': name, 'source_character_start': start,
                              'source_character_end': end, 'sha256': sha(body.encode())})
        actual = ('\n\n'.join(bodies) + '\n').encode('utf-8')
        (directory / 'actual.inc').write_bytes(actual)
        policies = []
        for constant in ['WIFI_CONNECTED_BIT', 'WIFI_FAILED_BIT', 'WIFI_MAX_RETRIES',
                         'WIFI_RETRIES_PER_CREDENTIAL', 'WIFI_MAX_CREDENTIALS',
                         'WIFI_RSSI_INTERVAL_MS']:
            match = re.search(r'^#define ' + constant + r'[^\n]*', source, re.M)
            if match:
                policies.append(match.group(0))
        policy = ('\n'.join(policies) + '\n').encode('utf-8')
        (directory / 'policy.inc').write_bytes(policy)
        binary = directory / 'baseline'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-unused-function', '-Wno-unused-variable',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-I' + helper.host(directory),
                   '-I' + helper.host(out / 'sources' / FIXTURE)]
        if target == 'c3':
            command.append('-DTARGET_C3=1')
        command += [helper.host(out / 'sources' / FIXTURE / 'test.c'), '-o', helper.host(binary)]
        result = execute(command, directory / 'build.log')
        assert result.returncode == 0, result.stdout.decode(errors='replace')
        target_report = {'actual_functions': functions, 'command': command,
                         'generated_source_sha256': {'actual.inc': sha(actual),
                                                     'policy.inc': sha(policy)},
                         'negative_controls': {}, 'characterizations': {}}
        report['targets'][target] = target_report
        cases = list(SAFETY_CASES) if target == 'c3' else ['late-fallback', 'manual-apsta']
        for case in cases + (['power-bool'] if target == 'c3' else []):
            result = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                              'UBSAN_OPTIONS=halt_on_error=1', helper.host(binary), case],
                             directory / (case + '.log'))
            log = result.stdout.decode(errors='replace')
            assert not any(marker in log for marker in [
                'AddressSanitizer', 'LeakSanitizer', 'runtime error:', 'Assertion']), log
            if case == 'power-bool':
                assert result.returncode == 0, log
                assert log == ('CHARACTERIZATION:unowned_bool_false_replaces_true\n'
                               'LIMIT:actual_audio_generation_interleaving_is_not_executed\n'), log
                target_report['characterizations'][case] = {
                    'passed': True, 'exit_code': 0, 'actual_audio_interleaving': False}
            else:
                marker = 'SAFETY_FAILURE:' + SAFETY_CASES[case]
                assert result.returncode == 42 and log == marker + '\n', (case, result.returncode, log)
                target_report['negative_controls'][case] = {
                    'detected': True, 'exit_code': result.returncode, 'expected_marker': marker}
            print(target + ': ' + log.strip())
        target_report['passed'] = True
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: historical safety failures reproduced; this does not certify the current runtime')


if __name__ == '__main__':
    main()
