"""Observe predictor orders in actual FLAC subframes and verify exact PCM.

Build a host-only copy of the production core with two stderr observation hooks.
The firmware is not changed. This measures bitstream choices, not ESP32 timing.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from run_output_dma_host import ROOT, host, run


def digest(data):
    return hashlib.sha256(data).hexdigest()


def summarize_trace(text):
    frames, predictions = [], []
    for line in text.splitlines():
        if line.startswith('RADIO_FRAME '):
            frames.append({k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)', line)})
        elif line.startswith('RADIO_LPC '):
            predictions.append({k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)', line)})
    if not frames:
        raise ValueError('No subframe observations')
    weights = Counter()
    for frame in frames:
        kind = frame['type']
        order = kind - 31 if kind >= 32 else kind-8 if 8 <= kind <= 12 else 0
        weights[order] += frame['block']
    total = sum(weights.values())
    lpc = [f for f in frames if f['type'] >= 32]
    if len(lpc) != len(predictions):
        raise ValueError('Missing/extra LPC observations')
    lpc_samples = sum(f['block'] for f in lpc)
    return dict(subframes=len(frames), lpc_subframes=len(lpc), channel_samples=total,
        lpc_channel_samples=lpc_samples, order_channel_samples=dict(sorted(weights.items())),
        mean_order_all_channel_samples=sum(k*v for k,v in weights.items())/total,
        lpc32_percent_all=100*weights[32]/total,
        above12_percent_all=100*sum(v for k,v in weights.items() if k>12)/total,
        lpc32_percent_lpc=100*weights[32]/lpc_samples if lpc_samples else 0,
        max_order=max(weights),
        mean_nonzero_lpc_taps=sum(p['nonzero']*p['block'] for p in predictions)/lpc_samples if lpc_samples else 0,
        rolling_eligible_percent_lpc=100*sum(p['block'] for p in predictions if p['rolling'])/lpc_samples if lpc_samples else 0)


def instrument(source):
    subframe = '    sampleDepth -= shift;'
    lpc = '    ret = decodeResiduals(lpcOrder, ch);'
    if source.count(subframe) != 1 or source.count(lpc) != 1:
        raise ValueError('Production observation anchors changed')
    source = '#include <cstdio>\n' + source.replace(subframe, subframe + r'''
    std::fprintf(stderr, "RADIO_FRAME ch=%u block=%u type=%u depth=%u\n",
                 ch, m_blockSize, type, sampleDepth);
''')
    return source.replace(lpc, r'''
    {
        unsigned active = coefficientCount, nonzero = 0;
        while(active && coefs[active - 1] == 0) --active;
        unsigned positive = 0, negative = 0;
        for(unsigned j = 0; j < active; ++j) {
            nonzero += coefs[j] != 0;
            if(j) {
                positive += coefs[j] != coefs[j-1];
                negative += coefs[j] != -coefs[j-1];
            }
        }
        unsigned deltas = std::min(positive, negative);
        bool rolling = active >= 8 && deltas <= 4 && (deltas + 2) * 2 <= active;
        std::fprintf(stderr, "RADIO_LPC ch=%u block=%u order=%u active=%u nonzero=%u precision=%u shift=%u rolling=%u\n",
                     ch, m_blockSize, coefficientCount, active, nonzero, precision, shift, unsigned(rolling));
    }
''' + lpc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((args.fixtures/'manifest.json').read_text())
    core = ROOT/'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'
    header = core.with_suffix('.h')
    test = ROOT/'tests/native/flac_bounds'
    files = [core, header, test/'Arduino.h', test/'main.cpp', Path(__file__)]
    report = dict(sources={}, cases=[], instrumentation='host stderr only; firmware unchanged', sanitizers=True)
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        target = out/'sources'/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes()); report['sources'][name] = digest(path.read_bytes())
    observed = out/'observed.cpp'; observed.write_text(instrument(core.read_text()))
    report['observed_source_sha256'] = digest(observed.read_bytes())
    binary = out/'observe'
    flags = ['g++','-std=c++14','-O2','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',
             '-DFLAC_OUTPUT_FRAMES=512','-DFLAC_SEGMENTED_WORKSPACE=1',
             '-I'+host(test),'-I'+host(core.parent),host(observed),host(test/'main.cpp'),'-o',host(binary)]
    (out/'build.log').write_bytes(run(flags))
    for spec in manifest['fixtures']:
        path = args.fixtures/spec['file']
        if digest(path.read_bytes()) != spec['sha256']:
            raise ValueError('Fixture hash changed')
        pcm = out/(spec['name']+'.pcm')
        log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(path),'full',host(pcm)])
        (out/(spec['name']+'.log')).write_bytes(log)
        data = pcm.read_bytes()
        if len(data) != spec['pcm_bytes'] or digest(data) != spec['pcm_sha256']:
            raise ValueError('Actual decoder PCM differs from known source / FFmpeg')
        stats = summarize_trace(log.decode())
        if stats['max_order'] > spec['max_lpc_order']:
            raise ValueError('Encoder exceeded requested LPC limit')
        if stats['channel_samples'] != spec['pcm_bytes']//2:
            raise ValueError('Subframe coverage differs from decoded PCM length')
        report['cases'].append(dict(name=spec['name'], fixture_sha256=spec['sha256'],
            pcm_sha256=digest(data), pcm_bytes=len(data), passed=True, **stats))
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(spec['name'], 'order32', round(stats['lpc32_percent_all'],2),
              'mean order', round(stats['mean_order_all_channel_samples'],2), flush=True)
    report['passed'] = all(c['passed'] for c in report['cases'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
