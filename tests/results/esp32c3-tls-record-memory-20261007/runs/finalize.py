import hashlib, json, subprocess
from pathlib import Path
root=Path('.build/c3-tls-records-20261007')
data=subprocess.check_output(['git','show','8826d7cc:tools/audio_test_server/tls_records.py'])
# The public run started before the optional CLI was added. Reconstruct only
# that removed suffix and require the report's exact historical content hash.
data=data.split(b'\n\ndef main():')[0].rstrip(b'\r\n')+b'\n'
assert hashlib.sha256(data).hexdigest()=='df4a59ffb9a0cf52e3dd7a8d95e6ba9f43895266975dbd828f5ba3b8d0d44060'
(root/'record_server_before_cli.py').write_bytes(data)
for variant in ('memory-icy-static-profile','memory-icy-tlslab-dynamic','memory-icy-tlslab-static'):
    folder=Path('firmware/development/esp32c3-idf-6.1-'+variant)
    manifest=json.loads((folder/'manifest.json').read_bytes())
    manifest['qualification']='Physical tests retained; NOT production-qualified: public HE allocation failures or full-sized TLS record allocation failures'
    manifest['physical_report']='docs/ESP32C3_TLS_RECORD_MEMORY_20261007.md'
    (folder/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    if 'tlslab' in variant:
        (folder/'README.md').write_text('# Laboratory firmware only\n\nThis image includes an additional short-lived local test CA. Do not use it as\nproduction firmware. Regenerate the CA and rebuild for later TLS record tests;\ncertificate verification must remain enabled. Private keys are not included.\n\nFull-sized-record memory checks failed. See the\n[physical test report](../../../docs/ESP32C3_TLS_RECORD_MEMORY_20261007.md)\nand the exact manifest and sdkconfig beside this image.\n')
known={}
for folder in ('tools/esp32c3_tests','tools/audio_test_server'):
    for p in Path(folder).glob('*.py'):known[hashlib.sha256(p.read_bytes()).hexdigest()]=str(p)
for p in root.glob('*.py'):known[hashlib.sha256(p.read_bytes()).hexdigest()]=str(p)
provenance={}
for name in ('static-public','physical-lab-dynamic','physical-lab-static','negative-ca'):
    report=json.loads((root/name/'report.json').read_text())
    refs={}
    for path,value in report['test_sources_sha256'].items():
        assert value in known,(name,path,value)
        refs[path]=dict(sha256=value,snapshot=known[value])
    provenance[name]=refs
(root/'runner-source-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
original=Path('.build/c3-memory-20261007/verify-staged.py').read_text()
original=original.replace('esp32c3-icy-rx-memory-20261007','esp32c3-tls-record-memory-20261007')
original=original.replace("('memory-control-profile','memory-rxcopy-profile','compact-icy-debug','compact-icy-quiet',\n             'memory-icy-rxcopy-profile','memory-icy-rxcopy-quiet')", "('memory-icy-static-profile','memory-icy-tlslab-dynamic','memory-icy-tlslab-static')")
assert 'memory-control-profile' not in original
(root/'verify-staged.py').write_text(original)
print('Historical runner hashes verified; firmware qualification labels saved')
