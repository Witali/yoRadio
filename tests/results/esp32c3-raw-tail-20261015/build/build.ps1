$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-raw-tail-20261015/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-read512-diagnostic/sdkconfig'))
$config = [regex]::Replace($config, '(?m)^(?:CONFIG_YORADIO_STREAM_READ_BYTES=.*|# CONFIG_YORADIO_STREAM_READ_BYTES is not set)\r?\n?', '')
$config = $config.TrimEnd() + "`nCONFIG_YORADIO_STREAM_READ_BYTES=512`n"
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf `
    -BuildDirectory build-raw-tail-20261015 `
    -Sdkconfig build-raw-tail-20261015/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-raw-tail-diagnostic `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-rawtail-20261015',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
