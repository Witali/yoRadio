"""Archive completed prefill tests using an explicit, credential-free allowlist."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-input-prefill-20261009'
assert not DEST.exists(), 'Preserve existing evidence'
assert (ROOT/'physical/restoration.json').is_file()
assert not (ROOT/'physical/restoration-failure.json').exists()
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
sources={}
for phase in ('hev2-ten-minutes','matrix','heavy-flac','transitions-faults-websocket','switch'):
    report=json.loads((ROOT/'physical'/phase/'report.json').read_text())
    for relative,expected in report['test_sources_sha256'].items():
        path=REPO/relative
        assert path.resolve().is_relative_to(REPO.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        sources['sources/'+relative]=path
    for name in ('report.json','status.json','performance.json'):
        sources[f'physical/{phase}/{name}']=ROOT/'physical'/phase/name
    sources[f'physical/{phase}.log']=ROOT/'physical'/(phase+'.log')
for name in ('initial.json','installed.json','fractional-clock.json','phases.json',
             'settings-after-tests.json','restoration.json','controller-failure.json'):
    path=ROOT/'physical'/name
    if path.is_file(): sources['physical/'+name]=path
for name in ('physical.py','summarize.py','summary.json','verify_evidence.py','verified.json',
             'archive.py','build.ps1','build.log','audit_build.py','build-audit.json',
             'decoder-task-disassembly.txt','verify-aac.json','verify-aac.json.log',
             'verify-http.json','verify-http.json.log'):
    sources[name]=ROOT/name
for path in (ROOT/'host').rglob('*'):
    if path.is_file() and path.suffix in ('.py','.c','.h','.log','.json'):
        sources[path.relative_to(ROOT).as_posix()]=path
audit=json.loads((ROOT/'build-audit.json').read_text())
for relative,expected in audit['source_overlay_sha256'].items():
    path=REPO/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    sources['sources/'+relative]=path
for relative in ('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py',
                 'idf/esp32c3-oled-native/main/native_audio_output.c',
                 'idf/esp32c3-oled-native/sdkconfig.pdm-fractional-clock.defaults'):
    sources['sources/'+relative]=REPO/relative
build=REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-input-prefill500'
sources['build/i2s_pdm.c']=build/'yoradio_i2s/i2s_pdm.c'
for path in (build/'log').iterdir():
    assert path.is_file()
    sources['build/compiler-log/'+path.name]=path
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-input-prefill500'
for name in ('manifest.json','sdkconfig'):
    sources['build/'+name]=artifact/name
sources['save-head.py']=REPO/'.build/c3-idf-head-20261008/save-head.py'
index=dict(kind='Bounded initial encoded-input prefill on existing buffers',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='Host cancellation tests, actual linked code and physical playback diagnostics. '
          'Original failures retained; no acoustic capture. Keys and private settings excluded.',files={})
for relative,path in sorted(sources.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',blob)
    dest=DEST/relative
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(blob)
    index['files'][relative]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
