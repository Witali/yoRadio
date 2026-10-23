from collections import Counter
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for board,location in [('cyd','lint-cyd-runtime-transfer-full'),('c3','lint-c3-runtime-transfer-resumed-02')]:
 report=json.loads((ROOT/'.build'/location/'report.json').read_text());old=json.loads((ROOT/f'.build/lint-{board}-ota-transfer-full/report.json').read_text())
 def key(d):return d['file'].replace('\\','/').lower(),d['check'],d['message']
 previous=Counter(key(d) for r in old['results'] for d in r['diagnostics'])
 new=[]
 for r in report['results']:
  for d in r['diagnostics']:
   k=key(d)
   if previous[k]:previous[k]-=1
   else:new.append(dict(unit=r['file'],**d))
 print(board,report['units'],report['warnings'],'prior',old['units'],old['warnings'],'new',len(new))
 for d in new:print(d['unit'],d['line'],d['check'],d['message'])
 (ROOT/f'.build/runtime-lint-{board}-new-warnings.json').write_text(json.dumps(new,indent=2)+'\n')
