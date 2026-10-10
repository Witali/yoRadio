"""Prepare the same four-case campaign against the newly audited image."""
import json,shutil
from pathlib import Path
root=Path('.build/c3-prefill1000-reneg-20261010')
old=Path('.build/c3-prefill500-reneg-20261010')
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000-reneg')
manifest=json.loads((artifact/'manifest.json').read_text())
assert json.loads((root/'quiet-prefill1000-reneg/build-audit.json').read_text())['result']=='PASS'
source=(old/'physical.py').read_text().replace('esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg',artifact.name)
source=source.replace('5096f10df159662a534a939f93da126c806345106b3b009af822ff00883a37c3',manifest['image']['sha256'])
(root/'physical.py').write_text(source)
shutil.copyfile(__file__,root/'prepare_physical.py')
print('Prepared four-case HE-AAC/HE-AACv2 campaign with exact restoration')
