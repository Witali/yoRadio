"""Freeze technical experiment evidence; do not copy private board snapshots."""
import hashlib,json,shutil
from pathlib import Path
root=Path('.build/c3-decoder-arena')
dest=Path('tests/results/esp32c3-shared-decoder-arena-20261012')
dest.mkdir(parents=True,exist_ok=False)
folders=['host-final','physical-96b','physical-96c','physical-baseline',
         'physical-baseline-2','physical-100']
for name in folders:
    for source in (root/name).rglob('*'):
        if not source.is_file() or source.suffix not in ('.json','.log','.c','.h','.py'):
            continue
        out=dest/source.relative_to(root)
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,out)
for name in ('link-audit.json','link-audit-100.json','review.json','review.py','freeze.py',
             'codec-object-comparison.json','compare-codecs.py','final-state.json',
             'resume-original-station.py','evidence-tests.log'):
    shutil.copyfile(root/name,dest/name)
for name in ('host-01','host-02','host-03','host-04','host-05'):
    for source in (root/name).glob('*.log'):
        out=dest/'host-attempts'/name/source.name
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,out)
sources=['idf/esp32c3-oled-native/main/decoder_arena.c',
         'idf/esp32c3-oled-native/main/decoder_arena.h',
         'tests/native/decoder_arena_test.c','tests/test-decoder-arena.py',
         'tests/check-decoder-arena-link.py','tests/test-decoder-arena-evidence.py',
         'tools/esp32c3_tests/decoder_arena_experiment.py']
for name in sources:
    out=dest/'sources'/name
    out.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(name,out)
manifest={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Frozen',len(manifest),'files')
