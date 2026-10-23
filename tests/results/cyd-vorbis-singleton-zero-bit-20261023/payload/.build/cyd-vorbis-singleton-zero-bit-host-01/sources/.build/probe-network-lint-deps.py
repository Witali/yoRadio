import json,re,subprocess
from pathlib import Path
root=Path.cwd();build=root/'idf/esp32-cyd2usb-native/build-lint-network-vendor-final'
entries=json.loads((build/'compile_commands.json').read_text(encoding='utf-8'))
entry=next(e for e in entries if e['file'].replace('\\','/').endswith('/main/network_runtime.c'))
target=root/'.build/network-runtime-clang-deps.d'
command,count=re.subn(r' -o (?:"[^"]*"|\S+) -c ', ' -M -MT dependency -MF "'+target.as_posix()+'" ',entry['command'])
assert count==1
result=subprocess.run(command,cwd=entry['directory'],capture_output=True)
(root/'.build/network-runtime-clang-deps.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0,(result.returncode,result.stderr)
print(target.read_text(encoding='utf-8')[:1800])
