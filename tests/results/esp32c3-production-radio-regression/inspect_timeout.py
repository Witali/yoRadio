import json
from pathlib import Path
p=Path('.build/c3-production-radio-regression/physical')
r=json.loads((p/'report.json').read_text())
for c in r['cases']:
    if c['result']!='PASS':print(json.dumps(c,indent=2))
b=[v for v in json.loads((p/'status.json').read_text()) if v['case'].startswith('hev2-44100-stereo:aac')]
for v in b:
    print(json.dumps(dict(case=v['case'],started=v['started_at'],ended=v['ended_at'],samples=len(v['samples']),last=v['samples'][-1] if v['samples'] else None),indent=2))
rows=[json.loads(line) for line in (p/'request-phases.jsonl').read_text().splitlines()]
for row in rows:
    if any(v['started_at']-2<=row.get('at',-1)<=v['ended_at']+2 for v in b) and ('error' in str(row).lower() or row.get('duration_ms',0)>1000):print(json.dumps(row))
print('Last trace entry fields',rows[-1].keys())
