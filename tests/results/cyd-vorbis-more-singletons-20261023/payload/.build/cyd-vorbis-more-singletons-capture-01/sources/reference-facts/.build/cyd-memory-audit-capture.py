import datetime,hashlib,importlib.util,json,pathlib,sys
sys.dont_write_bytecode=True
root=pathlib.Path.cwd();out=root/'.build/cyd-memory-transfer-audit-01';out.mkdir(parents=True,exist_ok=False)
paths=[]
c3=pathlib.Path('idf/esp32c3-oled-native');cyd=pathlib.Path('idf/esp32-cyd2usb-native')
paths += [c3/'main'/n for n in ['tls_large_reserve.c','tls_large_reserve.h','tls_input_reserve.c','tls_input_reserve.h','http_request_buffer.h','adaptive_input.c','adaptive_input.h','audio_service.c','CMakeLists.txt','Kconfig.projbuild']]
paths += [c3/n for n in ['CMakeLists.txt','sdkconfig.defaults','sdkconfig.tls-large-reserve.defaults','sdkconfig.tls-rx-reserve.defaults']]
paths += [cyd/'main'/n for n in ['audio_service.c','CMakeLists.txt','Kconfig.projbuild','native_health.c','native_health.h']]
paths += [cyd/n for n in ['CMakeLists.txt','sdkconfig.defaults']]
paths += [pathlib.Path(n) for n in ['idf/components/native_stream/adaptive_input.c','idf/components/native_stream/include/adaptive_input.h','idf/components/native_stream/CMakeLists.txt','tools/patch_tls_rx_reserve.py','tools/patch_http_request_buffer.py','tests/run-tls-large-reserve.py','tests/native/tls_large_reserve_test.c','tests/native/http_request_buffer_test.c','tests/native/adaptive_input_test.c','tests/run-cyd-receive-runtime.py']]
paths += [pathlib.Path('firmware/development')/variant/n for variant in ['esp32c3-oled-native-ap-timeout','esp32-cyd2usb-native-network-settings-pdm'] for n in ['manifest.json','sdkconfig.json']]
hashes={}
for relative in paths:
    source=root/relative
    if not source.is_file():continue
    raw=source.read_bytes();target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);hashes[relative.as_posix()]=hashlib.sha256(raw).hexdigest()
sdkpaths=['components/esp_http_client/esp_http_client.c','components/esp_http_client/include/esp_http_client.h','components/mbedtls/port/esp_mem.c','components/mbedtls/port/include/esp_mem.h','components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.h','components/mbedtls/port/include/mbedtls/esp_config.h','components/mbedtls/port/dynamic/esp_ssl_tls.c','components/mbedtls/CMakeLists.txt']
sdkhashes={};normalized={}
for version in ['v6.0.2','v6.1-9a97f6c54ec6']:
    base=pathlib.Path('C:/Work/yoRadio/.idf')/version;normalized[version]={}
    for relative in sdkpaths:
        source=base/relative;raw=source.read_bytes();target=out/'sdk'/version/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);sdkhashes[str(source)]=hashlib.sha256(raw).hexdigest();normalized[version][relative]=hashlib.sha256(raw.decode().replace('\r\n','\n').encode()).hexdigest()
patches={}
for label,script,relative in [('http','tools/patch_http_request_buffer.py','components/esp_http_client/esp_http_client.c'),('tls-rx','tools/patch_tls_rx_reserve.py','components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c')]:
    spec=importlib.util.spec_from_file_location(label,out/'sources'/script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    patches[label]={}
    for version in normalized:
        raw=(out/'sdk'/version/relative).read_bytes()
        try:generated=module.patch(raw);patches[label][version]={'accepted':True,'generated_sha256':hashlib.sha256(generated).hexdigest()}
        except ValueError as error:patches[label][version]={'accepted':False,'error':str(error)}
configkeys=['IDF_TARGET','FREERTOS_UNICORE','MBEDTLS_DYNAMIC_BUFFER','MBEDTLS_INTERNAL_MEM_ALLOC','MBEDTLS_SSL_IN_CONTENT_LEN','MBEDTLS_SSL_OUT_CONTENT_LEN','YORADIO_ADAPTIVE_INPUT_BUFFER','YORADIO_HTTP_RELEASE_REQUEST_BUFFER','YORADIO_TLS_LARGE_BLOCK_RESERVE','YORADIO_TLS_RX_ONLY_RESERVE','YORADIO_TLS_RETAIN_RX_BUFFER','YORADIO_FLAC_INPUT_EXTRA_SLOTS','YORADIO_AAC_INPUT_EXTRA_SLOTS','YORADIO_INPUT_MIN_BLOCKS','ESP_WIFI_IRAM_OPT','ESP_WIFI_RX_IRAM_OPT','SPIRAM']
configs={}
for variant in ['esp32c3-oled-native-ap-timeout','esp32-cyd2usb-native-network-settings-pdm']:
    cfg=json.loads((out/'sources/firmware/development'/variant/'sdkconfig.json').read_text());configs[variant]={key:cfg.get(key,'not_defined') for key in configkeys}
report={'scope':'Independent read-only stage13 donor/CYD memory policy audit. No tracked/Git/SDK mutation, build or board operation. Frozen code/config and pinned SDK sources only; completed-image map observations are separate static evidence. No deferred AAC owner-view investigation.','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':hashes,'sdk_sha256':sdkhashes,'sdk_normalized_sha256':normalized,'existing_patch_acceptance_without_writing_sdk':patches,'saved_production_configs':configs,'findings':[],'candidates':[]}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'frozen_repository_files':len(hashes),'frozen_sdk_files':len(sdkhashes),'patch_acceptance':patches,'production_configs':configs},indent=2))
