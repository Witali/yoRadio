$ErrorActionPreference = 'Stop'
$configPath = 'idf/esp32c3-oled-native/build-confirm-tls-lab-20261015/sdkconfig'
New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null
$config = [IO.File]::ReadAllText((Join-Path $PWD 'firmware/development/esp32c3-idf61-confirm-probe/sdkconfig'))
foreach ($option in @('MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')) {
    $config = [regex]::Replace($config, '(?m)^(?:CONFIG_' + $option + '=.*|# CONFIG_' + $option + ' is not set)\r?\n?', '')
    $config = $config.TrimEnd() + "`nCONFIG_" + $option + "=y`n"
}
$config = [regex]::Replace($config, '(?m)^CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH=.*\r?\n?', '')
$config += 'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH="C:/Work/yoRadio/.worktree/merge-c3-idf-20261013/.build/c3-confirm-tls-lab-20261015/trust/ca.pem"' + "`n"
[IO.File]::WriteAllText((Join-Path $PWD $configPath), $config, [Text.UTF8Encoding]::new($false))
& ./idf/esp32c3-oled-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile `
    -BuildDirectory build-confirm-tls-lab-20261015 `
    -Sdkconfig build-confirm-tls-lab-20261015/sdkconfig `
    -FirmwareOutputDirectory firmware/development/esp32c3-idf61-confirm-tls-lab `
    -IdfArguments @('-D', 'PROJECT_VER=idf61-ctls-20261015',
        '-D', 'CMAKE_JOB_POOLS=compile_limit=4',
        '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit',
        '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', 'build')
exit $LASTEXITCODE
