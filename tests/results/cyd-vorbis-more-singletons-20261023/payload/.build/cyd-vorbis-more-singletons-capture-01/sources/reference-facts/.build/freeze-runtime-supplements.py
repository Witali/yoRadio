import hashlib
import json
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
def copy(source,target):
    data=source.read_bytes()
    if target.exists(): assert target.read_bytes()==data,target
    else: target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
review=root/'.build/runtime-lint-review-campaign'
copy(root/'.build/runtime-lint-review.json',review/'report.json')
for name in ['review-runtime-lint.py','recover-runtime-lint.py','runtime-extra-webwifi-lint.py',
             'triage-json-boundaries.py','runtime-analysis-c3.out.log','runtime-analysis-cyd.out.log',
             'runtime-clang-config-cyd.out.log','runtime-clang-config-cyd.err.log']:
    copy(root/'.build'/name,review/name)
out=root/'.build/native-runtime-client-tests'
logs=['native-runtime-node-73.log','native-runtime-wifi-tools.log',
      'native-runtime-audit-tools.log','native-runtime-repeat-tools.log']
for name in logs: copy(root/'.build'/name,out/name)
paths=['tests/esp32c3-native-idf.test.js','tests/codec-benchmark.test.js','tests/native-wifi-editor.test.js',
       'tests/esp32c3-web-static-workers.test.js','tests/wifi-ssid-warning.test.js','tests/webui-firmware-ota.test.js',
       'tests/test-native-wifi-tools.py','tests/test-stream-probe-audit.py','tests/test-stream-probe-repeats.py',
       'tools/esp32c3_tests/common.py','tools/esp32c3_tests/ota.py','tools/esp32c3_tests/web_memory.py',
       'tools/esp32c3_tests/audit_stream_probe.py','tools/web/native_wifi_editor.js',
       'tools/update_native_wifi_web_assets.py','tools/update_wifi_ssid_warning_web_assets.ps1',
       'yoRadio/data/www/script.js.gz','idf/esp32c3-oled-native/main/CMakeLists.txt']
hashes={}
for relative in paths:
    path=root/relative;copy(path,out/'sources'/relative);hashes[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
report={'passed':True,'node_groups':73,'python_tool_cases':16,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'physical_hardware':False,'source_sha256':hashes,
        'scope':'Supplemental Node architecture/DOM and synthetic Python tooling checks; direct tests, edited UI/tool sources and manifest inputs frozen. Architecture tests also inspect repository source at the recorded commit; native executable campaigns and their frozen inputs qualify C behavior separately.'}
assert '# pass 73' in (out/logs[0]).read_text() and '# fail 0' in (out/logs[0]).read_text()
assert all('OK' in (out/name).read_text() for name in logs[1:])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Frozen supplemental client and lint-review evidence')
