"""Compare matched board windows without dropping failed acceptance cases.

CPU percentages are FreeRTOS task runtime, not wall time spent blocked on DMA.
Decoder time is divided by decoded audio duration; no emulator factor is used.
"""
import argparse
import json
from pathlib import Path
import re
import statistics

from common import sha


def summarize(folder):
    inputs={n:json.loads((folder/n).read_text()) for n in
            ('report.json','status.json','performance.json')}
    report,observations,performance=(inputs[n] for n in ('report.json','status.json','performance.json'))
    result={'image':report['board']['app_elf_sha256'],'cases':{},
            'input_sha256':{n:sha((folder/n).read_bytes()) for n in inputs}}
    for case in report['cases']:
        prefix='cpu-under-http-load:'
        if not case['name'].startswith(prefix):continue
        name=case['name'][len(prefix):]
        windows=[r for r in observations if r['case']=='load:'+name]
        if len(windows)!=1:raise ValueError('Missing or duplicate window')
        window=windows[0];start=window['started_at']+10;end=window['ended_at']
        rows=[r for r in performance if start<=r['at']<end]
        cpu=[];decode=[]
        for row in rows:
            if 'PERF CPU:' in row['line']:
                fields={k:float(v) for k,v in re.findall(r'\b(busy|decode|output|heap|largest)=([\d.]+)',row['line'])}
                if set(fields)!={'busy','decode','output','heap','largest'}:raise ValueError('Incomplete CPU row')
                cpu.append(fields)
            m=re.search(r'PERF (?:AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms',row['line'])
            if m:decode.append(tuple(map(int,m.groups())))
        if len(cpu)<3 or len(decode)<3:raise ValueError('Missing timing samples')
        item={'acceptance':case['result'],'reason':case.get('reason'),
              'cpu_samples':len(cpu),'decoder_windows':len(decode),
              'busy_percent':statistics.mean(r['busy'] for r in cpu),
              'decoder_percent':statistics.mean(r['decode'] for r in cpu),
              'output_percent':statistics.mean(r['output'] for r in cpu),
              'decode_ms_per_audio_second':sum(d[2] for d in decode)*1000/sum(d[1] for d in decode),
              'audio_wall_ratio':sum(d[1] for d in decode)/sum(d[0] for d in decode),
              'minimum_heap':min(r['heap'] for r in cpu),'minimum_largest':min(r['largest'] for r in cpu),
              'rssi':{'min':min(r['rssi'] for r in window['samples']),
                      'max':max(r['rssi'] for r in window['samples'])}}
        item['decoder_plus_output_percent']=item['decoder_percent']+item['output_percent']
        result['cases'][name]=item
    result['fixture_hashes']=report['fixture_hashes']
    return result


def compare(control,candidate):
    before,after=summarize(control),summarize(candidate)
    if before['fixture_hashes']!=after['fixture_hashes'] or before['cases'].keys()!=after['cases'].keys():
        raise ValueError('Different fixtures/cases')
    return {'control':before,'candidate':after,'hardware':True,
            'note':'Short load comparison. Does not certify sample-level DMA continuity or long-term stability.',
            'deltas':{n:{'decode_percent_change':(after['cases'][n]['decode_ms_per_audio_second']/
                before['cases'][n]['decode_ms_per_audio_second']-1)*100,
                'decoder_plus_output_percentage_points':after['cases'][n]['decoder_plus_output_percent']-
                    before['cases'][n]['decoder_plus_output_percent'],
                'output_percentage_points':after['cases'][n]['output_percent']-before['cases'][n]['output_percent']}
                for n in before['cases']}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=compare(a.control,a.candidate)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    for name,delta in result['deltas'].items():print(name,delta)
