import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
dest=Path('tests/results/esp32c3-radio-rx-owner-build')
assert not dest.exists()
failure=json.loads((root/'build-audit-failure.json').read_text())
assert failure['result']=='FAIL' and failure['build_succeeded'] and not failure['flashed']
verify=Path('.build/c3-production-radio-mp3-http/verify_commit.py').read_text().replace(
    'tests/results/esp32c3-production-radio-mp3-http','tests/results/esp32c3-radio-rx-owner-build')
(root/'verify_commit.py').write_text(verify)
for source in sorted(root.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts:continue
    target=dest/source.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(source.read_bytes())
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Preserved failed link audit and',len(index),'evidence files')
