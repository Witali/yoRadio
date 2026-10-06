import hashlib
import json
from pathlib import Path
import shutil

root = Path.cwd()
out = root / '.build/flac-rolling/physical'
out.mkdir(parents=True, exist_ok=True)
specs = []
for folder, name in [('.build/flac-predictor/dense-long', 'flac-24bit-stereo-lpc32dense'),
                     ('.build/flac-rolling/irregular-long', 'flac-24bit-stereo-lpc32irregular'),
                     ('.build/flac-bounds/stress', 'stress-flac-48000-2ch-16bit-120s')]:
    folder = root / folder
    entry = next(e for e in json.loads((folder / 'manifest.json').read_text())['fixtures'] if e['name'] == name)
    source = folder / entry['file']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
    entry = dict(entry, file=source.name)
    shutil.copyfile(source, out / source.name)
    specs.append(entry)
(out / 'manifest.json').write_text(json.dumps(dict(fixtures=specs), indent=2)+'\n')
print('Combined', len(specs), 'verified synthetic fixtures')
