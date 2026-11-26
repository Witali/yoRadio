"""Sequential terminal-evidence collection; wrapper success is not a resource PASS."""
import json
from pathlib import Path
import subprocess
import sys
BASE=Path(__file__).resolve().parent
release=json.loads((BASE/'runtime-release.json').read_bytes())
assert release['all_sdk_passed'] and set(release['profiles'])=={'legacy','pdm','continuous'}
results=[]
for backend in('legacy','pdm','continuous'):
    label='run-he-ws2-pbuf-01'
    child=subprocess.run([sys.executable,'-u','-B',str(BASE/'run-native.py'),backend,label])
    assert child.returncode==0,'Wrapper failed; raw controller evidence retained'
    report=json.loads((BASE/'native'/backend/label/'report.json').read_bytes())
    results.append(dict(backend=backend,label=label,state=report['state'],reason=report.get('reason')))
    (BASE/'native-matrix-progress.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results),flush=True)
