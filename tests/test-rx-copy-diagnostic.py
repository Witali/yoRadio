"""Exercise copied Wi-Fi RX ownership using the pinned lwIP input/free bodies.

Platform allocation and locking are host doubles. Function-name redirection
models linker wrapping; a separate firmware ELF audit must prove interposition.
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
from run_output_dma_host import host, run
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from rx_ownership import analyze, fields


def function(text, signature):
    """Pinned SDK functions have closing braces at column zero."""
    match = re.search(signature + r'\s*\{.*?^\}', text, re.M | re.S)
    if not match:
        raise ValueError('SDK function not found: ' + signature)
    return match.group(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdk-root', type=Path, default=ROOT /
        'tests/results/esp32c3-radio-rx-owner-build/sdk-sources')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'idf/esp32c3-oled-native/main/rx_buffer_diagnostic.c'
    harness = ROOT / 'tests/native/rx_copy_diagnostic_test.c'
    sdk_paths = {
        'input': 'components/esp_netif/lwip/netif/wlanif.c',
        'pbuf': 'components/lwip/lwip/src/core/pbuf.c',
        'mem': 'components/lwip/lwip/src/core/mem.c',
    }
    texts = {}
    hashes = {}
    for path in (source, harness, Path(__file__)):
        relative = path.relative_to(ROOT)
        dest = args.output / 'sources' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name, relative in sdk_paths.items():
        raw = (args.sdk_root / relative).read_bytes()
        dest = args.output / 'sdk-sources' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        texts[name] = raw.decode()
        hashes['sdk/' + relative] = hashlib.sha256(raw).hexdigest()
    sdk = [
        function(texts['input'], r'esp_err_t wlanif_input\([^\n]*\)'),
        function(texts['pbuf'], r'u8_t\s+pbuf_free\([^\n]*\)'),
        function(texts['mem'], r'void\s+mem_free\([^\n]*\)'),
    ]
    # Only public call/definition names change; retain SDK control flow intact.
    sdk[0] = re.sub(r'\bwlanif_input(?=\()', '__real_wlanif_input', sdk[0])
    sdk[0] = re.sub(r'\bpbuf_alloc(?=\()', '__wrap_pbuf_alloc', sdk[0])
    sdk[1] = re.sub(r'\bmem_free(?=\()', '__wrap_mem_free', sdk[1])
    sdk[2] = re.sub(r'\bmem_free(?=\()', '__real_mem_free', sdk[2])
    code = re.sub(r'^#include[^\n]*\n', '', source.read_text(), flags=re.M)
    unit = args.output / 'test.c'
    unit.write_text(harness.read_text().replace('/* PRODUCTION_SOURCE */', code)
                    .replace('/* SDK_FUNCTIONS */', '\n\n'.join(sdk)))
    binary = args.output / 'test'
    def logged(name, command):
        try:
            result = run(command)
        except subprocess.CalledProcessError as error:
            (args.output / name).write_bytes(error.output)
            print(error.output.decode(errors='replace'))
            raise
        (args.output / name).write_bytes(result)
        return result
    logged('build.log', ['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra',
        '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
        '-fno-pie', '-no-pie', '-pthread', host(unit), '-o', host(binary)])
    log = logged('run.log', ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
        'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
    lines = log.decode().splitlines()
    headers = [fields(line, 'PERF RX_OWNER3:') for line in lines if 'PERF RX_OWNER3:' in line]
    assert len(headers) == 4
    assert [h['live'] for h in headers] == [0, 2, 1, 0]
    assert headers[-1]['allocs'] == headers[-1]['frees'] == 9
    for h in headers:
        assert h['heap_free'] == 200000 - h['payload']
        assert h['heap_largest'] == 65536 and h['metadata'] == 0
        assert not (h['lost'] or h['unmatched'] or h['missing'])
    owner = analyze([dict(at=i, line=line) for i, line in enumerate(lines)])
    assert owner['maximum_live'] == 2
    report = {'pass': True, 'source_sha256': hashes, 'ownership': owner,
        'scope': 'Host SDK input/free control flow and diagnostic lifetimes; no target timing or interposition claim',
        'checks': ['allocation failure', 'down interface', 'null input', 'rejected input',
            'immediate consumption', 'retained references', 'chained final free',
            'shared tail', 'nested input', 'unrelated callback allocation',
            'other task allocation', 'scope restoration', 'paired heap',
            'ASan poisoned freed blocks', 'UBSan']}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(lines[-1])


if __name__ == '__main__':
    main()
