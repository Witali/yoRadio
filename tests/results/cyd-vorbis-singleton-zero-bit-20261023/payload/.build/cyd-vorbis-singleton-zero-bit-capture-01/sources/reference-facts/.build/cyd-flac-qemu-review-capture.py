import datetime,hashlib,json,pathlib
root=pathlib.Path.cwd();out=root/'.build/cyd-flac-qemu-independent-review-01';out.mkdir(parents=True,exist_ok=False)
evidence=root/'.build/cyd-custom-flac-qemu-tracked-01';raw=(evidence/'report.json').read_bytes();bundle=(evidence/'execution-bundle.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='13f63c393dca3ae5e154d3b9fc624555f879d6cfed6f51e97c6a560f6cbb327d'
assert hashlib.sha256(bundle).hexdigest()=='90b99c77226c3d03720b210fb5acaa0637d6a1fb90ee6607d0eaecaa00a9cca7'
source=json.loads(raw);hashes={}
for name,digest in source['source_sha256'].items():
    p=pathlib.Path(name);data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==digest,name
    relative=p.relative_to(root);target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);hashes[relative.as_posix()]=digest
target=out/'evidence';target.mkdir();(target/'report.json').write_bytes(raw);(target/'execution-bundle.json').write_bytes(bundle)
review={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent read-only review of the tracked classic dual-core ESP32 custom FLAC QEMU adapter/core checkpoint. Inspect actual source, generated image/config/commands and completed QEMU evidence without SDK builds, QEMU reruns, Git or board actions. Actual CYD decoder_task, OOM and deliberate target semantic-mutant runs remain open.','source_sha256':hashes,'report_sha256':hashlib.sha256(raw).hexdigest(),'execution_bundle_sha256':hashlib.sha256(bundle).hexdigest(),'findings':[]}
(out/'review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8');print('Frozen',len(hashes),'source inputs and exact completed report/bundle')
