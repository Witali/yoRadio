"""Actual firmware send/finish path with continuous frame confirmation and real queue."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from native_source import canonical,source_closure

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('queue_runner',ROOT/'tests/run-adaptive-input.py')
queue_runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue_runner)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--target',choices=('c3','cyd'),default='c3')
    parser.add_argument('--corpus',type=Path)
    parser.add_argument('--tail-coalesce',action='store_true')
    parser.add_argument('--queued-consumer',action='store_true',
                        help='Allow queue backpressure instead of forcing immediate consumption after commit')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    source=ROOT/('idf/esp32c3-oled-native/main' if args.target=='c3' else 'idf/esp32-cyd2usb-native/main')
    portable=ROOT/'idf/components/native_stream'
    platform=ROOT/'tests/native/adaptive_input_test.c';test=ROOT/'tests/native/stream_start_test.c'
    prelude=platform.read_text().split('#define MALLOC_CAP_INTERNAL')[0]
    prelude=prelude.replace('/* PRODUCTION_HEADER */',queue_runner.body(portable/'include/adaptive_input.h'))
    prelude=prelude.replace('/* PRODUCTION_QUEUE */',queue_runner.body(portable/'adaptive_input.c'))
    # The queue API is already embedded with host RTOS typedefs.
    shim=out/'include';shim.mkdir()
    for name in ('stream_staging.h','stream_start.h'):
        text=(portable/'include'/name).read_text().replace('#include "adaptive_input.h"','')
        (shim/name).write_text(text)
    send=(source/'audio_service.c').read_text()
    send=send[send.index('static bool send_encoded('):send.index('static void stream_bitrate_add(') if args.target=='c3' else send.index('static bool stream_audio(')]
    unit=out/'test.c';binary=out/'test'
    unit.write_text(prelude+test.read_text().replace('/* PRODUCTION_SEND */',send))
    (out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
        *(['-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1'] if args.tail_coalesce else []),
        *(['-DTEST_QUEUED_CONSUMER=1'] if args.queued_consumer else []),
        *(['-DSTREAM_TARGET_CYD=1'] if args.target=='cyd' else []),
        '-pthread','-fsanitize=address,undefined','-fno-pie','-no-pie','-I',host(shim),
        '-I',host(source),'-I',host(portable/'include'),host(unit),'-o',host(binary)]))
    try:
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1','timeout','60',host(binary)])
    except Exception as error:
        if hasattr(error,'output'):(out/'failure.log').write_bytes(error.output);print(error.output.decode())
        raise
    (out/'run.log').write_bytes(log);assert log.startswith(b'PASS startup:')
    cases=[]
    if args.corpus:
        original=json.loads((args.corpus/'report.json').read_text());assert original['passed']
        for case in original['cases']:
            path=args.corpus/(case['name']+'.input')
            assert hashlib.sha256(path.read_bytes()).hexdigest()==case['sha256']
            result=run(['timeout','30',host(binary),host(path),str(case['discard'])])
            assert result.startswith(b'PASS startup corpus:')
            (out/(case['name']+'.log')).write_bytes(result);cases.append(case)
        for name in ('he-48000-stereo.aac','mp3-320.mp3'):
            original_case=next(c for c in original['cases'] if c['name']==name)
            clean=(args.corpus/(name+'.input')).read_bytes()
            assert hashlib.sha256(clean).hexdigest()==original_case['sha256']
            # Short AAC fixtures otherwise reach EOF before the false candidate
            # fills four slots. Repeat complete elementary frames, not padding.
            repeats=(8191+10+len(clean)-1)//len(clean)
            clean*=repeats
            data=b'\xff\xf1\x4c\x83\xff\xff\xfc'+bytes(25)+clean
            path=out/('large-prefix-'+name+'.input');path.write_bytes(data)
            try:
                result=run(['timeout','30',host(binary),host(path),'32','require-control'])
            except Exception as error:
                if hasattr(error,'output'):
                    (out/('large-prefix-'+name+'.failure.log')).write_bytes(error.output)
                    print(error.output.decode())
                raise
            assert result.count(b'CONTROL chunk=')==3 and b'PASS startup corpus:' in result
            (out/('large-prefix-'+name+'.log')).write_bytes(result)
            cases.append(dict(name='large-prefix-'+name,sha256=hashlib.sha256(data).hexdigest(),
                source_sha256=original_case['sha256'],source_repeats=repeats,required_control=True,passed=True))
        # Mid-play recovery must preserve real encoded bytes across both codec
        # changes, including the false maximum-size ADTS candidate. These are
        # transport/ownership checks; the harness does not decode PCM.
        def clean_fixture(name):
            entry=next(c for c in original['cases'] if c['name']==name)
            data=(args.corpus/(name+'.input')).read_bytes()
            assert hashlib.sha256(data).hexdigest()==entry['sha256']
            return data
        mp3=clean_fixture('mp3-320.mp3');aac=clean_fixture('he-48000-stereo.aac')
        repeats=(8191+10+len(aac)-1)//len(aac);aac*=repeats
        expected=mp3+aac+mp3
        damaged=mp3+b'\xff\xf1\x4c\x83\xff\xff\xfc'+bytes(25)+aac+b'\xff\xfb\x90\0'+bytes(28)+mp3
        input_path=out/'midstream-recovery.input';input_path.write_bytes(damaged)
        expected_path=out/'midstream-recovery.expected';expected_path.write_bytes(expected)
        result=run(['timeout','60',host(binary),host(input_path),'--expected',host(expected_path),'2'])
        (out/'midstream-recovery.log').write_bytes(result)
        cases.append(dict(name='midstream-recovery',passed=True,chunks=[1,7,2048],drains=2,
            input_sha256=hashlib.sha256(damaged).hexdigest(),replayed_sha256=hashlib.sha256(expected).hexdigest(),
            replayed_bytes=len(expected),aac_repeats=repeats))
    sources=[Path(__file__).resolve(),ROOT/'tests/run-adaptive-input.py',platform,test,
             source/'audio_service.c',source/'Kconfig.projbuild',portable/'adaptive_input.c']+[portable/'include'/name
        for name in ('adaptive_input.h',
                     'stream_start.h','stream_staging.h','stream_encoded_router.h','stream_confirm.h',
                     'stream_probe.h','stream_frames.h','stream_tags.h','audio_completion.h')]
    hashes={}
    sources=source_closure(sources)
    for path in sources:
        relative=path.relative_to(ROOT);target=out/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        hashes[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/'report.json').write_text(json.dumps(dict(passed=True,target=args.target,sources=hashes,scope=__doc__,
        corpus=cases,tail_coalesce=args.tail_coalesce,queued_consumer=args.queued_consumer,
        http_socket=False,physical_playback=False),indent=2)+'\n')
    print(log.decode(),end='');print('PASS startup corpus:',len(cases))


if __name__=='__main__':main()
