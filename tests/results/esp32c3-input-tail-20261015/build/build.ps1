$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-input-tail-lab-20261015/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-confirm-tls-lab/sdkconfig'))
$config = [regex]::Replace($config, '(?m)^(?:CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=.*|# CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS is not set)\r?\n?', '')
$config = $config.TrimEnd() + "`nCONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS=0`nCONFIG_YORADIO_INPUT_TAIL_COALESCE=y`n"
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile `
    -BuildDirectory build-input-tail-lab-20261015 `
    -Sdkconfig build-input-tail-lab-20261015/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-input-tail-lab `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-intail-20261015',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
