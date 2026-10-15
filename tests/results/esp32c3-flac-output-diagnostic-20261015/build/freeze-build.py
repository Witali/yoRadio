import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-flac-output-diagnostic-20261015')
art=Path('firmware/development/esp32c3-idf61-flac-output-diagnostic')
dest=Path('tests/results/esp32c3-flac-output-diagnostic-20261015/build')
assert not dest.exists();dest.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(art/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
m=json.loads((art/'manifest.json').read_text())
m['profile']+=' + PIPELINE_HEALTH_DIAGNOSTIC'
m['qualification']='Build/link and single-option configuration comparison passed. Diagnostic physical test pending; not a production-qualified image.'
m['files']={p.name:sha(p) for p in art.iterdir() if p.is_file() and p.name!='manifest.json'}
(art/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
for name in ('build.ps1','build.log','package.py','check-config.py','config-comparison.json','build-audit.json',
             'aac-audit.json','aac-audit.log','http-audit.json','http-audit.log',
             'allocator-audit.json','allocator-audit.log','allocator-audit.disassembly.txt','allocator-audit.rx-object.txt',
             'freeze-build.py'):
    shutil.copyfile(base/name,dest/name)
shutil.copytree('idf/esp32c3-oled-native/build-flac-output-diagnostic-20261015/log',dest/'idf-logs')
for name in ('tools/codec_benchmark/verify_aac_network_build.py','tools/esp32c3_tests/verify_http_link.py',
             'tools/esp32c3_tests/verify_adaptive_input_link.py','idf/esp32c3-oled-native/main/audio_pipeline_probe.h'):
    saved=dest/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
shutil.copyfile(art/'manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved diagnostic build and audited artifact')
