"""Check static-response session ownership under a deterministic HTTPD interleaving."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('cyd_functions',ROOT/'tests/run-cyd-lifecycle.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'idf/esp32c3-oled-native/main/web_service.c'
    test=ROOT/'tests/native/static_session_ownership_test.c'
    baseline='533ce63328fc06d1a91c0369679cc9a559ba891d'
    old=subprocess.check_output(['git','show',baseline+':'+source.relative_to(ROOT).as_posix()],cwd=ROOT).decode()
    results={}
    for name,code in [('baseline',old),('current',source.read_text(encoding='utf-8'))]:
        directory=out/name;directory.mkdir(exist_ok=True)
        (directory/'close-production.inc').write_text(helpers.function(code,'finish_static_response'),encoding='utf-8')
        binary=directory/'test'
        (directory/'build.log').write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer',
            '-fno-pie','-no-pie','-I'+host(directory),host(test),'-o',host(binary)]))
        try:
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                     'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
            passed=True
        except subprocess.CalledProcessError as error:
            log=error.output;passed=False
        (directory/'test.log').write_bytes(log)
        assert passed==(name=='current'),(name,log.decode(errors='replace'))
        results[name]='PASS' if passed else 'EXPECTED ownership failure detected'
    files=[Path(__file__),test,source,ROOT/'tests/run-cyd-lifecycle.py']
    hashes={}
    for file in files:
        relative=file.relative_to(ROOT);data=file.read_bytes()
        hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
        frozen=out/'sources'/relative;frozen.parent.mkdir(parents=True,exist_ok=True);frozen.write_bytes(data)
    (out/'report.json').write_text(json.dumps(dict(passed=True,physical_hardware=False,baseline_commit=baseline,
        scope='Actual completion helper and modeled scheduling of the documented SDK session-close callback; no target scheduler or TCP timing proof.',
        results=results,source_sha256=hashes),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results))


if __name__=='__main__':main()
