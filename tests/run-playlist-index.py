"""Execute production playlist index/lookup functions on host files."""
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
from native_source import canonical,source_closure


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',choices=['c3','cyd'],default='c3')
    args=parser.parse_args()
    main=ROOT/'idf'/('esp32c3-oled-native' if args.target=='c3' else 'esp32-cyd2usb-native')/'main'
    out=ROOT/'.build'/('playlist-index-'+args.target);out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('helpers',ROOT/'tests/run-cyd-lifecycle.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    source=canonical(main/'radio_control.c').read_text()
    functions=['parse_playlist_line','next_playlist_row','load_playlist_index_locked','build_playlist_index_locked','playlist_station']
    (out/'production.inc').write_text('\n'.join(helper.function(source,name) for name in functions))
    binary=out/'test'
    try:
        build=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(out),'-I'+host(ROOT/'idf/components/native_storage'),
            '-I'+host(ROOT/'idf/components/native_storage/include'),
            host(ROOT/'tests/native/playlist_index_test.c'),
            host(ROOT/'idf/components/native_storage/file_transaction.c'),'-o',host(binary)])
        (out/'build.log').write_bytes(build)
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    except subprocess.CalledProcessError as error:
        (out/'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'),file=sys.stderr);raise
    (out/'test.log').write_bytes(log)
    sources=[Path(__file__),ROOT/'tests/run-cyd-lifecycle.py',ROOT/'tests/native/playlist_index_test.c',
             main/'radio_control.c',ROOT/'idf/components/native_storage/file_transaction.c',
             ROOT/'idf/components/native_storage/include/file_transaction.h']
    (out/'report.json').write_text(json.dumps(dict(target=args.target,passed=True,
        scope='Actual index functions, real host stdio and rename/write failure seams; no SPIFFS timing or flash durability qualification.',
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_closure(sources)}),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__': main()
