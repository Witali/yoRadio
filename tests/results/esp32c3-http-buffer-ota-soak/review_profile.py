import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
project=Path('idf/esp32c3-oled-native')
tested=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease/sdkconfig').read_bytes()
dest=ROOT/'profile-evidence';dest.mkdir(exist_ok=True)
hashes={}
for label,build in (
    ('fresh','build-idf61-radio-switch-audit'),
    ('reused','build-idf61-default-audit'),
    ('standard-control','build-idf61-standard-control')):
    raw=(project/build/'sdkconfig').read_bytes()
    digest=hashlib.sha256(raw).hexdigest();hashes[label]=digest
    if label=='standard-control':assert digest==json.loads((ROOT/'default-config-diff.json').read_text())['standard_sha256']
    else:assert raw==tested,label
    (dest/(label+'.sdkconfig')).write_bytes(raw)
sources={}
for name in ('build-production.ps1','build.ps1','sdkconfig.defaults','sdkconfig.production.defaults','sdkconfig.radio-tested.defaults','idf-revision.txt','idf-version.txt','idf-pin.ps1'):
    raw=(project/name).read_bytes();(dest/name).write_bytes(raw)
    sources[name]=hashlib.sha256(raw).hexdigest()
report=dict(result='PASS',scope='Real ESP-IDF reconfigure, no application compilation: fresh/reused selected profile exactly match tested sdkconfig; unselected default retains former hash',configs=hashes,sources=sources)
(ROOT/'profile-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
