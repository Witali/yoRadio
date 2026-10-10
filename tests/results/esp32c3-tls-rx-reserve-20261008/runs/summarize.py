import json, sys
from pathlib import Path
sys.path.insert(0, str(Path('tools/esp32c3_tests').resolve()))
from summarize_sustained import window, gate
from public_streams import no_runtime_faults

root=Path('.build/c3-reserve-soak-20261008/physical')
result={}
for name in ('aac-alternate-600','flac-https-600'):
    folder=root/name
    if not (folder/'performance.json').exists(): continue
    report=json.loads((folder/'report.json').read_text())
    rows=json.loads((folder/'performance.json').read_text())
    batches=json.loads((folder/'status.json').read_text())
    batch=next(b for b in batches if b['case'].startswith(('tls-record:','load:')))
    start,end=batch['started_at'],batch['ended_at']
    samples=batch['samples']
    result[name]=dict(cases=report['cases'],full=window(rows,start+10,end,max_busy=None),
        runtime=gate(lambda: no_runtime_faults([r for r in rows if start<=r['at']<=end])),
        polls=len(samples),http_max_ms=max(s['request_ms'] for s in samples),
        rssi_min=min(s['rssi'] for s in samples),rssi_max=max(s['rssi'] for s in samples),
        allocation_failure_rows=sum('alloc' in r['line'].lower() and 'fail' in r['line'].lower() for r in rows),
        subwindows=[window(rows,begin,min(begin+300,end),max_busy=None)
                    for begin in (start+10,start+310) if begin<end])
Path('.build/c3-reserve-soak-20261008/summary.json').write_text(json.dumps(result,indent=2)+'\n')
for name,item in result.items():
    print(name, json.dumps({k:v for k,v in item.items() if k not in ('cases','subwindows')},indent=2))
