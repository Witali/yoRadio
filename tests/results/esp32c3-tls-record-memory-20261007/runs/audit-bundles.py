import hashlib, json, struct
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import serialization

root=Path('.build/c3-tls-records-20261007')
base=Path('idf/esp32c3-oled-native')
def read_bundle(variant):
    path=base/f'build-idf-6.1-{variant}/esp-idf/mbedtls/x509_crt_bundle'
    data=path.read_bytes()
    first,=struct.unpack_from('<I',data)
    assert first%4==0 and 0<first<len(data)
    count=first//4
    offsets=struct.unpack_from(f'<{count}I',data)
    entries=[]
    for index,offset in enumerate(offsets):
        name_len,key_len=struct.unpack_from('<HH',data,offset)
        end=offset+4+name_len+key_len
        assert end==(offsets[index+1] if index+1<count else len(data))
        entries.append(data[offset+4:end])
    assert len(set(entries))==len(entries)
    return set(entries),dict(path=str(path),bytes=len(data),certificates=count,sha256=hashlib.sha256(data).hexdigest())

normal,baseline=read_bundle('memory-icy-static-profile')
ca=x509.load_pem_x509_certificate((root/'trust/ca.pem').read_bytes())
expected=ca.subject.public_bytes()+ca.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
assert expected not in normal
result=dict(normal=baseline,images=[])
for mode in ('dynamic','static'):
    entries,evidence=read_bundle('memory-icy-tlslab-'+mode)
    assert entries==normal|{expected}
    evidence.update(laboratory_only=True,normal_roots_preserved=True,extra_ca_matches=True)
    result['images'].append(evidence)
result['result']='PASS'
(root/'bundle-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
