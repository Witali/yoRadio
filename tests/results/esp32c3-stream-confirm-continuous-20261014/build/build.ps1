$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-continuous-confirm-20261014/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-production-20261013/sdkconfig'))
foreach ($option in @('YORADIO_FRAME_ROUTER','YORADIO_STREAM_CONFIRM','YORADIO_AAC_COMPACT_EARLY_OWNER')) {
    $config = [regex]::Replace($config, '(?m)^(?:CONFIG_' + $option + '=.*|# CONFIG_' + $option + ' is not set)\r?\n?', '')
    $config = $config.TrimEnd() + "`nCONFIG_" + $option + "=y`n"
}
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile `
    -BuildDirectory build-continuous-confirm-20261014 `
    -Sdkconfig build-continuous-confirm-20261014/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-continuous-confirm `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-confirm-20261014',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4',
        '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
