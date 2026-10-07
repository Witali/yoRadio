"""Archive numeric TLS/PCM/runtime evidence; never archive temporary private keys."""
import gzip, hashlib, json, re, subprocess
from pathlib import Path
root=Path('.build/c3-tls-records-20261007')
target=Path('tests/results/esp32c3-tls-record-memory-20261007')
target.mkdir(parents=True,exist_ok=True)
entries=[]
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,relative):
    raw=path.read_bytes()
    assert not re.search(rb'-----BEGIN (?:RSA |ENCRYPTED )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]{32}',raw)
    compressed=len(raw)>65536
    stored=gzip.compress(raw,mtime=0) if compressed else raw
    relative=str(relative).replace('\\','/')+('.gz' if compressed else '')
    dest=target/relative
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(stored)
    entries.append(dict(path=relative,raw_bytes=len(raw),stored_bytes=len(stored),raw_sha256=sha(raw),stored_sha256=sha(stored)))
for path in sorted(root.rglob('*')):
    if path.is_file() and path.suffix in ('.py','.ps1','.defaults','.json','.log'):
        save(path,Path('runs')/path.relative_to(root))
for name in ('ca.pem','server.pem'):
    save(root/'trust'/name,Path('public-certificates')/name)
for name in ('install.py','save-build.py','faad-reference-command.json'):
    save(Path('.build/idf-upgrade')/name,Path('helpers')/name)
for name in ('network-base.defaults','rx-copy.defaults'):
    save(Path('.build/c3-memory-20261007')/name,Path('helpers')/name)
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in sorted(Path(folder).glob('*.py')):save(path,Path('sources')/path)
for path in sorted(Path('idf/esp32c3-oled-native').glob('sdkconfig*.defaults')):save(path,Path('sources')/path)
for name in ('tests/test-tls-record-server.py','tools/codec_benchmark/verify_aac_network_build.py'):
    save(Path(name),Path('sources')/name)
for variant in ('memory-icy-static-profile','memory-icy-tlslab-dynamic','memory-icy-tlslab-static'):
    artifact=Path('firmware/development/esp32c3-idf-6.1-'+variant)
    manifest=json.loads((artifact/'manifest.json').read_text())
    assert sha((artifact/'app.bin').read_bytes())==manifest['image']['sha256']
    assert sha((artifact/'sdkconfig').read_bytes())==manifest['sdkconfig_sha256']
    for name in ('manifest.json','sdkconfig'):save(artifact/name,Path('firmware')/variant/name)
    directory=Path('idf/esp32c3-oled-native/build-idf-6.1-'+variant)
    for path in sorted((directory/'log').glob('idf_py_*')):
        if path.is_file():save(path,Path('build-logs')/variant/path.name)
    bundle=directory/'esp-idf/mbedtls/x509_crt_bundle'
    save(bundle,Path('certificate-bundles')/variant/'x509_crt_bundle.bin')
index=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    note='Original PASS/FAIL results retained. No broadcast audio, credentials, private keys or TLS secrets.',files=entries)
(target/'index.json').write_text(json.dumps(index,indent=2)+'\n')
(target/'.gitattributes').write_text('** -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
for entry in entries:
    data=(target/entry['path']).read_bytes()
    assert sha(data)==entry['stored_sha256']
    raw=gzip.decompress(data) if entry['path'].endswith('.gz') else data
    assert sha(raw)==entry['raw_sha256']
print('ARCHIVE_VERIFIED',len(entries),'files',sum(e['stored_bytes'] for e in entries),'bytes')
