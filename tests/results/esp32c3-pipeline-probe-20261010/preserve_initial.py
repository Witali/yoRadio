"""Preserve the terminal CLI failure and initial cycle-counter build audit."""
import json,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
restored=json.loads((root/'physical/restoration.json').read_text())
assert restored['identity']['app_elf_sha256']=='76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b'
assert all(restored['persistence'].values()) and all(not s['audio'] for s in restored['states'])
assert json.loads((root/'physical/phase.json').read_text())['code']==2
dest=root/'initial-cycles'
assert not dest.exists()
files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
for p in files:
    q=dest/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-pipeline-probe')
(dest/'firmware-manifest.json').write_bytes((artifact/'manifest.json').read_bytes())
# All original files remain here. The revised controller uses a new directory.
print('Preserved CLI failure, successful restoration and cycle-counter build evidence')
