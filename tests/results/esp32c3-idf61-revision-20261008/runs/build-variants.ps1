$ErrorActionPreference = 'Stop'
$python = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe'
foreach ($mode in @('quiet','deep-sleep','rtc32k')) {
    $variant = "r9a97f6c54ec6-$mode"
    $buildName = "build-idf-6.1-$variant"
    $parameters = @{
        DependencyRoot = 'C:/Work/yoRadio/.idf'
        BuildDirectory = $buildName
        Sdkconfig = "$buildName/sdkconfig"
        SdkconfigDefaults = @('sdkconfig.defaults','sdkconfig.production.defaults')
        DeepSleepClock = $mode -in @('deep-sleep','rtc32k')
        Rtc32kCrystal = $mode -eq 'rtc32k'
        IdfArguments = @('-D','CMAKE_JOB_POOLS=compile_limit=2','-D','CMAKE_JOB_POOL_COMPILE=compile_limit','-D','CMAKE_JOB_POOL_LINK=compile_limit','build')
    }
    Write-Output "START build-$mode"
    & ./idf/esp32c3-oled-native/build.ps1 @parameters *> ".build/c3-idf-head-20261008/build-$mode.log"
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $mode" }
    & $python -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
    if ($LASTEXITCODE -ne 0) { throw "Firmware export failed: $mode" }
    & $python -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build "idf/esp32c3-oled-native/$buildName" --objdump $objdump --output ".build/c3-idf-head-20261008/verify-aac-$mode.json" *> ".build/c3-idf-head-20261008/verify-aac-$mode.log"
    if ($LASTEXITCODE -ne 0) { throw "AAC audit failed: $mode" }
    & $python -X utf8 tools/esp32c3_tests/verify_http_link.py --sdkconfig "idf/esp32c3-oled-native/$buildName/sdkconfig" --elf "idf/esp32c3-oled-native/$buildName/yoradio_esp32c3_oled_native.elf" --objdump $objdump --output ".build/c3-idf-head-20261008/verify-http-$mode.json" *> ".build/c3-idf-head-20261008/verify-http-$mode.log"
    if ($LASTEXITCODE -ne 0) { throw "HTTP audit failed: $mode" }
    Write-Output "END build-$mode"
}
