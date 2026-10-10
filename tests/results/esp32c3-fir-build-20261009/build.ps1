$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$build = 'build-idf-6.1-r9a97-fir32'
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', 'PROJECT_VER=idf61-fir32', '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=ON', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build')
if ($LASTEXITCODE -ne 0) { throw 'FIR build failed' }
& $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant r9a97-fir32
if ($LASTEXITCODE -ne 0) { throw 'FIR export failed' }
Copy-Item -LiteralPath "idf/esp32c3-oled-native/$build/bootloader/bootloader.bin" -Destination firmware/development/esp32c3-idf-6.1-r9a97-fir32/bootloader.bin
