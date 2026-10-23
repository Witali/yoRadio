import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
variants=['esp32-cyd2usb-native-web-transfer-'+b for b in ['pdm','continuous','legacy']]+['esp32c3-oled-native-web-transfer']
names=[]
for variant in variants:
    relative='firmware/development/'+variant
    manifest=json.loads((root/relative/'manifest.json').read_text())
    assert hashlib.sha256((root/relative/'app.bin').read_bytes()).hexdigest()==manifest['app_sha256']
    names.extend(p.decode() for p in subprocess.check_output(['git','ls-files','-z','--',relative],cwd=root).split(b'\0') if p)
payload=subprocess.check_output(['git','cat-file','--batch'],input=''.join(':'+n+'\n' for n in names).encode(),cwd=root)
common=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=root,text=True).strip())
if not common.is_absolute(): common=root/common
at=0;total=0;lfs=0
for name in names:
    end=payload.index(b'\n',at);header=payload[at:end].split();assert header[1]==b'blob'
    size=int(header[2]);blob=payload[end+1:end+1+size];at=end+size+2
    data=(root/name).read_bytes()
    if blob.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        match=re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n',blob)
        assert match,name
        oid=match[1].decode();assert hashlib.sha256(data).hexdigest()==oid and len(data)==int(match[2]),name
        stored=common/'lfs/objects'/oid[:2]/oid[2:4]/oid
        assert stored.read_bytes()==data,name
        lfs+=1
    else: assert blob==data,name
    total+=len(data)
assert at==len(payload) and len(names)>=32
print(json.dumps({'passed':True,'firmware_variants':4,'files':len(names),'bytes':total,'verified_local_lfs_objects':lfs,'worktree_matches_git_or_lfs_oid':True}))
