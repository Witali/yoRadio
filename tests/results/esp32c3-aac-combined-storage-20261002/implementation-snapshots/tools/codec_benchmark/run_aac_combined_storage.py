#!/usr/bin/env python3
"""Compare cumulative AAC compression with unchanged native owner allocations."""
import statistics
import sys
import aac_precision
import run_aac_bfp16 as common
from run_aac_pc16_write import records, key
from run_aac_area_storage import AREAS as ORIGINAL_AREAS

AREAS = ORIGINAL_AREAS | {9: 'low_qmf_analysis'}
VARIANTS = {1: 'all_compatible', 2: 'bulk_qmf_smoothing_ps', 3: 'low_qmf_and_ps',
            4: 'qmf_and_smoothing', 5: 'qmf_and_exact_exponents',
            6: 'low_qmf_only', 7: 'ps_only', 8: 'exact_traversal', 0: 'binary_bypass', 9: 'all_low_qmf16',
            10: 'all_low_qmf16_ps16', 11: 'all_shared16', 12: 'bulk_shared16', 13: 'all_bulk16_small18'}
ALL = sum(1 << area for area in (1, 2, 4, 5, 6, 7, 8, 9, 10))
BULK = sum(1 << area for area in (1, 4, 5, 9, 10))
MASKS = {0: 0, 1: ALL, 2: BULK, 3: (1 << 9) | (1 << 10),
         4: BULK & ~(1 << 10), 5: (1 << 1) | (1 << 5) | (1 << 9),
         6: 1 << 9, 7: 1 << 10, 8: ALL, 9: ALL, 10: ALL, 11: ALL, 12: BULK, 13: ALL}
LABEL = 'AACCOMBINED'


