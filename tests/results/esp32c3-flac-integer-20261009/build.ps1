$ErrorActionPreference = 'Stop'
$py = 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
foreach ($slots in @(0, 4)) {
    $variant = "r9a97-flac-integer$slots"
    $build = "build-idf-6.1-$variant"
    $directory = "idf/esp32c3-oled-native/$build"
    if (Test-Path $directory) { throw 'Preserve existing build' }
    if (Test-Path "firmware/development/esp32c3-idf-6.1-$variant") { throw 'Preserve existing artifact' }
    New-Item -ItemType Directory -Force $directory | Out-Null
    $config = Get-Content -Raw firmware/development/esp32c3-idf-6.1-r9a97-flac-retained-owner/sdkconfig
    foreach ($option in @('YORADIO_PDM_FRACTIONAL_CLOCK', 'YORADIO_HEAP_FRAGMENT_PROBE', 'HEAP_USE_HOOKS', 'YORADIO_WEB_TCP_PROBE')) {
        $pattern = '(?m)^(?:CONFIG_' + $option + '=.*|# CONFIG_' + $option + ' is not set)\r?\n?'
        $config = [regex]::Replace($config, $pattern, '')
        $config += "`n# CONFIG_$option is not set`n"
    }
    $config = [regex]::Replace($config, '(?m)^CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=.*$', "CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=$slots")
    [IO.File]::WriteAllText((Join-Path (Get-Location) "$directory/sdkconfig"), $config)
    & ./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -SdkconfigDefaults @('sdkconfig.defaults') -IdfArguments @('-D', "PROJECT_VER=idf61-flac-int$slots", '-D', 'CMAKE_JOB_POOLS=compile_limit=2', '-D', 'CMAKE_JOB_POOL_COMPILE=compile_limit', '-D', 'CMAKE_JOB_POOL_LINK=compile_limit', '-D', 'YORADIO_FLASH_MODE_PROBE=ON', '-D', 'YORADIO_HARDWARE_FLAC_CLZ_TEST=OFF', 'build')
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    & $py -X utf8 .build/c3-idf-head-20261008/save-head.py --version 6.1 --variant $variant
    if ($LASTEXITCODE -ne 0) { throw 'Artifact export failed' }
    Copy-Item -LiteralPath "$directory/bootloader/bootloader.bin" -Destination "firmware/development/esp32c3-idf-6.1-$variant/bootloader.bin"
}
