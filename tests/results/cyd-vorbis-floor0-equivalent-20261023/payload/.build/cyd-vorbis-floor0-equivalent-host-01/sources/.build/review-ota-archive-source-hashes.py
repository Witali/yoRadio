import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
folder=root/'tests/results/native-ota-transfer-20261018'
manifest=json.loads((folder/'archive-manifest.json').read_text())
checked=0
for name,group in manifest.items():
    if name=='files':continue
    for report_name in group['reports']:
        report=json.loads((folder/name/report_name).read_text())
        for field in ['source_sha256','sources']:
            hashes=report.get(field,{})
            if not isinstance(hashes,dict):continue
            for relative,expected in hashes.items():
                if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):continue
                archived=folder/name/'sources'/relative
                assert archived.is_file(),(name,relative,'missing frozen source')
                assert hashlib.sha256(archived.read_bytes()).hexdigest()==expected,(name,relative,'source mismatch')
                checked+=1
print(json.dumps({'passed':True,'frozen_source_hashes_verified':checked}))
