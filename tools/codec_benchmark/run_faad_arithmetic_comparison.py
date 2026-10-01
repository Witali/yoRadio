#!/usr/bin/env python3
"""Compare pristine FAAD float32/fixed PCM using WSL GCC or native Linux GCC.

This measures arithmetic-mode differences, not the additional error of packed
history. Inputs and raw PCM remain in ignored local directories.
"""
from collections import Counter
from array import array
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tarfile

from run_faad_history_comparison import ROOT, REVISION, ARCHIVE_SHA256, digest, host_path, host_command
from run_faad_ps_patch import compare_pcm

PROBE = ROOT / 'tools/codec_benchmark/faad_arithmetic_probe.c'
RECORDINGS = ('abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')


def frame_diagnostics(base, candidate, frames):
    """Keep large transients visible and assign mono/stereo boundaries exactly."""
    a, b = array('h'), array('h')
    a.frombytes(base.read_bytes()); b.frombytes(candidate.read_bytes())
    if sys.byteorder != 'little':
        a.byteswap(); b.byteswap()
    if len(a) != len(b) or not a:
        raise ValueError('PCM shape differs')
    rows, offset = [], 0
    for frame in frames:
        count, channels = frame[1], frame[3]
        if channels not in (1, 2) or count % channels or offset + count > len(a):
            raise ValueError('Invalid frame shape')
        x, y = a[offset:offset+count], b[offset:offset+count]
        deltas = [v-u for u,v in zip(x,y)]
        rows.append([count, channels, frame[5], max(map(abs,deltas),default=0),
                     sum(d*d for d in deltas), sum(deltas),
                     sum(v in (-32768,32767) for v in x), sum(v in (-32768,32767) for v in y)])
        offset += count
    if offset != len(a):
        raise ValueError('PCM length disagrees with frame trace')
    return rows


def summarize(channels):
    """Aggregate integer sums before deriving metrics; no channel averaging."""
    hist = Counter()
    for row in channels:
        hist.update({int(k): v for k, v in row['histogram'].items()})
    count = sum(hist.values())
    if not count:
        raise ValueError('Empty comparison')
    square = sum(k*k*v for k, v in hist.items())
    signal = sum(r['square_signal'] for r in channels)
    signed = sum(r['signed_error'] for r in channels)
    percentiles = {}
    for label, fraction in (('p95', .95), ('p99', .99), ('p999', .999)):
        threshold, cumulative = math.ceil(count*fraction), 0
        for error, number in sorted(hist.items()):
            cumulative += number
            if cumulative >= threshold:
                percentiles[label] = error
                break
    return dict(samples=count, maximum=max(hist), different=count-hist.get(0, 0),
                over_two=sum(v for k,v in hist.items() if k > 2),
                over_five=sum(v for k,v in hist.items() if k > 5),
                square_error=square, square_signal=signal, signed_error=signed,
                rms_lsb=math.sqrt(square/count), mean_error_lsb=signed/count,
                signal_to_difference_db=10*math.log10(signal/square) if signal and square else None,
                absolute_percentiles=percentiles,
                histogram={str(k): v for k,v in sorted(hist.items())})


