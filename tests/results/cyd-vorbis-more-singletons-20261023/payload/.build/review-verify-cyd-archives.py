from pathlib import Path
import hashlib
import json

ROOT=Path.cwd()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
qemu=ROOT/'tests/results/cyd-flac-task-qemu-20261020'
manifest=json.loads((qemu/'manifest.json').read_text())
for original,row in manifest['source_mapping'].items():
    assert sha(Path(original))==row['sha256'],original
review='''# Parent review of the actual-task FLAC checkpoint

The parent reviewed the complete harness, linker wrappers, actual whole-TU
compile selection, runner input protection, source/fixture/compiler closure,
QEMU output parsing and original terminal result. No actionable defect was
found within this three-case scope. Archive hashes and all 474 currently bound
original source/dependency files were checked independently after copying.

The source hashes include the HTTP-buffer and telemetry integration later
committed in this branch; the earlier observed HEAD is not misrepresented as
the complete tested source. The usage README added after execution is a
documentation addition and was not an input to that historical campaign.

Actual decoder/client allocation and cleanup, original owner task profiles,
byte-exact output and public maintenance handoff execute. The HTTP/output/LED
seams are explicit. Disabled request-TX release is appropriate for synthetic
transport; its separate component qualification is required. This is three
lifecycle cases using three fixtures, not 130 actual-pipeline cases. There is
no claim of full-radio memory margin, physical IRQ/DMA, TLS network behavior,
audibility or performance. OOM, output backpressure and deliberate target
semantic controls remain open. This review did not rerun QEMU.
'''
(qemu/'REVIEW.md').write_text(review)
manifest['parent_review_included']=True
manifest['files']['REVIEW.md']={'sha256':sha(qemu/'REVIEW.md'),'bytes':(qemu/'REVIEW.md').stat().st_size}
(qemu/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for name in ('cyd-flac-task-qemu-20261020','cyd-http-request-buffer-20261020','cyd-output-telemetry-20261020'):
    base=ROOT/'tests/results'/name
    data=json.loads((base/'manifest.json').read_text())
    listed=data['files']
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==set(listed)|{'manifest.json'},name
    for relative,row in listed.items():
        path=base/relative
        digest=row if isinstance(row,str) else row['sha256']
        assert sha(path)==digest,(name,relative)
        if isinstance(row,dict) and 'bytes' in row:assert path.stat().st_size==row['bytes']
    print('VERIFIED',name,len(listed),'raw files',sha(base/'manifest.json'))
