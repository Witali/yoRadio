"""Summarize completed runs without converting any failed gate into a pass."""
import collections, json
from pathlib import Path
root=Path('.build/idf-upgrade')
names=('matrix','eof-recheck','public-http','public-https','load','flac-truncation',
       'switch','retry','hev2-soak','production-transition','ota','http-headers',
       'production','http-headers-recheck','http-ota','http-production','http-quiet-https')
results=[]
for name in names:
    stem=root/('physical-6.1-compact-ram-'+name)
    path=stem/'report.json' if stem.is_dir() else Path(str(stem)+'.json')
    report=json.loads(path.read_text())
    counts=dict(collections.Counter(row['result'] for row in report['cases']))
    failures=[{k:v for k,v in row.items() if k in ('name','result','reason','exception_chain')}
              for row in report['cases'] if row['result']!='PASS']
    results.append(dict(name=name,report=path.as_posix(),board=report['board'],
                        counts=counts,failures=failures))
(root/'qualification-6.1-compact-ram-final.json').write_text(json.dumps(dict(
    note='Original failed runs retained; guarded HTTP image has separate checks.',
    checks=results),indent=2)+'\n')
for item in results: print(item['name'],item['counts'])
