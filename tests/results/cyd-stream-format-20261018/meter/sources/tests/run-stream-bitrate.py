"""Portable audio-throughput meter with real shared header and sanitizer checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    case=ROOT/'tests/native/stream_bitrate_test.c'
    include=ROOT/'idf/components/native_stream/include'
    binary=out/'test'
    try:
        build=run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(include),host(case),'-o',host(binary)])
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    except subprocess.CalledProcessError as error:
        (out/'failure.log').write_bytes(error.output);print(error.output.decode(),file=sys.stderr);raise
    (out/'build.log').write_bytes(build);(out/'run.log').write_bytes(log)
    files=[Path(__file__).resolve(),case,include/'stream_bitrate.h']
    hashes={}
    for path in files:
        relative=path.relative_to(ROOT);target=out/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        hashes[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/'report.json').write_text(json.dumps(dict(passed=True,sources=hashes,
        compiler=run(['gcc','--version']).decode().splitlines()[0],physical_hardware=False),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__':main()
