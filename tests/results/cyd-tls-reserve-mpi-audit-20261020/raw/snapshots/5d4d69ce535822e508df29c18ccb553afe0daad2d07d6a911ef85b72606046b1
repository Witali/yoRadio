import datetime, hashlib, json, pathlib, sys
ROOT=pathlib.Path.cwd(); OUT=pathlib.Path(__file__).resolve().parent
SDK=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2'); DONOR=pathlib.Path('C:/Work/yoRadio/.idf/v6.1')
repo=[
 'idf/esp32c3-oled-native/main/'+name for name in ['tls_large_reserve.c','tls_large_reserve.h','tls_input_reserve.c','tls_input_reserve.h','Kconfig.projbuild','CMakeLists.txt','app_main.c','audio_service.c']]
repo+=['idf/esp32c3-oled-native/CMakeLists.txt','tools/patch_tls_rx_reserve.py','idf/esp32c3-oled-native/sdkconfig.tls-rx-reserve.defaults','idf/esp32c3-oled-native/sdkconfig.tls-large-reserve.defaults']
repo+=['idf/esp32-cyd2usb-native/main/'+name for name in ['CMakeLists.txt','Kconfig.projbuild','app_main.c','audio_service.c','native_input_reclaim.c','native_input_reclaim.h']]
repo+=['idf/esp32-cyd2usb-native/'+name for name in ['CMakeLists.txt','sdkconfig.defaults','build-c3-transfer/sdkconfig','build-c3-transfer/config/sdkconfig.h','build-c3-transfer/project_description.json','build-c3-transfer/compile_commands.json']]
sdk=[
 'tools/cmake/version.cmake','components/mbedtls/CMakeLists.txt','components/mbedtls/Kconfig',
 'components/mbedtls/port/esp_mem.c','components/mbedtls/port/include/esp_mem.h','components/mbedtls/port/include/mbedtls/esp_config.h',
 'components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.h','components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c','components/mbedtls/port/dynamic/esp_ssl_tls.c','components/mbedtls/port/dynamic/esp_ssl_cli.c','components/mbedtls/port/dynamic/esp_ssl_srv.c',
 'components/mbedtls/mbedtls/library/ssl_tls.c','components/mbedtls/mbedtls/library/ssl_msg.c','components/mbedtls/mbedtls/library/ssl_misc.h','components/mbedtls/mbedtls/include/mbedtls/ssl.h',
 'components/mbedtls/mbedtls/tf-psa-crypto/platform/platform.c','components/mbedtls/mbedtls/tf-psa-crypto/include/mbedtls/platform.h',
 'components/mbedtls/port/esp_psa_crypto_init.c','components/mbedtls/port/bignum/esp_bignum.c',
 'components/mbedtls/mbedtls/tf-psa-crypto/core/psa_crypto.c','components/mbedtls/mbedtls/tf-psa-crypto/core/psa_crypto_driver_wrappers_no_static.c',
 'components/esp_security/src/esp_crypto_lock.c','components/esp_security/include/esp_crypto_lock.h','components/esp_security/CMakeLists.txt',
 'components/esp_libc/src/locks.c','components/esp_libc/platform_include/sys/lock.h','components/esp_libc/src/init.c','components/esp_libc/src/picolibc/picolibc_init.c','components/esp_libc/CMakeLists.txt',
 'components/soc/esp32/include/soc/soc_caps.h','components/esp_system/startup.c',
 'components/freertos/FreeRTOS-Kernel/queue.c','components/freertos/app_startup.c']
state={'status':'frozen_before_detailed_analysis','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only stage13 TLS reserve/early MPI audit. AAC/deferred private owner-view excluded. No builds, crypto/network operations, SDK/config/Git/source mutations or device operations.','inputs':{},'missing_optional':[]}
def freeze(path,role,copy=True):
 path=path.resolve()
 if not path.is_file():state['missing_optional'].append(str(path));return
 raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest(); rec={'sha256':digest,'bytes':len(raw),'role':role}
 if copy:
  target=OUT/'snapshots'/digest; target.parent.mkdir(exist_ok=True);target.write_bytes(raw);rec['snapshot']=str(target.relative_to(OUT))
 state['inputs'][str(path)]=rec
for path in repo:freeze(ROOT/path,'repository source or existing build config/metadata')
for path in sdk:freeze(SDK/path,'pinned SDK6.0.2 source/header')
for name in ['esp_mbedtls_dynamic_impl.c','esp_mbedtls_dynamic_impl.h']:freeze(DONOR/'components/mbedtls/port/dynamic'/name,'donor SDK dynamic comparison')
freeze(pathlib.Path(__file__),'audit capture helper')
freeze(pathlib.Path(sys.executable),'Python metadata tool; hash only',False)
xt=pathlib.Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin')
for name in ['gcc','nm','objdump']:freeze(xt/('xtensa-esp32-elf-'+name+'.exe'),'target tool metadata; not executed',False)
for component in ['mbedtls','esp_security','esp_libc']:
 directory=ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer/esp-idf'/component
 for path in directory.glob('*.a'):freeze(path,'existing build archive identity only; not a new build or runtime proof',False)
state['python_version']=sys.version
(OUT/'capture.json').write_text(json.dumps(state,indent=2)+'\n')
print('Captured',len(state['inputs']),'inputs; missing optional',len(state['missing_optional']))
