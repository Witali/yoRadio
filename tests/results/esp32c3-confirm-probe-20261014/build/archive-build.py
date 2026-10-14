"""Archive diagnostic provenance without copying private board settings."""
import hashlib, json, shutil
from pathlib import Path

base = Path('.build/c3-confirm-probe-20261014')
dest = Path('tests/results/esp32c3-confirm-probe-20261014/build')
assert not dest.exists(), 'Preserve existing evidence'
dest.mkdir(parents=True)
names = ('build.ps1', 'package.py', 'compare-config.py', 'audit-timer.py',
         'audit-pipeline.py', 'build-audit.json', 'config-comparison.json',
         'aac-audit.json', 'http-audit.json', 'allocator-audit.json',
         'timer-audit.json', 'timer-isr.disassembly.txt',
         'allocator-audit.disassembly.txt', 'allocator-audit.rx-object.txt',
         'aac-audit.log', 'http-audit.log', 'allocator-audit.log', 'build.log')
for name in names:
    shutil.copyfile(base/name, dest/name)
build = Path('idf/esp32c3-oled-native/build-confirm-probe-20261014')
shutil.copytree(build/'log', dest/'idf-logs')
for name in ('main/audio_pipeline_probe.h', 'main/native_audio_output.c',
             'main/audio_service.c', 'main/web_service.c'):
    target = dest/'sources'/name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path('idf/esp32c3-oled-native')/name, target)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads(Path('firmware/development/esp32c3-idf61-confirm-probe/manifest.json').read_text())
record = dict(source_commit=manifest['source_commit'], image=manifest['image'],
              diagnostic_only=True, qualification='No production timing claim',
              relative_build_directory=build.as_posix())
(dest/'provenance.json').write_text(json.dumps(record, indent=2)+'\n')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
shutil.copyfile(Path(__file__), dest/'archive-build.py')
checks = {p.relative_to(dest).as_posix(): sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'sha256.json').write_text(json.dumps(checks, indent=2)+'\n')
print(json.dumps(dict(files=len(checks), image=manifest['image'])))
