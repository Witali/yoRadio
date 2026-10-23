import hashlib,json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
for board in ('cyd','c3'):
    directory=root/f'.build/lint-{board}-ota-transfer-full'
    path=directory/'report.json'
    if not path.is_file():continue
    report=json.loads(path.read_text())
    assert report['complete'] and report['errors']==0
    hashes={}
    for unit in report['results']:
        relative=unit['file'];source=root/relative
        dest=directory/'sources'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        data=source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=unit['source_sha256']:
            candidates=[dest,*sorted((root/'.build').glob('c3-maintenance-*/sources/'+relative))]
            data=next((p.read_bytes() for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==unit['source_sha256']),b'')
        assert hashlib.sha256(data).hexdigest()==unit['source_sha256'],relative
        if dest.exists():assert dest.read_bytes()==data
        else:dest.write_bytes(data)
        hashes[relative]=unit['source_sha256']
    config=root/'.clang-tidy';data=config.read_bytes()
    assert hashlib.sha256(data).hexdigest()==report['config_sha256']
    (directory/'.clang-tidy').write_bytes(data)
    (directory/'source-manifest.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(board,len(hashes),'source snapshots matched lint report')
