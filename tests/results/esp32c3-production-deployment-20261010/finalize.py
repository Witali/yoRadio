"""Record the installed production profile and preserve deployment evidence."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000')
DEST = Path('tests/results/esp32c3-production-deployment-20261010')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((ART/'manifest.json').read_text())
final = json.loads((ROOT/'deployment/final.json').read_text())
smoke = json.loads((ROOT/'deployment/playback.json').read_text())
assert smoke['result'] == 'PASS'
assert final['identity']['app_elf_sha256'] == manifest['image']['app_elf_sha256']
assert all(final['persistence'].values()) and len(final['states']) == 3
assert all(not s['audio'] for s in final['states'])
assert manifest['image']['sha256'] == sha(ART/'app.bin')
manifest.update(hardware_tested=True, production_qualified=False,
    qualification='Requested production profile installed via OTA; build/link and object-equivalence audits plus 60-second HE-AACv2 smoke pass. Public transport interruptions and earlier HE-AAC HTTPS headroom failures remain unresolved.',
    physical_report='docs/ESP32C3_PRODUCTION_DEPLOYMENT_20261010.md',
    evidence='tests/results/esp32c3-production-deployment-20261010',
    previous_normal_candidate='firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000',
    deployment_method='WebUI app-only OTA',
    installed_app_elf_sha256=final['identity']['app_elf_sha256'],
    settings_preserved=final['persistence'])
(ART/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
(ART/'.gitattributes').write_text('*.json -text\nsdkconfig -text\n')
assert not DEST.exists(), 'Preserve previous archive'
allowed = {'.py','.json','.jsonl','.log','.txt','.ps1','.c','.h','.cpp','.inc','.projbuild','.S'}
for source in sorted(ROOT.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts or source.suffix not in allowed:
        continue
    raw = source.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----', raw), source
    dest = DEST/source.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
(DEST/'.gitattributes').write_text('* -text -filter -whitespace\n')
index = {p.relative_to(DEST).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'index.json').write_text(json.dumps(index, indent=2)+'\n')
print('Saved installed firmware and',len(index),'evidence files')
