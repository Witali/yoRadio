"""Freeze controlled TLS/OTA evidence without private keys or board settings."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-tls-final-gates-20261009'
assert not DEST.exists(), 'Preserve earlier evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
assert (ROOT/'physical/restoration.json').is_file()
assert not (ROOT/'physical/restoration-failure.json').exists()
sources={}
initial=json.loads((ROOT/'physical/initial.json').read_text())
for relative,expected in initial['test_sources_sha256'].items():
    path=REPO/relative
    assert path.resolve().is_relative_to(REPO.resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
    sources['sources/'+relative]=path
for phase in ('records-short','records-long','framing','certificate-rejection','ota','records-after-ota'):
    folder=ROOT/'physical'/phase
    for name in ('report.json','status.json','performance.json','serial-health.json','capture.json'):
        path=folder/name
        if path.is_file(): sources[f'physical/{phase}/{name}']=path
    for suffix in ('.log','-request-phases.jsonl','-transport-timing.json'):
        path=ROOT/'physical'/(phase+suffix)
        if path.is_file(): sources['physical/'+path.name]=path
for name in ('initial.json','installed.json','fractional-clock.json','phases.json',
             'settings-after-tests.json','restoration.json','controller-failure.json'):
    path=ROOT/'physical'/name
    if path.is_file(): sources['physical/'+name]=path
for name in ('physical.py','summarize.py','summary.json','verify_evidence.py',
             'verified.json','archive.py','replay.py','host-record-server.log',
             'host-ota-format.log','host-ota-health.log','host-tcp-after-failure.json'):
    sources[name]=ROOT/name
for relative in ('tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py',
                 'tests/test-tls-record-server.py','tests/test-ota-playback-format.py',
                 'tests/test-esp32c3-ota-serial-health.py',
                 'idf/esp32c3-oled-native/main/audio_service.c'):
    sources['sources/'+relative]=REPO/relative
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail'
for name in ('manifest.json','sdkconfig'):
    sources['build/'+name]=artifact/name
trust=REPO/'.build/c3-tls-records-20261007/trust'
for name,key,path in (('ca.pem','ca_sha256',trust/'ca.pem'),
                      ('server.pem','leaf_sha256',trust/'server.pem'),
                      ('untrusted.pem','untrusted_cert_sha256',ROOT/'untrusted/cert.pem')):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==initial[key]
    sources['public-certificates/'+name]=path
index=dict(kind='Controlled TLS records, HTTP closure and full HE-AACv2 HTTPS OTA',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='Original gates and strict service telemetry; failures retained. '
          'No acoustic capture, private settings or private keys.',files={})
# Validate the complete allowlist before creating the immutable destination.
blobs={}
for relative,path in sorted(sources.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob)
    blobs[relative]=blob
for relative,blob in blobs.items():
    destination=DEST/relative
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_bytes(blob)
    index['files'][relative]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
