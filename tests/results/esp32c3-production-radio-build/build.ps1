$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
& ./idf/esp32c3-oled-native/build-production.ps1 -TestedRadioProfile -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory build-idf-6.1-r9a97-production-radio -Sdkconfig build-idf-6.1-r9a97-production-radio/sdkconfig -FirmwareOutputDirectory firmware/development/esp32c3-idf-6.1-r9a97-production-radio -IdfArguments @('-D','PROJECT_VER=idf61-production-radio','-D','CMAKE_JOB_POOLS=compile_limit=4','-D','CMAKE_JOB_POOL_COMPILE=compile_limit','-D','CMAKE_JOB_POOL_LINK=compile_limit','-D','YORADIO_FLASH_MODE_PROBE=OFF','-D','YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF','build') *> .build/c3-production-radio/build.log
if ($LASTEXITCODE -ne 0) { throw 'Production profile build failed' }
& $py -B -X utf8 .build/c3-production-radio/export-used.py --version 6.1 --variant r9a97-production-radio
if ($LASTEXITCODE -ne 0) { throw 'Production profile export failed' }
Copy-Item -LiteralPath idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-radio/bootloader/bootloader.bin -Destination firmware/development/esp32c3-idf-6.1-r9a97-production-radio/bootloader.bin
& $py -B -X utf8 .build/c3-production-radio/audit.py --target production-radio *> .build/c3-production-radio/audit.log
if ($LASTEXITCODE -ne 0) { throw 'Production profile audit failed' }
Get-Content .build/c3-production-radio/audit.log -Tail 2
