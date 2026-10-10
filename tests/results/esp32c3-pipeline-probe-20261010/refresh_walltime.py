"""Refresh the lab build after preserving initial-cycles evidence."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
assert (root/'initial-cycles/physical/restoration.json').exists()
hashes=json.loads((root/'source-hashes.json').read_text())
for name in hashes:
    data=Path(name).read_bytes();hashes[name]=hashlib.sha256(data).hexdigest()
    (root/'build-sources'/name).write_bytes(data)
(root/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
(root/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit=(root/'audit.py').read_text()
assert "OUT=ROOT/a.target;" in audit
audit=audit.replace('OUT=ROOT/a.target;', "OUT=ROOT/(a.target+'-walltime');")
(root/'audit.py').write_text(audit)
print('Refreshed sources for system timer build; initial evidence preserved')