def parse_log(log):
    limits = aac_precision.log_limits(log, LABEL)
    for marker in (LABEL+'_ARITHMETIC_PASS formats=shared18_four,shared16 variants=14 control=8',
                   'PSSTORAGE_ARITHMETIC_PASS pairs=100000 storage control',
                   LABEL+'_COUNTER_PASS nop1024=1025', LABEL+'_EXPERIMENT_COMPLETE',
                   'QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS', 'QEMU_OLED_PASS', 'QEMU_AUDIO_PASS'):
        if marker not in log:
            raise ValueError('Missing completion marker: '+marker)
    headers = records(log, 'EXTERNAL', LABEL)
    if len(headers) > 1:
        raise ValueError('Duplicate external input')
    external = headers[0] if headers else None
    cases = ('external',) if external else common.CASES
    # The shared harness uses the all-enabled variant as each LC control:
    # none of the SBR/PS hooks run for AAC-LC.
    expected = {(c, v, r) for c in cases
                for v in (VARIANTS if external or c.startswith('he') else (1,))
                for r in (1, 2, 3)}
    rows = records(log, 'RESULT', LABEL)
    areas = records(log, 'AREA', LABEL)
    ps_rows = records(log, 'PS', LABEL)
    storage = records(log, 'STORAGE', 'PSSTORAGE')
    windows = records(log, 'WINDOWS', LABEL)
    for table in (rows, ps_rows, storage, windows):
        if len(table) != len(expected) or {key(r) for r in table} != expected:
            raise ValueError('Missing/duplicate result, PS or window coverage')
    if (len(areas) != len(expected)*len(AREAS) or
        {(key(r), r['area']) for r in areas} != {(k, a) for k in expected for a in AREAS}):
        raise ValueError('Missing/duplicate area coverage')
    by_area = {(key(r), r['area']): r for r in areas}
    by_ps, by_storage = ({key(r): r for r in table} for table in (ps_rows, storage))
    if any(w['mask'] or w['transform1'] or w['transform2'] for w in windows):
        raise ValueError('Rejected IMDCT compression must remain disabled')
    pairs = {1: 48, 2: 12, 3: 512, 4: 32, 5: 32, 6: 11, 7: 10, 8: 10, 9: 32}
    for row in rows:
        v, k = row['variant'], key(row)
        maximum = max(row['max_l'], row['max_r'])
        counts = [row[f] for f in ('different', 'over_one', 'over_two', 'over_limit')]
        if (row['samples'] <= 0 or row['frames'] <= 10 or min(row['ref_work'], row['packed_work']) <= 0 or
            counts != sorted(counts, reverse=True) or min(counts) < 0 or counts[0] > row['samples']):
            raise ValueError('Invalid PCM counts/work')
        for threshold, count in zip((0, 1, 2, limits['development']), counts):
            if bool(maximum > threshold) != bool(count):
                raise ValueError('PCM maximum contradicts counters')
        if row['precision'] != ('FAIL' if row['over_limit'] else 'PASS'):
            raise ValueError('Invalid PCM verdict')
        a = [by_area[(k, i)] for i in AREAS]
        ps, store = by_ps[k], by_storage[k]
        if (ps['mask'] != MASKS[v] or ps['exact'] != int(v == 8) or ps['calls'] != store['calls'] or
            store['pairs'] != store['allocations']*617 or store['guards'] < store['pairs'] or
            store['native_payload'] != 4936 or store['packed_payload'] != (2780 if v >= 10 else 3088) or store['heap_saved'] or
            store['cache_bytes'] or store['cache_hits'] or store['cache_misses']):
            raise ValueError('Invalid PS storage/selection evidence')
        if (sum(i['calls'] for i in a)+ps['calls'] != row['complex_rows'] or
            sum(i['changed'] for i in a)+ps['changed'] != row['changed_qmf'] or
            max([i['max_shift'] for i in a]+[ps['max_shift']]) != row['max_shift'] or row['real_rows']):
            raise ValueError('Area/PS totals differ from paired result')
        if not (MASKS[v] & (1 << 10)) and any(ps[f] for f in ('calls', 'changed', 'max_shift')):
            raise ValueError('Disabled PS compression produced data')
        for i in a:
            if (i['pairs'] != pairs[i['area']]*i['calls'] or
                not 0 <= i['changed'] <= 2*i['pairs'] or not 0 <= i['max_shift'] <= 16 or
                not 0 <= i['nonzero'] <= 2*i['pairs'] or i['saturated'] or i['out_of_int16']):
                raise ValueError('Invalid area counters, overflow or saturation')
            if i['calls'] and not MASKS[v] & (1 << i['area']):
                raise ValueError('Disabled area was touched')
            if not i['calls'] and any(i[f] for f in ('changed', 'saturated', 'nonzero', 'minimum', 'maximum', 'max_shift', 'out_of_int16')):
                raise ValueError('Inactive area produced data')
            if row['run'] == 1 and i['calls'] and i['minimum'] > i['maximum']:
                raise ValueError('Invalid observed range')
            if (v == 8 or i['area'] == 5) and (i['changed'] or i['max_shift']):
                raise ValueError('Lossless control changed values')
        if store['saturations'] or (v in (0, 8) and (row['different'] or row['changed_qmf'])):
            raise ValueError('Saturation or changed lossless PCM')
        if not row['complex_rows'] and row['different']:
            raise ValueError('Inactive probe changed PCM')
        if not external and row['case'].startswith('hev2'):
            for area in (1, 2, 4, 5, 6, 7, 8, 9):
                if MASKS[v] & (1 << area) and not by_area[(k, area)]['calls']:
                    raise ValueError('Required synthetic probe missing')
            if MASKS[v] & (1 << 10) and not ps['calls']:
                raise ValueError('Required synthetic PS missing')
    summaries = []
    for case in cases:
        for v, name in VARIANTS.items():
            group = [r for r in rows if r['case'] == case and r['variant'] == v]
            if not group:
                continue
            for f in ('samples', 'frames', 'max_l', 'max_r', 'different', 'over_one', 'over_two', 'over_limit'):
                if len({r[f] for r in group}) != 1:
                    raise ValueError('Nondeterministic PCM or quantization')
            maximum = max(group[0]['max_l'], group[0]['max_r'])
            summaries.append(dict(case=case, variant=v, name=name, mask=MASKS[v],
                max_pcm_error_lsb=maximum, production_precision_pass=maximum <= limits['production'],
                samples_per_run=group[0]['samples'], over_two_per_run=group[0]['over_two'],
                over_limit_per_run=group[0]['over_limit'],
                instruction_overhead_median_percent=round(statistics.median(
                    100*(r['packed_work']/r['ref_work']-1) for r in group if r['run'] != 1), 3)))
    result = dict(experiment='combined_aac_storage18', precision_limit_lsb=limits['development'],
        precision_pass=aac_precision.passes(rows, limits['development']),
        production_precision_limit_lsb=limits['production'],
        production_precision_pass=aac_precision.passes(rows, limits['production']),
        ram_saved_bytes=0, timing_unit='QEMU guest instructions including probes; not physical CPU',
        summaries=summaries, runs=rows, areas=areas, ps=ps_rows, storage=storage, windows=windows)
    if external:
        normalized = log.replace(LABEL+'_', 'BFP16_').replace('variant=', 'bands=')
        stats = common.parse_statistics(normalized, [dict(r, bands=r['variant']) for r in rows], external)
        for s in stats:
            s['variant'] = s.pop('bands')
            for threshold, field in ((2, 'over_two'), (limits['development'], 'over_limit')):
                if s[field] != s['samples']-sum(s['histogram'].get(str(k), 0) for k in range(threshold+1)):
                    raise ValueError('Histogram contradicts precision counts')
        for r in rows:
            channels = [s for s in stats if (s['variant'], s['run']) == (r['variant'], r['run'])]
            if any(sum(s[f] for s in channels) != r[f] for f in ('over_two', 'over_limit')):
                raise ValueError('Channel precision counts disagree')
        result.update(external=external, error_statistics=stats)
    return result


if __name__ == '__main__':
    args = common.make_parser(__doc__, 'combined-storage').parse_args()
    sys.exit(common.run(args, log_parser=parse_log,
        config_key='YORADIO_QEMU_AAC_COMBINED_STORAGE_TEST', axis='variant'))
