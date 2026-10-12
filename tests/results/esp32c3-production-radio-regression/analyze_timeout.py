import json
from pathlib import Path
root=Path('.build/c3-production-radio-regression');p=root/'physical'
report=json.loads((p/'report.json').read_text());batches=json.loads((p/'status.json').read_text())
trace=[json.loads(line) for line in (p/'request-phases.jsonl').read_text().splitlines()]
health=json.loads((p/'health.json').read_text())
case=next(c for c in report['cases'] if c['name']=='file-eof:hev2-44100-stereo:aac')
terminal=next(b for b in batches if b['case']=='hev2-44100-stereo:aac:terminal')
failed=[r for r in trace if terminal['started_at']<=r.get('at',-1)<=terminal['ended_at'] and r.get('result')=='FAIL']
assert any(r['phase']=='connect' and r['ms']>=5000 for r in failed)
last=terminal['samples'][-1];assert not last['audio'] and last['format']=='stream ended'
rows=[h for h in health if terminal['started_at']<=h['at']<=terminal['ended_at']]
result=dict(case=case,failed_phases=failed,last_successful_status=last,last_health=rows[-1],
    interpretation='Host TCP connect timeout after observed correct terminal state; decoder fault, listener failure, Wi-Fi loss and network cause are not established.',
    next_measurement='Correlate host ephemeral port and timestamp with retained board TCP probe; include Wi-Fi event timing. USB 303A:1001 is currently available.')
(root/'timeout-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print('Retained post-EOF TCP timeout analysis')
