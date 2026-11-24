"""ASan/UBSan contracts for the bounded pbuf recorder and its external lock."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'tests/target/cyd_full_app_openeth_qemu'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def sha(data):
    return hashlib.sha256(data).hexdigest()


def logged(command, destination):
    try:
        body = run(command)
        code = 0
    except subprocess.CalledProcessError as error:
        body, code = error.output, error.returncode
    destination.write_bytes(body)
    return code, body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True)
    sources = output / 'sources'
    sources.mkdir()
    files = [TARGET / 'pbuf_failure_record.h', TARGET / 'pbuf_failure_record_test.c', Path(__file__).resolve()]
    for path in files:
        (sources / path.name).write_bytes(path.read_bytes())
    original = (sources / 'pbuf_failure_record.h').read_bytes().replace(b'\r\n', b'\n')
    mutations = [
        ('candidate', None, None, 0, b'PASS 6 pbuf recorder groups; table=128 bytes; slots=4'),
        ('narrow-type-negative', b'left->type == right->type',
         b'(uint8_t)left->type == (uint8_t)right->type', 42, b'table.used == 2 && table.total == 2'),
        ('ignore-caller-negative', b'left->caller_pc == right->caller_pc', b'true',
         42, b'table.used == 2 && table.total == 2'),
        ('wrap-total-negative',
         b'    if (table->total == UINT32_MAX) table->saturated |= PBUF_FAILURE_RECORD_TOTAL_SATURATED;\n    else ++table->total;',
         b'    ++table->total;', 42, b'table.total == UINT32_MAX && table.entries[0].count == UINT32_MAX'),
    ]
    report = {'scope': 'Portable table only; actual external pthread mutex with concurrent snapshots. Production wrapper, target ABI/frames and hardware timing are separate checks.',
              'physical_tested': False, 'table_bytes': 128, 'key_bytes': 20, 'entry_bytes': 28,
              'slots': 4, 'writer_events': 100000,
              'sources': {path.name: sha((sources / path.name).read_bytes()) for path in files},
              'variants': {}}
    code, _ = logged(['gcc', '--version'], output / 'compiler-version.log')
    if code:
        raise RuntimeError('Host GCC unavailable; original compiler-version.log preserved')
    for name, before, after, expected, needle in mutations:
        work = output / name
        work.mkdir()
        candidate = original
        if before is not None:
            assert candidate.count(before) == 1
            candidate = candidate.replace(before, after, 1)
        (work / 'pbuf_failure_record.h').write_bytes(candidate)
        binary = work / 'test'
        build = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                 '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                 '-fstack-usage', '-pthread', '-I' + host(work),
                 host(sources / 'pbuf_failure_record_test.c'), '-o', host(binary)]
        # Quote includes search the source's own directory first; compile its
        # frozen copy beside the per-variant header so controls exercise it.
        harness = work / 'pbuf_failure_record_test.c'
        harness.write_bytes((sources / 'pbuf_failure_record_test.c').read_bytes())
        build[-3] = host(harness)
        build_code, _ = logged(build, work / 'build.log')
        if build_code:
            raise RuntimeError(f'{name} compilation failed; raw build.log preserved')
        command = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary)]
        code, body = logged(command, work / 'test.log')
        item = {'source_sha256': sha(candidate), 'build_command': build,
                'test_command': command, 'returncode': code, 'expected_returncode': expected,
                'passed': code == expected and needle in body,
                'host_stack_usage': [{'file': path.name, 'sha256': sha(path.read_bytes())}
                                     for path in work.glob('*.su')]}
        report['variants'][name] = item
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        if not item['passed']:
            raise RuntimeError(f'Unexpected {name} result; original logs/report preserved')
        print(name + ': ' + ('passed six groups' if expected == 0 else 'correctly rejected'))
    report['passed'] = True
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
