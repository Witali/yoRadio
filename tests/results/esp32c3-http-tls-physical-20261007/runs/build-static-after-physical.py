import hashlib,json,subprocess,time
from pathlib import Path
root=Path('.build/c3-rfc-qualification-20261007')
deadline=time.monotonic()+1800
while not (root/'eof-fixed/final-board.json').exists():
    if time.monotonic()>deadline:raise SystemExit('No successful final board restoration; build not started')
    time.sleep(5)
assert json.loads((root/'eof-fixed/final-board.json').read_text())['result']=='PASS'
with (root/'build-static.log').open('xb') as log:
    result=subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build-static.ps1')],stdout=log,stderr=subprocess.STDOUT)
if result.returncode:raise SystemExit(result.returncode)
manifest=Path('firmware/development/esp32c3-idf-6.1-compact-icy-quiet-eof/manifest.json')
value=json.loads(manifest.read_text())
paths=['idf/esp32c3-oled-native/main/'+s for s in ('audio_service.c','CMakeLists.txt','stream_http_reader.c','stream_http_reader.h','tls_stream_eof.c')]
value['source_overlay_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
value['qualification']='Build and linked HTTP/TLS/AAC audits only. Static TLS, normal public roots; not installed or physically qualified.'
manifest.write_bytes((json.dumps(value,indent=2)+'\n').encode())
print('STATIC_TLS_BUILD_AND_LINK_AUDIT_COMPLETE',flush=True)
