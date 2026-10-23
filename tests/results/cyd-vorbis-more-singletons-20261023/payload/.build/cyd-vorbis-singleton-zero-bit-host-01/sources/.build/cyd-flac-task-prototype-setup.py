import pathlib,shutil,json,hashlib,re
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'.build/cyd-flac-task-qemu-01';out.mkdir(exist_ok=False)
frozen=out/'sources/repository'; project=out/'sources/project';(project/'main').mkdir(parents=True)
main=pathlib.Path('idf/esp32-cyd2usb-native/main')
names=['audio_service.c','audio_service.h','native_state.c','native_state.h','native_health.c','native_health.h','native_audio_output.c','native_audio_output.h','decoder_registration.c','decoder_registration.h','board_config.h','network_service.c','network_service.h','network_status.h','network_settings.h','input_prefill.h','Kconfig.projbuild','CMakeLists.txt']
paths=[root/main/n for n in names]
for comp in ['native_stream','native_network_power','native_wifi_store','custom_flac','custom_codec_support']:
 paths += [p for p in (root/'idf/components'/comp).rglob('*') if p.is_file()]
paths += [p for p in (root/'yoRadio/src/audioI2S/flac_decoder').glob('*') if p.is_file()]
paths += [root/'yoRadio/src/audioI2S'/n for n in ['CodecMemoryArena.cpp','CodecMemoryArena.h']]
paths += [root/'idf/components/audio_level_led/audio_level_led.h']
manifest={}
for p in paths:
 rel=p.relative_to(root);data=p.read_bytes();dest=frozen/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);manifest[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'snapshot':str(dest.relative_to(out))}
vendor=pathlib.Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec');vendordest=out/'sources/vendor/esp_audio_codec'
vfiles=[p for p in vendor.iterdir() if p.is_file()]+[p for folder in ['src','include','lib/esp32'] for p in (vendor/folder).rglob('*') if p.is_file()]
for p in vfiles:
 data=p.read_bytes();dest=vendordest/p.relative_to(vendor);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);manifest[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'snapshot':str(dest.relative_to(out))}
(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
blob=root/'.build/cyd-custom-flac-qemu-tracked-01/fixtures.bin';shutil.copyfile(blob,out/'fixtures.bin')
shutil.copyfile(root/'.build/cyd-custom-flac-qemu-tracked-01/fixture-manifest.json',out/'fixture-manifest.json')
(project/'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.16)
set(R "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}")
set(EXTRA_COMPONENT_DIRS "${R}/idf/components/native_stream" "${R}/idf/components/native_network_power"
 "${R}/idf/components/native_wifi_store" "${R}/idf/components/custom_flac"
 "${R}/idf/components/custom_codec_support" "$ENV{CYD_FLAC_TASK_VENDOR}")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cyd_flac_task_qemu)
''')
(project/'main/CMakeLists.txt').write_text('''set(M "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}/idf/esp32-cyd2usb-native/main")
idf_component_register(SRCS "main.cpp" "${M}/audio_service.c" "${M}/native_state.c" "${M}/native_health.c" "${M}/decoder_registration.c"
 INCLUDE_DIRS "." "${M}" "$ENV{CYD_FLAC_TASK_FROZEN_ROOT}/idf/components/audio_level_led"
 REQUIRES native_stream native_network_power native_wifi_store custom_flac custom_codec_support esp_audio_codec
 esp_http_client esp_ringbuf esp_timer esp_system esp_partition esp_driver_gpio mbedtls heap freertos log)
target_compile_definitions(${COMPONENT_LIB} PRIVATE FLAC_OUTPUT_FRAMES=512 FLAC_SEGMENTED_WORKSPACE=1)
foreach(symbol esp_http_client_init esp_http_client_open esp_http_client_fetch_headers esp_http_client_get_status_code
 esp_http_client_read esp_http_client_get_and_clear_last_tls_error esp_http_client_is_complete_data_received esp_http_client_cleanup
 custom_flac_decoder_create custom_flac_decoder_feed custom_flac_decoder_destroy xTaskCreatePinnedToCore)
 target_link_options(${COMPONENT_LIB} INTERFACE "-Wl,--wrap=${symbol}")
endforeach()
''')
(project/'main/Kconfig.projbuild').write_text('''menu "Actual CYD audio test profile"
config YORADIO_FLAC_DECODER_CUSTOM
 bool
 default y
config YORADIO_MP3_DECODER_ESPRESSIF
 bool
 default y
config YORADIO_AAC_DECODER_ESPRESSIF
 bool
 default y
config YORADIO_ADAPTIVE_INPUT_BUFFER
 bool
 default y
config YORADIO_FRAME_ROUTER
 bool
 default y
config YORADIO_STREAM_CONFIRM
 bool
 default y
config YORADIO_INPUT_TAIL_COALESCE
 bool
 default y
config YORADIO_INPUT_PREFILL_MS
 int
 default 0
endmenu
''')
defaults=(root/'tests/target/cyd_flac_qemu/project/sdkconfig.defaults').read_text()
defaults+='\nCONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y\nCONFIG_AUDIO_DECODER_AAC_SUPPORT=y\nCONFIG_AUDIO_DECODER_MP3_SUPPORT=y\nCONFIG_AUDIO_DECODER_FLAC_SUPPORT=y\nCONFIG_AUDIO_DECODER_OPUS_SUPPORT=y\nCONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y\nCONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y\n'
(project/'sdkconfig.defaults').write_text(defaults)
(project/'partitions.csv').write_text('nvs,data,nvs,0x9000,0x6000\nphy_init,data,phy,0xf000,0x1000\nfactory,app,factory,0x10000,0x1f0000\nfixtures,data,0x40,0x200000,0x200000\n')
build=(root/'tests/target/cyd_flac_qemu/sdk-build.ps1').read_text().replace("sources/harness/project","sources/project").replace("$env:CYD_FLAC_FROZEN_ROOT","$env:CYD_FLAC_TASK_FROZEN_ROOT")
build=build.replace("$env:IDF_PATH =", "$env:CYD_FLAC_TASK_VENDOR = Join-Path $output 'sources/vendor/esp_audio_codec'\n$env:IDF_PATH =")
(out/'sdk-build.ps1').write_text(build)
print(out)
