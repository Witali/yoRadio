import json
from pathlib import Path
root=Path(__file__).resolve().parent/'physical'
for mode in ('dio','qio'):
    for p in sorted((root/mode).glob('*/report.json')):
        try:r=json.loads(p.read_text())
        except ValueError:continue
        c=r['cases'];failed=[(x['name'],x.get('reason')) for x in c if x['result']!='PASS']
        print(mode,p.parent.name,'cases',len(c),'passed',sum(x['result']=='PASS' for x in c),'failed',failed)
p=root/'phases.json'
if p.exists():print('Latest phases',json.loads(p.read_text())[-3:])
