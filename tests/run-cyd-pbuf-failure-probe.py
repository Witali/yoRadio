"""ASan/UBSan host qualification of the actual diagnostic pbuf wrapper.

SDK platform seams are explicit stubs; record bodies and wrapper are unchanged.
Natural host pointer/mutex/size_t geometry is not ESP32 target footprint proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'tests/target/cyd_full_app_openeth_qemu'
CPU_HEADER_SHA = '8cc93319400baefa525cf200c829152f0dfb0ae55e060cb30adfea77a2254f75'


def pin(path):
    body = Path(path).read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command, log):
    prefix = ['wsl.exe', '--exec'] if sys.platform == 'win32' else []
    result = subprocess.run(prefix + command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
    log.write_bytes(result.stdout)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh output directory under the project .build')
    output.mkdir(parents=True, exist_ok=False)
    sources = output / 'sources'
    sources.mkdir()
    original_files = [Path(__file__), TARGET / 'pbuf_failure.c', TARGET / 'pbuf_failure_record.h',
                      TARGET / 'pbuf_failure_probe_test.c']
    originals = {path: pin(path) for path in original_files}
    for path in original_files:
        (sources / path.name).write_bytes(path.read_bytes())

    cpu_header = args.sdk / 'components/xtensa/include/esp_cpu_utils.h'
    cpu_identity = pin(cpu_header)
    if cpu_identity['sha256'] != CPU_HEADER_SHA:
        raise ValueError('Unexpected pinned SDK PC normalization header')
    sdk_public = {name: pin(args.sdk / relative) for name, relative in {
        'esp_cpu_utils.h': 'components/xtensa/include/esp_cpu_utils.h',
        'pbuf.h': 'components/lwip/lwip/src/include/lwip/pbuf.h',
        'mem.h': 'components/lwip/lwip/src/include/lwip/mem.h',
        'arch.h': 'components/lwip/lwip/src/include/lwip/arch.h',
        'lwipopts.h': 'components/lwip/port/include/lwipopts.h',
    }.items()}
    stubs = {
        'esp_attr.h': '#pragma once\n#define DRAM_ATTR\n',
        'esp_rom_sys.h': '#pragma once\nint esp_rom_printf(const char *, ...);\n',
        'freertos/FreeRTOS.h': '''#pragma once
#include <pthread.h>
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
void host_enter_critical(portMUX_TYPE *, unsigned);
void host_exit_critical(portMUX_TYPE *, unsigned);
#define portENTER_CRITICAL_ISR(lock) host_enter_critical((lock), 1)
#define portEXIT_CRITICAL_ISR(lock) host_exit_critical((lock), 1)
#define portENTER_CRITICAL(lock) host_enter_critical((lock), 0)
#define portEXIT_CRITICAL(lock) host_exit_critical((lock), 0)
''',
        'lwip/mem.h': '''#pragma once
#include <stddef.h>
/* Pinned MEM_LIBC_MALLOC branch; size_t follows the host ABI here. */
typedef size_t mem_size_t;
#define MEM_ALIGNMENT 4
#define LWIP_MEM_ALIGN_SIZE(size) (((size) + MEM_ALIGNMENT - 1U) & ~(MEM_ALIGNMENT - 1U))
''',
        'lwip/pbuf.h': '''#pragma once
#include <stdint.h>
typedef uint8_t u8_t;
typedef uint16_t u16_t;
/* Selected IPv4/ethernet profile: transport20 + IP20 + link14. */
typedef enum { PBUF_TRANSPORT=54, PBUF_IP=34, PBUF_LINK=14, PBUF_RAW_TX=0, PBUF_RAW=0 } pbuf_layer;
/* Full public enum values, not the pbuf.type_internal low byte. */
typedef enum { PBUF_RAM=0x280, PBUF_ROM=1, PBUF_REF=0x41, PBUF_POOL=0x182 } pbuf_type;
/* Public fields with natural host pointers/padding; NOT a packed target ABI. */
struct pbuf {
    struct pbuf *next;
    void *payload;
    u16_t tot_len, len;
    u8_t type_internal, flags, ref, if_idx;
};
''',
    }
    stub_dir = output / 'stubs'
    for relative, body in stubs.items():
        destination = stub_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(body, encoding='utf-8', newline='\n')
    # Copy the exact SDK inline implementation, including window-bit handling.
    (stub_dir / 'esp_cpu_utils.h').write_bytes(cpu_header.read_bytes())

    report = dict(state='PREPARED', passed=False, physical_tested=False,
        scope='Actual root wrapper and record header, explicit public SDK stubs, exact SDK PC helper, external pthread lock. '
              'Header calls pass through scope-checking trampolines into unchanged inline bodies. '
              'No firmware, target ABI size, linker wrap coverage or physical timing qualification.',
        sources={path.relative_to(ROOT).as_posix(): identity for path, identity in originals.items()},
        sdk_public_headers=sdk_public, copied_pc_header=pin(stub_dir / 'esp_cpu_utils.h'),
        stubs={p.relative_to(stub_dir).as_posix(): pin(p) for p in stub_dir.rglob('*') if p.is_file()}, variants={})

    def save():
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    try:
        version = execute(['gcc', '--version'], output / 'compiler-version.log')
        if version.returncode:
            raise RuntimeError('Host compiler unavailable; see compiler-version.log')
        actual = (sources / 'pbuf_failure.c').read_bytes()
        normalized = actual.replace(b'\r\n', b'\n')
        forward = b'struct pbuf *result = __real_pbuf_alloc(layer, length, type);'
        enter = b'portENTER_CRITICAL_ISR(&s_pbuf_failure_lock);'
        snapshot = (enter + b'\n    pbuf_failure_record_snapshot(&s_pbuf_failures, &snapshot);\n'
                    b'    portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);')
        if normalized.count(forward) != 1 or normalized.count(snapshot) != 1 or normalized.count(enter) != 2:
            raise ValueError('Probe changed; review exact negative-control seams')
        variants = [
            ('actual', actual, None),
            ('duplicate-real-call', normalized.replace(forward, forward +
                b'\n    (void)__real_pbuf_alloc(layer, length, type);', 1), b't_real_calls_in_wrapper == 0'),
            ('record-success', normalized.replace(b'if (!result) {', b'if (result) {', 1),
             b'atomic_load(&s_record_additions) == 0'),
            ('log-under-critical', normalized.replace(enter, enter +
                b'\n        esp_rom_printf("unexpected hot log\\n");', 1), b't_critical_depth == 0'),
            ('snapshot-outside-lock', normalized.replace(snapshot, enter +
                b'\n    portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);\n'
                b'    pbuf_failure_record_snapshot(&s_pbuf_failures, &snapshot);', 1), b't_critical_depth == 1'),
            ('extra-hot-heap', b'#include <stdlib.h>\n' + normalized.replace(enter,
                b'void *unexpected = malloc(1); free(unexpected);\n        ' + enter, 1),
             b'!t_wrapper_depth || t_real_depth'),
        ]
        for name, body, rejected_assertion in variants:
            work = output / name
            work.mkdir()
            for filename in ('pbuf_failure_probe_test.c', 'pbuf_failure_record.h'):
                (work / filename).write_bytes((sources / filename).read_bytes())
            (work / 'pbuf_failure.c').write_bytes(body)
            binary = work / 'test'
            command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                       '-pthread', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                       '-fno-optimize-sibling-calls', '-fno-ipa-icf', '-fno-pie', '-no-pie',
                       '-fno-builtin-malloc', '-fno-builtin-calloc', '-fno-builtin-realloc', '-fno-builtin-free',
                       '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free',
                       '-I' + host(stub_dir), host(work / 'pbuf_failure_probe_test.c'), '-o', host(binary)]
            built = execute(command, work / 'build.log')
            if built.returncode:
                raise RuntimeError(name + ' build failed; inspect its build.log')
            test_command = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                            'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary)]
            tested = execute(test_command, work / 'test.log')
            if rejected_assertion is None:
                if tested.returncode or b'PASS pbuf wrapper:' not in tested.stdout:
                    raise RuntimeError('Actual wrapper failed; inspect actual/test.log')
                geometry = re.search(rb'host_pbuf_bytes=(\d+) host_mem_size_bytes=(\d+) host_lock_bytes=(\d+) table_bytes=(\d+)', tested.stdout)
                if geometry is None:
                    raise RuntimeError('Missing explicit host geometry')
                report['host_geometry'] = dict(zip(('pbuf_bytes', 'mem_size_t_bytes', 'lock_bytes', 'record_bytes'),
                                                  map(int, geometry.groups())))
            elif (tested.returncode not in (-6,134) or rejected_assertion not in tested.stdout or
                  b'ERROR: AddressSanitizer' in tested.stdout or b'runtime error:' in tested.stdout):
                raise RuntimeError(name + ' did not fail its intended assertion')
            report['variants'][name] = dict(passed=True, expected='PASS' if rejected_assertion is None else 'assertion rejection',
                returncode=tested.returncode, build_command=command, test_command=test_command,
                wrapper=pin(work / 'pbuf_failure.c'), log=pin(work / 'test.log'))
            save()
            print(name + ': ' + ('PASS' if rejected_assertion is None else 'expected assertion rejection'))
        for path, identity in originals.items():
            if pin(path) != identity:
                raise RuntimeError('Input changed during host qualification; frozen evidence retained')
        if pin(cpu_header) != cpu_identity:
            raise RuntimeError('SDK PC helper changed during host qualification')
        report.update(state='TERMINAL_PASS', passed=True)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        report.update(state='TERMINAL_NONPASS', reason=str(error))
        save()
        raise
    save()


if __name__ == '__main__':
    main()
