import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
dest=Path('tests/results/esp32c3-radio-rx-copy-physical')
assert not dest.exists()
review=json.loads((root/'physical-review.json').read_text())
assert review['result']=='PASS' and not review['production_qualified']
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
for name in ('physical.py','prepare-physical.py','review-physical.py','physical-review.json','freeze-physical.py','write-report.py'):
    copy(root/name,dest/name)
for folder in ('physical','test-sources'):
    for p in sorted((root/folder).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:copy(p,dest/p.relative_to(root))
verify=Path('tests/results/esp32c3-radio-rx-copy-build/verify_commit.py').read_text().replace(
    'esp32c3-radio-rx-copy-build','esp32c3-radio-rx-copy-physical')
(dest/'verify_commit.py').write_text(verify)
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index),'physical evidence files including unchanged failed gates')
