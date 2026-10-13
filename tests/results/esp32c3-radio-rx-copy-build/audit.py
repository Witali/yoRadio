"""Bound the RX diagnostic configuration relative to the production candidate."""
import hashlib,json,re
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parent
linked=json.loads((root/'link-final/report.json').read_text())
assert linked['result']=='PASS'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-rx-copy')
base=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-radio')
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-radio-rx-copy')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((root/'source-hashes.json').read_text())
for path,digest in sources.items():assert sha(Path(path))==digest,path
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
a,b=config(base/'sdkconfig'),config(build/'sdkconfig')
changes={k:[a.get(k),b.get(k)] for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)}
allowed=('CONFIG_CONSOLE_UART_NONE','CONFIG_FREERTOS_USE_STATS_FORMATTING_FUNCTIONS',
    'CONFIG_ESP_CONSOLE','CONFIG_LOG_','CONFIG_FREERTOS_USE_TRACE',
    'CONFIG_FREERTOS_GENERATE_RUN_TIME','CONFIG_FREERTOS_RUN_TIME',
    'CONFIG_FREERTOS_TASK_FUNCTION_WRAPPER','CONFIG_YORADIO_CPU_PROFILE_HTTP',
    'CONFIG_YORADIO_NETWORK_HEAP_PROFILE','CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS')
assert all(k.startswith(allowed) for k in changes),changes
for key in ('YORADIO_RX_BUFFER_DIAGNOSTICS','YORADIO_NETWORK_HEAP_PROFILE',
            'YORADIO_HTTP_RELEASE_REQUEST_BUFFER','YORADIO_PDM_FRACTIONAL_CLOCK',
            'ESPTOOLPY_FLASHMODE_QIO','ESP_CONSOLE_USB_SERIAL_JTAG'):
    assert b['CONFIG_'+key]=='y',key
for key in ('YORADIO_WEB_TCP_PROBE','YORADIO_DEEP_SLEEP_CLOCK','MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE'):
    assert b.get('CONFIG_'+key)!='y',key
with (build/'yoradio_esp32c3_oled_native.elf').open('rb') as f:
    elf=ELFFile(f);symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    assert symbols['owners']['st_size']==512
    assert symbols['s_tls_large_storage']['st_size']==17058
    for name in ('rx_buffer_diagnostic_poll','__wrap_wlanif_input','__wrap_pbuf_alloc','__wrap_mem_free'):
        assert name in symbols,name
    assert '__wrap_tcp_input' not in symbols
    assert b['CONFIG_LWIP_L2_TO_L3_COPY']=='y'
    assert linked['elf_sha256']==sha(build/'yoradio_esp32c3_oled_native.elf')
    sections={s.name:s['sh_size'] for s in elf.iter_sections() if s.name.startswith(('.dram0.','.iram0.','.rtc.'))}
bundle=build/'esp-idf/mbedtls/x509_crt_bundle'
assert bundle.read_bytes()==(base/'esp-idf/mbedtls/x509_crt_bundle').read_bytes()
manifest=json.loads((art/'manifest.json').read_text())
assert manifest['image']['bytes']<=1900544 and manifest['image']['sha256']==sha(art/'app.bin')
manifest.update(laboratory_only=True,production_qualified=False,hardware_tested=False,
    qualification='Build only; RX ownership diagnostics alter timing and RAM. Linked copy-mode wrappers verified; physical RX attribution pending.',
    config_changes=changes,source_overlay_sha256=sources,
    rx_owner_table_bytes=512,tls_rx_reserve_bytes=17058,trust_bundle_sha256=sha(bundle),
    bootloader_sha256=sha(art/'bootloader.bin'))
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
result=dict(result='PASS',scope='Configuration/link audit only; no physical attribution',
    changes=changes,sections=sections,image=manifest['image'],rx_owner_table_bytes=512)
(root/'build-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
