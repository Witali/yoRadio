import json,re
from pathlib import Path
p=Path('.build/idf-upgrade/python-6.0.3')
rows=json.loads((p/'results.json').read_text())
for row in rows:
 name=row['test'].removesuffix('.py')
 candidates=[p/(row['test']+'-recheck.log')]
 if name=='test-aac-sbr-retention':candidates=[p/(name+'-native.log')]
 log=next((f for f in candidates if f.exists()),p/(row['test']+'.log'))
 text=log.read_text(errors='replace')
 row['final_log']=log.name
 row['final_passed']=bool(re.search(r'^OK(?:\s|$)',text,re.M)) or row['exit_code']==0 and log.name==row['test']+'.log'
 row['final_skipped']=int(m[1]) if (m:=re.search(r'skipped=(\d+)',text)) else 0
 row['final_failures']=int(m[1]) if (m:=re.search(r'failures=(\d+)',text)) else 0
 row['final_errors']=int(m[1]) if (m:=re.search(r'errors=(\d+)',text)) else 0
summary={'scripts':len(rows),'cases':sum(r['cases'] or 0 for r in rows),
 'passing_scripts':sum(r['final_passed'] for r in rows),
 'skipped':sum(r['final_skipped'] for r in rows),
 'failures':sum(r['final_failures'] for r in rows),'errors':sum(r['final_errors'] for r in rows),
 'failed_scripts':[r['test'] for r in rows if not r['final_passed']], 'runs':rows}
(p/'final-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='runs'}))
