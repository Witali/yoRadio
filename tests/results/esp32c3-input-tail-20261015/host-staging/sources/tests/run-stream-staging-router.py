"""Actual queue/staging/router liveness with four held slots and a concurrent consumer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('queue_runner',ROOT/'tests/run-adaptive-input.py')
queue_runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue_runner)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tail-coalesce',action='store_true')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'idf/esp32c3-oled-native/main'
    platform=ROOT/'tests/native/adaptive_input_test.c'
    test=ROOT/'tests/native/stream_staging_router_test.c'
    prelude=platform.read_text().split('#define MALLOC_CAP_INTERNAL')[0]
    prelude=prelude.replace('/* PRODUCTION_HEADER */',queue_runner.body(source/'adaptive_input.h'))
    prelude=prelude.replace('/* PRODUCTION_QUEUE */',queue_runner.body(source/'adaptive_input.c'))
    unit=out/'test.c';binary=out/'test'
    unit.write_text(prelude+test.read_text().replace('/* STAGING_HEADER */',queue_runner.body(source/'stream_staging.h')))
    (out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
        '-Wno-unused-function','-pthread','-fsanitize=address,undefined','-fno-pie','-no-pie',
        *(['-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1'] if args.tail_coalesce else []),
        '-I',host(source),host(unit),'-o',host(binary)]))
    try:
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
    except Exception as error:
        if hasattr(error,'output'):(out/'failure.log').write_bytes(error.output);print(error.output.decode())
        raise
    (out/'run.log').write_bytes(log);assert log.startswith(b'PASS staging router:')
    sources=[Path(__file__).resolve(),ROOT/'tests/run-adaptive-input.py',platform,test]+[source/name
        for name in ('adaptive_input.h','adaptive_input.c','stream_staging.h','stream_encoded_router.h',
                     'stream_confirm.h','stream_probe.h','stream_frames.h','stream_tags.h','audio_completion.h')]
    hashes={}
    for path in sources:
        relative=path.relative_to(ROOT);target=out/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        hashes[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/'report.json').write_text(json.dumps(dict(passed=True,sources=hashes,scope=__doc__,
        chunks=[1,7,2048],tail_coalesce=args.tail_coalesce,cancellation=True,http_integration=False,physical_playback=False),indent=2)+'\n')
    print(log.decode(),end='')


if __name__=='__main__':main()
