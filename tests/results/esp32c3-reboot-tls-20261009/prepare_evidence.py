"""Capture fixture metadata and source evidence for shutdown ordering."""
import hashlib
import json
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
repo=Path.cwd()
catalog=json.loads((repo/'tests/results/esp32c3-min250-tls-ota-20261009/case-catalog.json').read_text())
(root/'fixture.json').write_text(json.dumps(catalog['hev2-44100-stereo'],indent=2)+'\n')
sdk=repo.parents[1]/'.idf/v6.1-9a97f6c54ec6'
assert sdk.is_dir()
files={
    'components/esp_system/esp_system.c':(40,58),
    'components/esp_wifi/src/wifi_default.c':(288,293),
    'components/mbedtls/mbedtls/library/net_sockets.c':(528,564),
}
result=dict(idf_revision=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip(),files={})
for name,(start,end) in files.items():
    path=sdk/name
    blob=path.read_bytes()
    lines=blob.decode().splitlines()
    result['files'][name]=dict(sha256=hashlib.sha256(blob).hexdigest(),
        line=start,end_line=end,excerpt=lines[start-1:end],header=lines[:12])
(root/'sdk-shutdown-review.json').write_text(json.dumps(result,indent=2)+'\n')
app=root/'application-sources'
app.mkdir(exist_ok=True)
for name in ('audio_service.c','websocket_service.c'):
    (app/name).write_bytes((repo/'idf/esp32c3-oled-native/main'/name).read_bytes())
print('Saved fixture, application source and pinned SDK shutdown evidence')
