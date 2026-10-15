"""Archive build inputs and public certificates; never copy private keys."""
import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-confirm-tls-lab-20261015')
dest=Path('tests/results/esp32c3-confirm-tls-lab-20261015/build')
assert not dest.exists(),'Preserve existing evidence'
dest.mkdir(parents=True)
names=('prepare.py','build.ps1','package.py','check-config.py','audit-timer.py',
       'build-audit.json','config-comparison.json','aac-audit.json','http-audit.json',
       'allocator-audit.json','timer-audit.json','timer-isr.disassembly.txt',
       'allocator-audit.disassembly.txt','allocator-audit.rx-object.txt',
       'aac-audit.log','http-audit.log','allocator-audit.log','build.log','trust-metadata.json')
for name in names:shutil.copyfile(base/name,dest/name)
for name in ('ca.pem','server.pem'):shutil.copyfile(base/'trust'/name,dest/name)
build=Path('idf/esp32c3-oled-native/build-confirm-tls-lab-20261015')
shutil.copytree(build/'log',dest/'idf-logs')
for name in ('main/audio_pipeline_probe.h','main/native_audio_output.c','main/audio_service.c','main/web_service.c'):
    target=dest/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(Path('idf/esp32c3-oled-native')/name,target)
manifest=json.loads(Path('firmware/development/esp32c3-idf61-confirm-tls-lab/manifest.json').read_text())
(dest/'provenance.json').write_text(json.dumps(dict(source_commit=manifest['source_commit'],
    image=manifest['image'],diagnostic_only=True,laboratory_only=True,
    qualification='No production timing claim; additional local CA expires 2026-10-17'),indent=2)+'\n')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
shutil.copyfile(Path(__file__),dest/'archive-build.py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
assert not any(name.endswith('.key') for name in files)
(dest/'sha256.json').write_text(json.dumps(files,indent=2)+'\n')
print('Archived',len(files),'build/public-certificate files')
