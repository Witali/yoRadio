import hashlib,json,re,shutil,subprocess
from pathlib import Path
root=Path('.build/c3-radio-wifi-probe');build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-wifi-probe')
assert not build.exists();build.mkdir()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-radio/sdkconfig').read_text()
settings={'ESP_CONSOLE_NONE':None,'ESP_CONSOLE_USB_SERIAL_JTAG':'y','ESP_CONSOLE_UART_NONE':None,
'LOG_DEFAULT_LEVEL_NONE':None,'LOG_DEFAULT_LEVEL_INFO':'y','LOG_DEFAULT_LEVEL':'3','LOG_MAXIMUM_LEVEL':'3',
'FREERTOS_USE_TRACE_FACILITY':'y','FREERTOS_GENERATE_RUN_TIME_STATS':'y','YORADIO_CPU_PROFILE_HTTP':'y','YORADIO_NETWORK_HEAP_PROFILE':'y','YORADIO_WEB_TCP_PROBE':'y'}
for key,value in settings.items():
    config=re.sub(r'^(?:CONFIG_'+key+r'=.*|# CONFIG_'+key+r' is not set)\n?', '',config,flags=re.M)
    if key=='ESP_CONSOLE_UART_NONE':continue
    config+=('\n# CONFIG_'+key+' is not set\n') if value is None else '\nCONFIG_'+key+'='+value+'\n'
(build/'sdkconfig').write_text(config)
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_http_request_buffer.py'),Path('tools/patch_i2s_pdm_clock.py')]:
    if not path.is_file():continue
    raw=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(raw).hexdigest();dest=root/'sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
(root/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(root/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
shutil.copyfile('.build/c3-production-radio/export-used.py',root/'export-used.py')
print('Prepared diagnostic config and',len(sources),'source snapshots')
