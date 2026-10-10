$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
foreach ($variant in @('profile','deep-sleep','rtc32k')) {
    $build = "build-idf-6.1-compact-ram-$variant"
    $defaults = @('sdkconfig.defaults')
    if ($variant -eq 'profile') { $defaults += @('sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults') }
    else { $defaults += 'sdkconfig.production.defaults' }
    $parameters = @{
        DependencyRoot = 'C:/Work/yoRadio/.idf'
        BuildDirectory = $build
        Sdkconfig = "$build/sdkconfig"
        SdkconfigDefaults = $defaults
        DeepSleepClock = $variant -in @('deep-sleep','rtc32k')
        Rtc32kCrystal = $variant -eq 'rtc32k'
        IdfArguments = @('build')
    }
    Write-Output "START guarded $variant"
    & ./idf/esp32c3-oled-native/build.ps1 @parameters
    if ($LASTEXITCODE -ne 0) { throw "Build failed $variant" }
    & $py -X utf8 .build/idf-upgrade/save-build.py --version 6.1 --variant "compact-ram-http-$variant" --build-directory "idf/esp32c3-oled-native/$build"
    if ($LASTEXITCODE -ne 0) { throw "Export failed $variant" }
    Write-Output "END guarded $variant"
}
