"""Qualify exact shared multipart header parsing and historical receiver controls.

Compiles the portable production headers unchanged, and the actual C3 HTTP
receiver with host HTTP/time seams. No SDK, board, or network is accessed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT/'idf/esp32c3-oled-native/main'
SHARED = ROOT/'idf/components/native_storage/include'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def receiver(source):
    constants = '\n'.join(re.findall(r'^#define WEB_UPLOAD_[^\n]+', source, re.M))
    start = source.index('static bool receive_form(')
    end = source.index('\nstatic bool ', start + 1)
    return constants+'\n'+source[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', default='d13706c2')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    baseline = subprocess.check_output(['git', 'rev-parse', args.baseline], cwd=ROOT, text=True).strip()
    report = {'baseline_commit': baseline, 'negative_controls': {}, 'current': {},
              'scope': 'Production portable headers and actual C3 receive_form with HTTP/time host seams; no physical board or SDK evidence.'}
    flags = ['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
             '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']

    def compile_test(name, test, includes):
        binary = out/name
        command = flags+[item for path in includes for item in ['-I', host(path)]]+[host(test), '-o', host(binary)]
        try:
            log = run(command)
        except subprocess.CalledProcessError as error:
            (out/(name+'-build.log')).write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
        (out/(name+'-build.log')).write_bytes(log)
        return binary

    def execute(binary, name, arguments=(), negative=False):
        try:
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '30', host(binary), *arguments])
            success = True
        except subprocess.CalledProcessError as error:
            log = error.output; success = False
        (out/(name+'.log')).write_bytes(log)
        if negative:
            assert not success, name+' failed to detect historical acceptance'
            assert b'Assertion' in log, log.decode(errors='replace')
            report['negative_controls'][name] = 'DETECTED'
        else:
            assert success, log.decode(errors='replace')
            report['current'][name] = 'PASS'
            print(log.decode(), end='')

    test = ROOT/'tests/native/multipart_header_test.c'
    current = compile_test('headers', test, [MAIN])
    execute(current, 'headers')
    test = ROOT/'tests/native/multipart_header_receive_test.c'
    old = out/'baseline'; old.mkdir()
    for name in ['web_multipart.h', 'web_file_form.h', 'web_upload.c']:
        text = subprocess.check_output(['git', 'show', f'{baseline}:{(MAIN/name).relative_to(ROOT).as_posix()}'], cwd=ROOT)
        (old/name).write_bytes(text)
    (old/'receive-production.inc').write_text(receiver((old/'web_upload.c').read_text()))
    previous = compile_test('receiver-baseline', test, [old])
    for case in range(4):
        execute(previous, f'negative-receiver-{case}', [str(case)], negative=True)
    (out/'receive-production.inc').write_text(receiver((MAIN/'web_upload.c').read_text()))
    current = compile_test('receiver', test, [out, MAIN])
    for case in range(5):
        execute(current, f'receiver-{case}', [str(case)])
    # OTA now shares its bounded form/image/HTTP code with CYD. Exercise the
    # current production C3 wrapper/handler rather than the retired flash model.
    ota_runner = ROOT/'tests/run-native-ota-http.py'
    subprocess.run([sys.executable,str(ota_runner),'--target','c3','--output',str(out/'ota-current')],check=True)
    report['ota_current'] = json.loads((out/'ota-current/report.json').read_text())
    files = [Path(__file__), ROOT/'tests/native/multipart_header_test.c', test,
             ota_runner,
             MAIN/'ota_upload.c', MAIN/'ota_upload.h',
             MAIN/'web_upload.c', MAIN/'web_multipart.h', MAIN/'web_file_form.h',
             SHARED/'web_multipart.h', SHARED/'web_file_form.h']
    report['source_sha256'] = {path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    for path in files:
        snapshot = out/'sources'/path.relative_to(ROOT)
        snapshot.parent.mkdir(parents=True, exist_ok=True); snapshot.write_bytes(path.read_bytes())
    report['passed'] = True
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
