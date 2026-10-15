import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015');src=base/'profile-wrapper'
out=Path('tests/results/esp32c3-raw-tail-quiet-20261015/profile-wrapper')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((src/'summary.json').read_text())
assert [r['mode'] for r in rows]==['fresh','cached'] and all(r['result']=='PASS' for r in rows)
assert not out.exists(),'Preserve evidence'
for row in rows:
    r=json.loads(Path(row['comparison']).read_text())
    assert not r['differences'] and sha(Path(r['actual']))==r['actual_sha256']
shutil.copytree(src,out)
for name in ('check-profile-wrapper.ps1','verify-profile-wrapper.py','compare-profile.py','freeze-profile-wrapper.py','apply-promotion.py'):
    shutil.copyfile(base/name,out/name)
promotion=json.loads((base/'profile-promotion.json').read_text())
for row in promotion['evidence']:
    relative=Path(row['report']).relative_to(base)
    parts=list(relative.parts)
    parts[0]={'https-radio':'public-radio','https-lc-repeat':'public-lc-repeat'}.get(parts[0],parts[0])
    archived=out.parent/Path(*parts)
    assert sha(archived)==row['sha256']
    row['archived_report']=archived.as_posix()
for name,digest in promotion['files'].items():
    assert sha(Path(name))==digest['candidate_sha256']
    saved=out/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
(out/'promotion.json').write_text(json.dumps(promotion,indent=2)+'\n')
for name in ('build-production.ps1','build.ps1','idf-pin.ps1'):
    p=Path('idf/esp32c3-oled-native')/name;dest=out/'sources'/p
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
(out/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(out/'sha256.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved fresh/cached wrapper and promotion evidence')
