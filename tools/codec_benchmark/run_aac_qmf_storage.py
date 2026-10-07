#!/usr/bin/env python3
"""Compare storage roundtrips of new QMF analysis rows, without shrinking an allocation."""
import statistics
import sys
import run_aac_bfp16 as common
import aac_precision
from run_aac_pc16_write import records, key, storage_format_count

FORMATS={1:'shared16',2:'split16',3:'shared17_five',4:'shared17_four',5:'shared18_four',0:'binary_bypass'}

def parse_log(log):
    limits = aac_precision.log_limits(log,"QMFSTORAGE",required=False)
    label='QMFSTORAGE'
    count=storage_format_count(log,label)
    formats={k:v for k,v in FORMATS.items() if k<=count}
    for marker in (label+'_COUNTER_PASS nop1024=1025',label+'_EXPERIMENT_COMPLETE',
                   'QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS','QEMU_OLED_PASS','QEMU_AUDIO_PASS'):
        if marker not in log:raise ValueError('Missing completion marker: '+marker)
    external=records(log,'EXTERNAL',label)
    if len(external)>1:raise ValueError('Duplicate input header')
    external=external[0] if external else None
    cases=('external',) if external else common.CASES
    rows=records(log,'RESULT',label)
    expected={(case,v,run) for case in cases for v in ((1,) if case.startswith('lc') else formats) for run in (1,2,3)}
    if len(rows)!=len(expected) or {key(r) for r in rows}!=expected:raise ValueError('Incomplete/duplicate matrix')
    storage=records(log,'STORAGE',label)
    if len(storage)!=len(expected) or {key(r) for r in storage}!=expected:
        raise ValueError('Incomplete/duplicate storage matrix')
    stored={key(r):r for r in storage}
    for r in rows:
        maximum=max(r['max_l'],r['max_r'])
        counts=[r['different'],r['over_one'],r['over_two'],r['over_limit']]
        if r['samples']<=0 or r['frames']<=10 or min(r['ref_work'],r['packed_work'])<=0:raise ValueError('Missing decoded data')
        if counts!=sorted(counts,reverse=True) or min(counts)<0 or counts[0]>r['samples']:raise ValueError('Bad error counts')
        for threshold,n in zip((0,1,2,5),counts):
            if bool(maximum>threshold)!=bool(n):raise ValueError('Maximum contradicts error counts')
        if r['precision']!=('FAIL' if r['over_limit'] else 'PASS'):raise ValueError('Wrong precision verdict')
        exercised=r['complex_rows']+r['real_rows']
        if min(r['complex_rows'],r['real_rows'],r['changed_qmf'],stored[key(r)]['saturations'])<0:
            raise ValueError('Negative storage coverage')
        if stored[key(r)]['saturations']>64*exercised:raise ValueError('Invalid saturation count')
        if not exercised and stored[key(r)]['saturations']:raise ValueError('Inactive path saturated')
        if (not r['variant'] or r['case'].startswith('lc') or (external and not external['sbr'])) and exercised:
            raise ValueError('Unexpected QMF path')
        if not exercised and (r['different'] or r['changed_qmf']):raise ValueError('Inactive path changed PCM')
        if exercised and not r['changed_qmf']:raise ValueError('Storage not exercised')
        if not external and r['case'].startswith('he') and r['variant'] and not exercised:
            raise ValueError('Required QMF path missing')
    for a in (r for r in rows if r['variant']==3):
        b=next(r for r in rows if key(r)==(a['case'],4,a['run']))
        for field in ('samples','frames','max_l','max_r','different','over_one','over_two','over_limit'):
            if a[field]!=b[field]:raise ValueError('PC17 metadata layout changes PCM statistics')
    summaries=[]
    for case in cases:
        for v in ((1,) if case.startswith('lc') else formats):
            group=[r for r in rows if r['case']==case and r['variant']==v]
            for field in ('samples','frames','max_l','max_r','different','over_one','over_two','over_limit'):
                if len({r[field] for r in group})!=1:raise ValueError('Nondeterministic PCM')
            overhead=[100*(r['packed_work']/r['ref_work']-1) for r in group if r['run']!=1]
            summaries.append(dict(case=case,variant=v,name=FORMATS[v],max_pcm_error_lsb=max(group[0]['max_l'],group[0]['max_r']),
                samples_per_run=group[0]['samples'],over_two_per_run=group[0]['over_two'],over_limit_per_run=group[0]['over_limit'],
                coverage='quantized' if group[0]['complex_rows']+group[0]['real_rows'] else 'not_exercised',
                instruction_overhead_median_percent=round(statistics.median(overhead),3)))
    result=dict(experiment='qmf_analysis_storage_roundtrip',precision_limit_lsb=5,
                precision_pass=all(not r['over_limit'] for r in rows),production_precision_limit_lsb=limits["production"],
                production_precision_pass=aac_precision.passes(rows,limits['production']),ram_saved_bytes=0,
                quantization_exercised=any(s['coverage']=='quantized' for s in summaries),
                scope='Only new low-band QMF rows; unchanged allocation and native DSP; not compact high-band history',
                timing_unit='QEMU guest instructions including roundtrip wrappers; runs 2/3',summaries=summaries,runs=rows,storage=storage)
    if external:
        normalized=log.replace(label+'_','BFP16_').replace('variant=','bands=')
        stats=common.parse_statistics(normalized,[dict(r,bands=r['variant']) for r in rows],external)
        for s in stats:
            s['variant']=s.pop('bands');h=s['histogram']
            for threshold,field in ((2,'over_two'),(5,'over_limit')):
                if s[field]!=s['samples']-sum(h.get(str(k),0) for k in range(threshold+1)):
                    raise ValueError('Histogram differs from precision counts')
        for r in rows:
            channels=[s for s in stats if (s['variant'],s['run'])==(r['variant'],r['run'])]
            for field in ('over_two','over_limit'):
                if sum(s[field] for s in channels)!=r[field]:raise ValueError('Channel counts disagree')
        result.update(external=external,error_statistics=stats)
    return result

if __name__=='__main__':
    args=common.make_parser(__doc__,'qmf-storage').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_QMF_STORAGE_TEST',axis='variant'))
