"""Retain generated-config evidence without promoting or rebuilding the image."""
import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015')
out=Path('tests/results/esp32c3-raw-tail-quiet-20261015/profile-preflight')
assert not out.exists(),'Preserve evidence'
comparison=json.loads((base/'profile-preflight-comparison.json').read_text())
assert not comparison['differences']
out.mkdir()
for name in ('check-prepared-profile.ps1','compare-profile.py','profile-preflight.log',
             'profile-preflight-comparison.json','freeze-profile-preflight.py'):
    shutil.copyfile(base/name,out/name)
shutil.copyfile(base/'promotion-candidates/idf/esp32c3-oled-native/sdkconfig.radio-tested.defaults',out/'proposed-radio-tested.defaults')
shutil.copyfile(comparison['actual'],out/'generated.sdkconfig')
sources={}
for name in ('build.ps1','build-production.ps1','idf-pin.ps1','idf-version.json',
             'sdkconfig.defaults','sdkconfig.production.defaults','main/Kconfig.projbuild'):
    source=Path('idf/esp32c3-oled-native')/name
    if not source.is_file():continue
    target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    sources[source.as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
(out/'scope.json').write_text(json.dumps(dict(result='PASS',normalized_keys=1603,
    operation='Fresh ESP-IDF reconfigure with proposed profile; no application build or board operation',
    limitations=['Profile remains unapplied pending physical gates.',
        'Normal TestedRadioProfile wrapper fresh/reused configuration tests remain pending.',
        'Configuration equality is not binary identity or physical acceptance.'],sources=sources),indent=2)+'\n')
(out/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(out/'sha256.json').write_text(json.dumps({p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved proposed-profile preflight evidence')
