import hashlib,json,re,subprocess,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path('.build/c3-radio-wifi-probe');build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-wifi-probe');base=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-radio');art=Path('firmware/development/esp32c3-idf-6.1-r9a97-radio-wifi-probe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in json.loads((root/'source-hashes.json').read_text()).items():assert sha(Path(path))==digest,path
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
a,b=config(base/'sdkconfig'),config(build/'sdkconfig');changes={k:[a.get(k),b.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
allowed=('CONFIG_CONSOLE_UART_NONE','CONFIG_FREERTOS_USE_STATS_FORMATTING_FUNCTIONS','CONFIG_ESP_CONSOLE','CONFIG_LOG_','CONFIG_FREERTOS_USE_TRACE','CONFIG_FREERTOS_GENERATE_RUN_TIME','CONFIG_FREERTOS_RUN_TIME','CONFIG_FREERTOS_TASK_FUNCTION_WRAPPER','CONFIG_YORADIO_CPU_PROFILE_HTTP','CONFIG_YORADIO_NETWORK_HEAP_PROFILE','CONFIG_YORADIO_WEB_TCP_PROBE')
assert all(k.startswith(allowed) for k in changes),changes
for key in ('YORADIO_WEB_TCP_PROBE','YORADIO_NETWORK_HEAP_PROFILE','YORADIO_HTTP_RELEASE_REQUEST_BUFFER','YORADIO_PDM_FRACTIONAL_CLOCK','ESPTOOLPY_FLASHMODE_QIO','ESP_CONSOLE_USB_SERIAL_JTAG'):
    assert b['CONFIG_'+key]=='y',key
assert b.get('CONFIG_YORADIO_DEEP_SLEEP_CLOCK')!='y'
elfpath=build/'yoradio_esp32c3_oled_native.elf'
with elfpath.open('rb') as f:
    elf=ELFFile(f);symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert symbols['s_events']['st_size']==1024 and symbols['s_tls_large_storage']['st_size']==17058
    assert 'web_tcp_probe_record_wifi' in symbols and '__wrap_tcp_input' in symbols
    sections={s.name:s['sh_size'] for s in elf.iter_sections() if s.name.startswith(('.dram0.','.iram0.','.rtc.'))}
bundle=build/'esp-idf/mbedtls/x509_crt_bundle';assert bundle.read_bytes()==(base/'esp-idf/mbedtls/x509_crt_bundle').read_bytes()
manifest=json.loads((art/'manifest.json').read_text());assert manifest['image']['bytes']<=1900544 and manifest['image']['sha256']==sha(art/'app.bin')
manifest.update(laboratory_only=True,production_qualified=False,hardware_tested=False,
    qualification='Build and host diagnostic checks only; physical capture pending. Extra runtime statistics/logging alter timing and memory relative to quiet production.',
    config_changes=changes,source_overlay_sha256=json.loads((root/'source-hashes.json').read_text()),
    tcp_wifi_ring_bytes=1024,tls_rx_reserve_bytes=17058,trust_bundle_sha256=sha(bundle),bootloader_sha256=sha(art/'bootloader.bin'))
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',scope='Build/configuration/link audit, not physical qualification',changes=changes,sections=sections,image=manifest['image'],ring_bytes=1024)
(root/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
