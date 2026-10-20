"""Qualify complete CYD network-settings handlers with actual settings/NVS code.

Only includes are replaced by frozen production type headers and explicit
HTTPD/query/transport, bounded runtime snapshot, RTOS lock and NVS seams. Every
production function body is compiled. This does not model HTTPD wire parsing,
flash power loss, target ABI, SDK timing, DHCP/RF or a physical restart.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host


def stripped(path):
    return re.sub(r'^\s*#\s*include[^\n]*\n', '', path.read_text(encoding='utf-8'), flags=re.M)


def run(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main_dir = ROOT / 'idf/esp32-cyd2usb-native/main'
    test = ROOT / 'tests/native'
    power = ROOT / 'idf/components/native_network_power/include/native_network_power.h'
    files = [Path(__file__).resolve(), test / 'cyd_web_network_settings_test.c',
             test / 'cyd_network_settings/platform.h', power,
             *[main_dir / name for name in ('network_settings.c', 'network_settings.h',
                 'network_status.h', 'web_network_settings.c', 'web_network_settings.h')],
             ROOT / 'idf/components/native_stream/include/json_buffer.h']
    hashes = {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    for f in files:
        target = out / 'sources' / f.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(f.read_bytes())
    # Frozen copies provide the only build input; live files are checked later.
    frozen_main = out / 'sources/idf/esp32-cyd2usb-native/main'
    frozen_test = out / 'sources/tests/native'
    frozen_power = out / 'sources' / power.relative_to(ROOT)
    (out / 'headers.inc').write_text(stripped(frozen_main / 'network_settings.h') +
        stripped(frozen_power) + stripped(frozen_main / 'network_status.h'), encoding='utf-8')
    (out / 'settings.inc').write_text(stripped(frozen_main / 'network_settings.c'), encoding='utf-8')
    source = stripped(frozen_main / 'web_network_settings.c')
    (out / 'web-network-settings.inc').write_text(source, encoding='utf-8')
    # inttypes is the only standard header omitted by the platform fixture.
    (out / 'headers.inc').write_text('#include <inttypes.h>\n' + (out / 'headers.inc').read_text(encoding='utf-8'), encoding='utf-8')
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-function', '-Wno-unused-variable', '-pthread',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(out), '-I' + host(frozen_test / 'cyd_network_settings'),
               '-I' + host(out / 'sources/idf/components/native_stream/include'),
               host(frozen_test / 'cyd_web_network_settings_test.c')]
    report = {'passed': False, 'scope': __doc__, 'physical_hardware': False,
              'sanitizers': ['ASan', 'UBSan'], 'command': command, 'source_sha256': hashes,
              'cases': {}, 'positive_checks': 0, 'json_responses': 0, 'negative_controls': {}}

    def build(name):
        binary = out / name
        code, log = run(command + ['-o', host(binary)])
        (out / (name + '-build.log')).write_bytes(log)
        if code:
            raise RuntimeError(log.decode(errors='replace'))
        return binary

    def execute(binary, case, marker=None):
        code, log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                         'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
        (out / (binary.name + '-' + case + '.log')).write_bytes(log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log, log
        if marker:
            assert code == 80 and ('SEMANTIC_FAILURE:' + marker + ':').encode() in log, (case, code, log)
            return {'rejected': True, 'case': case, 'status': code, 'expected_marker': marker}
        assert code == 0, (case, code, log)
        for line in log.decode().splitlines():
            if line.startswith('JSON '):
                data = json.loads(line[5:])
                if 'hostname' in data:
                    assert set(data) == {'hostname', 'ap_timeout_minutes', 'desired_revision',
                        'runtime_available', 'configured_hostname', 'hostname_pending',
                        'hostname_revision', 'last_hostname_error', 'ap_timeout_armed', 'ap_timeout_remaining_ms'}
                else:
                    assert data == {'saved': True, 'application_pending': True, 'rebooting': False}
                report['json_responses'] += 1
        count = re.search(rb'PASS [a-z_]+: (\d+) checks', log)
        assert count, log
        report['positive_checks'] += int(count.group(1))
        report['cases'][case] = log.decode().strip()

    try:
        binary = build('http')
        for case in ('get', 'valid', 'invalid', 'body', 'boundaries', 'save_errors', 'uninitialized', 'response_errors'):
            execute(binary, case)
        mutations = {
            'accept_duplicate': (' || (seen & (1U << index))', '', 'invalid', 'strict_query_rejected'),
            'accept_nul': ('if (!value || value < 0x20U || value == 0x7fU ||',
                'if ((value && value < 0x20U) || value == 0x7fU ||', 'invalid', 'strict_query_rejected'),
            'accept_partial': ('if (seen != 3U || !network_settings_valid(&candidate))',
                'if (!network_settings_valid(&candidate))', 'invalid', 'strict_query_rejected'),
            'skip_persist_error': ('if (result != ESP_OK)\n        return reply(request, "500',
                'if (false)\n        return reply(request, "500', 'save_errors', 'honest_store_status'),
            'claim_hostname_by_revision': ('strcmp(desired.hostname, snapshot.settings.configured_hostname) != 0;',
                'revision != snapshot.settings.hostname_revision;', 'get', 'timeout_revision_does_not_unapply_hostname'),
            'hide_desired_when_runtime_busy': ('bool available = network_service_snapshot(&snapshot, 25U) == ESP_OK;',
                'bool available = network_service_snapshot(&snapshot, 25U) == ESP_OK;\n'
                '    if (!available) return reply(request, "503 Service Unavailable", "{}");',
                'get', 'runtime_failure_keeps_desired'),
            'sdk_body_purge': ('    return ESP_FAIL;\n}\n\nstatic int hex_value',
                '    return ESP_OK;\n}\n\nstatic int hex_value', 'body', 'body_never_enters_sdk_purge'),
        }
        for name, (old, new, case, marker) in mutations.items():
            assert source.count(old) == 1, name
            (out / 'web-network-settings.inc').write_text(source.replace(old, new), encoding='utf-8')
            alternate = build(name)
            report['negative_controls'][name] = execute(alternate, case, marker)
        report['source_files_still_match_snapshot'] = all(
            hashlib.sha256(f.read_bytes()).hexdigest() == hashes[f.relative_to(ROOT).as_posix()] for f in files)
        assert report['source_files_still_match_snapshot']
        report['passed'] = True
    finally:
        (out / 'web-network-settings.inc').write_text(source, encoding='utf-8')
        report['generated_sha256'] = {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
            for name in ('headers.inc', 'settings.inc', 'web-network-settings.inc')}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS', len(report['cases']), 'HTTP groups,', report['positive_checks'],
          'checks +', len(mutations), 'exact semantic mutants')


if __name__ == '__main__':
    main()
