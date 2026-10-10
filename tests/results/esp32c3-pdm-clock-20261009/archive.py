"""Preserve completed clock evidence and build inputs, excluding settings and keys."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST = REPO/'tests/results/esp32c3-pdm-clock-20261009'
assert not DEST.exists(), 'Preserve existing evidence'
assert (ROOT/'physical/restoration.json').is_file(), 'Wait for production restoration'
assert not (ROOT/'physical/restoration-failure.json').exists(), 'Inspect restore failure first'
phases = json.loads((ROOT/'physical/phases.json').read_text())
assert [p['name'] for p in phases] == ['integer', 'fractional']
assert all(p['code'] != 124 for p in phases), 'Inspect controller timeout first'
sources = {}
for mode in ('integer', 'fractional'):
    report = json.loads((ROOT/'physical'/mode/'report.json').read_text())
    for relative, expected in report['test_sources_sha256'].items():
        file = REPO/relative
        assert file.is_relative_to(REPO)
        assert hashlib.sha256(file.read_bytes()).hexdigest() == expected, relative
        sources['sources/'+relative] = file
    for name in ('report.json', 'status.json', 'performance.json'):
        sources[f'physical/{mode}/{name}'] = ROOT/'physical'/mode/name
    for suffix in ('.log', '-clock.json', '-installed.json'):
        sources['physical/'+mode+suffix] = ROOT/'physical'/(mode+suffix)
    for file in (ROOT/mode).iterdir():
        assert file.is_file() and file.suffix in ('.log', '.json', '.txt')
        sources['build/'+mode+'/'+file.name] = file
    build = REPO/f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-pdm-{mode}'
    sources['build/'+mode+'/i2s_pdm.c'] = build/'yoradio_i2s/i2s_pdm.c'
    for file in (build/'log').iterdir():
        assert file.is_file()
        sources['build/'+mode+'/compiler-log/'+file.name] = file
    artifact = REPO/f'firmware/development/esp32c3-idf-6.1-r9a97-pdm-{mode}'
    for name in ('manifest.json', 'sdkconfig'):
        sources['build/'+mode+'/'+name] = artifact/name
for name in ('initial.json', 'phases.json', 'restoration.json'):
    sources['physical/'+name] = ROOT/'physical'/name
for name in ('physical.py', 'summarize.py', 'summary.json', 'archive.py',
             'build.ps1', 'audit_build.py', 'build-audit.json', 'history.py', 'history.json',
             'sections.json', 'verify_evidence.py', 'verified.json'):
    sources[name] = ROOT/name
for file in (ROOT/'history-sources').rglob('*'):
    if file.is_file(): sources[str(file.relative_to(ROOT)).replace('\\','/')] = file
audit = json.loads((ROOT/'build-audit.json').read_text())
for relative, expected in audit['source_overlay_sha256'].items():
    file = REPO/relative
    assert hashlib.sha256(file.read_bytes()).hexdigest() == expected, relative
    sources['sources/'+relative] = file
for relative in ('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py',
                 'idf/esp32c3-oled-native/sdkconfig.pdm-fractional-clock.defaults',
                 'idf/esp32c3-oled-native/main/native_audio_output.c'):
    sources['sources/'+relative] = REPO/relative
sources['save-head.py'] = REPO/'.build/c3-idf-head-20261008/save-head.py'
index = dict(kind='Matched integer/fractional PDM clock experiment with two 600-second HE-AACv2 HTTPS runs',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='Actual configured clock register readback and playback diagnostics. '
          'No external clock, PCM or analog noise capture; original gates retained.', files={})
for relative, file in sorted(sources.items()):
    blob = file.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', blob)
    target = DEST/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    index['files'][relative] = dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
print('Archived',len(index['files']),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
