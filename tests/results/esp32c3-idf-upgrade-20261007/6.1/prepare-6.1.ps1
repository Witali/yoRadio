$ErrorActionPreference = 'Stop'
$python = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
foreach ($variant in @('production','profile','deep-sleep','rtc32k','qemu-vorbis','qemu-aac')) {
    $defaults = @('sdkconfig.defaults')
    if ($variant -eq 'profile') {
        $defaults += @('sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults')
    } elseif ($variant -eq 'qemu-vorbis') {
        $defaults += @('sdkconfig.qemu.defaults','sdkconfig.qemu-vorbis-lifecycle.defaults','sdkconfig.qemu-vorbis-repair.defaults')
    } elseif ($variant -eq 'qemu-aac') {
        $defaults += @('sdkconfig.qemu.defaults',[IO.Path]::GetFullPath('.build/idf-upgrade/qemu-aac.defaults'))
    } else {
        $defaults += 'sdkconfig.production.defaults'
    }
    $parameters = @{
        DependencyRoot = 'C:/Work/yoRadio/.idf'
        BuildDirectory = "build-idf-6.1-$variant"
        Sdkconfig = "build-idf-6.1-$variant/sdkconfig"
        SdkconfigDefaults = $defaults
        DeepSleepClock = $variant -in @('deep-sleep','rtc32k')
        Rtc32kCrystal = $variant -eq 'rtc32k'
        IdfArguments = @('build')
    }
    Write-Output "START $variant"
    & ./.build/idf-upgrade/build-prepare-6.1.ps1 @parameters *> ".build/idf-upgrade/build-6.1-$variant.log"
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $variant" }
    if (-not $variant.StartsWith('qemu-')) {
        & $python -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant $variant
        if ($LASTEXITCODE -ne 0) { throw "Firmware export failed: $variant" }
    }
    Write-Output "END $variant"
}
