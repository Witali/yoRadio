import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
folder=root/'tests/results/native-web-transfer-20261018'
manifest=json.loads((folder/'archive-manifest.json').read_text())
paths=list(manifest['files'])
requests=''.join(':tests/results/native-web-transfer-20261018/'+p+'\n' for p in paths)
payload=subprocess.check_output(['git','cat-file','--batch'],input=requests.encode(),cwd=root)
at=0;total=0
for relative in paths:
    data=(folder/relative).read_bytes();expected=manifest['files'][relative]
    assert hashlib.sha256(data).hexdigest()==expected,relative
    end=payload.index(b'\n',at);header=payload[at:end].split();assert header[1]==b'blob',header
    size=int(header[2]);blob=payload[end+1:end+1+size];at=end+size+2
    assert hashlib.sha256(blob).hexdigest()==expected,relative
    total+=size
assert at==len(payload)
result={'passed':True,'raw_files':len(paths),'bytes':total,'worktree_and_staged_git_sha256_match':True}
(root/'.build/native-web-evidence-git.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
