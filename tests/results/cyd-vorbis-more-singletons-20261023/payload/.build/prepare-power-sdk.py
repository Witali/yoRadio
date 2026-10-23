from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = (root / '.build/export-runtime-c3.py').read_text(encoding='utf-8')
source = source.replace('esp32c3-oled-native-runtime-transfer', 'esp32c3-oled-native-network-power')
source = source.replace('native-runtime-transfer-20261018/HOST.md', 'network-power-transfer-20261019/README.md')
source = source.replace('export-runtime-c3.log', 'export-power-c3.log')
source = source.replace('runtime-production-c3', 'power-production-c3')
(root / '.build/export-power-c3.py').write_text(source, encoding='utf-8')

source = (root / '.build/qualify-runtime-sdk.py').read_text(encoding='utf-8')
source = source.replace('native-runtime-transfer-20261018', 'network-power-transfer-20261019')
source = source.replace('esp32-cyd2usb-native-runtime-transfer-', 'esp32-cyd2usb-native-network-power-')
source = source.replace('esp32c3-oled-native-runtime-transfer', 'esp32c3-oled-native-network-power')
source = source.replace('esp32-cyd2usb-native-ota-transfer-', 'esp32-cyd2usb-native-runtime-transfer-')
source = source.replace('esp32c3-oled-native-ota-transfer', 'esp32c3-oled-native-runtime-transfer')
source = source.replace("allowed={'LWIP_SNTP_MAX_SERVERS'}", "allowed={'YORADIO_FLAC_DECODER_ESPRESSIF','YORADIO_FLAC_DECODER_CUSTOM'}")
source = source.replace("        layouts[board]={}", "        units['power']=build/'esp-idf/native_network_power/CMakeFiles/__idf_native_network_power.dir/native_network_power.c.obj'\n        if board=='cyd': units['network-runtime']=build/'esp-idf/main/CMakeFiles/__idf_main.dir/network_runtime.c.obj'\n        layouts[board]={}")
source = source.replace('Time/private-Wi-Fi checkpoint:', 'N4 network/audio power checkpoint:')
(root / '.build/qualify-power-sdk.py').write_text(source, encoding='utf-8')

source = (root / '.build/inspect-runtime-layout.py').read_text(encoding='utf-8')
start = source.index("names=['native_wifi_request_io'")
end = source.index('\nresult={}', start)
source = source[:start]+"names=['native_network_power_snapshot_t','wifi_config_t']"+source[end:]
source = source.replace("(['time_settings_t','time_snapshot_t'] if board=='cyd' else ['runtime_time_settings_t'])",
                        "(['network_owner_t','network_snapshot_t','network_profiles_t'] if board=='cyd' else [])")
source = source.replace('native-runtime-transfer-20261018/SDK-layout.json', 'network-power-transfer-20261019/SDK-layout.json')
(root / '.build/inspect-power-layout.py').write_text(source, encoding='utf-8')

source = (root / '.build/verify-runtime-firmware-index.py').read_text(encoding='utf-8')
source = source.replace('esp32-cyd2usb-native-runtime-transfer-', 'esp32-cyd2usb-native-network-power-')
source = source.replace('esp32c3-oled-native-runtime-transfer', 'esp32c3-oled-native-network-power')
(root / '.build/verify-power-firmware-index.py').write_text(source, encoding='utf-8')
print('Prepared production qualification helpers')
