from pathlib import Path
import hashlib,json,subprocess
root=Path.cwd();out=root/'.build/audio-power-supplements-qualified';out.mkdir(exist_ok=False)
node=['tests/esp32c3-native-idf.test.js','tests/codec-benchmark.test.js','tests/native-wifi-editor.test.js','tests/esp32c3-web-static-workers.test.js','tests/wifi-ssid-warning.test.js','tests/webui-firmware-ota.test.js']
files=node+['tests/run-esp32c3-eof.py','tests/native/esp32c3_eof_test.c','idf/esp32c3-oled-native/main/audio_service.c','idf/esp32c3-oled-native/main/native_state.c']
files += [p.relative_to(root).as_posix() for p in (root/'idf/esp32c3-oled-native/main').glob('*.h')]
hashes={}
for name in files:
 p=root/name;data=p.read_bytes();hashes[name]=hashlib.sha256(data).hexdigest();dest=out/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
commands=[['node','--test',*node],['C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe','tests/run-esp32c3-eof.py']]
for name,command in zip(['node','eof'],commands):
 result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
 (out/(name+'.log')).write_bytes(result.stdout);assert result.returncode==0,result.stdout.decode(errors='replace')
assert b'# pass 73' in (out/'node.log').read_bytes()
for name,digest in hashes.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
(out/'report.json').write_text(json.dumps(dict(passed=True,node_tests=73,eof_passed=True,scope='Supplemental current-tree architecture/UI checks and actual C3 EOF/PCM-drain host regression. Named inputs are frozen and unchanged; Node tests also read other repository sources and are not represented as a standalone frozen behavioral proof.',source_sha256=hashes,commands=commands),indent=2)+'\n')
print('PASS Node73 and actual C3 EOF/PCM-drain gates; logs/source snapshots saved')
