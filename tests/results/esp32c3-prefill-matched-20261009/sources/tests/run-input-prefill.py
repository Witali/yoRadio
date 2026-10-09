"""Compile the actual C3 prefill function with deterministic queue/time stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = ROOT/'idf/esp32c3-oled-native/main/audio_service.c'
    harness = ROOT/'tests/native/input_prefill_test.c'
    text = source.read_text()
    start = text.index('static bool prefill_encoded_input(')
    function = text[start:text.index('\n#endif\n\nstatic void decoder_task',start)]
    packet = re.search(r'typedef struct \{\n    uint32_t generation;\n    native_codec_t codec;.*?} encoded_packet_t;', text, re.S).group()
    poll = re.search(r'^#define INPUT_PREFILL_POLL_MS .*$', text, re.M).group()
    unit = args.output/'test.c'
    unit.write_text(harness.read_text().replace('/* PRODUCTION_PACKET_TYPE */',packet)
        .replace('/* PRODUCTION_POLL_CONSTANT */',poll)
        .replace('/* PRODUCTION_PREFILL */',function))
    report = dict(variants={}, scope='Actual prefill function with deterministic queue/time stubs; '
                  'not physical playback or full decoder-task integration')
    for source_file in (source,harness,Path(__file__).resolve()):
        dest = args.output/'sources'/source_file.relative_to(ROOT)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(source_file.read_bytes())
    report['source_sha256'] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (source,harness,Path(__file__).resolve())}
    for mode,minimum in ((mode,minimum) for mode in ('ring','adaptive') for minimum in (0,1,250,500)):
        name = mode+'-min'+str(minimum)
        binary = args.output/name
        command = ['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
                   '-fsanitize=address,undefined','-fno-pie','-no-pie']
        command += ['-DCONFIG_YORADIO_INPUT_PREFILL_MIN_MS='+str(minimum)]
        if mode=='adaptive': command += ['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1']
        (args.output/(name+'-build.log')).write_bytes(run(command+[host(unit),'-o',host(binary)]))
        log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        (args.output/(name+'.log')).write_bytes(log)
        assert log.startswith(b'PASS initial input prefill:')
        report['variants'][name] = dict(result='PASS',cases=12 if mode=='adaptive' else 10,minimum_ms=minimum)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
