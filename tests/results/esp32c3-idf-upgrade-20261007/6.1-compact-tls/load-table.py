import argparse,json,re,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
r=json.loads((a.input/'report.json').read_text())
batches=json.loads((a.input/'status.json').read_text())
rows=json.loads((a.input/'performance.json').read_text())
out=[]
for c in r['cases']:
 if not c['name'].startswith('cpu-under-http-load:'):continue
 name=c['name'].split(':',1)[1]
 b=next(b for b in batches if b['case']=='load:'+name)
 start,end=b['started_at']+10,b['ended_at']
 selected=[x for x in rows if start<=x['at']<=end]
 cpu=[];decoder=[]
 for x in selected:
  if 'PERF CPU:' in x['line']:
   values={k:float(v) for k,v in re.findall(r'\b(busy|heap|largest)=([\d.]+)',x['line'])}
   if set(values)=={'busy','heap','largest'}:cpu.append(values)
  m=re.search(r'PERF (?:AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms',x['line'])
  if m:decoder.append(tuple(map(int,m.groups())))
 item={'name':name,'acceptance':c['result'],'reason':c.get('reason'),
       'cpu_windows':len(cpu),'decoder_windows':len(decoder),
       'observed_formats':sorted({s['format'] for s in b['samples'] if s.get('audio')}),
       'warmup_excluded_seconds':10}
 if cpu:item.update(mean_busy=statistics.mean(x['busy'] for x in cpu),peak_busy=max(x['busy'] for x in cpu),
  minimum_heap=min(x['heap'] for x in cpu),minimum_largest=min(x['largest'] for x in cpu),
  initial_heap_median=statistics.median(x['heap'] for x in cpu[:3]),
  final_heap_median=statistics.median(x['heap'] for x in cpu[-3:]))
 if decoder:item['audio_wall_ratio']=sum(x[1] for x in decoder)/sum(x[0] for x in decoder)
 out.append(item)
a.output.write_text(json.dumps({'board':r['board'],'note':'Descriptive metrics preserve every original acceptance result; core fallback is not HE-AAC qualification.','cases':out},indent=2)+'\n')
for i in out:print(i['name'],i['acceptance'],'CPU',round(i.get('mean_busy',0),1),'heap',i.get('minimum_heap'),'audio/wall',round(i.get('audio_wall_ratio',0),4))
