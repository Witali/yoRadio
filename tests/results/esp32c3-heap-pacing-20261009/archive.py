"""Archive completed pacing evidence using an explicit allowlist, without keys/config snapshots."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST = REPO/'tests/results/esp32c3-heap-pacing-20261009'
assert not DEST.exists(), 'Preserve previous evidence'
assert (ROOT/'physical/restoration.json').is_file(), 'Wait for production restoration'
assert not (ROOT/'physical/restoration-failure.json').exists(), 'Inspect restore failure first'
phases = json.loads((ROOT/'physical/phases.json').read_text())
assert [p['name'] for p in phases] == ['rate100', 'rate102']
assert all(p['code'] != 124 for p in phases), 'Inspect controller timeout first'
sources = {}
for label in ('rate100', 'rate102'):
    report = json.loads((ROOT/'physical'/label/'report.json').read_text())
    for path, expected in report['test_sources_sha256'].items():
        file = REPO/path
        assert file.is_relative_to(REPO)
        assert hashlib.sha256(file.read_bytes()).hexdigest() == expected, path
        sources['sources/'+path] = file
    for name in ('report.json', 'status.json', 'performance.json'):
        sources['physical/'+label+'/'+name] = ROOT/'physical'/label/name
    sources['physical/'+label+'.log'] = ROOT/'physical'/(label+'.log')
for name in ('initial.json', 'installed.json', 'phases.json', 'restoration.json'):
    sources['physical/'+name] = ROOT/'physical'/name
for name in ('physical.py', 'summarize.py', 'summary.json', 'archive.py',
             'pdm_clock_audit.py', 'pdm-clock-audit.json', 'pdm-clock-disassembly.txt',
             'linked-clock-evidence.json', 'staged-dma-tests.log', 'heap-correlation-tests.log'):
    sources[name] = ROOT/name
for file in (ROOT/'clock-sources').iterdir():
    assert file.is_file()
    sources['clock-sources/'+file.name] = file
for name in ('test-staged-dma.py', 'test-heap-receive-correlation.py'):
    sources['sources/tests/'+name] = REPO/'tests'/name
sources['sources/sustained_summary.py'] = REPO/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
index = dict(kind='Sequential physical 600-second HE-AACv2 HTTPS pacing comparison',
             git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
             scope='Same saved diagnostic QIO image for both rates; original verdicts retained. '
                   'Clock audit is source/binary evidence, not a live-register measurement.', files={})
for relative, file in sorted(sources.items()):
    blob = file.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', blob)
    target = DEST/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    index['files'][relative] = dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
print('Archived', len(index['files']), 'files')
