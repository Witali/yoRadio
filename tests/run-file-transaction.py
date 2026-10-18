"""Fault-inject the actual portable filesystem publication/recovery code."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'idf/components/native_storage'
OUT=ROOT/'.build/file-transaction'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    binary=OUT/'test'
    try:
        build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-clobbered',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(COMPONENT),'-I'+host(COMPONENT/'include'),
            host(ROOT/'tests/native/file_transaction_test.c'),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    except subprocess.CalledProcessError as error:
        (OUT/'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    (OUT/'build.log').write_bytes(build);(OUT/'test.log').write_bytes(log)
    sources=[Path(__file__),ROOT/'tests/native/file_transaction_test.c',COMPONENT/'file_transaction.c',
             COMPONENT/'include/file_transaction.h']
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,
        scope='Actual portable file transaction with scripted filesystem failures/power cuts; no physical flash durability claim.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__':main()
