from pathlib import Path
root=Path(__file__).resolve().parents[1]
scripts={'run-ota-production.ps1':'run-runtime-production.ps1',
         'export-ota-c3.py':'export-runtime-c3.py',
         'qualify-ota-sdk.py':'qualify-runtime-sdk.py',
         'verify-ota-firmware-index.py':'verify-runtime-firmware-index.py'}
for old,new in scripts.items():
    source=(root/'.build'/old).read_text()
    source=source.replace('native-ota-transfer-20261018','native-runtime-transfer-20261018')
    source=source.replace('native-ota-transfer','native-runtime-transfer')
    source=source.replace('ota-production-','runtime-production-')
    source=source.replace('export-ota-c3.log','export-runtime-c3.log')
    if old=='qualify-ota-sdk.py':
        source=source.replace('esp32-cyd2usb-native-web-transfer','esp32-cyd2usb-native-ota-transfer')
        source=source.replace('esp32c3-oled-native-web-transfer','esp32c3-oled-native-ota-transfer')
        source=source.replace('allowed=set()',"allowed={'LWIP_SNTP_MAX_SERVERS'} if project=='esp32-cyd2usb-native' else set()")
    (root/'.build'/new).write_text(source)
    print(new)
