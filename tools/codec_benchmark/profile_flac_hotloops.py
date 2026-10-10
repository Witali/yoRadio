"""Locate FLAC hot loops using exclusive host thread CPU time and exact PCM.

No network, board access or media retention. Broadcast files remain local.
Clock probes are per block/subframe, never per bit, sample or predictor tap.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_output_dma_host import ROOT, host, run

CORE = 'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
STAGES = {
    'int8_t FLACDecode(uint8_t *inbuf, int *bytesLeft, short *outbuf){': 'frame',
    'int8_t decodeSubframes(){': 'stereo',
    'int8_t decodeSubframe(uint8_t sampleDepth, uint8_t ch) {': 'subframe',
    'int8_t decodeResiduals(uint8_t warmup, uint8_t ch) {': 'residual',
    'void restoreLinearPrediction(uint8_t ch, uint8_t shift) {': 'prediction',
}


def instrument(source):
    for signature, stage in STAGES.items():
        assert source.count(signature) == 1, signature
        source = source.replace(signature, signature +
            '\n    flac_profile::Scope scope(flac_profile::' + stage + ');')
    return source


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--case', action='append')
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--revision', help='Read an earlier core without modifying the checkout')
    p.add_argument('--define', action='append', default=[], help='Decoder experiment compiler definition')
    a = p.parse_args()
    assert a.repeats > 0
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((a.fixtures/'manifest.json').read_text())
    specs = manifest['fixtures']
    if a.case:
        assert set(a.case) <= {s['name'] for s in specs}
        specs = [s for s in specs if s['name'] in a.case]
    files = [CORE, CORE.replace('.cpp', '.h'), 'tests/native/flac_bounds/Arduino.h',
             'tests/native/flac_hotloops/profile.h', 'tests/native/flac_hotloops/main.cpp',
             Path(__file__).relative_to(ROOT).as_posix()]
    report = dict(platform='WSL x86_64 host; not ESP32-C3 timing', clock='CLOCK_THREAD_CPUTIME_ID',
                  revision=a.revision, repeats=a.repeats, defines=a.define, sources={}, cases=[],
                  compiler=run(['g++', '--version']).decode().splitlines()[0])
    for name in files:
        data = subprocess.check_output(['git', 'show', a.revision+':'+name], cwd=ROOT) \
            if a.revision and name.startswith('yoRadio/') else (ROOT/name).read_bytes()
        target = out/'sources'/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data); report['sources'][name] = sha(data)
    source = out/'sources'
    core = (source/CORE).read_text()
    for variant in ('plain', 'profile'):
        folder = out/variant; folder.mkdir()
        measured = instrument(core) if variant == 'profile' else core
        (folder/'measured_decoder.cpp').write_text(measured)
        cmd = ['g++', '-std=c++14', '-O3', '-fno-pie', '-no-pie',
               '-DFLAC_SEGMENTED_WORKSPACE=1', '-DFLAC_OUTPUT_FRAMES=512',
               '-I'+host(source/'tests/native/flac_bounds'), '-I'+host((source/CORE).parent),
               '-I'+host(folder)] + ['-D'+v for v in a.define] + [
               host(source/'tests/native/flac_hotloops/main.cpp'), '-o', host(folder/'decode')]
        (folder/'build.log').write_bytes(run(cmd))
    for spec in specs:
        fixture = a.fixtures/spec['file']
        assert sha(fixture.read_bytes()) == spec['sha256']
        case = dict(name=spec['name'], fixture_sha256=spec['sha256'], variants={})
        for variant in ('plain', 'profile'):
            folder = out/variant; pcm = folder/(spec['name']+'.pcm')
            log = run([host(folder/'decode'), host(fixture), host(pcm), str(a.repeats)])
            (folder/(spec['name']+'.log')).write_bytes(log)
            data = pcm.read_bytes()
            assert len(data) == spec['pcm_bytes'] and sha(data) == spec['pcm_sha256'], spec['name']
            lines = [line.split() for line in log.decode().splitlines()]
            timing = next(int(row[1]) for row in lines if row[0] == 'DECODE_NS')
            stages = {r[1]: dict(cpu_ns=int(r[2]), calls=int(r[3])) for r in lines if r[0] == 'STAGE'}
            case['variants'][variant] = dict(decode_ns=timing, stages=stages,
                pcm_sha256=sha(data), pcm_bytes=len(data), identical=True)
        report['cases'].append(case)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(spec['name'], case['variants']['profile']['stages'], flush=True)
    report['passed'] = True
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
