$ErrorActionPreference = 'Stop'
$python = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$objdump = Get-ChildItem 'C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe' | Select-Object -First 1 -ExpandProperty FullName
foreach ($variant in @('production','qemu','deep-sleep','rtc32k')) {
    $defaults = @('sdkconfig.defaults')
    if ($variant -eq 'profile') {
        $defaults += @('sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults')
    } elseif ($variant -eq 'qemu') {
        $defaults += @('sdkconfig.qemu.defaults',[IO.Path]::GetFullPath('.build/idf-upgrade/qemu-compact.defaults'))
    } else {
        $defaults += 'sdkconfig.production.defaults'
    }
    $buildName = "build-idf-6.1-compact-ram-$variant"
    $parameters = @{
        DependencyRoot = 'C:/Work/yoRadio/.idf'
        BuildDirectory = $buildName
        Sdkconfig = "$buildName/sdkconfig"
        SdkconfigDefaults = $defaults
        DeepSleepClock = $variant -in @('deep-sleep','rtc32k')
        Rtc32kCrystal = $variant -eq 'rtc32k'
        IdfArguments = @('build')
    }
    Write-Output "START compact-ram-$variant"
    & ./idf/esp32c3-oled-native/build.ps1 @parameters *> ".build/idf-upgrade/build-6.1-compact-ram-$variant.log"
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $variant" }
    if ($variant -ne 'qemu') {
        & $python -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant "compact-ram-$variant"
        if ($LASTEXITCODE -ne 0) { throw "Firmware export failed: $variant" }
    }
    if ($variant -in @('production','profile')) {
        & $python -X utf8 tools/codec_benchmark/verify_aac_network_build.py --build "idf/esp32c3-oled-native/$buildName" --objdump $objdump --output ".build/idf-upgrade/verify-6.1-compact-ram-$variant.json" *> ".build/idf-upgrade/verify-6.1-compact-ram-$variant.log"
        if ($LASTEXITCODE -ne 0) { throw "Linked AAC verification failed: $variant" }
    }
    Write-Output "END compact-ram-$variant"
}
