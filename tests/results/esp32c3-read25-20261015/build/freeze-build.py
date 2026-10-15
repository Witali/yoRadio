import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-read25-20261015')
dest=Path('tests/results/esp32c3-read25-20261015/build')
art=Path('firmware/development/esp32c3-idf61-read25-diagnostic')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((base/'build-audit.json').read_text())['result']=='PASS'
assert json.loads((base/'http-reader/report.json').read_text())['result']=='PASS'
for n in ('host-25-current','host-250'):assert json.loads((base/n/'report.json').read_text())['passed']
assert not dest.exists();dest.mkdir(parents=True)
for n in ('host-25','host-25-fixed','host-25-current','host-250','http-reader'):
    shutil.copytree(base/n,dest/n)
for n in ('build.ps1','build-and-audit.py','package.py','check-config.py','build.log',
          'build-legacy-shell-failed.log','build-audit.json','config-comparison.json',
          'aac-audit.json','aac-audit.log','http-audit.json','http-audit.log',
          'allocator-audit.json','allocator-audit.log','allocator-audit.disassembly.txt',
          'allocator-audit.rx-object.txt','freeze-build.py'):
    shutil.copyfile(base/n,dest/n)
for n in ('idf/esp32c3-oled-native/main/Kconfig.projbuild',
          'tools/codec_benchmark/verify_aac_network_build.py',
          'tools/esp32c3_tests/verify_http_link.py',
          'tools/esp32c3_tests/verify_adaptive_input_link.py',
          'tests/native/stream_http_reader_test.c','tests/test-stream-http-reader.py'):
    saved=dest/'sources'/n;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(n,saved)
(art/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
m=json.loads((art/'manifest.json').read_text())
m['files']={p.name:sha(p) for p in art.iterdir() if p.is_file() and p.name!='manifest.json'}
(art/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
shutil.copyfile(art/'manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved build, successful tests and earlier harness/build failures')
