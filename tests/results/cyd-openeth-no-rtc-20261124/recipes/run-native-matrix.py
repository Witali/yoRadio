"""Bounded quiet three-output matrix with the final post-EOF health gate."""
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
for backend in ('pdm','continuous','legacy'):
    assert json.loads((BASE/backend/'qualification.json').read_bytes())['passed'] is True
results=[]
cases=[('legacy','run-he-ws2-post-eof'),('pdm','run-he-ws2-post-eof'),
       ('continuous','run-he-ws2-post-eof')]
for backend,label in cases:
    child=subprocess.run([sys.executable,'-u','-B',str(BASE/'run-native.py'),backend,label])
    assert child.returncode==0,'Native controller wrapper failed; original logs retained'
    report=json.loads((BASE/backend/label/'report.json').read_bytes())
    results.append(dict(backend=backend,label=label,state=report['state'],reason=report.get('reason')))
    (BASE/'native-matrix-progress.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results),flush=True)
