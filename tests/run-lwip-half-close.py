"""Compile the installed pinned esp-lwIP sources; run on Linux/WSL with ASan/UBSan."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile
import sys
import json
import resource
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from patch_lwip_timewait import patch, patch_api

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lwip', type=Path)
parser.add_argument('--allocator', choices=('pool', 'heap'), default='pool')
parser.add_argument('--unpatched', action='store_true', help='reproduce the SDK defect')
parser.add_argument('--output', type=Path, help='retain source hashes and per-case output')
args = parser.parse_args()
idf_version = (ROOT/'idf/esp32c3-oled-native/idf-version.txt').read_text().strip()
lwip_relative = Path('.idf')/idf_version/'components/lwip/lwip'
lwip = args.lwip or next((p/lwip_relative for p in (ROOT, *ROOT.parents)
                         if (p/lwip_relative/'src/core/tcp.c').exists()), None)
if not lwip:
    parser.error('supply --lwip /path/to/pinned/esp-lwip')
revision = subprocess.check_output(['git', '-C', str(lwip), 'rev-parse', 'HEAD'], text=True).strip()
print('lwIP commit:', revision, flush=True)
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
report = dict(lwip_commit=revision, allocator=args.allocator, patched=not args.unpatched,
              sources={}, cases=[])
for source in (ROOT/'tests/lwip-half-close/case.c', ROOT/'tests/lwip-half-close/lwipopts.h',
               ROOT/'tools/patch_lwip_timewait.py',
               ROOT/'idf/esp32c3-oled-native/main/tcp_pcb_pool.c'):
    report['sources'][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='lwip-half-close-') as directory:
    tmp = Path(directory)
    # WSL's /mnt/c metadata latency dominates preprocessing. Use a byte copy
    # of the same SDK sources on the native temporary filesystem.
    local = tmp/'lwip'
    for part in ('src', 'test/unit/arch', 'contrib/ports/unix/port/include'):
        shutil.copytree(lwip/part, local/part)
    lwip = local
    if not args.unpatched:
        tcp = lwip/'src/core/tcp.c'
        tcp.write_text(patch(tcp.read_text()))
        api = lwip/'src/api/api_msg.c'
        api.write_text(patch_api(api.read_text()))
    # Upstream's test OS assumes zero-filled static memp storage here; the
    # public set_invalid contract also accepts an uninitialized new mailbox.
    # Match that contract for heap-backed memp, without changing TCP/API code.
    arch = lwip/'test/unit/arch/sys_arch.c'
    original = arch.read_text()
    line = '  LWIP_ASSERT("mbox->q_mem == NULL", mbox->q_mem == NULL);\n'
    assert original.count(line) == 1
    arch.write_text(original.replace(line, ''))
    (tmp/'esp_attr.h').write_text('#define RTC_DATA_ATTR\n')
    sources = [*sorted((lwip/'src/core').glob('*.c')),
               *sorted((lwip/'src/core/ipv4').glob('*.c')),
               *sorted((lwip/'src/api').glob('*.c')),
               lwip/'test/unit/arch/sys_arch.c', ROOT/'tests/lwip-half-close/case.c']
    wrappers = ['-Wl,--wrap=tcp_input']
    if args.allocator == 'pool':
        sources.append(ROOT/'idf/esp32c3-oled-native/main/tcp_pcb_pool.c')
        wrappers += ['-Wl,--wrap=memp_malloc', '-Wl,--wrap=memp_free']
    exe = tmp/'case'
    subprocess.run(['cc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie',
                    '-I'+str(ROOT/'tests/lwip-half-close'), '-I'+str(tmp),
                    '-I'+str(lwip/'test/unit'),
                    '-I'+str(lwip/'contrib/ports/unix/port/include'),
                    '-I'+str(lwip/'src/include'), *map(str, sources), *wrappers,
                    '-o', str(exe)], check=True)
    for case in ('reap', 'reap-unread', 'expire', 'expire-unread', 'lastack', 'full'):
        result = subprocess.run([str(exe), case], timeout=30, capture_output=True, text=True,
                                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=1:abort_on_error=1',
                                     'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'})
        passed = result.returncode == 0
        report['cases'].append(dict(name=case, result='PASS' if passed else 'FAIL',
                                   returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        print(case, 'PASS' if passed else 'FAIL', flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
    if not all(c['result'] == 'PASS' for c in report['cases']):
        for case in report['cases']:
            if case['result'] == 'FAIL':
                print(case['name'], case['stdout'], case['stderr'])
        raise SystemExit(1)
