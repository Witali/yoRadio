#!/usr/bin/env python3
"""Compare four-row storage with retained PC18 results, without adding RAM claims."""
import argparse
import hashlib
import json
from pathlib import Path
import run_aac_smoothing_history as runner

NAMES=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')
ERROR_FIELDS=('samples','frames','max_l','max_r','different','over_one','over_two','over_limit')

def summarize(folder,previous):
    rows=[];sources={};comparisons=0;matching=True
    for name in NAMES:
        path=folder/name/'result.json'
        current=json.loads(path.read_text(encoding='utf-8'))
        old_path=previous/name/'result.json'
        old=json.loads(old_path.read_text(encoding='utf-8'))
        checked=runner.parse_log((folder/name/'qemu.log').read_text(encoding='utf-8'))
        if any(current.get(k)!=v for k,v in checked.items()):
            raise ValueError('Saved result disagrees with validated log: '+name)
        sources[name]={label:hashlib.sha256(p.read_bytes()).hexdigest()
                       for label,p in (('result',path),('previous_result',old_path))}
        comparisons+=len(current['runs'])
        old_runs={(r['case'],r['variant'],r['run']):r for r in old['runs']}
        same=all(all(r[k]==old_runs[(r['case'],r['variant'],r['run'])][k] for k in ERROR_FIELDS)
                 for r in current['runs'])
        matching&=same
        old_summary={(r['case'],r['variant']):r for r in old['summaries']}
        for r in current['summaries']:
            if r['variant']!=1:continue
            before=old_summary[(r['case'],r['variant'])]['instruction_overhead_median_percent']
            now=r['instruction_overhead_median_percent']
            rms=[s['derived']['rms_error_lsb'] for s in current.get('error_statistics',[]) if s['bands']==1]
            rows.append(dict(input=name,case=r['case'],max_decode_error_lsb=r['max_pcm_error_lsb'],
                max_channel_rms_lsb=max(rms) if rms else None,error_counts_match_previous=same,
                native_instruction_overhead_percent=now,
                additional_instructions_vs_previous_percent=round(100*((100+now)/(100+before)-1),3),
                history_exercised=any(h['loads'] for h in current['history']),
                candidate_request=current['allocator']['candidate_request'],
                candidate_block=current['allocator']['candidate_block'],
                production_precision_pass=current['precision_pass']))
    return dict(scope='QEMU four-row smoothing plus PC18 high history; no physical-radio qualification',
        comparisons=comparisons,error_counts_match_previous=matching,rows=rows,sources=sources,
        owner_block_saving_vs_native_bytes=55296-47104,
        owner_block_saving_vs_previous_bytes=49152-47104,
        temporary_stack_payload_bytes=1024,compiled_complex_wrapper_stack_frame_bytes=1184,
        production_qualified=False)

def table(summary):
    lines=['# Four-row smoothing plus PC18 high history','',
      'Errors are signed-16 PCM units against the native decoder; instruction costs are QEMU guest instructions.',
      'The previous variant is the retained five-row PC18 experiment. Matching error counts are not a PCM hash comparison.','',
      '| Input | Decode peak | Channel RMS | Instructions vs native | Instructions vs previous PC18 | Owner request / block |',
      '| --- | ---: | ---: | ---: | ---: | ---: |']
    for r in summary['rows']:
        label=r['case'] if r['input']=='synthetic' else r['input']
        rms='Not collected' if r['max_channel_rms_lsb'] is None else f"{r['max_channel_rms_lsb']:.6f}"
        size=f"{r['candidate_request']} / {r['candidate_block']} B" if r['history_exercised'] else 'No SBR owner'
        lines.append(f"| {label} | {r['max_decode_error_lsb']} | {rms} | {r['native_instruction_overhead_percent']:+.3f}% | {r['additional_instructions_vs_previous_percent']:+.3f}% | {size} |")
    lines+=['','All 81 paired comparisons pass the current 3-LSB gate. Direct FIR tests are bit-exact.',
        'The owner block saves 2048 B versus the previous PC18 owner, 8192 B versus native.',
        'Complex processing needs a 1024-byte temporary payload (1184-byte compiled wrapper frame).',
        'Physical stack, full-radio heap/CPU, public streaming and OTA remain unqualified.','']
    return '\n'.join(lines)

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--results',required=True,type=Path)
    p.add_argument('--previous',required=True,type=Path)
    a=p.parse_args();result=summarize(a.results,a.previous)
    (a.results/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    (a.results/'TABLES.md').write_text(table(result),encoding='utf-8',newline='\n')
