import json
from pathlib import Path
root=Path(__file__).resolve().parent
old=Path('.build/c3-prefill500-reneg-20261010')
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-pipeline-probe')
manifest=json.loads((artifact/'manifest.json').read_text())
source=(old/'physical.py').read_text()
source=source.replace('esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg',artifact.name)
source=source.replace('5096f10df159662a534a939f93da126c806345106b3b009af822ff00883a37c3',manifest['image']['sha256'])
source=source.replace("'--seconds', '75',", "'--seconds', '75', '--name', 'he-44100-stereo',")
(root/'physical.py').write_text(source)
(root/'review.py').write_bytes((old/'review.py').read_bytes())
print('Prepared two-case HE-AAC diagnostic experiment with exact restoration')
