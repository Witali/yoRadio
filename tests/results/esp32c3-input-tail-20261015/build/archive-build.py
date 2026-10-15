import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-input-tail-20261015');dest=Path('tests/results/esp32c3-input-tail-20261015/build')
assert not dest.exists();dest.mkdir(parents=True)
for name in ('build.ps1','package.py','check-config.py','audit-timer.py','build-audit.json','config-comparison.json','aac-audit.json','http-audit.json','allocator-audit.json','timer-audit.json','timer-isr.disassembly.txt','allocator-audit.disassembly.txt','allocator-audit.rx-object.txt','aac-audit.log','http-audit.log','allocator-audit.log','build.log'):
    shutil.copyfile(base/name,dest/name)
for name in ('ca.pem','server.pem'):shutil.copyfile(Path('.build/c3-confirm-tls-lab-20261015/trust')/name,dest/name)
shutil.copytree('idf/esp32c3-oled-native/build-input-tail-lab-20261015/log',dest/'idf-logs')
for name in ('stream_encoded_router.h','stream_start.h','adaptive_input.c','adaptive_input.h','web_service.c','Kconfig.projbuild','audio_service.c','native_aac_decoder.c','native_aac_decoder.h','tls_input_reserve.c','tls_input_reserve.h','native_audio_output.c','audio_pipeline_probe.h'):
    p=dest/'sources'/name;p.parent.mkdir(exist_ok=True);shutil.copyfile(Path('idf/esp32c3-oled-native/main')/name,p)
m=json.loads(Path('firmware/development/esp32c3-idf61-input-tail-lab/manifest.json').read_text())
(dest/'provenance.json').write_text(json.dumps({'source_commit':m['source_commit'],'image':m['image'],'laboratory_only':True},indent=2)+'\n')
shutil.copyfile(Path(__file__),dest/'archive-build.py')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Archived input-tail build')
