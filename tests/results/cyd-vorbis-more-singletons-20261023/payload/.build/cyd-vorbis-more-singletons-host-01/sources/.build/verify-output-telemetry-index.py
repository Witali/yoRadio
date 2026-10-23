from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT=Path.cwd()
sha=lambda data:hashlib.sha256(data).hexdigest()
git=lambda *args,**kw:subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=ROOT,**kw)

def index_blobs(files):
    queries=''.join(':'+path.relative_to(ROOT).as_posix()+'\n' for path in files)
    result=git('cat-file','--batch',input=queries.encode())
    offset=0
    for path in files:
        end=result.index(b'\n',offset)
        header=result[offset:end].split()
        assert len(header)==3 and header[1]==b'blob',(path,header)
        size=int(header[2]);offset=end+1
        data=result[offset:offset+size];offset+=size+1
        yield path,data
    assert offset==len(result)

for name in ('cyd-flac-task-qemu-20261020','cyd-http-request-buffer-20261020','cyd-output-telemetry-20261020'):
    folder=ROOT/'tests/results'/name
    manifest=json.loads((folder/'manifest.json').read_text())
    files=sorted(path for path in folder.rglob('*') if path.is_file())
    assert {path.relative_to(folder).as_posix() for path in files}==set(manifest['files'])|{'manifest.json'}
    for relative,row in manifest['files'].items():
        assert sha((folder/relative).read_bytes())==(row if isinstance(row,str) else row['sha256'])
    for path,blob in index_blobs(files):assert blob==path.read_bytes(),path
    print('Verified raw Git evidence:',name,len(files),'files',flush=True)

common=Path(git('rev-parse','--git-common-dir').decode().strip())
if not common.is_absolute():common=(ROOT/common).resolve()
firmware=sorted((ROOT/'firmware/development').glob('esp32-cyd2usb-native-output-telemetry-*'))
assert len(firmware)==6
objects=set();raw_count=0;pointer_count=0
for folder in firmware:
    receipt=json.loads((folder/'manifest.json').read_text())
    assert receipt['build_check']=='PASS' and receipt['source_dirty'] is False
    for path,blob in index_blobs(sorted(path for path in folder.rglob('*') if path.is_file())):
        data=path.read_bytes()
        if path.suffix=='.bin':
            match=re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n',blob)
            assert match,(path,'Expected LFS pointer')
            digest=sha(data)
            assert match[1].decode()==digest and int(match[2])==len(data)
            obj=common/'lfs/objects'/digest[:2]/digest[2:4]/digest
            assert obj.read_bytes()==data,obj
            objects.add(digest);pointer_count+=1
        else:
            assert blob==data,path
            raw_count+=1
print('Verified six firmware variants:',raw_count,'raw metadata/log files,',pointer_count,
      'LFS pointers and',len(objects),'actual local LFS objects',flush=True)
