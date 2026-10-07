#!/usr/bin/env python3
"""Check actual 16+16 PS writes with eight packed exponent nibbles per word."""
import re
import statistics
import sys
import run_aac_bfp16 as common
import aac_precision

VARIANTS = {7:'native_source_control', 1:'packed_pc16_ps_writes', 0:'binary_bypass'}


def records(log, kind, label="PC16WRITE"):
    result=[]
    marker=f'{label}_{kind} '
    for line in log.splitlines():
        if marker not in line:continue
        fields=dict(re.findall(r'(\w+)=([\w.-]+)',line.split(marker,1)[1]))
        result.append({k:v if k in ('case','precision') else int(v) for k,v in fields.items()})
    return result


def key(row):return row['case'],row['variant'],row['run']


def storage_format_count(log, label):
    headers=records(log,'STORAGE_ARITHMETIC_PASS',label)
    if len(headers)!=1 or headers[0].get('random_pairs')!=10000 or headers[0].get('formats') not in (4,5):
        raise ValueError('Missing/invalid target storage arithmetic oracle')
    return headers[0]['formats']


def parse_log(log, *, variants=VARIANTS, payloads=None, label="PC16WRITE"):
    if payloads is None: payloads={1:2780}
    def read_records(kind): return records(log,kind,label)
    for marker in (f'{label}_ARITHMETIC_PASS pairs=100000',f'{label}_COUNTER_PASS nop1024=1025',
                   f'{label}_EXPERIMENT_COMPLETE','QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS',
                   'QEMU_OLED_PASS','QEMU_AUDIO_PASS'):
        if marker not in log:raise ValueError('Missing completion marker: '+marker)
    limits=aac_precision.log_limits(log,label)
    limit=limits["development"]
    headers=read_records('EXTERNAL')
    if len(headers)>1:raise ValueError('Duplicate external header')
    external=headers[0] if headers else None
    cases=('external',) if external else common.CASES
    expected={(case,v,run) for case in cases for v in ((7,) if case.startswith('lc') else variants) for run in (1,2,3)}
    rows,storage=read_records('RESULT'),read_records('STORAGE')
    for matrix in (rows,storage):
        if len(matrix)!=len(expected) or {key(r) for r in matrix}!=expected:
            raise ValueError('Incomplete/duplicate comparison matrix')
    stored={key(r):r for r in storage}
    for r in rows:
        s=stored[key(r)];v=r['variant'];maximum=max(r['max_l'],r['max_r'])
        if r['samples']<=0 or r['frames']<=10 or min(r['ref_work'],r['packed_work'])<=0:
            raise ValueError('Missing decode work')
        if not 0<=r['over_two']<=r['over_one']<=r['different']<=r['samples']:
            raise ValueError('Invalid error counts')
        counts={0:r['different'],1:r['over_one'],2:r['over_two']}
        if limit in counts and counts[limit]!=r['over_limit']:
            raise ValueError('Conflicting precision counts')
        counts[limit]=r['over_limit']
        ordered=[counts[k] for k in sorted(counts)]
        if min(ordered)<0 or ordered!=sorted(ordered,reverse=True):
            raise ValueError('Invalid precision counts')
        for threshold,field in ((0,'different'),(1,'over_one'),(2,'over_two'),(limit,'over_limit')):
            if bool(maximum>threshold)!=bool(r[field]):raise ValueError('Inconsistent maximum/error counts')
        if r['precision']!=('FAIL' if r['over_limit'] else 'PASS'):raise ValueError('Wrong precision verdict')
        if (s['native_payload'],s['packed_payload'],s['heap_saved'])!=(4936,payloads.get(v,2780),0):
            raise ValueError('Wrong storage accounting')
        if s['pairs']!=617*s['allocations'] or s['guards']<s['pairs'] or r['complex_rows']!=s['calls'] or r['real_rows']:
            raise ValueError('Missing PS storage coverage/guards')
        if not 0<=s['saturations']<=2*s['stores']:
            raise ValueError('Invalid saturation count')
        if min(s['calls'],s['stores'],s['allocations'],s['pairs'],s['guards'])<0:
            raise ValueError('Negative storage count')
        if bool(s['calls'])!=bool(s['stores']):raise ValueError('Missing history writes')
        if v not in payloads and (s['allocations'] or s['pairs'] or s['guards']):raise ValueError('Native control packed storage')
        if v==0 and s['calls']:raise ValueError('Bypass entered source replacement')
        if v in payloads and bool(s['calls'])!=bool(s['allocations']):raise ValueError('PS allocation wrapper missing')
        if (v not in payloads or not s['calls']) and (r['different'] or r['changed_qmf']):raise ValueError('Lossless control differs')
        if v in payloads and s['calls'] and r['run']==1 and not r['changed_qmf']:raise ValueError('Quantization not exercised')
        if not external and r['case']=='hev2_44100_stereo' and v and not s['calls']:
            raise ValueError('Required synthetic PS path missing')
        if r['case'].startswith('lc') and s['calls']:raise ValueError('LC entered PS')
    summaries=[]
    for case in cases:
        for variant in ((7,) if case.startswith('lc') else variants):
            group=[r for r in rows if r['case']==case and r['variant']==variant]
            for field in ('samples','frames','max_l','max_r','different','over_one','over_two','over_limit'):
                if len({r[field] for r in group})!=1:raise ValueError('Nondeterministic PCM')
            overhead=[100*(r['packed_work']/r['ref_work']-1) for r in group if r['run']!=1]
            summaries.append(dict(case=case,variant=variant,name=variants[variant],
                                  coverage='control' if variant not in payloads else 'quantized' if stored[key(group[0])]['calls'] else 'not_exercised',
                                  samples_per_run=group[0]['samples'],max_pcm_error_lsb=max(group[0]['max_l'],group[0]['max_r']),
                                  over_two_per_run=[r['over_two'] for r in group],over_limit_per_run=[r['over_limit'] for r in group],
                                  instruction_overhead_median_percent=round(statistics.median(overhead),3),
                                  instruction_overhead_range_percent=[round(min(overhead),3),round(max(overhead),3)]))
    result=dict(experiment='espressif_ps_pc16_write_port',precision_limit_lsb=limit,
                precision_pass=all(not r['over_limit'] for r in rows),production_precision_limit_lsb=limits["production"],
                production_precision_pass=aac_precision.passes(rows,limits['production']),
                quantization_exercised=any(s['coverage']=='quantized' for s in summaries),
                ram_saved_bytes=0,ps_delay_native_payload_bytes=4936,ps_delay_packed_payload_bytes=2780,
                timing_unit='QEMU guest instructions, including source wrapper and counters; runs 2/3 only',
                summaries=summaries,runs=rows,storage=storage)
    if len(payloads)>1:
        result['ps_delay_packed_payload_bytes']={str(k):v for k,v in payloads.items()}
    if external:
        normalized=log.replace(label+'_','BFP16_').replace('variant=','bands=')
        stats=common.parse_statistics(normalized,[dict(r,bands=r['variant']) for r in rows],external)
        for s in stats:
            s['variant']=s.pop('bands');h=s['histogram']
            for threshold,field in ((2,'over_two'),(limit,'over_limit')):
                if s[field]!=s['samples']-sum(h.get(str(k),0) for k in range(threshold+1)):
                    raise ValueError('Histogram differs from precision counts')
        for r in rows:
            channels=[s for s in stats if (s['variant'],s['run'])==(r['variant'],r['run'])]
            for field in ('over_two','over_limit'):
                if sum(s[field] for s in channels)!=r[field]:raise ValueError('Channel counts disagree')
        result.update(external=external,error_statistics=stats)
    return result


if __name__=='__main__':
    args=common.make_parser(__doc__,'pc16-write').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_PC16_WRITE_TEST',axis='variant'))
