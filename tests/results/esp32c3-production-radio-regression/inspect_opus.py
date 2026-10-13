import json,statistics
from pathlib import Path
root=Path('.build/c3-production-radio-regression/physical')
batches=json.loads((root/'status.json').read_text());health=json.loads((root/'health.json').read_text())
for b in batches:
    if not b['case'].startswith('opus-510:') or not b['case'].endswith(':playing'):continue
    rows=[h for h in health if b['started_at']<=h['at']<=b['ended_at']]
    pairs=[(s,h) for s,h in zip(b['samples'],rows) if s['seconds']>=4]
    print(b['case'],len(pairs))
    print([(round(s['seconds'],2),h['heap'],h['largest'],h['output']) for s,h in pairs])
    for key in ('heap','largest'):
        print(key,statistics.median(h[key] for s,h in pairs[:3]),statistics.median(h[key] for s,h in pairs[-3:]))
