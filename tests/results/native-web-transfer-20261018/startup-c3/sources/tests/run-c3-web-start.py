"""Qualify actual C3 web startup ownership with HTTPD/worker/TLS API seams."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('functions',ROOT/'tests/run-web-warning-regressions.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    files=[Path(__file__),ROOT/'tests/native/c3_web_start_test.c',MAIN/'web_service.c',ROOT/'tests/run-web-warning-regressions.py']
    hashes={}
    for file in files:
        destination=out/'sources'/file.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True)
        data=file.read_bytes();destination.write_bytes(data);hashes[file.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
    source=(out/'sources'/MAIN.relative_to(ROOT)/'web_service.c').read_text()
    (out/'web-start.inc').write_text(helper.function(source,'abort_static_startup')+helper.function(source,'web_service_start'))
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
        '-I'+host(out),host(out/'sources/tests/native/c3_web_start_test.c'),'-o',host(out/'test')]
    for name,args in [('build',command),('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(out/'test')])]:
        try: log=run(args)
        except subprocess.CalledProcessError as error:
            (out/(name+'.log')).write_bytes(error.output);print(error.output.decode(errors='replace'),file=sys.stderr);raise
        (out/(name+'.log')).write_bytes(log)
    (out/'report.json').write_text(json.dumps(dict(passed=True,sanitizers=['ASan','UBSan'],source_sha256=hashes,
        scope='Actual startup/abort functions; explicit HTTPD, storage, TLS and worker API seams. Live C3 listener retained on route failure because its producer has no stop API; no physical timing or TLS cryptographic qualification.'),indent=2)+'\n')
    print(log.decode(),end='')

if __name__=='__main__':main()
