import hashlib, json, re, shutil
from pathlib import Path

roots = [Path('.build/c3-tls-reserve-20261008'), Path('.build/c3-tls-reserve-floor-20261008')]
out = Path('tests/results/esp32c3-tls-reserve-20261008')
assert not (out/'index.json').exists()
for root in roots:
    assert json.loads((root/'matrix/final-board.json').read_text())['result'] == 'PASS'
    for phase in ('physical', 'extended', 'repeat'):
        if (root/phase).exists():
            assert json.loads((root/phase/'final-board.json').read_text())['result'] == 'PASS'
out.mkdir(exist_ok=True)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p, rel):
    target = out/rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): assert sha(p) == sha(target)
    else: shutil.copyfile(p, target)

for root in roots:
    for p in root.rglob('*'):
        if p.is_file() and p.suffix in ('.json', '.jsonl', '.log', '.py', '.ps1', '.c', '.h', '.txt', '.projbuild'):
            copy(p, Path('runs')/root.name/p.relative_to(root))
for name in ('ca.pem', 'server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name, Path('public-certificates')/name)
for name in ('.build/c3-memory-20261007/network-base.defaults',
             '.build/c3-memory-20261007/rx-copy.defaults',
             '.build/c3-tls-records-20261007/lab-ca.defaults',
             '.build/idf-upgrade/install.py', '.build/c3-idf-head-20261008/save-head.py'):
    copy(Path(name), Path('build-inputs')/Path(name).name)
images = {}
for suffix in ('r9a97f6c54ec6-rx6-reserve', 'r9a97f6c54ec6-rx6-reserve-floor', 'compact-icy-quiet'):
    folder = Path('firmware/development')/('esp32c3-idf-6.1-'+suffix)
    for name in ('manifest.json', 'sdkconfig', 'qualification.json'):
        if (folder/name).exists(): copy(folder/name, Path('images')/folder.name/name)
    images[folder.name] = dict(app_sha256=sha(folder/'app.bin'), bytes=(folder/'app.bin').stat().st_size)
(out/'images.json').write_text(json.dumps(images, indent=2)+'\n')
wanted = set()
for p in out.rglob('*.json'):
    data = json.loads(p.read_text())
    if not isinstance(data, dict): continue
    for key in ('sources', 'sources_sha256', 'source_sha256', 'test_sources_sha256', 'source_overlay_sha256'):
        values = data.get(key, {})
        if isinstance(values, dict):
            wanted.update((name.replace('\\', '/'), expected) for name, expected in values.items()
                          if isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected))
candidates = {}
for root in roots + [Path('tests/results/esp32c3-adaptive-input-20261008/sources'),
                      Path('tests/results/esp32c3-idf61-revision-20261008/sources')]:
    for p in root.rglob('*'):
        if p.is_file() and p.suffix in ('.c', '.h', '.py', '.ps1', '.txt', '.defaults', '.projbuild'):
            candidates.setdefault(sha(p), p)
catalog = []
for name, expected in sorted(wanted):
    p = Path(name)
    if not p.is_file() or sha(p) != expected: p = candidates.get(expected)
    assert p and p.is_file() and sha(p) == expected, (name, expected)
    rel = Path('sources')/expected/Path(name).name
    copy(p, rel)
    catalog.append(dict(path=name, sha256=expected, snapshot=rel.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog, indent=2)+'\n')
index = {p.relative_to(out).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size)
         for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index, indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(v['bytes'] for v in index.values()),'bytes')