def run(output, archive, recordings):
    output.mkdir(parents=True, exist_ok=True)
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError('Pinned FAAD archive differs')
    source = archive.parent / f'faad2-{REVISION}'
    # No patches and no changes to the shared reference extraction.
    with tarfile.open(archive) as bundle:
        for entry in bundle.getmembers():
            if entry.isfile() and (archive.parent / entry.name).read_bytes() != bundle.extractfile(entry).read():
                raise ValueError(f'Modified pristine FAAD source: {entry.name}')
    commands = {}

    def build(mode):
        cmd = ['gcc', '-O2', '-fno-strict-aliasing', '-ffloat-store', '-DAPPLY_DRC',
               '-DHAVE_INTTYPES_H=1', '-DHAVE_MEMCPY=1', '-DHAVE_STRING_H=1', '-DHAVE_STRINGS_H=1',
               '-DHAVE_SYS_STAT_H=1', '-DHAVE_SYS_TYPES_H=1', '-DHAVE_LRINTF=1', '-DPACKAGE_VERSION="comparison"']
        if mode == 'fixed':
            cmd += ['-DFIXED_POINT=1']
        cmd += ['-I'+host_path(source/'include'), '-I'+host_path(source/'libfaad')]
        cmd += [host_path(p) for p in sorted((source/'libfaad').glob('*.c'))]
        cmd += [host_path(PROBE), '-lm', '-o', host_path(output/mode)]
        commands[mode] = cmd
        with (output/f'build-{mode}.log').open('w') as log:
            subprocess.run(host_command(cmd), stdout=log, stderr=subprocess.STDOUT, check=True)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(build, ('float', 'fixed')))
    inputs = [(p.stem, p, 2) for p in sorted((ROOT/'tests/fixtures/aac_stream_format').glob('*.aac'))]
    inputs += [(name, recordings/f'{name}.aac', 1) for name in RECORDINGS]
    rows = []
    for name, path, repeats in inputs:
        runs = {}
        for mode in ('float', 'fixed'):
            prefix = output/f'{name}-{mode}'
            cmd = [host_path(output/mode), host_path(path), host_path(prefix), str(repeats)]
            process = subprocess.run(host_command(cmd), text=True, capture_output=True)
            (output/f'{name}-{mode}.log').write_text(process.stdout+process.stderr, encoding='utf-8', newline='\n')
            process.check_returncode()
            runs[mode] = json.loads(process.stdout)
            runs[mode].update(pcm_sha256=digest(prefix.with_suffix('.pcm')),
                              frames_sha256=digest(prefix.with_suffix('.frames')),
                              state_sha256=digest(prefix.with_suffix('.state')))
            # A fresh process/decoder must reproduce even the large transients.
            again = output/f'{name}-{mode}-repeat'
            cmd[2] = host_path(again)
            repeat = subprocess.run(host_command(cmd), text=True, capture_output=True, check=True)
            if repeat.stdout != process.stdout or repeat.stderr != process.stderr:
                raise ValueError(f'{name}/{mode}: nondeterministic decode summary')
            repeated = {kind: digest(again.with_suffix('.'+suffix))
                        for kind,suffix in (('pcm_sha256','pcm'),('frames_sha256','frames'),('state_sha256','state'))}
            if any(runs[mode][key] != value for key,value in repeated.items()):
                raise ValueError(f'{name}/{mode}: nondeterministic PCM/frame/state trace')
            runs[mode]['repeat_hashes'] = repeated
        if runs['float']['frames_sha256'] != runs['fixed']['frames_sha256']:
            raise ValueError(f'{name}: output shape/SBR/PS activation differs')
        frames = [list(map(int, line.split())) for line in (output/f'{name}-float.frames').read_text().splitlines()]
        channels = compare_pcm(output/f'{name}-float.pcm', output/f'{name}-fixed.pcm', frames)
        diagnostics = frame_diagnostics(output/f'{name}-float.pcm', output/f'{name}-fixed.pcm', frames)
        diag_path = output/f'{name}.errors.json'
        diag_path.write_text(json.dumps(diagnostics, separators=(',', ':'))+'\n', encoding='utf-8', newline='\n')
        for ch in channels:
            ch.update(mean_error_lsb=ch['signed_error']/ch['samples'],
                      signal_to_difference_db=10*math.log10(ch['square_signal']/ch['square_error'])
                      if ch['square_signal'] and ch['square_error'] else None)
        row = dict(input=name, input_sha256=digest(path), repeats=repeats, runs=runs,
                   output_layouts=sorted({(f[2], f[3]) for f in frames if f[1]}),
                   channels=channels, total=summarize(channels), frame_errors_sha256=digest(diag_path))
        rows.append(row)
        print(name, 'max', row['total']['maximum'], 'RMS', round(row['total']['rms_lsb'], 6),
              'difference dB', round(row['total']['signal_to_difference_db'], 3), flush=True)
    result = dict(source_revision=REVISION, source_archive_sha256=digest(archive),
                  probe_sha256=digest(PROBE),
                  runner_sha256=digest(Path(__file__)),
                  comparator_sha256=digest(ROOT/'tools/codec_benchmark/run_faad_ps_patch.py'),
                  compiler=subprocess.check_output(host_command(['gcc','--version']), text=True).splitlines()[0],
                  build_commands=commands, binary_sha256={m:digest(output/m) for m in ('float','fixed')},
                  reference='pristine FAAD float32, FAAD_FMT_16BIT',
                  candidate='pristine FAAD FIXED_POINT, FAAD_FMT_16BIT',
                  error_definition='fixed PCM minus float PCM; no alignment, gain matching or resampling',
                  frame_error_columns=['samples', 'channels', 'ps_active', 'maximum', 'square_error',
                                       'signed_error', 'float_at_pcm_rail', 'fixed_at_pcm_rail'],
                  state_columns=['sbr_ret', 'sbr_header_count', 'sbr_kx', 'sbr_M'],
                  note='Arithmetic baseline comparison, not packed-history error or a C3 speed benchmark', rows=rows)
    (output/'comparison.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'.build/faad-arithmetic-20261001')
    parser.add_argument('--archive', type=Path, default=ROOT/f'.build/faad2-comparison/faad2-{REVISION}.tar.gz')
    parser.add_argument('--recordings', type=Path, default=ROOT/'.build/aac-bfp16-real-20260930/inputs')
    args = parser.parse_args()
    run(args.output.resolve(), args.archive.resolve(), args.recordings.resolve())
