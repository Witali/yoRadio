$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$output = '.build/c3-pipeline-probe-20261010'
$target = 'quiet-pipeline-probe'
$variant = "r9a97-$target"
$build = "build-idf-6.1-$variant"
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', "PROJECT_VER=idf61-$target", '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=OFF', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build') *> "$output/build.log"
if ($LASTEXITCODE -ne 0) { throw 'Quiet build failed' }
& $py -X utf8 "$output/export-used.py" --version 6.1 --variant $variant
if ($LASTEXITCODE -ne 0) { throw 'Quiet export failed' }
Copy-Item -LiteralPath "idf/esp32c3-oled-native/$build/bootloader/bootloader.bin" -Destination "firmware/development/esp32c3-idf-6.1-$variant/bootloader.bin"
& $py -X utf8 "$output/audit.py" --target $target *> "$output/audit.log"
if ($LASTEXITCODE -ne 0) { throw 'Quiet audit failed' }
Get-Content "$output/audit.log" -Tail 3
