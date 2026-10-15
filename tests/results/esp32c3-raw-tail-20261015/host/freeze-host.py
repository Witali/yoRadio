import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-raw-tail-20261015');dest=Path('tests/results/esp32c3-raw-tail-20261015/host')
assert not dest.exists();dest.mkdir(parents=True)
assert 'Assertion' in (base/'before/failure.log').read_text()
for name in ('before','after','after-cancel','staging','start'):
    src=base/name
    if name!='before':assert json.loads((src/'report.json').read_text())['passed']
    for p in src.rglob('*'):
        if p.is_file() and p.suffix in ('.log','.json','.h','.c','.py'):
            target=dest/name/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
shutil.copyfile(__file__,dest/'freeze-host.py')
(dest/'README.md').write_text('''# Opaque FLAC/Ogg tail coalescing regression

`before` reproduces the packing failure on source commit 15de0c36. The captured
old router header and generated test unit are retained. `after` is the first
passing implementation, before the additional inter-call cancellation guard.
`after-cancel` tests the final implementation, including restoring an old queued
prefix if a generation changes between feeds. The final tests also cover
FLAC/Ogg codec/generation/EOF/drain barriers, eight 512-byte reads in three slots,
and 600,000 exact bytes with concurrent ownership transfers under ASan/UBSan.

`staging` verifies four held startup slots and a concurrent consumer; `start`
executes the actual send/finish paths with frame confirmation and queue pressure,
including FLAC/Ogg passthrough. These are host control-flow/byte-identity tests,
not decoder quality or hardware playback evidence.
''')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved failing regression and final passing ownership tests')
