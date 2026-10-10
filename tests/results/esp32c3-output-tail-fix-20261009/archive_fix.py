"""Preserve host and target-compiler evidence for the PCM boundary repair."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
DEST=REPO/'tests/results/esp32c3-output-tail-fix-20261009'
assert not DEST.exists()
promoted=json.loads((ROOT/'promoted.json').read_text())
files={}
for relative,hashes in promoted.items():
    path=REPO/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes['after_sha256'],relative
    files['sources/'+relative]=path
for group in ('candidate-tests-parity','candidate-tests-boundaries','candidate-tests-task2'):
    folder=ROOT/group
    report=json.loads((folder/'report.json').read_text())
    for relative,expected in report['sources'].items():
        path=folder/'sources'/relative
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        if 'sources/'+relative in files:
            assert files['sources/'+relative].read_bytes()==path.read_bytes(),relative
        files['sources/'+relative]=path
    for path in folder.iterdir():
        if path.is_file() and path.suffix in ('.c','.json','.log'):
            files['host/'+group+'/'+path.name]=path
for group in ('candidate-tests-task','negative-control','candidate-target-objects','candidate-target-objects2'):
    for path in (ROOT/group).iterdir():
        if path.is_file() and path.suffix in ('.c','.json','.log'):
            files['checks/'+group+'/'+path.name]=path
for name in ('archive_fix.py','prepare_fix.py','negative_control.py','compile_candidate.py',
             'promote_fix.py','promoted.json','reviewed-fix.diff'):
    files[name]=ROOT/name
index=dict(kind='PCM EOF/stream-boundary repair: host behavior and C3 object compilation',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='No final firmware linking or physical qualification for this repair. '
          'Negative control intentionally rejects the original staged EOF path. '
          'Initial test-header build failures retained alongside successful repairs.',files={})
for relative,path in sorted(files.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',blob)
    dest=DEST/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    index['files'][relative]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(files),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
