$ErrorActionPreference = 'Stop'
$python = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
$buildName = 'build-idf-6.1-r9a97f6c54ec6-rtc32k'
& ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $buildName -Sdkconfig "$buildName/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.production.defaults') -DeepSleepClock -Rtc32kCrystal -IdfArguments @('-D','CMAKE_JOB_POOLS=compile_limit=2','-D','CMAKE_JOB_POOL_COMPILE=compile_limit','-D','CMAKE_JOB_POOL_LINK=compile_limit','build')
if ($LASTEXITCODE -ne 0) { throw 'RTC build failed' }
& $python -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant r9a97f6c54ec6-rtc32k
if ($LASTEXITCODE -ne 0) { throw 'RTC export failed' }
foreach ($mode in @('deep-sleep','rtc32k')) {
    $folder = "idf/esp32c3-oled-native/build-idf-6.1-r9a97f6c54ec6-$mode"
    & $python -X utf8 tools/esp32c3_tests/verify_http_link.py --sdkconfig "$folder/sdkconfig" --elf "$folder/yoradio_esp32c3_oled_native.elf" --objdump $objdump --output ".build/c3-idf-head-20261008/verify-http-$mode.json"
    if ($LASTEXITCODE -ne 0) { throw "HTTP link audit failed: $mode" }
}
