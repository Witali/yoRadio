"""Promote the reviewed isolated fix only after prefill evidence is archived."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
required=REPO/'tests/results/esp32c3-input-prefill-20261009/verified.json'
assert required.is_file() and json.loads(required.read_text())['result']=='PASS'
assert json.loads((ROOT/'candidate-tests-parity/report.json').read_text())['pcm_identical']
assert json.loads((ROOT/'candidate-tests-boundaries/report.json').read_text())['pcm_identical']
assert all(c['result']=='PASS' for c in json.loads((ROOT/'candidate-target-objects2/report.json').read_text())['cases'])
files=['idf/esp32c3-oled-native/main/'+name for name in (
    'native_audio_output.c','native_audio_output.h','native_audio_output_qemu.c','audio_service.c')]
files+=['tests/native/output_dma/test.c','tests/native/output_dma/boundaries.c',
        'tests/native/output_task_boundaries.c','tests/run-output-task-boundaries.py',
        'tools/codec_benchmark/run_output_boundary_host.py']
diff=[];result={}
for relative in files:
    old=REPO/relative;new=ROOT/'candidate'/relative
    if old.exists():
        frozen=ROOT/'before'/relative
        assert frozen.exists(),relative
        assert old.read_bytes()==frozen.read_bytes(),relative
    before=old.read_text().splitlines(keepends=True) if old.exists() else []
    after=new.read_text().splitlines(keepends=True)
    diff.extend(difflib.unified_diff(before,after,fromfile='a/'+relative,tofile='b/'+relative))
    result[relative]=dict(before_sha256=hashlib.sha256(old.read_bytes()).hexdigest() if old.exists() else None,
                          after_sha256=hashlib.sha256(new.read_bytes()).hexdigest())
for relative in files:
    path=REPO/relative;path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/'candidate'/relative,path)
(ROOT/'reviewed-fix.diff').write_text(''.join(diff))
(ROOT/'promoted.json').write_text(json.dumps(result,indent=2)+'\n')
print('Promoted',len(files),'reviewed files')
