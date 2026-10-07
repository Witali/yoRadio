#!/usr/bin/env python3
"""Cumulative PCM evidence and an explicit SBR/PS union storage model."""
import argparse
import json
import math
from pathlib import Path
import run_aac_combined_storage as experiment
import run_aac_bfp16 as common
from aac_precision import PRODUCTION_LIMIT

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')
# Compiler-checked original RV32 ABI: aac_sbr_abi.h.
ORIGINAL_OWNER = 55128
COMPACT_CHANNEL = 24848
SYNTHESIS_OFFSET = 0x42c0
PS_MANTISSA_OFFSET = 0x1664
PS_CONTROL_OFFSET = 0x93b4 - 25792
PS_CONTROL_SIZE = 3536
OWNER_TAIL = 12
LOSSLESS_REQUEST_SAVING = 5420


def packed(pairs, bits):
    entries = 8 if bits == 16 else 4
    return 4*(pairs+(pairs+entries-1)//entries)


def memory_model(variant):
    """Persistent bytes before extra access windows/cache/allocator rounding.

    The right channel must fit BOTH full stereo SBR and the PS overlay. Smaller
    PS arrays release capacity within that same union, not a separate allocation.
    These are design estimates, not sizes allocated by the numerical probe.
    """
    mask = experiment.MASKS[variant] if variant not in (0, 8) else 0
    enabled = lambda area: bool(mask & (1 << area))
    bits = lambda area: 16 if (variant in (11, 12) or variant == 13 and area in (1, 4, 9) or
                               variant in (9, 10) and area == 9) else 18
    ps_bits = 16 if variant >= 10 else 18
    low = 2*40*(32*8-packed(32, bits(9))) if enabled(9) else 0
    high = 2*6*(48*8-packed(48, bits(1))) if enabled(1) else 0
    mantissa = 2*2*5*(64*4-packed(32, bits(4))) if enabled(4) else 0
    exponent = 2*2*5*64*2 if enabled(5) else 0
    hybrid = 3*(12*8-packed(12, bits(2))) if enabled(2) else 0
    previous = 4*(22*4-packed(11, bits(6))) if enabled(6) else 0
    output = 10*8-packed(10, bits(7)) if enabled(7) else 0
    energy = 3*(20*4-packed(10, bits(8))) if enabled(8) else 0
    ps = 617*8-packed(617, ps_bits) if enabled(10) else 0
    sbr_saving = low+high+mantissa+exponent
    left = COMPACT_CHANNEL-sbr_saving//2
    synthesis = SYNTHESIS_OFFSET-(low+high)//2
    suffix = COMPACT_CHANNEL-SYNTHESIS_OFFSET-(mantissa+exponent)//2
    if enabled(10):
        ps_end = PS_MANTISSA_OFFSET-hybrid-output-energy+packed(617, ps_bits)+PS_CONTROL_SIZE-previous
    else:
        ps_end = PS_CONTROL_OFFSET-hybrid-output-energy+PS_CONTROL_SIZE-previous
    overlap_padding = max(0, ps_end-synthesis)
    right = max(synthesis, ps_end)+suffix
    owner = left+right+OWNER_TAIL
    areas = dict(low_qmf=low, high_qmf=high, smoothing_mantissas=mantissa,
                 smoothing_exponents=exponent, ps_delays=ps, hybrid_history=hybrid,
                 previous_mix=previous, hybrid_output=output, ps_energy=energy)
    return dict(original_owner_bytes=ORIGINAL_OWNER, estimated_owner_bytes=owner,
        estimated_persistent_saving_bytes=ORIGINAL_OWNER-owner,
        estimated_persistent_saving_percent=100*(ORIGINAL_OWNER-owner)/ORIGINAL_OWNER,
        lossless_layout_request_saving_bytes=LOSSLESS_REQUEST_SAVING,
        logical_payload_savings=areas, naive_sum_bytes=LOSSLESS_REQUEST_SAVING+sum(areas.values()),
        left_channel_bytes=left, right_channel_bytes=right, ps_end_bytes=ps_end,
        synthesis_offset_bytes=synthesis, right_channel_extra_for_ps_bytes=overlap_padding,
        extra_unpack_workspace_bytes=None, extra_cache_bytes=None,
        measured_combined_heap_saving_bytes=0,
        qualification='Persistent-layout estimate only; all readers, scratch reuse and allocator rounding still require integration.')


def summarize(directory):
    results, hashes = [], {}
    for name in NAMES:
        p = directory/name
        saved = json.loads((p/'result.json').read_text())
        parsed = experiment.parse_log((p/'qemu.log').read_text())
        if any(saved[k] != v for k, v in parsed.items()):
            raise ValueError('Saved result differs from log: '+name)
        if common.sha256(p/'qemu.log') != saved['provenance']['qemu_log_sha256']:
            raise ValueError('Changed raw log: '+name)
        for f in ('result.json', 'qemu.log'):
            hashes[name+'/'+f] = common.sha256(p/f)
        results.append(saved)
    rows = []
    for v, name in experiment.VARIANTS.items():
        runs = [r for d in results for r in d['runs'] if r['variant'] == v]
        maximum = max(max(r['max_l'], r['max_r']) for r in runs)
        stats = [s for d in results for s in d.get('error_statistics', [])
                 if s['variant'] == v and s['run'] == 1]
        # This aggregate explicitly includes all five real captures, even where
        # a particular SBR/PS probe is inactive. Per-recording detail is retained.
        samples = sum(s['samples'] for s in stats)
        square_sum = sum(s['square_sum'] for s in stats)
        summaries = [s for d in results for s in d['summaries'] if s['variant'] == v]
        work = [s['instruction_overhead_median_percent'] for s in summaries]
        rows.append(dict(variant=v, name=name, paired_comparisons=len(runs),
            max_pcm_error_lsb=maximum, production_precision_pass=maximum <= PRODUCTION_LIMIT,
            real_samples_including_inactive_paths=samples,
            real_rms_error_lsb=math.sqrt(square_sum/samples),
            instruction_overhead_percent_range=[min(work), max(work)],
            per_recording=[dict(input=n, max_pcm_error_lsb=max(max(r['max_l'],r['max_r'])
                for r in d['runs'] if r['variant']==v)) for n,d in zip(NAMES,results)],
            memory=memory_model(v), production_qualified=False))
    candidates = [r for r in rows if r['production_precision_pass'] and r['variant'] not in (0,8)
                  and experiment.MASKS[r['variant']] == experiment.ALL]
    best = max(candidates, key=lambda r:r['memory']['estimated_persistent_saving_bytes'])
    return dict(production_precision_limit_lsb=PRODUCTION_LIMIT, rows=rows, evidence_sha256=hashes,
        selected_by_persistent_bytes_variant=best['variant'],
        measured_combined_heap_saving_bytes=0,
        note='Corpus precision and persistent-size model; not a production promotion or measured combined RAM reduction.')


def table(result):
    lines = ['# Combined AAC storage: measured fidelity and estimated persistent bytes', '',
        'The maxima include synthetic and real inputs. RMS includes all five real',
        'captures, including inactive paths. Instruction costs include test probes.',
        'Every combined numerical run retains the original owner allocation: **0 bytes',
        'of measured heap saving**. Estimates below include the separately verified',
        'lossless layout and the right-channel PS/SBR union, before additional',
        'unpack/cache workspace and allocator rounding.', '',
        '| Variant | Max PCM error, LSB | +/-3 gate | Real RMS, LSB | Extra QEMU instructions | Estimated SBR owner | Estimated saving |',
        '| --- | ---: | --- | ---: | --- | ---: | ---: |']
    for row in result['rows']:
        lo, hi = row['instruction_overhead_percent_range']
        memory = row['memory']
        lines.append(f"| {row['variant']}: {row['name']} | {row['max_pcm_error_lsb']} | "
            f"{'PASS' if row['production_precision_pass'] else 'FAIL'} | {row['real_rms_error_lsb']:.8f} | "
            f"{lo:+.3f}% to {hi:+.3f}% | {memory['estimated_owner_bytes']:,} B | "
            f"{memory['estimated_persistent_saving_bytes']:,} B |")
    lines += ['', 'Variants 0 and 8 are numerical controls; their memory column only',
        'shows the independent lossless-layout estimate. They do not allocate it.', '',
        '## Largest passing complete combination', '']
    best = next(r for r in result['rows'] if r['variant']==result['selected_by_persistent_bytes_variant'])
    memory = best['memory']
    lines += [f"Variant **{best['variant']}: {best['name']}**: maximum **{best['max_pcm_error_lsb']} LSB**;",
        f"persistent-layout estimate **{memory['estimated_persistent_saving_bytes']:,} B** "
        f"(**{memory['estimated_persistent_saving_percent']:.2f}%** of the original SBR owner).", '',
        '| Logical area | Separate payload saving |', '| --- | ---: |']
    for name, value in memory['logical_payload_savings'].items():
        lines.append(f'| {name} | {value:,} B |')
    lines += ['', 'The rows above overlap in physical memory. Do not add them to the',
        'lossless-layout saving. The persistent model uses the maximum of SBR and PS',
        'space on the right channel and preserves the synthesis suffix.', '',
        'Passing the retained corpus does not establish a bound for all AAC inputs',
        'or qualify the frame-boundary probes as compact storage for every consumer.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.results)
    (args.results/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    (args.results/'TABLES.md').write_text(table(result),encoding='utf-8',newline='\n')
    for row in result['rows']:
        print(row['variant'], row['name'], row['max_pcm_error_lsb'],
              row['production_precision_pass'], row['memory']['estimated_persistent_saving_bytes'])
