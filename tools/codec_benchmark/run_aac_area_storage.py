#!/usr/bin/env python3
"""Probe separate AAC state areas; original allocations and DSP stay unchanged."""
import statistics
import sys
import run_aac_bfp16 as common
from run_aac_pc16_write import records, key

AREAS = {1: 'high_qmf_history', 2: 'hybrid_history', 3: 'imdct_overlap',
         4: 'smoothing_mantissas', 5: 'smoothing_exponents_int16',
         6: 'previous_mix', 7: 'hybrid_analysis_output', 8: 'ps_energy_history'}
VARIANTS = AREAS | {9: 'exact_traversal', 0: 'binary_bypass'}
LABEL = 'AREASTORAGE'


def parse_log(log):
    for marker in (LABEL+'_ARITHMETIC_PASS format=shared18_four probes=8 control=9',
                   LABEL+'_COUNTER_PASS nop1024=1025', LABEL+'_EXPERIMENT_COMPLETE',
                   'QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS', 'QEMU_OLED_PASS', 'QEMU_AUDIO_PASS'):
        if marker not in log:
            raise ValueError('Missing completion marker: '+marker)
    headers = records(log, 'EXTERNAL', LABEL)
    if len(headers) > 1:
        raise ValueError('Duplicate external input')
    external = headers[0] if headers else None
    cases = ('external',) if external else common.CASES
    expected = {(c, v, r) for c in cases for v in VARIANTS for r in (1, 2, 3)}
    rows = records(log, 'RESULT', LABEL)
    area_rows = records(log, 'AREA', LABEL)
    windows = records(log, 'WINDOWS', LABEL)
    for table in (rows, windows):
        if len(table) != len(expected) or {key(r) for r in table} != expected:
            raise ValueError('Missing/duplicate result or window coverage')
    if (len(area_rows) != len(expected)*len(AREAS) or
            {(key(r), r['area']) for r in area_rows} != {(k, a) for k in expected for a in AREAS}):
        raise ValueError('Missing/duplicate area coverage')
    by_area = {(key(r), r['area']): r for r in area_rows}
    by_window = {key(r): r for r in windows}
    pairs_per_call = {1: 48, 2: 12, 3: 512, 4: 32, 5: 32, 6: 11, 7: 10, 8: 10}
    for row in rows:
        v, k = row['variant'], key(row)
        maximum = max(row['max_l'], row['max_r'])
        counts = [row[f] for f in ('different', 'over_one', 'over_two', 'over_limit')]
        if (row['samples'] <= 0 or row['frames'] <= 10 or min(row['ref_work'], row['packed_work']) <= 0 or
                counts != sorted(counts, reverse=True) or min(counts) < 0 or counts[0] > row['samples']):
            raise ValueError('Invalid PCM counts/work')
        for threshold, count in zip((0, 1, 2, 5), counts):
            if bool(maximum > threshold) != bool(count):
                raise ValueError('PCM maximum contradicts counters')
        if row['precision'] != ('FAIL' if row['over_limit'] else 'PASS'):
            raise ValueError('Invalid PCM verdict')
        areas = [by_area[(k, a)] for a in AREAS]
        if (sum(a['calls'] for a in areas) != row['complex_rows'] or
                sum(a['changed'] for a in areas) != row['changed_qmf'] or
                max(a['max_shift'] for a in areas) != row['max_shift'] or row['real_rows']):
            raise ValueError('Area totals differ from paired result')
        for a in areas:
            if (a['pairs'] != pairs_per_call[a['area']]*a['calls'] or
                    not 0 <= a['changed'] <= 2*a['pairs'] or not 0 <= a['max_shift'] <= 14 or
                    not 0 <= a['saturated'] <= 2*a['pairs'] or not 0 <= a['nonzero'] <= 2*a['pairs']):
                raise ValueError('Invalid area counters')
            if a['calls'] and v not in (a['area'], 9):
                raise ValueError('Probe touched unrelated area')
            if not a['calls'] and any(a[f] for f in ('changed', 'saturated', 'nonzero', 'minimum', 'maximum', 'max_shift', 'out_of_int16')):
                raise ValueError('Inactive area produced data')
            if row['run'] == 1 and a['calls'] and a['minimum'] > a['maximum']:
                raise ValueError('Invalid observed range')
            if (v == 9 or a['area'] == 5) and (a['changed'] or a['saturated'] or a['max_shift']):
                raise ValueError('Lossless probe changed values')
        w = by_window[k]
        overlap = by_area[(k, 3)]
        if (not 0 <= w['mask'] <= 15 or w['transform1']+w['transform2'] != overlap['calls'] or
                bool(w['mask']) != bool(overlap['calls'])):
            raise ValueError('Invalid transform coverage')
        if v in (0, 5, 9) and (row['different'] or row['changed_qmf']):
            raise ValueError('Lossless control changed PCM')
        if not row['complex_rows'] and row['different']:
            raise ValueError('Inactive probe changed PCM')
        # LC also exercises overlap; no false LC pass from an SBR-only matrix.
        if v in (3, 9) and not overlap['calls']:
            raise ValueError('Missing IMDCT hook')
        if not external:
            must_run = (v in (1, 4, 5) and row['case'].startswith('he') or
                        v in (2, 6, 7, 8) and row['case'].startswith('hev2'))
            if must_run and not row['complex_rows']:
                raise ValueError('Required synthetic probe missing')
    summaries = []
    for case in cases:
        for v, name in VARIANTS.items():
            group = [r for r in rows if r['case'] == case and r['variant'] == v]
            for f in ('samples', 'frames', 'max_l', 'max_r', 'different', 'over_one', 'over_two', 'over_limit', 'changed_qmf'):
                if len({r[f] for r in group}) != 1:
                    raise ValueError('Nondeterministic PCM or quantization')
            a = [by_area[(key(group[0]), area)] for area in AREAS]
            summaries.append(dict(case=case, variant=v, name=name,
                max_pcm_error_lsb=max(group[0]['max_l'], group[0]['max_r']),
                samples_per_run=group[0]['samples'], over_two_per_run=group[0]['over_two'],
                over_limit_per_run=group[0]['over_limit'],
                coverage='exercised' if group[0]['complex_rows'] else 'not_exercised',
                saturations=sum(r['saturated'] for r in a), out_of_int16=sum(r['out_of_int16'] for r in a),
                instruction_overhead_median_percent=round(statistics.median(
                    100*(r['packed_work']/r['ref_work']-1) for r in group if r['run'] != 1), 3)))
    result = dict(experiment='isolated_aac_array_storage18', precision_limit_lsb=5,
        precision_pass=all(not r['over_limit'] for r in rows), production_precision_limit_lsb=2,
        production_precision_pass=all(not r['over_two'] for r in rows), ram_saved_bytes=0,
        exponent_int16_range_pass=all(not a['out_of_int16'] for a in area_rows),
        timing_unit='QEMU guest instructions including probe; runs 2/3, not hardware time',
        summaries=summaries, runs=rows, areas=area_rows, windows=windows)
    if external:
        normalized = log.replace(LABEL+'_', 'BFP16_').replace('variant=', 'bands=')
        stats = common.parse_statistics(normalized, [dict(r, bands=r['variant']) for r in rows], external)
        for s in stats:
            s['variant'] = s.pop('bands')
            for threshold, field in ((2, 'over_two'), (5, 'over_limit')):
                if s[field] != s['samples']-sum(s['histogram'].get(str(k), 0) for k in range(threshold+1)):
                    raise ValueError('Histogram contradicts precision counts')
        for r in rows:
            channels = [s for s in stats if (s['variant'], s['run']) == (r['variant'], r['run'])]
            for field in ('over_two', 'over_limit'):
                if sum(s[field] for s in channels) != r[field]:
                    raise ValueError('Channel precision counts disagree')
        result.update(external=external, error_statistics=stats)
    return result


if __name__ == '__main__':
    args = common.make_parser(__doc__, 'area-storage').parse_args()
    sys.exit(common.run(args, log_parser=parse_log, config_key='YORADIO_QEMU_AAC_AREA_STORAGE_TEST', axis='variant'))
