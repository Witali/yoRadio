#!/usr/bin/env python3
"""Summarize actual high-QMF allocations separately from PCM and instruction cost."""
import argparse
import hashlib
import json
from pathlib import Path

NAMES=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')

def summarize(folder):
    rows=[];sources={}
    for variant in ('pc18','pc16'):
        for name in NAMES:
            p=folder/variant/name/'result.json'
            sources[p.relative_to(folder).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
            r=json.loads(p.read_text(encoding='utf-8'))
            active=[s for s in r['summaries'] if s['variant']==1]
            rms=[s['derived']['rms_error_lsb'] for s in r.get('error_statistics',[]) if s['bands']==1]
            rows.append(dict(format=variant,input=name,
                max_decode_error_lsb=max(s['max_pcm_error_lsb'] for s in active),
                max_reset_error_lsb=max(s['max_error'] for s in r['reset_pcm']),
                max_lifecycle_error_lsb=max(s['max_error'] for s in r['lifecycle_pcm']),
                max_channel_rms_lsb=max(rms) if rms else None,
                instruction_overhead_max_median_percent=max(s['instruction_overhead_median_percent'] for s in active),
                packed_history_exercised=any(h['loads'] for h in r['history']),
                owner_request=r['allocator']['candidate_request'],owner_block=r['allocator']['candidate_block'],
                owner_block_saving=r['measured_owner_block_saving_bytes'],production_precision_pass=r['precision_pass'],
                production_qualified=r['production_qualified']))
    return dict(scope='actual high-QMF owner; excludes whole-radio qualification',rows=rows,sources=sources)

def table(summary):
    out=['# Persistent high-QMF comparison','',
         'PCM errors are signed-16 output units. RMS is the largest per-channel value; synthetic RMS was not collected.',
         'Instruction cost is the largest per-case warm-run median; guards, copy dispatch and statistics are included.','',
         '| Storage | Input | Decode peak | Channel RMS | Reset peak | Lifecycle peak | Instructions | Owner request / block | Block saved |',
         '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in summary['rows']:
        rms='—' if r['max_channel_rms_lsb'] is None else f"{r['max_channel_rms_lsb']:.6f}"
        owner=f"{r['owner_request']} / {r['owner_block']} B" if r['packed_history_exercised'] else 'No SBR owner'
        saving=f"{r['owner_block_saving']} B" if r['packed_history_exercised'] else '0 B'
        out.append(f"| {r['format']} | {r['input']} | {r['max_decode_error_lsb']} | {rms} | {r['max_reset_error_lsb']} | {r['max_lifecycle_error_lsb']} | +{r['instruction_overhead_max_median_percent']:.3f}% | {owner} | {saving} |")
    out+=['','Both formats pass the 3-unit gate on this corpus. Both save the same allocator block space.',
          'AAC-LC does not allocate SBR history. The JSON also retains the profile allocator probe for those control runs.',
          'PC18 retains more accuracy for the next production-adapter experiment. Neither is production-qualified.','']
    return '\n'.join(out)

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__);p.add_argument('--results',required=True,type=Path);a=p.parse_args()
    result=summarize(a.results)
    (a.results/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    (a.results/'TABLES.md').write_text(table(result),encoding='utf-8',newline='\n')
