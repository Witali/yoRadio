$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-decode-probe-20261015/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-flac-output-diagnostic/sdkconfig'))
$config = [regex]::Replace($config, '(?m)^(?:CONFIG_YORADIO_STREAM_READ_TIMEOUT_MS=.*|# CONFIG_YORADIO_STREAM_READ_TIMEOUT_MS is not set)\r?\n?', '')
$config = $config.TrimEnd() + "`nCONFIG_YORADIO_STREAM_READ_TIMEOUT_MS=250`n"
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf `
    -BuildDirectory build-decode-probe-20261015 `
    -Sdkconfig build-decode-probe-20261015/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-decode-probe-diagnostic `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-decdiag-20261015',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
