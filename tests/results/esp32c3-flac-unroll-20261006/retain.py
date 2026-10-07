import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

root = Path.cwd()
base = root / '.build/flac-unroll'
out = root / 'tests/results/esp32c3-flac-unroll-20261006'
sys.path.insert(0, str(root / 'tools/esp32c3_tests'))
from summarize_sustained import summarize

def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

out.mkdir(parents=True, exist_ok=True)
(out / '.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
for name in ('expanded-bounds', 'expanded-contiguous', 'matrix', 'dense-host', 'real24-large', 'verify'):
    folder = base / name
    for path in folder.rglob('*'):
        if path.is_file() and ('/sources/' in path.as_posix() or path.suffix in ('.json', '.log', '.asm')):
            copy(path, out / name / path.relative_to(folder))
for name in ('before', 'ota', 'after', 'regression', 'load16'):
    folder = base / name
    if name != 'ota':
        (folder / 'summary.json').write_text(json.dumps(summarize(folder), indent=2)+'\n')
    for path in folder.glob('*.json'):
        destination = out / name / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.name in ('performance.json', 'status.json'):
            destination.with_suffix('.json.gz').write_bytes(gzip.compress(path.read_bytes(), mtime=0))
        else:
            copy(path, destination)
    report = json.loads((folder / 'report.json').read_text())
    for name, digest in report['test_sources_sha256'].items():
        if Path(name).stem not in ('common', 'run', 'diagnostic', 'ota', 'ota_transition', 'serial_lines',
                                   'memory', 'server', 'fixtures', 'summarize_sustained', 'generate_stress'):
            continue
        data = (root / name).read_bytes()
        candidates = [data, data.replace(b'\r\n', b'\n'), data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')]
        data = next(c for c in candidates if hashlib.sha256(c).hexdigest() == digest)
        destination = out / 'runner-sources' / digest / Path(name).name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
copy(root / '.build/flac-predictor/dense-long/manifest.json', out / 'dense-fixture-manifest.json')
copy(root / '.build/flac-bounds/stress/manifest.json', out / 'stress-fixture-manifest.json')
copy(Path(__file__), out / 'retain.py')
manifest = {p.relative_to(out).as_posix(): dict(bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.rglob('*'))
            if p.is_file() and p != out / 'manifest.json'}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('Retained', len(manifest), 'files')
