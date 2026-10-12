import hashlib,json,shutil
from pathlib import Path
root=Path('.build/c3-production-radio')
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-radio')
manifest=json.loads((art/'manifest.json').read_text())
manifest.update(build_audit='tests/results/esp32c3-production-radio-build/production-radio/build-audit.json',
    object_comparison='tests/results/esp32c3-production-radio-build/normalized-object-review.json',
    reproduction_command='idf/esp32c3-oled-native/build-production.ps1 -TestedRadioProfile',
    hardware_tested=False,production_qualified=False,
    qualification='Fresh build from the measured defaults; build/link/configuration checks passed. This exact application has not been installed or tested on hardware. Earlier hardware results concern the quiet-http-txrelease image.',
    source_note='Quiet production profile generated from defaults with -TestedRadioProfile; full compact AAC, QIO 80 MHz, fractional output, one-second prefill, no deep sleep.')
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(art/'.gitattributes').write_text('*.json -text -whitespace\nsdkconfig -text -whitespace\n')
logdir=Path(manifest['build_directory'])/'log'
for source in logdir.glob('*'):
    if source.is_file():
        dest=root/'idf-logs'/source.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest)
for name in ('manifest.json','sdkconfig'):
    shutil.copyfile(art/name,root/('artifact-'+name))
verify=Path('.build/c3-http-buffer-ota-soak/verify_commit.py').read_text().replace('tests/results/esp32c3-http-buffer-ota-soak','tests/results/esp32c3-production-radio-build')
(root/'verify_commit.py').write_text(verify)
dest=Path('tests/results/esp32c3-production-radio-build');assert not dest.exists()
assert json.loads((root/'normalized-object-review.json').read_text())['result']=='PASS'
for source in sorted(root.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts:continue
    target=dest/source.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index),'files')
