"""Run actual C3 multipart/form/sink code under ASan/UBSan (GCC or WSL GCC)."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.build/c3-web-memory/host'
MAIN = ROOT/'idf/esp32c3-oled-native/main'


def native(path):
    value = str(path.resolve()).replace('\\','/')
    return '/mnt/'+value[0].lower()+value[2:] if os.name == 'nt' else value


def run(args):
    command = ['wsl.exe','--exec',*args] if os.name == 'nt' else args
    result = subprocess.run(command,capture_output=True,text=True)
    print(result.stdout,end='')
    if result.returncode:
        print(result.stderr,end='',file=sys.stderr)
        raise RuntimeError('Host check failed')
    return result.stdout+result.stderr


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    OUT=parser.parse_args().output.resolve()
    OUT.mkdir(parents=True,exist_ok=True)
    source = (MAIN/'web_upload.c').read_text()
    # Compile the production sink verbatim with mock POSIX/allocator functions.
    # Explicit anchors fail if its definition is moved or removed.
    constants = '\n'.join(re.findall(r'^#define WEB_UPLOAD_[^\n]+', source, re.M)) + '\n'
    sink = constants + source[source.index('// All three routes'):source.index('static bool receive_form(')]
    (OUT/'sink-under-test.h').write_text(sink)
    results = {}
    for name, source_path in (
        ('multipart',ROOT/'tests/native/esp8266_multipart_test.c'),
        ('form',ROOT/'tests/native/esp32c3_web_file_form_test.c'),
        ('sink',ROOT/'tests/native/esp32c3_web_upload_sink_test.c')):
        binary = OUT/(name+'-test')
        run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
             '-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-fno-pie','-no-pie',
             '-I',native(MAIN),'-I',native(OUT),native(source_path),'-o',native(binary)])
        results[name] = run([native(binary)])
    results['source_sha256'] = {name:hashlib.sha256((MAIN/name).read_bytes()).hexdigest()
        for name in ('web_multipart.h','web_file_form.h','web_upload.c')}
    (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
