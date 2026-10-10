"""Freeze the rejected rate-compensation experiment and unchanged-default checks."""
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path.cwd()
ROOT = REPO/'.build/c3-integer-rate-20261009'
OUT = REPO/'tests/results/esp32c3-integer-rate-20261009'
assert not OUT.exists()
OUT.mkdir()
for folder in ('host-v2','default-regression'):
    for name in ('report.json','build.log','test.log','staged.log','dma.log','dma-profile.log',
                 'staged-profile.log','normalizer.log','normalizer-build.log',
                 'staged-build.log','dma-build.log','dma-profile-build.log','staged-profile-build.log'):
        src = ROOT/folder/name
        if src.exists():
            dest = OUT/folder/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dest)
    # Both successful runs use the same unchanged source bytes where shared.
    for src in (ROOT/folder/'sources').rglob('*'):
        if not src.is_file(): continue
        dest = OUT/'sources'/src.relative_to(ROOT/folder/'sources')
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): assert dest.read_bytes()==src.read_bytes(),dest
        else: shutil.copyfile(src,dest)
for name in ('filter-study.json','pdm-clock.log','node.log','freeze.py','README.md','replay.py'):
    shutil.copyfile(ROOT/name,OUT/name)
for name in ('tools/codec_benchmark/compare_integer_rate_filters.py','tools/patch_i2s_pdm_clock.py',
             'tests/test-pdm-clock.py','idf/esp32c3-oled-native/main/Kconfig.projbuild',
             'idf/esp32c3-oled-native/CMakeLists.txt'):
    dest=OUT/'sources'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(REPO/name,dest)
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(v['bytes'] for v in files.values()),'bytes')
