"""Replay comparable case windows; retain original reports and gate corrections."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
sys.path.insert(0,'tools/esp32c3_tests')
from decoder_arena_experiment import check_transition_memory,evaluate,arena_check
from common import sha
from production_health import output_window

report={'scope':'Short physical prototype comparison; not production qualification',
        'cases':{},'gate_notes':[
          'The original 96 KiB runner required a lifetime-zero arena failure count; later implicit-SBR inherited the earlier changing failure. Replay uses per-case increments without erasing that failure.',
          'The initial baseline runner applied a constant-format heap trend gate to changing AAC parameters. Replay preserves absolute headroom/fault floors and reports the original trend rejection; deliberate LC/SBR growth is not evidence of a leak.'
        ]}
for directory,label in [('physical-96c','arena96'),('physical-baseline-2','baseline'),('physical-100','arena100')]:
    folder=root/directory
    phase='baseline' if label=='baseline' else 'candidate'
    health=json.loads((folder/(phase+'-health.json')).read_text())
    arenas=json.loads((folder/(phase+'-arena.json')).read_text())
    batches=json.loads((folder/phase/'status.json').read_text())
    results=json.loads((folder/'results.json').read_text())
    assert sum(len(b['samples']) for b in batches)==len(health)==len(arenas)
    report[label+'_health']={'samples':len(health),
        'boot_low_water':min(h['minimum_heap'] for h in health),
        'allocation_failures':max(h['allocation_failures'] for h in health),
        'task_watchdog_events':max(h['task_watchdog_events'] for h in health)}
    cursor=0
    for batch in batches:
        count=len(batch['samples'])
        batch['health']=health[cursor:cursor+count]
        batch['arena']=arenas[cursor:cursor+count]
        batch['arena_failures_before']=arenas[cursor-1]['failures'] if cursor and arenas[cursor-1] else 0
        cursor+=count
    for case,original in results.items():
        name=case.split(':',1)[1]
        batch=next(b for b in batches if b['case']==name)
        warmup=15 if name=='https-he-aac' else 3
        steady=[h for s,h in zip(batch['samples'],batch['health']) if s['seconds']>=warmup]
        stop=next(b for b in batches if b['case']==('https-stop' if name=='https-he-aac' else name+':stop'))
        row={'original_gates':{k:v['result'] for k,v in original.items()},
             'min_heap':min(h['heap'] for h in steady),
             'min_largest':min(h['largest'] for h in steady),
             'max_status_request_ms':max(s['request_ms'] for s in batch['samples']),
             'min_rssi':min(s.get('rssi',0) for s in batch['samples'])}
        row['output_counters']=output_window(steady)
        if name in ('changing','implicit-sbr'):
            row['transition_headroom']=evaluate(lambda:check_transition_memory(steady))
        if label!='baseline':
            a=batch['arena']; idle=stop['arena']
            row.update(maximum_live=max(r['live'] for r in a),
                minimum_arena_free=min(r['free'] for r in a),
                new_failures=idle[-1]['failures']-batch['arena_failures_before'],
                stop_live=idle[-1]['live'],stop_blocks=idle[-1]['blocks'],
                arena_replay=evaluate(lambda:arena_check(a,idle,batch['arena_failures_before'])))
        report['cases'][label+':'+name]=row
    report[label+'_restoration']=json.loads((folder/'restoration.json').read_text())['identity']
report['inputs']={p.relative_to(root).as_posix():sha(p.read_bytes())
                 for d in ('physical-96c','physical-baseline-2','physical-100')
                 for p in (root/d).rglob('*.json')}
(root/'review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{x:v for x,v in row.items() if x in ('min_heap','min_largest','maximum_live','minimum_arena_free','new_failures','stop_live')}
                  for k,row in report['cases'].items()},indent=2))
