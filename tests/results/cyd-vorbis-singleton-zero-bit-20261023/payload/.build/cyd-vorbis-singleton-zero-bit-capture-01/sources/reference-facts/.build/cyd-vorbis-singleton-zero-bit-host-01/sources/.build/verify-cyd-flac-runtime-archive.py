from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();dest=root/'tests/results/cyd-flac-runtime-20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for group in ['host','vendor-regression']:
 report=json.loads((dest/group/'report.json').read_text())
 for name,expected in report['source_sha256'].items():
  assert sha(dest/group/'sources'/name)==expected,(group,name)
report=json.loads((dest/'host/report.json').read_text())
for name,expected in report['generated_sha256'].items():assert sha(dest/'host'/name)==expected,name
for mode in ['custom','vendor']:
 report=json.loads((dest/'sdk'/mode/'integration-compile.json').read_text())
 assert sha(dest/'sdk'/mode/'sdkconfig')==report['sdkconfig_sha256']
 assert sha(dest/'sdk'/mode/'config/sdkconfig.json')==report['config_json_sha256']
 for row in report['units']:assert sha(dest/'sdk/sources'/row['source'])==row['sha256']
files={p.relative_to(dest).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in dest.rglob('*') if p.is_file() and p.name!='archive-manifest.json'}
(dest/'archive-manifest.json').write_text(json.dumps(dict(passed=True,files=files),indent=2)+'\n')
print('PASS',len(files),'archived files and all source/generated/config digests')
base=subprocess.check_output(['git','show','HEAD:idf/esp32-cyd2usb-native/main/CMakeLists.txt'],text=True)
assert '    custom_flac\n' not in base
(root/'.build/flac-cmake-index.txt').write_bytes(base.replace('    custom_legacy_codecs\n','    custom_legacy_codecs\n    custom_flac\n',1).encode())
base=subprocess.check_output(['git','show','HEAD:.gitattributes'],text=True)
assert '/tests/results/cyd-flac-runtime-20261019/' not in base
(root/'.build/flac-attributes-index.txt').write_bytes((base.rstrip()+'\n\n/tests/results/cyd-flac-runtime-20261019/** -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n').encode())
