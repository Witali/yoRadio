import hashlib,json
from pathlib import Path
root=Path('tests/results/esp32c3-aac-asymmetric-production-20261004')
manifest=json.loads((root/'implementation.json').read_text())
rows=[]
for name,record in manifest['files'].items():
    path=Path(name)
    if not name.startswith('idf/') or 'aac' not in path.name.lower():continue
    old=root/record['snapshot']
    assert hashlib.sha256(old.read_bytes()).hexdigest()==record['sha256']
    current=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    rows.append(dict(path=name,reference=old.as_posix(),reference_sha256=record['sha256'],
                     current_sha256=current,identical=current==record['sha256']))
Path('.build/c3-raw-tail-quiet-20261015/evidence-audit/aac-source-comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Compared',len(rows),'captured AAC files;',sum(r['identical'] for r in rows),'identical')
for row in rows:
    if not row['identical']:print(row['path'])
