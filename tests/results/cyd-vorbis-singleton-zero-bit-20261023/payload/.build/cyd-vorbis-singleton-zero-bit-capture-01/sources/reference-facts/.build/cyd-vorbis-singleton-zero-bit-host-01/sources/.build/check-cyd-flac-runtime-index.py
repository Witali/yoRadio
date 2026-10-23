from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();folder=root/'tests/results/cyd-flac-runtime-20261019';prefix=folder.relative_to(root).as_posix()+'/'
manifest=json.loads((folder/'archive-manifest.json').read_text());assert manifest['passed']
entries={}
for item in subprocess.check_output(['git','ls-files','--stage','-z','--',prefix]).split(b'\0'):
 if not item:continue
 header,path=item.split(b'\t',1);mode,sha,stage=header.decode().split();assert mode=='100644' and stage=='0';entries[path.decode()]=sha
expected={prefix+name for name in manifest['files']}|{prefix+'archive-manifest.json'}
assert set(entries)==expected,(len(entries),len(expected))
for name in expected:
 data=(root/name).read_bytes();digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert digest==entries[name],name
for name,row in manifest['files'].items():
 p=folder/name;assert len(p.read_bytes())==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
staged=set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines());assert staged==expected|{'.gitattributes'}
print('PASS',len(entries),'raw staged archive blobs and all manifest digests; only FLAC artifact paths staged')
