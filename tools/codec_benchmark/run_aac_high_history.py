#!/usr/bin/env python3
"""Measure actual compact high-QMF storage, PCM error, reset and allocator bins."""
import statistics
import sys
import aac_precision
import run_aac_bfp16 as common
import run_aac_sbr_layout as layout
import run_aac_reset as reset

def high_records(log,kind):
    selected='\n'.join(line.replace('HIGHHISTORY_','SBRLAYOUT_')
                       for line in log.splitlines() if 'HIGHHISTORY_'+kind+' ' in line)
    return layout.records(selected,kind)

def parse_log(log):
    for marker in ('SBRLAYOUT_INITIALIZERS_PASS channel_rows=5 modes=2 PS=checked',
                   'SBRLAYOUT_COUNTER_PASS nop1024=1025','SBRLAYOUT_EXPERIMENT_COMPLETE',
                   'QEMU_AAC_FORMAT_PASS','QEMU_SMOKE_PASS','QEMU_OLED_PASS','QEMU_AUDIO_PASS'):
        if marker not in log: raise ValueError('Missing completion marker: '+marker)
    probe=layout.records(log,'ALLOCATOR')
    if len(probe)!=1 or probe[0]['reference_request']!=55128:
        raise ValueError('Missing unguarded allocator probe')
    p=probe[0]
    bits={47980:18,47692:16}.get(p['candidate_request'])
    if bits is None or not p['candidate_request']<=p['candidate_block']<p['reference_block']:
        raise ValueError('Unexpected layout or no actual allocator saving')
    channels={18:23984,16:23840}
    if f'compact_smoothing_tables=5 channel={channels[bits]} owner={p["candidate_request"]}' not in log:
        raise ValueError('Missing typed owner size')
    if layout.records(log,'FIR_PASS')!=[dict(cases=24,slots=32,frames=3,max_index=4,qmf_equal=1)]:
        raise ValueError('Missing smoothing FIR qualification')
    external=layout.records(log,'EXTERNAL')
    if len(external)>1: raise ValueError('Duplicate input')
    cases=('external',) if external else common.CASES
    expected={(c,v,r) for c in cases for v in ((7,) if c.startswith('lc') else (7,1,0)) for r in (1,2,3)}
    runs=layout.records(log,'RESULT');memory=layout.records(log,'MEMORY');hist=high_records(log,'MEMORY')
    for matrix in (runs,memory,hist):
        if len(matrix)!=len(expected) or {layout.key(r) for r in matrix}!=expected:
            raise ValueError('Missing/duplicate PCM or memory comparison')
    by_mem={layout.key(r):r for r in memory};by_hist={layout.key(r):r for r in hist}
    limits=aac_precision.log_limits(log,'SBRLAYOUT')
    for r in runs:
        k=layout.key(r);m=by_mem[k];h=by_hist[k]
        peak=max(r['max_l'],r['max_r'])
        if min(r['samples'],r['frames'],r['ref_work'],r['packed_work'])<=0:
            raise ValueError('Empty decode')
        counts=[r[n] for n in ('different','over_one','over_two','over_limit')]
        if counts!=sorted(counts,reverse=True) or min(counts)<0 or counts[0]>r['samples']:
            raise ValueError('Invalid error counts')
        for threshold,count in zip((0,1,2,limits['development']),counts):
            if bool(peak>threshold)!=bool(count):raise ValueError('PCM peak/count mismatch')
        if r['precision']!=('FAIL' if r['over_limit'] else 'PASS'):
            raise ValueError('Incorrect development precision verdict')
        if m['guard_bytes']!=32 or m['static_test_state']!=144:
            raise ValueError('Guard/adapter accounting changed')
        if m['allocations'] not in (0,2) or m['frees']:
            raise ValueError('Unexpected live owner count')
        if h['bytes']!={18:1440,16:1296}[bits] or h['state_bytes']!=44 or h['saturations']:
            raise ValueError('Storage size/counter accounting or saturation failure')
        if h['loads']!=h['stores'] or h['loads']!=h['real_frames']+h['complex_frames']:
            raise ValueError('Missing history transfer or unsupported mode')
        if r['variant']==1 and m['calls']:
            if (m['reference'],m['candidate'])!=(55128,p['candidate_request']) or not h['loads']:
                raise ValueError('Candidate did not use smaller storage')
            if not m['candidate']+32<=m['physical_candidate']<m['physical_reference'] or m['allocations']!=2:
                raise ValueError('No guarded allocation saving')
        elif (any(h[n] for n in ('loads','stores','changed','real_frames','complex_frames')) or peak or
              any(m[n] for n in ('candidate','physical_candidate','calls','ps_reads'))):
            raise ValueError('Control changed PCM or used packed storage')
    if not external:
        active=[h for h in hist if h['variant']==1]
        if not sum(h['real_frames'] for h in active) or not sum(h['complex_frames'] for h in active):
            raise ValueError('Both real and complex SBR must be exercised')
    lifecycle=layout.records(log,'LIFECYCLE_PASS');life_error=high_records(log,'LIFECYCLE')
    if [(r['trial'],r['allocation_failure']) for r in lifecycle]!=[(0,0),(1,55128),(2,1180)]:
        raise ValueError('Missing lifecycle/failure paths')
    if len(life_error)!=3 or [r['trial'] for r in life_error]!=[0,1,2]:
        raise ValueError('Missing lifecycle PCM measurements')
    for r,e in zip(lifecycle,life_error):
        if r['cleanup']!='complete' or r['PCM']!=('measured' if e['max_error'] else 'exact'):
            raise ValueError('Lifecycle PCM/cleanup mismatch')
    if layout.records(log,'LIFECYCLE_COMPLETE')!=[dict(samples=1102848,segments=21,failure_paths=2)]:
        raise ValueError('Incomplete format-change sequence')
    resets=reset.records(log,'PASS');reset_error=high_records(log,'RESET')
    samples={'lc44':147456,'lc22':39936,'lc48':159744,'he44':172032,'he48':184320,'hev2':184320}
    if len(resets)!=6 or len(reset_error)!=6 or {r['case'] for r in resets}!=set(samples):
        raise ValueError('Missing reset coverage')
    for r,e in zip(resets,reset_error):
        if r['case']!=e['case'] or r['cycles']!=3 or r['resets']!=2 or r['samples']!=samples[r['case']] or r['guards']!='pass' or r['cleanup']!='complete':
            raise ValueError('Incomplete repaired reset comparison')
        if r['PCM']!=('measured' if e['max_error'] else 'exact'):raise ValueError('Reset PCM mislabeled')
    if 'AACRESET_COMPLETE baseline_oob_writes=6 paired_reset_calls=24 core_bytes=35460 old_offset=87004' not in log:
        raise ValueError('Missing reset completion')
    summaries=[]
    for case in cases:
        for variant in ((7,) if case.startswith('lc') else (7,1,0)):
            group=[r for r in runs if r['case']==case and r['variant']==variant]
            if any(len({r[f] for r in group})!=1 for f in ('frames','samples')):
                raise ValueError('Inconsistent decoded shape')
            summaries.append(dict(case=case,variant=variant,max_pcm_error_lsb=max(max(r['max_l'],r['max_r']) for r in group),
                instruction_overhead_median_percent=round(statistics.median(100*(r['packed_work']/r['ref_work']-1)
                    for r in group if r['run']!=1),3)))
    peak=max([s['max_pcm_error_lsb'] for s in summaries]+[r['max_error'] for r in life_error+reset_error])
    result=dict(experiment='persistent_high_qmf_history',mantissa_bits=bits,precision_limit_lsb=limits['production'],
                precision_pass=peak<=limits['production'],max_pcm_error_lsb=peak,summaries=summaries,runs=runs,
                memory=memory,history=hist,allocator=p,measured_owner_block_saving_bytes=p['reference_block']-p['candidate_block'],
                lifecycle=lifecycle,lifecycle_pcm=life_error,resets=resets,reset_pcm=reset_error,
                production_qualified=False)
    if external:
        result['external']=external[0]
        result['error_statistics']=common.parse_statistics(log.replace('SBRLAYOUT_','BFP16_').replace('variant=','bands='),
            [dict(r,bands=r['variant']) for r in runs],external[0])
    return result

if __name__=='__main__':
    args=common.make_parser(__doc__,'high-history').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_HIGH_HISTORY_TEST',axis='variant'))
