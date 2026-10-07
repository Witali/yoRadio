import json, re, statistics, sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from network_memory import parse_snapshot, parse_receive_snapshot, ranges
root=Path('.build/c3-memory-20261007')
result={'note':'Original verdicts retained. Host builds overlapped both physical soaks; CPU means are diagnostic, not isolated timing benchmarks. One pair is not long-term network or acoustic qualification.', 'cases':[]}
for variant in ('control','rxcopy'):
    folder=root/(variant+'-soak')
    checkpoint=json.loads((folder/'checkpoint.json').read_text())
    assert checkpoint.get('complete') and checkpoint.get('finished'),variant+' is incomplete'
    report=json.loads((folder/'report.json').read_text())
    status=json.loads((folder/'status.json').read_text())
    rows=json.loads((folder/'performance.json').read_text())
    summary=json.loads((root/(variant+'-soak-summary.json')).read_text())['cases'][0]
    load=next(b for b in status if b['case'].startswith('load:'))
    start,end=load['started_at'],load['ended_at']
    selected=[r for r in rows if start <= r['at'] < end]
    failed=[r for r in selected if 'allocation failed' in r['line']]
    snapshots=[s for r in rows if (s:=parse_snapshot(r)) is not None]
    credit=[s for r in rows if (s:=parse_receive_snapshot(r)) is not None]
    phases={}
    for label,begin,finish in (('first-minute',start+10,start+70),('last-minute',end-60,end)):
        net=[s for s in snapshots if begin <= s['sample_at'] < finish]
        rx=[s for s in credit if begin <= s['sample_at'] < finish]
        phases[label]={'heap':ranges(net,('heap','largest','blocks','free_blocks')),
            'receive_credit':ranges(rx,('uncredited','refused')), 'samples':len(net)}
    delivery=[w for e in report.get('server_events',[]) for w in e.get('delivery',{}).get('windows',[])]
    result['cases'].append(dict(variant=variant,app_elf_sha256=report['board']['app_elf_sha256'],
        requested_seconds=report['load_seconds'],observed_seconds=end-start,
        original_cases=report['cases'],summary=summary,allocation_failures=failed,
        network_phases=phases,
        host_delivery=dict(windows=len(delivery),max_late_seconds=max(w['max_late_seconds'] for w in delivery),
            max_write_seconds=max(w['max_write_seconds'] for w in delivery)),
        rssi=dict(min=min(s['rssi'] for s in load['samples']),median=statistics.median(s['rssi'] for s in load['samples'])),
        idle=[c for c in report['cases'] if c['name'] in ('idle-before','idle-after')]))
(root/'pair-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for c in result['cases']:
    print(c['variant'],c['summary']['original']['result'],'OOM',len(c['allocation_failures']),c['summary']['full_window']['diagnostic'],c['host_delivery'])
