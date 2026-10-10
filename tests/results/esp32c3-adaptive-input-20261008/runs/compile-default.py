import hashlib, json, subprocess
from pathlib import Path
root=Path('.build/c3-adaptive-input-20261008')
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-quiet')
entries=json.loads((build/'compile_commands.json').read_text())
entry=next(e for e in entries if e['file'].replace('\\','/').endswith('/main/audio_service.c'))
assert 'CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=y' not in (build/'sdkconfig').read_text()
output=(root/'audio-service-default.obj').resolve().as_posix()
command=entry['command'].replace('-o '+entry['output']+' -c ', '-o "'+output+'" -c ')
assert command!=entry['command']
result=subprocess.run(command,shell=False,cwd=entry['directory'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(root/'compile-default.log').write_bytes(result.stdout)
report=dict(passed=result.returncode==0,scope='Compile-only check of actual audio_service.c with ordinary quiet settings; no new application image.',
 command=command,source_sha256=hashlib.sha256(Path(entry['file']).read_bytes()).hexdigest(),
 sdkconfig_sha256=hashlib.sha256((build/'sdkconfig').read_bytes()).hexdigest())
(root/'compile-default.json').write_text(json.dumps(report,indent=2)+'\n')
print('DEFAULT_COMPILE',result.returncode)
raise SystemExit(result.returncode)
