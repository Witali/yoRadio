"""Compile actual bounded Wi-Fi store/file transactions with faults and pthreads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    component = ROOT / 'idf/components/native_wifi_store'
    storage = ROOT / 'idf/components/native_storage'
    files = [Path(__file__), ROOT / 'tests/native/native_wifi_store_test.c',
             *component.rglob('*.c'), *component.rglob('*.h'), component / 'CMakeLists.txt',
             storage / 'file_transaction.c', storage / 'include/file_transaction.h']
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        frozen = out / 'sources' / relative
        frozen.parent.mkdir(parents=True, exist_ok=True)
        frozen.write_bytes(raw)
        hashes[relative.as_posix()] = hashlib.sha256(raw).hexdigest()
    frozen = out / 'sources'
    component = frozen / component.relative_to(ROOT)
    storage = frozen / storage.relative_to(ROOT)
    binary = out / 'wifi-store'
    wrappers = ['fopen', 'fwrite', 'fread', 'ferror', 'fflush', 'fclose',
                'remove', 'rename', 'calloc', 'free']
    command = ['gcc', '-std=c11', '-D_POSIX_C_SOURCE=200809L', '-O1', '-g',
               '-Wall', '-Wextra', '-Werror', '-pthread', '-fsanitize=address,undefined',
               '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(component / 'include'), '-I' + host(storage / 'include'),
               host(component / 'native_wifi_store.c'), host(component / 'native_wifi_file.c'),
               host(storage / 'file_transaction.c'),
               host(frozen / 'tests/native/native_wifi_store_test.c'),
               *['-Wl,--wrap=' + name for name in wrappers], '-o', host(binary)]
    try:
        (out / 'build.log').write_bytes(run(command))
        log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '40', host(binary)])
        (out / 'test.log').write_bytes(log)
        print(log.decode().strip())
    except subprocess.CalledProcessError as error:
        (out / 'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'))
        raise
    controls = {}
    original = (component / 'native_wifi_store.c').read_text()
    mutations = {
        'keep-wrong-duplicate-ssid': ('password = old->password;',
                                    'password = workspace->rows[0].password;'),
        'ignore-stale-revision': ('if (strcmp(expected, edit->revision))',
                                  'if (strcmp(expected, edit->revision) && false)'),
        'advance-revision-on-publish-failure':
            ('if (result == NATIVE_WIFI_OK) {\n        if (store->ops.committed_csv)',
             'if (result != NATIVE_WIFI_OK) ++store->generation;\n    if (result == NATIVE_WIFI_OK) {\n        if (store->ops.committed_csv)'),
        'skip-secret-workspace-erase': ('native_wifi_erase(workspace, sizeof(*workspace));',
                                       '/* mutant: omitted erase */'),
        'secret-in-public-metadata': ('memcpy(out->profiles[i].ssid, workspace->rows[i].ssid,',
                                      'memcpy(out->profiles[i].ssid, workspace->rows[i].password,'),
    }
    expected_failures = {
        'keep-wrong-duplicate-ssid': 'check_live',
        'ignore-stale-revision': 'typed_cases',
        'advance-revision-on-publish-failure': 'fault_cases',
        'skip-secret-workspace-erase': '__wrap_free',
        'secret-in-public-metadata': 'typed_cases',
    }
    for name, (before, after) in mutations.items():
        if original.count(before) != 1:
            raise RuntimeError('Mutation anchor is not unique: ' + name)
        directory = out / name
        directory.mkdir()
        source = directory / 'native_wifi_store.c'
        source.write_text(original.replace(before, after))
        mutant_binary = directory / 'test'
        mutant_command = [host(source) if word == host(component / 'native_wifi_store.c')
                          else host(mutant_binary) if word == host(binary) else word
                          for word in command]
        (directory / 'build.log').write_bytes(run(mutant_command))
        try:
            result = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                          'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '40', host(mutant_binary)])
        except subprocess.CalledProcessError as error:
            result = error.output
            text = result.decode(errors='replace')
            if (expected_failures[name] not in text or 'Assertion' not in text or
                    'ERROR: AddressSanitizer' in text or 'runtime error:' in text):
                (directory / 'unexpected.log').write_bytes(result)
                raise RuntimeError('Mutation failed outside its semantic assertion: ' + name) from error
            controls[name] = {'rejected': True, 'semantic_assertion': expected_failures[name]}
            (directory / 'test.log').write_bytes(result)
        else:
            (directory / 'test.log').write_bytes(result)
            raise RuntimeError('Semantic control survived: ' + name)
    report = {'passed': True, 'source_sha256': hashes, 'result': log.decode().strip(),
              'semantic_controls': controls,
              'sanitizers': ['ASan', 'UBSan'],
              'scope': 'Actual portable production store/file helpers and file_transaction.c; real Linux temporary files and pthread owner locking; injected stdio/rename/allocation faults. Synthetic credentials only. Does not prove target filesystem power-loss durability, HTTP/UI privacy or target networking.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(str(len(controls)) + ' semantic controls rejected')


if __name__ == '__main__':
    main()
