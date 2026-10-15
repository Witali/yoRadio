$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-aac-prefill2-lab-20261015/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-confirm-tls-lab/sdkconfig'))
$config = [regex]::Replace($config, '(?m)^(?:CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=.*|# CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS is not set)\r?\n?', '')
$config = $config.Replace('CONFIG_YORADIO_INPUT_PREFILL_MS=1000', 'CONFIG_YORADIO_INPUT_PREFILL_MS=2000').Replace('CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=1000', 'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=2000')
$config = $config.TrimEnd() + "`nCONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=0`n"
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf `
    -BuildDirectory build-aac-prefill2-lab-20261015 `
    -Sdkconfig build-aac-prefill2-lab-20261015/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-aac-prefill2-lab `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-aacpf2-20261015',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
