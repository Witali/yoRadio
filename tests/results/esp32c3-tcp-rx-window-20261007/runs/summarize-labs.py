import copy, json, re, statistics, sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import matches
from tls_records import record_evidence
root=Path('.build/c3-rx-window-20261007')
result=[]
for mode in ('dynamic','static'):
    folder=root/f'physical-lab-{mode}'
    report=json.loads((folder/'report.json').read_text())
    batches=json.loads((folder/'status.json').read_text())
    rows=json.loads((folder/'performance.json').read_text())
    for batch in batches:
        name=batch['case']
        if not name.startswith('tls-record:'):continue
        record_mode=name.split(':')[1]
        case=next(c for c in report['cases'] if c['name']==name)
        subset=[r for r in rows if batch['started_at']-1<=r['at']<=batch['ended_at']]
        events=[e for e in report['server_events'] if e.get('mode')==record_mode or
                not e.get('mode') and batch['started_at']-1<=min((r['at'] for r in e['records']),default=e['ended_at'])<=batch['ended_at']]
        samples=batch['samples']
        playing=[s for s in samples if s.get('audio')]
        correct=[s for s in samples if matches(s,dict(rate=44100,channels=2,bits=16,label='HE-AACv2 '))]
        cpu=[]
        first=next((batch['started_at']+s['seconds'] for s in correct),None)
        last=batch['started_at']+correct[-1]['seconds'] if correct else None
        for r in subset:
            if first is None or not first+5<=r['at']<=last:continue
            m=re.search(r'PERF CPU: busy=([\d.]+)%.*heap=(\d+) largest=(\d+)',r['line'])
            if m:cpu.append(dict(busy=float(m[1]),heap=int(m[2]),largest=int(m[3])))
        item=dict(tls=mode,record_mode=record_mode,acceptance=case,
            playing_samples=len(playing),full_rate_samples=len(correct),
            formats=sorted({s['format'] for s in playing}),
            first_full_pcm_seconds=next((s['seconds'] for s in correct),None),
            max_http_ms=max((s['request_ms'] for s in samples),default=None),
            rssi_min=min((s['rssi'] for s in samples if 'rssi' in s),default=None),
            rssi_median=statistics.median([s['rssi'] for s in samples if 'rssi' in s]) if samples else None,
            runtime_faults=[r for r in subset if re.search(r'allocation failed|decode (?:error|failed)|TLS failure:|PANIC|watchdog|serial capture interrupted',r['line'])],
            cpu_scope='After first full PCM +5 seconds, no later than the last full PCM observation; idle after failure excluded',
            cpu_samples=len(cpu),mean_busy=statistics.mean(c['busy'] for c in cpu) if len(cpu)>=3 else None,
            minimum_free=min((c['heap'] for c in cpu),default=None),minimum_largest=min((c['largest'] for c in cpu),default=None))
        observed=report['record_observations'][record_mode]['events']
        item['record_replay_scope']='Frozen gate snapshot captured before Stop'
        try:item['records']=record_evidence(observed,record_mode)
        except AssertionError as e:item['record_gate_error']=str(e)
        result.append(item)
(root/'lab-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for c in result:
    print(c['tls'],c['record_mode'],c['acceptance']['result'],c['acceptance'].get('reason'),
          'full_pcm',c['full_rate_samples'],'min_heap',c['minimum_free'],'min_largest',c['minimum_largest'],
          'faults',len(c['runtime_faults']))
