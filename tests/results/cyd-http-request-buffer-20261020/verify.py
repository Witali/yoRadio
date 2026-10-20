"""Verify this immutable evidence bundle; no SDK, tools or live sources required."""
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent


def main():
    manifest=json.loads((ROOT/'manifest.json').read_bytes())
    actual={path.relative_to(ROOT).as_posix() for path in ROOT.rglob('*') if path.is_file()}
    assert actual==set(manifest['files'])|{'manifest.json'},'Unexpected or missing archive files'
    for relative,expected in manifest['files'].items():
        path=ROOT/relative
        assert path.resolve().is_relative_to(ROOT),'Path escapes archive'
        raw=path.read_bytes()
        assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],relative
    catalog=json.loads((ROOT/'catalog.json').read_bytes())
    for item in catalog['files']:
        if item['payload'] is None:
            assert item['omitted_reason'] and item['sha256'] and item['bytes']>0
        else:
            raw=(ROOT/item['payload']).read_bytes()
            assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],item['source']
    target=(ROOT/'target/esp_http_client.c.obj').read_bytes()
    assert target[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<HH',target,16)==(1,94)
    assert hashlib.sha256(target).hexdigest()=='d7707c43bdbcc9ac1f0ab3f058d5f2fc446f7a4cea861f1741d69ca56fe4f1d2'
    for name,expected in manifest['raw_report_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    kept=sum(item['payload'] is not None for item in catalog['files'])
    print('PASS archive: '+str(len(manifest['files']))+' payload/metadata files; '+str(kept)+
          ' captured artifact files; '+str(len(catalog['files'])-kept)+' binary payloads omitted with hashes; Xtensa ET_REL94 retained')
    print('manifest SHA256 '+hashlib.sha256((ROOT/'manifest.json').read_bytes()).hexdigest())


if __name__=='__main__':main()
