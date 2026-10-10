import gzip,hashlib,json,re,subprocess
from pathlib import Path
root=Path('.build/c3-rx-window-20261007')
target=Path('tests/results/esp32c3-tcp-rx-window-20261007')
target.mkdir(parents=True,exist_ok=False)
entries=[]
def save(path,relative):
    raw=path.read_bytes()
    assert not re.search(rb'-----BEGIN (?:RSA |ENCRYPTED )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]{32}',raw)
    relative=str(relative).replace('\\','/')
    packed=len(raw)>65536
    data=gzip.compress(raw,mtime=0) if packed else raw
    relative+=('.gz' if packed else '')
    dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    entries.append(dict(path=relative,raw_bytes=len(raw),stored_bytes=len(data),raw_sha256=hashlib.sha256(raw).hexdigest(),stored_sha256=hashlib.sha256(data).hexdigest()))
for folder in ('physical-lab-dynamic','physical-lab-static'):
    for path in sorted((root/folder).glob('*.json')):save(path,Path('runs')/path.relative_to(root))
for name in ('build-window.py','build-window.ps1','audit-bundles.py','physical-labs.py','final-board.py','summarize-labs.py','collect.py',
             'build-dynamic.log','build-static.log','verify-dynamic.json','verify-static.json','bundle-audit.json','lab-summary.json',
             'dynamic-alternate-heap.json','physical-labs.json','install-lab-dynamic.json','install-lab-static.json','restore-after-labs.json','final-board.json'):
    save(root/name,Path('runs')/name)
for name in ('ca.pem','server.pem'):
    save(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for path in [Path('.build/idf-upgrade')/n for n in ('install.py','save-build.py')]+[Path('.build/c3-memory-20261007')/n for n in ('network-base.defaults','rx-copy.defaults')]+[Path('.build/c3-tls-records-20261007')/n for n in ('static.defaults','lab-ca.defaults')]:
    save(path,Path('helpers')/path.name)
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in sorted(Path(folder).glob('*.py')):save(path,Path('sources')/path)
for path in sorted(Path('idf/esp32c3-oled-native').glob('sdkconfig*.defaults')):save(path,Path('sources')/path)
for name in ('tests/test-tls-record-server.py','tools/codec_benchmark/verify_aac_network_build.py'):
    save(Path(name),Path('sources')/name)
for mode in ('dynamic','static'):
    variant='esp32c3-idf-6.1-memory-icy-tlslab-rx4-'+mode
    artifact=Path('firmware/development')/variant
    m=json.loads((artifact/'manifest.json').read_text())
    assert hashlib.sha256((artifact/'app.bin').read_bytes()).hexdigest()==m['image']['sha256']
    assert hashlib.sha256((artifact/'sdkconfig').read_bytes()).hexdigest()==m['sdkconfig_sha256']
    for name in ('manifest.json','sdkconfig'):save(artifact/name,Path('firmware')/variant/name)
(target/'index.json').write_text(json.dumps(dict(base_source_commit='919c7f34ffe6452dd51e757031befc784a94c390',
    note='Original PASS/FAIL retained. Baseline RX4 images exclude the later HTTP guard. No private keys, broadcast audio or TLS secrets.',files=entries),indent=2)+'\n')
(target/'.gitattributes').write_text('** -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
for e in entries:
    data=(target/e['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==e['stored_sha256']
    raw=gzip.decompress(data) if e['path'].endswith('.gz') else data
    assert hashlib.sha256(raw).hexdigest()==e['raw_sha256']
print('ARCHIVE_VERIFIED',len(entries),'files',sum(e['stored_bytes'] for e in entries),'bytes')
