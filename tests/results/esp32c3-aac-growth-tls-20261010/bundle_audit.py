import hashlib,json,struct
from collections import Counter
from cryptography import x509
from cryptography.hazmat.primitives import serialization

def entries(data):
    first=struct.unpack_from('<I',data)[0]
    assert first>=4 and first%4==0
    offsets=struct.unpack_from('<'+str(first//4)+'I',data)
    assert offsets==tuple(sorted(offsets))
    result=[]
    for start,end in zip(offsets,(*offsets[1:],len(data))):
        n,k=struct.unpack_from('<HH',data,start)
        assert start+4+n+k==end
        result.append((data[start+4:start+4+n],data[start+4+n:end]))
    return Counter(result)

def verify_bundle(before,after,ca,output):
    original,current=entries(before.read_bytes()),entries(after.read_bytes())
    root=x509.load_pem_x509_certificate(ca.read_bytes())
    pair=(root.subject.public_bytes(),root.public_key().public_bytes(serialization.Encoding.DER,
                                                     serialization.PublicFormat.SubjectPublicKeyInfo))
    assert current==original+Counter([pair]),'Bundle change exceeds one explicit test CA'
    result=dict(result='PASS',public_entries=sum(original.values()),lab_entries=sum(current.values()),
                added_ca_sha256=hashlib.sha256(ca.read_bytes()).hexdigest(),
                scope='Normal trust entries retained byte-for-byte; exactly one supplied CA added')
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result
