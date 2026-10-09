"""Freeze the measured image and host test inputs before further development."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={}
for file,key in [('physical/initial.json','test_sources_sha256'),
                 ('build-audit.json','source_overlay_sha256'),('host-min-prefill/report.json','source_sha256')]:
    for name,digest in json.loads((ROOT/file).read_text())[key].items():
        if name in sources: assert sources[name]==digest
        sources[name]=digest
for name in ('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py',
             'tests/test-pipeline-flow.py','tests/test-pipeline-flow-evidence.py'):
    sources[name]=sha(REPO/name)
for name,digest in sources.items():
    source=REPO/name
    assert source.resolve().is_relative_to(REPO.resolve()) and sha(source)==digest,name
    target=ROOT/'sources'/name
    if target.exists(): assert sha(target)==digest,name
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(source.read_bytes())
(ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
print('Frozen',len(sources),'source files')
