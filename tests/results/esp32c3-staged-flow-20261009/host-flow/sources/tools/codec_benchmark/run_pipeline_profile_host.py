"""Compile the real queue wrappers, both diagnostic and production paths."""
import argparse
import hashlib
import json
from pathlib import Path
from run_output_dma_host import ROOT, host, run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    main = ROOT/'idf/esp32c3-oled-native/main'
    test = ROOT/'tests/native/pipeline_profile'
    sources = [main/'pipeline_profile.h', main/'pipeline_wait.h', main/'audio_service.c', Path(__file__)]
    sources += [f for f in test.rglob('*') if f.is_file()]
    report = dict(sources={}, variants={})
    for source in sources:
        name = source.relative_to(ROOT)
        target = args.output/'sources'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        report['sources'][name.as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    for enabled in (False, True):
        name = 'enabled' if enabled else 'disabled'
        binary = args.output/name
        command = ['gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
            '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
            '-I'+host(test), '-I'+host(main)]
        if enabled:
            command += ['-DCONFIG_YORADIO_PIPELINE_PROFILE=1']
        (args.output/(name+'-build.log')).write_bytes(run(command+[host(test/'main.c'), '-o', host(binary)]))
        log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        (args.output/(name+'.log')).write_bytes(log)
        report['variants'][name] = 'PASS'
    # Compile the exact staged/direct reporting code with deterministic clocks.
    # Queue/PCM ownership and scheduler behavior are outside this host test.
    service = (main/'audio_service.c').read_text()
    begin = service.index('typedef struct {\n    int64_t start_us;\n    pipeline_wait_t empty, submit;')
    finish = service.index('static void output_task(', begin)
    body = service[begin:finish].rsplit('#endif', 1)[0]
    for direct in (False, True):
        name = 'flow-direct' if direct else 'flow-staged'
        unit, binary = args.output/(name+'.c'), args.output/name
        unit.write_text('#include "output_flow_stubs.h"\n'+body+'\n#include "output_flow.c"\n')
        command = ['gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
            '-Wno-unused-function', '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
            '-I'+host(test), '-I'+host(main)]
        if direct:
            command += ['-DCONFIG_YORADIO_DIRECT_DMA_PCM=1']
        (args.output/(name+'-build.log')).write_bytes(run(command+[host(unit), '-o', host(binary)]))
        (args.output/(name+'.log')).write_bytes(run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1', host(binary)]))
        report['variants'][name] = 'PASS'
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['variants']))


if __name__ == '__main__':
    main()
