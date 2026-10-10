"""Save error definitions from the pinned SDK used to build this candidate."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

root=Path(__file__).resolve().parent
sdk=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
directory=sdk/'components/mbedtls/mbedtls'
wanted={'ssl.h':['MBEDTLS_ERR_SSL_CONN_EOF'],
        'net_sockets.h':['MBEDTLS_ERR_NET_CONN_RESET','MBEDTLS_ERR_NET_RECV_FAILED'],
        'x509.h':['MBEDTLS_ERR_X509_FATAL_ERROR']}
result=dict(idf_revision=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip(),
            mbedtls_revision=subprocess.check_output(['git','-C',str(directory),'rev-parse','HEAD'],text=True).strip(),files={})
for filename,names in wanted.items():
    path=directory/'include/mbedtls'/filename
    blob=path.read_bytes()
    lines=blob.decode().splitlines()
    definitions={}
    for name in names:
        for i,line in enumerate(lines):
            match=re.fullmatch(r'#define\s+'+name+r'\s+(-0x[0-9A-Fa-f]+)',line)
            if match:
                definitions[name]=dict(value=-int(match[1][1:],16),line=i+1,definition=line,comment=lines[i-1])
                break
        assert name in definitions
    result['files'][path.relative_to(sdk).as_posix()]=dict(sha256=hashlib.sha256(blob).hexdigest(),definitions=definitions)
(root/'sdk-error-codes.json').write_text(json.dumps(result,indent=2)+'\n')
print('Saved four error definitions from pinned SDK')
