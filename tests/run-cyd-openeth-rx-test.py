"""Test generated pinned OpenETH RX functions under ASan/UBSan on the host."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'tests/target/cyd_full_app_openeth_qemu'
TEST = TARGET / 'openeth_rx'
PRIOR_OVERLAY_SHA = '77827f4605a712e9057484fe5999c8a3405e3e617f3f45e52ca8933d96be6cca'
TASK = b'static void emac_opencores_rx_task(void *arg)'
RECEIVE = b'static esp_err_t emac_opencores_receive(esp_eth_mac_t *mac, uint8_t *buf, uint32_t *length)'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def function(source, marker):
    start = source.index(marker + b'\n{')
    brace = start + len(marker) + 1
    depth = 0
    for end in range(brace, len(source)):
        depth += (source[end] == ord('{')) - (source[end] == ord('}'))
        if depth == 0 and end > brace:
            return source[start:end + 1]
    raise ValueError('Incomplete pinned SDK function')


def execute(command, log):
    prefix = ['wsl.exe', '--exec'] if sys.platform == 'win32' else []
    result = subprocess.run(prefix + command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=90)
    log.write_bytes(result.stdout)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True)
    generator = TARGET / 'prepare-rx-source.py'
    namespace = {'__name__': 'openeth_rx_host_overlay'}
    exec(compile(generator.read_text(), str(generator), 'exec'), namespace)
    raw = (args.sdk / 'components/esp_eth/src/openeth/esp_eth_mac_openeth.c').read_bytes()
    original = raw.replace(b'\r\n', b'\n')
    candidate = namespace['overlay'](raw)
    assert namespace['overlay'](original.replace(b'\n', b'\r\n')) == candidate
    try:
        namespace['overlay'](raw + b'\n')
    except ValueError as error:
        assert 'pinned ESP-IDF 6.0.2' in str(error)
    else:
        raise AssertionError('Wrong-source overlay guard did not reject changed SDK bytes')

    control = (TEST / 'max-allocation-control.inc').read_bytes().replace(b'\r\n', b'\n')
    control_task = function(control, TASK)
    control_receive = function(control, RECEIVE)
    assert control_receive == function(original, RECEIVE) == function(candidate, RECEIVE)
    # Reconstruct the entire exact prior overlay, rather than a look-alike MAX mock.
    prior = original.replace(function(original, TASK), control_task, 1)
    prior = prior.replace(b'#include "esp_intr_alloc.h"\n',
                          b'#include "esp_intr_alloc.h"\n#include "esp_heap_caps.h"\n', 1)
    assert sha(prior) == PRIOR_OVERLAY_SHA

    header = (args.sdk / 'components/esp_eth/src/openeth/openeth.h').read_bytes().replace(b'\r\n', b'\n')
    start = header.index(b'typedef struct {\n    uint16_t lc: 1;')
    end = header.index(b'} openeth_rx_desc_t;', start) + len(b'} openeth_rx_desc_t;')
    descriptor = header[start:end] + b'\n'
    sources = output / 'sources'
    sources.mkdir()
    for name, data in (('sdk-original.c', original), ('sdk-generated.c', candidate),
                       ('sdk-prior-overlay.c', prior), ('openeth.h', header),
                       ('prepare-rx-source.py', generator.read_bytes()),
                       ('test.c', (TEST / 'test.c').read_bytes()),
                       ('max-allocation-control.inc', control),
                       ('runner.py', Path(__file__).read_bytes())):
        (sources / name).write_bytes(data)

    report = {'sdk_source_sha256': sha(original), 'candidate_sha256': sha(candidate),
              'exact_prior_overlay_sha256': sha(prior), 'wrong_source_guard_passed': True,
              'crlf_normalization_passed': True,
              'sources': {path.name: sha(path.read_bytes()) for path in sources.iterdir()},
              'physical_tested': False,
              'scope': 'Actual generated SDK RX task and unchanged receive body, host platform/allocator stubs; no firmware or QEMU timing qualification.',
              'variants': {}}
    compiler = execute(['gcc', '--version'], output / 'compiler-version.log')
    assert compiler.returncode == 0
    for mode, source in (('candidate', candidate), ('max-allocation-control', prior)):
        work = output / mode
        work.mkdir()
        functions = b'\n\n'.join(function(source, marker) for marker in (TASK, RECEIVE)) + b'\n'
        (work / 'receive.inc').write_bytes(functions)
        (work / 'descriptor.inc').write_bytes(descriptor)
        binary = work / 'test'
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                   '-I' + host(work)]
        if mode == 'max-allocation-control':
            command.append('-DMAX_ALLOCATION_CONTROL=1')
        command += [host(sources / 'test.c'), '-o', host(binary)]
        build = execute(command, work / 'build.log')
        if build.returncode:
            raise RuntimeError(f'{mode} build failed; see {work / "build.log"}')
        run = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
               'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary)]
        result = execute(run, work / 'test.log')
        expected = 0 if mode == 'candidate' else 17
        message = (b'PASS 18 OpenETH exact-length RX' if mode == 'candidate' else
                   b'EXPECTED REJECTION: exact pre-fix MAX allocation')
        if result.returncode != expected or message not in result.stdout:
            raise RuntimeError(f'Unexpected {mode} result; see {work / "test.log"}')
        report['variants'][mode] = {'build_command': command, 'test_command': run,
                                    'returncode': result.returncode, 'expected_returncode': expected,
                                    'function_source_sha256': sha(functions), 'passed': True}
        print(f'{mode}: {"passed 18 cases" if expected == 0 else "correctly rejected under constrained heap"}')
    report['passed'] = True
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
