"""Sanitize shared ICY framing/JSON code and validate emitted JSON with Python."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.build/native-stream-body'
SHARED=ROOT/'idf/components/native_stream'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    binary=OUT/'test';corpus=OUT/'json-corpus.jsonl'
    try:
        build=run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(SHARED/'include'),host(SHARED/'icy_title.c'),
            host(ROOT/'tests/native/native_stream_body_test.c'),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(corpus)])
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    rows={}
    for line in log.decode().splitlines():
        if '=' in line:
            key,value=line.split('=',1);rows[key]=json.loads(value)
    assert rows['VALID']=='quote " slash \\ line\nПривет 🌍'
    assert rows['CONTROLS']==''.join(map(chr,range(1,32)))
    assert rows['INVALID']=='\ufffd'*7
    fuzz=[json.loads(line) for line in corpus.read_text(encoding='utf-8').splitlines()]
    assert len(fuzz)==1000 and all(isinstance(value,str) for value in fuzz)
    for value in fuzz:value.encode('utf-8',errors='strict')
    (OUT/'build.log').write_bytes(build);(OUT/'test.log').write_bytes(log)
    sources=[Path(__file__),ROOT/'tests/native/native_stream_body_test.c',SHARED/'icy_title.c',
             *[SHARED/'include'/name for name in ('icy_title.h','stream_body.h','json_buffer.h')]]
    (OUT/'report.json').write_text(json.dumps(dict(passed=True,json_fuzz_cases=1000,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print('\n'.join(line for line in log.decode().splitlines() if line.startswith('PASS')))


if __name__=='__main__':main()
