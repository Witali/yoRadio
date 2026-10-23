from pathlib import Path

root = Path(__file__).resolve().parents[1]
scripts = {
    'run-web-production.ps1': 'run-ota-production.ps1',
    'export-web-c3.py': 'export-ota-c3.py',
    'qualify-web-sdk.py': 'qualify-ota-sdk.py',
    'verify-web-firmware-index.py': 'verify-ota-firmware-index.py',
}
for old, new in scripts.items():
    source = (root / '.build' / old).read_text(encoding='utf-8')
    source = source.replace('native-web-transfer-20261018', 'native-ota-transfer-20261018')
    source = source.replace('native-web-transfer', 'native-ota-transfer')
    source = source.replace('web-production-', 'ota-production-')
    source = source.replace('export-web-c3.log', 'export-ota-c3.log')
    source = source.replace('HOST_GCC.md', 'HOST.md')
    # Compare against the last qualified WebUI profiles, not older PCM seeds.
    if old == 'qualify-web-sdk.py':
        source = source.replace('esp32-cyd2usb-native-startup-web-pcm-pdm', 'esp32-cyd2usb-native-web-transfer-pdm')
        source = source.replace('esp32-cyd2usb-native-startup-web-pcm-dac', 'esp32-cyd2usb-native-web-transfer-continuous')
        source = source.replace('esp32-cyd2usb-native-startup-web-pcm-legacy', 'esp32-cyd2usb-native-web-transfer-legacy')
        source = source.replace('esp32c3-oled-native-warning-fixes', 'esp32c3-oled-native-web-transfer')
        source = source.replace("allowed={'HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT','HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT','HTTPD_WS_STRICTER_RFC6455','YORADIO_NATIVE_WEBSOCKET_TRANSPORT'}", 'allowed=set()')
        source = source.replace('No physical heap/stack/timing/audio admission or full RFC conformance claim.', 'No physical OTA/flash, power-loss, heap/stack/timing or audio admission claim.')
    if old == 'run-web-production.ps1':
        source = source.replace("@('tests/results/native-ota-transfer-20261018/HOST.md','tests/results/native-ota-transfer-20261018/HOST.md')", "@('tests/results/native-ota-transfer-20261018/HOST.md')")
    (root / '.build' / new).write_text(source, encoding='utf-8')
    print(new)
