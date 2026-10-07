import argparse, collections, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('paths',nargs='+');a=p.parse_args()
for name in a.paths:
 path=Path(name)
 if not path.exists():continue
 data=json.loads(path.read_text(encoding='utf-8-sig'))
 cases=data.get('cases',[]) if isinstance(data,dict) else data
 counts=collections.Counter(c.get('result',c.get('status',str(c.get('exit_code')))) for c in cases)
 print(path.parent.name,path.name,dict(counts))
 for c in cases:
  result=c.get('result',c.get('status',c.get('exit_code')))
  if result in ('FAIL','BLOCKED','TIMEOUT') or isinstance(result,int) and result:
   print(' ',c.get('name',c.get('test')),result,c.get('reason',''))
