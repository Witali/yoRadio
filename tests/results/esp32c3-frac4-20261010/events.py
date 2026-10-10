"""Correlate complete DMA counter brackets with queue-wait windows."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from staged_dma import parse, summarize
from pipeline_flow import FIELDS

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'events.json');a=p.parse_args()
review=json.loads((ROOT/'review.json').read_text())
result=dict(phases={},note='Counter brackets and overlapping task windows are not exact event times or proof of causality. '
            'Queue waits are wall time, not CPU use; input and output waits can overlap. '
            'No analog gap count or source-clock drift is measured.')
for label in ('hev2-tls-grow','flac-https'):
    folder=ROOT/'physical'/label
    rows=json.loads((folder/'performance.json').read_text())
    batches=json.loads((folder/'status.json').read_text())
    batch=next(b for b in batches if b['case'].startswith(('load:','tls-record:')))
    start,end=batch['started_at'],batch['ended_at']
    item=dict(observation_seconds=end-start,interrupted=bool(batch.get('interrupted')),events=[])
    result['phases'][label]=item
    try:
        # Canonical validator rejects merged rows, resets and incomplete coverage.
        summary=summarize(rows,start+10,end)
        item.update(dma=summary,coverage_valid=summary['coverage_complete'])
        dma=[v for row in rows if (v:=parse(row)) and start+10<=v['at']<=end]
        for previous,current in zip(dma,dma[1:]):
            delta=current['q_overruns']-previous['q_overruns']
            if not delta:continue
            overlaps={}
            for kind in ('DEC','STAGED_OUT'):
                selected=[]
                for row in rows:
                    if 'PERF FLOW_'+kind+':' not in row['line']:continue
                    pairs=re.findall(r'(\w+)=(\d+)\b',row['line'])
                    values={k:int(v) for k,v in pairs}
                    required=['gen','window_us']
                    for field in FIELDS[kind]:
                        required += [field+'_us',field+'_n',field+'_max']
                        if field!='submit':required += [field+'_timeouts']
                    if kind=='STAGED_OUT':required += ['overruns']
                    if row['line'].count('PERF ')!=1 or any(sum(k==f for k,v in pairs)!=1 for f in required):
                        item.setdefault('flow_parse_issues',[]).append(row);continue
                    left=row['at']-values['window_us']/1e6
                    if left<current['at'] and row['at']>previous['at']:
                        selected.append(dict(start=left-start,end=row['at']-start,values=values,row=row))
                overlaps[kind]=selected
            item['events'].append(dict(start=previous['at']-start,end=current['at']-start,events=delta,flow=overlaps))
        item['total']=sum(e['events'] for e in item['events'])
        assert item['total']==summary['delta']['q_overruns']
    except (AssertionError,ValueError) as error:
        item.update(coverage_valid=False,reason=str(error))
    sustained=review['phases'][label]['sustained']
    for key in ('flow_decoder','flow_output'):
        item[key]={k:v for k,v in sustained[key].items() if k not in ('windows','intervals')}
a.output.write_text(json.dumps(result,indent=2)+'\n')
for name,item in result['phases'].items():
    print(json.dumps(dict(phase=name,events=item.get('total'),coverage_valid=item['coverage_valid'],
        input_wait=item['flow_decoder'].get('input'),pcm_full=item['flow_decoder'].get('pcm'),
        pcm_empty=item['flow_output'].get('empty'))))
