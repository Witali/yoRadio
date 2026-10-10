import hashlib
import json
from pathlib import Path
import re

root = Path('.build/c3-tick-20261008')
out = Path('tests/results/esp32c3-freertos-tick-20261008')
summary = json.loads((root/'summary.json').read_text())
assert summary['complete']
assert not (out/'index.json').exists(), 'Preserve earlier completed evidence'
out.mkdir(parents=True,exist_ok=True)
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source, name):
    target = out/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(source.read_bytes())

for tick in (2,5):
    final = json.loads((root/('tick'+str(tick))/'physical/final-board.json').read_text())
    assert final['result'] == 'PASS'
    image = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tick'+str(tick))
    manifest = json.loads((image/'manifest.json').read_text())
    assert digest(image/'app.bin') == manifest['image']['sha256']
    cases = [c for c in summary['cases'] if c['tick_ms']==tick]
    assert len(cases)==2
    assert all(c['board']['app_elf_sha256']==manifest['image']['app_elf_sha256'] for c in cases)
    manifest['qualification'] = 'Physical heavy-case comparison completed; laboratory-only, NOT_QUALIFIED. See docs/ESP32C3_FREERTOS_TICK_20261008.md.'
    qualification = json.loads((image/'qualification.json').read_text())
    qualification.update(physical_tests=True, report='docs/ESP32C3_FREERTOS_TICK_20261008.md',
        evidence=out.as_posix(),restoration='PASS',
        original_failures=[dict(case=c['case'],name=g['name'],reason=g.get('reason'))
            for c in cases for g in c['original_acceptance'] if g['result']!='PASS'])
    for name,data in (('manifest.json',manifest),('qualification.json',qualification)):
        (image/name).write_bytes((json.dumps(data,indent=2)+'\n').encode())
    for name in ('manifest.json','qualification.json','sdkconfig'):
        copy(image/name,Path('images')/image.name/name)

for source in root.rglob('*'):
    if source.is_file() and '__pycache__' not in source.parts:
        assert source.suffix in ('.py','.ps1','.log','.json','.jsonl','.txt')
        copy(source,Path('runs')/source.relative_to(root))
for name in ('.build/idf-upgrade/install.py','.build/c3-idf-head-20261008/save-head.py',
             '.build/c3-memory-20261007/network-base.defaults',
             '.build/c3-memory-20261007/rx-copy.defaults',
             '.build/c3-tls-records-20261007/lab-ca.defaults'):
    copy(Path(name),Path('build-inputs')/Path(name).name)
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)

wanted = set()
for source in list(out.rglob('*.json')):
    data = json.loads(source.read_text())
    if isinstance(data,dict):
        for key in ('test_sources_sha256','source_overlay_sha256'):
            wanted.update(data.get(key,{}).items())
for name in ('tools/esp32c3_tests/staged_dma.py','tools/esp32c3_tests/summarize_radio_flac.py'):
    wanted.add((name,digest(Path(name))))
source_index = []
for name,expected in sorted(wanted):
    assert re.fullmatch('[a-f0-9]{64}',expected)
    source = Path(name)
    assert digest(source)==expected,(name,expected)
    target = Path('sources')/expected/source.name
    copy(source,target)
    source_index.append(dict(path=name,sha256=expected,snapshot=target.as_posix()))
(out/'source-index.json').write_text(json.dumps(source_index,indent=2)+'\n')
references = []
for name in ('esp32c3-rxonly-long-20261008','esp32c3-staged-dma-profile-20261008'):
    p = Path('tests/results')/name/'index.json'
    references.append(dict(path=p.as_posix(),sha256=digest(p)))
(out/'baseline-references.json').write_text(json.dumps(references,indent=2)+'\n')
entries = {p.relative_to(out).as_posix():dict(sha256=digest(p),bytes=p.stat().st_size)
    for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries,indent=2)+'\n')
print('ARCHIVED',len(entries),'files',sum(e['bytes'] for e in entries.values()),'bytes')
