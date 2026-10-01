#!/usr/bin/env python3
"""Run guarded SBR allocation/PCM experiments on the actual RV32 AAC decoder."""
import statistics
import sys
import run_aac_bfp16 as common
import re


def records(log, kind):
    rows=[]
    for line in log.splitlines():
        if f'SBRLAYOUT_{kind} ' not in line: continue
        fields=dict(re.findall(r'(\w+)=([\w.-]+)',line.split(f'SBRLAYOUT_{kind} ',1)[1]))
        rows.append({k:v if k in ('case','precision','PCM','cleanup') else int(v) for k,v in fields.items()})
    return rows


def key(row): return row['case'],row['variant'],row['run']


def parse_log(log):
    for marker in ('SBRLAYOUT_LAYOUT_PASS','SBRLAYOUT_COUNTER_PASS nop1024=1025',
                   'SBRLAYOUT_EXPERIMENT_COMPLETE','SBRLAYOUT_LIFECYCLE_COMPLETE',
                   'QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS'):
        if marker not in log: raise ValueError('Missing marker: '+marker)
    lifecycle=records(log,'LIFECYCLE_PASS')
    if len(lifecycle)!=3 or [(r['trial'],r['allocation_failure']) for r in lifecycle]!=[(0,0),(1,55128),(2,1180)]:
        raise ValueError('Missing lifecycle/failure coverage')
    if any(r.get('PCM')!='exact' or r.get('cleanup')!='complete' for r in lifecycle):
        raise ValueError('Lifecycle comparison or cleanup failed')
    completed=records(log,'LIFECYCLE_COMPLETE')
    if len(completed)!=1 or completed[0]!={'samples':1102848,'segments':21,'failure_paths':2}:
        raise ValueError('Incomplete lifecycle sequence')
    external=records(log,'EXTERNAL')
    if len(external)>1: raise ValueError('Duplicate input header')
    cases=('external',) if external else common.CASES
    expected={(c,v,r) for c in cases for v in ((7,) if c.startswith('lc') else (7,1,0)) for r in (1,2,3)}
    runs,memory=records(log,'RESULT'),records(log,'MEMORY')
    for matrix in (runs,memory):
        if len(matrix)!=len(expected) or {key(r) for r in matrix}!=expected:
            raise ValueError('Missing/duplicate measurement')
    for r in runs:
        if any(r[k] for k in ('different','max_l','max_r','over_one','over_two','over_limit','changed_qmf')):
            raise ValueError('Lossless layout changed PCM')
        if r['precision']!='PASS' or min(r['ref_work'],r['packed_work'],r['samples'],r['frames'])<=0:
            raise ValueError('Incomplete decode')
    for m in memory:
        if m['static_test_state']!=144 or m['guard_bytes']!=32:
            raise ValueError('Missing adapter/guard accounting')
        if m['allocations'] not in (0,2) or m['frees']!=0:
            raise ValueError('Unexpected live owner count')
        if m['variant']==1 and m['calls']:
            if (m['reference'],m['candidate'])!=(55128,51596):
                raise ValueError('Allocation did not shrink as specified')
            if m['physical_reference']<m['reference']+32 or m['physical_candidate']<m['candidate']+32:
                raise ValueError('Allocator size is smaller than its guarded request')
            if m['physical_reference']<=m['physical_candidate'] or m['allocations']!=2:
                raise ValueError('No measured allocation saving')
        elif any(m[k] for k in ('candidate','physical_candidate','calls','ps_reads')):
            raise ValueError('Unexpected compact storage in control')
        if m['case'].startswith('he') and m['variant']==1 and not m['calls']:
            raise ValueError('SBR fixture did not exercise compact layout')
        if m['case'].startswith('hev2') and m['variant']==1 and not m['ps_reads']:
            raise ValueError('PS fixture did not exercise relocation')
    summaries=[]
    for case in cases:
        for variant in ((7,) if case.startswith('lc') else (7,1,0)):
            group=[r for r in runs if r['case']==case and r['variant']==variant]
            for field in ('samples','frames'):
                if len({r[field] for r in group})!=1: raise ValueError('Inconsistent output shape')
            summary=dict(case=case,variant=variant,max_pcm_error_lsb=0,
                         instruction_overhead_median_percent=round(statistics.median(
                             100*(r['packed_work']/r['ref_work']-1) for r in group if r['run']!=1),3))
            summaries.append(summary)
    result=dict(experiment='lossless_sbr_owner_layout',precision_limit_lsb=0,precision_pass=True,
                summaries=summaries,runs=runs,memory=memory,lifecycle=lifecycle,lifecycle_complete=completed[0])
    if external:
        result['external']=external[0]
        result['error_statistics']=common.parse_statistics(log.replace('SBRLAYOUT_','BFP16_').replace('variant=','bands='),
            [dict(r,bands=r['variant']) for r in runs],external[0])
    return result


if __name__=='__main__':
    args=common.make_parser(__doc__,'sbr-layout').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_SBR_LAYOUT_TEST',axis='variant'))
