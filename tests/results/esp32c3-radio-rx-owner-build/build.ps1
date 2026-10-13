$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory build-idf-6.1-r9a97-radio-rx-owner -Sdkconfig build-idf-6.1-r9a97-radio-rx-owner/sdkconfig -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D','PROJECT_VER=idf61-radio-rx-owner','-D','CMAKE_JOB_POOLS=compile_limit=4','-D','CMAKE_JOB_POOL_COMPILE=compile_limit','-D','CMAKE_JOB_POOL_LINK=compile_limit','-D','YORADIO_FLASH_MODE_PROBE=OFF','-D','YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF','build') *> .build/c3-radio-rx-owner/build.log
if ($LASTEXITCODE -ne 0) { throw 'Diagnostic build failed' }
& $py -B -X utf8 .build/c3-radio-rx-owner/export-used.py --version 6.1 --variant r9a97-radio-rx-owner
if ($LASTEXITCODE -ne 0) { throw 'Diagnostic export failed' }
Copy-Item -LiteralPath idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-rx-owner/bootloader/bootloader.bin -Destination firmware/development/esp32c3-idf-6.1-r9a97-radio-rx-owner/bootloader.bin
