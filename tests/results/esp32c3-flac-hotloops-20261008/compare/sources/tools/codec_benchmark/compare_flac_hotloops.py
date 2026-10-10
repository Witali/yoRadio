"""Compare exact FLAC loop experiments in alternating order on the host.

Reads a locally retained fixture manifest. Does not access or flash a board.
Host CPU timings and RV32 code size must not be called ESP32-C3 speedups.
"""
import argparse
import json
from pathlib import Path
import statistics
from profile_flac_hotloops import CORE, ROOT, host, run, sha

VARIANTS = {'scalar': [], 'rice': ['FLAC_BYTEWISE_RICE=1'],
            'lpc': ['FLAC_LPC_NO_AUTO_UNROLL=1'],
            'combined': ['FLAC_BYTEWISE_RICE=1', 'FLAC_LPC_NO_AUTO_UNROLL=1']}


def summarize(rows):
    result = []
    for name in sorted({r['name'] for r in rows}):
        cases = [r for r in rows if r['name'] == name]
        timings = {v: [r['decode_ns'] for r in cases if r['variant'] == v] for v in VARIANTS}
        medians = {v: statistics.median(t) for v, t in timings.items()}
        result.append(dict(name=name, measurements_ns=timings, median_ns=medians,
            change_percent={v: 100*(t/medians['scalar']-1) for v, t in medians.items()}))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--case', action='append', required=True)
    p.add_argument('--rounds', type=int, default=4)
    p.add_argument('--repeats', type=int, default=3)
    a = p.parse_args(); assert a.rounds >= 2 and a.repeats > 0
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    specs = json.loads((a.fixtures/'manifest.json').read_text())['fixtures']
    assert set(a.case) <= {s['name'] for s in specs}
    specs = [s for s in specs if s['name'] in a.case]
    files = [CORE, CORE.replace('.cpp', '.h'), 'tests/native/flac_bounds/Arduino.h',
             'tests/native/flac_hotloops/profile.h', 'tests/native/flac_hotloops/main.cpp',
             'tools/codec_benchmark/profile_flac_hotloops.py', Path(__file__).relative_to(ROOT).as_posix()]
    report = dict(platform='WSL x86_64 host; not ESP32-C3 timing', clock='CLOCK_THREAD_CPUTIME_ID',
        rounds=a.rounds, repeats=a.repeats, definitions=VARIANTS, sources={}, rows=[],
        compiler=run(['g++', '--version']).decode().splitlines()[0])
    source = out/'sources'
    for name in files:
        data = (ROOT/name).read_bytes(); target = source/name
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        report['sources'][name] = sha(data)
    (out/'measured_decoder.cpp').write_bytes((source/CORE).read_bytes())
    for variant, defines in VARIANTS.items():
        cmd = ['g++', '-std=c++14', '-O3', '-fno-pie', '-no-pie',
            '-DFLAC_SEGMENTED_WORKSPACE=1', '-DFLAC_OUTPUT_FRAMES=512',
            '-I'+host(source/'tests/native/flac_bounds'), '-I'+host((source/CORE).parent),
            '-I'+host(out)] + ['-D'+v for v in defines] + [
            host(source/'tests/native/flac_hotloops/main.cpp'), '-o', host(out/variant)]
        (out/(variant+'-build.log')).write_bytes(run(cmd))
    for spec in specs:
        fixture = a.fixtures/spec['file']; assert sha(fixture.read_bytes()) == spec['sha256']
        for round_index in range(a.rounds):
            # Reverse the whole order on alternate rounds, including the control.
            variants = list(VARIANTS)
            if round_index % 2: variants.reverse()
            for variant in variants:
                label = f"{spec['name']}-{round_index}-{variant}"
                pcm = out/'last.pcm'
                log = run([host(out/variant), host(fixture), host(pcm), str(a.repeats)])
                (out/(label+'.log')).write_bytes(log)
                data = pcm.read_bytes()
                assert len(data) == spec['pcm_bytes'] and sha(data) == spec['pcm_sha256'], label
                timing = next(int(line.split()[1]) for line in log.decode().splitlines()
                              if line.startswith('DECODE_NS '))
                report['rows'].append(dict(name=spec['name'], round=round_index, variant=variant,
                    decode_ns=timing, fixture_sha256=spec['sha256'], pcm_sha256=sha(data),
                    pcm_bytes=len(data), identical=True))
                (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        summary = next(row for row in summarize(report['rows']) if row['name'] == spec['name'])
        print(spec['name'], summary['change_percent'], flush=True)
    report['summary'] = summarize(report['rows']); report['passed'] = True
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
