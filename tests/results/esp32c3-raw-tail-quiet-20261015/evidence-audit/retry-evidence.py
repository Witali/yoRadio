import hashlib,json,subprocess,sys
from pathlib import Path
out=Path('.build/c3-raw-tail-quiet-20261015/evidence-audit')
name=Path('tests/test-aac-asymmetric-production.py')
with (out/'retry-asymmetric.log').open('xb') as log:
    result=subprocess.run([sys.executable,'-B','-X','utf8',str(name)],stdout=log,stderr=subprocess.STDOUT,timeout=120)
record=dict(test=name.as_posix(),test_sha256=hashlib.sha256(name.read_bytes()).hexdigest(),
    exit_code=result.returncode,reason='Original run encountered a 132-byte Git LFS pointer. Hydrated the exact tracked application from local LFS storage; no code or assertion changed.',
    firmware_sha256=hashlib.sha256(Path('firmware/development/esp32c3-aac-asymmetric-owner/app.bin').read_bytes()).hexdigest())
(out/'retry-asymmetric.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
raise SystemExit(result.returncode)
