"""Exercise actual bounded Wi-Fi JSON production grammar, Unicode and limits."""
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
    files = [Path(__file__), ROOT / 'tests/native/native_wifi_json_test.c',
             component / 'native_wifi_store.c', component / 'native_wifi_json.c',
             *component.glob('include/*.h'), component / 'CMakeLists.txt']
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        dest = out / 'sources' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        hashes[relative.as_posix()] = hashlib.sha256(raw).hexdigest()
    frozen = out / 'sources'
    component = frozen / component.relative_to(ROOT)
    binary = out / 'test'
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(component / 'include'), host(component / 'native_wifi_store.c'),
               host(component / 'native_wifi_json.c'),
               host(frozen / 'tests/native/native_wifi_json_test.c'), '-o', host(binary)]
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
    original = (component / 'native_wifi_json.c').read_text()
    mutations = {
        'accept-duplicate-member': ('(fields & bit) || !profiles(&in, out)',
                                  '!profiles(&in, out)'),
        'retain-secret-after-invalid-json': ('native_wifi_erase(out, sizeof(*out));',
                                           '/* mutant: retained partially decoded password */'),
        'accept-trailing-data': ('fields == 3U && in.at == in.end', 'fields == 3U'),
        'invalid-utf8-in-metadata': ('else { raw(out, "\\\\ufffd"); ++i; }',
                                     'else { bytes(out, text + i, 1); ++i; }'),
    }
    for name, (before, after) in mutations.items():
        if original.count(before) != 1:
            raise RuntimeError('Nonunique mutation anchor: ' + name)
        directory = out / name
        directory.mkdir()
        source = directory / 'native_wifi_json.c'
        source.write_text(original.replace(before, after))
        mutant = directory / 'test'
        mutant_command = [host(source) if part == host(component / 'native_wifi_json.c')
                          else host(mutant) if part == host(binary) else part for part in command]
        (directory / 'build.log').write_bytes(run(mutant_command))
        try:
            output = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                          'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '40', host(mutant)])
        except subprocess.CalledProcessError as error:
            output = error.output
            text = output.decode(errors='replace')
            if 'Assertion' not in text or 'ERROR: AddressSanitizer' in text or 'runtime error:' in text:
                (directory / 'unexpected.log').write_bytes(output)
                raise RuntimeError('Nonsemantic failure: ' + name) from error
            (directory / 'test.log').write_bytes(output)
            controls[name] = {'rejected': True}
        else:
            (directory / 'test.log').write_bytes(output)
            raise RuntimeError('Surviving semantic control: ' + name)
    report = {'passed': True, 'source_sha256': hashes, 'result': log.decode().strip(),
              'sanitizers': ['ASan', 'UBSan'], 'semantic_controls': controls,
              'scope': 'Actual production bounded JSON decoder/metadata encoder. Complete source frozen; synthetic values only. HTTP transport, UI and persistence separately qualified.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(str(len(controls)) + ' semantic controls rejected')


if __name__ == '__main__':
    main()
